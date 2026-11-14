import unittest

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialogButtonBox

from soundsausage.document import Document
from soundsausage.space_ui import DelayDialog, EchoDialog, ReverbDialog
from soundsausage.window import MainWindow


class SpaceGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.source = np.random.default_rng(7).normal(0, .1, (6000, 2)).astype(np.float32)
        self.window = MainWindow(Document(self.source, 8000), no_audio=True)
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.reject(); dialog.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater()
        self.app.processEvents()

    def dialog(self, cls, no_audio=True):
        result = cls(self.window.document, self.window, no_audio=no_audio)
        result.show(); self.dialogs.append(result); self.app.processEvents()
        self.assertFalse(result.grab().isNull())
        return result

    def test_menu_audio_modes_and_recording_lock(self):
        keys = ("delay", "echo", "reverb")
        for key in keys:
            self.assertIn(self.window.actions[key], self.window.menus["delay"].actions())
            self.assertTrue(self.window.actions[key].isEnabled())
        self.window._record_context = {}; self.window.update_recording_actions()
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None; self.window.refresh()
        self.window.set_mode("multitrack")
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())
        self.window.set_mode("waveform"); self.window.document = Document(); self.window.refresh()
        for key in keys:
            self.assertFalse(self.window.actions[key].isEnabled())

    def test_delay_presets_independent_times_and_reset(self):
        dialog = self.dialog(DelayDialog)
        self.assertFalse(dialog.right_delay.isEnabled())
        dialog.presets.setCurrentIndex(4)
        self.assertTrue(dialog.right_delay.isEnabled())
        self.assertEqual(dialog.settings()["right_delay_ms"], 35)
        dialog.delay.setValue(40)
        self.assertEqual(dialog.presets.currentIndex(), 0)
        dialog.preset(1)
        self.assertIsNone(dialog.settings()["right_delay_ms"])
        self.assertFalse(dialog.keep_tail.isChecked())
        self.assertFalse(dialog.preview_button.isEnabled())

    def test_echo_feedback_pingpong_and_tail_hint(self):
        dialog = self.dialog(EchoDialog)
        dialog.presets.setCurrentIndex(3)
        self.assertTrue(dialog.settings()["ping_pong"])
        dialog.feedback.setValue(95); dialog.delay.setValue(2000)
        self.assertGreater(dialog.suggested_tail(), 60)
        self.assertIn("Suggested tail", dialog.hint.text())
        self.assertEqual(dialog.settings()["tail_seconds"], 0)
        dialog.automatic_tail.setChecked(False); dialog.keep_tail.setChecked(True); dialog.tail.setValue(60)
        self.assertEqual(dialog.settings()["tail_seconds"], 60)

    def test_automatic_tail_controls_and_manual_extended_limit(self):
        dialog = self.dialog(EchoDialog)
        dialog.keep_tail.setChecked(True)
        self.assertTrue(dialog.settings()['auto_tail']); self.assertFalse(dialog.tail.isEnabled())
        preview = dialog.preview_samples()
        self.window.document.apply('echo', **dialog.settings())
        np.testing.assert_array_equal(self.window.document.view()[:len(preview)], preview)
        self.window.document.undo()
        dialog.automatic_tail.setChecked(False); dialog.tail.setValue(120)
        self.assertTrue(dialog.tail.isEnabled()); self.assertFalse(dialog.settings()['auto_tail'])
        self.assertEqual(dialog.settings()['tail_seconds'], 120)

    def test_reverb_preset_fields_and_mono_controls(self):
        dialog = self.dialog(ReverbDialog)
        dialog.presets.setCurrentIndex(3)
        self.assertEqual(dialog.settings()["decay_seconds"], 3)
        self.assertEqual(dialog.settings()["room_size"], 85)
        dialog.preset(1)
        self.assertEqual(dialog.settings()["decay_seconds"], .6)
        self.window.document = Document(self.source[:, :1], 8000)
        mono = self.dialog(ReverbDialog)
        self.assertFalse(mono.width.isEnabled())
        echo = self.dialog(EchoDialog)
        self.assertFalse(echo.ping_pong.isVisible())
        self.assertFalse(echo.presets.model().item(3).isEnabled())

    def test_tail_preview_and_apply_use_same_selection_with_one_undo(self):
        for cls in (DelayDialog, EchoDialog, ReverbDialog):
            doc = self.window.document
            doc.select(500, 5500)
            dialog = self.dialog(cls)
            dialog.automatic_tail.setChecked(False); dialog.keep_tail.setChecked(True); dialog.tail.setValue(.1)
            self.assertTrue(dialog.tail.isEnabled())
            preview = dialog.preview_samples()
            self.assertEqual(preview.shape, (5800, 2))
            np.testing.assert_array_equal(doc.read(), self.source)
            self.assertFalse(doc.dirty)
            doc.apply(dialog.effect_name, **dialog.settings())
            self.assertEqual(len(doc.undo_stack), 1)
            self.assertEqual(doc.frames, 6800)
            np.testing.assert_array_equal(preview, doc.read(500, 6300))
            doc.undo(); np.testing.assert_array_equal(doc.read(), self.source)
            doc.redo(); self.assertEqual(doc.frames, 6800); doc.undo()

    def test_parameter_and_tail_changes_stop_preview(self):
        for cls in (DelayDialog, EchoDialog, ReverbDialog):
            dialog = self.dialog(cls, no_audio=False)
            dialog.player._set_state("Playing")
            dialog.keep_tail.setChecked(True)
            self.assertEqual(dialog.player.state, "Stopped")
            dialog.player._set_state("Playing")
            dialog.wet.setValue(50)
            self.assertEqual(dialog.player.state, "Stopped")

    def test_modal_tail_apply_and_cancel(self):
        def accept():
            dialog = self.app.activeModalWidget()
            self.assertIsInstance(dialog, EchoDialog)
            dialog.automatic_tail.setChecked(False); dialog.keep_tail.setChecked(True); dialog.tail.setValue(.1)
            dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept)
        self.window.actions["echo"].trigger()
        self.assertEqual(self.window.document.frames, 6800)
        self.window.actions["undo"].trigger()
        def cancel():
            dialog = self.app.activeModalWidget()
            dialog.keep_tail.setChecked(True); dialog.reject()
        QTimer.singleShot(0, cancel)
        self.window.actions["reverb"].trigger()
        np.testing.assert_array_equal(self.window.document.read(), self.source)
        self.assertEqual(len(self.window.document.redo_stack), 1)

    def test_clip_copy_tail_extends_only_that_clip_and_session_undo_restores_it(self):
        window = self.window
        first = window.session.import_audio([(self.source, 8000, 'First')])[0]
        second = window.session.import_audio([(self.source, 8000, 'Next')], start=48000)[0]
        original_start = window.session.find_clip(second)[1].start
        original_frames = window.session.find_clip(first)[1].frames
        window.document.mark_saved()
        window.edit_clip_copy(first)
        window.document.apply('reverb', tail_seconds=.1)
        window.apply_waveform_to_clip()
        self.assertEqual(window.mode, 'multitrack')
        self.assertEqual(window.session.find_clip(first)[1].frames, original_frames+round(.1*window.session.sample_rate))
        self.assertEqual(window.session.find_clip(second)[1].start, original_start)
        window.session.undo()
        self.assertEqual(window.session.find_clip(first)[1].frames, original_frames)
