"""Track insert rack; existing effect controls remain familiar in both views."""
from .i18n import Literal
from dataclasses import replace
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QDialog, QLabel, QListWidget, QListWidgetItem, QComboBox, QPushButton, QMessageBox, QDoubleSpinBox

from .document import Document
from .trackfx import NAMES, effect, Processor
from .theme import colors
from .icons import make_icon


def effect_icon(kind):return make_icon('amplify' if kind=='gain' else kind, colors())


def dialog_for(kind, session, parent):
    from .window import AmplifyDialog
    from .amplitude_ui import ChannelMixerDialog, DynamicsDialog
    from .filters_ui import GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog
    from .space_ui import DelayDialog, EchoDialog, ReverbDialog
    classes = dict(gain=AmplifyDialog, channel_mix=ChannelMixerDialog, dynamics=DynamicsDialog,
                   graphic_eq=GraphicEqualizerDialog, parametric_eq=ParametricEqualizerDialog,
                   filter=FilterDialog, delay=DelayDialog, echo=EchoDialog, reverb=ReverbDialog)
    document = Document(np.zeros((1, 2), np.float32), session.sample_rate, dsp=session.dsp)
    dialog = classes[kind](document, parent, no_audio=True)
    dialog.preview_button.hide()
    dialog.range_note.setText('Track insert: the source audio stays unchanged.\nApply changes while listening; the same chain is included in mixdown.')
    if kind == 'gain':
        dialog.constant.setChecked(True); dialog.constant.setEnabled(False)
        for index in (3, 4): dialog.presets.model().item(index).setEnabled(False)
    if hasattr(dialog, 'keep_tail'):
        dialog.keep_tail.setChecked(False); dialog.keep_tail.setEnabled(False)
        dialog.keep_tail.setToolTip('Set the tail length in Track Effects.')
        dialog.automatic_tail.setChecked(False); dialog.automatic_tail.setEnabled(False)
    if hasattr(dialog, 'boundary'):
        dialog.boundary.setValue(0); dialog.boundary.hide(); dialog.boundary_label.hide(); dialog.boundary_note.hide()
    return dialog


def load_settings(dialog, kind, values):
    if kind == 'gain':
        dialog.lock_channels.setChecked(False)
        for key in ('initial', 'final'):
            for field, value in zip(getattr(dialog, key), np.broadcast_to(values.get(key, values.get('initial', 1)), (2,))): field.setValue(value*100)
    elif kind == 'channel_mix':
        for fields, row in zip(dialog.weights, values['matrix']):
            for field, value in zip(fields, row): field.setValue(value*100)
    elif kind == 'dynamics':
        dialog.curve.set_points(tuple(tuple(p) for p in values['points']))
        for key, attr in (('attack_ms','attack'),('release_ms','release'),('makeup_db','makeup')):
            if key in values: getattr(dialog, attr).setValue(values[key])
        dialog.linked.setChecked(values.get('linked', True))
    elif kind == 'graphic_eq':
        for field, value in zip(dialog.gains, values['gains']): field.setValue(value)
    elif kind == 'parametric_eq':
        for row, band in zip(dialog.bands, values['bands']):
            enabled, frequency, gain, q = row
            enabled.setChecked(band.get('enabled', True)); frequency.setValue(band['frequency'])
            gain.setValue(band.get('gain_db', 0)); q.setValue(band.get('q', 1))
    elif kind == 'filter':
        dialog.kind.setCurrentIndex(('high_pass','low_pass','band_pass','notch').index(values['kind']))
        dialog.frequency.setValue(values['frequency']); dialog.q.setValue(values.get('q',1))
        dialog.slope.setCurrentIndex(round(values.get('slope', 24)/12)-1)
    else:
        mapping = {'delay_ms':('delay',1), 'right_delay_ms':('right_delay',1), 'feedback':('feedback',100),
                   'damping':('damping',100), 'room_size':('room',1), 'decay_seconds':('decay',1),
                   'predelay_ms':('predelay',1), 'width':('width',100), 'dry':('dry',100), 'wet':('wet',100)}
        for key, (attr, factor) in mapping.items():
            if key in values and values[key] is not None and hasattr(dialog,attr): getattr(dialog,attr).setValue(values[key]*factor)
        if hasattr(dialog,'linked'): dialog.linked.setChecked(values.get('right_delay_ms') is None)
        if hasattr(dialog,'ping_pong'): dialog.ping_pong.setChecked(values.get('ping_pong',False))
    if 'output_db' in values and hasattr(dialog,'output'): dialog.output.setValue(values['output_db'])


class TrackEffectsDialog(QDialog):
    def __init__(self, editor, track_id):
        super().__init__(editor)
        self.editor, self.session, self.track_id = editor, editor.session, track_id
        self.setWindowTitle('Track Effects'); self.resize(570, 430)
        layout = QVBoxLayout(self)
        self.name = QLabel(); layout.addWidget(self.name)
        self.effects = QListWidget(); layout.addWidget(self.effects, 1)
        self.effects.itemChanged.connect(self.bypass)
        self.effects.itemDoubleClicked.connect(lambda *_: self.edit_selected())
        row = QHBoxLayout(); self.kind = QComboBox()
        for key, name in NAMES.items(): self.kind.addItem(effect_icon(key), name, key)
        row.addWidget(self.kind, 1)
        add = QPushButton(make_icon('new', colors()), 'Add'); add.clicked.connect(self.add); row.addWidget(add); layout.addLayout(row)
        row = QHBoxLayout()
        for text, icon, callback in [('Edit…','clip_properties',self.edit_selected), ('Up','to_start',lambda: self.move(-1)),
                                     ('Down','to_end',lambda: self.move(1)), ('Remove','remove_clip',self.remove)]:
            button = QPushButton(make_icon(icon, colors()), text); button.clicked.connect(callback); row.addWidget(button)
        layout.addLayout(row)
        row = QHBoxLayout(); row.addWidget(QLabel('Tail after last clip'))
        self.tail = QDoubleSpinBox(); self.tail.setRange(0,60); self.tail.setDecimals(2); self.tail.setSuffix(' s')
        self.tail.editingFinished.connect(self.set_tail); row.addWidget(self.tail); layout.addLayout(row)
        note = QLabel('Effects run from top to bottom, before track volume and pan.\nUncheck an effect to bypass it. Changes can be undone with Ctrl+Z.')
        note.setWordWrap(True); layout.addWidget(note)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); box.rejected.connect(self.close); layout.addWidget(box)
        self.reload()

    def track(self):
        if self.editor.session is not self.session: raise ValueError('The session changed. Reopen Track Effects.')
        if getattr(self.editor.window(),'recording_busy',False): raise ValueError('Stop recording before changing track effects.')
        return self.session.tracks[self.session.track_index(self.track_id)]

    def reload(self, selected=None):
        track = self.track(); self.name.setText(track.name)
        selected = self.effects.currentRow() if selected is None else selected
        self.effects.blockSignals(True); self.effects.clear()
        for spec in track.effects:
            item = QListWidgetItem(effect_icon(spec.kind), Literal(spec.settings.get('name',NAMES[spec.kind])) if spec.kind=='plugin' else NAMES[spec.kind]); item.setData(Qt.ItemDataRole.UserRole,spec.id)
            item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if spec.enabled else Qt.CheckState.Unchecked)
            self.effects.addItem(item)
        self.effects.setCurrentRow(min(max(0,selected),len(track.effects)-1)); self.effects.blockSignals(False)
        self.tail.setValue(track.tail_seconds)

    def commit(self, effects):
        self.track()
        self.session.configure_track(self.track_id, effects=effects)
        self.editor._did_edit(); self.reload()

    def guarded(self, callback):
        try: callback()
        except (ValueError, OSError, RuntimeError) as error: QMessageBox.warning(self,'Track Effects',str(error))

    def configure(self, kind, original=None):
        def run():
            if kind == 'invert':
                if original is None: self.commit((*self.track().effects,effect(kind)))
                return
            if kind=='plugin':
                from .plugins_ui import PluginDialog
                dialog=PluginDialog(self.session,self,original.settings if original else None)
            else:
                dialog = dialog_for(kind,self.session,self)
                if original is not None: load_settings(dialog,kind,original.settings)
            applied = [False]
            def apply():
                def save():
                    values = dialog.settings()
                    if kind in ('graphic_eq', 'parametric_eq', 'filter'): values.pop('edge_ms', None)
                    if kind in ('delay', 'echo', 'reverb'): values.pop('auto_tail', None)
                    spec = effect(kind,values,key=original.id if original else None,enabled=original.enabled if original else True)
                    processor = Processor(spec,self.session.sample_rate,self.session.dsp); processor.close()
                    current = list(self.track().effects)
                    if original is not None or applied[0]:
                        key = original.id if original else applied[0]
                        index = next((i for i,e in enumerate(current) if e.id==key),None)
                        if index is None: raise ValueError('The effect was removed. Reopen its controls.')
                        spec = replace(spec,id=key); current[index]=spec
                    else: current.append(spec)
                    self.commit(current); applied[0]=spec.id
                self.guarded(save)
            button = dialog.button_box.addButton('Apply',QDialogButtonBox.ButtonRole.ApplyRole); button.clicked.connect(apply)
            try:
                if dialog.exec()==QDialog.DialogCode.Accepted: apply()
            finally:
                if hasattr(dialog,'close_processor'):dialog.close_processor()
                dialog.deleteLater()
        self.guarded(run)

    def add(self): self.configure(self.kind.currentData())
    def edit_selected(self):
        row=self.effects.currentRow()
        if row>=0:
            spec=self.track().effects[row]; self.configure(spec.kind,spec)
    def bypass(self,item):
        self.guarded(lambda: self.commit(tuple(replace(e,enabled=item.checkState()==Qt.CheckState.Checked)
            if e.id==item.data(Qt.ItemDataRole.UserRole) else e for e in self.track().effects)))
    def remove(self):
        row=self.effects.currentRow()
        if row>=0: self.guarded(lambda: self.commit(tuple(e for i,e in enumerate(self.track().effects) if i!=row)))
    def move(self,direction):
        def run():
            row=self.effects.currentRow(); values=list(self.track().effects); target=row+direction
            if row>=0 and 0<=target<len(values):
                values[row],values[target]=values[target],values[row]; self.commit(values); self.reload(target)
        self.guarded(run)
    def set_tail(self):
        def run():
            self.track(); self.session.configure_track(self.track_id,tail_seconds=self.tail.value()); self.editor._did_edit()
        self.guarded(run)
