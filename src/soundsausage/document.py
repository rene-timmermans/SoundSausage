"""Frame-exact edits over immutable audio pieces with shared undo snapshots."""
from dataclasses import dataclass
from copy import deepcopy
from itertools import count

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, validate_audio
from .dsp import Dsp
from . import storage, metadata, peaks
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
        return Snapshot(self._pieces, self.selection, self.cursor, self._state_id, label, self.sample_rate, self.metadata)

    def _restore(self, snapshot):
        self._pieces = snapshot.pieces
        self.selection = snapshot.selection
        self.cursor = snapshot.cursor
        self._state_id = snapshot.state_id
        self.sample_rate = snapshot.sample_rate
        self.metadata = snapshot.metadata
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
        self.undo_stack.append(self._snapshot(label))
        self.redo_stack.clear()
        self._pieces = tuple(piece for piece in pieces if len(piece))
        if sample_rate is not None:
            self.sample_rate = sample_rate
        if metadata is not None:
            self.metadata = metadata
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
                     metadata=metadata.replace(self.metadata, start, end, len(samples)) if new_metadata is None else new_metadata)

    def copy(self):
        if not self.selected:
            raise AudioError("Select the audio to copy first.")
        return Clip(self.view(*self.selection), self.sample_rate, metadata.crop(self.metadata,*self.selection))

    def delete(self):
        if not self.selected:
            return
        a, b = self.selection
        self.replace(a, b, np.empty((0, self.channels), dtype=np.float32), "Delete")

    def cut(self):
        clip = self.copy()
        a, b = self.selection
        self.replace(a, b, np.empty((0, self.channels), dtype=np.float32), "Cut")
        return clip

    def paste(self, clip, mix=False):
        if clip is None:
            return
        if clip.samples.shape[1] != self.channels:
            raise AudioError("Clipboard audio has a different channel count. Mono/stereo conversion is not available for paste yet.")
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
            info=metadata.replace(self.metadata,end,end,max(0,len(samples)-(end-start)))
            self.replace(start, end, combined, "Mix Paste",new_metadata=metadata.insert_markers(info,source_metadata,start))
        else:
            info=metadata.replace(self.metadata,start,end,len(samples))
            self.replace(start, end, samples, "Paste",new_metadata=metadata.insert_markers(info,source_metadata,start))

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
        if not self.selected:
            raise AudioError("Select the audio to keep first.")
        start, end = self.selection
        if start == 0 and end == self.frames:
            return
        self._commit(self._slices(start, end), (0, end - start), "Trim",
                     metadata=metadata.crop(self.metadata, start, end))

    def apply(self, name, **settings):
        start, end = self.effect_range
        if start == end:
            return
        result = self.dsp.process_blocks(name, self.view(start, end), self.sample_rate, **settings)
        label = {"gain": "Amplify / Fade", "channel_mix": "Channel Mixer",
                 "dynamics": "Dynamics Processing"}.get(name, name.capitalize())
        # Validate before committing: failed or overflowing effects leave the document intact.
        new_metadata = metadata.remap(self.metadata, lambda p: start + end - 1 - p if start <= p < end else p) if name == "reverse" else self.metadata
        self.replace(start, end, result, label, new_metadata=new_metadata)
        # Store immutable settings, independent of a dialog's mutable controls.
        self.last_effect = (name, deepcopy(settings))

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
            segment = data[lo:b,0]
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
