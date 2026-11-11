"""Small producer queue: mix/resample off the GUI thread, never render a whole session."""
from collections import deque
from queue import Queue, Empty, Full
from threading import Event, Thread, Lock
import ctypes as C
import numpy as np

from .audio import AudioError
from .resample import _library, SrcData, frame_count


def converted_blocks(stream, target_rate, block=1024):
    if stream.sample_rate == target_rate:
        while stream.position < len(stream): yield stream.read(block)
        return
    ratio = target_rate/stream.sample_rate
    if not 1/256 <= ratio <= 256: raise AudioError('Choose an output rate closer to the session rate.')
    lib = _library(); error = C.c_int()
    state = lib.src_new(2, 2, C.byref(error))  # Sinc fastest, continuous filter state.
    if not state: raise AudioError(lib.src_strerror(error.value).decode('utf-8', 'replace'))
    wanted = frame_count(len(stream), stream.sample_rate, target_rate)
    written = 0; source = np.empty((0, 2), np.float32)
    output = np.empty((block, 2), np.float32)
    try:
        while written < wanted:
            if not len(source) and stream.position < len(stream): source = stream.read(block)
            final = stream.position == len(stream)
            info = SrcData(source.ctypes.data_as(C.POINTER(C.c_float)), output.ctypes.data_as(C.POINTER(C.c_float)),
                           len(source), len(output), 0, 0, int(final), ratio)
            status = lib.src_process(state, C.byref(info))
            if status: raise AudioError(lib.src_strerror(status).decode('utf-8', 'replace'))
            source = source[info.input_frames_used:]
            count = min(info.output_frames_gen, wanted-written)
            if count:
                written += count; yield output[:count].copy()
            if not info.input_frames_used and not info.output_frames_gen:
                if not final: raise AudioError('Live sample-rate conversion stopped unexpectedly.')
                # The sinc filter may round down by one frame at the end.
                if wanted-written > 1: raise AudioError('Incomplete live sample-rate conversion.')
                if written < wanted: yield np.zeros((wanted-written, 2), np.float32)
                break
    finally: lib.src_delete(state)


class StreamPayload:
    def __init__(self, factory, rate, fmt):
        self.factory, self.rate, self.format = factory, rate, fmt
        self.stream = factory()
        self.source_frames = len(self.stream)
        self.total = frame_count(self.source_frames, rate, fmt.sampleRate())*fmt.bytesPerFrame()
        self.queue = Queue(maxsize=3)
        self.cancel = Event(); self.done = Event(); self.ready = Event(); self.error = None
        self._cache = b''; self._cache_start = 0
        self.history = deque(maxlen=64); self.lock = Lock()
        self.thread = Thread(target=self._produce, daemon=True, name='SoundSausage-mix')
        self.thread.start()

    def __len__(self): return self.total

    def wait_ready(self):
        from .operations import progress
        while not self.ready.wait(.02):
            if self.done.is_set():
                if self.error: raise AudioError(self.error)
                return
            progress(0,1,'Afspelen voorbereiden')

    def _produce(self):
        from .playback import encode_output
        try:
            written = 0
            for data in converted_blocks(self.stream, self.format.sampleRate()):
                if self.cancel.is_set(): break
                encoded = encode_output(data, self.format.sampleRate(), self.format)
                # Retain only enough mixed audio for output meters.
                with self.lock: self.history.append((written, data))
                written += len(data)
                while not self.cancel.is_set():
                    try: self.queue.put(encoded, timeout=.02); self.ready.set(); break
                    except Full: pass
            if not self.cancel.is_set() and written*self.format.bytesPerFrame() != self.total:
                raise AudioError('The live mix ended at an unexpected position.')
        except Exception as error:
            self.error = str(error)
        finally:
            self.stream.close(); self.done.set()

    def __getitem__(self, item):
        start, stop, step = item.indices(self.total)
        if step != 1 or stop-start > 65536: raise AudioError('Invalid streaming output range.')
        if self.error: raise AudioError(self.error)
        if start == self._cache_start+len(self._cache):
            try: data = self.queue.get_nowait()
            except Empty: return b''
            self._cache_start = start; self._cache = data
        if not self._cache_start <= start <= stop or start > self._cache_start+len(self._cache):
            raise AudioError('Live output must be read sequentially.')
        offset = start-self._cache_start
        return self._cache[offset:offset+stop-start]

    def meter_samples(self, frame):
        end = round(frame*self.format.sampleRate()/self.rate)
        begin = max(0, end-self.format.sampleRate()//30)
        with self.lock: history = tuple(self.history)
        parts = [data[max(0, begin-first):min(len(data), end-first)] for first, data in history
                 if first < end and first+len(data) > begin]
        return np.concatenate(parts) if parts else None

    def close(self):
        self.cancel.set()
        # The producer owns and closes DSP resources, even after a slow effect.
        self.thread.join(timeout=.05)
