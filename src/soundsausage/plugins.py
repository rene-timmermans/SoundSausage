"""Local plug-in registry and crash-isolated VST3 requests; projects never supply a library path."""
import base64
import hashlib
import json
import os
from pathlib import Path
import select
import struct
import subprocess
import sys
import time

import numpy as np
from .audio import AudioError
from . import storage

MAX_MESSAGE=3*1024*1024


class Pipe:
    def __init__(self,read_fd,write_fd):
        self.read_fd,self.write_fd=read_fd,write_fd
        os.set_blocking(write_fd,False)
    def fileno(self):return self.read_fd
    def recv(self,count):return os.read(self.read_fd,count)
    def sendall(self,data):
        sent=0;deadline=time.monotonic()+3
        while sent<len(data):
            remaining=deadline-time.monotonic()
            if remaining<=0 or not select.select([],[self.write_fd],[],remaining)[1]:raise AudioError('The plug-in stopped reading.')
            try:sent+=os.write(self.write_fd,data[sent:])
            except BlockingIOError:continue
    def close(self):
        for fd in (self.read_fd,self.write_fd):
            try:os.close(fd)
            except OSError:pass
        self.read_fd=self.write_fd=-1


def registry_path():
    config=Path(os.environ.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'SoundSausage/plugin-registry.json'
    return Path(os.environ.get('SOUNDSAUSAGE_PLUGIN_REGISTRY',str(config)))


def digest(path):
    with Path(path).open('rb') as source: return hashlib.file_digest(source,'sha256').hexdigest()


def bundle_digest(path):
    root=Path(path).resolve();files=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in ('.ttl','.so'))
    if len(files)>4096:raise AudioError('The plug-in bundle contains too many files.')
    value=hashlib.sha256()
    for file in files:
        value.update(str(file.relative_to(root)).encode());value.update(digest(file).encode())
    return value.hexdigest()


def fingerprint(entry):
    if entry.get('format')=='LV2':
        return hashlib.sha256((bundle_digest(entry['bundle'])+digest(entry['path'])).encode()).hexdigest()
    return digest(entry['path'])


def read_registry():
    path=registry_path()
    if not path.exists():return {}
    if path.stat().st_size>2*1024*1024:raise AudioError('The plug-in list is too large. Scan the plug-ins again.')
    value=json.loads(path.read_text('utf-8'))
    if not isinstance(value,dict):raise AudioError('Invalid local plug-in list.')
    return value


def save_registry(value):
    path=registry_path();path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf-8')
    os.replace(temporary,path)


def plugin_binary(path):
    path=Path(path).resolve()
    if path.is_file() and path.suffix=='.so':return path
    if path.is_dir() and path.suffix.lower()=='.vst3':
        choices=sorted((path/'Contents/x86_64-linux').glob('*.so'))
        if len(choices)==1:return choices[0]
    raise AudioError('Choose a Linux VST3 bundle or its shared library.')


def send(sock,value):
    data=json.dumps(value,allow_nan=False,separators=(',',':')).encode()
    if len(data)>MAX_MESSAGE:raise AudioError('The plug-in message is too large.')
    sock.sendall(struct.pack('<I',len(data))+data)


def receive(sock,timeout=3,poll=None,poll_interval=.05):
    deadline=time.monotonic()+timeout
    def read(count):
        result=bytearray()
        while len(result)<count:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise AudioError('The plug-in stopped responding.')
            if not select.select([sock],[],[],min(poll_interval,remaining) if poll else remaining)[0]:
                if poll:poll();continue
                raise AudioError('The plug-in stopped responding.')
            data=sock.recv(count-len(result))
            if not data:raise AudioError('The plug-in helper closed unexpectedly.')
            result.extend(data)
        return bytes(result)
    count=struct.unpack('<I',read(4))[0]
    if count>MAX_MESSAGE:raise AudioError('Invalid plug-in response length.')
    value=json.loads(read(count))
    if not isinstance(value,dict):raise AudioError('Invalid plug-in response.')
    return value


class Helper:
    def __init__(self):
        parent_read,child_write=os.pipe();child_read,parent_write=os.pipe()
        self.sock=Pipe(parent_read,parent_write)
        try:
            self.process=subprocess.Popen([sys.executable,'-m','soundsausage.plugin_worker',str(child_read),str(child_write)],
                pass_fds=(child_read,child_write),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except Exception:self.sock.close();raise
        finally:os.close(child_read);os.close(child_write)

    def request(self,value,timeout=3,poll=None):
        try:
            send(self.sock,value);result=receive(self.sock,timeout,poll)
            if not result.get('ok'):raise AudioError(result.get('error','The plug-in failed.'))
            return result
        except (OSError,ValueError) as error:
            self.close(graceful=False);raise AudioError(str(error)) from error

    def close(self,graceful=True):
        if graceful and self.process.poll() is None and self.sock.read_fd>=0:
            try:
                send(self.sock,dict(op='shutdown'));receive(self.sock,timeout=.15)
                self.process.wait(timeout=.15)
            except (OSError,ValueError,subprocess.TimeoutExpired):pass
        self.sock.close()
        if self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=.1)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=.5)


def scan_plugin(path,format='VST3'):
    from .operations import progress
    if Path(path).suffix.lower()=='.lv2':format='LV2'
    if format not in ('VST3','LV2','LADSPA'):raise AudioError('Unsupported plug-in format.')
    binary=Path(path).resolve() if format!='VST3' else plugin_binary(path)
    if format=='LV2' and (not binary.is_dir() or binary.suffix.lower()!='.lv2'):raise AudioError('Choose an installed LV2 bundle.')
    if format=='LADSPA' and (not binary.is_file() or binary.suffix!='.so'):raise AudioError('Choose a LADSPA shared library.')
    signature=bundle_digest if format=='LV2' else digest
    before=signature(binary);helper=Helper()
    try: result=helper.request(dict(op='scan',format=format,path=str(binary)),timeout=20,poll=lambda:progress(0,1,'Plug-in onderzoeken'))['plugins']
    finally:helper.close()
    if signature(binary)!=before:raise AudioError('The plug-in changed during scanning. Scan it again.')
    if not result:raise AudioError('No audio effects were found.')
    registry=read_registry();keys=[]
    for item in result:
        key=format.lower()+':'+item['id']
        entry=dict(id=key,class_id=item['id'],name=item['name'],path=item.get('path',str(binary)),format=format)
        if format=='LV2':entry['bundle']=item['bundle']
        entry['fingerprint']=fingerprint(entry);registry[key]=entry
        keys.append(key)
    save_registry(registry);return [registry[key] for key in keys]


class PluginProcess:
    def __init__(self,settings,rate):
        self.helper=None;self.rate=rate
        if set(settings)-{'plugin_id','name','fingerprint','values','state'}:raise AudioError('Unknown plug-in setting.')
        key=settings.get('plugin_id');entry=read_registry().get(key)
        if entry is None:raise AudioError(f"Missing plug-in: {settings.get('name',key)}. Add the installed plug-in in Track Effects.")
        if settings.get('fingerprint',entry['fingerprint'])!=entry['fingerprint'] or fingerprint(entry)!=entry['fingerprint']:
            raise AudioError('The plug-in differs from the saved version. Scan and select the installed version again.')
        self.helper=Helper()
        try:self.info=self.helper.request(dict(op='open',entry=entry,settings=settings,rate=rate),timeout=10)['info']
        except Exception:self.close();raise

    def process(self,data):
        if len(data)>1024:
            for first in range(0,len(data),1024):self.process(data[first:first+1024])
            return data
        result=self.helper.request(dict(op='process',frames=len(data),data=base64.b64encode(data.tobytes()).decode()))
        latency=result.get('latency',0)
        if type(latency) is not int or not 0<=latency<=round(self.rate*10):raise AudioError('The plug-in reported an invalid processing delay.')
        self.info['latency']=latency
        raw=base64.b64decode(result['data'],validate=True)
        if len(raw)!=data.nbytes:raise AudioError('The plug-in returned an invalid audio length.')
        output=np.frombuffer(raw,np.float32).reshape(data.shape)
        if not np.isfinite(output).all():raise AudioError('The plug-in returned invalid audio.')
        data[:]=output;return data

    def snapshot(self):
        return self.helper.request(dict(op='snapshot'))

    def restore(self,state):
        self.info=self.helper.request(dict(op='restore',state=state))['info']

    def open_editor(self):
        return self.helper.request(dict(op='editor_open'),timeout=10)

    def close_editor(self):
        return self.helper.request(dict(op='editor_close'))

    def close(self):
        if self.helper is not None:self.helper.close();self.helper=None
