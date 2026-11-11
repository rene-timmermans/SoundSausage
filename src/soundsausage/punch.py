"""Non-destructive covered regions in source-frame coordinates, with crossfades."""
import numpy as np
from .audio import AudioError

MAX_REGIONS=1024


def validate_ranges(values,source_frames):
    if not isinstance(values,(tuple,list)) or len(values)>MAX_REGIONS:raise AudioError('Invalid or oversized punch region list.')
    result=[];bound=max(source_frames,384000*86400)
    for row in values:
        if not isinstance(row,(tuple,list)) or len(row)!=3:raise AudioError('Invalid punch region.')
        a,b,fade=row
        if any(isinstance(n,bool) or not isinstance(n,(int,np.integer)) for n in row):raise AudioError('Punch positions must be whole samples.')
        if not -bound<=a<b<=2*bound or not 0<=fade<=(b-a)//2:raise AudioError('A punch region is outside the supported range.')
        result.append((int(a),int(b),int(fade)))
    return tuple(sorted(set(result)))


def gain(values,start,count):
    result=np.ones(count,np.float64)
    positions=np.arange(start,start+count,dtype=np.int64)
    for a,b,fade in values:
        if b<=start or a>=start+count:continue
        inside=(positions>=a)&(positions<b)
        envelope=np.ones(count,np.float64);envelope[inside]=0
        if fade>1:
            edge=np.maximum(1-(positions-a)/(fade-1),1-(b-1-positions)/(fade-1))
            envelope[inside]=np.clip(edge[inside],0,1)
        elif fade==1:envelope[(positions==a)|(positions==b-1)]=1
        result=np.minimum(result,envelope)
    return result


def remap(values,start,end,frames):
    ratio=frames/(end-start);result=[]
    for a,b,fade in values:
        if b<=start or a>=end:continue
        left,right=round((a-start)*ratio),round((b-start)*ratio)
        if right>left:result.append((left,right,min((right-left)//2,round(fade*ratio))))
    return validate_ranges(result,frames)
