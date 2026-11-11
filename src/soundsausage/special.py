"""Waveshaping and uniform partitioned FFT convolution with bounded working state."""
import hashlib
from pathlib import Path

import numpy as np

from . import storage
from .audio import read_wav
from .filters import number
from .operations import blocks, progress
from .resample import resample, frame_count

EFFECTS = ('distortion', 'convolution')
IR_MAX_FRAMES = 524288
IR_MAX_BYTES = 32*1024*1024


def file_digest(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > IR_MAX_BYTES:
        raise ValueError('Choose a WAV impulse-response file of at most 32 MiB.')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        count = 0
        while part := source.read(65536):
            count += len(part)
            if count > IR_MAX_BYTES: raise ValueError('The impulse-response file became too large.')
            digest.update(part)
            progress(count, max(1, path.stat().st_size), 'Impulsrespons lezen')
    return digest.hexdigest()


def load_impulse(path, rate, channels, expected_digest=None):
    digest = file_digest(path)
    if expected_digest is not None and expected_digest != digest:
        raise ValueError('The impulse-response file has changed. Choose it again before applying or repeating Convolution.')
    audio = read_wav(path)
    wanted = frame_count(len(audio.samples), audio.sample_rate, rate)
    if not wanted or wanted > min(IR_MAX_FRAMES, 10*rate):
        raise ValueError('The impulse response must be non-empty and at most 10 seconds / 524288 output samples.')
    if audio.samples.shape[1] == 2 and channels == 1:
        raise ValueError('Choose a mono impulse response for a mono waveform.')
    samples = resample(audio.samples, audio.sample_rate, rate) if audio.sample_rate != rate else audio.samples
    if not np.any(samples): raise ValueError('The impulse response contains only silence.')
    if file_digest(path) != digest:
        raise ValueError('The impulse-response file changed while opening it.')
    return samples, digest


def distortion(source, rate, *, kind='soft', drive_db=12, ceiling=.9, bits=8,
               mix=.5, output_db=0, oversample=True, limit=None, block_frames=262144):
    rate = int(number(rate, 1000, 384000, 'Sample rate'))
    drive = 10**(number(drive_db, 0, 36, 'Drive (dB)')/20)
    ceiling = number(ceiling, .1, 1, 'Ceiling')
    mix = number(mix, 0, 1, 'Effect mix')
    gain = 10**(number(output_db, -24, 24, 'Output gain (dB)')/20)
    if kind not in ('soft', 'hard', 'fold', 'crush') or type(bits) is not int or not 2 <= bits <= 16 or not isinstance(oversample, bool):
        raise ValueError('Invalid distortion settings.')
    wanted = len(source) if limit is None else min(len(source), max(0, int(limit)))
    progress(0, wanted, 'Vervorming toepassen')
    factor = (4 if rate <= 96000 else 2 if rate <= 192000 else 1) if oversample else 1
    if mix == 0: factor = 1
    if factor > 1:
        up = resample(source, rate, rate*factor)
        shaped = distortion(up, rate*factor, kind=kind, drive_db=drive_db, ceiling=ceiling,
                            bits=bits, mix=1, output_db=0, oversample=False)
        wet = resample(shaped, rate*factor, rate)
    else:
        wet = None
    result = storage.allocate((wanted, source.shape[1]))
    for a, b in blocks(wanted, block_frames):
        original = np.asarray(source[a:b], np.float64)
        if mix == 0:
            out = original*gain
        else:
            if wet is None:
                z = original*drive
                if kind == 'soft': effected = ceiling*np.tanh(z/ceiling)
                elif kind == 'hard': effected = np.clip(z, -ceiling, ceiling)
                elif kind == 'fold': effected = ceiling-np.abs((z+ceiling) % (4*ceiling)-2*ceiling)
                else:
                    levels = 2**(bits-1)
                    effected = np.clip(np.rint(z/ceiling*levels), -levels, levels-1)/levels*ceiling
            else: effected = np.asarray(wet[a:b], np.float64)
            out = ((1-mix)*original+mix*effected)*gain
        if not np.isfinite(out).all() or (abs(out) > np.finfo(np.float32).max).any():
            raise ValueError('The distortion result exceeds float32 precision.')
        result[a:b] = out
        storage.release_pages(source)
        if wet is not None: storage.release_pages(wet)
        if isinstance(result, np.memmap): result.flush(); storage.release_pages(result)
        progress(b, wanted, 'Vervorming toepassen')
    return storage.seal(result, checked=True)


def convolution(source, rate, *, ir_path, ir_sha256=None, normalize=True, dry=1, wet=.3,
                output_db=0, keep_tail=False, limit=None, block_frames=262144):
    rate = int(number(rate, 1000, 384000, 'Sample rate'))
    dry = number(dry, 0, 1, 'Dry level'); wet = number(wet, 0, 1, 'Wet level')
    gain = 10**(number(output_db, -24, 24, 'Output gain (dB)')/20)
    if not isinstance(normalize, bool) or not isinstance(keep_tail, bool): raise ValueError('Invalid convolution switch.')
    impulse, _ = load_impulse(ir_path, rate, source.shape[1], ir_sha256)
    energies = np.zeros(impulse.shape[1])
    for a, b in blocks(len(impulse), 65536):
        energies += np.sum(np.asarray(impulse[a:b], np.float64)**2, axis=0)
    if max(energies) == 0: raise ValueError('The impulse response contains only silence.')
    scale = 1/np.sqrt(max(energies)) if normalize else 1
    hop = 2048 if len(impulse) <= 16384 else 8192
    size = hop*2; count = (len(impulse)+hop-1)//hop
    channels = source.shape[1]
    kernels = np.empty((count, hop+1, impulse.shape[1]), np.complex128)
    progress(0, count, 'Impulsrespons voorbereiden')
    for p in range(count):
        data = np.zeros((size, impulse.shape[1]))
        part = impulse[p*hop:min(len(impulse), (p+1)*hop)]
        data[:len(part)] = part
        kernels[p] = np.fft.rfft(data, axis=0)*scale
        progress(p+1, count, 'Impulsrespons voorbereiden')
    history = np.zeros((count, hop+1, channels), np.complex128)
    scratch = np.empty((hop+1, channels), np.complex128)
    overlap = np.zeros((hop, channels))
    total = len(source)+(len(impulse)-1 if keep_tail and len(source) else 0)
    wanted = total if limit is None else min(total, max(0, int(limit)))
    result = storage.allocate((wanted, channels))
    index = 0
    progress(0, wanted, 'Convolutie toepassen')
    for a, b in blocks(wanted, hop):
        data = np.zeros((size, channels))
        if a < len(source):
            n = min(hop, len(source)-a)
            data[:n] = source[a:a+n]
        history[index] = np.fft.rfft(data, axis=0)
        spectrum = np.zeros((hop+1, channels), np.complex128)
        for p in range(count):
            np.multiply(history[(index-p)%count], kernels[p], out=scratch)
            spectrum += scratch
        convolved = np.fft.irfft(spectrum, n=size, axis=0)
        convolved[:hop] += overlap; overlap[:] = convolved[hop:]
        output = (dry*data[:b-a]+wet*convolved[:b-a])*gain
        if not np.isfinite(output).all() or (abs(output) > np.finfo(np.float32).max).any():
            raise ValueError('The convolution result exceeds float32 precision.')
        result[a:b] = output
        index = (index+1)%count
        storage.release_pages(source)
        if isinstance(result, np.memmap): result.flush(); storage.release_pages(result)
        progress(b, wanted, 'Convolutie toepassen')
    return storage.seal(result, checked=True)


def process_blocks(name, source, rate, **settings):
    if name not in EFFECTS: raise ValueError('Unknown special effect.')
    try: return globals()[name](source, rate, **settings)
    except TypeError as error: raise ValueError('Invalid special effect settings.') from error
