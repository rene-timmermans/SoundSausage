from pathlib import Path
import tempfile
import unittest
import numpy as np
from PySide6.QtWidgets import QApplication, QDialogButtonBox
from soundsausage.audio import write_wav
from soundsausage.document import Document
from soundsausage.window import MainWindow
from soundsausage.special_ui import DistortionDialog, ConvolutionDialog


class SpecialGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.window = MainWindow(Document(np.ones((8000, 2), np.float32)*.1, 8000), no_audio=True); self.dialogs = []
        self.folder = tempfile.TemporaryDirectory(); self.path = Path(self.folder.name)/'Response.wav'
        write_wav(self.path, np.array([[1], [.5]], np.float32), 8000, 'float32')
    def tearDown(self):
        for d in self.dialogs: d.reject(); d.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved(); self.window.close(); self.window.deleteLater(); self.app.processEvents(); self.folder.cleanup()
    def test_distortion_presets_and_mix_controls(self):
        d = DistortionDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(d)
        d.preset(4); self.assertEqual(d.settings()['kind'], 'crush'); self.assertTrue(d.bits.isEnabled())
        self.assertFalse(d.settings()['oversample']); d.preset(1); self.assertFalse(d.bits.isEnabled())
        d.show(); self.app.processEvents(); self.assertFalse(d.grab().isNull())
    def test_convolution_requires_ir_and_preview_matches_apply(self):
        d = ConvolutionDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(d)
        self.assertFalse(d.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        d.use_impulse(self.path); self.assertTrue(d.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        d.tail.setChecked(True); preview = d.preview_samples()
        self.window.document.apply(d.effect_name, **d.settings())
        np.testing.assert_array_equal(self.window.document.view(), preview)
        self.assertEqual(self.window.document.frames, 8001)
    def test_special_actions_follow_mode_and_recording_lock(self):
        for key in ('distortion', 'convolution'): self.assertIn(self.window.actions[key], self.window.menus['special'].actions())
        self.window._record_context = {}; self.window.update_recording_actions()
        for key in ('distortion', 'convolution'): self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None; self.window.refresh(); self.window.set_mode('multitrack')
        for key in ('distortion', 'convolution'): self.assertFalse(self.window.actions[key].isEnabled())
