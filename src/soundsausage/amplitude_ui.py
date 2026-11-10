"""Amplitude dialogs with editable curves and non-destructive listening previews."""
from bisect import bisect_left

import numpy as np
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QGroupBox, QLabel, QDoubleSpinBox, QComboBox, QCheckBox, QSlider,
    QDialogButtonBox, QPushButton, QMessageBox, QRadioButton,
)

from .audio import validate_audio
from .playback import Playback
from .theme import colors


def spin(value, low, high, suffix="", decimals=1):
    field = QDoubleSpinBox()
    field.setRange(low, high)
    field.setDecimals(decimals)
    field.setSuffix(suffix)
    field.setValue(value)
    field.setKeyboardTracking(False)
    return field


class EffectDialog(QDialog):
    effect_name = ""

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(parent)
        self.document = document
        self.no_audio = no_audio
        self.player = Playback(self, devices=getattr(parent, "audio_devices", None))
        self.player.failed.connect(lambda message: QMessageBox.warning(self, "Preview", message))
        self.player.state_changed.connect(self.preview_state)

    def add_footer(self, layout):
        note = QLabel("Applies to the selection, or the whole waveform if nothing is selected.\n"
                      "Preview plays the first 8 seconds without changing the waveform.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.preview_button = self.button_box.addButton("Preview", QDialogButtonBox.ButtonRole.ActionRole)
        self.preview_button.setEnabled(not self.no_audio)
        if self.no_audio:
            self.preview_button.setToolTip("Audio playback is disabled for this run")
        self.preview_button.clicked.connect(self.preview)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        for control in self.findChildren(QDoubleSpinBox):
            control.valueChanged.connect(self.stop_preview)
        for control in self.findChildren(QCheckBox):
            control.toggled.connect(self.stop_preview)
        for control in self.findChildren(QRadioButton):
            control.toggled.connect(self.stop_preview)
        for control in self.findChildren(QComboBox):
            control.currentIndexChanged.connect(self.stop_preview)
        for control in self.findChildren(CurveEditor):
            control.changed.connect(self.stop_preview)

    def preview_state(self, state):
        if hasattr(self, "preview_button"):
            self.preview_button.setText("Stop Preview" if state != "Stopped" else "Preview")

    def stop_preview(self, *_):
        if self.player.state != "Stopped":
            self.player.stop()

    def preview_samples(self):
        data = self.document.read(*self.document.effect_range)
        self.document.dsp.process(self.effect_name, data, self.document.sample_rate, **self.settings())
        validate_audio(data, self.document.sample_rate)
        return np.ascontiguousarray(data[:8 * self.document.sample_rate])

    def preview(self):
        if self.no_audio:
            return
        if self.player.state != "Stopped":
            self.player.stop()
            return
        try:
            data = self.preview_samples()
            self.player.play(data, self.document.sample_rate)
        except (ValueError, OSError, RuntimeError) as error:
            QMessageBox.warning(self, "Preview", str(error))

    def done(self, result):
        self.player.shutdown()
        super().done(result)


class ChannelMixerDialog(EffectDialog):
    effect_name = "channel_mix"
    PRESETS = (
        ("Default", ((100, 0), (0, 100))),
        ("Swap Left / Right", ((0, 100), (100, 0))),
        ("Mono (L + R average)", ((50, 50), (50, 50))),
        ("Left to Both", ((100, 0), (100, 0))),
        ("Right to Both", ((0, 100), (0, 100))),
        ("Side Signal (L − R)", ((50, -50), (50, -50))),
    )

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle("Channel Mixer")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        self.presets = QComboBox()
        self.presets.addItems(["Custom", *(p[0] for p in self.PRESETS)])
        layout.addWidget(self.presets)
        self.weights, self.sliders, self.invert = [], [], []
        self._setting_preset = False
        for output in range(2):
            group = QGroupBox("New Left Channel" if output == 0 else "New Right Channel")
            grid = QGridLayout(group)
            weights, sliders = [], []
            for source in range(2):
                label = QLabel("From Left" if source == 0 else "From Right")
                field = spin(100 if source == output else 0, -200, 200, " %")
                field.setAccessibleName(f"{'Left' if output == 0 else 'Right'} output from {'left' if source == 0 else 'right'}")
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(-2000, 2000)
                slider.setValue(round(field.value() * 10))
                slider.setAccessibleName(field.accessibleName())
                slider.valueChanged.connect(lambda value, f=field: f.setValue(value / 10))
                field.valueChanged.connect(lambda value, s=slider: s.setValue(round(value * 10)))
                field.valueChanged.connect(self.custom)
                label.setBuddy(field)
                grid.addWidget(label, source, 0)
                grid.addWidget(slider, source, 1)
                grid.addWidget(field, source, 2)
                weights.append(field)
                sliders.append(slider)
            invert = QCheckBox("Invert output polarity")
            invert.toggled.connect(self.custom)
            grid.addWidget(invert, 2, 0, 1, 3)
            self.weights.append(weights)
            self.sliders.append(sliders)
            self.invert.append(invert)
            layout.addWidget(group)
        note = QLabel("Negative percentages invert an input's polarity. Mono mixes keep two channels.\n"
                      "Mixing can raise the level above 0 dBFS; lower the percentages if needed.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.presets.setCurrentIndex(1)
        self.presets.currentIndexChanged.connect(self.preset)
        self.add_footer(layout)

    def custom(self, *_):
        if not self._setting_preset:
            self.presets.setCurrentIndex(0)

    def preset(self, index):
        if index <= 0:
            return
        self._setting_preset = True
        for row, values in enumerate(self.PRESETS[index - 1][1]):
            for field, value in zip(self.weights[row], values):
                field.setValue(value)
            self.invert[row].setChecked(False)
        self._setting_preset = False

    def settings(self):
        return dict(matrix=tuple(tuple(field.value() / 100 * (-1 if self.invert[row].isChecked() else 1)
                                       for field in weights) for row, weights in enumerate(self.weights)))


class CurveEditor(QWidget):
    """Small, bounded point editor; endpoints keep their horizontal position."""
    changed = Signal()
    selected = Signal(int)

    def __init__(self, x_range, y_range, points, x_label, y_label, parent=None):
        super().__init__(parent)
        self.x_range, self.y_range = x_range, y_range
        self.x_label, self.y_label = x_label, y_label
        self.points = tuple(points)
        self.index = 0
        self._drag = False
        self.setMinimumSize(420, 220)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"{y_label} by {x_label}; click to add or drag points, Delete to remove")
        self.setToolTip("Click to add a point; drag to move. Right-click or Delete removes an interior point.")

    def plot_rect(self):
        return QRectF(57, 16, max(1, self.width() - 78), max(1, self.height() - 62))

    def point_position(self, point):
        rect = self.plot_rect()
        x, y = point
        return QPointF(rect.left() + (x - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * rect.width(),
                       rect.bottom() - (y - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * rect.height())

    def position_value(self, position):
        rect = self.plot_rect()
        x = self.x_range[0] + (position.x() - rect.left()) / rect.width() * (self.x_range[1] - self.x_range[0])
        y = self.y_range[0] + (rect.bottom() - position.y()) / rect.height() * (self.y_range[1] - self.y_range[0])
        return (round(min(self.x_range[1], max(self.x_range[0], x)), 1),
                round(min(self.y_range[1], max(self.y_range[0], y)), 1))

    def set_points(self, points):
        self.points = tuple(points)
        self.index = 0
        self.changed.emit()
        self.selected.emit(self.index)
        self.update()

    def move_point(self, x, y):
        points = list(self.points)
        index = self.index
        if index == 0 or index == len(points) - 1:
            x = points[index][0]
        else:
            x = min(points[index + 1][0] - .1, max(points[index - 1][0] + .1, x))
        points[index] = (round(x, 1), round(min(self.y_range[1], max(self.y_range[0], y)), 1))
        self.points = tuple(points)
        self.changed.emit()
        self.selected.emit(index)
        self.update()

    def remove_point(self):
        if 0 < self.index < len(self.points) - 1:
            points = list(self.points)
            del points[self.index]
            self.set_points(points)

    def hit(self, position):
        for index, point in enumerate(self.points):
            if (self.point_position(point) - position).manhattanLength() < 14:
                return index
        return None

    def mousePressEvent(self, event):
        position = event.position()
        index = self.hit(position)
        if event.button() == Qt.MouseButton.RightButton:
            if index is not None:
                self.index = index
                self.remove_point()
            return
        if event.button() != Qt.MouseButton.LeftButton or not self.plot_rect().contains(position):
            return
        if index is None:
            point = self.position_value(position)
            index = bisect_left(self.points, point)
            if len(self.points) >= 64 or index == 0 or index == len(self.points) or any(
                    abs(p[0] - point[0]) < .1 for p in self.points):
                return
            points = list(self.points)
            points.insert(index, point)
            self.points = tuple(points)
            self.changed.emit()
        self.index = index
        self._drag = True
        self.selected.emit(index)
        self.update()

    def mouseMoveEvent(self, event):
        if self._drag:
            self.move_point(*self.position_value(event.position()))

    def mouseReleaseEvent(self, event):
        self._drag = False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.remove_point()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c, rect = colors(), self.plot_rect()
        p.fillRect(rect, c.plot)
        for step in range(5):
            fraction = step / 4
            x, y = rect.left() + rect.width() * fraction, rect.bottom() - rect.height() * fraction
            p.setPen(QPen(c.plot_grid, 1))
            p.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            p.setPen(c.text)
            xv = self.x_range[0] + fraction * (self.x_range[1] - self.x_range[0])
            yv = self.y_range[0] + fraction * (self.y_range[1] - self.y_range[0])
            p.drawText(QRectF(x - 25, rect.bottom() + 3, 50, 19), Qt.AlignmentFlag.AlignCenter, f"{xv:g}")
            p.drawText(QRectF(0, y - 10, 50, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{yv:g}")
        p.setPen(QPen(c.accent, 2))
        p.drawPolyline(QPolygonF([self.point_position(point) for point in self.points]))
        for index, point in enumerate(self.points):
            p.setBrush(c.accent if index == self.index else c.plot)
            p.drawEllipse(self.point_position(point), 5, 5)
        p.setPen(c.text)
        p.drawText(QRectF(rect.left(), self.height() - 22, rect.width(), 20), Qt.AlignmentFlag.AlignCenter, self.x_label)
        p.drawText(QRectF(4, 0, self.width() - 8, 16), Qt.AlignmentFlag.AlignLeft, self.y_label)


class CurveDialog(EffectDialog):
    def add_curve(self, layout, x_range, y_range, points, x_label, y_label):
        self.curve = CurveEditor(x_range, y_range, points, x_label, y_label)
        layout.addWidget(self.curve, 1)
        row = QHBoxLayout()
        self.position = spin(points[0][0], *x_range)
        self.level = spin(points[0][1], *y_range)
        self.position.setAccessibleName(x_label)
        self.level.setAccessibleName(y_label)
        row.addWidget(QLabel(x_label))
        row.addWidget(self.position)
        row.addWidget(QLabel(y_label))
        row.addWidget(self.level)
        self.remove = QPushButton("Remove Point")
        self.remove.clicked.connect(self.curve.remove_point)
        row.addWidget(self.remove)
        layout.addLayout(row)
        self._syncing = False
        self.curve.selected.connect(self.sync_fields)
        self.position.valueChanged.connect(self.update_point)
        self.level.valueChanged.connect(self.update_point)
        self.sync_fields(0)

    def sync_fields(self, index):
        self._syncing = True
        x, y = self.curve.points[index]
        interior = 0 < index < len(self.curve.points) - 1
        self.position.setEnabled(interior)
        self.remove.setEnabled(interior)
        self.position.setValue(x)
        self.level.setValue(y)
        self._syncing = False

    def update_point(self, *_):
        if not self._syncing:
            self.curve.move_point(self.position.value(), self.level.value())


class EnvelopeDialog(CurveDialog):
    effect_name = "envelope"
    PRESETS = (
        ("Default", ((0, 100), (100, 100))),
        ("Fade In", ((0, 0), (100, 100))),
        ("Fade Out", ((0, 100), (100, 0))),
        ("Fade In / Out", ((0, 0), (20, 100), (80, 100), (100, 0))),
        ("Dip in the Middle", ((0, 100), (40, 100), (50, 25), (60, 100), (100, 100))),
    )

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle("Envelope")
        self.resize(620, 490)
        layout = QVBoxLayout(self)
        self.presets = QComboBox()
        self.presets.addItems(["Custom", *(p[0] for p in self.PRESETS)])
        self.presets.setCurrentIndex(1)
        layout.addWidget(self.presets)
        self.add_curve(layout, (0, 100), (0, 200), self.PRESETS[0][1], "Position (%)", "Amplification (%)")
        self.logarithmic = QCheckBox("Logarithmic interpolation (positive levels only)")
        layout.addWidget(self.logarithmic)
        self.curve.changed.connect(lambda: self.presets.setCurrentIndex(0))
        self.presets.currentIndexChanged.connect(self.preset)
        self.add_footer(layout)

    def preset(self, index):
        if index > 0:
            self.curve.set_points(self.PRESETS[index - 1][1])
            self.presets.blockSignals(True)
            self.presets.setCurrentIndex(index)
            self.presets.blockSignals(False)
            self.logarithmic.setChecked(False)

    def settings(self):
        return dict(points=tuple((x / 100, y / 100) for x, y in self.curve.points),
                    logarithmic=self.logarithmic.isChecked())

    def accept(self):
        if self.logarithmic.isChecked() and any(y <= 0 for _, y in self.curve.points):
            QMessageBox.information(self, "Envelope", "Use positive levels for logarithmic interpolation, or turn it off for a fade to silence.")
            return
        super().accept()


class DynamicsDialog(CurveDialog):
    effect_name = "dynamics"
    PRESETS = (
        ("Default", ((-60, -60), (0, 0)), 10, 100),
        ("Compressor (3:1 above −18 dB)", ((-60, -60), (-18, -18), (0, -12)), 10, 100),
        ("Peak Limiter (−6 dB)", ((-60, -60), (-6, -6), (0, -6)), 0, 50),
        ("Soft Gate", ((-60, -96), (-45, -81), (-40, -40), (0, 0)), 1, 100),
        ("Downward Expander", ((-60, -96), (-30, -30), (0, 0)), 5, 100),
    )

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle("Dynamics Processing")
        self.resize(650, 570)
        layout = QVBoxLayout(self)
        self.presets = QComboBox()
        self.presets.addItems(["Custom", *(p[0] for p in self.PRESETS)])
        self.presets.setCurrentIndex(1)
        layout.addWidget(self.presets)
        self.add_curve(layout, (-96, 0), (-96, 24), ((-96, -96), (0, 0)), "Input (dB)", "Output (dB)")
        form = QFormLayout()
        self.attack = spin(10, 0, 1000, " ms")
        self.release = spin(100, 0, 5000, " ms")
        self.makeup = spin(0, -24, 24, " dB")
        form.addRow("Attack", self.attack)
        form.addRow("Release", self.release)
        form.addRow("Output gain", self.makeup)
        layout.addLayout(form)
        self.linked = QCheckBox("Link stereo channels (preserve stereo balance)")
        self.linked.setChecked(True)
        self.linked.setVisible(document.channels == 2)
        layout.addWidget(self.linked)
        note = QLabel("Peak detection with attack/release. No look-ahead; a slower attack lets transients through.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self._setting_preset = False
        self.curve.changed.connect(self.custom)
        for field in (self.attack, self.release, self.makeup):
            field.valueChanged.connect(self.custom)
        self.presets.currentIndexChanged.connect(self.preset)
        self.add_footer(layout)

    def custom(self, *_):
        if not self._setting_preset:
            self.presets.setCurrentIndex(0)

    def preset(self, index):
        if index <= 0:
            return
        self._setting_preset = True
        _, points, attack, release = self.PRESETS[index - 1]
        self.curve.set_points(((-96, -96), *points))
        self.attack.setValue(attack)
        self.release.setValue(release)
        self.makeup.setValue(0)
        self._setting_preset = False

    def settings(self):
        return dict(points=self.curve.points, attack_ms=self.attack.value(), release_ms=self.release.value(),
                    makeup_db=self.makeup.value(), linked=self.linked.isChecked())


class NormalizeDialog(EffectDialog):
    effect_name = "normalize"

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle("Normalize")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.target = spin(98, 0, 100, " %", 2)
        form.addRow("Normalize peak to", self.target)
        layout.addLayout(form)
        self.linked = QCheckBox("Normalize left / right equally")
        self.linked.setChecked(True)
        self.linked.setVisible(document.channels == 2)
        self.remove_dc = QCheckBox("Remove DC offset before normalizing")
        layout.addWidget(self.linked)
        layout.addWidget(self.remove_dc)
        self.add_footer(layout)

    def settings(self):
        return dict(target=self.target.value() / 100, linked=self.linked.isChecked(), remove_dc=self.remove_dc.isChecked())
