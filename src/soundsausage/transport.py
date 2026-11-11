"""Compact transport strip, selection/view times and stereo dBFS meter."""
import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QFont, QPen
from .i18n_widgets import QPainter
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from .i18n_widgets import QWidget, QToolButton, QLabel, QLineEdit

from .theme import colors
from .waveform import clock_text


class LevelMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LevelMeter")
        self.setFixedHeight(34)
        self.peaks = (0.0, 0.0)
        self.setToolTip("Peak levels in dBFS. Red at the right edge indicates clipping.")
        self.setAccessibleName("Stereo peak level meter")

    def set_samples(self, samples):
        peaks = [0.0, 0.0]
        if samples is not None and len(samples):
            for channel in range(min(2, samples.shape[1])):
                peak = float(np.max(np.abs(samples[:, channel])))
                peaks[channel] = peak if math.isfinite(peak) else 0.0
        self.peaks = tuple(peaks)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        painter.fillRect(self.rect(), c.plot)
        font = QFont(self.font())
        font.setPointSizeF(max(7, font.pointSizeF() - 1))
        painter.setFont(font)
        left, right = 16, self.width() - 27
        width = max(1, right - left)
        for channel, peak in enumerate(self.peaks):
            y = 3 + channel * 9
            painter.setPen(c.plot_text)
            painter.drawText(QRectF(2, y - 2, 12, 12), Qt.AlignmentFlag.AlignLeft, "L" if channel == 0 else "R")
            db = max(-60.0, min(0.0, 20 * math.log10(peak))) if peak > 0 else -60.0
            fraction = (db + 60) / 60
            for x in range(left, right, 5):
                position = (x - left) / width
                color = QColor("#e64b4b" if position >= .95 else "#e9c64f" if position >= .8 else "#36ca75")
                if position >= fraction:
                    color.setAlpha(28)
                painter.fillRect(QRectF(x, y, min(4, right - x), 6), color)
            painter.fillRect(QRectF(right + 4, y, 17, 6), QColor("#e64b4b") if peak >= 1 else QColor("#321f24"))
        painter.setPen(c.plot_text)
        for db in range(-60, 1, 3):
            x = left + (db + 60) / 60 * width
            painter.drawLine(QPointF(x, 20), QPointF(x, 23))
            if self.width() >= 950 or db % 6 == 0:
                label = str(db)
                painter.drawText(QRectF(x - 14, 22, 28, 12), Qt.AlignmentFlag.AlignCenter, label)
        painter.drawText(QRectF(right + 2, 22, 24, 12), Qt.AlignmentFlag.AlignCenter, "dB")


class TransportPanel(QWidget):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setObjectName("TransportPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 3, 4, 0)
        outer.setSpacing(3)
        row = QHBoxLayout()
        row.setSpacing(10)
        controls = QGridLayout()
        controls.setSpacing(2)

        def button(key):
            result = QToolButton()
            result.setDefaultAction(actions[key])
            result.setObjectName("transport_" + key)
            result.setProperty("compact", True)
            result.setProperty("primary", key == "play")
            result.setFixedSize(27, 25)
            result.setIconSize(QSize(16, 16))
            return result

        for index, key in enumerate(("stop", "play", "pause", "loop", "record")):
            controls.addWidget(button(key), 0, index)
        for index, key in enumerate(("to_start", "seek_back", "seek_forward", "to_end")):
            controls.addWidget(button(key), 1, index)
        row.addLayout(controls)
        zoom = QGridLayout()
        zoom.setSpacing(2)
        for index, key in enumerate(("zoom_in", "zoom_out", "zoom_full", "zoom_selection")):
            zoom.addWidget(button(key), index // 2, index % 2)
        row.addLayout(zoom)
        self.time_label = QLabel("0:00.000")
        self.time_label.setObjectName("TimeDisplay")
        self.time_label.setAccessibleName("Playhead time")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("DejaVu Sans Mono", 27))
        self.time_label.setMinimumWidth(230)
        row.addWidget(self.time_label, 1)
        table = QGridLayout()
        table.setSpacing(2)
        self.fields, self.view_fields = {}, {}
        for column, title in enumerate(("Begin", "End", "Length"), 1):
            label = QLabel(title)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            table.addWidget(label, 0, column)
        for number, (label, fields) in enumerate((("Sel", self.fields), ("View", self.view_fields)), 1):
            table.addWidget(QLabel(label), number, 0)
            for column, title in enumerate(("Begin", "End", "Length"), 1):
                field = QLineEdit("0:00.000")
                field.setReadOnly(True)
                field.setAccessibleName(f"Selection {title}" if label=="Sel" else f"View {title}")
                field.setProperty("compact", True)
                field.setAlignment(Qt.AlignmentFlag.AlignRight)
                field.setFixedWidth(92)
                field.setFixedHeight(20)
                fields[title] = field
                table.addWidget(field, number, column)
        table.addWidget(button("select_range"), 1, 4, 2, 1)
        row.addLayout(table)
        outer.addLayout(row)
        self.meter = LevelMeter(self)
        outer.addWidget(self.meter)

    def set_view_range(self, begin, end, rate):
        for key, frame in (("Begin", begin), ("End", end), ("Length", end - begin)):
            self.view_fields[key].setText(clock_text(frame / rate))
