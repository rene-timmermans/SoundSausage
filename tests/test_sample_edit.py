"""Single-sample corrections leave every other scalar, timing and history intact."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialogButtonBox

from soundsausage.audio import AudioError, read_wav, write_wav
from soundsausage.document import Document
from soundsausage.sample_ui import SampleDialog
from soundsausage.window import MainWindow


class SampleEditTests(unittest.TestCase):
    def test_only_the_addressed_scalar_changes_with_full_undo_and_redo(self):
        original = np.arange(60, dtype=np.float32).reshape(30, 2) / 100
        for channel in (0, 1):
            for frame in (0, 12, 29):
                doc = Document(original)
                doc.metadata = ((b'cue ', b'unchanged marker'),)
                doc.select(3, 22); doc.cursor = 17; doc.select_channels((1,))
                doc.set_sample(frame, channel, -.333)
                expected = original.copy(); expected[frame, channel] = -.333
                np.testing.assert_array_equal(doc.read(), expected)
                self.assertEqual((doc.frames, doc.selection, doc.cursor, doc.selected_channels), (30, (3, 22), 17, (1,)))
                self.assertEqual(doc.metadata, ((b'cue ', b'unchanged marker'),))
                self.assertEqual(len(doc.undo_stack), 1); self.assertTrue(doc.dirty)
                doc.undo(); np.testing.assert_array_equal(doc.read(), original); self.assertFalse(doc.dirty)
                doc.redo(); np.testing.assert_array_equal(doc.read(), expected)

    def test_no_op_and_invalid_edits_preserve_history_and_audio(self):
        doc = Document(np.full((5, 1), .25, np.float32))
        doc.set_sample(2, 0, .5); doc.undo()
        redo = tuple(doc.redo_stack)
        doc.set_sample(2, 0, .25)
        self.assertEqual(tuple(doc.redo_stack), redo); self.assertFalse(doc.dirty)
        for frame, channel, value in ((-1, 0, 0), (5, 0, 0), (1, 1, 0), (1, 0, float('nan')), (1, 0, float('inf')), (1, 0, 1e40)):
            with self.assertRaises(AudioError): doc.set_sample(frame, channel, value)
        np.testing.assert_array_equal(doc.read(), np.full((5, 1), .25, np.float32))

    def test_a_small_edit_keeps_large_file_backing_shared_and_roundtrips_losslessly(self):
        from soundsausage import storage
        data = storage.allocate((600000, 2), force_disk=True, zero=True)
        data[350001] = (.125, -.375)
        doc = Document(storage.seal(data, checked=True))
        backing = doc._pieces[0]
        doc.set_sample(350001, 1, .625)
        self.assertTrue(np.shares_memory(doc._pieces[0], backing))
        self.assertTrue(np.shares_memory(doc._pieces[-1], backing))
        self.assertEqual(sum(p.nbytes for p in doc._pieces if not np.shares_memory(p, backing)), 8)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'sample.wav'
            write_wav(path, doc.view(), 44100, 'float32')
            reopened = read_wav(path)
            self.assertEqual(tuple(reopened.samples[350001]), (.125, .625))
            self.assertEqual(np.count_nonzero(reopened.samples), 2)
        doc.undo(); self.assertEqual(tuple(doc.view(350001,350002)[0]), (.125, -.375))


class SampleEditGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        values = np.sin(np.arange(1000)*.1).astype(np.float32)*.5
        self.data = np.column_stack((values, -values))
        self.window = MainWindow(Document(self.data), no_audio=True)
        self.window.show(); self.app.processEvents()
        self.wave = self.window.waveform
        self.wave.set_view(300, 340); self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def point(self, frame=320, channel=1):
        return QPoint(round(self.wave.x_at(frame)), round(self.wave.sample_y(channel, self.data[frame, channel])))

    def test_drag_changes_one_sample_even_when_crossing_other_frames_and_channels(self):
        doc = self.window.document
        doc.select(50, 900); doc.cursor = 800; doc.select_channels((0,))
        first = self.point()
        QTest.mousePress(self.wave, Qt.MouseButton.LeftButton, pos=first)
        for dx in (10, 20, 30):
            QTest.mouseMove(self.wave, first + QPoint(dx, -35), 5)
            np.testing.assert_array_equal(doc.read(), self.data)  # preview only until release
        QTest.mouseMove(self.wave, self.point(330,0), 5)
        QTest.mouseMove(self.wave, first + QPoint(30,-35), 5)
        QTest.mouseRelease(self.wave, Qt.MouseButton.LeftButton, pos=first + QPoint(30, -35))
        changed = np.argwhere(doc.read() != self.data)
        np.testing.assert_array_equal(changed, [[320, 1]])
        self.assertEqual(len(doc.undo_stack), 1)
        self.assertEqual((doc.selection, doc.cursor, doc.selected_channels), ((50,900),800,(0,)))
        self.window.actions['undo'].trigger(); np.testing.assert_array_equal(doc.read(), self.data)
        self.window.actions['redo'].trigger(); self.assertNotEqual(doc.read()[320,1], self.data[320,1])

    def test_escape_cancels_and_shift_drag_keeps_selection_available(self):
        first = self.point()
        QTest.mousePress(self.wave, Qt.MouseButton.LeftButton, pos=first)
        QTest.mouseMove(self.wave, first + QPoint(0,40), 5)
        QTest.keyClick(self.wave, Qt.Key.Key_Escape)
        QTest.mouseRelease(self.wave, Qt.MouseButton.LeftButton, pos=first+QPoint(0,40))
        self.assertFalse(self.window.document.undo_stack)
        QTest.mousePress(self.wave, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ShiftModifier, first)
        QTest.mouseMove(self.wave, first+QPoint(70,0),5)
        QTest.mouseRelease(self.wave, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ShiftModifier, first+QPoint(70,0))
        self.assertTrue(self.window.document.selected)
        np.testing.assert_array_equal(self.window.document.read(), self.data)

    def test_points_require_zoom_and_recording_disables_direct_and_menu_edits(self):
        self.assertTrue(self.wave.sample_points_visible())
        self.wave.fit(); self.assertFalse(self.wave.sample_points_visible())
        self.assertIsNone(self.wave.sample_at(self.point()))
        self.wave.set_view(300,340)
        self.window._record_context = {}; self.window.update_recording_actions()
        self.assertIsNone(self.wave.sample_at(self.point()))
        self.assertFalse(self.window.actions['edit_sample'].isEnabled())
        self.window.edit_sample(320, 1, .25)
        np.testing.assert_array_equal(self.window.document.read(), self.data)
        self.window._record_context = None; self.window.refresh()
        self.assertTrue(self.window.actions['edit_sample'].isEnabled())
        self.window.set_mode('multitrack'); self.assertFalse(self.window.actions['edit_sample'].isEnabled())

    def test_double_click_and_menu_open_exact_editor_and_cancel_leaves_audio_intact(self):
        doc = self.window.document
        def accept_value():
            dialog = self.window.findChild(SampleDialog)
            self.assertIsNotNone(dialog)
            self.assertEqual(dialog.sample_edit()[:2], (320,1))
            dialog.units.setCurrentIndex(2)
            dialog.value.setValue(-16384)
            dialog.box.button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept_value)
        QTest.mouseDClick(self.wave, Qt.MouseButton.LeftButton, pos=self.point())
        self.assertEqual(doc.view(320,321)[0,1], -.5)
        self.assertEqual(len(doc.undo_stack), 1)
        before = doc.read()
        doc.select(600,600); doc.select_channels((0,))
        def reject_value():
            dialog = next(d for d in self.window.findChildren(SampleDialog) if d.isVisible())
            self.assertEqual(dialog.sample_edit()[:2], (600,0))
            dialog.value.setValue(.125); dialog.reject()
        QTimer.singleShot(0,reject_value)
        self.window.actions['edit_sample'].trigger()
        np.testing.assert_array_equal(doc.read(),before)
        self.assertEqual(len(doc.undo_stack),1)

    def test_display_ranges_do_not_quantize_until_a_value_is_edited(self):
        doc = self.window.document
        dialog = SampleDialog(doc,320,1,self.window)
        original = dialog.normalized_value
        for units in (1,2,3,0):
            dialog.units.setCurrentIndex(units)
            self.assertEqual(dialog.normalized_value,original)
        dialog.units.setCurrentIndex(3); dialog.value.setValue(-4194304)
        self.assertEqual(dialog.normalized_value,-.5)
        dialog.frame.setValue(999); dialog.channel.setCurrentIndex(0)
        self.assertEqual(dialog.normalized_value,float(self.data[999,0]))
        dialog.deleteLater()

    def test_typed_value_is_committed_when_the_dialog_result_is_read(self):
        dialog = SampleDialog(self.window.document,320,1,self.window)
        dialog.show(); self.app.processEvents()
        dialog.value.setFocus(); dialog.value.lineEdit().selectAll()
        QTest.keyClicks(dialog.value.lineEdit(),'0.375')
        self.assertEqual(dialog.sample_edit(), (320,1,.375))
        np.testing.assert_array_equal(self.window.document.read(),self.data)
        dialog.reject(); dialog.deleteLater()
