"""Conservative drum-gated recovery of sustained sound in a finished stereo mix.

Linked harmonic/percussive masks follow median-filter HPSS (FitzGerald, DAFx-10).
Only short dips in sustained mid/high sound are lifted; bass is left unboosted.
The final ceiling is achieved with one constant attenuation, not compression.
"""
import math

import numpy as np

from . import storage
from .filters import number
from .operations import blocks, progress

EFFECTS = ('remaster',)


def parameters(amount=60, recovery_db=4, sensitivity_db=3, release_ms=180, ceiling_db=-1):
    return (number(amount,0,100,'Recovery amount')/100,
            number(recovery_db,0,9,'Maximum recovery'),
            number(sensitivity_db,0,12,'Drum threshold'),
            number(release_ms,50,500,'Recovery time')/1000,
            10**(number(ceiling_db,-12,0,'Output ceiling')/20))


def _geometry(rate, frames):
    size=min(8192,max(256,2**round(math.log2(rate*.046))))
    hop=size//4
    return size,hop,(frames+hop-1)//hop+3


def _spectra(source, first, stop, size, hop, window, source_gain):
    left=first*hop-(size-hop);right=(stop-1)*hop+hop
    data=np.zeros((right-left,source.shape[1]),np.float32)
    a,b=max(0,left),min(len(source),right)
    if b>a:data[a-left:b-left]=np.asarray(source[a:b],np.float64)*source_gain
    if not np.isfinite(data).all():raise ValueError('Invalid remaster audio.')
    view=np.lib.stride_tricks.sliding_window_view(data,size,axis=0)[::hop]
    return np.fft.rfft(view.transpose(0,2,1)*window[None,:,None],axis=1)


def _separate(source, first, stop, total, size, hop, window, source_gain):
    context=8
    a,b=max(0,first-context),min(total,stop+context)
    spectra=_spectra(source,a,b,size,hop,window,source_gain)
    magnitude=np.sqrt(np.mean(abs(spectra)**2,axis=2))
    temporal=np.pad(magnitude,((context,context),(0,0)),mode='edge')
    harmonic=np.median(np.lib.stride_tricks.sliding_window_view(temporal,17,axis=0),axis=-1)
    frequency=np.pad(magnitude,((0,0),(context,context)),mode='edge')
    percussive=np.median(np.lib.stride_tricks.sliding_window_view(frequency,17,axis=1),axis=-1)
    mask=harmonic**2/(harmonic**2+percussive**2+1e-20)
    offset=first-a
    return spectra[offset:offset+stop-first],mask[offset:offset+stop-first]


def _median(values, radius, first, stop):
    a,b=max(0,first-radius),min(len(values),stop+radius)
    part=np.asarray(values[a:b],np.float64)
    part=np.pad(part,((max(0,radius-first),max(0,stop+radius-len(values))),(0,0)),mode='edge')
    return np.median(np.lib.stride_tricks.sliding_window_view(part,2*radius+1,axis=0),axis=-1)


def process_blocks(name, source, rate, *, amount=60, recovery_db=4, sensitivity_db=3,
                   release_ms=180, ceiling_db=-1, limit=None, block_frames=262144):
    if name!='remaster':raise ValueError('Unknown remaster effect.')
    amount,maximum,threshold,release,ceiling=parameters(amount,recovery_db,sensitivity_db,release_ms,ceiling_db)
    number(rate,1000,384000,'Sample rate')
    if (not isinstance(source,np.ndarray) or source.ndim!=2 or source.shape[1] not in (1,2)
            or type(block_frames) is not int or block_frames<1):
        raise ValueError('Invalid remaster audio.')
    frames,channels=source.shape
    wanted=frames if limit is None else min(frames,max(0,int(limit)))
    if not wanted:return storage.seal(storage.allocate((0,channels)),checked=True)
    # A complete processed range is needed to apply one output gain, including previews.
    result=storage.allocate((frames,channels),zero=True)
    size,hop,total=_geometry(rate,frames)
    window=np.sqrt(np.hanning(size+1)[:-1])
    frequencies=np.fft.rfftfreq(size,1/rate)
    crossover=np.clip((frequencies-180)/420,0,1)
    high_weight=crossover*crossover*(3-2*crossover)
    bass=(frequencies>=30)&(frequencies<min(180,rate*.4))
    weights=np.full(size//2+1,2.,np.float64);weights[[0,-1]]=1
    normalization=size*float(np.sum(window.astype(np.float64)**2))
    batch=max(8,min(64,block_frames//hop))
    source_gain=1.
    if amount and maximum:
        input_peak=0.
        for a,b in blocks(frames,block_frames):
            data=np.asarray(source[a:b])
            if not np.isfinite(data).all():raise ValueError('Invalid remaster audio.')
            input_peak=max(input_peak,float(np.max(abs(data))))
            storage.release_pages(source)
            progress(b,frames,'Remaster analysis')
        source_gain=min(1.,1/input_peak) if input_peak else 1.
        features=storage.allocate((total,3))
        progress(0,total*3,'Remaster analysis')
        for first in range(0,total,batch):
            stop=min(total,first+batch)
            spectra,mask=_separate(source,first,stop,total,size,hop,window,source_gain)
            power=np.mean(abs(spectra)**2,axis=2)*weights[None,:]/normalization
            energy=np.column_stack(((power*mask**2*high_weight).sum(axis=1),
                                    power[:,bass].sum(axis=1),
                                    (power*(1-mask)**2*high_weight).sum(axis=1)))
            features[first:stop]=10*np.log10(np.maximum(energy,1e-15))
            storage.release_pages(source)
            progress(stop,total*3,'Remaster analysis')
        features=storage.seal(features,checked=True)
        gain=storage.allocate((total,1),zero=True)
        radius=max(2,round(.45*rate/hop))
        gate=smoothed=0.
        gate_decay=math.exp(-hop/(release*rate))
        attack=math.exp(-hop/(.012*rate));recover=math.exp(-hop/(.06*rate))
        for first in range(0,total,512):
            stop=min(total,first+512)
            baseline=_median(features,radius,first,stop)
            current=np.asarray(features[first:stop],np.float64)
            event=np.clip((np.maximum(current[:,1]-baseline[:,1],current[:,2]-baseline[:,2])-threshold)/6,0,1)
            missing=np.clip(baseline[:,0]-current[:,0],0,maximum)
            missing[current[:,0]<-60]=0
            for i in range(stop-first):
                gate=max(float(event[i]),gate*gate_decay)
                target=float(missing[i])*gate*amount
                coefficient=attack if target>smoothed else recover
                smoothed=coefficient*smoothed+(1-coefficient)*target
                gain[first+i,0]=smoothed
            progress(total+stop,total*3,'Recovering musical detail')
        gain=storage.seal(gain,checked=True)
        for first in range(0,total,batch):
            stop=min(total,first+batch)
            spectra,mask=_separate(source,first,stop,total,size,hop,window,source_gain)
            boosts=10**(np.asarray(gain[first:stop,0],np.float64)/20)-1
            spectra*=1+mask[:,:,None]*high_weight[None,:,None]*boosts[:,None,None]
            samples=np.fft.irfft(spectra,n=size,axis=1)*window[None,:,None]/2
            for i in range(stop-first):
                start=(first+i)*hop-(size-hop)
                a,b=max(0,start),min(frames,start+size)
                if b>a:result[a:b]+=samples[i,a-start:b-start]
            storage.release_pages(source)
            if isinstance(result,np.memmap):result.flush();storage.release_pages(result)
            progress(total*2+stop,total*3,'Recovering musical detail')
    else:
        for a,b in blocks(frames,block_frames):
            if not np.isfinite(source[a:b]).all():raise ValueError('Invalid remaster audio.')
            result[a:b]=source[a:b]
            progress(b,frames,'Remaster analysis')
    peak=0.
    for a,b in blocks(frames,block_frames):
        peak=max(peak,float(np.max(abs(result[a:b]))))
        storage.release_pages(result)
        progress(b,frames,'Setting output headroom')
    attenuation=min(1/source_gain,ceiling/peak) if peak else 1.
    if attenuation!=1:
        for a,b in blocks(frames,block_frames):
            result[a:b]*=attenuation
            storage.release_pages(result)
            progress(b,frames,'Setting output headroom')
    return storage.seal(result,checked=True)[:wanted]
