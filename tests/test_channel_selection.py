import json
from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np

from soundsausage.audio import write_wav
from soundsausage.document import Document, Clip
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.restoration import learn_profile
from soundsausage import storage


class ChannelSelectionTests(unittest.TestCase):
    def setUp(self):
        t = np.arange(2048)/8000
        self.data = np.column_stack((.15*np.sin(2*np.pi*250*t), .6*np.sin(2*np.pi*500*t))).astype(np.float32)

    def test_gain_on_left_or_right_keeps_other_channel_bit_exact(self):
        for channel in (0, 1):
            doc = Document(self.data, 8000); doc.select_channels((channel,)); doc.select(100, 1600)
            doc.apply('gain', initial=.25)
            expected = self.data.copy(); expected[100:1600, channel] *= .25
            np.testing.assert_array_equal(doc.view().view(np.uint32), expected.view(np.uint32))
            self.assertEqual(doc.selected_channels, (channel,)); doc.undo()
            np.testing.assert_array_equal(doc.view(), self.data); self.assertEqual(doc.selected_channels, (channel,))
            doc.redo(); np.testing.assert_array_equal(doc.view(), expected)

    def test_normalize_measures_only_selected_channel(self):
        doc = Document(self.data, 8000); doc.select_channels((0,)); doc.apply('normalize', target=.9)
        self.assertAlmostEqual(float(abs(doc.view()[:, 0]).max()), .9, places=6)
        np.testing.assert_array_equal(doc.view()[:, 1], self.data[:, 1])

    def test_every_same_length_effect_preview_matches_application_and_preserves_other_channel(self):
        settings = [('invert', {}), ('reverse', {}), ('silence', {}),
            ('envelope', dict(points=((0, .2), (1, .8)))),
            ('dynamics', dict(points=((-96, -96), (-12, -12), (0, -8)))),
            ('graphic_eq', dict(gains=(0, 0, 0, 0, 3, 0, 0, 0, 0, 0))),
            ('parametric_eq', dict(bands=[dict(frequency=500, gain_db=-6)])),
            ('filter', dict(kind='high_pass', frequency=250)), ('delay', dict(delay_ms=5)),
            ('echo', dict(delay_ms=7)), ('reverb', dict(decay_seconds=.2)),
            ('click_removal', {}), ('pitch_shift', dict(semitones=3)),
            ('distortion', dict(drive_db=6))]
        for name, values in settings:
            with self.subTest(name=name):
                doc = Document(self.data, 8000); doc.select_channels((1,)); doc.select(100, 1800)
                preview = doc.preview_effect(name, limit=500, **values)
                doc.apply(name, **values)
                np.testing.assert_array_equal(doc.view(100, 600), preview)
                np.testing.assert_array_equal(doc.view()[:, 0].view(np.uint32), self.data[:, 0].view(np.uint32))
                np.testing.assert_array_equal(doc.view()[:100], self.data[:100])
                np.testing.assert_array_equal(doc.view()[1800:], self.data[1800:])

    def test_channel_mixer_reads_stereo_but_changes_only_chosen_output(self):
        doc = Document(self.data, 8000); doc.select_channels((0,))
        doc.apply('channel_mix', matrix=((0, 1), (1, 0)))
        np.testing.assert_array_equal(doc.view()[:, 0], self.data[:, 1])
        np.testing.assert_array_equal(doc.view()[:, 1], self.data[:, 1])

    def test_stereo_noise_profile_uses_matching_selected_spectrum(self):
        profile = learn_profile(self.data, 8000)
        doc = Document(self.data, 8000); doc.select_channels((1,))
        effective = doc.effect_profile(profile)
        np.testing.assert_array_equal(np.asarray(effective['power'])[:, 0], np.asarray(profile['power'])[:, 1])
        doc.apply('noise_reduction', profile=profile)
        np.testing.assert_array_equal(doc.view()[:, 0], self.data[:, 0])

    def test_stereo_impulse_uses_selected_response_channel(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'Stereo.wav'
            write_wav(path, np.array([[1, .25]], np.float32), 8000, 'float32')
            doc = Document(self.data, 8000); doc.select_channels((1,))
            doc.apply('convolution', ir_path=str(path), normalize=False, dry=0, wet=1)
            np.testing.assert_allclose(doc.view()[:, 1], self.data[:, 1]*.25, atol=1e-7)
            np.testing.assert_array_equal(doc.view()[:, 0], self.data[:, 0])

    def test_stretch_extends_only_chosen_channel_and_keeps_other_at_original_times(self):
        doc = Document(self.data, 8000); doc.select_channels((0,)); doc.select(100, 1000)
        doc.apply('stretch', time_ratio=2)
        self.assertEqual(doc.frames, len(self.data)+900)
        np.testing.assert_array_equal(doc.view()[:len(self.data), 1], self.data[:, 1])
        np.testing.assert_array_equal(doc.view()[len(self.data):, 1], 0)
        np.testing.assert_array_equal(doc.view()[1900:, 0], self.data[1000:, 0])
        doc.undo(); np.testing.assert_array_equal(doc.view(), self.data)

    def test_copy_and_paste_one_channel_keep_stereo_timing_and_other_samples(self):
        doc = Document(self.data, 8000); doc.select_channels((0,)); doc.select(100, 300)
        clip = doc.copy(); self.assertEqual(clip.samples.shape, (200, 1))
        doc.select_channels((1,)); doc.select(500, 700); doc.paste(clip)
        expected = self.data.copy(); expected[500:700, 1] = self.data[100:300, 0]
        np.testing.assert_array_equal(doc.view(), expected)
        doc.undo(); doc.select_channels((1,)); doc.select(500, 500); doc.paste(clip, True)
        expected = self.data.copy(); expected[500:700, 1] += self.data[100:300, 0]
        np.testing.assert_array_equal(doc.view(), expected)
        doc.select(500, 500)
        before = doc.read(); doc.paste(clip)
        self.assertEqual(doc.frames, len(before)+len(clip.samples))
        np.testing.assert_array_equal(doc.view()[:len(before), 0], before[:, 0])
        np.testing.assert_array_equal(doc.view()[700:, 1], before[500:, 1])

    def test_single_channel_reverse_preserves_shared_markers(self):
        doc = Document(self.data, 8000)
        info = ((b'cue ', struct.pack('<I', 1)+struct.pack('<II4sIII', 1, 500, b'data', 0, 0, 500)),)
        doc.metadata = info; doc.select_channels((1,)); doc.apply('reverse')
        self.assertEqual(doc.metadata, info)

    def test_repeat_uses_current_channel_target_and_cancel_is_atomic(self):
        doc = Document(self.data, 8000); doc.select_channels((0,)); doc.apply('invert')
        doc.select_channels((1,)); doc.repeat(); np.testing.assert_array_equal(doc.view(), -self.data)
        before = doc.view()
        with self.assertRaises(OperationCancelled), operation(lambda *args: False): doc.apply('gain', initial=.5)
        np.testing.assert_array_equal(doc.view(), before); self.assertEqual(doc.selected_channels, (1,))
        for channel in (0, 1):
            doc = Document(self.data, 8000)
            doc.apply('gain', initial=(.25, .75), final=(.25, .75))
            before = doc.read(); doc.select_channels((channel,)); doc.repeat()
            expected = before.copy(); expected[:, channel] *= (.25, .75)[channel]
            np.testing.assert_array_equal(doc.view(), expected)
        doc = Document(self.data, 8000)
        settings = dict(delay_ms=5, right_delay_ms=10)
        doc.apply('delay', **settings); doc.select_channels((1,))
        expected = doc.dsp.process_blocks('delay', doc.effect_view(), 8000, delay_ms=10)
        before = doc.read(); doc.repeat()
        np.testing.assert_array_equal(doc.view()[:, 0], before[:, 0])
        np.testing.assert_array_equal(doc.view()[:, 1], expected[:, 0])

    def test_large_stereo_result_retains_disk_storage_and_unselected_channel(self):
        source = storage.allocate((1100000, 2)); source[:] = (.125, .25); source = storage.seal(source)
        doc = Document(source, 48000); doc.select_channels((1,)); doc.apply('gain', initial=.5)
        self.assertIsInstance(doc.view(), np.memmap)
        np.testing.assert_array_equal(doc.view()[:, 0], source[:, 0])
        np.testing.assert_array_equal(doc.view()[:, 1], .125)

    def test_recovery_preserves_channels_and_old_journals_default_to_both(self):
        from soundsausage.recovery import Recovery, restore
        from soundsausage.session import Session
        doc = Document(self.data, 8000); doc.select_channels((1,)); doc.apply('invert')
        manager = Recovery()
        try:
            manager.checkpoint(doc, Session(8000, 1))
            recovered, _, _, _ = restore(manager.owner)
            self.assertEqual(recovered.selected_channels, (1,)); np.testing.assert_array_equal(recovered.view(), doc.view())
            data = json.loads(manager.path.read_text()); data['document'].pop('selected_channels')
            manager.path.write_text(json.dumps(data)); recovered, _, _, _ = restore(manager.owner)
            self.assertEqual(recovered.selected_channels, (0, 1))
        finally: manager.close()

    def test_mono_and_invalid_channel_masks(self):
        mono = Document(self.data[:, :1], 8000); self.assertEqual(mono.selected_channels, (0,)); self.assertFalse(mono.partial_channels)
        for mask in ((), (1,), (False,), (0, 0)):
            with self.assertRaises(ValueError): mono.select_channels(mask)
