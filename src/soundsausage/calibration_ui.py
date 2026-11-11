"""Explicit loopback calibration using the same device clocks as overdubbing."""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout
from .i18n_widgets import QDialog,QLabel,QSpinBox,QFormLayout,QPushButton,QDialogButtonBox
from .capture import Recorder
from .playback import Playback
from .resample import resample_frames
from .synchronization import DuplexClock,calibration_probe,measure_latency,save_calibration,read_calibration
from .icons import make_icon
from .theme import colors


class CalibrationDialog(QDialog):
    def __init__(self,window,parent=None,*,rate=None,first_channel=0):
        super().__init__(parent or window)
        self.window=window;self.devices=window.audio_devices
        self._running=False;self._expected_finish=False;self._clock=None;self.calibration_result=None;self._rate_locked=rate is not None
        self.setWindowTitle('Recording Calibration');self.setMinimumWidth(560)
        layout=QVBoxLayout(self)
        note=QLabel('Connect the selected output to the selected input with a loopback cable. A microphone near a speaker also works, but includes acoustic delay. Start Calibration plays quiet test signals for about six seconds. The input is never monitored through the speakers.')
        note.setWordWrap(True);layout.addWidget(note)
        form=QFormLayout();self.rate=QSpinBox();self.rate.setRange(1000,384000)
        self.rate.setValue(rate or window.active_model().sample_rate);self.rate.setEnabled(rate is None)
        self.first=QSpinBox();self.first.setRange(1,32);self.first.setValue(first_channel+1)
        form.addRow('Sample rate (Hz)',self.rate);form.addRow('First input channel',self.first);layout.addLayout(form)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.start_button=QPushButton(make_icon('record',colors()),'Start Calibration');self.start_button.clicked.connect(self.start_calibration)
        row=QHBoxLayout();row.addWidget(self.start_button);row.addStretch();layout.addLayout(row)
        self.box=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);self.box.rejected.connect(self.reject);layout.addWidget(self.box)
        self.recorder=Recorder(self,devices=self.devices);self.player=Playback(self,devices=self.devices)
        self.recorder.timing.connect(self.input_timing);self.recorder.finished.connect(self.finished_take)
        self.recorder.failed.connect(self.failed);self.player.failed.connect(self.failed)
        self._play_timer=QTimer(self);self._play_timer.setSingleShot(True);self._play_timer.timeout.connect(self.play_probe)
        self._stop_timer=QTimer(self);self._stop_timer.setSingleShot(True);self._stop_timer.timeout.connect(self.finish_measurement)
        self.rate.valueChanged.connect(self.show_profile);self.first.valueChanged.connect(self.show_profile)
        self.show_profile()

    def show_profile(self,*_):
        if self._running:return
        if self.window.no_audio:
            self.status.setText('Audio is disabled.');self.start_button.setEnabled(False)
            return
        try:
            profile=read_calibration(self.devices,self.rate.value(),self.first.value()-1)
            if profile:self.status.setText(f"Saved correction: {profile['offset_ms']:.3f} ms")
            else:self.status.setText('No calibration is saved for this device combination.')
            self.start_button.setEnabled(not self.window.no_audio)
        except (ValueError,OSError,RuntimeError) as error:self.status.setText(str(error));self.start_button.setEnabled(False)

    def start_calibration(self):
        if self._running or self.window.no_audio:return
        self._running=True;self._expected_finish=False;self._clock=None;self.calibration_result=None
        self._rate=self.rate.value();self._first=self.first.value()-1
        self.reference,self.markers=calibration_probe(self._rate)
        self.start_button.setEnabled(False);self.rate.setEnabled(False);self.first.setEnabled(False)
        self.status.setText('Measuring the input/output connection…')
        if self.recorder.start(self._rate,1,self._first,limit_seconds=8,skip_start_ms=0):
            self._play_timer.start(200)

    def play_probe(self):
        if not self._running:return
        self.player.play(self.reference,self._rate)
        if self._running:self._stop_timer.start(6000)

    def input_timing(self,native_frames):
        if not self._running or self.player.state!='Playing':return
        self.player._tick()
        if self.player.state!='Playing':return
        if self._clock is None:self._clock=DuplexClock(self.recorder.format.sampleRate(),self._rate)
        self._clock.observe(native_frames,self.player._last_frame)

    def finish_measurement(self):
        if not self._running:return
        self._expected_finish=True;self.player.stop();self.recorder.stop()

    def finished_take(self,take):
        expected=self._running and self._expected_finish
        self._running=False;self._play_timer.stop();self._stop_timer.stop();self.player.stop()
        try:
            if not expected:return
            if self._clock is None:raise ValueError('The device clocks could not be measured. Try the calibration again.')
            clock=self._clock.result()
            if not clock.reliable:raise ValueError('The device clocks were not stable enough for calibration. Try again.')
            frames=max(1,round(take.frames*self._rate/take.rate*clock.ratio))
            captured=resample_frames(take.samples,frames,take.rate)
            result=measure_latency(captured,self.markers,self._rate,clock.anchor)
            save_calibration(self.devices,self._rate,self._first,result);self.calibration_result=result
            self.status.setText(f"Calibration saved: {result['offset_ms']:.3f} ms. Automatic synchronization will use this device combination.")
        except (ValueError,OSError,RuntimeError) as error:self.status.setText(str(error))
        finally:
            take.discard();self.start_button.setEnabled(not self.window.no_audio);self.first.setEnabled(True);self.rate.setEnabled(not self._rate_locked)

    def failed(self,message):
        self._running=False;self._expected_finish=False;self._play_timer.stop();self._stop_timer.stop()
        self.player.stop()
        if self.recorder.active:self.recorder.stop(keep=False)
        self.status.setText(str(message));self.start_button.setEnabled(not self.window.no_audio);self.first.setEnabled(True);self.rate.setEnabled(not self._rate_locked)

    def done(self,result):
        self._running=False;self._expected_finish=False;self._play_timer.stop();self._stop_timer.stop()
        self.player.stop();self.recorder.stop(keep=False)
        super().done(result)
