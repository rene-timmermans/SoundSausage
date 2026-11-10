"""Check the rendered variants, including alpha and high-DPI icon selection."""
import unittest

from PySide6.QtCore import QSize, QTimer
from PySide6.QtWidgets import QApplication

from soundsausage.icons import application_icon, mascot_icon, taskbar_icon
from soundsausage.window import MainWindow
from soundsausage.about import AboutDialog


class ApplicationIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_caption_and_taskbar_variants_have_different_backgrounds_at_both_scales(self):
        for ratio in (1, 2):
            icon = application_icon(device_pixel_ratio=ratio)
            for size in (16, 20, 24, 32, 48, 64):
                with self.subTest(ratio=ratio, size=size):
                    image = icon.pixmap(QSize(size, size), ratio).toImage()
                    self.assertEqual(image.width(), size * ratio)
                    # Left of the character, but inside the rounded tile.
                    background = image.pixelColor(round(image.width() * .08), image.height() // 2)
                    if size <= 24:
                        self.assertLessEqual(background.alpha(), 10)
                    else:
                        self.assertGreaterEqual(background.alpha(), 240)
                    self.assertGreaterEqual(image.pixelColor(image.width() // 2, image.height() // 2).alpha(), 240)

    def test_taskbar_corners_are_transparent_and_purple_background_is_retained(self):
        image = taskbar_icon().pixmap(128, 128).toImage()
        for x, y in ((0, 0), (127, 0), (0, 127), (127, 127)):
            self.assertLessEqual(image.pixelColor(x, y).alpha(), 10)
        purple = image.pixelColor(10, 64)
        self.assertGreaterEqual(purple.alpha(), 240)
        self.assertGreater(purple.blue(), purple.green())

    def test_mascot_has_no_tile_and_arm_openings_are_transparent(self):
        image = mascot_icon().pixmap(1254, 1254).toImage()
        for x, y in ((.08, .5), (.28, .54), (.61, .55)):
            self.assertLessEqual(image.pixelColor(round(x * image.width()), round(y * image.height())).alpha(), 10)
        self.assertGreaterEqual(image.pixelColor(round(.66 * image.width()), round(.32 * image.height())).alpha(), 240)

    def test_about_dialog_uses_the_isolated_character_at_large_size(self):
        window = MainWindow(no_audio=True)
        captured = []

        def inspect():
            for widget in self.app.topLevelWidgets():
                if isinstance(widget, AboutDialog) and widget.parent() is window:
                    captured.append(widget.mascot.pixmap().toImage())
                    self.assertIn("René Timmermans", widget.description.text())
                    self.assertIn("General Public License", widget.description.text())
                    self.assertIn("https://github.com/rene-timmermans/SoundSausage", widget.description.text())
                    widget.accept()

        try:
            QTimer.singleShot(0, inspect)
            window.about()
            self.assertEqual(len(captured), 1)
            image = captured[0]
            self.assertLessEqual(image.pixelColor(round(image.width() * .08), image.height() // 2).alpha(), 10)
        finally:
            window.close()
            window.deleteLater()
