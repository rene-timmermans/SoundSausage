"""Recording setup, bounded live waveform and editor transaction integration."""
from collections import deque
from datetime import datetime

import numpy as np
from PySide6.QtCore import Qt,QPointF,QRectF,QTimer
from PySide6.QtGui import QPainter,QPen
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QLabel,QDialog,QFormLayout,QComboBox,QSpinBox,
                             QDoubleSpinBox,QDialogButtonBox,QPushButton,QHBoxLayout,QMessageBox)

from .audio import AudioError
from .capture import Recorder,input_format,recover_take
from .document import Document
from .errors import OperationCancelled
from .progress_ui import long_operation
from .resample import resample
from .theme import colors
from .waveform import clock_text


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
            self.target.addItem('New clip on '+name,'multitrack')
        elif window.document.frames:
            self.target.addItem('Insert at cursor','insert')
            if window.document.selected:self.target.addItem('Replace selection','replace')
        self.target.addItem('New waveform','new')
        self.rate=QSpinBox();self.rate.setRange(1000,384000);self.rate.setValue(window.active_model().sample_rate)
        self.channels=QComboBox();self.channels.addItems(('Mono','Stereo'));self.channels.setCurrentIndex(window.document.channels-1)
        self.first=QSpinBox();self.first.setRange(1,32);self.first.setValue(1)
        self.duration=QDoubleSpinBox();self.duration.setRange(0,86400);self.duration.setDecimals(3)
        self.duration.setSpecialValueText('Until Stop');self.duration.setSuffix(' sec')
        form.addRow('Input',self.input);form.addRow('Destination',self.target)
        form.addRow('Sample rate (Hz)',self.rate);form.addRow('Channels',self.channels)
        form.addRow('First input channel',self.first);form.addRow('Maximum duration',self.duration)
        self.note=QLabel();self.note.setWordWrap(True);form.addRow(self.note)
        form.addRow(QLabel('Stop keeps the take. Discard removes only this recording.\nThe input is not played through the speakers.'))
        self.box=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.box.button(QDialogButtonBox.StandardButton.Ok).setText('Start Recording')
        self.box.accepted.connect(self.accept);self.box.rejected.connect(self.reject);form.addRow(self.box)
        self.reload(self.devices.input_id)
        self.devices.inputs_changed.connect(self.reload)
        for field in (self.input,self.target,self.channels):field.currentIndexChanged.connect(self.sync)
        self.rate.valueChanged.connect(self.sync);self.first.valueChanged.connect(self.sync)
        self.sync()

    def reload(self,selected=None):
        selected=(self.input.currentData() or '') if selected is None else selected
        self.input.clear();self.input.addItem('System Default','')
        for device in self.devices.inputs():self.input.addItem(device.description(),bytes(device.id()).hex())
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
        existing=target in ('insert','replace');multi=target=='multitrack'
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
            text=device.description()
            if fmt.channelCount()==1 and self.channels.currentIndex()==1:
                text+='\nMono input is recorded on both stereo channels.'
            if fmt.sampleRate()!=self.rate.value():text+=f'\nInput at {fmt.sampleRate():,} Hz; the take is converted after Stop.'
            self.note.setText(text);self.box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        except (ValueError,RuntimeError) as error:
            self.note.setText(str(error));self.box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def settings(self):
        return dict(target=self.target.currentData(),rate=self.rate.value(),channels=self.channels.currentIndex()+1,
                    first_channel=self.first.value()-1,input_id=self.input.currentData(),
                    limit_seconds=self.duration.value() or None)


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
        discard=QPushButton('Discard Recording');discard.clicked.connect(window.discard_recording)
        row=QHBoxLayout();row.addStretch();row.addWidget(discard);layout.addLayout(row)

    def reset(self,rate,channels,description):
        self.rate=rate;self.channels=channels;self.frames=0;self.bins.clear()
        self.heading.setText('Recording — '+description);self._paint_timer.start();self.plot.update()

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
        width=max(1,self.width()-18);height=max(1,self.height()-28)
        for channel in range(view.channels):
            center=(channel+.5)*height/view.channels
            scale=height/view.channels*.44
            p.setPen(QPen(c.plot_grid,1));p.drawLine(QPointF(9,center),QPointF(9+width,center))
            p.setPen(QPen(c.waveform,1))
            for a,b,low,high in view.bins:
                if b<=start:continue
                x=9+(max(a,start)-start)/span*width
                p.drawLine(QPointF(x,center-min(1.08,max(-1.08,float(high[channel])))*scale),
                           QPointF(x,center-min(1.08,max(-1.08,float(low[channel])))*scale))
        p.setPen(c.plot_text)
        p.drawText(QRectF(9,height,width,26),Qt.AlignmentFlag.AlignLeft,clock_text(start/view.rate))
        p.drawText(QRectF(9,height,width,26),Qt.AlignmentFlag.AlignRight,clock_text((start+span)/view.rate))


class RecordingActions:
    def init_recording(self):
        self._record_context=None;self._applying_recording=False
        self.recorder=Recorder(self,devices=self.audio_devices)
        self.recorder.state_changed.connect(self.recording_state)
        self.recorder.samples.connect(self.recording_samples)
        self.recorder.finished.connect(self.recording_finished)
        self.recorder.failed.connect(self.recording_failed)

    @property
    def recording_busy(self):return self._record_context is not None

    def record(self):
        if self.no_audio:return
        if self.recorder.active:return self.stop_recording()
        if self.recording_busy:return
        self.player.stop()
        dialog=RecordDialog(self)
        try:
            if dialog.exec()==QDialog.DialogCode.Accepted:self.start_recording(**dialog.settings())
        finally:
            self.update_recording_actions();dialog.deleteLater()

    def start_recording(self,target='new',rate=44100,channels=2,first_channel=0,input_id=None,limit_seconds=None):
        if self.recording_busy:return False
        if target not in ('new','insert','replace','multitrack'):raise AudioError('Invalid recording destination.')
        if target=='new' and not self._confirm_discard():return False
        if target in ('insert','replace') and (rate!=self.document.sample_rate or channels!=self.document.channels):
            raise AudioError('Recording into a waveform requires its sample rate and channel count.')
        if target=='replace' and not self.document.selected:raise AudioError('Select audio to replace first.')
        if target=='multitrack' and rate!=self.session.sample_rate:raise AudioError('Use the session sample rate for recording.')
        if input_id is not None:self.audio_devices.configure(self.audio_devices.output_id,self.audio_devices.buffer_ms,input_id)
        self.player.stop()
        start,end=self.document.selection if target=='replace' else (self.active_model().cursor,self.active_model().cursor)
        if target=='multitrack':
            remaining=86400-start/rate
            if remaining<=0:raise AudioError('The recording would exceed the 24-hour timeline.')
            limit_seconds=min(limit_seconds,remaining) if limit_seconds is not None else remaining
        self._record_context=dict(target=target,rate=rate,channels=channels,start=start,end=end,
                                  document=self.document,session=self.session,revision=self.active_model().revision,
                                  track=self.session.selected_track,
                                  actions={key:action.isEnabled() for key,action in self.actions.items()})
        self.update_recording_actions()
        ok=self.recorder.start(rate,channels,first_channel,limit_seconds)
        if not ok and self.recording_busy:self.end_recording_view()
        return ok

    def update_recording_actions(self):
        if 'record' not in self.actions:return
        busy=self.recording_busy
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
        self.recording_view.feed(data,frames)
        self.time_label.setText(clock_text(frames/self.recording_view.rate))
        self.detail_label.setText(f' {frames:,} captured frames ')
        rate=self.recording_view.rate
        self.transport.set_view_range(max(0,frames-rate*20),max(frames,rate*20),rate)
        self.update_meters(data)

    def stop_recording(self):
        if self._applying_recording:return
        self.recorder.stop()
        if not self.recorder.active and self.recording_busy:self.end_recording_view()

    def discard_recording(self):
        if not self.recording_busy or self._applying_recording:return
        result=QMessageBox.question(self,'Discard Recording','Discard this take? Existing audio remains unchanged.',
                                   QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if result==QMessageBox.StandardButton.Discard:
            self.recorder.stop(keep=False);self.end_recording_view()

    def toggle_pause(self):
        if self.recorder.active:self.recorder.toggle_pause()
        else:self.player.toggle_pause()

    def stop_transport(self):
        if self.recorder.active:self.stop_recording()
        else:self.player.stop()

    @long_operation
    def apply_recorded_take(self,take,context):
        data=resample(take.samples,take.rate,context['rate']) if take.rate!=context['rate'] else take.samples
        target=context['target']
        if target=='new':
            doc=Document(sample_rate=context['rate'],channels=context['channels'],encoding='float32',dsp=self.document.dsp)
            doc.replace(0,0,data,'Record');doc.display_name='Recording '+datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.document=doc;self.editing_clip_id=None;self.mode='waveform'
        elif target=='multitrack':
            if self.session is not context['session'] or self.session.revision!=context['revision']:
                raise AudioError('The destination changed; the take is available under Recover Work.')
            self.session.import_audio([(data,context['rate'],'Recording '+datetime.now().strftime('%H-%M-%S'))],
                                      context['track'],context['start'],label='Record')
            self.mode='multitrack'
        else:
            if self.document is not context['document'] or self.document.revision!=context['revision']:
                raise AudioError('The destination changed; the take is available under Recover Work.')
            self.document.replace(context['start'],context['end'],data,'Record')
        return True

    def recording_finished(self,take):
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
                self.statusBar().showMessage('Recording kept for recovery. Use File → Recover Work.',12000)

    def end_recording_view(self,fit=False):
        context=self._record_context
        self._record_context=None;self.recording_view.stop();self.recording_view.bins.clear()
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

    def confirm_recording_close(self):
        if not self.recording_busy:return True
        if self._applying_recording or self.recorder.state in ('Starting','Finishing'):return False
        result=QMessageBox.question(self,'Stop Recording','Stop and keep the recording before closing?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if result==QMessageBox.StandardButton.Cancel:return False
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
