"""Independent LADSPA/LV2 ABIs, mono pairing, native state and delay alignment."""
import base64
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage.plugins import scan_plugin,PluginProcess
from soundsausage.trackfx import effect
from soundsausage.session import Session
from soundsausage.mixing import SessionStream
from soundsausage.project import save_project,load_project

ROOT=Path(__file__).resolve().parents[1]
URI='urn:soundsausage:test:lv2:gain'
TTL='''@prefix lv2: <http://lv2plug.in/ns/lv2core#> .
@prefix doap: <http://usefulinc.com/ns/doap#> .
@prefix urid: <http://lv2plug.in/ns/ext/urid#> .
<urn:soundsausage:test:lv2:gain> a lv2:Plugin ; doap:name "SoundSausage LV2 fixture" ;
 lv2:requiredFeature urid:map ; lv2:port
 [ a lv2:InputPort,lv2:AudioPort;lv2:index 0;lv2:symbol "in";lv2:name "Input" ],
 [ a lv2:OutputPort,lv2:AudioPort;lv2:index 1;lv2:symbol "out";lv2:name "Output" ],
 [ a lv2:InputPort,lv2:ControlPort;lv2:index 2;lv2:symbol "gain";lv2:name "Gain";lv2:minimum 0;lv2:maximum 2;lv2:default 1 ],
 [ a lv2:OutputPort,lv2:ControlPort;lv2:index 3;lv2:symbol "latency";lv2:name "Latency";lv2:minimum 0;lv2:maximum 1024;
   lv2:portProperty lv2:reportsLatency,lv2:integer;lv2:designation lv2:latency ],
 [ a lv2:InputPort,lv2:ControlPort;lv2:index 4;lv2:symbol "delay";lv2:name "Delay";lv2:minimum 0;lv2:maximum 28;lv2:default 7;lv2:portProperty lv2:integer ] .
'''


class LinuxPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary=ROOT/'build/linux-test-gain.so'
        subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','tests/fixtures/linux_gain.c','-ldl','-o',str(cls.binary)],cwd=ROOT,check=True)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_PLUGIN_REGISTRY':str(self.path/'registry.json'),'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
        self.bundle=self.path/'Gain.lv2';self.bundle.mkdir();shutil.copy2(self.binary,self.bundle/'gain.so')
        (self.bundle/'manifest.ttl').write_text('''@prefix lv2: <http://lv2plug.in/ns/lv2core#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<urn:soundsausage:test:lv2:gain> a lv2:Plugin;lv2:binary <gain.so>;rdfs:seeAlso <gain.ttl> .\n''')
        (self.bundle/'gain.ttl').write_text(TTL)

    def tearDown(self):self.env.stop();self.temp.cleanup()

    def settings(self,format):
        path=self.bundle if format=='LV2' else self.binary
        e=scan_plugin(path,format)[0]
        return dict(plugin_id=e['id'],name=e['name'],fingerprint=e['fingerprint'],values={'2':.25})

    def test_discovery_mono_pairing_parameter_mapping_and_independent_stereo_history(self):
        source=np.column_stack((np.arange(200)/1000,np.arange(200)[::-1]/2000)).astype(np.float32)
        for format in ('LADSPA','LV2'):
            with self.subTest(format=format):
                p=PluginProcess(self.settings(format),8000)
                try:
                    out=source.copy();p.process(out)
                    np.testing.assert_array_equal(out[:7],0)
                    np.testing.assert_array_equal(out[7:],source[:-7]*.5)
                    self.assertEqual(p.info['latency'],7)
                    params={str(item['id']):item for item in p.info['parameters']}
                    self.assertEqual(params['2']['value'],.25);self.assertTrue(params['3']['readonly'])
                    with self.assertRaises(ValueError):p.helper.request(dict(op='parameters',values={'3':.5}))
                    with self.assertRaises(ValueError):p.helper.request(dict(op='parameters',values={'2':float('inf')}))
                finally:p.close()

    def test_live_and_export_compensate_chains_bypass_and_the_last_sample(self):
        source=np.zeros((1500,2),np.float32);source[[0,13,1499]]=(.4,-.2)
        for format in ('LADSPA','LV2'):
            with self.subTest(format=format):
                settings=self.settings(format);s=Session(8000,2)
                for track in s.tracks:s.import_audio([(source,8000,'Impulse')],track.id,0)
                specs=(effect('plugin',settings),effect('plugin',settings))
                s.configure_track(s.tracks[0].id,effects=specs)
                np.testing.assert_allclose(s.render(),source*1.25,rtol=1e-7,atol=0)
                stream=SessionStream(s);parts=[]
                try:
                    while stream.position<len(stream):parts.append(stream.read(127))
                    self.assertEqual(stream.pipes[s.tracks[0].id].delay,14)
                finally:stream.close()
                np.testing.assert_array_equal(np.concatenate(parts),s.render())
                from dataclasses import replace
                s.configure_track(s.tracks[0].id,effects=(specs[0],replace(specs[1],enabled=False)))
                np.testing.assert_allclose(s.render(),source*1.5,rtol=1e-7,atol=0)

    def test_live_change_of_reported_delay_preserves_logical_timeline(self):
        settings=self.settings('LADSPA');s=Session(8000,1)
        source=np.arange(4000,dtype=np.float32)[:,None]/10000
        source=np.concatenate((source,-source),axis=1);s.import_audio([(source,8000,'Ramp')])
        first=effect('plugin',settings);s.configure_track(s.selected_track,effects=(first,))
        stream=SessionStream(s)
        try:
            np.testing.assert_array_equal(stream.read(211),source[:211]*.5)
            newer=dict(settings,values={'2':.25,'4':.5})
            s.configure_track(s.selected_track,effects=(effect('plugin',newer,key=first.id),))
            np.testing.assert_array_equal(stream.read(211),source[211:422]*.5)
            self.assertEqual(stream.pipes[s.selected_track].delay,14)
        finally:stream.close()

    def test_native_lv2_properties_survive_restart_and_project_roundtrip(self):
        settings=self.settings('LV2');p=PluginProcess(settings,8000)
        try:snapshot=p.snapshot()
        finally:p.close()
        state=json.loads(base64.b64decode(snapshot['state']))
        self.assertEqual(len(state['properties']),2)
        for props in state['properties']:props['urn:soundsausage:test:hidden']['data']=base64.b64encode(struct.pack('f',.5)).decode()
        saved=dict(settings,values={},state=base64.b64encode(json.dumps(state).encode()).decode())
        s=Session(8000,1);source=np.ones((100,2),np.float32)*.25;s.import_audio([(source,8000,'State')])
        s.configure_track(s.selected_track,effects=(effect('plugin',saved),))
        np.testing.assert_array_equal(s.render(),source*.25)
        path=self.path/'State.celp';save_project(s,path);opened=load_project(path)
        np.testing.assert_array_equal(opened.render(),s.render())

    def test_changed_metadata_and_unsupported_features_are_not_silently_accepted(self):
        settings=self.settings('LV2');path=self.bundle/'gain.ttl'
        path.write_text(TTL+'\n# changed\n')
        with self.assertRaisesRegex(ValueError,'differs'):PluginProcess(settings,8000)
        path.write_text(TTL.replace('lv2:requiredFeature urid:map','lv2:requiredFeature <urn:soundsausage:unsupported>'))
        changed=self.settings('LV2')
        with self.assertRaisesRegex(ValueError,'Unsupported required LV2'):PluginProcess(changed,8000)

    def test_applying_opaque_state_while_playing_keeps_compensated_audio_aligned(self):
        settings=self.settings('LV2');p=PluginProcess(settings,8000)
        try:state=json.loads(base64.b64decode(p.snapshot()['state']))
        finally:p.close()
        for props in state['properties']:props['urn:soundsausage:test:hidden']['data']=base64.b64encode(struct.pack('f',.5)).decode()
        saved=dict(settings,state=base64.b64encode(json.dumps(state).encode()).decode())
        s=Session(8000,1);source=np.ones((1000,2),np.float32)*.25;s.import_audio([(source,8000,'State')])
        spec=effect('plugin',settings);s.configure_track(s.selected_track,effects=(spec,));stream=SessionStream(s)
        try:
            np.testing.assert_array_equal(stream.read(211),source[:211]*.5)
            s.configure_track(s.selected_track,effects=(effect('plugin',saved,key=spec.id),))
            np.testing.assert_array_equal(stream.read(211),source[211:422]*.25)
        finally:stream.close()

    @unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_PLUGIN_UI_TEST')=='1','Native LV2 X11 check is enabled on distribution runners.')
    def test_native_lv2_window_uses_port_callbacks_resize_and_saved_controls(self):
        path=self.bundle/'gain.ttl'
        path.write_text(TTL+"""
@prefix ui: <http://lv2plug.in/ns/extensions/ui#> .
<urn:soundsausage:test:lv2:gain> ui:ui <urn:soundsausage:test:lv2:ui> .
<urn:soundsausage:test:lv2:ui> a ui:X11UI;ui:binary <gain.so>;
 lv2:requiredFeature ui:parent,ui:resize .
""")
        settings=self.settings('LV2');processor=PluginProcess(settings,8000)
        try:
            processor.open_editor();deadline=time.monotonic()+4
            while time.monotonic()<deadline:
                snapshot=processor.snapshot()
                if snapshot['editor_size']==[400,220] and snapshot['info']['parameters'][0]['value']==.75:break
                time.sleep(.02)
            self.assertEqual(snapshot['editor_size'],[400,220])
            self.assertEqual(snapshot['info']['parameters'][0]['value'],.75)
            processor.close_editor();self.assertIsNone(processor.snapshot()['editor_size'])
            saved=dict(settings,values={},state=snapshot['state'])
        finally:processor.close()
        restored=PluginProcess(saved,8000)
        try:
            data=np.ones((100,2),np.float32);restored.process(data)
            np.testing.assert_array_equal(data[7:],1.5)
        finally:restored.close()
