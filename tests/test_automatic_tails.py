"""Late taps, long bounded tails, preview equivalence and atomic edit persistence."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import space, storage
from soundsausage.audio import read_wav, write_wav
from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.project import save_project, load_project
from soundsausage.recovery import Recovery, restore
from soundsausage.session import Session


class AutomaticTailTests(unittest.TestCase):
    def setUp(self): self.dsp = Dsp()

    def test_delayed_tap_after_a_two_second_gap_is_retained_with_a_quiet_taper(self):
        source = np.zeros((100, 2), np.float32); source[-1] = (1, .5)
        out = self.dsp.process_blocks('delay', source, 8000, delay_ms=20, right_delay_ms=2000, dry=0, wet=1, auto_tail=True)
        self.assertEqual(out[99+160, 0], 1)
        self.assertEqual(out[99+16000, 1], .5)
        self.assertGreaterEqual(len(out), 99+16000+80)
        np.testing.assert_array_equal(out[-80:], 0)
        self.assertFalse(out.flags.writeable)

    def test_high_feedback_retains_a_tail_longer_than_sixty_seconds(self):
        source = np.zeros((1, 1), np.float32); source[0] = 1
        out = self.dsp.process_blocks('echo', source, 1000, delay_ms=2000, feedback=.95, damping=0, dry=0, wet=1, auto_tail=True)
        self.assertGreater(len(out), 60*1000)
        self.assertLessEqual(len(out), 600*1000+1)
        self.assertAlmostEqual(float(out[62000, 0]), .95**30, places=6)
        self.assertLess(float(abs(out[-100:]).max()), 4e-5)
        self.assertIsNotNone(storage.lease_of(out))

    def test_manual_duration_and_reverb_decay_have_extended_ranges(self):
        source = np.zeros((100, 1), np.float32)
        out = self.dsp.process_blocks('reverb', source, 1000, decay_seconds=60, tail_seconds=61)
        self.assertEqual(out.shape, (61100, 1)); np.testing.assert_array_equal(out, 0)
        for settings in (dict(tail_seconds=601), dict(decay_seconds=61), dict(auto_tail='yes'), dict(auto_tail=True, tail_seconds=1)):
            with self.assertRaises(ValueError): self.dsp.process_blocks('reverb', source, 1000, **settings)

    def test_auto_prefix_and_result_do_not_depend_on_output_blocks(self):
        source = np.random.default_rng(4).normal(0, .1, (731, 2)).astype(np.float32)
        for name, settings in (('delay', dict(delay_ms=37, right_delay_ms=83)),
                               ('echo', dict(delay_ms=40, feedback=.5, ping_pong=True)),
                               ('reverb', dict(decay_seconds=.3))):
            whole = self.dsp.process_blocks(name, source, 8000, auto_tail=True, **settings)
            for block in (1, 127):
                result = self.dsp.process_blocks(name, source, 8000, auto_tail=True, block_frames=block, **settings)
                np.testing.assert_array_equal(result, whole)
            for limit in (0, 100, len(source), len(source)+3, len(whole)-3, len(whole)+100):
                preview = self.dsp.process_blocks(name, source, 8000, auto_tail=True, limit=limit, **settings)
                np.testing.assert_array_equal(preview, whole[:limit])

    def test_silent_dry_only_and_empty_inputs_do_not_gain_empty_tail_time(self):
        source = np.zeros((100, 2), np.float32)
        for name in ('delay', 'echo', 'reverb'):
            result = self.dsp.process_blocks(name, source, 8000, auto_tail=True)
            self.assertEqual(result.shape, source.shape); np.testing.assert_array_equal(result, 0)
            result = self.dsp.process_blocks(name, source+1, 8000, auto_tail=True, wet=0)
            np.testing.assert_array_equal(result, source+1)
            empty = self.dsp.process_blocks(name, source[:0], 8000, auto_tail=True)
            self.assertEqual(empty.shape, (0, 2))

    def test_actual_storage_does_not_reserve_the_six_hundred_second_limit(self):
        source = np.ones((100, 1), np.float32)
        out = self.dsp.process_blocks('delay', source, 8000, delay_ms=20, auto_tail=True)
        lease = storage.lease_of(out)
        self.assertEqual(lease.path.stat().st_size, out.nbytes)
        self.assertLess(out.nbytes, 100000)

    def test_streaming_storage_handles_partial_writes_without_truncating_samples(self):
        source = np.arange(18, dtype=np.float32).reshape(9, 2)
        with storage.StreamBuffer(2, 9) as writer:
            original = writer.file
            class ShortWriter:
                def write(self, data): return original.write(data[:7])
                def flush(self): return original.flush()
                def fileno(self): return original.fileno()
                def close(self): return original.close()
            writer.file = ShortWriter()
            writer.write(source); result = writer.finish()
        np.testing.assert_array_equal(result, source)

    def test_late_cancel_limit_and_write_failure_preserve_document_and_redo(self):
        source = np.ones((400, 1), np.float32)*.1
        doc = Document(source, 1000); doc.select(100, 200)
        doc.apply('invert'); doc.undo()
        before = doc._pieces; redo = list(doc.redo_stack); revision = doc.revision
        def cancel(done, total, label): return not (label == 'Effect toepassen' and done > 500)
        with self.assertRaises(OperationCancelled), operation(cancel):
            doc.apply('echo', delay_ms=1000, auto_tail=True)
        with patch.object(space, 'MAX_TAIL_SECONDS', .2):
            with self.assertRaisesRegex(ValueError, 'still audible'):
                doc.apply('delay', delay_ms=1000, auto_tail=True)
        owner = storage.workspace(); paths = set(owner.path.glob('*.buffer'))
        with patch.object(storage.StreamBuffer, 'write', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError, 'disk full'): doc.apply('delay', auto_tail=True)
        self.assertEqual(set(owner.path.glob('*.buffer')), paths)
        self.assertIs(doc._pieces, before); self.assertEqual(doc.revision, revision)
        self.assertEqual(doc.redo_stack, redo); self.assertEqual(doc.selection, (100, 200))

    def test_actual_tail_shifts_shared_cues_or_pads_only_the_chosen_lane_and_undo(self):
        source = np.zeros((1000, 2), np.float32); source[199] = (1, .5)
        cue = (b'cue ', struct.pack('<I', 1)+struct.pack('<II4sIII', 1, 700, b'data', 0, 0, 700))
        for channels in ((0, 1), (1,)):
            doc = Document(source, 1000); doc.metadata = (cue,); doc.select_channels(channels); doc.select(100, 200)
            doc.apply('echo', delay_ms=100, feedback=.2, damping=0, auto_tail=True)
            extra = doc.frames-len(source)
            self.assertGreater(extra, 0)
            position = struct.unpack_from('<I', dict(doc.metadata)[b'cue '], 24)[0]
            self.assertEqual(position, 700+(extra if len(channels) == 2 else 0))
            if len(channels) == 1:
                np.testing.assert_array_equal(doc.view()[:1000, 0].view(np.uint32), source[:, 0].view(np.uint32))
                np.testing.assert_array_equal(doc.view()[1000:, 0], 0)
            expected = doc.read(); doc.undo(); self.assertEqual(doc.metadata, (cue,)); np.testing.assert_array_equal(doc.view(), source)
            doc.redo(); np.testing.assert_array_equal(doc.view(), expected)
            self.assertTrue(doc.last_effect[1]['auto_tail'])

    def test_automatic_tail_survives_wav_project_and_recovery(self):
        source = np.zeros((100, 1), np.float32); source[-1] = 1
        doc = Document(source, 8000); doc.apply('reverb', decay_seconds=.2, auto_tail=True)
        session = Session(8000, 1); session.import_audio([(doc.view(), 8000, 'Tail')])
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder)/'tail.wav'; project = Path(folder)/'tail.celp'
            write_wav(wav, doc.view(), 8000, 'float32'); np.testing.assert_array_equal(read_wav(wav).samples, doc.view())
            save_project(session, project); np.testing.assert_array_equal(load_project(project).render()[:, :1], doc.view())
        recovery = Recovery()
        try:
            recovery.checkpoint(doc, session)
            loaded, _, _, _ = restore(recovery.owner); np.testing.assert_array_equal(loaded.view(), doc.view())
        finally: recovery.close()
