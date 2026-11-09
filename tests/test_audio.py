from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import wave

import numpy as np

from soundsausage.audio import AudioError, AmbiguousWavError, read_wav, write_wav, tone


ROOT = Path(__file__).resolve().parents[1]


def carrier(fmt, payload, extras=b""):
    body = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
    body += extras + b"data" + struct.pack("<I", len(payload)) + payload
    if len(payload) & 1:
        body += b"\0"
    return b"RIFF" + struct.pack("<I", len(body)) + body


class AudioTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "build").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "build")
        self.path = Path(self.temp.name) / "test.wav"

    def tearDown(self):
        self.temp.cleanup()

    def test_pcm16_export_matches_independent_standard_library_reader(self):
        data = np.array([[-1, 1], [-0.5, 0.5], [0, 0]], np.float32)
        write_wav(self.path, data, 44100)
        with wave.open(str(self.path), "rb") as stream:
            self.assertEqual((stream.getnchannels(), stream.getsampwidth(), stream.getframerate()), (2, 2, 44100))
            self.assertEqual(struct.unpack("<6h", stream.readframes(3)), (-32768, 32767, -16384, 16384, 0, 0))

    def test_pcm24_signed_boundaries_and_stereo_order(self):
        samples = np.array([[-1, 0.5], [-1 / 8388608, 1 / 8388608]], np.float32)
        write_wav(self.path, samples, 48000, "pcm24")
        with wave.open(str(self.path), "rb") as stream:
            self.assertEqual(stream.readframes(2), bytes.fromhex("000080000040ffffff010000"))
        np.testing.assert_array_equal(read_wav(self.path).samples, samples)

    def test_pcm8_odd_chunk_padding_and_unsigned_silence(self):
        samples = np.array([[-1], [0], [0.5]], np.float32)
        write_wav(self.path, samples, 8000, "pcm8")
        np.testing.assert_array_equal(read_wav(self.path).samples, samples)
        self.assertEqual(self.path.stat().st_size % 2, 0)

    def test_float_roundtrip_preserves_headroom_and_every_sample(self):
        samples = np.array([[-1.75, 1.25], [0.0000123, -0.75]], np.float32)
        write_wav(self.path, samples, 96000, "float32")
        result = read_wav(self.path)
        self.assertEqual(result.encoding, "float32")
        np.testing.assert_array_equal(result.samples, samples)

    def test_ambiguous_type1_pcm32_requires_a_choice(self):
        fmt = struct.pack("<HHIIHH", 1, 1, 44100, 176400, 4, 32)
        self.path.write_bytes(carrier(fmt, struct.pack("<ii", -2147483648, 1073741824)))
        with self.assertRaises(AmbiguousWavError):
            read_wav(self.path)
        np.testing.assert_array_equal(read_wav(self.path, "integer").samples[:, 0], [-1, 0.5])

    def test_explicit_legacy_float_choice_uses_the_observed_scale(self):
        fmt = struct.pack("<HHIIHH", 1, 1, 44100, 176400, 4, 32)
        self.path.write_bytes(carrier(fmt, struct.pack("<ff", -32768, 8192)))
        result = read_wav(self.path, "cool-edit-float")
        np.testing.assert_array_equal(result.samples[:, 0], [-1, 0.25])
        self.assertEqual(result.encoding, "float32")

    def test_historical_24bit_float_container_is_not_misread_as_pcm24(self):
        fmt = struct.pack("<HHIIHH", 1, 1, 44100, 176400, 4, 24)
        self.path.write_bytes(carrier(fmt, struct.pack("<f", 1024)))
        with self.assertRaisesRegex(AudioError, "historical"):
            read_wav(self.path)

    def test_extensible_integer_pcm32_is_unambiguous(self):
        guid = bytes.fromhex("0100000000001000800000aa00389b71")
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, 44100, 176400, 4, 32, 22, 32, 4) + guid
        self.path.write_bytes(carrier(fmt, struct.pack("<i", -1073741824)))
        np.testing.assert_array_equal(read_wav(self.path).samples[:, 0], [-0.5])

    def test_unknown_metadata_is_reported_to_the_caller(self):
        fmt = struct.pack("<HHIIHH", 1, 1, 8000, 16000, 2, 16)
        self.path.write_bytes(carrier(fmt, b"\0\0", b"LIST\x04\0\0\0INFO"))
        self.assertEqual(read_wav(self.path).extra_chunks, ("LIST",))

    def test_truncated_and_partial_frames_are_rejected(self):
        fmt = struct.pack("<HHIIHH", 1, 2, 44100, 176400, 4, 16)
        self.path.write_bytes(carrier(fmt, b"\0\0"))
        with self.assertRaisesRegex(AudioError, "partial"):
            read_wav(self.path)
        self.path.write_bytes(self.path.read_bytes()[:-5])
        with self.assertRaises(AudioError):
            read_wav(self.path)

    def test_failed_atomic_save_keeps_the_existing_file(self):
        self.path.write_bytes(b"original file bytes")
        with patch("soundsausage.audio.os.replace", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                write_wav(self.path, np.zeros((10, 2), np.float32), 44100)
        self.assertEqual(self.path.read_bytes(), b"original file bytes")
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_nonfinite_audio_is_rejected_before_overwriting(self):
        self.path.write_bytes(b"keep this")
        with self.assertRaises(AudioError):
            write_wav(self.path, np.array([[np.nan]], np.float32), 44100)
        self.assertEqual(self.path.read_bytes(), b"keep this")

    def test_empty_document_can_be_saved_and_reopened(self):
        write_wav(self.path, np.empty((0, 2), np.float32), 44100)
        self.assertEqual(read_wav(self.path).samples.shape, (0, 2))

    def test_tone_has_the_requested_frequency_and_channel_values(self):
        samples = tone(1, 8000, 2, 1000, 0.25)
        self.assertEqual(samples.shape, (8000, 2))
        np.testing.assert_array_equal(samples[:, 0], samples[:, 1])
        self.assertEqual(int(np.argmax(np.abs(np.fft.rfft(samples[:, 0])))), 1000)
        self.assertAlmostEqual(float(np.max(samples)), 0.25)


if __name__ == "__main__":
    unittest.main()
