"""Bounded duplex clock estimates and repeatable loopback latency measurement."""
from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np
from .audio import AudioError
from .resample import frame_count


@dataclass(frozen=True)
class ClockResult:
    anchor: float
    ratio: float=1.0
    reliable: bool=False
    drift_measured: bool=False
    error_ms: float=0.0
    pause_shifts: tuple=()  # (native input boundary, session-frame shift from the first segment)

    @property
    def ppm(self):return (self.ratio-1)*1000000


class DuplexClock:
    """Fit relative sample clocks, excluding warm-up, outliers and pause jumps."""
    def __init__(self,source_rate,session_rate):
        frame_count(0,source_rate,session_rate)
        self.source_rate,self.rate=source_rate,session_rate
        self.points=[];self.first_points=[];self.group=0;self.beginnings={};self.last=None
        self.boundaries={}

    def new_segment(self,native_frames=None):
        self.group+=1;self.last=None
        if native_frames is not None:
            if type(native_frames) is not int or native_frames<0:raise ValueError('Invalid recording boundary.')
            self.boundaries[self.group]=native_frames

    def observe(self,native_frames,playback_frame):
        if not math.isfinite(native_frames) or not math.isfinite(playback_frame) or native_frames<0:return
        x=float(native_frames)*self.rate/self.source_rate;y=float(playback_frame)
        if self.last is not None and (x<=self.last[0] or y<self.last[1]):return
        self.beginnings.setdefault(self.group,(x,y))
        point=(self.group,x,y)
        if self.points and self.points[-1][0]==self.group and y==self.points[-1][2]:self.points[-1]=point
        else:self.points.append(point)
        if self.group==0 and len(self.first_points)<512:self.first_points.append(point)
        self.last=(x,y)
        if len(self.points)>4096:self.points=self.points[::2]

    def result(self,fallback=0):
        groups=[];group_ids=[]
        for group in sorted({p[0] for p in self.points}):
            begin=self.beginnings[group]
            data=np.array([(x,y) for g,x,y in self.points if g==group and x-begin[0]>=self.rate*.2 and y-begin[1]>=self.rate*.2],np.float64)
            if len(data)>=6 and np.ptp(data[:,0])>=self.rate*.5:
                groups.append(data);group_ids.append(group)
        if not groups:return ClockResult(float(fallback))
        def estimate(parts):
            xx=xy=0
            for data in parts:
                x,y=(data-data.mean(axis=0)).T;xx+=float(x@x);xy+=float(x@y)
            return (xy/xx if xx else 1),xx
        ratio,denominator=estimate(groups)
        if not .995<=ratio<=1.005:return ClockResult(float(fallback))
        cleaned=[];cleaned_ids=[]
        for group,data in zip(group_ids,groups):
            residual=data[:,1]-ratio*data[:,0];residual-=np.median(residual)
            limit=max(self.rate*.002,float(np.median(np.abs(residual)))*4)
            keep=data[np.abs(residual)<=limit]
            if len(keep)>=6:cleaned.append(keep);cleaned_ids.append(group)
        if not cleaned:return ClockResult(float(fallback))
        ratio,denominator=estimate(cleaned)
        if not .995<=ratio<=1.005:return ClockResult(float(fallback))
        residuals=np.concatenate([data[:,1]-ratio*data[:,0]-np.median(data[:,1]-ratio*data[:,0]) for data in cleaned])
        error=float(np.sqrt(np.mean(residuals**2)))
        if error>self.rate*.02:return ClockResult(float(fallback))
        stderr=error/math.sqrt(max(1,denominator))
        # Short-lived backend scheduling/packet jitter can look like clock drift.
        # Keep calibration/placement active, but require a longer observation
        # before changing recorded duration.
        measured=max(np.ptp(data[:,0]) for data in cleaned)>=self.rate*10 and abs(ratio-1)>max(1e-8,3*stderr)
        if not measured:ratio=1.0
        first=self.first_points or self.points
        begin=self.beginnings[first[0][0]]
        offsets=np.array([y-ratio*x for _,x,y in first if x-begin[0]>=self.rate*.2 and y-begin[1]>=self.rate*.2])
        if len(offsets)<6:return ClockResult(float(fallback))
        middle=float(np.median(offsets));limit=max(self.rate*.002,float(np.median(np.abs(offsets-middle)))*4)
        offsets=offsets[np.abs(offsets-middle)<=limit]
        anchor=float(np.median(offsets));pauses=[];previous=0.
        for group,data in zip(cleaned_ids,cleaned):
            if group not in self.boundaries:continue
            residual=data[:,1]-ratio*data[:,0]
            shift=float(np.median(residual))-anchor
            uncertainty=max(self.rate*.001,3*error/math.sqrt(len(data)))
            # A pause is a separate placement change, never a clock-rate change.
            # Reject implausible scheduling jumps rather than moving arbitrary audio.
            if abs(shift)>self.rate*.5:continue
            if abs(shift-previous)<=uncertainty:shift=previous
            pauses.append((self.boundaries[group],shift));previous=shift
        return ClockResult(anchor,ratio,True,measured,error*1000/self.rate,tuple(pauses))


def align_pause_segments(samples,rate,source_rate,skipped_frames,fit):
    """Place already rate-corrected segments; retain immutable, bounded source audio.

    Gaps become silence with short fades; overlaps are joined with a linear fade.
    Only pause boundaries with a reliable clock measurement receive a shift.
    """
    from . import storage
    from .operations import blocks,progress
    boundaries=[(0,0)]
    for native,shift in fit.pause_shifts:
        frame=max(0,min(len(samples),round((native-skipped_frames)*rate/source_rate*fit.ratio)))
        offset=round(shift)
        if frame==0 or frame==len(samples):continue
        if frame<=boundaries[-1][0]:continue
        if offset!=boundaries[-1][1]:boundaries.append((frame,offset))
    if len(boundaries)==1:return samples
    pieces=[]
    for i,(start,shift) in enumerate(boundaries):
        end=boundaries[i+1][0] if i+1<len(boundaries) else len(samples)
        destination=start+shift
        if destination<0:
            start-=destination;destination=0
        if start<end:pieces.append((start,end,destination))
    length=max(destination+end-start for start,end,destination in pieces)
    output=storage.allocate((length,samples.shape[1]),zero=True)
    written=0;done=0;fade=max(2,round(rate*.005))
    progress(0,len(samples),'Audio kopiëren')
    for start,end,destination in pieces:
        overlap=max(0,min(written-destination,end-start,fade))
        previous=output[destination:destination+overlap].copy() if overlap else None
        if destination>written and written:
            count=min(fade,written)
            output[written-count:written]*=np.linspace(1,0,count,dtype=np.float32)[:,None]
        for left,right in blocks(end-start,storage.BLOCK_FRAMES):
            output[destination+left:destination+right]=samples[start+left:start+right]
            storage.release_pages(samples)
            if isinstance(output,np.memmap):output.flush();storage.release_pages(output)
            done+=right-left;progress(done,len(samples),'Audio kopiëren')
        if overlap:
            gain=np.linspace(0,1,overlap,dtype=np.float32)[:,None]
            output[destination:destination+overlap]=previous*(1-gain)+output[destination:destination+overlap]*gain
        elif destination>written:
            count=min(fade,end-start)
            output[destination:destination+count]*=np.linspace(0,1,count,dtype=np.float32)[:,None]
        written=max(written,destination+end-start)
    return storage.seal(output,checked=True)


def calibration_probe(rate):
    """Four distinct, quietly faded broadband markers, followed by a silent tail."""
    frame_count(0,rate,rate)
    size=max(64,round(rate*.06));starts=[round(rate*(.4+i*.8)) for i in range(4)]
    output=np.zeros((round(rate*3.5),2),np.float32);markers=[]
    for i,start in enumerate(starts):
        rng=np.random.default_rng(84013+i)
        signal=rng.normal(size=size)
        spectrum=np.fft.rfft(signal);frequencies=np.fft.rfftfreq(size,1/rate)
        spectrum[(frequencies<min(300,rate*.1))|(frequencies>min(6000,rate*.4))]=0
        signal=np.fft.irfft(spectrum,n=size)*np.hanning(size)
        signal-=signal.mean();peak=max(1e-12,float(np.max(np.abs(signal))))
        signal=(signal*.08/peak).astype(np.float32)
        output[start:start+size]=signal[:,None];markers.append((start,signal))
    return output,markers


def measure_latency(captured,markers,rate,anchor=0,*,diagnostics=None):
    """Return a signed placement correction; reject silence, aliases and clipping."""
    if captured.ndim!=2 or captured.shape[1] not in (1,2) or not np.isfinite(captured).all():raise AudioError('Invalid calibration recording.')
    if len(captured)<max(len(m) for _,m in markers):raise AudioError('The calibration recording is too short.')
    channel=int(np.argmax(np.mean(captured.astype(np.float64)**2,axis=0)))
    signal=captured[:,channel].astype(np.float64)
    if np.max(np.abs(signal))>=.999:raise AudioError('The calibration input clipped. Lower its level and try again.')
    length=len(signal);nfft=1<<(length+max(len(m) for _,m in markers)-2).bit_length()
    transformed=np.fft.rfft(signal,nfft)
    offsets=[];scores=[]
    for expected,marker in markers:
        count=len(marker);ref=marker.astype(np.float64);ref-=ref.mean()
        correlation=np.fft.irfft(transformed*np.conj(np.fft.rfft(ref,nfft)),nfft)[:length-count+1]
        sums=np.r_[0,np.cumsum(signal)];squared=np.r_[0,np.cumsum(signal*signal)]
        variance=np.maximum(0,squared[count:]-squared[:-count]-(sums[count:]-sums[:-count])**2/count)
        normalized=np.abs(correlation)/np.sqrt(np.maximum(1e-30,variance*float(ref@ref)))
        center=round(expected-anchor);left=max(0,center-rate*2);right=min(len(normalized),center+rate*2+1)
        if right<=left:continue
        index=left+int(np.argmax(normalized[left:right]));score=float(normalized[index])
        if score<.35:continue
        sidelobes=normalized[left:right].copy();radius=max(2,round(rate*.005))
        sidelobes[max(0,index-left-radius):min(right-left,index-left+radius+1)]=0
        if len(sidelobes) and float(np.max(sidelobes))>score*.9:continue
        fraction=0
        if 0<index<len(normalized)-1:
            a,b,c=normalized[index-1:index+2];denom=a-2*b+c
            if denom<0:fraction=float(np.clip(.5*(a-c)/denom,-.5,.5))
        offsets.append(anchor+index+fraction-expected);scores.append(score)
    if len(offsets)<3:raise AudioError('No reliable loopback signal was found. Check the input/output connection and levels.')
    median=float(np.median(offsets));spread=max(offsets)-min(offsets)
    if diagnostics is not None:
        diagnostics.update(offsets_ms=[x*1000/rate for x in offsets],spread_ms=spread*1000/rate,confidence=min(scores))
    if spread>rate*.005:raise AudioError('The calibration timing varied too much. Check the connection and try again.')
    correction=-median*1000/rate
    if abs(correction)>2000:raise AudioError('The measured recording delay exceeds two seconds.')
    return dict(offset_ms=correction,confidence=float(min(scores)),spread_ms=spread*1000/rate)


def calibration_key(devices,rate,first_channel=0,*,channels=1,input_device=None):
    from .capture import input_format
    from .playback import output_format
    source,sink=input_device or devices.input(),devices.output()
    incoming=input_format(source,rate,channels,first_channel);outgoing=output_format(sink,rate,2)
    data=dict(input=bytes(source.id()).hex(),output=bytes(sink.id()).hex(),rate=rate,channels=channels,
              input_rate=incoming.sampleRate(),input_channels=incoming.channelCount(),
              input_format=incoming.sampleFormat().value,first_channel=first_channel,
              output_rate=outgoing.sampleRate(),output_channels=outgoing.channelCount(),
              output_format=outgoing.sampleFormat().value,buffer_ms=devices.buffer_ms)
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def read_calibration(devices,rate,first_channel=0,*,channels=1,input_device=None):
    key=calibration_key(devices,rate,first_channel,channels=channels,input_device=input_device)
    value=devices.settings.value('recording/calibration/'+key,'')
    if not value:return None
    try:
        data=json.loads(value)
        if data['version']!=1 or not math.isfinite(data['offset_ms']) or abs(data['offset_ms'])>2000:return None
        return data
    except (KeyError,ValueError,TypeError):return None


def save_calibration(devices,rate,first_channel,result,*,channels=1):
    key=calibration_key(devices,rate,first_channel,channels=channels)
    offset=float(result['offset_ms'])
    if not math.isfinite(offset) or abs(offset)>2000:raise AudioError('Invalid calibration result.')
    data=dict(result,version=1)
    devices.settings.setValue('recording/calibration/'+key,json.dumps(data,allow_nan=False))
    devices.settings.sync()
