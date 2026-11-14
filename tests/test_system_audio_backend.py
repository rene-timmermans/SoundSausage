"""Real output monitor recording on the CI jobs' private PulseAudio server."""
import os
import unittest
from PySide6.QtWidgets import QApplication
from soundsausage.selftest import run_system_audio


@unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_AUDIO_TEST')=='1','Explicit private audio server required')
class SystemAudioBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_default_monitor_records_distinct_output_channels_at_two_rates(self):
        for rate in (44100,48000):
            with self.subTest(rate=rate):run_system_audio(rate=rate)
