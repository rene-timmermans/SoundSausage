"""Real Qt/PulseAudio loopback calibration and automatically aligned overdub."""
import os
import time
import unittest
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from soundsausage.window import MainWindow
from soundsausage.calibration_ui import CalibrationDialog
from soundsausage.synchronization import calibration_probe,measure_latency
from soundsausage.session import Session
from test_playback import MemorySettings


@unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_AUDIO_TEST')=='1','Explicit private loopback audio backend required')
class SynchronizationBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_real_loopback_calibration_aligns_a_new_recording(self):
        window=MainWindow(no_audio=False);window.audio_devices.settings=MemorySettings();dialog=None
        errors=[];window.recorder.failed.connect(errors.append);window.player.failed.connect(errors.append)
        try:
            inputs=window.audio_devices.inputs();outputs=window.audio_devices.outputs()
            incoming=next((d for d in inputs if b'soundsausage_loopback' in bytes(d.id())),None)
            outgoing=next((d for d in outputs if b'soundsausage_test' in bytes(d.id())),None)
            self.assertIsNotNone(incoming,[(bytes(d.id()),d.description()) for d in inputs])
            self.assertIsNotNone(outgoing,[(bytes(d.id()),d.description()) for d in outputs])
            window.audio_devices.configure(bytes(outgoing.id()).hex(),80,bytes(incoming.id()).hex())
            dialog=CalibrationDialog(window,rate=48000);dialog.start_calibration()
            deadline=time.monotonic()+12
            while dialog._running and time.monotonic()<deadline:QTest.qWait(20)
            self.assertIsNotNone(dialog.calibration_result,dialog.status.text())
            self.assertGreater(dialog.calibration_result['confidence'],.9)
            probe,markers=calibration_probe(48000)
            window.session=Session(48000,2);window.session.import_audio([(probe,48000,'Loopback reference')])
            window.session.selected_track=window.session.tracks[1].id;window.set_mode('multitrack');window.session.select(0,0)
            self.assertTrue(window.start_recording(target='multitrack',rate=48000,channels=2,accompaniment=True,automatic_sync=True,skip_start_ms=50))
            deadline=time.monotonic()+4.2
            while time.monotonic()<deadline:QTest.qWait(20)
            window.stop_recording();self.assertFalse(errors)
            clip=window.session.tracks[1].clips[0]
            measured=measure_latency(window.session.media[clip.media_id].samples,markers,48000,clip.start)
            self.assertLess(abs(measured['offset_ms']),10,measured)
        finally:
            if dialog is not None:dialog.reject();dialog.deleteLater()
            if window.recorder.active:window.recorder.stop(keep=False)
            window.player.stop();window.document.mark_saved();window.session.mark_saved();window.close();window.deleteLater();self.app.processEvents()
