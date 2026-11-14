"""Bounded Qt input and durable takes, independent of waveform/session mutation.

QAudioSource pull-mode API: https://doc.qt.io/qt-6.8/qaudiosource.html
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import sys
import time
from uuid import uuid4

import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtMultimedia import QAudioSource, QAudioFormat

from .audio import AudioError
from .audio_devices import AudioDevices
from .playback import QtAudio
from .resample import frame_count
from . import storage
from .system_audio import SystemOutputDevice, SystemAudioSource, SYSTEM_OUTPUT


def input_format(device, rate, channels, first_channel=0):
    frame_count(0,rate,rate)
    if channels not in (1,2) or type(first_channel) is not int or not 0 <= first_channel < 32:
        raise AudioError("Choose mono/stereo and an available input channel.")
    preferred=device.preferredFormat()
    counts=dict.fromkeys((max(first_channel+channels,preferred.channelCount()),first_channel+channels,
                          preferred.channelCount(),
                          device.maximumChannelCount() if hasattr(device,"maximumChannelCount") else 2,2,1))
    for r in dict.fromkeys((rate,preferred.sampleRate(),48000,44100)):
        if not 1000 <= r <= 384000:continue
        for count in counts:
            if not 1 <= count <= 32:continue
            if count < first_channel+channels and not (count==1 and channels==2 and first_channel==0):continue
            for kind in dict.fromkeys((QAudioFormat.SampleFormat.Float,preferred.sampleFormat(),
                                      QAudioFormat.SampleFormat.Int16,QAudioFormat.SampleFormat.Int32,QAudioFormat.SampleFormat.UInt8)):
                if kind==QAudioFormat.SampleFormat.Unknown:continue
                fmt=QAudioFormat();fmt.setSampleRate(r);fmt.setChannelCount(count);fmt.setSampleFormat(kind)
                if device.isFormatSupported(fmt):return fmt
    raise AudioError("This input cannot provide the requested channels in a supported recording format.")


def decode_input(raw, fmt, channels, first_channel=0):
    order='<' if sys.byteorder=='little' else '>'
    kind=fmt.sampleFormat()
    if kind==QAudioFormat.SampleFormat.Float:
        data=np.frombuffer(raw,dtype=order+'f4')
    elif kind==QAudioFormat.SampleFormat.Int16:
        data=np.frombuffer(raw,dtype=order+'i2').astype(np.float32)/32768
    elif kind==QAudioFormat.SampleFormat.Int32:
        data=(np.frombuffer(raw,dtype=order+'i4').astype(np.float64)/2147483648).astype(np.float32)
    elif kind==QAudioFormat.SampleFormat.UInt8:
        data=(np.frombuffer(raw,np.uint8).astype(np.float32)-128)/128
    else:raise AudioError("Unsupported recording sample format.")
    data=data.reshape(-1,fmt.channelCount())
    if data.shape[1]==1 and channels==2:
        data=np.repeat(data,2,axis=1)
    else:data=data[:,first_channel:first_channel+channels]
    if data.shape[1]!=channels or not np.isfinite(data).all():
        raise AudioError("The input produced invalid audio; the completed recording has been retained.")
    return np.ascontiguousarray(data,dtype=np.float32)


class Take:
    """Append-only float32 audio with an atomic durable-frame journal."""
    def __init__(self, rate, channels, description='', *, owner=None, path=None, frames=0):
        self.rate,self.channels=int(rate),int(channels)
        self.description=description
        self.owner=owner or storage.Workspace()
        self.path=Path(path) if path else self.owner.path/(uuid4().hex+'.buffer')
        self.journal=self.owner.path/'recording.json'
        self.frames=int(frames)
        self._last_checkpoint=0
        self._executor=None;self._pending_checkpoint=None
        self._samples=None
        self._file=self.path.open('r+b' if path else 'x+b',buffering=0)
        os.chmod(self.path,0o600)
        self._file.seek(self.frames*self.channels*4)
        if not path:self.checkpoint()

    def append(self, samples):
        if samples.ndim!=2 or samples.shape[1]!=self.channels or not np.isfinite(samples).all():
            raise AudioError("Invalid captured audio.")
        if self._pending_checkpoint is not None and self._pending_checkpoint.done():
            self._pending_checkpoint.result();self._pending_checkpoint=None
        raw=samples.astype('<f4',copy=False).tobytes()
        offset=0
        try:
            while offset<len(raw):
                count=self._file.write(raw[offset:])
                if not count:raise OSError('The recording disk stopped accepting data.')
                offset+=count
        except BaseException:
            # A failed partial write is never advertised as a complete audio frame.
            self._file.truncate(self.frames*self.channels*4)
            self._file.seek(self.frames*self.channels*4)
            raise
        self.frames+=len(samples)
        storage.release_pages(samples)
        if time.monotonic()-self._last_checkpoint>=1 and self._pending_checkpoint is None:
            if self._executor is None:self._executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix="soundsausage-take")
            self._pending_checkpoint=self._executor.submit(self._write_checkpoint,self.frames)
            self._last_checkpoint=time.monotonic()

    def checkpoint(self):
        if self._pending_checkpoint is not None:
            self._pending_checkpoint.result();self._pending_checkpoint=None
        self._write_checkpoint(self.frames)
        self._last_checkpoint=time.monotonic()

    def _write_checkpoint(self,frames):
        # fsync runs away from Qt's event thread during capture. Only a fully
        # written prefix is advertised, even if new blocks arrive concurrently.
        self._file.flush();os.fsync(self._file.fileno())
        value=dict(format='soundsausage-recording',version=1,file=self.path.name,rate=self.rate,
                   channels=self.channels,frames=frames,description=self.description,time=time.time())
        temporary=self.journal.with_suffix('.tmp')
        try:
            with temporary.open('w',encoding='utf-8') as output:
                json.dump(value,output,allow_nan=False);output.flush();os.fsync(output.fileno())
            os.replace(temporary,self.journal)
            directory=os.open(self.owner.path,os.O_RDONLY)
            try:os.fsync(directory)
            finally:os.close(directory)
        finally:temporary.unlink(missing_ok=True)

    def finish(self):
        if self._file is not None:
            self._file.truncate(self.frames*self.channels*4)
            self.checkpoint();self._file.close();self._file=None
        if self._executor is not None:
            self._executor.shutdown(wait=True);self._executor=None
        return self

    @property
    def samples(self):
        if self._file is not None:raise AudioError("Stop the recording before applying it.")
        if self._samples is None:
            self._samples=np.memmap(self.path,dtype='<f4',mode='r',shape=(self.frames,self.channels)) if self.frames else np.empty((0,self.channels),np.float32)
            self._samples.flags.writeable=False
        return self._samples

    def _close_data(self):
        if self._executor is not None:
            self._executor.shutdown(wait=True);self._executor=None
        if self._file is not None:self._file.close();self._file=None
        self._samples=None;self._pending_checkpoint=None

    def leave_for_recovery(self):
        self._close_data();self.owner.close()

    def discard(self):
        self._close_data()
        try:
            self.journal.unlink(missing_ok=True);self.path.unlink(missing_ok=True)
        finally:self.owner.close()


def recover_take(owner):
    journal=owner.path/'recording.json'
    if journal.stat().st_size>65536:raise AudioError("Invalid recording recovery information.")
    try:
        value=json.loads(journal.read_text('utf-8'))
        if value['format']!='soundsausage-recording' or value['version']!=1:raise ValueError()
        name=value['file'];rate=value['rate'];channels=value['channels'];frames=value['frames']
        frame_count(0,rate,rate)
        if (not isinstance(name,str) or not re.fullmatch(r'[0-9a-f]{32}\.buffer',name) or
                type(channels) is not int or channels not in (1,2) or type(frames) is not int or frames<0):raise ValueError()
        path=(owner.path/name).resolve()
        if path.parent!=owner.path or path.stat().st_size<frames*channels*4:raise ValueError()
        description=value.get('description','')
        if not isinstance(description,str) or len(description)>1024:raise ValueError()
        take=Take(rate,channels,description,owner=owner,path=path,frames=frames)
        # Frames beyond the last fsynced journal were never committed.
        return take.finish()
    except (KeyError,TypeError,ValueError,OverflowError) as error:
        raise AudioError("The interrupted recording is invalid or incomplete.") from error


class Recorder(QObject):
    state_changed=Signal(str)
    samples=Signal(object,object)  # bounded decoded block, total captured frames
    timing=Signal(object)  # native input frames received, including the skipped start
    finished=Signal(object)
    failed=Signal(str)

    def __init__(self,parent=None,devices=None,source_factory=None):
        super().__init__(parent)
        self.devices=devices if devices is not None else AudioDevices(self)
        self._source_factory=source_factory or QAudioSource
        self.devices.inputs_changed.connect(self._inputs_changed)
        self.devices.outputs_changed.connect(self._outputs_changed)
        self.devices.changed.connect(self._settings_changed)
        self.source=None;self._io=None;self.take=None;self.format=None
        self.state='Stopped';self._starting=False;self._draining=False;self._tail=b''
        self._input_id='';self._channels=1;self._first_channel=0;self._limit=None
        self._generation=0
        self._timer=QTimer(self);self._timer.setInterval(10);self._timer.timeout.connect(self._drain)

    @property
    def active(self):return self.state!='Stopped'

    def _set_state(self,state):
        if self.state!=state:self.state=state;self.state_changed.emit(state)

    def start(self,rate,channels=1,first_channel=0,limit_seconds=None,*,skip_start_ms=0):
        if self.active:raise AudioError("An audio recording is already running.")
        self._generation+=1
        try:
            if not np.isfinite(skip_start_ms) or not 0<=skip_start_ms<=500:
                raise AudioError("Choose a recording start skip between 0 and 500 ms.")
            device=self.devices.input()
            self.format=input_format(device,rate,channels,first_channel)
            if limit_seconds is not None and (not np.isfinite(limit_seconds) or limit_seconds<=0):
                raise AudioError("Choose a positive recording duration.")
            self._limit=max(1,round(limit_seconds*self.format.sampleRate())) if limit_seconds is not None else None
            self._input_id=bytes(device.id()).hex();self._channels=channels;self._first_channel=first_channel
            self._tail=b''
            self._skip_remaining=round(skip_start_ms*self.format.sampleRate()/1000)
            self.skipped_frames=0
            self.received_frames=0
            self._fade_frames=max(2,round(self.format.sampleRate()*.005)) if self._skip_remaining else 0
            self._fade_position=0
            self.take=Take(self.format.sampleRate(),channels,device.description())
            factory = SystemAudioSource if isinstance(device, SystemOutputDevice) else self._source_factory
            self.source=factory(device,self.format,self)
            source=self.source
            source.setBufferSize(max(self.format.bytesPerFrame(),self.format.bytesForDuration(100000)))
            source.stateChanged.connect(self._source_changed)
            self._set_state('Starting');self._starting=True
            try:self._io=source.start()
            finally:self._starting=False
            if self._io is None or source.error()!=QtAudio.Error.NoError:
                raise AudioError("The recording input could not start. Check the selected input in Audio Hardware.")
            self._io.readyRead.connect(self._drain)
            self._timer.start();self._set_state('Recording');self._drain()
            return True
        except (ValueError,OSError,RuntimeError) as error:
            self._fail(str(error));return False

    def _drain(self,*,force=False):
        if self._draining or self._io is None or (self.state!='Recording' and not force):return
        self._draining=True
        try:
            previous_received=self.received_frames
            # Qt 6.8's read device may report zero while QAudioSource itself
            # has buffered input. Query both through their public APIs.
            available=max(0,self._io.bytesAvailable(),self.source.bytesAvailable())
            budget=min(available,16*1024*1024 if force else 8*65536)
            while budget>0:
                raw=bytes(self._io.read(min(65536,budget)))
                if not raw:break
                budget-=len(raw);raw=self._tail+raw
                length=len(raw)//self.format.bytesPerFrame()*self.format.bytesPerFrame()
                self._tail=raw[length:]
                if not length:continue
                self.received_frames+=length//self.format.bytesPerFrame()
                skipped=min(self._skip_remaining,length//self.format.bytesPerFrame())
                self._skip_remaining-=skipped;self.skipped_frames+=skipped
                raw=raw[skipped*self.format.bytesPerFrame():length]
                if not raw:continue
                data=decode_input(raw,self.format,self._channels,self._first_channel)
                if self._limit is not None:data=data[:max(0,self._limit-self.take.frames)]
                if len(data):
                    if self._fade_position<self._fade_frames:
                        count=min(len(data),self._fade_frames-self._fade_position)
                        data=data.copy()
                        gain=np.arange(self._fade_position,self._fade_position+count,dtype=np.float32)/(self._fade_frames-1)
                        data[:count]*=gain[:,None];self._fade_position+=count
                    self.take.append(data);self.samples.emit(data,self.take.frames)
                    if self.take is None or self.source is None:return
                if self._limit is not None and self.take.frames>=self._limit:
                    generation=self._generation
                    QTimer.singleShot(0,lambda:self.stop() if generation==self._generation else None)
                    break
            if self.source is not None and self.take is not None and self.received_frames>previous_received:
                queued=max(0,self._io.bytesAvailable(),self.source.bytesAvailable())//self.format.bytesPerFrame()
                self.timing.emit(self.received_frames+queued)
        except (ValueError,OSError,RuntimeError) as error:self._fail(str(error))
        finally:self._draining=False

    def toggle_pause(self):
        if self.source is None:return
        if self.state=='Recording':
            self._drain(force=True)
            if self.source is not None:
                self._set_state('Paused');self._timer.stop();self.source.suspend()
        elif self.state=='Paused':
            self._set_state('Recording');self._timer.start();self.source.resume();self._drain()

    def limit_from_now(self,seconds):
        if not self.active or self.take is None or not np.isfinite(seconds) or seconds<=0:
            raise AudioError('Invalid remaining recording duration.')
        self._limit=self.take.frames+max(1,round(seconds*self.format.sampleRate()))

    def _release_source(self):
        self._timer.stop()
        source,self.source=self.source,None
        self._io=None
        if source is not None:source.stop();source.deleteLater()

    def stop(self,keep=True):
        if self.state in ('Stopped','Finishing'):return
        self._generation+=1
        if keep:self._drain(force=True)
        if self.state=='Stopped':return  # A drain error already retained the take.
        self._set_state('Finishing');self._release_source()
        take,self.take=self.take,None
        try:
            if take is not None:
                if keep and take.frames:
                    take.finish();self._set_state('Stopped');self.finished.emit(take)
                else:take.discard()
        except (ValueError,OSError) as error:
            if take is not None:take.leave_for_recovery()
            self.failed.emit("The recording stopped; its last recovery copy was retained. "+str(error))
        finally:self._set_state('Stopped')

    def _fail(self,message):
        # Keep every complete, decodable block; an error must not erase a take.
        self._generation+=1;self._release_source()
        take,self.take=self.take,None
        try:
            if take is not None:
                if take.frames:
                    take.finish();self._set_state('Stopped');self.finished.emit(take)
                else:take.discard()
        except (ValueError,OSError):
            if take is not None:take.leave_for_recovery()
            message+=' The last durable recording copy remains under File → Recover Work.'
        self._set_state('Stopped');self.failed.emit(message)

    @Slot()
    def _source_changed(self):
        source=self.sender()
        if source is not None and source is self.source:
            self._source_state(source,source.state())

    def _source_state(self,source,state):
        if source is not self.source or self._starting:return
        if state==QtAudio.State.StoppedState:
            self._fail("The recording input stopped unexpectedly. The captured audio has been retained.")
        elif state==QtAudio.State.SuspendedState and self.state=='Recording':
            source.resume()

    def _inputs_changed(self):
        if self.source is None:return
        try:
            if bytes(self.devices.input().id()).hex()==self._input_id:return
        except AudioError:pass
        self._fail("The recording input disconnected or changed. The captured audio has been retained.")

    def _settings_changed(self):
        if self.active:self._fail("The audio settings changed during recording. The captured audio has been retained.")

    def _outputs_changed(self):
        if self.devices.input_id == SYSTEM_OUTPUT:
            self._inputs_changed()

    def shutdown(self):
        self.stop(keep=True)
