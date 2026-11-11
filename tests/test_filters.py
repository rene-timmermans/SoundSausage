"""Measured response, continuous state, bounded storage and edit atomicity."""
import unittest
import struct

import numpy as np

from soundsausage.document import Document
from soundsausage.dsp import Dsp
from soundsausage.filters import biquad, design, response
from soundsausage.operations import operation
from soundsausage.errors import OperationCancelled
from soundsausage import storage


class FilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dsp = Dsp()

    def levels(self, name, frequencies, **settings):
        coefficients, gain = design(name, 48000, **settings)
        return response(coefficients, gain, frequencies, 48000)

    def test_bell_exact_centre_gain_and_reciprocal_cut(self):
        for gain in (-24, -6, 0, 12, 24):
            settings = dict(bands=[dict(frequency=1234, gain_db=gain, q=3)])
            self.assertAlmostEqual(self.levels("parametric_eq", [1234], **settings)[0], gain, places=9)
        a = np.array([biquad("bell", 1234, 48000, 12, 3), biquad("bell", 1234, 48000, -12, 3)])
        np.testing.assert_allclose(response(a, 1, np.geomspace(1, 23999, 1000), 48000), 0, atol=1e-9)

    def test_shelves_have_expected_endpoints_and_half_gain_midpoint(self):
        for kind in ("low_shelf", "high_shelf"):
            for gain in (-24, 12, 24):
                a = np.array([biquad(kind, 1000, 48000, gain)])
                db = response(a, 1, [0, 1000, 24000], 48000)
                np.testing.assert_allclose(db, [gain, gain/2, 0] if kind == "low_shelf" else [0, gain/2, gain], atol=1e-9)
                curve = response(a, 1, np.geomspace(1, 23999, 1000), 48000)
                self.assertGreaterEqual(curve.min(), min(0, gain)-1e-8)
                self.assertLessEqual(curve.max(), max(0, gain)+1e-8)

    def test_butterworth_cutoff_is_minus_three_db_at_every_slope(self):
        for kind in ("low_pass", "high_pass"):
            for slope in (12, 24, 36, 48):
                db = self.levels("filter", [1000], kind=kind, frequency=1000, slope=slope)[0]
                self.assertAlmostEqual(db, -10*np.log10(2), places=8)

    def test_butterworth_far_band_attenuation_increases_with_order(self):
        for kind, passed, rejected in (("low_pass", 10, 4000), ("high_pass", 12000, 100)):
            previous = 0
            for slope in (12, 24, 36, 48):
                db = self.levels("filter", [passed, rejected], kind=kind, frequency=1000, slope=slope)
                self.assertAlmostEqual(db[0], 0, delta=.001)
                self.assertLess(db[1], previous-20)
                previous = db[1]

    def test_bandpass_and_notch_at_centre_and_dc(self):
        self.assertAlmostEqual(self.levels("filter", [1000], kind="band_pass", frequency=1000, q=5)[0], 0, places=9)
        self.assertLess(self.levels("filter", [0], kind="band_pass", frequency=1000)[0], -200)
        self.assertLess(self.levels("filter", [50], kind="notch", frequency=50, q=25)[0], -150)
        self.assertAlmostEqual(self.levels("filter", [0], kind="notch", frequency=50)[0], 0, places=8)

    def test_native_sine_gain_agrees_with_response(self):
        rate, frequency = 48000, 1000
        t = np.arange(rate*2)/rate
        source = (.1*np.sin(2*np.pi*frequency*t)).astype(np.float32)[:, None]
        settings = dict(bands=[dict(frequency=frequency, gain_db=12, q=2)])
        output = self.dsp.process_blocks("parametric_eq", source, rate, block_frames=137, **settings)
        ratio = np.linalg.norm(output[rate:].astype(np.float64))/np.linalg.norm(source[rate:].astype(np.float64))
        self.assertAlmostEqual(20*np.log10(ratio), 12, places=5)

    def test_native_impulse_fft_matches_independent_complex_response(self):
        source = np.zeros((131072, 1), np.float32); source[0] = .25
        settings = dict(kind="low_pass", frequency=1234, slope=48, output_db=-3)
        output = self.dsp.process_blocks("filter", source, 48000, block_frames=137, **settings)
        measured = 20*np.log10(np.maximum(abs(np.fft.rfft(output[:, 0]))/.25, 1e-12))
        frequencies = np.fft.rfftfreq(len(source), 1/48000)
        a, g = design("filter", 48000, **settings)
        predicted = response(a, g, frequencies, 48000)
        np.testing.assert_allclose(measured[predicted > -70], predicted[predicted > -70], atol=.003)

    def test_continuous_blocks_mono_stereo_and_preview_prefix(self):
        source = np.random.default_rng(3).normal(0, .1, (8191, 2)).astype(np.float32)
        for name, settings in (
            ("graphic_eq", dict(gains=(4, -3, 8, -2, 2, 3, -3, 1, 2, -5))),
            ("parametric_eq", dict(bands=[dict(frequency=70, gain_db=20, q=40), dict(kind="high_shelf", frequency=8000, gain_db=-12)])),
            ("filter", dict(kind="notch", frequency=50, q=50)),
        ):
            for channels in (1, 2):
                data = source[:, :channels].copy()
                whole = data.copy(); self.dsp.process(name, whole, 48000, **settings)
                for block in (1, 127, 8192):
                    chunked = self.dsp.process_blocks(name, data, 48000, block_frames=block, **settings)
                    np.testing.assert_array_equal(whole, chunked)
                preview = self.dsp.process_blocks(name, data, 48000, limit=700, **settings)
                np.testing.assert_array_equal(preview, whole[:700])

    def test_stereo_channels_do_not_leak_and_flat_eq_is_bit_exact(self):
        source = np.zeros((48000, 2), np.float32); source[0, 0] = 1
        output = self.dsp.process_blocks("filter", source, 48000, kind="high_pass", frequency=80)
        np.testing.assert_array_equal(output[:, 1], 0)
        for name in ("graphic_eq", "parametric_eq"):
            np.testing.assert_array_equal(self.dsp.process_blocks(name, source, 48000), source)

    def test_low_sample_rate_omits_unusable_graphic_bands(self):
        gains = [0]*10; gains[-1] = 24
        source = np.ones((100, 1), np.float32)
        np.testing.assert_array_equal(self.dsp.process_blocks("graphic_eq", source, 8000, gains=gains), source)
        for rate in (1000, 8000, 11025, 44100, 192000, 768000):
            for frequency in (1, rate*.499):
                for kind in ("low_pass", "high_pass", "band_pass", "notch"):
                    out = self.dsp.process_blocks("filter", source, rate, kind=kind, frequency=frequency, q=50, slope=48)
                    self.assertTrue(np.isfinite(out).all())

    def test_selection_undo_redo_repeat_and_metadata_preservation(self):
        source = np.random.default_rng(5).normal(0, .1, (1000, 2)).astype(np.float32)
        doc = Document(source, 48000)
        cues = ((b"cue ", struct.pack("<I", 1) + struct.pack("<II4sIII", 7, 400, b"data", 0, 0, 400)),)
        doc.metadata = cues
        doc.select(200, 600)
        settings = dict(bands=[dict(frequency=1000, gain_db=6)])
        doc.apply("parametric_eq", **settings)
        expected = self.dsp.process_blocks("parametric_eq", source[200:600], 48000, **settings)
        np.testing.assert_array_equal(doc.read(200, 600), expected)
        np.testing.assert_array_equal(doc.read(0, 200), source[:200])
        np.testing.assert_array_equal(doc.read(600, 1000), source[600:])
        self.assertEqual(doc.undo_stack[-1].label, "Parametric Equalizer")
        self.assertEqual(doc.frames, 1000)
        self.assertEqual(doc.metadata, cues)
        doc.undo(); np.testing.assert_array_equal(doc.read(), source)
        doc.redo(); np.testing.assert_array_equal(doc.read(200, 600), expected)
        settings["bands"][0]["gain_db"] = -24
        doc.select(600, 1000); doc.repeat()
        np.testing.assert_array_equal(doc.read(600, 1000), self.dsp.process_blocks("parametric_eq", source[600:], 48000, bands=[dict(frequency=1000, gain_db=6)]))

    def test_cancel_and_invalid_settings_leave_history_and_audio_intact(self):
        source = np.ones((300000, 1), np.float32)*.1
        doc = Document(source, 48000)
        with self.assertRaises(OperationCancelled), operation(lambda done, total, label: False):
            doc.apply("filter", kind="high_pass", frequency=80)
        for name, settings in (
            ("graphic_eq", dict(gains=[0]*9)), ("graphic_eq", dict(gains=[float("nan")]*10)),
            ("filter", dict(frequency=24000)), ("filter", dict(frequency=0)),
            ("filter", dict(slope=24.0)), ("filter", dict(q=float("inf"), kind="notch")),
            ("filter", dict(kind="oops")), ("filter", dict(output_db=25)),
            ("parametric_eq", dict(bands=[dict(frequency=-1, gain_db=2)])),
            ("parametric_eq", dict(bands=[dict(enabled="yes")])),
            ("parametric_eq", dict(typo=1)),
        ):
            with self.subTest(name=name, settings=settings), self.assertRaises(ValueError):
                doc.apply(name, **settings)
        np.testing.assert_array_equal(doc.read(), source)
        self.assertFalse(doc.undo_stack); self.assertFalse(doc.dirty)

    def test_native_rejects_unstable_coefficients_before_mutation(self):
        for coefficients in ((1, 0, 0, -2, 1), (1, 0, 0, 0, float("nan")), (1, 0, 0, 3, .5)):
            data = np.ones((10, 2), np.float32)
            with self.assertRaises(ValueError):
                self.dsp.biquads(data, np.array([coefficients], np.float64), np.zeros((1, 2, 2)), 1)
            np.testing.assert_array_equal(data, 1)

    def test_large_output_uses_disk_and_can_undo(self):
        source = storage.seal(storage.allocate((1100000, 2)))
        doc = Document(source, 48000)
        doc.apply("filter", frequency=80)
        self.assertIsInstance(doc.view(), np.memmap)
        self.assertEqual(doc.frames, len(source))
        doc.undo()
        self.assertEqual(doc.frames, len(source))

    def test_overflow_does_not_commit(self):
        doc = Document(np.full((32, 1), np.finfo(np.float32).max, np.float32))
        with self.assertRaises(ValueError):
            doc.apply("graphic_eq", output_db=24)
        self.assertFalse(doc.undo_stack); self.assertFalse(doc.dirty)
