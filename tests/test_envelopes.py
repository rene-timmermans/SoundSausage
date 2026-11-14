from pathlib import Path
import json
import tempfile
import unittest
import zipfile

import numpy as np

from soundsausage.audio import AudioError
from soundsausage.envelopes import MAX_ENVELOPE_POINTS
from soundsausage.project import load_project, save_project
from soundsausage.session import Session


ROOT = Path(__file__).resolve().parents[1]


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.session = Session(8000, 2)
        self.clip_id = self.session.import_audio([(np.ones((9, 1), np.float32), 8000, "Constant")])[0]

    def test_linear_volume_and_pan_match_hand_calculated_channel_samples(self):
        s = self.session
        s.set_envelope(self.clip_id, "volume", ((0, 0), (8, 2)))
        s.set_envelope(self.clip_id, "pan", ((0, -1), (8, 1)))
        expected = [[0, 0], [.25, .0625], [.5, .25], [.75, .5625], [1, 1],
                    [.9375, 1.25], [.75, 1.5], [.4375, 1.75], [0, 2]]
        np.testing.assert_array_equal(s.render(), np.array(expected, np.float32))

    def test_points_hold_end_values_and_a_single_point_is_constant(self):
        self.session.set_envelope(self.clip_id, "volume", ((2, .25), (6, .75)))
        expected = [.25, .25, .25, .375, .5, .625, .75, .75, .75]
        np.testing.assert_array_equal(self.session.render()[:, 0], expected)
        self.session.set_envelope(self.clip_id, "volume", ((4, .125),))
        np.testing.assert_array_equal(self.session.render(), np.full((9, 2), .125, np.float32))
        self.session.set_envelope(self.clip_id, "volume", ())
        np.testing.assert_array_equal(self.session.render(), np.ones((9, 2), np.float32))

    def test_partial_renders_use_source_frames_and_keep_exact_interpolation(self):
        s = self.session
        s.set_envelope(self.clip_id, "volume", ((0, .137), (3, 1.47), (8, .271)))
        s.set_envelope(self.clip_id, "pan", ((1, -.67), (5, .39), (7, .98)))
        s.configure_clip(self.clip_id, start=3, source_start=1, source_end=8, gain=.81, fade_in=2, fade_out=2)
        full = s.render()
        np.testing.assert_array_equal(np.concatenate([s.render(0, 4), s.render(4, 7), s.render(7, 10)]), full)

    def test_envelopes_multiply_static_gain_balance_and_fades_without_clipping(self):
        s = self.session
        s.configure_clip(self.clip_id, gain=4, pan=-.5, fade_in=3, fade_out=3)
        s.configure_track(s.tracks[0].id, gain=.5, pan=.5)
        s.set_envelope(self.clip_id, "volume", ((0, 2), (8, 2)))
        s.set_envelope(self.clip_id, "pan", ((0, -.5), (8, -.5)))
        expected = np.array([0, .5, 1, 1, 1, 1, 1, .5, 0])
        np.testing.assert_array_equal(s.render()[:, 0], expected * 2)
        np.testing.assert_array_equal(s.render()[:, 1], expected)

    def test_stereo_pan_keeps_channels_separate(self):
        s = Session(8000, 1)
        clip = s.import_audio([(np.tile(np.array([[.25, .75]], np.float32), (3, 1)), 8000, "Stereo")])[0]
        s.set_envelope(clip, "pan", ((0, -1), (2, 1)))
        np.testing.assert_array_equal(s.render(), [[.25, 0], [.25, .75], [0, .75]])

    def test_move_trim_reveal_and_duplicate_keep_source_anchored_points(self):
        s = self.session
        points = ((0, 0), (4, 1), (8, 0))
        s.set_envelope(self.clip_id, "volume", points)
        full = s.render().copy()
        s.move_clip(self.clip_id, 10)
        s.trim_clip(self.clip_id, 12, 17)
        self.assertEqual(s.find_clip(self.clip_id)[1].volume_envelope, points)
        np.testing.assert_array_equal(s.render(12, 17), full[2:7])
        s.trim_clip(self.clip_id, 10, 19)
        np.testing.assert_array_equal(s.render(10, 19), full)
        duplicate = s.duplicate_clip(self.clip_id)
        s.set_envelope(duplicate, "volume", ((0, .5),))
        self.assertEqual(s.find_clip(self.clip_id)[1].volume_envelope, points)
        np.testing.assert_array_equal(s.render(19, 28), np.full((9, 2), .5))
        s.undo()
        np.testing.assert_array_equal(s.render(19, 28), full)

    def test_replacing_trimmed_audio_rescales_visible_curves_and_undo_restores_them(self):
        s = self.session
        s.set_envelope(self.clip_id, "volume", ((0, 0), (4, 1), (8, 0)))
        s.set_envelope(self.clip_id, "pan", ((0, -1), (8, 1)))
        s.trim_clip(self.clip_id, 2, 7)
        old = s.find_clip(self.clip_id)[1]
        s.replace_clip_audio(self.clip_id, np.ones((9, 1), np.float32), 8000)
        clip = s.find_clip(self.clip_id)[1]
        self.assertEqual(clip.volume_envelope, ((0, .5), (4, 1), (8, .5)))
        self.assertEqual(clip.pan_envelope, ((0, -.5), (8, .5)))
        s.undo()
        self.assertEqual(s.find_clip(self.clip_id)[1], old)

    def test_replacing_audio_with_one_frame_preserves_its_initial_envelope_value(self):
        self.session.set_envelope(self.clip_id, "volume", ((0, .25), (8, 1)))
        self.session.replace_clip_audio(self.clip_id, np.ones((1, 1), np.float32), 8000)
        np.testing.assert_array_equal(self.session.render(), [[.25, .25]])

    def test_invalid_curves_leave_audio_history_and_dirty_state_intact(self):
        s = self.session
        s.mark_saved()
        before, history = s.render(), len(s.undo_stack)
        for points in (None, ((-1, .5),), ((9, .5),), ((True, .5),), ((2, .5), (1, .5)),
                       ((2, .5), (2, 1)), ((0, float("nan")),), ((0, 2.1),),
                       ((0, True),), tuple((0, 1) for _ in range(MAX_ENVELOPE_POINTS + 1))):
            with self.subTest(points=str(points)[:80]), self.assertRaises(AudioError):
                s.set_envelope(self.clip_id, "volume", points)
        self.assertFalse(s.dirty)
        self.assertEqual(len(s.undo_stack), history)
        np.testing.assert_array_equal(s.render(), before)

    def test_maximum_interior_points_stay_bounded_when_audio_is_replaced(self):
        s = Session(8000)
        clip = s.import_audio([(np.ones((514, 1), np.float32), 8000, "Many")])[0]
        s.set_envelope(clip, "volume", tuple((i + 1, i / 512) for i in range(512)))
        s.replace_clip_audio(clip, np.ones((1028, 1), np.float32), 8000)
        self.assertLessEqual(len(s.find_clip(clip)[1].volume_envelope), 512)
        self.assertTrue(np.isfinite(s.render()).all())


class EnvelopeProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "build")
        self.path = Path(self.temp.name) / "curves.celp"
        self.session = Session(8000, 1)
        self.clip_id = self.session.import_audio([(np.ones((9, 1), np.float32), 8000, "Test")])[0]

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, change):
        with zipfile.ZipFile(self.path) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        record = json.loads(files["project.json"])
        change(record)
        files["project.json"] = json.dumps(record).encode()
        with zipfile.ZipFile(self.path, "w") as archive:
            for name, data in files.items():
                archive.writestr(name, data)

    def test_current_version_roundtrip_keeps_immutable_points_and_exact_mix(self):
        self.session.set_envelope(self.clip_id, "volume", [[0, 0], [4, 1], [8, .5]])
        self.session.set_envelope(self.clip_id, "pan", [[0, -1], [8, 1]])
        expected = self.session.render()
        save_project(self.session, self.path)
        restored = load_project(self.path)
        self.assertEqual(restored.tracks, self.session.tracks)
        np.testing.assert_array_equal(restored.render(), expected)
        self.assertFalse(restored.dirty)
        with zipfile.ZipFile(self.path) as archive:
            self.assertEqual(json.loads(archive.read("project.json"))["version"], 6)

    def test_version_one_projects_load_with_neutral_curves(self):
        save_project(self.session, self.path)
        def old(record):
            record["version"] = 1
            clip = record["tracks"][0]["clips"][0]
            del clip["volume_envelope"], clip["pan_envelope"]
        self.mutate(old)
        restored = load_project(self.path)
        np.testing.assert_array_equal(restored.render(), self.session.render())
        self.assertEqual(restored.find_clip(self.clip_id)[1].volume_envelope, ())

    def test_malformed_curves_and_missing_fields_are_rejected(self):
        for points in ([[1, .5], [1, 1]], [[9, .5]], [[0, 3]], "bad", None):
            with self.subTest(points=points):
                save_project(self.session, self.path)
                self.mutate(lambda r: r["tracks"][0]["clips"][0].update(volume_envelope=points))
                with self.assertRaises(AudioError):
                    load_project(self.path)
        save_project(self.session, self.path)
        self.mutate(lambda r: r["tracks"][0]["clips"][0].pop("pan_envelope"))
        with self.assertRaises(AudioError):
            load_project(self.path)

    def test_envelopes_cannot_be_mislabelled_as_version_one(self):
        self.session.set_envelope(self.clip_id, "pan", ((0, -1), (8, 1)))
        save_project(self.session, self.path)
        self.mutate(lambda r: r.update(version=1))
        with self.assertRaisesRegex(AudioError, "version 1"):
            load_project(self.path)


if __name__ == "__main__":
    unittest.main()
