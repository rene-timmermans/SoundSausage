"""Independent lane timing against explicit audio, timeline and storage expectations."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import storage
from soundsausage.audio import read_wav, write_wav
from soundsausage.document import Document, Clip
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.project import save_project, load_project
from soundsausage.recovery import Recovery, restore
from soundsausage.session import Session
from test_id3_metadata import chunks, times, tags_of


class ChannelTimingTests(unittest.TestCase):
    def setUp(self):
        self.data = np.column_stack((np.arange(12)/32, -np.arange(12)/16)).astype(np.float32)

    def document(self, channel):
        doc = Document(self.data, 8000)
        doc.select_channels((channel,))
        return doc

    def test_cut_delete_and_trim_each_lane_and_restore_exact_snapshot(self):
        for channel in (0, 1):
            for action in ('cut', 'delete', 'trim'):
                with self.subTest(channel=channel, action=action):
                    doc = self.document(channel); doc.select(3, 7); doc.cursor = 5
                    clip = getattr(doc, action)()
                    expected = self.data.copy()
                    if action == 'trim':
                        expected[:4, channel] = self.data[3:7, channel]
                        expected[4:, channel] = 0
                        self.assertEqual(doc.selection, (0, 4))
                    else:
                        expected[3:8, channel] = self.data[7:, channel]
                        expected[8:, channel] = 0
                        self.assertEqual(doc.selection, (3, 3))
                    if action == 'cut':
                        np.testing.assert_array_equal(clip.samples, self.data[3:7, channel:channel+1])
                    np.testing.assert_array_equal(doc.view().view(np.uint32), expected.view(np.uint32))
                    self.assertEqual(len(doc.undo_stack), 1)
                    doc.undo(); np.testing.assert_array_equal(doc.view(), self.data)
                    self.assertEqual(doc.selection, (3, 7)); self.assertEqual(doc.cursor, 5)
                    self.assertEqual(doc.selected_channels, (channel,))
                    self.assertFalse(doc.dirty)
                    doc.redo(); np.testing.assert_array_equal(doc.view(), expected)

    def test_paste_shorter_longer_at_cursor_and_eof_on_either_lane(self):
        for channel in (0, 1):
            for start, end, length in ((3, 7, 2), (3, 7, 8), (3, 3, 2), (12, 12, 3), (0, 12, 1)):
                with self.subTest(channel=channel, interval=(start, end), length=length):
                    doc = self.document(channel); doc.select(start, end)
                    samples = np.full((length, 1), .75, np.float32)
                    doc.paste(Clip(samples, 8000))
                    chosen = np.concatenate((self.data[:start, channel], samples[:, 0], self.data[end:, channel]))
                    expected = np.zeros((max(len(chosen), 12), 2), np.float32)
                    expected[:12, 1-channel] = self.data[:, 1-channel]
                    expected[:len(chosen), channel] = chosen
                    np.testing.assert_array_equal(doc.view().view(np.uint32), expected.view(np.uint32))
                    self.assertEqual(doc.selection, (start, start+length))
                    self.assertTrue(samples.flags.writeable)  # Caller storage remains its own.
                    samples[:] = 0
                    np.testing.assert_array_equal(doc.view(), expected)

    def test_stereo_clip_uses_corresponding_lane_and_resamples_mono_clip(self):
        stereo = np.tile([.25, -.5], (6, 1)).astype(np.float32)
        for channel in (0, 1):
            doc = self.document(channel); doc.select(4, 8); doc.paste(Clip(stereo, 8000))
            np.testing.assert_array_equal(doc.view()[4:10, channel], stereo[:, channel])
            np.testing.assert_array_equal(doc.view()[:12, 1-channel], self.data[:, 1-channel])
            doc.undo(); doc.select(0, 0)
            doc.paste(Clip(np.zeros((16, 1), np.float32), 16000))
            self.assertEqual(doc.frames, 20)
            np.testing.assert_array_equal(doc.view()[8:, channel], self.data[:, channel])

    def test_mix_crosses_eof_without_shifting_any_existing_samples(self):
        for channel in (0, 1):
            doc = self.document(channel); doc.select(9, 11)
            doc.paste(Clip(np.full((7, 1), .25, np.float32), 8000), mix=True)
            expected = np.zeros((16, 2), np.float32); expected[:12] = self.data
            expected[9:, channel] += .25
            np.testing.assert_array_equal(doc.view().view(np.uint32), expected.view(np.uint32))
            self.assertEqual(doc.selection, (9, 16))
            doc.undo(); np.testing.assert_array_equal(doc.view(), self.data)

    def test_whole_lane_delete_still_preserves_other_and_both_still_changes_shared_time(self):
        doc = self.document(1); doc.select(0, 12); doc.delete()
        np.testing.assert_array_equal(doc.view()[:, 0], self.data[:, 0])
        np.testing.assert_array_equal(doc.view()[:, 1], 0)
        doc.undo(); doc.select_channels(); doc.select(3, 7); doc.delete()
        np.testing.assert_array_equal(doc.view(), self.data[[0, 1, 2, 7, 8, 9, 10, 11]])
        doc = Document(sample_rate=8000); doc.select_channels((1,))
        doc.paste(Clip(np.ones((3, 1), np.float32), 8000))
        np.testing.assert_array_equal(doc.view(), [[0, 1], [0, 1], [0, 1]])

    def test_effect_duration_and_preview_keep_other_lane_at_absolute_positions(self):
        data = np.column_stack((np.linspace(-.3, .3, 2400), np.linspace(.5, -.5, 2400))).astype(np.float32)
        for channel in (0, 1):
            for name, settings in (('stretch', dict(time_ratio=2)), ('stretch', dict(time_ratio=.5)),
                                   ('echo', dict(delay_ms=10, tail_seconds=.1)),
                                   ('reverb', dict(decay_seconds=.2, tail_seconds=.1))):
                with self.subTest(channel=channel, effect=name, settings=settings):
                    doc = Document(data, 8000); doc.select_channels((channel,)); doc.select(400, 1600)
                    processed = doc.dsp.process_blocks(name, data[400:1600, channel:channel+1], 8000, **settings)
                    preview = doc.preview_effect(name, **settings)
                    np.testing.assert_array_equal(preview[:, channel], processed[:, 0])
                    other = np.zeros(len(processed), np.float32)
                    count = min(len(processed), len(data)-400)
                    other[:count] = data[400:400+count, 1-channel]
                    np.testing.assert_array_equal(preview[:, 1-channel], other)
                    doc.apply(name, **settings)
                    np.testing.assert_array_equal(doc.view()[400:400+len(processed), channel], processed[:, 0])
                    np.testing.assert_array_equal(doc.view()[400+len(processed):400+len(processed)+800, channel], data[1600:, channel])
                    np.testing.assert_array_equal(doc.view()[:2400, 1-channel], data[:, 1-channel])
                    np.testing.assert_array_equal(doc.view()[2400:, 1-channel], 0)
                    doc.undo(); np.testing.assert_array_equal(doc.view(), data)

    def test_convolution_tail_on_right_uses_right_impulse_without_moving_left(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'response.wav'
            response = np.zeros((81, 2), np.float32); response[0] = (1, .5); response[80] = (.5, .25)
            write_wav(path, response, 8000, 'float32')
            doc = self.document(1); doc.select(3, 7)
            doc.apply('convolution', ir_path=str(path), keep_tail=True, normalize=False, dry=0, wet=1)
            self.assertEqual(doc.frames, 92)
            np.testing.assert_array_equal(doc.view()[:12, 0], self.data[:, 0])
            np.testing.assert_array_equal(doc.view()[12:, 0], 0)
            np.testing.assert_allclose(doc.view()[3:7, 1], self.data[3:7, 1]*.5, atol=1e-7)
            np.testing.assert_array_equal(doc.view()[87:, 1], self.data[7:, 1])

    def test_shared_cues_and_chapters_stay_at_same_times_and_undo_restores_raw_tags(self):
        cue = (b'cue ', struct.pack('<I', 1)+struct.pack('<II4sIII', 1, 16000, b'data', 0, 0, 16000))
        for action in ('delete', 'trim', 'paste', 'stretch'):
            doc = Document(np.zeros((32000, 2), np.float32), 8000)
            doc.metadata = (cue,)+chunks(); original = doc.metadata; before = times(original)
            doc.select_channels((1,)); doc.select(8000, 16000)
            if action == 'paste': doc.paste(Clip(np.ones((12000, 1), np.float32), 8000, chunks()))
            elif action == 'stretch': doc.apply('stretch', time_ratio=2)
            else: getattr(doc, action)()
            self.assertEqual(doc.metadata[0], cue)
            self.assertEqual(times(doc.metadata), before)
            self.assertEqual(str(tags_of(doc.metadata)['TLEN']), str(doc.frames*1000//8000))
            self.assertFalse(any('replaygain' in key.lower() for key in tags_of(doc.metadata)))
            doc.undo(); self.assertEqual(doc.metadata, original)

    def test_disk_suffix_cancel_and_metadata_failure_are_atomic_including_redo(self):
        source = storage.allocate((1200000, 2)); source[:] = (.125, -.25); source = storage.seal(source)
        doc = Document(source, 48000); doc.select_channels((1,)); doc.select(10, 20)
        doc.apply('invert'); doc.undo()
        before = doc._pieces; redo = list(doc.redo_stack); revision = doc.revision
        def cancel(done, total, label): return not (label == 'Paste' and done >= 262144)
        clip = Clip(np.ones((30, 1), np.float32), 48000)
        with self.assertRaises(OperationCancelled), operation(cancel): doc.paste(clip)
        self.assertIs(doc._pieces, before); self.assertEqual(doc.revision, revision)
        self.assertEqual(doc.redo_stack, redo); self.assertEqual(doc.selection, (10, 20))
        with patch('soundsausage.id3_metadata.audio_changed', side_effect=ValueError('bad tags')):
            with self.assertRaisesRegex(ValueError, 'bad tags'): doc.paste(clip)
        self.assertIs(doc._pieces, before); self.assertEqual(doc.redo_stack, redo)
        doc.paste(clip)
        self.assertIsNotNone(storage.lease_of(doc._pieces[-1]))
        self.assertEqual(doc.frames, 1200020)
        np.testing.assert_array_equal(doc.view()[:1200000, 0], source[:, 0])
        np.testing.assert_array_equal(doc.view()[1200000:, 0], 0)
        np.testing.assert_array_equal(source[:, 1], -.25)

    def test_address_limit_and_malformed_replacements_leave_document_unchanged(self):
        doc = self.document(0); doc.select(3, 7)
        with patch('soundsausage.document.MAX_AUDIO_BYTES', 100):
            with self.assertRaisesRegex(ValueError, 'address space'):
                doc.paste(Clip(np.ones((20, 1), np.float32), 8000))
        for data in (np.ones((3, 2), np.float32), np.full((3, 1), np.inf, np.float32)):
            with self.assertRaises(ValueError): doc.replace_selected(3, 7, data)
        np.testing.assert_array_equal(doc.view(), self.data); self.assertFalse(doc.undo_stack)

    def test_wav_project_and_crash_recovery_keep_padding_audio_and_channel_choice(self):
        doc = self.document(1); doc.select(3, 5)
        doc.paste(Clip(np.full((6, 1), .75, np.float32), 8000)); expected = doc.read()
        session = Session(8000, 1); session.import_audio([(doc.view(), 8000, 'Edited stereo', doc.metadata)])
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder)/'edited.wav'; project = Path(folder)/'edited.celp'
            write_wav(wav, doc.view(), 8000, 'float32', metadata=doc.metadata)
            np.testing.assert_array_equal(read_wav(wav).samples.view(np.uint32), expected.view(np.uint32))
            save_project(session, project); loaded = load_project(project)
            np.testing.assert_array_equal(loaded.render(), expected)
        manager = Recovery()
        try:
            manager.checkpoint(doc, session)
            recovered, loaded, _, _ = restore(manager.owner)
            np.testing.assert_array_equal(recovered.view(), expected)
            self.assertEqual(recovered.selected_channels, (1,)); self.assertEqual(recovered.selection, (3, 9))
            np.testing.assert_array_equal(loaded.render(), expected)
        finally: manager.close()
