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
MAX_TAIL_SECONDS = 600


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
        self.tail_frames = round(number(options.pop("tail_seconds", 0), 0, MAX_TAIL_SECONDS, "Tail (seconds)") * self.sample_rate)
        self.auto_tail = options.pop('auto_tail', False)
        if type(self.auto_tail) is not bool:
            raise ValueError('Invalid automatic tail setting.')
        if self.auto_tail and self.tail_frames:
            raise ValueError('Choose automatic or manual tail length.')
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
            decay = number(options.pop("decay_seconds", 1.5), .1, 60, "Decay (seconds)")
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

    def pending_bound(self):
        """Conservative future wet peak, including unplayed delayed events."""
        if not self.wet:
            return 0.
        peak = max((float(np.max(abs(buffer))) for buffer in self.buffers if len(buffer)), default=0.)
        peak = max(peak, max((abs(line.filter) for line in self.lines if line.feedback), default=0.))
        # Eight parallel combs and four allpasses: a generous sup-norm bound
        # also covers state already stored inside the allpass chain.
        factor = 1024 if self.name == 'reverb' else 1
        return peak*self.wet*self.gain*factor


def _fade_tail(result, total, frames, sample_rate):
    fade = min(total-frames, max(1, round(.01*sample_rate)))
    start = max(frames, total-fade)
    if fade and len(result) > start:
        stop = min(len(result), total)
        result[start:stop] *= ((total-1-np.arange(start, stop, dtype=np.float64))/max(1, fade-1))[:, None]


def _automatic(dsp, processor, source, sample_rate, limit, block_frames):
    from .audio import MAX_AUDIO_BYTES
    frames, channels = source.shape
    maximum = frames+round(MAX_TAIL_SECONDS*sample_rate)
    wanted = maximum if limit is None else min(maximum, max(0, int(limit)))
    if not frames or not wanted:
        return storage.seal(np.empty((0, channels), np.float32), checked=True)
    if maximum*channels*4 > MAX_AUDIO_BYTES:
        raise ValueError('The effect exceeds the supported address space.')
    reference = 0.
    total = frames
    guard = max(1, round(sample_rate*.01))
    progress(0, maximum, 'Effect toepassen')
    with storage.StreamBuffer(channels, wanted) as output:
        for a, b in blocks(min(frames, wanted), block_frames):
            data = np.array(source[a:b], dtype=np.float32, order='C')
            reference = max(reference, float(np.max(abs(data)))*processor.wet*processor.gain)
            processor.process(dsp, data)
            reference = max(reference, float(np.max(abs(data))))
            output.write(data); storage.release_pages(source)
            progress(b, maximum, 'Effect toepassen')
        # A preview wholly inside the source cannot overlap any final tail fade.
        if wanted > frames:
            threshold = max(1e-7, reference*10**(-90/20))
            bound = processor.pending_bound()
            if bound > threshold:
                quiet = False
                quantum = max(1, round(sample_rate*.1))
                for a in range(frames, maximum-guard, quantum):
                    b = min(maximum-guard, a+quantum)
                    data = np.zeros((b-a, channels), np.float32)
                    processor.process(dsp, data)
                    if a < wanted:
                        output.write(np.ascontiguousarray(data[:max(0, min(b, wanted)-a)]))
                    total = b
                    progress(b, maximum, 'Effect toepassen')
                    if processor.pending_bound() <= threshold:
                        quiet = True
                        break
                if not quiet:
                    raise ValueError('The automatic tail is still audible at the limit. Lower Feedback or Decay, or choose a manual tail.')
                # Keep a complete quiet taper after the last possibly loud tap.
                data = np.zeros((guard, channels), np.float32)
                processor.process(dsp, data)
                if total < wanted:
                    output.write(np.ascontiguousarray(data[:min(guard, wanted-total)]))
                total += guard
        result = output.finish()
    _fade_tail(result, total, frames, sample_rate)
    progress(len(result), len(result), 'Effect toepassen')
    return storage.seal(result, checked=True)


def process_blocks(dsp, name, source, sample_rate, *, limit=None, block_frames=262144, **settings):
    frames, channels = source.shape
    processor = Processor(name, sample_rate, channels, **settings)
    if processor.auto_tail:
        return _automatic(dsp, processor, source, sample_rate, limit, block_frames)
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
