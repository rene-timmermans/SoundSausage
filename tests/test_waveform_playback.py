"""Large playback views must reuse their scene without stalling audio delivery."""
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.document import Document
from soundsausage.waveform import Waveform, _peak_data
from soundsausage.window import MainWindow


class WaveformPlaybackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        values = .7*np.sin(np.arange(100000)*.13)
        self.document = Document(np.column_stack((values, -values)).astype(np.float32), 44100)
        self.wave = Waveform(self.document)
        self.wave.resize(1920, 900)
        self.wave.show()
        self.app.processEvents()

    def tearDown(self):
        self.wave.close()
        self.wave.deleteLater()
        self.app.processEvents()

    def wait_for(self, condition):
        deadline = time.monotonic()+5
        while not condition() and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertTrue(condition())

    def test_cursor_updates_reuse_scene_and_erase_previous_cursor(self):
        wave = self.wave
        wave.playhead = 12000
        with patch.object(wave, '_paint_scene', wraps=wave._paint_scene) as paint:
            original = wave.grab().toImage()
            wave.playhead = 55000
            second = wave.grab().toImage()
            wave.playhead = 12000
            restored = wave.grab().toImage()
            self.assertEqual(original, restored)
            self.assertNotEqual(original, second)
            self.assertEqual(paint.call_count, 0)
        self.assertEqual(self.document.cursor, 0)

    def test_audio_edits_selection_and_live_palette_invalidate_scene(self):
        wave = self.wave
        original = wave.grab().toImage()
        self.document.select(10000, 70000)
        self.document.select_channels((1,))
        selected = wave.grab().toImage()
        self.assertNotEqual(original, selected)
        self.document.apply("silence")
        edited = wave.grab().toImage()
        self.assertNotEqual(selected, edited)
        self.document.undo()
        self.assertEqual(selected, wave.grab().toImage())
        old_palette = QPalette(self.app.palette())
        try:
            palette = QPalette(old_palette)
            palette.setColor(QPalette.ColorRole.Highlight, QColor('#ea52a5'))
            palette.setColor(QPalette.ColorRole.Accent, QColor('#ea52a5'))
            self.app.setPalette(palette)
            self.assertNotEqual(selected, wave.grab().toImage())
        finally:
            self.app.setPalette(old_palette)

    def test_resize_prepares_peaks_away_from_gui_and_discards_stale_result(self):
        wave = self.wave
        wave.playhead = 2000
        gate, started = threading.Event(), threading.Event()
        threads = []
        main_thread = threading.get_ident()
        def delayed(*args):
            threads.append(threading.get_ident())
            started.set()
            if not gate.wait(5):
                raise RuntimeError('Test peak gate timed out')
            return _peak_data(*args)
        with patch('soundsausage.waveform._peak_data', side_effect=delayed):
            try:
                wave.resize(3840, 1800)
                wave.grab()
                self.app.processEvents()
                self.assertTrue(started.wait(2))
                # More viewport changes must not queue one background job per frame.
                pending = wave._peak_job
                replacement = Document(np.full((18000, 1), .22, np.float32), 48000)
                wave.set_document(replacement)
                wave.playhead = 1000
                wave.resize(1510, 800)
                wave.grab()
                wave.resize(1710, 840)
                wave.grab()
                self.assertIs(wave._peak_job, pending)
                self.assertEqual(len(threads), 1)
            finally:
                gate.set()
            self.wait_for(lambda: wave._cache is not None and
                          wave._cache[0] == wave._peak_key(int(wave.plot_rect().width())))
        self.assertEqual(len(threads), 2)
        self.assertNotIn(main_thread, threads)
        low, high, envelope = wave._cache[1]
        self.assertTrue(envelope)
        np.testing.assert_array_equal(low, np.float32(.22))
        np.testing.assert_array_equal(high, np.float32(.22))
        self.assertEqual(low.shape[1], 1)

    def test_peak_failure_does_not_retry_without_a_changed_view(self):
        wave = self.wave
        wave.playhead = 1000
        with patch('soundsausage.waveform._peak_data', side_effect=OSError('fixture unavailable')) as prepare:
            with self.assertLogs('soundsausage.waveform', level='ERROR'):
                wave.resize(2000, 1000)
                wave.grab()
                self.wait_for(lambda: wave._peak_error is not None)
            for frame in range(20):
                wave.playhead = frame*100
                wave.grab()
                self.app.processEvents()
            self.assertEqual(prepare.call_count, 1)

    def test_empty_document_has_uniform_workspace_after_playback_and_resize(self):
        self.wave.playhead = 1000
        self.wave.grab()
        self.wave.set_document(Document())
        self.wave.resize(2000, 1000)
        image = self.wave.grab().toImage()
        color = image.pixelColor(1, 1)
        self.assertTrue(all(image.pixelColor(x, y) == color
                            for x in range(0, image.width(), 79)
                            for y in range(0, image.height(), 57)))

    def test_display_throttling_preserves_exact_model_clock_and_pause_position(self):
        window = MainWindow(self.document, no_audio=True)
        try:
            window.player.state = 'Playing'
            with patch('soundsausage.window.time.monotonic', return_value=123.):
                window.playback_position(1000)
                window.playback_position(1001)
                self.assertEqual(self.document.cursor, 1001)
                self.assertEqual(window.waveform.playhead, 1000)
            window.playback_state('Paused')
            self.assertEqual(window.waveform.playhead, 1001)
            self.assertEqual(window.time_label.text(), '0:00.023')
        finally:
            window.player.state = 'Stopped'
            self.document.mark_saved()
            window.session.mark_saved()
            window.close()
            window.deleteLater()
            self.app.processEvents()
