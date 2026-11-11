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
    lib.ss_vst_process.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_process.restype=C.c_int
    lib.ss_vst_info.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_info.restype=C.c_int
    lib.ss_vst_set.argtypes=[C.c_void_p,C.c_uint32,C.c_double];lib.ss_vst_set.restype=C.c_int
    lib.ss_vst_state.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_state.restype=C.c_int
    lib.ss_vst_restore.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ss_vst_restore.restype=C.c_int
    return lib


def checked(result):
    if result is None or result<0: raise AudioError(library().ss_vst_error().decode('utf-8','replace'))
    return result


def scan(path):
    buffer=C.create_string_buffer(2*1024*1024)
    checked(library().ss_vst_scan(str(path).encode(),buffer,len(buffer)))
    return json.loads(buffer.value.decode('utf-8','replace'))


class Vst3:
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
