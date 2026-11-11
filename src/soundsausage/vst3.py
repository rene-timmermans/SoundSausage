"""VST3 native bridge. Imported exclusively by the isolated plug-in helper."""
import ctypes as C
from functools import lru_cache
import json
from pathlib import Path
import numpy as np
from .audio import AudioError

MAX_STATE = 1024*1024


@lru_cache(maxsize=1)
def library():
    path=Path(__file__).resolve().parents[2]/'build/libsoundsausage_vst3.so'
    try: lib=C.CDLL(str(path))
    except OSError as error: raise AudioError('The VST3 host is missing. Reinstall SoundSausage or run make.') from error
    lib.ss_vst_error.restype=C.c_char_p
    lib.ss_vst_scan.argtypes=[C.c_char_p,C.c_void_p,C.c_int];lib.ss_vst_scan.restype=C.c_int
    lib.ss_vst_open.argtypes=[C.c_char_p,C.c_char_p,C.c_double];lib.ss_vst_open.restype=C.c_void_p
    lib.ss_vst_close.argtypes=[C.c_void_p];lib.ss_vst_close.restype=None
    lib.ss_vst_latency.argtypes=[C.c_void_p];lib.ss_vst_latency.restype=C.c_uint32
    lib.ss_vst_process.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_process.restype=C.c_int
    lib.ss_vst_info.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_info.restype=C.c_int
    lib.ss_vst_set.argtypes=[C.c_void_p,C.c_uint32,C.c_double];lib.ss_vst_set.restype=C.c_int
    lib.ss_vst_state.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_state.restype=C.c_int
    lib.ss_vst_restore.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_restore.restype=C.c_int
    lib.ss_vst_editor_open.argtypes=[C.c_void_p,C.c_size_t,C.c_double];lib.ss_vst_editor_open.restype=C.c_int
    lib.ss_vst_editor_close.argtypes=[C.c_void_p];lib.ss_vst_editor_close.restype=None
    lib.ss_vst_editor_size.argtypes=[C.c_void_p,C.POINTER(C.c_int),C.POINTER(C.c_int)];lib.ss_vst_editor_size.restype=C.c_int
    lib.ss_vst_editor_resize.argtypes=[C.c_void_p,C.c_int,C.c_int];lib.ss_vst_editor_resize.restype=C.c_int
    lib.ss_vst_editor_idle.argtypes=[C.c_void_p];lib.ss_vst_editor_idle.restype=C.c_int
    return lib


def checked(result):
    if result is None or result<0: raise AudioError(library().ss_vst_error().decode('utf-8','replace'))
    return result


def scan(path):
    buffer=C.create_string_buffer(2*1024*1024)
    checked(library().ss_vst_scan(str(path).encode(),buffer,len(buffer)))
    return json.loads(buffer.value.decode('utf-8','replace'))


class Vst3:
    def latency(self):return int(library().ss_vst_latency(self.handle))
    def __init__(self,path,identifier,rate):
        self.handle=library().ss_vst_open(str(path).encode(),identifier.encode(),rate)
        if not self.handle: raise AudioError(library().ss_vst_error().decode('utf-8','replace'))

    def info(self):
        data=C.create_string_buffer(2*1024*1024);checked(library().ss_vst_info(self.handle,data,len(data)))
        return json.loads(data.value.decode('utf-8','replace'))

    def set_values(self,values):
        available={str(p['id']):p for p in self.info()['parameters']}
        if not isinstance(values,dict) or len(values)>4096: raise AudioError('Invalid VST3 parameter list.')
        for key,value in values.items():
            if key not in available or available[key]['readonly']: raise AudioError('The VST3 parameter is missing or read-only.')
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not np.isfinite(value) or not 0<=value<=1:
                raise AudioError('VST3 parameters must be between zero and one.')
            checked(library().ss_vst_set(self.handle,int(key),value))

    def state(self):
        data=C.create_string_buffer(MAX_STATE);count=checked(library().ss_vst_state(self.handle,data,len(data)))
        return data.raw[:count]

    def restore(self,state):
        if len(state)>MAX_STATE: raise AudioError('VST3 state exceeds 1 MiB.')
        checked(library().ss_vst_restore(self.handle,state,len(state)))

    def process(self,data):
        if data.dtype!=np.float32 or data.ndim!=2 or data.shape[1]!=2 or len(data)>1024 or not data.flags.c_contiguous:
            raise AudioError('Invalid VST3 audio block.')
        checked(library().ss_vst_process(self.handle,data.ctypes.data,len(data)))
        return data

    def close(self):
        if self.handle:library().ss_vst_close(self.handle);self.handle=None

    def open_editor(self, parent, scale=1):
        checked(library().ss_vst_editor_open(self.handle,parent,scale))
        return self.editor_size()

    def editor_size(self):
        width,height=C.c_int(),C.c_int()
        available=library().ss_vst_editor_size(self.handle,C.byref(width),C.byref(height))
        return (width.value,height.value) if available else None

    def resize_editor(self,width,height): checked(library().ss_vst_editor_resize(self.handle,width,height))
    def close_editor(self): library().ss_vst_editor_close(self.handle)
    def idle(self): checked(library().ss_vst_editor_idle(self.handle))
