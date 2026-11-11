"""Bounded spectral noise reduction and conservative impulse interpolation.

Noise estimation and spectral weighting follow the conventional STFT approach:
https://www.inf.uni-hamburg.de/en/inst/ab/sp/research/intro.html
"""
import json
from pathlib import Path

import numpy as np

from . import storage
from .filters import number
from .operations import blocks, progress

EFFECTS = ("noise_reduction", "click_removal")


def fft_size(rate):
    number(rate, 1000, 384000, "Sample rate")
    return min(8192, max(256, 2 ** round(np.log2(rate*.04))))


def validate_profile(profile, rate=None, channels=None):
    if not isinstance(profile, dict) or set(profile) != {"version", "sample_rate", "fft_size", "frames", "power"}:
        raise ValueError("Invalid noise profile.")
    size = profile["fft_size"]
    if profile["version"] != 1 or type(size) is not int or size not in (256, 512, 1024, 2048, 4096, 8192):
        raise ValueError("Unsupported noise profile.")
    sr = number(profile["sample_rate"], 1000, 384000, "Profile sample rate")
    if type(profile["frames"]) is not int or not size <= profile["frames"] <= 30*sr:
        raise ValueError("Invalid noise profile duration.")
    power = np.asarray(profile["power"], np.float64)
    if power.ndim != 2 or power.shape[0] != size//2+1 or power.shape[1] not in (1, 2) or not np.isfinite(power).all() or (power < 0).any():
        raise ValueError("Invalid noise profile spectrum.")
    if rate is not None and sr != rate or channels is not None and power.shape[1] != channels:
        raise ValueError("Capture a profile with the same sample rate and channel count as this waveform.")
    return power


def learn_profile(source, rate):
    size = fft_size(rate)
    count = min(len(source), 30*int(rate))
    if count < size:
        raise ValueError(f"Select at least {size/rate:.3f} seconds containing only background noise.")
    window = np.sqrt(np.hanning(size+1)[:-1])[:, None]
    power = np.zeros((size//2+1, source.shape[1]), np.float64)
    positions = range(0, count-size+1, size//2)
    progress(0, len(positions), "Ruisprofiel opnemen")
    for i, start in enumerate(positions):
        spectrum = np.fft.rfft(np.asarray(source[start:start+size], np.float64)*window, axis=0)
        power += abs(spectrum)**2
        if i % 64 == 0:
            storage.release_pages(source)
            progress(i+1, len(positions), "Ruisprofiel opnemen")
    power /= len(positions)
    progress(len(positions), len(positions), "Ruisprofiel opnemen")
    return dict(version=1, sample_rate=int(rate), fft_size=size, frames=count, power=power.tolist())


def save_profile(path, profile):
    validate_profile(profile)
    path = Path(path)
    # A single atomic replacement also leaves an existing profile intact on error.
    from tempfile import NamedTemporaryFile
    import os
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            output.write(json.dumps(profile, allow_nan=False).encode())
            output.flush(); os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_profile(path):
    with Path(path).open('rb') as file:
        data = file.read(1024*1024+1)
    if len(data) > 1024*1024:
        raise ValueError("The noise profile is too large.")
    try:
        profile = json.loads(data)
        validate_profile(profile)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError("This is not a valid SoundSausage noise profile.") from error
    return profile


def _copy(source, wanted, residual=False):
    result = storage.allocate((wanted, source.shape[1]), zero=residual)
    for a, b in blocks(wanted):
        if not residual:
            result[a:b] = source[a:b]
        storage.release_pages(source)
        if isinstance(result, np.memmap):
            result.flush(); storage.release_pages(result)
        progress(b, wanted, "Effect toepassen")
    return storage.seal(result, checked=True)


def noise_reduction(source, rate, *, profile, reduction_db=12, sensitivity=2,
                    smoothing=60, linked=True, residual=False, limit=None, block_frames=262144):
    noise = validate_profile(profile, rate, source.shape[1])
    reduction_db = number(reduction_db, 0, 36, "Noise reduction (dB)")
    sensitivity = number(sensitivity, .5, 4, "Sensitivity")
    smoothing = number(smoothing, 0, 100, "Smoothing")/100*.95
    if not isinstance(linked, bool) or not isinstance(residual, bool):
        raise ValueError("Invalid noise reduction switch.")
    wanted = len(source) if limit is None else min(len(source), max(0, int(limit)))
    progress(0, wanted, "Ruis verminderen")
    if reduction_db == 0 or not noise.any():
        return _copy(source, wanted, residual)
    size = profile["fft_size"]; hop = size//4
    channels = source.shape[1]
    window = np.sqrt(np.hanning(size+1)[:-1])[:, None]
    overlap = np.zeros((size, channels), np.float64)
    weights = np.zeros((size, 1), np.float64)
    previous = np.ones_like(noise)
    floor = 10**(-reduction_db/20)
    result = storage.allocate((wanted, channels))
    pending = np.empty((max(8192, hop), channels), np.float32)
    filled = written = 0
    for start in range(-size+hop, wanted, hop):
        frame = np.zeros((size, channels), np.float64)
        a, b = max(0, start), min(len(source), start+size)
        if b > a:
            frame[a-start:b-start] = source[a:b]
        spectrum = np.fft.rfft(frame*window, axis=0)
        power = abs(spectrum)**2
        gain = np.maximum(floor, 1-sensitivity*noise/np.maximum(power, 1e-30))
        # Average three neighbouring bins; smooth closing while opening promptly.
        padded = np.pad(gain, ((1, 1), (0, 0)), mode='edge')
        gain = (padded[:-2]+padded[1:-1]+padded[2:])/3
        gain = np.maximum(gain, smoothing*previous+(1-smoothing)*gain)
        if linked and channels == 2:
            gain[:] = gain.max(axis=1, keepdims=True)
        previous = gain
        overlap += np.fft.irfft(spectrum*((1-gain) if residual else gain), n=size, axis=0)*window
        weights += window*window
        if start >= 0:
            count = min(hop, wanted-start)
            chunk = overlap[:count]/np.maximum(weights[:count], 1e-30)
            if not np.isfinite(chunk).all() or (abs(chunk) > np.finfo(np.float32).max).any():
                raise ValueError("The noise reduction result exceeds float32 precision.")
            if filled+count > len(pending):
                result[written:written+filled] = pending[:filled]; written += filled; filled = 0
            pending[filled:filled+count] = chunk; filled += count
            if filled >= len(pending)-hop or start+hop >= wanted:
                result[written:written+filled] = pending[:filled]; written += filled; filled = 0
                storage.release_pages(source)
                if isinstance(result, np.memmap):
                    result.flush(); storage.release_pages(result)
                progress(written, wanted, "Ruis verminderen")
        overlap[:-hop] = overlap[hop:]; overlap[-hop:] = 0
        weights[:-hop] = weights[hop:]; weights[-hop:] = 0
    return storage.seal(result, checked=True)


def click_removal(source, rate, *, sensitivity=8, threshold_db=-35, max_width_ms=1,
                  limit=None, block_frames=262144):
    rate = number(rate, 1000, 384000, "Sample rate")
    sensitivity = number(sensitivity, 2, 20, "Click sensitivity")
    threshold = 10**(number(threshold_db, -60, -6, "Minimum click level (dBFS)")/20)
    width = max(1, round(number(max_width_ms, .02, 2, "Maximum click width (ms)")*rate/1000))
    number(rate, 1000, 384000, "Sample rate")
    wanted = len(source) if limit is None else min(len(source), max(0, int(limit)))
    result = storage.allocate((wanted, source.shape[1]))
    context = 2*width+20
    progress(0, wanted, "Klikken herstellen")
    for a, b in blocks(wanted, min(8192, block_frames)):
        left, right = max(0, a-context), min(len(source), b+context)
        original = np.array(source[left:right], np.float64)
        repaired = original.copy()
        for channel in range(source.shape[1]):
            x = original[:, channel]
            difference = np.diff(x)
            if not len(difference):
                continue
            neighbourhood = np.lib.stride_tricks.sliding_window_view(np.pad(abs(difference), (8, 8), mode='edge'), 17)
            baseline = np.median(neighbourhood, axis=1)
            candidates = np.flatnonzero(abs(difference) > np.maximum(threshold, sensitivity*baseline))
            for i, j in zip(candidates[:-1], candidates[1:]):
                if j-i > width or i == 0 or j+1 >= len(difference) or difference[i]*difference[j] >= 0:
                    continue
                jump = min(abs(difference[i]), abs(difference[j]))
                if abs(x[j+1]-x[i]) > jump*.5 or max(abs(difference[i-1]), abs(difference[j+1])) > jump*.3:
                    continue
                repaired[i+1:j+1, channel] = np.linspace(x[i], x[j+1], j-i+2)[1:-1]
        result[a:b] = repaired[a-left:b-left]
        storage.release_pages(source)
        if isinstance(result, np.memmap):
            result.flush(); storage.release_pages(result)
        progress(b, wanted, "Klikken herstellen")
    return storage.seal(result, checked=True)


def process_blocks(name, source, rate, **settings):
    if name not in EFFECTS:
        raise ValueError("Unknown restoration effect.")
    try:
        return globals()[name](source, rate, **settings)
    except TypeError as error:
        raise ValueError("Invalid restoration settings.") from error
