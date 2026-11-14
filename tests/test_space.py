"""Measured echoes, reverberant decay, streaming state and retained-tail edits."""
import json
import struct
import unittest
import tempfile
from pathlib import Path

import numpy as np

from soundsausage import storage
from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.space import Processor


class SpaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dsp = Dsp()

    def impulse(self, rate=8000, seconds=1, channels=1):
        source = np.zeros((round(rate*seconds), channels), np.float32)
        source[0, 0] = 1
        return source

    def test_delay_has_exact_time_level_and_independent_right_time(self):
        source = self.impulse(channels=2)
        source[0, 1] = .5
        out = self.dsp.process_blocks("delay", source, 8000, delay_ms=25,
                                      right_delay_ms=40, dry=.5, wet=.75, output_db=-6.020599913279624)
        expected = np.zeros_like(source)
        expected[0] = (.25, .125)
        expected[200, 0] = .375; expected[320, 1] = .1875
        np.testing.assert_array_equal(out, expected)

    def test_echo_geometric_repeats_and_zero_feedback_is_single_delay(self):
        source = self.impulse()
        out = self.dsp.process_blocks("echo", source, 8000, delay_ms=100, feedback=.5, damping=0, dry=0, wet=1)
        expected = np.zeros_like(source)
        for repeat in range(1, 10):
            expected[repeat*800] = .5**(repeat-1)
        np.testing.assert_array_equal(out, expected)
        echo = self.dsp.process_blocks("echo", source, 8000, feedback=0, damping=.9)
        delay = self.dsp.process_blocks("delay", source, 8000)
        np.testing.assert_array_equal(echo, delay)

    def test_ping_pong_alternates_channels_without_order_dependence(self):
        source = self.impulse(channels=2)
        settings = dict(delay_ms=100, feedback=.5, damping=0, ping_pong=True, dry=0, wet=1)
        out = self.dsp.process_blocks("echo", source, 8000, **settings)
        expected = np.zeros_like(source)
        for repeat in range(1, 10):
            expected[repeat*800, (repeat-1)%2] = .5**(repeat-1)
        np.testing.assert_array_equal(out, expected)
        right = source[:, ::-1].copy()
        np.testing.assert_array_equal(self.dsp.process_blocks("echo", right, 8000, **settings), out[:, ::-1])

    def test_feedback_damping_has_known_one_pole_response(self):
        source = self.impulse(seconds=.05)
        out = self.dsp.process_blocks("echo", source, 8000, delay_ms=10, feedback=.5, damping=.5, dry=0, wet=1)
        self.assertEqual(out[80, 0], 1)  # First repeat stays unfiltered.
        np.testing.assert_array_equal(out[160:170, 0], .25*.5**np.arange(10))

    def test_mono_ping_pong_is_ordinary_mono_echo(self):
        source = self.impulse()
        a = self.dsp.process_blocks("echo", source, 8000, ping_pong=True)
        b = self.dsp.process_blocks("echo", source, 8000, ping_pong=False)
        np.testing.assert_array_equal(a, b)

    def test_dry_only_is_bit_exact_and_silence_never_grows(self):
        source = np.random.default_rng(42).normal(0, .1, (10000, 2)).astype(np.float32)
        for name in ("delay", "echo", "reverb"):
            np.testing.assert_array_equal(self.dsp.process_blocks(name, source, 8000, wet=0), source)
            out = self.dsp.process_blocks(name, np.zeros_like(source), 8000, tail_seconds=.1)
            np.testing.assert_array_equal(out, 0)

    def test_reverb_predelay_shifts_only_wet_and_stereo_width_zero_is_mono(self):
        source = self.impulse(seconds=2, channels=2)
        settings = dict(dry=0, wet=1, damping=.3)
        a = self.dsp.process_blocks("reverb", source, 8000, predelay_ms=0, **settings)
        b = self.dsp.process_blocks("reverb", source, 8000, predelay_ms=40, **settings)
        np.testing.assert_array_equal(b[320:], a[:-320])
        np.testing.assert_array_equal(b[:320], 0)
        self.assertGreater(np.count_nonzero(a), 1000)
        self.assertGreater(np.linalg.norm(a[:, 0]-a[:, 1]), .01)
        mono_wet = self.dsp.process_blocks("reverb", source, 8000, width=0, **settings)
        np.testing.assert_array_equal(mono_wet[:, 0], mono_wet[:, 1])

    def test_reverb_measured_decay_tracks_requested_rt60(self):
        rate = 16000
        for seconds in (.5, 1.5, 3):
            out = self.dsp.process_blocks("reverb", self.impulse(rate, seconds*3), rate,
                dry=0, wet=1, predelay_ms=0, decay_seconds=seconds, damping=0)[:, 0].astype(np.float64)
            energy = np.cumsum((out*out)[::-1])[::-1]
            db = 10*np.log10(np.maximum(energy/energy[0], 1e-30))
            mask = (db < -5) & (db > -35)
            slope, _ = np.polyfit(np.flatnonzero(mask)/rate, db[mask], 1)
            self.assertAlmostEqual(-60/slope, seconds, delta=seconds*.12)

    def test_reverb_damping_reduces_late_high_frequency_energy(self):
        rate = 16000
        source = self.impulse(rate, 3)
        ratios = []
        for damping in (0, .85):
            out = self.dsp.process_blocks("reverb", source, rate, dry=0, wet=1,
                damping=damping, decay_seconds=2, predelay_ms=0)[:, 0]
            spectrum = abs(np.fft.rfft(out[rate//2:rate*2].astype(np.float64)))**2
            freq = np.fft.rfftfreq(rate*3//2, 1/rate)
            ratios.append(spectrum[freq > 4000].sum()/spectrum[freq < 1000].sum())
        self.assertLess(ratios[1], ratios[0]*.01)

    def test_room_size_changes_first_reflection_and_rt60_remains_finite(self):
        source = self.impulse(seconds=1)
        starts = []
        for room in (20, 100):
            out = self.dsp.process_blocks("reverb", source, 8000, room_size=room, predelay_ms=0, dry=0, wet=1)
            starts.append(np.flatnonzero(out[:, 0])[0])
        self.assertGreater(starts[1], starts[0]*2)

    def test_block_boundaries_and_preview_are_bit_equal_including_tail_fade(self):
        source = np.random.default_rng(45).normal(0, .1, (1451, 2)).astype(np.float32)
        for name, settings in (("delay", dict(delay_ms=8.7, right_delay_ms=11.2)),
            ("echo", dict(delay_ms=12.3, feedback=.7, damping=.45, ping_pong=True)),
            ("reverb", dict(decay_seconds=.6, predelay_ms=8, width=.6))):
            for channels in (1, 2):
                data = source[:, :channels].copy()
                whole = self.dsp.process_blocks(name, data, 8000, tail_seconds=.1, **settings)
                for block in (1, 127, 262144):
                    out = self.dsp.process_blocks(name, data, 8000, tail_seconds=.1, block_frames=block, **settings)
                    np.testing.assert_array_equal(out, whole)
                for limit in (100, 1500, len(whole)-3):
                    preview = self.dsp.process_blocks(name, data, 8000, tail_seconds=.1, limit=limit, **settings)
                    np.testing.assert_array_equal(preview, whole[:limit])
                np.testing.assert_array_equal(whole[-1], 0)

    def test_inplace_without_tail_agrees_with_streaming(self):
        for name in ("delay", "echo", "reverb"):
            source = self.impulse(channels=2)
            whole = source.copy(); self.dsp.process(name, whole, 8000)
            np.testing.assert_array_equal(whole, self.dsp.process_blocks(name, source, 8000, block_frames=777))
            with self.assertRaisesRegex(ValueError, "tail"):
                self.dsp.process(name, source, 8000, tail_seconds=.1)

    def test_tail_appends_time_and_preserves_markers_undo_redo_repeat(self):
        source = np.ones((1000, 1), np.float32)*.1
        doc = Document(source, 1000)
        positions = (10, 200, 599, 600, 999)
        cue = struct.pack('<I', 5)+b''.join(struct.pack('<II4sIII', i, p, b'data', 0, 0, p) for i, p in enumerate(positions))
        doc.metadata = ((b'cue ', cue),)
        doc.select(200, 600)
        settings = dict(delay_ms=20, dry=1, wet=.5, tail_seconds=.1)
        doc.apply("delay", **settings)
        self.assertEqual(doc.frames, 1100)
        self.assertEqual(doc.selection, (200, 700))
        raw = dict(doc.metadata)[b'cue ']
        self.assertEqual([struct.unpack_from('<I', raw, 4+i*24+20)[0] for i in range(5)], [10, 200, 599, 700, 1099])
        np.testing.assert_array_equal(doc.read(700, 1100), source[600:])
        doc.undo(); self.assertEqual(doc.metadata, ((b'cue ', cue),)); np.testing.assert_array_equal(doc.read(), source)
        doc.redo(); self.assertEqual(doc.frames, 1100)
        # Settings survive the same JSON representation used by crash recovery.
        doc.last_effect = tuple(json.loads(json.dumps(doc.last_effect)))
        doc.select(0, 100); doc.repeat(); self.assertEqual(doc.frames, 1200)

    def test_invalid_parameters_and_overflow_do_not_commit(self):
        source = self.impulse()
        doc = Document(source, 8000)
        for name, settings in (
            ("delay", dict(delay_ms=0)), ("delay", dict(right_delay_ms=float('nan'))),
            ("delay", dict(feedback=.5)), ("echo", dict(feedback=1)),
            ("echo", dict(damping=.96)), ("echo", dict(ping_pong='yes')),
            ("reverb", dict(decay_seconds=0)), ("reverb", dict(room_size=101)),
            ("reverb", dict(predelay_ms=251)), ("reverb", dict(width=-1)),
            ("reverb", dict(typo=1)), ("delay", dict(dry=-1)),
            ("echo", dict(wet=2)), ("reverb", dict(tail_seconds=601)),
            ("echo", dict(output_db=float('inf'))),
        ):
            with self.subTest(name=name, settings=settings), self.assertRaises(ValueError):
                doc.apply(name, **settings)
        np.testing.assert_array_equal(doc.read(), source)
        self.assertFalse(doc.undo_stack); self.assertFalse(doc.dirty)
        huge = Document(np.full((100, 1), np.finfo(np.float32).max, np.float32), 8000)
        with self.assertRaises(ValueError):
            huge.apply("delay", output_db=24)
        self.assertFalse(huge.undo_stack)

    def test_cancel_after_processing_a_block_keeps_document_and_history(self):
        doc = Document(np.ones((300000, 2), np.float32)*.1, 48000)
        doc.select(100, 299900)
        before = doc.view()
        with self.assertRaises(OperationCancelled), operation(lambda done, total, label: done == 0):
            doc.apply("reverb", tail_seconds=1)
        self.assertEqual(doc.selection, (100, 299900))
        np.testing.assert_array_equal(doc.view(), before)
        self.assertFalse(doc.undo_stack); self.assertFalse(doc.dirty)

    def test_low_and_high_samplerates_have_finite_bounded_state(self):
        for rate in (1000, 8000, 44100, 192000, 384000):
            for name in ("delay", "echo", "reverb"):
                processor = Processor(name, rate, 2)
                self.assertLess(sum(b.nbytes for b in processor.buffers), 4*1024*1024)
                out = self.dsp.process_blocks(name, self.impulse(seconds=.01), rate)
                self.assertTrue(np.isfinite(out).all())

    def test_large_effect_output_uses_disk_and_empty_audio_does_not_create_tail(self):
        source = storage.seal(storage.allocate((1100000, 2)))
        out = self.dsp.process_blocks("echo", source, 48000, tail_seconds=.1)
        self.assertIsInstance(out, np.memmap)
        self.assertEqual(out.shape, (1104800, 2))
        self.assertEqual(self.dsp.process_blocks("reverb", np.zeros((0, 1), np.float32), 8000, tail_seconds=60).shape, (0, 1))

    def test_retained_tail_survives_wav_project_and_crash_recovery_roundtrips(self):
        from soundsausage.audio import read_wav, write_wav
        from soundsausage.project import save_project, load_project
        from soundsausage.session import Session
        from soundsausage.recovery import Recovery, restore
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            doc = Document(self.impulse(seconds=.2), 8000)
            doc.apply("echo", delay_ms=40, tail_seconds=.3)
            write_wav(path/'tail.wav', doc.view(), 8000, 'float32')
            np.testing.assert_array_equal(read_wav(path/'tail.wav').samples, doc.view())
            session = Session(8000, 1)
            session.import_audio([(doc.view(), 8000, 'Echo tail')])
            save_project(session, path/'tail.celp')
            reopened = load_project(path/'tail.celp')
            np.testing.assert_array_equal(reopened.render(), session.render())
            manager = Recovery()
            try:
                manager.checkpoint(doc, session)
                recovered, _, _, _ = restore(manager.owner)
                np.testing.assert_array_equal(recovered.view(), doc.view())
                self.assertEqual(recovered.last_effect[0], 'echo')
                self.assertEqual(recovered.last_effect[1]['tail_seconds'], .3)
            finally:
                manager.close()
