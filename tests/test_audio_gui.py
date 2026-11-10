"""Sample-rate conversion through the modal UI and shared preview preferences."""
import unittest

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QSpinBox

from soundsausage.document import Document
from soundsausage.window import MainWindow
from soundsausage.amplitude_ui import ChannelMixerDialog


class AudioGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(Document(np.full((800, 2), .1, np.float32), 8000), no_audio=True)
        self.window.show(); self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_modal_conversion_and_undo_update_format_selection_and_view(self):
        doc = self.window.document
        doc.select(80, 400)
        self.window.refresh()
        def accept():
            dialog = self.app.activeModalWidget()
            dialog.findChild(QSpinBox).setValue(48000)
            dialog.accept()
        QTimer.singleShot(0, accept)
        self.window.actions["convert_rate"].trigger()
        self.assertEqual(doc.sample_rate, 48000)
        self.assertEqual(doc.selection, (480, 2400))
        self.assertEqual(self.window.fields["Begin"].text(), "0:00.010")
        self.assertEqual(self.window.fields["End"].text(), "0:00.050")
        self.assertIn("48000 Hz", self.window.format_label.text())
        self.window.actions["undo"].trigger()
        self.assertEqual(doc.sample_rate, 8000)
        self.assertIn("8000 Hz", self.window.format_label.text())
        self.assertEqual(doc.selection, (80, 400))
        self.window.set_mode("multitrack")
        self.assertFalse(self.window.actions["convert_rate"].isEnabled())

    def test_preview_shares_output_preferences_and_conversion_cancel_is_unchanged(self):
        dialog = ChannelMixerDialog(self.window.document, self.window, no_audio=True)
        self.assertIs(dialog.player.devices, self.window.audio_devices)
        self.assertIs(self.window.player.devices, self.window.audio_devices)
        dialog.reject(); dialog.deleteLater()
        QTimer.singleShot(0, lambda: self.app.activeModalWidget().reject())
        self.window.actions["convert_rate"].trigger()
        self.assertEqual(self.window.document.sample_rate, 8000)
        self.assertFalse(self.window.document.dirty)
