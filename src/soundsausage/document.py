"""Frame-exact edits over immutable audio pieces with shared undo snapshots."""
from dataclasses import dataclass
from copy import deepcopy
from itertools import count
from pathlib import Path

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, validate_audio
from .dsp import Dsp
from . import storage, metadata, peaks, id3_metadata
from .operations import blocks, progress
from .resample import resample, frame_count


_state_ids = count(1)


@dataclass(frozen=True)
class Clip:
    samples: np.ndarray
    sample_rate: int
    metadata: tuple = ()


@dataclass(frozen=True)
class Snapshot:
    pieces: tuple
    selection: tuple
    cursor: int
    state_id: int
    label: str
    sample_rate: int
    metadata: tuple = ()
    selected_channels: tuple = ()


def _freeze(samples):
    result = storage.freeze(samples)
    peaks.prepare(result)
    return result


class Document:
    def __init__(self, samples=None, sample_rate=44100, channels=2, encoding="pcm16", dsp=None):
        if samples is None:
            samples = np.empty((0, channels), dtype=np.float32)
        validate_audio(samples, sample_rate)
        self.sample_rate = sample_rate
        self.channels = samples.shape[1]
        self.encoding = encoding
        self.extra_chunks = ()
        self.metadata = ()
        self.path = None
        self.dsp = dsp or Dsp()
        self._pieces = (_freeze(samples),) if len(samples) else ()
        self.selection = (0, 0)
        self.selected_channels = tuple(range(self.channels))
        self.cursor = 0
        self._state_id = next(_state_ids)
        self._saved_state_id = self._state_id
        self.revision = 0
        self.undo_stack = []
        self.redo_stack = []
        self.last_effect = None

    @property
    def frames(self):
        return sum(len(piece) for piece in self._pieces)

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

    @property
    def partial_channels(self):
        return len(self.selected_channels) != self.channels

    @property
    def effect_channel_count(self):
        return len(self.selected_channels)

    @property
    def channel_label(self):
        return "Mono" if self.channels == 1 else "Both (L+R)" if not self.partial_channels else "Left (L)" if self.selected_channels == (0,) else "Right (R)"

    def select_channels(self, channels=None):
        channels = tuple(range(self.channels)) if channels is None else tuple(channels)
        if not channels or any(type(c) is not int or c not in range(self.channels) for c in channels) or tuple(sorted(set(channels))) != channels:
            raise AudioError("Invalid channel selection.")
        self.selected_channels = channels

    def effect_view(self, start=0, end=None):
        source = self.view(start, end)
        return source[:, self.selected_channels[0]:self.selected_channels[0]+1] if self.partial_channels else source

    def effect_profile(self, profile):
        if self.partial_channels and isinstance(profile, dict):
            power = np.asarray(profile.get("power", ()))
            if power.ndim == 2 and power.shape[1] == self.channels:
                return dict(profile, power=power[:, self.selected_channels[0]:self.selected_channels[0]+1].tolist())
        return profile

    def _require_linked_timing(self):
        if self.partial_channels:
            raise AudioError("Select Both channels to change stereo duration. Use Silence to clear only the selected channel.")

    def mark_saved(self):
        self._saved_state_id = self._state_id

    def select(self, start, end):
        start, end = sorted((int(start), int(end)))
        self.selection = (max(0, min(start, self.frames)), max(0, min(end, self.frames)))
        self.cursor = self.selection[0]

    def _slices(self, start, end):
        result = []
        offset = 0
        for piece in self._pieces:
            stop = offset + len(piece)
            a, b = max(0, start - offset), min(len(piece), end - offset)
            if b > a:
                result.append(piece[a:b])
            offset = stop
            if offset >= end:
                break
        return tuple(result)

    def view(self, start=0, end=None):
        """Immutable range; assemble split pieces on disk for large ranges."""
        end = self.frames if end is None else int(end)
        if not 0 <= start <= end <= self.frames:
            raise AudioError("The requested audio range is outside the document.")
        pieces = self._slices(start, end)
        if not pieces:
            result = np.empty((0, self.channels), dtype=np.float32)
        elif len(pieces) == 1:
            return pieces[0]
        else:
            result = storage.allocate((end-start, self.channels))
            offset = 0
            progress(0, end-start, "Audio samenstellen")
            for piece in pieces:
                for a,b in blocks(len(piece)):
                    result[offset+a:offset+b] = piece[a:b]
                    storage.release_pages(piece)
                    if isinstance(result, np.memmap):
                        result.flush(); storage.release_pages(result)
                    progress(offset+b, end-start, "Audio samenstellen")
                offset += len(piece)
        return storage.seal(result, checked=True)

    def read(self, start=0, end=None):
        return storage.copy_array(self.view(start,end))

    def _snapshot(self, label):
        return Snapshot(self._pieces, self.selection, self.cursor, self._state_id, label, self.sample_rate, self.metadata, self.selected_channels)

    def _restore(self, snapshot):
        self._pieces = snapshot.pieces
        self.selection = snapshot.selection
        self.cursor = snapshot.cursor
        self._state_id = snapshot.state_id
        self.sample_rate = snapshot.sample_rate
        self.metadata = snapshot.metadata
        self.select_channels(snapshot.selected_channels or None)
        self.revision += 1

    @staticmethod
    def _storage_bytes(states):
        buffers = {}
        for state in states:
            for piece in state.pieces:
                owner = piece
                while isinstance(owner.base, np.ndarray):
                    owner = owner.base
                buffers[id(owner)] = 0 if storage.lease_of(owner) else owner.nbytes
        return sum(buffers.values())

    def _commit(self, pieces, selection, label, sample_rate=None, metadata=None):
        pieces = tuple(piece for piece in pieces if len(piece))
        information = id3_metadata.audio_changed(self.metadata if metadata is None else metadata,
            sum(len(piece) for piece in pieces), self.sample_rate if sample_rate is None else sample_rate)
        self.undo_stack.append(self._snapshot(label))
        self.redo_stack.clear()
        self._pieces = pieces
        if sample_rate is not None:
            self.sample_rate = sample_rate
        self.metadata = information
        self.select(*selection)
        self._state_id = next(_state_ids)
        self.revision += 1
        self.undo_stack = self.undo_stack[-50:]
        while len(self.undo_stack) > 1 and self._storage_bytes([self._snapshot(label), *self.undo_stack]) > 256 * 1024 * 1024:
            self.undo_stack.pop(0)

    def replace(self, start, end, samples, label="Paste", *, new_metadata=None):
        validate_audio(samples, self.sample_rate)
        if samples.shape[1] != self.channels or not 0 <= start <= end <= self.frames:
            raise AudioError("The replacement does not match the document.")
        frames = self.frames - (end - start) + len(samples)
        if frames * self.channels * 4 > MAX_AUDIO_BYTES:
            raise AudioError("The edit exceeds the supported address space.")
        if start == end and len(samples) == 0:
            return
        pieces = self._slices(0, start)
        if len(samples):
            pieces += (_freeze(samples),)
        pieces += self._slices(end, self.frames)
        self._commit(pieces, (start, start + len(samples)), label,
                     metadata=metadata.replace(self.metadata, start, end, len(samples), sample_rate=self.sample_rate) if new_metadata is None else new_metadata)

    def copy(self):
        if not self.selected:
            raise AudioError("Select the audio to copy first.")
        return Clip(self.effect_view(*self.selection), self.sample_rate,
                    metadata.crop(self.metadata,*self.selection,sample_rate=self.sample_rate))

    def set_sample(self, frame, channel, value):
        """Change one scalar only, sharing every untouched audio piece with Undo."""
        if type(frame) is not int or not 0 <= frame < self.frames or type(channel) is not int or not 0 <= channel < self.channels:
            raise AudioError("The sample position or channel is outside the document.")
        value = float(value)
        if not np.isfinite(value) or abs(value) > float(np.finfo(np.float32).max):
            raise AudioError("The sample value must be a finite 32-bit number.")
        row = self.read(frame, frame + 1)
        value = np.float32(value)
        if row[0, channel] == value:
            return
        row[0, channel] = value
        pieces = self._slices(0, frame) + (_freeze(row),) + self._slices(frame + 1, self.frames)
        cursor = self.cursor
        self._commit(pieces, self.selection, "Edit Sample")
        self.cursor = cursor

    def draw_samples(self, channel, patches):
        """Confirm disjoint strokes atomically, preserving timing and the other channel."""
        patches = tuple(patches)
        previous = 0
        for start, end, first, last in patches:
            if (type(channel) is not int or not 0 <= channel < self.channels or
                    type(start) is not int or type(end) is not int or
                    not previous <= start < end <= self.frames or end-start > self.sample_rate or
                    not np.isfinite((first, last)).all() or not -1 <= first <= 1 or not -1 <= last <= 1):
                raise AudioError("Invalid waveform drawing range.")
            previous = end
        force_disk = sum(end-start for start,end,_,_ in patches)*self.channels*4 > storage.MEMORY_THRESHOLD
        pieces = ()
        previous = 0
        changed = False
        for index, (start, end, first, last) in enumerate(patches):
            progress(index, len(patches), "Draw Waveform")
            values = np.linspace(first, last, end-start, dtype=np.float32)
            original = self.view(start, end)
            if np.array_equal(original[:,channel], values):
                continue
            result = storage.allocate((end-start, self.channels), force_disk=force_disk)
            result[:] = original
            result[:,channel] = values
            pieces += self._slices(previous, start) + (storage.seal(result, checked=True),)
            previous = end
            changed = True
        progress(len(patches), len(patches), "Draw Waveform")
        if changed:
            pieces += self._slices(previous, self.frames)
            cursor = self.cursor
            self._commit(pieces, self.selection, "Draw Waveform")
            self.cursor = cursor

    def delete(self):
        if not self.selected:
            return
        self._require_linked_timing()
        a, b = self.selection
        self.replace(a, b, np.empty((0, self.channels), dtype=np.float32), "Delete")

    def cut(self):
        self._require_linked_timing()
        clip = self.copy()
        a, b = self.selection
        self.replace(a, b, np.empty((0, self.channels), dtype=np.float32), "Cut")
        return clip

    def paste(self, clip, mix=False):
        if clip is None:
            return
        if self.partial_channels:
            return self._paste_channel(clip, mix)
        if clip.samples.shape[1] != self.channels:
            raise AudioError("Clipboard audio has a different channel count. Choose Left or Right to paste mono audio into a stereo waveform.")
        samples = resample(clip.samples, clip.sample_rate, self.sample_rate) if clip.sample_rate != self.sample_rate else clip.samples
        source_metadata = metadata.resample(clip.metadata,clip.sample_rate,self.sample_rate,len(samples)) if clip.sample_rate != self.sample_rate else clip.metadata
        start, end = self.selection if self.selected else (self.cursor, self.cursor)
        if mix:
            end = min(self.frames, start + len(samples))
            combined = storage.allocate(samples.shape, zero=True)
            original = self.view(start, end)
            progress(0, len(samples), "Mix Paste")
            for a,b in blocks(len(samples)):
                combined[a:b] = samples[a:b]
                if a < len(original):
                    stop = min(b,len(original))
                    combined[a:stop] += original[a:stop]
                storage.release_pages(original); storage.release_pages(samples)
                if isinstance(combined, np.memmap):
                    combined.flush(); storage.release_pages(combined)
                progress(b, len(samples), "Mix Paste")
            combined = storage.seal(combined)
            info=metadata.replace(self.metadata,end,end,max(0,len(samples)-(end-start)),sample_rate=self.sample_rate)
            self.replace(start, end, combined, "Mix Paste",new_metadata=metadata.insert_markers(info,source_metadata,start,sample_rate=self.sample_rate))
        else:
            info=metadata.replace(self.metadata,start,end,len(samples),sample_rate=self.sample_rate)
            self.replace(start, end, samples, "Paste",new_metadata=metadata.insert_markers(info,source_metadata,start,sample_rate=self.sample_rate))

    def convert_sample_rate(self, target_rate):
        frame_count(self.frames, self.sample_rate, target_rate)  # Validate even for an empty waveform.
        if target_rate == self.sample_rate:
            return
        source_rate = self.sample_rate
        result = resample(self.view(), source_rate, target_rate)
        remap = lambda frame: min(len(result), (frame * target_rate + source_rate // 2) // source_rate)
        selection = tuple(remap(frame) for frame in self.selection)
        cursor = remap(self.cursor)
        self._commit((_freeze(result),), selection, "Convert Sample Rate", sample_rate=int(target_rate),
                     metadata=metadata.resample(self.metadata, source_rate, target_rate, len(result)))
        self.cursor = cursor

    def trim(self):
        self._require_linked_timing()
        if not self.selected:
            raise AudioError("Select the audio to keep first.")
        start, end = self.selection
        if start == 0 and end == self.frames:
            return
        self._commit(self._slices(start, end), (0, end - start), "Trim",
                     metadata=metadata.crop(self.metadata, start, end, sample_rate=self.sample_rate))

    def apply(self, name, **settings):
        start, end = self.effect_range
        if start == end:
            return
        if name == "convolution":
            from .special import file_digest
            settings = dict(settings)
            if not settings.get("ir_path"): raise AudioError("Choose an impulse response first.")
            settings["ir_path"] = str(Path(settings["ir_path"]).resolve())
            if settings.get("ir_sha256") is None: settings["ir_sha256"] = file_digest(settings["ir_path"])
        result = self.preview_effect(name, **settings)
        label = {"gain": "Amplify / Fade", "channel_mix": "Channel Mixer",
                 "dynamics": "Dynamics Processing", "graphic_eq": "Graphic Equalizer",
                 "stretch": "Stretch", "pitch_shift": "Pitch Shift", "noise_reduction": "Noise Reduction", "click_removal": "Click Removal",
                 "parametric_eq": "Parametric Equalizer", "filter": "Filters"}.get(name, name.capitalize())
        # Validate before committing: failed or overflowing effects leave the document intact.
        if name == "reverse" and not self.partial_channels:
            new_metadata = metadata.remap(self.metadata, lambda p: start + end - 1 - p if start <= p < end else p)
            new_metadata = id3_metadata.timeline(new_metadata, 'reverse', start, end, 0, self.sample_rate)
        elif name == "stretch" and len(result) != end-start:
            extra = len(result)-(end-start)
            def position(p):
                if p < start: return p
                if p >= end: return p+extra
                return start+min(len(result)-1, ((p-start)*len(result)+(end-start)//2)//(end-start))
            new_metadata = metadata.remap(self.metadata, position)
            new_metadata = id3_metadata.timeline(new_metadata, 'stretch', start, end, len(result), self.sample_rate)
        elif len(result) != end-start:
            # A retained effect tail inserts time after the original range:
            # preserve markers inside it, shift only those following the range.
            extra = len(result)-(end-start)
            new_metadata = metadata.remap(self.metadata, lambda p: p+extra if p >= end else p)
            new_metadata = id3_metadata.timeline(new_metadata, 'replace', end, end, extra, self.sample_rate)
        else:
            new_metadata = self.metadata
        tempo_changed = name == 'stretch' and settings.get('time_ratio', 1) != 1
        pitch_changed = name in ('stretch', 'pitch_shift') and settings.get('semitones', 0) != 0
        if tempo_changed or pitch_changed:
            new_metadata = id3_metadata.musical_change(new_metadata, tempo=tempo_changed, pitch=pitch_changed)
        self.replace(start, end, result, label, new_metadata=new_metadata)
        # Store immutable settings, independent of a dialog's mutable controls.
        self.last_effect = (name, deepcopy(settings))

    def _merge_channel(self, start, end, processed, channel=0):
        if len(processed) != end-start:
            raise AudioError("Select Both channels for an effect that changes stereo duration, or turn off the added tail.")
        source = self.view(start, end)
        result = storage.allocate(source.shape)
        progress(0, len(source), "Gekozen kanaal toepassen")
        for a, b in blocks(len(source)):
            result[a:b] = source[a:b]
            result[a:b, self.selected_channels[0]] = processed[a:b, channel]
            storage.release_pages(source); storage.release_pages(processed)
            if isinstance(result, np.memmap): result.flush(); storage.release_pages(result)
            progress(b, len(source), "Gekozen kanaal toepassen")
        return storage.seal(result)

    def preview_effect(self, name, *, limit=None, **settings):
        start, end = self.effect_range
        if self.partial_channels:
            if (name == "stretch" and settings.get("time_ratio", 1) != 1 or
                name in ("delay", "echo", "reverb") and settings.get("tail_seconds", 0) or
                name == "convolution" and settings.get("keep_tail", False)):
                self._require_linked_timing()
            settings = dict(settings)
            if name == "gain":
                # F2 can repeat settings recorded with both stereo inputs visible.
                for key in ("initial", "final"):
                    values = np.asarray(settings.get(key))
                    if values.shape == (self.channels,):
                        settings[key] = float(values[self.selected_channels[0]])
            if name in ("delay", "echo") and settings.get("right_delay_ms") is not None:
                if self.selected_channels == (1,):
                    settings["delay_ms"] = settings["right_delay_ms"]
                settings["right_delay_ms"] = None
            if name == "noise_reduction": settings["profile"] = self.effect_profile(settings.get("profile"))
            if name == "convolution": settings["ir_channel"] = self.selected_channels[0]
        source = self.view(start, end) if name == "channel_mix" else self.effect_view(start, end)
        processed = self.dsp.process_blocks(name, source, self.sample_rate, limit=limit, **settings)
        if self.partial_channels:
            count = end-start if limit is None else min(end-start, max(0, int(limit)))
            return self._merge_channel(start, start+count, processed, self.selected_channels[0] if name == "channel_mix" else 0)
        return processed

    def _paste_channel(self, clip, mix):
        samples = clip.samples
        if samples.shape[1] == self.channels:
            index = self.selected_channels[0]; samples = samples[:, index:index+1]
        elif samples.shape[1] != 1:
            raise AudioError("The clipboard does not match the chosen channel.")
        samples = resample(samples, clip.sample_rate, self.sample_rate) if clip.sample_rate != self.sample_rate else samples
        start, end = self.selection if self.selected else (self.cursor, self.cursor)
        if mix:
            end = start+len(samples)
            if end > self.frames: self._require_linked_timing()
            original = self.effect_view(start, end)
            combined = storage.allocate(samples.shape)
            for a, b in blocks(len(samples)):
                combined[a:b] = original[a:b]+samples[a:b]
                storage.release_pages(original); storage.release_pages(samples)
                if isinstance(combined, np.memmap): combined.flush(); storage.release_pages(combined)
                progress(b, len(samples), "Mix Paste")
            samples = storage.seal(combined)
        result = self._merge_channel(start, end, samples)
        self.replace(start, end, result, "Mix Paste" if mix else "Paste", new_metadata=self.metadata)

    def repeat(self):
        if self.last_effect:
            name, settings = self.last_effect
            self.apply(name, **settings)

    def undo(self):
        if self.undo_stack:
            snapshot = self.undo_stack.pop()
            self.redo_stack.append(self._snapshot(snapshot.label))
            self._restore(snapshot)

    def redo(self):
        if self.redo_stack:
            snapshot = self.redo_stack.pop()
            self.undo_stack.append(self._snapshot(snapshot.label))
            self._restore(snapshot)

    def zero_crossings(self):
        if not self.selected:
            return
        start, end = self.selection
        first_point = last_point = None
        data = self.view(start, end)
        progress(0, len(data), "Nuldoorgangen zoeken")
        for a,b in blocks(len(data)):
            lo = max(0,a-1)
            segment = data[lo:b,self.selected_channels[0]]
            points = np.flatnonzero(segment == 0) + lo
            if len(segment) > 1:
                x,y = segment[:-1],segment[1:]
                flips = np.flatnonzero((x != 0) & (y != 0) & (np.signbit(x) != np.signbit(y))) + lo + 1
                points = np.union1d(points, flips)
            if len(points):
                first_point = int(points[0]) if first_point is None else first_point
                last_point = int(points[-1])
            storage.release_pages(data)
            progress(b,len(data),"Nuldoorgangen zoeken")
        if first_point is not None and last_point > first_point:
            self.select(start + first_point, start + last_point)
