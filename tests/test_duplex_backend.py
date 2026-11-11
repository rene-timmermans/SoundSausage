"""Explicit CI loop with a private PulseAudio source/sink; never opens host audio by default."""
import os
import unittest
from PySide6.QtWidgets import QApplication
from soundsausage.window import MainWindow
from soundsausage.selftest import run_duplex


@unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_AUDIO_TEST')=='1','Explicit virtual audio backend required')
class DuplexBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def check_duplex(self,rate):
        window=MainWindow(no_audio=True)
        try:run_duplex(window,rate)
        finally:
            window.document.mark_saved();window.session.mark_saved();window.close();window.deleteLater();self.app.processEvents()
    def test_simultaneous_output_capture_and_linked_pause(self):self.check_duplex(48000)
    def test_different_input_session_rates_keep_the_overdub(self):self.check_duplex(44100)
