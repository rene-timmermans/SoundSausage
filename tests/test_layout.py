"""Desktop layout and transport behaviour at the reference window sizes."""
import unittest

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton

from soundsausage.document import Document
from soundsausage.theme import colors
from soundsausage.waveform import clock_text
from soundsausage.window import MainWindow


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(no_audio=True)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.session.mark_saved()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def load_waveform(self):
        samples = np.full((8000, 2), .25, np.float32)
        self.window.document = Document(samples, 8000, dsp=self.window.document.dsp)
        self.window.refresh(fit=True)
        self.app.processEvents()

    def test_empty_workspace_and_two_compact_toolbar_rows_leave_room_for_audio(self):
        for width, height in ((1015, 609), (1180, 720), (1280, 800)):
            with self.subTest(width=width, height=height):
                self.window.resize(width, height)
                self.app.processEvents()
                bars = self.window.findChildren(QToolBar)
                self.assertEqual(len({bar.geometry().y() for bar in bars if bar.isVisible()}), 2)
                self.assertLess(sum({bar.height() for bar in bars}), 80)
                self.assertGreater(self.window.waveform.height(), height * .62)
                image = self.window.waveform.grab().toImage()
                self.assertEqual(image.pixelColor(100, 100), colors().workspace)
                self.assertFalse(self.window.scroll.isVisible())
                self.assertEqual(self.window.view_fields["End"].text(), "0:00.000")
                self.assertLess(self.window.transport.geometry().bottom(), self.window.centralWidget().height() + 1)

    def test_reference_menu_groups_and_unimplemented_effects_do_not_claim_to_work(self):
        expected = ["File", "Edit", "View", "Transform", "Generate", "Analyze", "Favorites", "Options", "Window", "Help"]
        actual = [action.text().replace("&", "") for action in self.window.menuBar().actions()]
        self.assertEqual(actual, expected)
        amplitude = self.window.menus["amplitude"]
        self.assertIn(self.window.actions["amplify"], amplitude.actions())
        self.assertIn(self.window.actions["normalize"], amplitude.actions())
        mixer = next(action for action in amplitude.actions() if action.text() == "Channel Mixer…")
        self.assertFalse(mixer.isEnabled())
        self.assertFalse(self.window.actions["record"].isEnabled())

    def test_all_toolbar_commands_have_visible_icons_and_named_tooltips(self):
        for bar in self.window.findChildren(QToolBar):
            for action in bar.actions():
                if action.isSeparator():
                    continue
                button = bar.widgetForAction(action)
                self.assertIsInstance(button, QToolButton)
                self.assertFalse(button.icon().isNull(), action.text())
                self.assertTrue(button.toolTip(), action.text())

    def test_selection_and_visible_range_fields_follow_zoom_and_working_mode(self):
        self.load_waveform()
        self.window.document.select(2000, 4000)
        self.window.refresh()
        self.window.waveform.zoom_selection()
        self.assertEqual(self.window.fields["Begin"].text(), "0:00.250")
        self.assertEqual(self.window.fields["End"].text(), "0:00.500")
        self.assertEqual(self.window.view_fields["Length"].text(), "0:00.250")
        self.window.insert_waveform()
        view = self.window.multitrack.timeline
        self.assertEqual(self.window.view_fields["End"].text(), clock_text(view.view_end / self.window.session.sample_rate))
        view.set_view(8000, 24000)
        self.assertEqual(self.window.view_fields["Begin"].text(), "0:01.000")
        self.assertEqual(self.window.view_fields["End"].text(), "0:03.000")
        self.window.set_mode("waveform")
        self.assertEqual(self.window.view_fields["End"].text(), "0:00.500")

    def test_transport_navigation_and_level_meter_use_actual_audio_state(self):
        self.load_waveform()
        self.window.waveform.setFocus()
        QTest.keyClick(self.window.waveform, Qt.Key.Key_End)
        self.assertEqual(self.window.document.cursor, 8000)
        QTest.keyClick(self.window.waveform, Qt.Key.Key_Home)
        self.assertEqual(self.window.document.cursor, 0)
        self.window.actions["seek_forward"].trigger()
        self.assertEqual(self.window.document.cursor, 8000)
        self.window.actions["seek_back"].trigger()
        self.assertEqual(self.window.document.cursor, 0)
        self.window.update_meters(np.array([[1.2, .25]], np.float32))
        meter = self.window.transport.meter
        self.assertGreater(meter.peaks[0], 1)
        self.assertAlmostEqual(meter.peaks[1], .25)
        image = meter.grab().toImage()
        self.assertEqual(image.pixelColor(image.width() - 16, 5).name(), "#e64b4b")
        self.assertNotEqual(image.pixelColor(image.width() - 16, 14).name(), "#e64b4b")
        self.window.player.stop()
        self.assertEqual(meter.peaks, (0.0, 0.0))
