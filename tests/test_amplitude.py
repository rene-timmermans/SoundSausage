"""Independent numeric expectations for the amplitude processors and edit history."""
import ctypes as C
import unittest

import numpy as np

from soundsausage.document import Document
from soundsausage.dsp import Dsp


class AmplitudeTests(unittest.TestCase):
    def setUp(self):
        self.original = np.array([[.25, -.5], [.75, .125], [-.25, .375], [0, -.25]], np.float32)
        self.doc = Document(self.original, 8000)

    def test_channel_mix_reads_both_original_channels_before_writing(self):
        self.doc.apply("channel_mix", matrix=((0, 1), (1, 0)))
        np.testing.assert_array_equal(self.doc.read(), self.original[:, ::-1])

    def test_channel_mix_selection_polarity_and_headroom(self):
        self.doc.select(1, 3)
        self.doc.apply("channel_mix", matrix=((2, 2), (-1, .5)))
        expected = self.original.copy()
        expected[1:3, 0] = 2 * (self.original[1:3, 0] + self.original[1:3, 1])
        expected[1:3, 1] = -self.original[1:3, 0] + .5 * self.original[1:3, 1]
        np.testing.assert_array_equal(self.doc.read(), expected)
        self.assertGreater(expected[1, 0], 1)
        self.doc.undo()
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertEqual(self.doc.selection, (1, 3))
        self.assertFalse(self.doc.dirty)
        self.doc.redo()
        np.testing.assert_array_equal(self.doc.read(), expected)

    def test_mono_average_and_side_signal(self):
        self.doc.apply("channel_mix", matrix=((.5, .5), (.5, .5)))
        np.testing.assert_array_equal(self.doc.read(), np.repeat(self.original.mean(axis=1)[:, None], 2, axis=1))
        self.assertEqual(self.doc.channels, 2)
        centered = Document(np.full((20, 2), .25, np.float32))
        centered.apply("channel_mix", matrix=((.5, -.5), (.5, -.5)))
        np.testing.assert_array_equal(centered.read(), np.zeros((20, 2)))

    def test_invalid_channel_mix_does_not_mutate_a_buffer_or_document(self):
        for matrix in (((1, 0), (0, float("nan"))), ((1, 0), (0, 2.1)), ((1, 0),), ((1, 0), (float("inf"), 1))):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                self.doc.apply("channel_mix", matrix=matrix)
            np.testing.assert_array_equal(self.doc.read(), self.original)
        mono = Document(self.original[:, :1])
        with self.assertRaises(ValueError):
            mono.apply("channel_mix", matrix=((1, 0), (0, 1)))
        self.assertFalse(self.doc.undo_stack)
        self.assertFalse(self.doc.dirty)
        data = self.original.copy()
        with self.assertRaises(ValueError):
            self.doc.dsp.channel_mix(data, ((1, 0), (0, float("nan"))))
        np.testing.assert_array_equal(data, self.original)

    def test_envelope_matches_a_piecewise_linear_curve_on_mono_and_stereo(self):
        for channels in (1, 2):
            doc = Document(np.ones((9, channels), np.float32))
            doc.apply("envelope", points=((0, 0), (.25, 1), (.5, .5), (1, 2)))
            gain = [0, .5, 1, .75, .5, .875, 1.25, 1.625, 2]
            np.testing.assert_array_equal(doc.read(), np.repeat(np.array(gain)[:, None], channels, axis=1))

    def test_envelope_is_relative_to_selection_and_repeat_uses_new_length(self):
        doc = Document(np.ones((10, 1), np.float32))
        doc.select(1, 4)
        points = [[0, 0], [1, 1]]
        doc.apply("envelope", points=points)
        points[1][1] = 0  # Settings stored for F2 must not alias callers.
        doc.select(5, 10)
        doc.repeat()
        np.testing.assert_array_equal(doc.read()[:, 0], [1, 0, .5, 1, 1, 0, .25, .5, .75, 1])

    def test_log_envelope_endpoints_and_single_frame(self):
        doc = Document(np.ones((3, 1), np.float32))
        doc.apply("envelope", points=((0, .25), (1, 1)), logarithmic=True)
        np.testing.assert_array_equal(doc.read()[:, 0], [.25, .5, 1])
        single = Document(np.ones((1, 1), np.float32))
        single.apply("envelope", points=((0, .5), (1, 1)))
        np.testing.assert_array_equal(single.read(), [[.5]])

    def test_invalid_envelope_keeps_audio_selection_and_history(self):
        for points in (((0, 1), (0, 0)), ((.1, 1), (1, 1)), ((0, 1), (1, 3)),
                       ((0, 1), (.5, float("inf")), (1, 1)), ((0, 1),), tuple((i / 64, 1) for i in range(65))):
            with self.subTest(points=points), self.assertRaises(ValueError):
                self.doc.apply("envelope", points=points)
        with self.assertRaises(ValueError):
            self.doc.apply("envelope", points=((0, 0), (1, 1)), logarithmic=True)
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertFalse(self.doc.undo_stack)
        self.assertFalse(self.doc.dirty)

    def test_normalize_removes_channel_dc_before_measuring_peaks(self):
        data = np.array([[.75, -.25], [.25, -.75]], np.float32)
        doc = Document(data)
        doc.apply("normalize", target=.5, linked=True, remove_dc=True)
        np.testing.assert_array_equal(doc.read(), [[.5, .5], [-.5, -.5]])
        constant = Document(np.full((5, 2), .25, np.float32))
        constant.apply("normalize", remove_dc=True)
        np.testing.assert_array_equal(constant.read(), np.zeros((5, 2)))

    def test_dynamics_neutral_is_exact_and_silence_remains_finite(self):
        for data in (self.original, np.zeros((10, 1), np.float32)):
            doc = Document(data)
            doc.apply("dynamics", points=((-96, -96), (0, 0)))
            np.testing.assert_array_equal(doc.read(), data)

    def test_compressor_matches_known_db_transfer_including_headroom(self):
        db = np.array([-60, -30, -18, -12, -6, 0, 6])
        samples = (10 ** (db / 20)).astype(np.float32)[:, None]
        doc = Document(samples)
        doc.apply("dynamics", points=((-96, -96), (-18, -18), (0, -12)), attack_ms=0, release_ms=0)
        expected_db = [-60, -30, -18, -16, -14, -12, -10]
        np.testing.assert_allclose(doc.read()[:, 0], 10 ** (np.array(expected_db) / 20), rtol=1e-6)

    def test_limiter_bounds_peaks_and_stereo_link_preserves_balance(self):
        samples = np.tile([1.5, -.15], (10, 1)).astype(np.float32)
        doc = Document(samples)
        settings = dict(points=((-96, -96), (-6, -6), (0, -6)), attack_ms=0, release_ms=0)
        doc.apply("dynamics", **settings)
        np.testing.assert_allclose(doc.read()[:, 0], 10 ** (-6 / 20), rtol=1e-6)
        np.testing.assert_allclose(doc.read()[:, 1] / doc.read()[:, 0], -.1, rtol=1e-6)
        separate = Document(samples)
        separate.apply("dynamics", linked=False, **settings)
        np.testing.assert_array_equal(separate.read()[:, 1], samples[:, 1])

    def test_dynamics_attack_and_release_have_measured_time_constants(self):
        # Constant target output at −6 dB makes the detector's envelope independently observable.
        samples = np.array([[1], [0.1], [0.1]], np.float32)
        doc = Document(samples, 1000)
        doc.apply("dynamics", points=((-96, -6), (0, -6)), attack_ms=1, release_ms=2)
        coefficient = np.exp(-1)
        detector = 1 - coefficient
        expected = [10 ** (-6 / 20) / detector]
        for _ in range(2):
            detector = np.exp(-.5) * detector + (1 - np.exp(-.5)) * .1
            expected.append(.1 * 10 ** (-6 / 20) / detector)
        np.testing.assert_allclose(doc.read()[:, 0], expected, rtol=1e-6)

    def test_dynamics_makeup_selection_undo_and_repeat(self):
        self.doc.select(0, 1)
        self.doc.apply("dynamics", points=((-96, -96), (0, 0)), makeup_db=6.020599913279624)
        self.doc.select(2, 4)
        self.doc.repeat()
        expected = self.original.copy()
        expected[[0, 2, 3]] *= 2
        np.testing.assert_allclose(self.doc.read(), expected)
        self.doc.undo()
        np.testing.assert_array_equal(self.doc.read()[2:], self.original[2:])

    def test_invalid_dynamics_and_overflow_preserve_document(self):
        valid = dict(points=((-96, -96), (0, 0)))
        for invalid in (dict(attack_ms=-1), dict(release_ms=float("nan")), dict(makeup_db=25),
                        dict(points=((-96, -96), (-100, 0))), dict(points=((-96, -96), (0, 25)))):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.doc.apply("dynamics", **(valid | invalid))
        huge = Document(np.full((2, 2), np.finfo(np.float32).max, np.float32))
        with self.assertRaises(ValueError):
            huge.apply("channel_mix", matrix=((2, 2), (2, 2)))
        self.assertFalse(huge.dirty)
        self.assertFalse(huge.undo_stack)
        self.assertFalse(self.doc.dirty)
        self.assertFalse(self.doc.undo_stack)

    def test_old_native_library_is_rejected_before_loading_new_functions(self):
        class OldLibrary:
            class Abi:
                restype = None
                def __call__(self): return 3
            ce_dsp_abi_version = Abi()
        from unittest.mock import patch
        with patch.object(C, "CDLL", return_value=OldLibrary()), self.assertRaisesRegex(RuntimeError, "Rebuild"):
            Dsp()
