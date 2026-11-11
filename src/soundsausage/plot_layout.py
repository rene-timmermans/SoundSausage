"""Logical-pixel text geometry shared by painted audio displays."""
from dataclasses import dataclass
import math

from PySide6.QtCore import QRectF, QEvent

from .i18n import tr


def text_width(metrics, text):
    text = tr(text)
    return math.ceil(max(metrics.horizontalAdvance(text), metrics.boundingRect(text).width())) + 4


def separated_labels(candidates, gap=4):
    """Retain ordered labels only where their actual boxes have room."""
    items = list(candidates)
    previous = None
    for index, (rect, text) in enumerate(items):
        if index < len(items) - 1 and rect.right() + gap > items[-1][0].left():
            continue
        if previous is None or rect.left() >= previous.right() + gap:
            yield rect, text
            previous = rect


@dataclass
class PlotLayout:
    plot: QRectF
    metrics: object
    line_height: int
    x_title: QRectF
    y_title: QRectF

    def x_tick(self, x, text):
        width = text_width(self.metrics, text)
        return QRectF(x - width / 2, self.plot.bottom() + self.line_height / 2 + 4, width, self.line_height)

    def y_tick(self, y, text):
        return QRectF(2, y - self.line_height / 2, self.plot.left() - 8, self.line_height)


def axes_layout(widget, x_ticks, y_ticks, x_title="", y_title=""):
    metrics = widget.fontMetrics()
    line = metrics.height() + 2
    half_tick = max((text_width(metrics, text) for text in x_ticks), default=0) / 2
    left = max(8 + max((text_width(metrics, text) for text in y_ticks), default=0), half_tick + 4)
    right = max(8, half_tick + 4)
    top = 4 + line / 2 + (line + 4 if y_title else 0)
    bottom = 1.5 * line + 8 + (line + 4 if x_title else 0)
    plot = QRectF(left, top, max(1, widget.width() - left - right), max(1, widget.height() - top - bottom))
    return PlotLayout(plot, metrics, line,
                      QRectF(plot.left(), plot.bottom() + 1.5 * line + 8, plot.width(), line),
                      QRectF(0, 2, widget.width(), line))


class AxisHeightMixin:
    axis_rows = 7
    axis_minimum = 180
    axis_titles = False

    def update_axis_height(self):
        line = self.fontMetrics().height() + 2
        margins = 2 * line + 12 + (2 * line + 8 if self.axis_titles else 0)
        self.setMinimumHeight(max(self.axis_minimum, math.ceil(margins + (self.axis_rows - 1) * (line + 4))))

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self.update_axis_height()
