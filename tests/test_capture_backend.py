"""Real Qt capture against the CI job's private source; never host microphones."""
from contextlib import redirect_stderr
import io
import os
import time
import unittest

import numpy as np
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.capture import Recorder


@unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_AUDIO_TEST')=='1','private virtual audio server not enabled')
class CaptureBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self._callback_errors=io.StringIO()
        self._capture_stderr=redirect_stderr(self._callback_errors)
        self._capture_stderr.__enter__()

    def tearDown(self):
        self._capture_stderr.__exit__(None,None,None)
        self.assertNotIn('TypeError:',self._callback_errors.getvalue(),self._callback_errors.getvalue())

    def wait_for(self,predicate,seconds=8,diagnostic=None):
        deadline=time.monotonic()+seconds
        while not predicate() and time.monotonic()<deadline:QTest.qWait(10)
        self.assertTrue(predicate(),'Capture backend did not reach the expected state; '+str(diagnostic() if diagnostic else '')+'; callbacks: '+self._callback_errors.getvalue())
    @staticmethod
    def status(recorder):
        return dict(state=recorder.state,native=recorder.source.state() if recorder.source else None,
                    source_bytes=recorder.source.bytesAvailable() if recorder.source else None,
                    io_bytes=recorder._io.bytesAvailable() if recorder._io else None,
                    frames=recorder.take.frames if recorder.take else None,
                    format=(recorder.format.sampleRate(),recorder.format.channelCount(),recorder.format.sampleFormat()) if recorder.format else None)

    def test_real_input_duration_pause_resume_and_complete_frames_at_two_rates(self):
        for rate,channels in ((44100,1),(48000,2)):
            with self.subTest(rate=rate,channels=channels):
                recorder=Recorder();takes=[];errors=[];frames=[]
                recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
                recorder.samples.connect(lambda data,count:frames.append(count))
                try:
                    self.assertTrue(recorder.start(rate,channels),errors)
                    self.wait_for(lambda:frames and frames[-1]>recorder.format.sampleRate()//10,diagnostic=lambda:self.status(recorder))
                    recorder.toggle_pause();self.assertEqual(recorder.state,'Paused')
                    frozen=frames[-1];QTest.qWait(120);self.assertEqual(frames[-1],frozen)
                    recorder.toggle_pause();self.wait_for(lambda:frames[-1]>frozen)
                    recorder.stop();self.assertFalse(errors,errors);self.assertEqual(len(takes),1)
                    self.assertEqual(takes[0].samples.shape,(frames[-1],channels))
                    self.assertTrue(np.isfinite(takes[0].samples).all())
                    self.assertEqual(frames,sorted(frames))
                finally:
                    recorder.stop(keep=False)
                    for take in takes:take.discard()
                    recorder.deleteLater();self.app.processEvents()
    def test_real_input_auto_stop_and_cancel_do_not_leave_an_active_microphone(self):
        recorder=Recorder();takes=[];errors=[]
        recorder.finished.connect(takes.append);recorder.failed.connect(errors.append)
        try:
            self.assertTrue(recorder.start(48000,2,limit_seconds=.15),errors)
            expected=round(.15*recorder.format.sampleRate())
            self.wait_for(lambda:recorder.state=='Stopped',diagnostic=lambda:self.status(recorder))
            self.assertEqual(takes[0].frames,expected);self.assertIsNone(recorder.source)
            self.assertTrue(recorder.start(48000,1),errors)
            self.wait_for(lambda:recorder.take is not None and recorder.take.frames>0)
            path=recorder.take.path;recorder.stop(keep=False)
            QTest.qWait(100);self.assertEqual(recorder.state,'Stopped')
            self.assertIsNone(recorder.source);self.assertFalse(path.exists());self.assertFalse(errors,errors)
        finally:
            recorder.stop(keep=False)
            for take in takes:take.discard()
            recorder.deleteLater();self.app.processEvents()
