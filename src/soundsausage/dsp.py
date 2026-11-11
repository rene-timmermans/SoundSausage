"""Typed boundary to our C++ DSP kernel. This never loads original Windows modules."""
import ctypes as C
from pathlib import Path

from . import storage
from .operations import blocks, progress
from .filters import EFFECTS as FILTER_EFFECTS, design
from . import space, restoration, time_pitch, special

import numpy as np


class EnvelopePoint(C.Structure):
    _fields_ = [("frame", C.c_uint64), ("value", C.c_double)]


class EffectPoint(C.Structure):
    _fields_ = [("position", C.c_double), ("value", C.c_double)]


class Dsp:
    def __init__(self, library=None):
        path = library or Path(__file__).resolve().parents[2] / "build/libsoundsausage_dsp.so"
        try:
            self.lib = C.CDLL(str(path))
        except OSError as error:
            raise RuntimeError("The audio kernel is not built. Run 'make' in the project folder.") from error
        self.lib.ce_dsp_abi_version.restype = C.c_uint32
        if self.lib.ce_dsp_abi_version() != 7:
            raise RuntimeError("The audio kernel has an incompatible ABI. Rebuild it with make.")
        self.ptr = C.POINTER(C.c_float)
        signature = [self.ptr, C.c_size_t, C.c_size_t]
        space.bind(self.lib, signature)
        for name in ("ce_reverse", "ce_invert", "ce_silence"):
            getattr(self.lib, name).argtypes = signature
            getattr(self.lib, name).restype = C.c_int
        self.lib.ce_gain.argtypes = signature + [C.POINTER(C.c_double), C.POINTER(C.c_double), C.c_int, C.c_size_t, C.c_size_t]
        self.lib.ce_gain.restype = C.c_int
        self.lib.ce_normalize.argtypes = signature + [C.c_double, C.c_int, C.c_int]
        self.lib.ce_normalize.restype = C.c_int
        self.lib.ce_channel_mix.argtypes = signature + [C.c_double] * 4
        self.lib.ce_channel_mix.restype = C.c_int
        self.lib.ce_envelope.argtypes = signature + [C.POINTER(EffectPoint), C.c_size_t, C.c_int, C.c_size_t, C.c_size_t]
        self.lib.ce_envelope.restype = C.c_int
        self.lib.ce_dynamics.argtypes = signature + [C.c_double, C.POINTER(EffectPoint), C.c_size_t,
                                                   C.c_double, C.c_double, C.c_double, C.c_int, C.POINTER(C.c_double)]
        self.lib.ce_dynamics.restype = C.c_int
        self.lib.ce_biquads.argtypes = signature + [C.POINTER(C.c_double), C.c_size_t,
                                                   C.POINTER(C.c_double), C.c_double]
        self.lib.ce_biquads.restype = C.c_int
        self.lib.ce_mix_add.argtypes = [self.ptr, C.c_size_t, self.ptr,
            C.c_size_t, C.c_size_t, C.c_size_t, C.c_size_t, C.c_size_t,
            C.c_size_t, C.c_size_t, C.c_double, C.c_double]
        self.lib.ce_mix_add.restype = C.c_int
        self.lib.ce_mix_add_automated.argtypes = self.lib.ce_mix_add.argtypes + [C.c_uint64,
            C.POINTER(EnvelopePoint), C.c_size_t, C.POINTER(EnvelopePoint), C.c_size_t]
        self.lib.ce_mix_add_automated.restype = C.c_int

    def _buffer(self, data):
        if not isinstance(data, np.ndarray) or data.ndim != 2 or data.shape[1] not in (1, 2):
            raise ValueError("Audio must be a mono or stereo frame array.")
        if data.dtype != np.dtype("float32") or not data.flags.c_contiguous or not data.flags.writeable:
            raise ValueError("DSP requires an owned, writable, contiguous float32 buffer.")
        return data.ctypes.data_as(self.ptr), data.shape[0], data.shape[1]

    @staticmethod
    def _check(result):
        if result:
            raise ValueError("Invalid effect settings.")

    def gain(self, data, initial, final=None, logarithmic=False, *, offset=0, total=None):
        channels = data.shape[1]
        start = np.broadcast_to(np.asarray(initial, dtype=np.float64), (channels,)).copy()
        end = np.broadcast_to(np.asarray(initial if final is None else final, dtype=np.float64), (channels,)).copy()
        self._check(self.lib.ce_gain(*self._buffer(data),
            start.ctypes.data_as(C.POINTER(C.c_double)), end.ctypes.data_as(C.POINTER(C.c_double)), int(logarithmic), offset, len(data) if total is None else total))

    def normalize(self, data, target=0.98, linked=True, remove_dc=False):
        self._check(self.lib.ce_normalize(*self._buffer(data), target, int(linked), int(remove_dc)))

    def channel_mix(self, data, matrix):
        weights = np.asarray(matrix, dtype=np.float64)
        if weights.shape != (2, 2):
            raise ValueError("The channel mixer needs a 2 × 2 matrix.")
        self._check(self.lib.ce_channel_mix(*self._buffer(data), *weights.ravel()))

    @staticmethod
    def _effect_points(points):
        if not isinstance(points, (tuple, list)) or not 2 <= len(points) <= 64 or any(
            not isinstance(p, (tuple, list)) or len(p) != 2 for p in points):
            raise ValueError("An effect curve needs 2–64 ordered points.")
        return (EffectPoint * len(points))(*(EffectPoint(x, y) for x, y in points))

    def envelope(self, data, points, logarithmic=False, *, offset=0, total=None):
        curve = self._effect_points(points)
        self._check(self.lib.ce_envelope(*self._buffer(data), curve, len(curve), int(logarithmic), offset, len(data) if total is None else total))

    def dynamics(self, data, sample_rate, points, attack_ms=10, release_ms=100, makeup_db=0, linked=True, *, state=None):
        curve = self._effect_points(points)
        state = (C.c_double * 2)() if state is None else state
        self._check(self.lib.ce_dynamics(*self._buffer(data), sample_rate, curve, len(curve),
                                        attack_ms, release_ms, makeup_db, int(linked), state))

    def process(self, name, data, sample_rate, **settings):
        if name in special.EFFECTS:
            self._buffer(data)
            result = special.process_blocks(name, data, sample_rate, **settings)
            if result.shape != data.shape: raise ValueError("Use block processing to retain convolution tails.")
            data[:] = result
        elif name in time_pitch.EFFECTS:
            self._buffer(data)
            result = time_pitch.process_blocks(name, data, sample_rate, **settings)
            if result.shape != data.shape: raise ValueError("Use block processing to change audio length.")
            data[:] = result
        elif name in restoration.EFFECTS:
            self._buffer(data)
            data[:] = restoration.process_blocks(name, data, sample_rate, **settings)
        elif name in space.EFFECTS:
            processor = space.Processor(name, sample_rate, data.shape[1], **settings)
            if processor.tail_frames:
                raise ValueError("Use block processing to append an effect tail.")
            processor.process(self, data)
        elif name in FILTER_EFFECTS:
            coefficients, gain = design(name, sample_rate, **settings)
            state = np.zeros((len(coefficients), data.shape[1], 2), np.float64)
            self.biquads(data, coefficients, state, gain)
        elif name == "dynamics":
            self.dynamics(data, sample_rate, **settings)
        elif name in ("gain", "normalize", "channel_mix", "envelope"):
            getattr(self, name)(data, **settings)
        else:
            self.simple(name, data)

    def biquads(self, data, coefficients, state, gain):
        channels = self._buffer(data)[2]
        if (not isinstance(coefficients, np.ndarray) or coefficients.dtype != np.float64 or
            coefficients.ndim != 2 or coefficients.shape[1] != 5 or len(coefficients) > 64 or
            not coefficients.flags.c_contiguous or not isinstance(state, np.ndarray) or
            state.dtype != np.float64 or state.shape != (len(coefficients), channels, 2) or
            not state.flags.c_contiguous or not state.flags.writeable):
            raise ValueError("Invalid filter coefficients or state buffer.")
        self._check(self.lib.ce_biquads(*self._buffer(data),
            coefficients.ctypes.data_as(C.POINTER(C.c_double)), len(coefficients),
            state.ctypes.data_as(C.POINTER(C.c_double)), gain))

    def process_blocks(self, name, source, sample_rate, *, limit=None, block_frames=262144, **settings):
        """Offline processing with bounded memory and one continuous effect state.

        A preview may restrict the output while analysis still spans the full range.
        No mutation of the immutable source occurs before the caller commits.
        """
        if name in special.EFFECTS:
            return special.process_blocks(name, source, sample_rate, limit=limit, block_frames=block_frames, **settings)
        if name in time_pitch.EFFECTS:
            return time_pitch.process_blocks(name, source, sample_rate, limit=limit, block_frames=block_frames, **settings)
        if name in restoration.EFFECTS:
            return restoration.process_blocks(name, source, sample_rate, limit=limit,
                                              block_frames=block_frames, **settings)
        if name in space.EFFECTS:
            return space.process_blocks(self, name, source, sample_rate, limit=limit,
                                        block_frames=block_frames, **settings)
        frames, channels = source.shape
        wanted = frames if limit is None else min(frames, max(0, int(limit)))
        if name in FILTER_EFFECTS:
            coefficients, output_gain = design(name, sample_rate, **settings)
            filter_state = np.zeros((len(coefficients), channels, 2), np.float64)
        result = storage.allocate((wanted, channels))
        state = (C.c_double * 2)()
        means = np.zeros(channels, np.float64)
        peaks = np.zeros(channels, np.float64)
        if name == "normalize":
            unknown = set(settings) - {"target", "linked", "remove_dc"}
            target = settings.get("target", .98)
            if unknown or not np.isfinite(target) or not 0 <= target <= 1:
                raise ValueError("Invalid normalization settings.")
            if settings.get("remove_dc", False) and frames:
                progress(0, frames, "DC analyseren")
                for a, b in blocks(frames, block_frames):
                    means += np.sum(source[a:b], axis=0, dtype=np.float64)
                    storage.release_pages(source)
                    progress(b, frames, "DC analyseren")
                means /= frames
            progress(0, frames, "Pieken analyseren")
            for a, b in blocks(frames, block_frames):
                peaks = np.maximum(peaks, np.max(np.abs(source[a:b].astype(np.float64) - means), axis=0))
                storage.release_pages(source)
                progress(b, frames, "Pieken analyseren")
            if settings.get("linked", True):
                peaks[:] = max(peaks)
        progress(0, wanted, "Effect toepassen")
        for a, b in blocks(wanted, block_frames):
            if name == "reverse":
                data = np.array(source[frames-b:frames-a][::-1], dtype=np.float32, order="C")
            else:
                data = np.array(source[a:b], dtype=np.float32, order="C")
                if name == "normalize":
                    scale = np.divide(target, peaks, out=np.ones_like(peaks), where=peaks > 0)
                    data[:] = (data.astype(np.float64) - means) * scale
                elif name in FILTER_EFFECTS:
                    self.biquads(data, coefficients, filter_state, output_gain)
                elif name in ("gain", "envelope"):
                    getattr(self, name)(data, offset=a, total=frames, **settings)
                elif name == "dynamics":
                    self.dynamics(data, sample_rate, state=state, **settings)
                else:
                    self.process(name, data, sample_rate, **settings)
            if not np.isfinite(data).all():
                raise ValueError("The effect overflows float32 precision.")
            result[a:b] = data
            storage.release_pages(source)
            if isinstance(result, np.memmap):
                result.flush(); storage.release_pages(result)
            progress(b, wanted, "Effect toepassen")
        return storage.seal(result, checked=True)

    def simple(self, name, data):
        if name not in ("reverse", "invert", "silence"):
            raise ValueError("Unknown effect.")
        self._check(getattr(self.lib, "ce_" + name)(*self._buffer(data)))

    def mix_add(self, output, source, output_offset, clip_offset, clip_frames,
                fade_in=0, fade_out=0, left=1.0, right=1.0, *, source_offset=0,
                volume_envelope=(), pan_envelope=()):
        out, frames, channels = self._buffer(output)
        if channels != 2 or source.ndim != 2 or source.shape[1] not in (1, 2):
            raise ValueError("The mixer needs stereo output and mono/stereo sources.")
        if source.dtype != np.dtype("float32") or not source.flags.c_contiguous:
            raise ValueError("The mixer source must be contiguous float32 audio.")
        if min(output_offset, clip_offset, clip_frames, fade_in, fade_out) < 0:
            raise ValueError("Mixer offsets cannot be negative.")
        args = (out, frames, source.ctypes.data_as(self.ptr),
            len(source), source.shape[1], output_offset, clip_offset, clip_frames,
            fade_in, fade_out, left, right)
        if not volume_envelope and not pan_envelope:
            self._check(self.lib.ce_mix_add(*args))
            return
        if type(source_offset) is not int or not 0 <= source_offset < 2 ** 64:
            raise ValueError("Invalid envelope source position.")
        arrays = []
        for points in (volume_envelope, pan_envelope):
            if len(points) > 512 or any(type(frame) is not int or not 0 <= frame < 2 ** 64 for frame, value in points):
                raise ValueError("Invalid envelope points.")
            arrays.append((EnvelopePoint * len(points))(*(EnvelopePoint(frame, value) for frame, value in points)))
        self._check(self.lib.ce_mix_add_automated(*args, source_offset,
                    arrays[0], len(arrays[0]), arrays[1], len(arrays[1])))
