"""Finished-mix recovery: controlled pumping, unchanged timing and safe commits."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import markers, remaster, storage
from soundsausage.audio import read_wav, write_wav
from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation


def pumping(rate=16000, seconds=4, ducked=True):
    t=np.arange(round(rate*seconds))/rate
    kick=np.zeros(len(t));envelope=np.ones(len(t))
    for beat in np.arange(1,seconds-.25,.5):
        tau=t-beat;active=(tau>=0)&(tau<.3)
        kick[active]+=.5*np.sin(2*np.pi*70*tau[active])*np.exp(-tau[active]/.045)
        if ducked:envelope[active]*=1-.65*np.exp(-tau[active]/.11)
    harmonic=.2*np.sin(2*np.pi*887*t)*envelope
    return np.column_stack((harmonic+kick,.8*harmonic+.8*kick)).astype(np.float32)


def tone_level(data,rate,start,stop,frequency=887):
    a,b=round(start*rate),round(stop*rate)
    return 2*abs(np.mean(data[a:b,0]*np.exp(-2j*np.pi*frequency*np.arange(a,b)/rate)))


class RemasterTests(unittest.TestCase):
    def test_reduces_controlled_drum_ducking_without_changing_stereo_ratio(self):
        source=pumping();before=source.copy()
        result=remaster.process_blocks('remaster',source,16000,ceiling_db=0)
        def dip(data):return 20*np.log10(tone_level(data,16000,2.04,2.12)/tone_level(data,16000,1.88,1.96))
        self.assertLess(dip(source),-3)
        self.assertGreater(dip(result)-dip(source),1.5)
        self.assertLess(dip(result),0)
        np.testing.assert_allclose(result[:,1],result[:,0]*.8,atol=2e-7)
        np.testing.assert_array_equal(source,before)
        self.assertEqual(result.shape,source.shape)
        self.assertFalse(result.flags.writeable)

    def test_steady_tone_does_not_receive_false_pumping_recovery(self):
        rate=16000;t=np.arange(rate*3)/rate
        source=(.2*np.sin(2*np.pi*887*t))[:,None].astype(np.float32)
        result=remaster.process_blocks('remaster',source,rate)
        np.testing.assert_allclose(result[rate//2:-rate//2],source[rate//2:-rate//2],atol=2e-5)

    def test_drum_hits_without_ducking_leave_sustained_tone_stable(self):
        source=pumping(ducked=False);result=remaster.process_blocks('remaster',source,16000)
        before=tone_level(source,16000,2.04,2.12);after=tone_level(result,16000,2.04,2.12)
        self.assertLess(abs(20*np.log10(after/before)),.2)

    def test_bass_only_is_not_boosted(self):
        rate=16000;t=np.arange(rate*3)/rate
        source=(.3*np.sin(2*np.pi*70*t)*(1+.5*np.sin(2*np.pi*2*t)))[:,None].astype(np.float32)
        result=remaster.process_blocks('remaster',source,rate,amount=100,recovery_db=9)
        self.assertLess(abs(20*np.log10(tone_level(result,rate,.5,2.5,70)/tone_level(source,rate,.5,2.5,70))),.01)

    def test_zero_amount_or_recovery_only_applies_constant_headroom(self):
        source=pumping()*3
        for settings in ({'amount':0},{'recovery_db':0}):
            result=remaster.process_blocks('remaster',source,16000,**settings)
            target=source*(10**(-1/20)/np.max(abs(source)))
            np.testing.assert_allclose(result,target,atol=2e-7)

    def test_full_analysis_preview_and_block_sizes_produce_the_same_audio(self):
        source=pumping(seconds=2.5)
        full=remaster.process_blocks('remaster',source,16000,block_frames=1)
        other=remaster.process_blocks('remaster',source,16000,block_frames=262144)
        preview=remaster.process_blocks('remaster',source,16000,limit=7000,block_frames=2048)
        np.testing.assert_allclose(full,other,atol=3e-7)
        np.testing.assert_allclose(preview,full[:7000],atol=3e-7)

    def test_silence_short_ranges_rates_and_high_finite_input(self):
        for rate,frames in ((1000,1),(8000,63),(44100,2049),(192000,8193),(384000,5)):
            source=np.zeros((frames,2),np.float32)
            result=remaster.process_blocks('remaster',source,rate)
            np.testing.assert_array_equal(source,result)
        source=pumping(seconds=2)*np.float32(1e30)
        result=remaster.process_blocks('remaster',source,16000,ceiling_db=-3)
        self.assertTrue(np.isfinite(result).all())
        self.assertLessEqual(np.max(abs(result)),10**(-3/20)+1e-7)
        self.assertGreater(np.max(abs(result)),.5)
        empty=remaster.process_blocks('remaster',source,16000,limit=0)
        self.assertEqual(empty.shape,(0,2))

    def test_invalid_parameters_and_audio_are_rejected(self):
        source=pumping(seconds=1)
        for settings in ({'amount':101},{'recovery_db':-1},{'release_ms':0},{'ceiling_db':1},{'sensitivity_db':float('nan')},{'block_frames':0}):
            with self.assertRaises(ValueError):remaster.process_blocks('remaster',source,16000,**settings)
        for data in (np.zeros(2),np.zeros((2,3)),np.full((2,1),float('nan')),np.full((2,2),float('inf'))):
            with self.assertRaises(ValueError):remaster.process_blocks('remaster',data,16000)
        with self.assertRaises(ValueError):remaster.process_blocks('unknown',source,16000)

    def test_cancelling_analysis_or_render_leaves_document_and_undo_untouched(self):
        source=pumping(seconds=2)
        for target in ('Remaster analysis','Recovering musical detail','Setting output headroom'):
            doc=Document(source,16000);doc.select(1000,20000)
            with operation(lambda done,total,label:label!=target):
                with self.assertRaises(OperationCancelled):doc.apply('remaster')
            np.testing.assert_array_equal(doc.read(),source)
            self.assertEqual(doc.selection,(1000,20000));self.assertEqual(doc.undo_stack,[])

    def test_selected_channel_range_markers_undo_and_repeat(self):
        source=pumping(seconds=3);doc=Document(source,16000)
        doc.metadata,_=markers.add((),16000,doc.frames,18000,'Verse')
        info=doc.metadata;doc.select(8000,40000);doc.select_channels((1,))
        doc.apply('remaster')
        after=doc.read().copy()
        np.testing.assert_array_equal(after[:,0],source[:,0])
        np.testing.assert_array_equal(after[:8000],source[:8000])
        np.testing.assert_array_equal(after[40000:],source[40000:])
        self.assertGreater(np.max(abs(after[8000:40000,1]-source[8000:40000,1])),.001)
        self.assertEqual(doc.metadata,info);self.assertEqual(doc.frames,len(source))
        self.assertEqual(doc.last_effect,('remaster',{}))
        doc.undo();np.testing.assert_array_equal(doc.read(),source)
        doc.redo();np.testing.assert_array_equal(doc.read(),after)

    def test_disk_buffers_and_lossless_roundtrip(self):
        source=pumping(seconds=2)
        with patch.object(storage,'MEMORY_THRESHOLD',1024):
            result=remaster.process_blocks('remaster',source,16000)
            self.assertIsInstance(result,np.memmap)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'remaster.wav'
            write_wav(path,result,16000,encoding='float32')
            np.testing.assert_array_equal(read_wav(path).samples,result)
