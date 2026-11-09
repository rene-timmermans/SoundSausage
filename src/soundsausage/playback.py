"""Nonblocking playback adapter. Only its own ffplay child is controlled."""
import os
import shutil
import signal

import numpy as np
from PySide6.QtCore import QObject, QProcess, QTimer, QElapsedTimer, Signal


class Playback(QObject):
    position = Signal(object)
    state_changed = Signal(str)
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.state = "Stopped"
        self.loop = False
        self._data = None
        self._buffer = None
        self._sent = 0
        self._closed_input = False
        self._rate = 44100
        self._start_frame = 0
        self._elapsed_before_pause = 0
        self._clock = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)

    def _set_state(self, state):
        self.state = state
        self.state_changed.emit(state)

    def play(self, samples, rate, start_frame=0):
        self.stop()
        executable = shutil.which("ffplay")
        if not executable:
            self.failed.emit("Playback needs ffplay, which was not found on PATH.")
            return
        if len(samples) == 0:
            return
        self._data = np.ascontiguousarray(samples, dtype="<f4")
        self._buffer = memoryview(self._data).cast("B")
        self._rate = rate
        self._start_frame = start_frame
        self._sent = 0
        self._closed_input = False
        self._elapsed_before_pause = 0
        proc = QProcess(self)
        self.process = proc
        proc.setProgram(executable)
        proc.setArguments(["-nodisp", "-autoexit", "-loglevel", "error", "-f", "f32le",
            "-ar", str(rate), "-ch_layout", "mono" if samples.shape[1] == 1 else "stereo", "-i", "pipe:0"])
        proc.started.connect(lambda: self._started(proc))
        proc.bytesWritten.connect(lambda _: self._feed(proc))
        proc.finished.connect(lambda code, status: self._finished(proc, code))
        proc.errorOccurred.connect(lambda error: self._error(proc, error))
        self._set_state("Starting")
        proc.start()

    def _started(self, proc):
        if proc is not self.process:
            return
        self._clock.start()
        self._timer.start()
        self._set_state("Playing")
        self._feed(proc)

    def _feed(self, proc):
        if proc is not self.process or self._buffer is None or self._closed_input:
            return
        while proc.bytesToWrite() < 262144 and self._sent < len(self._buffer):
            end = min(len(self._buffer), self._sent + 65536)
            written = proc.write(bytes(self._buffer[self._sent:end]))
            if written <= 0:
                return
            self._sent += written
        if self._sent == len(self._buffer):
            self._closed_input = True
            proc.closeWriteChannel()

    def _tick(self):
        if self.state != "Playing" or self._data is None:
            return
        elapsed = self._elapsed_before_pause + self._clock.elapsed()
        offset = min(len(self._data), round(elapsed * self._rate / 1000))
        self.position.emit(self._start_frame + offset)

    def meter_samples(self, frame):
        if self._data is None:
            return None
        end = max(0, min(len(self._data), int(frame) - self._start_frame))
        start = max(0, end - self._rate // 30)
        return self._data[start:end]

    def toggle_pause(self):
        if self.process is None or self.process.processId() <= 0:
            return
        try:
            if self.state == "Playing":
                os.kill(self.process.processId(), signal.SIGSTOP)
                self._elapsed_before_pause += self._clock.elapsed()
                self._set_state("Paused")
            elif self.state == "Paused":
                os.kill(self.process.processId(), signal.SIGCONT)
                self._clock.restart()
                self._set_state("Playing")
        except ProcessLookupError:
            self.stop()

    def _error(self, proc, error):
        if proc is self.process and error == QProcess.ProcessError.FailedToStart:
            message = proc.errorString()
            self.stop()
            self.failed.emit(message)

    def _finished(self, proc, code):
        if proc is not self.process:
            proc.deleteLater()
            return
        message = bytes(proc.readAllStandardError()).decode("utf-8", "replace").strip()
        data, rate, start = self._data, self._rate, self._start_frame
        looping = self.loop and code == 0
        self.process = None
        self._timer.stop()
        self._data = self._buffer = None
        self._set_state("Stopped")
        proc.deleteLater()
        if code != 0:
            self.failed.emit(message[-1200:] or "The audio player could not play this audio.")
        elif looping:
            self.play(data, rate, start)

    def stop(self):
        proc = self.process
        self.process = None
        self._timer.stop()
        if proc is not None:
            pid = proc.processId()
            if pid > 0:
                try:
                    if self.state == "Paused":
                        os.kill(pid, signal.SIGCONT)
                except ProcessLookupError:
                    pass
                proc.terminate()
                QTimer.singleShot(800, lambda: self._kill_if_running(proc))
            else:
                proc.kill()
                if proc.state() == QProcess.ProcessState.NotRunning:
                    proc.deleteLater()
        self._data = self._buffer = None
        self._set_state("Stopped")

    @staticmethod
    def _kill_if_running(proc):
        try:
            if proc.state() != QProcess.ProcessState.NotRunning:
                proc.kill()
        except RuntimeError:
            pass

    def shutdown(self):
        proc = self.process
        self.stop()
        if proc is not None and not proc.waitForFinished(1000):
            proc.kill()
            proc.waitForFinished(500)
