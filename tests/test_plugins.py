"""An independent VST3 binary exercises discovery, ABI, state and process isolation."""
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication

from soundsausage.plugins import scan_plugin, PluginProcess, read_registry
from soundsausage.trackfx import effect
from soundsausage.session import Session
from soundsausage.project import save_project,load_project
from soundsausage.mixing import SessionStream
from soundsausage.plugins_ui import PluginDialog
from soundsausage.document import Document
from soundsausage.recovery import Recovery,restore

ROOT=Path(__file__).resolve().parents[1]


class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.binary=ROOT/'build/vst3-test-gain.so'
        subprocess.run(['c++','-std=c++20','-O2','-fPIC','-shared','-Ithird_party/vst3',
            'tests/fixtures/vst3_gain.cpp','third_party/vst3/pluginterfaces/base/funknown.cpp','-o',str(cls.binary)],cwd=ROOT,check=True)
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_PLUGIN_REGISTRY':str(self.path/'registry.json'),
                                      'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
        self.entry=scan_plugin(self.binary)[0]
        self.settings=dict(plugin_id=self.entry['id'],name=self.entry['name'],fingerprint=self.entry['fingerprint'],values={'0':.25})
    def tearDown(self):self.env.stop();self.folder.cleanup()

    def test_bundle_scan_metadata_and_stereo_audio_cross_real_vst3_abi(self):
        bundle=self.path/'Gain.vst3/Contents/x86_64-linux';bundle.mkdir(parents=True)
        shutil.copy2(self.binary,bundle/'Gain.so');entry=scan_plugin(bundle.parents[1])[0]
        self.assertEqual(entry['name'],'SoundSausage Test Gain')
        processor=PluginProcess(self.settings,48000)
        try:
            data=np.arange(6000,dtype=np.float32).reshape(3000,2)/10000
            actual=data.copy();processor.process(actual);np.testing.assert_array_equal(actual,data*.5)
            self.assertEqual(processor.info['parameters'][0]['name'],'Gain')
        finally:processor.close()

    def test_parameter_and_component_state_survive_helper_restart_project_and_recovery(self):
        processor=PluginProcess(self.settings,8000)
        try:snapshot=processor.snapshot()
        finally:processor.close()
        self.assertTrue(snapshot['state'])
        # Restore only binary component state, without replaying parameter values.
        saved=dict(self.settings,state=snapshot['state'],values={})
        processor=PluginProcess(saved,8000)
        try:
            data=np.ones((27,2),np.float32);processor.process(data);np.testing.assert_array_equal(data,.5)
        finally:processor.close()
        s=Session(8000,1);s.import_audio([(np.full((2000,2),.2,np.float32),8000,'Source')])
        s.configure_track(s.selected_track,effects=(effect('plugin',saved),))
        path=self.path/'Project.celp';save_project(s,path);opened=load_project(path)
        self.assertEqual(opened.tracks,s.tracks);np.testing.assert_array_equal(opened.render(),s.render())
        s.configure_track(s.selected_track,gain=.75);manager=Recovery()
        try:
            manager.checkpoint(Document(),s);_,recovered,_,_=restore(manager.owner)
            self.assertEqual(recovered.tracks,s.tracks);np.testing.assert_array_equal(recovered.render(),s.render())
        finally:manager.close()

    def test_live_parameter_updates_reuse_the_helper_and_leave_source_unmodified(self):
        s=Session(8000,1);source=np.full((4096,2),.25,np.float32);s.import_audio([(source,8000,'Source')])
        spec=effect('plugin',self.settings);s.configure_track(s.selected_track,effects=(spec,))
        stream=SessionStream(s)
        try:
            np.testing.assert_array_equal(stream.read(1024),.125)
            helper=stream.racks[s.selected_track].processors[spec.id].plugin.helper.process.pid
            settings=dict(self.settings,values={'0':.75});s.configure_track(s.selected_track,effects=(effect('plugin',settings,key=spec.id),))
            np.testing.assert_array_equal(stream.read(1024),.375)
            self.assertEqual(stream.racks[s.selected_track].processors[spec.id].plugin.helper.process.pid,helper)
            np.testing.assert_array_equal(next(iter(s.media.values())).samples,source)
        finally:stream.close()

    def test_crashing_and_hanging_plugin_stops_only_the_helper(self):
        for key in ('3','4'):
            with self.subTest(parameter=key):
                settings=dict(self.settings,values={'0':.25,key:1})
                processor=PluginProcess(settings,8000)
                try:
                    with self.assertRaises(ValueError):processor.process(np.ones((16,2),np.float32))
                    self.assertIsNotNone(processor.helper.process.poll())
                finally:processor.close()
        safe=PluginProcess(self.settings,8000)
        try:
            data=np.ones((2,2),np.float32);safe.process(data);np.testing.assert_array_equal(data,.5)
        finally:safe.close()

    def test_missing_or_changed_plugin_is_not_executed_or_silently_bypassed(self):
        s=Session(8000,1);s.import_audio([(np.ones((100,2),np.float32),8000,'Source')])
        s.configure_track(s.selected_track,effects=(effect('plugin',self.settings),))
        path=self.path/'Project.celp';save_project(s,path);(self.path/'registry.json').unlink()
        opened=load_project(path);self.assertEqual(opened.tracks,s.tracks)
        with self.assertRaisesRegex(ValueError,'Missing plug-in'):opened.render()
        self.assertEqual(opened.frames,100)
        self.entry=scan_plugin(self.binary)[0]
        altered=dict(self.settings,fingerprint='0'*64)
        with self.assertRaisesRegex(ValueError,'differs'):PluginProcess(altered,8000)
        disabled=replace(opened.tracks[0].effects[0],enabled=False)
        opened.configure_track(opened.selected_track,effects=(disabled,));np.testing.assert_array_equal(opened.render(),1)

    def test_generic_parameter_editor_saves_applied_value_and_binary_state(self):
        s=Session(8000,1);dialog=PluginDialog(s,saved=self.settings)
        try:
            self.assertEqual(dialog.parameter.currentText(),'Gain');self.assertEqual(dialog.value.value(),25)
            dialog.value.setValue(75);settings=dialog.settings()
            self.assertEqual(settings['values']['0'],.75);self.assertTrue(settings['state'])
        finally:dialog.close_processor();dialog.reject();dialog.deleteLater();self.app.processEvents()

    def test_unregistered_project_cannot_supply_an_executable_path(self):
        with self.assertRaisesRegex(ValueError,'Unknown plug-in setting'):
            PluginProcess(dict(self.settings,path=str(self.binary)),8000)
        broken=self.path/'broken.so';broken.write_text('not a shared object')
        with self.assertRaises(ValueError):scan_plugin(broken)
        self.assertEqual(list(read_registry()),[self.entry['id']])
