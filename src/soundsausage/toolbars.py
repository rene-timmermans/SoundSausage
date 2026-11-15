"""Dockable workspace bars and options for the active editing tool."""
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QBoxLayout, QHBoxLayout, QSizePolicy

from .i18n import bind
from .i18n_widgets import QToolBar, QToolButton, QWidget, QLabel
from .icons import application_icon


class WorkspaceToolbars:
    STATE_VERSION = 1

    def __init__(self, window):
        self.window = window
        self.bars = {}
        self.general = self.bar('General', 'GeneralToolbar', Qt.ToolBarArea.TopToolBarArea)
        self.add_groups(self.general, (
            ('mode_wave', 'mode_multi'), ('new', 'open', 'save'),
            ('cut', 'copy', 'paste', 'trim'), ('undo', 'redo'),
            ('insert_wave', 'apply_clip', 'import_audio', 'mixdown'),
        ))
        window.addToolBarBreak(Qt.ToolBarArea.TopToolBarArea)
        self.options = self.bar('Tool Options', 'ToolOptionsToolbar', Qt.ToolBarArea.TopToolBarArea)
        self.tools = self.bar('Tools', 'ToolsToolbar', Qt.ToolBarArea.LeftToolBarArea)
        window.action('select_wave', 'Select Waveform', self.select_wave)
        window.actions['select_wave'].setCheckable(True)
        window.actions['select_wave'].setToolTip('Drag to select audio; click to place the cursor.')
        group = QActionGroup(window)
        self.multi_tools = {}
        for mode, key, label in (('move', 'move_clips', 'Move Clips'),
                                 ('volume', 'volume_line', 'Volume Line'),
                                 ('pan', 'pan_line', 'Pan Line')):
            action = window.action(key, label, lambda mode=mode: window.multitrack.set_envelope_mode(mode))
            action.setCheckable(True)
            group.addAction(action)
            self.multi_tools[mode] = action
            if mode == 'volume':
                action.setToolTip('Volume line: bottom 0%, middle 100%, top 200%. Multiplies clip and track volume.')
            elif mode == 'pan':
                action.setToolTip('Pan line: top R, middle centre, bottom L. Adds balance to the clip and track pan; centre keeps their settings.')
        self.add_groups(self.tools, (('select_wave', 'draw_waveform', 'move_clips', 'volume_line', 'pan_line'),
                                   ('marker_add', 'markers')))
        editor = window.multitrack
        # These controls also work in the standalone editor. The main window
        # exposes them through shared actions and its dockable options bar.
        editor.command_row.hide()
        editor.tool_row.hide()
        editor.envelope_buttons = {mode: self.tools.widgetForAction(action)
                                   for mode, action in self.multi_tools.items()}
        for key, label, callback in (('add_track', '+ Track', editor.add_track),
                                     ('remove_track', '− Track', editor.remove_track)):
            action = window.action(key, label, callback)
            self.general.addAction(action)
            window.menus['window'].addAction(action)
        self.name = QLabel()
        self.name.setMargin(4)
        self.options.addWidget(self.name)
        self.options.addSeparator()
        self.option_groups = {}
        for name, keys in (('select', ('select_range', 'zero')),
                           ('draw', ('edit_sample',)),
                           ('clip', ('clip_properties', 'duplicate_clip', 'remove_clip'))):
            group_widget = QWidget()
            row = QHBoxLayout(group_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(2)
            for key in keys:
                button = QToolButton()
                button.setDefaultAction(window.actions[key])
                row.addWidget(button)
            self.option_groups[name] = self.options.addWidget(group_widget)
            self.options.orientationChanged.connect(
                lambda orientation, row=row: self.orient(row, orientation))
        self.wave_options = QWidget()
        row = QHBoxLayout(self.wave_options)
        row.setContentsMargins(4, 0, 4, 0)
        row.addWidget(window.channel_label_widget)
        row.addWidget(window.channel_choice)
        self.wave_options_action = self.options.addWidget(self.wave_options)
        self.options.orientationChanged.connect(lambda orientation: self.orient(self.wave_options.layout(), orientation))
        self.multi_options = QWidget()
        row = QHBoxLayout(self.multi_options)
        row.setContentsMargins(4, 0, 4, 0)
        row.addWidget(editor.reset_line)
        self.multi_options_action = self.options.addWidget(self.multi_options)
        self.hint = editor.envelope_hint
        self.hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.hint.setMinimumWidth(0)
        self.hint_action = self.options.addWidget(self.hint)
        tools_menu = window.menus['edit'].addMenu('Tools')
        for key in ('select_wave', 'draw_waveform', 'move_clips', 'volume_line', 'pan_line'):
            tools_menu.addAction(window.actions[key])
        window.actions['draw_waveform'].toggled.connect(self.sync)
        editor.tool_changed.connect(self.sync)
        window.actions['toolbar_labels'].toggled.connect(self.show_labels)
        self.sync()

    def show_labels(self, enabled):
        style = (Qt.ToolButtonStyle.ToolButtonTextBesideIcon if enabled
                 else Qt.ToolButtonStyle.ToolButtonIconOnly)
        for action in self.option_groups.values():
            for button in action.defaultWidget().findChildren(QToolButton):
                button.setToolButtonStyle(style)

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

    @staticmethod
    def orient(layout, orientation):
        layout.setDirection(QBoxLayout.Direction.LeftToRight if orientation == Qt.Orientation.Horizontal
                            else QBoxLayout.Direction.TopToBottom)

    def select_wave(self):
        self.window.actions['draw_waveform'].setChecked(False)
        self.sync()

    def sync(self, *_):
        window = self.window
        multi = window.mode == 'multitrack'
        busy = window.recording_busy
        drawing = window.actions['draw_waveform'].isChecked()
        for bar in (self.tools, self.options):
            bar.setEnabled(not busy)
        window.actions['select_wave'].setChecked(not drawing)
        window.actions['select_wave'].setEnabled(not busy and not multi)
        for key in ('select_wave', 'draw_waveform'):
            window.actions[key].setVisible(not multi)
        for mode, action in self.multi_tools.items():
            action.setVisible(multi)
            action.setEnabled(multi and not busy)
            action.setChecked(window.multitrack.timeline.envelope_mode == mode)
        for key in ('add_track', 'remove_track'):
            window.actions[key].setVisible(multi)
            window.actions[key].setEnabled(multi and not busy)
        window.actions['remove_track'].setEnabled(multi and not busy and len(window.session.tracks) > 1)
        self.option_groups['select'].setVisible(not multi and not drawing)
        self.option_groups['draw'].setVisible(not multi and drawing)
        self.option_groups['clip'].setVisible(multi)
        self.wave_options_action.setVisible(not multi)
        self.multi_options_action.setVisible(multi and window.multitrack.timeline.envelope_mode != 'move')
        self.hint_action.setVisible(multi)
        self.name.setText('Move Clips' if multi and window.multitrack.timeline.envelope_mode == 'move'
                          else 'Volume Line' if multi and window.multitrack.timeline.envelope_mode == 'volume'
                          else 'Pan Line' if multi else 'Draw Waveform' if drawing else 'Select Waveform')
        window.multitrack.update_envelope_controls()

    def restore(self):
        window = self.window
        saved = window.ui_settings.value('ui/toolbar_layout', None)
        restored = False
        if saved:
            try:
                restored = window.restoreState(saved, self.STATE_VERSION)
            except (TypeError, ValueError):
                pass
        window.actions['toolbar_labels'].setChecked(window.ui_settings.value('ui/toolbar_labels', False, type=bool))
        self.sync()
        return restored

    def save(self):
        window = self.window
        window.ui_settings.setValue('ui/toolbar_layout', window.saveState(self.STATE_VERSION))
        window.ui_settings.setValue('ui/toolbar_labels', window.actions['toolbar_labels'].isChecked())
