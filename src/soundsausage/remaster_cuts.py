"""Short, drum-linked mid/high dips with two-sided support and bounded disk buffers.

The source remains intact. A complementary high band replaces only confirmed
6–120 ms dips, crossfading with the ordinary HPSS result rather than stacking gain.
"""
import math
import numpy as np
from . import storage
from .operations import progress,blocks

def _release_written(array):
    if isinstance(array,np.memmap):array.flush();storage.release_pages(array)

def _sample_curve(values,positions,size,hop,upper=False):
    indices=(positions+(size/2-hop))/hop
    first=np.floor(indices).astype(np.int64);fraction=indices-first
    if upper:
        take=np.clip(first[:,None]+np.arange(-4,6),0,len(values)-1)
        return np.max(values[take,0],axis=1)
    a=np.clip(first,0,len(values)-1);b=np.clip(first+1,0,len(values)-1)
    return values[a,0]*(1-fraction)+values[b,0]*fraction

def repair(source,detail,result,rate,source_gain,gain,gate,size,hop,amount,maximum,block_frames=262144):
    """Repair short dips without lifting bass, silence or an unsupported fade-out."""
    frames=len(source);step=max(1,round(rate*.001));count=(frames+step-1)//step
    # Four-millisecond linked RMS, sampled every millisecond, resolves dips that
    # the ordinary spectral gain (one value per FFT hop) cannot follow closely.
    level=storage.allocate((count,1));batch=max(1,min(4096,block_frames//step));half=max(1,round(rate*.002))
    for first in range(0,count,batch):
        stop=min(count,first+batch);centers=np.arange(first,stop)*step
        a=max(0,int(centers[0])-half);b=min(frames,int(centers[-1])+half+1)
        data=np.asarray(detail[a:b],np.float64);power=np.mean(data*data,axis=1)
        prefix=np.concatenate(([0.],np.cumsum(power)))
        left=np.maximum(0,centers-half)-a;right=np.minimum(frames,centers+half+1)-a
        energy=(prefix[right]-prefix[left])/(right-left)
        level[first:stop,0]=10*np.log10(np.maximum(energy,1e-20))
        _release_written(level)
        storage.release_pages(detail);progress(stop,count*3,'Repairing short volume drops')
    level=storage.seal(level,checked=True)
    raw=storage.allocate((count,2),zero=True)
    outer=max(2,round(.080*rate/step));inner=max(1,round(.020*rate/step))
    min_run=max(2,round(.006*rate/step));max_run=max(min_run,round(.120*rate/step))
    pending=[];too_long=False
    def finish():
        nonlocal pending,too_long
        if not too_long and len(pending)>=min_run:
            start=pending[0][0];raw[start:start+len(pending),0]=[v for _,v in pending]
        pending=[];too_long=False
    for first in range(0,count,512):
        stop=min(count,first+512);a=max(0,first-outer);b=min(count,stop+outer)
        padded=np.pad(np.asarray(level[a:b,0]),(max(0,outer-first),max(0,stop+outer-count)),mode='edge')
        windows=np.lib.stride_tricks.sliding_window_view(padded,outer*2+1)
        # Both sides must support the missing sound; a one-way fade is not a hole.
        reference=np.minimum(np.median(windows[:,:outer-inner+1],axis=1),np.median(windows[:,outer+inner:],axis=1))
        current=np.asarray(level[first:stop,0]);missing=np.maximum(0,reference-current)
        detection=_sample_curve(gate,np.arange(first,stop)*step,size,hop)
        raw[first:stop,1]=np.minimum(maximum,missing)*amount
        eligible=(missing>=4)&(detection>=.25)&(current>-65)
        for offset,valid in enumerate(eligible):
            if valid:
                if not too_long:
                    pending.append((first+offset,min(maximum,float(missing[offset]))*amount))
                    if len(pending)>max_run:pending=[];too_long=True
            else:finish()
        storage.release_pages(level);storage.release_pages(gate);_release_written(raw)
        progress(count+stop,count*3,'Repairing short volume drops')
    finish();raw=storage.seal(raw,checked=True)
    control=storage.allocate((count,2),zero=True);ahead=max(1,round(.002*rate/step))
    attack=math.exp(-step/(rate*.0015));release=math.exp(-step/(rate*.003));smoothed=0.
    for first in range(0,count,512):
        stop=min(count,first+512);a=max(0,first-ahead);b=min(count,stop+ahead)
        padded=np.pad(np.asarray(raw[a:b,0]),(max(0,ahead-first),max(0,stop+ahead-count)),mode='edge')
        targets=np.max(np.lib.stride_tricks.sliding_window_view(padded,2*ahead+1),axis=1)
        upper=_sample_curve(gain,np.arange(first,stop)*step,size,hop,upper=True)
        for i,target in enumerate(targets):
            coefficient=attack if target>smoothed else release
            smoothed=min(float(raw[first+i,1]),coefficient*smoothed+(1-coefficient)*float(target))
            # Replace only when stronger recovery is needed, never add two gains.
            control[first+i]=(smoothed,min(1,max(0,(smoothed-float(upper[i]))/.5)))
        storage.release_pages(raw);storage.release_pages(gain);_release_written(control)
        progress(count*2+stop,count*3,'Repairing short volume drops')
    control=storage.seal(control,checked=True)
    for a,b in blocks(frames,block_frames):
        positions=np.arange(a,b)/step;first=np.minimum(count-1,positions.astype(np.int64));last=np.minimum(count-1,first+1);fraction=positions-first
        values=control[first]*(1-fraction[:,None])+control[last]*fraction[:,None]
        blend=values[:,1:];amplitude=10**(values[:,:1]/20)-1
        alternative=np.asarray(source[a:b],np.float64)*source_gain+detail[a:b]*amplitude
        result[a:b]=result[a:b]*(1-blend)+alternative*blend
        storage.release_pages(source);storage.release_pages(detail);storage.release_pages(control)
        _release_written(result)
        progress(b,frames,'Repairing short volume drops')
    return result
