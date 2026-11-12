"""Control/audio-port Linux effects. Loaded only inside the isolated helper.

ABI sources: https://www.ladspa.org/ladspa_sdk/ladspa.h.txt and
https://lv2plug.in/c/html/group__core.html . Lilv reads LV2 metadata.
"""
import base64
import ctypes as C
import json
import math
from pathlib import Path

import numpy as np
from .audio import AudioError

P=C.c_void_p; F=C.c_float; U=C.c_uint32; Z=C.c_size_t
FP=C.POINTER(F)
MAX_STATE=1024*1024


class Port:
    def __init__(self,index,name,kind,input,low=0,high=1,default=0,*,log=False,integer=False,toggled=False):
        self.index,self.name,self.kind,self.input=index,name,kind,input
        self.low,self.high=float(low),float(high)
        if not math.isfinite(self.low) or not math.isfinite(self.high) or self.high<self.low:
            raise AudioError('Invalid plug-in parameter bounds.')
        self.log=log and low>0 and high>low
        self.integer,self.toggled=integer,toggled
        self.value=F(min(self.high,max(self.low,default)))

    def plain(self,value):
        result=(math.exp(math.log(self.low)+value*math.log(self.high/self.low)) if self.log
                else self.low+value*(self.high-self.low))
        return (self.high if value>=.5 else self.low) if self.toggled else round(result) if self.integer else result

    def normalized(self):
        if self.high==self.low:return 0.0
        value=min(self.high,max(self.low,self.value.value))
        return math.log(value/self.low)/math.log(self.high/self.low) if self.log else (value-self.low)/(self.high-self.low)


class PortPlugin:
    def initialize_ports(self,ports):
        self.ports=ports
        if len(ports)>4096:raise AudioError('Too many plug-in ports.')
        self.inputs=[p for p in ports if p.kind=='audio' and p.input]
        self.outputs=[p for p in ports if p.kind=='audio' and not p.input]
        if (len(self.inputs),len(self.outputs)) not in ((1,1),(2,2)):
            raise AudioError('Choose a mono or stereo audio effect with matching inputs and outputs.')
        self.controls={str(p.index):p for p in ports if p.kind=='control'}
        self.handles=[];self.audio=[];self.latency_port=None

    def latency(self):
        latency=0
        if self.latency_port is not None:
            raw=self.ports[self.latency_port].value.value
            if not math.isfinite(raw) or raw<0 or raw>self.rate*10:
                raise AudioError('The plug-in reported an invalid processing delay.')
            latency=round(raw)
        return latency

    def info(self):
        return dict(latency=self.latency(),parameters=[dict(id=p.index,name=p.name,unit='',
                    display=f'{p.value.value:.9g}',steps=1 if p.toggled else round(p.high-p.low) if p.integer else 0,
                    readonly=not p.input,value=p.normalized()) for p in self.controls.values()])

    def set_values(self,values):
        if not isinstance(values,dict) or len(values)>4096:raise AudioError('Invalid plug-in parameter list.')
        converted=[]
        for key,value in values.items():
            port=self.controls.get(key)
            if port is None or not port.input:raise AudioError('The plug-in parameter is missing or read-only.')
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1:
                raise AudioError('Plug-in parameters must be between zero and one.')
            converted.append((port,port.plain(value)))
        for port,value in converted:port.value.value=value

    def connect(self,handle):
        buffers={}
        for port in self.ports:
            if port.kind=='audio':
                buffers[port.index]=np.zeros(1024,np.float32)
                data=buffers[port.index].ctypes.data_as(FP)
            elif port.kind=='control':data=C.pointer(port.value)
            else:
                # Optional unknown ports may be unconnected; mandatory ones were rejected.
                data=None
            self.descriptor.connect_port(handle,port.index,data)
        self.audio.append(buffers)

    def process(self,data):
        if data.dtype!=np.float32 or data.ndim!=2 or data.shape[1]!=2 or len(data)>1024 or not data.flags.c_contiguous:
            raise AudioError('Invalid plug-in audio block.')
        n=len(data)
        for instance,(handle,buffers) in enumerate(zip(self.handles,self.audio)):
            for channel,port in enumerate(self.inputs):buffers[port.index][:n]=data[:,instance if len(self.inputs)==1 else channel]
            self.descriptor.run(handle,n)
            for channel,port in enumerate(self.outputs):data[:,instance if len(self.outputs)==1 else channel]=buffers[port.index][:n]
        if not np.isfinite(data).all():raise AudioError('The plug-in returned invalid audio.')
        return data

    def state(self):
        return json.dumps(dict(version=1,values={k:p.normalized() for k,p in self.controls.items() if p.input}),allow_nan=False).encode()

    def restore(self,state):
        if len(state)>MAX_STATE:raise AudioError('Plug-in state exceeds 1 MiB.')
        data=json.loads(state)
        if not isinstance(data,dict) or data.get('version')!=1:raise AudioError('Invalid plug-in state.')
        self.set_values(data.get('values',{}))

    def open_editor(self,*_):raise AudioError('This plug-in has no supported custom editor. Use its parameter controls.')
    def editor_size(self):return None
    def close_editor(self):pass
    def idle(self):pass

    def close(self):
        for handle in getattr(self,'handles',[]):
            if self.descriptor.deactivate:self.descriptor.deactivate(handle)
            self.descriptor.cleanup(handle)
        self.handles=[]


class LadspaHint(C.Structure):
    _fields_=[('flags',C.c_int),('low',F),('high',F)]


class LadspaDescriptor(C.Structure):pass
LD=C.POINTER(LadspaDescriptor)
LadspaDescriptor._fields_=[('unique_id',C.c_ulong),('label',C.c_char_p),('properties',C.c_int),
    ('name',C.c_char_p),('maker',C.c_char_p),('copyright',C.c_char_p),('count',C.c_ulong),
    ('ports',C.POINTER(C.c_int)),('names',C.POINTER(C.c_char_p)),('hints',C.POINTER(LadspaHint)),('implementation',P),
    ('instantiate',C.CFUNCTYPE(P,LD,C.c_ulong)),('connect_port',C.CFUNCTYPE(None,P,C.c_ulong,P)),
    ('activate',C.CFUNCTYPE(None,P)),('run',C.CFUNCTYPE(None,P,C.c_ulong)),
    ('run_adding',P),('set_run_adding_gain',P),('deactivate',C.CFUNCTYPE(None,P)),('cleanup',C.CFUNCTYPE(None,P))]


def ladspa_descriptors(path):
    lib=C.CDLL(str(path));lib.ladspa_descriptor.argtypes=[C.c_ulong];lib.ladspa_descriptor.restype=LD
    for index in range(4096):
        pointer=lib.ladspa_descriptor(index)
        if not pointer:return
        yield lib,pointer
    raise AudioError('Too many LADSPA descriptors.')


def scan_ladspa(path):
    return [dict(id=str(p.contents.unique_id),name=p.contents.name.decode('utf-8','replace'),path=str(Path(path).resolve()))
            for _,p in ladspa_descriptors(path)]


class Ladspa(PortPlugin):
    def __init__(self,path,identifier,rate):
        self.rate=rate;found=next(((lib,p) for lib,p in ladspa_descriptors(path) if str(p.contents.unique_id)==identifier),None)
        if found is None:raise AudioError('The LADSPA effect is missing from its library.')
        self.library,self.pointer=found;self.descriptor=self.pointer.contents;desc=self.descriptor
        if desc.count>4096 or not desc.instantiate or not desc.connect_port or not desc.run or not desc.cleanup:
            raise AudioError('Invalid LADSPA descriptor.')
        ports=[]
        for index in range(desc.count):
            flags=desc.ports[index]
            if bool(flags&1)==bool(flags&2) or bool(flags&4)==bool(flags&8):raise AudioError('Invalid LADSPA port direction or type.')
            if flags&8:
                ports.append(Port(index,desc.names[index].decode('utf-8','replace'),'audio',bool(flags&1)))
                continue
            hint=desc.hints[index];h=hint.flags
            factor=rate if h&8 else 1
            low=float(hint.low)*factor if h&1 else 0
            high=float(hint.high)*factor if h&2 else 1
            default={0x200:0,0x240:1,0x280:100,0x2c0:440}.get(h&0x3c0)
            if h&4:low,high,default=0,1,0 if default is None else default
            if default is not None:
                if not h&1:low=min(low,default)
                if not h&2:high=max(high,default*4)
            elif h&0x3c0 in (0x40,0x80,0xc0,0x100,0x140):
                fraction={0x40:0,0x80:.25,0xc0:.5,0x100:.75,0x140:1}[h&0x3c0]
                default=math.exp(math.log(low)*(1-fraction)+math.log(high)*fraction) if h&16 and low>0 and high>0 else low*(1-fraction)+high*fraction
            else:default=min(high,max(low,0))
            if h&32:default=round(default)
            ports.append(Port(index,desc.names[index].decode('utf-8','replace'),'audio' if flags&8 else 'control',bool(flags&1),low,high,default,log=bool(h&16),integer=bool(h&32),toggled=bool(h&4)))
        self.initialize_ports(ports)
        self.latency_port=next((p.index for p in ports if p.kind=='control' and not p.input and p.name.lower() in ('latency','_latency')),None)
        try:
            for _ in range(2 if len(self.inputs)==1 else 1):
                handle=desc.instantiate(self.pointer,round(rate))
                if not handle:raise AudioError('LADSPA initialization failed.')
                self.handles.append(handle);self.connect(handle)
                if desc.activate:desc.activate(handle)
        except Exception:self.close();raise
