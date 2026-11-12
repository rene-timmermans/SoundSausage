"""Non-destructive multitrack model. All positions and source ranges use frames."""
from dataclasses import dataclass, replace
from itertools import count
import math
from types import MappingProxyType
from uuid import uuid4

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, validate_audio
from .dsp import Dsp
from . import storage, peaks, punch
from .operations import blocks, progress
from .resample import resample, frame_count
from .envelopes import validate_points, remap_points
from .trackfx import chain
from .i18n import tr


MAX_TRACKS = 32
MAX_CLIPS = 4096
MAX_MEDIA = 128
MAX_SECONDS = 24 * 3600
_ids = count(1)


def identifier():
    return uuid4().hex


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise AudioError("Names must contain between 1 and 256 characters.")
    return value.strip()


def integer(value, label="Frame", minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum or (maximum is not None and value > maximum):
        raise AudioError(f"{label} is outside the supported range.")
    return int(value)


def number(value, minimum, maximum, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise AudioError(f"{label} must be between {minimum:g} and {maximum:g}.")
    return float(value)


@dataclass(frozen=True, eq=False)
class Media:
    id: str
    name: str
    samples: np.ndarray
    sample_rate: int
    metadata: tuple = ()


@dataclass(frozen=True)
class SessionClip:
    id: str
    media_id: str
    name: str
    start: int
    source_start: int
    source_end: int
    gain: float = 1.0
    pan: float = 0.0
    fade_in: int = 0
    fade_out: int = 0
    muted: bool = False
    volume_envelope: tuple = ()
    pan_envelope: tuple = ()
    punch_ranges: tuple = ()

    @property
    def frames(self):
        return self.source_end - self.source_start

    @property
    def end(self):
        return self.start + self.frames


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    clips: tuple = ()
    gain: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    effects: tuple = ()
    tail_seconds: float = 0.0


@dataclass(frozen=True)
class SessionSnapshot:
    tracks: tuple
    sample_rate: int
    selected_clip: object
    selected_track: object
    selection: tuple
    cursor: int
    state_id: int
    label: str


def balance(gain, pan):
    """Linear balance, unity in both channels at center; mono is duplicated first."""
    return gain * (1 - max(0, pan)), gain * (1 + min(0, pan))


def bounded_fades(clip, length):
    total = clip.fade_in + clip.fade_out
    if total <= length:
        return clip.fade_in, clip.fade_out
    first = min(length, round(length * clip.fade_in / total)) if total else 0
    return first, length - first


class Session:
    channels = 2
    encoding = "float32 mix"

    def __init__(self, sample_rate=44100, track_count=4, dsp=None, adopt_first_rate=True):
        self.sample_rate = integer(sample_rate, "Sample rate", 1000, 384000)
        integer(track_count, "Track count", 1, MAX_TRACKS)
        self.dsp = dsp or Dsp()
        self.adopt_first_rate = bool(adopt_first_rate)
        self._tracks = tuple(Track(identifier(), tr(f"Track {i + 1}")) for i in range(track_count))
        self._media = {}
        self.selected_track = self._tracks[0].id
        self.selected_clip = None
        self.selection = (0, 0)
        self.cursor = 0
        self.path = None
        self._state_id = next(_ids)
        self._saved_state_id = self._state_id
        self.revision = 0
        self.undo_stack = []
        self.redo_stack = []

    @property
    def tracks(self):
        return self._tracks

    @property
    def media(self):
        return MappingProxyType(self._media)

    @property
    def frames(self):
        return min(self.sample_rate*MAX_SECONDS, max((max((clip.end for clip in track.clips), default=0)
                   + (round(track.tail_seconds*self.sample_rate) if track.clips and any(e.enabled for e in track.effects) else 0)
                   for track in self.tracks), default=0))

    @property
    def duration(self):
        return self.frames / self.sample_rate

    @property
    def dirty(self):
        return self._state_id != self._saved_state_id

    @property
    def selected(self):
        return self.selection[1] > self.selection[0]

    @property
    def effect_range(self):
        return self.selection if self.selected else (0, self.frames)

    def mark_saved(self):
        self._saved_state_id = self._state_id

    def select(self, start, end):
        a, b = sorted((int(start), int(end)))
        maximum = self.sample_rate * MAX_SECONDS
        self.selection = (max(0, min(a, maximum)), max(0, min(b, maximum)))
        self.cursor = self.selection[0]

    def track_index(self, track_id):
        for index, track in enumerate(self.tracks):
            if track.id == track_id:
                return index
        raise AudioError("That track is no longer in this session.")

    def find_clip(self, clip_id):
        for track in self.tracks:
            for clip in track.clips:
                if clip.id == clip_id:
                    return track, clip
        raise AudioError("That clip is no longer in this session.")

    def choose_clip(self, clip_id):
        track, clip = self.find_clip(clip_id)
        self.selected_track, self.selected_clip = track.id, clip.id
        self.select(clip.start, clip.end)

    def _snapshot(self, label):
        return SessionSnapshot(self.tracks, self.sample_rate, self.selected_clip,
                               self.selected_track, self.selection, self.cursor, self._state_id, label)

    def _restore(self, snapshot):
        self._tracks = snapshot.tracks
        self.sample_rate = snapshot.sample_rate
        self.selected_track, self.selected_clip = snapshot.selected_track, snapshot.selected_clip
        self.selection, self.cursor = snapshot.selection, snapshot.cursor
        self._state_id = snapshot.state_id
        self.revision += 1

    def _collect_media(self):
        states = [self._snapshot(""), *self.undo_stack, *self.redo_stack]
        keep = {clip.media_id for state in states for track in state.tracks for clip in track.clips}
        self._media = {key: value for key, value in self._media.items() if key in keep}

    def _commit(self, tracks, label, rate=None, selected_clip=None, selected_track=None):
        tracks = tuple(tracks)
        if tracks == self.tracks and (rate is None or rate == self.sample_rate):
            return
        self.undo_stack.append(self._snapshot(label))
        self.redo_stack.clear()
        self.undo_stack = self.undo_stack[-50:]
        self._tracks = tracks
        if rate is not None:
            self.sample_rate = rate
        self._state_id = next(_ids)
        self.revision += 1
        self.selected_clip = selected_clip
        if selected_track is not None:
            self.selected_track = selected_track
        if self.selected_track not in {track.id for track in self.tracks}:
            self.selected_track = self.tracks[0].id
        if selected_clip:
            self.choose_clip(selected_clip)
        self._collect_media()

    def add_track(self, name=None):
        if len(self.tracks) >= MAX_TRACKS:
            raise AudioError(f"SoundSausage supports at most {MAX_TRACKS} tracks.")
        track = Track(identifier(), text(name or tr(f"Track {len(self.tracks) + 1}")))
        self._commit((*self.tracks, track), "Add Track", selected_track=track.id)
        return track.id

    def remove_track(self, track_id):
        self.track_index(track_id)
        if len(self.tracks) == 1:
            raise AudioError("A session needs at least one track.")
        self._commit([track for track in self.tracks if track.id != track_id], "Remove Track")

    def configure_track(self, track_id, **settings):
        index = self.track_index(track_id)
        allowed = {"name", "gain", "pan", "muted", "solo", "effects", "tail_seconds"}
        if not set(settings) <= allowed:
            raise AudioError("Unknown track setting.")
        if "name" in settings:
            settings["name"] = text(settings["name"])
        if "gain" in settings:
            settings["gain"] = number(settings["gain"], 0, 100, "Volume")
        if "pan" in settings:
            settings["pan"] = number(settings["pan"], -1, 1, "Pan")
        if "effects" in settings:
            settings["effects"] = chain(settings["effects"])
        if "tail_seconds" in settings:
            settings["tail_seconds"] = number(settings["tail_seconds"], 0, 60, "Track tail")
        for name in ("muted", "solo"):
            if name in settings and not isinstance(settings[name], bool):
                raise AudioError("Mute and solo must be boolean values.")
        tracks = list(self.tracks)
        tracks[index] = replace(tracks[index], **settings)
        self._commit(tracks, "Track Settings", selected_clip=self.selected_clip, selected_track=track_id)

    def _prepare_media(self, samples, rate, name, metadata=()):
        validate_audio(samples, rate)
        if len(samples) == 0:
            raise AudioError("An empty waveform cannot become a clip.")
        data = storage.freeze(samples)
        peaks.prepare(data)
        return Media(identifier(), text(name), data, rate, metadata)

    def import_audio(self, items, track_id=None, start=None, *, label="Import Audio"):
        """Import (samples, sample_rate, name) tuples into successive tracks atomically."""
        if not items:
            return []
        target = self.track_index(track_id or self.selected_track)
        if target + len(items) > MAX_TRACKS:
            raise AudioError(f"There is room for at most {MAX_TRACKS} tracks.")
        automatic = self.adopt_first_rate and self.path is None and not any(track.clips for track in self.tracks)
        rate = items[0][1] if automatic else self.sample_rate
        integer(rate, "Sample rate", 1000, 384000)
        start = integer(self.cursor if start is None else start, "Clip position", 0, rate * MAX_SECONDS)
        total = sum(media.samples.nbytes for media in self.media.values())
        for item in items:
            samples, item_rate, name = item[:3]
            validate_audio(samples, item_rate)
            text(name)
            frames = frame_count(len(samples), item_rate, rate)
            if start + frames > rate * MAX_SECONDS:
                raise AudioError("A clip cannot extend past the 24-hour timeline limit.")
            total += frames * samples.shape[1] * 4
        if total > MAX_AUDIO_BYTES or len(self.media) + len(items) > MAX_MEDIA:
            raise AudioError("A session supports at most 128 media items, including undo history.")
        if sum(len(track.clips) for track in self.tracks) + len(items) > MAX_CLIPS:
            raise AudioError("There are too many clips in this session.")
        from .metadata import resample as remap_metadata
        prepared = []
        for item in items:
            samples, item_rate, name = item[:3]
            info = item[3] if len(item) == 4 else ()
            prepared.append(self._prepare_media(resample(samples,item_rate,rate) if item_rate != rate else samples,
                rate,name,remap_metadata(info,item_rate,rate,frame_count(len(samples),item_rate,rate)) if item_rate != rate else info))
        tracks = list(self.tracks)
        while len(tracks) < target + len(items):
            tracks.append(Track(identifier(), tr(f"Track {len(tracks) + 1}")))
        result = []
        for i, media in enumerate(prepared):
            clip = SessionClip(identifier(), media.id, media.name, start, 0, len(media.samples))
            tracks[target + i] = replace(tracks[target + i], clips=(*tracks[target + i].clips, clip))
            result.append(clip.id)
        self._media.update({media.id: media for media in prepared})
        self._commit(tracks, label, rate=rate, selected_clip=result[0], selected_track=tracks[target].id)
        return result

    def _validate_clip(self, clip):
        if clip.media_id not in self.media:
            raise AudioError("A clip refers to missing audio.")
        source = self.media[clip.media_id]
        text(clip.name)
        integer(clip.start, "Clip position", 0, self.sample_rate * MAX_SECONDS)
        integer(clip.source_start, "Source begin", 0, len(source.samples))
        integer(clip.source_end, "Source end", clip.source_start + 1, len(source.samples))
        if clip.end > self.sample_rate * MAX_SECONDS:
            raise AudioError("A clip cannot extend past the 24-hour timeline limit.")
        number(clip.gain, 0, 100, "Clip volume")
        number(clip.pan, -1, 1, "Clip pan")
        integer(clip.fade_in, "Fade in", 0, clip.frames)
        integer(clip.fade_out, "Fade out", 0, clip.frames - clip.fade_in)
        if not isinstance(clip.muted, bool):
            raise AudioError("Clip mute must be a boolean value.")
        for kind in ("volume", "pan"):
            points = getattr(clip, kind + "_envelope")
            if not isinstance(points, tuple) or any(not isinstance(point, tuple) for point in points):
                raise AudioError("Envelope points must be immutable.")
            validate_points(points, kind, len(source.samples))
        if not isinstance(clip.punch_ranges,tuple) or any(not isinstance(row,tuple) for row in clip.punch_ranges):
            raise AudioError('Punch regions must be immutable.')
        punch.validate_ranges(clip.punch_ranges,len(source.samples))

    def configure_clip(self, clip_id, track_id=None, **settings):
        track, original = self.find_clip(clip_id)
        if not set(settings) <= {"name", "start", "source_start", "source_end", "gain", "pan", "fade_in", "fade_out", "muted", "volume_envelope", "pan_envelope", "punch_ranges"}:
            raise AudioError("Unknown clip setting.")
        for kind in ("volume", "pan"):
            key = kind + "_envelope"
            if key in settings:
                settings[key] = validate_points(settings[key], kind, len(self.media[original.media_id].samples))
        if 'punch_ranges' in settings:settings['punch_ranges']=punch.validate_ranges(settings['punch_ranges'],len(self.media[original.media_id].samples))
        clip = replace(original, **settings)
        self._validate_clip(clip)
        destination = self.track_index(track_id or track.id)
        if clip == original and self.tracks[destination].id == track.id:
            return
        tracks = [replace(t, clips=tuple(c for c in t.clips if c.id != clip_id)) for t in self.tracks]
        tracks[destination] = replace(tracks[destination], clips=(*tracks[destination].clips, clip))
        label = "Volume Line" if set(settings) == {"volume_envelope"} else "Pan Line" if set(settings) == {"pan_envelope"} else "Restore Covered Audio" if set(settings)=={'punch_ranges'} else "Clip Settings"
        self._commit(tracks, label, selected_clip=clip.id, selected_track=tracks[destination].id)

    def set_envelope(self, clip_id, kind, points):
        if kind not in ("volume", "pan"):
            raise AudioError("Choose the volume or pan line.")
        self.configure_clip(clip_id, **{kind + "_envelope": points})

    def move_clip(self, clip_id, start, track_id=None):
        self.configure_clip(clip_id, track_id=track_id, start=start)

    def trim_clip(self, clip_id, start, end):
        _, original = self.find_clip(clip_id)
        integer(start, "Clip begin")
        integer(end, "Clip end", start + 1)
        source_start = original.source_start + (start - original.start)
        source_end = original.source_end + (end - original.end)
        fade_in, fade_out = bounded_fades(original, end - start)
        self.configure_clip(clip_id, start=start, source_start=source_start, source_end=source_end,
                            fade_in=fade_in, fade_out=fade_out)

    def remove_clip(self, clip_id):
        track, clip = self.find_clip(clip_id)
        tracks = [replace(t, clips=tuple(c for c in t.clips if c.id != clip.id)) for t in self.tracks]
        self._commit(tracks, "Remove Clip", selected_track=track.id)

    def duplicate_clip(self, clip_id):
        track, original = self.find_clip(clip_id)
        if sum(len(t.clips) for t in self.tracks) >= MAX_CLIPS:
            raise AudioError("There are too many clips in this session.")
        clip = replace(original, id=identifier(), start=original.end)
        self._validate_clip(clip)
        tracks = [replace(t, clips=(*t.clips, clip)) if t.id == track.id else t for t in self.tracks]
        self._commit(tracks, "Duplicate Clip", selected_clip=clip.id, selected_track=track.id)
        return clip.id

    def replace_clip_audio(self, clip_id, samples, sample_rate, name=None, metadata=()):
        track, original = self.find_clip(clip_id)
        if sample_rate != self.sample_rate:
            from .metadata import resample as remap_metadata
            metadata = remap_metadata(metadata, sample_rate, self.sample_rate, frame_count(len(samples),sample_rate,self.sample_rate))
            samples = resample(samples, sample_rate, self.sample_rate)
        media = self._prepare_media(samples, self.sample_rate, name or original.name, metadata)
        if sum(m.samples.nbytes for m in self.media.values()) + media.samples.nbytes > MAX_AUDIO_BYTES or len(self.media) >= MAX_MEDIA:
            raise AudioError("The edited audio would exceed the session's source-audio limit.")
        fade_in, fade_out = bounded_fades(original, len(samples))
        curves = {kind + "_envelope": validate_points(remap_points(getattr(original, kind + "_envelope"),
                    original.source_start, original.source_end, len(samples), neutral), kind, len(samples))
                  for kind, neutral in (("volume", 1.0), ("pan", 0.0))}
        clip = replace(original, media_id=media.id, source_start=0, source_end=len(samples),
                       fade_in=fade_in, fade_out=fade_out,
                       punch_ranges=punch.remap(original.punch_ranges,original.source_start,original.source_end,len(samples)),**curves)
        if clip.end > self.sample_rate * MAX_SECONDS:
            raise AudioError("The edited clip would exceed the timeline limit.")
        tracks = [replace(t, clips=tuple(clip if c.id == clip_id else c for c in t.clips)) for t in self.tracks]
        self._media[media.id] = media
        self._commit(tracks, "Apply Waveform to Clip", selected_clip=clip.id, selected_track=track.id)

    def punch_audio(self,samples,track_id,start,*,fade_frames=0,name=None):
        """Cover only this take's range on one track, retaining all original audio."""
        validate_audio(samples,self.sample_rate)
        if not len(samples):raise AudioError('There is no audio inside the punch selection.')
        start=integer(start,'Punch begin',0,self.sample_rate*MAX_SECONDS)
        end=start+len(samples)
        if end>self.sample_rate*MAX_SECONDS:raise AudioError('The punch recording exceeds the timeline limit.')
        fade=integer(fade_frames,'Crossfade',0,len(samples)//2)
        target=self.track_index(track_id)
        if len(self.media)>=MAX_MEDIA or sum(m.samples.nbytes for m in self.media.values())+samples.nbytes>MAX_AUDIO_BYTES:
            raise AudioError('The recording would exceed the session’s source-audio limit.')
        if sum(len(track.clips) for track in self.tracks)>=MAX_CLIPS:raise AudioError('There are too many clips in this session.')
        clips=[]
        for clip in self.tracks[target].clips:
            if not clip.muted and clip.start<end and clip.end>start:
                a=clip.source_start+start-clip.start;b=clip.source_start+end-clip.start
                values=punch.validate_ranges((*clip.punch_ranges,(a,b,fade)),len(self.media[clip.media_id].samples))
                clip=replace(clip,punch_ranges=values)
            clips.append(clip)
        media=self._prepare_media(samples,self.sample_rate,tr('Punch Recording') if name is None else name)
        clip=SessionClip(identifier(),media.id,media.name,start,0,len(samples),fade_in=fade,fade_out=fade)
        tracks=list(self.tracks);tracks[target]=replace(tracks[target],clips=(*clips,clip))
        self._media[media.id]=media
        self._commit(tracks,'Punch Recording',selected_clip=clip.id,selected_track=track_id)
        return clip.id

    def render(self, start=0, end=None):
        end = self.frames if end is None else end
        start, end = integer(start, "Mix begin"), integer(end, "Mix end")
        if end < start or end > self.sample_rate * MAX_SECONDS:
            raise AudioError("Invalid mixdown range.")
        if (end - start) * 8 > MAX_AUDIO_BYTES:
            raise AudioError("The mix exceeds the supported address space.")
        from .mixing import SessionStream
        stream = SessionStream(self, start, end, live=False)
        output = storage.allocate((end-start, 2))
        try:
            progress(0, end-start, "Sporen mixen")
            for a, b in blocks(end-start, 1024):
                output[a:b] = stream.read(b-a)
                if isinstance(output, np.memmap) and (b % 262144 == 0 or b == end-start):
                    output.flush(); storage.release_pages(output)
                progress(b, end-start, "Sporen mixen")
            return storage.seal(output, checked=True)
        finally:
            stream.close()

    def undo(self):
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(self._snapshot(state.label))
            self._restore(state)

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(self._snapshot(state.label))
            self._restore(state)
