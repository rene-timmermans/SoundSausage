from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QFormLayout, QLabel, QComboBox, QCheckBox, QPushButton, QMessageBox

from .amplitude_ui import EffectDialog, spin


class StretchDialog(EffectDialog):
    effect_name = 'stretch'

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Stretch'); self.setMinimumWidth(520)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.length = spin(100, 25, 400, ' %', 2)
        form.addRow('New length (100% = unchanged)', self.length)
        self.quality = QComboBox(); self.quality.addItems(['Fine', 'Fast'])
        form.addRow('Quality', self.quality); layout.addLayout(form)
        row = QHBoxLayout()
        self.original_bpm = spin(120, 20, 400, ' BPM')
        self.target_bpm = spin(100, 20, 400, ' BPM')
        calculate = QPushButton('Set from tempo')
        calculate.clicked.connect(self.set_tempo)
        row.addWidget(QLabel('From')); row.addWidget(self.original_bpm); row.addWidget(QLabel('to')); row.addWidget(self.target_bpm); row.addWidget(calculate)
        layout.addLayout(row)
        self.duration_label = QLabel(); layout.addWidget(self.duration_label)
        self.length.valueChanged.connect(self.update_duration); self.update_duration()
        note = QLabel('Changes duration while keeping pitch. 200% is twice as long; 50% is half as long.\n'
                      'Cue positions inside the selection follow the new timing; later audio moves with it.\n'
                      'Preview analyses the entire selection first, including for long files.')
        note.setWordWrap(True); layout.addWidget(note)
        self.add_footer(layout)

    def update_duration(self):
        a, b = self.document.effect_range
        self.duration_label.setText(f'Original: {(b-a)/self.document.sample_rate:.3f} s → '
                                    f'Result: {(b-a)*self.length.value()/100/self.document.sample_rate:.3f} s')

    def set_tempo(self):
        length = 100*self.original_bpm.value()/self.target_bpm.value()
        if not 25 <= length <= 400:
            QMessageBox.information(self, 'Stretch', 'Choose a tempo change within the 25–400% length range.')
            return
        self.length.setValue(length)

    def settings(self):
        return dict(time_ratio=self.length.value()/100, quality=('fine', 'fast')[self.quality.currentIndex()])


class PitchShiftDialog(EffectDialog):
    effect_name = 'pitch_shift'

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        self.setWindowTitle('Pitch Shift'); self.setMinimumWidth(500)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.semitones = spin(0, -24, 24, ' semitones', 2)
        form.addRow('Pitch change (+12 = one octave up)', self.semitones)
        self.quality = QComboBox(); self.quality.addItems(['Fine', 'Fast']); form.addRow('Quality', self.quality)
        layout.addLayout(form)
        self.formants = QCheckBox('Preserve formants (natural vocal character)'); self.formants.setChecked(True)
        layout.addWidget(self.formants)
        note = QLabel('Changes pitch while keeping duration. Fractions of a semitone give fine tuning.\n'
                      'Extreme shifts may sound artificial; compare both formant settings on instruments.\n'
                      'Preview analyses the complete selection first, then plays at most 8 seconds.')
        note.setWordWrap(True); layout.addWidget(note)
        self.add_footer(layout)

    def settings(self):
        return dict(semitones=self.semitones.value(), preserve_formants=self.formants.isChecked(),
                    quality=('fine', 'fast')[self.quality.currentIndex()])
