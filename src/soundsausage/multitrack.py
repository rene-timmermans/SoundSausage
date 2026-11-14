"""Qt multitrack timeline and track/clip controls for the native session model."""
from .i18n import Literal, tr, install_language
from dataclasses import replace
import math
from .peaks import piece_peaks
from .plot_layout import text_width, separated_labels

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QEvent
from PySide6.QtGui import QColor, QPen
from .i18n_widgets import QPainter
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QScrollBar, QButtonGroup, QSizePolicy
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QWidget, QLabel, QLineEdit, QPushButton, QToolButton, QDoubleSpinBox, QCheckBox, QDialog, QFormLayout, QMenu

from .audio import AudioError
from .session import bounded_fades
from .theme import colors, blend, readable
from .icons import make_icon
from .envelope_ui import EnvelopeTimeline
from .waveform import envelope_polygon, draw_envelope


HEADER = 184
RULER = 27
ROW = 118


def decimal(value, low, high, suffix="", decimals=3):
    result = QDoubleSpinBox()
    result.setRange(low, high)
    result.setDecimals(decimals)
    result.setValue(value)
    result.setSuffix(suffix)
    result.setKeyboardTracking(False)
    return result


class TrackControls(QWidget):
    def __init__(self, track, editor, parent):
        super().__init__(parent)
        self.setObjectName("TrackControls")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.track_id = track.id
        layout = QGridLayout(self)
        layout.setContentsMargins(7, 5, 7, 5)
        layout.setSpacing(3)
        self.name = QLineEdit(track.name)
        self.name.setToolTip("Track name")
        self.name.editingFinished.connect(lambda: editor.configure_track(track.id, name=self.name.text()))
        layout.addWidget(self.name, 0, 0, 1, 3)
        active_fx = any(e.enabled for e in track.effects)
        fx = QPushButton(make_icon('track_fx', colors(), primary=active_fx), 'FX')
        fx.setToolTip('Track Effects')
        fx.setProperty('primary', active_fx)
        fx.clicked.connect(lambda *_: editor.track_effects(track.id))
        layout.addWidget(fx, 0, 3)
        mute, solo = QPushButton("M"), QPushButton("S")
        self.state_buttons = (mute, solo)
        for widget, checked, label in ((mute, track.muted, "Mute"), (solo, track.solo, "Solo")):
            widget.setCheckable(True)
            widget.setChecked(checked)
            widget.setFixedWidth(34)
            widget.setToolTip(label)
        mute.setProperty("trackState", "mute")
        solo.setProperty("trackState", "solo")
        mute.clicked.connect(lambda value: editor.configure_track(track.id, muted=value))
        solo.clicked.connect(lambda value: editor.configure_track(track.id, solo=value))
        layout.addWidget(mute, 1, 0)
        layout.addWidget(solo, 1, 1)
        layout.addWidget(QLabel("Vol %"), 1, 2)
        self.volume = decimal(track.gain * 100, 0, 10000, decimals=1)
        self.volume.setMaximumWidth(76)
        starting_volume = self.volume.value()
        self.volume.editingFinished.connect(lambda: editor.configure_track(track.id, gain=self.volume.value() / 100)
            if self.volume.value() != starting_volume else None)
        layout.addWidget(self.volume, 1, 3)
        layout.addWidget(QLabel("Pan"), 2, 0, 1, 2)
        self.pan = decimal(track.pan * 100, -100, 100, decimals=1)
        self.pan.setToolTip("−100 = left, 0 = center, +100 = right")
        self.pan.setMaximumWidth(76)
        starting_pan = self.pan.value()
        self.pan.editingFinished.connect(lambda: editor.configure_track(track.id, pan=self.pan.value() / 100)
            if self.pan.value() != starting_pan else None)
        layout.addWidget(self.pan, 2, 2, 1, 2)
        self.update_metrics()

    def update_metrics(self):
        for button in self.state_buttons:
            button.setFixedWidth(max(34, text_width(button.fontMetrics(), button.text()) + 16))
        for field, example in ((self.volume, "10000.0"), (self.pan, "−100.0")):
            field.setMaximumWidth(max(76, text_width(field.fontMetrics(), example) + 24))


class Timeline(EnvelopeTimeline, QWidget):
    selection_changed = Signal()
    edited = Signal()
    view_changed = Signal(object, object)
    failed = Signal(str)
    clip_properties = Signal()
    edit_copy = Signal(str)
    import_files = Signal(object, object, object)

    def __init__(self, session, editor):
        super().__init__()
        self.session = session
        self.editor = editor
        self.view_start = 0
        self.view_end = session.sample_rate * 10
        self.playhead = None
        self._controls = []
        self.header_width, self.row_height, self.ruler_height = HEADER, ROW, RULER
        self.clip_title_height = 20
        self._peaks = {}
        self._drag = None
        self._preview = None
        self._range_anchor = None
        self.init_envelopes()
        self.setMinimumWidth(600)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAcceptDrops(True)
        self.setToolTip("Drag clips to move them. Drag a clip edge to trim. Double-click a clip to edit a waveform copy.")
        self.rebuild_controls()
        install_language().changed.connect(self.layout_controls)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange) and hasattr(self, "_controls"):
            self.layout_controls()

    def layout_controls(self, *_):
        for control in self._controls:
            control.update_metrics()
        self.header_width = max([HEADER] + [control.sizeHint().width() + 4 for control in self._controls])
        self.row_height = max([ROW] + [control.sizeHint().height() + 3 for control in self._controls])
        self.ruler_height = max(RULER, self.fontMetrics().height() + 8)
        self.clip_title_height = max(20, self.fontMetrics().height() + 4)
        self.setMinimumHeight(self.ruler_height + self.row_height * len(self.session.tracks) + 12)
        for index, control in enumerate(self._controls):
            control.setGeometry(0, self.ruler_height + index * self.row_height, self.header_width - 4, self.row_height - 3)
        self.update()

    def rebuild_controls(self):
        for control in self._controls:
            control.hide()
            control.deleteLater()
        self._controls = []
        for track in self.session.tracks:
            control = TrackControls(track, self.editor, self)
            control.show()
            self._controls.append(control)
        self.layout_controls()
        self._peaks.clear()
        self.update()

    def set_session(self, session, fit=False):
        self.session = session
        self.cancel_envelope_gesture()
        self._point_selection = None
        self._preview = self._drag = None
        self.playhead = None
        self.rebuild_controls()
        if fit:
            self.fit()
        else:
            self.set_view(self.view_start, self.view_end)

    def plot_width(self):
        return max(1, self.width() - self.header_width - 12)

    def x_at(self, frame):
        return self.header_width + (frame - self.view_start) * self.plot_width() / (self.view_end - self.view_start)

    def frame_at(self, x):
        frame = round(self.view_start + (x - self.header_width) * (self.view_end - self.view_start) / self.plot_width())
        return min(self.session.sample_rate * 86400, max(0, frame))

    def set_view(self, start, end):
        length = max(8, int(end) - int(start))
        maximum = self.session.sample_rate * 86400
        length = min(length, maximum)
        self.view_start = max(0, min(int(start), maximum - length))
        self.view_end = self.view_start + length
        self.view_changed.emit(self.view_start, self.view_end)
        self._peaks.clear()
        self.update()

    def fit(self):
        self.set_view(0, max(self.session.frames + self.session.sample_rate // 2, self.session.sample_rate * 5))

    def zoom(self, factor, anchor=None):
        anchor = self.session.cursor if anchor is None else anchor
        anchor = min(self.view_end, max(self.view_start, anchor))
        length = self.view_end - self.view_start
        new_length = max(8, round(length / factor))
        start = round(anchor - (anchor - self.view_start) / length * new_length)
        self.set_view(start, start + new_length)

    def zoom_selection(self):
        if self.session.selected:
            self.set_view(*self.session.selection)

    def clip_rect(self, clip, row):
        return QRectF(self.x_at(clip.start), self.ruler_height + row * self.row_height + 5,
                      max(3, self.x_at(clip.end) - self.x_at(clip.start)), self.row_height - 13)

    def _display_clips(self):
        for row, track in enumerate(self.session.tracks):
            for clip in track.clips:
                if self._preview and clip.id == self._preview[1].id:
                    continue
                yield row, track, clip
        if self._preview:
            row, clip = self._preview
            yield row, self.session.tracks[row], clip

    def _wave_peaks(self, clip, begin, end, width):
        key = (clip.media_id, begin, end, width)
        if key not in self._peaks:
            data = self.session.media[clip.media_id].samples[begin:end]
            columns = max(1, min(width, len(data)))
            self._peaks[key] = piece_peaks((data,),len(data),data.shape[1],columns)[:2]
            if len(self._peaks) > 200:
                oldest = next(iter(self._peaks))
                if oldest != key:
                    self._peaks.pop(oldest)
        return self._peaks[key]

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        accent_on_plot = readable(c.accent, c.plot, 3.0)
        painter.fillRect(self.rect(), c.window)
        painter.fillRect(QRectF(self.header_width, 0, self.plot_width(), self.height()), c.plot)
        seconds = (self.view_end - self.view_start) / self.session.sample_rate
        raw = seconds / max(2, self.plot_width() / 85)
        power = 10 ** math.floor(math.log10(max(raw, 1e-9)))
        step = next(n * power for n in (1, 2, 5, 10) if n * power >= raw)
        first = math.ceil((self.view_start / self.session.sample_rate) / step) * step
        time = first
        ticks = []
        while time <= self.view_end / self.session.sample_rate + step * 1e-6 and len(ticks) < 100:
            ticks.append((time, self.x_at(time * self.session.sample_rate)))
            time += step
        for row, track in enumerate(self.session.tracks):
            rect = QRectF(self.header_width, self.ruler_height + row * self.row_height, self.plot_width(), self.row_height - 3)
            painter.fillRect(rect, QColor("#0d2021" if row % 2 else "#09191a"))
            if track.id == self.session.selected_track:
                painter.fillRect(QRectF(self.header_width - 4, rect.top(), 4, rect.height()), c.accent)
            painter.setPen(QPen(QColor("#2b4445"), 1))
            for _, x in ticks:
                painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            painter.setPen(QColor("#385153"))
            painter.drawLine(QPointF(self.header_width, rect.bottom()), QPointF(self.width() - 12, rect.bottom()))
        a, b = self.session.selection
        if b > a:
            left, right = max(self.header_width, self.x_at(a)), min(self.width() - 12, self.x_at(b))
            if right > left:
                painter.fillRect(QRectF(left, self.ruler_height, right - left, self.height() - self.ruler_height), blend(c.plot, c.accent, 0.22))
        painter.save()
        painter.setClipRect(QRectF(self.header_width, self.ruler_height, self.plot_width(), self.height() - self.ruler_height))
        for row, track, clip in self._display_clips():
            if clip.end <= self.view_start or clip.start >= self.view_end:
                continue
            rect = self.clip_rect(clip, row)
            selected = clip.id == self.session.selected_clip
            painter.fillRect(rect, blend(c.plot, c.accent, 0.17) if selected else QColor("#123329"))
            painter.fillRect(QRectF(rect.left(), rect.top(), rect.width(), self.clip_title_height), c.accent if selected else QColor("#294d43"))
            painter.setPen(c.accent_text if selected else c.plot_text)
            title = clip.name
            if clip.gain != 1:
                title += f" · {20 * math.log10(clip.gain):+.2f} dB" if clip.gain > 0 else " · −∞ dB"
            if clip.pan != 0:
                title += f" · {'R' if clip.pan > 0 else 'L'} {abs(clip.pan) * 100:.1f}%"
            if clip.muted:
                title += tr(" · MUTE")
            if clip.volume_envelope:
                title += tr(" · VOL line")
            if clip.pan_envelope:
                title += tr(" · PAN line")
            title_area = QRectF(rect.left() + 6, rect.top() + 1, max(0, rect.width() - 12), self.clip_title_height - 2)
            painter.drawText(title_area, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             Literal(self.fontMetrics().elidedText(title, Qt.TextElideMode.ElideRight, int(title_area.width()))))
            begin = max(clip.start, self.view_start)
            end = min(clip.end, self.view_end)
            source_start = clip.source_start + begin - clip.start
            source_end = source_start + end - begin
            left, right = self.x_at(begin), self.x_at(end)
            if source_end > source_start:
                minimum, maximum = self._wave_peaks(clip, source_start, source_end, max(1, int(right - left)))
                channels = minimum.shape[1]
                wave_height = rect.height() - self.clip_title_height - 5
                inactive = track.muted or clip.muted or (any(t.solo for t in self.session.tracks) and not track.solo)
                painter.setPen(QPen(QColor("#8a9b93") if inactive else c.waveform, 1))
                for channel in range(channels):
                    center = rect.top() + self.clip_title_height + 3 + (channel + 0.5) * wave_height / channels
                    scale = wave_height / channels * 0.43
                    painter.setBrush(QColor("#8a9b93") if inactive else c.waveform)
                    draw_envelope(painter,minimum,maximum,channel,left,right-left,center,scale,1.1)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
            self.draw_envelopes(painter, clip, row, accent_on_plot)
            for first,last,fade in clip.punch_ranges:
                begin=max(clip.start,clip.start+first-clip.source_start)
                end=min(clip.end,clip.start+last-clip.source_start)
                if end>begin:
                    left=max(rect.left(),self.x_at(begin));right=min(rect.right(),self.x_at(end))
                    painter.fillRect(QRectF(left,rect.top()+self.clip_title_height,max(0,right-left),rect.height()-self.clip_title_height),QColor(5,12,14,190))
            painter.setPen(QPen(accent_on_plot if selected else QColor("#7aa79a"), 2 if selected else 1))
            painter.drawRect(rect)
            if clip.fade_in:
                painter.drawLine(QPointF(rect.left(), rect.bottom()), QPointF(self.x_at(clip.start + clip.fade_in), rect.top() + self.clip_title_height))
            if clip.fade_out:
                painter.drawLine(QPointF(self.x_at(clip.end - clip.fade_out), rect.top() + self.clip_title_height), QPointF(rect.right(), rect.bottom()))
        cursor = self.session.cursor if self.playhead is None else self.playhead
        if self.view_start <= cursor <= self.view_end:
            painter.setPen(QPen(accent_on_plot if self.playhead is not None else c.plot_text, 1))
            painter.drawLine(QPointF(self.x_at(cursor), self.ruler_height), QPointF(self.x_at(cursor), self.height()))
        painter.restore()
        painter.fillRect(QRectF(self.header_width, 0, self.plot_width(), self.ruler_height), c.panel)
        painter.setPen(c.text)
        labels = []
        line = self.fontMetrics().height() + 2
        for time, x in ticks:
            text = f"{time:.3f}" if step < 0.1 else f"{time:.1f}"
            width = text_width(self.fontMetrics(), text)
            left = max(self.header_width, min(x - width / 2, self.width() - 12 - width))
            labels.append((QRectF(left, 3, width, line), text))
        for area, text in separated_labels(labels):
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, text)
        unit_width = text_width(self.fontMetrics(), "sec")
        painter.drawText(QRectF(8, 3, self.header_width - unit_width - 24, line), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Tracks")
        painter.drawText(QRectF(self.header_width - unit_width - 8, 3, unit_width, line), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "sec")

    def hit_clip(self, point):
        for row, track, clip in reversed(list(self._display_clips())):
            if point.x() >= self.header_width and self.clip_rect(clip, row).contains(point):
                return row, track, clip
        return None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self.setFocus()
        if self.envelope_press(event.position()):
            return
        self._point_selection = None
        hit = self.hit_clip(event.position())
        if hit:
            row, track, clip = hit
            self.session.choose_clip(clip.id)
            rect = self.clip_rect(clip, row)
            kind = "left" if abs(event.position().x() - rect.left()) <= 8 else "right" if abs(event.position().x() - rect.right()) <= 8 else "move"
            self._drag = (kind, row, clip, self.frame_at(event.position().x()))
            self.setCursor(Qt.CursorShape.ClosedHandCursor if kind == "move" else Qt.CursorShape.SizeHorCursor)
        elif event.position().x() >= self.header_width:
            self.session.selected_clip = None
            row = min(len(self.session.tracks) - 1, max(0, int((event.position().y() - self.ruler_height) // self.row_height)))
            self.session.selected_track = self.session.tracks[row].id
            frame = self.frame_at(event.position().x())
            self._range_anchor = frame
            self.session.select(frame, frame)
        self.selection_changed.emit()
        self.update()

    def mouseMoveEvent(self, event):
        if self.envelope_move(event.position(), event.buttons()):
            return
        if self._drag and event.buttons() & Qt.MouseButton.LeftButton:
            kind, row, original, anchor = self._drag
            delta = self.frame_at(event.position().x()) - anchor
            if kind == "move":
                row = min(len(self.session.tracks) - 1, max(0, int((event.position().y() - self.ruler_height) // self.row_height)))
                start = max(0, min(original.start + delta, self.session.sample_rate * 86400 - original.frames))
                preview = replace(original, start=start)
            elif kind == "left":
                delta = max(-min(original.start, original.source_start), min(original.frames - 1, delta))
                preview = replace(original, start=original.start + delta, source_start=original.source_start + delta)
            else:
                source = self.session.media[original.media_id]
                delta = min(len(source.samples) - original.source_end, max(1 - original.frames, delta))
                preview = replace(original, source_end=original.source_end + delta)
            fades = bounded_fades(original, preview.frames)
            self._preview = (row, replace(preview, fade_in=fades[0], fade_out=fades[1]))
            self.update()
        elif self._range_anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.session.select(self._range_anchor, self.frame_at(event.position().x()))
            self.selection_changed.emit()
            self.update()
        else:
            hit = self.hit_clip(event.position())
            if hit:
                rect = self.clip_rect(hit[2], hit[0])
                edge = min(abs(event.position().x() - rect.left()), abs(event.position().x() - rect.right())) <= 8
                self.setCursor(Qt.CursorShape.SizeHorCursor if edge else Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.IBeamCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.envelope_release():
            return
        if self._drag and self._preview:
            kind, _, original, _ = self._drag
            row, preview = self._preview
            try:
                if kind == "move":
                    self.session.move_clip(original.id, preview.start, self.session.tracks[row].id)
                else:
                    self.session.trim_clip(original.id, preview.start, preview.end)
                self.edited.emit()
            except AudioError as error:
                self.failed.emit(str(error))
        self._drag = self._preview = self._range_anchor = None
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.update()

    def mouseDoubleClickEvent(self, event):
        hit = self.hit_clip(event.position())
        if hit and self.envelope_mode != "move" and event.position().y() >= self.clip_rect(hit[2], hit[0]).top() + 21:
            self.cancel_envelope_gesture()
            points = getattr(hit[2], self.envelope_mode + "_envelope")
            index = self.envelope_hit(event.position(), hit[2], hit[0], self.envelope_mode, points)
            if index is not None:
                self.edit_envelope_point(hit[2], self.envelope_mode, index)
            return
        if hit:
            self.session.choose_clip(hit[2].id)
            self._drag = self._preview = None
            self.selection_changed.emit()
            self.edit_copy.emit(hit[2].id)

    def contextMenuEvent(self, event):
        if self.envelope_context(event):
            return
        hit = self.hit_clip(QPointF(event.pos()))
        if hit:
            self.session.choose_clip(hit[2].id)
            self.selection_changed.emit()
            menu = QMenu(self)
            menu.addAction("Clip Properties…", self.clip_properties.emit)
            menu.addAction("Edit Copy in Waveform", lambda: self.edit_copy.emit(hit[2].id))
            menu.addAction("Duplicate Clip", self.editor.duplicate_clip)
            if hit[2].punch_ranges:
                menu.addAction(make_icon('restore_punch',colors()),'Restore Covered Audio',lambda:self.editor.guarded(lambda:self.session.configure_clip(hit[2].id,punch_ranges=())))
            menu.addAction("Remove Clip", self.editor.remove_clip)
            menu.exec(event.globalPos())

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom(1.5 if event.angleDelta().y() > 0 else 1 / 1.5, self.frame_at(event.position().x()))
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        row = min(len(self.session.tracks) - 1, max(0, int((event.position().y() - self.ruler_height) // self.row_height)))
        self.import_files.emit(files, self.session.tracks[row].id, self.frame_at(event.position().x()))
        event.acceptProposedAction()


class MultitrackEditor(QWidget):
    edited = Signal()
    selection_changed = Signal()
    failed = Signal(str)
    import_requested = Signal()
    import_files = Signal(object, object, object)
    edit_copy = Signal(str)
    mixdown_requested = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        row = QHBoxLayout()
        self.primary_buttons = {}
        for name, callback in (("Import Audio…", self.import_requested.emit), ("+ Track", self.add_track),
            ("− Track", self.remove_track), ("Clip Properties…", self.properties),
            ("Duplicate", self.duplicate_clip), ("Remove Clip", self.remove_clip),
            ("Mix Down…", self.mixdown_requested.emit)):
            button = QPushButton(name)
            button.setProperty("compact", True)
            if name in ("Import Audio…", "Mix Down…"):
                button.setProperty("primary", True)
                self.primary_buttons["import_audio" if name == "Import Audio…" else "mixdown"] = button
            button.clicked.connect(lambda checked=False, action=callback: action())
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)
        envelope_row = QHBoxLayout()
        self.envelope_buttons = {}
        group = QButtonGroup(self)
        for mode, label in (("move", "Move Clips"), ("volume", "Volume Line"), ("pan", "Pan Line")):
            button = QToolButton()
            button.setProperty("compact", True)
            button.setText(label)
            button.setCheckable(True)
            button.setChecked(mode == "move")
            button.clicked.connect(lambda checked=False, mode=mode: self.set_envelope_mode(mode))
            group.addButton(button)
            self.envelope_buttons[mode] = button
            envelope_row.addWidget(button)
        self.envelope_buttons["volume"].setToolTip("Volume line: bottom 0%, middle 100%, top 200%. Multiplies clip and track volume.")
        self.envelope_buttons["pan"].setToolTip("Pan line: top R, middle centre, bottom L. Adds balance to the clip and track pan; centre keeps their settings.")
        self.reset_line = QPushButton("Reset Line")
        self.reset_line.clicked.connect(self.reset_envelope)
        envelope_row.addWidget(self.reset_line)
        self.envelope_hint = QLabel("Move clips or choose a volume/pan line.")
        self.envelope_hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        envelope_row.addWidget(self.envelope_hint, 1)
        layout.addLayout(envelope_row)
        self.scroll = QScrollBar(Qt.Orientation.Horizontal)
        layout.addWidget(self.scroll)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline = Timeline(session, self)
        area.setWidget(self.timeline)
        layout.addWidget(area, 1)
        self.timeline.edited.connect(self._did_edit)
        self.timeline.selection_changed.connect(self.selection_changed)
        self.timeline.selection_changed.connect(self.update_envelope_controls)
        self.timeline.failed.connect(self.failed)
        self.timeline.clip_properties.connect(self.properties)
        self.timeline.edit_copy.connect(self.edit_copy)
        self.timeline.import_files.connect(self.import_files)
        self.timeline.view_changed.connect(self._view_changed)
        self.scroll.valueChanged.connect(self._scroll_to)
        self.timeline.fit()
        self.update_theme()
        self.update_envelope_controls()

    def update_theme(self):
        for key, button in self.primary_buttons.items():
            button.setIcon(make_icon(key, colors(), primary=True))

    def set_session(self, session, fit=False):
        self.session = session
        self.timeline.set_session(session, fit)
        self.update_envelope_controls()

    def set_envelope_mode(self, mode):
        if mode not in ("move", "volume", "pan"):
            raise AudioError("Choose Move Clips, Volume Line or Pan Line.")
        self.timeline.cancel_envelope_gesture()
        self.timeline._drag = self.timeline._range_anchor = None
        self.timeline._point_selection = None
        self.timeline.envelope_mode = mode
        self.update_envelope_controls()
        self.timeline.update()

    def update_envelope_controls(self):
        mode = self.timeline.envelope_mode
        for key, button in self.envelope_buttons.items():
            button.setChecked(key == mode)
        selected = None
        if self.session.selected_clip:
            selected = self.session.find_clip(self.session.selected_clip)[1]
        self.reset_line.setEnabled(mode != "move" and selected is not None and bool(getattr(selected, mode + "_envelope", ())))
        if self.timeline._envelope_drag is None:
            hint = ("Move clips or choose a volume/pan line." if mode == "move" else
                    "Click to add · drag points · right-click for exact values/removal")
            self.envelope_hint.setText(hint)
            self.envelope_hint.setToolTip(hint)

    def reset_envelope(self):
        if self.session.selected_clip and self.timeline.envelope_mode != "move":
            self.perform(lambda: self.session.set_envelope(self.session.selected_clip, self.timeline.envelope_mode, ()))

    def _view_changed(self, start, end):
        self.scroll.blockSignals(True)
        length = end - start
        # A finite scrollbar follows the content plus a little empty workspace.
        maximum = max(self.session.frames + self.session.sample_rate * 10, end) - length
        self._scroll_scale = max(1,(max(0,maximum)+2147483646)//2147483647)
        scale=self._scroll_scale
        self.scroll.setRange(0,(max(0,maximum)+scale-1)//scale)
        self.scroll.setPageStep(min(2147483647,max(1,length//scale)))
        self.scroll.setSingleStep(min(2147483647,max(1,length//(20*scale))))
        self.scroll.setValue(start//scale)
        self.scroll.blockSignals(False)

    def _scroll_to(self, start):
        length = self.timeline.view_end - self.timeline.view_start
        start *= getattr(self,"_scroll_scale",1)
        self.timeline.set_view(start, start + length)

    def perform(self, action):
        try:
            action()
            self._did_edit()
        except (AudioError, ValueError) as error:
            self.failed.emit(str(error))

    def _did_edit(self):
        self.set_session(self.session)
        self.edited.emit()

    def configure_track(self, track_id, **settings):
        self.perform(lambda: self.session.configure_track(track_id, **settings))

    def track_effects(self, track_id=None):
        from .trackfx_ui import TrackEffectsDialog
        self.session.selected_track = track_id or self.session.selected_track
        dialog = TrackEffectsDialog(self, self.session.selected_track)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()

    def add_track(self):
        self.perform(self.session.add_track)

    def remove_track(self):
        self.perform(lambda: self.session.remove_track(self.session.selected_track))

    def remove_clip(self):
        if self.session.selected_clip:
            self.perform(lambda: self.session.remove_clip(self.session.selected_clip))

    def duplicate_clip(self):
        if self.session.selected_clip:
            self.perform(lambda: self.session.duplicate_clip(self.session.selected_clip))

    def properties(self):
        if not self.session.selected_clip:
            return
        session = self.session
        _, clip = session.find_clip(session.selected_clip)
        media = session.media[clip.media_id]
        dialog = QDialog(self)
        dialog.setWindowTitle("Wave Block Properties")
        form = QFormLayout(dialog)
        name = QLineEdit(Literal(clip.name))
        position = decimal(clip.start / session.sample_rate, 0, 86400, " sec", 6)
        begin = decimal(clip.source_start / session.sample_rate, 0, len(media.samples) / session.sample_rate, " sec", 6)
        end = decimal(clip.source_end / session.sample_rate, 0, len(media.samples) / session.sample_rate, " sec", 6)
        volume = decimal(clip.gain * 100, 0, 10000, " %", 2)
        pan = decimal(clip.pan * 100, -100, 100, decimals=2)
        fade_in = decimal(clip.fade_in / session.sample_rate, 0, clip.frames / session.sample_rate, " sec", 6)
        fade_out = decimal(clip.fade_out / session.sample_rate, 0, clip.frames / session.sample_rate, " sec", 6)
        mute = QCheckBox("Mute this clip")
        mute.setChecked(clip.muted)
        initial_values = {widget: widget.value() for widget in (position, begin, end, volume, pan, fade_in, fade_out)}
        for label, widget in (("Name", name), ("Timeline position", position), ("Source begin", begin), ("Source end (exclusive)", end),
                              ("Volume", volume), ("Pan: −100 L / +100 R", pan), ("Fade in", fade_in), ("Fade out", fade_out)):
            form.addRow(label, widget)
        form.addRow(mute)
        note = QLabel("Trimming keeps the source audio. Fades must fit inside the clip.")
        form.addRow(note)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.rejected.connect(dialog.reject)
        def apply():
            try:
                settings = {}
                for key, widget, convert in (("start", position, lambda value: round(value * session.sample_rate)),
                    ("source_start", begin, lambda value: round(value * session.sample_rate)),
                    ("source_end", end, lambda value: round(value * session.sample_rate)),
                    ("gain", volume, lambda value: value / 100), ("pan", pan, lambda value: value / 100),
                    ("fade_in", fade_in, lambda value: round(value * session.sample_rate)),
                    ("fade_out", fade_out, lambda value: round(value * session.sample_rate))):
                    if widget.value() != initial_values[widget]:
                        settings[key] = convert(widget.value())
                if name.text() != clip.name:
                    settings["name"] = name.text()
                if mute.isChecked() != clip.muted:
                    settings["muted"] = mute.isChecked()
                session.configure_clip(clip.id, **settings)
            except AudioError as error:
                note.setText(str(error))
                return
            dialog.accept()
        box.accepted.connect(apply)
        form.addRow(box)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._did_edit()
