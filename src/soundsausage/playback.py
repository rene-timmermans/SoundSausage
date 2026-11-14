"""Qt audio output with a device clock and bounded writes, shared by previews."""
import sys

import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtMultimedia import QAudioSink, QAudioFormat
try:
    from PySide6.QtMultimedia import QtAudio
except ImportError:  # PySide6 6.8 retains the QAudio namespace name.
    from PySide6.QtMultimedia import QAudio as QtAudio

from .audio import AudioError, validate_audio
from .errors import OperationCancelled
from .audio_devices import AudioDevices
from .resample import resample
from . import storage


def output_format(device, rate, channels):
    preferred = device.preferredFormat()
    rates = dict.fromkeys((rate, preferred.sampleRate(), 48000, 44100))
    counts = dict.fromkeys((channels, preferred.channelCount(), 2, 1))
    types = dict.fromkeys((QAudioFormat.SampleFormat.Float, preferred.sampleFormat(),
                          QAudioFormat.SampleFormat.Int16, QAudioFormat.SampleFormat.Int32,
                          QAudioFormat.SampleFormat.UInt8))
    for r in rates:
        for count in counts:
            if not 1000 <= r <= 384000 or count not in (1, 2):
                continue
            for kind in types:
                if kind == QAudioFormat.SampleFormat.Unknown:
                    continue
                fmt = QAudioFormat()
                fmt.setSampleRate(r)
                fmt.setChannelCount(count)
                fmt.setSampleFormat(kind)
                if device.isFormatSupported(fmt):
                    return fmt
    raise AudioError("This output device does not support a usable mono or stereo format.")


def encode_output(samples, source_rate, fmt):
    data = samples if source_rate == fmt.sampleRate() else resample(samples, source_rate, fmt.sampleRate())
    if data.shape[1] != fmt.channelCount():
        data = data.mean(axis=1, keepdims=True) if fmt.channelCount() == 1 else np.repeat(data, 2, axis=1)
    data = np.clip(data, -1, 1)
    byteorder = "<" if sys.byteorder == "little" else ">"
    kind = fmt.sampleFormat()
    if kind == QAudioFormat.SampleFormat.Float:
        return data.astype(byteorder + "f4", copy=False).tobytes()
    if kind == QAudioFormat.SampleFormat.Int16:
        return np.clip(np.rint(data.astype(np.float64) * 32768), -32768, 32767).astype(byteorder + "i2").tobytes()
    if kind == QAudioFormat.SampleFormat.Int32:
        return np.clip(np.rint(data.astype(np.float64) * 2147483648), -2147483648, 2147483647).astype(byteorder + "i4").tobytes()
    return np.clip(np.rint(data * 128 + 128), 0, 255).astype(np.uint8).tobytes()


class EncodedAudio:
    """Byte-addressed output, encoding only the requested bounded block.

    Resampling is stateful and disk-backed before playback; slicing never
    materializes an entire PCM payload, including on short/partial writes.
    """
    def __init__(self, samples, rate, fmt):
        self.samples = samples if rate == fmt.sampleRate() else resample(samples,rate,fmt.sampleRate())
        self.format = fmt
        self.frame_bytes = fmt.bytesPerFrame()
        self._cache_start = 0
        self._cache = b""

    def __len__(self):
        return len(self.samples) * self.frame_bytes

    def __getitem__(self, item):
        start,stop,step = item.indices(len(self))
        if step != 1 or stop-start > 65536:
            raise ValueError("Audio writes must be sequential bounded byte ranges.")
        if not self._cache_start <= start <= stop <= self._cache_start + len(self._cache):
            first = start // self.frame_bytes
            last = min(len(self.samples), max((stop+self.frame_bytes-1)//self.frame_bytes, first+8192))
            self._cache = encode_output(self.samples[first:last],self.format.sampleRate(),self.format)
            self._cache_start = first * self.frame_bytes
            storage.release_pages(self.samples)
        offset = start-self._cache_start
        return self._cache[offset:offset+stop-start]


class Playback(QObject):
    position = Signal(object)
    state_changed = Signal(str)
    failed = Signal(str)

    def __init__(self, parent=None, devices=None, sink_factory=None):
        super().__init__(parent)
        self.devices = devices if devices is not None else AudioDevices(self)
        self._sink_factory = sink_factory or QAudioSink
        self.devices.changed.connect(self.stop)
        self.devices.outputs_changed.connect(self._outputs_changed)
        self.sink = None
        self._io = None
        self.state = "Stopped"
        self.loop = False
        self._data = None
        self._payload = b""
        self._sent = 0
        self._rate = 44100
        self._start_frame = self._last_frame = 0
        self._starting = False
        self._feeding = False
        self._generation = 0
        self._loop_pending = False
        self._pause_requested = False
        self._output_id = ""
        self.output_description = ""
        self.format = None
        self._stream_factory = None
        self._timer = QTimer(self)
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._tick)

    def _create_sink(self, device):
        if self._sink_factory is QAudioSink:
            from .audio_output import ThreadedOutput
            return ThreadedOutput(device, self.format, self, lambda: self._payload)
        return self._sink_factory(device, self.format, self)

    def _set_state(self, state):
        if self.state != state:
            self.state = state
            self.state_changed.emit(state)

    def play(self, samples, rate, start_frame=0):
        self.stop()
        try:
            validate_audio(samples, rate)
            if not len(samples):
                return
            if not isinstance(start_frame, int) or start_frame < 0:
                raise AudioError("Invalid playback position.")
            device = self.devices.output()
            self.format = output_format(device, rate, samples.shape[1])
            self._data = storage.freeze(samples)
            self._payload = EncodedAudio(self._data, rate, self.format)
            self._rate, self._start_frame, self._last_frame = rate, start_frame, start_frame
            self._output_id = bytes(device.id()).hex()
            self.output_description = device.description()
            self.sink = self._create_sink(device)
            sink = self.sink
            sink.setBufferSize(max(self.format.bytesPerFrame(), min(len(self._payload),
                                   self.format.bytesForDuration(self.devices.buffer_ms * 1000))))
            sink.stateChanged.connect(self._sink_changed)
            self._set_state("Starting")
            self._start_sink()
        except OperationCancelled:
            self.stop()
            raise
        except (ValueError, OSError, RuntimeError) as error:
            self._fail(str(error))

    def _start_sink(self):
        self._starting = True
        self._pause_requested = False
        self._sent = 0
        self._last_frame = self._start_frame
        try:
            self._io = self.sink.start()
        finally:
            self._starting = False
        if self._io is None or self.sink.error() not in (QtAudio.Error.NoError, QtAudio.Error.UnderrunError):
            self._fail("The audio output could not start. Check the selected device in Options → Audio Hardware.")
            return
        self._timer.start()
        self._set_state("Playing")
        self.position.emit(self._start_frame)
        self._feed()

    def play_session(self, session, start=0, end=None,*,punch=None):
        from .mixing import SessionStream
        from .streaming import StreamPayload
        self.stop()
        try:
            factory = lambda: SessionStream(session, start, end,punch=punch)
            device = self.devices.output()
            self.format = output_format(device, session.sample_rate, 2)
            self._rate = session.sample_rate
            self._start_frame = self._last_frame = start
            self._payload = StreamPayload(factory, self._rate, self.format)
            self._stream_factory = factory
            self._data = self._payload.stream
            if not len(self._data): self.stop(); return
            self._payload.wait_ready()
            self._output_id = bytes(device.id()).hex()
            self.output_description = device.description()
            self.sink = self._create_sink(device)
            self.sink.setBufferSize(max(self.format.bytesPerFrame(), min(len(self._payload), self.format.bytesForDuration(self.devices.buffer_ms*1000))))
            self.sink.stateChanged.connect(self._sink_changed)
            self._set_state('Starting')
            self._start_sink()
        except OperationCancelled:
            self.stop()
            raise
        except (ValueError, OSError, RuntimeError) as error: self._fail(str(error))

    def _feed(self):
        if self.sink is None or self._io is None or self._feeding or self.state == "Paused":
            return
        from .audio_output import ThreadedOutput
        if isinstance(self.sink, ThreadedOutput):
            self._sent = self.sink.sent
            if self.sink.clock.failure:
                self._fail(self.sink.clock.failure)
            return
        self._feeding = True
        try:
            count = min(len(self._payload) - self._sent, self.sink.bytesFree(), 65536)
            if count > 0:
                data = self._payload[self._sent:self._sent + count]
                written = self._io.write(data) if data else 0
                if written < 0:
                    self._fail("The audio device rejected playback data.")
                else:
                    self._sent += written
        except (ValueError, OSError, RuntimeError) as error:
            self._fail(str(error))
        finally:
            self._feeding = False

    def _tick(self):
        if self.sink is None or self.state != "Playing" or self._data is None:
            return
        self._feed()
        if self.sink is None or self._data is None:return
        offset = max(0, self.sink.processedUSecs()) * self._rate // 1000000
        self._last_frame = max(self._last_frame, self._start_frame + min(len(self._data), offset))
        self.position.emit(self._last_frame)
        if self.sink is not None and self.sink.state() == QtAudio.State.IdleState and self._sent == len(self._payload):
            self._sink_state(self.sink, QtAudio.State.IdleState)

    def meter_samples(self, frame):
        if self._data is None:
            return None
        if self._stream_factory is not None:
            return self._payload.meter_samples(int(frame)-self._start_frame)
        end = max(0, min(len(self._data), int(frame) - self._start_frame))
        return self._data[max(0, end - max(1, self._rate // 30)):end]

    def toggle_pause(self):
        if self.sink is None:
            return
        if self.state == "Playing":
            self._tick()
            if self.sink is not None:
                self._pause_requested = True
                self._timer.stop()
                self._set_state("Paused")
                self.sink.suspend()
        elif self.state == "Paused":
            self._pause_requested = False
            self._set_state("Playing")
            self._timer.start()
            self.sink.resume()
            self._feed()

    @Slot()
    def _sink_changed(self):
        # Qt retains the legacy QAudio::State signal name. A zero-argument slot
        # avoids enum-name conversion failures in newer PySide bindings.
        sink=self.sender()
        if sink is not None and sink is self.sink:
            self._feed()
            if sink is self.sink:self._sink_state(sink,sink.state())

    def _sink_state(self, sink, state):
        if sink is not self.sink or self._starting:
            return
        if state == QtAudio.State.SuspendedState:
            self._timer.stop()
            if self._pause_requested:
                self._set_state("Paused")
            else:
                sink.resume()
        elif state == QtAudio.State.ActiveState:
            if not self._pause_requested:
                self._timer.start()
                self._set_state("Playing")
        elif state == QtAudio.State.IdleState:
            if self._sent < len(self._payload):
                self._feed()
            elif self._data is not None:
                self._timer.stop()
                self._last_frame = self._start_frame + len(self._data)
                self.position.emit(self._last_frame)
                if self.loop and not self._loop_pending:
                    self._loop_pending = True
                    generation = self._generation
                    QTimer.singleShot(0, lambda: self._restart(generation))
                elif not self.loop:
                    self.stop()
        elif state == QtAudio.State.StoppedState and sink.error() != QtAudio.Error.NoError:
            self._fail("The audio output stopped unexpectedly. Reconnect the device or choose another output in Audio Hardware.")

    def _restart(self, generation):
        if generation == self._generation and self.sink is not None:
            self._loop_pending = False
            self._starting = True
            try:
                self.sink.reset()
            finally:
                self._starting = False
            if self._stream_factory is not None:
                from .streaming import StreamPayload
                self._payload.close()
                self._payload = StreamPayload(self._stream_factory, self._rate, self.format)
                self._data = self._payload.stream
            self._start_sink()

    def _outputs_changed(self):
        if self.sink is None:
            return
        try:
            if bytes(self.devices.output().id()).hex() == self._output_id:
                return
        except AudioError:
            pass
        self._fail("The playback device changed or disconnected. Choose an output in Options → Audio Hardware and start playback again.")

    def _fail(self, message):
        self.stop()
        self.failed.emit(message)

    def stop(self):
        already_stopped = self.state == "Stopped"
        self._generation += 1
        self._timer.stop()
        sink, self.sink = self.sink, None
        self._io = None
        if self._stream_factory is not None:
            self._payload.close()
            self._stream_factory = None
        self._data = None
        self._payload = b""
        self._sent = 0
        self._loop_pending = False
        self._pause_requested = False
        if sink is not None:
            sink.reset()
            sink.deleteLater()
        self._set_state("Stopped")
        if already_stopped:
            self.state_changed.emit("Stopped")

    def shutdown(self):
        self.stop()
