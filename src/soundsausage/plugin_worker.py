"""Disposable native plug-in process; audio is transferred through private pipes."""
import base64
import resource
import sys
import numpy as np
from .plugins import send, receive, Pipe
from .vst3 import scan, Vst3, library


def main():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    sock=Pipe(int(sys.argv[1]),int(sys.argv[2]));plugin=None
    try:
        while True:
            message=receive(sock,timeout=86400);op=message.get('op')
            try:
                if op=='host_info':result=dict(ready=bool(library()))
                elif op=='scan':result=dict(plugins=scan(message['path']))
                elif op=='open':
                    if plugin is not None:plugin.close()
                    plugin=Vst3(message['entry']['path'],message['entry']['class_id'],message['rate'])
                    settings=message['settings'];state=base64.b64decode(settings.get('state',''),validate=True)
                    if state:plugin.restore(state)
                    plugin.set_values(settings.get('values',{}));result=dict(info=plugin.info())
                elif op=='process':
                    frames=message['frames']
                    if type(frames) is not int or not 0<=frames<=1024:raise ValueError('Invalid audio block size.')
                    raw=base64.b64decode(message['data'],validate=True)
                    if len(raw)!=frames*8:raise ValueError('Invalid audio buffer.')
                    data=np.frombuffer(raw,np.float32).reshape(frames,2).copy()
                    plugin.process(data);result=dict(data=base64.b64encode(data.tobytes()).decode())
                elif op=='parameters':
                    plugin.set_values(message['values']);result={}
                elif op=='snapshot':
                    plugin.process(np.zeros((0,2),np.float32))
                    result=dict(info=plugin.info(),state=base64.b64encode(plugin.state()).decode())
                else:raise ValueError('Unknown plug-in request.')
                send(sock,dict(ok=True,**result))
            except Exception as error:send(sock,dict(ok=False,error=str(error)))
    except (OSError,ValueError):pass
    finally:
        if plugin is not None:plugin.close()
        sock.close()


if __name__=='__main__':main()
