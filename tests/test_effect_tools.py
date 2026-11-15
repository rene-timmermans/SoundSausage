"""Shared effect flyouts, single execution, settings, state and live UI changes."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QElapsedTimer, QPoint, QSettings, Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolButton

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

    def load(self, channels=2, window=None):
        window = window or self.window
        window.document = Document(np.full((8000, channels), .2, np.float32), 8000,
                                   dsp=window.document.dsp)
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
                    QTest.mouseClick(menu, Qt.MouseButton.LeftButton,
                                     pos=menu.actionGeometry(self.window.actions[key]).center())
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

    def test_arrow_uses_shared_menu_and_effect_choice_and_main_click_each_apply_once(self):
        self.load()
        w = self.window
        group = w.toolbar_controller.effect_buttons['amplitude']
        self.assertIs(group.menu(), w.menus['amplitude'])
        self.assertEqual(group.popupMode(), QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.assertGreaterEqual(group.width(), group.iconSize().width() + 14)
        w.document.select(1000, 3000)
        w.document.select_channels((1,))
        before = w.document.read().copy()
        self.popup(group, 'fade_in')
        self.assertEqual(group.selected_key, 'fade_in')
        self.assertEqual(len(w.document.undo_stack), 1)
        after = w.document.read()
        np.testing.assert_array_equal(after[:, 0], before[:, 0])
        np.testing.assert_array_equal(after[:1000], before[:1000])
        np.testing.assert_array_equal(after[3000:], before[3000:])
        self.assertEqual(float(after[1000, 1]), 0.0)
        w.actions['undo'].trigger()
        np.testing.assert_array_equal(w.document.read(), before)
        QTest.mouseClick(group, Qt.MouseButton.LeftButton, pos=QPoint(10, group.height() // 2))
        self.assertEqual(len(w.document.undo_stack), 1)
        np.testing.assert_array_equal(w.document.read(), after)

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
            self.assertIs(w.toolbar_controller.effect_buttons[name].menu(), w.menus[name])
        for key in ('invert', 'reverse', 'silence'):
            self.assertIn(w.actions[key], w.toolbar_controller.effect_buttons['wave_edits'].menu().actions())

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
        c.options.toggleViewAction().trigger()
        w.close()
        second = self.new_window()
        restored = second.toolbar_controller
        self.assertEqual(second.toolBarArea(restored.tools), Qt.ToolBarArea.RightToolBarArea)
        self.assertFalse(restored.options.isVisible())
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
