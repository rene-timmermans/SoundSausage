"""Device-clock correction, explicit calibration, cancellation and user controls."""
from contextlib import ExitStack
import os
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication

from soundsausage.window import MainWindow
from soundsausage.session import Session
from soundsausage.recording_ui import RecordDialog
from soundsausage.calibration_ui import CalibrationDialog
from soundsausage.synchronization import save_calibration,read_calibration
from test_playback import Device,MemorySettings,Sink
from test_capture import Source


class AutomaticRecordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.stack=ExitStack()
        self.stack.enter_context(patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':self.temp.name}))
        self.window=MainWindow(no_audio=False);w=self.window
        w.audio_devices.settings=MemorySettings()
        self.stack.enter_context(patch.object(w.audio_devices,'inputs',return_value=[Device('Input',b'input')]))
        self.stack.enter_context(patch.object(w.audio_devices,'outputs',return_value=[Device()]))
        self.errors=self.stack.enter_context(patch.object(w,'error'))
        w.recorder._source_factory=Source;w.player._sink_factory=Sink
        w.session=Session(48000,2);w.session.import_audio([(np.zeros((480000,2),np.float32),48000,'Backing')])
        w.session.selected_track=w.session.tracks[1].id;w.set_mode('multitrack');w.session.select(4800,4800)
        self.dialogs=[]

    def tearDown(self):
        for dialog in self.dialogs:dialog.reject();dialog.deleteLater()
        w=self.window
        if w.recorder.active:w.recorder.stop(keep=False)
        w.player.stop();w.document.mark_saved();w.session.mark_saved();w.close();w.deleteLater();self.app.processEvents()
        self.stack.close();self.temp.cleanup()

    def test_automatic_take_uses_calibration_skip_and_measured_clock_ratio(self):
        w=self.window;ratio=.9996;offset=120
        save_calibration(w.audio_devices,48000,0,dict(offset_ms=-10,confidence=1))
        self.assertTrue(w.start_recording(target='multitrack',rate=48000,channels=1,accompaniment=True,skip_start_ms=10,automatic_sync=True))
        context=w._record_context
        with patch.object(w.player,'_tick',side_effect=lambda:setattr(w.player,'_last_frame',4800+offset+round(w.recorder.received_frames*ratio))):
            for _ in range(320):w.recorder.source.push(np.full((480,2),.2,np.float32).tobytes())
            count=w.recorder.take.frames;fit=context['clock'].result()
            self.assertTrue(fit.drift_measured)
            w.stop_recording()
        clip=w.session.tracks[1].clips[0]
        self.assertAlmostEqual(clip.start,round(4800+offset+480*ratio-480),delta=1)
        self.assertEqual(clip.frames,round(count*fit.ratio))
        self.assertEqual(len(w.session.undo_stack),2) # backing import + recording
        w.session.undo();self.assertFalse(w.session.tracks[1].clips)
        self.errors.assert_not_called()

    def test_short_take_uses_calibration_without_unmeasured_drift_stretch(self):
        w=self.window;save_calibration(w.audio_devices,48000,0,dict(offset_ms=-5,confidence=1))
        self.assertTrue(w.start_recording(target='multitrack',rate=48000,channels=2,accompaniment=True,skip_start_ms=0,automatic_sync=True))
        with patch.object(w.player,'_tick',side_effect=lambda:setattr(w.player,'_last_frame',4800+w.recorder.received_frames)):
            w.recorder.source.push(np.full((480,2),.25,np.float32).tobytes());w.stop_recording()
        clip=w.session.tracks[1].clips[0]
        self.assertEqual((clip.start,clip.frames),(4560,480))
        np.testing.assert_array_equal(w.session.media[clip.media_id].samples,.25)

    def calibration_dialog(self):
        dialog=CalibrationDialog(self.window,rate=48000);self.dialogs.append(dialog)
        dialog.recorder._source_factory=Source;dialog.player._sink_factory=Sink
        return dialog

    def test_calibration_runs_the_capture_playback_measurement_and_saves_a_profile(self):
        dialog=self.calibration_dialog();dialog.start_calibration();dialog._play_timer.stop()
        dialog.play_probe();dialog._stop_timer.stop()
        delay=480;capture=np.pad(dialog.reference*.5,((delay,480),(0,0)))
        with patch.object(dialog.player,'_tick',side_effect=lambda:setattr(dialog.player,'_last_frame',dialog.recorder.received_frames)):
            for start in range(0,len(capture),480):dialog.recorder.source.push(capture[start:start+480].tobytes())
            dialog.finish_measurement()
        self.assertIsNotNone(dialog.calibration_result)
        profile=read_calibration(self.window.audio_devices,48000)
        self.assertAlmostEqual(profile['offset_ms'],-10,delta=.02)
        self.assertFalse(dialog.recorder.active);self.assertFalse(self.window.document.dirty)

    def test_cancelled_or_failed_calibration_preserves_the_previous_profile_and_audio(self):
        save_calibration(self.window.audio_devices,48000,0,dict(offset_ms=-17,confidence=1))
        dialog=self.calibration_dialog();dialog.start_calibration();take=dialog.recorder.take
        audio_path,journal=take.path,take.journal
        dialog.recorder.source.push(np.full((480,2),.1,np.float32).tobytes());dialog.reject()
        self.assertFalse(audio_path.exists());self.assertFalse(journal.exists());self.assertIsNone(dialog.calibration_result)
        self.assertEqual(read_calibration(self.window.audio_devices,48000)['offset_ms'],-17)
        dialog=self.calibration_dialog();dialog.start_calibration();dialog.failed('Input disconnected')
        self.assertIsNone(dialog.calibration_result);self.assertFalse(dialog.recorder.active)
        self.assertEqual(read_calibration(self.window.audio_devices,48000)['offset_ms'],-17)

    def test_automatic_and_manual_controls_are_exclusive(self):
        dialog=RecordDialog(self.window);self.dialogs.append(dialog)
        self.assertTrue(dialog.automatic.isChecked());self.assertFalse(dialog.offset.isEnabled())
        dialog.automatic.setChecked(False);dialog.offset.setValue(-17)
        self.assertTrue(dialog.offset.isEnabled());self.assertEqual(dialog.settings()['recording_offset_ms'],-17)
        self.assertFalse(dialog.settings()['automatic_sync'])
        dialog.automatic.setChecked(True)
        self.assertTrue(dialog.settings()['automatic_sync']);self.assertEqual(dialog.settings()['recording_offset_ms'],0)
        dialog.accompaniment.setChecked(False);self.assertFalse(dialog.settings()['automatic_sync'])

    def test_audio_disabled_dialogs_do_not_discover_devices(self):
        self.window.no_audio=True
        with patch.object(self.window.audio_devices,'inputs',side_effect=AssertionError('Audio is disabled')) as inputs, patch.object(self.window.audio_devices,'outputs',side_effect=AssertionError('Audio is disabled')) as outputs:
            for cls in (RecordDialog,CalibrationDialog):
                dialog=cls(self.window);self.dialogs.append(dialog)
            inputs.assert_not_called();outputs.assert_not_called()
