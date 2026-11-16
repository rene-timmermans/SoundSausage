"""Dockable commands and tools, with compact controls inside each editor."""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy

from .i18n import bind
from .i18n_widgets import QToolBar, QToolButton, QWidget
from .icons import application_icon
from .effect_tools import EffectToolButton


class WorkspaceToolbars:
    STATE_VERSION = 2

    def __init__(self, window):
        self.window = window
        self.bars = {}
        self.general = self.bar('General', 'GeneralToolbar', Qt.ToolBarArea.TopToolBarArea)
        self.add_groups(self.general, (
            ('mode_wave', 'mode_multi'), ('new', 'open', 'save'),
            ('cut', 'copy', 'paste', 'trim'), ('undo', 'redo'), ('marker_add', 'markers'),
            ('insert_wave', 'apply_clip', 'import_audio', 'mixdown'),
        ))
        self.tools = self.bar('Tools', 'ToolsToolbar', Qt.ToolBarArea.LeftToolBarArea)
        self.multi_tools = window.multitrack_tool_actions
        self.add_groups(self.tools, (('select_wave', 'draw_waveform', 'move_clips', 'volume_line', 'pan_line'),))
        self.tools.addSeparator()
        self.effect_buttons = {}
        self.effect_widgets = []
        remaster = QToolButton()
        remaster.setDefaultAction(window.actions['remaster'])
        self.effect_widgets.append(self.tools.addWidget(remaster))
        self.tools.toolButtonStyleChanged.connect(remaster.setToolButtonStyle)
        groups = (
            ('wave_edits', 'Waveform Edits', window.menus['wave_edits'], 'invert'),
            ('amplitude', 'Amplitude', window.menus['amplitude'], 'amplify'),
            ('filters', 'Filters', window.menus['filters'], 'graphic_eq'),
            ('delay', 'Delay Effects', window.menus['delay'], 'delay'),
            ('noise', 'Noise Reduction', window.menus['noise'], 'noise_reduction'),
            ('time_pitch', 'Time/Pitch', window.menus['time_pitch'], 'stretch'),
            ('special', 'Special', window.menus['special'], 'distortion'),
        )
        for key, title, menu, default in groups:
            button = EffectToolButton(window, key, title, menu, default, self.tools)
            button.setIconSize(self.tools.iconSize())
            button.setToolButtonStyle(self.tools.toolButtonStyle())
            self.tools.iconSizeChanged.connect(button.setIconSize)
            self.tools.toolButtonStyleChanged.connect(button.setToolButtonStyle)
            self.effect_buttons[key] = button
            self.effect_widgets.append(self.tools.addWidget(button))
        track_fx = QToolButton()
        track_fx.setDefaultAction(window.actions['track_fx'])
        self.track_effects_action = self.tools.addWidget(track_fx)
        self.tools.toolButtonStyleChanged.connect(track_fx.setToolButtonStyle)
        editor = window.multitrack
        # These controls also work in the standalone editor. The main window
        # exposes them through shared actions and editor-local controls.
        editor.command_row.hide()
        editor.tool_row.hide()
        editor.envelope_buttons = {mode: self.tools.widgetForAction(action)
                                   for mode, action in self.multi_tools.items()}
        for key, label, callback in (('add_track', '+ Track', editor.add_track),
                                     ('remove_track', '− Track', editor.remove_track)):
            action = window.action(key, label, callback)
            self.general.addAction(action)
            window.menus['window'].addAction(action)
        self.clip_controls = QWidget()
        row = QHBoxLayout(self.clip_controls)
        row.setContentsMargins(2, 0, 2, 0)
        row.setSpacing(4)
        for key in ('clip_properties', 'duplicate_clip', 'remove_clip'):
            button = QToolButton()
            button.setProperty('compact', True)
            button.setDefaultAction(window.actions[key])
            row.addWidget(button)
        row.addWidget(editor.reset_line)
        editor.envelope_hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        row.addWidget(editor.envelope_hint, 1)
        editor.layout().insertWidget(0, self.clip_controls)
        window.actions['draw_waveform'].toggled.connect(self.sync)
        editor.tool_changed.connect(self.sync)
        self.sync()

    def bar(self, title, name, area):
        window = self.window
        toolbar = QToolBar(title, window)
        toolbar.setObjectName(name)
        toolbar.setWindowIcon(application_icon())
        toolbar.setProperty('compact', True)
        toolbar.setMovable(True)
        toolbar.setFloatable(True)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        window.addToolBar(area, toolbar)
        bind(toolbar.toggleViewAction(), 'setText', title)
        window.menus['toolbars'].addAction(toolbar.toggleViewAction())
        self.bars[name] = toolbar
        return toolbar

    def add_groups(self, toolbar, groups):
        for index, keys in enumerate(groups):
            if index:
                toolbar.addSeparator()
            for key in keys:
                toolbar.addAction(self.window.actions[key])

    def select_wave(self):
        self.window.actions['draw_waveform'].setChecked(False)
        self.sync()

    def sync(self, *_):
        window = self.window
        multi = window.mode == 'multitrack'
        busy = window.recording_busy
        drawing = window.actions['draw_waveform'].isChecked()
        self.tools.setEnabled(not busy)
        self.clip_controls.setEnabled(not busy)
        window.menus['wave_tools'].menuAction().setVisible(not multi)
        window.menus['clip_tools'].menuAction().setVisible(multi)
        window.actions['select_wave'].setChecked(not drawing)
        window.actions['select_wave'].setEnabled(not busy and not multi)
        for key in ('select_wave', 'draw_waveform'):
            window.actions[key].setVisible(not multi)
        for action in self.effect_widgets:
            action.setVisible(not multi)
        self.track_effects_action.setVisible(multi)
        for mode, action in self.multi_tools.items():
            action.setVisible(multi)
            action.setEnabled(multi and not busy)
            action.setChecked(window.multitrack.timeline.envelope_mode == mode)
        for key in ('add_track', 'remove_track'):
            window.actions[key].setVisible(multi)
            window.actions[key].setEnabled(multi and not busy)
        window.actions['remove_track'].setEnabled(multi and not busy and len(window.session.tracks) > 1)
        window.sample_button.setVisible(not multi and drawing and window.document.frames > 0)
        window.multitrack.reset_line.setVisible(window.multitrack.timeline.envelope_mode != 'move')
        window.multitrack.update_envelope_controls()

    def restore(self):
        window = self.window
        for button in self.effect_buttons.values():
            button.restore()
        saved = window.ui_settings.value('ui/toolbar_layout', None)
        restored = False
        if saved:
            try:
                restored = window.restoreState(saved, self.STATE_VERSION)
                if not restored:
                    # Restore the previous three-bar layout before discarding
                    # its options bar, preserving the other bars' positions and
                    # visibility without retaining an empty toolbar row.
                    legacy = QToolBar(window)
                    legacy.setObjectName('ToolOptionsToolbar')
                    window.addToolBar(legacy)
                    legacy.hide()
                    try:
                        restored = window.restoreState(saved, 1)
                    finally:
                        window.removeToolBar(legacy)
                        legacy.hide()
                        legacy.deleteLater()
            except (TypeError, ValueError):
                pass
        window.actions['toolbar_labels'].setChecked(window.ui_settings.value('ui/toolbar_labels', False, type=bool))
        self.sync()
        return restored

    def save(self):
        window = self.window
        for button in self.effect_buttons.values():
            button.save()
        window.ui_settings.setValue('ui/toolbar_layout', window.saveState(self.STATE_VERSION))
        window.ui_settings.setValue('ui/toolbar_labels', window.actions['toolbar_labels'].isChecked())
