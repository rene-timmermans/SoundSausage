"""Disposable native plug-in process; audio is transferred through private pipes."""
import base64
import resource
import sys
import numpy as np
from .plugins import send, receive, Pipe
from .vst3 import scan, Vst3, library


def main():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    sock=Pipe(int(sys.argv[1]),int(sys.argv[2]));plugin=None;editor=None
    def idle():
        if editor is not None:editor.idle()
    try:
        while True:
            idle()
            message=receive(sock,timeout=86400,poll=idle,poll_interval=.01);op=message.get('op')
            try:
                if op=='host_info':result=dict(ready=bool(library()))
                elif op=='scan':
                    format=message.get('format','VST3')
                    if format=='LV2':
                        from .lv2 import scan as scan_lv2
                        plugins=scan_lv2(message['path'])
                    elif format=='LADSPA':
                        from .linux_plugin import scan_ladspa
                        plugins=scan_ladspa(message['path'])
                    elif format=='VST3':plugins=scan(message['path'])
                    else:raise ValueError('Unsupported plug-in format.')
                    result=dict(plugins=plugins)
                elif op=='open':
                    if editor is not None:editor.close();editor=None
                    if plugin is not None:plugin.close()
                    entry=message['entry'];format=entry.get('format','VST3')
                    if format=='LV2':
                        from .lv2 import Lv2
                        plugin=Lv2(entry['bundle'],entry['class_id'],message['rate'])
                    elif format=='LADSPA':
                        from .linux_plugin import Ladspa
                        plugin=Ladspa(entry['path'],entry['class_id'],message['rate'])
                    elif format=='VST3':plugin=Vst3(entry['path'],entry['class_id'],message['rate'])
                    else:raise ValueError('Unsupported plug-in format.')
                    settings=message['settings'];state=base64.b64decode(settings.get('state',''),validate=True)
                    if state:plugin.restore(state)
                    plugin.set_values(settings.get('values',{}));result=dict(info=plugin.info())
                elif op=='editor_open':
                    from .plugin_editor import Editor
                    if editor is not None:editor.close();editor=None
                    editor=Editor(plugin,'SoundSausage — '+entry['name'])
                    result=dict(open=True)
                elif op=='editor_close':
                    if editor is not None:editor.close();editor=None
                    result=dict(open=False)
                elif op=='process':
                    frames=message['frames']
                    if type(frames) is not int or not 0<=frames<=1024:raise ValueError('Invalid audio block size.')
                    raw=base64.b64decode(message['data'],validate=True)
                    if len(raw)!=frames*8:raise ValueError('Invalid audio buffer.')
                    data=np.frombuffer(raw,np.float32).reshape(frames,2).copy()
                    plugin.process(data);result=dict(data=base64.b64encode(data.tobytes()).decode(),latency=plugin.latency())
                elif op=='parameters':
                    plugin.set_values(message['values']);result={}
                elif op=='restore':
                    plugin.restore(base64.b64decode(message['state'],validate=True));result=dict(info=plugin.info())
                elif op=='snapshot':
                    if isinstance(plugin,Vst3):plugin.process(np.zeros((0,2),np.float32))
                    result=dict(info=plugin.info(),state=base64.b64encode(plugin.state()).decode(),editor_size=plugin.editor_size())
                else:raise ValueError('Unknown plug-in request.')
                send(sock,dict(ok=True,**result))
            except Exception as error:send(sock,dict(ok=False,error=str(error)))
    except (OSError,ValueError):pass
    finally:
        if editor is not None:editor.close()
        if plugin is not None:plugin.close()
        sock.close()


if __name__=='__main__':main()
