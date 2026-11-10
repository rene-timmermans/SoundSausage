"""Measure conversion quality, duration, atomic imports and sample-rate undo."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage.audio import AudioError, read_wav, write_wav
from soundsausage.document import Document, Clip
from soundsausage.project import save_project, load_project
from soundsausage.resample import resample, frame_count
from soundsausage.session import Session


class ResampleTests(unittest.TestCase):
    def tone(self, rate, frequency=1000, duration=.2):
        t = np.arange(round(rate * duration)) / rate
        return (.25 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)[:, None]

    def test_duration_pitch_and_channel_isolation_for_common_rates(self):
        for source, target in ((44100, 48000), (48000, 44100), (96000, 48000), (8000, 44100)):
            with self.subTest(source=source, target=target):
                mono = self.tone(source)
                data = np.column_stack((mono[:, 0], np.zeros(len(mono))))
                data = data.astype(np.float32)
                before = data.copy()
                result = resample(data, source, target)
                self.assertEqual(len(result), round(.2 * target))
                np.testing.assert_array_equal(data, before)
                np.testing.assert_array_equal(result[:, 1], 0)
                expected = self.tone(target)
                np.testing.assert_allclose(result[512:-512, 0], expected[512:-512, 0], atol=2e-5)

    def test_downsampling_rejects_energy_above_the_new_nyquist_frequency(self):
        result = resample(self.tone(48000, 18000), 48000, 22050)
        rms = np.sqrt(np.mean(result[512:-512] ** 2))
        self.assertLess(rms, 1e-5)

    def test_identity_is_exact_owned_and_writable_and_empty_audio_is_defined(self):
        data = self.tone(8000)
        data.flags.writeable = False
        result = resample(data, 8000, 8000)
        np.testing.assert_array_equal(data, result)
        self.assertTrue(result.flags.writeable)
        self.assertFalse(np.shares_memory(data, result))
        self.assertEqual(resample(np.empty((0, 2), np.float32), 44100, 48000).shape, (0, 2))

    def test_fractional_tail_and_extreme_ratios_keep_a_defined_nonzero_short_signal(self):
        for source, target in ((48000, 44100), (384000, 1000), (1000, 384000)):
            result = resample(np.full((1, 1), .1, np.float32), source, target)
            self.assertEqual(len(result), max(1, round(target / source)))
            self.assertTrue(np.isfinite(result).all())
            self.assertGreater(float(abs(result).max()), 0)

    def test_invalid_rates_and_size_limit_fail_before_any_large_allocation(self):
        data = self.tone(8000)
        for rate in (999, 384001, 44100.5, True):
            with self.subTest(rate=rate), self.assertRaises(AudioError):
                resample(data, 8000, rate)
        with patch("soundsausage.resample._library") as library, self.assertRaises(AudioError):
            resample(np.zeros((60000, 2), np.float32), 1000, 384000)
        library.assert_not_called()

    def test_document_conversion_preserves_times_and_undo_restores_rate_and_samples(self):
        data = self.tone(44100)
        doc = Document(data, 44100)
        doc.select(441, 2205)
        doc.convert_sample_rate(48000)
        self.assertEqual(doc.sample_rate, 48000)
        self.assertEqual(doc.selection, (480, 2400))
        self.assertEqual(doc.cursor, 480)
        converted = doc.read()
        self.assertTrue(doc.dirty)
        doc.undo()
        self.assertEqual(doc.sample_rate, 44100)
        self.assertEqual(doc.selection, (441, 2205))
        self.assertFalse(doc.dirty)
        np.testing.assert_array_equal(doc.read(), data)
        doc.redo()
        self.assertEqual(doc.sample_rate, 48000)
        np.testing.assert_array_equal(doc.read(), converted)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "converted.wav"
            write_wav(path, doc.read(), doc.sample_rate, "float32")
            self.assertEqual(read_wav(path).sample_rate, 48000)
            np.testing.assert_array_equal(read_wav(path).samples, converted)

    def test_document_conversion_noop_and_failure_keep_history_intact(self):
        doc = Document(self.tone(8000), 8000)
        doc.convert_sample_rate(8000)
        self.assertFalse(doc.dirty)
        with patch("soundsausage.document.resample", side_effect=AudioError("conversion failed")), self.assertRaises(AudioError):
            doc.convert_sample_rate(44100)
        self.assertEqual(doc.sample_rate, 8000)
        self.assertFalse(doc.undo_stack)

    def test_paste_and_mix_paste_convert_to_the_document_rate_without_changing_clipboard(self):
        data = self.tone(44100)
        clip = Clip(data, 44100)
        converted = resample(data, 44100, 48000)
        doc = Document(np.zeros((48000, 1), np.float32), 48000)
        doc.select(480, 480)
        doc.paste(clip)
        np.testing.assert_array_equal(doc.read(480, 480 + len(converted)), converted)
        doc.undo(); doc.select(480, 480); doc.paste(clip, mix=True)
        np.testing.assert_array_equal(doc.read(480, 480 + len(converted)), converted)
        np.testing.assert_array_equal(clip.samples, data)
        self.assertEqual(clip.sample_rate, 44100)

    def test_mixed_rate_import_preserves_duration_and_native_project_roundtrip(self):
        first, second = self.tone(44100), self.tone(48000)
        session = Session(44100, adopt_first_rate=False)
        session.import_audio([(first, 44100, "A"), (second, 48000, "B")], start=441)
        self.assertEqual(session.sample_rate, 44100)
        self.assertEqual(session.tracks[0].clips[0].frames, session.tracks[1].clips[0].frames)
        self.assertEqual(session.tracks[1].clips[0].start, 441)
        self.assertEqual({m.sample_rate for m in session.media.values()}, {44100})
        expected = session.render()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "mixed.celp"
            save_project(session, path)
            np.testing.assert_array_equal(load_project(path).render(), expected)
        session.undo()
        self.assertEqual(session.frames, 0)
        session.redo()
        np.testing.assert_array_equal(session.render(), expected)

    def test_failed_import_conversion_is_atomic(self):
        session = Session(44100, adopt_first_rate=False)
        with patch("soundsausage.session.resample", side_effect=AudioError("converter unavailable")), self.assertRaises(AudioError):
            session.import_audio([(self.tone(44100), 44100, "A"), (self.tone(48000), 48000, "B")])
        self.assertFalse(session.dirty)
        self.assertFalse(session.undo_stack)
        self.assertFalse(session.media)
        self.assertEqual(session.frames, 0)

    def test_edited_clip_at_another_rate_is_converted_back_before_applying(self):
        session = Session(44100, adopt_first_rate=False)
        clip = session.import_audio([(self.tone(44100), 44100, "A")])[0]
        original = session.render()
        session.replace_clip_audio(clip, self.tone(48000), 48000)
        self.assertEqual(session.frames, len(original))
        self.assertEqual(session.find_clip(clip)[1].frames, len(original))
        session.undo()
        np.testing.assert_array_equal(session.render(), original)
