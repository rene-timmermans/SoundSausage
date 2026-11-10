"""Context-local progress and cancellation, usable without a GUI or thread."""
from contextlib import contextmanager
from contextvars import ContextVar
import time

from .errors import OperationCancelled


_current = ContextVar("soundsausage_operation", default=None)


class Operation:
    def __init__(self, callback=None):
        self.callback = callback
        self.cancelled = False
        self._last_update = 0.0
        self._last_label = None

    def cancel(self):
        self.cancelled = True

    def update(self, done, total, label="Verwerken"):
        if self.cancelled:
            raise OperationCancelled("Bewerking geannuleerd.")
        now = time.monotonic()
        if self.callback is not None and (label != self._last_label or done >= total or now - self._last_update >= .025):
            self._last_update, self._last_label = now, label
            if self.callback(done, total, label) is False:
                self.cancel()
        if self.cancelled:
            raise OperationCancelled("Bewerking geannuleerd.")


@contextmanager
def operation(callback=None):
    active = Operation(callback)
    token = _current.set(active)
    try:
        yield active
    finally:
        _current.reset(token)


def progress(done, total, label="Verwerken"):
    current = _current.get()
    if current is not None:
        current.update(done, total, label)


def blocks(frames, block_frames=262144):
    for start in range(0, frames, block_frames):
        yield start, min(frames, start + block_frames)
