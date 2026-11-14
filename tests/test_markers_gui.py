"""Marker gestures, dialog context, export and audio/channel preservation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QPoint, Qt, QSettings
from PySide6.QtGui import QFont
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from soundsausage import markers
from soundsausage.audio import read_wav
from soundsausage.document import Document
from soundsausage.i18n import install_language, tr
from soundsausage.marker_ui import MarkerDialog
from soundsausage.window import MainWindow


class MarkerGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.data=np.column_stack((np.sin(np.arange(20000)*.1),np.cos(np.arange(20000)*.1))).astype(np.float32)*.3
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        settings=QSettings(str(Path(self.folder.name)/"ui.ini"),QSettings.Format.IniFormat)
        self.window=MainWindow(Document(self.data,8000),no_audio=True,ui_settings=settings)
        self.errors=patch.object(self.window,'error');self.error=self.errors.start()
        self.window.show();self.app.processEvents()
        self.language=install_language();self.dialogs=[]
    def tearDown(self):
        self.language.set_language('en',False)
        self.window._record_context=None
        for dialog in self.dialogs:dialog.close();dialog.deleteLater()
        self.window.document.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater();self.app.processEvents();self.errors.stop()

    def add(self,frame=2000):
        self.window.active_model().select(frame,frame)
        self.window.add_marker();self.app.processEvents()
        return markers.for_model(self.window.active_model())[-1]

    def point(self,view,frame):
        return QPoint(round(view.x_at(frame)),round(view.marker_band().center().y()))

    def test_shortcut_add_and_exact_dialog_edit_are_undoable_without_pcm_changes(self):
        window=self.window;doc=window.document;doc.select(1000,1000);doc.select_channels((1,))
        self.assertIn(window.actions['markers'],window.menus['edit'].actions())
        self.assertIn(window.actions['marker_next'],window.menus['view'].actions())
        QTest.keyClick(window.waveform,Qt.Key.Key_M)
        item=markers.for_model(doc)[0]
        self.assertEqual(item.start,1000)
        self.assertEqual(len(doc.undo_stack),1)
        def properties(dialog):
            dialog.name.setText('Normalize');dialog.frame.setText('4567')
            return QDialog.DialogCode.Accepted
        with patch.object(MarkerDialog,'exec',properties):window.edit_marker_dialog(item.key)
        changed=markers.for_model(doc)[0]
        self.assertEqual((changed.name,changed.start),('Normalize',4567))
        self.assertEqual(doc.selected_channels,(1,))
        window.actions['undo'].trigger();self.assertEqual(markers.for_model(doc)[0].start,1000)
        window.actions['redo'].trigger();self.assertEqual(markers.for_model(doc)[0].start,4567)
        np.testing.assert_array_equal(doc.read(),self.data);self.error.assert_not_called()

    def test_waveform_flag_drag_previews_and_commits_once_and_escape_discards(self):
        item=self.add();window=self.window;view=window.waveform;doc=window.document
        doc.select_channels((1,));original=doc.metadata;history=len(doc.undo_stack)
        first,last=self.point(view,item.start),self.point(view,8000)
        QTest.mousePress(view,Qt.MouseButton.LeftButton,pos=first)
        QTest.mouseMove(view,last,5)
        self.assertEqual(doc.metadata,original)
        self.assertFalse(view.grab().isNull())
        QTest.mouseRelease(view,Qt.MouseButton.LeftButton,pos=last)
        moved=markers.for_model(doc)[0]
        self.assertLess(abs(moved.start-8000),30)
        self.assertEqual(len(doc.undo_stack),history+1)
        self.assertEqual(doc.selected_channels,(1,))
        before=doc.metadata
        QTest.mousePress(view,Qt.MouseButton.LeftButton,pos=self.point(view,moved.start))
        QTest.mouseMove(view,self.point(view,12000),5)
        QTest.keyClick(view,Qt.Key.Key_Escape)
        QTest.mouseRelease(view,Qt.MouseButton.LeftButton,pos=self.point(view,12000))
        self.assertEqual(doc.metadata,before)
        self.assertIsNone(view._marker_drag)
        np.testing.assert_array_equal(doc.read(),self.data);self.error.assert_not_called()

    def test_session_flags_keep_clips_and_can_be_placed_beyond_the_last_clip(self):
        window=self.window;window.session.import_audio([(self.data,8000,'Source')]);window.set_mode('multitrack')
        item=self.add(24000);session=window.session;tracks=session.tracks
        self.assertEqual(item.start,24000)
        self.assertEqual(session.frames,20000)
        view=window.multitrack.timeline;view.fit();self.app.processEvents()
        QTest.mousePress(view,Qt.MouseButton.LeftButton,pos=self.point(view,item.start))
        QTest.mouseMove(view,self.point(view,30000),5)
        QTest.mouseRelease(view,Qt.MouseButton.LeftButton,pos=self.point(view,30000))
        self.assertLess(abs(markers.for_model(session)[0].start-30000),80)
        self.assertEqual(session.tracks,tracks)
        session.undo();self.assertEqual(markers.for_model(session)[0].start,24000)
        self.error.assert_not_called()

    def test_list_rebinds_to_current_model_and_blocks_changes_while_recording(self):
        window=self.window;self.add(1000);window.open_markers();dialog=window.marker_dialog
        self.assertEqual(dialog.table.rowCount(),1)
        window.session.import_audio([(self.data,8000,'Source')]);window.set_mode('multitrack')
        self.assertEqual(dialog.table.rowCount(),0)
        item=self.add(4000);self.assertEqual(dialog.table.rowCount(),1)
        before=window.session.metadata
        window._record_context={};window.update_recording_actions()
        self.assertFalse(dialog.add_button.isEnabled());self.assertFalse(dialog.table.isEnabled())
        window.remove_marker(item.key);window.move_marker(item.key,7000);window.add_marker()
        self.assertEqual(window.session.metadata,before)
        window._record_context=None;window.refresh()
        self.assertTrue(dialog.table.isEnabled())
        window.set_mode('waveform');self.assertEqual(dialog.table.rowCount(),1)
        self.assertEqual(markers.for_model(window.document)[0].start,1000)

    def test_list_names_are_literal_during_language_switch_and_goto_changes_no_audio(self):
        window=self.window;item=self.add(15000)
        window.edit(lambda:window.document.set_marker_metadata(markers.edit(window.document.metadata,8000,20000,item.key,name='Normalize'),'Edit Marker'))
        window.open_markers();dialog=window.marker_dialog
        for code in ('nl','de','fr','es','en'):
            self.language.set_language(code,False);self.app.processEvents()
            self.assertEqual(dialog.table.item(0,0).text(),'Normalize')
            self.assertEqual(dialog.windowTitle(),tr('Marker List'))
        window.waveform.set_view(0,4000)
        history=len(window.document.undo_stack);dialog.go()
        self.assertEqual(window.document.cursor,15000)
        self.assertTrue(window.waveform.view_start<=15000<window.waveform.view_end)
        self.assertEqual(len(window.document.undo_stack),history)
        np.testing.assert_array_equal(window.document.read(),self.data)

    def test_marker_list_closes_with_main_window(self):
        self.add();self.window.open_markers();dialog=self.window.marker_dialog
        self.window.document.mark_saved();self.window.session.mark_saved();self.window.close()
        self.assertFalse(dialog.isVisible())

    def test_properties_validate_exact_frame_without_changing_the_model(self):
        item=self.add();model=self.window.document;before=model.metadata
        dialog=MarkerDialog(model,item,self.window);self.dialogs.append(dialog)
        dialog.frame.setText('invalid')
        with patch('soundsausage.marker_ui.QMessageBox.warning') as warning:
            dialog.accept();warning.assert_called_once()
        self.assertNotEqual(dialog.result(),QDialog.DialogCode.Accepted)
        self.assertEqual(model.metadata,before)

    def test_marker_dialogs_render_with_larger_font_in_five_languages(self):
        self.add();self.window.open_markers();listing=self.window.marker_dialog
        dialog=MarkerDialog(self.window.document,markers.for_model(self.window.document)[0],self.window)
        self.dialogs.append(dialog)
        font=QFont(self.window.font());font.setPointSize(14)
        for widget in (dialog,listing):widget.setFont(font);widget.show()
        for code in ('nl','de','fr','es','en'):
            self.language.set_language(code,False);self.app.processEvents()
            self.assertFalse(dialog.grab().isNull());self.assertFalse(listing.grab().isNull())
            self.assertGreaterEqual(dialog.width(),dialog.minimumWidth())

    def test_supported_marker_export_does_not_request_loss_permission(self):
        item=self.add();doc=self.window.document
        doc.extra_chunks=('cue ','LIST')
        with patch('soundsausage.window.QMessageBox.question') as question:
            self.assertTrue(self.window._metadata_permission('mp3_192'))
        question.assert_not_called()

    def test_mixdown_exports_only_session_markers_and_refusing_loss_keeps_existing_file(self):
        window=self.window;doc=window.document
        doc.metadata,_=markers.add((),8000,doc.frames,1000,'Source marker')
        window.insert_waveform();self.add(4000)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'mix.wav'
            with patch.object(window,'_save_path',return_value=(path,'float32')):window.mixdown()
            self.assertEqual([(m.start,m.name) for m in markers.read(read_wav(path).metadata,8000)],[(4000,'Marker 1')])
            window.session.metadata+=((b'abcd',b'Unmapped information'),)
            target=Path(folder)/'mix.mp3';target.write_bytes(b'existing recording')
            with patch.object(window,'_save_path',return_value=(target,'mp3_192')),patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.No):
                window.mixdown()
            self.assertEqual(target.read_bytes(),b'existing recording')
        self.error.assert_not_called()
