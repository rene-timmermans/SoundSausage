"""Time entry through the real editor: drafts, bounds, navigation and audio integrity."""
from contextlib import ExitStack
from decimal import Decimal
import os
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.document import Document
from soundsausage.session import Session
from soundsausage.transport import parse_time_frames
from soundsausage.waveform import clock_text
from soundsausage.window import MainWindow


class TimeParsingTests(unittest.TestCase):
    def test_seconds_clocks_decimal_comma_and_exact_frame_rounding(self):
        for text,seconds in (('1.25','1.25'),('1,25','1.25'),('.5','.5'),('1:08.696','68.696'),
                             ('01:02:03,456','3723.456'),('24:00:00','86400')):
            with self.subTest(text=text):
                self.assertEqual(parse_time_frames(text,48000,48000*86400),int(Decimal(seconds)*48000))
        self.assertEqual(parse_time_frames('0.0000625',8000,8000),1)
        self.assertEqual(parse_time_frames('9999999999999999999999',48000,12345),12345)

    def test_invalid_input_is_rejected_and_formatted_minute_rollover_is_parseable(self):
        for text in ('','-1','nan','inf','1e3','1:60','1:2:3:4','1:60:00','1..2','1:abc'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):parse_time_frames(text,48000,48000*86400)
        for seconds,expected in ((59.9996,'1:00.000'),(3599.9996,'1:00:00.000'),(86400,'24:00:00.000')):
            self.assertEqual(clock_text(seconds),expected)
            self.assertEqual(parse_time_frames(expected,8000,8000*86400),round(seconds)*8000)


class TimeFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.stack=ExitStack()
        self.stack.enter_context(patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':self.temp.name}))
        self.source=np.column_stack((np.linspace(-.4,.4,240000),np.linspace(.2,-.2,240000))).astype(np.float32)
        self.window=MainWindow(Document(self.source,8000),no_audio=True)
        self.window.show();self.app.processEvents()

    def tearDown(self):
        w=self.window;w._record_context=None;w.player.state='Stopped'
        w.document.mark_saved();w.session.mark_saved();w.close();w.deleteLater();self.app.processEvents()
        self.stack.close();self.temp.cleanup()

    def type_value(self,row,key,text,confirm=True):
        field=(self.window.fields if row=='Sel' else self.window.view_fields)[key]
        field.setFocus();self.app.processEvents();self.assertTrue(field.hasFocus())
        QTest.keyClick(field,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier)
        QTest.keyClicks(field,text)
        if confirm:QTest.keyClick(field,Qt.Key.Key_Return);self.app.processEvents()
        return field

    def test_all_selection_fields_change_only_selection_with_crossing_and_bounds(self):
        w=self.window;w.document.select(40000,80000);w.selection_changed(*w.document.selection)
        self.type_value('Sel','Begin','0:06.250');self.assertEqual(w.document.selection,(50000,80000))
        self.type_value('Sel','End','12,5');self.assertEqual(w.document.selection,(50000,100000))
        self.type_value('Sel','Length','0:02.500');self.assertEqual(w.document.selection,(50000,70000))
        self.type_value('Sel','Begin','15');self.assertEqual(w.document.selection,(120000,120000))
        self.type_value('Sel','End','4');self.assertEqual(w.document.selection,(32000,32000))
        self.type_value('Sel','Length','9999');self.assertEqual(w.document.selection,(32000,240000))
        self.assertEqual(w.fields['End'].text(),'0:30.000')
        self.assertFalse(w.document.undo_stack);self.assertFalse(w.document.dirty)
        np.testing.assert_array_equal(w.document.read(),self.source)

    def test_all_view_fields_control_zoom_without_changing_selection_or_samples(self):
        w=self.window;w.document.select(8000,16000);w.selection_changed(*w.document.selection)
        w.waveform.set_view(40000,160000)
        self.type_value('View','Begin','6');self.assertEqual((w.waveform.view_start,w.waveform.view_end),(48000,160000))
        self.type_value('View','End','12');self.assertEqual((w.waveform.view_start,w.waveform.view_end),(48000,96000))
        self.type_value('View','Length','2,5');self.assertEqual((w.waveform.view_start,w.waveform.view_end),(48000,68000))
        self.type_value('View','End','0');self.assertEqual((w.waveform.view_start,w.waveform.view_end),(0,1))
        self.assertEqual(w.document.selection,(8000,16000));self.assertFalse(w.document.undo_stack)
        np.testing.assert_array_equal(w.document.read(),self.source)

    def test_invalid_input_escape_and_focus_loss_preserve_or_commit_the_correct_draft(self):
        w=self.window;w.document.select(8000,16000);w.selection_changed(*w.document.selection)
        with patch('soundsausage.transport.QToolTip.showText') as tooltip:
            field=self.type_value('Sel','End','not-a-time');tooltip.assert_called_once()
        self.assertEqual(w.document.selection,(8000,16000));self.assertEqual(field.text(),'0:02.000')
        field=self.type_value('Sel','End','9',False)
        w.selection_changed(*w.document.selection);self.assertEqual(field.text(),'9')
        QTest.keyClick(field,Qt.Key.Key_Escape);self.assertEqual(field.text(),'0:02.000')
        self.assertEqual(w.document.selection,(8000,16000))
        self.type_value('Sel','End','3',False)
        w.waveform.setFocus();self.app.processEvents()
        self.assertEqual(w.document.selection,(8000,24000))

    def test_local_undo_and_home_end_do_not_trigger_audio_shortcuts(self):
        w=self.window;w.document.replace(0,10,np.zeros((10,2),np.float32),'Test edit')
        before=w.document.read().copy();history=len(w.document.undo_stack)
        field=self.type_value('Sel','End','7',False)
        QTest.keyClick(field,Qt.Key.Key_Z,Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(field,Qt.Key.Key_Home);QTest.keyClick(field,Qt.Key.Key_End)
        self.assertEqual(len(w.document.undo_stack),history)
        np.testing.assert_array_equal(w.document.read(),before)
        QTest.keyClick(field,Qt.Key.Key_Escape)

    def test_multitrack_time_entry_supports_hours_without_modifying_session_history(self):
        w=self.window;w.insert_waveform();history=len(w.session.undo_stack)
        self.type_value('Sel','End','1:02:03.456')
        self.assertEqual(w.session.selection,(0,round(3723.456*8000)))
        self.type_value('View','Begin','1:00:00');self.assertEqual(w.multitrack.timeline.view_start,3600*8000)
        self.type_value('View','Length','5');self.assertEqual(w.multitrack.timeline.view_end,(3600+5)*8000)
        self.assertEqual(len(w.session.undo_stack),history)
        w.session=Session(384000,2);w.refresh(fit=True)
        self.type_value('Sel','End','24:00:00')
        self.assertEqual(w.session.selection,(0,33177600000))
        self.assertEqual(w.fields['End'].text(),'24:00:00.000')

    def test_playback_continues_and_recording_locks_time_entry(self):
        w=self.window;w.player.state='Playing'
        with patch.object(w.player,'stop') as stop:
            self.type_value('Sel','End','2');self.type_value('View','Length','4')
            stop.assert_not_called();self.assertEqual(w.player.state,'Playing')
        before=w.document.selection;w._record_context={}
        w.transport.configure_time_fields(w.document,w.mode,False)
        self.assertTrue(all(f.isReadOnly() for f in (*w.fields.values(),*w.view_fields.values())))
        w.edit_transport_range('Sel','End',80000);self.assertEqual(w.document.selection,before)
        w._record_context=None;w.player.state='Stopped'

    def test_switching_models_discards_a_draft_and_empty_waveforms_are_read_only(self):
        w=self.window;field=self.type_value('Sel','End','12',False)
        w.document=Document(np.zeros((8000,2),np.float32),8000)
        QTest.keyClick(field,Qt.Key.Key_Return)
        self.assertEqual(w.document.selection,(0,0))
        w.refresh(fit=True)
        self.assertEqual(w.fields['End'].text(),'0:00.000');self.assertEqual(w.document.selection,(0,0))
        w.document=Document();w.refresh(fit=True)
        self.assertTrue(w.fields['Begin'].isReadOnly());self.assertTrue(w.view_fields['End'].isReadOnly())
