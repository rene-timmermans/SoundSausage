"""Frame-exact edits over immutable audio pieces with shared undo snapshots."""
from dataclasses import dataclass
from itertools import count

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, validate_audio
from .dsp import Dsp


_state_ids = count(1)


@dataclass(frozen=True)
class Clip:
    samples: np.ndarray
    sample_rate: int


@dataclass(frozen=True)
class Snapshot:
    pieces: tuple
    selection: tuple
    cursor: int
    state_id: int
    label: str


def _freeze(samples):
    result = np.array(samples, dtype=np.float32, copy=True, order="C")
    result.flags.writeable = False
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

    def read(self, start=0, end=None):
        end = self.frames if end is None else int(end)
        if not 0 <= start <= end <= self.frames:
            raise AudioError("The requested audio range is outside the document.")
        pieces = self._slices(start, end)
        if not pieces:
            return np.empty((0, self.channels), dtype=np.float32)
        if len(pieces) == 1:
            return pieces[0].copy()
        return np.concatenate(pieces)

    def _snapshot(self, label):
        return Snapshot(self._pieces, self.selection, self.cursor, self._state_id, label)

    def _restore(self, snapshot):
        self._pieces = snapshot.pieces
        self.selection = snapshot.selection
        self.cursor = snapshot.cursor
        self._state_id = snapshot.state_id
        self.revision += 1

    @staticmethod
    def _storage_bytes(states):
        buffers = {}
        for state in states:
            for piece in state.pieces:
                owner = piece
                while isinstance(owner.base, np.ndarray):
                    owner = owner.base
                buffers[id(owner)] = owner.nbytes
        return sum(buffers.values())

    def _commit(self, pieces, selection, label):
        self.undo_stack.append(self._snapshot(label))
        self.redo_stack.clear()
        self._pieces = tuple(piece for piece in pieces if len(piece))
        self.select(*selection)
        self._state_id = next(_state_ids)
        self.revision += 1
        self.undo_stack = self.undo_stack[-50:]
        while len(self.undo_stack) > 1 and self._storage_bytes([self._snapshot(label), *self.undo_stack]) > 256 * 1024 * 1024:
            self.undo_stack.pop(0)

    def replace(self, start, end, samples, label="Paste"):
        validate_audio(samples, self.sample_rate)
        if samples.shape[1] != self.channels or not 0 <= start <= end <= self.frames:
            raise AudioError("The replacement does not match the document.")
        frames = self.frames - (end - start) + len(samples)
        if frames * self.channels * 4 > MAX_AUDIO_BYTES:
            raise AudioError("This edit would exceed the 128 MiB document limit.")
        if start == end and len(samples) == 0:
            return
        pieces = self._slices(0, start)
        if len(samples):
            pieces += (_freeze(samples),)
        pieces += self._slices(end, self.frames)
        self._commit(pieces, (start, start + len(samples)), label)

    def copy(self):
        if not self.selected:
            raise AudioError("Select the audio to copy first.")
        return Clip(_freeze(self.read(*self.selection)), self.sample_rate)

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
        if clip.sample_rate != self.sample_rate or clip.samples.shape[1] != self.channels:
            raise AudioError("Clipboard audio has a different sample rate or channel count. Automatic conversion is not available yet.")
        start, end = self.selection if self.selected else (self.cursor, self.cursor)
        if mix:
            end = min(self.frames, start + len(clip.samples))
            combined = np.zeros_like(clip.samples)
            original = self.read(start, end)
            combined[:len(original)] = original
            combined += clip.samples
            self.replace(start, end, combined, "Mix Paste")
        else:
            self.replace(start, end, clip.samples, "Paste")

    def trim(self):
        if not self.selected:
            raise AudioError("Select the audio to keep first.")
        start, end = self.selection
        if start == 0 and end == self.frames:
            return
        self._commit(self._slices(start, end), (0, end - start), "Trim")

    def apply(self, name, **settings):
        start, end = self.effect_range
        if start == end:
            return
        result = self.read(start, end)
        if name == "gain":
            self.dsp.gain(result, **settings)
            label = "Amplify / Fade"
        elif name == "normalize":
            self.dsp.normalize(result, **settings)
            label = "Normalize"
        else:
            self.dsp.simple(name, result)
            label = name.capitalize()
        # Validate before committing: failed or overflowing effects leave the document intact.
        self.replace(start, end, result, label)
        self.last_effect = (name, dict(settings))

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
        data = self.read(start, end)
        # Use the first channel as the selection reference; never split stereo frames.
        if len(data) > 1:
            first = data[:-1, 0]
            following = data[1:, 0]
            flips = np.flatnonzero((first != 0) & (following != 0) & (np.signbit(first) != np.signbit(following))) + 1
            points = np.union1d(np.flatnonzero(data[:, 0] == 0), flips)
            if len(points):
                a, b = start + int(points[0]), start + int(points[-1])
                if b > a:
                    self.select(a, b)
