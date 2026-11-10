"""Owned immutable audio buffers, spilling large arrays to private disk storage."""
import atexit
import errno
import fcntl
import math
import os
import re
from pathlib import Path
import shutil
import uuid
import weakref

import numpy as np

from .errors import AudioError
from .operations import blocks, progress


MEMORY_THRESHOLD = 8 * 1024 * 1024
BLOCK_FRAMES = 262144
_default_workspace = None
_pinned_paths = set()
_workspaces = weakref.WeakValueDictionary()
_persisted = {}


def cache_root():
    configured = os.environ.get("SOUNDSAUSAGE_CACHE_DIR")
    if configured:
        return Path(configured).resolve()
    data = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    return data / "SoundSausage/work"


class BufferLease:
    def __init__(self, workspace, path):
        self.workspace, self.path = workspace, path

    def release(self):
        count = self.workspace.arrays.get(self.path, 1) - 1
        if count:
            self.workspace.arrays[self.path] = count
            return
        self.workspace.arrays.pop(self.path, None)
        if self.path not in _pinned_paths:
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass


class Workspace:
    def __init__(self, root=None, *, existing=None):
        self.root = Path(root or cache_root()).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = Path(existing).resolve() if existing else self.root / uuid.uuid4().hex
        if not self.path.is_relative_to(self.root) or self.path == self.root:
            raise AudioError("Invalid audio workspace path.")
        self.path.mkdir(mode=0o700, exist_ok=bool(existing))
        self.lock = open(self.path / ".lock", "a+b")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.lock.close()
            raise AudioError("This audio workspace is already in use.") from error
        self.arrays = {}
        _workspaces[str(self.path)] = self

    def allocate(self, shape, dtype=np.float32):
        shape = tuple(int(n) for n in shape)
        if not shape or min(shape) < 0:
            raise AudioError("Invalid audio buffer dimensions.")
        dtype = np.dtype(dtype)
        size = math.prod(shape) * dtype.itemsize
        if size == 0:
            return np.empty(shape, dtype=dtype)
        if size > shutil.disk_usage(self.path).free:
            raise AudioError("There is not enough free disk space for this audio operation.")
        path = self.path / (uuid.uuid4().hex + ".buffer")
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            try:
                os.ftruncate(fd, size)
                # Reserve backing space before mmap writes: a full sparse file
                # can otherwise deliver SIGBUS instead of a recoverable error.
                try:
                    os.posix_fallocate(fd, 0, size)
                except OSError as error:
                    if error.errno not in (errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL):
                        raise
                    zeros = bytes(1024 * 1024)
                    done = 0
                    while done < size:
                        done += os.write(fd, zeros[:min(len(zeros), size-done)])
                        progress(done, size, "Werkruimte reserveren")
            finally:
                os.close(fd)
            array = np.memmap(path, dtype=dtype, mode="r+", shape=shape)
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return self.register(array, path)

    def register(self, array, path):
        lease = BufferLease(self, Path(path).resolve())
        array._ss_lease = lease
        self.arrays[lease.path] = self.arrays.get(lease.path, 0) + 1
        weakref.finalize(array, lease.release)
        return array

    def close(self):
        if not self.lock.closed:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
        if _workspaces.get(str(self.path)) is self:
            _workspaces.pop(str(self.path),None)

    def __del__(self):
        try:
            self.close()
        except (AttributeError, OSError):
            pass


def workspace():
    global _default_workspace
    root = cache_root()
    if _default_workspace is None or _default_workspace.root != root:
        _default_workspace = Workspace(root)
    return _default_workspace


def root_array(array):
    result = array
    while isinstance(result.base, np.ndarray):
        result = result.base
    return result


def lease_of(array):
    return getattr(root_array(array), "_ss_lease", None)


def allocate(shape, *, zero=False, force_disk=False, owner=None):
    shape = tuple(int(n) for n in shape)
    if not shape or min(shape) < 0:
        raise AudioError("Invalid audio buffer dimensions.")
    size = math.prod(shape) * 4
    if size > MEMORY_THRESHOLD or (force_disk and size):
        # New sparse files read as zeros without allocating the whole array in RAM.
        return (owner or workspace()).allocate(shape)
    return np.zeros(shape, np.float32) if zero else np.empty(shape, np.float32)


def release_pages(array):
    """Drop mapped pages after a bounded pass; the backing file remains intact."""
    owner = root_array(array)
    if getattr(owner, "_ss_lease", None) is not None:
        try:
            import mmap
            owner._mmap.madvise(mmap.MADV_DONTNEED)
        except (AttributeError, OSError, ValueError):
            pass


def finite(array):
    progress(0, len(array), "Audio controleren")
    for a, b in blocks(len(array), BLOCK_FRAMES):
        if not np.isfinite(array[a:b]).all():
            raise AudioError("The audio contains non-finite sample values.")
        release_pages(array)
        progress(b, len(array), "Audio controleren")


def seal(array, *, checked=False):
    if not checked:
        finite(array)
    lease = lease_of(array)
    if lease is not None:
        root_array(array).flush()
        with open(lease.path, "rb") as file:
            os.fsync(file.fileno())
        release_pages(array)
    array.flags.writeable = False
    return array


def copy_array(samples, *, owner=None, force_disk=False, label="Audio kopiëren"):
    progress(0, len(samples), label)
    result = allocate(samples.shape, owner=owner, force_disk=force_disk)
    for a, b in blocks(len(samples), BLOCK_FRAMES):
        with np.errstate(over="ignore", invalid="ignore"):
            result[a:b] = samples[a:b]
        if not np.isfinite(result[a:b]).all():
            raise AudioError("The audio overflows float32 precision.")
        release_pages(samples)
        if isinstance(result, np.memmap):
            result.flush()
            release_pages(result)
        progress(b, len(samples), label)
    return result


def freeze(samples):
    if (samples.dtype == np.float32 and samples.flags.c_contiguous and
            not samples.flags.writeable and lease_of(samples) is not None):
        return samples
    return seal(copy_array(samples), checked=True)


def pin_paths(paths):
    previous = _pinned_paths.copy()
    _pinned_paths.clear()
    _pinned_paths.update(Path(path).resolve() for path in paths)
    for path in previous - _pinned_paths:
        owner = _workspaces.get(str(path.parent))
        if owner is not None and path not in owner.arrays:
            path.unlink(missing_ok=True)


def persist_array(samples):
    """Return a durable root and slice descriptor; keep the returned root alive until pinned."""
    root = root_array(samples)
    if root.ndim != 2 or root.dtype != np.float32 or not samples.flags.c_contiguous:
        root = seal(copy_array(samples, force_disk=True), checked=True)
        samples = root
    lease = lease_of(root)
    if lease is None:
        cached = _persisted.get(id(root))
        if cached and cached[0]() is root and cached[1].is_file():
            copied = open_buffer(cached[1], root.shape)
        else:
            copied = seal(copy_array(root, force_disk=True), checked=True)
            _persisted[id(root)] = (weakref.ref(root), lease_of(copied).path)
        offset = (samples.ctypes.data - root.ctypes.data) // root.dtype.itemsize
        root = copied
        lease = lease_of(root)
    else:
        offset = (samples.ctypes.data - root.ctypes.data) // root.dtype.itemsize
        root.flush()
    return root, dict(file=str(lease.path.relative_to(cache_root())),
                     shape=list(root.shape), offset=int(offset), frames=len(samples))


def open_buffer(path, shape):
    path = Path(path).resolve()
    base = cache_root().resolve()
    shape = tuple(int(n) for n in shape)
    if (path.parent.parent != base or not re.fullmatch(r"[0-9a-f]{32}\.buffer", path.name) or
            not path.is_relative_to(base) or len(shape) != 2 or shape[0] <= 0 or
            shape[1] not in (1, 2) or path.stat().st_size != math.prod(shape) * 4):
        raise AudioError("A recovered audio buffer is missing or invalid.")
    folder = path.parent
    owner = _workspaces.get(str(folder))
    if owner is None:
        owner = Workspace(base, existing=folder)
    array = np.memmap(path, np.float32, mode="r", shape=shape)
    owner.register(array, path)
    return array


def _close_workspace():
    if _default_workspace is not None:
        _default_workspace.close()


atexit.register(_close_workspace)
