"""A separate marker strip, with non-destructive drag previews on both timelines."""
from PySide6.QtCore import Qt, QRectF, QPointF, QEvent
from PySide6.QtGui import QPen, QPolygonF
from . import markers
from .i18n import Literal, tr
from .theme import colors, readable


class MarkerOverlay:
    def init_markers(self): self._marker_drag=None
    def marker_model(self): return self.document if hasattr(self,'document') else self.session
    def marker_height(self): return self.fontMetrics().height()+8 if markers.for_model(self.marker_model()) else 0
    def marker_plot(self):
        return self.plot_rect() if hasattr(self,'document') else QRectF(self.header_width,self.ruler_height,self.plot_width(),self.height()-self.ruler_height)
    def marker_band(self):
        plot=self.marker_plot();height=self.marker_height()
        return QRectF(plot.left(),plot.top()-height,plot.width(),height)
    def marker_hit(self, point):
        if not self.marker_band().contains(point):return None
        candidates=[m for m in markers.for_model(self.marker_model()) if self.view_start<=m.start<=self.view_end and abs(self.x_at(m.start)-point.x())<=7]
        return min(candidates,key=lambda m:abs(self.x_at(m.start)-point.x())) if candidates else None
    def marker_press(self, point):
        marker=self.marker_hit(point)
        if marker is None:return False
        self.setFocus();self.marker_started.emit()
        self._marker_drag=(marker,marker.start)
        model=self.marker_model();model.select(marker.start,marker.start)
        if hasattr(self,'document'):self.selection_changed.emit(*model.selection)
        else:self.selection_changed.emit()
        self.update();return True
    def marker_move(self, point):
        if self._marker_drag is None:return False
        marker,_=self._marker_drag;model=self.marker_model()
        maximum=getattr(model,'marker_frames',model.frames)-1
        if marker.kind=='Chapter' and marker.end is not None:maximum-=max(0,marker.end-marker.start-1)
        frame=max(0,min(maximum,self.frame_at(point.x())))
        self._marker_drag=(marker,frame);self.update();return True
    def marker_release(self):
        if self._marker_drag is None:return False
        marker,frame=self._marker_drag;self._marker_drag=None
        if frame!=marker.start:self.marker_moved.emit(marker.key,frame)
        self.update();return True
    def cancel_marker(self):
        if self._marker_drag is not None:self._marker_drag=None;self.update()
    def marker_double_click(self, point):
        marker=self.marker_hit(point)
        if marker is None:return False
        self.cancel_marker();self.marker_edit_requested.emit(marker.key);return True
    def event(self,event):
        if event.type()==QEvent.Type.ShortcutOverride and event.key()==Qt.Key.Key_Escape and self._marker_drag is not None:
            event.accept();return True
        return super().event(event)
    def focusOutEvent(self,event):
        self.cancel_marker();super().focusOutEvent(event)
    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_Escape and self._marker_drag is not None:
            self.cancel_marker();event.accept()
        else:super().keyPressEvent(event)
    def draw_markers(self,painter):
        band=self.marker_band()
        if not band.height():return
        model=self.marker_model();plot=self.marker_plot();c=colors();ink=readable(c.accent,c.plot,3)
        last_label=band.left()-1
        painter.save();painter.setClipRect(QRectF(plot.left(),band.top(),plot.width(),plot.bottom()-band.top()))
        for marker in markers.for_model(model):
            start=marker.start;end=marker.end
            if self._marker_drag is not None and self._marker_drag[0].key==marker.key:
                start=self._marker_drag[1]
                if end is not None:end+=start-marker.start
            if end is not None and self.view_start<=end<=self.view_end:
                painter.setPen(QPen(ink,1,Qt.PenStyle.DotLine));x=self.x_at(end)
                painter.drawLine(QPointF(x,plot.top()),QPointF(x,plot.bottom()))
            if not self.view_start<=start<=self.view_end:continue
            x=self.x_at(start)
            painter.setPen(QPen(ink,1,Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(x,plot.top()),QPointF(x,plot.bottom()))
            painter.setPen(Qt.PenStyle.NoPen);painter.setBrush(ink)
            painter.drawPolygon(QPolygonF([QPointF(x-4,band.top()+2),QPointF(x+4,band.top()+2),QPointF(x,band.bottom()-2)]))
            left=max(x+7,band.left()+7)
            if left<last_label+8:continue
            width=min(150,band.right()-left-3)
            if width<12:continue
            title=marker.name or tr('Marker')
            title=self.fontMetrics().elidedText(title,Qt.TextElideMode.ElideRight,int(width))
            width=self.fontMetrics().horizontalAdvance(title)
            painter.setPen(readable(c.text,c.window,4.5))
            painter.drawText(QRectF(left,band.top(),width+2,band.height()),Qt.AlignmentFlag.AlignVCenter,Literal(title))
            last_label=left+width
        painter.restore()
