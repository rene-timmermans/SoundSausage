import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QDialog

from soundsausage.audio import read_wav
from soundsausage.document import Document
from soundsausage.theme import colors
from soundsausage.window import MainWindow, AmplifyDialog
from soundsausage.amplitude_ui import ChannelMixerDialog, NormalizeDialog
from soundsausage.space_ui import EchoDialog
from soundsausage.recording_ui import RecordDialog


class ChannelZoomGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.previous_palette = QPalette(self.app.palette())
        values = np.linspace(-.8, .8, 20000, dtype=np.float32)
        self.data = np.column_stack((values, values[::-1]))
        self.window = MainWindow(Document(self.data, 8000), no_audio=True)
        self.window.show(); self.app.processEvents(); self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs: dialog.reject(); dialog.deleteLater()
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater(); self.app.processEvents(); self.app.setPalette(self.previous_palette)

    def drag(self, first_channel, last_channel):
        wave = self.window.waveform
        first = QPoint(round(wave.x_at(3000)), round(wave.channel_rect(first_channel).center().y()))
        last = QPoint(round(wave.x_at(14000)), round(wave.channel_rect(last_channel).center().y()))
        QTest.mousePress(wave, Qt.MouseButton.LeftButton, pos=first)
        QTest.mouseMove(wave, last, 10); QTest.mouseRelease(wave, Qt.MouseButton.LeftButton, pos=last)

    def test_dragging_left_right_and_across_updates_target_and_highlight(self):
        for first, last, expected, index in ((0, 0, (0,), 1), (1, 1, (1,), 2), (0, 1, (0, 1), 0)):
            self.drag(first, last)
            self.assertEqual(self.window.document.selected_channels, expected)
            self.assertEqual(self.window.channel_choice.currentIndex(), index)
            self.assertTrue(self.window.document.selected)
        self.window.choose_channels((1,)); self.app.processEvents()
        wave = self.window.waveform; image = wave.grab().toImage()
        x = round(wave.x_at(8000)); top = round(wave.channel_rect(0).top()+30); bottom = round(wave.channel_rect(1).top()+30)
        # A gridline can pass exactly through the requested time coordinate.
        # Compare its neighbourhood so the highlight, rather than that line,
        # determines the result on every font-dependent plot width.
        self.assertTrue(any(image.pixelColor(x+dx,top+dy) != image.pixelColor(x+dx,bottom+dy)
                            for dx in range(-2,3) for dy in range(-2,3)))

    def test_header_menu_shortcuts_and_mono_behavior(self):
        self.window.channel_choice.setCurrentIndex(1)
        self.assertEqual(self.window.document.selected_channels, (0,))
        self.assertTrue(self.window.actions['channels_left'].isChecked())
        self.window.actions['channels_right'].trigger(); self.assertEqual(self.window.channel_choice.currentIndex(), 2)
        QTest.keyClick(self.window.waveform, Qt.Key.Key_B, Qt.KeyboardModifier.AltModifier)
        self.assertEqual(self.window.document.selected_channels, (0, 1))
        self.window.document = Document(self.data[:, :1], 8000); self.window.refresh()
        self.assertFalse(self.window.channel_choice.isVisible())
        self.assertFalse(self.window.actions['channels_right'].isEnabled())

    def test_effect_dialogs_show_right_channel_and_preview_preserves_left(self):
        self.window.choose_channels((1,)); self.window.document.select(100, 18000)
        amplify = AmplifyDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(amplify)
        self.assertEqual(len(amplify.initial), 1)
        amplify.initial[0].setValue(50)
        preview = amplify.preview_samples()
        np.testing.assert_array_equal(preview[:, 0], self.data[100:18000, 0])
        np.testing.assert_array_equal(preview[:, 1], self.data[100:18000, 1]*.5)
        normal = NormalizeDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(normal)
        normal.show(); self.app.processEvents(); self.assertFalse(normal.linked.isVisible())
        mixer = ChannelMixerDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(mixer)
        self.assertFalse(mixer.weights[0][0].isEnabled()); self.assertTrue(mixer.weights[1][0].isEnabled())
        echo = EchoDialog(self.window.document, self.window, no_audio=True); self.dialogs.append(echo)
        self.assertTrue(echo.keep_tail.isEnabled())
        echo.keep_tail.setChecked(True); self.assertFalse(echo.tail.isEnabled())
        self.assertTrue(echo.automatic_tail.isEnabled())
        echo.automatic_tail.setChecked(False); self.assertTrue(echo.tail.isEnabled())

    def test_length_actions_follow_selection_and_remain_available_for_one_channel(self):
        self.drag(0, 0)
        for key in ('cut', 'delete', 'trim', 'stretch', 'tone', 'generate_silence'):
            self.assertTrue(self.window.actions[key].isEnabled(), key)
        for key in ('copy', 'save_selection', 'amplify', 'pitch_shift'):
            self.assertTrue(self.window.actions[key].isEnabled(), key)
        self.window.refresh()
        self.assertTrue(self.window.actions['stretch'].isEnabled())
        self.window.choose_channels(None)
        for key in ('cut', 'delete', 'trim', 'stretch'): self.assertTrue(self.window.actions[key].isEnabled(), key)

    def test_export_selection_writes_only_selected_mono_channel(self):
        self.window.choose_channels((1,)); self.window.document.select(100, 500)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'Right.wav'
            with patch.object(self.window, '_save_path', return_value=(path, 'float32')):
                self.window.save_selection()
            np.testing.assert_array_equal(read_wav(path).samples, self.data[100:500, 1:2])

    def test_generation_uses_chosen_channel_for_tones_and_longer_silence(self):
        doc = self.window.document; self.window.choose_channels((1,)); doc.select(100, 200)
        with patch('soundsausage.window.QDialog.exec', return_value=QDialog.DialogCode.Accepted):
            self.window.generate_tone()
        np.testing.assert_array_equal(doc.view()[:len(self.data), 0], self.data[:, 0])
        np.testing.assert_array_equal(doc.view()[len(self.data):, 0], 0)
        self.assertFalse(np.array_equal(doc.view()[100:200, 1], self.data[100:200, 1]))
        doc.undo(); doc.select(100, 200)
        with patch('soundsausage.window.QInputDialog.getDouble', return_value=(.02, True)):
            self.window.generate_silence()
        self.assertEqual(doc.frames, len(self.data)+60)
        np.testing.assert_array_equal(doc.view()[:len(self.data), 0], self.data[:, 0])
        np.testing.assert_array_equal(doc.view()[100:260, 1], 0)
        np.testing.assert_array_equal(doc.view()[260:, 1], self.data[200:, 1])
        doc.undo(); np.testing.assert_array_equal(doc.view(), self.data)

    def test_recording_locks_header_and_partial_channel_setup_offers_mono_insertion(self):
        self.window.choose_channels((0,))
        with patch.object(self.window.audio_devices, 'inputs', return_value=[]):
            dialog = RecordDialog(self.window); self.dialogs.append(dialog)
        self.assertEqual([dialog.target.itemData(i) for i in range(dialog.target.count())], ['insert', 'new'])
        self.assertEqual(dialog.channels.currentIndex(), 0)
        self.assertFalse(dialog.channels.isEnabled())
        self.window._record_context = {}; self.window.update_recording_actions()
        self.assertFalse(self.window.channel_choice.isEnabled())
        for key in ('channels_both', 'channels_left', 'channels_right'): self.assertFalse(self.window.actions[key].isEnabled())
        self.window._record_context = None; self.window.refresh(); self.assertTrue(self.window.channel_choice.isEnabled())

    def test_partial_channel_recording_note_translates_and_switches_live(self):
        from test_playback import Device
        from soundsausage.i18n import install_language, tr
        self.window.choose_channels((1,)); self.window.no_audio = False
        manager = install_language()
        try:
            with patch.object(self.window.audio_devices, 'inputs', return_value=[Device('USB input', b'input')]):
                dialog = RecordDialog(self.window); self.dialogs.append(dialog); dialog.show()
                for lang in ('nl', 'de', 'fr', 'es', 'en'):
                    manager.set_language(lang, False); self.app.processEvents()
                    self.assertIn(tr('Only the chosen channel shifts. The other stays in place; shorter audio is padded with silence.'), dialog.note.text())
                    self.assertEqual(dialog.channels.currentIndex(), 0)
        finally:
            manager.set_language('en', False); self.window.no_audio = True

    def test_waveform_is_continuous_at_raw_envelope_transition_and_during_zoom(self):
        wave = self.window.waveform; rect = wave.plot_rect(); color = colors().waveform.rgb()
        for samples_per_pixel in (.5, 1, 2, 4, 4.1, 8, 16):
            span = min(len(self.data), round(rect.width()*samples_per_pixel))
            wave.set_view(400, 400+span); self.app.processEvents(); image = wave.grab().toImage()
            lane = wave.channel_rect(0)
            gaps = []
            for x in range(round(rect.left())+30, round(rect.right())-3):
                if not any(image.pixelColor(x, y).rgb() == color for y in range(round(lane.top())+25, round(lane.bottom())-2)):
                    gaps.append(x)
            self.assertLessEqual(len(gaps), 1, (samples_per_pixel, gaps[:20]))

    def test_multitrack_uses_connected_waveform_contour(self):
        self.window.session.import_audio([(self.data, 8000, 'Ramp')]); self.window.set_mode('multitrack')
        self.window.multitrack.timeline.fit(); self.app.processEvents()
        self.assertFalse(self.window.multitrack.timeline.grab().isNull())

    def test_every_function_icon_is_visible_unique_and_zoom_functions_differ(self):
        for size in (16, 24, 48):
            signatures = {}
            for key, action in self.window.actions.items():
                image = action.icon().pixmap(size, size).toImage()
                self.assertFalse(image.isNull(), key)
                self.assertTrue(any(image.pixelColor(x, y).alpha() > (100 if size == 16 else 200) for y in range(size) for x in range(size)), key)
                signature = hashlib.sha256(bytes(image.constBits())).hexdigest()
                self.assertNotIn(signature, signatures, (size, key, signatures.get(signature)))
                signatures[signature] = key
                self.assertTrue(action.isIconVisibleInMenu(), key)
            self.assertNotEqual(self.window.actions['zoom_full'].icon().cacheKey(), self.window.actions['zoom_selection'].icon().cacheKey())
