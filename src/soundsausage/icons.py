"""Small vector icons, rendered in the current desktop accent and state colours."""
from pathlib import Path

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF


ICON_ACTIONS = {"new", "open", "save", "save_session", "save_session_as", "undo", "redo",
                "cut", "copy", "paste", "trim", "zoom_in", "zoom_out", "zoom_full", "zoom_selection",
                "play", "pause", "stop", "loop", "mode_wave", "mode_multi", "import_audio", "mixdown"}
PRIMARY_ACTIONS = {"open", "save", "play", "import_audio", "mixdown"}
_CACHE = {}
_APPLICATION_ICONS = {}
_ASSETS = Path(__file__).with_name("assets")


def mascot_icon():
    """The isolated mascot for in-program artwork at any size."""
    return QIcon(str(_ASSETS / "soundsausage-mascot.png"))


def taskbar_icon():
    """The purple tile with transparent outer corners for taskbars and launchers."""
    return QIcon(str(_ASSETS / "soundsausage.png"))


def application_icon(*, device_pixel_ratio=None):
    """Supply small caption icons and larger taskbar icons in one native set.

    Linux window managers use the same window icon property for captions and
    taskbars. Publish both variants at their respective pixel sizes instead of
    overriding the window with a single image that also replaces its task icon.
    """
    if device_pixel_ratio is None:
        screen = QGuiApplication.primaryScreen()
        device_pixel_ratio = screen.devicePixelRatio() if screen else 1.0
    ratio = float(device_pixel_ratio)
    if ratio not in _APPLICATION_ICONS:
        small, large = mascot_icon(), taskbar_icon()
        icon = QIcon()
        for size in (16, 20, 22, 24, 32, 40, 48, 64, 128, 256):
            pixels = max(1, round(size * ratio))
            source = small if size <= 24 else large
            icon.addPixmap(source.pixmap(pixels, pixels))
        _APPLICATION_ICONS[ratio] = icon
    return QIcon(_APPLICATION_ICONS[ratio])


def draw(p, name, color):
    line = lambda x1, y1, x2, y2: p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    rect = lambda x, y, w, h: p.drawRect(QRectF(x, y, w, h))
    if name == "open":
        path = QPainterPath(QPointF(3, 19))
        for x, y in ((3, 6), (9, 6), (11, 9), (20, 9), (20, 12), (7, 12), (3, 19), (18, 19), (22, 12)):
            path.lineTo(x, y)
        p.drawPath(path)
    elif name in ("save", "save_session", "save_session_as"):
        rect(4, 3, 16, 18)
        rect(8, 3, 8, 6)
        rect(8, 14, 8, 7)
        line(14, 5, 14, 7)
    elif name == "new":
        rect(5, 3, 14, 18)
        line(9, 12, 15, 12)
        line(12, 9, 12, 15)
    elif name in ("undo", "redo"):
        if name == "redo":
            p.translate(24, 0)
            p.scale(-1, 1)
        path = QPainterPath(QPointF(5, 9))
        path.cubicTo(18, 3, 23, 13, 17, 19)
        p.drawPath(path)
        line(5, 9, 6, 3)
        line(5, 9, 11, 11)
    elif name == "cut":
        p.drawEllipse(QRectF(3, 15, 5, 5))
        p.drawEllipse(QRectF(15, 15, 5, 5))
        line(7, 16, 18, 4)
        line(16, 16, 5, 4)
    elif name == "copy":
        rect(4, 3, 12, 15)
        rect(9, 8, 12, 14)
    elif name == "paste":
        rect(5, 5, 14, 17)
        rect(9, 3, 6, 5)
        line(9, 12, 15, 12)
        line(9, 16, 15, 16)
    elif name == "trim":
        line(5, 3, 5, 21)
        line(19, 3, 19, 21)
        line(1, 12, 23, 12)
        line(9, 8, 5, 12)
        line(9, 16, 5, 12)
        line(15, 8, 19, 12)
        line(15, 16, 19, 12)
    elif name in ("zoom_in", "zoom_out", "zoom_full", "zoom_selection"):
        p.drawEllipse(QRectF(3, 3, 13, 13))
        line(15, 15, 21, 21)
        line(6, 9.5, 13, 9.5)
        if name == "zoom_in":
            line(9.5, 6, 9.5, 13)
        elif name in ("zoom_full", "zoom_selection"):
            line(6, 6, 6, 13)
            line(13, 6, 13, 13)
    elif name in ("play", "pause", "stop"):
        p.setBrush(color)
        if name == "play":
            p.drawPolygon(QPolygonF([QPointF(7, 4), QPointF(20, 12), QPointF(7, 20)]))
        elif name == "pause":
            rect(5, 4, 4, 16)
            rect(15, 4, 4, 16)
        else:
            rect(5, 5, 14, 14)
    elif name == "loop":
        p.drawEllipse(QRectF(3, 6, 8, 12))
        p.drawEllipse(QRectF(13, 6, 8, 12))
        line(10, 10, 14, 14)
        line(10, 14, 14, 10)
    elif name == "mode_wave":
        for x, y in ((3, 9), (6, 5), (9, 11), (12, 3), (15, 8), (18, 6), (21, 10)):
            line(x, y, x, 24 - y)
    elif name == "mode_multi":
        for y, x in ((4, 4), (10, 8), (16, 5)):
            rect(x, y, 19 - x, 4)
    elif name == "import_audio":
        rect(12, 4, 9, 16)
        line(2, 12, 16, 12)
        line(12, 8, 16, 12)
        line(12, 16, 16, 12)
    elif name == "mixdown":
        for x in (4, 12, 20):
            line(x, 3, x, 7)
            line(x, 7, 12, 14)
        line(12, 14, 12, 21)
        line(8, 17, 12, 21)
        line(16, 17, 12, 21)
    elif name == "more":
        for x in (5, 12):
            line(x, 6, x + 6, 12)
            line(x + 6, 12, x, 18)


def make_icon(name, colors, primary=False, checked_accent=False):
    key = (name, colors.icon.rgba(), colors.accent_text.rgba(), colors.disabled.rgba(), primary, checked_accent)
    if key in _CACHE:
        return QIcon(_CACHE[key])
    icon = QIcon()
    for mode in (QIcon.Mode.Normal, QIcon.Mode.Active, QIcon.Mode.Disabled, QIcon.Mode.Selected):
        for state in (QIcon.State.Off, QIcon.State.On):
            color = (colors.disabled if mode == QIcon.Mode.Disabled else colors.accent_text
                     if primary or (checked_accent and state == QIcon.State.On)
                     or mode == QIcon.Mode.Selected else colors.icon)
            for size in (16, 20, 24, 32, 48):
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.scale(size / 24, size / 24)
                painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine,
                                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                draw(painter, name, color)
                painter.end()
                icon.addPixmap(pixmap, mode, state)
    if len(_CACHE) >= 256:
        _CACHE.clear()
    _CACHE[key] = icon
    return QIcon(icon)
