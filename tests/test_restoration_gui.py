import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtWidgets import QApplication, QDialogButtonBox

from soundsausage.document import Document
from soundsausage.window import MainWindow
from soundsausage.restoration_ui import NoiseReductionDialog, ClickRemovalDialog


class RestorationGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = np.random.default_rng(2).normal(0, .01, (8000, 2)).astype(np.float32)
        self.window = MainWindow(Document(self.data, 8000), no_audio=True); self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs: dialog.reject(); dialog.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def dialog(self, cls):
        d = cls(self.window.document, self.window, no_audio=True); self.dialogs.append(d); d.show(); self.app.processEvents(); return d

    def test_capture_then_full_waveform_dialog_preview_and_apply(self):
        self.window.document.select(0, 2000); self.window.actions['noise_profile'].trigger()
        self.window.document.select(0, 0)
        d = self.dialog(NoiseReductionDialog)
        self.assertTrue(d.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        before = self.window.document.view(); preview = d.preview_samples()
        self.window.document.apply(d.effect_name, **d.settings())
        np.testing.assert_array_equal(preview, self.window.document.view())
        self.window.document.undo(); np.testing.assert_array_equal(before, self.window.document.view())

    def test_missing_profile_disables_apply_capture_is_non_destructive(self):
        d = self.dialog(NoiseReductionDialog)
        self.assertFalse(d.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        with patch('soundsausage.restoration_ui.QMessageBox.warning') as warning: d.capture()
        warning.assert_called_once()
        self.window.document.select(0, 2000); d.capture()
        self.assertTrue(d.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        self.assertFalse(self.window.document.dirty); self.assertFalse(self.window.document.undo_stack)
        d.preset(3); self.assertEqual(d.settings()['reduction_db'], 24)

    def test_presets_noise_only_and_click_dialog(self):
        self.window.document.select(0, 2000); self.window.capture_noise_profile()
        d = self.dialog(NoiseReductionDialog); d.residual.setChecked(True)
        self.assertTrue(d.settings()['residual']); self.assertFalse(d.preview_button.isEnabled())
        clicks = self.dialog(ClickRemovalDialog); clicks.preset(2)
        self.assertEqual(clicks.settings()['threshold_db'], -40)
        self.assertFalse(clicks.grab().isNull())

    def test_mode_and_recording_lock(self):
        keys = ('noise_profile', 'noise_reduction', 'click_removal')
        for key in keys: self.assertIn(self.window.actions[key], self.window.menus['noise'].actions())
        self.window._record_context = {}; self.window.update_recording_actions()
        for key in keys: self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None; self.window.refresh(); self.window.set_mode('multitrack')
        for key in keys: self.assertFalse(self.window.actions[key].isEnabled())
