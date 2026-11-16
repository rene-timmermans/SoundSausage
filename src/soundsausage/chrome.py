"""Compact desktop menus and toolbars shared by the two editor modes."""
from PySide6.QtCore import Qt
from .i18n_widgets import QToolBar
from .i18n import LANGUAGES, install_language, language
from .i18n_widgets import QAction
from PySide6.QtGui import QActionGroup
from .icons import make_icon
from .theme import colors


def seek(window, seconds):
    model = window.active_model()
    frame = max(0, min(model.frames, model.cursor + round(seconds * model.sample_rate)))
    if window.player.state == "Playing":
        window.seek_playback(frame)
    else:
        window.player.stop()
        model.select(frame, frame)
    view = window.active_view()
    length = view.view_end - view.view_start
    if frame < view.view_start or frame > view.view_end:
        view.set_view(max(0, frame - length // 2), max(0, frame - length // 2) + length)
    window.selection_changed(frame, frame)
    view.update()


def show_toolbar_labels(window, enabled):
    style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if enabled else Qt.ToolButtonStyle.ToolButtonIconOnly
    for toolbar in window.findChildren(QToolBar):
        toolbar.setToolButtonStyle(style)
    window.update_minimum_size()


def create_actions(window):
    window.action('select_wave', 'Select Waveform', lambda: window.toolbar_controller.select_wave())
    window.actions['select_wave'].setCheckable(True)
    window.actions['select_wave'].setToolTip('Drag to select audio; click to place the cursor.')
    group = QActionGroup(window)
    window.multitrack_tool_actions = {}
    for mode, key, label in (('move', 'move_clips', 'Move Clips'),
                             ('volume', 'volume_line', 'Volume Line'),
                             ('pan', 'pan_line', 'Pan Line')):
        action = window.action(key, label, lambda mode=mode: window.multitrack.set_envelope_mode(mode))
        action.setCheckable(True)
        group.addAction(action)
        window.multitrack_tool_actions[mode] = action
        if mode == 'volume':
            action.setToolTip('Volume line: bottom 0%, middle 100%, top 200%. Multiplies clip and track volume.')
        elif mode == 'pan':
            action.setToolTip('Pan line: top R, middle centre, bottom L. Adds balance to the clip and track pan; centre keeps their settings.')
    window.action('marker_add','Add Marker',window.add_marker,'M')
    window.action('markers','Marker List…',window.open_markers,'Ctrl+Shift+M')
    window.action('marker_previous','Previous Marker',lambda:window.step_marker(-1),'Alt+Left')
    window.action('marker_next','Next Marker',lambda:window.step_marker(1),'Alt+Right')
    window.action("to_start", "Go to Start", window.to_start, "Home")
    window.action("to_end", "Go to End", window.to_end, "End")
    window.action("seek_back", "Back 5 Seconds", lambda: seek(window, -5))
    window.action("seek_forward", "Forward 5 Seconds", lambda: seek(window, 5))
    window.action("record", "Record…", window.record, "R")
    window.actions["record"].setCheckable(True)
    window.actions["record"].setEnabled(not window.no_audio)
    window.action('calibrate','Calibrate Recording…',window.calibrate_recording)
    window.action('punch','Punch In/Out…',lambda:window.record(punch=True),'Shift+R')
    window.actions["record"].setToolTip("Record from the selected microphone or audio interface")
    window.action("discard_recording", "Discard Recording…", window.discard_recording)
    window.actions["discard_recording"].setEnabled(False)
    labels = window.action("toolbar_labels", "Show Toolbar Labels", lambda: None)
    labels.setCheckable(True)
    labels.toggled.connect(lambda checked: show_toolbar_labels(window, checked))
    status = window.action("show_status", "Show Status Bar", lambda: None)
    status.setCheckable(True)
    status.setChecked(window.ui_settings.value("ui/show_status_bar", True, type=bool))
    status.setToolTip("Show or hide the bottom information line (playback state and file details)")
    status.toggled.connect(window.set_status_bar_visible)
    window.action("fullscreen", "Full Screen", lambda: window.showNormal() if window.isFullScreen() else window.showFullScreen(), "F11")


def create_menus(window):
    window.menus = {}

    def menu(name, label):
        result = window.menuBar().addMenu(label)
        result.setToolTipsVisible(True)
        window.menus[name] = result
        return result

    def add(target, keys):
        for key in keys:
            target.addSeparator() if key is None else target.addAction(window.actions[key])

    file = menu("file", "&File")
    add(file, ("new", "open", "close_file", None, "save", "save_as", "save_selection", None,
               "new_session", "open_session", "save_session", "save_session_as", None,
               "import_audio", "mixdown", None, "recover", None, "exit"))
    edit = menu("edit", "&Edit")
    add(edit, ("undo", "redo", "repeat", None, "cut", "copy", "paste", "mix_paste", "delete", "trim", None,
               "select_all", "select_range", "zero"))
    channels = edit.addMenu("Select Channels")
    window.menus["channels"] = channels
    add(channels, ("channels_both", "channels_left", "channels_right"))
    wave_tools = edit.addMenu('Waveform Tools')
    window.menus['wave_tools'] = wave_tools
    add(wave_tools, ('select_wave', 'draw_waveform', None, 'edit_sample'))
    clip_tools = edit.addMenu('Clip Tools')
    window.menus['clip_tools'] = clip_tools
    add(clip_tools, ('move_clips', 'volume_line', 'pan_line'))
    add(edit, (None, "convert_rate", None, "clip_properties", "duplicate_clip", "remove_clip"))
    add(edit,(None,'marker_add','markers'))
    view = menu("view", "&View")
    add(view, ("mode_wave", "mode_multi", None, "zoom_in", "zoom_out", "zoom_full", "zoom_selection", None, "fullscreen"))
    add(view,(None,'marker_previous','marker_next'))
    view.addSeparator()
    window.menus['toolbars'] = view.addMenu('Toolbars')
    transform = menu("transform", "&Transform")
    add(transform, ('remaster', 'track_fx', None))
    wave_edits = transform.addMenu('Waveform Edits')
    window.menus['wave_edits'] = wave_edits
    add(wave_edits, ('invert', 'reverse', 'silence'))
    amplitude = transform.addMenu("&Amplitude")
    amplitude.setToolTipsVisible(True)
    window.menus["amplitude"] = amplitude
    add(amplitude, ("amplify", "channel_mix", "dynamics", "envelope"))

    add(amplitude, ("normalize", None, "fade_in", "fade_out"))
    filters = transform.addMenu("Filters")
    window.menus["filters"] = filters
    add(filters, ("graphic_eq", "parametric_eq", "filter"))
    delay = transform.addMenu("Delay Effects")
    window.menus["delay"] = delay
    add(delay, ("delay", "echo", "reverb"))
    noise = transform.addMenu("Noise Reduction")
    window.menus["noise"] = noise
    add(noise, ("noise_profile", "noise_reduction", "click_removal"))
    timing = transform.addMenu("Time/Pitch")
    window.menus["time_pitch"] = timing
    add(timing, ("stretch", "pitch_shift"))
    special = transform.addMenu("Special")
    window.menus["special"] = special
    add(special, ("distortion", "convolution"))
    generate = menu("generate", "&Generate")
    add(generate, ("tone", "generate_silence"))
    analyze = menu("analyze", "&Analyze")
    add(analyze, ("frequency",))
    favorites = menu("favorites", "F&avorites")
    add(favorites, ("repeat", None, "normalize", "fade_in", "fade_out"))
    options = menu("options", "&Options")
    language_menu=options.addMenu('Language')
    language_menu.setIcon(make_icon('language',colors()))
    window.menus['language']=language_menu
    window.language_actions={};group=QActionGroup(window)
    for code,name in LANGUAGES.items():
        action=QAction(name,window);action.setCheckable(True);action.setChecked(code==language())
        action.triggered.connect(lambda checked=False,code=code:install_language().set_language(code))
        group.addAction(action);language_menu.addAction(action);window.language_actions[code]=action
    install_language().changed.connect(window.update_language_actions)
    options.addSeparator()
    add(options, ("audio_hardware", "calibrate", "record", "punch", "discard_recording", None, "toolbar_labels", "show_status", None, "loop"))
    windows = menu("window", "&Window")
    add(windows, ("mode_wave", "mode_multi", None, "insert_wave", "apply_clip", None, "fullscreen"))
    help_menu = menu("help", "&Help")
    add(help_menu, ("manual", None, "about"))


def create_toolbars(window):
    from .toolbars import WorkspaceToolbars
    window.toolbar_controller = WorkspaceToolbars(window)
