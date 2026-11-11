import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from soundsausage import storage
from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled
from soundsausage.restoration import learn_profile, save_profile, load_profile, validate_profile


class RestorationTests(unittest.TestCase):
    def setUp(self):
        self.rate = 16000
        self.rng = np.random.default_rng(42)
        self.noise = self.rng.normal(0, .02, (16000, 1)).astype(np.float32)
        self.profile = learn_profile(self.noise, self.rate)
        self.dsp = Dsp()

    def test_measured_noise_reduction_improves_stationary_tone_snr(self):
        t = np.arange(32000)/self.rate
        clean = (.2*np.sin(2*np.pi*440*t))[:, None]
        noise = self.rng.normal(0, .02, clean.shape)
        source = (clean+noise).astype(np.float32)
        result = self.dsp.process_blocks('noise_reduction', source, self.rate, profile=self.profile)
        before = np.mean((source[2048:]-clean[2048:])**2)
        after = np.mean((result[2048:]-clean[2048:])**2)
        self.assertGreater(10*np.log10(before/after), 6)

    def test_residual_plus_clean_reconstruct_original_with_no_boundary_holes(self):
        clean = self.dsp.process_blocks('noise_reduction', self.noise, self.rate, profile=self.profile)
        removed = self.dsp.process_blocks('noise_reduction', self.noise, self.rate, profile=self.profile, residual=True)
        np.testing.assert_allclose(clean+removed, self.noise, atol=1e-8, rtol=1e-6)
        for length in (1, 20, 255, 256, 1000):
            result = self.dsp.process_blocks('noise_reduction', self.noise[:length], self.rate, profile=self.profile)
            self.assertEqual(result.shape, (length, 1)); self.assertTrue(np.isfinite(result).all())

    def test_zero_reduction_and_silent_profile_are_exact_bypasses(self):
        result = self.dsp.process_blocks('noise_reduction', self.noise, self.rate, profile=self.profile, reduction_db=0)
        np.testing.assert_array_equal(result, self.noise)
        removed = self.dsp.process_blocks('noise_reduction', self.noise, self.rate, profile=self.profile, reduction_db=0, residual=True)
        np.testing.assert_array_equal(removed, 0)
        profile = learn_profile(np.zeros_like(self.noise), self.rate)
        np.testing.assert_array_equal(self.dsp.process_blocks('noise_reduction', self.noise, self.rate, profile=profile), self.noise)

    def test_prefix_and_output_do_not_depend_on_external_block_size(self):
        for name, settings in [('noise_reduction', dict(profile=self.profile)), ('click_removal', {})]:
            source = self.noise.copy(); source[127:129] += 1; source[1022] -= 1
            expected = self.dsp.process_blocks(name, source, self.rate, **settings)
            for block in (127, 8192):
                np.testing.assert_array_equal(self.dsp.process_blocks(name, source, self.rate, block_frames=block, **settings), expected)
            np.testing.assert_array_equal(self.dsp.process_blocks(name, source, self.rate, limit=1050, **settings), expected[:1050])

    def test_linked_stereo_preserves_proportional_channels(self):
        source = np.column_stack((self.noise[:, 0], self.noise[:, 0]*.5))
        profile = learn_profile(source, self.rate)
        out = self.dsp.process_blocks('noise_reduction', source, self.rate, profile=profile, linked=True)
        np.testing.assert_array_equal(out[:, 1], out[:, 0]*.5)

    def test_click_interpolation_repairs_impulses_and_leaves_clean_sine_alone(self):
        clean = (.2*np.sin(2*np.pi*220*np.arange(16000)/self.rate)).astype(np.float32)[:, None]
        np.testing.assert_array_equal(self.dsp.process_blocks('click_removal', clean, self.rate), clean)
        source = clean.copy(); source[5000] += 1; source[9000:9004] -= 1
        out = self.dsp.process_blocks('click_removal', source, self.rate)
        self.assertLess(np.max(abs(out-clean)), .005)
        np.testing.assert_array_equal(out[:4999], clean[:4999])

    def test_width_and_threshold_do_not_repair_long_or_subthreshold_events(self):
        source = np.zeros((2000, 1), np.float32); source[200:220] = .5; source[500] = .005
        out = self.dsp.process_blocks('click_removal', source, self.rate, max_width_ms=.5)
        np.testing.assert_array_equal(out, source)
        stereo = np.repeat(source, 2, axis=1); stereo[1000, 0] = 1
        out = self.dsp.process_blocks('click_removal', stereo, self.rate)
        self.assertEqual(out[1000, 0], 0); np.testing.assert_array_equal(out[:, 1], stereo[:, 1])

    def test_selection_undo_and_repeat_keep_shape_and_original_source(self):
        doc = Document(self.noise, self.rate); doc.select(500, 15000)
        doc.apply('noise_reduction', profile=self.profile)
        np.testing.assert_array_equal(doc.read(0, 500), self.noise[:500])
        self.assertEqual(doc.frames, len(self.noise)); doc.undo()
        np.testing.assert_array_equal(doc.read(), self.noise)
        doc.last_effect = tuple(json.loads(json.dumps(doc.last_effect))); doc.repeat()
        self.assertTrue(doc.dirty)

    def test_profile_files_roundtrip_and_reject_mismatch_or_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'Noise.ssnoise'; save_profile(path, self.profile)
            self.assertEqual(load_profile(path), self.profile)
            for content in ('{}', '{"version":99}', 'not json', 'x'*1048577):
                path.write_text(content)
                with self.assertRaises(ValueError): load_profile(path)
        for invalid in (dict(self.profile, fft_size=999), dict(self.profile, power=[[float('nan')]])):
            with self.assertRaises(ValueError): validate_profile(invalid)
        with self.assertRaises(ValueError): validate_profile(self.profile, 8000, 1)
        with self.assertRaises(ValueError): validate_profile(self.profile, 16000, 2)
        with self.assertRaises(ValueError): learn_profile(self.noise[:1], self.rate)

    def test_cancel_learn_or_effect_and_invalid_settings_keep_document(self):
        doc = Document(self.noise, self.rate)
        for name, settings in [('noise_reduction', dict(profile=self.profile)), ('click_removal', {})]:
            with self.assertRaises(OperationCancelled), operation(lambda *args: False): doc.apply(name, **settings)
        with self.assertRaises(OperationCancelled), operation(lambda *args: False): learn_profile(self.noise, self.rate)
        for name, settings in [('noise_reduction', dict(profile=self.profile, reduction_db=37)),
                               ('noise_reduction', dict(profile=self.profile, smoothing=-1)),
                               ('click_removal', dict(max_width_ms=3)), ('click_removal', dict(typo=True))]:
            with self.assertRaises(ValueError): doc.apply(name, **settings)
        self.assertFalse(doc.undo_stack); np.testing.assert_array_equal(doc.view(), self.noise)

    def test_large_restoration_output_is_disk_backed(self):
        source = storage.seal(storage.allocate((1100000, 2)))
        profile = learn_profile(np.zeros((2000, 2), np.float32), 8000)
        profile['power'] = np.full((129, 2), 1e-4).tolist()
        out = self.dsp.process_blocks('noise_reduction', source, 8000, profile=profile)
        self.assertIsInstance(out, np.memmap); self.assertEqual(out.shape, source.shape)
