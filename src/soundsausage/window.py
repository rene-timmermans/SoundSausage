from pathlib import Path
from functools import partial

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QToolBar, QToolButton, QStyle, QFileDialog, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox,
    QCheckBox, QRadioButton, QScrollBar,
    QInputDialog, QStackedWidget,
)

from .about import AboutDialog
from .manual import ManualDialog
from .audio import AudioError, AmbiguousWavError, read_wav, write_wav, tone
from .document import Document
from .recording_ui import RecordingActions,RecordingView
from .playback import Playback
from .audio_devices import AudioDevices, AudioHardwareDialog
from .waveform import Waveform, clock_text
from .multitrack import MultitrackEditor
from .session_actions import SessionActions
from . import chrome, metadata, storage
from .errors import OperationCancelled
from .progress_ui import long_operation
from .transport import TransportPanel
from .restoration_ui import NoiseReductionDialog, ClickRemovalDialog
from .restoration import learn_profile
from .space_ui import DelayDialog, EchoDialog, ReverbDialog
from .filters_ui import GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog
from .amplitude_ui import EffectDialog, ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog
from .theme import install_theme, colors
from .icons import ICON_ACTIONS, PRIMARY_ACTIONS, make_icon, application_icon


FORMAT_LABELS = {
    "pcm8": "WAV · 8-bit PCM (*.wav)",
    "pcm16": "WAV · 16-bit PCM (*.wav)",
    "pcm24": "WAV · 24-bit PCM (*.wav)",
    "pcm32": "WAV · 32-bit integer PCM (*.wav)",
    "float32": "WAV · 32-bit normalized float (*.wav)",
}


def spin(value, minimum=0, maximum=1000, decimals=3, suffix=""):
    widget = QDoubleSpinBox()
    widget.setRange(minimum, maximum)
    widget.setDecimals(decimals)
    widget.setValue(value)
    widget.setSuffix(suffix)
    widget.setKeyboardTracking(False)
    return widget


def buttons(dialog):
    box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    box.accepted.connect(dialog.accept)
    box.rejected.connect(dialog.reject)
    return box


class AmplifyDialog(EffectDialog):
    effect_name = "gain"

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        channels = document.channels
        self.setWindowTitle("Amplify")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        grid.addWidget(QLabel("Initial amplification"), 0, 1)
        grid.addWidget(QLabel("Final amplification"), 0, 2)
        self.initial = []
        self.final = []
        for channel in range(channels):
            start = spin(100, 0, 10000, 2, " %")
            end = spin(100, 0, 10000, 2, " %")
            self.initial.append(start)
            self.final.append(end)
            grid.addWidget(QLabel("Left" if channel == 0 else "Right"), channel + 1, 0)
            grid.addWidget(start, channel + 1, 1)
            grid.addWidget(end, channel + 1, 2)
        layout.addLayout(grid)
        self.lock_channels = QCheckBox("Lock left / right")
        self.lock_channels.setChecked(True)
        self.lock_channels.setVisible(channels == 2)
        self.constant = QCheckBox("Keep initial and final amplification equal")
        self.constant.setChecked(True)
        layout.addWidget(self.lock_channels)
        layout.addWidget(self.constant)
        modes = QHBoxLayout()
        self.linear = QRadioButton("Linear fades")
        self.logarithmic = QRadioButton("Logarithmic fades")
        self.linear.setChecked(True)
        modes.addWidget(self.linear)
        modes.addWidget(self.logarithmic)
        layout.addLayout(modes)
        self.presets = QComboBox()
        self.presets.addItems(["Choose a preset…", "Amplify +6 dB", "Amplify −6 dB", "Fade In", "Fade Out"])
        layout.addWidget(self.presets)
        self.add_footer(layout)
        self._syncing = False
        for c, widget in enumerate(self.initial):
            widget.valueChanged.connect(lambda value, channel=c: self.sync(channel, False, value))
        for c, widget in enumerate(self.final):
            widget.valueChanged.connect(lambda value, channel=c: self.sync(channel, True, value))
        self.lock_channels.toggled.connect(lambda _: self.sync(0, False, self.initial[0].value()))
        self.constant.toggled.connect(lambda _: self.sync(0, False, self.initial[0].value()))
        self.presets.currentIndexChanged.connect(self.preset)

    def sync(self, channel, is_final, value):
        if self._syncing:
            return
        self._syncing = True
        group = self.final if is_final else self.initial
        if self.lock_channels.isChecked():
            for widget in group:
                widget.setValue(value)
        if self.constant.isChecked():
            for c in range(len(self.initial)):
                (self.initial if is_final else self.final)[c].setValue(group[c].value())
        self._syncing = False

    def preset(self, index):
        if index == 0:
            return
        self._syncing = True
        self.linear.setChecked(True)
        self.constant.setChecked(index < 3)
        gain = 100 * (10 ** (6 / 20) if index == 1 else 10 ** (-6 / 20))
        for start, end in zip(self.initial, self.final):
            start.setValue(0 if index == 3 else 100 if index == 4 else gain)
            end.setValue(100 if index == 3 else 0 if index == 4 else gain)
        self._syncing = False

    def settings(self):
        return dict(initial=tuple(w.value() / 100 for w in self.initial),
                    final=tuple(w.value() / 100 for w in self.final), logarithmic=self.logarithmic.isChecked())

    def accept(self):
        if self.logarithmic.isChecked() and any(w.value() <= 0 for w in self.initial + self.final):
            QMessageBox.information(self, "Logarithmic fade", "Use positive endpoints for a logarithmic fade, or select Linear fades for a fade to silence.")
            return
        super().accept()


class MainWindow(RecordingActions, SessionActions, QMainWindow):
    def __init__(self, document=None, no_audio=False):
        super().__init__()
        self.setWindowIcon(application_icon())
        self.theme = install_theme()
        self.document = document or Document()
        self.init_session()
        self.clipboard = None
        self._manual_dialog = None
        self.recovery = None
        self._recovery_error = None
        self.no_audio = no_audio
        self.audio_devices = AudioDevices(self)
        self.player = Playback(self, devices=self.audio_devices)
        self.init_recording()
        self.player.state_changed.connect(self.playback_state)
        self.player.position.connect(self.playback_position)
        self.player.failed.connect(lambda message: self.error("Playback", message))
        self.actions = {}
        self.resize(1180, 720)
        self.setMinimumSize(850, 540)
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_editor()
        self._create_status()
        self.bind_button_icons()
        self.theme.changed.connect(self.apply_theme)
        self.apply_theme()
        self.refresh(fit=True)

    def bind_button_icons(self):
        self._action_buttons = []
        by_action = {self.actions[key]: key for key in ICON_ACTIONS}
        for button in self.findChildren(QToolButton):
            action = button.defaultAction()
            key = by_action.get(action)
            if key is not None:
                button.setProperty("primary", key in PRIMARY_ACTIONS)
                button.setProperty("compact", True)
                self._action_buttons.append((key, button))
                # QToolButton copies its QAction icon again on every action change.
                # Reapply the button variant after that copy; menus keep the accent icon.
                action.changed.connect(partial(self.update_button_icon, key, button))

    def update_button_icon(self, key, button):
        icon_key="stop" if key=="play" and self.recording_busy else key
        button.setIcon(make_icon(icon_key, colors(), key in PRIMARY_ACTIONS, button.isCheckable()))

    def apply_theme(self):
        c = colors()
        for key in ICON_ACTIONS:
            # Menus have neutral backgrounds; their icons use the readable accent.
            icon_key="stop" if key=="play" and self.recording_busy else key
            self.actions[key].setIcon(make_icon(icon_key, c))
        for toolbar in self.findChildren(QToolBar):
            overflow = toolbar.findChild(QToolButton, "qt_toolbar_ext_button")
            if overflow is not None:
                overflow.setIcon(make_icon("more", c, primary=True))
                overflow.setToolTip("More actions")
        for key, button in self._action_buttons:
            self.update_button_icon(key, button)
        self.multitrack.update_theme()
        self.waveform.update()
        self.multitrack.timeline.update()

    def action(self, key, text, callback, shortcut=None, icon=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if icon:
            action.setIcon(self.style().standardIcon(icon))
        action.triggered.connect(lambda checked=False: callback())
        self.actions[key] = action
        return action

    def _create_actions(self):
        standard = QStyle.StandardPixmap
        self.action("new", "&New…", self.new_document, "Ctrl+N", standard.SP_FileIcon)
        self.action("open", "&Open…", self.open_dialog, "Ctrl+O", standard.SP_DirOpenIcon)
        self.action("close_file", "&Close", self.close_current, "Ctrl+W")
        self.action("save", "&Save", self.save, "Ctrl+S", standard.SP_DialogSaveButton)
        self.action("save_as", "Save &As…", lambda: self.save(True), "Ctrl+Shift+S")
        self.action("save_selection", "Save S&election…", self.save_selection)
        self.action("recover", "Recover Work…", self.offer_recovery)
        self.action("exit", "E&xit", self.close, "Ctrl+Q")
        self.action("undo", "&Undo", lambda: self.edit(self.active_model().undo), "Ctrl+Z", standard.SP_ArrowBack)
        self.action("redo", "&Redo", lambda: self.edit(self.active_model().redo), "Ctrl+Shift+Z", standard.SP_ArrowForward)
        self.action("repeat", "Repeat Last Comma&nd", lambda: self.edit(self.document.repeat), "F2")
        self.action("cut", "Cu&t", self.cut, "Ctrl+X")
        self.action("copy", "&Copy", self.copy, "Ctrl+C")
        self.action("paste", "&Paste", lambda: self.edit(lambda: self.document.paste(self.clipboard)), "Ctrl+V")
        self.action("mix_paste", "&Mix Paste", lambda: self.edit(lambda: self.document.paste(self.clipboard, True)), "Ctrl+M")
        self.action("delete", "&Delete Selection", self.delete_selection, "Delete")
        self.action("trim", "Tri&m", lambda: self.edit(self.document.trim), "Ctrl+T")
        self.action("select_all", "Select &Entire Wave", self.select_all, "Ctrl+A")
        self.action("select_range", "Set Selection…", self.select_range)
        self.action("zero", "Adjust Selection Inward to &Zero Crossings", self.zero_crossings, "F4")
        self.action("zoom_in", "Zoom &In", lambda: self.active_view().zoom(2), "+", standard.SP_ArrowUp)
        self.action("zoom_out", "Zoom &Out", lambda: self.active_view().zoom(0.5), "-", standard.SP_ArrowDown)
        self.action("zoom_full", "Zoom &Full", lambda: self.active_view().fit(), "Ctrl+0")
        self.action("zoom_selection", "Zoom to &Selection", lambda: self.active_view().zoom_selection(), "Ctrl+Shift+A")
        self.action("amplify", "&Amplify / Fade…", self.amplify)
        self.action("channel_mix", "Channel Mixer…", lambda: self.amplitude_dialog(ChannelMixerDialog))
        self.actions["channel_mix"].setToolTip("Mix the left and right channels of a stereo waveform")
        self.action("dynamics", "Dynamics Processing…", lambda: self.amplitude_dialog(DynamicsDialog))
        self.action("envelope", "Envelope…", lambda: self.amplitude_dialog(EnvelopeDialog))
        self.action("noise_profile", "Capture Noise Profile", self.capture_noise_profile)
        self.action("noise_reduction", "Noise Reduction…", lambda: self.amplitude_dialog(NoiseReductionDialog))
        self.action("click_removal", "Click Removal…", lambda: self.amplitude_dialog(ClickRemovalDialog))
        self.action("delay", "Delay…", lambda: self.amplitude_dialog(DelayDialog))
        self.action("echo", "Echo…", lambda: self.amplitude_dialog(EchoDialog))
        self.action("reverb", "Reverb…", lambda: self.amplitude_dialog(ReverbDialog))
        self.action("graphic_eq", "Graphic Equalizer…", lambda: self.amplitude_dialog(GraphicEqualizerDialog))
        self.action("parametric_eq", "Parametric Equalizer…", lambda: self.amplitude_dialog(ParametricEqualizerDialog))
        self.action("filter", "Filters…", lambda: self.amplitude_dialog(FilterDialog))
        self.action("normalize", "&Normalize…", self.normalize)
        self.action("fade_in", "Fade &In", lambda: self.effect("gain", initial=0.0, final=1.0))
        self.action("fade_out", "Fade &Out", lambda: self.effect("gain", initial=1.0, final=0.0))
        self.action("invert", "&Invert", lambda: self.effect("invert"))
        self.action("reverse", "&Reverse", lambda: self.effect("reverse"))
        self.action("silence", "&Silence", lambda: self.effect("silence"))
        self.action("tone", "&Tones…", self.generate_tone)
        self.action("generate_silence", "&Silence…", self.generate_silence)
        self.action("frequency", "&Frequency Analysis…", self.frequency_analysis, "Alt+Z")
        self.action("convert_rate", "Convert Sample Rate…", self.convert_sample_rate)
        self.action("audio_hardware", "Audio Hardware…", self.audio_hardware)
        self.actions["audio_hardware"].setEnabled(not self.no_audio)
        self.action("play", "Play / Stop", self.toggle_play, "Space", standard.SP_MediaPlay)
        self.action("pause", "Pause / Resume", self.toggle_pause, "P", standard.SP_MediaPause)
        self.action("stop", "Stop", self.stop_transport, "Esc", standard.SP_MediaStop)
        self.action("loop", "Loop", lambda: None)
        self.actions["loop"].setCheckable(True)
        self.actions["loop"].toggled.connect(lambda value: setattr(self.player, "loop", value))
        self.action("about", "&About…", self.about)
        self.action("manual", "&Handleiding", self.open_manual, "F1")
        self.create_session_actions()
        chrome.create_actions(self)

    def _create_menus(self):
        chrome.create_menus(self)

    def _create_toolbars(self):
        chrome.create_toolbars(self)

    def _create_editor(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(3, 3, 3, 0)
        layout.setSpacing(2)
        self.scroll = QScrollBar(Qt.Orientation.Horizontal)
        self.scroll.setFixedHeight(14)
        wave_page = QWidget()
        wave_layout = QVBoxLayout(wave_page)
        wave_layout.setContentsMargins(0, 0, 0, 0)
        wave_layout.setSpacing(4)
        wave_layout.addWidget(self.scroll)
        self.waveform = Waveform(self.document)
        self.waveform.selection_changed.connect(self.selection_changed)
        self.waveform.view_changed.connect(self.view_changed)
        self.scroll.valueChanged.connect(self.scroll_view)
        wave_layout.addWidget(self.waveform, 1)
        self.multitrack = MultitrackEditor(self.session)
        self.multitrack.edited.connect(self.session_edited)
        self.multitrack.selection_changed.connect(self.session_selection_changed)
        self.multitrack.failed.connect(lambda message: self.error("Multitrack", message))
        self.multitrack.import_requested.connect(self.import_audio_dialog)
        self.multitrack.import_files.connect(self.import_session_files)
        self.multitrack.edit_copy.connect(self.edit_clip_copy)
        self.multitrack.mixdown_requested.connect(self.mixdown)
        self.editor_stack = QStackedWidget()
        self.editor_stack.addWidget(wave_page)
        self.editor_stack.addWidget(self.multitrack)
        self.recording_view=RecordingView(self)
        self.editor_stack.addWidget(self.recording_view)
        layout.addWidget(self.editor_stack, 1)
        self.transport = TransportPanel(self.actions, self)
        self.time_label = self.transport.time_label
        self.fields = self.transport.fields
        self.view_fields = self.transport.view_fields
        layout.addWidget(self.transport)
        self.multitrack.timeline.view_changed.connect(self.multitrack_view_changed)

    def _create_status(self):
        self.state_label = QLabel("Stopped")
        self.format_label = QLabel()
        self.detail_label = QLabel()
        self.statusBar().addWidget(self.state_label, 1)
        self.statusBar().addPermanentWidget(self.format_label)
        self.statusBar().addPermanentWidget(self.detail_label)

    def error(self, title, message):
        if isinstance(message, OperationCancelled):
            self.statusBar().showMessage("Bewerking geannuleerd", 4000)
            return
        QMessageBox.warning(self, title, str(message))

    def refresh(self, fit=False):
        doc = self.active_model()
        if self.mode == "waveform":
            self.waveform.set_document(self.document, fit=fit)
            self.scroll.setVisible(self.document.frames > 0)
        elif fit:
            self.multitrack.set_session(self.session, fit=True)
        name = doc.path.name if doc.path else getattr(doc, "display_name", None) or ("Untitled Session" if self.mode == "multitrack" else "Untitled")
        self.setWindowTitle(f"{'* ' if doc.dirty else ''}{name} — SoundSausage")
        self.format_label.setText(f" {doc.sample_rate} Hz · {doc.encoding} · {'Stereo' if doc.channels == 2 else 'Mono'} ")
        self.detail_label.setText(f" {clock_text(doc.duration)} · {doc.frames:,} frames ")
        self.selection_changed(*doc.selection)
        has_audio = doc.frames > 0
        for key in ("noise_profile", "noise_reduction", "click_removal", "delay", "echo", "reverb", "graphic_eq", "parametric_eq", "filter", "amplify", "normalize", "dynamics", "envelope", "fade_in", "fade_out", "invert", "reverse", "silence", "frequency", "convert_rate", "select_all", "zoom_in", "zoom_out", "zoom_full"):
            self.actions[key].setEnabled(has_audio)
        self.actions["channel_mix"].setEnabled(has_audio and doc.channels == 2)
        self.actions["play"].setEnabled(has_audio and not self.no_audio)
        self.actions["undo"].setEnabled(bool(doc.undo_stack))
        self.actions["redo"].setEnabled(bool(doc.redo_stack))
        self.actions["undo"].setText("&Undo" + (" " + doc.undo_stack[-1].label if doc.undo_stack else ""))
        self.actions["redo"].setText("&Redo" + (" " + doc.redo_stack[-1].label if doc.redo_stack else ""))
        self.actions["repeat"].setEnabled(getattr(doc, "last_effect", None) is not None and has_audio)
        self.actions["paste"].setEnabled(self.clipboard is not None)
        self.actions["mix_paste"].setEnabled(self.clipboard is not None)
        self.actions["save"].setEnabled(doc.dirty or doc.path is None)
        self.actions["close_file"].setEnabled(self.mode == "multitrack" or bool(
            doc.frames or doc.path is not None or doc.dirty or doc.undo_stack or doc.redo_stack or self.editing_clip_id))
        self.actions["pause"].setEnabled(self.player.state in ("Playing", "Paused"))
        self.actions["stop"].setEnabled(self.player.state != "Stopped")
        self.update_session_actions()
        for key in ("to_start", "to_end", "seek_back", "seek_forward"):
            self.actions[key].setEnabled(has_audio)
        self.sync_view_fields()
        self.checkpoint_recovery()
        self.update_recording_actions()

    def selection_changed(self, start, end):
        if self.recovery is not None:
            self._recovery_timer.start()
        doc = self.active_model()
        self.fields["Begin"].setText(clock_text(start / doc.sample_rate))
        self.fields["End"].setText(clock_text(end / doc.sample_rate))
        self.fields["Length"].setText(clock_text((end - start) / doc.sample_rate))
        if self.player.state == "Stopped" and not self.recording_busy:
            self.time_label.setText(clock_text(doc.cursor / doc.sample_rate))
        for key in ("cut", "copy", "delete", "trim", "zero", "save_selection", "zoom_selection"):
            self.actions[key].setEnabled(end > start)
        self.update_session_actions()

    def view_changed(self, start, end):
        self.scroll.blockSignals(True)
        maximum = max(0, self.document.frames - (end-start))
        self._scroll_scale = max(1, (maximum + 2147483646)//2147483647)
        scale = self._scroll_scale
        self.scroll.setRange(0, (maximum+scale-1)//scale)
        self.scroll.setPageStep(min(2147483647,max(1,(end-start)//scale)))
        self.scroll.setSingleStep(min(2147483647,max(1,(end-start)//(20*scale))))
        self.scroll.setValue(start//scale)
        self.scroll.blockSignals(False)
        if self.mode == "waveform":
            self.sync_view_fields()

    def sync_view_fields(self):
        if not hasattr(self, "transport"):
            return
        model, view = self.active_model(), self.active_view()
        begin, end = view.view_start, view.view_end
        if self.mode == "waveform" and not model.frames:
            begin = end = 0
        self.transport.set_view_range(begin, end, model.sample_rate)

    def multitrack_view_changed(self, start, end):
        if self.mode == "multitrack":
            self.sync_view_fields()

    def scroll_view(self, value):
        length = self.waveform.view_end - self.waveform.view_start
        value = value * getattr(self,"_scroll_scale",1)
        self.waveform.set_view(value, value + length)

    @long_operation
    def edit(self, operation):
        if self.recording_busy:return
        self.player.stop()
        previous_frames = self.active_model().frames
        try:
            operation()
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Edit", error)
            return
        changed_length = previous_frames != self.active_model().frames
        if self.mode == "multitrack":
            self.multitrack.set_session(self.session, fit=changed_length)
        self.refresh(fit=changed_length)

    def delete_selection(self):
        if self.mode == "multitrack":
            self.multitrack.remove_clip()
        else:
            self.edit(self.document.delete)

    def effect(self, name, **settings):
        self.edit(lambda: self.document.apply(name, **settings))

    def audio_hardware(self):
        if self.no_audio:
            return
        dialog = AudioHardwareDialog(self.audio_devices, self)
        dialog.exec()
        dialog.deleteLater()

    def convert_sample_rate(self):
        if self.mode != "waveform" or not self.document.frames:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Convert Sample Rate")
        form = QFormLayout(dialog)
        rate = QSpinBox()
        rate.setRange(1000, 384000)
        rate.setValue(self.document.sample_rate)
        form.addRow("New sample rate (Hz)", rate)
        note = QLabel("Converts the whole waveform, preserving pitch and duration.\nSelection and cursor positions follow the same times.")
        note.setWordWrap(True)
        form.addRow(note)
        form.addRow(buttons(dialog))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.edit(lambda: self.document.convert_sample_rate(rate.value()))
            self.refresh(fit=True)
        dialog.deleteLater()

    @long_operation
    def copy(self):
        try:
            self.clipboard = self.document.copy()
            self.refresh()
        except AudioError as error:
            self.error("Copy", error)

    def cut(self):
        def perform():
            self.clipboard = self.document.cut()
        self.edit(perform)

    def select_all(self):
        doc = self.active_model()
        doc.select(0, doc.frames)
        self.selection_changed(*doc.selection)
        self.active_view().update()

    def select_range(self):
        doc = self.active_model()
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Selection — Audio Frames")
        form = QFormLayout(dialog)
        begin, end = QDoubleSpinBox(), QDoubleSpinBox()
        for widget, value in ((begin, doc.selection[0]), (end, doc.selection[1])):
            widget.setDecimals(0)
            widget.setRange(0, min(2**53, doc.frames))
            widget.setValue(value)
            widget.setGroupSeparatorShown(True)
        form.addRow("Begin frame", begin)
        form.addRow("End frame (exclusive)", end)
        form.addRow(QLabel(f"{doc.sample_rate:,} frames = 1 second"))
        form.addRow(buttons(dialog))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            doc.select(begin.value(), end.value())
            self.selection_changed(*doc.selection)
            self.active_view().update()

    @long_operation
    def zero_crossings(self):
        self.document.zero_crossings()
        self.selection_changed(*self.document.selection)
        self.waveform.update()

    @long_operation
    def capture_noise_profile(self):
        if self.mode != "waveform" or not self.document.selected:
            self.error("Noise Profile", "Select a fragment containing only background noise first.")
            return
        try:
            self.player.stop()
            profile = learn_profile(self.document.view(*self.document.selection), self.document.sample_rate)
            self.noise_profile = profile
            self.statusBar().showMessage("Noise profile captured. Select the audio to clean and open Noise Reduction.", 8000)
        except (ValueError, OSError) as error:
            self.error("Noise Profile", error)

    def amplify(self):
        self.amplitude_dialog(AmplifyDialog)

    def amplitude_dialog(self, dialog_class):
        if self.mode != "waveform" or not self.document.frames:
            return
        if dialog_class is ChannelMixerDialog and self.document.channels != 2:
            return
        self.player.stop()
        dialog = dialog_class(self.document, self, no_audio=self.no_audio)
        try:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.effect(dialog.effect_name, **dialog.settings())
        finally:
            dialog.player.shutdown()
            dialog.deleteLater()

    def normalize(self):
        self.amplitude_dialog(NormalizeDialog)

    def _confirm_discard(self):
        if not self.document.dirty:
            return True
        result = QMessageBox.question(self, "Save Changes", "Save changes to the current waveform?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if result == QMessageBox.StandardButton.Save:
            return self.save_waveform()
        return result == QMessageBox.StandardButton.Discard

    def close_current(self):
        if self.mode == "multitrack":
            return self.close_session()
        if not self._confirm_discard():
            return False
        self.player.stop()
        previous = self.document
        self.document = Document(sample_rate=previous.sample_rate, channels=previous.channels, dsp=previous.dsp)
        self.editing_clip_id = None
        self.refresh(fit=True)
        return True

    def new_document(self):
        if self.mode == "multitrack":
            return self.new_session()
        if not self._confirm_discard():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("New Waveform")
        form = QFormLayout(dialog)
        rate = QSpinBox()
        rate.setRange(1000, 384000)
        rate.setValue(44100)
        channels = QComboBox()
        channels.addItems(["Mono", "Stereo"])
        channels.setCurrentIndex(1)
        form.addRow("Sample rate (Hz)", rate)
        form.addRow("Channels", channels)
        form.addRow(buttons(dialog))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.player.stop()
            self.document = Document(sample_rate=rate.value(), channels=channels.currentIndex() + 1, dsp=self.document.dsp)
            self.editing_clip_id = None
            self.refresh(fit=True)

    def open_dialog(self):
        if self.mode == "multitrack":
            return self.open_session_dialog()
        path, _ = QFileDialog.getOpenFileName(self, "Open a Waveform", "", "Waveform audio (*.wav *.WAV);;All files (*)")
        if path:
            self.open_selected_path(path)

    def open_selected_path(self,path):
        if self.recording_busy:return False
        project=Path(path).suffix.lower() in (".celp",".ses")
        if not (self.confirm_session_discard() if project else self._confirm_discard()):return False
        return self.load_path(path)

    @long_operation
    def read_audio_file(self, path):
        try:
            return read_wav(path)
        except AmbiguousWavError:
            choice, accepted = QInputDialog.getItem(self, "32-bit WAV Interpretation",
                "This header is ambiguous. How was its audio stored?",
                ["Signed 32-bit PCM integers (float32 editing precision)",
                 "Legacy type-1 floats (convert to normalized float32)"], 0, False)
            if not accepted:
                return None
            return read_wav(path, "integer" if choice.startswith("Signed") else "cool-edit-float")

    @long_operation
    def load_path(self, path):
        if Path(path).suffix.lower() in (".celp", ".ses"):
            return self.load_session_path(path)
        try:
            audio = self.read_audio_file(path)
            if audio is None:
                return False
            doc = Document(audio.samples, audio.sample_rate, encoding=audio.encoding, dsp=self.document.dsp)
            doc.extra_chunks = audio.extra_chunks
            doc.metadata = audio.metadata
            doc.path = Path(path).resolve()
            self.player.stop()
            self.document = doc
            self.editing_clip_id = None
            self.set_mode("waveform")
            self.refresh(fit=True)
            return True
        except (ValueError, OSError, RuntimeError) as error:
            self.error("Open Audio", error)
            return False

    def _save_path(self, title, suggested=None, encoding=None):
        encoding = encoding or self.document.encoding
        labels = ";;".join(FORMAT_LABELS.values())
        path, selected = QFileDialog.getSaveFileName(self, title, str(suggested or "Untitled.wav"), labels, FORMAT_LABELS[encoding])
        if not path:
            return None, None
        if not Path(path).suffix:
            path += ".wav"
        return Path(path), next((key for key, value in FORMAT_LABELS.items() if value == selected), encoding)

    def _metadata_permission(self):
        preserved = {kind.decode("ascii","replace") for kind,_ in self.document.metadata}
        omitted = [name for name in self.document.extra_chunks if name not in preserved]
        if not omitted:
            return True
        names = ", ".join(omitted)
        result = QMessageBox.question(self, "Audio-only WAV Export",
            f"These additional WAV chunks could not be preserved and will be omitted: {names}.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        return result == QMessageBox.StandardButton.Yes

    def save(self, save_as=False):
        if self.mode == "multitrack":
            return self.save_session(save_as)
        return self.save_waveform(save_as)

    @long_operation
    def save_waveform(self, save_as=False):
        path, encoding = self.document.path, self.document.encoding
        if save_as or path is None:
            path, encoding = self._save_path("Save a Waveform", path)
        if path is None or not self._metadata_permission():
            return False
        try:
            write_wav(path, self.document.view(), self.document.sample_rate, encoding, metadata=self.document.metadata)
        except (ValueError, OSError) as error:
            self.error("Save Audio", error)
            return False
        self.document.path = path.resolve()
        self.document.encoding = encoding
        self.document.extra_chunks = tuple(kind.decode("ascii","replace") for kind,_ in self.document.metadata)
        self.document.mark_saved()
        self.refresh()
        return True

    @long_operation
    def save_selection(self):
        if not self.document.selected:
            return
        path, encoding = self._save_path("Save Selection", "Selection.wav")
        if path is None or not self._metadata_permission():
            return
        try:
            write_wav(path, self.document.view(*self.document.selection), self.document.sample_rate, encoding,
                      metadata=metadata.crop(self.document.metadata,*self.document.selection))
        except (ValueError, OSError) as error:
            self.error("Save Selection", error)

    def generate_tone(self):
        doc = self.document
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Tones")
        form = QFormLayout(dialog)
        duration = spin((doc.selection[1] - doc.selection[0]) / doc.sample_rate if doc.selected else 2, 0.001, 600, 3, " sec")
        frequency = spin(440, 1, doc.sample_rate / 2 - 1, 2, " Hz")
        level = spin(25, 0, 100, 2, " %")
        form.addRow("Duration", duration)
        form.addRow("Frequency", frequency)
        form.addRow("Amplitude", level)
        form.addRow(buttons(dialog))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            def perform():
                data = tone(duration.value(), doc.sample_rate, doc.channels, frequency.value(), level.value() / 100)
                a, b = doc.selection if doc.selected else (doc.cursor, doc.cursor)
                doc.replace(a, b, data, "Generate Tones")
            self.edit(perform)

    def generate_silence(self):
        doc = self.document
        duration, accepted = QInputDialog.getDouble(self, "Generate Silence", "Duration (seconds)", 1.0, 0.001, 600, 3)
        if accepted:
            def perform():
                frames = max(1, round(duration * doc.sample_rate))
                from .audio import MAX_AUDIO_BYTES
                if frames * doc.channels * 4 > MAX_AUDIO_BYTES:
                    raise AudioError("The generated silence would exceed the document limit.")
                a, b = doc.selection if doc.selected else (doc.cursor, doc.cursor)
                doc.replace(a, b, storage.seal(storage.allocate((frames, doc.channels), zero=True), checked=True), "Generate Silence")
            self.edit(perform)

    def frequency_analysis(self):
        from .spectrum import SpectrumDialog
        start, end = self.document.effect_range
        if end > start:
            # A bounded, centered analysis window avoids blocking on a long document.
            middle = (start + end) // 2
            a = max(start, middle - 131072)
            b = min(end, a + 262144)
            SpectrumDialog(self.document.read(a, b), self.document.sample_rate, self).exec()

    @long_operation
    def toggle_play(self):
        if self.recorder.active:
            self.stop_recording()
            return
        if self.no_audio:
            return
        if self.player.state != "Stopped":
            self.player.stop()
            return
        doc = self.active_model()
        start, end = doc.selection if doc.selected else (doc.cursor, doc.frames)
        if start >= end:
            start = 0
        if end > start:
            try:
                audio = doc.render(start, end) if self.mode == "multitrack" else doc.view(start, end)
                self.player.play(audio, doc.sample_rate, start)
            except (ValueError, RuntimeError) as error:
                self.error("Playback", error)

    def playback_state(self, state):
        if self.recording_busy:
            self.update_recording_actions()
            return
        if not hasattr(self, "state_label"):
            return
        self.state_label.setText(state)
        self.state_label.setToolTip(self.player.output_description if state != "Stopped" else "")
        self.actions["pause"].setEnabled(state in ("Playing", "Paused"))
        self.actions["stop"].setEnabled(state != "Stopped")
        if state == "Stopped":
            self.active_view().playhead = None
            self.active_view().update()
            self.selection_changed(*self.active_model().selection)
            self.update_meters(None)

    def playback_position(self, frame):
        frame = min(frame, self.active_model().frames)
        self.active_model().cursor = frame
        self.time_label.setText(clock_text(frame / self.active_model().sample_rate))
        self.active_view().playhead = frame
        self.active_view().update()
        self.update_meters(self.player.meter_samples(frame))

    def update_meters(self, data):
        self.transport.meter.set_samples(data)

    def to_start(self):
        self.player.stop()
        self.active_model().select(0, 0)
        view = self.active_view()
        view.set_view(0, view.view_end - view.view_start)
        self.selection_changed(0, 0)

    def to_end(self):
        self.player.stop()
        frame = self.active_model().frames
        self.active_model().select(frame, frame)
        view = self.active_view()
        length = view.view_end - view.view_start
        view.set_view(max(0, frame - length), max(1, frame))
        self.selection_changed(frame, frame)

    def about(self):
        dialog = AboutDialog(self)
        dialog.exec()
        dialog.deleteLater()

    def open_manual(self):
        if self._manual_dialog is None:
            try:
                self._manual_dialog = ManualDialog(self)
                screen = self.screen()
                if screen is not None:
                    area = screen.availableGeometry()
                    self._manual_dialog.resize(min(850, max(550, area.width() - 40)), min(680, max(400, area.height() - 50)))
            except OSError:
                self.error("Handleiding", "De handleiding ontbreekt in deze installatie. Installeer SoundSausage opnieuw.")
                return
        self._manual_dialog.show()
        self._manual_dialog.raise_()
        self._manual_dialog.activateWindow()

    def enable_recovery(self, offer=True):
        from .recovery import Recovery, collect_orphans
        try:
            self.recovery = Recovery()
            self._recovery_timer = QTimer(self)
            self._recovery_timer.setSingleShot(True)
            self._recovery_timer.setInterval(1000)
            self._recovery_timer.timeout.connect(self.checkpoint_recovery)
            collect_orphans()
            if offer:
                self.offer_recovery(quiet=True)
            self.checkpoint_recovery()
        except (ValueError,OSError) as error:
            self._recovery_error = str(error)
            self.statusBar().showMessage(f"Herstelkopie niet beschikbaar: {error}")

    def checkpoint_recovery(self):
        if self.recovery is None:
            return
        try:
            self.recovery.checkpoint(self.document,self.session,self.mode,self.editing_clip_id)
            self._recovery_error = None
        except (ValueError,OSError) as error:
            self._recovery_error = str(error)
            self.statusBar().showMessage(f"Herstelkopie niet bijgewerkt: {error}")

    @long_operation
    def restore_recovery(self, owner):
        from .recovery import restore, discard
        document,session,mode,editing = restore(owner,self.document.dsp)
        # Publish a new journal before releasing the previous crash record.
        self.recovery.checkpoint(document,session,mode,editing)
        self.player.stop()
        self.document,self.session = document,session
        self.editing_clip_id = editing
        self.multitrack.set_session(session,fit=True)
        self.set_mode(mode)
        self.refresh(fit=True)
        discard(owner)
        return True

    def offer_recovery(self, quiet=False):
        if self.recovery is None:
            self.enable_recovery(offer=False)
            if self.recovery is None:
                return
        from .recovery import candidates, discard
        available = candidates()
        if not available and not quiet:
            QMessageBox.information(self,"Werk herstellen","Er zijn geen herstelkopieën uit een vorige sessie gevonden.")
        for owner in available:
            try:
                box = QMessageBox(self)
                box.setWindowTitle("Werk herstellen")
                interrupted=(owner.path/"recording.json").exists()
                box.setText("Er is een onderbroken opname gevonden." if interrupted else "Er is werk gevonden uit een vorige, onverwacht beëindigde sessie.")
                box.setInformativeText("Herstel de laatst vastgelegde stand. De oorspronkelijke bestanden blijven behouden. Undo begint na herstel opnieuw.")
                recover = box.addButton("Herstellen",QMessageBox.ButtonRole.AcceptRole)
                remove = box.addButton("Verwijderen",QMessageBox.ButtonRole.DestructiveRole)
                box.addButton("Later",QMessageBox.ButtonRole.RejectRole)
                box.setDefaultButton(recover)
                box.exec()
                if box.clickedButton() is remove:
                    discard(owner)
                elif box.clickedButton() is recover:
                    if self._confirm_discard() and (interrupted or self.confirm_session_discard()):
                        if interrupted:self.restore_recorded_take(owner)
                        else:self.restore_recovery(owner)
            except (ValueError,OSError,RuntimeError) as error:
                self.error("Werk herstellen",error)
            finally:
                owner.close()

    def closeEvent(self, event):
        if self.confirm_recording_close() and self._confirm_discard() and self.confirm_session_discard():
            if self._manual_dialog is not None:
                self._manual_dialog.close()
            self.player.shutdown()
            self.recorder.shutdown()
            if self.recovery is not None:
                self._recovery_timer.stop()
                self.recovery.close()
                self.recovery = None
            event.accept()
        else:
            event.ignore()
