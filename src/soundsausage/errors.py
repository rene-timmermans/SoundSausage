"""Shared errors for audio, storage and cancellable operations."""


class AudioError(ValueError):
    pass


class OperationCancelled(AudioError):
    """A requested cancellation, distinct from invalid audio or failed I/O."""


class AmbiguousWavError(AudioError):
    pass
