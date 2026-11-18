"""New waveforms contain the requested silence and replace work only on success."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QDoubleSpinBox, QSpinBox

from soundsausage.audio import read_wav, write_wav
from soundsausage.document import Document
from soundsausage.errors import AudioError, OperationCancelled
from soundsausage.window import MainWindow


class NewWaveformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.window = MainWindow(no_audio=True, ui_settings=QSettings(
            str(Path(self.folder.name) / 'ui.ini'), QSettings.Format.IniFormat))

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.folder.cleanup()

    def choose(self, rate=44100, channels=2, duration=10, accept=True):
        def execute(dialog):
            dialog.findChild(QSpinBox).setValue(rate)
            dialog.findChild(QComboBox).setCurrentIndex(channels - 1)
            field = dialog.findChild(QDoubleSpinBox)
            self.assertEqual(field.value(), 10)
            self.assertGreater(field.minimum(), 0)
            field.setValue(duration)
            return QDialog.DialogCode.Accepted if accept else QDialog.DialogCode.Rejected
        return patch('soundsausage.window.QDialog.exec', execute)

    def test_requested_rate_channels_and_duration_create_saveable_silence(self):
        w = self.window
        for rate, channels, duration in ((44100, 2, .137), (11025, 1, .001), (48000, 2, 24)):
            with self.subTest(rate=rate, channels=channels, duration=duration):
                w.document.mark_saved()
                with self.choose(rate, channels, duration):
                    w.new_document()
                doc = w.document
                self.assertEqual(doc.frames, round(rate * duration))
                self.assertEqual(doc.sample_rate, rate)
                self.assertEqual(doc.channels, channels)
                self.assertEqual(doc.selected_channels, tuple(range(channels)))
                self.assertFalse(doc.selected)
                self.assertTrue(doc.dirty)
                self.assertIsNone(doc.path)
                self.assertTrue(w.actions['save'].isEnabled())
                self.assertTrue(w.actions['close_file'].isEnabled())
                self.assertFalse(w.actions['invert'].isEnabled())
                self.assertEqual(np.count_nonzero(doc.view()), 0)
                path = Path(self.folder.name) / 'new.wav'
                write_wav(path, doc.view(), rate, 'pcm16')
                audio = read_wav(path)
                self.assertEqual(audio.sample_rate, rate)
                np.testing.assert_array_equal(audio.samples, doc.view())
                doc.undo()
                self.assertEqual(doc.frames, 0)
                doc.redo()
                self.assertEqual(doc.frames, round(rate * duration))

    def test_cancel_and_discard_refusal_keep_the_current_document(self):
        w = self.window
        original = Document(np.full((100, 2), .25, np.float32), 1000)
        w.document = original
        with self.choose(accept=False), patch.object(w.player, 'stop') as stop:
            w.new_document()
            self.assertIs(w.document, original)
            stop.assert_not_called()
        with patch.object(w, '_confirm_discard', return_value=False), patch('soundsausage.window.QDialog.exec') as execute:
            w.new_document()
            self.assertIs(w.document, original)
            execute.assert_not_called()
        np.testing.assert_array_equal(original.view(), .25)

    def test_storage_error_and_cancellation_do_not_discard_existing_audio(self):
        w = self.window
        original = Document(np.full((100, 2), .25, np.float32), 1000)
        w.document = original
        for error in (AudioError('disk full'), OperationCancelled()):
            with self.subTest(error=type(error).__name__), self.choose(), patch(
                    'soundsausage.window.storage.allocate', side_effect=error), patch.object(w, 'error') as report, patch.object(w.player, 'stop') as stop:
                w.new_document()
                self.assertIs(w.document, original)
                np.testing.assert_array_equal(original.view(), .25)
                stop.assert_not_called()
                self.assertEqual(report.call_count, 0 if isinstance(error, OperationCancelled) else 1)
