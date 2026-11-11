from pathlib import Path
import tempfile
import unittest
import numpy as np

from soundsausage.audio import write_wav
from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.special import distortion, convolution, file_digest, load_impulse
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled
from soundsausage import storage


class SpecialTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.path = Path(self.folder.name)/'Impulse.wav'
        self.ir = np.array([[1], [0], [.5], [-.25]], np.float32)
        write_wav(self.path, self.ir, 8000, 'float32'); self.dsp = Dsp()
    def tearDown(self): self.folder.cleanup()

    def test_waveshapers_match_known_transfer_functions_and_zero_stays_zero(self):
        x = np.array([[-2], [-1], [-.5], [0], [.5], [1], [2]], np.float32)
        for kind in ('soft', 'hard', 'fold', 'crush'):
            out = distortion(x, 8000, kind=kind, drive_db=0, ceiling=1, mix=1, bits=2, oversample=False)
            expected = np.tanh(x) if kind == 'soft' else np.clip(x, -1, 1) if kind == 'hard' else 1-abs((x+1)%4-2) if kind == 'fold' else np.clip(np.rint(x*2), -2, 1)/2
            np.testing.assert_allclose(out, expected, atol=1e-7)
            self.assertEqual(out[3, 0], 0)
        np.testing.assert_array_equal(distortion(x, 8000, mix=0), x)

    def test_oversampling_measurably_reduces_aliased_seventh_harmonic(self):
        rate = 48000
        source = (.8*np.sin(2*np.pi*5000*np.arange(rate)/rate)).astype(np.float32)[:, None]
        ratios = []
        for quality in (False, True):
            out = distortion(source, rate, kind='hard', drive_db=18, ceiling=.5, mix=1, oversample=quality)
            spectrum = abs(np.fft.rfft(out[4800:-4800, 0].astype(np.float64)))
            ratios.append(spectrum[10400]/spectrum[4000])  # 13 kHz alias / 5 kHz fundamental
        self.assertLess(20*np.log10(ratios[1]/ratios[0]), -20)

    def test_distortion_preview_and_block_sizes_match_full_application(self):
        source = np.random.default_rng(1).normal(0, .1, (8000, 2)).astype(np.float32)
        for quality in (False, True):
            full = distortion(source, 8000, oversample=quality)
            np.testing.assert_array_equal(distortion(source, 8000, oversample=quality, limit=1000), full[:1000])
            np.testing.assert_array_equal(distortion(source, 8000, oversample=quality, block_frames=127), full)

    def test_convolution_matches_direct_linear_reference_with_tail(self):
        source = np.random.default_rng(5).normal(0, .1, (5000, 2)).astype(np.float32)
        ir = np.zeros((5000, 1), np.float32); ir[0] = 1; ir[2100] = .5; ir[4999] = -.1
        write_wav(self.path, ir, 8000, 'float32')
        out = convolution(source, 8000, ir_path=self.path, normalize=False, dry=0, wet=1, keep_tail=True)
        expected = np.column_stack([np.convolve(source[:, c].astype(np.float64), ir[:, 0]) for c in range(2)])
        np.testing.assert_allclose(out, expected, atol=4e-8)
        clipped = convolution(source, 8000, ir_path=self.path, normalize=False, dry=0, wet=1)
        np.testing.assert_array_equal(clipped, out[:len(source)])

    def test_convolution_normalization_dry_wet_and_stereo_kernels(self):
        impulse = np.array([[1, .5], [.5, 0]], np.float32); write_wav(self.path, impulse, 8000, 'float32')
        source = np.zeros((10, 2), np.float32); source[0] = (1, 1)
        out = convolution(source, 8000, ir_path=self.path, normalize=False, dry=.5, wet=.25)
        expected = np.zeros_like(source); expected[0] = .5; expected[:2] += .25*impulse
        np.testing.assert_allclose(out, expected, atol=1e-7)
        norm = convolution(source, 8000, ir_path=self.path, dry=0, wet=1)
        np.testing.assert_allclose(norm[:2], impulse/np.sqrt(1.25), atol=1e-7)
        with self.assertRaises(ValueError): load_impulse(self.path, 8000, 1)

    def test_large_partition_and_resampled_ir_remain_correct(self):
        impulse = np.zeros((20000, 1), np.float32); impulse[0] = 1; impulse[-1] = .2
        write_wav(self.path, impulse, 8000, 'float32')
        source = np.zeros((5000, 1), np.float32); source[0] = 1
        out = convolution(source, 8000, ir_path=self.path, normalize=False, dry=0, wet=1, keep_tail=True)
        np.testing.assert_allclose(out[:20000], impulse, atol=1e-7)
        np.testing.assert_allclose(out[20000:], 0, atol=1e-7)
        ir, _ = load_impulse(self.path, 16000, 1)
        self.assertEqual(len(ir), 40000)

    def test_convolution_preview_prefix_is_identical(self):
        source = np.random.default_rng(8).normal(0, .1, (8000, 2)).astype(np.float32)
        settings = dict(ir_path=self.path, keep_tail=True)
        full = convolution(source, 8000, **settings)
        prefix = convolution(source, 8000, limit=3000, **settings)
        np.testing.assert_array_equal(prefix, full[:3000])

    def test_repeat_requires_unchanged_ir_and_undo_restores_length(self):
        source = np.ones((100, 1), np.float32)*.1; doc = Document(source, 8000)
        doc.select(20, 80); doc.apply('convolution', ir_path=str(self.path), keep_tail=True)
        self.assertEqual(doc.frames, 103); self.assertEqual(doc.last_effect[1]['ir_sha256'], file_digest(self.path))
        doc.undo(); self.assertEqual(doc.frames, 100); np.testing.assert_array_equal(doc.view(), source)
        write_wav(self.path, self.ir*.5, 8000, 'float32')
        with self.assertRaisesRegex(ValueError, 'changed'): doc.repeat()
        self.assertFalse(doc.undo_stack)
        self.path.unlink()
        with self.assertRaises(ValueError): doc.repeat()

    def test_invalid_ir_parameters_and_cancel_do_not_commit(self):
        source = np.ones((1000, 1), np.float32)*.1; doc = Document(source, 8000)
        for name, settings in [('distortion', dict(kind='bad')), ('distortion', dict(bits=1)),
            ('distortion', dict(drive_db=40)), ('convolution', dict(ir_path=str(self.path), dry=2)),
            ('convolution', dict(ir_path=str(self.path), normalize='yes'))]:
            with self.assertRaises(ValueError): doc.apply(name, **settings)
        with self.assertRaises(OperationCancelled), operation(lambda *args: False): doc.apply('convolution', ir_path=str(self.path))
        with self.assertRaises(OperationCancelled), operation(lambda *args: False): doc.apply('distortion')
        np.testing.assert_array_equal(doc.view(), source); self.assertFalse(doc.undo_stack)
        write_wav(self.path, np.zeros((100, 1), np.float32), 8000, 'float32')
        with self.assertRaisesRegex(ValueError, 'silence'): load_impulse(self.path, 8000, 1)
        with self.path.open('wb') as file: file.truncate(33*1024*1024)
        with self.assertRaises(ValueError): load_impulse(self.path, 8000, 1)

    def test_large_effect_outputs_use_disk(self):
        source = storage.seal(storage.allocate((1100000, 2)))
        for name, settings in [('distortion', dict(oversample=False)), ('convolution', dict(ir_path=str(self.path)))]:
            out = self.dsp.process_blocks(name, source, 48000, **settings)
            self.assertIsInstance(out, np.memmap); self.assertEqual(out.shape, source.shape)

    def test_rendered_convolution_survives_recovery_and_project_without_external_ir(self):
        from soundsausage.recovery import Recovery, restore
        from soundsausage.session import Session
        from soundsausage.project import save_project, load_project
        doc = Document(np.ones((2000, 1), np.float32)*.1, 8000)
        doc.apply('convolution', ir_path=str(self.path), keep_tail=True)
        session = Session(8000, 1); session.import_audio([(doc.view(), 8000, 'Convolved')])
        project = self.path.parent/'Result.celp'; save_project(session, project)
        manager = Recovery()
        try:
            manager.checkpoint(doc, session)
            self.path.unlink()
            recovered, _, _, _ = restore(manager.owner)
            np.testing.assert_array_equal(recovered.view(), doc.view())
            np.testing.assert_array_equal(load_project(project).render(), session.render())
            with self.assertRaises(ValueError): recovered.repeat()
            np.testing.assert_array_equal(recovered.view(), doc.view())
        finally: manager.close()
