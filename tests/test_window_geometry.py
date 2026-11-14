"""Remember accepted exits, using Qt's display-aware window geometry format."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from soundsausage.window import MainWindow


class WindowGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_geometry_survives_a_new_settings_instance_and_clean_start(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/'window.ini')
            first = MainWindow(no_audio=True, ui_settings=QSettings(path, QSettings.Format.IniFormat))
            second = None
            try:
                self.assertFalse(first.restore_window_geometry())
                first.resize(first.minimumWidth(), 590)
                first.move(0, 30)
                first.show()
                self.app.processEvents()
                expected = first.size()
                first.close()
                second = MainWindow(no_audio=True, ui_settings=QSettings(path, QSettings.Format.IniFormat))
                self.assertTrue(second.restore_window_geometry())
                second.show()
                self.app.processEvents()
                self.assertEqual(second.size(), expected)
                self.assertFalse(second.document.frames)
            finally:
                for window in (first, second):
                    if window is not None:
                        window.close()
                        window.deleteLater()
                self.app.processEvents()

    def test_cancelled_close_does_not_overwrite_saved_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = QSettings(str(Path(folder)/'window.ini'), QSettings.Format.IniFormat)
            settings.setValue('ui/window_geometry', b'invalid')
            window = MainWindow(no_audio=True, ui_settings=settings)
            try:
                self.assertFalse(window.restore_window_geometry())
                window.show()
                with patch.object(window, '_confirm_discard', return_value=False):
                    self.assertFalse(window.close())
                self.assertEqual(bytes(settings.value('ui/window_geometry')), b'invalid')
                self.assertTrue(window.close())
                self.assertNotEqual(bytes(settings.value('ui/window_geometry')), b'invalid')
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()
