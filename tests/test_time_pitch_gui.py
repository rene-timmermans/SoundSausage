import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication
from soundsausage.document import Document
from soundsausage.window import MainWindow
from soundsausage.time_pitch_ui import StretchDialog, PitchShiftDialog


class TimePitchGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.window = MainWindow(Document(np.zeros((16000, 2), np.float32), 16000), no_audio=True); self.dialogs = []
    def tearDown(self):
        for d in self.dialogs: d.reject(); d.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved(); self.window.close(); self.window.deleteLater(); self.app.processEvents()
    def test_tempo_calculation_and_pitch_options(self):
        d = StretchDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(d)
        d.set_tempo(); self.assertEqual(d.settings()['time_ratio'], 1.2)
        d.original_bpm.setValue(400); d.target_bpm.setValue(20)
        with patch('soundsausage.time_pitch_ui.QMessageBox.information') as info: d.set_tempo()
        info.assert_called_once(); self.assertEqual(d.settings()['time_ratio'], 1.2)
        p = PitchShiftDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(p)
        p.semitones.setValue(12); self.assertTrue(p.settings()['preserve_formants'])
        self.assertEqual(p.preview_samples().shape, (16000, 2)); self.assertFalse(p.preview_button.isEnabled())
    def test_modes_and_recording_lock(self):
        for key in ('stretch', 'pitch_shift'): self.assertIn(self.window.actions[key], self.window.menus['time_pitch'].actions())
        self.window._record_context = {}; self.window.update_recording_actions()
        for key in ('stretch', 'pitch_shift'): self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None; self.window.refresh(); self.window.set_mode('multitrack')
        for key in ('stretch', 'pitch_shift'): self.assertFalse(self.window.actions[key].isEnabled())
