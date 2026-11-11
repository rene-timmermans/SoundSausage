"""Real MP3 codecs, tags, cancellation, file choices and editor round trips."""
from io import BytesIO
import os
import struct
import zlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from mutagen.id3 import ID3,TIT2,TPE1,APIC
from mutagen.mp3 import MP3
from PySide6.QtWidgets import QApplication,QMessageBox

from soundsausage.audio import AudioError,read_wav,write_wav
from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.i18n import install_language,tr
from soundsausage.media import read_mp3,write_mp3,MP3_ENCODINGS
from soundsausage.operations import operation
from soundsausage.project import save_project,load_project
from soundsausage.recovery import Recovery,restore
from soundsausage.session import Session
from soundsausage.window import MainWindow,FORMAT_LABELS
from soundsausage import storage


ROOT=Path(__file__).resolve().parents[1]


def signal(rate=44100,channels=2,frames=None):
    time=np.arange(frames or rate)/rate
    data=np.column_stack((.2*np.sin(2*np.pi*440*time),.15*np.cos(2*np.pi*660*time))).astype(np.float32)
    return data[:,:channels]


def assert_close(test,actual,expected):
    test.assertEqual(actual.shape,expected.shape)
    test.assertTrue(np.isfinite(actual).all())
    snr=10*np.log10(np.sum(expected.astype(np.float64)**2)/max(1e-20,np.sum((actual-expected).astype(np.float64)**2)))
    test.assertGreater(snr,20)


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build');self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
    def tearDown(self):self.env.stop();self.folder.cleanup()

    def test_mono_stereo_and_all_bitrates_reopen_with_exact_length(self):
        for channels in (1,2):
            for encoding,bitrate in MP3_ENCODINGS.items():
                with self.subTest(channels=channels,encoding=encoding):
                    data=signal(channels=channels);p=self.path/'audio.mp3'
                    write_mp3(p,data,44100,encoding);info=MP3(p)
                    self.assertAlmostEqual(info.info.bitrate,bitrate*1000,delta=100)
                    audio=read_mp3(p);self.assertEqual(audio.sample_rate,44100)
                    self.assertEqual(audio.encoding,encoding);assert_close(self,audio.samples,data)

    def test_vbr_foreign_file_and_unicode_path_decode(self):
        data=signal();wave=self.path/'source.wav';p=self.path/'Één همسات $!.MP3'
        write_wav(wave,data,44100,'float32')
        subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(wave),'-c:a','libmp3lame','-q:a','2',str(p)],check=True,timeout=15)
        result=read_mp3(p);self.assertEqual(result.sample_rate,44100);assert_close(self,result.samples,data)

    def test_text_and_cover_art_survive_mp3_wav_mp3(self):
        tags=ID3();tags.add(TIT2(encoding=3,text=['Één همسات']));tags.add(TPE1(encoding=3,text=['Test artist']))
        def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        picture=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\xff\x00\x00'))+chunk(b'IEND',b'')
        tags.add(APIC(encoding=3,mime='image/png',type=3,desc='Cover',data=picture))
        raw=BytesIO();tags.save(raw,padding=lambda _:0)
        first=self.path/'tagged.mp3';write_mp3(first,signal(),44100,metadata=((b'id3 ',raw.getvalue()),))
        audio=read_mp3(first);wave=self.path/'copy.wav'
        write_wav(wave,audio.samples,audio.sample_rate,'float32',metadata=audio.metadata)
        back=read_wav(wave);last=self.path/'last.mp3'
        write_mp3(last,back.samples[:22050],44100,metadata=back.metadata)
        result=ID3(last)
        self.assertEqual(str(result['TIT2']),'Één همسات');self.assertEqual(str(result['TPE1']),'Test artist')
        self.assertEqual(result.getall('APIC')[0].data,picture)
        self.assertEqual(str(result['TLEN']),'500')
        self.assertEqual(len(read_mp3(last).samples),22050)

    def test_rates_are_converted_and_shorter_than_two_ms_is_rejected(self):
        for source_rate,target_rate in ((8000,32000),(96000,48000)):
            p=self.path/f'{source_rate}.mp3';write_mp3(p,signal(source_rate),source_rate)
            audio=read_mp3(p);self.assertEqual(audio.sample_rate,target_rate);self.assertEqual(len(audio.samples),target_rate)
        with self.assertRaisesRegex(AudioError,'2 ms'):write_mp3(self.path/'tiny.mp3',signal(frames=1),44100)
        with self.assertRaises(AudioError):write_mp3(self.path/'empty.mp3',np.empty((0,2),np.float32),44100)

    def test_decoded_audio_uses_owned_disk_storage(self):
        p=self.path/'disk.mp3';write_mp3(p,signal(),44100)
        with patch.object(storage,'MEMORY_THRESHOLD',1024):audio=read_mp3(p)
        self.assertIsInstance(audio.samples,np.memmap)
        self.assertIsNotNone(storage.lease_of(audio.samples));self.assertFalse(audio.samples.flags.writeable)

    def test_cancelled_decode_reaps_the_child_and_removes_temporary_files(self):
        p=self.path/'cancel.mp3';write_mp3(p,signal(),44100)
        children=[];native=subprocess.Popen;updates=[]
        def popen(*args,**kwargs):child=native(*args,**kwargs);children.append(child);return child
        def callback(done,total,label):
            updates.append(label);return len(updates)<2
        with patch('soundsausage.media.subprocess.Popen',side_effect=popen),self.assertRaises(OperationCancelled),operation(callback):read_mp3(p)
        self.assertTrue(children);self.assertTrue(all(p.poll() is not None for p in children))
        self.assertEqual(list((self.path/'work').glob('*/mp3-read-*')),[])

    def test_cancelled_encode_and_failure_leave_the_existing_file_intact(self):
        p=self.path/'keep.mp3';p.write_bytes(b'unchanged destination');updates=[]
        def callback(done,total,label):
            if label=='MP3 opslaan':updates.append(done)
            return len(updates)<2
        with self.assertRaises(OperationCancelled),operation(callback):write_mp3(p,signal(),44100)
        self.assertEqual(p.read_bytes(),b'unchanged destination')
        with patch('soundsausage.media._ffmpeg',side_effect=AudioError('codec failed')),self.assertRaises(AudioError):write_mp3(p,signal(),44100)
        self.assertEqual(p.read_bytes(),b'unchanged destination');self.assertEqual(list(self.path.glob('.keep.mp3.*.tmp')),[])

    def test_invalid_files_and_oversized_tags_are_rejected(self):
        bad=self.path/'bad.mp3';bad.write_bytes(b'not an MP3')
        with self.assertRaises(AudioError):read_mp3(bad)
        bad.write_bytes(b'ID3\x04\x00\x00\x08\x00\x00\x00')
        with self.assertRaisesRegex(AudioError,'16 MiB'):read_mp3(bad)
        with patch('soundsausage.media.shutil.which',return_value=None),self.assertRaisesRegex(AudioError,'requires'):write_mp3(self.path/'missing.mp3',signal(),44100)


class MediaGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build');self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
        self.manager=install_language();self.manager.set_language('en',False)
        self.source=self.path/'Source.MP3';write_mp3(self.source,signal(),44100)
        self.window=MainWindow(Document(signal(),44100),no_audio=True)
        self.errors=patch.object(self.window,'error');self.error=self.errors.start()
    def tearDown(self):
        w=self.window;w.document.mark_saved();w.session.mark_saved();w.close();w.deleteLater();self.app.processEvents()
        self.manager.set_language('en',False);self.errors.stop();self.env.stop();self.folder.cleanup()

    def test_open_edit_and_save_as_wav_or_mp3_preserves_the_import(self):
        w=self.window;before=self.source.read_bytes();self.assertTrue(w.load_path(self.source))
        self.assertTrue(w.document.encoding.startswith('mp3_'));w.document.apply('gain',initial=.5);expected=w.document.read().copy()
        wave=self.path/'result.wav'
        with patch.object(w,'_save_path',return_value=(wave,'float32')):self.assertTrue(w.save_waveform(True))
        np.testing.assert_array_equal(read_wav(wave).samples,expected)
        mp3=self.path/'result.mp3'
        with patch.object(w,'_save_path',return_value=(mp3,'mp3_320')):self.assertTrue(w.save_waveform(True))
        assert_close(self,read_mp3(mp3).samples,expected)
        self.assertEqual(w.document.encoding,'mp3_320');self.assertFalse(w.document.dirty)
        self.assertEqual(self.source.read_bytes(),before);self.error.assert_not_called()

    def test_translated_file_choices_match_the_encoding_and_actual_extension(self):
        w=self.window
        for code in ('nl','en','de','fr','es'):
            self.manager.set_language(code,False)
            for encoding in ('float32','pcm16',*MP3_ENCODINGS):
                wrong=self.path/('target.wav' if encoding in MP3_ENCODINGS else 'target.mp3')
                with patch('soundsausage.window.QFileDialog.getSaveFileName',return_value=(str(wrong),tr(FORMAT_LABELS[encoding]))) as picker:
                    path,chosen=w._save_path('Save a Waveform')
                actual_filters=picker.call_args.args[3].split(';;')
                self.assertIn(tr(FORMAT_LABELS['float32']),actual_filters)
                self.assertIn(picker.call_args.args[4],actual_filters)
                self.assertEqual(chosen,encoding);self.assertEqual(path.suffix,'.mp3' if encoding in MP3_ENCODINGS else '.wav')
        destination=self.path/'existing.mp3';destination.write_bytes(b'keep')
        with patch('soundsausage.window.QFileDialog.getSaveFileName',return_value=(str(destination.with_suffix('.wav')),FORMAT_LABELS['mp3_192'])),patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.Cancel):
            self.assertEqual(w._save_path('Save a Waveform'),(None,None))
        self.assertEqual(destination.read_bytes(),b'keep')

    def test_selection_and_mixdown_can_be_saved_as_mp3(self):
        w=self.window;self.assertTrue(w.load_path(self.source));original=w.document.read().copy()
        w.document.select(100,2100);w.document.select_channels((1,))
        selection=self.path/'right.mp3'
        with patch.object(w,'_save_path',return_value=(selection,'mp3_256')):w.save_selection()
        assert_close(self,read_mp3(selection).samples,original[100:2100,1:2])
        np.testing.assert_array_equal(w.document.read(),original)
        w.session.import_audio([(original,44100,'First')]);w.session.configure_track(w.session.selected_track,gain=.5)
        w.set_mode('multitrack');mix=self.path/'mix.mp3';expected=w.session.render()
        with patch.object(w,'_save_path',return_value=(mix,'mp3_320')):w.mixdown()
        assert_close(self,read_mp3(mix).samples,expected);self.error.assert_not_called()

    def test_mp3_encoding_and_tags_survive_recovery_and_self_contained_projects(self):
        w=self.window;w.load_path(self.source);w.document.apply('gain',initial=.5)
        expected=w.document.read().copy();manager=Recovery()
        try:
            manager.checkpoint(w.document,w.session)
            recovered,_,_,_=restore(manager.owner,dsp=w.document.dsp)
            self.assertEqual(recovered.encoding,w.document.encoding);self.assertEqual(recovered.metadata,w.document.metadata)
            np.testing.assert_array_equal(recovered.read(),expected)
        finally:manager.close()
        session=Session(44100,1);session.import_audio([(expected,44100,'MP3',w.document.metadata)])
        project=self.path/'project.celp';save_project(session,project);loaded=load_project(project)
        np.testing.assert_array_equal(loaded.render(),expected)
        self.assertEqual(next(iter(loaded.media.values())).metadata,w.document.metadata)

    def test_cancel_and_invalid_open_keep_the_previous_document(self):
        w=self.window;before=w.document
        with operation(lambda done,total,label:False):self.assertFalse(w.load_path(self.source))
        self.assertIs(w.document,before)
        bad=self.path/'broken.mp3';bad.write_bytes(b'broken');self.assertFalse(w.load_path(bad));self.assertIs(w.document,before)

    def test_failed_mp3_save_keeps_the_file_and_unsaved_edits(self):
        w=self.window;w.load_path(self.source);w.document.apply('gain',initial=.5);before=self.source.read_bytes()
        with patch('soundsausage.media._ffmpeg',side_effect=AudioError('failed')):self.assertFalse(w.save_waveform())
        self.assertEqual(self.source.read_bytes(),before);self.assertTrue(w.document.dirty)

    def test_mp3_metadata_omission_needs_the_actual_choice(self):
        w=self.window;w.document.metadata=((b'LIST',b'INFO'),(b'LIST',b'adtl'),(b'cue ',struct.pack('<I',0)))
        with patch('soundsausage.window.QMessageBox.question',return_value=QMessageBox.StandardButton.No) as question:
            self.assertFalse(w._metadata_permission('mp3_192'))
        self.assertIn('cue',question.call_args.args[2]);self.assertIn('LIST',question.call_args.args[2])


if __name__=='__main__':unittest.main()
