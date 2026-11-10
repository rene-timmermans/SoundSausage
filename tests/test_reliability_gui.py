from pathlib import Path
import os
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QProgressDialog,QMessageBox

from soundsausage.document import Document
from soundsausage.window import MainWindow

ROOT=Path(__file__).resolve().parents[1]


class ReliabilityGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build')
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':self.folder.name})
        self.env.start()
        self.window=MainWindow(Document(np.ones((3000,2),np.float32),48000),no_audio=True)

    def tearDown(self):
        self.window.document.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater();self.app.processEvents()
        self.env.stop();self.folder.cleanup()

    def test_cancel_button_preserves_model_without_showing_an_error(self):
        ticks=iter(range(10000));dialogs=[]
        def dialog(*args):
            result=QProgressDialog(*args);dialogs.append(result)
            QTimer.singleShot(0,result.cancel)
            return result
        before=(self.window.document._pieces,self.window.document.revision)
        with patch('soundsausage.progress_ui.time',SimpleNamespace(monotonic=lambda:next(ticks))),patch('soundsausage.progress_ui.QProgressDialog',side_effect=dialog),patch.object(self.window,'error') as error:
            self.window.effect('invert')
        self.assertTrue(dialogs)
        self.assertEqual((self.window.document._pieces,self.window.document.revision),before)
        # Cancellation reaches the shared error adapter as a typed cancellation,
        # which quietly displays status text instead of an error dialog.
        if error.called:
            from soundsausage.errors import OperationCancelled
            self.assertIsInstance(error.call_args.args[1],OperationCancelled)
        self.assertEqual(self.window.document.undo_stack,[])

    def test_recovery_is_updated_after_edit_and_removed_after_save_or_confirmed_close(self):
        self.window.enable_recovery(offer=False)
        journal=self.window.recovery.path
        self.assertFalse(journal.exists())
        self.window.effect('invert');self.assertTrue(journal.exists())
        path=Path(self.folder.name)/'saved.wav'
        with patch.object(self.window,'_save_path',return_value=(path,'float32')):
            self.assertTrue(self.window.save_waveform())
        self.assertFalse(journal.exists());self.assertTrue(path.exists())
        self.window.effect('invert');self.assertTrue(journal.exists())
        with patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.Discard):
            self.window.close()
        self.assertFalse(journal.exists())

    def test_scrollbar_reaches_beyond_32bit_frame_positions(self):
        with patch.object(Document,'frames',new=property(lambda self:5_000_000_000)):
            self.window.view_changed(4_000_000_000,4_000_100_000)
            self.assertLessEqual(self.window.scroll.maximum(),2147483647)
            self.window.scroll_view(self.window.scroll.maximum())
            self.assertGreater(self.window.waveform.view_start,4_900_000_000)


if __name__=='__main__':unittest.main()
