"""Disk-backed edits, block continuity, cancellation and metadata regression tests."""
import gc
import io
import json
import os
import subprocess
import sys
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import storage, peaks, metadata
from soundsausage.audio import AudioError, read_wav, write_wav, wav_header
from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.resample import resample
from soundsausage.session import Session
from soundsausage.project import save_project,load_project

ROOT=Path(__file__).resolve().parents[1]


def cues(*positions):
    return ((b'cue ',struct.pack('<I',len(positions))+b''.join(struct.pack('<II4sIII',i,p,b'data',0,0,p) for i,p in enumerate(positions))),)


def positions(chunks):
    raw=dict(chunks)[b'cue ']
    return [struct.unpack_from('<I',raw,4+i*24+20)[0] for i in range(struct.unpack_from('<I',raw)[0])]


class StorageTests(unittest.TestCase):
    def test_long_workflow_keeps_resident_memory_bounded(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            result=subprocess.run([sys.executable,str(ROOT/'tools/check_large_audio_memory.py')],
                cwd=ROOT,env={**os.environ,'SOUNDSAUSAGE_CACHE_DIR':folder,'PYTHONPATH':str(ROOT/'src')},
                capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout)
            self.assertLess(max(report['extra_resident_mib'].values()),80)

    def test_copied_markers_get_fresh_ids_and_mix_paste_keeps_original_markers(self):
        doc=Document(np.zeros((10,1),np.float32),8000)
        doc.metadata=cues(2,8)
        doc.select(4,10);clip=doc.copy()
        doc.select(0,0);doc.paste(clip)
        self.assertEqual(positions(doc.metadata),[8,14,4])
        raw=dict(doc.metadata)[b'cue ']
        self.assertEqual([struct.unpack_from('<I',raw,4+i*24)[0] for i in range(3)],[0,1,2])
        doc.undo();self.assertEqual(positions(doc.metadata),[2,8])
        doc.select(0,10);clip=doc.copy();doc.select(5,5);doc.paste(clip,mix=True)
        self.assertEqual(positions(doc.metadata),[2,8,7,13])

    def test_cue_at_fractional_resampled_tail_stays_inside_waveform(self):
        doc=Document(np.ones((101,1),np.float32),8000);doc.metadata=cues(100)
        doc.convert_sample_rate(1000)
        self.assertEqual(positions(doc.metadata),[12]);self.assertEqual(doc.frames,13)

    def test_shared_maps_live_until_all_owners_release_them(self):
        original=storage.seal(storage.copy_array(np.full((1000,2),.125,np.float32),force_disk=True))
        path=storage.lease_of(original).path
        copy=storage.open_buffer(path,original.shape)
        del original;gc.collect()
        self.assertTrue(path.exists())
        np.testing.assert_array_equal(copy,.125)
        del copy;gc.collect()
        self.assertFalse(path.exists())

    def test_long_waveform_roundtrip_edit_undo_and_project_above_old_limit(self):
        frames=17*1024*1024  # 136 MiB decoded stereo, above the old 128 MiB guard.
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            folder=Path(folder)
            source=storage.allocate((frames,2),zero=True)
            source[0]=[-.5,.25];source[262143]=[.75,-.125];source[-1]=[1.25,-1.5]
            source=storage.seal(source)
            path=folder/'long.wav'
            write_wav(path,source,48000,'float32',metadata=cues(262143,frames-1))
            audio=read_wav(path)
            self.assertIsInstance(audio.samples,np.memmap)
            self.assertFalse(audio.samples.flags.writeable)
            doc=Document(audio.samples,48000)
            doc.metadata=audio.metadata
            doc.apply('gain',initial=.5)
            self.assertEqual(len(doc.undo_stack),1)
            self.assertEqual(Document._storage_bytes([doc._snapshot(''),*doc.undo_stack]),0)
            np.testing.assert_array_equal(doc.view()[-1],[.625,-.75])
            doc.undo();np.testing.assert_array_equal(doc.view()[-1],[1.25,-1.5])
            doc.redo();np.testing.assert_array_equal(doc.view()[262143],[.375,-.0625])
            session=Session(48000,1)
            session.import_audio([(doc.view(),48000,'Long recording',doc.metadata)])
            project=folder/'long.celp';save_project(session,project)
            reopened=load_project(project)
            np.testing.assert_array_equal(next(iter(reopened.media.values())).samples[-1],[.625,-.75])
            self.assertEqual(positions(next(iter(reopened.media.values())).metadata),[262143,frames-1])
            np.testing.assert_array_equal(reopened.render(frames-2,frames)[-1],[.625,-.75])

    def test_every_amplitude_processor_is_independent_of_chunk_boundaries(self):
        random=np.random.default_rng(44)
        data=random.uniform(-.8,.9,(2403,2)).astype(np.float32)
        dsp=Dsp()
        cases=[('gain',dict(initial=[.1,2],final=[1.7,.2])),
               ('gain',dict(initial=.01,final=2,logarithmic=True)),
               ('envelope',dict(points=((0,.1),(.23,1.9),(.62,.2),(1,1)))),
               ('envelope',dict(points=((0,.1),(1,1.8)),logarithmic=True)),
               ('dynamics',dict(points=((-96,-96),(-18,-18),(0,-12)),attack_ms=3,release_ms=17)),
               ('normalize',dict(target=.9,linked=True,remove_dc=True)),
               ('normalize',dict(target=.75,linked=False)),
               ('channel_mix',dict(matrix=((.5,.25),(-.4,.7)))),
               ('reverse',{}),('invert',{}),('silence',{})]
        for name,settings in cases:
            expected=data.copy();dsp.process(name,expected,48000,**settings)
            for block in (1,37,256,10000):
                with self.subTest(name=name,block=block):
                    actual=dsp.process_blocks(name,data,48000,block_frames=block,**settings)
                    np.testing.assert_allclose(actual,expected,atol=1e-7,rtol=1e-6)
                    preview=dsp.process_blocks(name,data,48000,limit=91,block_frames=block,**settings)
                    np.testing.assert_allclose(preview,expected[:91],atol=1e-7,rtol=1e-6)

    def test_stateful_resampling_matches_whole_stream_at_tiny_block_sizes(self):
        data=np.random.default_rng(6).uniform(-.1,.1,(1021,2)).astype(np.float32)
        for old,new in ((44100,48000),(48000,8000),(1000,48000)):
            expected=resample(data,old,new)
            for block in (7,31,1024):
                np.testing.assert_allclose(resample(data,old,new,block_frames=block),expected,atol=1e-7,rtol=1e-6)

    def test_cancelled_edit_and_save_keep_audio_selection_history_and_file(self):
        doc=Document(np.ones((600000,2),np.float32),48000)
        doc.apply('invert');doc.undo()
        doc.select(12,599999)
        state=(doc._pieces,doc.selection,doc.cursor,list(doc.undo_stack),list(doc.redo_stack),doc.last_effect,doc.revision)
        def cancel(done,total,label):
            return done==0
        with operation(cancel),self.assertRaises(OperationCancelled):
            doc.apply('dynamics',points=((-96,-96),(0,0)))
        self.assertEqual((doc._pieces,doc.selection,doc.cursor,doc.undo_stack,doc.redo_stack,doc.last_effect,doc.revision),state)
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            path=Path(folder)/'keep.wav';path.write_bytes(b'previous')
            with operation(cancel),self.assertRaises(OperationCancelled):
                write_wav(path,doc.view(),48000)
            self.assertEqual(path.read_bytes(),b'previous')
            self.assertEqual(list(path.parent.iterdir()),[path])

    def test_cancellation_while_preparing_result_waveform_is_still_atomic(self):
        with patch.object(storage,'MEMORY_THRESHOLD',128):
            doc=Document(np.ones((3000,2),np.float32),48000)
            original=doc._pieces
            with operation(lambda done,total,label:label!='Golfvorm voorbereiden'),self.assertRaises(OperationCancelled):
                doc.apply('gain',initial=.5)
            self.assertIs(doc._pieces,original)
            self.assertEqual(doc.undo_stack,[]);self.assertIsNone(doc.last_effect)

    def test_cancelled_project_save_keeps_target_and_unsaved_state(self):
        session=Session(48000,1)
        session.import_audio([(np.ones((3000,2),np.float32),48000,'Recording')])
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            path=Path(folder)/'keep.celp';path.write_bytes(b'previous project')
            with operation(lambda done,total,label:not(label=='WAV opslaan' and done>0)),self.assertRaises(OperationCancelled):
                save_project(session,path)
            self.assertEqual(path.read_bytes(),b'previous project')
            self.assertTrue(session.dirty);self.assertIsNone(session.path)
            self.assertEqual(list(path.parent.iterdir()),[path])

    def test_disk_full_is_reported_before_creating_a_buffer(self):
        with patch('soundsausage.storage.shutil.disk_usage') as usage:
            usage.return_value.free=100
            with self.assertRaisesRegex(AudioError,'free disk'):
                storage.allocate((10000,2),force_disk=True)

    def test_metadata_cues_follow_delete_trim_reverse_resample_and_undo(self):
        doc=Document(np.zeros((100,1),np.float32),8000)
        doc.metadata=cues(5,25,50,90)
        doc.select(20,40);doc.delete()
        self.assertEqual(positions(doc.metadata),[5,30,70])
        doc.undo();self.assertEqual(positions(doc.metadata),[5,25,50,90])
        doc.select(20,80);doc.trim()
        self.assertEqual(positions(doc.metadata),[5,30])
        doc.apply('reverse');self.assertEqual(positions(doc.metadata),[54,29])
        doc.convert_sample_rate(16000);self.assertEqual(positions(doc.metadata),[108,58])
        doc.undo();self.assertEqual(positions(doc.metadata),[54,29])

    def test_wav_metadata_roundtrip_keeps_text_cue_labels_and_broadcast_reference(self):
        bext=bytearray(602);struct.pack_into('<Q',bext,338,123456)
        label=b'labl'+struct.pack('<I',8)+struct.pack('<I',0)+b'One\0'
        info=((b'LIST',b'INFOINAM\x06\0\0\0Title\0'),(b'bext',bytes(bext)),(b'LIST',b'adtl'+label))+cues(10,50)
        data=np.zeros((80,1),np.float32)
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            path=Path(folder)/'meta.wav'
            write_wav(path,data,8000,'float32',metadata=info)
            audio=read_wav(path);self.assertEqual(audio.metadata,info)
            cropped=metadata.crop(info,20,70)
            self.assertEqual(positions(cropped),[30])
            self.assertEqual([raw for kind,raw in cropped if kind==b'LIST' and raw[:4]==b'adtl'],[b'adtl'])
            ref,=struct.unpack_from('<Q',dict(cropped)[b'bext'],338)
            self.assertEqual(ref,123476)

    def test_metadata_limit_rejects_open_instead_of_silently_losing_duplicate_chunks(self):
        import io
        raw=io.BytesIO()
        from soundsausage.audio import write_stream
        write_stream(raw,np.ones((2,1),np.float32),8000,metadata=((b'LIST',b'INFO'),(b'LIST',b'adtl')))
        with patch('soundsausage.audio.MAX_METADATA_BYTES',4),self.assertRaisesRegex(AudioError,'metadata'):
            read_wav(raw)

    def test_rf64_header_uses_64_bit_sizes_and_small_rf64_file_reads(self):
        header=wav_header(2**30,2,48000,'float32')
        self.assertEqual(header[:4],b'RF64')
        self.assertEqual(struct.unpack_from('<Q',header,28)[0],2**33)
        small=wav_header(3,1,8000,'float32')
        size=len(small)+12+36-8
        rf64=b'RF64\xff\xff\xff\xffWAVEds64'+struct.pack('<IQQQI',28,size,12,3,0)+small[12:-4]+b'\xff\xff\xff\xff'+np.ones((3,1),np.float32).tobytes()
        np.testing.assert_array_equal(read_wav(io.BytesIO(rf64)).samples,1)

    def test_large_peak_pyramid_is_exact_for_views_and_split_pieces(self):
        data=np.random.default_rng(7).uniform(-1,1,(4099,2)).astype(np.float32)
        with patch.object(storage,'MEMORY_THRESHOLD',128):
            doc=Document(data,8000)
            for start,end,columns in ((0,4099,83),(17,3899,101),(99,141,200),(301,333,7)):
                actual=peaks.piece_peaks(doc._slices(start,end),end-start,2,columns)
                if end-start>=columns:
                    edges=np.linspace(start,end,columns+1,dtype=np.int64)
                    expected=(np.minimum.reduceat(data[start:end],edges[:-1]-start,axis=0),np.maximum.reduceat(data[start:end],edges[:-1]-start,axis=0))
                    np.testing.assert_array_equal(actual[0],expected[0]);np.testing.assert_array_equal(actual[1],expected[1])
            doc.select(150,800);doc.delete()
            expected=np.concatenate((data[:150],data[800:]))
            actual=peaks.piece_peaks(doc._pieces,doc.frames,2,99)
            edges=np.linspace(0,len(expected),100,dtype=np.int64)[:-1]
            np.testing.assert_array_equal(actual[0],np.minimum.reduceat(expected,edges,axis=0))
            np.testing.assert_array_equal(actual[1],np.maximum.reduceat(expected,edges,axis=0))


if __name__=='__main__':unittest.main()
