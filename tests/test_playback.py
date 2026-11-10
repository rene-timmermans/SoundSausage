"""Output-clock, buffering and device transitions, without touching host audio."""
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import QAudioFormat
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.audio import AudioError
from soundsausage.audio_devices import AudioDevices, AudioHardwareDialog
from soundsausage.playback import Playback, output_format, encode_output, QtAudio


class MemorySettings:
    def __init__(self): self.values = {}
    def value(self, key, fallback=None): return self.values.get(key, fallback)
    def setValue(self, key, value): self.values[key] = value
    def sync(self): pass


class Device:
    def __init__(self, name="Test output", identity=b"test", supported=None, default=True):
        self.name, self.identity, self.supported, self.default = name, identity, supported, default
    def id(self): return self.identity
    def description(self): return self.name
    def isDefault(self): return self.default
    def preferredFormat(self):
        f = QAudioFormat()
        rate, channels, kind = next(iter(self.supported)) if self.supported else (48000, 2, QAudioFormat.SampleFormat.Float)
        f.setSampleRate(rate); f.setChannelCount(channels); f.setSampleFormat(kind)
        return f
    def isFormatSupported(self, fmt):
        return self.supported is None or (fmt.sampleRate(), fmt.channelCount(), fmt.sampleFormat()) in self.supported


class Sink(QObject):
    stateChanged = Signal(object)
    def __init__(self, device, fmt, parent):
        super().__init__(parent)
        self.fmt = fmt
        self.capacity = 512
        self.queued = 0
        self.received = bytearray()
        self.us = 0
        self._state = QtAudio.State.StoppedState
        self._error = QtAudio.Error.NoError
        self.write_limit = 1000000
    def setBufferSize(self, size): self.requested_buffer = size
    def bytesFree(self): return self.capacity - self.queued
    def processedUSecs(self): return self.us
    def error(self): return self._error
    def state(self): return self._state
    def transition(self, state): self._state = state; self.stateChanged.emit(state)
    def start(self):
        self.us = 0; self.queued = 0
        self.transition(QtAudio.State.IdleState)
        return self
    def write(self, data):
        count = min(len(data), self.write_limit, self.bytesFree())
        self.received.extend(data[:count]); self.queued += count
        self.transition(QtAudio.State.ActiveState)
        return count
    def suspend(self): self.transition(QtAudio.State.SuspendedState)
    def resume(self): self.transition(QtAudio.State.ActiveState)
    def reset(self): self.queued = 0; self.transition(QtAudio.State.StoppedState)
    def drain(self): self.queued = 0; self.transition(QtAudio.State.IdleState)


class PlaybackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.devices = AudioDevices(settings=MemorySettings())
        self.outputs = [Device()]
        self.query = patch.object(self.devices, "outputs", side_effect=lambda: self.outputs)
        self.query.start()
        self.player = Playback(devices=self.devices, sink_factory=Sink)
        self.errors, self.positions = [], []
        self.player.failed.connect(self.errors.append)
        self.player.position.connect(self.positions.append)
        self.data = np.full((8000, 2), .25, np.float32)

    def tearDown(self):
        self.player.shutdown(); self.player.deleteLater(); self.devices.deleteLater()
        self.app.processEvents(); self.query.stop()

    def test_lazy_startup_does_not_query_or_open_audio_devices(self):
        self.devices.outputs.assert_not_called()
        self.assertEqual(self.player.state, "Stopped")

    def test_clock_uses_processed_frames_and_excludes_waiting_and_pause(self):
        self.player.play(self.data, 8000, 123)
        sink = self.player.sink
        QTest.qWait(25)
        self.assertEqual(self.positions[-1], 123)
        sink.us = 250000
        self.player._tick()
        self.assertEqual(self.positions[-1], 2123)
        self.player.toggle_pause()
        self.assertEqual(self.player.state, "Paused")
        frozen = self.positions[-1]
        QTest.qWait(30)
        self.assertEqual(self.positions[-1], frozen)
        self.player.toggle_pause()
        sink.us = 500000
        self.player._tick()
        self.assertEqual(self.positions[-1], 4123)
        sink.us = 450000  # An imperfect backend timestamp cannot move the cursor backwards.
        self.player._tick()
        self.assertEqual(self.positions[-1], 4123)
        np.testing.assert_array_equal(self.player.meter_samples(4123), self.data[3734:4000])

    def test_partial_writes_preserve_every_pcm_byte_and_wait_for_drain(self):
        data = np.arange(12, dtype=np.float32).reshape(6, 2) / 16
        self.player.play(data, 8000, 11)
        sink = self.player.sink
        self.assertEqual(self.player.state, "Playing")
        expected = data.tobytes()
        self.assertEqual(bytes(sink.received), expected)
        sink.drain()
        self.assertEqual(self.positions[-1], 17)
        self.assertEqual(self.player.state, "Stopped")
        self.player.play(self.data[:100], 8000)
        sink = self.player.sink
        sink.write_limit = 7
        for _ in range(200):
            if self.player.state == "Stopped": break
            sink.drain()
        self.assertEqual(bytes(sink.received), self.data[:100].tobytes())
        self.assertEqual(self.player.state, "Stopped")

    def test_loop_restarts_after_drain_and_stop_cancels_a_pending_restart(self):
        self.player.loop = True
        self.player.play(self.data[:4], 8000, 20)
        sink = self.player.sink
        sink._error = QtAudio.Error.UnderrunError
        sink.drain(); self.app.processEvents()
        self.assertEqual(self.player.state, "Playing")
        self.assertEqual(self.positions[-1], 20)
        sink.drain()
        self.player.stop(); self.app.processEvents()
        self.assertEqual(self.player.state, "Stopped")
        self.assertIsNone(self.player.sink)

    def test_missing_output_disconnect_and_backend_error_are_recoverable(self):
        self.outputs.clear()
        self.player.play(self.data, 8000)
        self.assertEqual(self.player.state, "Stopped")
        self.assertIn("No audio output", self.errors[-1])
        self.outputs.append(Device())
        self.player.play(self.data, 8000)
        self.outputs.clear(); self.devices.outputs_changed.emit()
        self.assertEqual(self.player.state, "Stopped")
        self.assertIn("disconnected", self.errors[-1])
        self.outputs.append(Device())
        self.player.play(self.data, 8000)
        self.player.sink._error = QtAudio.Error.IOError
        self.player.sink.transition(QtAudio.State.StoppedState)
        self.assertEqual(self.player.state, "Stopped")
        self.assertIn("unexpectedly", self.errors[-1])

    def test_stale_events_from_a_stopped_sink_cannot_stop_new_playback(self):
        self.player.play(self.data, 8000)
        old = self.player.sink
        self.player.play(self.data, 8000)
        old._error = QtAudio.Error.IOError
        old.transition(QtAudio.State.StoppedState)
        self.assertEqual(self.player.state, "Playing")
        self.assertFalse(self.errors)

    def test_device_and_buffer_preferences_are_shared_and_persisted(self):
        preview = Playback(devices=self.devices, sink_factory=Sink)
        try:
            self.player.play(self.data, 8000); preview.play(self.data, 8000)
            self.devices.configure("74657374", 80)
            self.assertEqual(self.player.state, "Stopped")
            self.assertEqual(preview.state, "Stopped")
            loaded = AudioDevices(settings=self.devices.settings)
            self.assertEqual((loaded.output_id, loaded.buffer_ms), ("74657374", 80))
            loaded.deleteLater()
            self.player.play(self.data, 8000)
            self.assertEqual(self.player.sink.requested_buffer, 5120)
        finally: preview.shutdown(); preview.deleteLater()

    def test_missing_chosen_device_is_not_silently_rerouted(self):
        self.devices.output_id = "deadbeef"
        self.player.play(self.data, 8000)
        self.assertEqual(self.player.state, "Stopped")
        self.assertIn("selected audio output", self.errors[-1])

    def test_device_dialog_cancel_preserves_settings_and_hotplug_refreshes_list(self):
        dialog = AudioHardwareDialog(self.devices)
        dialog.output.setCurrentIndex(1); dialog.buffer.setValue(40)
        dialog.reject()
        self.assertEqual(self.devices.output_id, "")
        dialog = AudioHardwareDialog(self.devices)
        self.outputs.append(Device("Headphones", b"headphones", default=False))
        self.devices.outputs_changed.emit()
        self.assertEqual(dialog.output.count(), 3)
        dialog.output.setCurrentIndex(2); dialog.accept()
        self.assertEqual(self.devices.output_id, b"headphones".hex())
        dialog.deleteLater()

    def test_format_fallback_resamples_and_converts_channels_and_integer_pcm(self):
        device = Device(supported={(48000, 1, QAudioFormat.SampleFormat.Int16)})
        fmt = output_format(device, 44100, 2)
        self.assertEqual((fmt.sampleRate(), fmt.channelCount(), fmt.sampleFormat()), (48000, 1, QAudioFormat.SampleFormat.Int16))
        data = np.tile([.25, .75], (4410, 1)).astype(np.float32)
        pcm = np.frombuffer(encode_output(data, 44100, fmt), dtype=np.int16)
        self.assertEqual(len(pcm), 4800)
        np.testing.assert_allclose(pcm[200:-200], 16384, atol=2)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int32)
        fmt.setSampleRate(44100); fmt.setChannelCount(2)
        peaks = np.array([[-2, 2], [-.5, .5]], np.float32)
        encoded = np.frombuffer(encode_output(peaks, 44100, fmt), dtype=np.int32)
        np.testing.assert_array_equal(encoded, [-2147483648, 2147483647, -1073741824, 1073741824])
