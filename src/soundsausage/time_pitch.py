"""Two-pass Rubber Band C API with bounded audio buffers and exact output length."""
import ctypes as C
from ctypes.util import find_library

import numpy as np

from . import storage
from .filters import number
from .operations import blocks, progress

EFFECTS = ('stretch', 'pitch_shift')
_library = None


def library():
    global _library
    if _library is not None:
        return _library
    error = None
    for path in (find_library('rubberband'), 'librubberband.so.3', 'librubberband.so.2'):
        if not path: continue
        try:
            lib = C.CDLL(path); break
        except OSError as caught: error = caught
    else:
        raise RuntimeError('Time/Pitch requires the Rubber Band library. Install the distribution package.') from error
    pointer = C.POINTER(C.c_float)
    signatures = dict(new=([C.c_uint, C.c_uint, C.c_int, C.c_double, C.c_double], C.c_void_p),
        delete=([C.c_void_p], None), get_engine_version=([C.c_void_p], C.c_int),
        set_expected_input_duration=([C.c_void_p, C.c_uint], None),
        set_max_process_size=([C.c_void_p, C.c_uint], None),
        study=([C.c_void_p, C.POINTER(pointer), C.c_uint, C.c_int], None),
        process=([C.c_void_p, C.POINTER(pointer), C.c_uint, C.c_int], None),
        available=([C.c_void_p], C.c_int), retrieve=([C.c_void_p, C.POINTER(pointer), C.c_uint], C.c_uint))
    try:
        for name, (arguments, result) in signatures.items():
            function = getattr(lib, 'rubberband_'+name); function.argtypes = arguments; function.restype = result
    except AttributeError as caught:
        raise RuntimeError('The installed Rubber Band library is too old; version 3 or later is required.') from caught
    _library = lib
    return lib


def pointers(planar):
    return (C.POINTER(C.c_float)*len(planar))(*(row.ctypes.data_as(C.POINTER(C.c_float)) for row in planar))


def process_blocks(name, source, rate, *, time_ratio=1, semitones=0, preserve_formants=True,
                   quality='fine', limit=None, block_frames=262144, **unknown):
    if unknown: raise ValueError('Unknown Time/Pitch settings.')
    if name not in EFFECTS:
        raise ValueError('Unknown Time/Pitch effect.')
    rate = int(number(rate, 1000, 384000, 'Sample rate'))
    time_ratio = number(time_ratio, .25, 4, 'Length ratio')
    semitones = number(semitones, -24, 24, 'Semitones')
    if not isinstance(preserve_formants, bool) or quality not in ('fine', 'fast'):
        raise ValueError('Invalid Time/Pitch quality setting.')
    if name == 'pitch_shift' and time_ratio != 1:
        raise ValueError('Pitch Shift keeps the original duration; use Stretch to change duration.')
    frames, channels = source.shape
    total = max(1, int(frames*time_ratio+.5)) if frames else 0
    wanted = total if limit is None else min(total, max(0, int(limit)))
    if semitones == 0 and time_ratio == 1:
        from .restoration import _copy
        return _copy(source, wanted)
    if frames < max(64, round(rate*.05)):
        raise ValueError('Select at least 50 ms of audio for Time/Pitch processing (64 samples at low sample rates).')
    result = storage.allocate((wanted, channels))
    lib = library()
    # Offline | ThreadingNever | ChannelsTogether | optional R3/fine engine.
    options = 0x00010000 | 0x10000000 | (0x20000000 if quality == 'fine' else 0)
    if semitones:
        options |= 0x02000000
        if preserve_formants: options |= 0x01000000
    chunk_size = 4096  # Fixed grid gives Preview and Apply identical analysis/input.
    pending = np.empty((65536, channels), np.float32); filled = written = produced = 0
    output = np.empty((channels, 8192), np.float32)
    state = lib.rubberband_new(rate, channels, options, time_ratio, 2**(semitones/12))
    if not state: raise RuntimeError('Rubber Band could not allocate its processing state.')

    def drain():
        nonlocal filled, written, produced
        while lib.rubberband_available(state) > 0:
            count = lib.rubberband_retrieve(state, pointers(output), min(8192, lib.rubberband_available(state)))
            if not count: raise RuntimeError('Time/Pitch returned an empty output block.')
            produced += count
            take = min(count, wanted-written-filled)
            if take > 0:
                if not np.isfinite(output[:, :take]).all(): raise ValueError('Time/Pitch produced invalid audio.')
                if filled+take > len(pending):
                    result[written:written+filled] = pending[:filled]; written += filled; filled = 0
                pending[filled:filled+take] = output[:, :take].T; filled += take
                if filled >= len(pending)-8192:
                    result[written:written+filled] = pending[:filled]; written += filled; filled = 0
                    if isinstance(result, np.memmap): result.flush(); storage.release_pages(result)
            if limit is not None and written+filled >= wanted:
                return True
        return False

    try:
        lib.rubberband_set_max_process_size(state, chunk_size)
        if frames <= 0xffffffff: lib.rubberband_set_expected_input_duration(state, frames)
        progress(0, frames, 'Tijd/toonhoogte analyseren')
        for a, b in blocks(frames, chunk_size):
            planar = np.ascontiguousarray(source[a:b].T, dtype=np.float32)
            lib.rubberband_study(state, pointers(planar), b-a, int(b == frames))
            storage.release_pages(source); progress(b, frames, 'Tijd/toonhoogte analyseren')
        progress(0, frames, 'Tijd/toonhoogte toepassen')
        for a, b in blocks(frames, chunk_size):
            planar = np.ascontiguousarray(source[a:b].T, dtype=np.float32)
            lib.rubberband_process(state, pointers(planar), b-a, int(b == frames))
            done = drain()
            storage.release_pages(source); progress(b, frames, 'Tijd/toonhoogte toepassen')
            if done: break
        if filled:
            result[written:written+filled] = pending[:filled]; written += filled
        if written < wanted:
            if wanted-written > 1:
                raise RuntimeError(f'Time/Pitch returned {written} frames; {wanted} were expected.')
            result[written:wanted] = 0
        if limit is None and abs(produced-total) > 1:
            raise RuntimeError(f'Time/Pitch duration mismatch: {produced} frames, expected {total}.')
        return storage.seal(result)
    finally:
        lib.rubberband_delete(state)
