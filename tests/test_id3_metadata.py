from pathlib import Path
import os
import struct
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from mutagen.id3 import ID3, CHAP, CTOC, TIT2, TPE1, TXXX, COMM, APIC, RVA2, SYLT, TBPM, TKEY
from PySide6.QtWidgets import QApplication, QMessageBox

from soundsausage import metadata, id3_metadata as id3
from soundsausage.audio import AudioError, read_wav, write_wav
from soundsausage.document import Document
from soundsausage.media import read_mp3, write_mp3
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled
from soundsausage.project import save_project, load_project
from soundsausage.recovery import Recovery, restore
from soundsausage.session import Session
from soundsausage.window import MainWindow


ROOT = Path(__file__).resolve().parents[1]
RATE = 8000


def chunks():
    tags = ID3()
    tags.add(TIT2(encoding=3, text=['Original title']))
    tags.add(TPE1(encoding=3, text=['Artist']))
    tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=b'original image'))
    tags.add(TXXX(encoding=3, desc='REPLAYGAIN_TRACK_GAIN', text=['-8 dB']))
    tags.add(TXXX(encoding=3, desc='replaygain_album_peak', text=['.9']))
    tags.add(TXXX(encoding=3, desc='MP3GAIN_MINMAX', text=['80,120']))
    tags.add(TXXX(encoding=3, desc='MusicBrainz Album Id', text=['keep this identity']))
    tags.add(COMM(encoding=3, lang='eng', desc='iTunNORM', text=['obsolete volume']))
    tags.add(COMM(encoding=3, lang='eng', desc='Notes', text=['Keep the comment']))
    tags.add(RVA2(desc='track', channel=1, gain=-8, peak=.9))
    tags.add(SYLT(encoding=3, lang='eng', format=2, type=1, desc='lyrics', text=[('word', 1000)]))
    for i, name in enumerate(('a', 'b', 'c')):
        tags.add(CHAP(element_id=name, start_time=i*1000, end_time=(i+1)*1000,
                      start_offset=100+i*100, end_offset=200+i*100,
                      sub_frames=[TIT2(encoding=3, text=[name.upper()])]))
    tags.add(CTOC(element_id='root', flags=3, child_element_ids=['a','b','c']))
    return ((b'id3 ', id3.dump(tags)),)


def tags_of(info):
    return id3.load(next(raw for kind, raw in info if kind.lower()==b'id3 '), strict=True)


def times(info):
    return {c.element_id:(c.start_time,c.end_time) for c in tags_of(info).getall('CHAP')}


def info_chunk(**values):
    raw=b'INFO'
    for name, text in values.items():
        data=text.encode('utf-8')+b'\0'
        raw+=name.encode('ascii')+struct.pack('<I',len(data))+data+b'\0'*(len(data)&1)
    return b'LIST',raw


class ChapterTests(unittest.TestCase):
    def setUp(self):
        self.doc=Document(np.zeros((RATE*4,2),np.float32),RATE)
        self.doc.metadata=chunks()

    def test_audio_changes_remove_measurements_but_preserve_text_cover_and_undo(self):
        doc=self.doc; original=doc.metadata
        doc.set_sample(10,1,.25)
        tags=tags_of(doc.metadata)
        self.assertEqual(str(tags['TIT2']),'Original title')
        self.assertEqual(tags.getall('APIC')[0].data,b'original image')
        self.assertEqual(str(tags['TXXX:MusicBrainz Album Id']),'keep this identity')
        self.assertEqual(tags.getall('RVA2'),[]);self.assertEqual(tags.getall('SYLT'),[])
        self.assertFalse(any('replaygain' in key.casefold() or 'mp3gain' in key.casefold() for key in tags))
        self.assertFalse(tags.getall('COMM:iTunNORM'))
        self.assertTrue(tags.getall('COMM:Notes'))
        self.assertEqual(str(tags['TLEN']),'4000')
        self.assertTrue(all(c.start_offset==c.end_offset==id3.UNKNOWN for c in tags.getall('CHAP')))
        changed=doc.metadata;doc.undo();self.assertEqual(doc.metadata,original)
        doc.redo();self.assertEqual(doc.metadata,changed)
        doc.undo();doc.set_sample(10,1,0)
        self.assertEqual(doc.metadata,original);self.assertEqual(len(doc.redo_stack),1)

    def test_delete_clamps_chapters_and_removes_empty_entries_and_toc_links(self):
        doc=self.doc;doc.select(RATE,2*RATE);doc.delete()
        self.assertEqual(times(doc.metadata),{'a':(0,1000),'c':(1000,2000)})
        self.assertEqual(tags_of(doc.metadata).getall('CTOC')[0].child_element_ids,['a','c'])
        doc.undo();doc.select(RATE//2,3*RATE//2);doc.delete()
        self.assertEqual(times(doc.metadata),{'a':(0,500),'b':(500,1000),'c':(1000,2000)})

    def test_insert_keeps_left_boundary_and_shifts_the_next_chapter(self):
        self.doc.replace(RATE,RATE,np.zeros((RATE//4,2),np.float32))
        self.assertEqual(times(self.doc.metadata),{'a':(0,1000),'b':(1250,2250),'c':(2250,3250)})

    def test_crop_keeps_overlapping_chapters_relative_to_selection(self):
        result=metadata.crop(self.doc.metadata,RATE//2,5*RATE//2,sample_rate=RATE)
        self.assertEqual(times(result),{'a':(0,500),'b':(500,1500),'c':(1500,2000)})
        self.assertEqual(str(tags_of(result)['TLEN']),'2000')
        self.doc.select(RATE//2,5*RATE//2);self.doc.trim()
        self.assertEqual(self.doc.metadata,result)

    def test_reverse_reorders_chapters_and_discards_disjoint_partial_ranges(self):
        doc=self.doc;doc.select(0,3*RATE);doc.apply('reverse')
        self.assertEqual(times(doc.metadata),{'a':(2000,3000),'b':(1000,2000),'c':(0,1000)})
        self.assertEqual(tags_of(doc.metadata).getall('CTOC')[0].child_element_ids,['c','b','a'])
        doc.undo();doc.select(RATE//2,3*RATE//2);doc.apply('reverse')
        self.assertEqual(times(doc.metadata),{'c':(2000,3000)})

    def test_stretch_and_tail_use_interval_boundaries_instead_of_sample_centres(self):
        doc=self.doc;doc.select(RATE//2,3*RATE//2)
        with patch.object(doc,'preview_effect',return_value=np.zeros((RATE*2,2),np.float32)):
            doc.apply('stretch',time_ratio=2)
        self.assertEqual(times(doc.metadata),{'a':(0,1500),'b':(1500,3000),'c':(3000,4000)})
        doc.undo();doc.select(0,RATE)
        with patch.object(doc,'preview_effect',return_value=np.zeros((RATE+RATE//4,2),np.float32)):
            doc.apply('echo',tail_seconds=.25)
        self.assertEqual(times(doc.metadata),{'a':(0,1000),'b':(1250,2250),'c':(2250,3250)})

    def test_samplerate_conversion_preserves_millisecond_positions(self):
        before=times(self.doc.metadata)
        self.doc.convert_sample_rate(16000)
        self.assertEqual(times(self.doc.metadata),before)
        self.assertEqual(str(tags_of(self.doc.metadata)['TLEN']),'4000')

    def test_tempo_and_key_are_only_invalidated_by_corresponding_effects(self):
        doc=self.doc;tags=tags_of(doc.metadata)
        tags.add(TBPM(text=['120']));tags.add(TKEY(text=['C']))
        doc.metadata=((b'id3 ',id3.dump(tags)),)
        doc.apply('gain',initial=.5)
        self.assertEqual(str(tags_of(doc.metadata)['TBPM']),'120')
        self.assertEqual(str(tags_of(doc.metadata)['TKEY']),'C')
        doc.undo()
        with patch.object(doc,'preview_effect',return_value=np.zeros((RATE*8,2),np.float32)):
            doc.apply('stretch',time_ratio=2)
        self.assertFalse(tags_of(doc.metadata).getall('TBPM'))
        self.assertEqual(str(tags_of(doc.metadata)['TKEY']),'C')
        doc.undo()
        with patch.object(doc,'preview_effect',return_value=np.zeros((RATE*4,2),np.float32)):
            doc.apply('pitch_shift',semitones=12)
        self.assertEqual(str(tags_of(doc.metadata)['TBPM']),'120')
        self.assertFalse(tags_of(doc.metadata).getall('TKEY'))
        doc.undo()
        with patch.object(doc,'preview_effect',return_value=np.zeros((RATE*8,2),np.float32)):
            doc.apply('stretch',time_ratio=2,semitones=12)
        self.assertFalse(tags_of(doc.metadata).getall('TBPM'))
        self.assertFalse(tags_of(doc.metadata).getall('TKEY'))

    def test_paste_chapters_assigns_unique_ids_and_retains_both_hierarchies(self):
        self.doc.select(RATE,2*RATE);source=self.doc.copy()
        self.doc.select(3*RATE,3*RATE);self.doc.paste(source)
        tags=tags_of(self.doc.metadata);chapters=tags.getall('CHAP')
        imported=[c for c in chapters if c.element_id not in ('a','b','c')]
        self.assertEqual(len(imported),1)
        self.assertEqual((imported[0].start_time,imported[0].end_time),(3000,4000))
        self.assertEqual(str(imported[0].sub_frames['TIT2']),'B')
        self.assertEqual(str(tags['TIT2']),'Original title')
        elements=[c for name in ('CHAP','CTOC') for c in tags.getall(name)]
        names={c.element_id for c in elements}
        self.assertEqual(len(names),len(elements))
        self.assertEqual(sum(bool(c.flags&2) for c in tags.getall('CTOC')),1)
        self.assertTrue(all(child in names for c in tags.getall('CTOC') for child in c.child_element_ids))

    def test_toc_cycles_missing_ids_and_dead_branches_are_pruned(self):
        tags=ID3();tags.add(CHAP(element_id='a',start_time=0,end_time=1000))
        tags.add(CTOC(element_id='x',flags=3,child_element_ids=['y','missing']))
        tags.add(CTOC(element_id='y',flags=1,child_element_ids=['x','a']))
        tags.add(CTOC(element_id='empty',flags=0,child_element_ids=['missing']))
        id3.clean_toc(tags)
        self.assertEqual(tags['CTOC:x'].child_element_ids,['y'])
        self.assertEqual(tags['CTOC:y'].child_element_ids,['a'])
        self.assertNotIn('CTOC:empty',tags)

    def test_pasting_many_chapters_builds_tables_with_at_most_255_children(self):
        tags=ID3()
        for i in range(300):
            tags.add(CHAP(element_id=str(i),start_time=i,end_time=i+1))
        result=id3.paste_chapters((),((b'id3 ',id3.dump(tags)),),0,RATE)
        updated=tags_of(result)
        self.assertEqual(len(updated.getall('CHAP')),300)
        self.assertEqual(sum(bool(table.flags&2) for table in updated.getall('CTOC')),1)
        self.assertTrue(all(1<=len(table.child_element_ids)<=255 for table in updated.getall('CTOC')))

    def test_measurements_inside_chapters_are_invalidated_too(self):
        tags=tags_of(chunks());tags['CHAP:a'].sub_frames.add(TXXX(desc='replaygain_track_peak',text=['1']))
        tags['CHAP:a'].sub_frames.add(APIC(desc='replaygain_track_peak',data=b'chapter cover'))
        id3.sanitise(tags,4*RATE,RATE)
        self.assertEqual(tags['CHAP:a'].sub_frames.getall('TXXX'),[])
        self.assertEqual(tags['CHAP:a'].sub_frames.getall('APIC')[0].data,b'chapter cover')

    def test_unknown_or_submillisecond_chapters_and_empty_document(self):
        tags=ID3()
        tags.add(CHAP(element_id='unknown',start_time=1000,end_time=id3.UNKNOWN))
        tags.add(CHAP(element_id='invalid',start_time=id3.UNKNOWN,end_time=id3.UNKNOWN))
        info=((b'id3 ',id3.dump(tags)),)
        cropped=metadata.crop(info,RATE//2,2*RATE,sample_rate=RATE)
        self.assertEqual(times(cropped),{'unknown':(500,1500)})
        tiny_tags=ID3();tiny_tags.add(CHAP(element_id='tiny',start_time=0,end_time=1))
        tiny=((b'id3 ',id3.dump(tiny_tags)),)
        self.assertEqual(tags_of(metadata.crop(tiny,0,2,sample_rate=RATE)).getall('CHAP'),[])
        self.doc.select(0,self.doc.frames);self.doc.delete()
        self.assertEqual(tags_of(self.doc.metadata).getall('CHAP'),[])
        self.assertEqual(tags_of(self.doc.metadata).getall('CTOC'),[])
        self.assertEqual(str(tags_of(self.doc.metadata)['TLEN']),'0')

    def test_metadata_failure_during_commit_is_atomic(self):
        before=self.doc.metadata
        with patch('soundsausage.id3_metadata.dump',side_effect=AudioError('metadata too large')):
            with self.assertRaises(AudioError):self.doc.set_sample(0,0,.5)
        self.assertEqual(self.doc.metadata,before);self.assertFalse(self.doc.undo_stack)
        self.assertEqual(np.count_nonzero(self.doc.read()),0)

    def test_cancelling_metadata_processing_preserves_audio_metadata_and_history(self):
        before=self.doc.metadata
        with self.assertRaises(OperationCancelled),operation(lambda done,total,label:False):
            self.doc.set_sample(10,0,.5)
        self.assertEqual(self.doc.metadata,before);self.assertFalse(self.doc.undo_stack)
        self.assertEqual(np.count_nonzero(self.doc.read()),0)


class MetadataExportTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build');self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
    def tearDown(self):self.env.stop();self.folder.cleanup()

    def test_info_fields_preserve_original_id3_and_report_unknown_conflicts(self):
        info=chunks()+(info_chunk(INAM='Different title',ICMT='Different notes',ICOP='Copyright',ZZZZ='private'),)
        tags,omitted=id3.export_tags(info)
        self.assertEqual(str(tags['TIT2']),'Original title')
        self.assertEqual(str(tags['TCOP']),'Copyright')
        self.assertEqual(omitted,{'LIST/INFO/INAM','LIST/INFO/ICMT','LIST/INFO/ZZZZ'})
        _,duplicate=id3.export_tags(chunks()+chunks())
        self.assertEqual(duplicate,{'ID3/2'})

    def test_known_info_values_utf8_dates_and_malformed_subchunks(self):
        tags,omitted=id3.export_tags((info_chunk(INAM='Één lied',IART='Artist',IPRD='Album',IGNR='Rock',ICRD='2026',ITRK='2',ICOP='Rights',ICMT='Note',ISFT='old encoder'),))
        self.assertFalse(omitted)
        self.assertEqual(str(tags['TIT2']),'Één lied');self.assertEqual(str(tags['TDRC']),'2026')
        self.assertEqual(tags.getall('COMM')[0].text,['Note'])
        latin=((b'LIST',b'INFOINAM'+struct.pack('<I',2)+b'\xe9\0'),)
        self.assertEqual(str(id3.export_tags(latin)[0]['TIT2']),'é')
        _,bad=id3.export_tags(((b'LIST',b'INFOINAM'+struct.pack('<I',100)+b'x'),))
        self.assertEqual(bad,{'LIST/INFO'})
        _,invalid_date=id3.export_tags((info_chunk(ICRD='not a date'),))
        self.assertEqual(invalid_date,{'LIST/INFO/ICRD'})

    def test_real_mp3_export_keeps_chapters_and_cover_and_updates_encoder_details(self):
        source=chunks();target=self.path/'chapter.mp3'
        write_mp3(target,np.zeros((RATE*4,2),np.float32),RATE,metadata=source)
        tags=ID3(target)
        self.assertEqual(str(tags['TIT2']),'Original title')
        self.assertEqual(tags.getall('APIC')[0].data,b'original image')
        self.assertEqual(tags['CHAP:b'].start_time,1000)
        self.assertEqual(tags['CHAP:b'].start_offset,id3.UNKNOWN)
        self.assertFalse(tags.getall('RVA2'));self.assertFalse(tags.getall('SYLT'))
        self.assertFalse(tags.getall('TXXX:REPLAYGAIN_TRACK_GAIN'))
        self.assertTrue(tags.getall('TSSE'));self.assertEqual(str(tags['TLEN']),'4000')
        self.assertEqual(tags_of(read_mp3(target).metadata)['CHAP:b'].start_time,1000)
        self.assertTrue(tags_of(source).getall('RVA2'))  # Export never mutates the source document.

    def test_real_wav_info_export_without_id3_roundtrips_text(self):
        target=self.path/'info.mp3'
        write_mp3(target,np.zeros((16000,1),np.float32),RATE,
                  metadata=(info_chunk(INAM='Title',IART='Artist',ICMT='Comment',ICRD='2026'),))
        tags=ID3(target)
        self.assertEqual(str(tags['TIT2']),'Title');self.assertEqual(str(tags['TPE1']),'Artist')
        self.assertEqual(str(tags['TDRC']),'2026');self.assertEqual(tags.getall('COMM')[0].text,['Comment'])

    def test_wav_and_project_keep_transformed_chapters(self):
        doc=Document(np.zeros((32000,2),np.float32),RATE);doc.metadata=chunks()
        doc.select(RATE//2,5*RATE//2);doc.trim()
        wave=self.path/'trim.wav';write_wav(wave,doc.view(),RATE,'float32',metadata=doc.metadata)
        self.assertEqual(times(read_wav(wave).metadata),times(doc.metadata))
        session=Session(RATE,1);session.import_audio([(doc.view(),RATE,'clip',doc.metadata)])
        project=self.path/'project.celp';save_project(session,project);loaded=load_project(project)
        self.assertEqual(times(next(iter(loaded.media.values())).metadata),times(doc.metadata))

    def test_unreadable_embedded_wav_id3_is_opaque_but_mp3_export_is_atomic(self):
        doc=Document(np.zeros((32000,1),np.float32),RATE);doc.metadata=((b'id3 ',b'opaque'),)
        doc.set_sample(10,0,.5);self.assertEqual(doc.metadata,((b'id3 ',b'opaque'),))
        path=self.path/'keep.mp3';path.write_bytes(b'original')
        with self.assertRaises(AudioError):write_mp3(path,doc.view(),RATE,metadata=doc.metadata)
        self.assertEqual(path.read_bytes(),b'original')

    def test_recovery_preserves_updated_chapters_and_invalidated_measurements(self):
        doc=Document(np.zeros((32000,2),np.float32),RATE);doc.metadata=chunks()
        doc.select(RATE,2*RATE);doc.delete()
        manager=Recovery()
        try:
            manager.checkpoint(doc,Session(RATE,1))
            reopened,_,_,_=restore(manager.owner)
            self.assertEqual(reopened.metadata,doc.metadata)
            self.assertEqual(times(reopened.metadata),{'a':(0,1000),'c':(1000,2000)})
            self.assertFalse(tags_of(reopened.metadata).getall('RVA2'))
        finally:manager.close()


class MetadataGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.window=MainWindow(Document(np.zeros((8000,1),np.float32),RATE),no_audio=True)
    def tearDown(self):
        self.window.document.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater();self.app.processEvents()

    def test_unknown_info_and_conflicting_titles_need_the_actual_export_choice(self):
        window=self.window;window.document.metadata=chunks()+(info_chunk(INAM='Other',ZZZZ='custom'),)
        with patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.No) as ask:
            self.assertFalse(window._metadata_permission('mp3_192'))
        self.assertIn('LIST/INFO/ZZZZ',ask.call_args.args[2])
        self.assertIn('LIST/INFO/INAM',ask.call_args.args[2])
        with patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.Yes):
            self.assertTrue(window._metadata_permission('mp3_192'))

    def test_supported_info_does_not_prompt_and_unreadable_id3_reports_an_error(self):
        window=self.window;window.document.metadata=(info_chunk(INAM='Title',ISFT='previous encoder'),)
        with patch('soundsausage.window.QMessageBox.question') as ask:
            self.assertTrue(window._metadata_permission('mp3_192'));ask.assert_not_called()
        window.document.metadata=((b'id3 ',b'invalid'),)
        with patch.object(window,'error') as error:
            self.assertFalse(window._metadata_permission('mp3_192'))
        error.assert_called_once()

    def test_refusing_omitted_fields_preserves_target_and_unsaved_document(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            target=Path(folder)/'keep.mp3';target.write_bytes(b'original')
            window=self.window;window.document.metadata=(info_chunk(ZZZZ='custom'),)
            window.document.set_sample(0,0,.5)
            before=window.document.metadata
            with (patch.object(window,'_save_path',return_value=(target,'mp3_192')),
                  patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.No)):
                self.assertFalse(window.save_waveform(True))
            self.assertEqual(target.read_bytes(),b'original')
            self.assertEqual(window.document.metadata,before);self.assertTrue(window.document.dirty)
