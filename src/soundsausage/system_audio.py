"""Record the explicitly resolved PulseAudio/PipeWire output monitor.

Uses pactl's JSON monitor_source, never the default microphone or a guessed name.
parec runs without a shell; pause closes the stream so paused audio cannot queue.
https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/
"""
import json
import shutil
import subprocess

from PySide6.QtCore import QIODevice, QProcess, Signal
from PySide6.QtMultimedia import QAudioFormat

from .audio import AudioError
from .i18n import tr
try:
    from PySide6.QtMultimedia import QtAudio
except ImportError:
    from PySide6.QtMultimedia import QAudio as QtAudio

SYSTEM_OUTPUT = 'system-output'
SYSTEM_OUTPUT_LABEL = 'System Audio (What You Hear)'


def utility(name):
    path = shutil.which(name)
    if not path:
        raise AudioError('System audio recording needs the PulseAudio client utilities (pactl and parec). Install the audio utilities and try again.')
    return path


def query(*arguments):
    command = [utility('pactl'), '--format=json', *arguments]
    try:
        result = subprocess.run(command,
                                capture_output=True, timeout=2, check=True)
        return json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        raise AudioError('The system audio output is unavailable. Check that PipeWire or PulseAudio is running and choose a default output in the system sound settings.') from error


class SystemOutputDevice:
    """A two-channel monitor facade for the existing recording format chooser."""
    def __init__(self, monitor, description):
        self.monitor, self.name = monitor, description

    @classmethod
    def resolve(cls):
        utility('parec')
        info, sinks = query('info'), query('list', 'sinks')
        if (isinstance(info, dict) and isinstance(info.get('default_sink_name'), str)
                and info['default_sink_name'] and isinstance(sinks, list)):
            for sink in sinks:
                if isinstance(sink, dict) and sink.get('name') == info.get('default_sink_name'):
                    monitor = sink.get('monitor_source')
                    if isinstance(monitor, str) and monitor and not any(c in monitor for c in '\x00\n\r'):
                        return cls(monitor, str(sink.get('description') or sink['name']))
        raise AudioError('The default output has no recording monitor. Choose another default output in the system sound settings.')

    def id(self): return ('soundsausage:monitor:' + self.monitor).encode('utf-8')
    def description(self): return tr(SYSTEM_OUTPUT_LABEL) + ' — ' + self.name
    def isDefault(self): return False
    def maximumChannelCount(self): return 2
    def preferredFormat(self):
        fmt = QAudioFormat(); fmt.setSampleRate(48000); fmt.setChannelCount(2)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Float)
        return fmt
    def isFormatSupported(self, fmt):
        return (1000 <= fmt.sampleRate() <= 384000 and fmt.channelCount() == 2 and
                fmt.sampleFormat() == QAudioFormat.SampleFormat.Float)


def capture_command(device, fmt):
    return utility('parec'), ['--raw', '--format=float32ne', '--rate='+str(fmt.sampleRate()),
        '--channels=2', '--channel-map=front-left,front-right', '--latency-msec=20',
        '--client-name=SoundSausage', '--stream-name=SoundSausage system audio',
        '--device='+device.monitor]


class SystemAudioSource(QIODevice):
    """Qt input-shaped pull stream; bounded reads reuse Recorder/Take unchanged."""
    stateChanged = Signal(object)

    def __init__(self, device, fmt, parent=None):
        super().__init__(parent)
        self.device, self.format = device, fmt
        self.process = None
        self._state = QtAudio.State.StoppedState
        self._error = QtAudio.Error.NoError
        self._ending = False
        self._stderr = b''

    def state(self): return self._state
    def error(self): return self._error
    def setBufferSize(self, size): pass
    def isSequential(self): return True
    def bytesAvailable(self):
        return super().bytesAvailable() + (self.process.bytesAvailable() if self.process else 0)
    def readData(self, maximum):
        return bytes(self.process.read(maximum)) if self.process else b''

    def _set_state(self, state):
        if state != self._state:
            self._state = state; self.stateChanged.emit(state)

    def _readable(self):
        process = self.sender()
        if process is not self.process: return
        self.readyRead.emit()
        if self.process is process and self.bytesAvailable() > 8*1024*1024:
            # A stalled consumer must not accumulate an unbounded Qt buffer.
            self._error = QtAudio.Error.IOError
            self._set_state(QtAudio.State.StoppedState)

    def _diagnostic(self):
        if self.sender() is self.process:
            self._stderr = (self._stderr + bytes(self.process.readAllStandardError()))[-4096:]

    def _exited(self, *_):
        process = self.sender()
        if process is not self.process or self._ending: return
        # Offer all complete buffered frames before reporting an interrupted take.
        self.readyRead.emit()
        if self.process is process:
            self._error = QtAudio.Error.IOError
            self._set_state(QtAudio.State.StoppedState)

    def _launch(self):
        self._error = QtAudio.Error.NoError; self._stderr = b''
        process = QProcess(self); self.process = process
        process.readyReadStandardOutput.connect(self._readable)
        process.readyReadStandardError.connect(self._diagnostic)
        process.finished.connect(self._exited)
        self.open(QIODevice.OpenModeFlag.ReadOnly)
        command, arguments = capture_command(self.device, self.format)
        process.start(command, arguments)
        if not process.waitForStarted(2000):
            self._error = QtAudio.Error.OpenError
            self._stop_process(); self.close()
            self._set_state(QtAudio.State.StoppedState)
            return False
        self._set_state(QtAudio.State.ActiveState)
        return True

    def start(self): return self if self._launch() else None

    def _stop_process(self):
        process, self.process = self.process, None
        if process is not None:
            self._ending = True
            try:
                if process.state() != QProcess.ProcessState.NotRunning:
                    process.kill(); process.waitForFinished(2000)
            finally:
                self._ending = False; process.deleteLater()

    def suspend(self):
        self._stop_process(); self.close()
        self._set_state(QtAudio.State.SuspendedState)

    def resume(self):
        if self._state == QtAudio.State.SuspendedState:
            try:
                self._launch()
            except (ValueError, OSError, RuntimeError):
                self._error = QtAudio.Error.OpenError
                self._stop_process(); self.close()
                self._set_state(QtAudio.State.StoppedState)

    def stop(self):
        self._stop_process(); self.close()
        self._set_state(QtAudio.State.StoppedState)
