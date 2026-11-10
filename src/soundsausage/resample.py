"""Band-limited whole-buffer sample-rate conversion through libsamplerate."""
import ctypes as C
from functools import lru_cache

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, validate_audio


class SrcData(C.Structure):
    _fields_ = [("data_in", C.POINTER(C.c_float)), ("data_out", C.POINTER(C.c_float)),
                ("input_frames", C.c_long), ("output_frames", C.c_long),
                ("input_frames_used", C.c_long), ("output_frames_gen", C.c_long),
                ("end_of_input", C.c_int), ("src_ratio", C.c_double)]


@lru_cache(maxsize=1)
def _library():
    try:
        lib = C.CDLL("libsamplerate.so.0")
    except OSError as error:
        raise AudioError("Sample-rate conversion needs libsamplerate. Install the distribution's libsamplerate package.") from error
    lib.src_simple.argtypes = [C.POINTER(SrcData), C.c_int, C.c_int]
    lib.src_simple.restype = C.c_int
    lib.src_strerror.argtypes = [C.c_int]
    lib.src_strerror.restype = C.c_char_p
    return lib


def frame_count(frames, source_rate, target_rate):
    for rate in (source_rate, target_rate):
        if isinstance(rate, bool) or not isinstance(rate, (int, np.integer)) or not 1000 <= rate <= 384000:
            raise AudioError("The sample rate must be an integer between 1,000 and 384,000 Hz.")
    if frames == 0:
        return 0
    return max(1, (frames * int(target_rate) + int(source_rate) // 2) // int(source_rate))


def resample(samples, source_rate, target_rate):
    """Keep duration within half a target frame; never modify the source array.

    This is an offline, full-buffer conversion. A future streaming reader must
    retain converter state rather than calling src_simple for separate chunks.
    """
    validate_audio(samples, source_rate)
    frames = frame_count(len(samples), source_rate, target_rate)
    channels = samples.shape[1]
    if frames * channels * 4 > MAX_AUDIO_BYTES:
        raise AudioError("Sample-rate conversion would exceed the 128 MiB audio limit.")
    if not len(samples) or source_rate == target_rate:
        return np.array(samples, dtype=np.float32, order="C", copy=True)
    # libsamplerate accepts ratios between 1/256 and 256. Split the extremes.
    if not 1 / 256 <= target_rate / source_rate <= 256:
        converted = resample(resample(samples, source_rate, 48000), 48000, target_rate)
        result = np.zeros((frames, channels), np.float32)
        result[:min(frames, len(converted))] = converted[:frames]
        return result
    source = np.ascontiguousarray(samples, dtype=np.float32)
    required = (frames * int(source_rate) + int(target_rate) - 1) // int(target_rate)
    if required > len(source):
        source = np.pad(source, ((0, required - len(source)), (0, 0)))
    # One spare frame covers the converter's rounding at the end of the stream.
    output = np.zeros((frames + 1, channels), np.float32)
    info = SrcData(source.ctypes.data_as(C.POINTER(C.c_float)),
                   output.ctypes.data_as(C.POINTER(C.c_float)), len(source), len(output), 0, 0, 1,
                   target_rate / source_rate)
    lib = _library()
    status = lib.src_simple(C.byref(info), 0, channels)  # SRC_SINC_BEST_QUALITY
    if status:
        raise AudioError(lib.src_strerror(status).decode("utf-8", "replace"))
    if info.input_frames_used != len(source):
        raise AudioError("The sample-rate converter did not consume the complete waveform.")
    # The filter sees silence beyond the actual end, including a fractional tail.
    result = output[:frames].copy()
    validate_audio(result, target_rate)
    return result
