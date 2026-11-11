"""Lilv metadata and public LV2 C ABI; imported only in the plug-in helper."""
import base64
import ctypes as C
import json
import math
from pathlib import Path
from urllib.parse import urlparse,unquote

from .audio import AudioError
from .linux_plugin import PortPlugin,Port,P,F,U,Z,MAX_STATE

CORE='http://lv2plug.in/ns/lv2core#'
URID='http://lv2plug.in/ns/ext/urid#'
STATE='http://lv2plug.in/ns/ext/state#'
UI='http://lv2plug.in/ns/extensions/ui#'
ATOM='http://lv2plug.in/ns/ext/atom#'


def file_path(uri):
    parsed=urlparse(uri)
    if parsed.scheme!='file' or parsed.netloc not in ('','localhost'):raise AudioError('The LV2 bundle refers to a non-local library.')
    return str(Path(unquote(parsed.path)).resolve())


class World:
    def __init__(self,bundle):
        try:self.lib=C.CDLL('liblilv-0.so.0')
        except OSError as error:raise AudioError('LV2 support needs Lilv. Install the distribution’s Lilv package.') from error
        lib=self.lib
        def bind(name,result,*args):
            fn=getattr(lib,'lilv_'+name);fn.restype=result;fn.argtypes=list(args)
        bind('world_new',P);bind('world_free',None,P)
        bind('new_file_uri',P,P,C.c_char_p,C.c_char_p);bind('new_uri',P,P,C.c_char_p)
        bind('world_load_bundle',None,P,P);bind('world_get_all_plugins',P,P)
        bind('world_find_nodes',P,P,P,P,P)
        for collection in ('plugins','nodes','uis'):
            bind(collection+'_begin',P,P);bind(collection+'_is_end',C.c_bool,P,P)
            bind(collection+'_next',P,P,P);bind(collection+'_get',P,P,P)
        bind('nodes_free',None,P);bind('uis_free',None,P)
        bind('node_free',None,P);bind('node_as_string',C.c_char_p,P);bind('node_as_uri',C.c_char_p,P)
        bind('node_as_float',F,P);bind('node_as_int',C.c_int,P)
        bind('node_is_float',C.c_bool,P);bind('node_is_int',C.c_bool,P)
        for method in ('uri','name','library_uri','bundle_uri','required_features','uis'):
            bind('plugin_get_'+method,P,P)
        bind('plugin_get_num_ports',U,P);bind('plugin_get_port_by_index',P,P,U)
        bind('port_get_name',P,P,P);bind('port_get_symbol',P,P,P)
        bind('port_is_a',C.c_bool,P,P,P);bind('port_has_property',C.c_bool,P,P,P)
        bind('port_get_range',None,P,P,C.POINTER(P),C.POINTER(P),C.POINTER(P))
        bind('plugin_has_latency',C.c_bool,P);bind('plugin_get_latency_port_index',U,P)
        for method in ('uri','binary_uri','bundle_uri'):bind('ui_get_'+method,P,P)
        bind('ui_is_a',C.c_bool,P,P)
        self.world=lib.lilv_world_new()
        if not self.world:raise AudioError('Cannot create the LV2 metadata world.')
        self.nodes={}
        try:
            uri=lib.lilv_new_file_uri(self.world,None,(str(Path(bundle).resolve())+'/').encode())
            if not uri:raise AudioError('Invalid LV2 bundle path.')
            try:lib.lilv_world_load_bundle(self.world,uri)
            finally:lib.lilv_node_free(uri)
        except Exception:self.close();raise

    def node(self,uri):
        if uri not in self.nodes:self.nodes[uri]=self.lib.lilv_new_uri(self.world,uri.encode())
        return self.nodes[uri]

    def text(self,node,owned=False,uri=False):
        if not node:return ''
        try:
            value=(self.lib.lilv_node_as_uri if uri else self.lib.lilv_node_as_string)(node)
            return value.decode('utf-8','replace') if value else ''
        finally:
            if owned:self.lib.lilv_node_free(node)

    def collection(self,kind,value):
        if not value:return
        lib=self.lib;iterator=getattr(lib,'lilv_'+kind+'_begin')(value)
        count=0
        while not getattr(lib,'lilv_'+kind+'_is_end')(value,iterator):
            count+=1
            if count>4096:raise AudioError('The LV2 metadata list is too large.')
            yield getattr(lib,'lilv_'+kind+'_get')(value,iterator)
            iterator=getattr(lib,'lilv_'+kind+'_next')(value,iterator)

    def required(self,subject):
        nodes=self.lib.lilv_world_find_nodes(self.world,subject,self.node(CORE+'requiredFeature'),None)
        try:return [self.text(n,uri=True) for n in self.collection('nodes',nodes)]
        finally:self.lib.lilv_nodes_free(nodes)

    def metadata(self,plugin):
        lib=self.lib
        result=dict(id=self.text(lib.lilv_plugin_get_uri(plugin),uri=True),
                    name=self.text(lib.lilv_plugin_get_name(plugin),True),
                    path=file_path(self.text(lib.lilv_plugin_get_library_uri(plugin),uri=True)),
                    bundle=file_path(self.text(lib.lilv_plugin_get_bundle_uri(plugin),uri=True)),
                    required=self.required(lib.lilv_plugin_get_uri(plugin)))
        ports=[]
        count=lib.lilv_plugin_get_num_ports(plugin)
        if count>4096:raise AudioError('Too many LV2 ports.')
        for index in range(count):
            port=lib.lilv_plugin_get_port_by_index(plugin,index)
            is_a=lambda name:lib.lilv_port_is_a(plugin,port,self.node(CORE+name))
            prop=lambda uri:lib.lilv_port_has_property(plugin,port,self.node(uri))
            defaults,low,high=P(),P(),P()
            lib.lilv_port_get_range(plugin,port,C.byref(defaults),C.byref(low),C.byref(high))
            def number(node,fallback):
                try:
                    if node and lib.lilv_node_is_float(node):return float(lib.lilv_node_as_float(node))
                    if node and lib.lilv_node_is_int(node):return float(lib.lilv_node_as_int(node))
                    return fallback
                finally:
                    if node:lib.lilv_node_free(node)
            ports.append(dict(index=index,name=self.text(lib.lilv_port_get_name(plugin,port),True),
                symbol=self.text(lib.lilv_port_get_symbol(plugin,port)),
                kind='audio' if is_a('AudioPort') else 'control' if is_a('ControlPort') else 'optional' if prop(CORE+'connectionOptional') else 'unsupported',
                input=bool(is_a('InputPort')),low=number(low,0),high=number(high,1),default=number(defaults,0),
                log=bool(prop('http://lv2plug.in/ns/ext/port-props#logarithmic')),integer=bool(prop(CORE+'integer')),
                toggled=bool(prop(CORE+'toggled')),sample_rate=bool(prop(CORE+'sampleRate'))))
        result['ports']=ports
        result['latency_port']=int(lib.lilv_plugin_get_latency_port_index(plugin)) if lib.lilv_plugin_has_latency(plugin) else None
        uis=lib.lilv_plugin_get_uis(plugin);result['uis']=[]
        try:
            for ui in self.collection('uis',uis):
                if lib.lilv_ui_is_a(ui,self.node(UI+'X11UI')):
                    result['uis'].append(dict(id=self.text(lib.lilv_ui_get_uri(ui),uri=True),
                        path=file_path(self.text(lib.lilv_ui_get_binary_uri(ui),uri=True)),
                        bundle=file_path(self.text(lib.lilv_ui_get_bundle_uri(ui),uri=True)),
                        required=self.required(lib.lilv_ui_get_uri(ui))))
        finally:lib.lilv_uis_free(uis)
        return result

    def plugins(self):
        for plugin in self.collection('plugins',self.lib.lilv_world_get_all_plugins(self.world)):
            yield self.metadata(plugin)

    def close(self):
        if getattr(self,'world',None):
            for node in self.nodes.values():self.lib.lilv_node_free(node)
            self.lib.lilv_world_free(self.world);self.world=None


def scan(bundle):
    world=World(bundle)
    try:return list(world.plugins())
    finally:world.close()


class Feature(C.Structure):_fields_=[('uri',C.c_char_p),('data',P)]
FEATURES=C.POINTER(C.POINTER(Feature))
class Descriptor(C.Structure):pass
DP=C.POINTER(Descriptor)
Descriptor._fields_=[('uri',C.c_char_p),('instantiate',C.CFUNCTYPE(P,DP,C.c_double,C.c_char_p,FEATURES)),
    ('connect_port',C.CFUNCTYPE(None,P,U,P)),('activate',C.CFUNCTYPE(None,P)),('run',C.CFUNCTYPE(None,P,U)),
    ('deactivate',C.CFUNCTYPE(None,P)),('cleanup',C.CFUNCTYPE(None,P)),('extension_data',C.CFUNCTYPE(P,C.c_char_p))]
MAP=C.CFUNCTYPE(U,P,C.c_char_p)
UNMAP=C.CFUNCTYPE(P,P,U)
class Map(C.Structure):_fields_=[('handle',P),('map',MAP)]
class Unmap(C.Structure):_fields_=[('handle',P),('unmap',UNMAP)]
class Option(C.Structure):_fields_=[('context',U),('subject',U),('key',U),('size',U),('type',U),('value',P)]
STORE=C.CFUNCTYPE(C.c_int,P,U,P,Z,U,U)
RETRIEVE=C.CFUNCTYPE(P,P,U,C.POINTER(Z),C.POINTER(U),C.POINTER(U))
SAVE=C.CFUNCTYPE(C.c_int,P,STORE,P,U,FEATURES)
RESTORE=C.CFUNCTYPE(C.c_int,P,RETRIEVE,P,U,FEATURES)
class StateInterface(C.Structure):_fields_=[('save',SAVE),('restore',RESTORE)]
WRITE=C.CFUNCTYPE(None,P,U,U,U,P)
class UiDescriptor(C.Structure):pass
UDP=C.POINTER(UiDescriptor)
UiDescriptor._fields_=[('uri',C.c_char_p),('instantiate',C.CFUNCTYPE(P,UDP,C.c_char_p,C.c_char_p,WRITE,P,C.POINTER(P),FEATURES)),
    ('cleanup',C.CFUNCTYPE(None,P)),('port_event',C.CFUNCTYPE(None,P,U,U,U,P)),('extension_data',C.CFUNCTYPE(P,C.c_char_p))]
class UiIdle(C.Structure):_fields_=[('idle',C.CFUNCTYPE(C.c_int,P))]
RESIZE=C.CFUNCTYPE(C.c_int,P,C.c_int,C.c_int)
class UiResize(C.Structure):_fields_=[('handle',P),('resize',RESIZE)]
class DataAccess(C.Structure):_fields_=[('extension_data',C.CFUNCTYPE(P,C.c_char_p))]


class Lv2(PortPlugin):
    def __init__(self,bundle,identifier,rate):
        self.rate=rate;self.world=World(bundle);self.handles=[];self._editor=None
        try:
            self.meta=next((p for p in self.world.plugins() if p['id']==identifier),None)
            if self.meta is None:raise AudioError('The LV2 effect is missing from its bundle.')
            self.library=C.CDLL(self.meta['path']);self.library.lv2_descriptor.argtypes=[U];self.library.lv2_descriptor.restype=DP
            self.pointer=None
            for i in range(4096):
                candidate=self.library.lv2_descriptor(i)
                if not candidate:break
                if candidate.contents.uri.decode()==identifier:self.pointer=candidate;break
            if not self.pointer:raise AudioError('The LV2 descriptor is missing.')
            self.descriptor=self.pointer.contents
            self._uris={};self._uri_buffers={};self._keep=[]
            self.map_callback=MAP(lambda handle,uri:self.map_uri(uri.decode()))
            self.unmap_callback=UNMAP(lambda handle,key:C.addressof(self._uri_buffers[key]) if key in self._uri_buffers else None)
            self.urid_map=Map(None,self.map_callback);self.urid_unmap=Unmap(None,self.unmap_callback)
            self.features={URID+'map':C.addressof(self.urid_map),URID+'unmap':C.addressof(self.urid_unmap),
                'http://lv2plug.in/ns/ext/buf-size#boundedBlockLength':None}
            self.options=(Option*5)()
            for index,(key,value,kind) in enumerate((('http://lv2plug.in/ns/ext/buf-size#minBlockLength',1,C.c_int),
                    ('http://lv2plug.in/ns/ext/buf-size#maxBlockLength',1024,C.c_int),
                    ('http://lv2plug.in/ns/ext/buf-size#nominalBlockLength',1024,C.c_int),
                    ('http://lv2plug.in/ns/ext/parameters#sampleRate',rate,F))):
                data=kind(value);self._keep.append(data)
                self.options[index]=Option(0,0,self.map_uri(key),C.sizeof(data),self.map_uri(ATOM+('Float' if kind is F else 'Int')),C.addressof(data))
            self.features['http://lv2plug.in/ns/ext/options#options']=C.addressof(self.options)
            missing=set(self.meta['required'])-set(self.features)
            if missing:raise AudioError('Unsupported required LV2 features: '+', '.join(sorted(missing)))
            self.feature_list=self.make_features(self.features)
            ports=[]
            for data in self.meta['ports']:
                if data['kind']=='unsupported':raise AudioError('This LV2 effect requires an unsupported port type.')
                item=dict(data);item.pop('symbol');scale=rate if item.pop('sample_rate') else 1
                for key in ('low','high','default'):item[key]*=scale
                ports.append(Port(**item))
            self.initialize_ports(ports);self.latency_port=self.meta['latency_port']
            for _ in range(2 if len(self.inputs)==1 else 1):
                handle=self.descriptor.instantiate(self.pointer,rate,(self.meta['bundle']+'/').encode(),self.feature_list)
                if not handle:raise AudioError('LV2 initialization failed.')
                self.handles.append(handle);self.connect(handle)
                if self.descriptor.activate:self.descriptor.activate(handle)
        except Exception:self.close();raise

    def map_uri(self,uri):
        if uri not in self._uris:
            key=len(self._uris)+1
            if key>65536:raise AudioError('Too many LV2 URIs.')
            self._uris[uri]=key;self._uri_buffers[key]=C.create_string_buffer(uri.encode())
        return self._uris[uri]

    def make_features(self,values):
        records=[Feature(uri.encode(),data) for uri,data in values.items()];self._keep.extend(records)
        return (C.POINTER(Feature)*(len(records)+1))(*(C.pointer(r) for r in records),None)

    def state(self):
        data=json.loads(super().state());states=[];total=0
        interface=self.descriptor.extension_data((STATE+'interface').encode()) if self.descriptor.extension_data else None
        if interface:
            api=C.cast(interface,C.POINTER(StateInterface)).contents
            for handle in self.handles:
                properties={};errors=[]
                @STORE
                def store(context,key,value,size,type,flags):
                    nonlocal total
                    if not value or size<1 or size>MAX_STATE or total+size>MAX_STATE or flags&3!=3 or key not in self._uri_buffers or type not in self._uri_buffers:
                        errors.append('Unsupported LV2 state property.');return 2
                    name=self._uri_buffers[key].value.decode();kind=self._uri_buffers[type].value.decode()
                    if kind==ATOM+'Path':errors.append('LV2 state references an external file.');return 2
                    total+=size;properties[name]=dict(type=kind,flags=int(flags),data=base64.b64encode(C.string_at(value,size)).decode());return 0
                status=api.save(handle,store,None,3,self.feature_list)
                if status or errors:raise AudioError('The LV2 state cannot be saved completely: '+('; '.join(errors) or str(status)))
                states.append(properties)
        data['properties']=states
        result=json.dumps(data,allow_nan=False).encode()
        if len(result)>MAX_STATE:raise AudioError('Plug-in state exceeds 1 MiB.')
        return result

    def restore(self,state):
        for handle in self.handles:
            if self.descriptor.deactivate:self.descriptor.deactivate(handle)
        try:self._restore(state)
        finally:
            for handle in self.handles:
                if self.descriptor.activate:self.descriptor.activate(handle)

    def _restore(self,state):
        super().restore(state);data=json.loads(state);states=data.get('properties',[])
        if not states:return
        if len(states)!=len(self.handles):raise AudioError('LV2 state does not match its audio layout.')
        pointer=self.descriptor.extension_data((STATE+'interface').encode()) if self.descriptor.extension_data else None
        if not pointer:raise AudioError('The installed LV2 effect cannot restore the saved state.')
        interface=C.cast(pointer,C.POINTER(StateInterface)).contents
        for handle,properties in zip(self.handles,states):
            if not isinstance(properties,dict) or len(properties)>4096:raise AudioError('Invalid LV2 state properties.')
            buffers={}
            for name,item in properties.items():
                raw=base64.b64decode(item['data'],validate=True)
                if not raw or len(raw)>MAX_STATE or item['type']==ATOM+'Path' or item['flags']&3!=3:raise AudioError('Invalid LV2 state property.')
                buffers[self.map_uri(name)]=(C.create_string_buffer(raw),len(raw),self.map_uri(item['type']),item['flags'])
            @RETRIEVE
            def retrieve(context,key,size,type,flags):
                item=buffers.get(key)
                if item is None:return None
                buffer,count,kind,stored_flags=item;size[0]=count;type[0]=kind;flags[0]=stored_flags
                return C.addressof(buffer)
            if interface.restore(handle,retrieve,None,3,self.feature_list):raise AudioError('The LV2 effect rejected its saved state.')

    def close(self):
        self.close_editor();super().close()
        if getattr(self,'world',None):self.world.close();self.world=None

    def open_editor(self,parent,scale=1):
        self.close_editor()
        if not self.meta['uis']:raise AudioError('This LV2 effect has no X11 editor. Use its parameter controls.')
        from .plugin_x11 import X11
        self._editor_keep=[];features=dict(self.features)
        self._editor_size=(640,480)
        @WRITE
        def write(controller,index,size,protocol,data):
            port=self.controls.get(str(index))
            if protocol==0 and size==4 and port is not None and port.input and data:
                value=C.cast(data,C.POINTER(F))[0]
                if math.isfinite(value):port.value.value=min(port.high,max(port.low,value))
        @RESIZE
        def resize(handle,width,height):
            if not 16<=width<=8192 or not 16<=height<=8192:return 1
            self._editor_size=(width,height);return 0
        resize_feature=UiResize(None,resize);data_feature=DataAccess(self.descriptor.extension_data)
        self._editor_keep.extend((write,resize,resize_feature,data_feature))
        features.update({UI+'parent':parent,UI+'resize':C.addressof(resize_feature),UI+'idleInterface':None,
                         'http://lv2plug.in/ns/ext/data-access':C.addressof(data_feature)})
        if len(self.handles)==1:features['http://lv2plug.in/ns/ext/instance-access']=self.handles[0]
        choices=[ui for ui in self.meta['uis'] if not set(ui['required'])-set(features)]
        if not choices:raise AudioError('The LV2 editor requires unsupported host features. Use its parameter controls.')
        ui=choices[0];self.ui_library=C.CDLL(ui['path'])
        self.ui_library.lv2ui_descriptor.argtypes=[U];self.ui_library.lv2ui_descriptor.restype=UDP
        pointer=None
        for index in range(4096):
            item=self.ui_library.lv2ui_descriptor(index)
            if not item:break
            if item.contents.uri.decode()==ui['id']:pointer=item;break
        if not pointer:raise AudioError('The LV2 editor descriptor is missing.')
        self.ui_descriptor=pointer.contents;widget=P()
        self.ui_features=self.make_features(features)
        handle=self.ui_descriptor.instantiate(pointer,self.meta['id'].encode(),(ui['bundle']+'/').encode(),write,None,C.byref(widget),self.ui_features)
        if not handle:raise AudioError('The LV2 editor could not open. Use its parameter controls.')
        self._editor=handle;self._editor_window=widget.value;self._editor_x11=None
        try:
            if not widget.value:raise AudioError('The LV2 editor returned no window.')
            self._editor_x11=X11();size=self._editor_x11.size(widget.value)
            if size and 16<=size[0]<=8192 and 16<=size[1]<=8192:self._editor_size=size
            idle=self.ui_descriptor.extension_data((UI+'idleInterface').encode()) if self.ui_descriptor.extension_data else None
            self._editor_idle=C.cast(idle,C.POINTER(UiIdle)).contents if idle else None
            self._editor_values={};self.idle()
            return self._editor_size
        except Exception:self.close_editor();raise

    def editor_size(self):return getattr(self,'_editor_size',None) if self._editor is not None else None

    def resize_editor(self,width,height):
        if self._editor is not None and 16<=width<=8192 and 16<=height<=8192:
            self._editor_size=(width,height);self._editor_x11.resize(self._editor_window,width,height)

    def idle(self):
        if self._editor is not None:
            for key,port in self.controls.items():
                value=port.value.value
                if self._editor_values.get(key)!=value and self.ui_descriptor.port_event:
                    self.ui_descriptor.port_event(self._editor,port.index,4,0,C.byref(port.value));self._editor_values[key]=value
            if self._editor_idle is not None and self._editor_idle.idle(self._editor):self.close_editor()

    def close_editor(self):
        if getattr(self,'_editor',None) is not None:
            self.ui_descriptor.cleanup(self._editor);self._editor=None
            if self._editor_x11:self._editor_x11.close();self._editor_x11=None
