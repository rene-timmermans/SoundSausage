"""Daily capture/edit/mix/save/reopen/export workflow through the real Qt editor."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtWidgets import QApplication,QMessageBox,QDialogButtonBox
from PySide6.QtMultimedia import QAudioFormat

from soundsausage.audio import read_wav,write_wav
from soundsausage.document import Document
from soundsausage.project import save_project
from soundsausage.recovery import candidates,discard
from soundsausage.recording_ui import RecordDialog
from soundsausage.window import MainWindow
from test_capture import Source
from test_playback import Device,MemorySettings

ROOT=Path(__file__).resolve().parents[1]


class RecordingGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build');self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
        self.window=MainWindow(no_audio=False)
        self.input=patch.object(self.window.audio_devices,'inputs',return_value=[Device('USB stereo microphone',b'webcam',supported={(48000,2,QAudioFormat.SampleFormat.Float)})]);self.input.start()
        self.output=patch.object(self.window.audio_devices,'outputs',return_value=[]);self.output.start()
        self.window.recorder._source_factory=Source
        self.errors=patch.object(self.window,'error');self.error=self.errors.start()
        self.window.enable_recovery(offer=False)
    def tearDown(self):
        if self.window.recorder.active:
            self.window.recorder.stop(keep=False)
            if self.window.recording_busy:self.window.end_recording_view()
        self.window.document.mark_saved();self.window.session.mark_saved();self.window.close()
        self.window.deleteLater();self.app.processEvents()
        self.errors.stop();self.output.stop();self.input.stop();self.env.stop();self.folder.cleanup()

    def capture(self,data,target='new',rate=48000,channels=2):
        self.assertTrue(self.window.start_recording(target=target,rate=rate,channels=channels))
        self.window.recorder.source.push(data.astype(np.float32).tobytes())
        self.window.stop_recording()
        self.assertEqual(self.window.recorder.state,'Stopped')
        self.assertFalse(self.window.recording_busy)
        self.error.assert_not_called()

    def test_record_new_waveform_live_levels_single_undo_and_actions_restore(self):
        self.assertTrue(self.window.start_recording(rate=48000,channels=2))
        self.assertFalse(self.window.actions['open'].isEnabled())
        self.assertFalse(self.window.actions['mode_multi'].isEnabled())
        self.window.recorder.source.push(np.full((400,2),.25,np.float32).tobytes())
        self.assertEqual(self.window.transport.meter.peaks,(.25,.25))
        self.assertEqual(self.window.recording_view.frames,400)
        self.assertGreater(len(self.window.recording_view.bins),0)
        self.assertEqual(self.window.document.frames,0)
        self.window.toggle_pause();self.assertEqual(self.window.recorder.state,'Paused')
        self.window.toggle_pause();self.window.actions["play"].trigger()
        self.assertEqual(self.window.document.frames,400);self.assertTrue(self.window.document.dirty)
        self.assertEqual(self.window.document.undo_stack[-1].label,'Record')
        self.assertTrue(self.window.actions['open'].isEnabled());self.assertTrue(self.window.actions['mode_multi'].isEnabled())
        self.assertFalse(self.window.actions['discard_recording'].isEnabled())
        self.window.edit(self.window.document.undo);self.assertEqual(self.window.document.frames,0)
        self.window.edit(self.window.document.redo);np.testing.assert_array_equal(self.window.document.view(),.25)

    def test_insert_and_replace_selection_can_be_undone_without_mutating_original(self):
        original=np.full((100,2),.1,np.float32)
        self.window.document=Document(original,48000);self.window.refresh(fit=True)
        self.window.document.select(20,50)
        self.capture(np.full((15,2),.3,np.float32),target='insert')
        expected=np.concatenate((original[:20],np.full((15,2),.3,np.float32),original[20:]))
        np.testing.assert_array_equal(self.window.document.view(),expected)
        self.window.document.undo();self.window.document.select(20,50)
        self.capture(np.full((15,2),.3,np.float32),target='replace')
        self.assertEqual(self.window.document.frames,85)
        self.window.document.undo();np.testing.assert_array_equal(self.window.document.view(),original)

    def test_cancelled_final_processing_leaves_existing_work_and_recoverable_take(self):
        self.window.document=Document(np.ones((20,2),np.float32),48000);self.window.refresh()
        self.window.start_recording(target='insert',rate=48000,channels=2)
        self.window.recorder.source.push(np.full((80,2),.25,np.float32).tobytes())
        with patch.object(self.window,'apply_recorded_take',return_value=False):self.window.stop_recording()
        np.testing.assert_array_equal(self.window.document.view(),1)
        available=candidates();self.assertEqual(len(available),1)
        self.assertTrue(self.window.restore_recorded_take(available[0]))
        np.testing.assert_array_equal(self.window.document.view(),.25)
        self.assertEqual(self.window.document.frames,80);available[0].close()

    def test_discard_and_cancel_close_preserve_existing_document(self):
        self.window.start_recording(rate=48000,channels=2)
        self.window.recorder.source.push(np.ones((100,2),np.float32).tobytes())
        with patch('soundsausage.recording_ui.QMessageBox.question',return_value=QMessageBox.StandardButton.Cancel):
            self.window.close()
        self.assertEqual(self.window.recorder.state,'Recording')
        with patch('soundsausage.recording_ui.QMessageBox.question',return_value=QMessageBox.StandardButton.Discard):
            self.window.discard_recording()
        self.assertFalse(self.window.recording_busy);self.assertEqual(self.window.document.frames,0)
        self.assertEqual(candidates(),[])

    def test_opening_another_view_cannot_discard_the_wrong_unsaved_model(self):
        self.window.session.add_track('Unsaved track')
        project=self.path/'other.celp'
        from soundsausage.session import Session
        save_project(Session(48000,1),project)
        original=self.window.session
        with patch.object(self.window,'confirm_session_discard',return_value=False) as confirm,patch.object(self.window,'_confirm_discard') as wave_confirm:
            self.assertFalse(self.window.open_selected_path(project))
        confirm.assert_called_once();wave_confirm.assert_not_called()
        self.assertIs(self.window.session,original)
        wave=self.path/'other.wav';write_wav(wave,np.ones((10,1),np.float32),48000)
        self.window.set_mode('multitrack')
        with patch.object(self.window,'_confirm_discard',return_value=False) as confirm,patch.object(self.window,'confirm_session_discard') as session_confirm:
            self.assertFalse(self.window.open_selected_path(wave))
        confirm.assert_called_once();session_confirm.assert_not_called()
        self.assertIs(self.window.session,original)

    def test_stop_keeps_playback_cursor_for_resume_and_recording(self):
        self.window.document=Document(np.ones((1000,2),np.float32),48000);self.window.refresh()
        self.window.playback_position(317);self.window.player.stop()
        self.assertEqual(self.window.document.cursor,317)
        with patch.object(self.window.player,'play') as play:
            self.window.toggle_play()
        self.assertEqual(play.call_args.args[2],317)
        self.capture(np.full((10,2),.5,np.float32),target='insert')
        np.testing.assert_array_equal(self.window.document.view(317,327),.5)

    def test_setup_shows_usb_input_and_locks_existing_waveform_format(self):
        self.window.document=Document(np.ones((100,1),np.float32),44100)
        dialog=RecordDialog(self.window)
        self.assertEqual(dialog.target.currentData(),'insert')
        self.assertFalse(dialog.rate.isEnabled());self.assertFalse(dialog.channels.isEnabled())
        self.assertEqual(dialog.channels.currentIndex(),0)
        self.assertIn('converted',dialog.note.text())
        dialog.input.setCurrentIndex(1)
        self.assertEqual(dialog.settings()['input_id'],b'webcam'.hex())
        self.assertTrue(dialog.box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        dialog.reject();dialog.deleteLater()

    def test_start_skip_preference_and_live_audio_exclude_the_initial_peak(self):
        w=self.window
        with patch.object(w.audio_devices,'settings',MemorySettings()):
            dialog=RecordDialog(w)
            self.assertEqual(dialog.skip_start.value(),50)
            dialog.skip_start.setValue(100);dialog.reject();dialog.deleteLater()
            self.assertIsNone(w.audio_devices.settings.value('recording/skip_start_ms'))
            self.assertTrue(w.start_recording(rate=48000,channels=2,skip_start_ms=100))
            data=np.concatenate((np.ones((4800,2),np.float32),np.full((500,2),.25,np.float32)))
            w.recorder.source.push(data.tobytes())
            self.assertEqual(w.recording_view.frames,500)
            self.assertEqual(w.transport.meter.peaks,(.25,.25))
            w.stop_recording()
            self.assertEqual(w.document.frames,500);self.assertEqual(w.document.read()[0,0],0)
            self.assertEqual(w.document.read()[-1,0],.25)
            dialog=RecordDialog(w);self.assertEqual(dialog.skip_start.value(),100)
            dialog.reject();dialog.deleteLater()
        self.error.assert_not_called()

    def test_start_skip_insertion_is_one_undo_step(self):
        w=self.window;original=np.full((20,2),.1,np.float32)
        w.document=Document(original,48000);w.document.select(10,10);w.refresh()
        with patch.object(w.audio_devices,'settings',MemorySettings()):
            self.assertTrue(w.start_recording(target='insert',rate=48000,channels=2,skip_start_ms=5))
            w.recorder.source.push(np.full((740,2),.3,np.float32).tobytes());w.stop_recording()
        self.assertEqual(w.document.frames,520)
        np.testing.assert_array_equal(w.document.read()[:10],original[:10])
        np.testing.assert_array_equal(w.document.read()[-10:],original[10:])
        self.assertEqual(len(w.document.undo_stack),1)
        w.document.undo();np.testing.assert_array_equal(w.document.read(),original)
        self.error.assert_not_called()

    def test_full_record_edit_multitrack_save_reopen_and_mixdown_chain(self):
        data=np.column_stack((np.linspace(-.5,.5,4800),np.linspace(.2,-.2,4800))).astype(np.float32)
        self.capture(data)
        self.window.effect('gain',initial=.5)
        waveform=self.path/'take.wav'
        with patch.object(self.window,'_save_path',return_value=(waveform,'float32')):
            self.assertTrue(self.window.save_waveform())
        saved=read_wav(waveform).samples
        np.testing.assert_array_equal(saved,data*.5)
        self.window.insert_waveform();self.assertEqual(self.window.mode,'multitrack')
        self.window.session.select(2400,2400)
        self.capture(np.tile([.1,.3],(2400,1)),target='multitrack')
        clips=self.window.session.tracks[0].clips;self.assertEqual(len(clips),2)
        self.assertEqual(self.window.session.undo_stack[-1].label,'Record')
        self.window.session.configure_clip(clips[1].id,gain=.5,fade_in=40,fade_out=50,
                                          volume_envelope=((0,1.),(2399,.8)))
        expected=self.window.session.render()
        project=self.path/'project.celp'
        with patch('soundsausage.session_actions.QFileDialog.getSaveFileName',return_value=(str(project),'')):
            self.assertTrue(self.window.save_session())
        self.assertTrue(self.window.close_session());self.assertEqual(self.window.document.frames,len(data))
        self.assertTrue(self.window.load_session_path(project))
        np.testing.assert_array_equal(self.window.session.render(),expected)
        output=self.path/'mix.wav'
        with patch.object(self.window,'_save_path',return_value=(output,'float32')):self.window.mixdown()
        np.testing.assert_array_equal(read_wav(output).samples,expected)
        np.testing.assert_array_equal(read_wav(waveform).samples,saved)
        self.error.assert_not_called()


if __name__=='__main__':unittest.main()
