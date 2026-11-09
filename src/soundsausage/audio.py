"""Bounded RIFF/WAVE I/O with explicit handling of ambiguous historical formats."""
from dataclasses import dataclass
from contextlib import nullcontext
import os
from pathlib import Path
import stat
import struct
import tempfile

import numpy as np


MAX_AUDIO_BYTES = 128 * 1024 * 1024
FORMATS = {"pcm8": (1, 8), "pcm16": (1, 16), "pcm24": (1, 24),
           "pcm32": (1, 32), "float32": (3, 32)}


class AudioError(ValueError):
    pass


class AmbiguousWavError(AudioError):
    pass


@dataclass(frozen=True)
class AudioFile:
    samples: np.ndarray
    sample_rate: int
    encoding: str
    extra_chunks: tuple = ()


def validate_audio(samples, sample_rate):
    if not isinstance(samples, np.ndarray) or samples.ndim != 2 or samples.shape[1] not in (1, 2):
        raise AudioError("This prototype supports mono and stereo audio.")
    if not 1000 <= sample_rate <= 384000:
        raise AudioError("The sample rate must be between 1,000 and 384,000 Hz.")
    if samples.shape[0] * samples.shape[1] * 4 > MAX_AUDIO_BYTES:
        raise AudioError("This prototype supports at most 128 MiB of decoded audio per document.")
    if not np.isfinite(samples).all():
        raise AudioError("The audio contains non-finite sample values.")


def read_wav(path, pcm32_mode=None):
    with (open(path, "rb") if isinstance(path, (str, os.PathLike)) else nullcontext(path)) as source:
        source.seek(0, 2)
        file_size = source.tell()
        source.seek(0)
        header = source.read(12)
        if len(header) != 12 or header[:4] != b"RIFF" or header[8:] != b"WAVE":
            raise AudioError("This is not a little-endian RIFF/WAVE file.")
        riff_end = struct.unpack_from("<I", header, 4)[0] + 8
        if riff_end < 12 or riff_end > file_size:
            raise AudioError("The WAV file is truncated or has an invalid RIFF length.")
        fmt = None
        data_location = None
        extras = []
        while source.tell() + 8 <= riff_end:
            kind, length = struct.unpack("<4sI", source.read(8))
            start = source.tell()
            if start + length > riff_end:
                raise AudioError("A WAV chunk extends beyond the end of the file.")
            if kind == b"fmt ":
                if length < 16 or length > 65536 or fmt is not None:
                    raise AudioError("Invalid or duplicate WAV format chunk.")
                fmt = source.read(length)
            elif kind == b"data":
                if data_location is not None:
                    raise AudioError("Multiple WAV audio chunks are not supported yet.")
                data_location = (start, length)
            elif kind not in (b"JUNK", b"PAD ", b"fact"):
                extras.append(kind.decode("ascii", "replace"))
            source.seek(start + length + (length & 1))
        if fmt is None or data_location is None:
            raise AudioError("The WAV file needs both a format chunk and an audio chunk.")
        code, channels, rate, byte_rate, alignment, bits = struct.unpack_from("<HHIIHH", fmt)
        extensible = code == 0xfffe
        if extensible:
            if len(fmt) < 40 or struct.unpack_from("<H", fmt, 16)[0] < 22:
                raise AudioError("Invalid extensible WAV format.")
            guid = fmt[24:40]
            if guid[4:] != bytes.fromhex("00001000800000aa00389b71"):
                raise AudioError("Unsupported extensible WAV subformat.")
            code = struct.unpack_from("<I", guid)[0]
            valid_bits = struct.unpack_from("<H", fmt, 18)[0]
            if valid_bits not in (0, bits):
                raise AudioError("WAV containers with a different valid-bit count are not supported yet.")
        if channels not in (1, 2) or not 1000 <= rate <= 384000:
            raise AudioError("This prototype supports mono/stereo audio at 1,000–384,000 Hz.")
        if code not in (1, 3) or bits not in (8, 16, 24, 32) or (code == 3 and bits != 32):
            raise AudioError("Supported WAV formats: PCM 8/16/24/32 and normalized float32.")
        if alignment != channels * (bits // 8):
            raise AudioError("The WAV container layout is unsupported; this may be a historical Cool Edit float variant.")
        if byte_rate != rate * alignment:
            raise AudioError("The WAV byte rate is inconsistent with its format.")
        length = data_location[1]
        if length % alignment:
            raise AudioError("The WAV data ends in a partial audio frame.")
        frames = length // alignment
        if frames * channels * 4 > MAX_AUDIO_BYTES:
            raise AudioError("This prototype supports at most 128 MiB of decoded audio per document.")
        if code == 1 and bits == 32 and not extensible and pcm32_mode not in ("integer", "cool-edit-float"):
            raise AmbiguousWavError("32-bit type-1 WAV may contain signed PCM integers or Cool Edit's historical floats.")
        source.seek(data_location[0])
        raw = source.read(length)
    if code == 3:
        samples = np.frombuffer(raw, dtype="<f4").copy()
        encoding = "float32"
    elif bits == 8:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128
        encoding = "pcm8"
    elif bits == 16:
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
        encoding = "pcm16"
    elif bits == 24:
        octets = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        values = octets[:, 0] | (octets[:, 1] << 8) | (octets[:, 2] << 16)
        values = (values ^ 0x800000) - 0x800000
        samples = values.astype(np.float32) / 8388608
        encoding = "pcm24"
    elif pcm32_mode == "cool-edit-float" and not extensible:
        samples = np.frombuffer(raw, dtype="<f4").copy() / 32768
        # Re-export in the unambiguous normalized format, not the historical carrier.
        encoding = "float32"
    else:
        samples = (np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2147483648).astype(np.float32)
        encoding = "pcm32"
    samples = np.ascontiguousarray(samples.reshape(frames, channels), dtype=np.float32)
    validate_audio(samples, rate)
    return AudioFile(samples, rate, encoding, tuple(extras))


def write_wav(path, samples, sample_rate, encoding="pcm16", *, pcm16_symmetric=False):
    """Write WAV; session mixdowns can use the observed Cool Edit PCM16 limits."""
    validate_audio(samples, sample_rate)
    if encoding not in FORMATS:
        raise AudioError("Unknown output format.")
    code, bits = FORMATS[encoding]
    channels = samples.shape[1]
    alignment = channels * bits // 8
    if code == 3:
        payload = samples.astype("<f4").tobytes()
    elif bits == 8:
        payload = np.clip(np.rint(samples.astype(np.float64) * 128 + 128), 0, 255).astype(np.uint8).tobytes()
    else:
        scale = 1 << (bits - 1)
        minimum = -32767 if bits == 16 and pcm16_symmetric else -scale
        values = np.clip(np.rint(samples.astype(np.float64) * scale), minimum, scale - 1).astype(np.int64)
        if bits == 24:
            unsigned = values.reshape(-1).astype(np.uint32)
            packed = np.column_stack((unsigned & 255, (unsigned >> 8) & 255, (unsigned >> 16) & 255))
            payload = packed.astype(np.uint8).tobytes()
        else:
            payload = values.astype("<i2" if bits == 16 else "<i4").tobytes()
    fmt = struct.pack("<HHIIHH", code, channels, sample_rate, sample_rate * alignment, alignment, bits)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    if code == 3:
        chunks += b"fact" + struct.pack("<II", 4, samples.shape[0])
    chunks += b"data" + struct.pack("<I", len(payload))
    total = 4 + len(chunks) + len(payload) + (len(payload) & 1)
    path = Path(path)
    previous_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(b"RIFF" + struct.pack("<I", total) + b"WAVE" + chunks)
            output.write(payload)
            if len(payload) & 1:
                output.write(b"\0")
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, previous_mode)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def tone(duration, rate=44100, channels=2, frequency=440.0, amplitude=0.25):
    if not np.isfinite(duration) or duration <= 0 or not np.isfinite(frequency) or not 0 < frequency < rate / 2:
        raise AudioError("Choose a positive duration and a frequency below half the sample rate.")
    frames = max(1, round(duration * rate))
    if frames * channels * 4 > MAX_AUDIO_BYTES:
        raise AudioError("The generated audio would exceed the 128 MiB document limit.")
    if not np.isfinite(amplitude) or not 0 <= amplitude <= 1:
        raise AudioError("The amplitude must be between 0 and 1.")
    mono = (np.sin(2 * np.pi * frequency * np.arange(frames) / rate) * amplitude).astype(np.float32)
    return np.repeat(mono[:, None], channels, axis=1)
