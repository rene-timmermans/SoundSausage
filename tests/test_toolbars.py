"""Workspace tools, menu visibility and native toolbar layout persistence."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolButton

from soundsausage.document import Document
from soundsausage.i18n import install_language, language as current_language
from soundsausage.window import MainWindow


class ToolbarTests(unittest.TestCase):
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
            window.document.mark_saved()
            window.session.mark_saved()
            window.close()
            window.deleteLater()
        self.app.processEvents()
        self.folder.cleanup()

    def load(self):
        self.window.document = Document(np.full((8000, 2), .2, np.float32), 8000,
                                        dsp=self.window.document.dsp)
        self.window.refresh(fit=True)
        self.app.processEvents()

    def test_three_movable_bars_have_native_handles_and_no_duplicate_zoom_group(self):
        w = self.window
        c = w.toolbar_controller
        self.assertEqual(len(c.bars), 3)
        self.assertEqual(w.toolBarArea(c.general), Qt.ToolBarArea.TopToolBarArea)
        self.assertEqual(w.toolBarArea(c.options), Qt.ToolBarArea.TopToolBarArea)
        self.assertLess(c.general.geometry().y(), c.options.geometry().y())
        self.assertEqual(w.toolBarArea(c.tools), Qt.ToolBarArea.LeftToolBarArea)
        self.assertEqual(c.tools.orientation(), Qt.Orientation.Vertical)
        for bar in c.bars.values():
            self.assertTrue(bar.isMovable())
            self.assertTrue(bar.isFloatable())
            self.assertTrue(bar.objectName())
            self.assertIn(bar.toggleViewAction(), w.menus['toolbars'].actions())
            for button in bar.findChildren(QToolButton):
                self.assertNotIn(button.defaultAction(), [w.actions[k] for k in
                    ('zoom_in', 'zoom_out', 'zoom_full', 'zoom_selection')])
        self.load()
        w.document.select(1000, 3000)
        w.selection_changed(1000, 3000)
        for key in ('zoom_in', 'zoom_out', 'zoom_full', 'zoom_selection'):
            self.assertIn(w.actions[key], w.menus['view'].actions())
            self.assertTrue(any(b.defaultAction() is w.actions[key]
                                for b in w.transport.findChildren(QToolButton)))
        w.actions['zoom_selection'].trigger()
        self.assertEqual((w.waveform.view_start, w.waveform.view_end), (1000, 3000))

    def test_waveform_tools_and_context_follow_clicks_shortcuts_and_channel_changes(self):
        w = self.window
        c = w.toolbar_controller
        self.load()
        before = w.document.read().copy()
        self.assertTrue(w.actions['select_wave'].isChecked())
        QTest.mouseClick(c.tools.widgetForAction(w.actions['draw_waveform']), Qt.MouseButton.LeftButton)
        self.assertTrue(w.waveform.drawing)
        self.assertFalse(w.actions['select_wave'].isChecked())
        self.assertTrue(c.option_groups['draw'].isVisible())
        self.assertFalse(c.option_groups['select'].isVisible())
        w.waveform.setFocus()
        QTest.keyClick(w.waveform, Qt.Key.Key_D)
        self.assertFalse(w.waveform.drawing)
        self.assertTrue(w.actions['select_wave'].isChecked())
        w.actions['draw_waveform'].trigger()
        QTest.mouseClick(c.tools.widgetForAction(w.actions['select_wave']), Qt.MouseButton.LeftButton)
        self.assertFalse(w.waveform.drawing)
        QTest.mouseClick(c.tools.widgetForAction(w.actions['select_wave']), Qt.MouseButton.LeftButton)
        self.assertTrue(w.actions['select_wave'].isChecked())
        w.channel_choice.setCurrentIndex(2)
        self.assertEqual(w.document.selected_channels, (1,))
        self.assertTrue(w.actions['channels_right'].isChecked())
        np.testing.assert_array_equal(w.document.read(), before)
        self.assertFalse(w.document.undo_stack)

    def test_multitrack_tools_and_options_keep_existing_editing_and_undo(self):
        w = self.window
        self.load()
        w.insert_waveform()
        c = w.toolbar_controller
        clip_id = w.session.selected_clip
        self.assertFalse(w.actions['draw_waveform'].isVisible())
        self.assertTrue(w.actions['move_clips'].isChecked())
        self.assertTrue(c.option_groups['clip'].isVisible())
        self.assertFalse(c.wave_options_action.isVisible())
        for mode, key in (('volume', 'volume_line'), ('pan', 'pan_line'), ('move', 'move_clips')):
            QTest.mouseClick(c.tools.widgetForAction(w.actions[key]), Qt.MouseButton.LeftButton)
            self.assertEqual(w.multitrack.timeline.envelope_mode, mode)
            self.assertTrue(w.actions[key].isChecked())
        w.multitrack.set_envelope_mode('volume')
        self.assertTrue(w.actions['volume_line'].isChecked())
        w.session.set_envelope(clip_id, 'volume', ((0, .5), (7999, 1.0)))
        w.refresh()
        self.assertTrue(w.multitrack.reset_line.isEnabled())
        QTest.mouseClick(w.multitrack.reset_line, Qt.MouseButton.LeftButton)
        self.assertFalse(w.session.find_clip(clip_id)[1].volume_envelope)
        w.actions['undo'].trigger()
        self.assertTrue(w.session.find_clip(clip_id)[1].volume_envelope)
        count = len(w.session.tracks)
        w.actions['add_track'].trigger()
        self.assertEqual(len(w.session.tracks), count + 1)
        w.actions['remove_track'].trigger()
        self.assertEqual(len(w.session.tracks), count)
        c.tools.toggleViewAction().trigger()
        w.set_mode('waveform')
        self.assertFalse(c.tools.isVisible())
        self.assertTrue(w.actions['amplify'].isEnabled())
        self.assertIn(w.actions['edit_sample'], w.menus['edit'].actions())

    def test_recording_locks_tool_edits_and_restores_them_after_stop(self):
        self.load()
        w = self.window
        w._record_context = {}
        w.update_recording_actions()
        self.assertFalse(w.toolbar_controller.tools.isEnabled())
        self.assertFalse(w.toolbar_controller.options.isEnabled())
        for key in ('select_wave', 'draw_waveform', 'move_clips', 'add_track', 'edit_sample'):
            self.assertFalse(w.actions[key].isEnabled())
        self.assertTrue(w.menus['toolbars'].menuAction().isEnabled())
        w._record_context = None
        w.refresh()
        self.assertTrue(w.toolbar_controller.tools.isEnabled())
        self.assertTrue(w.actions['draw_waveform'].isEnabled())
        self.assertTrue(w.channel_choice.isEnabled())

    def test_layout_visibility_and_labels_survive_restart_and_mode_switches(self):
        w = self.window
        c = w.toolbar_controller
        w.addToolBar(Qt.ToolBarArea.RightToolBarArea, c.tools)
        w.addToolBar(Qt.ToolBarArea.BottomToolBarArea, c.options)
        c.general.toggleViewAction().trigger()
        w.actions['toolbar_labels'].setChecked(True)
        self.app.processEvents()
        self.assertFalse(c.general.isVisible())
        w.close()
        second = self.new_window()
        restored = second.toolbar_controller
        self.assertEqual(second.toolBarArea(restored.tools), Qt.ToolBarArea.RightToolBarArea)
        self.assertEqual(second.toolBarArea(restored.options), Qt.ToolBarArea.BottomToolBarArea)
        self.assertFalse(restored.general.isVisible())
        self.assertFalse(restored.general.toggleViewAction().isChecked())
        self.assertTrue(second.actions['toolbar_labels'].isChecked())
        second.set_mode('multitrack')
        second.set_mode('waveform')
        self.assertFalse(restored.general.isVisible())
        restored.general.toggleViewAction().trigger()
        self.assertTrue(restored.general.isVisible())

    def test_drag_handle_floats_a_bar_and_restart_keeps_its_window(self):
        bar = self.window.toolbar_controller.general
        QTest.mousePress(bar, Qt.MouseButton.LeftButton, pos=QPoint(5, bar.height() // 2))
        QTest.mouseMove(bar, QPoint(180, 180), delay=50)
        QTest.mouseRelease(bar, Qt.MouseButton.LeftButton, pos=QPoint(180, 180))
        self.app.processEvents()
        self.assertTrue(bar.isFloating())
        self.assertTrue(bar.isVisible())
        self.assertFalse(bar.windowIcon().isNull())
        expected = bar.geometry()
        self.window.close()
        second = self.new_window()
        restored = second.toolbar_controller.general
        self.assertTrue(restored.isFloating())
        self.assertTrue(restored.isVisible())
        self.assertEqual(restored.geometry(), expected)
        # Closing a floating bar can always be undone through View -> Toolbars.
        restored.close()
        self.app.processEvents()
        self.assertFalse(restored.toggleViewAction().isChecked())
        restored.toggleViewAction().trigger()
        self.assertTrue(restored.isVisible())

    def test_invalid_saved_state_and_cancelled_close_preserve_preferences(self):
        w = self.window
        w.ui_settings.setValue('ui/toolbar_layout', b'invalid')
        self.assertFalse(w.toolbar_controller.restore())
        self.assertEqual(w.toolBarArea(w.toolbar_controller.tools), Qt.ToolBarArea.LeftToolBarArea)
        with patch.object(w, '_confirm_discard', return_value=False):
            self.assertFalse(w.close())
        self.assertEqual(bytes(w.ui_settings.value('ui/toolbar_layout')), b'invalid')
        self.assertTrue(w.close())
        self.assertNotEqual(bytes(w.ui_settings.value('ui/toolbar_layout')), b'invalid')

    def test_toolbar_titles_and_menu_choices_follow_all_five_languages(self):
        manager = install_language()
        old = current_language()
        try:
            for language in ('nl', 'en', 'de', 'fr', 'es'):
                manager.set_language(language, persist=False)
                for bar in self.window.toolbar_controller.bars.values():
                    self.assertEqual(bar.windowTitle(), bar.toggleViewAction().text())
                self.assertTrue(self.window.toolbar_controller.name.text())
        finally:
            manager.set_language(old, persist=False)
