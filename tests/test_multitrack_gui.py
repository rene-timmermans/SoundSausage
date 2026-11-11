from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

import numpy as np
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QDialogButtonBox, QSpinBox, QDoubleSpinBox

from soundsausage.audio import read_wav
from soundsausage.document import Document
from soundsausage.multitrack import RULER, ROW
from soundsausage.project import save_project
from soundsausage.window import MainWindow


ROOT = Path(__file__).resolve().parents[1]


class MultitrackGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        t = np.arange(8000) / 8000
        self.data = (0.25 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)[:, None]
        self.window = MainWindow(Document(self.data, 8000), no_audio=True)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.document.mark_saved()
        self.window.session.mark_saved()
        self.window.close()
        self.app.processEvents()

    def insert(self):
        self.window.insert_waveform()
        self.app.processEvents()
        return self.window.session.selected_clip

    def test_insert_current_waveform_switches_mode_and_undo_targets_session(self):
        self.insert()
        self.assertEqual(self.window.mode, "multitrack")
        self.assertEqual(self.window.session.frames, 8000)
        self.assertFalse(self.window.actions["cut"].isEnabled())
        self.assertTrue(self.window.actions["clip_properties"].isEnabled())
        self.window.actions["undo"].trigger()
        self.assertEqual(self.window.session.frames, 0)
        np.testing.assert_array_equal(self.window.document.read(), self.data)
        self.window.actions["redo"].trigger()
        self.assertEqual(self.window.session.frames, 8000)

    def test_drag_moves_a_clip_to_another_track_as_one_undo_step(self):
        clip_id = self.insert()
        timeline = self.window.multitrack.timeline
        original = self.window.session.find_clip(clip_id)[1]
        rect = timeline.clip_rect(original, 0)
        begin = QPoint(round(rect.center().x()), round(rect.center().y()))
        end = QPoint(begin.x() + 90, begin.y() + ROW)
        before = len(self.window.session.undo_stack)
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(timeline, end, 20)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=end)
        track, clip = self.window.session.find_clip(clip_id)
        self.assertEqual(track.id, self.window.session.tracks[1].id)
        self.assertGreater(clip.start, original.start)
        self.assertEqual(len(self.window.session.undo_stack), before + 1)
        self.window.actions["undo"].trigger()
        self.assertEqual(self.window.session.find_clip(clip_id)[1].start, 0)

    def test_dragging_an_edge_trims_without_modifying_source(self):
        clip_id = self.insert()
        timeline = self.window.multitrack.timeline
        original = self.window.session.find_clip(clip_id)[1]
        rect = timeline.clip_rect(original, 0)
        begin = QPoint(round(rect.right()) - 1, round(rect.center().y()))
        end = QPoint(begin.x() - 60, begin.y())
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(timeline, end, 20)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=end)
        clip = self.window.session.find_clip(clip_id)[1]
        self.assertLess(clip.frames, original.frames)
        np.testing.assert_array_equal(self.window.session.media[clip.media_id].samples, self.data)

    def test_editing_a_copy_is_explicit_and_apply_is_undoable(self):
        clip_id = self.insert()
        before = self.window.session.render()
        self.window.edit_clip_copy(clip_id)
        self.assertEqual(self.window.mode, "waveform")
        self.window.effect("invert")
        np.testing.assert_array_equal(self.window.session.render(), before)
        self.window.apply_waveform_to_clip()
        self.assertEqual(self.window.mode, "multitrack")
        np.testing.assert_array_equal(self.window.session.render(), -before)
        self.window.actions["undo"].trigger()
        np.testing.assert_array_equal(self.window.session.render(), before)

    def test_ctrl_s_saves_a_project_in_multitrack_mode(self):
        self.insert()
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "saved.celp"
            self.window.session.path = path
            self.window.actions["save"].trigger()
            self.assertTrue(path.exists())
            self.assertFalse(self.window.session.dirty)
            self.assertIsNone(self.window.document.path)
            self.assertTrue(self.window.load_session_path(path))
            np.testing.assert_array_equal(self.window.session.render(), np.repeat(self.data, 2, axis=1))

    def test_canceling_a_session_close_keeps_the_window_open(self):
        self.insert()
        with patch("soundsausage.session_actions.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
            self.window.close()
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.session.dirty)

    def test_bad_project_does_not_replace_the_current_session(self):
        self.insert()
        previous = self.window.session
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "broken.celp"
            path.write_bytes(b"not a project")
            with patch.object(self.window, "error"):
                self.assertFalse(self.window.load_session_path(path))
        self.assertIs(self.window.session, previous)

    def test_mixdown_exports_the_entire_session_as_audio(self):
        self.insert()
        # The selected clip need not include the session's complete time range.
        self.window.session.move_clip(self.window.session.selected_clip, 4000)
        self.window.session.select(4500, 5000)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "mix.wav"
            with patch.object(self.window, "_save_path", return_value=(path, "float32")):
                self.window.mixdown()
            result = read_wav(path)
            np.testing.assert_array_equal(result.samples, self.window.session.render())
            self.assertEqual(len(result.samples), 12000)

    def test_pcm16_session_exports_match_original_volume_and_pan_mixes(self):
        fixtures = ROOT / "reference/vm-session-test"
        for session_name, reference_name in (("04-volume.ses", "04-volume-mix.wav"),
                                             ("05-pan.ses", "05-mix-down.wav")):
            with self.subTest(session=session_name), tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
                self.assertTrue(self.window.load_session_path(fixtures / session_name))
                before = self.window.session.render()
                self.assertGreater(float(np.max(np.abs(before))), 1.0)
                path = Path(folder) / "mix.wav"
                with patch.object(self.window, "_save_path", return_value=(path, "pcm16")):
                    self.window.actions["mixdown"].trigger()
                with wave.open(str(fixtures / reference_name), "rb") as original, wave.open(str(path), "rb") as exported:
                    self.assertEqual(exported.getparams()[:3], original.getparams()[:3])
                    self.assertEqual(exported.getnframes(), 220500)
                    self.assertEqual(original.getnframes(), 220501)
                    self.assertEqual(exported.readframes(220500), original.readframes(220500))
                    self.assertEqual(original.readframes(1), b"\0" * 4)
                # Export saturation must not alter the session's audio or headroom.
                np.testing.assert_array_equal(self.window.session.render(), before)
                with patch.object(self.window, "_save_path", return_value=(path, "float32")):
                    self.window.actions["mixdown"].trigger()
                np.testing.assert_array_equal(read_wav(path).samples, before)

    def test_track_volume_control_updates_the_actual_mix(self):
        self.insert()
        control = self.window.multitrack.timeline._controls[0]
        control.volume.setValue(50)
        control.volume.editingFinished.emit()
        self.assertEqual(self.window.session.tracks[0].gain, 0.5)
        np.testing.assert_array_equal(self.window.session.render(), np.repeat(self.data * 0.5, 2, axis=1))

    def test_switching_back_restores_waveform_effect_actions(self):
        self.insert()
        self.assertFalse(self.window.actions["amplify"].isEnabled())
        self.window.set_mode("waveform")
        self.assertTrue(self.window.actions["amplify"].isEnabled())
        self.assertTrue(self.window.actions["tone"].isEnabled())
        self.assertTrue(self.window.effects_toolbar.isVisible())
        self.window.effect("invert")
        np.testing.assert_array_equal(self.window.document.read(), -self.data)

    def test_waveform_save_prompt_in_multitrack_does_not_save_the_wrong_document(self):
        self.insert()
        self.window.document.apply("invert")
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            wave_path = Path(folder) / "wave.wav"
            session_path = Path(folder) / "project.celp"
            self.window.document.path = wave_path
            self.window.session.path = session_path
            with patch("soundsausage.window.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
                self.assertTrue(self.window._confirm_discard())
            self.assertTrue(wave_path.exists())
            self.assertFalse(session_path.exists())
            self.assertTrue(self.window.session.dirty)

    def test_legacy_session_opens_in_multitrack_without_overwriting_its_path(self):
        source = ROOT / "reference/vm-session-test/02-basis.ses"
        if not source.exists():
            self.skipTest("User-provided SES fixture unavailable")
        self.assertTrue(self.window.load_path(source))
        self.assertEqual(self.window.mode, "multitrack")
        self.assertIsNone(self.window.session.path)
        self.assertEqual(len(self.window.session.tracks), 2)
        self.assertEqual(self.window.session.tracks[1].clips[0].start, 50809)

    def test_accepting_unchanged_properties_preserves_imported_gain_precision(self):
        source = ROOT / "reference/vm-session-test/05-pan.ses"
        if not source.exists():
            self.skipTest("User-provided SES fixture unavailable")
        self.assertTrue(self.window.load_session_path(source))
        session = self.window.session
        session.choose_clip(session.tracks[1].clips[0].id)
        before = session.tracks
        def accept_dialog():
            dialog = QApplication.activeModalWidget()
            box = dialog.findChild(QDialogButtonBox)
            box.button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept_dialog)
        self.window.multitrack.properties()
        self.assertEqual(session.tracks, before)
        self.assertFalse(session.dirty)

    def test_volume_line_drag_previews_without_changing_audio_and_commits_one_undo(self):
        clip_id = self.insert()
        s = self.window.session
        s.mark_saved()
        before, history = s.render().copy(), len(s.undo_stack)
        editor = self.window.multitrack
        QTest.mouseClick(editor.envelope_buttons["volume"], Qt.MouseButton.LeftButton)
        timeline = editor.timeline
        clip = s.find_clip(clip_id)[1]
        body = timeline.envelope_rect(clip, 0)
        begin = QPoint(round(body.left() + body.width() * .4), round(body.center().y()))
        end = QPoint(begin.x() + 18, round(body.top() + body.height() * .8))
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(timeline, end, 20)
        self.assertFalse(s.dirty)
        self.assertEqual(s.find_clip(clip_id)[1].volume_envelope, ())
        np.testing.assert_array_equal(s.render(), before)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=end)
        self.assertEqual(len(s.undo_stack), history + 1)
        self.assertEqual(len(s.find_clip(clip_id)[1].volume_envelope), 3)
        self.assertGreater(float(np.max(np.abs(s.render() - before))), .05)
        self.assertTrue(editor.reset_line.isEnabled())
        self.window.actions["undo"].trigger()
        self.assertFalse(s.dirty)
        np.testing.assert_array_equal(s.render(), before)

    def test_pan_points_and_delete_affect_the_line_without_removing_the_clip(self):
        clip_id = self.insert()
        editor = self.window.multitrack
        QTest.mouseClick(editor.envelope_buttons["pan"], Qt.MouseButton.LeftButton)
        timeline = editor.timeline
        clip = self.window.session.find_clip(clip_id)[1]
        body = timeline.envelope_rect(clip, 0)
        at = QPoint(round(body.center().x()), round(body.top() + 1))
        QTest.mouseClick(timeline, Qt.MouseButton.LeftButton, pos=at)
        points = self.window.session.find_clip(clip_id)[1].pan_envelope
        self.assertEqual(len(points), 3)
        self.assertGreater(points[1][1], .9)
        frame = points[1][0] + 2
        mixed = self.window.session.render(frame, frame + 1)[0]
        self.assertLess(abs(mixed[0]), abs(mixed[1]) * .1)
        QTest.keyClick(timeline, Qt.Key.Key_Delete)
        self.assertEqual(len(self.window.session.find_clip(clip_id)[1].pan_envelope), 2)
        QTest.keyClick(timeline, Qt.Key.Key_Delete)
        self.assertEqual(self.window.session.find_clip(clip_id)[1].id, clip_id)
        self.window.actions["undo"].trigger()
        self.assertEqual(self.window.session.find_clip(clip_id)[1].pan_envelope, points)

    def test_escape_discards_an_uncommitted_line_drag(self):
        clip_id = self.insert()
        editor = self.window.multitrack
        editor.set_envelope_mode("volume")
        timeline = editor.timeline
        clip = self.window.session.find_clip(clip_id)[1]
        body = timeline.envelope_rect(clip, 0)
        begin = QPoint(round(body.center().x()), round(body.top() + 2))
        history = len(self.window.session.undo_stack)
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(timeline, QPoint(begin.x() + 5, begin.y() + 20), 20)
        QTest.keyClick(timeline, Qt.Key.Key_Escape)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=begin)
        self.assertEqual(self.window.session.find_clip(clip_id)[1].volume_envelope, ())
        self.assertEqual(len(self.window.session.undo_stack), history)
        self.assertIsNone(timeline._preview)

    def test_line_point_dialog_applies_exact_frame_and_value_and_reset_is_undoable(self):
        clip_id = self.insert()
        editor = self.window.multitrack
        editor.set_envelope_mode("volume")
        self.window.session.set_envelope(clip_id, "volume", ((0, 1), (7999, 1)))
        editor.set_session(self.window.session)
        clip = self.window.session.find_clip(clip_id)[1]
        def accept():
            dialog = QApplication.activeModalWidget()
            dialog.findChild(QSpinBox).setValue(1000)
            dialog.findChild(QDoubleSpinBox).setValue(50)
            dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(0, accept)
        editor.timeline.edit_envelope_point(clip, "volume", 1)
        self.assertEqual(self.window.session.find_clip(clip_id)[1].volume_envelope, ((0, 1), (1000, .5)))
        QTest.mouseClick(editor.reset_line, Qt.MouseButton.LeftButton)
        self.assertEqual(self.window.session.find_clip(clip_id)[1].volume_envelope, ())
        self.window.actions["undo"].trigger()
        self.assertEqual(self.window.session.find_clip(clip_id)[1].volume_envelope, ((0, 1), (1000, .5)))

    def test_automation_reaches_gui_mixdown_and_project_save(self):
        clip_id = self.insert()
        self.window.session.set_envelope(clip_id, "volume", ((0, 0), (7999, 1)))
        self.window.session.set_envelope(clip_id, "pan", ((0, -1), (7999, 1)))
        expected = self.window.session.render()
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as folder:
            path = Path(folder) / "mix.wav"
            with patch.object(self.window, "_save_path", return_value=(path, "float32")):
                self.window.actions["mixdown"].trigger()
            np.testing.assert_array_equal(read_wav(path).samples, expected)
            project = Path(folder) / "lines.celp"
            self.window.session.path = project
            self.window.actions["save"].trigger()
            self.assertTrue(self.window.load_session_path(project))
            np.testing.assert_array_equal(self.window.session.render(), expected)

    def test_play_action_uses_the_automated_selection_without_host_audio(self):
        clip_id = self.insert()
        self.window.session.set_envelope(clip_id, "volume", ((0, 0), (7999, 1)))
        self.window.session.set_envelope(clip_id, "pan", ((0, -1), (7999, 1)))
        expected = self.window.session.render()[1000:3000]
        self.window.session.select(1000, 3000)
        self.window.no_audio = False
        self.window.refresh()
        with patch.object(self.window.player, "play_session") as play, patch.object(self.window.session, "render", side_effect=AssertionError('Playback must stream')):
            self.window.actions["play"].trigger()
        play.assert_called_once()
        session, start, end = play.call_args.args
        self.assertIs(session, self.window.session)
        from soundsausage.mixing import SessionStream
        stream = SessionStream(session, start, end)
        np.testing.assert_array_equal(stream.read(end-start), expected)
        stream.close()
        self.assertEqual((start, end), (1000, 3000))
        self.window.no_audio = True

    def test_clip_header_can_move_over_another_clip_while_editing_a_line(self):
        clip_id = self.insert()
        s = self.window.session
        other = s.import_audio([(self.data, 8000, "Other")], s.tracks[1].id, 0)[0]
        editor = self.window.multitrack
        editor.set_session(s)
        editor.set_envelope_mode("volume")
        timeline = editor.timeline
        first = timeline.clip_rect(s.find_clip(clip_id)[1], 0)
        second = timeline.clip_rect(s.find_clip(other)[1], 1)
        begin = QPoint(round(first.center().x()), round(first.top() + 8))
        end = QPoint(begin.x() + 20, round(second.center().y()))
        QTest.mousePress(timeline, Qt.MouseButton.LeftButton, pos=begin)
        QTest.mouseMove(timeline, end, 20)
        QTest.mouseRelease(timeline, Qt.MouseButton.LeftButton, pos=end)
        self.assertEqual(s.find_clip(clip_id)[0].id, s.tracks[1].id)
        self.assertGreater(s.find_clip(clip_id)[1].start, 0)
        self.assertEqual(s.find_clip(other)[1].volume_envelope, ())


if __name__ == "__main__":
    unittest.main()
