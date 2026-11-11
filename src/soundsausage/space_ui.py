"""Delay, echo and reverb controls with the shared non-destructive preview."""
import math

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QFormLayout, QLabel, QComboBox, QCheckBox, QPushButton

from .amplitude_ui import EffectDialog, spin


class SpaceDialog(EffectDialog):
    def header(self, title, presets):
        self.setWindowTitle(title)
        self.setMinimumWidth(530)
        self._setting = False
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Preset"))
        self.presets = QComboBox()
        self.presets.addItems(["Custom", *presets])
        row.addWidget(self.presets, 1)
        reset = QPushButton("Reset")
        reset.clicked.connect(lambda: self.preset(1))
        row.addWidget(reset)
        layout.addLayout(row)
        return layout

    def footer(self, layout, tail_default):
        form = QFormLayout()
        self.dry = spin(100, 0, 100, " %")
        self.wet = spin(30, 0, 100, " %")
        self.output = spin(0, -24, 24, " dB")
        form.addRow("Dry (original)", self.dry)
        form.addRow("Wet (effect)", self.wet)
        form.addRow("Output gain", self.output)
        self.keep_tail = QCheckBox("Add effect tail after the selection")
        self.keep_tail.setEnabled(not self.document.partial_channels)
        self.keep_tail.setToolTip("Choose Both channels to add time to a stereo waveform.")
        self.tail = spin(tail_default, .01, 60, " s", 2)
        self.tail.setEnabled(False)
        form.addRow(self.keep_tail, self.tail)
        layout.addLayout(form)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)
        note = QLabel("Adding a tail inserts time and moves the following audio forward.\n"
                      "With the box unchecked, the existing length is kept.\n"
                      "Dry and Wet add together; lower Output gain if peaks become too loud.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.add_footer(layout)
        self.keep_tail.toggled.connect(self.tail.setEnabled)
        for field in (self.dry, self.wet, self.output, self.tail):
            field.valueChanged.connect(self.changed)
        self.keep_tail.toggled.connect(self.changed)
        self.presets.currentIndexChanged.connect(self.preset)
        self.preset(1)

    def changed(self, *_):
        if not self._setting:
            self.presets.setCurrentIndex(0)
        self.update_hint()

    def common_settings(self):
        return dict(dry=self.dry.value()/100, wet=self.wet.value()/100,
                    output_db=self.output.value(), tail_seconds=self.tail.value() if self.keep_tail.isChecked() else 0)

    def update_hint(self):
        if not hasattr(self, "hint"):
            return
        duration = self.suggested_tail()
        limit = " This exceeds the 60 s tail limit; lower Feedback or Delay for a full decay." if duration > 60 else ""
        self.hint.setText(f"Suggested tail: about {duration:.2f} s.{limit}\n"
                          "The final 10 ms of an added tail fade to silence.")


class DelayDialog(SpaceDialog):
    effect_name = "delay"
    PRESETS = (("Single delay", 250, None, .3), ("Slapback", 80, None, .4),
               ("Doubling", 25, None, .35), ("Stereo widening", 20, 35, .4))

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        layout = self.header("Delay", [p[0] for p in self.PRESETS])
        self.add_times(layout)
        self.footer(layout, .5)
        if document.effect_channel_count == 1:
            self.presets.model().item(4).setEnabled(False)

    def add_times(self, layout):
        form = QFormLayout()
        self.delay = spin(250, 1, 2000, " ms", 2)
        self.right_delay = spin(250, 1, 2000, " ms", 2)
        self.linked = QCheckBox("Same delay for both channels")
        self.linked.setChecked(True)
        self.right_delay.setEnabled(False)
        form.addRow("Delay" if self.document.partial_channels else "Delay (left / mono)", self.delay)
        if self.document.effect_channel_count == 2:
            form.addRow("Right delay", self.right_delay)
            form.addRow(self.linked)
        else:
            # Keep hidden mono-only controls owned by the dialog as well.
            self.right_delay.setParent(self); self.right_delay.hide()
            self.linked.setParent(self); self.linked.hide()
        layout.addLayout(form)
        self.linked.toggled.connect(lambda value: self.right_delay.setEnabled(not value))
        self.linked.toggled.connect(self.changed)
        self.delay.valueChanged.connect(self.changed)
        self.right_delay.valueChanged.connect(self.changed)

    def time_settings(self):
        return dict(delay_ms=self.delay.value(), right_delay_ms=self.right_delay.value()
                    if self.document.effect_channel_count == 2 and not self.linked.isChecked() else None)

    def suggested_tail(self):
        times = self.time_settings()
        return max(times["delay_ms"], times["right_delay_ms"] or 0)/1000 + .01

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        _, delay, right, wet = self.PRESETS[index-1]
        self.delay.setValue(delay); self.right_delay.setValue(right or delay)
        self.linked.setChecked(right is None)
        self.dry.setValue(100); self.wet.setValue(wet*100); self.output.setValue(0)
        self.keep_tail.setChecked(False); self.tail.setValue(max(.5, self.suggested_tail()))
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.update_hint()

    def settings(self):
        return self.common_settings() | self.time_settings()


class EchoDialog(DelayDialog):
    effect_name = "echo"
    PRESETS = (("Repeating echo", 250, .4, .2, False, .3),
               ("Warm echo", 380, .5, .65, False, .4),
               ("Stereo ping pong", 375, .55, .3, True, .4),
               ("Long repeats", 650, .7, .4, False, .35))

    def __init__(self, document, parent=None, no_audio=False):
        SpaceDialog.__init__(self, document, parent, no_audio)
        layout = self.header("Echo", [p[0] for p in self.PRESETS])
        self.add_times(layout)
        form = QFormLayout()
        self.feedback = spin(40, 0, 95, " %")
        self.damping = spin(20, 0, 95, " %")
        self.ping_pong = QCheckBox("Alternate repeats between left and right")
        self.ping_pong.setVisible(document.effect_channel_count == 2)
        form.addRow("Feedback", self.feedback)
        form.addRow("High-frequency damping", self.damping)
        form.addRow(self.ping_pong)
        layout.addLayout(form)
        self.feedback.valueChanged.connect(self.changed)
        self.damping.valueChanged.connect(self.changed)
        self.ping_pong.toggled.connect(self.changed)
        self.footer(layout, 2)
        if document.effect_channel_count == 1:
            self.presets.model().item(3).setEnabled(False)

    def suggested_tail(self):
        delay = super().suggested_tail()-.01
        feedback = self.feedback.value()/100
        repeats = 1 if feedback == 0 else max(1, math.ceil(math.log(.001)/math.log(feedback)))
        return delay*repeats+.01

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        _, delay, feedback, damping, ping_pong, wet = self.PRESETS[index-1]
        self.delay.setValue(delay); self.right_delay.setValue(delay); self.linked.setChecked(True)
        self.feedback.setValue(feedback*100); self.damping.setValue(damping*100)
        self.ping_pong.setChecked(ping_pong and self.document.effect_channel_count == 2)
        self.dry.setValue(100); self.wet.setValue(wet*100); self.output.setValue(0)
        self.keep_tail.setChecked(False); self.tail.setValue(min(60, self.suggested_tail()))
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.update_hint()

    def settings(self):
        return super().settings() | dict(feedback=self.feedback.value()/100,
                    damping=self.damping.value()/100, ping_pong=self.ping_pong.isChecked())


class ReverbDialog(SpaceDialog):
    effect_name = "reverb"
    PRESETS = (("Small room", 30, .6, 8, .5, .25),
               ("Studio", 50, 1.2, 15, .45, .3),
               ("Large hall", 85, 3, 35, .35, .35),
               ("Long ambient", 100, 7, 60, .3, .45))

    def __init__(self, document, parent=None, no_audio=False):
        super().__init__(document, parent, no_audio)
        layout = self.header("Reverb", [p[0] for p in self.PRESETS])
        form = QFormLayout()
        self.room = spin(50, 20, 100, " %")
        self.decay = spin(1.5, .1, 10, " s", 2)
        self.predelay = spin(20, 0, 250, " ms", 2)
        self.damping = spin(40, 0, 95, " %")
        self.width = spin(100, 0, 100, " %")
        self.width.setEnabled(document.effect_channel_count == 2)
        form.addRow("Room size", self.room)
        form.addRow("Decay (approx. RT60)", self.decay)
        form.addRow("Predelay", self.predelay)
        form.addRow("High-frequency damping", self.damping)
        form.addRow("Stereo width", self.width)
        layout.addLayout(form)
        for field in (self.room, self.decay, self.predelay, self.damping, self.width):
            field.valueChanged.connect(self.changed)
        self.footer(layout, 2)

    def suggested_tail(self):
        return self.predelay.value()/1000 + self.decay.value()*1.25 + .1

    def preset(self, index):
        if index <= 0:
            return
        self._setting = True
        _, room, decay, predelay, damping, wet = self.PRESETS[index-1]
        for field, value in ((self.room, room), (self.decay, decay), (self.predelay, predelay),
                             (self.damping, damping*100), (self.wet, wet*100), (self.width, 100),
                             (self.dry, 100), (self.output, 0)):
            field.setValue(value)
        self.keep_tail.setChecked(False); self.tail.setValue(self.suggested_tail())
        self.presets.setCurrentIndex(index)
        self._setting = False
        self.update_hint()

    def settings(self):
        return self.common_settings() | dict(room_size=self.room.value(), decay_seconds=self.decay.value(),
                    predelay_ms=self.predelay.value(), damping=self.damping.value()/100, width=self.width.value()/100)
