import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QDialogButtonBox

from .theme import colors


class SpectrumPlot(QWidget):
    def __init__(self, samples, rate, parent=None):
        super().__init__(parent)
        self.setMinimumSize(650, 300)
        n = len(samples)
        window = np.hanning(n) if n > 2 else np.ones(n)
        channels = np.fft.rfft(samples.astype(np.float64) * window[:, None], axis=0)
        magnitude = np.sqrt(np.mean(np.abs(channels) ** 2, axis=1)) / max(float(window.sum()) / 2, 1e-12)
        self.db = 20 * np.log10(np.maximum(magnitude, 1e-6))
        self.frequency = np.fft.rfftfreq(n, 1 / rate)
        self.rate = rate
        index = int(np.argmax(magnitude[1:])) + 1 if len(magnitude) > 1 else 0
        self.peak_frequency = float(self.frequency[index])
        self.peak_db = float(self.db[index])

    def paintEvent(self, event):
        painter = QPainter(self)
        c = colors()
        painter.fillRect(self.rect(), c.plot)
        rect = QRectF(50, 14, self.width() - 70, self.height() - 50)
        for db in range(-120, 1, 20):
            y = rect.bottom() - (db + 120) / 120 * rect.height()
            painter.setPen(QPen(c.plot_grid, 1))
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            painter.setPen(c.plot_text)
            painter.drawText(QRectF(2, y - 8, 42, 18), Qt.AlignmentFlag.AlignRight, str(db))
        nyquist = self.rate / 2
        lo = min(20, nyquist / 10)
        def x(f):
            return rect.left() + math.log10(max(lo, f) / lo) / math.log10(nyquist / lo) * rect.width()
        for hz in (20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000):
            if lo <= hz <= nyquist:
                xx = x(hz)
                painter.setPen(QPen(c.plot_grid, 1))
                painter.drawLine(QPointF(xx, rect.top()), QPointF(xx, rect.bottom()))
                painter.setPen(c.plot_text)
                painter.drawText(QRectF(xx - 24, rect.bottom() + 7, 48, 20), Qt.AlignmentFlag.AlignHCenter, f"{hz / 1000:g}k" if hz >= 1000 else str(hz))
        # Aggregate by display column; do not draw hundreds of thousands of segments.
        bins = np.clip(((np.log10(np.maximum(self.frequency, lo) / lo) / math.log10(nyquist / lo)) * rect.width()).astype(int), 0, int(rect.width()))
        peaks = np.full(int(rect.width()) + 1, -120.0)
        np.maximum.at(peaks, bins, self.db)
        points = QPolygonF([QPointF(rect.left() + i, rect.bottom() - (min(0, max(-120, value)) + 120) / 120 * rect.height()) for i, value in enumerate(peaks)])
        painter.setPen(QPen(c.waveform, 1))
        painter.drawPolyline(points)


class SpectrumDialog(QDialog):
    def __init__(self, samples, rate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Frequency Analysis")
        self.resize(760, 420)
        layout = QVBoxLayout(self)
        plot = SpectrumPlot(samples, rate)
        layout.addWidget(plot, 1)
        layout.addWidget(QLabel(f"Peak: {plot.peak_frequency:,.1f} Hz · {plot.peak_db:.1f} dBFS     |     Hann window · {len(samples):,} frames · channel power average"))
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        box.rejected.connect(self.reject)
        layout.addWidget(box)
