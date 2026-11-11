"""Exact single-sample entry without changing neighbouring frames."""
from PySide6.QtWidgets import QVBoxLayout

from .i18n_widgets import QDialog, QFormLayout, QLabel, QComboBox, QDoubleSpinBox, QDialogButtonBox


class SampleDialog(QDialog):
    def __init__(self, document, frame, channel, parent=None):
        super().__init__(parent)
        self.document = document
        self.setWindowTitle("Edit Sample")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.frame = QDoubleSpinBox()
        self.frame.setDecimals(0)
        self.frame.setRange(0, document.frames - 1)
        self.frame.setValue(frame)
        self.frame.setKeyboardTracking(False)
        form.addRow("Sample index (from 0)", self.frame)
        self.channel = QComboBox()
        self.channel.addItems(["Mono"] if document.channels == 1 else ["Left (L)", "Right (R)"])
        self.channel.setCurrentIndex(channel)
        form.addRow("Channel", self.channel)
        self.units = QComboBox()
        self.units.addItems(["Normalized (−1 … +1)", "8-bit signed", "16-bit signed", "24-bit signed"])
        form.addRow("Interpret as", self.units)
        self.value = QDoubleSpinBox()
        self.value.setKeyboardTracking(False)
        form.addRow("Sample value", self.value)
        layout.addLayout(form)
        note = QLabel("Only this sample in the chosen channel changes. Other samples, duration and metadata stay intact. Changing the displayed range does not convert the file.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        layout.addWidget(self.box)
        self.frame.valueChanged.connect(self.load_sample)
        self.channel.currentIndexChanged.connect(self.load_sample)
        self.units.currentIndexChanged.connect(self.show_value)
        self.value.valueChanged.connect(self.value_changed)
        self.load_sample()

    def scale(self):
        return (1, 128, 32768, 8388608)[self.units.currentIndex()]

    def load_sample(self, *_):
        self.normalized_value = float(self.document.view(int(self.frame.value()), int(self.frame.value()) + 1)[0, self.channel.currentIndex()])
        self.show_value()

    def show_value(self, *_):
        scale = self.scale()
        # Preserve float headroom and exact original values until a value is edited.
        extent = max(1.0, abs(self.normalized_value)) * scale
        self.value.blockSignals(True)
        self.value.setDecimals(9 if scale == 1 else 0)
        self.value.setRange(-extent, max(extent - (1 if scale > 1 else 0), self.normalized_value * scale))
        self.value.setSingleStep(.001 if scale == 1 else 1)
        self.value.setValue(self.normalized_value * scale)
        self.value.blockSignals(False)

    def value_changed(self, value):
        self.normalized_value = value / self.scale()

    def sample_edit(self):
        self.frame.interpretText()
        self.value.interpretText()
        return int(self.frame.value()), self.channel.currentIndex(), self.normalized_value
