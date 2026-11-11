import struct
import unittest

import numpy as np

from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage import storage
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled


class TimePitchTests(unittest.TestCase):
    def setUp(self):
        self.rate = 16000
        self.source = (.2*np.sin(2*np.pi*440*np.arange(16000)/self.rate)).astype(np.float32)[:, None]
        self.dsp = Dsp()

    def frequency(self, data):
        signal = data[len(data)//5:-len(data)//5, 0].astype(np.float64)
        spectrum = abs(np.fft.rfft(signal*np.hanning(len(signal))))
        return np.argmax(spectrum)*self.rate/len(signal)

    def test_stretch_changes_length_and_preserves_pitch(self):
        for ratio in (.25, .75, 1.5, 4):
            out = self.dsp.process_blocks('stretch', self.source, self.rate, time_ratio=ratio)
            self.assertEqual(len(out), round(len(self.source)*ratio))
            self.assertAlmostEqual(self.frequency(out), 440, delta=8)

    def test_pitch_changes_frequency_and_preserves_duration_for_both_engines(self):
        for quality in ('fine', 'fast'):
            for shift, frequency in ((-12, 220), (7, 440*2**(7/12)), (12, 880)):
                out = self.dsp.process_blocks('pitch_shift', self.source, self.rate, semitones=shift, quality=quality)
                self.assertEqual(len(out), len(self.source))
                self.assertAlmostEqual(self.frequency(out), frequency, delta=4)

    def test_identity_is_bit_exact_and_preview_matches_apply_prefix(self):
        np.testing.assert_array_equal(self.dsp.process_blocks('stretch', self.source, self.rate), self.source)
        for name, settings in [('stretch', dict(time_ratio=1.5)), ('pitch_shift', dict(semitones=5))]:
            out = self.dsp.process_blocks(name, self.source, self.rate, **settings)
            prefix = self.dsp.process_blocks(name, self.source, self.rate, limit=8000, **settings)
            np.testing.assert_array_equal(prefix, out[:8000])

    def test_stereo_balance_and_silence_remain_well_behaved(self):
        stereo = np.column_stack((self.source[:, 0], self.source[:, 0]*.5))
        out = self.dsp.process_blocks('stretch', stereo, self.rate, time_ratio=1.5)
        np.testing.assert_allclose(out[:, 1], out[:, 0]*.5, atol=2e-5)
        out = self.dsp.process_blocks('pitch_shift', np.zeros_like(stereo), self.rate, semitones=12)
        np.testing.assert_array_equal(out, 0)

    def test_stretch_remaps_selected_cues_and_shifts_following_audio_with_undo(self):
        doc = Document(self.source, self.rate)
        cues = (100, 4000, 8000, 12000, 15999)
        raw = struct.pack('<I', len(cues))+b''.join(struct.pack('<II4sIII', i, p, b'data', 0, 0, p) for i, p in enumerate(cues))
        doc.metadata = ((b'cue ', raw),); doc.select(4000, 12000)
        doc.apply('stretch', time_ratio=1.5)
        self.assertEqual(doc.frames, 20000); self.assertEqual(doc.selection, (4000, 16000))
        new = dict(doc.metadata)[b'cue ']
        self.assertEqual([struct.unpack_from('<I', new, 4+i*24+20)[0] for i in range(5)], [100, 4000, 10000, 16000, 19999])
        np.testing.assert_array_equal(doc.read(16000, 20000), self.source[12000:])
        doc.undo(); self.assertEqual(doc.metadata, ((b'cue ', raw),)); np.testing.assert_array_equal(doc.view(), self.source)
        doc.redo(); self.assertEqual(doc.frames, 20000)

    def test_short_or_invalid_processing_and_cancel_keep_document_unchanged(self):
        doc = Document(self.source, self.rate)
        for name, settings in [('stretch', dict(time_ratio=0)), ('pitch_shift', dict(semitones=25)),
            ('pitch_shift', dict(time_ratio=2)), ('stretch', dict(quality='no')), ('stretch', dict(typo=1))]:
            with self.assertRaises(ValueError): doc.apply(name, **settings)
        with self.assertRaises(OperationCancelled), operation(lambda *args: False): doc.apply('stretch', time_ratio=2)
        short = Document(self.source[:10], self.rate)
        with self.assertRaisesRegex(ValueError, '50 ms'): short.apply('pitch_shift', semitones=1)
        self.assertFalse(doc.dirty); self.assertFalse(doc.undo_stack); np.testing.assert_array_equal(doc.view(), self.source)

    def test_large_output_is_disk_backed(self):
        source = storage.seal(storage.allocate((1100000, 2)))
        out = self.dsp.process_blocks('stretch', source, 48000, time_ratio=1.1)
        self.assertIsInstance(out, np.memmap); self.assertEqual(out.shape, (1210000, 2))
