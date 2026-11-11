import unittest

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialogButtonBox

from soundsausage.document import Document
from soundsausage.filters_ui import GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog
from soundsausage.window import MainWindow


class FilterGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = np.random.default_rng(7).normal(0, .1, (70000, 2)).astype(np.float32)
        self.window = MainWindow(Document(self.data, 8000), no_audio=True)
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.reject(); dialog.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater()
        self.app.processEvents()

    def dialog(self, cls):
        dialog = cls(self.window.document, self.window, no_audio=True)
        self.dialogs.append(dialog)
        dialog.show(); self.app.processEvents()
        self.assertFalse(dialog.grab().isNull())
        return dialog

    def test_menu_modes_empty_audio_and_recording_lock(self):
        keys = ("graphic_eq", "parametric_eq", "filter")
        for key in keys:
            self.assertIn(self.window.actions[key], self.window.menus["filters"].actions())
            self.assertTrue(self.window.actions[key].isEnabled())
        self.window._record_context = {}
        self.window.update_recording_actions()
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None
        self.window.refresh()
        self.window.set_mode("multitrack")
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())
        self.window.set_mode("waveform")
        self.window.document = Document()
        self.window.refresh()
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())

    def test_graphic_sliders_presets_reset_low_rate_and_preview_stop(self):
        dialog = self.dialog(GraphicEqualizerDialog)
        self.assertFalse(dialog.gains[7].isEnabled())  # 4 kHz at 8 kHz rate
        dialog.presets.setCurrentIndex(2)
        self.assertEqual(dialog.gains[0].value(), 5)
        dialog.player._set_state("Playing")
        dialog.sliders[0].setValue(-35)
        self.assertEqual(dialog.gains[0].value(), -3.5)
        self.assertEqual(dialog.player.state, "Stopped")
        self.assertEqual(dialog.presets.currentIndex(), 0)
        dialog.preset(1)
        self.assertEqual(dialog.settings()["gains"], (0,)*10)
        self.assertFalse(dialog.preview_button.isEnabled())

    def test_parametric_enables_band_controls_and_low_rate_presets(self):
        dialog = self.dialog(ParametricEqualizerDialog)
        self.assertFalse(dialog.bands[-1][0].isChecked())
        self.assertFalse(dialog.bands[0][3].isEnabled())
        band = dialog.bands[2]
        band[0].setChecked(False)
        self.assertFalse(band[1].isEnabled())
        band[0].setChecked(True); band[2].setValue(6)
        self.assertTrue(band[3].isEnabled())
        self.assertEqual(dialog.presets.currentIndex(), 0)
        dialog.presets.setCurrentIndex(2)
        self.assertTrue(np.isfinite(dialog.preview_samples()).all())
        dialog.preset(1)
        np.testing.assert_array_equal(dialog.preview_samples(), self.data[:64000])

    def test_filter_type_fields_and_fifty_hz_notch_preset(self):
        dialog = self.dialog(FilterDialog)
        self.assertFalse(dialog.q.isEnabled())
        self.assertTrue(dialog.slope.isEnabled())
        dialog.presets.setCurrentIndex(4)
        self.assertTrue(dialog.q.isEnabled())
        self.assertFalse(dialog.slope.isEnabled())
        self.assertEqual(dialog.settings()["kind"], "notch")
        self.assertEqual(dialog.settings()["frequency"], 50)
        dialog.frequency.setValue(60)
        self.assertEqual(dialog.presets.currentIndex(), 0)

    def test_all_preview_selection_prefix_matches_apply_and_cancel_is_inert(self):
        for cls in (GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog):
            doc = self.window.document
            doc.select(100, 69000)
            dialog = self.dialog(cls)
            dialog.preset(2)
            preview = dialog.preview_samples()
            self.assertEqual(preview.shape, (64000, 2))
            self.assertFalse(doc.dirty)
            doc.apply(dialog.effect_name, **dialog.settings())
            np.testing.assert_array_equal(preview, doc.read(100, 64100))
            doc.undo()
            np.testing.assert_array_equal(doc.read(), self.data)
            dialog.reject()

    def test_modal_apply_undo_and_cancel(self):
        def accept():
            dialog = self.app.activeModalWidget()
            self.assertIsInstance(dialog, GraphicEqualizerDialog)
            dialog.preset(2)
            dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept)
        self.window.actions["graphic_eq"].trigger()
        self.assertEqual(len(self.window.document.undo_stack), 1)
        self.window.document.undo()
        def cancel():
            self.app.activeModalWidget().reject()
        QTimer.singleShot(0, cancel)
        self.window.actions["filter"].trigger()
        np.testing.assert_array_equal(self.window.document.read(), self.data)
        self.assertEqual(len(self.window.document.redo_stack), 1)
