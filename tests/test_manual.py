"""Help-menu access, offline content, nonmodal use, search and bundled-path smoke tests."""
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.manual import ManualDialog, manual_path
from soundsausage.window import MainWindow


class ManualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(no_audio=True)
        self.window.show(); self.app.processEvents()

    def tearDown(self):
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_f1_opens_one_nonmodal_manual_with_the_current_features(self):
        self.window.waveform.setFocus()
        QTest.keyClick(self.window.waveform, Qt.Key.Key_F1)
        self.app.processEvents()
        dialog = self.window._manual_dialog
        self.assertIsInstance(dialog, ManualDialog)
        self.assertTrue(dialog.isVisible())
        self.assertFalse(dialog.isModal())
        self.assertTrue(self.window.isEnabled())
        text = dialog.browser.toPlainText()
        for phrase in ("Amplify / Fade", "Channel Mixer", "Dynamics Processing", "Envelope", "Normalize", "Mix Paste", "Frequency Analysis", "Audio Hardware", "Convert Sample Rate", "Volume Line", "Pan Line"):
            self.assertIn(phrase, text)
        self.assertTrue(manual_path().is_file())
        self.window.open_manual()
        self.assertIs(dialog, self.window._manual_dialog)
        dialog.close(); self.window.open_manual()
        self.assertIs(dialog, self.window._manual_dialog)
        self.window.close()
        self.assertFalse(dialog.isVisible())

    def test_search_finds_wraps_and_reports_missing_terms_without_closing(self):
        self.window.open_manual()
        dialog = self.window._manual_dialog
        dialog.browser.moveCursor(QTextCursor.MoveOperation.End)
        dialog.search.setText("Normalize")
        QTest.keyClick(dialog.search, Qt.Key.Key_Return)
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.browser.textCursor().selectedText().casefold(), "normalize")
        dialog.find(True)
        self.assertEqual(dialog.browser.textCursor().selectedText().casefold(), "normalize")
        dialog.search.setText("zzzonderzoekresultaat")
        dialog.find()
        self.assertIn("Not found", dialog.search_status.text())

    def test_only_explicit_web_links_open_a_browser(self):
        self.window.open_manual()
        dialog = self.window._manual_dialog
        with patch("soundsausage.manual.QDesktopServices.openUrl") as open_url:
            dialog.open_link(QUrl("file:///tmp/not-a-manual"))
            dialog.open_link(QUrl("#samplerates"))
            open_url.assert_not_called()
            dialog.open_link(QUrl("https://github.com/rene-timmermans/SoundSausage"))
            open_url.assert_called_once()
