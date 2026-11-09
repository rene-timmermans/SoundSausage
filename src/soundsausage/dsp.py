"""Typed boundary to our C++ DSP kernel. This never loads original Windows modules."""
import ctypes as C
from pathlib import Path

import numpy as np


class EnvelopePoint(C.Structure):
    _fields_ = [("frame", C.c_uint64), ("value", C.c_double)]


class Dsp:
    def __init__(self, library=None):
        path = library or Path(__file__).resolve().parents[2] / "build/libsoundsausage_dsp.so"
        try:
            self.lib = C.CDLL(str(path))
        except OSError as error:
            raise RuntimeError("The audio kernel is not built. Run 'make' in the project folder.") from error
        self.lib.ce_dsp_abi_version.restype = C.c_uint32
        if self.lib.ce_dsp_abi_version() != 3:
            raise RuntimeError("The audio kernel has an incompatible ABI. Rebuild it with make.")
        self.ptr = C.POINTER(C.c_float)
        signature = [self.ptr, C.c_size_t, C.c_size_t]
        for name in ("ce_reverse", "ce_invert", "ce_silence"):
            getattr(self.lib, name).argtypes = signature
            getattr(self.lib, name).restype = C.c_int
        self.lib.ce_gain.argtypes = signature + [C.POINTER(C.c_double), C.POINTER(C.c_double), C.c_int]
        self.lib.ce_gain.restype = C.c_int
        self.lib.ce_normalize.argtypes = signature + [C.c_double, C.c_int]
        self.lib.ce_normalize.restype = C.c_int
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

    def gain(self, data, initial, final=None, logarithmic=False):
        channels = data.shape[1]
        start = np.broadcast_to(np.asarray(initial, dtype=np.float64), (channels,)).copy()
        end = np.broadcast_to(np.asarray(initial if final is None else final, dtype=np.float64), (channels,)).copy()
        self._check(self.lib.ce_gain(*self._buffer(data),
            start.ctypes.data_as(C.POINTER(C.c_double)), end.ctypes.data_as(C.POINTER(C.c_double)), int(logarithmic)))

    def normalize(self, data, target=0.98, linked=True):
        self._check(self.lib.ce_normalize(*self._buffer(data), target, int(linked)))

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
