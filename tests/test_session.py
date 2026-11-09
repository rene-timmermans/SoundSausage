from pathlib import Path
from dataclasses import replace
import io
import json
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np

from soundsausage.audio import AudioError, read_wav
from soundsausage.project import save_project, load_project
from soundsausage.session import Session


ROOT = Path(__file__).resolve().parents[1]


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.session = Session(8000)
        self.mono = np.array([[0.2], [0.4], [-0.4], [-0.2]], np.float32)

    def add(self, data=None, track=0, start=0):
        source = self.mono if data is None else data
        return self.session.import_audio([(source, 8000, "Test")], self.session.tracks[track].id, start)[0]

    def test_overlapping_clips_mix_by_frame_without_clipping_headroom(self):
        self.add(np.ones((4, 1), np.float32))
        self.add(np.ones((4, 2), np.float32) * 0.5, 1, 2)
        expected = np.array([[1, 1], [1, 1], [1.5, 1.5], [1.5, 1.5], [0.5, 0.5], [0.5, 0.5]], np.float32)
        np.testing.assert_array_equal(self.session.render(), expected)

    def test_track_and_clip_balance_and_gain_combine(self):
        clip_id = self.add(np.ones((4, 1), np.float32))
        self.session.configure_clip(clip_id, gain=2, pan=-0.5)
        self.session.configure_track(self.session.tracks[0].id, gain=0.5, pan=0.5)
        np.testing.assert_array_equal(self.session.render(), np.tile([0.5, 0.5], (4, 1)))

    def test_stereo_hard_right_keeps_right_channel_without_crossfeed(self):
        clip_id = self.add(np.array([[0.25, 0.75]], np.float32))
        self.session.configure_clip(clip_id, pan=1)
        np.testing.assert_array_equal(self.session.render(), [[0, 0.75]])

    def test_mute_and_solo_are_applied_before_mixing(self):
        self.add(np.ones((4, 1), np.float32) * 0.25)
        self.add(np.ones((4, 1), np.float32) * 0.5, 1)
        second = self.session.tracks[1].id
        self.session.configure_track(second, solo=True)
        np.testing.assert_array_equal(self.session.render(), np.ones((4, 2)) * 0.5)
        self.session.configure_track(second, muted=True)
        np.testing.assert_array_equal(self.session.render(), np.zeros((4, 2)))

    def test_fades_use_absolute_clip_positions_in_partial_renders(self):
        clip_id = self.add(np.ones((12, 1), np.float32), start=3)
        self.session.configure_clip(clip_id, fade_in=4, fade_out=4)
        full = self.session.render()
        pieces = [self.session.render(0, 5), self.session.render(5, 10), self.session.render(10, 15)]
        np.testing.assert_array_equal(np.concatenate(pieces), full)
        np.testing.assert_allclose(full[3:7, 0], [0, 1 / 3, 2 / 3, 1])
        np.testing.assert_allclose(full[11:15, 0], [1, 2 / 3, 1 / 3, 0])

    def test_move_and_trim_leave_the_source_unchanged_and_can_be_undone(self):
        clip_id = self.add()
        source_id = self.session.find_clip(clip_id)[1].media_id
        self.session.mark_saved()
        self.session.move_clip(clip_id, 10, self.session.tracks[1].id)
        self.session.trim_clip(clip_id, 11, 13)
        np.testing.assert_array_equal(self.session.render(11, 13), np.repeat(self.mono[1:3], 2, axis=1))
        np.testing.assert_array_equal(self.session.media[source_id].samples, self.mono)
        self.assertFalse(self.session.media[source_id].samples.flags.writeable)
        self.session.undo()
        self.session.undo()
        self.assertFalse(self.session.dirty)
        self.assertEqual(self.session.find_clip(clip_id)[0].id, self.session.tracks[0].id)
        np.testing.assert_array_equal(self.session.render(), np.repeat(self.mono, 2, axis=1))

    def test_trim_can_reveal_original_audio_again(self):
        clip_id = self.add(start=4)
        self.session.trim_clip(clip_id, 5, 7)
        self.session.trim_clip(clip_id, 4, 8)
        self.assertEqual(self.session.find_clip(clip_id)[1].source_start, 0)
        np.testing.assert_array_equal(self.session.render(4, 8), np.repeat(self.mono, 2, axis=1))

    def test_duplicate_reuses_media_and_replaces_only_the_edited_copy(self):
        clip_id = self.add()
        duplicate = self.session.duplicate_clip(clip_id)
        self.assertEqual(len(self.session.media), 1)
        self.session.replace_clip_audio(duplicate, np.ones((2, 1), np.float32), 8000)
        np.testing.assert_array_equal(self.session.render(0, 4), np.repeat(self.mono, 2, axis=1))
        np.testing.assert_array_equal(self.session.render(4, 6), np.ones((2, 2)))
        self.session.undo()
        np.testing.assert_array_equal(self.session.render(4, 8), np.repeat(self.mono, 2, axis=1))

    def test_removing_a_track_is_undoable(self):
        clip_id = self.add(track=1)
        self.session.remove_track(self.session.tracks[1].id)
        self.assertEqual(self.session.frames, 0)
        self.session.undo()
        self.assertEqual(self.session.find_clip(clip_id)[0].name, "Track 2")

    def test_import_of_multiple_files_is_atomic_on_rate_mismatch(self):
        with self.assertRaises(AudioError):
            self.session.import_audio([(self.mono, 8000, "A"), (self.mono, 44100, "B")])
        self.assertFalse(self.session.dirty)
        self.assertEqual(len(self.session.media), 0)

    def test_first_import_adopts_rate_and_undo_restores_it(self):
        self.session.import_audio([(self.mono, 48000, "First")])
        self.assertEqual(self.session.sample_rate, 48000)
        self.session.undo()
        self.assertEqual(self.session.sample_rate, 8000)
        self.session.redo()
        self.assertEqual(self.session.sample_rate, 48000)

    def test_explicitly_chosen_session_rate_is_not_changed_by_import(self):
        session = Session(44100, adopt_first_rate=False)
        with self.assertRaises(AudioError):
            session.import_audio([(self.mono, 48000, "Different rate")])
        self.assertEqual(session.sample_rate, 44100)
        self.assertFalse(session.dirty)

    def test_invalid_settings_preserve_the_previous_session(self):
        clip_id = self.add()
        self.session.mark_saved()
        before = self.session.render()
        for settings in ({"start": -1}, {"source_end": 100}, {"gain": float("nan")}, {"fade_in": 3, "fade_out": 3}):
            with self.assertRaises(AudioError):
                self.session.configure_clip(clip_id, **settings)
        np.testing.assert_array_equal(self.session.render(), before)
        self.assertFalse(self.session.dirty)

    def test_undo_restores_the_time_selection(self):
        clip_id = self.add()
        self.session.select(1, 3)
        self.session.configure_track(self.session.tracks[0].id, gain=0.5)
        self.session.select(0, 4)
        self.session.undo()
        self.assertEqual(self.session.selection, (1, 3))

    def test_shortening_a_faded_clip_keeps_valid_fade_lengths(self):
        clip_id = self.add(np.ones((10, 1), np.float32))
        self.session.configure_clip(clip_id, fade_in=4, fade_out=4)
        self.session.trim_clip(clip_id, 3, 6)
        clip = self.session.find_clip(clip_id)[1]
        self.assertLessEqual(clip.fade_in + clip.fade_out, clip.frames)
        self.assertEqual(self.session.render(3, 6).shape, (3, 2))


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "build")
        self.path = Path(self.temp.name) / "session.celp"
        self.session = Session(8000)
        data = np.array([[1.5, -1.25], [0.25, -0.125], [0, 0], [-0.5, 0.75]], np.float32)
        self.clip = self.session.import_audio([(data, 8000, "Audio α.wav")])[0]
        self.session.configure_clip(self.clip, start=5, source_start=1, source_end=4, gain=0.75, pan=-0.2, fade_in=1, fade_out=1)
        self.session.configure_track(self.session.tracks[0].id, name="Stem α", gain=0.5, pan=0.25, solo=True)

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, change):
        with zipfile.ZipFile(self.path) as archive:
            contents = {name: archive.read(name) for name in archive.namelist()}
        manifest = json.loads(contents["project.json"])
        change(manifest)
        contents["project.json"] = json.dumps(manifest).encode()
        with zipfile.ZipFile(self.path, "w") as archive:
            for name, data in contents.items():
                archive.writestr(name, data)

    def test_portable_roundtrip_preserves_audio_positions_names_and_mix(self):
        expected = self.session.render()
        save_project(self.session, self.path)
        loaded = load_project(self.path)
        self.assertEqual(loaded.tracks, self.session.tracks)
        self.assertFalse(loaded.dirty)
        self.assertEqual(loaded.sample_rate, 8000)
        np.testing.assert_array_equal(loaded.render(), expected)
        source_id = self.session.find_clip(self.clip)[1].media_id
        np.testing.assert_array_equal(loaded.media[source_id].samples, self.session.media[source_id].samples)
        with zipfile.ZipFile(self.path) as archive:
            audio = read_wav(io.BytesIO(archive.read(f"media/{source_id}.wav")))
            self.assertEqual(audio.encoding, "float32")
            self.assertGreater(float(np.max(audio.samples)), 1)

    def test_empty_session_roundtrip(self):
        save_project(Session(44100, 3), self.path)
        loaded = load_project(self.path)
        self.assertEqual(len(loaded.tracks), 3)
        self.assertEqual(loaded.frames, 0)
        self.assertEqual(loaded.render().shape, (0, 2))
        with self.assertRaises(AudioError):
            loaded.import_audio([(np.zeros((10, 1), np.float32), 48000, "Different rate")])

    def test_deleted_media_in_undo_history_is_not_saved(self):
        self.session.remove_clip(self.clip)
        self.assertTrue(self.session.media)
        save_project(self.session, self.path)
        with zipfile.ZipFile(self.path) as archive:
            self.assertEqual(archive.namelist(), ["project.json"])
        self.assertEqual(len(load_project(self.path).media), 0)

    def test_failed_save_preserves_existing_file_and_dirty_state(self):
        self.path.write_bytes(b"keep existing project")
        with patch("soundsausage.project.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                save_project(self.session, self.path)
        self.assertEqual(self.path.read_bytes(), b"keep existing project")
        self.assertTrue(self.session.dirty)
        self.assertIsNone(self.session.path)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_future_version_is_rejected(self):
        save_project(self.session, self.path)
        self.mutate(lambda manifest: manifest.update(version=99))
        with self.assertRaisesRegex(AudioError, "version"):
            load_project(self.path)

    def test_missing_media_is_rejected(self):
        save_project(self.session, self.path)
        self.mutate(lambda manifest: manifest["tracks"][0]["clips"][0].update(media_id="0" * 32))
        with self.assertRaisesRegex(AudioError, "missing"):
            load_project(self.path)

    def test_out_of_bounds_source_range_is_rejected(self):
        save_project(self.session, self.path)
        self.mutate(lambda manifest: manifest["tracks"][0]["clips"][0].update(source_end=99999))
        with self.assertRaises(AudioError):
            load_project(self.path)

    def test_invalid_pan_is_rejected(self):
        save_project(self.session, self.path)
        self.mutate(lambda manifest: manifest["tracks"][0].update(pan=2))
        with self.assertRaises(AudioError):
            load_project(self.path)

    def test_archive_paths_cannot_redirect_media_reads(self):
        save_project(self.session, self.path)
        self.mutate(lambda manifest: manifest["media"][0].update(file="../../outside.wav"))
        with self.assertRaises(AudioError):
            load_project(self.path)

    def test_duplicate_clip_ids_are_rejected(self):
        save_project(self.session, self.path)
        def duplicate(manifest):
            manifest["tracks"][1]["clips"].append(dict(manifest["tracks"][0]["clips"][0]))
        self.mutate(duplicate)
        with self.assertRaisesRegex(AudioError, "Duplicate clip"):
            load_project(self.path)


if __name__ == "__main__":
    unittest.main()
