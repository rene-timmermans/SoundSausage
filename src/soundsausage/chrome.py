"""Compact desktop menus and toolbars shared by the two editor modes."""
from PySide6.QtCore import Qt, QSize
from .i18n_widgets import QToolBar
from .i18n import LANGUAGES, install_language, language
from .i18n_widgets import QAction
from PySide6.QtGui import QActionGroup
from .icons import make_icon
from .theme import colors


def seek(window, seconds):
    window.player.stop()
    model = window.active_model()
    frame = max(0, min(model.frames, model.cursor + round(seconds * model.sample_rate)))
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
    add(edit, (None, "edit_sample", "draw_waveform", "convert_rate", None, "clip_properties", "duplicate_clip", "remove_clip"))
    add(edit,(None,'marker_add','markers'))
    view = menu("view", "&View")
    add(view, ("mode_wave", "mode_multi", None, "zoom_in", "zoom_out", "zoom_full", "zoom_selection", None, "fullscreen"))
    add(view,(None,'marker_previous','marker_next'))
    transform = menu("transform", "&Transform")
    add(transform, ('remaster',None,"invert", "reverse", "silence", None))
    add(transform, ("track_fx", None))
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
    def bar(name, groups):
        toolbar = QToolBar(name, window)
        toolbar.setObjectName(name.replace(" ", "") + "Toolbar")
        toolbar.setProperty("compact", True)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        window.addToolBar(toolbar)
        for index, keys in enumerate(groups):
            if index:
                toolbar.addSeparator()
            for key in keys:
                toolbar.addAction(window.actions[key])
        return toolbar

    bar("Working Mode", (("mode_wave", "mode_multi"),))
    bar("File and Edit", (("new", "open", "save"), ("cut", "copy", "paste", "trim"), ("undo", "redo")))
    bar("View", (("zoom_in", "zoom_out", "zoom_full", "zoom_selection"), ("draw_waveform",'marker_add','markers')))
    window.addToolBarBreak()
    window.effects_toolbar = bar("Transform", (("amplify", "normalize", "fade_in", "fade_out"),
                                              ("invert", "reverse", "silence", "frequency")))
    bar("Multitrack", (("insert_wave", "apply_clip"), ("import_audio", "mixdown")))
