import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.audio import AudioError
from soundsausage.document import Document
from soundsausage.drawing import DrawingStroke
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled
from soundsausage import storage
from soundsausage.window import MainWindow


class DrawingTests(unittest.TestCase):
    def test_groups_follow_zoom_and_never_exceed_one_second(self):
        doc = Document(np.zeros((80000, 2), np.float32), sample_rate=8000)
        for visible, width, expected in ((40, 80, 1), (80, 80, 2), (160, 80, 4), (80000, 10, 8000)):
            stroke = DrawingStroke(doc, 1, visible, width)
            self.assertEqual(stroke.size, expected)
            stroke.add(17001, .3)
            patches = stroke.patches()
            self.assertTrue(any(a <= 17001 < b for a,b,_,_ in patches))
            self.assertTrue(all(b-a <= doc.sample_rate for a,b,_,_ in patches))
        stroke.add(40001, -.4)
        self.assertGreater(len(stroke.groups), 1)  # A gesture can cross several one-second groups.
        self.assertTrue(all(b-a <= 8000 for a,b,_,_ in stroke.patches()))

    def test_interpolation_backtracking_clamping_and_document_edges(self):
        doc = Document(np.zeros((12, 1), np.float32))
        stroke = DrawingStroke(doc, 0, 12, 24)
        stroke.add(2, 0); stroke.add(6, 1)
        doc.draw_samples(0, stroke.patches())
        np.testing.assert_array_equal(doc.read()[2:7,0], [0, .25, .5, .75, 1])
        stroke.add(4, -1)
        stroke.add(-100, -2); stroke.add(99, 2)
        self.assertTrue(all(0 <= a < b <= 12 and -1 <= v <= 1 and -1 <= w <= 1
                            for a,b,v,w in stroke.patches()))

    def test_atomic_commit_preserves_other_channel_timing_metadata_and_history(self):
        data = np.arange(40, dtype=np.float32).reshape(20,2)/100
        doc = Document(data)
        doc.select(3, 15); doc.cursor = 9; doc.select_channels((0,))
        doc.metadata = ((b'cue ', b'unchanged'),)
        doc.draw_samples(1, ((2,5,-.5,.5), (10,12,.2,.3)))
        np.testing.assert_array_equal(doc.read()[:,0], data[:,0])
        np.testing.assert_array_equal(doc.read()[2:5,1], [-.5,0,.5])
        np.testing.assert_array_equal(doc.read()[5:10], data[5:10])
        self.assertEqual((doc.selection,doc.cursor,doc.selected_channels,doc.frames), ((3,15),9,(0,),20))
        self.assertEqual(doc.metadata, ((b'cue ', b'unchanged'),))
        self.assertEqual(len(doc.undo_stack),1)
        result = doc.read()
        doc.undo(); np.testing.assert_array_equal(doc.read(),data)
        doc.redo(); np.testing.assert_array_equal(doc.read(),result)
        doc.draw_samples(1, ((2,5,-.5,.5),))
        self.assertEqual(len(doc.undo_stack),1)

    def test_invalid_ranges_cancellation_and_allocation_failure_leave_source_intact(self):
        data = np.zeros((16001,2), np.float32)
        doc = Document(data, sample_rate=8000)
        for patches in (((0,8001,0,.5),), ((0,2,0,2),), ((0,3,0,.5),(2,4,0,.5)), ((-1,2,0,.5),), ((0,1,float('nan'),0),)):
            with self.assertRaises(AudioError): doc.draw_samples(0, patches)
        with self.assertRaises(OperationCancelled):
            with operation(lambda done,total,label: done < 1):
                doc.draw_samples(0, ((0,2,0,.5), (10,12,0,.5)))
        with patch.object(storage,'allocate',side_effect=OSError('disk full')):
            with self.assertRaises(OSError): doc.draw_samples(0, ((0,2,0,.5),))
        np.testing.assert_array_equal(doc.read(),data)
        self.assertFalse(doc.undo_stack)

    def test_larger_stroke_uses_disk_storage_and_keeps_original_backing(self):
        source = storage.allocate((12000,2), force_disk=True, zero=True)
        doc = Document(storage.seal(source, checked=True), sample_rate=8000)
        with patch.object(storage, 'MEMORY_THRESHOLD', 128):
            doc.draw_samples(0, ((100,200,.1,.2), (300,400,.2,.3)))
        self.assertTrue(any(storage.lease_of(p) for p in doc._pieces))
        np.testing.assert_array_equal(source, np.zeros((12000,2),np.float32))
        doc.undo(); self.assertEqual(np.count_nonzero(doc.read()),0)


class DrawingGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = np.zeros((8000,2),np.float32)
        self.window = MainWindow(Document(self.data, sample_rate=8000), no_audio=True)
        self.window.show(); self.app.processEvents()
        self.wave = self.window.waveform

    def tearDown(self):
        self.window.document.mark_saved(); self.window.session.mark_saved()
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def point(self, frame, channel, value):
        return QPoint(round(self.wave.x_at(frame)), round(self.wave.sample_y(channel,value)))

    def test_freehand_at_coarse_zoom_without_points_is_one_undo_and_channel_locked(self):
        self.assertFalse(self.wave.sample_points_visible())
        self.window.actions['draw_waveform'].trigger()
        start,end = self.point(2000,1,.4),self.point(4000,1,-.4)
        QTest.mousePress(self.wave,Qt.MouseButton.LeftButton,pos=start)
        QTest.mouseMove(self.wave,end,10)
        self.assertIsNotNone(self.wave._drawing_stroke)
        np.testing.assert_array_equal(self.window.document.read(),self.data)
        self.assertFalse(self.wave.grab().isNull())
        QTest.mouseRelease(self.wave,Qt.MouseButton.LeftButton,pos=end)
        doc = self.window.document
        self.assertEqual(len(doc.undo_stack),1)
        np.testing.assert_array_equal(doc.read()[:,0],self.data[:,0])
        self.assertGreater(doc.read()[2000,1],.3)
        self.assertLess(doc.read()[4000,1],-.3)
        self.assertAlmostEqual(float(doc.read()[3000,1]),0,delta=.03)
        result=doc.read();doc.undo();np.testing.assert_array_equal(doc.read(),self.data)
        doc.redo();np.testing.assert_array_equal(doc.read(),result)

    def test_escape_shift_mode_switch_and_recording_cannot_commit_a_preview(self):
        action=self.window.actions['draw_waveform'];action.trigger()
        start,end=self.point(2000,0,.4),self.point(4000,0,.2)
        for cancel in ('escape','mode','view','recording'):
            with self.subTest(cancel=cancel):
                QTest.mousePress(self.wave,Qt.MouseButton.LeftButton,pos=start)
                QTest.mouseMove(self.wave,end,5)
                if cancel=='escape': QTest.keyClick(self.wave,Qt.Key.Key_Escape)
                elif cancel=='mode': action.trigger();action.trigger()
                elif cancel=='view': self.wave.fit()
                else:
                    self.window._record_context={};self.window.update_recording_actions()
                QTest.mouseRelease(self.wave,Qt.MouseButton.LeftButton,pos=end)
                self.assertFalse(self.window.document.undo_stack)
                self.window._record_context=None;self.window.refresh()
        QTest.mousePress(self.wave,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.ShiftModifier,start)
        QTest.mouseMove(self.wave,end,5)
        QTest.mouseRelease(self.wave,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.ShiftModifier,end)
        self.assertTrue(self.window.document.selected)
        self.assertFalse(self.window.document.undo_stack)
