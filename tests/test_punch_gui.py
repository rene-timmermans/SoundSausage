"""Punch transport pre-roll, warmed-up input, exact cropping and early stop."""
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
from test_playback import Device,MemorySettings,Sink
from test_capture import Source


class PunchGuiTests(unittest.TestCase):
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
        w.session=Session(48000,1);self.original=np.full((48000,2),.25,np.float32)
        w.session.import_audio([(self.original,48000,'Original')]);w.set_mode('multitrack')
        w.session.select(4800,9600);w.selection_changed(*w.session.selection)

    def tearDown(self):
        w=self.window
        if w.recorder.active:w.recorder.stop(keep=False)
        w.player.stop();w.document.mark_saved();w.session.mark_saved();w.close();w.deleteLater();self.app.processEvents()
        self.stack.close();self.temp.cleanup()

    def prepare(self,automatic=True,pre_roll=.05,skip=10):
        w=self.window
        self.assertTrue(w.start_recording(target='punch',rate=48000,channels=2,pre_roll_seconds=pre_roll,
            punch_fade_ms=0,skip_start_ms=skip,automatic_sync=automatic))
        w._punch_wait_timer.stop()
        # The input warms up before playback so Begin overslaan never removes
        # the first selected samples, including a punch at timeline zero.
        for _ in range(16):w.recorder.source.push(np.zeros((480,2),np.float32).tobytes())
        w.begin_punch_playback();self.assertTrue(w._record_context['play_started'])
        context=w._record_context
        callback=lambda:setattr(w.player,'_last_frame',context['start']+w.recorder.received_frames-context['preplay_received'])
        return context,self.stack.enter_context(patch.object(w.player,'_tick',side_effect=callback))

    def test_punch_auto_stops_crops_to_selection_and_is_one_undo_step(self):
        w=self.window;before=w.session.render();history=len(w.session.undo_stack)
        context,_=self.prepare();seconds=(context['play_end']-context['start'])/48000
        for _ in range(round(seconds*100)):
            w.recorder.source.push(np.full((480,2),.75,np.float32).tobytes())
        self.app.processEvents()
        self.assertFalse(w.recorder.active);self.assertFalse(w.recording_busy)
        clip=w.session.tracks[0].clips[-1];self.assertEqual((clip.start,clip.end),(4800,9600))
        expected=before.copy();expected[4800:9600]=.75
        np.testing.assert_array_equal(w.session.render(),expected)
        self.assertEqual(len(w.session.undo_stack),history+1)
        w.session.undo();np.testing.assert_array_equal(w.session.render(),before)
        self.errors.assert_not_called()

    def test_stopping_during_pre_roll_changes_no_existing_audio(self):
        w=self.window;before=w.session.tracks;history=tuple(w.session.undo_stack)
        self.prepare(automatic=False)
        w.recorder.source.push(np.full((480,2),.75,np.float32).tobytes());w.stop_recording()
        self.assertEqual(w.session.tracks,before);self.assertEqual(tuple(w.session.undo_stack),history)
        self.assertIn('kept',w.statusBar().currentMessage())
        self.errors.assert_not_called()

    def test_punch_at_zero_keeps_first_samples_even_with_start_skip(self):
        w=self.window;w.session.select(0,4800)
        self.prepare(automatic=False,pre_roll=2,skip=50)
        for _ in range(12):w.recorder.source.push(np.full((480,2),.8,np.float32).tobytes())
        w.stop_recording()
        clip=w.session.tracks[0].clips[-1]
        self.assertEqual((clip.start,clip.end),(0,4800))
        np.testing.assert_array_equal(w.session.media[clip.media_id].samples,np.float32(.8))
        self.errors.assert_not_called()

    def test_punch_controls_require_a_multitrack_selection_and_show_range_options(self):
        w=self.window;self.assertTrue(w.actions['punch'].isEnabled())
        dialog=RecordDialog(w);dialog.show();self.app.processEvents()
        try:
            dialog.target.setCurrentIndex(dialog.target.findData('punch'));self.app.processEvents()
            self.assertTrue(dialog.pre_roll.isVisible());self.assertTrue(dialog.crossfade.isVisible())
            self.assertFalse(dialog.accompaniment.isEnabled());self.assertTrue(dialog.accompaniment.isChecked())
            self.assertFalse(dialog.duration.isEnabled());self.assertEqual(dialog.settings()['target'],'punch')
        finally:dialog.reject();dialog.deleteLater()
        w.session.select(0,0);w.selection_changed(0,0);self.assertFalse(w.actions['punch'].isEnabled())
        with self.assertRaises(ValueError):w.start_recording(target='punch',rate=48000)
