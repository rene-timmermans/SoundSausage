"""Exercise the actual dialogs, modal actions, curve gestures and preview lifecycle."""
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox

from soundsausage.amplitude_ui import ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog
from soundsausage.document import Document
from soundsausage.window import MainWindow, AmplifyDialog


class AmplitudeGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = np.array([[.5, -.25], [-.25, .75], [.125, .25], [.375, -.125]], np.float32)
        self.window = MainWindow(Document(self.data, 8000), no_audio=True)
        self.window.show()
        self.app.processEvents()
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.reject()
            dialog.deleteLater()
        self.window.document.mark_saved()
        self.window.session.mark_saved()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def dialog(self, cls, no_audio=False):
        result = cls(self.window.document, self.window, no_audio=no_audio)
        result.show()
        self.dialogs.append(result)
        self.app.processEvents()
        return result

    def test_amplitude_menu_enables_only_supported_audio_and_modes(self):
        keys = ("amplify", "channel_mix", "dynamics", "envelope", "normalize", "fade_in", "fade_out")
        for key in keys:
            self.assertIn(self.window.actions[key], self.window.menus["amplitude"].actions())
            self.assertTrue(self.window.actions[key].isEnabled(), key)
        self.window.document = Document(self.data[:, :1], 8000)
        self.window.refresh()
        self.assertFalse(self.window.actions["channel_mix"].isEnabled())
        self.assertTrue(self.window.actions["dynamics"].isEnabled())
        self.window.set_mode("multitrack")
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled(), key)
        self.window.set_mode("waveform")
        self.window.close_current()
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled(), key)

    def test_channel_presets_sliders_invert_and_custom_values(self):
        dialog = self.dialog(ChannelMixerDialog)
        dialog.presets.setCurrentIndex(2)
        self.assertEqual(dialog.settings()["matrix"], ((0, 1), (1, 0)))
        dialog.invert[1].setChecked(True)
        self.assertEqual(dialog.settings()["matrix"], ((0, 1), (-1, 0)))
        self.assertEqual(dialog.presets.currentIndex(), 0)
        dialog.sliders[0][0].setValue(-1250)
        self.assertEqual(dialog.weights[0][0].value(), -125)
        dialog.presets.setCurrentIndex(3)
        self.assertEqual(dialog.settings()["matrix"], ((.5, .5), (.5, .5)))
        self.assertFalse(dialog.invert[1].isChecked())

    def test_preview_uses_selection_without_touching_document_or_history(self):
        document = self.window.document
        document.select(1, 3)
        dialog = self.dialog(ChannelMixerDialog)
        dialog.presets.setCurrentIndex(2)
        with patch.object(dialog.player, "play") as play:
            dialog.preview_button.click()
        np.testing.assert_array_equal(play.call_args.args[0], self.data[1:3, ::-1])
        self.assertEqual(play.call_args.args[1], 8000)
        np.testing.assert_array_equal(document.read(), self.data)
        self.assertEqual(document.selection, (1, 3))
        self.assertFalse(document.dirty)
        self.assertFalse(document.undo_stack)

    def test_preview_matches_application_and_limits_playback_to_eight_seconds(self):
        self.window.document = Document(np.ones((80010, 1), np.float32) * .25, 8000)
        dialog = self.dialog(EnvelopeDialog)
        dialog.presets.setCurrentIndex(2)
        preview = dialog.preview_samples()
        self.assertEqual(len(preview), 64000)
        self.window.document.apply("envelope", **dialog.settings())
        np.testing.assert_array_equal(preview, self.window.document.read(0, 64000))

    def test_preview_stops_on_parameter_change_and_dialog_close(self):
        dialog = self.dialog(DynamicsDialog)
        dialog.player._set_state("Playing")
        self.assertEqual(dialog.preview_button.text(), "Stop Preview")
        dialog.attack.setValue(20)
        self.assertEqual(dialog.player.state, "Stopped")
        with patch.object(dialog.player, "shutdown") as shutdown:
            dialog.reject()
        shutdown.assert_called_once()

    def test_no_audio_mode_disables_preview_and_invalid_log_curve_cannot_apply(self):
        dialog = self.dialog(EnvelopeDialog, no_audio=True)
        self.assertFalse(dialog.preview_button.isEnabled())
        dialog.presets.setCurrentIndex(2)
        dialog.logarithmic.setChecked(True)
        with patch("soundsausage.amplitude_ui.QMessageBox.information") as info:
            dialog.accept()
        info.assert_called_once()
        self.assertTrue(dialog.isVisible())

    def test_curve_mouse_and_numeric_edits_keep_order_and_endpoints(self):
        dialog = self.dialog(EnvelopeDialog)
        curve = dialog.curve
        middle = curve.point_position((50, 50)).toPoint()
        QTest.mouseClick(curve, Qt.MouseButton.LeftButton, pos=middle)
        self.assertEqual(len(curve.points), 3)
        self.assertAlmostEqual(curve.points[1][0], 50, delta=.5)
        dialog.position.setValue(70)
        dialog.level.setValue(25)
        self.assertEqual(curve.points[1], (70, 25))
        start = curve.point_position(curve.points[1]).toPoint()
        finish = curve.point_position((90, 150)).toPoint()
        QTest.mousePress(curve, Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(curve, finish)
        QTest.mouseRelease(curve, Qt.MouseButton.LeftButton, pos=finish)
        self.assertAlmostEqual(curve.points[1][0], 90, delta=.5)
        self.assertAlmostEqual(curve.points[1][1], 150, delta=1)
        QTest.keyClick(curve, Qt.Key.Key_Delete)
        self.assertEqual(len(curve.points), 2)
        self.assertEqual(curve.points[0][0], 0)
        self.assertEqual(curve.points[-1][0], 100)

    def test_dynamics_preset_curve_and_settings_match_preview_math(self):
        dialog = self.dialog(DynamicsDialog)
        dialog.presets.setCurrentIndex(2)
        self.assertEqual(dialog.curve.points, ((-96, -96), (-60, -60), (-18, -18), (0, -12)))
        preview = dialog.preview_samples()
        applied = Document(self.data, 8000)
        applied.apply("dynamics", **dialog.settings())
        np.testing.assert_array_equal(preview, applied.read())
        dialog.makeup.setValue(3)
        self.assertEqual(dialog.presets.currentIndex(), 0)

    def test_amplify_and_normalize_preview_use_their_actual_settings(self):
        amplify = self.dialog(AmplifyDialog)
        amplify.presets.setCurrentIndex(3)
        np.testing.assert_allclose(amplify.preview_samples(), self.data * np.linspace(0, 1, 4)[:, None], rtol=1e-6)
        normalize = self.dialog(NormalizeDialog)
        normalize.remove_dc.setChecked(True)
        expected = self.data - self.data.mean(axis=0)
        expected *= .98 / abs(expected).max()
        np.testing.assert_allclose(normalize.preview_samples(), expected, rtol=1e-6)

    def test_real_modal_action_accepts_once_and_cancel_preserves_undo(self):
        def accept():
            dialog = self.app.activeModalWidget()
            self.assertIsInstance(dialog, ChannelMixerDialog)
            dialog.presets.setCurrentIndex(2)
            dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept)
        self.window.actions["channel_mix"].trigger()
        np.testing.assert_array_equal(self.window.document.read(), self.data[:, ::-1])
        self.assertEqual(len(self.window.document.undo_stack), 1)
        self.window.actions["undo"].trigger()
        def cancel():
            dialog = self.app.activeModalWidget()
            dialog.presets.setCurrentIndex(3)
            dialog.reject()
        QTimer.singleShot(0, cancel)
        self.window.actions["channel_mix"].trigger()
        np.testing.assert_array_equal(self.window.document.read(), self.data)
        self.assertFalse(self.window.document.dirty)
        self.assertEqual(len(self.window.document.redo_stack), 1)
