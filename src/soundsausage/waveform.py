import math
from concurrent.futures import ThreadPoolExecutor
import logging

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF, QTimer, Signal
from PySide6.QtGui import QColor, QPen, QPolygonF, QPixmap
from .i18n_widgets import QPainter
from .i18n_widgets import QWidget

from .theme import colors, blend, readable
from .peaks import piece_peaks
from .plot_layout import text_width, separated_labels
from .i18n import tr, language
from .drawing import DrawingStroke


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


def draw_envelope(painter, minimum, maximum, channel, left, width, center, scale, clamp=1.08):
    """Batch vertical peak spans and connected contours; avoid a huge filled polygon."""
    count=len(minimum)
    if not count:return
    high=center-np.clip(maximum[:,channel],-clamp,clamp)*scale
    low=center-np.clip(minimum[:,channel],-clamp,clamp)*scale
    step=width/count
    xs=left+np.arange(count)*step
    painter.save()
    pen=QPen(painter.pen());pen.setWidthF(max(1.,step));pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(pen)
    painter.drawLines([QLineF(float(x+step/2),float(a),float(x+step/2),float(b)) for x,a,b in zip(xs,high,low)])
    pen.setWidthF(1.);pen.setCapStyle(Qt.PenCapStyle.SquareCap);painter.setPen(pen)
    for values in (high,low):
        points=QPolygonF([QPointF(float(x),float(y)) for x,y in zip(xs,values)])
        points.append(QPointF(left+width,float(values[-1])))
        painter.drawPolyline(points)
    painter.restore()


def _peak_data(pieces, frames, channels, columns, cooperative=False):
    if frames<=columns*4:
        data=np.concatenate(pieces) if pieces else np.empty((0,channels),np.float32)
        return data,data,False
    return piece_peaks(pieces,frames,channels,columns,cooperative=cooperative)


def clock_text(seconds):
    seconds = max(0.0, seconds)
    minutes, rest = divmod(seconds, 60)
    if minutes >= 60:
        hours, minutes = divmod(int(minutes), 60)
        return f"{hours}:{minutes:02d}:{rest:06.3f}"
    return f"{int(minutes)}:{rest:06.3f}"


class Waveform(QWidget):
    _peaks_ready = Signal(object)
    selection_changed = Signal(object, object)
    view_changed = Signal(object, object)
    sample_edit_started = Signal()
    sample_edited = Signal(object, object, float)
    sample_edit_requested = Signal(object, object)
    waveform_drawn = Signal(object, object)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self._scene_cache = None
        self.view_start = 0
        self.view_end = max(1, document.frames)
        self.playhead = None
        self._anchor = None
        self._anchor_channel = None
        self._keep_channels = False
        self._cache = None
        self._peaks_revision = 0
        self._peak_job = None
        self._peak_error = None
        self._peak_executor = None
        self._pending_peaks = None
        self._peak_start_timer = QTimer(self)
        self._peak_start_timer.setSingleShot(True)
        self._peak_start_timer.timeout.connect(self._start_peaks)
        self._peaks_ready.connect(self._accept_peaks)
        self.sample_editable = True
        self._sample_drag = None
        self._sample_hover = None
        self.drawing = False
        self._drawing_stroke = None
        self.setMinimumSize(500, 230)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.IBeamCursor if document.frames else Qt.CursorShape.ArrowCursor)
        self.setToolTip("Drag inside L or R to select that channel; drag across both for stereo. Double-click selects visible audio. Ctrl+wheel zooms; wheel scrolls. Zoom in until sample points appear: drag a point vertically to edit it, or double-click for its exact value. Shift+drag selects audio; Escape cancels a sample drag.")

    def set_document(self, document, fit=True):
        self._scene_cache = None
        self._peak_error = None
        self._sample_drag = None
        self._sample_hover = None
        self._drawing_stroke = None
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
        right = max(61, text_width(metrics, "−32768") + 6, text_width(metrics, tr("samples")) + 6)
        bottom = max(29, metrics.height() + 8)
        return QRectF(9, 7, max(1, self.width() - 9 - right), max(1, self.height() - 7 - bottom))

    def set_view(self, start, end):
        self._sample_drag = None
        self._sample_hover = None
        self._drawing_stroke = None
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

    def sample_spacing(self):
        return self.plot_rect().width() / (self.view_end - self.view_start)

    def sample_points_visible(self):
        return bool(self.document.frames and self.sample_spacing() >= 2)

    def sample_y(self, channel, value):
        lane = self.channel_rect(channel)
        return lane.center().y() - min(1.08, max(-1.08, float(value))) * lane.height() * .45

    def sample_at(self, position):
        if not self.sample_editable or not self.sample_points_visible() or not self.plot_rect().contains(position):
            return None
        channel = self.channel_at(position.y())
        frame = self.frame_at(position.x())
        if channel is None or not self.view_start <= frame < min(self.view_end, self.document.frames):
            return None
        value = float(self.document.view(frame, frame + 1)[0, channel])
        if abs(position.x() - self.x_at(frame)) <= 5 and abs(position.y() - self.sample_y(channel, value)) <= 6:
            return frame, channel, value

    def cancel_sample_drag(self):
        self._sample_drag = None
        self._sample_hover = None
        self._drawing_stroke = None
        self.update()

    def set_drawing(self, enabled):
        self.cancel_sample_drag()
        self.drawing = bool(enabled)
        self.setCursor(Qt.CursorShape.CrossCursor if self.drawing else Qt.CursorShape.IBeamCursor)

    def _draw_at(self, position):
        stroke = self._drawing_stroke
        lane = self.channel_rect(stroke.channel)
        value = (lane.center().y()-position.y())/(lane.height()*.45)
        frame = min(self.view_end-1, max(self.view_start, self.frame_at(position.x())))
        stroke.add(frame, value)
        self.update()

    def leaveEvent(self, event):
        self._sample_hover = None
        self.update()
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and (self._sample_drag is not None or self._drawing_stroke is not None):
            self.cancel_sample_drag()
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.cancel_sample_drag()
        super().focusOutEvent(event)

    def _peak_key(self, columns):
        return (self.document,self.document.revision,min(self.view_start,self.document.frames),
                min(self.view_end,self.document.frames),columns)

    def _accept_peaks(self, payload):
        future,key,result,error=payload
        if self._peak_job is future:self._peak_job=None
        # A stale result must also trigger preparation for the newest viewport.
        self._scene_cache=None
        if key==self._peak_key(max(1,int(self.plot_rect().width()))):
            if error:
                self._peak_error=key
                logging.getLogger(__name__).error('Waveform preview preparation failed: %s',error)
            else:
                self._cache=(key,result);self._peaks_revision+=1;self._scene_cache=None
        self.update()

    def _start_peaks(self):
        token,key,pieces,frames,channels,columns=self._pending_peaks
        self._pending_peaks=None
        if key!=self._peak_key(max(1,int(self.plot_rect().width()))):
            self._peak_job=None;self._scene_cache=None;self.update();return
        if self._peak_executor is None:
            executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='soundsausage-waveform')
            self._peak_executor=executor
            self.destroyed.connect(lambda *_:executor.shutdown(wait=False,cancel_futures=True))
        future=self._peak_executor.submit(_peak_data,pieces,frames,channels,columns,True)
        self._peak_job=future
        def finished(job):
            try:result,error=job.result(),None
            except Exception as failure:result,error=None,str(failure)
            try:self._peaks_ready.emit((job,key,result,error))
            except RuntimeError:pass  # The editor was closed while the job finished.
        future.add_done_callback(finished)

    def _peaks(self, columns):
        key=self._peak_key(columns)
        if self._cache is not None and self._cache[0]==key:return self._cache[1]
        _,_,start,end,_=key
        pieces=self.document._slices(start,end)
        if self.playhead is not None:
            # A resize must never scan source ranges on the audio-feeding GUI thread.
            if self._peak_job is None and self._peak_error!=key:
                self._peak_job=object()
                self._pending_peaks=(self._peak_job,key,pieces,end-start,self.document.channels,columns)
                # Finish the first resized image before the worker starts competing
                # for Python/Qt binding time. A QObject timer also dies with the view.
                self._peak_start_timer.start(0)
            if self._cache is not None and self._cache[0][:4]==key[:4]:return self._cache[1]
            data=np.empty((0,self.document.channels),np.float32)
            return data,data,False
        result=_peak_data(pieces,end-start,self.document.channels,columns)
        self._cache=(key,result);self._peaks_revision+=1
        return result

    def _scene_key(self):
        return (self.document,self.document.revision,self.view_start,self.view_end,
                self.width(),self.height(),self.devicePixelRatioF(),self.font().toString(),language(),
                self.document.selection,self.document.selected_channels,self._peaks_revision,
                self._sample_drag,self._sample_hover,
                tuple(value.rgba() for value in vars(colors()).values()))

    def paintEvent(self,event):
        painter=QPainter(self);c=colors()
        if not self.document.frames:
            painter.fillRect(self.rect(),c.workspace);return
        key=self._scene_key()
        if self._drawing_stroke is not None:key=object()
        if self._scene_cache is None or self._scene_cache[0]!=key:
            ratio=self.devicePixelRatioF()
            image=QPixmap(max(1,round(self.width()*ratio)),max(1,round(self.height()*ratio)))
            image.setDevicePixelRatio(ratio)
            background=QPainter(image)
            self._paint_scene(background)
            background.end()
            self._scene_cache=(self._scene_key() if self._drawing_stroke is None else key,image)
        painter.drawPixmap(0,0,self._scene_cache[1])
        rect=self.plot_rect();cursor=self.document.cursor if self.playhead is None else self.playhead
        if self.view_start<=cursor<=self.view_end:
            painter.setPen(QPen(c.plot_text if self.playhead is None else readable(c.accent,c.plot,3.0),1))
            painter.drawLine(QPointF(self.x_at(cursor),rect.top()),QPointF(self.x_at(cursor),rect.bottom()))
        painter.setPen(QPen(QColor('#b5c9ca'),1));painter.drawRect(rect)

    def _paint_scene(self, painter):
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
        sample_axis = self.sample_points_visible()
        if sample_axis:
            raw = (self.view_end-self.view_start) / max(2, rect.width()/85)
            power = 10 ** math.floor(math.log10(max(1, raw)))
            step = next(n*power for n in (1, 2, 5, 10) if n*power >= raw)
        unit = 1 if sample_axis else self.document.sample_rate
        first = math.ceil((self.view_start / unit) / step) * step
        ticks = []
        time = first
        while time <= self.view_end / unit + step * 1e-6 and len(ticks) < 100:
            ticks.append((time, self.x_at(time * unit)))
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
            if self._sample_drag is not None:
                frame, channel, value = self._sample_drag
                minimum = minimum.copy()
                minimum[frame-self.view_start, channel] = value
            painter.save()
            painter.setClipRect(rect)
            painter.setPen(QPen(c.waveform, 1))
            for channel in range(channels):
                top = rect.top() + channel * (channel_height + gap)
                center = top + channel_height / 2
                scale = channel_height * 0.45
                if envelope:
                    painter.setBrush(c.waveform)
                    draw_envelope(painter,minimum,maximum,channel,rect.left(),rect.width(),center,scale)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                else:
                    points = QPolygonF([QPointF(self.x_at(self.view_start + i), center - min(1.08, max(-1.08, float(row[channel]))) * scale)
                                        for i, row in enumerate(minimum)])
                    painter.drawPolyline(points)
                    if self.sample_points_visible():
                        # Keep adjacent sample markers separate at the lower zoom levels.
                        size = min(4.0, self.sample_spacing() - 1.0)
                        for point in points:
                            painter.fillRect(QRectF(point.x()-size/2, point.y()-size/2, size, size), c.waveform)
                    elif len(points) == 1:
                        painter.drawEllipse(points[0], 2, 2)
            active = self._sample_drag[:2] if self._sample_drag is not None else self._sample_hover
            if self.sample_editable and self.sample_points_visible() and active is not None:
                frame, channel = active
                if self.view_start <= frame < self.view_start + len(minimum):
                    value = float(minimum[frame-self.view_start, channel])
                    painter.setPen(QPen(c.plot_text, 1))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawRect(QRectF(self.x_at(frame)-3, self.sample_y(channel, value)-3, 6, 6))
            painter.restore()
        if self._drawing_stroke is not None:
            stroke = self._drawing_stroke
            lane = self.channel_rect(stroke.channel)
            painter.save()
            painter.setClipRect(lane)
            for start, end, first, last in stroke.patches():
                x1, x2 = self.x_at(start), self.x_at(end)
                painter.fillRect(QRectF(x1, lane.top(), x2-x1, lane.height()), blend(c.plot, c.accent, .18))
                painter.setPen(QPen(c.plot_text, 2))
                painter.drawLine(QPointF(x1, self.sample_y(stroke.channel, first)),
                                 QPointF(x2, self.sample_y(stroke.channel, last)))
            painter.restore()
        if channels==2:
            separator=QPen(blend(c.plot,c.plot_text,.55),1);separator.setCosmetic(True)
            painter.setPen(separator)
            for y in (self.channel_rect(0).bottom(),self.channel_rect(1).top()):
                painter.drawLine(QPointF(rect.left(),y),QPointF(rect.right(),y))
        painter.setPen(c.text)
        labels = []
        for time, x in ticks:
            label = str(round(time)) if sample_axis else f"{time:.3f}" if step < 0.1 else f"{time:.1f}"
            width = text_width(self.fontMetrics(), label)
            left = max(rect.left(), min(x - width / 2, rect.right() - width))
            labels.append((QRectF(left, rect.bottom() + 4, width, line), label))
        for area, text in separated_labels(labels):
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, text)
        painter.drawText(QRectF(rect.right() + 4, rect.bottom() + 4, amplitude_width, line), Qt.AlignmentFlag.AlignLeft, "samples" if sample_axis else "sec")
        painter.setPen(QPen(QColor("#b5c9ca"), 1))
        painter.drawRect(rect)

    def _select(self, start, end):
        self.document.select(start, end)
        self.selection_changed.emit(*self.document.selection)
        self.update()

    def mousePressEvent(self, event):
        if (self.drawing and self.sample_editable and self.document.frames and
                event.button() == Qt.MouseButton.LeftButton and
                not event.modifiers() & Qt.KeyboardModifier.ShiftModifier and
                self.plot_rect().contains(event.position())):
            channel = self.channel_at(event.position().y())
            if channel is not None:
                self.setFocus()
                self.sample_edit_started.emit()
                self._drawing_stroke = DrawingStroke(self.document, channel,
                    self.view_end-self.view_start, self.plot_rect().width())
                self._anchor = None
                self._draw_at(event.position())
                event.accept()
                return
        sample = self.sample_at(event.position())
        if sample is not None and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if event.button() == Qt.MouseButton.RightButton:
                self.sample_edit_requested.emit(sample[0], sample[1])
                event.accept()
                return
            if event.button() == Qt.MouseButton.LeftButton:
                self.setFocus()
                self.sample_edit_started.emit()
                self._sample_drag = sample
                self._anchor = None
                event.accept()
                return
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
        if self._drawing_stroke is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._draw_at(event.position())
            return
        if self._sample_drag is not None and event.buttons() & Qt.MouseButton.LeftButton:
            frame, channel, _ = self._sample_drag
            lane = self.channel_rect(channel)
            value = min(1.0, max(-1.0, (lane.center().y()-event.position().y())/(lane.height()*.45)))
            self._sample_drag = frame, channel, value
            self.update()
            return
        sample = self.sample_at(event.position())
        hovered = sample[:2] if sample is not None else None
        if hovered != self._sample_hover:
            self._sample_hover = hovered
            self.update()
        self.setCursor(Qt.CursorShape.CrossCursor if self.drawing and self.sample_editable else
                       Qt.CursorShape.SizeVerCursor if sample is not None else
                       Qt.CursorShape.IBeamCursor if self.document.frames else Qt.CursorShape.ArrowCursor)
        if self._anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            channel = self.channel_at(event.position().y())
            if not self._keep_channels:
                self.document.select_channels((channel,) if channel is not None and channel == self._anchor_channel else None)
            self._select(self._anchor, self.frame_at(event.position().x()))

    def mouseReleaseEvent(self, event):
        if self._drawing_stroke is not None and event.button() == Qt.MouseButton.LeftButton:
            self._draw_at(event.position())
            stroke = self._drawing_stroke
            self._drawing_stroke = None
            self.waveform_drawn.emit(stroke.channel, stroke.patches())
            self.update()
        if self._sample_drag is not None and event.button() == Qt.MouseButton.LeftButton:
            sample = self._sample_drag
            self._sample_drag = None
            self._sample_hover = None
            self.sample_edited.emit(*sample)
            self.update()
        self._anchor = None
        self._anchor_channel = None
        self._keep_channels = False

    def mouseDoubleClickEvent(self, event):
        if self.drawing and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.mousePressEvent(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            sample = self.sample_at(event.position())
            if sample is not None and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.cancel_sample_drag()
                self.sample_edit_requested.emit(sample[0], sample[1])
                return
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
