"""Audition drum-pumping recovery against the original at a chosen song position."""
import numpy as np
from PySide6.QtWidgets import QVBoxLayout
from .i18n_widgets import QFormLayout, QLabel, QComboBox, QCheckBox, QDialogButtonBox, QMessageBox
from .amplitude_ui import EffectDialog, spin
from .progress_ui import long_operation
from .errors import OperationCancelled


class RemasterDialog(EffectDialog):
    effect_name='remaster'

    def __init__(self,document,parent=None,no_audio=False):
        self._kind=None;self._cache=None
        super().__init__(document,parent,no_audio)
        self.setWindowTitle('Remaster');self.setMinimumWidth(560)
        layout=QVBoxLayout(self)
        explanation=QLabel('Reduce voices and instruments sinking behind strong drum hits. Compare a section where the pumping is clearly audible.')
        explanation.setWordWrap(True);layout.addWidget(explanation)
        self.presets=QComboBox();self.presets.addItems(['Custom','Gentle recovery','Balanced recovery','Strong recovery','Short volume drops'])
        layout.addWidget(self.presets)
        form=QFormLayout();layout.addLayout(form)
        self.amount=spin(60,0,100,' %')
        self.recovery=spin(4,0,9,' dB')
        self.cuts=spin(0,0,18,' dB')
        self.cuts.setToolTip('Repairs short mid/high volume drops near drums. 0 dB disables this extra repair; start with 12 dB for deep cuts. Silence and gradual fades are retained.')
        self.sensitivity=spin(3,0,12,' dB')
        self.release=spin(180,50,500,' ms',0)
        self.ceiling=spin(-1,-12,0,' dBFS')
        for title,field in [('Pumping reduction',self.amount),('Maximum recovery',self.recovery),
                            ('Short-drop repair',self.cuts),('Drum threshold',self.sensitivity),('Recovery time',self.release),('Output ceiling',self.ceiling)]:
            form.addRow(title,field)
        start,end=document.effect_range
        self.position=spin(min(max(start,document.cursor),max(start,end-1))/document.sample_rate,
                           start/document.sample_rate,max(start,end-1)/document.sample_rate,' s',3)
        form.addRow('Preview from',self.position)
        self.match=QCheckBox('Match listening volume for original and preview');self.match.setChecked(True)
        layout.addWidget(self.match)
        note=QLabel('The first preview analyses the complete range. Sustained mid/high sound is recovered with linked stereo balance; the bass foundation is retained. Output headroom uses one constant gain.\nStronger recovery can change the balance of voices and drums. Missing or clipped detail cannot be reconstructed exactly.')
        note.setWordWrap(True);layout.addWidget(note)
        self.add_footer(layout)
        self.range_note.setText(f'Channels: {document.channel_label}. Applies to the selection, or the whole waveform if nothing is selected.\nOriginal and preview play up to 8 seconds from the chosen position.')
        self.original_button=self.button_box.addButton('Original',QDialogButtonBox.ButtonRole.ActionRole)
        self.original_button.setEnabled(not no_audio);self.original_button.clicked.connect(self.original)
        self.presets.currentIndexChanged.connect(self.preset)
        for field in (self.amount,self.recovery,self.cuts,self.sensitivity,self.release,self.ceiling):
            field.valueChanged.connect(lambda *_:self.presets.setCurrentIndex(0))
        self.presets.setCurrentIndex(2)

    def preset(self,index):
        if index<=0:return
        amount,recovery,threshold,release,cuts=((35,2,4,160,0),(60,4,3,180,0),(90,6,2,240,0),(90,6,2,240,12))[index-1]
        for field,value in ((self.amount,amount),(self.recovery,recovery),(self.sensitivity,threshold),(self.release,release),(self.cuts,cuts)):
            field.blockSignals(True);field.setValue(value);field.blockSignals(False)
        self.stop_preview()

    def settings(self):
        return dict(amount=self.amount.value(),recovery_db=self.recovery.value(),sensitivity_db=self.sensitivity.value(),
                    release_ms=self.release.value(),ceiling_db=self.ceiling.value(),cut_repair_db=self.cuts.value())

    def _processed(self):
        key=(self.document.revision,self.document.effect_range,self.document.selected_channels,tuple(sorted(self.settings().items())))
        if self._cache is None or self._cache[0]!=key:
            result=self.document._process_effect(self.effect_name,**self.settings())
            self._cache=(key,result)
        return self._cache[1]

    def audition_samples(self):
        start,end=self.document.effect_range
        position=min(max(start,round(self.position.value()*self.document.sample_rate)),end)
        stop=min(end,position+8*self.document.sample_rate)
        processed=self._processed()[position-start:stop-start]
        if self.document.partial_channels:processed=self.document._merge_channel(position,processed)
        original=self.document.view(position,stop)
        original=np.array(original,copy=True);processed=np.array(processed,copy=True)
        if self.match.isChecked() and len(original):
            rms=[float(np.sqrt(np.mean(data.astype(np.float64)**2))) for data in (original,processed)]
            peaks=[float(np.max(abs(data))) for data in (original,processed)]
            if min(rms)>1e-12:
                target=min(*rms,*(r*.89/max(p,1e-12) for r,p in zip(rms,peaks)))
                original*=target/rms[0];processed*=target/rms[1]
        return original,processed

    def preview_samples(self):return self.audition_samples()[1]

    def preview_state(self,state):
        if hasattr(self,'preview_button'):
            self.preview_button.setText('Stop Preview' if state!='Stopped' and self._kind=='processed' else 'Preview')
        if hasattr(self,'original_button'):
            self.original_button.setText('Stop Original' if state!='Stopped' and self._kind=='original' else 'Original')

    @long_operation
    def _audition(self,kind):
        if self.no_audio:return
        if self.player.state!='Stopped' and self._kind==kind:self.stop_preview();return
        self.stop_preview()
        try:
            original,processed=self.audition_samples();self._kind=kind
            self.player.play(original if kind=='original' else processed,self.document.sample_rate)
        except OperationCancelled:return
        except (ValueError,OSError,RuntimeError) as error:QMessageBox.warning(self,'Preview',str(error))

    def preview(self):self._audition('processed')
    def original(self):self._audition('original')
