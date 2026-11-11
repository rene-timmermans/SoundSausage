"""Recording setup, bounded live waveform and editor transaction integration."""
from .i18n import Literal
from collections import deque
from datetime import datetime
import time

import numpy as np
from PySide6.QtCore import Qt,QPointF,QRectF,QTimer
from PySide6.QtGui import QPen
from .i18n_widgets import QPainter
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QWidget, QLabel, QDialog, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QCheckBox

from .audio import AudioError
from .capture import Recorder,input_format,recover_take
from .document import Document
from .errors import OperationCancelled
from .progress_ui import long_operation
from .resample import resample,resample_frames
from .synchronization import DuplexClock,read_calibration
from .theme import colors,blend
from .icons import make_icon
from .waveform import clock_text
from .i18n_widgets import set_text


class RecordDialog(QDialog):
    def __init__(self,window):
        super().__init__(window)
        self.window=window;self.devices=window.audio_devices
        self.setWindowTitle('Record');self.setMinimumWidth(520)
        form=QFormLayout(self)
        self.input=QComboBox();self.input.setAccessibleName('Recording input')
        self.target=QComboBox();self.target.setAccessibleName('Recording destination')
        if window.mode=='multitrack':
            name=window.session.tracks[window.session.track_index(window.session.selected_track)].name
            self.target.addItem(f'New clip on {name}','multitrack')
            if window.session.selected:self.target.addItem('Punch In/Out in Selection','punch')
        elif window.document.frames and not window.document.partial_channels:
            self.target.addItem('Insert at cursor','insert')
            if window.document.selected:self.target.addItem('Replace selection','replace')
        self.target.addItem('New waveform','new')
        self.rate=QSpinBox();self.rate.setRange(1000,384000);self.rate.setValue(window.active_model().sample_rate)
        self.channels=QComboBox();self.channels.addItems(('Mono','Stereo'));self.channels.setCurrentIndex(window.document.channels-1)
        self.first=QSpinBox();self.first.setRange(1,32);self.first.setValue(1)
        self.duration=QDoubleSpinBox();self.duration.setRange(0,86400);self.duration.setDecimals(3)
        self.duration.setSpecialValueText('Until Stop');self.duration.setSuffix(' sec')
        self.skip_start=QDoubleSpinBox();self.skip_start.setRange(0,500);self.skip_start.setDecimals(1);self.skip_start.setSuffix(' ms')
        self.skip_start.setValue(float(self.devices.settings.value('recording/skip_start_ms',50)))
        self.skip_start.setToolTip('Discard the first input milliseconds once per take, followed by a 5 ms fade-in. Use 0 ms to keep the complete start.')
        form.addRow('Input',self.input);form.addRow('Destination',self.target)
        form.addRow('Sample rate (Hz)',self.rate);form.addRow('Channels',self.channels)
        form.addRow('First input channel',self.first);form.addRow('Maximum duration',self.duration)
        form.addRow('Skip at start',self.skip_start)
        self.accompaniment = QCheckBox('Play existing tracks while recording')
        self.accompaniment.setChecked(window.mode=='multitrack' and window.session.frames>0)
        self.offset = QDoubleSpinBox(); self.offset.setRange(-2000,2000); self.offset.setDecimals(1); self.offset.setSuffix(' ms')
        self.offset.setValue(float(self.devices.settings.value('recording/offset_ms',0)))
        self.offset.setToolTip('Negative moves the new clip earlier; positive moves it later. Calibrate with a loopback recording.')
        form.addRow(self.accompaniment); form.addRow('Recording position offset',self.offset)
        self.offset_label=form.labelForField(self.offset)
        self.automatic=QCheckBox('Automatic synchronization')
        self.automatic.setChecked(str(self.devices.settings.value('recording/automatic_sync',True)).lower() in ('true','1'))
        self.calibrate=QPushButton(make_icon('calibrate',colors()),'Calibrate Recording…');self.calibrate.clicked.connect(self.calibrate_recording)
        form.addRow(self.automatic,self.calibrate)
        self.sync_info=QLabel();self.sync_info.setWordWrap(True);form.addRow(self.sync_info)
        self.pre_roll=QDoubleSpinBox();self.pre_roll.setRange(0,30);self.pre_roll.setDecimals(2);self.pre_roll.setSuffix(' sec')
        self.pre_roll.setValue(float(self.devices.settings.value('recording/pre_roll_seconds',2)))
        self.crossfade=QDoubleSpinBox();self.crossfade.setRange(0,100);self.crossfade.setDecimals(1);self.crossfade.setSuffix(' ms')
        self.crossfade.setValue(float(self.devices.settings.value('recording/punch_fade_ms',5)))
        form.addRow('Pre-roll',self.pre_roll);self.pre_roll_label=form.labelForField(self.pre_roll)
        form.addRow('Punch crossfade',self.crossfade);self.crossfade_label=form.labelForField(self.crossfade)
        self.note=QLabel();self.note.setWordWrap(True);form.addRow(self.note)
        guidance=QLabel('Stop keeps the take. Discard removes only this recording.\nThe input is not played through the speakers.')
        guidance.setWordWrap(True);form.addRow(guidance)
        self.box=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        set_text(self.box.button(QDialogButtonBox.StandardButton.Ok),'Start Recording')
        self.box.accepted.connect(self.accept);self.box.rejected.connect(self.reject);form.addRow(self.box)
        self.reload(self.devices.input_id)
        self.devices.inputs_changed.connect(self.reload)
        for field in (self.input,self.target,self.channels):field.currentIndexChanged.connect(self.sync)
        self.rate.valueChanged.connect(self.sync);self.first.valueChanged.connect(self.sync)
        self.automatic.toggled.connect(self.sync);self.accompaniment.toggled.connect(self.sync)
        self.sync()

    def reload(self,selected=None):
        selected=(self.input.currentData() or '') if selected is None else selected
        self.input.clear();self.input.addItem('System Default','')
        for device in self.devices.inputs():self.input.addItem(Literal(device.description()),bytes(device.id()).hex())
        index=self.input.findData(selected)
        if selected and index<0:self.input.addItem('Selected input (disconnected)',selected);index=self.input.count()-1
        self.input.setCurrentIndex(max(0,index))
        if hasattr(self,'box'):self.sync()

    def device(self):
        inputs=self.devices.inputs();selected=self.input.currentData()
        if selected:
            for device in inputs:
                if bytes(device.id()).hex()==selected:return device
            raise AudioError('The selected input is disconnected.')
        if not inputs:raise AudioError('Connect a microphone or audio interface to start recording.')
        return next((d for d in inputs if d.isDefault()),inputs[0])

    def sync(self,*_):
        target=self.target.currentData()
        existing=target in ('insert','replace');multi=target in ('multitrack','punch');punch=target=='punch'
        if punch and not self.accompaniment.isChecked():
            self.accompaniment.blockSignals(True);self.accompaniment.setChecked(True);self.accompaniment.blockSignals(False)
        self.accompaniment.setEnabled(not punch)
        self.pre_roll.setVisible(punch);self.pre_roll_label.setVisible(punch)
        self.crossfade.setVisible(punch);self.crossfade_label.setVisible(punch);self.duration.setEnabled(not punch)
        self.accompaniment.setVisible(multi); self.offset.setVisible(multi)
        self.offset_label.setVisible(multi)
        self.automatic.setVisible(multi);self.calibrate.setVisible(multi);self.sync_info.setVisible(multi)
        automatic=multi and self.accompaniment.isChecked() and self.automatic.isChecked()
        self.automatic.setEnabled(multi and self.accompaniment.isChecked())
        self.offset.setEnabled(not automatic)
        self.rate.setEnabled(not existing and not multi)
        self.channels.setEnabled(not existing)
        if existing:
            self.rate.setValue(self.window.document.sample_rate)
            self.channels.setCurrentIndex(self.window.document.channels-1)
        elif multi:self.rate.setValue(self.window.session.sample_rate)
        try:
            device=self.device()
            maximum=min(32,max(1,device.maximumChannelCount() if hasattr(device,'maximumChannelCount') else device.preferredFormat().channelCount()))
            self.first.setMaximum(max(1,maximum-(self.channels.currentIndex()+1)+1))
            fmt=input_format(device,self.rate.value(),self.channels.currentIndex()+1,self.first.value()-1)
            text=f'Device: {device.description()}'
            if fmt.channelCount()==1 and self.channels.currentIndex()==1:
                text+='\nMono input is recorded on both stereo channels.'
            if fmt.sampleRate()!=self.rate.value():text+=f'\nInput at {fmt.sampleRate():,} Hz; the take is converted after Stop.'
            if punch:text+='\nOnly the selected interval is replaced. Playback starts with pre-roll; recording stops automatically after the selection.'
            if multi:
                profile=read_calibration(self.devices,self.rate.value(),self.first.value()-1,input_device=device) if automatic else None
                self.sync_info.setText(f"Calibrated correction: {profile['offset_ms']:.3f} ms" if profile else
                    'No calibration for these devices yet. Clock drift is measured while backing tracks play.' if automatic else 'The manual recording position offset is used.')
            self.note.setText(text);self.box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        except (ValueError,RuntimeError) as error:
            self.note.setText(str(error));self.box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def settings(self):
        return dict(target=self.target.currentData(),rate=self.rate.value(),channels=self.channels.currentIndex()+1,
                    first_channel=self.first.value()-1,input_id=self.input.currentData(),
                    limit_seconds=None if self.target.currentData()=='punch' else self.duration.value() or None,skip_start_ms=self.skip_start.value(),
                    accompaniment=self.target.currentData() in ('multitrack','punch') and self.accompaniment.isChecked(),
                    recording_offset_ms=0 if self.target.currentData() in ('multitrack','punch') and self.accompaniment.isChecked() and self.automatic.isChecked() else self.offset.value(),
                    automatic_sync=self.target.currentData() in ('multitrack','punch') and self.accompaniment.isChecked() and self.automatic.isChecked(),
                    pre_roll_seconds=self.pre_roll.value(),punch_fade_ms=self.crossfade.value())

    def calibrate_recording(self):
        from .calibration_ui import CalibrationDialog
        self.devices.configure(self.devices.output_id,self.devices.buffer_ms,self.input.currentData())
        dialog=CalibrationDialog(self.window,self,rate=self.rate.value(),first_channel=self.first.value()-1)
        dialog.exec()
        if dialog.calibration_result is not None:self.automatic.setChecked(True)
        dialog.deleteLater();self.sync()


class RecordingView(QWidget):
    def __init__(self,window):
        super().__init__();self.window=window
        self.bins=deque(maxlen=2200);self.rate=48000;self.channels=2;self.frames=0
        layout=QVBoxLayout(self);layout.setContentsMargins(16,10,16,10)
        self.heading=QLabel('Recording');layout.addWidget(self.heading)
        self.plot=LivePlot(self);layout.addWidget(self.plot,1)
        self._paint_timer=QTimer(self);self._paint_timer.setInterval(33);self._paint_timer.timeout.connect(self.plot.update)
        self.note=QLabel('Stop keeps the take. Pause excludes the paused time. Discard removes this take.')
        layout.addWidget(self.note)
        self.sync_status=QLabel();self.sync_status.setWordWrap(True);layout.addWidget(self.sync_status)
        discard=QPushButton('Discard Recording');discard.clicked.connect(window.discard_recording)
        row=QHBoxLayout();row.addStretch();row.addWidget(discard);layout.addLayout(row)

    def reset(self,rate,channels,description):
        self.rate=rate;self.channels=channels;self.frames=0;self.bins.clear()
        self.heading.setText(f'Recording — {description}');self.sync_status.setText('');self._paint_timer.start();self.plot.update()

    def feed(self,data,frames):
        start=frames-len(data);step=max(1,self.rate//100);offset=0
        while offset<len(data):
            position=start+offset;stop=min(len(data),offset+step-position%step)
            block=data[offset:stop];low,high=block.min(axis=0),block.max(axis=0)
            if self.bins and self.bins[-1][0]//step==position//step:
                a,b,previous_low,previous_high=self.bins[-1]
                self.bins[-1]=(a,start+stop,np.minimum(low,previous_low),np.maximum(high,previous_high))
            else:self.bins.append((position,start+stop,low,high))
            offset=stop
        self.frames=frames

    def stop(self):
        self._paint_timer.stop()


class LivePlot(QWidget):
    def __init__(self,view):
        super().__init__();self.view=view;self.setMinimumHeight(200)
    def paintEvent(self,event):
        p=QPainter(self);c=colors();p.fillRect(self.rect(),c.plot)
        view=self.view;span=max(1,view.rate*20);start=max(0,view.frames-span)
        line=self.fontMetrics().height()+2
        width=max(1,self.width()-18);height=max(1,self.height()-line-4)
        gap=8 if view.channels==2 else 0
        channel_height=max(1,(height-gap)/view.channels)
        for channel in range(view.channels):
            center=channel*(channel_height+gap)+channel_height/2
            scale=channel_height*.44
            p.setPen(QPen(c.plot_grid,1));p.drawLine(QPointF(9,center),QPointF(9+width,center))
            p.setPen(QPen(c.waveform,1))
            for a,b,low,high in view.bins:
                if b<=start:continue
                x=9+(max(a,start)-start)/span*width
                p.drawLine(QPointF(x,center-min(1.08,max(-1.08,float(high[channel])))*scale),
                           QPointF(x,center-min(1.08,max(-1.08,float(low[channel])))*scale))
        if view.channels==2:
            separator=QPen(blend(c.plot,c.plot_text,.55),1);separator.setCosmetic(True);p.setPen(separator)
            for y in (channel_height,channel_height+gap):
                p.drawLine(QPointF(9,y),QPointF(9+width,y))
        p.setPen(c.plot_text)
        p.drawText(QRectF(9,height+2,width,line),Qt.AlignmentFlag.AlignLeft,clock_text(start/view.rate))
        p.drawText(QRectF(9,height+2,width,line),Qt.AlignmentFlag.AlignRight,clock_text((start+span)/view.rate))


class RecordingActions:
    def init_recording(self):
        self._record_context=None;self._applying_recording=False
        self.recorder=Recorder(self,devices=self.audio_devices)
        self.recorder.state_changed.connect(self.recording_state)
        self.recorder.samples.connect(self.recording_samples)
        self.recorder.timing.connect(self.recording_timing)
        self.recorder.finished.connect(self.recording_finished)
        self.recorder.failed.connect(self.recording_failed)
        self.player.failed.connect(self.recording_output_failed)
        self._punch_wait_timer=QTimer(self);self._punch_wait_timer.setInterval(20);self._punch_wait_timer.timeout.connect(self.begin_punch_playback)

    @property
    def recording_busy(self):return self._record_context is not None

    def record(self,punch=False):
        if self.no_audio:return
        if self.recorder.active:return self.stop_recording()
        if self.recording_busy:return
        if punch and (self.mode!='multitrack' or not self.session.selected):
            self.error('Punch Recording','Select a time range in Multitrack before punching in/out.');return
        self.player.stop()
        dialog=RecordDialog(self)
        if punch:dialog.target.setCurrentIndex(dialog.target.findData('punch'))
        try:
            if dialog.exec()==QDialog.DialogCode.Accepted:self.start_recording(**dialog.settings())
        finally:
            self.update_recording_actions();dialog.deleteLater()

    def start_recording(self,target='new',rate=44100,channels=2,first_channel=0,input_id=None,limit_seconds=None,accompaniment=False,recording_offset_ms=0,skip_start_ms=None,automatic_sync=None,pre_roll_seconds=2,punch_fade_ms=5):
        if self.recording_busy:return False
        if target not in ('new','insert','replace','multitrack','punch'):raise AudioError('Invalid recording destination.')
        if target=='punch':
            if self.mode!='multitrack' or not self.session.selected:raise AudioError('Select a time range in Multitrack before punching in/out.')
            accompaniment=True
        if not np.isfinite(pre_roll_seconds) or not 0<=pre_roll_seconds<=30 or not np.isfinite(punch_fade_ms) or not 0<=punch_fade_ms<=100:
            raise AudioError('Invalid punch pre-roll or crossfade.')
        if target in ('insert','replace') and self.document.partial_channels:
            raise AudioError('Choose Both channels to record into an existing stereo waveform.')
        if target=='new' and not self._confirm_discard():return False
        if target in ('insert','replace') and (rate!=self.document.sample_rate or channels!=self.document.channels):
            raise AudioError('Recording into a waveform requires its sample rate and channel count.')
        if target=='replace' and not self.document.selected:raise AudioError('Select audio to replace first.')
        if target in ('multitrack','punch') and rate!=self.session.sample_rate:raise AudioError('Use the session sample rate for recording.')
        if accompaniment and target not in ('multitrack','punch'): raise AudioError('Playback accompaniment requires a multitrack recording.')
        if automatic_sync is not None and type(automatic_sync) is not bool:raise AudioError('Invalid automatic synchronization setting.')
        if automatic_sync and not accompaniment:raise AudioError('Automatic synchronization requires playback accompaniment.')
        if automatic_sync and recording_offset_ms:raise AudioError('Choose automatic synchronization or a manual recording offset.')
        if not np.isfinite(recording_offset_ms) or not -2000<=recording_offset_ms<=2000: raise AudioError('Invalid recording position offset.')
        if skip_start_ms is not None and (not np.isfinite(skip_start_ms) or not 0<=skip_start_ms<=500):
            raise AudioError('Choose a recording start skip between 0 and 500 ms.')
        if input_id is not None:self.audio_devices.configure(self.audio_devices.output_id,self.audio_devices.buffer_ms,input_id)
        self.player.stop()
        profile=read_calibration(self.audio_devices,rate,first_channel) if automatic_sync else None
        start,end=self.document.selection if target=='replace' else (self.active_model().cursor,self.active_model().cursor)
        if target=='punch':
            punch_in,end=self.session.selection;start=max(0,punch_in-round(pre_roll_seconds*rate))
        if target=='multitrack':
            remaining=86400-start/rate
            if remaining<=0:raise AudioError('The recording would exceed the 24-hour timeline.')
            limit_seconds=min(limit_seconds,remaining) if limit_seconds is not None else remaining
        self._record_context=dict(target=target,rate=rate,channels=channels,start=start,end=end,
                                  accompaniment=bool(accompaniment),recording_offset_ms=recording_offset_ms,
                                  automatic_sync=bool(automatic_sync),calibration=profile,clock=None,
                                  playback_loop=self.player.loop,
                                  document=self.document,session=self.session,revision=self.active_model().revision,
                                  track=self.session.selected_track,
                                  actions={key:action.isEnabled() for key,action in self.actions.items()})
        if target=='punch':
            self._record_context.update(punch_in=punch_in,punch_out=end,punch_fade=round(punch_fade_ms*rate/1000),
                play_started=False,play_end=min(rate*86400,end+round(rate*2.25)),wait_deadline=time.monotonic()+2)
            self.audio_devices.settings.setValue('recording/pre_roll_seconds',pre_roll_seconds)
            self.audio_devices.settings.setValue('recording/punch_fade_ms',punch_fade_ms)
            limit_seconds=None
        self.update_recording_actions()
        if accompaniment and target!='punch' and start<self.session.frames:
            self.player.loop=False
            self.player.play_session(self.session,start,self.session.frames)
            if self.player.state=='Stopped':
                if self.recording_busy:self.end_recording_view()
                return False
        if not automatic_sync:self.audio_devices.settings.setValue('recording/offset_ms',recording_offset_ms)
        if automatic_sync is not None:self.audio_devices.settings.setValue('recording/automatic_sync',bool(automatic_sync))
        if skip_start_ms is not None:
            self.audio_devices.settings.setValue('recording/skip_start_ms',skip_start_ms)
            self.audio_devices.settings.sync()
        ok=self.recorder.start(rate,channels,first_channel,limit_seconds,skip_start_ms=skip_start_ms or 0)
        if not ok and self.recording_busy:self.end_recording_view()
        elif ok and target=='punch':self._punch_wait_timer.start()
        return ok

    def begin_punch_playback(self):
        context=self._record_context
        if context is None or context['target']!='punch' or not self.recorder.active:
            self._punch_wait_timer.stop();return
        if self.recorder.state=='Paused':return
        if self.recorder.take.frames<self.recorder.format.sampleRate()*.1:
            if time.monotonic()>context['wait_deadline']:
                self._punch_wait_timer.stop();self.recorder.stop()
                self.error('Punch Recording','The input did not start in time. Check the recording device.')
            return
        self._punch_wait_timer.stop();self.player.loop=False
        self.player.play_session(self.session,context['start'],context['play_end'],punch=(context['track'],context['punch_in'],context['punch_out'],min(context['punch_fade'],(context['punch_out']-context['punch_in'])//2)))
        if self._record_context is not context:return
        if self.player.state=='Playing':
            context['play_started']=True
            context['preplay_received']=self.recorder.received_frames
            self.recorder.limit_from_now((context['play_end']-context['start'])/context['rate'])
        else:self.recorder.stop()

    def calibrate_recording(self):
        if self.recording_busy:return
        from .calibration_ui import CalibrationDialog
        self.player.stop();dialog=CalibrationDialog(self);dialog.exec();dialog.deleteLater()

    def recording_timing(self,native_frames):
        context=self._record_context
        if context is None or not context.get('automatic_sync') or self.player.state!='Playing':return
        self.player._tick()
        if self._record_context is not context or self.player.state!='Playing':return
        if context['clock'] is None:context['clock']=DuplexClock(self.recorder.format.sampleRate(),context['rate'])
        context['clock'].observe(native_frames,self.player._last_frame)
        if context['target']!='punch' and native_frames-context.get('clock_update',0)>=self.recorder.format.sampleRate():
            context['clock_update']=native_frames;fit=context['clock'].result()
            self.recording_view.sync_status.setText(f"Clock correction: {fit.ppm:+.1f} ppm" if fit.drift_measured else
                'Automatic synchronization is active.' if context.get('calibration') else 'Clock synchronization is active; no input/output calibration is saved.')

    def update_recording_actions(self):
        if 'record' not in self.actions:return
        busy=self.recording_busy
        if 'punch' in self.actions:self.actions['punch'].setEnabled(not busy and not self.no_audio and self.mode=='multitrack' and self.session.selected)
        self.waveform.sample_editable = not busy
        if busy: self.waveform.cancel_sample_drag()
        if hasattr(self, 'channel_choice'): self.channel_choice.setEnabled(not busy and self.document.channels == 2)
        self.actions['record'].setChecked(busy)
        self.actions['record'].setText('Stop Recording' if busy else 'Record…')
        self.actions['record'].setEnabled(not self.no_audio and not self._applying_recording)
        self.actions['discard_recording'].setEnabled(busy and not self._applying_recording)
        if busy:
            allowed={'record','play','stop','pause','discard_recording','manual','about','exit','toolbar_labels','show_status','fullscreen'}
            for key,action in self.actions.items():
                if key not in allowed:action.setEnabled(False)
            ready=self.recorder.state in ('Recording','Paused') and not self._applying_recording
            self.actions['record'].setEnabled(ready)
            self.actions['play'].setText('Stop Recording')
            self.actions['play'].setEnabled(ready)
            self.actions['stop'].setEnabled(ready)
            self.actions['pause'].setEnabled(self.recorder.state in ('Recording','Paused'))

    def recording_state(self,state):
        if not hasattr(self,'recording_view'):return
        if state=='Recording' and self.recorder.take is not None:
            if not self.recording_view.bins:
                take=self.recorder.take;self.recording_view.reset(take.rate,take.channels,take.description)
                self.format_label.setText(f" {take.rate} Hz · Input · {'Stereo' if take.channels==2 else 'Mono'} ")
            self.editor_stack.setCurrentWidget(self.recording_view)
        self.state_label.setText(state)
        self.update_recording_actions()

    def recording_samples(self,data,frames):
        if not self.recording_busy:return
        context=self._record_context
        if context.get('accompaniment') and 'anchor' not in context and (context['target']!='punch' or context.get('play_started')):
            self.player._tick()
            elapsed=max(0,self.player._last_frame-context['start'])
            captured=round(frames*context['rate']/self.recorder.take.rate)
            skipped=round(getattr(self.recorder,'skipped_frames',0)*context['rate']/self.recorder.take.rate)
            context['anchor']=context['start']+(elapsed-captured if context['target']=='punch' else max(skipped,elapsed-captured))
        self.recording_view.feed(data,frames)
        self.time_label.setText(clock_text(frames/self.recording_view.rate))
        self.detail_label.setText(f' {frames:,} captured frames ')
        rate=self.recording_view.rate
        self.transport.set_view_range(max(0,frames-rate*20),max(frames,rate*20),rate)
        self.update_meters(data)
        if context['target']=='punch':
            frame=self.player._last_frame
            self.recording_view.sync_status.setText('Preparing punch recording…' if not context.get('play_started') else
                'Pre-roll: the original audio is playing.' if frame<context['punch_in'] else
                'Punch recording: the selected interval is being captured.' if frame<context['punch_out'] else
                'Finishing punch recording…')

    def stop_recording(self):
        if self._applying_recording:return
        self.player.stop()
        self.recorder.stop()
        if not self.recorder.active and self.recording_busy:self.end_recording_view()

    def discard_recording(self):
        if not self.recording_busy or self._applying_recording:return
        result=QMessageBox.question(self,'Discard Recording','Discard this take? Existing audio remains unchanged.',
                                   QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if result==QMessageBox.StandardButton.Discard:
            self.player.stop()
            self.recorder.stop(keep=False);self.end_recording_view()

    def toggle_pause(self):
        if self.recorder.active:
            paused=self.recorder.state=='Paused'
            if paused and self._record_context and self._record_context['target']=='punch' and not self._record_context.get('play_started'):
                self._record_context['wait_deadline']=time.monotonic()+2
            if paused and self._record_context and self._record_context.get('clock') is not None:self._record_context['clock'].new_segment()
            if not paused and self.player.state=='Playing':self.player.toggle_pause()
            self.recorder.toggle_pause()
            if paused and self.player.state=='Paused':self.player.toggle_pause()
        else:self.player.toggle_pause()

    def stop_transport(self):
        if self.recorder.active:self.stop_recording()
        else:self.player.stop()

    @long_operation
    def apply_recorded_take(self,take,context):
        data=take.samples
        if context.get('automatic_sync'):
            skipped=getattr(self.recorder,'skipped_frames',0)*context['rate']/take.rate
            fallback=context.get('anchor',context['start'])-skipped
            clock=context.get('clock')
            fit=clock.result(fallback) if clock is not None else None
            ratio=fit.ratio if fit is not None else 1
            frames=max(1,round(take.frames*context['rate']/take.rate*ratio))
            if frames!=take.frames or take.rate!=context['rate']:data=resample_frames(data,frames,take.rate)
            calibration=context.get('calibration') or {}
            correction=calibration.get('offset_ms',0)*context['rate']/1000
            context['synchronized_position']=round((fit.anchor if fit is not None else fallback)+skipped*ratio+correction)
            context['sync_result']=fit
        elif take.rate!=context['rate']:data=resample(data,take.rate,context['rate'])
        target=context['target']
        if target=='new':
            doc=Document(sample_rate=context['rate'],channels=context['channels'],encoding='float32',dsp=self.document.dsp)
            doc.replace(0,0,data,'Record');doc.display_name='Recording '+datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.document=doc;self.editing_clip_id=None;self.mode='waveform'
        elif target in ('multitrack','punch'):
            if self.session is not context['session'] or self.session.revision!=context['revision']:
                raise AudioError('The destination changed; the take is available under Recover Work.')
            position=context.get('synchronized_position',context.get('anchor',context['start']))+round(context.get('recording_offset_ms',0)*context['rate']/1000)
            if target=='punch':
                if not context.get('play_started') or 'anchor' not in context:
                    context['outside_punch']=True;return False
                first=max(context['punch_in'],position);last=min(context['punch_out'],position+len(data))
                if last<=first:context['outside_punch']=True;return False
                body=data[first-position:last-position]
                self.session.punch_audio(body,context['track'],first,fade_frames=min(context['punch_fade'],len(body)//2))
                self.mode='multitrack';return True
            if position<0:
                data=data[min(len(data),-position):];position=0
            if not len(data): raise AudioError('The position offset removes the whole take. Recover it as a new waveform.')
            self.session.import_audio([(data,context['rate'],'Recording '+datetime.now().strftime('%H-%M-%S'))],
                                      context['track'],position,label='Record')
            self.mode='multitrack'
        else:
            if self.document is not context['document'] or self.document.revision!=context['revision']:
                raise AudioError('The destination changed; the take is available under Recover Work.')
            self.document.replace(context['start'],context['end'],data,'Record')
        return True

    def recording_finished(self,take):
        self.player.stop()
        context=self._record_context
        if context is None:
            take.leave_for_recovery();return
        success=False;self._applying_recording=True;self.update_recording_actions()
        try:success=self.apply_recorded_take(take,context)
        except (ValueError,OSError,RuntimeError) as error:self.error('Recording',error)
        finally:
            self._applying_recording=False;self.end_recording_view(fit=bool(success))
            if success and self._recovery_error is None:take.discard()
            else:
                take.leave_for_recovery()
                self.statusBar().showMessage('No audio inside the punch interval. The take was kept under File → Recover Work.' if context.get('outside_punch') else 'Recording kept for recovery. Use File → Recover Work.',12000)
        if success and context.get('automatic_sync'):self.statusBar().showMessage('Recording synchronized.',8000)

    def end_recording_view(self,fit=False):
        self._punch_wait_timer.stop()
        if self._record_context and self._record_context.get('accompaniment'):self.player.stop()
        context=self._record_context
        self._record_context=None;self.recording_view.stop();self.recording_view.bins.clear()
        if context is not None:self.player.loop=context.get('playback_loop',self.player.loop)
        if context is not None:
            for key,enabled in context.get("actions",{}).items():self.actions[key].setEnabled(enabled)
        self.editor_stack.setCurrentIndex(1 if self.mode=='multitrack' else 0)
        self.multitrack.set_session(self.session,fit=fit)
        self.actions['mode_multi'].setChecked(self.mode=='multitrack');self.actions['mode_wave'].setChecked(self.mode=='waveform')
        self.actions['play'].setText('Play / Stop')
        self.refresh(fit=fit);self.update_meters(None)
        self.state_label.setText('Stopped')

    def recording_failed(self,message):
        if self.recording_busy and not self.recorder.active:self.end_recording_view()
        self.error('Recording',message)

    def recording_output_failed(self,message):
        if self.recording_busy and self._record_context.get('accompaniment'):
            self.recorder.stop()
            if self.recording_busy:self.end_recording_view()

    def confirm_recording_close(self):
        if not self.recording_busy:return True
        if self._applying_recording or self.recorder.state in ('Starting','Finishing'):return False
        result=QMessageBox.question(self,'Stop Recording','Stop and keep the recording before closing?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if result==QMessageBox.StandardButton.Cancel:return False
        self.player.stop()
        self.recorder.stop(keep=result==QMessageBox.StandardButton.Save)
        if self.recording_busy:self.end_recording_view()
        return True

    @long_operation
    def restore_recorded_take(self,owner):
        take=recover_take(owner)
        try:
            context=dict(target='new',rate=take.rate,channels=take.channels)
            if not self.apply_recorded_take(take,context):return False
            self.end_recording_view(fit=True)
            if self._recovery_error is None:take.discard()
            return True
        finally:take.leave_for_recovery()
