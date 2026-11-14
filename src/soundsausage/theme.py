"""Desktop palette, readable controls and accent colours shared by both editors."""
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def luminance(color):
    values = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in color.getRgbF()[:3]]
    return sum(a * b for a, b in zip(values, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    lo, hi = sorted((luminance(first), luminance(second)))
    return (hi + 0.05) / (lo + 0.05)


def blend(first, second, amount):
    return QColor.fromRgbF(*(a * (1 - amount) + b * amount
                             for a, b in zip(first.getRgbF()[:3], second.getRgbF()[:3])))


def readable(color, background, minimum=4.5):
    """Keep the chosen hue, adjusting only as much as its contrast requires."""
    if contrast(color, background) >= minimum:
        return QColor(color)
    target = max((QColor("#000000"), QColor("#ffffff")), key=lambda c: contrast(c, background))
    for step in range(1, 101):
        candidate = QColor(blend(color, target, step / 100).name())
        if contrast(candidate, background) >= minimum:
            return candidate
    return target


@dataclass(frozen=True)
class Colors:
    window: QColor
    text: QColor
    panel: QColor
    button: QColor
    button_text: QColor
    base: QColor
    field_text: QColor
    muted: QColor
    disabled: QColor
    border: QColor
    accent: QColor
    accent_text: QColor
    icon: QColor
    plot: QColor
    plot_text: QColor
    plot_grid: QColor
    waveform: QColor
    workspace: QColor


def from_palette(palette):
    role = QPalette.ColorRole
    group = QPalette.ColorGroup.Active
    get = lambda r: QColor(palette.color(group, r))
    window, button, base = get(role.Window), get(role.Button), get(role.Base)
    text = readable(get(role.WindowText), window)
    button_text = readable(get(role.ButtonText), button)
    accent = get(role.Accent)
    return Colors(
        window, text, blend(window, text, 0.035), button, button_text, base,
        readable(get(role.Text), base), readable(blend(window, text, 0.65), window),
        readable(blend(button, button_text, 0.45), button, 3.0),
        blend(window, text, 0.3), accent, readable(get(role.HighlightedText), accent),
        readable(accent, button, 3.0), QColor("#070d0e"), QColor("#e3eeeb"),
        QColor("#29413f"), QColor("#27efae"), QColor("#404347"),
    )


def stylesheet(c):
    # Explicit foreground/background pairs avoid mixing a dark desktop palette
    # with fixed light toolbar backgrounds.
    n = lambda color: color.name()
    hover = blend(c.button, c.accent, 0.13)
    away_from_text = max((QColor("#000000"), QColor("#ffffff")),
                         key=lambda color: contrast(color, c.accent_text))
    pressed = blend(c.accent, away_from_text, 0.10)
    tool_hover = blend(c.button, c.button_text, .07)
    tool_pressed = blend(c.button, c.button_text, .12)
    return f"""
        QMainWindow, QDialog {{ background: {n(c.window)}; color: {n(c.text)}; }}
        QLabel, QGroupBox {{ color: {n(c.text)}; }}
        QMenuBar, QMenu, QStatusBar {{ background: {n(c.window)}; color: {n(c.text)}; }}
        QMenuBar::item:selected, QMenu::item:selected {{ background: {n(c.accent)}; color: {n(c.accent_text)}; }}
        QMenu::item:disabled {{ color: {n(c.disabled)}; }}
        QToolBar {{ background: {n(c.panel)}; border: none; border-bottom: 1px solid {n(c.border)};
                    spacing: 4px; padding: 4px; }}
        QToolBar::separator {{ background: {n(c.border)}; width: 1px; margin: 4px; }}
        QToolBar[compact="true"] {{ spacing: 2px; padding: 2px; }}
        QToolButton, QPushButton {{ background: {n(c.button)}; color: {n(c.button_text)};
            border: 1px solid {n(c.border)}; border-radius: 4px; padding: 4px 7px; min-height: 18px; }}
        QToolButton:hover:enabled {{ background: {n(tool_hover)}; border-color: {n(c.icon)}; }}
        QPushButton:hover:enabled {{ background: {n(hover)}; border-color: {n(c.icon)}; }}
        QToolButton:focus, QPushButton:focus {{ border-color: {n(c.icon)}; border-style: dashed; }}
        QToolButton:checked:enabled {{
            background: {n(c.button)}; color: {n(c.button_text)}; border-color: {n(c.icon)}; }}
        QPushButton:checked:enabled, QPushButton[primary="true"]:enabled,
        QPushButton:default:enabled {{
            background: {n(c.accent)}; color: {n(c.accent_text)}; border-color: {n(c.icon)}; }}
        QToolButton#qt_toolbar_ext_button {{ padding: 0px; }}
        QToolButton:pressed:enabled {{ background: {n(tool_pressed)}; color: {n(c.button_text)}; border-color: {n(c.icon)}; }}
        QPushButton[primary="true"]:hover:enabled, QPushButton:pressed:enabled {{
            background: {n(pressed)}; color: {n(c.accent_text)}; border-color: {n(c.icon)}; }}
        QToolButton:disabled, QPushButton:disabled {{ background: {n(c.button)}; color: {n(c.disabled)};
            border-color: {n(c.border)}; }}
        QToolBar[compact="true"] QToolButton, QToolButton[compact="true"], QPushButton[compact="true"] {{
            padding: 2px; min-width: 20px; min-height: 18px; border-radius: 2px; }}
        QWidget#TransportPanel {{ background: {n(c.panel)}; border-top: 1px solid {n(c.border)}; }}
        QLineEdit, QComboBox {{ background: {n(c.base)}; color: {n(c.field_text)};
            border: 1px solid {n(c.border)}; border-radius: 3px; padding: 3px;
            selection-background-color: {n(c.accent)}; selection-color: {n(c.accent_text)}; }}
        QAbstractSpinBox {{ background: {n(c.base)}; color: {n(c.field_text)};
            selection-background-color: {n(c.accent)}; selection-color: {n(c.accent_text)}; }}
        QLineEdit:focus, QComboBox:focus {{ border-color: {n(c.icon)}; }}
        QLineEdit[compact="true"] {{ padding: 0px 3px; border-radius: 1px; }}
        QGroupBox {{ border: 1px solid {n(c.border)}; border-radius: 4px; margin-top: 8px; padding-top: 5px; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 9px; padding: 0 4px; }}
        QStatusBar::item {{ border: none; }}
        QLabel#TimeDisplay {{ background: {n(c.panel)}; color: {n(c.text)};
            border: none; padding: 0px; }}
        QWidget#TrackControls {{ background: {n(c.panel)}; border: 1px solid {n(c.border)}; border-radius: 4px; }}
        QPushButton[trackState="mute"]:checked {{ background: #ae3544; color: #ffffff; border-color: #ae3544; }}
        QPushButton[trackState="solo"]:checked {{ background: #e3be52; color: #15130b; border-color: #b38d24; }}
        QScrollBar:horizontal {{ background: {n(c.panel)}; height: 12px; margin: 2px 0; border-radius: 3px; }}
        QScrollBar::handle:horizontal {{ background: {n(c.icon)}; min-width: 28px; border-radius: 3px; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
        QProgressBar {{ border: 1px solid {n(c.border)}; border-radius: 2px;
            background: {n(c.plot)}; color: {n(c.plot_text)}; text-align: center; }}
        QProgressBar::chunk {{ background: #187646; }}
        QToolTip {{ background: {n(c.base)}; color: {n(c.field_text)}; border: 1px solid {n(c.border)}; padding: 4px; }}
    """


class Theme(QObject):
    changed = Signal()

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self._applying = False
        self.colors = from_palette(app.palette())
        app.paletteChanged.connect(self.update)
        self.update(app.palette())

    def update(self, palette):
        if self._applying:
            return
        self._applying = True
        try:
            self.colors = from_palette(palette)
            self.app.setStyleSheet(stylesheet(self.colors))
            self.changed.emit()
        finally:
            self._applying = False


def install_theme(app=None):
    app = app or QApplication.instance()
    if not hasattr(app, "_soundsausage_theme"):
        app._soundsausage_theme = Theme(app)
    return app._soundsausage_theme


def colors():
    app = QApplication.instance()
    theme = getattr(app, "_soundsausage_theme", None)
    return theme.colors if theme else from_palette(app.palette())
