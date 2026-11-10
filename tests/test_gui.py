import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from soundsausage.audio import read_wav
from soundsausage.document import Document
from soundsausage.playback import Playback
from soundsausage.spectrum import SpectrumPlot
from soundsausage.window import MainWindow


ROOT = Path(__file__).resolve().parents[1]


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")

    def setUp(self):
        values = np.sin(2 * np.pi * 1000 * np.arange(800) / 8000).astype(np.float32) * 0.5
        self.samples = np.column_stack((values, -values))
        self.window = MainWindow(Document(self.samples, 8000), no_audio=True)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.close()
        self.app.processEvents()

    def test_mouse_selection_and_keyboard_cut_undo(self):
        wave = self.window.waveform
        rect = wave.plot_rect()
        begin = QPoint(round(rect.left() + rect.width() * 0.25), round(rect.center().y()))
        end = QPoint(round(rect.left() + rect.width() * 0.75), round(rect.center().y()))
        QTest.mousePress(wave, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(wave, end, 10)
        QTest.mouseRelease(wave, Qt.MouseButton.LeftButton, pos=end)
        self.assertTrue(self.window.document.selected)
        self.assertTrue(self.window.actions["cut"].isEnabled())
        expected_length = self.window.document.selection[1] - self.window.document.selection[0]
        QTest.keyClick(wave, Qt.Key.Key_X, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.window.document.frames, len(self.samples) - expected_length)
        QTest.keyClick(wave, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        np.testing.assert_array_equal(self.window.document.read(), self.samples)

    def test_save_from_the_window_reopens_with_the_edited_samples(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "edited.wav"
            self.window.document.path = path
            self.window.document.select(100, 200)
            self.window.effect("invert")
            expected = self.samples.copy()
            expected[100:200] *= -1
            self.assertTrue(self.window.save())
            self.assertFalse(self.window.document.dirty)
            np.testing.assert_allclose(read_wav(path).samples, expected, atol=1 / 32768)

    def test_failed_save_leaves_the_document_unsaved(self):
        self.window.document.path = ROOT / "build/unwritten.wav"
        self.window.effect("invert")
        with patch("soundsausage.window.write_wav", side_effect=OSError("disk full")), patch.object(self.window, "error"):
            self.assertFalse(self.window.save())
        self.assertTrue(self.window.document.dirty)

    def test_metadata_is_not_removed_without_the_users_choice(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "with-cues.wav"
            path.write_bytes(b"original data and metadata")
            self.window.document.path = path
            self.window.document.extra_chunks = ("cue ", "LIST")
            self.window.effect("invert")
            with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.No):
                self.assertFalse(self.window.save())
            self.assertEqual(path.read_bytes(), b"original data and metadata")
            self.assertTrue(self.window.document.dirty)

    def test_redo_and_zoom_shortcuts_do_not_conflict(self):
        shortcuts = [a.shortcut().toString() for a in self.window.actions.values() if not a.shortcut().isEmpty()]
        self.assertEqual(len(shortcuts), len(set(shortcuts)))

    def test_zoom_and_scroll_change_the_visible_range(self):
        self.window.document.select(200, 400)
        self.window.waveform.zoom_selection()
        self.assertEqual((self.window.waveform.view_start, self.window.waveform.view_end), (200, 400))
        self.window.scroll.setValue(300)
        self.assertEqual((self.window.waveform.view_start, self.window.waveform.view_end), (300, 500))

    def test_spectrum_detects_a_known_tone(self):
        t = np.arange(8000) / 8000
        data = np.sin(2 * np.pi * 1000 * t).astype(np.float32)[:, None]
        plot = SpectrumPlot(data, 8000)
        self.assertAlmostEqual(plot.peak_frequency, 1000)
        self.assertAlmostEqual(plot.peak_db, 0, places=2)

    def test_spectrum_does_not_cancel_opposite_phase_stereo(self):
        t = np.arange(8000) / 8000
        channel = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        plot = SpectrumPlot(np.column_stack((channel, -channel)), 8000)
        self.assertAlmostEqual(plot.peak_frequency, 1000)
        self.assertAlmostEqual(plot.peak_db, 0, places=2)



if __name__ == "__main__":
    unittest.main()
