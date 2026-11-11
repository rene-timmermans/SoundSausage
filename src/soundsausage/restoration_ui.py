from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QCheckBox, QComboBox, QFileDialog, QMessageBox

from .amplitude_ui import EffectDialog, spin
from .progress_ui import long_operation
from .errors import OperationCancelled
from .restoration import learn_profile, validate_profile, save_profile, load_profile


class NoiseReductionDialog(EffectDialog):
    effect_name = 'noise_reduction'

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Noise Reduction'); self.setMinimumWidth(570)
        self.profile = getattr(parent, 'noise_profile', None)
        layout = QVBoxLayout(self)
        self.profile_label = QLabel(); self.profile_label.setWordWrap(True); layout.addWidget(self.profile_label)
        buttons = QHBoxLayout()
        for title, action in [('Capture from selection', self.capture), ('Load Profile…', self.load), ('Save Profile…', self.save)]:
            button = QPushButton(title); button.clicked.connect(action); buttons.addWidget(button)
            if title.startswith('Save'): self.save_button = button
        layout.addLayout(buttons)
        self.presets = QComboBox(); self.presets.addItems(['Custom', 'Gentle', 'Balanced', 'Strong'])
        self.presets.currentIndexChanged.connect(self.preset); layout.addWidget(self.presets)
        form = QFormLayout()
        self.reduction = spin(12, 0, 36, ' dB')
        self.sensitivity = spin(2, .5, 4, '', 2)
        self.smoothing = spin(60, 0, 100, ' %')
        form.addRow('Maximum noise reduction', self.reduction)
        form.addRow('Sensitivity', self.sensitivity)
        form.addRow('Smoothing', self.smoothing)
        layout.addLayout(form)
        self.linked = QCheckBox('Link stereo channels (preserve balance)'); self.linked.setChecked(True)
        self.linked.setVisible(document.channels == 2); layout.addWidget(self.linked)
        self.residual = QCheckBox('Keep removed noise only (instead of cleaned audio)'); layout.addWidget(self.residual)
        note = QLabel('First capture a selection containing only background noise. Then close this window,\n'
                      'select the audio to clean and open Noise Reduction again.\n'
                      'Use modest reduction for changing noise or delicate musical detail.')
        note.setWordWrap(True); layout.addWidget(note)
        self.add_footer(layout)
        self.update_profile()
        for field in (self.reduction, self.sensitivity, self.smoothing):
            field.valueChanged.connect(lambda *_: self.presets.setCurrentIndex(0))

    def update_profile(self):
        try:
            validate_profile(self.profile, self.document.sample_rate, self.document.channels)
            valid = True
            self.profile_label.setText(f"Noise profile: {self.profile['sample_rate']} Hz, "
                f"{self.document.channels} channel(s), {self.profile['frames']/self.document.sample_rate:.2f} s")
        except (ValueError, TypeError):
            valid = False
            self.profile_label.setText('No compatible noise profile. Capture one from a noise-only selection or load a saved profile.')
        from PySide6.QtWidgets import QDialogButtonBox
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)
        self.preview_button.setEnabled(valid and not self.no_audio)
        self.save_button.setEnabled(valid)

    def use_profile(self, profile):
        validate_profile(profile, self.document.sample_rate, self.document.channels)
        self.stop_preview(); self.profile = profile
        if self.parent() is not None:
            self.parent().noise_profile = profile
        self.update_profile()

    @long_operation
    def capture(self):
        self.stop_preview()
        try:
            if not self.document.selected:
                raise ValueError('Select a short fragment containing only background noise first.')
            self.use_profile(learn_profile(self.document.view(*self.document.selection), self.document.sample_rate))
        except OperationCancelled:
            return
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, 'Noise Profile', str(error))

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load Noise Profile', '', 'Noise profiles (*.ssnoise);;All files (*)')
        if path:
            try: self.use_profile(load_profile(path))
            except (ValueError, OSError) as error: QMessageBox.warning(self, 'Noise Profile', str(error))

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Noise Profile', 'Noise.ssnoise', 'Noise profiles (*.ssnoise)')
        if path:
            try: save_profile(path, self.profile)
            except (ValueError, OSError) as error: QMessageBox.warning(self, 'Noise Profile', str(error))

    def preset(self, index):
        if index <= 0: return
        reduction, sensitivity, smoothing = ((6, 1.5, 75), (12, 2, 60), (24, 3, 75))[index-1]
        self.reduction.setValue(reduction); self.sensitivity.setValue(sensitivity); self.smoothing.setValue(smoothing)
        self.presets.blockSignals(True); self.presets.setCurrentIndex(index); self.presets.blockSignals(False)

    def settings(self):
        validate_profile(self.profile, self.document.sample_rate, self.document.channels)
        return dict(profile=self.profile, reduction_db=self.reduction.value(), sensitivity=self.sensitivity.value(),
                    smoothing=self.smoothing.value(), linked=self.linked.isChecked(), residual=self.residual.isChecked())


class ClickRemovalDialog(EffectDialog):
    effect_name = 'click_removal'

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Click Removal'); self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        self.presets = QComboBox(); self.presets.addItems(['Custom', 'Conservative', 'Small clicks', 'Wider clicks'])
        layout.addWidget(self.presets)
        form = QFormLayout()
        self.sensitivity = spin(8, 2, 20)
        self.threshold = spin(-35, -60, -6, ' dBFS')
        self.width = spin(1, .02, 2, ' ms', 2)
        form.addRow('Threshold multiplier (higher = fewer repairs)', self.sensitivity)
        form.addRow('Minimum jump level', self.threshold)
        form.addRow('Maximum click width', self.width)
        layout.addLayout(form)
        note = QLabel('Repairs short, isolated impulses by joining the undamaged samples around them.\n'
                      'Check Preview on percussion and sharp attacks. Long crackles and clipping need other treatment.')
        note.setWordWrap(True); layout.addWidget(note)
        self.add_footer(layout)
        for field in (self.sensitivity, self.threshold, self.width):
            field.valueChanged.connect(lambda *_: self.presets.setCurrentIndex(0))
        self.presets.currentIndexChanged.connect(self.preset)

    def preset(self, index):
        if index <= 0: return
        sensitivity, threshold, width = ((10, -30, .5), (6, -40, .5), (8, -35, 2))[index-1]
        self.sensitivity.setValue(sensitivity); self.threshold.setValue(threshold); self.width.setValue(width)
        self.presets.blockSignals(True); self.presets.setCurrentIndex(index); self.presets.blockSignals(False)

    def settings(self):
        return dict(sensitivity=self.sensitivity.value(), threshold_db=self.threshold.value(), max_width_ms=self.width.value())
