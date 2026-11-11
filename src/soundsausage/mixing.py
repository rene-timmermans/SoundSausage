"""Bounded, sequential session rendering shared by live playback and mixdown."""
import numpy as np

from .audio import AudioError
from .session import balance
from .trackfx import Rack
from . import storage
from .operations import progress


class TrackStream:
    """Read a track ahead by its reported insert delay, with one bounded block."""
    def __init__(self,owner,rack,start):
        self.owner,self.rack=owner,rack
        self.signature=None;self.position=start;self.raw_position=start
        self.delay=None;self.skip=0;self.buffer=np.empty((0,2),np.float32)
        self.state_tokens={}

    def reset(self,start):
        self.rack.close();self.position=self.raw_position=start
        self.delay=None;self.skip=0;self.buffer=np.empty((0,2),np.float32)

    def raw(self,track,count):
        a,b=self.raw_position,self.raw_position+count
        output=np.zeros((count,2),np.float32)
        for clip in track.clips:
            if clip.muted:continue
            left,right=max(a,clip.start),min(b,clip.end)
            if right<=left:continue
            offset=left-clip.start
            source=self.owner.media[clip.media_id].samples[clip.source_start+offset:clip.source_start+offset+right-left]
            cl,cr=balance(clip.gain,clip.pan)
            self.owner.session.dsp.mix_add(output[left-a:right-a],source,0,offset,clip.frames,
                clip.fade_in,clip.fade_out,cl,cr,source_offset=clip.source_start+offset,
                volume_envelope=clip.volume_envelope,pan_envelope=clip.pan_envelope)
            storage.release_pages(source)
        self.raw_position=b
        self.rack.process(output,track.effects)
        return output

    def read(self,track,start,count):
        tokens=[]
        for spec in track.effects:
            state=None
            if spec.kind=='plugin':
                previous=self.state_tokens.get(spec.id)
                if previous is None or previous[0]!=spec.parameters:
                    previous=(spec.parameters,spec.settings.get('state'));self.state_tokens[spec.id]=previous
                state=previous[1]
            tokens.append((spec.id,spec.kind,spec.enabled,state))
        signature=tuple(tokens)
        if signature!=self.signature or start!=self.position:
            self.reset(start);self.signature=signature
        output=np.empty((count,2),np.float32);written=0;restarts=0;blocks=0
        while written<count:
            if not len(self.buffer):
                block=self.raw(track,min(1024,count-written+self.skip))
                delay=self.rack.latency
                if delay>self.owner.sample_rate*10:raise AudioError('The track processing delay exceeds ten seconds.')
                if self.delay is None:self.delay=delay;self.skip=delay
                elif delay!=self.delay:
                    # A preset may change a plug-in's algorithmic delay. Start the
                    # new configuration at the current logical output position.
                    restarts+=1
                    if restarts>3:raise AudioError('The plug-in processing delay keeps changing.')
                    self.reset(start);written=0;continue
                skip=min(self.skip,len(block));self.skip-=skip;self.buffer=block[skip:]
                blocks+=1
                if blocks%32==0:progress(0,1,'Spoorvertraging compenseren')
                if not len(self.buffer):continue
            n=min(len(self.buffer),count-written)
            output[written:written+n]=self.buffer[:n];self.buffer=self.buffer[n:];written+=n
        self.position=start+count
        return output


class SessionStream:
    channels = 2
    def __init__(self, session, start=0, end=None, *, live=True):
        self.session, self.start = session, start
        self.end = session.frames if end is None else end
        if not 0 <= start <= self.end <= session.sample_rate*86400:
            raise AudioError('Invalid playback range.')
        self.sample_rate = session.sample_rate
        self.frames = self.end-start
        self.tracks = None if live else session.tracks
        self.media = dict(session.media)
        self.racks = {}
        self.pipes = {}
        self.position = 0

    def __len__(self): return self.frames

    def read(self, count):
        count = min(max(0, count), self.frames-self.position)
        a, b = self.start+self.position, self.start+self.position+count
        tracks = self.session.tracks if self.tracks is None else self.tracks
        # Hold immutable media references even if an edit removes them from the model.
        current_media = dict(self.session.media)
        self.media.update(current_media)
        needed = {clip.media_id for track in tracks for clip in track.clips}
        self.media = {key: value for key, value in self.media.items() if key in needed or key in current_media}
        output = np.zeros((count, 2), np.float32)
        solo = any(t.solo for t in tracks)
        active = {t.id for t in tracks}
        for key in set(self.racks)-active:
            self.racks.pop(key).close();self.pipes.pop(key,None)
        for track in tracks:
            if track.muted or (solo and not track.solo):
                # No stale reverb is retained across a muted region.
                if track.id in self.racks:self.racks.pop(track.id).close()
                self.pipes.pop(track.id,None);continue
            rack = self.racks.setdefault(track.id, Rack(self.sample_rate, self.session.dsp))
            pipe = self.pipes.setdefault(track.id,TrackStream(self,rack,a))
            tl, tr = balance(track.gain, track.pan)
            destination=pipe.read(track,a,count)
            output[:,0]+=destination[:,0]*tl;output[:,1]+=destination[:,1]*tr
        if not np.isfinite(output).all(): raise AudioError('The live mix overflowed. Reduce track levels.')
        self.position += count
        return output

    def reset(self):
        self.close(); self.position = 0

    def close(self):
        for rack in self.racks.values(): rack.close()
        self.racks.clear()
        self.pipes.clear()
