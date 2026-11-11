"""EQ and filter controls with the response of the actual processing cascade."""
import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QPolygonF
from .i18n_widgets import QPainter
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from .i18n_widgets import QSlider
from .i18n_widgets import QWidget, QFormLayout, QLabel, QComboBox, QCheckBox, QPushButton

from .amplitude_ui import EffectDialog, spin
from .filters import GRAPHIC_CENTRES, design, response, frequency_limit
from .theme import colors


class ResponsePlot(QWidget):
    def __init__(self, dialog):
        super().__init__(dialog)
        self.dialog = dialog
        self.setMinimumSize(420, 180)
        self.setAccessibleName("Frequency response: Hz horizontally, gain in dB vertically")
        self.setToolTip("Combined response, including output gain. Display range: −36 to +36 dB.")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = colors()
        rect = QRectF(42, 8, self.width()-58, self.height()-38)
        rate = self.dialog.document.sample_rate
        lo, hi = 10, rate/2
        x = lambda f: rect.left() + math.log(f/lo)/math.log(hi/lo)*rect.width()
        y = lambda db: rect.center().y() - np.clip(db, -36, 36)/72*rect.height()
        p.fillRect(rect, c.plot)
        for db in (-36, -24, -12, 0, 12, 24, 36):
            p.setPen(QPen(c.plot_grid, 1))
            p.drawLine(QPointF(rect.left(), y(db)), QPointF(rect.right(), y(db)))
            p.setPen(c.text)
            p.drawText(QRectF(0, y(db)-9, 36, 18), Qt.AlignmentFlag.AlignRight, f"{db:+d}")
        for f in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000):
            if f > hi:
                continue
            p.setPen(QPen(c.plot_grid, 1))
            p.drawLine(QPointF(x(f), rect.top()), QPointF(x(f), rect.bottom()))
            p.setPen(c.text)
            if f in (10, 50, 200, 1000, 5000, 20000):
                p.drawText(QRectF(x(f)-22, rect.bottom()+3, 44, 20), Qt.AlignmentFlag.AlignCenter,
                           f"{f/1000:g}k" if f >= 1000 else str(f))
        try:
            coefficients, gain = design(self.dialog.effect_name, rate, **self.dialog.settings())
            frequencies = np.geomspace(lo, hi*.999999, max(200, self.width()))
            levels = response(coefficients, gain, frequencies, rate)
            p.setClipRect(rect)
            p.setPen(QPen(c.waveform, 2))
            p.drawPolyline(QPolygonF([QPointF(x(f), y(db)) for f, db in zip(frequencies, levels)]))
        except ValueError:
            pass  # A partially constructed dialog has no valid curve yet.


class FrequencyDialog(EffectDialog):
    def header(self, title, presets):
        self.setWindowTitle(title)
        self._setting = False
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.presets = QComboBox()
        self.presets.addItems(["Custom", *presets])
        row.addWidget(QLabel("Preset"))
        row.addWidget(self.presets, 1)
        reset = QPushButton("Reset")
        reset.clicked.connect(lambda: self.preset(1))
        row.addWidget(reset)
        layout.addLayout(row)
        self.plot = ResponsePlot(self)
        layout.addWidget(self.plot, 1)
        self.output = spin(0, -24, 24, " dB")
        return layout

    def footer(self, layout):
        row = QFormLayout()
        row.addRow("Output gain", self.output)
        layout.addLayout(row)
        note = QLabel("Boosting bands can raise peaks above 0 dBFS. Lower Output gain to leave headroom.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.add_footer(layout)
        self.output.valueChanged.connect(self.changed)
        self.presets.currentIndexChanged.connect(self.preset)
        self.preset(1)

    def changed(self, *_):
        if not self._setting:
            self.presets.setCurrentIndex(0)
        self.plot.update()


class GraphicEqualizerDialog(FrequencyDialog):
    effect_name = "graphic_eq"
    PRESETS = (
        ("Flat", (0,)*10),
        ("Bass lift", (5, 5, 4, 2, 0, 0, 0, 0, 0, 0)),
        ("Voice presence", (-6, -5, -3, -1, 0, 1, 3, 2, 0, 0)),
        ("Gentle smile", (3, 3, 2, 0, -2, -2, 0, 2, 3, 3)),
    )

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.resize(790, 590)
        layout = self.header("Graphic Equalizer", [p[0] for p in self.PRESETS])
        grid = QGridLayout()
        self.gains, self.sliders = [], []
        for i, frequency in enumerate(GRAPHIC_CENTRES):
            label = f"{frequency/1000:g}k" if frequency >= 1000 else f"{frequency:g}"
            title = QLabel(label)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(title, 0, i)
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-240, 240)
            slider.setTickInterval(60)
            slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            slider.setMinimumHeight(130)
            slider.setAccessibleName(f"{frequency:g} Hz band gain")
            field = spin(0, -24, 24, "", 1)
            field.setAccessibleName(f"{frequency:g} Hz gain (dB)")
            field.setMinimumWidth(62)
            slider.valueChanged.connect(lambda value, f=field: f.setValue(value/10))
            field.valueChanged.connect(lambda value, s=slider: s.setValue(round(value*10)))
            field.valueChanged.connect(self.changed)
            usable = frequency <= frequency_limit(document.sample_rate)
            slider.setEnabled(usable)
            field.setEnabled(usable)
            if not usable:
                title.setToolTip("Above the usable frequency range at this sample rate; band is omitted.")
                field.setToolTip(title.toolTip())
            grid.addWidget(slider, 1, i, alignment=Qt.AlignmentFlag.AlignHCenter)
            grid.addWidget(field, 2, i)
            self.gains.append(field)
            self.sliders.append(slider)
        layout.addLayout(grid)
        label = QLabel("10 octave bands · gain in dB · bands above the sample rate limit are disabled")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.footer(layout)

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        for field, gain in zip(self.gains, self.PRESETS[index-1][1]):
            field.setValue(gain if field.isEnabled() else 0)
        self.output.setValue(0)
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.plot.update()

    def settings(self):
        return dict(gains=tuple(field.value() if field.isEnabled() else 0 for field in self.gains),
                    output_db=self.output.value())


class ParametricEqualizerDialog(FrequencyDialog):
    effect_name = "parametric_eq"
    FREQUENCIES = (100, 160, 400, 1000, 2500, 6300, 10000)
    KINDS = ("low_shelf", "bell", "bell", "bell", "bell", "bell", "high_shelf")

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.resize(720, 635)
        layout = self.header("Parametric Equalizer", ("Flat", "Voice clarity", "Warmth"))
        grid = QGridLayout()
        for column, text in enumerate(("Band", "Frequency", "Gain", "Q (higher = narrower)")):
            grid.addWidget(QLabel(text), 0, column)
        self.bands = []
        for i, (frequency, kind) in enumerate(zip(self.FREQUENCIES, self.KINDS)):
            enabled = QCheckBox("Low shelf" if i == 0 else "High shelf" if i == 6 else f"Bell {i}")
            freq = spin(min(frequency, frequency_limit(document.sample_rate)), 1,
                        math.floor(frequency_limit(document.sample_rate)), " Hz", 1)
            gain = spin(0, -24, 24, " dB")
            q = spin(1, .1, 50, "", 2)
            q.setToolTip("Bell bandwidth. Shelves use a fixed monotonic slope.")
            for column, control in enumerate((enabled, freq, gain, q)):
                grid.addWidget(control, i+1, column)
                control.setAccessibleName(f"Parametric band {i+1}: {('enabled', 'frequency', 'gain', 'Q')[column]}")
            def toggle(value, f=freq, g=gain, qfield=q, k=kind):
                f.setEnabled(value); g.setEnabled(value); qfield.setEnabled(value and k == "bell")
                self.changed()
            enabled.toggled.connect(toggle)
            for field in (freq, gain, q):
                field.valueChanged.connect(self.changed)
            self.bands.append((enabled, freq, gain, q))
        layout.addLayout(grid)
        self.footer(layout)

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        gains = (0,)*7 if index == 1 else (-3, -2, -2, 0, 3, 1, 0) if index == 2 else (3, 2, 0, 0, -1, 0, -2)
        for row, frequency, gain in zip(self.bands, self.FREQUENCIES, gains):
            enabled, freq, level, q = row
            freq.setValue(min(frequency, freq.maximum()))
            level.setValue(gain)
            q.setValue(1)
            enabled.setChecked(frequency <= frequency_limit(self.document.sample_rate))
            freq.setEnabled(enabled.isChecked()); level.setEnabled(enabled.isChecked())
            q.setEnabled(enabled.isChecked() and row is not self.bands[0] and row is not self.bands[-1])
        self.output.setValue(0)
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.plot.update()

    def settings(self):
        return dict(bands=tuple(dict(enabled=e.isChecked(), kind=kind, frequency=f.value(),
                                    gain_db=g.value(), q=q.value())
                                for kind, (e, f, g, q) in zip(self.KINDS, self.bands)),
                    output_db=self.output.value())


class FilterDialog(FrequencyDialog):
    effect_name = "filter"
    KINDS = ("high_pass", "low_pass", "band_pass", "notch")

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.resize(610, 490)
        layout = self.header("Filters", ("Remove low rumble", "Soften high frequencies", "Telephone band", "50 Hz notch", "60 Hz notch"))
        form = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItems(("High-pass", "Low-pass", "Band-pass", "Notch"))
        self.frequency = spin(80, 1, math.floor(frequency_limit(document.sample_rate)), " Hz", 1)
        self.slope = QComboBox()
        self.slope.addItems(("12 dB/oct", "24 dB/oct", "36 dB/oct", "48 dB/oct"))
        self.q = spin(1, .1, 50, "", 2)
        form.addRow("Type", self.kind)
        form.addRow("Cutoff / centre frequency", self.frequency)
        form.addRow("Butterworth slope (low/high-pass)", self.slope)
        form.addRow("Q (band-pass / notch)", self.q)
        layout.addLayout(form)
        for field in (self.frequency, self.q):
            field.valueChanged.connect(self.changed)
        self.slope.currentIndexChanged.connect(self.changed)
        self.kind.currentIndexChanged.connect(self.type_changed)
        self.footer(layout)

    def type_changed(self, *_):
        band = self.kind.currentIndex() >= 2
        self.q.setEnabled(band)
        self.slope.setEnabled(not band)
        self.changed()

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        kind, frequency, q = ((0, 80, 1), (1, 8000, 1), (2, 1200, .7), (3, 50, 25), (3, 60, 25))[index-1]
        self.kind.setCurrentIndex(kind)
        self.frequency.setValue(min(frequency, self.frequency.maximum()))
        self.q.setValue(q)
        self.slope.setCurrentIndex(1)
        self.output.setValue(0)
        self.type_changed()
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.plot.update()

    def settings(self):
        return dict(kind=self.KINDS[self.kind.currentIndex()], frequency=self.frequency.value(),
                    slope=(12, 24, 36, 48)[self.slope.currentIndex()], q=self.q.value(), output_db=self.output.value())
