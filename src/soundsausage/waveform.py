import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from .theme import colors, blend, readable


def clock_text(seconds):
    seconds = max(0.0, seconds)
    minutes, rest = divmod(seconds, 60)
    if minutes >= 60:
        hours, minutes = divmod(int(minutes), 60)
        return f"{hours}:{minutes:02d}:{rest:06.3f}"
    return f"{int(minutes)}:{rest:06.3f}"


class Waveform(QWidget):
    selection_changed = Signal(object, object)
    view_changed = Signal(object, object)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.view_start = 0
        self.view_end = max(1, document.frames)
        self.playhead = None
        self._anchor = None
        self._cache = None
        self.setMinimumSize(500, 230)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setToolTip("Drag to select audio. Double-click selects the visible audio. Ctrl+wheel zooms; wheel scrolls.")

    def set_document(self, document, fit=True):
        self.document = document
        self.playhead = None
        self._cache = None
        if fit:
            self.fit()
        else:
            self.set_view(self.view_start, self.view_end)
        self.update()

    def plot_rect(self):
        return QRectF(9, 7, max(1, self.width() - 70), max(1, self.height() - 36))

    def set_view(self, start, end):
        total = max(1, self.document.frames)
        length = min(total, max(1, int(end) - int(start)))
        self.view_start = max(0, min(int(start), total - length))
        self.view_end = self.view_start + length
        self._cache = None
        self.view_changed.emit(self.view_start, self.view_end)
        self.update()

    def fit(self):
        self.set_view(0, max(1, self.document.frames))

    def zoom(self, factor, anchor=None):
        if self.document.frames == 0:
            return
        old_length = self.view_end - self.view_start
        length = max(8, round(old_length / factor))
        anchor = self.document.cursor if anchor is None else anchor
        anchor = min(self.view_end, max(self.view_start, anchor))
        fraction = (anchor - self.view_start) / old_length
        start = round(anchor - fraction * length)
        self.set_view(start, start + length)

    def zoom_selection(self):
        if self.document.selected:
            self.set_view(*self.document.selection)

    def frame_at(self, x):
        rect = self.plot_rect()
        fraction = min(1.0, max(0.0, (x - rect.left()) / rect.width()))
        return min(self.document.frames, round(self.view_start + fraction * (self.view_end - self.view_start)))

    def x_at(self, frame):
        rect = self.plot_rect()
        return rect.left() + (frame - self.view_start) / (self.view_end - self.view_start) * rect.width()

    def _peaks(self, columns):
        start = min(self.view_start, self.document.frames)
        end = min(self.view_end, self.document.frames)
        key = (self.document.revision, start, end, columns)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        data = self.document.read(start, end)
        if len(data) >= columns and len(data):
            edges = np.linspace(0, len(data), columns + 1, dtype=np.int64)
            result = (np.minimum.reduceat(data, edges[:-1], axis=0),
                      np.maximum.reduceat(data, edges[:-1], axis=0), True)
        else:
            result = (data, data, False)
        self._cache = (key, result)
        return result

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        painter.fillRect(self.rect(), c.window)
        rect = self.plot_rect()
        painter.fillRect(rect, c.plot)
        channels = self.document.channels
        gap = 8
        channel_height = (rect.height() - gap * (channels - 1)) / channels
        visible_seconds = (self.view_end - self.view_start) / self.document.sample_rate
        raw_step = visible_seconds / max(2, rect.width() / 85)
        power = 10 ** math.floor(math.log10(max(raw_step, 1e-9)))
        step = next((n * power for n in (1, 2, 5, 10) if n * power >= raw_step), 10 * power)
        first = math.ceil((self.view_start / self.document.sample_rate) / step) * step
        ticks = []
        time = first
        while time <= self.view_end / self.document.sample_rate + step * 1e-6 and len(ticks) < 100:
            ticks.append((time, self.x_at(time * self.document.sample_rate)))
            time += step
        if not self.document.frames:
            ticks = [(0, rect.left())]
        a, b = self.document.selection
        if b > a:
            left, right = max(rect.left(), self.x_at(a)), min(rect.right(), self.x_at(b))
            if right > left:
                painter.fillRect(QRectF(left, rect.top(), right - left, rect.height()), blend(c.plot, c.accent, 0.26))
        for channel in range(channels):
            top = rect.top() + channel * (channel_height + gap)
            center = top + channel_height / 2
            for fraction in (-1, -0.5, 0, 0.5, 1):
                y = center - fraction * channel_height * 0.45
                painter.setPen(QPen(QColor("#617675" if fraction == 0 else "#243b3c"), 1))
                painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            painter.setPen(QPen(QColor("#263f40"), 1))
            for _, x in ticks:
                painter.drawLine(QPointF(x, top), QPointF(x, top + channel_height))
            painter.setPen(c.text)
            painter.drawText(QRectF(rect.right() + 5, top, 49, 17), Qt.AlignmentFlag.AlignLeft, "32768")
            painter.drawText(QRectF(rect.right() + 5, center - 8, 49, 17), Qt.AlignmentFlag.AlignLeft, "0")
            painter.drawText(QRectF(rect.right() + 5, top + channel_height - 17, 49, 17), Qt.AlignmentFlag.AlignLeft, "−32768")
            painter.setPen(c.plot_text)
            painter.drawText(QRectF(rect.left() + 5, top + 3, 35, 16), Qt.AlignmentFlag.AlignLeft, "L" if channel == 0 else "R")
        if self.document.frames:
            minimum, maximum, envelope = self._peaks(max(1, int(rect.width())))
            painter.save()
            painter.setClipRect(rect)
            painter.setPen(QPen(c.waveform, 1))
            for channel in range(channels):
                top = rect.top() + channel * (channel_height + gap)
                center = top + channel_height / 2
                scale = channel_height * 0.45
                if envelope:
                    for i in range(len(minimum)):
                        x = rect.left() + i * rect.width() / len(minimum)
                        painter.drawLine(QPointF(x, center - min(1.08, max(-1.08, float(maximum[i, channel]))) * scale),
                                         QPointF(x, center - min(1.08, max(-1.08, float(minimum[i, channel]))) * scale))
                else:
                    points = QPolygonF([QPointF(self.x_at(self.view_start + i), center - min(1.08, max(-1.08, float(row[channel]))) * scale)
                                        for i, row in enumerate(minimum)])
                    painter.drawPolyline(points)
                    if len(points) == 1:
                        painter.drawEllipse(points[0], 2, 2)
            painter.restore()
        else:
            painter.setPen(c.plot_text)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Open a WAV file or generate a tone")
        painter.setPen(c.text)
        for time, x in ticks:
            label = f"{time:.3f}" if step < 0.1 else f"{time:.1f}"
            left = max(rect.left(), min(x - 32, rect.right() - 64))
            painter.drawText(QRectF(left, rect.bottom() + 4, 64, 21), Qt.AlignmentFlag.AlignHCenter, label)
        painter.drawText(QRectF(rect.right() + 4, rect.bottom() + 4, 50, 21), Qt.AlignmentFlag.AlignLeft, "sec")
        cursor = self.document.cursor if self.playhead is None else self.playhead
        if self.view_start <= cursor <= self.view_end:
            painter.setPen(QPen(c.plot_text if self.playhead is None else readable(c.accent, c.plot, 3.0), 1))
            painter.drawLine(QPointF(self.x_at(cursor), rect.top()), QPointF(self.x_at(cursor), rect.bottom()))
        painter.setPen(QPen(QColor("#b5c9ca"), 1))
        painter.drawRect(rect)

    def _select(self, start, end):
        self.document.select(start, end)
        self.selection_changed.emit(*self.document.selection)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            frame = self.frame_at(event.position().x())
            self._anchor = self.document.selection[0] if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else frame
            self._select(self._anchor, frame)
            self.setFocus()

    def mouseMoveEvent(self, event):
        if self._anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._select(self._anchor, self.frame_at(event.position().x()))

    def mouseReleaseEvent(self, event):
        self._anchor = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._select(self.view_start, min(self.document.frames, self.view_end))

    def wheelEvent(self, event):
        amount = event.angleDelta().y()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom(1.5 if amount > 0 else 1 / 1.5, self.frame_at(event.position().x()))
        else:
            length = self.view_end - self.view_start
            shift = round(length * (-0.15 if amount > 0 else 0.15))
            self.set_view(self.view_start + shift, self.view_end + shift)
        event.accept()
