"""Close the active waveform/session without losing another document or canceled edits."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from soundsausage.audio import read_wav
from soundsausage.document import Document
from soundsausage.project import load_project
from soundsausage.window import MainWindow


class CloseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = np.array([[.25, -.5], [.125, .375]], np.float32)
        self.window = MainWindow(Document(self.data, 8000), no_audio=True)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.session.mark_saved()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def close_shortcut(self):
        self.window.waveform.setFocus()
        QTest.keyClick(self.window.waveform, Qt.Key.Key_W, Qt.KeyboardModifier.ControlModifier)
        self.app.processEvents()

    def make_session(self):
        self.window.insert_waveform()
        self.assertEqual(self.window.mode, "multitrack")
        return self.window.session

    def test_file_menu_and_ctrl_w_close_saved_waveform_without_exiting(self):
        self.assertIn(self.window.actions["close_file"], self.window.menus["file"].actions())
        with patch("soundsausage.window.QMessageBox.question") as question:
            self.close_shortcut()
        question.assert_not_called()
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.document.frames, 0)
        self.assertIsNone(self.window.document.path)
        self.assertEqual(self.window.document.undo_stack, [])
        self.assertFalse(self.window.document.dirty)
        self.assertFalse(self.window.actions["close_file"].isEnabled())
        self.assertEqual(self.window.time_label.text(), "0:00.000")

    def test_close_clears_redo_after_undoing_audio_creation(self):
        self.window.close_current()
        self.window.edit(lambda: self.window.document.replace(0, 0, self.data, "Generate"))
        self.window.actions["undo"].trigger()
        self.assertEqual(self.window.document.frames, 0)
        self.assertTrue(self.window.document.redo_stack)
        self.assertTrue(self.window.actions["close_file"].isEnabled())
        with patch("soundsausage.window.QMessageBox.question") as question:
            self.close_shortcut()
        question.assert_not_called()
        self.assertEqual(self.window.document.redo_stack, [])
        self.assertFalse(self.window.actions["redo"].isEnabled())

    def test_cancel_preserves_edits_selection_and_clipboard(self):
        self.window.effect("invert")
        document = self.window.document
        document.select(0, 1)
        self.window.copy()
        clipboard = self.window.clipboard
        with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
            self.close_shortcut()
        self.assertIs(self.window.document, document)
        self.assertTrue(document.dirty)
        self.assertEqual(document.selection, (0, 1))
        self.assertIs(self.window.clipboard, clipboard)
        np.testing.assert_array_equal(document.read(), -self.data)

    def test_discard_closes_only_waveform_and_retains_multitrack_audio(self):
        session = self.make_session()
        before = session.render()
        self.window.set_mode("waveform")
        self.window.effect("invert")
        with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.window.close_current())
        self.assertEqual(self.window.document.frames, 0)
        self.assertIs(self.window.session, session)
        np.testing.assert_array_equal(session.render(), before)
        self.assertTrue(session.dirty)

    def test_save_then_close_writes_the_edited_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "saved.wav"
            self.window.document.path = path
            self.window.effect("invert")
            with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
                self.assertTrue(self.window.close_current())
            np.testing.assert_array_equal(read_wav(path).samples, -self.data)
            self.assertEqual(self.window.document.frames, 0)

    def test_canceling_save_or_a_write_error_keeps_waveform_open(self):
        self.window.effect("invert")
        document = self.window.document
        with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
            with patch.object(self.window, "_save_path", return_value=(None, None)):
                self.assertFalse(self.window.close_current())
            self.assertIs(self.window.document, document)
            with tempfile.TemporaryDirectory() as folder:
                document.path = Path(folder) / "cannot-write.wav"
                with patch("soundsausage.window.write_wav", side_effect=OSError("disk full")), patch.object(self.window, "error"):
                    self.assertFalse(self.window.close_current())
        self.assertIs(self.window.document, document)
        self.assertTrue(document.dirty)
        np.testing.assert_array_equal(document.read(), -self.data)

    def test_cancel_keeps_current_session_and_waveform(self):
        document = self.window.document
        session = self.make_session()
        with patch("soundsausage.session_actions.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.window.close_current())
        self.assertEqual(self.window.mode, "multitrack")
        self.assertIs(self.window.session, session)
        self.assertIs(self.window.document, document)

    def test_discarding_session_keeps_waveform_and_returns_to_waveform_view(self):
        document = self.window.document
        self.make_session()
        with patch("soundsausage.session_actions.QMessageBox.question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.window.close_current())
        self.assertEqual(self.window.mode, "waveform")
        self.assertIs(self.window.document, document)
        np.testing.assert_array_equal(document.read(), self.data)
        self.assertEqual(self.window.session.frames, 0)
        self.assertIsNone(self.window.session.path)
        self.assertFalse(self.window.session.dirty)

    def test_saving_session_before_close_preserves_project(self):
        session = self.make_session()
        expected = session.render()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "saved.celp"
            session.path = path
            with patch("soundsausage.session_actions.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
                self.assertTrue(self.window.close_current())
            reopened = load_project(path, dsp=self.window.document.dsp)
            np.testing.assert_array_equal(reopened.render(), expected)
        self.assertEqual(self.window.session.frames, 0)

    def test_canceling_session_save_or_a_write_error_keeps_session_open(self):
        session = self.make_session()
        expected = session.render()
        with patch("soundsausage.session_actions.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
            with patch("soundsausage.session_actions.QFileDialog.getSaveFileName", return_value=("", "")):
                self.assertFalse(self.window.close_current())
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "existing.celp"
                path.write_bytes(b"existing project")
                session.path = path
                with patch("soundsausage.session_actions.save_project", side_effect=OSError("disk full")), patch.object(self.window, "error"):
                    self.assertFalse(self.window.close_current())
                self.assertEqual(path.read_bytes(), b"existing project")
        self.assertEqual(self.window.mode, "multitrack")
        self.assertIs(self.window.session, session)
        self.assertTrue(session.dirty)
        np.testing.assert_array_equal(session.render(), expected)

    def test_closing_clip_copy_detaches_it_without_applying_edits(self):
        session = self.make_session()
        clip_id = session.tracks[0].clips[0].id
        session.mark_saved()
        before = session.render()
        self.window.edit_clip_copy(clip_id)
        self.window.effect("invert")
        with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.window.close_current())
        self.assertIsNone(self.window.editing_clip_id)
        self.assertFalse(self.window.actions["apply_clip"].isEnabled())
        np.testing.assert_array_equal(session.render(), before)
