"""Remaster A/B listening, cache invalidation, safe application and translations."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialog, QLabel

from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.i18n import install_language, tr
from soundsausage.remaster_ui import RemasterDialog
from soundsausage.window import MainWindow
from test_remaster import pumping


class RemasterGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.data=pumping(seconds=3);self.doc=Document(self.data,16000)
        settings=QSettings(str(Path(self.folder.name)/'ui.ini'),QSettings.Format.IniFormat)
        self.window=MainWindow(self.doc,no_audio=True,ui_settings=settings)
        self.dialog=RemasterDialog(self.doc,self.window,no_audio=True)
        self.language=install_language()
    def tearDown(self):
        self.language.set_language('en',False)
        self.dialog.close();self.dialog.deleteLater()
        self.doc.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater();self.app.processEvents()

    def test_preview_position_volume_match_and_source_preservation(self):
        self.dialog.position.setValue(1.5)
        original,processed=self.dialog.audition_samples()
        self.assertEqual(original.shape,(24000,2))
        self.assertAlmostEqual(float(np.mean(original.astype(float)**2)),float(np.mean(processed.astype(float)**2)),places=8)
        self.assertGreater(np.max(abs(original-processed)),.005)
        np.testing.assert_array_equal(self.doc.read(),self.data)
        self.assertEqual(self.doc.undo_stack,[])
        self.dialog.match.setChecked(False)
        raw_original,raw_processed=self.dialog.audition_samples()
        np.testing.assert_array_equal(raw_original,self.data[24000:])
        self.assertLessEqual(np.max(abs(raw_processed)),10**(-1/20)+1e-7)

    def test_analysis_cache_survives_ab_and_position_but_not_changed_parameters(self):
        with patch.object(self.doc,'_process_effect',wraps=self.doc._process_effect) as process:
            self.dialog.audition_samples()
            self.dialog.position.setValue(.5);self.dialog.match.setChecked(False)
            self.dialog.audition_samples();self.dialog.audition_samples()
            self.assertEqual(process.call_count,1)
            self.dialog.recovery.setValue(5);self.dialog.audition_samples()
            self.assertEqual(process.call_count,2)
            self.doc.select(8000,30000);self.dialog.audition_samples()
            self.assertEqual(process.call_count,3)

    def test_one_channel_preview_keeps_the_other_channel_and_selected_interval(self):
        self.doc.select(8000,40000);self.doc.select_channels((1,))
        self.dialog.position.setValue(.75);self.dialog.match.setChecked(False)
        original,processed=self.dialog.audition_samples()
        np.testing.assert_array_equal(original,self.data[12000:40000])
        np.testing.assert_array_equal(processed[:,0],original[:,0])
        self.assertGreater(np.max(abs(processed[:,1]-original[:,1])),.001)

    def test_ab_buttons_play_the_correct_samples_and_cancel_silently(self):
        self.dialog.no_audio=False
        with patch.object(self.dialog.player,'play') as play:
            self.dialog.original();self.assertEqual(self.dialog._kind,'original')
            first=play.call_args.args[0].copy()
            self.dialog.preview();self.assertEqual(self.dialog._kind,'processed')
            self.assertGreater(np.max(abs(first-play.call_args.args[0])),.001)
        with patch.object(self.dialog,'_processed',side_effect=OperationCancelled),patch('soundsausage.remaster_ui.QMessageBox.warning') as warning,patch.object(self.dialog.player,'play') as play:
            self.dialog.preview();play.assert_not_called();warning.assert_not_called()

    def test_accept_applies_one_undo_step_and_action_is_waveform_only(self):
        self.assertTrue(self.window.actions['remaster'].isEnabled())
        with patch.object(RemasterDialog,'exec',return_value=QDialog.DialogCode.Accepted):
            self.window.actions['remaster'].trigger()
        self.assertEqual(len(self.doc.undo_stack),1)
        self.assertEqual(self.doc.last_effect[0],'remaster')
        self.doc.undo();np.testing.assert_array_equal(self.doc.read(),self.data)
        self.window.insert_waveform()
        self.assertFalse(self.window.actions['remaster'].isEnabled())
        self.window.set_mode('waveform')
        self.assertTrue(self.window.actions['remaster'].isEnabled())

    def test_presets_layout_and_five_languages_with_larger_font(self):
        self.dialog.presets.setCurrentIndex(3)
        self.assertEqual(self.dialog.settings()['recovery_db'],6)
        self.dialog.amount.setValue(45);self.assertEqual(self.dialog.presets.currentIndex(),0)
        font=QFont(self.dialog.font());font.setPointSize(14);self.dialog.setFont(font)
        self.dialog.show()
        for code in ('nl','de','fr','es','en'):
            self.language.set_language(code,False);self.app.processEvents();self.dialog.adjustSize();self.app.processEvents()
            self.assertEqual(self.dialog.original_button.text(),tr('Original'))
            self.assertFalse(self.dialog.grab().isNull())
            self.assertTrue(self.dialog.rect().contains(self.dialog.button_box.geometry()))
            for label in self.dialog.findChildren(QLabel):
                if label.wordWrap():self.assertGreaterEqual(label.height()+2,label.heightForWidth(label.width()))
        self.assertFalse(self.dialog.preview_button.isEnabled())
        self.assertFalse(self.dialog.original_button.isEnabled())
