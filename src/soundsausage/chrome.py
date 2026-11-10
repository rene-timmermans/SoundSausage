"""Compact desktop menus and toolbars shared by the two editor modes."""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QToolBar


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


def create_actions(window):
    window.action("to_start", "Go to Start", window.to_start, "Home")
    window.action("to_end", "Go to End", window.to_end, "End")
    window.action("seek_back", "Back 5 Seconds", lambda: seek(window, -5))
    window.action("seek_forward", "Forward 5 Seconds", lambda: seek(window, 5))
    window.action("record", "Record", lambda: None)
    window.actions["record"].setEnabled(False)
    window.actions["record"].setToolTip("Recording is not available yet")
    labels = window.action("toolbar_labels", "Show Toolbar Labels", lambda: None)
    labels.setCheckable(True)
    labels.toggled.connect(lambda checked: show_toolbar_labels(window, checked))
    status = window.action("show_status", "Show Status Bar", lambda: None)
    status.setCheckable(True)
    status.setChecked(True)
    status.toggled.connect(lambda checked: window.statusBar().setVisible(checked))
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
               "import_audio", "mixdown", None, "exit"))
    edit = menu("edit", "&Edit")
    add(edit, ("undo", "redo", "repeat", None, "cut", "copy", "paste", "mix_paste", "delete", "trim", None,
               "select_all", "select_range", "zero", None, "convert_rate", None, "clip_properties", "duplicate_clip", "remove_clip"))
    view = menu("view", "&View")
    add(view, ("mode_wave", "mode_multi", None, "zoom_in", "zoom_out", "zoom_full", "zoom_selection", None, "fullscreen"))
    transform = menu("transform", "&Transform")
    add(transform, ("invert", "reverse", "silence", None))
    amplitude = transform.addMenu("&Amplitude")
    amplitude.setToolTipsVisible(True)
    window.menus["amplitude"] = amplitude
    add(amplitude, ("amplify", "channel_mix", "dynamics", "envelope"))

    def unavailable(target, label):
        action = target.addAction(label)
        action.setEnabled(False)
        action.setToolTip("Not available yet")

    add(amplitude, ("normalize", None, "fade_in", "fade_out"))
    for name, items in (
        ("Delay Effects", ("Delay…", "Echo…", "Reverb…")),
        ("Filters", ("Graphic Equalizer…", "Parametric Equalizer…")),
        ("Noise Reduction", ("Noise Reduction…", "Click Removal…")),
        ("Special", ("Distortion…", "Convolution…")),
        ("Time/Pitch", ("Stretch…", "Pitch Shift…")),
    ):
        group = transform.addMenu(name)
        group.setToolTipsVisible(True)
        for item in items:
            unavailable(group, item)
    generate = menu("generate", "&Generate")
    add(generate, ("tone", "generate_silence"))
    analyze = menu("analyze", "&Analyze")
    add(analyze, ("frequency",))
    favorites = menu("favorites", "F&avorites")
    add(favorites, ("repeat", None, "normalize", "fade_in", "fade_out"))
    options = menu("options", "&Options")
    add(options, ("audio_hardware", None, "toolbar_labels", "show_status", None, "loop"))
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
    bar("View", (("zoom_in", "zoom_out", "zoom_full", "zoom_selection"),))
    window.addToolBarBreak()
    window.effects_toolbar = bar("Transform", (("amplify", "normalize", "fade_in", "fade_out"),
                                              ("invert", "reverse", "silence", "frequency")))
    bar("Multitrack", (("insert_wave", "apply_clip"), ("import_audio", "mixdown")))
