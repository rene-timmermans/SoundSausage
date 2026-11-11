from pathlib import Path
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QFormLayout, QLabel, QPushButton, QComboBox, QCheckBox, QFileDialog, QMessageBox

from .amplitude_ui import EffectDialog, spin
from .special import load_impulse
from .progress_ui import long_operation
from .errors import OperationCancelled


class DistortionDialog(EffectDialog):
    effect_name = 'distortion'
    KINDS = ('soft', 'hard', 'fold', 'crush')

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Distortion'); self.setMinimumWidth(510)
        layout = QVBoxLayout(self)
        self.presets = QComboBox(); self.presets.addItems(['Custom', 'Soft warmth', 'Crunch', 'Wavefold', 'Bit crush'])
        layout.addWidget(self.presets); form = QFormLayout()
        self.kind = QComboBox(); self.kind.addItems(['Soft clip', 'Hard clip', 'Wavefold', 'Bit crush'])
        self.drive = spin(12, 0, 36, ' dB'); self.ceiling = spin(90, 10, 100, ' %')
        self.bits = spin(8, 2, 16, '', 0); self.mix = spin(50, 0, 100, ' %')
        self.output = spin(0, -24, 24, ' dB')
        for label, control in [('Type', self.kind), ('Drive', self.drive), ('Ceiling', self.ceiling),
                               ('Bit depth (Bit crush)', self.bits), ('Effect mix', self.mix), ('Output gain', self.output)]:
            form.addRow(label, control)
        layout.addLayout(form)
        self.quality = QCheckBox('High quality (oversampling)'); self.quality.setChecked(True); layout.addWidget(self.quality)
        note = QLabel('High quality reduces aliasing and processes the whole selection for Preview.\n'
                      'Standard processing is faster and can give a harsher digital character.\n'
                      'Ceiling shapes only the distorted signal; Effect mix blends it with the original.')
        note.setWordWrap(True); layout.addWidget(note); self.add_footer(layout)
        self._preset = False
        for field in (self.drive, self.ceiling, self.bits, self.mix, self.output): field.valueChanged.connect(self.changed)
        self.quality.toggled.connect(self.changed); self.kind.currentIndexChanged.connect(self.changed)
        self.presets.currentIndexChanged.connect(self.preset); self.changed()

    def changed(self, *_):
        self.bits.setEnabled(self.kind.currentIndex() == 3)
        if not self._preset: self.presets.setCurrentIndex(0)

    def preset(self, index):
        if index <= 0: return
        self._preset = True
        kind, drive, mix, bits, quality = ((0, 9, 25, 8, True), (1, 18, 40, 8, True), (2, 24, 40, 8, True), (3, 0, 100, 6, False))[index-1]
        self.kind.setCurrentIndex(kind); self.drive.setValue(drive); self.mix.setValue(mix); self.bits.setValue(bits)
        self.ceiling.setValue(90); self.output.setValue(-3); self.quality.setChecked(quality)
        self._preset = False

    def settings(self):
        return dict(kind=self.KINDS[self.kind.currentIndex()], drive_db=self.drive.value(), ceiling=self.ceiling.value()/100,
                    bits=int(self.bits.value()), mix=self.mix.value()/100, output_db=self.output.value(), oversample=self.quality.isChecked())


class ConvolutionDialog(EffectDialog):
    effect_name = 'convolution'

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Convolution'); self.setMinimumWidth(560)
        self.ir_path = None; self.ir_sha256 = None
        layout = QVBoxLayout(self); self.description = QLabel('Choose a WAV impulse response.'); self.description.setWordWrap(True)
        layout.addWidget(self.description)
        browse = QPushButton('Choose Impulse Response…'); browse.clicked.connect(self.browse); layout.addWidget(browse)
        self.normalize = QCheckBox('Normalize impulse energy'); self.normalize.setChecked(True); layout.addWidget(self.normalize)
        form = QFormLayout(); self.dry = spin(100, 0, 100, ' %'); self.wet = spin(30, 0, 100, ' %'); self.output = spin(0, -24, 24, ' dB')
        form.addRow('Dry (original)', self.dry); form.addRow('Wet (convolved)', self.wet); form.addRow('Output gain', self.output)
        layout.addLayout(form)
        self.tail = QCheckBox('Keep full response tail (inserts time after selection)'); layout.addWidget(self.tail)
        self.tail.setEnabled(not document.partial_channels)
        self.tail.setToolTip("Choose Both channels to add time to a stereo waveform.")
        note = QLabel('A mono response works on either channel. A stereo response requires a stereo waveform.\n'
                      'Keep the response file unchanged to use Repeat later. Dry and Wet add together;\n'
                      'lower Output gain if needed. Tail insertion moves the following audio forward.')
        note.setWordWrap(True); layout.addWidget(note); self.add_footer(layout)
        self.set_ready(False)

    def set_ready(self, ready):
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ready)
        self.preview_button.setEnabled(ready and not self.no_audio)

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Choose Impulse Response', '', 'WAV impulse responses (*.wav *.wave);;All files (*)')
        if path: self.use_impulse(path)

    @long_operation
    def use_impulse(self, path):
        self.stop_preview()
        try:
            impulse, digest = load_impulse(path, self.document.sample_rate, self.document.effect_channel_count,
                ir_channel=self.document.selected_channels[0] if self.document.partial_channels else None)
            self.ir_path = str(Path(path).resolve()); self.ir_sha256 = digest
            self.description.setText(f'{Path(path).name} · {len(impulse)/self.document.sample_rate:.3f} s · {impulse.shape[1]} channel(s)')
            self.set_ready(True)
        except OperationCancelled: return
        except (ValueError, OSError, RuntimeError) as error: QMessageBox.warning(self, 'Impulse Response', str(error))

    def settings(self):
        if not self.ir_path: raise ValueError('Choose an impulse response first.')
        return dict(ir_path=self.ir_path, ir_sha256=self.ir_sha256, normalize=self.normalize.isChecked(),
                    dry=self.dry.value()/100, wet=self.wet.value()/100, output_db=self.output.value(), keep_tail=self.tail.isChecked())
