"""Explicit monitor discovery and capture lifecycle without host audio access."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.audio import AudioError
from soundsausage.audio_devices import AudioDevices, AudioHardwareDialog
from soundsausage.capture import Recorder, input_format
from soundsausage.recording_ui import RecordDialog
from soundsausage.system_audio import SystemOutputDevice, SystemAudioSource, SYSTEM_OUTPUT, capture_command, query
from soundsausage.window import MainWindow
from test_playback import MemorySettings


class SystemAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name)
        self.env = patch.dict(os.environ, {'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')}); self.env.start()
        self.device = SystemOutputDevice('output.monitor', 'Main speakers')
        self.devices = AudioDevices(settings=MemorySettings())
        self.monitor = patch.object(AudioDevices, '_ensure_monitor'); self.monitor.start()
        self.devices.configure('', 100, SYSTEM_OUTPUT)

    def tearDown(self):
        self.devices.deleteLater(); self.app.processEvents()
        self.monitor.stop()
        self.env.stop(); self.folder.cleanup()

    def wait_for(self, predicate, seconds=5):
        end = time.monotonic()+seconds
        while not predicate() and time.monotonic() < end: QTest.qWait(10)
        self.assertTrue(predicate(), 'System audio capture timed out')

    def producer(self, script=None):
        self.marker = self.path/'marker'; self.marker.write_text('.25')
        fixture = self.path/'producer.py'
        fixture.write_text(script or '''import sys,time,struct
from pathlib import Path
while True:
    value=float(Path(sys.argv[1]).read_text())
    sys.stdout.buffer.write(struct.pack('ff',value,-value)*240)
    sys.stdout.buffer.flush()
    time.sleep(.005)
''')
        return patch('soundsausage.system_audio.capture_command', return_value=(sys.executable, ['-u', str(fixture), str(self.marker)]))

    def test_resolves_named_monitor_and_never_guesses_or_uses_default_microphone(self):
        with patch('soundsausage.system_audio.utility',return_value='/usr/bin/parec'), patch('soundsausage.system_audio.query',side_effect=[
                {'default_sink_name':'main'}, [{'name':'other','monitor_source':'wrong'},
                 {'name':'main','monitor_source':'explicit.monitor','description':'USB DAC'}]]):
            device = SystemOutputDevice.resolve()
        self.assertEqual(device.monitor, 'explicit.monitor'); self.assertIn('USB DAC', device.description())
        self.assertNotEqual(device.id(), self.device.id())
        for info, sinks in (({},[{'monitor_source':'oops'}]), ({'default_sink_name':'main'},[]),
                            ({'default_sink_name':'main'},[{'name':'main','monitor_source':7}])):
            with patch('soundsausage.system_audio.utility',return_value='parec'), patch('soundsausage.system_audio.query',side_effect=[info,sinks]):
                with self.assertRaises(AudioError): SystemOutputDevice.resolve()

    def test_query_uses_json_no_shell_and_reports_unavailable_server_or_utilities(self):
        with patch('soundsausage.system_audio.utility',return_value='/usr/bin/pactl'), patch('soundsausage.system_audio.subprocess.run') as run:
            run.return_value.stdout = json.dumps({'default_sink_name':'main'}).encode()
            self.assertEqual(query('info')['default_sink_name'],'main')
            self.assertEqual(run.call_args.args[0],['/usr/bin/pactl','--format=json','info'])
            self.assertEqual(run.call_args.kwargs['timeout'],2)
            for failure in (subprocess.TimeoutExpired('pactl',2), OSError('disconnected'), ValueError('bad JSON')):
                run.side_effect=failure
                with self.assertRaisesRegex(AudioError,'system audio output'): query('info')
        with patch('soundsausage.system_audio.shutil.which',return_value=None):
            with self.assertRaisesRegex(AudioError,'client utilities'): SystemOutputDevice.resolve()

    def test_preference_is_persistent_and_works_without_any_microphone(self):
        with patch.object(self.devices,'inputs',return_value=[]), patch.object(SystemOutputDevice,'resolve',return_value=self.device) as resolve:
            self.assertIs(self.devices.input(),self.device)
            restored=AudioDevices(settings=self.devices.settings)
            self.assertEqual(restored.input_id,SYSTEM_OUTPUT); self.assertIs(restored.input(),self.device)
            restored.deleteLater(); self.assertEqual(resolve.call_count,2)

    def test_float_stereo_format_keeps_mono_channel_selection_and_explicit_process_arguments(self):
        for rate in (1000,44100,48000,384000):
            fmt=input_format(self.device,rate,1,1)
            self.assertEqual((fmt.sampleRate(),fmt.channelCount()),(rate,2))
            with patch('soundsausage.system_audio.utility',return_value='/usr/bin/parec'):
                command,args=capture_command(self.device,fmt)
            self.assertEqual(command,'/usr/bin/parec');self.assertIn('--device=output.monitor',args)
            self.assertIn('--format=float32ne',args);self.assertIn('--channels=2',args)
        with self.assertRaises(AudioError):input_format(self.device,48000,2,1)

    def test_both_dialogs_offer_system_audio_and_cancel_preserves_preferences(self):
        with patch.object(self.devices,'inputs',return_value=[]),patch.object(self.devices,'outputs',return_value=[]):
            dialog=AudioHardwareDialog(self.devices)
            self.assertEqual(dialog.input.currentData(),SYSTEM_OUTPUT)
            dialog.input.setCurrentIndex(0);dialog.reject()
            self.assertEqual(self.devices.input_id,SYSTEM_OUTPUT);dialog.deleteLater()
        from soundsausage.i18n import install_language, language, tr
        previous=language()
        with patch.object(AudioDevices,'inputs',return_value=[]),patch.object(AudioDevices,'outputs',return_value=[]),patch.object(SystemOutputDevice,'resolve',return_value=self.device):
            window=MainWindow(no_audio=False)
            try:
                dialog=RecordDialog(window)
                self.assertGreaterEqual(dialog.input.findData(SYSTEM_OUTPUT),0)
                dialog.input.setCurrentIndex(dialog.input.findData(SYSTEM_OUTPUT))
                dialog.show();self.app.processEvents()
                sentence='Records the default system output, including other apps and any backing tracks played there. Pause excludes paused audio. A new take uses the current default output.'
                for code in ('nl','en','de','fr','es'):
                    install_language().set_language(code,False)
                    self.assertIn(tr(sentence),dialog.note.text())
                    self.assertTrue(dialog.box.buttons()[0].isEnabled())
                dialog.reject();dialog.deleteLater()
            finally:
                install_language().set_language(previous,False)
                window.document.mark_saved();window.session.mark_saved();window.close();window.deleteLater()

    def test_actual_pull_stream_captures_float_samples_and_stops_at_exact_limit(self):
        takes=[];errors=[];recorder=Recorder(devices=self.devices)
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device), self.producer():
                self.assertTrue(recorder.start(48000,2,limit_seconds=.05),errors)
                self.assertIsInstance(recorder.source,SystemAudioSource)
                self.wait_for(lambda:recorder.state=='Stopped')
            self.assertFalse(errors,errors);self.assertEqual(len(takes),1)
            self.assertEqual(takes[0].frames,2400)
            np.testing.assert_array_equal(takes[0].samples[:,0],.25)
            np.testing.assert_array_equal(takes[0].samples[:,1],-.25)
            self.assertIsNone(recorder.source)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater()

    def test_pause_discards_queued_time_and_resume_starts_a_fresh_stream_on_same_monitor(self):
        takes=[];errors=[];recorder=Recorder(devices=self.devices)
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device), self.producer():
                recorder.start(48000,1,first_channel=1)
                self.wait_for(lambda:recorder.take.frames>=480)
                recorder.toggle_pause(); frozen=recorder.take.frames
                self.assertIsNone(recorder.source.process)
                self.marker.write_text('.75');QTest.qWait(80)
                self.assertEqual(recorder.take.frames,frozen)
                recorder.toggle_pause();self.wait_for(lambda:recorder.take.frames>frozen+240)
                recorder.stop()
            self.assertFalse(errors,errors)
            np.testing.assert_array_equal(takes[0].samples[:frozen],-.25)
            np.testing.assert_array_equal(takes[0].samples[frozen:],-.75)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater()

    def test_process_failure_retains_complete_frames_and_discards_partial_frame(self):
        script="import sys,struct;sys.stdout.buffer.write(struct.pack('ff',.25,-.5)*100+b'abc');sys.stdout.buffer.flush()"
        takes=[];errors=[];recorder=Recorder(devices=self.devices)
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device),self.producer(script):
                self.assertTrue(recorder.start(48000,2))
                self.wait_for(lambda:recorder.state=='Stopped')
            self.assertEqual(len(errors),1);self.assertEqual(takes[0].frames,100)
            np.testing.assert_array_equal(takes[0].samples[:,1],-.5)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater()

    def test_discard_and_missing_output_never_open_a_microphone(self):
        recorder=Recorder(devices=self.devices);errors=[];recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device),self.producer():
                recorder.start(48000,2);self.wait_for(lambda:recorder.take.frames>0)
                path=recorder.take.path;recorder.stop(keep=False)
                self.assertFalse(path.exists());self.assertIsNone(recorder.source)
            with patch.object(SystemOutputDevice,'resolve',side_effect=AudioError('No system output')),patch.object(self.devices,'inputs') as microphones:
                self.assertFalse(recorder.start(48000,2));microphones.assert_not_called()
        finally:recorder.stop(keep=False);recorder.deleteLater()

    def test_output_change_retains_take_instead_of_switching_to_another_monitor(self):
        recorder=Recorder(devices=self.devices);takes=[];errors=[]
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device),self.producer():
                recorder.start(48000,2);self.wait_for(lambda:recorder.take.frames>0)
                with patch.object(SystemOutputDevice,'resolve',return_value=SystemOutputDevice('other.monitor','Other')):
                    self.devices.outputs_changed.emit()
            self.assertEqual(recorder.state,'Stopped');self.assertEqual(len(takes),1);self.assertEqual(len(errors),1)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater()

    def test_system_recording_inserts_as_one_undo_step_and_saves_the_result(self):
        from soundsausage.audio import write_wav, read_wav
        from soundsausage.document import Document
        window=MainWindow(no_audio=False);errors=[]
        window.audio_devices.settings=MemorySettings()
        window.audio_devices.input_id='';window.audio_devices.output_id=''
        window.error=lambda title,message:errors.append(str(message))
        original=np.zeros((320,2),np.float32)
        window.document=Document(original,8000);window.document.select(90,90);window.refresh(fit=True)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device),self.producer():
                self.assertTrue(window.start_recording(target='insert',rate=8000,channels=2,input_id=SYSTEM_OUTPUT,limit_seconds=.02,skip_start_ms=0))
                self.wait_for(lambda:not window.recording_busy)
            self.assertFalse(errors,errors);self.assertEqual(window.document.frames,480)
            self.assertEqual(len(window.document.undo_stack),1)
            result=window.document.read()
            np.testing.assert_array_equal(result[90:250,0],.25)
            np.testing.assert_array_equal(result[90:250,1],-.25)
            window.document.undo();np.testing.assert_array_equal(window.document.view(),original)
            window.document.redo();np.testing.assert_array_equal(window.document.view(),result)
            path=self.path/'system.wav';write_wav(path,result,8000,'float32')
            np.testing.assert_array_equal(read_wav(path).samples,result)
        finally:
            window.recorder.stop(keep=False)
            window.document.mark_saved();window.session.mark_saved();window.close();window.deleteLater()

    def test_resume_failure_keeps_the_already_recorded_take(self):
        recorder=Recorder(devices=self.devices);takes=[];errors=[]
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            with patch.object(SystemOutputDevice,'resolve',return_value=self.device),self.producer():
                recorder.start(48000,2);self.wait_for(lambda:recorder.take.frames>0)
                recorder.toggle_pause();frames=recorder.take.frames
                with patch('soundsausage.system_audio.capture_command',side_effect=AudioError('missing utility')):
                    recorder.toggle_pause()
            self.assertEqual(recorder.state,'Stopped');self.assertIsNone(recorder.source)
            self.assertEqual(takes[0].frames,frames);self.assertEqual(len(errors),1)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater()
