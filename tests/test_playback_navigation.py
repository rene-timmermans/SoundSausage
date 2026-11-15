"""Clicks seek audible PCM during playback without turning selection into seeking."""
from contextlib import ExitStack
import os
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.document import Document
from soundsausage.session import Session
from soundsausage.window import MainWindow
from soundsausage.waveform import clock_text
from test_capture import Source
from test_playback import Device, MemorySettings, Sink


class PlaybackNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.stack = ExitStack()
        self.temp = tempfile.TemporaryDirectory()
        self.stack.enter_context(patch.dict(os.environ, {'SOUNDSAUSAGE_CACHE_DIR': self.temp.name}))
        self.rate = 48000
        ramp = np.linspace(-.6, .6, self.rate*12, dtype=np.float32)
        self.audio = np.column_stack((ramp, -ramp))
        self.doc = Document(self.audio, self.rate)
        ui = QSettings(os.path.join(self.temp.name, 'window.ini'), QSettings.Format.IniFormat)
        self.window = w = MainWindow(self.doc, no_audio=False, ui_settings=ui)
        w.audio_devices.settings = MemorySettings()
        self.stack.enter_context(patch.object(w.audio_devices, 'outputs', return_value=[Device()]))
        self.stack.enter_context(patch.object(w.audio_devices, 'inputs', return_value=[Device('Input', b'input')]))
        self.errors = self.stack.enter_context(patch.object(w, 'error'))
        w.player._sink_factory = Sink
        w.recorder._source_factory = Source
        w.show()
        self.app.processEvents()

    def tearDown(self):
        w = self.window
        if w.recorder.active:
            w.recorder.stop(keep=False)
        if w.recording_busy:
            w.end_recording_view()
        w.player.stop()
        w.document.mark_saved()
        w.session.mark_saved()
        w.close()
        w.deleteLater()
        self.app.processEvents()
        self.stack.close()
        self.temp.cleanup()

    def point(self, seconds):
        wave = self.window.waveform
        return QPoint(round(wave.x_at(round(seconds*self.rate))), round(wave.channel_rect(0).center().y()))

    def assert_pcm_starts_at(self, frame):
        w = self.window
        self.assertEqual(w.player.state, 'Playing')
        self.assertEqual(w.player._start_frame, frame)
        self.assertEqual(w.active_model().cursor, frame)
        self.assertEqual(w.active_view().playhead, frame)
        self.assertEqual(w.time_label.text(), clock_text(frame/self.rate))
        actual = np.frombuffer(w.player.sink.received, dtype='<f4').reshape(-1, 2)
        self.assertGreater(len(actual), 0)
        np.testing.assert_array_equal(actual, self.audio[frame:frame+len(actual)])

    def test_click_restarts_running_waveform_at_clicked_pcm_and_clears_old_loop_range(self):
        w = self.window
        self.doc.select(self.rate, self.rate*2)
        w.player.loop = True
        w.toggle_play()
        previous = w.player.sink
        pos = self.point(7.5)
        frame = w.waveform.frame_at(pos.x())
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, pos=pos)
        self.assertIsNot(w.player.sink, previous)
        self.assert_pcm_starts_at(frame)
        self.assertEqual(self.doc.selection, (frame, frame))
        self.assertTrue(w.player.loop)
        self.assertEqual(len(w.player._data), self.doc.frames-frame)
        self.assertFalse(self.doc.undo_stack)
        np.testing.assert_array_equal(self.doc.read(), self.audio)
        self.errors.assert_not_called()

    def test_dragging_and_shift_selecting_do_not_restart_running_audio(self):
        w = self.window
        w.toggle_play()
        sink = w.player.sink
        QTest.mousePress(w.waveform, Qt.MouseButton.LeftButton, pos=self.point(2))
        QTest.mouseMove(w.waveform, self.point(5), 20)
        QTest.mouseRelease(w.waveform, Qt.MouseButton.LeftButton, pos=self.point(5))
        self.assertTrue(self.doc.selected)
        self.assertIs(w.player.sink, sink)
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ShiftModifier, self.point(8))
        self.assertTrue(self.doc.selected)
        self.assertIs(w.player.sink, sink)
        self.assertEqual(w.player.state, 'Playing')

    def test_click_on_an_individual_sample_during_playback_seeks_instead_of_editing(self):
        w = self.window
        frame = self.rate*3
        w.waveform.set_view(frame-20, frame+21)
        w.toggle_play()
        pos = QPoint(round(w.waveform.x_at(frame)), round(w.waveform.sample_y(0, self.audio[frame, 0])))
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, pos=pos)
        self.assert_pcm_starts_at(frame)
        self.assertIsNone(w.waveform._sample_drag)
        self.assertFalse(self.doc.undo_stack)
        np.testing.assert_array_equal(self.doc.read(), self.audio)

    def test_click_at_end_stops_without_wrapping_to_start(self):
        w = self.window
        w.toggle_play()
        pos = QPoint(round(w.waveform.plot_rect().right()), round(w.waveform.channel_rect(0).center().y()))
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, pos=pos)
        self.assertEqual(w.player.state, 'Stopped')
        self.assertEqual(self.doc.cursor, self.doc.frames)
        self.assertEqual(self.doc.selection, (self.doc.frames, self.doc.frames))

    def test_stopped_and_paused_clicks_never_start_playback(self):
        w = self.window
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, pos=self.point(2))
        self.assertEqual(w.player.state, 'Stopped')
        w.toggle_play()
        w.player.toggle_pause()
        sink = w.player.sink
        QTest.mouseClick(w.waveform, Qt.MouseButton.LeftButton, pos=self.point(6))
        self.assertEqual(w.player.state, 'Paused')
        self.assertIs(w.player.sink, sink)

    def test_five_second_buttons_and_home_keep_playing(self):
        w = self.window
        w.toggle_play()
        w.actions['seek_forward'].trigger()
        self.assert_pcm_starts_at(self.rate*5)
        w.actions['seek_back'].trigger()
        self.assert_pcm_starts_at(0)
        w.actions['seek_forward'].trigger()
        w.actions['to_start'].trigger()
        self.assert_pcm_starts_at(0)

    def test_multitrack_ruler_seeks_pcm_but_drag_keeps_time_selection(self):
        w = self.window
        w.session = Session(self.rate, 2)
        w.session.import_audio([(self.audio, self.rate, 'Reference')])
        w.set_mode('multitrack')
        timeline = w.multitrack.timeline
        w.toggle_play()
        pos = QPoint(round(timeline.x_at(self.rate*7)), timeline.ruler_height//2)
        frame = timeline.frame_at(pos.x())
        QTest.mouseClick(timeline, Qt.MouseButton.LeftButton, pos=pos)
        self.assert_pcm_starts_at(frame)
        sink = w.player.sink
        a = QPoint(round(timeline.x_at(self.rate*2)), timeline.ruler_height//2)
        b = QPoint(round(timeline.x_at(self.rate*5)), timeline.ruler_height//2)
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=a)
        QTest.mouseMove(timeline, b, 20)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=b)
        self.assertTrue(w.session.selected)
        self.assertIs(w.player.sink, sink)

    def test_seek_cannot_interrupt_an_active_recording(self):
        w = self.window
        self.assertTrue(w.start_recording(rate=self.rate, channels=2, limit_seconds=1))
        take = w.recorder.take
        w.seek_playback(self.rate*3)
        self.assertTrue(w.recorder.active)
        self.assertIs(w.recorder.take, take)
        self.assertEqual(w.player.state, 'Stopped')
        self.errors.assert_not_called()
