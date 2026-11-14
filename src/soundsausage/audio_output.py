"""Own the Qt sink and bounded PCM writes on a dedicated event-loop thread."""
from concurrent.futures import Future
from dataclasses import dataclass

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtMultimedia import QAudioSink
try:
    from PySide6.QtMultimedia import QtAudio
except ImportError:
    from PySide6.QtMultimedia import QAudio as QtAudio


@dataclass
class OutputClock:
    state: object = QtAudio.State.StoppedState
    error: object = QtAudio.Error.NoError
    processed: int = 0
    sent: int = 0
    failure: str = ''


class OutputWorker(QObject):
    changed = Signal()

    def __init__(self, device, fmt, clock, sink_factory):
        super().__init__()
        self.device, self.format, self.clock = device, fmt, clock
        self.sink_factory = sink_factory
        self.sink = self.io = self.payload = None
        self.feeding = False
        self.timer = QTimer(self)
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.feed)

    def sample_clock(self):
        if self.sink is not None:
            self.clock.processed = max(0, self.sink.processedUSecs())
            if not self.clock.failure:
                self.clock.state = self.sink.state()
                self.clock.error = self.sink.error()

    @Slot()
    def state_changed(self):
        self.sample_clock()
        self.changed.emit()

    @Slot()
    def feed(self):
        if self.sink is None or self.io is None or self.feeding:
            return
        if self.sink.state() == QtAudio.State.SuspendedState:
            return
        self.feeding = True
        try:
            count = min(len(self.payload)-self.clock.sent, self.sink.bytesFree(), 65536)
            if count > 0:
                data = self.payload[self.clock.sent:self.clock.sent+count]
                written = self.io.write(data) if data else 0
                if written < 0:
                    raise OSError('The audio device rejected playback data.')
                self.clock.sent += written
            self.sample_clock()
        except (ValueError, OSError, RuntimeError) as error:
            self.clock.failure = str(error)
            self.clock.error = QtAudio.Error.IOError
            self.clock.state = QtAudio.State.StoppedState
            self.timer.stop()
            self.changed.emit()
        finally:
            self.feeding = False

    @Slot(object)
    def command(self, request):
        name, value, result = request
        try:
            if name == 'start':
                payload, size = value
                self.payload = payload
                self.clock.sent = self.clock.processed = 0
                self.clock.failure = ''
                self.sink = self.sink_factory(self.device, self.format, self)
                self.sink.setBufferSize(size)
                self.sink.stateChanged.connect(self.state_changed)
                self.io = self.sink.start()
                self.feed()
                self.sample_clock()
                if self.io is not None and not self.clock.failure:
                    self.timer.start()
                result.set_result(self.io is not None and not self.clock.failure)
            elif name == 'suspend':
                self.timer.stop()
                self.sink.suspend()
                self.sample_clock()
                result.set_result(None)
            elif name == 'resume':
                self.sink.resume()
                self.feed()
                self.timer.start()
                result.set_result(None)
            elif name == 'stop':
                self.timer.stop()
                if self.sink is not None:
                    self.sink.reset()
                    self.sink.deleteLater()
                self.sink = self.io = self.payload = None
                self.clock.state = QtAudio.State.StoppedState
                result.set_result(None)
            else:
                raise ValueError(name)
        except (ValueError, OSError, RuntimeError) as error:
            result.set_exception(error)


class ThreadedOutput(QObject):
    """A GUI-owned sink facade; Qt audio objects are only touched by their owner."""
    stateChanged = Signal(object)
    _command = Signal(object)

    def __init__(self, device, fmt, parent, payload_factory, sink_factory=QAudioSink):
        super().__init__(parent)
        self.device, self.format = device, fmt
        self.payload_factory, self.sink_factory = payload_factory, sink_factory
        self.clock = OutputClock()
        self.size = 0
        self.worker = self.output_thread = None

    def setBufferSize(self, size): self.size = size
    def state(self): return self.clock.state
    def error(self): return self.clock.error
    def processedUSecs(self): return self.clock.processed
    @property
    def sent(self): return self.clock.sent

    @Slot()
    def _changed(self):
        self.stateChanged.emit(self.clock.state)

    def _invoke(self, name, value=None):
        result = Future()
        self._command.emit((name, value, result))
        try:
            return result.result(timeout=15)
        except TimeoutError as error:
            raise RuntimeError('The audio output could not start. Check the selected device in Options → Audio Hardware.') from error

    def start(self):
        self.clock = OutputClock()
        self.output_thread = QThread(self)
        self.worker = OutputWorker(self.device, self.format, self.clock, self.sink_factory)
        self.worker.moveToThread(self.output_thread)
        self._command.connect(self.worker.command, Qt.ConnectionType.QueuedConnection)
        self.worker.changed.connect(self._changed, Qt.ConnectionType.QueuedConnection)
        self.output_thread.finished.connect(self.worker.deleteLater)
        self.output_thread.start()
        return self if self._invoke('start', (self.payload_factory(), self.size)) else None

    def suspend(self): self._invoke('suspend')
    def resume(self): self._invoke('resume')

    def reset(self):
        if self.output_thread is None:
            return
        thread = self.output_thread
        try:
            self._invoke('stop')
        finally:
            self._command.disconnect(self.worker.command)
            thread.quit()
            thread.wait()
            self.worker = self.output_thread = None
            thread.deleteLater()
