"""Bounded state and streaming delay/reverberation, including optional tails.

Reverb: eight parallel damped combs followed by four Schroeder allpasses.
Feedback g=10**(-3*delay/T60); input normalization sqrt(1-g*g).
Structures described by Julius O. Smith, Physical Audio Signal Processing:
https://www.dsprelated.com/freebooks/pasp/Artificial_Reverberation.html
No original program code or third-party implementation is included.
"""
import ctypes as C
import math

import numpy as np

from . import storage
from .filters import number
from .operations import blocks, progress

EFFECTS = ("delay", "echo", "reverb")


class DelayLine(C.Structure):
    _fields_ = [("data", C.POINTER(C.c_double)), ("length", C.c_size_t),
                ("cursor", C.c_size_t), ("filter", C.c_double),
                ("feedback", C.c_double), ("injection", C.c_double)]


def bind(lib, signature):
    lib.ce_delay.argtypes = signature + [C.POINTER(DelayLine), C.c_double, C.c_int,
                                       C.c_double, C.c_double, C.c_double]
    lib.ce_delay.restype = C.c_int
    lib.ce_reverb.argtypes = signature + [C.POINTER(DelayLine), C.c_double, C.c_double,
                                        C.c_double, C.c_double, C.c_double]
    lib.ce_reverb.restype = C.c_int


class Processor:
    def __init__(self, name, sample_rate, channels, **settings):
        self.name = name
        self.sample_rate = number(sample_rate, 1000, 384000, "Sample rate")
        if channels not in (1, 2):
            raise ValueError("Delay and reverb support mono or stereo.")
        self.channels = channels
        options = dict(settings)
        self.dry = number(options.pop("dry", 1), 0, 1, "Dry level")
        self.wet = number(options.pop("wet", .3), 0, 1, "Wet level")
        self.gain = 10 ** (number(options.pop("output_db", 0), -24, 24, "Output gain (dB)") / 20)
        self.tail_frames = round(number(options.pop("tail_seconds", 0), 0, 60, "Tail (seconds)") * self.sample_rate)
        self.damping = 0
        self.ping_pong = False
        self.width = 1
        specs = []
        if name in ("delay", "echo"):
            delay = number(options.pop("delay_ms", 250), 1, 2000, "Delay (ms)")
            right = options.pop("right_delay_ms", None)
            right = delay if right is None else number(right, 1, 2000, "Right delay (ms)")
            feedback = 0
            if name == "echo":
                feedback = number(options.pop("feedback", .4), 0, .95, "Feedback")
                self.damping = number(options.pop("damping", .2), 0, .95, "Damping")
                self.ping_pong = options.pop("ping_pong", False)
                if not isinstance(self.ping_pong, bool):
                    raise ValueError("Invalid ping pong setting.")
            for c in range(channels):
                length = max(1, round((delay if c == 0 else right) * self.sample_rate / 1000))
                specs.append((length, feedback, 1))
        elif name == "reverb":
            room = number(options.pop("room_size", 50), 20, 100, "Room size")
            decay = number(options.pop("decay_seconds", 1.5), .1, 10, "Decay (seconds)")
            pre = number(options.pop("predelay_ms", 20), 0, 250, "Predelay (ms)")
            self.damping = number(options.pop("damping", .4), 0, .95, "Damping")
            self.width = number(options.pop("width", 1), 0, 1, "Stereo width")
            scale = (.4 + .016*room) * self.sample_rate / 44100
            for c in range(channels):
                specs.append((round(pre*self.sample_rate/1000), 0, 1))
                for length in (1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617):
                    length = max(1, round((length + c*23)*scale))
                    feedback = 10 ** (-3*length/(self.sample_rate*decay))
                    specs.append((length, feedback, math.sqrt(1-feedback*feedback)))
                for length in (556, 441, 341, 225):
                    length = max(1, round((length + c*23)*scale))
                    feedback = min(.5, 10 ** (-3*length/(self.sample_rate*decay)))
                    specs.append((length, feedback, 1))
        else:
            raise ValueError("Unknown delay effect.")
        if options:
            raise ValueError("Unknown delay settings: " + ", ".join(sorted(options)))
        # Validate everything before allocating any delay buffers.
        self.buffers = [np.zeros(length, np.float64) for length, _, _ in specs]
        self.lines = (DelayLine * len(specs))(*(DelayLine(buffer.ctypes.data_as(C.POINTER(C.c_double)),
            length, 0, 0, feedback, injection) for buffer, (length, feedback, injection) in zip(self.buffers, specs)))

    def process(self, dsp, data):
        if data.shape[1] != self.channels:
            raise ValueError("Delay state does not match the audio channels.")
        function = dsp.lib.ce_reverb if self.name == "reverb" else dsp.lib.ce_delay
        mode = self.width if self.name == "reverb" else int(self.ping_pong)
        dsp._check(function(*dsp._buffer(data), self.lines, self.damping, mode, self.dry, self.wet, self.gain))


def process_blocks(dsp, name, source, sample_rate, *, limit=None, block_frames=262144, **settings):
    frames, channels = source.shape
    processor = Processor(name, sample_rate, channels, **settings)
    total = frames + processor.tail_frames if frames else 0
    wanted = total if limit is None else min(total, max(0, int(limit)))
    result = storage.allocate((wanted, channels))
    fade = min(processor.tail_frames, max(1, round(.01*sample_rate)))
    progress(0, wanted, "Effect toepassen")
    for a, b in blocks(wanted, block_frames):
        data = np.zeros((b-a, channels), np.float32)
        if a < frames:
            count = min(b, frames)-a
            data[:count] = source[a:a+count]
        processor.process(dsp, data)
        # Fade only the appended tail's final 10 ms, using global output positions.
        # A preview gets the exact prefix, even if its boundary is inside the tail.
        if fade and b > total-fade:
            start = max(a, total-fade)
            envelope = (total-1-np.arange(start, b, dtype=np.float64))/max(1, fade-1)
            data[start-a:] *= envelope[:, None]
        if not np.isfinite(data).all():
            raise ValueError("The effect overflows float32 precision.")
        result[a:b] = data
        storage.release_pages(source)
        if isinstance(result, np.memmap):
            result.flush(); storage.release_pages(result)
        progress(b, wanted, "Effect toepassen")
    return storage.seal(result, checked=True)
