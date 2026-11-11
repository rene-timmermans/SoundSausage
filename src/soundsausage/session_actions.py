"""Main-window actions for sessions; waveform and project save paths stay separate."""
from pathlib import Path

from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import (
    QFileDialog, QMessageBox, QDialog, QFormLayout,
    QSpinBox, QDialogButtonBox,
)

from .audio import AudioError, write_wav
from . import metadata
from .progress_ui import long_operation
from .document import Document
from .project import save_project, load_project
from .session import Session
from .legacy import load_legacy_project, MissingMediaError


class SessionActions:
    def init_session(self):
        self.mode = "waveform"
        self.session = Session(dsp=self.document.dsp)
        self.editing_clip_id = None

    def active_model(self):
        return self.session if self.mode == "multitrack" else self.document

    def active_view(self):
        return self.multitrack.timeline if self.mode == "multitrack" else self.waveform

    def create_session_actions(self):
        self.action("mode_wave", "Edit Waveform View", lambda: self.set_mode("waveform"))
        self.action("mode_multi", "Multitrack View", lambda: self.set_mode("multitrack"))
        group = QActionGroup(self)
        for key in ("mode_wave", "mode_multi"):
            self.actions[key].setCheckable(True)
            group.addAction(self.actions[key])
        self.actions["mode_wave"].setChecked(True)
        self.action("toggle_mode", "Switch Waveform / Multitrack", self.toggle_mode, "Tab")
        self.addAction(self.actions["toggle_mode"])
        self.action("new_session", "New Multitrack Session…", self.new_session, "Ctrl+Alt+N")
        self.action("open_session", "Open Session…", self.open_session_dialog, "Ctrl+Alt+O")
        self.action("save_session", "Save Session", self.save_session, "Ctrl+Alt+S")
        self.action("save_session_as", "Save Session As…", lambda: self.save_session(True))
        self.action("insert_wave", "Insert Current Waveform in Multitrack", self.insert_waveform)
        self.action("import_audio", "Import WAV into Multitrack…", self.import_audio_dialog)
        self.action("apply_clip", "Apply Waveform to Clip", self.apply_waveform_to_clip)
        self.action("clip_properties", "Clip Properties…", lambda: self.multitrack.properties())
        self.action("duplicate_clip", "Duplicate Clip", lambda: self.multitrack.duplicate_clip(), "Ctrl+D")
        self.action("remove_clip", "Remove Clip", lambda: self.multitrack.remove_clip())
        self.action("mixdown", "Mix Down Session…", self.mixdown)
        self.action("track_fx", "Track Effects…", lambda: self.multitrack.track_effects())

    def set_mode(self, mode):
        if self.recording_busy:return
        if mode not in ("waveform", "multitrack"):
            return
        self.player.stop()
        self.mode = mode
        self.editor_stack.setCurrentIndex(1 if mode == "multitrack" else 0)
        self.actions["mode_multi"].setChecked(mode == "multitrack")
        self.actions["mode_wave"].setChecked(mode == "waveform")
        if mode == "multitrack":
            self.multitrack.set_session(self.session)
        self.refresh()

    def toggle_mode(self):
        self.set_mode("waveform" if self.mode == "multitrack" else "multitrack")

    def update_session_actions(self):
        if "mode_multi" not in self.actions:
            return
        multi = self.mode == "multitrack"
        self.actions['track_fx'].setEnabled(multi)
        if hasattr(self, "effects_toolbar"):
            self.effects_toolbar.setVisible(not multi)
        self.actions["new"].setText("&New Session…" if multi else "&New…")
        self.actions["open"].setText("&Open Session…" if multi else "&Open…")
        self.actions["save"].setText("&Save Session" if multi else "&Save")
        self.actions["save_as"].setText("Save Session &As…" if multi else "Save &As…")
        self.actions["close_file"].setText("&Close Session" if multi else "&Close")
        if multi:
            for key in ("cut", "copy", "paste", "mix_paste", "trim", "zero", "amplify", "normalize", "channel_mix", "dynamics", "envelope", "graphic_eq", "parametric_eq", "filter", "delay", "echo", "reverb", "distortion", "convolution", "stretch", "pitch_shift", "noise_profile", "noise_reduction", "click_removal",
                "fade_in", "fade_out", "invert", "reverse", "silence", "frequency", "tone",
                "generate_silence", "repeat", "save_selection", "convert_rate"):
                self.actions[key].setEnabled(False)
            self.actions["delete"].setEnabled(self.session.selected_clip is not None)
        else:
            self.actions["tone"].setEnabled(True)
            self.actions["generate_silence"].setEnabled(True)
        for key in ("clip_properties", "duplicate_clip", "remove_clip"):
            self.actions[key].setEnabled(multi and self.session.selected_clip is not None)
        if not multi and self.document.partial_channels:
            for key in ("tone", "generate_silence", "stretch"): self.actions[key].setEnabled(False)
        self.actions["insert_wave"].setEnabled(self.document.frames > 0)
        self.actions["mixdown"].setEnabled(self.session.frames > 0)
        self.actions["save_session"].setEnabled(self.session.dirty or self.session.path is None)
        linked = False
        if self.editing_clip_id:
            try:
                self.session.find_clip(self.editing_clip_id)
                linked = True
            except AudioError:
                pass
        self.actions["apply_clip"].setEnabled(not multi and linked and self.document.frames > 0)

    def session_selection_changed(self):
        if self.mode == "multitrack":
            self.selection_changed(*self.session.selection)

    def session_edited(self):
        # The streaming mixer observes immutable track snapshots at block boundaries.
        self.refresh()

    def confirm_session_discard(self):
        if not self.session.dirty:
            return True
        result = QMessageBox.question(self, "Save Session", "Save changes to the multitrack session?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if result == QMessageBox.StandardButton.Save:
            return self.save_session()
        return result == QMessageBox.StandardButton.Discard

    def new_session(self):
        if not self.confirm_session_discard():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("New Multitrack Session")
        form = QFormLayout(dialog)
        rate, tracks = QSpinBox(), QSpinBox()
        rate.setRange(1000, 384000)
        rate.setValue(self.document.sample_rate)
        tracks.setRange(1, 32)
        tracks.setValue(4)
        form.addRow("Sample rate (Hz)", rate)
        form.addRow("Tracks", tracks)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.accepted.connect(dialog.accept)
        box.rejected.connect(dialog.reject)
        form.addRow(box)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.player.stop()
            self.session = Session(rate.value(), tracks.value(), dsp=self.document.dsp, adopt_first_rate=False)
            self.editing_clip_id = None
            self.multitrack.set_session(self.session, fit=True)
            self.set_mode("multitrack")

    def close_session(self):
        if not self.confirm_session_discard():
            return False
        self.player.stop()
        self.session = Session(self.session.sample_rate, dsp=self.document.dsp)
        self.editing_clip_id = None
        self.multitrack.set_session(self.session, fit=True)
        self.set_mode("waveform")
        return True

    def open_session_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Multitrack Session", "", "Supported projects (*.celp *.ses *.SES);;SoundSausage Project (*.celp);;Legacy session (*.ses *.SES)")
        if path:
            self.open_selected_path(path)

    @long_operation
    def load_session_path(self, path):
        try:
            if Path(path).suffix.lower() == ".ses":
                try:
                    session = load_legacy_project(path, dsp=self.document.dsp)
                except MissingMediaError as missing:
                    folder = QFileDialog.getExistingDirectory(self, str(missing), str(Path(path).parent))
                    if not folder:
                        return False
                    session = load_legacy_project(path, dsp=self.document.dsp, media_dirs=[folder])
            else:
                session = load_project(path, dsp=self.document.dsp)
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Open Session", error)
            return False
        self.player.stop()
        self.session = session
        self.editing_clip_id = None
        self.multitrack.set_session(session, fit=True)
        self.set_mode("multitrack")
        if hasattr(session, "legacy_report"):
            message = "Imported SES session. Save as .celp to keep a SoundSausage project."
            if session.legacy_report["warnings"]:
                message += " Empty source track metadata was invalid; an empty track was created."
            self.state_label.setText("SES imported — save as .celp" if not session.legacy_report["warnings"] else "SES imported — empty track metadata recovered")
            self.state_label.setToolTip(message)
        return True

    @long_operation
    def save_session(self, save_as=False):
        path = self.session.path
        if path is None or save_as:
            path, _ = QFileDialog.getSaveFileName(self, "Save Multitrack Session", str(path or "Untitled.celp"), "SoundSausage Project (*.celp)")
            if not path:
                return False
            path = Path(path)
            if not path.suffix:
                path = path.with_suffix(".celp")
        try:
            save_project(self.session, path)
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Save Session", error)
            return False
        self.refresh()
        return True

    def import_audio_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Import Audio into Multitrack", "", "WAV audio (*.wav *.WAV)")
        if paths:
            self.import_session_files(paths)

    @long_operation
    def import_session_files(self, paths, track_id=None, start=None):
        try:
            items = []
            for path in paths:
                audio = self.read_audio_file(path)
                if audio is None:
                    return
                items.append((audio.samples, audio.sample_rate, Path(path).name, audio.metadata))
            self.player.stop()
            self.session.import_audio(items, track_id, start)
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Import Audio", error)
            return
        self.multitrack.set_session(self.session, fit=True)
        self.set_mode("multitrack")

    @long_operation
    def insert_waveform(self):
        if not self.document.frames:
            return
        try:
            name = getattr(self.document, "display_name", None) or (self.document.path.name if self.document.path else "Untitled waveform")
            self.player.stop()
            self.session.import_audio([(self.document.view(), self.document.sample_rate, name, self.document.metadata)])
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Insert in Multitrack", error)
            return
        self.multitrack.set_session(self.session, fit=True)
        self.set_mode("multitrack")

    @long_operation
    def edit_clip_copy(self, clip_id):
        if not self._confirm_discard():
            return
        try:
            _, clip = self.session.find_clip(clip_id)
            media = self.session.media[clip.media_id]
            data = media.samples[clip.source_start:clip.source_end]
            document = Document(data, self.session.sample_rate, encoding="float32", dsp=self.document.dsp)
            document.metadata = metadata.crop(media.metadata,clip.source_start,clip.source_end)
            document.extra_chunks = tuple(kind.decode("ascii","replace") for kind,_ in document.metadata)
            document.display_name = f"{clip.name} (clip copy)"
        except (ValueError, RuntimeError) as error:
            self.error("Edit Clip", error)
            return
        self.document = document
        self.editing_clip_id = clip_id
        self.set_mode("waveform")
        self.refresh(fit=True)

    @long_operation
    def apply_waveform_to_clip(self):
        if not self.editing_clip_id:
            return
        try:
            self.player.stop()
            self.session.replace_clip_audio(self.editing_clip_id, self.document.view(), self.document.sample_rate, metadata=self.document.metadata)
        except (ValueError, RuntimeError) as error:
            self.error("Apply Waveform to Clip", error)
            return
        self.document.mark_saved()
        self.multitrack.set_session(self.session)
        self.set_mode("multitrack")

    @long_operation
    def mixdown(self):
        if self.session.frames == 0:
            return
        path, encoding = self._save_path("Mix Down Entire Session", "Mixdown.wav", encoding="pcm16")
        if path is None:
            return
        try:
            audio = self.session.render()
            # The supplied original PCM16 mixes saturate at -32767 and +32767.
            # Keep the float render's headroom and ordinary waveform saves intact.
            write_wav(path, audio, self.session.sample_rate, encoding, pcm16_symmetric=True)
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Mix Down", error)
            return
        self.statusBar().showMessage(f"Mixdown saved: {path}", 7000)
