"""Real Qt output against the CI job's private null sink; never host audio."""
from contextlib import redirect_stderr
import io
import os
import time
import unittest

import numpy as np
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.playback import Playback


@unittest.skipUnless(os.environ.get("SOUNDSAUSAGE_AUDIO_TEST") == "1", "private virtual audio server not enabled")
class AudioBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._callback_errors=io.StringIO()
        self._capture_stderr=redirect_stderr(self._callback_errors)
        self._capture_stderr.__enter__()

    def tearDown(self):
        self._capture_stderr.__exit__(None,None,None)
        self.assertNotIn('TypeError:',self._callback_errors.getvalue(),self._callback_errors.getvalue())

    def wait_for(self, predicate, seconds=7, diagnostic=None):
        deadline = time.monotonic() + seconds
        while not predicate() and time.monotonic() < deadline:
            QTest.qWait(10)
        self.assertTrue(predicate(), "Audio backend did not reach the expected state: " + str(diagnostic() if diagnostic else ""))

    def test_real_output_clock_pause_resume_and_completion_at_two_rates(self):
        for rate, channels in ((44100, 2), (48000, 1)):
            with self.subTest(rate=rate, channels=channels):
                player, errors, positions = Playback(), [], []
                player.failed.connect(errors.append)
                player.position.connect(positions.append)
                try:
                    data = np.zeros((rate // 2, channels), np.float32)
                    player.play(data, rate, 317)
                    self.assertEqual(player.state, "Playing", errors)
                    self.wait_for(lambda: positions and positions[-1] > 317)
                    player.toggle_pause()
                    self.assertEqual(player.state, "Paused")
                    frozen = positions[-1]
                    QTest.qWait(80)
                    self.assertEqual(positions[-1], frozen)
                    player.toggle_pause()
                    self.wait_for(lambda: positions[-1] > frozen, diagnostic=lambda: dict(
                        state=player.state, sink=player.sink.state() if player.sink else None,
                        timer=player._timer.isActive(), sent=player._sent, payload=len(player._payload), errors=errors))
                    self.assertEqual(player.state, "Playing")
                    self.wait_for(lambda: player.state == "Stopped")
                    self.assertFalse(errors, errors)
                    self.assertEqual(positions[-1], 317 + len(data))
                    self.assertEqual(positions, sorted(positions))
                finally: player.shutdown(); player.deleteLater()

    def test_real_loop_stop_and_stale_callbacks_do_not_restart_output(self):
        player, errors, positions = Playback(), [], []
        player.failed.connect(errors.append); player.position.connect(positions.append)
        player.loop = True
        try:
            player.play(np.zeros((2400, 2), np.float32), 48000, 23)
            self.wait_for(lambda: sum(p == 23 for p in positions) >= 3, diagnostic=lambda: dict(
                state=player.state, sink=player.sink.state() if player.sink else None,
                processed=player.sink.processedUSecs() if player.sink else None,
                sent=player._sent, payload=len(player._payload), positions=positions[-10:], errors=errors))
            player.stop()
            QTest.qWait(100)
            self.assertEqual(player.state, "Stopped")
            self.assertIsNone(player.sink)
            self.assertFalse(errors, errors)
        finally: player.shutdown(); player.deleteLater()
