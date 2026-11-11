"""VST3 bundle selection and a generic parameter editor with saved component state."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,
    QLabel,QDoubleSpinBox,QDialogButtonBox,QFileDialog)
from .plugins import read_registry, scan_plugin, PluginProcess
from .progress_ui import long_operation
from .icons import make_icon
from .theme import colors


class PluginDialog(QDialog):
    def __init__(self,session,parent=None,saved=None):
        super().__init__(parent);self.session=session;self.saved=saved;self.process=None;self.values={};self.parameters=[]
        self.setWindowTitle('VST3 Track Effect');self.resize(610,330)
        layout=QVBoxLayout(self);row=QHBoxLayout();self.plugin=QComboBox();row.addWidget(self.plugin,1)
        add=QPushButton(make_icon('plugin',colors()),'Add VST3 Bundle…');add.clicked.connect(self.add_bundle);row.addWidget(add);layout.addLayout(row)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.parameter=QComboBox();self.parameter.setEditable(True);self.parameter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        layout.addWidget(QLabel('Parameter'));layout.addWidget(self.parameter)
        row=QHBoxLayout();row.addWidget(QLabel('Normalized value'))
        self.value=QDoubleSpinBox();self.value.setRange(0,100);self.value.setDecimals(6);self.value.setSuffix(' %');self.value.setKeyboardTracking(False)
        row.addWidget(self.value);layout.addLayout(row)
        self.display=QLabel();layout.addWidget(self.display)
        note=QLabel('Apply updates the track while playback continues.\nThe project keeps parameter values and the plug-in state. The plug-in itself stays installed separately.')
        note.setWordWrap(True);layout.addWidget(note)
        self.button_box=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept);self.button_box.rejected.connect(self.reject);layout.addWidget(self.button_box)
        self.plugin.currentIndexChanged.connect(self.load_plugin);self.parameter.currentIndexChanged.connect(self.show_parameter)
        self.value.valueChanged.connect(self.change_value)
        self.reload(saved.get('plugin_id') if saved else None)

    def reload(self,key=None):
        registry=read_registry();self.plugin.blockSignals(True);self.plugin.clear()
        for identifier,entry in sorted(registry.items(),key=lambda item:item[1]['name'].casefold()):self.plugin.addItem(entry['name'],identifier)
        if key and key not in registry:self.plugin.addItem((self.saved or {}).get('name','Missing plug-in'),key)
        if key:self.plugin.setCurrentIndex(max(0,self.plugin.findData(key)))
        self.plugin.blockSignals(False);self.load_plugin()

    @long_operation
    def add_bundle(self):
        default=next((p for p in (Path.home()/'.vst3',Path('/usr/lib/vst3'),Path('/usr/local/lib/vst3')) if p.is_dir()),Path.home())
        path=QFileDialog.getExistingDirectory(self,'Choose a Linux VST3 bundle',str(default))
        if not path:return
        try:
            entries=scan_plugin(path);self.saved=None;self.reload(entries[0]['id'])
        except (ValueError,OSError,RuntimeError) as error:self.status.setText(str(error))

    def load_plugin(self,*_):
        if self.process is not None:self.process.close();self.process=None
        self.parameters=[];self.parameter.clear();key=self.plugin.currentData()
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        try:
            if key is None:raise ValueError('Add an installed Linux VST3 bundle to choose an effect.')
            entry=read_registry().get(key)
            if entry is None:raise ValueError('This plug-in is missing. Add its VST3 bundle to restore the effect.')
            settings=self.saved if self.saved and self.saved.get('plugin_id')==key else dict(plugin_id=key,name=entry['name'],fingerprint=entry['fingerprint'])
            self.process=PluginProcess(settings,self.session.sample_rate)
            self.parameters=self.process.info['parameters'];self.values={str(p['id']):p['value'] for p in self.parameters if not p['readonly']}
            self.values.update(settings.get('values',{}))
            for parameter in self.parameters:self.parameter.addItem(parameter['name'],str(parameter['id']))
            latency=self.process.info['latency']*1000/self.session.sample_rate
            self.status.setText(entry['name']+(' · Plug-in delay: %.2f ms (without automatic compensation)'%latency if latency else ''))
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True);self.show_parameter()
        except (ValueError,OSError,RuntimeError) as error:self.status.setText(str(error));self.value.setEnabled(False)

    def show_parameter(self,*_):
        index=self.parameter.currentIndex()
        if not 0<=index<len(self.parameters):self.value.setEnabled(False);return
        parameter=self.parameters[index];self.value.blockSignals(True)
        self.value.setValue(self.values.get(str(parameter['id']),parameter['value'])*100)
        self.value.setSingleStep(100/parameter['steps'] if parameter['steps']>0 else .1)
        self.value.setEnabled(not parameter['readonly']);self.value.blockSignals(False)
        self.display.setText(parameter.get('unit',''))

    def change_value(self,value):
        index=self.parameter.currentIndex()
        if 0<=index<len(self.parameters) and not self.parameters[index]['readonly']:
            self.values[str(self.parameters[index]['id'])]=value/100

    def settings(self):
        if self.process is None:raise ValueError('Choose an available VST3 effect.')
        self.process.helper.request(dict(op='parameters',values=self.values))
        snapshot=self.process.snapshot();key=self.plugin.currentData();entry=read_registry()[key]
        return dict(plugin_id=key,name=entry['name'],fingerprint=entry['fingerprint'],values=self.values.copy(),state=snapshot['state'])

    def done(self,result):
        # The rack reads settings immediately after Accepted; close after deleteLater.
        if result!=QDialog.DialogCode.Accepted and self.process is not None:self.process.close();self.process=None
        super().done(result)

    def close_processor(self):
        if self.process is not None:self.process.close();self.process=None
