"""Shared input/output preferences; device discovery starts only when audio is used."""
from .i18n import Literal
from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QVBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QDialog, QFormLayout, QComboBox, QSpinBox, QLabel

from .audio import AudioError


class AudioDevices(QObject):
    changed = Signal()
    outputs_changed = Signal()
    inputs_changed = Signal()

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings if settings is not None else QSettings("SoundSausage", "SoundSausage")
        self.output_id = str(self.settings.value("audio/output", ""))
        self.input_id = str(self.settings.value("audio/input", ""))
        try:
            self.buffer_ms = min(500, max(20, int(self.settings.value("audio/buffer_ms", 100))))
        except (ValueError, TypeError):
            self.buffer_ms = 100
        self._monitor = None

    def _ensure_monitor(self):
        if self._monitor is None:
            self._monitor = QMediaDevices(self)
            self._monitor.audioOutputsChanged.connect(self.outputs_changed)
            self._monitor.audioInputsChanged.connect(self.inputs_changed)

    def outputs(self):
        self._ensure_monitor()
        return QMediaDevices.audioOutputs()

    def inputs(self):
        self._ensure_monitor()
        return QMediaDevices.audioInputs()

    def output(self):
        devices = self.outputs()
        if not devices:
            raise AudioError("No audio output is available. Connect an output device and check the system's audio settings.")
        if self.output_id:
            for device in devices:
                if bytes(device.id()).hex() == self.output_id:
                    return device
            raise AudioError("The selected audio output is unavailable. Choose an output in Options → Audio Hardware.")
        return next((device for device in devices if device.isDefault()), devices[0])

    def input(self):
        devices = self.inputs()
        if not devices:
            raise AudioError("No recording input is available. Connect a microphone or audio interface and check the system's audio settings.")
        if self.input_id:
            for device in devices:
                if bytes(device.id()).hex() == self.input_id:
                    return device
            raise AudioError("The selected recording input is unavailable. Choose an input in Options → Audio Hardware.")
        return next((device for device in devices if device.isDefault()), devices[0])

    def configure(self, output_id, buffer_ms, input_id=None):
        if not isinstance(output_id, str) or not isinstance(buffer_ms, int) or not 20 <= buffer_ms <= 500:
            raise AudioError("The playback buffer must be between 20 and 500 ms.")
        if input_id is not None and not isinstance(input_id,str):
            raise AudioError("Invalid recording input.")
        self.output_id, self.buffer_ms = output_id, buffer_ms
        if input_id is not None:
            self.input_id = input_id
            self.settings.setValue("audio/input", input_id)
        self.settings.setValue("audio/output", output_id)
        self.settings.setValue("audio/buffer_ms", buffer_ms)
        self.settings.sync()
        self.changed.emit()


class AudioHardwareDialog(QDialog):
    def __init__(self, devices, parent=None):
        super().__init__(parent)
        self.devices = devices
        self.setWindowTitle("Audio Hardware")
        self.setMinimumWidth(490)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.output = QComboBox()
        self.output.setAccessibleName("Playback device")
        self.input = QComboBox()
        self.input.setAccessibleName("Recording device")
        self.buffer = QSpinBox()
        self.buffer.setRange(20, 500)
        self.buffer.setSuffix(" ms")
        self.buffer.setValue(devices.buffer_ms)
        form.addRow("Playback device", self.output)
        form.addRow("Playback buffer", self.buffer)
        form.addRow("Recording device", self.input)
        layout.addLayout(form)
        self.note = QLabel("A larger buffer tolerates interruptions better; a smaller buffer responds faster.\n"
                           "Changing these settings stops playback and effect previews.\nNo microphone is opened until Record is started.")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        layout.addWidget(box)
        self.reload(devices.output_id)
        self.reload_input(devices.input_id)
        devices.outputs_changed.connect(self.reload)
        devices.inputs_changed.connect(self.reload_input)

    def reload(self, selected=None):
        if selected is None:
            selected = self.output.currentData() or ""
        self.output.clear()
        self.output.addItem("System Default", "")
        for device in self.devices.outputs():
            self.output.addItem(Literal(device.description()), bytes(device.id()).hex())
        index = self.output.findData(selected)
        if selected and index < 0:
            self.output.addItem("Selected output (disconnected)", selected)
            index = self.output.count() - 1
        self.output.setCurrentIndex(max(0, index))

    def reload_input(self, selected=None):
        selected = self.input.currentData() or "" if selected is None else selected
        self.input.clear()
        self.input.addItem("System Default", "")
        for device in self.devices.inputs():
            self.input.addItem(Literal(device.description()),bytes(device.id()).hex())
        index = self.input.findData(selected)
        if selected and index < 0:
            self.input.addItem("Selected input (disconnected)",selected)
            index = self.input.count()-1
        self.input.setCurrentIndex(max(0,index))

    def accept(self):
        self.devices.configure(self.output.currentData(), self.buffer.value(), self.input.currentData())
        super().accept()
