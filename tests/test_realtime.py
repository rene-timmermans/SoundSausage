"""Live/offline equivalence, bounded playback, rack persistence and duplex lifecycle."""
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QAudioFormat
from PySide6.QtTest import QTest

from soundsausage.session import Session
from soundsausage.document import Document
from soundsausage.trackfx import effect, chain, Processor, Rack
from soundsausage.mixing import SessionStream
from soundsausage.project import save_project, load_project
from soundsausage.recovery import Recovery, restore
from soundsausage.playback import Playback
from soundsausage.audio_devices import AudioDevices
from soundsausage.window import MainWindow
from soundsausage.trackfx_ui import TrackEffectsDialog, dialog_for, load_settings
from test_playback import Device, Sink, MemorySettings
from test_capture import Source


class RealtimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])

    def session(self):
        t=np.arange(12000)/8000
        self.data=np.column_stack((np.sin(2*np.pi*440*t),np.cos(2*np.pi*700*t))).astype(np.float32)*.2
        session=Session(8000,1);session.import_audio([(self.data,8000,'Reference')]);return session

    def test_every_stateful_track_effect_matches_offline_and_block_partition(self):
        settings=[('gain',dict(initial=(.5,.25))),('channel_mix',dict(matrix=((0,1),(1,0)))),
            ('dynamics',dict(points=((-96,-96),(-18,-18),(0,-9)),attack_ms=7,release_ms=90)),
            ('graphic_eq',dict(gains=(0,0,0,0,3,0,0,0,0,0))),
            ('parametric_eq',dict(bands=[dict(frequency=900,gain_db=3)])),
            ('filter',dict(kind='high_pass',frequency=120)),('delay',dict(delay_ms=13)),
            ('echo',dict(delay_ms=17,feedback=.4)),('reverb',dict(decay_seconds=.3)),('invert',{})]
        for kind,values in settings:
            with self.subTest(kind=kind):
                s=self.session();spec=effect(kind,values);s.configure_track(s.selected_track,effects=(spec,))
                reference=s.dsp.process_blocks(kind,self.data,8000,**values)
                np.testing.assert_array_equal(s.render(),reference)
                stream=SessionStream(s);parts=[]
                while stream.position<len(stream):parts.append(stream.read(377))
                stream.close();np.testing.assert_array_equal(np.concatenate(parts),reference)
                np.testing.assert_array_equal(next(iter(s.media.values())).samples,self.data)

    def test_live_gain_pan_solo_and_effect_changes_take_effect_without_restarting(self):
        s=self.session();stream=SessionStream(s)
        np.testing.assert_array_equal(stream.read(400),self.data[:400])
        s.configure_track(s.selected_track,effects=(effect('gain',dict(initial=.5)),),pan=1)
        actual=stream.read(400);np.testing.assert_array_equal(actual[:,0],0)
        np.testing.assert_array_equal(actual[:,1],self.data[400:800,1]*.5)
        s.configure_track(s.selected_track,muted=True);np.testing.assert_array_equal(stream.read(400),0)
        s.undo();self.assertTrue(np.any(stream.read(400)));stream.close()

    def test_chain_order_bypass_tail_and_undo(self):
        s=self.session();track=s.selected_track
        delay=effect('delay',dict(delay_ms=20,dry=0,wet=1))
        invert=effect('invert');s.configure_track(track,effects=(delay,invert),tail_seconds=.05)
        self.assertEqual(s.frames,len(self.data)+400)
        mixed=s.render();np.testing.assert_array_equal(mixed[:160],0)
        np.testing.assert_array_equal(mixed[160:len(self.data)+160],-self.data)
        s.configure_track(track,effects=(replace(delay,enabled=False),invert))
        np.testing.assert_array_equal(s.render()[:len(self.data)],-self.data)
        s.undo();np.testing.assert_array_equal(s.render(),mixed)
        s.redo();self.assertFalse(s.tracks[0].effects[0].enabled)
        with self.assertRaises(ValueError):chain([invert,invert])
        with self.assertRaises(ValueError):chain([effect('invert') for _ in range(17)])

    def test_project_and_recovery_keep_chain_order_bypass_and_exact_mix(self):
        s=self.session();s.configure_track(s.selected_track,effects=(effect('gain',dict(initial=.7)),effect('echo',dict(delay_ms=15)),effect('invert',enabled=False)),tail_seconds=.1)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'Session.celp';save_project(s,path);loaded=load_project(path)
            self.assertEqual(loaded.tracks,s.tracks);np.testing.assert_array_equal(loaded.render(),s.render())
        s.configure_track(s.selected_track,gain=.8);manager=Recovery()
        try:
            manager.checkpoint(Document(),s);_,recovered,_,_=restore(manager.owner)
            self.assertEqual(recovered.tracks,s.tracks);np.testing.assert_array_equal(recovered.render(),s.render())
        finally:manager.close()

    def test_streamed_playback_preserves_partial_pcm_writes_and_never_renders_whole_mix(self):
        s=self.session();s.configure_track(s.selected_track,effects=(effect('gain',dict(initial=.5)),))
        expected=s.render().tobytes();devices=AudioDevices(settings=MemorySettings())
        with patch.object(devices,'outputs',return_value=[Device()]),patch.object(devices,'inputs',return_value=[]):
            player=Playback(devices=devices,sink_factory=Sink);errors=[];player.failed.connect(errors.append)
            try:
                with patch.object(s,'render',side_effect=AssertionError('Full render during playback')):player.play_session(s)
                sink=player.sink;sink.write_limit=83;deadline=time.monotonic()+5
                while player.state!='Stopped' and time.monotonic()<deadline:
                    sink.drain();player._tick();QTest.qWait(1)
                self.assertEqual(player.state,'Stopped');self.assertFalse(errors)
                self.assertEqual(bytes(sink.received),expected)
            finally:player.shutdown();devices.deleteLater()

    def test_live_resampling_keeps_duration_and_finite_stereo_output(self):
        from soundsausage.streaming import converted_blocks
        s=self.session();stream=SessionStream(s)
        result=np.concatenate(list(converted_blocks(stream,48000,127)));stream.close()
        self.assertEqual(result.shape,(72000,2));self.assertTrue(np.isfinite(result).all())
        self.assertGreater(float(np.abs(result).max()),.19)

    def test_effect_editors_restore_existing_values_and_validate_racks(self):
        s=self.session();window=MainWindow(no_audio=True);window.session=s;window.set_mode('multitrack')
        dialogs=[]
        try:
            for kind in ('gain','channel_mix','dynamics','graphic_eq','parametric_eq','filter','delay','echo','reverb'):
                first=dialog_for(kind,s,window);dialogs.append(first)
                settings=first.settings();second=dialog_for(kind,s,window);dialogs.append(second)
                load_settings(second,kind,settings)
                self.assertEqual(second.settings(),settings,kind)
                Processor(effect(kind,settings),s.sample_rate,s.dsp).close()
            rack=TrackEffectsDialog(window.multitrack,s.selected_track);dialogs.append(rack)
            rack.commit((effect('invert'),));self.assertEqual(len(s.tracks[0].effects),1)
            rack.effects.item(0).setCheckState(__import__('PySide6.QtCore',fromlist=['Qt']).Qt.CheckState.Unchecked)
            self.assertFalse(s.tracks[0].effects[0].enabled)
            revision=s.revision;window._record_context={}
            with self.assertRaisesRegex(ValueError,'Stop recording'):rack.commit(())
            self.assertEqual(s.revision,revision);window._record_context=None
        finally:
            for dialog in dialogs:dialog.reject();dialog.deleteLater()
            s.mark_saved();window.document.mark_saved();window.close();window.deleteLater();self.app.processEvents()


class DuplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':self.folder.name});self.env.start()
        self.window=MainWindow(no_audio=False);w=self.window
        self.inp=patch.object(w.audio_devices,'inputs',return_value=[Device('Input',b'input')]);self.inp.start()
        self.out=patch.object(w.audio_devices,'outputs',return_value=[Device()]);self.out.start()
        w.recorder._source_factory=Source;w.player._sink_factory=Sink
        w.session=Session(48000,2);w.session.import_audio([(np.full((48000,2),.1,np.float32),48000,'Backing')])
        w.session.selected_track=w.session.tracks[1].id;w.set_mode('multitrack');w.session.select(4800,4800)
        self.err=patch.object(w,'error');self.errors=self.err.start()
    def tearDown(self):
        w=self.window;w.player.stop()
        if w.recorder.active:w.recorder.stop(keep=False)
        if w.recording_busy:w.end_recording_view()
        w.document.mark_saved();w.session.mark_saved();w.close();w.deleteLater();self.app.processEvents()
        self.err.stop();self.inp.stop();self.out.stop();self.env.stop();self.folder.cleanup()
    def test_overdub_pause_stop_offset_and_undo_preserve_backing(self):
        w=self.window;before=w.session.render();track=w.session.selected_track
        self.assertTrue(w.start_recording(target='multitrack',rate=48000,channels=1,accompaniment=True,recording_offset_ms=-10))
        self.assertEqual(w.player.state,'Playing')
        w.recorder.source.push(np.full((480,2),.3,np.float32).tobytes())
        w.toggle_pause();self.assertEqual((w.recorder.state,w.player.state),('Paused','Paused'))
        w.toggle_pause();self.assertEqual((w.recorder.state,w.player.state),('Recording','Playing'))
        w.stop_recording();self.assertEqual(w.player.state,'Stopped');self.assertFalse(w.recording_busy)
        clip=w.session.tracks[w.session.track_index(track)].clips[0]
        self.assertEqual(clip.start,4320);self.assertEqual(clip.frames,480)
        np.testing.assert_array_equal(w.session.media[clip.media_id].samples,np.float32(.3))
        w.session.undo();np.testing.assert_array_equal(w.session.render(),before);self.errors.assert_not_called()
    def test_output_failure_keeps_completed_take_and_missing_output_starts_no_input(self):
        w=self.window
        self.assertTrue(w.start_recording(target='multitrack',rate=48000,channels=2,accompaniment=True))
        w.recorder.source.push(np.full((100,2),.2,np.float32).tobytes())
        w.player._fail('Output disconnected')
        self.assertFalse(w.recording_busy);self.assertFalse(w.recorder.active)
        self.assertEqual(len(w.session.tracks[1].clips),1)
        with patch.object(w.audio_devices,'outputs',return_value=[]):
            self.assertFalse(w.start_recording(target='multitrack',rate=48000,channels=2,accompaniment=True))
        self.assertFalse(w.recorder.active)
