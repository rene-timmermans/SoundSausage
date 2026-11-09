"""Clip-line painting and mouse gestures; previews commit once on release."""
from bisect import bisect_left
from dataclasses import replace

from PySide6.QtCore import Qt, QEvent, QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QPolygonF
from PySide6.QtWidgets import QMenu, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QLabel

from .audio import AudioError
from .envelopes import KINDS, MAX_ENVELOPE_POINTS, value_at
from .theme import colors


class EnvelopeTimeline:
    def init_envelopes(self):
        self.envelope_mode = "move"
        self._envelope_drag = None
        self._point_selection = None

    def cancel_envelope_gesture(self):
        self._envelope_drag = None
        self._preview = None

    def envelope_rect(self, clip, row):
        return self.clip_rect(clip, row).adjusted(0, 25, 0, -7)

    def envelope_y(self, clip, row, kind, value):
        rect = self.envelope_rect(clip, row)
        low, high, _ = KINDS[kind]
        return rect.bottom() - (value - low) / (high - low) * rect.height()

    def envelope_point_position(self, clip, row, kind, point):
        frame, value = point
        return QPointF(self.x_at(clip.start + frame - clip.source_start), self.envelope_y(clip, row, kind, value))

    def envelope_value_from_y(self, clip, row, kind, y):
        rect = self.envelope_rect(clip, row)
        low, high, _ = KINDS[kind]
        fraction = min(1, max(0, (rect.bottom() - y) / max(1, rect.height())))
        return round(low + (high - low) * fraction, 6)

    def envelope_seed(self, clip, kind):
        points = getattr(clip, kind + "_envelope")
        if points:
            return points
        neutral = KINDS[kind][2]
        return ((clip.source_start, neutral),) if clip.frames == 1 else (
            (clip.source_start, neutral), (clip.source_end - 1, neutral))

    def envelope_hit(self, pos, clip, row, kind, points):
        closest, distance = None, 11.0
        for index, point in enumerate(points):
            if not clip.source_start <= point[0] < clip.source_end:
                continue
            node = self.envelope_point_position(clip, row, kind, point)
            if not self.x_at(self.view_start) <= node.x() <= self.x_at(self.view_end):
                continue
            delta = ((node.x() - pos.x()) ** 2 + (node.y() - pos.y()) ** 2) ** 0.5
            if delta < distance:
                closest, distance = index, delta
        return closest

    def envelope_press(self, pos):
        if self.envelope_mode == "move":
            return False
        hit = self.hit_clip(pos)
        if not hit or pos.y() < self.clip_rect(hit[2], hit[0]).top() + 21:
            return False
        row, _, original = hit
        kind = self.envelope_mode
        self.session.choose_clip(original.id)
        self.selection_changed.emit()
        points = list(self.envelope_seed(original, kind))
        index = self.envelope_hit(pos, original, row, kind, points)
        if index is None:
            frame = min(original.source_end - 1, max(original.source_start,
                original.source_start + self.frame_at(pos.x()) - original.start))
            index = bisect_left(points, (frame,))
            point = (frame, self.envelope_value_from_y(original, row, kind, pos.y()))
            if index < len(points) and points[index][0] == frame:
                points[index] = point
            else:
                if len(points) >= MAX_ENVELOPE_POINTS:
                    self.failed.emit("This line already has 512 points. Remove a point first.")
                    return True
                points.insert(index, point)
        self._envelope_drag = dict(row=row, original=original, kind=kind, index=index, points=points)
        self._point_selection = (original.id, kind, points[index][0])
        self._preview = (row, replace(original, **{kind + "_envelope": tuple(points)}))
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.show_envelope_value(original, kind, points[index])
        self.update()
        return True

    def show_envelope_value(self, clip, kind, point):
        value = f"{point[1] * 100:.1f}%" if kind == "volume" else (
            "Centre" if point[1] == 0 else f"{'R' if point[1] > 0 else 'L'} {abs(point[1]) * 100:.1f}%")
        seconds = (point[0] - clip.source_start) / self.session.sample_rate
        self.editor.envelope_hint.setText(f"{kind.title()} {value} · {seconds:.3f} s in clip")

    def envelope_move(self, pos, buttons):
        drag = self._envelope_drag
        if drag and buttons & Qt.MouseButton.LeftButton:
            clip, points, index, kind = drag["original"], drag["points"], drag["index"], drag["kind"]
            low = max(clip.source_start, points[index - 1][0] + 1 if index else clip.source_start)
            high = min(clip.source_end - 1, points[index + 1][0] - 1 if index + 1 < len(points) else clip.source_end - 1)
            frame = min(high, max(low, clip.source_start + self.frame_at(pos.x()) - clip.start))
            points[index] = (frame, self.envelope_value_from_y(clip, drag["row"], kind, pos.y()))
            self._preview = (drag["row"], replace(clip, **{kind + "_envelope": tuple(points)}))
            self._point_selection = (clip.id, kind, frame)
            self.show_envelope_value(clip, kind, points[index])
            self.update()
            return True
        if self.envelope_mode != "move" and self._drag is None and self._range_anchor is None:
            hit = self.hit_clip(pos)
            if hit and pos.y() >= self.clip_rect(hit[2], hit[0]).top() + 21:
                row, _, clip = hit
                node = self.envelope_hit(pos, clip, row, self.envelope_mode, self.envelope_seed(clip, self.envelope_mode))
                self.setCursor(Qt.CursorShape.PointingHandCursor if node is not None else Qt.CursorShape.CrossCursor)
                return True
        return False

    def envelope_release(self):
        if self._envelope_drag is None:
            return False
        drag = self._envelope_drag
        selection = self._point_selection
        self.cancel_envelope_gesture()
        try:
            self.session.set_envelope(drag["original"].id, drag["kind"], tuple(drag["points"]))
            self.edited.emit()
            self._point_selection = selection
        except AudioError as error:
            self.failed.emit(str(error))
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.update()
        return True

    def remove_envelope_point(self, clip_id, kind, frame):
        try:
            _, clip = self.session.find_clip(clip_id)
            points = tuple(p for p in getattr(clip, kind + "_envelope") if p[0] != frame)
            self.session.set_envelope(clip_id, kind, points)
            self._point_selection = None
            self.edited.emit()
        except AudioError as error:
            self.failed.emit(str(error))

    def edit_envelope_point(self, clip, kind, index):
        points = getattr(clip, kind + "_envelope")
        frame, value = points[index]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{kind.title()} Line Point")
        form = QFormLayout(dialog)
        position = QSpinBox()
        position.setRange(0, clip.frames - 1)
        position.setValue(frame - clip.source_start)
        level = QDoubleSpinBox()
        level.setRange(KINDS[kind][0] * 100, KINDS[kind][1] * 100)
        level.setDecimals(3)
        level.setSuffix(" %")
        level.setValue(value * 100)
        displayed = level.value()
        form.addRow("Frame within clip", position)
        form.addRow("Volume" if kind == "volume" else "Pan: −100 L / +100 R", level)
        note = QLabel(f"{self.session.sample_rate:,} frames = 1 second")
        form.addRow(note)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        form.addRow(box)
        box.rejected.connect(dialog.reject)
        def apply():
            new_frame = clip.source_start + position.value()
            if any(i != index and point[0] == new_frame for i, point in enumerate(points)):
                note.setText("A point already exists at that frame.")
                return
            updated = list(points)
            updated[index] = (new_frame, value if level.value() == displayed else level.value() / 100)
            try:
                self.session.set_envelope(clip.id, kind, tuple(sorted(updated)))
            except AudioError as error:
                note.setText(str(error))
                return
            dialog.accept()
        box.accepted.connect(apply)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.edited.emit()

    def envelope_context(self, event):
        if self.envelope_mode == "move":
            return False
        hit = self.hit_clip(QPointF(event.pos()))
        if not hit:
            return False
        row, _, clip = hit
        kind = self.envelope_mode
        self.session.choose_clip(clip.id)
        self.selection_changed.emit()
        self.cancel_envelope_gesture()
        points = getattr(clip, kind + "_envelope")
        index = self.envelope_hit(QPointF(event.pos()), clip, row, kind, points)
        menu = QMenu(self)
        if index is not None:
            menu.addAction("Edit Point…", lambda: self.edit_envelope_point(clip, kind, index))
            menu.addAction("Remove Point", lambda: self.remove_envelope_point(clip.id, kind, points[index][0]))
        else:
            def add():
                if self.envelope_press(QPointF(event.pos())):
                    self.envelope_release()
            menu.addAction("Add Point Here", add)
        reset = menu.addAction(f"Reset {kind.title()} Line", self.editor.reset_envelope)
        reset.setEnabled(bool(points))
        menu.addSeparator()
        menu.addAction("Clip Properties…", self.clip_properties.emit)
        menu.addAction("Edit Copy in Waveform", lambda: self.edit_copy.emit(clip.id))
        menu.exec(event.globalPos())
        return True

    def draw_envelopes(self, painter, clip, row, accent):
        c = colors()
        selected = clip.id == self.session.selected_clip
        kinds = ("volume", "pan") if self.envelope_mode == "move" else (self.envelope_mode,)
        painter.save()
        painter.setClipRect(self.clip_rect(clip, row))
        for kind in kinds:
            points = getattr(clip, kind + "_envelope")
            if self.envelope_mode == "move" and not points:
                continue
            begin = max(clip.source_start, clip.source_start + self.view_start - clip.start)
            end = min(clip.source_end - 1, clip.source_start + self.view_end - clip.start)
            if end < begin:
                continue
            visible = [(begin, value_at(points, begin, KINDS[kind][2])),
                       *(p for p in points if begin < p[0] < end),
                       (end, value_at(points, end, KINDS[kind][2]))]
            poly = QPolygonF([self.envelope_point_position(clip, row, kind, point) for point in visible])
            colour = accent if self.envelope_mode != "move" else QColor("#e5c979" if kind == "volume" else "#c0a3ed")
            painter.setPen(QPen(c.plot, 4))
            painter.drawPolyline(poly)
            painter.setPen(QPen(colour, 2))
            painter.drawPolyline(poly)
            if selected and self.envelope_mode != "move":
                painter.setBrush(c.plot)
                for point in self.envelope_seed(clip, kind):
                    if clip.source_start <= point[0] < clip.source_end:
                        node = self.envelope_point_position(clip, row, kind, point)
                        active = self._point_selection == (clip.id, kind, point[0])
                        painter.setBrush(colour if active else c.plot)
                        painter.drawEllipse(node, 5 if active else 4, 5 if active else 4)
                body = self.envelope_rect(clip, row)
                if body.width() > 75:
                    painter.setPen(c.plot_text)
                    for label, y in (("200%" if kind == "volume" else "R", body.top()),
                                     ("0%" if kind == "volume" else "L", body.bottom() - 15)):
                        area = QRectF(body.right() - 43, y, 40, 15)
                        painter.fillRect(area, c.plot)
                        painter.drawText(area, Qt.AlignmentFlag.AlignRight, label)
        painter.restore()

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride and (
            (event.key() == Qt.Key.Key_Delete and self.envelope_mode != "move")
            or (event.key() == Qt.Key.Key_Escape and self._envelope_drag is not None)):
            event.accept()
            return True
        return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete and self.envelope_mode != "move":
            if self._point_selection is not None:
                self.remove_envelope_point(*self._point_selection)
            event.accept()
        elif event.key() == Qt.Key.Key_Escape and self._envelope_drag is not None:
            self.cancel_envelope_gesture()
            self._point_selection = None
            self.update()
            event.accept()
        else:
            super().keyPressEvent(event)
