"""Non-destructive punch boundaries, crossfades, transactions and persistence."""
from dataclasses import replace
from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import numpy as np

from soundsausage.session import Session
from soundsausage.project import save_project,load_project
from soundsausage.recovery import Recovery,restore
from soundsausage.document import Document
from soundsausage.mixing import SessionStream


class PunchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()

    def tearDown(self):self.env.stop();self.temp.cleanup()

    def session(self):
        s=Session(8000,2)
        data=np.random.default_rng(8).normal(0,.1,(6000,2)).astype(np.float32)
        s.import_audio([(data,8000,'Original')],s.tracks[0].id,0)
        s.configure_clip(s.selected_clip,gain=.7,pan=-.3,fade_in=450,fade_out=1400,volume_envelope=((0,.4),(5999,1.3)))
        s.import_audio([(data,8000,'Overlap')],s.tracks[0].id,200)
        s.configure_clip(s.selected_clip,gain=.31)
        s.import_audio([(data,8000,'Other track')],s.tracks[1].id,0)
        return s,data

    def test_only_the_punch_window_changes_with_overlaps_fades_and_automation(self):
        s,source=self.session();before=s.render();tracks=s.tracks;count=len(s.undo_stack)
        media={k:m.samples.copy() for k,m in s.media.items()}
        new=np.full((2000,2),.3,np.float32)
        s.punch_audio(new,s.tracks[0].id,3000,fade_frames=40)
        after=s.render()
        np.testing.assert_array_equal(after[:3000],before[:3000]);np.testing.assert_array_equal(after[5000:],before[5000:])
        np.testing.assert_allclose(after[3040:4960],new[40:-40]+source[3040:4960],rtol=1e-7,atol=1e-8)
        for key,data in media.items():np.testing.assert_array_equal(s.media[key].samples,data)
        self.assertEqual(len(s.undo_stack),count+1)
        s.undo();self.assertEqual(s.tracks,tracks);np.testing.assert_array_equal(s.render(),before)
        s.redo();np.testing.assert_array_equal(s.render(),after)

    def test_equal_signals_crossfade_without_a_gap_and_regions_can_start_before_a_clip(self):
        s=Session(8000,1);source=np.full((2000,2),.25,np.float32);s.import_audio([(source,8000,'Constant')])
        s.punch_audio(source[:500],s.selected_track,500,fade_frames=40)
        np.testing.assert_allclose(s.render(),source,rtol=1e-7,atol=0)
        s=Session(8000,1);s.import_audio([(source,8000,'Late')],s.selected_track,100)
        s.punch_audio(np.full((150,2),.5,np.float32),s.selected_track,50,fade_frames=20)
        self.assertLess(s.tracks[0].clips[0].punch_ranges[0][0],0)
        np.testing.assert_array_equal(s.render(100,170),.5)

    def test_repeated_punches_project_and_recovery_keep_all_original_sources(self):
        s=Session(8000,1);source=np.full((2000,2),.25,np.float32);s.import_audio([(source,8000,'Original')])
        s.punch_audio(np.full((500,2),.1,np.float32),s.selected_track,500)
        s.punch_audio(np.full((400,2),-.25,np.float32),s.selected_track,800)
        expected=source.copy();expected[500:800]=.1;expected[800:1200]=-.25
        np.testing.assert_array_equal(s.render(),expected)
        path=self.path/'Punch.celp';save_project(s,path);opened=load_project(path)
        self.assertEqual(opened.tracks,s.tracks);np.testing.assert_array_equal(opened.render(),expected)
        s.configure_track(s.selected_track,gain=.9);expected=s.render()
        manager=Recovery()
        try:
            manager.checkpoint(Document(),s);_,recovered,_,_=restore(manager.owner)
            self.assertEqual(recovered.tracks,s.tracks);np.testing.assert_array_equal(recovered.render(),expected)
        finally:manager.close()

    def test_invalid_punch_is_atomic_and_old_audio_can_be_restored_after_reopening(self):
        s=Session(8000,1);source=np.full((1000,2),.25,np.float32);s.import_audio([(source,8000,'Original')])
        original=s.tracks;history=tuple(s.undo_stack);bank=set(s.media)
        for data,start,fade in ((np.empty((0,2),np.float32),0,0),(source,-1,0),(source,0,501)):
            with self.assertRaises(ValueError):s.punch_audio(data,s.selected_track,start,fade_frames=fade)
            self.assertEqual(s.tracks,original);self.assertEqual(tuple(s.undo_stack),history);self.assertEqual(set(s.media),bank)
        new=s.punch_audio(np.full((500,2),.5,np.float32),s.selected_track,100)
        s.configure_clip(new,muted=True)
        s.configure_clip(original[0].clips[0].id,punch_ranges=())
        np.testing.assert_array_equal(s.render(),source)

    def test_version_four_still_opens_and_invalid_punch_metadata_is_rejected(self):
        s=Session(8000,1);s.import_audio([(np.zeros((1000,2),np.float32),8000,'Original')])
        path=self.path/'Legacy.celp';save_project(s,path)
        with zipfile.ZipFile(path) as archive:files={name:archive.read(name) for name in archive.namelist()}
        manifest_name=next(n for n in files if n.endswith('.json'))
        manifest=json.loads(files[manifest_name]);manifest['version']=4
        for track in manifest['tracks']:
            for clip in track['clips']:clip.pop('punch_ranges',None)
        files[manifest_name]=json.dumps(manifest).encode()
        with zipfile.ZipFile(path,'w') as archive:
            for name,data in files.items():archive.writestr(name,data)
        np.testing.assert_array_equal(load_project(path).render(),s.render())
        manifest['version']=5;manifest['tracks'][0]['clips'][0]['punch_ranges']=[[10,9,0]]
        files[manifest_name]=json.dumps(manifest).encode()
        with zipfile.ZipFile(path,'w') as archive:
            for name,data in files.items():archive.writestr(name,data)
        with self.assertRaises(ValueError):load_project(path)

    def test_punch_playback_mutes_only_the_target_interval_without_editing_the_session(self):
        s=Session(8000,2);source=np.full((2000,2),.25,np.float32)
        for track in s.tracks:s.import_audio([(source,8000,'Backing')],track.id,0)
        before=s.render();tracks=s.tracks;revision=s.revision
        stream=SessionStream(s,punch=(s.tracks[0].id,500,1000,40))
        try:actual=stream.read(2000)
        finally:stream.close()
        np.testing.assert_array_equal(actual[:500],before[:500]);np.testing.assert_array_equal(actual[1000:],before[1000:])
        np.testing.assert_array_equal(actual[540:960],.25)
        self.assertEqual(s.tracks,tracks);self.assertEqual(s.revision,revision);np.testing.assert_array_equal(s.render(),before)
