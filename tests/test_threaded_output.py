"""Thread affinity and continued PCM delivery while the GUI cannot process events."""
import threading
import time
import unittest

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtMultimedia import QAudioFormat
from PySide6.QtWidgets import QApplication

from soundsausage.audio_output import ThreadedOutput, QtAudio


class ConsumingSink(QObject):
    stateChanged = Signal(object)
    calls = []
    received = bytearray()
    def __init__(self, device, fmt, parent):
        super().__init__(parent)
        self._state = QtAudio.State.StoppedState
        self.queued = self.us = 0
        self.timer = QTimer(self)
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.consume)
        self.record('construct')
    def record(self, name): self.calls.append((name, threading.get_ident()))
    def setBufferSize(self, size): self.record('buffer')
    def bytesFree(self): self.record('free'); return 800-self.queued
    def state(self): self.record('state'); return self._state
    def error(self): self.record('error'); return QtAudio.Error.NoError
    def processedUSecs(self): self.record('clock'); return self.us
    def transition(self, state): self._state=state; self.stateChanged.emit(state)
    def start(self):
        self.record('start'); self.transition(QtAudio.State.IdleState);self.timer.start();return self
    def write(self, data):
        self.record('write'); count=min(len(data),self.bytesFree());self.received.extend(data[:count]);self.queued+=count
        self.transition(QtAudio.State.ActiveState);return count
    def consume(self):
        if self._state!=QtAudio.State.SuspendedState:
            self.queued=max(0,self.queued-400);self.us+=5000
            if not self.queued:self.transition(QtAudio.State.IdleState)
    def suspend(self): self.record('pause');self.transition(QtAudio.State.SuspendedState)
    def resume(self): self.record('resume');self.transition(QtAudio.State.ActiveState)
    def reset(self): self.record('reset');self.timer.stop();self.transition(QtAudio.State.StoppedState)


class ThreadedOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        ConsumingSink.calls=[];ConsumingSink.received=bytearray()
        self.data=bytes(range(256))*500
        self.output=ThreadedOutput(None,QAudioFormat(),None,lambda:self.data,sink_factory=ConsumingSink)
        self.output.setBufferSize(800)
    def tearDown(self):
        self.output.reset();self.output.deleteLater();self.app.processEvents()

    def test_gui_stall_does_not_stop_delivery_and_all_sink_calls_belong_to_one_worker(self):
        self.assertIs(self.output.start(),self.output)
        first=self.output.sent
        time.sleep(.2)  # No GUI events or Playback._feed calls.
        self.output.suspend()
        self.assertGreater(self.output.sent,first+1600)
        self.assertEqual(bytes(ConsumingSink.received),self.data[:self.output.sent])
        threads={identity for _,identity in ConsumingSink.calls}
        self.assertEqual(len(threads),1)
        self.assertNotIn(threading.get_ident(),threads)
        self.assertGreater(self.output.processedUSecs(),20000)

    def test_pause_freezes_clock_and_resume_continues_at_the_same_pcm_offset(self):
        self.output.start();time.sleep(.04);self.output.suspend()
        position=self.output.sent;clock=self.output.processedUSecs()
        time.sleep(.04)
        self.assertEqual(self.output.sent,position);self.assertEqual(self.output.processedUSecs(),clock)
        self.output.resume();time.sleep(.04)
        self.output.suspend()
        self.assertGreater(self.output.sent,position)
        self.assertEqual(bytes(ConsumingSink.received),self.data[:self.output.sent])

    def test_reset_joins_worker_and_restart_uses_the_new_payload(self):
        self.output.start();time.sleep(.03);thread=self.output.output_thread;self.output.reset()
        self.assertFalse(thread.isRunning())
        self.data=b'fresh-payload'*10000;ConsumingSink.received=bytearray()
        self.output.start();time.sleep(.03);self.output.suspend()
        self.assertEqual(bytes(ConsumingSink.received),self.data[:self.output.sent])

    def test_write_failure_is_reported_and_worker_can_still_be_joined(self):
        class Rejected(ConsumingSink):
            def write(self, data): raise OSError('fixture rejected PCM')
        self.output.sink_factory=Rejected
        self.output.start()
        self.assertEqual(self.output.clock.failure,'fixture rejected PCM')
        self.assertEqual(self.output.error(),QtAudio.Error.IOError)
