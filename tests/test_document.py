import unittest

import numpy as np

from soundsausage.audio import AudioError
from soundsausage.document import Document, Clip


class DocumentTests(unittest.TestCase):
    def setUp(self):
        left = np.arange(8, dtype=np.float32) / 10
        self.original = np.column_stack((left, -left))
        self.doc = Document(self.original, 44100)

    def test_cut_paste_undo_redo_and_saved_state(self):
        self.doc.select(2, 5)
        clip = self.doc.cut()
        np.testing.assert_array_equal(clip.samples, self.original[2:5])
        np.testing.assert_array_equal(self.doc.read(), self.original[[0, 1, 5, 6, 7]])
        self.assertEqual(self.doc.selection, (2, 2))
        self.doc.paste(clip)
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertEqual(self.doc.selection, (2, 5))
        self.assertTrue(self.doc.dirty)
        self.doc.undo()
        self.assertEqual(self.doc.frames, 5)
        self.doc.undo()
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertFalse(self.doc.dirty)
        self.doc.redo()
        self.assertTrue(self.doc.dirty)
        self.assertEqual(self.doc.frames, 5)

    def test_trim_and_undo_preserve_both_channels_and_the_selection(self):
        self.doc.select(1, 7)
        self.doc.trim()
        np.testing.assert_array_equal(self.doc.read(), self.original[1:7])
        self.doc.undo()
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertEqual(self.doc.selection, (1, 7))

    def test_gain_touches_only_the_selected_frames_and_keeps_headroom(self):
        self.doc.select(2, 6)
        self.doc.apply("gain", initial=(0, 2), final=(1, 4))
        expected = self.original.copy()
        expected[2:6, 0] *= np.linspace(0, 1, 4)
        expected[2:6, 1] *= np.linspace(2, 4, 4)
        np.testing.assert_allclose(self.doc.read(), expected, rtol=1e-6)
        self.assertLess(float(np.min(self.doc.read())), -1)

    def test_reverse_reverses_frames_instead_of_swapping_channels(self):
        self.doc.select(2, 6)
        self.doc.apply("reverse")
        expected = self.original.copy()
        expected[2:6] = expected[2:6][::-1]
        np.testing.assert_array_equal(self.doc.read(), expected)

    def test_normalization_can_link_or_separate_stereo(self):
        data = np.array([[0.5, -0.25], [-0.1, 0.1]], np.float32)
        linked = Document(data)
        linked.apply("normalize", target=1, linked=True)
        np.testing.assert_allclose(linked.read(), [[1, -0.5], [-0.2, 0.2]])
        independent = Document(data)
        independent.apply("normalize", target=1, linked=False)
        np.testing.assert_allclose(independent.read(), [[1, -1], [-0.2, 0.4]])

    def test_normalizing_silence_does_not_create_nan(self):
        doc = Document(np.zeros((10, 1), np.float32))
        doc.apply("normalize")
        np.testing.assert_array_equal(doc.read(), np.zeros((10, 1)))

    def test_invalid_effect_does_not_change_data_or_history(self):
        self.doc.select(1, 5)
        with self.assertRaises(ValueError):
            self.doc.apply("gain", initial=-1)
        np.testing.assert_array_equal(self.doc.read(), self.original)
        self.assertFalse(self.doc.dirty)
        self.assertFalse(self.doc.undo_stack)

    def test_mix_paste_extends_at_the_end_without_shifting_existing_frames(self):
        self.doc.select(6, 6)
        clip = Clip(np.ones((4, 2), np.float32) * 0.25, 44100)
        self.doc.paste(clip, mix=True)
        expected = np.zeros((10, 2), np.float32)
        expected[:8] = self.original
        expected[6:10] += 0.25
        np.testing.assert_array_equal(self.doc.read(), expected)

    def test_clipboard_mismatch_is_rejected_without_an_edit(self):
        with self.assertRaises(AudioError):
            self.doc.paste(Clip(np.zeros((5, 1), np.float32), 48000))
        self.assertFalse(self.doc.dirty)

    def test_a_new_edit_after_undo_discards_redo_history(self):
        self.doc.apply("invert")
        self.doc.undo()
        self.doc.apply("silence")
        self.assertFalse(self.doc.redo_stack)
        np.testing.assert_array_equal(self.doc.read(), np.zeros_like(self.original))

    def test_repeat_uses_the_new_selection(self):
        self.doc.select(0, 2)
        self.doc.apply("invert")
        self.doc.select(4, 6)
        self.doc.repeat()
        expected = self.original.copy()
        expected[:2] *= -1
        expected[4:6] *= -1
        np.testing.assert_array_equal(self.doc.read(), expected)

    def test_new_samples_and_clipboard_do_not_alias_mutable_callers(self):
        self.original[:] = 0
        self.assertGreater(float(self.doc.read()[-1, 0]), 0)
        self.doc.select(2, 4)
        clip = self.doc.copy()
        self.assertFalse(clip.samples.flags.writeable)

    def test_single_frame_fade_and_empty_document_are_defined(self):
        doc = Document(np.ones((1, 1), np.float32))
        doc.apply("gain", initial=0.5, final=0)
        np.testing.assert_array_equal(doc.read(), [[0.5]])
        empty = Document()
        empty.apply("reverse")
        self.assertFalse(empty.dirty)

    def test_zero_crossing_adjustment_keeps_an_exact_zero_at_the_start(self):
        doc = Document(np.array([[0], [0.2], [-0.1], [0.3], [0], [-0.4]], np.float32))
        doc.select(0, 6)
        doc.zero_crossings()
        self.assertEqual(doc.selection, (0, 4))


if __name__ == "__main__":
    unittest.main()
