"""Frame-exact marker edits, unchanged PCM and lossless marker storage paths."""
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
from mutagen.id3 import CHAP, CTOC, ID3, TIT2, TXXX

from soundsausage import markers, metadata, id3_metadata as id3
from soundsausage.audio import AudioError, read_wav, write_wav
from soundsausage.document import Document
from soundsausage.media import read_mp3, write_mp3
from soundsausage.project import save_project, load_project
from soundsausage.recovery import Recovery, restore
from soundsausage.session import Session


def subchunk(tag, data):
    return struct.pack('<4sI',tag,len(data))+data+(b'\0' if len(data)&1 else b'')


def chapters():
    tags=ID3()
    tags.add(TIT2(text=['Album title']))
    tags.add(TXXX(desc='replaygain_track_gain',text=['-6 dB']))
    tags.add(CHAP(element_id='a',start_time=1000,end_time=2000,
                  start_offset=123,end_offset=456,sub_frames=[TIT2(text=['Original chapter'])]))
    tags.add(CHAP(element_id='b',start_time=2500,end_time=id3.UNKNOWN))
    tags.add(CTOC(element_id='root',flags=3,child_element_ids=['a','b']))
    return ((b'id3 ',id3.dump(tags)),)


class MarkerTests(unittest.TestCase):
    def test_add_move_rename_remove_preserves_unknown_chunks_and_related_notes(self):
        info=((b'abcd',b'opaque payload'),)
        info,first=markers.add(info,48000,240000,100,'Intro é')
        info,second=markers.add(info,48000,240000,200,'Second')
        first_id=int(first.split(':')[1])
        note=subchunk(b'note',struct.pack('<I',first_id)+b'Keep note\0')
        unknown=subchunk(b'priv',b'opaque list field')
        info+=((b'LIST',b'adtl'+note+unknown),)
        before=info
        info=markers.edit(info,48000,240000,first,start=300,name='Renamed')
        items=markers.read(info,48000)
        self.assertEqual([(m.key,m.start,m.name) for m in items],[(second,200,'Second'),(first,300,'Renamed')])
        self.assertIn((b'abcd',b'opaque payload'),info)
        self.assertTrue(any(note in raw and unknown in raw for _,raw in info))
        info=markers.edit(info,48000,240000,first,remove=True)
        self.assertEqual([m.key for m in markers.read(info,48000)],[second])
        self.assertFalse(any(note in raw for _,raw in info))
        self.assertTrue(any(unknown in raw for _,raw in info))
        self.assertEqual(markers.read(before,48000)[0].name,'Intro é')

    def test_metadata_only_undo_keeps_pcm_selection_channel_and_original_id3(self):
        data=np.linspace(-.7,.7,24000,dtype=np.float32).reshape(-1,2)
        doc=Document(data,48000);doc.metadata=chapters()
        doc.select(100,700);doc.cursor=450;doc.select_channels((1,))
        source=doc._pieces[0];original=doc.metadata
        info,key=markers.add(original,doc.sample_rate,doc.frames,120,'Cue')
        doc.set_marker_metadata(info,'Add Marker')
        self.assertIs(doc._pieces[0],source)
        self.assertEqual((doc.selection,doc.cursor,doc.selected_channels),((100,700),450,(1,)))
        self.assertEqual(next(raw for kind,raw in doc.metadata if kind==b'id3 '),original[0][1])
        self.assertTrue(doc.dirty);self.assertEqual(len(doc.undo_stack),1)
        doc.undo();self.assertEqual(doc.metadata,original);self.assertFalse(doc.dirty)
        redo=tuple(doc.redo_stack)
        doc.set_marker_metadata(original,'No change');self.assertEqual(tuple(doc.redo_stack),redo)
        doc.redo();self.assertEqual(markers.for_model(doc)[0].key,key)
        np.testing.assert_array_equal(doc.read(),data)

    def test_invalid_positions_names_and_limits_are_rejected_without_mutation(self):
        info,key=markers.add((),48000,1000,100,'A')
        for values in [dict(start=-1),dict(start=1000),dict(start=True),dict(start=1.5),
                       dict(name='x'*257),dict(name='bad\nname'),dict(name='bad\x7fname'),dict(name='bad\x85name'),dict(end=500)]:
            with self.subTest(values=values),self.assertRaises(AudioError):
                markers.edit(info,48000,1000,key,**values)
        with self.assertRaises(AudioError):markers.add((),48000,2**32+2,2**32,'Too late')
        with patch.object(markers,'MAX_MARKERS',1),self.assertRaises(AudioError):
            markers.add(info,48000,1000,200,'B')
        with patch.object(markers,'MAX_METADATA_BYTES',10),self.assertRaises(AudioError):
            markers.edit(info,48000,1000,key,name='Another')
        self.assertEqual(markers.read(info,48000)[0].name,'A')

    def test_unsupported_and_duplicate_cues_remain_opaque_and_cannot_be_rewritten(self):
        good,_=markers.add((),8000,80000,400,'A')
        cue=next(raw for kind,raw in good if kind==b'cue ')
        duplicate=((b'cue ',struct.pack('<I',2)+cue[4:]*2),)
        noncanonical=bytearray(cue);noncanonical[12:16]=b'wavl'
        for info in [((b'cue ',b'bad'),),duplicate,((b'cue ',bytes(noncanonical)),)]:
            with self.subTest(info=info):
                self.assertEqual(markers.read(info,8000),())
                with self.assertRaises(AudioError):markers.add(info,8000,80000,300,'New')

    def test_existing_wav_character_set_is_honoured(self):
        info=((b'CSET',struct.pack('<4H',1252,0,0,0)),)
        info,key=markers.add(info,8000,80000,200,'Café')
        self.assertTrue(any(b'Caf\xe9\0' in raw for _,raw in info))
        self.assertEqual(markers.read(info,8000)[0].name,'Café')
        with self.assertRaises(AudioError):markers.edit(info,8000,80000,key,name='🎵')

    def test_chapter_name_preserves_offsets_measurements_and_submillisecond_move_is_noop(self):
        info=chapters();key='chapter:0:a'
        renamed=markers.edit(info,48000,192000,key,name='New chapter')
        tags=id3.load(renamed[0][1]);chapter=tags['CHAP:a']
        self.assertEqual((chapter.start_time,chapter.end_time,chapter.start_offset,chapter.end_offset),(1000,2000,123,456))
        self.assertEqual(str(chapter.sub_frames['TIT2']),'New chapter')
        self.assertTrue(tags.getall('TXXX:replaygain_track_gain'))
        self.assertIs(markers.edit(info,48000,192000,key,start=48001),info)
        moved=markers.move(renamed,48000,192000,key,72000)
        chapter=id3.load(moved[0][1])['CHAP:a']
        self.assertEqual((chapter.start_time,chapter.end_time),(1500,2500))
        self.assertEqual((chapter.start_offset,chapter.end_offset),(id3.UNKNOWN,id3.UNKNOWN))

    def test_chapter_delete_cleans_toc_and_invalid_range_is_rejected(self):
        info=chapters()
        for values in [dict(end=48000),dict(start=144000,end=96000),dict(end=192001)]:
            with self.assertRaises(AudioError):markers.edit(info,48000,192000,'chapter:0:a',**values)
        updated=markers.edit(info,48000,192000,'chapter:0:a',remove=True)
        tags=id3.load(updated[0][1]);self.assertNotIn('CHAP:a',tags)
        self.assertEqual(tags['CTOC:root'].child_element_ids,['b'])
        self.assertEqual(str(tags['TIT2']),'Album title')

    def test_waveform_timeline_edits_keep_cues_aligned_and_partial_channel_keeps_time(self):
        doc=Document(np.zeros((8000,2),np.float32),8000)
        for frame in (1000,3000,6000):doc.metadata,_=markers.add(doc.metadata,8000,8000,frame,str(frame))
        doc.select(2000,4000);doc.delete()
        self.assertEqual([(m.name,m.start) for m in markers.for_model(doc)],[('1000',1000),('6000',4000)])
        doc.undo();doc.select_channels((0,));doc.select(2000,4000);doc.delete()
        self.assertEqual([m.start for m in markers.for_model(doc)],[1000,3000,6000])
        doc.undo();doc.select_channels(None);doc.select(0,doc.frames);doc.apply('reverse')
        self.assertEqual([(m.name,m.start) for m in markers.for_model(doc)],[('6000',1999),('3000',4999),('1000',6999)])
        doc.undo();doc.convert_sample_rate(16000)
        self.assertEqual([m.start for m in markers.for_model(doc)],[2000,6000,12000])

    def test_wav_cues_convert_to_unique_mp3_chapters_and_keep_existing_hierarchy(self):
        info=chapters()
        for frame,name in [(0,'Start'),(24000,'Half second'),(48000,'One second')]:
            info,_=markers.add(info,48000,192000,frame,name)
        tags,omitted=id3.export_tags(info,sample_rate=48000,frames=192000)
        self.assertFalse(omitted)
        self.assertEqual(len(tags.getall('CHAP')),5)
        self.assertEqual(str(tags['CHAP:ss-cue-0'].sub_frames['TIT2']),'Start')
        self.assertEqual((tags['CHAP:ss-cue-0'].start_time,tags['CHAP:ss-cue-0'].end_time),(0,500))
        self.assertEqual(tags['CTOC:root'].child_element_ids,['a','b'])
        elements=[f for kind in ('CHAP','CTOC') for f in tags.getall(kind)]
        names={f.element_id for f in elements}
        self.assertEqual(len(elements),len(names))
        self.assertEqual(sum(bool(f.flags&2) for f in tags.getall('CTOC')),1)
        self.assertTrue(all(child in names for f in tags.getall('CTOC') for child in f.child_element_ids))

    def test_large_cue_export_has_bounded_toc_groups_and_reports_unhandled_notes(self):
        records=b''.join(struct.pack('<II4sIII',i,i*100,b'data',0,0,i*100) for i in range(300))
        info=((b'cue ',struct.pack('<I',300)+records),)
        info+=((b'LIST',b'adtl'+subchunk(b'note',struct.pack('<I',0)+b'Unmapped note\0')),)
        tags,omitted=id3.export_tags(info,sample_rate=48000,frames=48000)
        self.assertEqual(len(tags.getall('CHAP')),300)
        self.assertIn('LIST',omitted)
        self.assertTrue(all(len(t.child_element_ids)<=255 for t in tags.getall('CTOC')))


class MarkerStorageTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'cache')});self.env.start()
        self.data=np.column_stack((.2*np.sin(np.arange(96000)*.11),.1*np.cos(np.arange(96000)*.13))).astype(np.float32)
        self.info=()
        for frame,name in [(0,'Begin'),(24000,'Couplet é'),(72000,'Einde')]:
            self.info,_=markers.add(self.info,48000,len(self.data),frame,name)
    def tearDown(self):self.env.stop();self.folder.cleanup()

    def test_wav_and_real_mp3_reopen_names_and_timing(self):
        wav=self.path/'markers.wav';mp3=self.path/'markers.mp3'
        write_wav(wav,self.data,48000,'float32',metadata=self.info)
        audio=read_wav(wav);np.testing.assert_array_equal(audio.samples,self.data)
        self.assertEqual(markers.read(audio.metadata,48000),markers.read(self.info,48000))
        write_mp3(mp3,audio.samples,48000,metadata=audio.metadata)
        reopened=read_mp3(mp3)
        self.assertEqual([(m.name,m.start) for m in markers.read(reopened.metadata,48000)],
                         [('Begin',0),('Couplet é',24000),('Einde',72000)])

    def test_session_undo_project_and_recovery_preserve_global_and_source_markers(self):
        session=Session(48000,1);ids=session.import_audio([(self.data,48000,'Audio',self.info)])
        original=session.media[session.tracks[0].clips[0].media_id]
        information,key=markers.add((),48000,session.marker_frames,10000,'Session')
        session.select(300,800);session.cursor=500;clip=session.selected_clip
        session.set_marker_metadata(information,'Add Marker')
        self.assertEqual((session.selection,session.cursor,session.selected_clip),((300,800),500,clip))
        self.assertIs(session.media[original.id],original)
        session.undo();self.assertEqual(session.metadata,())
        session.redo();self.assertEqual(session.metadata,information)
        path=self.path/'session.celp';save_project(session,path)
        restored=load_project(path)
        self.assertEqual(restored.metadata,information)
        self.assertEqual(restored.media[original.id].metadata,self.info)
        session.move_clip(ids[0],start=4000)
        self.assertEqual(markers.for_model(session)[0].start,10000)
        recovery=Recovery()
        try:
            recovery.checkpoint(Document(self.data,48000),session,'multitrack')
            _,recovered,_,_=restore(recovery.owner)
            self.assertEqual(recovered.metadata,information)
        finally:recovery.close()

    def test_old_projects_still_open_and_invalid_global_metadata_is_rejected(self):
        session=Session(48000,1);session.import_audio([(self.data,48000,'Audio')])
        source=self.path/'source.celp';save_project(session,source)
        with zipfile.ZipFile(source) as archive:files={n:archive.read(n) for n in archive.namelist()}
        manifest=json.loads(files['project.json'])
        def project(version,info):
            manifest['version']=version;manifest['metadata']=info
            target=self.path/'changed.celp'
            with zipfile.ZipFile(target,'w') as archive:
                for name,data in files.items():archive.writestr(name,json.dumps(manifest).encode() if name=='project.json' else data)
            return target
        self.assertEqual(load_project(project(5,[])).metadata,())
        for info in [None,[['data','AAAA']],[['cue ','%%%']],metadata.encode(self.info)]:
            version=5 if info==metadata.encode(self.info) else 6
            with self.subTest(info=info),self.assertRaises(AudioError):load_project(project(version,info))

    def test_version_two_recovery_reads_without_global_metadata_and_rejects_injection(self):
        doc=Document(self.data,48000);doc.apply('invert')
        session=Session(48000,1);session.import_audio([(self.data,48000,'Audio')])
        manager=Recovery()
        try:
            manager.checkpoint(doc,session)
            record=json.loads(manager.path.read_text());record['version']=2
            record['session'].pop('metadata')
            manager.path.write_text(json.dumps(record))
            recovered,recovered_session,_,_=restore(manager.owner)
            np.testing.assert_array_equal(recovered.view(),doc.view())
            np.testing.assert_array_equal(recovered_session.render(),session.render())
            self.assertEqual(recovered_session.metadata,())
            record['session']['metadata']=metadata.encode(self.info)
            manager.path.write_text(json.dumps(record))
            with self.assertRaises(AudioError):restore(manager.owner)
        finally:manager.close()
