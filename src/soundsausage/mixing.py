"""Bounded, sequential session rendering shared by live playback and mixdown."""
import numpy as np

from .audio import AudioError
from .session import balance
from .trackfx import Rack
from . import storage


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
        for key in set(self.racks)-active: self.racks.pop(key).close()
        for track in tracks:
            rack = self.racks.setdefault(track.id, Rack(self.sample_rate, self.session.dsp))
            if track.muted or (solo and not track.solo):
                # No stale reverb is retained across a muted region.
                rack.close(); continue
            effects = any(e.enabled for e in track.effects)
            destination = np.zeros_like(output) if effects else output
            tl, tr = balance(track.gain, track.pan)
            for clip in track.clips:
                if clip.muted: continue
                left, right = max(a, clip.start), min(b, clip.end)
                if right <= left: continue
                offset = left-clip.start
                source = self.media[clip.media_id].samples[clip.source_start+offset:clip.source_start+offset+right-left]
                cl, cr = balance(clip.gain, clip.pan)
                self.session.dsp.mix_add(destination[left-a:right-a], source, 0, offset, clip.frames,
                    clip.fade_in, clip.fade_out, cl if effects else tl*cl, cr if effects else tr*cr,
                    source_offset=clip.source_start+offset, volume_envelope=clip.volume_envelope,
                    pan_envelope=clip.pan_envelope)
                storage.release_pages(source)
            if effects:
                rack.process(destination, track.effects)
                output[:, 0] += destination[:, 0]*tl
                output[:, 1] += destination[:, 1]*tr
            else: rack.close()
        if not np.isfinite(output).all(): raise AudioError('The live mix overflowed. Reduce track levels.')
        self.position += count
        return output

    def reset(self):
        self.close(); self.position = 0

    def close(self):
        for rack in self.racks.values(): rack.close()
        self.racks.clear()
