"""Marker properties and a modeless list bound to the active waveform/session."""
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from .i18n_widgets import QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QLabel, QPushButton, QDialogButtonBox, QMessageBox
from .i18n import tr, install_language
from . import markers
from .icons import application_icon, make_icon
from .theme import colors


class MarkerDialog(QDialog):
    def __init__(self, model, marker=None, parent=None):
        super().__init__(parent)
        self.model,self.marker=model,marker
        self.setWindowTitle('Edit Marker' if marker else 'Add Marker')
        self.setWindowIcon(application_icon());self.setMinimumWidth(440)
        layout=QVBoxLayout(self);form=QFormLayout();layout.addLayout(form)
        self.name=QLineEdit(marker.name if marker else tr('Marker {0}').format(len(markers.for_model(model))+1))
        self.name.setMaxLength(max(256,len(marker.name) if marker else 0))
        self.position=QDoubleSpinBox();self.position.setDecimals(6);self.position.setKeyboardTracking(False)
        self.limit=getattr(model,'marker_frames',model.frames)
        frame=marker.start if marker else min(model.cursor,max(0,self.limit-1))
        self.position.setRange(0,max(0,max(self.limit-1,frame)/model.sample_rate));self.position.setSuffix(' s')
        self.position.setValue(frame/model.sample_rate)
        self.frame=QLineEdit(str(frame));self.frame.setAccessibleName('Marker frame')
        self.position.valueChanged.connect(lambda value:self.frame.setText(str(round(value*model.sample_rate))))
        self.frame.editingFinished.connect(self.frame_changed)
        self.end=QDoubleSpinBox();self.end.setDecimals(6);self.end.setKeyboardTracking(False)
        self.end.setRange(-1,max(self.limit,marker.end or 0 if marker else 0)/model.sample_rate);self.end.setSpecialValueText('Unspecified');self.end.setSuffix(' s')
        self.end.setValue(marker.end/model.sample_rate if marker and marker.end is not None else -1)
        form.addRow('Name',self.name);form.addRow('Position',self.position);form.addRow('Frame',self.frame);form.addRow('Chapter end',self.end)
        chapter=marker is not None and marker.kind=='Chapter'
        self.end.setVisible(chapter);form.labelForField(self.end).setVisible(chapter)
        note=QLabel('Markers are shared by both channels. Moving or naming a marker does not change the audio. MP3 chapters use millisecond positions.')
        note.setWordWrap(True);layout.addWidget(note)
        box=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        box.accepted.connect(self.accept);box.rejected.connect(self.reject);layout.addWidget(box)
    def frame_changed(self):
        try:frame=int(self.frame.text())
        except ValueError:return
        if 0<=frame<self.limit:self.position.setValue(frame/self.model.sample_rate)
    def values(self):
        try:frame=int(self.frame.text())
        except ValueError as error:raise ValueError('The marker must be inside the audio.') from error
        values={}
        if self.marker is None or frame!=self.marker.start:values['start']=frame
        if self.marker is None or self.name.text()!=self.marker.name:values['name']=self.name.text()
        if self.marker is not None and self.marker.kind=='Chapter':
            end=None if self.end.value()<0 else round(self.end.value()*self.model.sample_rate)
            if end!=self.marker.end:values['end']=end
        return values
    def accept(self):
        try:
            values=self.values()
            if self.marker:markers.edit(self.model.metadata,self.model.sample_rate,self.limit,self.marker.key,**values)
            else:markers.add(self.model.metadata,self.model.sample_rate,self.limit,**values)
        except (ValueError,OSError,RuntimeError) as error:
            QMessageBox.warning(self,'Marker',str(error));return
        super().accept()


class MarkerListDialog(QDialog):
    def __init__(self,window):
        super().__init__(window)
        self.window=window;self._key=None
        self.setWindowTitle('Marker List');self.setWindowIcon(application_icon())
        self.resize(760,420);self.setMinimumSize(520,300)
        layout=QVBoxLayout(self)
        self.context=QLabel();self.context.setWordWrap(True);layout.addWidget(self.context)
        self.table=QTableWidget(0,4)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        for column in (1,2,3):self.table.horizontalHeader().setSectionResizeMode(column,QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.update_buttons)
        self.table.cellDoubleClicked.connect(lambda *_:self.edit())
        layout.addWidget(self.table,1)
        buttons=QHBoxLayout();layout.addLayout(buttons)
        self.add_button=QPushButton(make_icon('marker_add',colors()),'Add…');self.add_button.clicked.connect(lambda:self.window.add_marker(True))
        self.edit_button=QPushButton('Edit…');self.edit_button.clicked.connect(self.edit)
        self.remove_button=QPushButton('Remove');self.remove_button.clicked.connect(self.remove)
        self.go_button=QPushButton('Go to');self.go_button.clicked.connect(self.go)
        for button in (self.add_button,self.edit_button,self.remove_button,self.go_button):buttons.addWidget(button)
        buttons.addStretch();close=QPushButton('Close');close.clicked.connect(self.close);buttons.addWidget(close)
        self.note=QLabel('Select a marker to edit, remove or visit it. Drag a flag above the timeline to move it. Escape cancels a drag.')
        self.note.setWordWrap(True);layout.addWidget(self.note)
        install_language().changed.connect(self.reload)
        for key in ('marker_add','markers'):window.actions[key].changed.connect(self.update_buttons)
        self._shortcuts=[]
        for keys,call in (('Ctrl+Z',lambda:window.edit(window.active_model().undo)),('Ctrl+Shift+Z',lambda:window.edit(window.active_model().redo))):
            shortcut=QShortcut(QKeySequence(keys),self);shortcut.activated.connect(call);self._shortcuts.append(shortcut)
        self.reload()
    def selected_key(self):
        item=self.table.item(self.table.currentRow(),0)
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None
    def reload(self,*_):
        selected=self.selected_key();model=self.window.active_model()
        self.table.setHorizontalHeaderLabels([tr(s) for s in ('Name','Position (s)','End (s)','Type')])
        self.context.setText('Session markers stay at absolute timeline positions when clips move.' if self.window.mode=='multitrack' else 'Waveform markers follow edits to both channels; editing one channel keeps their shared positions.')
        values=markers.for_model(model);self.table.setRowCount(len(values));chosen=-1
        for row,marker in enumerate(values):
            texts=(marker.name,QLocale().toString(marker.start/model.sample_rate,'f',6),
                   QLocale().toString(marker.end/model.sample_rate,'f',6) if marker.end is not None else '',tr(marker.kind))
            for column,text in enumerate(texts):
                item=QTableWidgetItem(text)
                if column==0:item.setData(Qt.ItemDataRole.UserRole,marker.key)
                item.setToolTip(tr('Frame {0}').format(marker.start));self.table.setItem(row,column,item)
            if marker.key==selected:chosen=row
        if chosen<0 and values:chosen=0
        if chosen>=0:self.table.selectRow(chosen)
        self.update_buttons()
    def update_buttons(self,*_):
        busy=self.window.recording_busy;selected=self.selected_key() is not None
        self.table.setEnabled(not busy)
        self.add_button.setEnabled(not busy and self.window.active_model().frames>0)
        for button in (self.edit_button,self.remove_button,self.go_button):button.setEnabled(not busy and selected)
    def edit(self):
        if not self.window.recording_busy and self.selected_key():self.window.edit_marker_dialog(self.selected_key())
    def remove(self):
        if not self.window.recording_busy and self.selected_key():self.window.remove_marker(self.selected_key())
    def go(self):
        if not self.window.recording_busy and self.selected_key():self.window.visit_marker(self.selected_key())
