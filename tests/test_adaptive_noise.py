"""Measured changing-noise/detail trade-offs and editor transaction regressions."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import numpy as np

from soundsausage import storage
from soundsausage.audio import read_wav, write_wav
from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage.restoration import learn_profile, noise_reduction


class AdaptiveNoiseTests(unittest.TestCase):
    def setUp(self):
        self.rate = 16000
        self.rng = np.random.default_rng(21)
        self.profile = learn_profile(self.rng.normal(0, .008, (self.rate, 1)).astype(np.float32), self.rate)

    def test_rising_noise_tracks_better_than_fixed_profile_without_losing_main_tone(self):
        rate = self.rate; t = np.arange(rate*8)/rate
        level = np.interp(t, [0, 1, 3, 5, 7, 8], [.008, .008, .04, .04, .01, .01])
        clean = .06*np.sin(2*np.pi*440*t)+.002*np.sin(2*np.pi*1371*t)
        noise = self.rng.normal(0, 1, len(t))*level
        source = (clean+noise).astype(np.float32)[:, None]
        fixed = noise_reduction(source, rate, profile=self.profile, detail=50)[:, 0]
        adaptive = noise_reduction(source, rate, profile=self.profile, detail=50, adaptive=True)[:, 0]
        region = slice(4*rate, 5*rate)
        error = lambda x: np.mean((x[region]-clean[region])**2)
        self.assertGreater(10*np.log10(error(fixed)/error(adaptive)), 4)
        self.assertGreater(10*np.log10(np.mean(noise[region]**2)/error(adaptive)), 6)
        projection = 2*np.mean(adaptive[region]*np.sin(2*np.pi*440*t[region]))
        self.assertGreater(projection/.06, .85)

    def test_detail_protection_recovers_more_weak_tone_while_still_reducing_background(self):
        rate = self.rate; t = np.arange(rate*6)/rate
        clean = .002*np.sin(2*np.pi*437*t)
        source = (clean+self.rng.normal(0, .008, len(t))).astype(np.float32)[:, None]
        projection = []; background = self.rng.normal(0, .008, (rate*3, 1)).astype(np.float32)
        for detail in (0, 50, 100):
            result = noise_reduction(source, rate, profile=self.profile, detail=detail)[:, 0]
            projection.append(2*np.mean(result[rate:-rate]*np.sin(2*np.pi*437*t[rate:-rate]))/.002)
        self.assertGreater(projection[1]-projection[0], .05)
        self.assertGreater(projection[2]-projection[0], .12)
        reduced = noise_reduction(background, rate, profile=self.profile, detail=100)
        self.assertGreater(10*np.log10(np.mean(background[1024:]**2)/np.mean(reduced[1024:]**2)), 3)

    def test_changed_noise_spectrum_is_followed_instead_of_reusing_the_old_shape(self):
        rate = self.rate
        white = self.rng.normal(0, 1, rate*7)
        kernel = np.hanning(33); kernel /= kernel.sum()
        low = np.convolve(white, kernel, mode='same'); high = white-low
        low *= .015/low.std(); high *= .015/high.std()
        background = low+.1*high; background[2*rate:] = high[2*rate:]+.1*low[2*rate:]
        profile = learn_profile(background[:rate, None].astype(np.float32), rate)
        source = background.astype(np.float32)[:, None]
        fixed = noise_reduction(source, rate, profile=profile, detail=50)
        adaptive = noise_reduction(source, rate, profile=profile, adaptive=True, detail=50)
        region = slice(5*rate, 6*rate)
        self.assertGreater(10*np.log10(np.mean(fixed[region]**2)/np.mean(adaptive[region]**2)), 4)

    def test_abrupt_rise_and_fall_follow_background_without_noise_in_digital_silence(self):
        rate = self.rate; t = np.arange(rate*8)/rate
        levels = np.where(t < 1, .008, np.where(t < 5, .04, .006))
        source = (self.rng.normal(0, 1, len(t))*levels).astype(np.float32)[:, None]
        source[7*rate:] = 0
        fixed = noise_reduction(source, rate, profile=self.profile)
        adaptive = noise_reduction(source, rate, profile=self.profile, adaptive=True, detail=50)
        region = slice(3*rate, 4*rate)
        self.assertLess(np.mean(adaptive[region]**2), np.mean(fixed[region]**2))
        # After the fall, the earlier loud background must not leave a stuck
        # high estimate. Compare with the identical quiet tail processed alone.
        fresh = noise_reduction(source[5*rate:], rate, profile=self.profile, adaptive=True, detail=50)
        ratio = np.mean(adaptive[6*rate:round(6.5*rate)]**2)/np.mean(fresh[rate:round(1.5*rate)]**2)
        self.assertAlmostEqual(float(ratio), 1, delta=.2)
        np.testing.assert_array_equal(adaptive[7*rate+1024:], 0)

    def test_shorter_tracking_time_follows_an_abrupt_broadband_rise_sooner(self):
        rate = self.rate
        source = self.rng.normal(0, 1, (rate*5, 1)).astype(np.float32)
        source[:rate] *= .008; source[rate:] *= .04
        fast = noise_reduction(source, rate, profile=self.profile, adaptive=True, tracking=.05)
        slow = noise_reduction(source, rate, profile=self.profile, adaptive=True, tracking=.5)
        region = slice(2*rate, 3*rate)
        self.assertGreater(10*np.log10(np.mean(slow[region]**2)/np.mean(fast[region]**2)), 3)

    def test_unlinked_stereo_matches_separate_mono_processing(self):
        source = self.rng.normal(0, .008, (16000, 2)).astype(np.float32)
        source[8000:, 1] *= 4
        profile = learn_profile(source[:8000], self.rate)
        stereo = noise_reduction(source, self.rate, profile=profile, adaptive=True, linked=False, detail=50)
        for channel in (0, 1):
            mono = dict(profile, power=np.asarray(profile['power'])[:, channel:channel+1].tolist())
            expected = noise_reduction(source[:, channel:channel+1], self.rate, profile=mono, adaptive=True, detail=50)
            np.testing.assert_array_equal(stereo[:, channel:channel+1], expected)

    def test_sustained_partial_and_sharp_attack_do_not_become_tracked_background(self):
        rate = self.rate; t = np.arange(rate*16)/rate
        clean = .06*np.sin(2*np.pi*437*t)
        source = (clean+self.rng.normal(0, .02, len(t))).astype(np.float32)[:, None]
        result = noise_reduction(source, rate, profile=self.profile, adaptive=True, tracking=.05, detail=50)[:, 0]
        region = slice(12*rate, 15*rate)
        projection = 2*np.mean(result[region]*np.sin(2*np.pi*437*t[region]))/.06
        self.assertGreater(projection, .85)
        attack = self.rng.normal(0, .008, (rate*2, 1)).astype(np.float32)
        attack[rate:rate+17, 0] += .8*np.hanning(17)
        result = noise_reduction(attack, rate, profile=self.profile, adaptive=True, detail=50)
        self.assertLessEqual(abs(int(np.argmax(result[:, 0]))-(rate+8)), 1)
        self.assertGreater(result[rate:rate+17].max(), .65)

    def test_clean_and_removed_reconstruct_input_with_consistent_preview_and_blocks(self):
        source = self.rng.normal(0, .02, (18000, 1)).astype(np.float32)
        for adaptive in (False, True):
            settings = dict(profile=self.profile, adaptive=adaptive, detail=65)
            full = noise_reduction(source, self.rate, **settings)
            removed = noise_reduction(source, self.rate, residual=True, **settings)
            np.testing.assert_allclose(full+removed, source, atol=1e-8, rtol=1e-6)
            for limit in (1, 31, 511, 1050, len(source)-31):
                np.testing.assert_array_equal(noise_reduction(source, self.rate, limit=limit, **settings), full[:limit])
            np.testing.assert_array_equal(noise_reduction(source, self.rate, block_frames=127, **settings), full)

    def test_linked_stereo_and_one_channel_keep_balance_and_other_samples(self):
        source = self.rng.normal(0, .008, (32000, 1)).astype(np.float32)
        source[16000:] *= 3
        stereo = np.column_stack((source[:, 0], source[:, 0]*.5))
        profile = learn_profile(stereo[:8000], self.rate)
        result = noise_reduction(stereo, self.rate, profile=profile, adaptive=True, detail=50)
        np.testing.assert_array_equal(result[:, 1], result[:, 0]*.5)
        doc = Document(stereo, self.rate); doc.select_channels((1,)); doc.select(1024, 30000)
        doc.apply('noise_reduction', profile=profile, adaptive=True, detail=50)
        np.testing.assert_array_equal(doc.view()[:, 0].view(np.uint32), stereo[:, 0].view(np.uint32))
        np.testing.assert_array_equal(doc.view()[:1024], stereo[:1024])
        self.assertEqual(doc.frames, len(stereo)); doc.undo()
        np.testing.assert_array_equal(doc.view(), stereo)

    def test_profile_and_source_immutable_repeat_and_float_wav_round_trip(self):
        original = deepcopy(self.profile)
        source = self.rng.normal(0, .01, (16000, 1)).astype(np.float32)
        doc = Document(source, self.rate)
        doc.apply('noise_reduction', profile=self.profile, adaptive=True, tracking=.3, detail=75)
        expected = doc.read(); doc.undo(); doc.repeat()
        np.testing.assert_array_equal(doc.view(), expected)
        self.assertEqual(doc.last_effect[1]['tracking'], .3); self.assertEqual(self.profile, original)
        np.testing.assert_array_equal(source, doc.undo_stack[-1].pieces[0])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'cleaned.wav'; write_wav(path, doc.view(), self.rate, 'float32')
            np.testing.assert_array_equal(read_wav(path).samples, expected)

    def test_late_cancel_and_invalid_settings_leave_history_selection_and_profile_intact(self):
        source = self.rng.normal(0, .01, (32000, 1)).astype(np.float32)
        doc = Document(source, self.rate); doc.select(100, 30000)
        doc.apply('invert'); doc.undo()
        revision = doc.revision; original = deepcopy(self.profile); redo = list(doc.redo_stack)
        def cancel(done, total, label): return not (label == 'Ruis verminderen' and done > 8192)
        with self.assertRaises(OperationCancelled), operation(cancel):
            doc.apply('noise_reduction', profile=self.profile, adaptive=True, detail=50)
        self.assertEqual(doc.revision, revision); self.assertEqual(doc.redo_stack, redo)
        self.assertEqual(doc.selection, (100, 30000)); self.assertEqual(self.profile, original)
        np.testing.assert_array_equal(doc.view(), source)
        for settings in (dict(adaptive=1), dict(adaptive='yes'), dict(detail=-1), dict(detail=101),
                         dict(detail=True), dict(tracking=0), dict(tracking=6), dict(tracking=float('nan'))):
            with self.assertRaises(ValueError): doc.apply('noise_reduction', profile=self.profile, **settings)
        self.assertEqual(doc.revision, revision); self.assertFalse(doc.undo_stack)

    def test_silence_zero_reduction_short_ranges_and_multiple_rates_remain_defined(self):
        for rate in (1000, 8000, 44100, 48000, 96000, 384000):
            profile = learn_profile(self.rng.normal(0, .01, (max(rate//5, 8192), 1)).astype(np.float32), rate)
            for length in (0, 1, 31, 8193):
                source = np.zeros((length, 1), np.float32)
                output = noise_reduction(source, rate, profile=profile, adaptive=True, detail=100)
                self.assertEqual(output.shape, source.shape); np.testing.assert_array_equal(output, source)
        source = self.rng.normal(0, .01, (2000, 1)).astype(np.float32)
        np.testing.assert_array_equal(noise_reduction(source, self.rate, profile=self.profile, adaptive=True, detail=100, reduction_db=0), source)

    def test_large_adaptive_output_spills_to_disk_and_preserves_immutable_source(self):
        source = storage.allocate((1100000, 2), zero=True); source = storage.seal(source)
        profile = learn_profile(self.rng.normal(0, .01, (2000, 2)).astype(np.float32), 8000)
        out = noise_reduction(source, 8000, profile=profile, adaptive=True, detail=50)
        self.assertIsNotNone(storage.lease_of(out)); self.assertEqual(out.shape, source.shape)
        self.assertFalse(source.flags.writeable); np.testing.assert_array_equal(source, 0)
