"""Exact reusable min/max pyramids over immutable audio, including disk buffers."""
import math
import weakref
import numpy as np

from . import storage
from .operations import blocks, progress

BASE = 256
_cache = {}


def prepare(samples):
    root = storage.root_array(samples)
    if root.ndim != 2 or not root.flags.c_contiguous or root.nbytes <= storage.MEMORY_THRESHOLD:
        return None
    key = id(root)
    if key in _cache and _cache[key][0]() is root:
        return _cache[key][1]
    count = (len(root) + BASE-1)//BASE
    level = storage.allocate((count, root.shape[1], 2))
    progress(0,len(root),"Golfvorm voorbereiden")
    for a,b in blocks(len(root)):
        full = (b-a)//BASE*BASE
        if full:
            group = root[a:a+full].reshape(-1,BASE,root.shape[1])
            level[a//BASE:(a+full)//BASE,:,0] = group.min(axis=1)
            level[a//BASE:(a+full)//BASE,:,1] = group.max(axis=1)
        if full < b-a:
            level[(a+full)//BASE,:,0] = root[a+full:b].min(axis=0)
            level[(a+full)//BASE,:,1] = root[a+full:b].max(axis=0)
        storage.release_pages(root)
        if isinstance(level,np.memmap):
            level.flush(); storage.release_pages(level)
        progress(b,len(root),"Golfvorm voorbereiden")
    levels = [storage.seal(level,checked=True)]
    while len(levels[-1]) > 1:
        previous = levels[-1]
        level = storage.allocate(((len(previous)+1)//2,root.shape[1],2))
        for a,b in blocks(len(level)):
            paired = min(b,len(previous)//2)
            if paired > a:
                level[a:paired,:,0] = np.minimum(previous[2*a:2*paired:2,:,0],previous[2*a+1:2*paired:2,:,0])
                level[a:paired,:,1] = np.maximum(previous[2*a:2*paired:2,:,1],previous[2*a+1:2*paired:2,:,1])
            if paired < b:
                level[paired:b] = previous[-1]
            storage.release_pages(previous)
            if isinstance(level,np.memmap):
                level.flush();storage.release_pages(level)
            progress(b,len(level),"Golfvorm samenvatten")
        levels.append(storage.seal(level,checked=True))
    _cache[key] = (weakref.ref(root,lambda ref,k=key: _cache.pop(k,None)),levels)
    return levels


def bounds(samples, start, end):
    """Exact extrema for a nonempty half-open frame range."""
    levels = prepare(samples)
    if levels is None:
        # Small RAM roots need no persistent index. Noncontiguous callers stay bounded.
        low = np.full(samples.shape[1],np.inf,np.float32)
        high = -low
        for a,b in blocks(end-start):
            data=samples[start+a:start+b]
            low=np.minimum(low,data.min(axis=0));high=np.maximum(high,data.max(axis=0))
        return low,high
    root=storage.root_array(samples)
    offset=(samples.ctypes.data-root.ctypes.data)//(4*root.shape[1])
    a,b=start+offset,end+offset
    first,last=(a+BASE-1)//BASE,b//BASE
    low=np.full(root.shape[1],np.inf,np.float32);high=-low
    for p,q in ((a,min(b,first*BASE)),(max(a,last*BASE),b)):
        if q>p:
            low=np.minimum(low,root[p:q].min(axis=0));high=np.maximum(high,root[p:q].max(axis=0))
    while first < last:
        remaining=last-first
        power=min((first & -first).bit_length()-1 if first else len(levels)-1,remaining.bit_length()-1,len(levels)-1)
        value=levels[power][first>>power]
        low=np.minimum(low,value[:,0]);high=np.maximum(high,value[:,1])
        storage.release_pages(levels[power])
        first+=1<<power
    # Page read-ahead can otherwise populate a whole long mapping while only
    # touching the small edges of each screen column.
    storage.release_pages(root)
    return low,high


def piece_peaks(pieces, frames, channels, columns):
    if frames < columns:
        data=np.concatenate(pieces) if pieces else np.empty((0,channels),np.float32)
        return data,data,False
    edges=np.linspace(0,frames,columns+1,dtype=np.int64)
    low=np.full((columns,channels),np.inf,np.float32);high=-low
    offset=0
    for piece in pieces:
        stop=offset+len(piece)
        first=max(0,int(np.searchsorted(edges,offset,side='right'))-1)
        last=min(columns,int(np.searchsorted(edges,stop,side='left')))
        for i in range(first,last):
            a,b=max(0,int(edges[i])-offset),min(len(piece),int(edges[i+1])-offset)
            if b>a:
                p,q=bounds(piece,a,b)
                low[i]=np.minimum(low[i],p);high[i]=np.maximum(high[i],q)
        storage.release_pages(piece)
        for level in prepare(piece) or ():
            storage.release_pages(level)
        offset=stop
    return low,high,True
