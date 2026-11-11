import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPen, QPolygonF
from .i18n_widgets import QPainter
from .i18n_widgets import QWidget

from .theme import colors, blend, readable
from .peaks import piece_peaks
from .plot_layout import text_width, separated_labels


def envelope_polygon(minimum, maximum, channel, left, width, center, scale, clamp=1.08):
    """Join neighbouring min/max columns, including offset and very thin signals."""
    count = len(minimum)
    if not count:
        return QPolygonF()
    def points(values):
        result = [QPointF(left+i*width/count, center-min(clamp, max(-clamp, float(row[channel])))*scale)
                  for i, row in enumerate(values)]
        # The last bin covers the right edge too, rather than leaving one blank pixel.
        result.append(QPointF(left+width, result[-1].y()))
        return result
    return QPolygonF(points(maximum) + list(reversed(points(minimum))))


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
        self._anchor_channel = None
        self._keep_channels = False
        self._cache = None
        self.setMinimumSize(500, 230)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.IBeamCursor if document.frames else Qt.CursorShape.ArrowCursor)
        self.setToolTip("Drag inside L or R to select that channel; drag across both for stereo. Double-click selects visible audio. Ctrl+wheel zooms; wheel scrolls.")

    def set_document(self, document, fit=True):
        self.document = document
        self.setCursor(Qt.CursorShape.IBeamCursor if document.frames else Qt.CursorShape.ArrowCursor)
        self.playhead = None
        self._cache = None
        if fit:
            self.fit()
        else:
            self.set_view(self.view_start, self.view_end)
        self.update()

    def plot_rect(self):
        metrics = self.fontMetrics()
        right = max(61, text_width(metrics, "−32768") + 6)
        bottom = max(29, metrics.height() + 8)
        return QRectF(9, 7, max(1, self.width() - 9 - right), max(1, self.height() - 7 - bottom))

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

    def channel_at(self, y):
        if self.document.channels == 1: return 0
        rect = self.plot_rect(); middle = rect.center().y()
        return None if abs(y-middle) <= 4 else 0 if y < middle else 1

    def channel_rect(self, channel):
        rect = self.plot_rect(); height = (rect.height()-8*(self.document.channels-1))/self.document.channels
        return QRectF(rect.left(), rect.top()+channel*(height+8), rect.width(), height)

    def _peaks(self, columns):
        start = min(self.view_start, self.document.frames)
        end = min(self.view_end, self.document.frames)
        key = (self.document.revision, start, end, columns)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        pieces = self.document._slices(start, end)
        if end-start <= columns*4:
            data = np.concatenate(pieces) if pieces else np.empty((0, self.document.channels), np.float32)
            result = (data, data, False)
        else:
            result = piece_peaks(pieces, end-start, self.document.channels, columns)
        self._cache = (key, result)
        return result

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        if not self.document.frames:
            painter.fillRect(self.rect(), c.workspace)
            return
        painter.fillRect(self.rect(), c.window)
        rect = self.plot_rect()
        painter.fillRect(rect, c.plot)
        channels = self.document.channels
        line = self.fontMetrics().height() + 2
        amplitude_width = self.width() - rect.right() - 7
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
                for channel in self.document.selected_channels:
                    lane = self.channel_rect(channel)
                    painter.fillRect(QRectF(left, lane.top(), right-left, lane.height()), blend(c.plot, c.accent, 0.26))
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
            painter.drawText(QRectF(rect.right() + 5, top, amplitude_width, line), Qt.AlignmentFlag.AlignLeft, "32768")
            painter.drawText(QRectF(rect.right() + 5, center - line / 2, amplitude_width, line), Qt.AlignmentFlag.AlignLeft, "0")
            painter.drawText(QRectF(rect.right() + 5, top + channel_height - line, amplitude_width, line), Qt.AlignmentFlag.AlignLeft, "−32768")
            painter.setPen(c.plot_text)
            badge = QRectF(rect.left()+3, top+2, max(21, text_width(self.fontMetrics(), "R")), max(19, line))
            if channel in self.document.selected_channels:
                painter.fillRect(badge, c.accent); painter.setPen(c.accent_text)
            painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, "L" if channel == 0 else "R")
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
                    painter.setBrush(c.waveform)
                    painter.drawPolygon(envelope_polygon(minimum, maximum, channel, rect.left(), rect.width(), center, scale))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                else:
                    points = QPolygonF([QPointF(self.x_at(self.view_start + i), center - min(1.08, max(-1.08, float(row[channel]))) * scale)
                                        for i, row in enumerate(minimum)])
                    painter.drawPolyline(points)
                    if len(points) == 1:
                        painter.drawEllipse(points[0], 2, 2)
            painter.restore()
        else:
            painter.setPen(c.plot_text)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Open an audio file or generate a tone")
        if channels==2:
            separator=QPen(blend(c.plot,c.plot_text,.55),1);separator.setCosmetic(True)
            painter.setPen(separator)
            y=round(rect.center().y())+.5
            painter.drawLine(QPointF(0,y),QPointF(self.width(),y))
        painter.setPen(c.text)
        labels = []
        for time, x in ticks:
            label = f"{time:.3f}" if step < 0.1 else f"{time:.1f}"
            width = text_width(self.fontMetrics(), label)
            left = max(rect.left(), min(x - width / 2, rect.right() - width))
            labels.append((QRectF(left, rect.bottom() + 4, width, line), label))
        for area, text in separated_labels(labels):
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, text)
        painter.drawText(QRectF(rect.right() + 4, rect.bottom() + 4, amplitude_width, line), Qt.AlignmentFlag.AlignLeft, "sec")
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
            self._keep_channels = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self._anchor_channel = self.channel_at(event.position().y())
            if not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.document.select_channels(None if self._anchor_channel is None else (self._anchor_channel,))
            self._anchor = self.document.selection[0] if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else frame
            self._select(self._anchor, frame)
            self.setFocus()

    def mouseMoveEvent(self, event):
        if self._anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            channel = self.channel_at(event.position().y())
            if not self._keep_channels:
                self.document.select_channels((channel,) if channel is not None and channel == self._anchor_channel else None)
            self._select(self._anchor, self.frame_at(event.position().x()))

    def mouseReleaseEvent(self, event):
        self._anchor = None
        self._anchor_channel = None
        self._keep_channels = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            channel = self.channel_at(event.position().y())
            self.document.select_channels(None if channel is None else (channel,))
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
