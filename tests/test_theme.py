"""Regression checks for the reported unreadable dark-theme controls, using Qt rendering."""
import unittest

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPalette, QIcon
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton

from soundsausage.theme import contrast
from soundsausage.window import MainWindow


class ThemeGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.previous = QPalette(self.app.palette())
        self.window = MainWindow(no_audio=True)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.session.mark_saved()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.app.setPalette(self.previous)

    def toolbar_button(self, key):
        for bar in self.window.findChildren(QToolBar):
            result = bar.widgetForAction(self.window.actions[key])
            if isinstance(result, QToolButton):
                return result
        self.fail(f"No toolbar button for {key}")

    def use_palette(self, background, text, accent):
        palette = self.app.style().standardPalette()
        for role in ("Window", "Base", "Button"):
            palette.setColor(getattr(QPalette.ColorRole, role), QColor(background))
        for role in ("WindowText", "Text", "ButtonText"):
            palette.setColor(getattr(QPalette.ColorRole, role), QColor(text))
        palette.setColor(QPalette.ColorRole.Accent, QColor(accent))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(accent))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
        self.app.setPalette(palette)
        QTest.mouseMove(self.window.waveform, QPoint(200, 100))
        self.app.processEvents()

    def test_rendered_controls_follow_live_light_dark_and_pale_accent_changes(self):
        for background, text, accent in (("#f0f1f3", "#20252b", "#794bc4"),
                                         ("#252a30", "#ecf0f4", "#36c5ac"),
                                         ("#f0f1f3", "#20252b", "#f7d349")):
            with self.subTest(background=background, accent=accent):
                self.use_palette(background, text, accent)
                self.window.actions["open"].setText("&Open audio…")
                # Actual rendered pixels catch the old fixed light-grey backgrounds.
                image = self.window.grab().toImage()
                self.assertEqual(image.pixelColor(2, self.window.height() // 2).name(), background)
                button = self.toolbar_button("open")
                rendered = button.grab().toImage()
                fill = rendered.pixelColor(5, button.height() // 2)
                self.assertEqual(fill.name(), accent)
                foreground = button.palette().color(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText)
                self.assertGreaterEqual(contrast(foreground, fill), 4.5)
                icon_image = button.icon().pixmap(24, 24).toImage()
                ink = [icon_image.pixelColor(x, y) for y in range(24) for x in range(24)
                       if icon_image.pixelColor(x, y).alpha() >= 220]
                self.assertTrue(ink)
                self.assertGreaterEqual(contrast(ink[0], fill), 4.5)
                QTest.mouseMove(button, QPoint(10, 10))
                self.app.processEvents()
                hover_fill = button.grab().toImage().pixelColor(5, button.height() // 2)
                self.assertGreaterEqual(contrast(foreground, hover_fill), 4.5)
                clock_palette = self.window.time_label.palette()
                self.assertGreaterEqual(contrast(clock_palette.windowText().color(), clock_palette.window().color()), 4.5)
                # Inactive actions stay inactive, while their labels remain legible.
                undo = self.toolbar_button("undo")
                self.assertFalse(undo.isEnabled())
                disabled = undo.palette().color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText)
                disabled_background = undo.grab().toImage().pixelColor(5, undo.height() // 2)
                self.assertGreaterEqual(contrast(disabled, disabled_background), 3.0)

    def test_mode_buttons_keep_their_labels_and_highlight_the_active_view(self):
        self.use_palette("#252a30", "#ecf0f4", "#36c5ac")
        for key, mode in (("mode_multi", "multitrack"), ("mode_wave", "waveform")):
            with self.subTest(mode=mode):
                self.window.actions[key].trigger()
                self.app.processEvents()
                button = self.toolbar_button(key)
                self.assertTrue(button.isChecked())
                self.assertEqual(button.toolButtonStyle(), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                self.assertIn("View", button.text())
                self.assertEqual(self.window.mode, mode)
                fill = button.grab().toImage().pixelColor(5, button.height() // 2)
                self.assertEqual(fill.name(), "#36c5ac")

    def test_menu_icons_are_visible_on_neutral_backgrounds_including_checked_modes(self):
        self.use_palette("#f0f1f3", "#20252b", "#794bc4")
        for key, state in (("open", QIcon.State.Off), ("mode_wave", QIcon.State.On)):
            with self.subTest(action=key):
                pixmap = self.window.actions[key].icon().pixmap(24, 24, QIcon.Mode.Normal, state)
                image = pixmap.toImage()
                solid = [image.pixelColor(x, y) for y in range(image.height()) for x in range(image.width())
                         if image.pixelColor(x, y).alpha() >= 220]
                self.assertTrue(solid)
                self.assertGreaterEqual(contrast(solid[0], QColor("#f0f1f3")), 3.0)


if __name__ == "__main__":
    unittest.main()
