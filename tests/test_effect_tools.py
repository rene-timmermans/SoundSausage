"""Immediate command buttons and dialog groups, selection safety and preferences."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QElapsedTimer, QPoint, QSettings, Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QToolButton

from soundsausage.document import Document
from soundsausage.filters_ui import ParametricEqualizerDialog
from soundsausage.i18n import install_language, language, tr
from soundsausage.window import MainWindow


class EffectToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = str(Path(self.folder.name) / 'workspace.ini')
        self.windows = []
        self.window = self.new_window()

    def new_window(self):
        window = MainWindow(no_audio=True, ui_settings=QSettings(self.path, QSettings.Format.IniFormat))
        self.windows.append(window)
        window.restore_window_geometry()
        window.show()
        self.app.processEvents()
        return window

    def tearDown(self):
        for window in self.windows:
            window._record_context = None
            window.document.mark_saved()
            window.session.mark_saved()
            window.close()
            window.deleteLater()
        self.app.processEvents()
        self.folder.cleanup()

    def load(self, channels=2, window=None, selected=True):
        window = window or self.window
        window.document = Document(np.full((8000, channels), .2, np.float32), 8000,
                                   dsp=window.document.dsp)
        if selected:
            window.document.select(0, window.document.frames)
        window.refresh(fit=True)
        self.app.processEvents()

    def popup(self, button, key=None):
        menu = button.menu()
        observations = []
        errors = []
        def choose():
            observations.append((menu.isVisible(), menu.geometry().left(),
                                 button.mapToGlobal(QPoint(button.width(), 0)).x()))
            try:
                if key is None:
                    QTest.keyClick(menu, Qt.Key.Key_Escape)
                else:
                    action = button.choice_actions[key]
                    position = menu.actionGeometry(action).center()
                    self.assertTrue(menu.rect().contains(position))
                    # Deliver a real pointer path through QWindow. Older Qt
                    # menus reject clicks without movement since opening, and
                    # offscreen QWidget moves need not generate mouse events.
                    surface = menu.windowHandle()
                    for offset in range(8, 0, -1):
                        QTest.mouseMove(surface, position - QPoint(offset, 0))
                    self.assertIs(menu.actionAt(position), action)
                    self.assertIs(menu.activeAction(), action)
                    QTest.mouseClick(surface, Qt.MouseButton.LeftButton, pos=position)
            except Exception as error:
                errors.append(error)
            finally:
                menu.close()
        timer = QTimer(button)
        timer.setSingleShot(True)
        timer.timeout.connect(choose)
        timer.start(30)
        try:
            QTest.mouseClick(button, Qt.MouseButton.LeftButton,
                             pos=QPoint(button.width() - 4, button.height() // 2))
            # Qt versions may open menus with a nested event loop or return
            # immediately. In both cases wait for the scheduled menu action.
            elapsed = QElapsedTimer()
            elapsed.start()
            while not observations and elapsed.elapsed() < 2000:
                QTest.qWait(10)
        finally:
            timer.stop()
            menu.close()
            timer.deleteLater()
        if errors:
            raise errors[0]
        self.assertTrue(observations)
        self.assertTrue(observations[0][0])
        self.assertGreaterEqual(observations[0][1], observations[0][2] - 4)

    def test_dedicated_commands_apply_once_to_the_selected_channel_and_support_undo(self):
        self.load()
        w = self.window
        data = np.column_stack((np.linspace(-.3, .4, 8000), np.linspace(.6, -.2, 8000))).astype(np.float32)
        w.document = Document(data, 8000, dsp=w.document.dsp)
        w.document.select(1000, 3000)
        w.document.select_channels((1,))
        w.refresh(fit=True)
        for key in ('invert', 'reverse', 'silence', 'fade_in', 'fade_out'):
            with self.subTest(command=key):
                button = w.toolbar_controller.direct_buttons[key]
                self.assertIs(button.defaultAction(), w.actions[key])
                self.assertIsNone(button.menu())
                expected = data.copy()
                if key == 'invert': expected[1000:3000, 1] *= -1
                elif key == 'reverse': expected[1000:3000, 1] = data[1000:3000, 1][::-1]
                elif key == 'silence': expected[1000:3000, 1] = 0
                else:
                    ramp = np.linspace(0, 1, 2000) if key == 'fade_in' else np.linspace(1, 0, 2000)
                    expected[1000:3000, 1] *= ramp
                QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                self.assertEqual(len(w.document.undo_stack), 1)
                np.testing.assert_allclose(w.document.read(), expected, rtol=2e-7, atol=1e-7)
                np.testing.assert_array_equal(w.document.read()[:, 0], data[:, 0])
                np.testing.assert_array_equal(w.document.read()[:1000], data[:1000])
                np.testing.assert_array_equal(w.document.read()[3000:], data[3000:])
                w.actions['undo'].trigger()
                np.testing.assert_array_equal(w.document.read(), data)
        self.assertFalse(w.document.undo_stack)
        self.assertNotIn('noise_profile', w.toolbar_controller.command_buttons)
        self.assertIn(w.actions['noise_profile'], w.menus['noise'].actions())
        w.actions['noise_profile'].trigger()
        self.assertIsNotNone(w.noise_profile)
        self.assertFalse(w.document.undo_stack)
        np.testing.assert_array_equal(w.document.read(), data)

    def test_cancelled_popup_preserves_audio_and_main_icon_reopens_last_dialog(self):
        self.load()
        w = self.window
        group = w.toolbar_controller.effect_buttons['filters']
        before = w.document.read().copy()
        self.popup(group)
        self.assertEqual(group.selected_key, 'graphic_eq')
        self.assertFalse(w.document.undo_stack)
        with patch.object(w, 'amplitude_dialog') as dialog:
            self.popup(group, 'parametric_eq')
            dialog.assert_called_once_with(ParametricEqualizerDialog)
            self.assertEqual(group.selected_key, 'parametric_eq')
            dialog.reset_mock()
            QTest.mouseClick(group, Qt.MouseButton.LeftButton, pos=QPoint(10, group.height() // 2))
            dialog.assert_called_once_with(ParametricEqualizerDialog)
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertFalse(w.document.undo_stack)
        for name in ('amplitude', 'filters', 'delay', 'noise', 'time_pitch', 'special'):
            button = w.toolbar_controller.effect_buttons[name]
            self.assertIsNot(button.menu(), w.menus[name])
            for key, source in button.effects.items():
                self.assertIn(source, w.menus[name].actions())
                self.assertIsNot(button.choice_actions[key], source)
            self.assertFalse(set(button.effects) & set(w.DIRECT_EFFECT_ACTIONS))
            self.assertFalse(button.menu().actions()[-1].isSeparator())
        self.assertNotIn('wave_edits', w.toolbar_controller.effect_buttons)

    def test_no_selection_blocks_menu_direct_dialog_and_repeat_until_explicit_select_all(self):
        self.load(selected=False)
        w = self.window
        before = w.document.read().copy()
        with patch.object(w.document, 'apply', wraps=w.document.apply) as apply, \
                patch.object(ParametricEqualizerDialog, 'exec', return_value=QDialog.DialogCode.Rejected) as dialog:
            for key in w.EFFECT_ACTIONS:
                self.assertFalse(w.actions[key].isEnabled(), key)
                w.actions[key].trigger()
            w.effect('invert')
            w.amplitude_dialog(ParametricEqualizerDialog)
            w.repeat_effect()
            apply.assert_not_called()
            dialog.assert_not_called()
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertFalse(w.document.dirty)
        self.assertFalse(w.document.undo_stack)
        self.assertIn('Ctrl+A', w.statusBar().currentMessage())
        group = w.toolbar_controller.effect_buttons['amplitude']
        self.assertFalse(group.isEnabled())
        group.choose('normalize')
        group.run()
        w.toolbar_controller.direct_buttons['invert'].click()
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertFalse(w.document.undo_stack)
        w.waveform.setFocus()
        QTest.keyClick(w.waveform, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(w.document.selection, (0, w.document.frames))
        w.actions['invert'].trigger()
        np.testing.assert_array_equal(w.document.read(), -before)
        self.assertEqual(len(w.document.undo_stack), 1)
        w.document.select(2000, 2000)
        w.selection_changed(*w.document.selection)
        self.assertFalse(w.actions['repeat'].isEnabled())
        QTest.keyClick(w.waveform, Qt.Key.Key_F2)
        w.repeat_effect()
        w.effect('invert')
        self.assertEqual(len(w.document.undo_stack), 1)
        np.testing.assert_array_equal(w.document.read(), -before)
        QTest.keyClick(w.waveform, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(w.waveform, Qt.Key.Key_F2)
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertEqual(len(w.document.undo_stack), 2)

    def test_dialog_choices_open_once_without_committing_and_top_menu_executes_once(self):
        self.load()
        w = self.window
        w.document.select(1000, 3000)
        w.document.select_channels((1,))
        w.selection_changed(*w.document.selection)
        before = w.document.read().copy()
        executed = []
        for key in w.EFFECT_ACTIONS:
            w.actions[key].triggered.connect(lambda checked=False, key=key: executed.append(key))
        chosen = []
        with patch('soundsausage.window.QDialog.exec', return_value=QDialog.DialogCode.Rejected) as dialogs:
            for group in w.toolbar_controller.effect_buttons.values():
                for key in group.effects:
                    self.assertNotIn(key, w.DIRECT_EFFECT_ACTIONS)
                    count = dialogs.call_count
                    self.popup(group, key)
                    chosen.append(key)
                    self.assertEqual(group.current_key, key)
                    self.assertTrue(group.choice_actions[key].isChecked())
                    self.assertEqual(dialogs.call_count, count + 1)
                    self.assertEqual(executed, chosen)
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertFalse(w.document.undo_stack)
        w.actions['invert'].trigger()
        expected = before.copy()
        expected[1000:3000, 1] *= -1
        np.testing.assert_array_equal(w.document.read(), expected)
        self.assertEqual(executed, chosen + ['invert'])
        self.assertEqual(len(w.document.undo_stack), 1)

    def test_unavailable_choices_use_enabled_fallback_and_recording_and_modes_stay_safe(self):
        w = self.window
        groups = w.toolbar_controller.effect_buttons
        self.assertTrue(all(not button.isEnabled() for button in groups.values()))
        self.load()
        group = groups['amplitude']
        group.remember('channel_mix')
        self.assertEqual(group.current_key, 'channel_mix')
        self.load(channels=1)
        self.assertTrue(group.isEnabled())
        self.assertEqual(group.selected_key, 'channel_mix')
        self.assertEqual(group.current_key, 'amplify')
        self.assertFalse(w.actions['channel_mix'].isEnabled())
        self.load()
        self.assertEqual(group.current_key, 'channel_mix')
        before = w.document.read().copy()
        w._record_context = {}
        w.update_recording_actions()
        self.assertTrue(all(not button.isEnabled() for button in groups.values()))
        group.run()
        self.assertFalse(w.document.undo_stack)
        np.testing.assert_array_equal(w.document.read(), before)
        w._record_context = None
        w.refresh()
        self.assertTrue(group.isEnabled())
        w.set_mode('multitrack')
        self.assertTrue(all(not action.isVisible() for action in w.toolbar_controller.effect_widgets))
        self.assertTrue(w.toolbar_controller.track_effects_action.isVisible())
        self.assertTrue(w.actions['track_fx'].isEnabled())
        w.set_mode('waveform')
        self.assertTrue(all(action.isVisible() for action in w.toolbar_controller.effect_widgets))
        self.assertTrue(group.isEnabled())

    def test_last_choices_and_layout_survive_restart_and_bad_preferences_are_ignored(self):
        w = self.window
        c = w.toolbar_controller
        c.effect_buttons['delay'].remember('echo')
        w.addToolBar(Qt.ToolBarArea.RightToolBarArea, c.tools)
        c.general.toggleViewAction().trigger()
        w.close()
        second = self.new_window()
        restored = second.toolbar_controller
        self.assertEqual(second.toolBarArea(restored.tools), Qt.ToolBarArea.RightToolBarArea)
        self.assertFalse(restored.general.isVisible())
        self.assertEqual(restored.effect_buttons['delay'].selected_key, 'echo')
        self.load(window=second)
        self.assertEqual(restored.effect_buttons['delay'].current_key, 'echo')
        restored.effect_buttons['delay'].remember('reverb')
        with patch.object(second, '_confirm_discard', return_value=False):
            self.assertFalse(second.close())
        self.assertEqual(second.ui_settings.value('ui/effect_tools/delay'), 'echo')
        for invalid in ('missing_effect', 'normalize', ['echo']):
            second.ui_settings.setValue('ui/effect_tools/delay', invalid)
            restored.effect_buttons['delay'].restore()
            self.assertEqual(restored.effect_buttons['delay'].selected_key, 'delay')
        for group, old_key in (('amplitude', 'fade_in'), ('noise', 'noise_profile')):
            second.ui_settings.setValue('ui/effect_tools/' + group, old_key)
            restored.effect_buttons[group].restore()
            self.assertEqual(restored.effect_buttons[group].selected_key, restored.effect_buttons[group].default_key)

    def test_last_effect_tracks_live_language_palette_labels_and_source_action_changes(self):
        self.load()
        w = self.window
        button = w.toolbar_controller.effect_buttons['delay']
        button.remember('echo')
        manager, previous_language, previous_palette = install_language(), language(), QPalette(self.app.palette())
        try:
            for code in ('nl', 'en', 'de', 'fr', 'es'):
                manager.set_language(code, persist=False)
                self.assertIn(tr('Delay Effects'), button.toolTip())
                self.assertEqual(button.text(), w.actions['echo'].text().replace('&', ''))
                self.assertIn(button.text(), button.accessibleName())
            palette = QPalette(previous_palette)
            palette.setColor(QPalette.ColorRole.Accent, QColor('#c165d5'))
            self.app.setPalette(palette)
            w.actions['delay'].setEnabled(False)
            w.actions['delay'].setEnabled(True)
            self.assertEqual(button.icon().cacheKey(), w.actions['echo'].icon().cacheKey())
            self.assertNotEqual(button.icon().cacheKey(), w.actions['delay'].icon().cacheKey())
            self.assertFalse(any(b is button for _, b in w._action_buttons))
            w.actions['toolbar_labels'].setChecked(True)
            self.assertEqual(button.toolButtonStyle(), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            w.actions['toolbar_labels'].setChecked(False)
            self.assertEqual(button.toolButtonStyle(), Qt.ToolButtonStyle.ToolButtonIconOnly)
        finally:
            manager.set_language(previous_language, persist=False)
            self.app.setPalette(previous_palette)
