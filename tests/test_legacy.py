from pathlib import Path
import struct
import tempfile
import unittest
import wave

import numpy as np

from soundsausage.audio import AudioError, read_wav, write_wav
from soundsausage.legacy import inspect_ses, load_legacy_project, MissingMediaError
from soundsausage.project import save_project, load_project


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "reference/vm-session-test"


@unittest.skipUnless((FIXTURES / "02-basis.ses").exists(), "User-provided SES reference files unavailable")
class LegacyTests(unittest.TestCase):
    def test_all_six_real_reference_sessions_are_inspectable(self):
        expected = [(0, 0), (1, 1), (2, 2), (2, 2), (2, 2), (2, 2)]
        for path, (tracks, clips) in zip(sorted(FIXTURES.glob("*.ses")), expected):
            report = inspect_ses(path)
            self.assertEqual(report["version"], "Cool Edit Pro 1.0")
            self.assertEqual(report["sample_rate"], 44100)
            self.assertEqual((len(report["tracks"]), len(report["blocks"])), (tracks, clips))

    def test_position_change_is_read_in_frames_without_rounding_to_seconds(self):
        before = inspect_ses(FIXTURES / "02-basis.ses")
        after = inspect_ses(FIXTURES / "03-verplaatst.ses")
        self.assertEqual(before["blocks"][1]["start"], 50809)
        self.assertEqual(after["blocks"][1]["start"], 88200)
        self.assertEqual(after["blocks"][1]["frames"], 132300)

    def test_baseline_mix_matches_original_vm_export_except_one_silent_tail_frame(self):
        reference_path = FIXTURES / "02-basis-mix.wav"
        reference = read_wav(reference_path)
        session = load_legacy_project(FIXTURES / "02-basis.ses")
        mixed = session.render()
        self.assertEqual(reference.sample_rate, session.sample_rate)
        self.assertEqual(reference.encoding, "pcm16")
        self.assertEqual(mixed.shape, (183109, 2))
        self.assertEqual(reference.samples.shape, (183110, 2))
        np.testing.assert_array_equal(mixed, reference.samples[:-1])
        np.testing.assert_array_equal(reference.samples[-1], [0, 0])

        # Also check the exported PCM bytes with an independent WAV reader.
        with wave.open(str(reference_path), "rb") as stream:
            expected_bytes = stream.readframes(len(mixed))
            self.assertEqual(stream.readframes(1), b"\0" * 4)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            exported = Path(folder) / "mix.wav"
            write_wav(exported, mixed, session.sample_rate, "pcm16")
            with wave.open(str(exported), "rb") as stream:
                self.assertEqual((stream.getnchannels(), stream.getsampwidth(), stream.getframerate()),
                                 (2, 2, 44100))
                self.assertEqual(stream.getnframes(), len(mixed))
                self.assertEqual(stream.readframes(len(mixed)), expected_bytes)

    def test_db_change_is_imported_as_the_recorded_linear_gain(self):
        session = load_legacy_project(FIXTURES / "04-volume.ses")
        clip = session.tracks[0].clips[0]
        self.assertAlmostEqual(clip.gain, 10 ** (13.93 / 20), places=12)
        source = read_wav(FIXTURES / "A-mono.wav").samples
        expected = np.repeat(source * np.float32(clip.gain), 2, axis=1)
        np.testing.assert_allclose(session.render(0, len(source)), expected, atol=1e-7)

    def test_right_pan_preserves_the_original_minus_100db_left_floor(self):
        session = load_legacy_project(FIXTURES / "05-pan.ses")
        clip = session.tracks[1].clips[0]
        source = read_wav(FIXTURES / "B-stereo.wav").samples
        mixed = session.render(clip.start, clip.end)
        expected = source.copy()
        expected[:, 0] *= 1e-5
        np.testing.assert_allclose(mixed, expected, atol=1e-10)

    def test_empty_file_reports_its_malformed_track_fields(self):
        path = FIXTURES / "00-leeg.ses"
        report = inspect_ses(path)
        self.assertTrue(report["warnings"])
        self.assertTrue(next(chunk for chunk in report["chunks"] if chunk["kind"] == "trks")["recovered_empty"])
        session = load_legacy_project(path)
        self.assertEqual(session.frames, 0)
        self.assertIsNone(session.path)

    def test_import_then_native_save_keeps_samples_and_session_mix(self):
        session = load_legacy_project(FIXTURES / "05-pan.ses")
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "converted.celp"
            save_project(session, path)
            reopened = load_project(path)
            np.testing.assert_array_equal(reopened.render(), session.render())
        self.assertEqual(len(session.tracks), 2)

    def test_missing_audio_can_be_resolved_with_an_explicit_folder(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "copy.ses"
            path.write_bytes((FIXTURES / "02-basis.ses").read_bytes())
            with self.assertRaises(MissingMediaError):
                load_legacy_project(path)
            loaded = load_legacy_project(path, media_dirs=[FIXTURES])
            self.assertEqual(len(loaded.media), 2)

    def test_nonflat_automation_is_rejected_instead_of_lost(self):
        original = FIXTURES / "02-basis.ses"
        data = bytearray(original.read_bytes())
        offset = data.find(b"envp") + 12 + 16 + 8
        struct.pack_into("<d", data, offset, 0.25)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "automation.ses"
            path.write_bytes(data)
            with self.assertRaisesRegex(AudioError, "automation"):
                load_legacy_project(path, media_dirs=[FIXTURES])

    def test_corrupt_chunk_length_is_rejected(self):
        data = bytearray((FIXTURES / "02-basis.ses").read_bytes())
        struct.pack_into("<I", data, 16, 0xffffffff)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "corrupt.ses"
            path.write_bytes(data)
            with self.assertRaises(AudioError):
                inspect_ses(path)


if __name__ == "__main__":
    unittest.main()
