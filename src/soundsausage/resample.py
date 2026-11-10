"""Band-limited streaming sample-rate conversion through libsamplerate."""
import ctypes as C
from functools import lru_cache

import numpy as np

from .audio import AudioError, validate_audio
from . import storage
from .operations import progress


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
    # Public API: https://libsndfile.github.io/libsamplerate/api_full.html
    lib.src_new.argtypes = [C.c_int, C.c_int, C.POINTER(C.c_int)]
    lib.src_new.restype = C.c_void_p
    lib.src_process.argtypes = [C.c_void_p, C.POINTER(SrcData)]
    lib.src_process.restype = C.c_int
    lib.src_delete.argtypes = [C.c_void_p]
    lib.src_delete.restype = C.c_void_p
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


def resample(samples, source_rate, target_rate, *, block_frames=262144):
    """Keep converter/filter state across blocks; round duration to target frames."""
    validate_audio(samples, source_rate)
    frames = frame_count(len(samples), source_rate, target_rate)
    channels = samples.shape[1]
    if not len(samples) or source_rate == target_rate:
        return storage.copy_array(samples)
    if not 1 / 256 <= target_rate / source_rate <= 256:
        converted = resample(resample(samples, source_rate, 48000), 48000, target_rate)
        if len(converted) == frames:
            return converted
        result = storage.allocate((frames, channels), zero=True)
        for a in range(0,min(frames,len(converted)),block_frames):
            b = min(a+block_frames,frames,len(converted))
            result[a:b] = converted[a:b]
            storage.release_pages(converted)
            if isinstance(result,np.memmap):
                result.flush();storage.release_pages(result)
            progress(b,frames,"Samplerate afronden")
        return storage.seal(result)
    result = storage.allocate((frames, channels), zero=True)
    required = max(len(samples), (frames * int(source_rate) + int(target_rate) - 1) // int(target_rate))
    lib = _library()
    error = C.c_int()
    state = lib.src_new(0, channels, C.byref(error))  # SRC_SINC_BEST_QUALITY
    if not state:
        raise AudioError(lib.src_strerror(error.value).decode("utf-8", "replace"))
    consumed = written = 0
    output = np.empty((block_frames, channels), np.float32)
    source = np.empty((0, channels), np.float32)
    progress(0, required, "Samplerate converteren")
    try:
        while True:
            if not len(source) and consumed < required:
                count = min(block_frames,required-consumed)
                source = np.zeros((count,channels),np.float32)
                available = min(count,max(0,len(samples)-consumed))
                source[:available] = samples[consumed:consumed+available]
                storage.release_pages(samples)
            final = consumed + len(source) == required
            info = SrcData(source.ctypes.data_as(C.POINTER(C.c_float)),
                           output.ctypes.data_as(C.POINTER(C.c_float)), len(source), len(output),
                           0, 0, int(final), target_rate / source_rate)
            status = lib.src_process(state, C.byref(info))
            if status:
                raise AudioError(lib.src_strerror(status).decode("utf-8", "replace"))
            used, generated = info.input_frames_used, info.output_frames_gen
            count = min(generated,frames-written)
            if count:
                result[written:written+count] = output[:count]
                written += count
                if isinstance(result,np.memmap):
                    result.flush(); storage.release_pages(result)
            consumed += used
            source = source[used:]
            progress(consumed, required, "Samplerate converteren")
            if not used and not generated:
                if not final:
                    raise AudioError("The sample-rate converter stopped before consuming the waveform.")
                break
    finally:
        lib.src_delete(state)
    return storage.seal(result)
