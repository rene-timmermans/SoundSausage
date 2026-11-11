"""Compact transport strip, selection/view times and stereo dBFS meter."""
import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, QSize, QEvent
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPen
from .i18n_widgets import QPainter
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from .i18n_widgets import QWidget, QToolButton, QLabel, QLineEdit

from .theme import colors
from .waveform import clock_text
from .plot_layout import text_width, separated_labels


class LevelMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LevelMeter")
        self.setFixedHeight(self.meter_height())
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

    def meter_font(self):
        font = QFont(self.font())
        if font.pointSizeF() > 0:
            font.setPointSizeF(max(7, font.pointSizeF() - 1))
        else:
            font.setPixelSize(max(10, font.pixelSize() - 1))
        return font

    def channel_height(self):
        metrics = QFontMetrics(self.meter_font(), self)
        return max(metrics.tightBoundingRect(letter).height() for letter in ("L", "R")) + 2

    def meter_height(self):
        return 2 * self.channel_height() + QFontMetrics(self.meter_font(), self).height() + 3

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self.setFixedHeight(self.meter_height())

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        painter.fillRect(self.rect(), c.plot)
        painter.setFont(self.meter_font())
        metrics = painter.fontMetrics()
        line = metrics.height()
        channel_height = self.channel_height()
        left = max(16, text_width(metrics, "R") + 4)
        clip_width = max(17, text_width(metrics, "dB"))
        zero_half = text_width(metrics, "0") / 2
        right = math.floor(self.width() - clip_width - zero_half - 8)
        clip_left = right + zero_half + 4
        width = max(1, right - left)
        for channel, peak in enumerate(self.peaks):
            area = QRectF(1, 1 + channel * channel_height, left - 4, channel_height)
            y = area.center().y() - 3
            painter.setPen(c.plot_text)
            letter = "L" if channel == 0 else "R"
            ink = metrics.tightBoundingRect(letter)
            baseline = QPointF(area.center().x() - ink.width() / 2 - ink.left(),
                               area.center().y() - ink.height() / 2 - ink.top())
            painter.drawText(baseline, letter)
            db = max(-60.0, min(0.0, 20 * math.log10(peak))) if peak > 0 else -60.0
            fraction = (db + 60) / 60
            for x in range(left, right, 5):
                position = (x - left) / width
                color = QColor("#e64b4b" if position >= .95 else "#e9c64f" if position >= .8 else "#36ca75")
                if position >= fraction:
                    color.setAlpha(28)
                painter.fillRect(QRectF(x, y, min(4, right - x), 6), color)
            painter.fillRect(QRectF(clip_left, y, clip_width, 6), QColor("#e64b4b") if peak >= 1 else QColor("#321f24"))
        painter.setPen(c.plot_text)
        scale_top = 2 * channel_height + 2
        candidates = []
        for db in range(-60, 1, 3):
            x = left + (db + 60) / 60 * width
            painter.drawLine(QPointF(x, scale_top - 3), QPointF(x, scale_top - 1))
            label = str(db)
            label_width = text_width(metrics, label)
            candidates.append((QRectF(x - label_width / 2, scale_top, label_width, line), label))
        for area, label in separated_labels(candidates):
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, label)
        painter.drawText(QRectF(clip_left, scale_top, clip_width, line), Qt.AlignmentFlag.AlignCenter, "dB")


class TimeField(QLineEdit):
    """Compact time readout that still fits the desktop font and hour values."""
    def update_size(self):
        if getattr(self, "_sizing", False):
            return
        self._sizing = True
        try:
            self.setFixedSize(max(92, self.fontMetrics().horizontalAdvance("00:00:00.000") + 10),
                              max(20, self.fontMetrics().height() + 4))
        finally:
            self._sizing = False

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self.update_size()


class ClockLabel(QLabel):
    """Keep the clock legible even with a wider fallback font or hour values."""
    def update_size(self):
        needed = max(230, self.fontMetrics().horizontalAdvance(self.text()) + 8)
        if needed != self.minimumWidth():
            self.setMinimumWidth(needed)
            window = self.window()
            if hasattr(window, "update_minimum_size"):
                window.update_minimum_size()

    def setText(self, text):
        super().setText(text)
        self.update_size()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self.update_size()


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
        self.time_label = ClockLabel("0:00.000")
        self.time_label.setObjectName("TimeDisplay")
        self.time_label.setAccessibleName("Playhead time")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("DejaVu Sans Mono", 27))
        self.time_label.update_size()
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
                field = TimeField("0:00.000")
                field.setReadOnly(True)
                field.setAccessibleName(f"Selection {title}" if label=="Sel" else f"View {title}")
                field.setProperty("compact", True)
                field.setAlignment(Qt.AlignmentFlag.AlignRight)
                field.ensurePolished()
                field.update_size()
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
