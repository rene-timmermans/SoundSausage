"""Qt widgets that retain translatable UI source text, without translating editable data."""
import time
from PySide6 import QtWidgets as W,QtGui as G
from PySide6.QtCore import Qt, QEvent, QTimer, QSize
from shiboken6 import isValid
from .i18n import tr,watch,bind,install_language,Literal

# Unchanged Qt classes remain available from this module.
for _name in dir(W):
    if _name.startswith('Q'):globals()[_name]=getattr(W,_name)

_SETTERS=('setWindowTitle','setToolTip','setStatusTip','setWhatsThis','setAccessibleName',
          'setPlaceholderText','setTitle','setSpecialValueText','setSuffix','setPrefix',
          'setLabelText','setCancelButtonText','setInformativeText','setDetailedText')


def localized(base,text_method=None):
    class Localized(base):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self._loc_sources={};self._loc_replaying=False;watch(self)
            install_language()
            if text_method:
                source=next((arg for arg in args if isinstance(arg,str)),None)
                if source is not None:getattr(self,text_method)(source)
            if base is W.QProgressDialog:
                if args and isinstance(args[0],str):self.setLabelText(args[0])
                if len(args)>1 and isinstance(args[1],str):self.setCancelButtonText(args[1])
    def setter(method):
        native=getattr(base,method)
        def set_value(self,value):
            if not getattr(self,'_loc_replaying',False):
                if not hasattr(self,'_loc_sources'):self._loc_sources={}
                self._loc_sources[(method,())]=value
                value=tr(value)
            return native(self,value)
        return set_value
    for method in (*_SETTERS,*((text_method,) if text_method else ())):
        if hasattr(base,method):setattr(Localized,method,setter(method))
    Localized.__name__=base.__name__
    return Localized


for _name in ('QWidget','QDialog','QGroupBox','QLabel','QPushButton','QCheckBox','QRadioButton',
              'QToolButton','QSlider','QLineEdit','QDoubleSpinBox','QSpinBox','QProgressDialog','QTextBrowser'):
    _text='setText' if _name in ('QLabel','QPushButton','QCheckBox','QRadioButton') else 'setTitle' if _name=='QGroupBox' else None
    globals()[_name]=localized(getattr(W,_name),_text)
QAction=localized(G.QAction,'setText')
QToolBar=localized(W.QToolBar,'setWindowTitle')


class QDialog(QDialog):
    """Fit translated content to its font; scroll if it cannot fit the screen."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._fit_pending=False;self._fitting=False;self._base_minimum=None
        self._content=None;self._content_scroll=None
        install_language().changed.connect(self._queue_fit)

    def _queue_fit(self,*_):
        if self.isVisible() and not self._fit_pending and not self._fitting:
            self._fit_pending=True
            QTimer.singleShot(0,self._fit_content)

    def showEvent(self,event):
        super().showEvent(event)
        self._fit_content()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'_fit_pending'):self._queue_fit()

    def changeEvent(self,event):
        super().changeEvent(event)
        if hasattr(self,'_fit_pending') and event.type() in (QEvent.Type.FontChange,QEvent.Type.StyleChange):
            self._queue_fit()

    def eventFilter(self,watched,event):
        if event.type() in (QEvent.Type.LayoutRequest,QEvent.Type.Resize):self._queue_fit()
        return super().eventFilter(watched,event)

    def _make_scrollable(self):
        layout=self.layout()
        boxes=self.findChildren(W.QDialogButtonBox)
        for box in boxes:
            for child in self.findChildren(W.QLayout):child.removeWidget(box)
        self._content=W.QWidget()
        self._content.setLayout(layout)
        self._content.installEventFilter(self)
        self._content_scroll=W.QScrollArea(self)
        self._content_scroll.setFrameShape(W.QFrame.Shape.NoFrame)
        self._content_scroll.setWidgetResizable(True)
        self._content_scroll.setWidget(self._content)
        self._content_scroll.viewport().installEventFilter(self)
        outer=W.QVBoxLayout(self);outer.setContentsMargins(0,0,0,0)
        outer.addWidget(self._content_scroll,1)
        if boxes:
            footer=W.QHBoxLayout();footer.setContentsMargins(11,0,11,11)
            for box in boxes:footer.addWidget(box)
            outer.addLayout(footer)

    def _fit_content(self):
        if not isValid(self):return
        self._fit_pending=False
        if self._fitting or not self.isVisible() or self.layout() is None:return
        self._fitting=True
        try:
            if self._base_minimum is None:self._base_minimum=QSize(self.minimumSize())
            available=self.screen().availableGeometry()
            max_width=max(240,available.width()-32)
            max_height=max(200,available.height()-60)
            layout=self._content.layout() if self._content is not None else self.layout()
            # Nested grids cache their own hints; invalidate them after a
            # translation or font change before measuring the outer form.
            for child in self.findChildren(W.QLayout):child.invalidate()
            layout.invalidate()
            minimum=layout.minimumSize()
            preferred=layout.sizeHint()
            width=min(max_width,max(W.QWidget.width(self),self._base_minimum.width(),preferred.width(),minimum.width()))
            needed=max(minimum.height(),layout.totalHeightForWidth(width))
            if self._content is None and (needed>max_height or minimum.width()>max_width):
                self._make_scrollable()
            if self._content is None:
                self.setMinimumSize(max(self._base_minimum.width(),minimum.width()),max(self._base_minimum.height(),needed))
                self.resize(width,min(max_height,max(W.QWidget.height(self),needed,self.minimumHeight())))
            else:
                self.setMinimumSize(min(max_width,self._base_minimum.width()),min(max_height,self._base_minimum.height()))
                self.resize(width,min(max_height,max(W.QWidget.height(self),needed)))
                self.layout().activate()
                scrollbar=self.style().pixelMetric(W.QStyle.PixelMetric.PM_ScrollBarExtent)
                content_width=max(minimum.width(),self._content_scroll.viewport().width()-scrollbar)
                content_height=max(minimum.height(),layout.totalHeightForWidth(content_width))
                self._content.setMinimumSize(minimum.width(),content_height)
        finally:self._fitting=False


def set_text(widget,source):
    """Use for standard buttons created internally by Qt."""
    if not hasattr(widget,'_loc_sources'):widget._loc_sources={}
    widget._loc_sources[('setText',())]=source;watch(widget);widget.setText(tr(source))


class QComboBox(localized(W.QComboBox)):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self._loc_items=[]
    def addItem(self,*args,**kwargs):
        index=self.count();super().addItem(*args,**kwargs)
        source=next((arg for arg in args if isinstance(arg,str)),None)
        self._loc_items.insert(index,source)
        if source is not None:W.QComboBox.setItemText(self,index,tr(source))
    def addItems(self,texts):
        for text in texts:self.addItem(text)
    def insertItem(self,index,*args,**kwargs):
        super().insertItem(index,*args,**kwargs);index=max(0,min(index,self.count()-1))
        source=next((arg for arg in args if isinstance(arg,str)),None);self._loc_items.insert(index,source)
        if source is not None:W.QComboBox.setItemText(self,index,tr(source))
    def clear(self):self._loc_items=[];super().clear()
    def removeItem(self,index):
        if 0<=index<len(self._loc_items):self._loc_items.pop(index)
        super().removeItem(index)
    def setItemText(self,index,text):
        if 0<=index<len(self._loc_items):self._loc_items[index]=text
        W.QComboBox.setItemText(self,index,tr(text))
    def findText(self,text,*args):return super().findText(tr(text),*args)
    def setCurrentText(self,text):super().setCurrentText(tr(text))
    def _localize_items(self):
        old=self.blockSignals(True)
        try:
            for index,source in enumerate(self._loc_items):
                if source is not None and index<self.count():W.QComboBox.setItemText(self,index,tr(source))
        finally:self.blockSignals(old)


class QFormLayout(W.QFormLayout):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setRowWrapPolicy(W.QFormLayout.RowWrapPolicy.WrapLongRows)
        self.setLabelAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

    def addRow(self,*args):
        result=super().addRow(*args)
        if len(args)==2 and isinstance(args[0],str):
            label=self.labelForField(args[1])
            if label is not None:set_text(label,args[0])
        return result


class QDialogButtonBox(W.QDialogButtonBox):
    def addButton(self,*args):
        if len(args)==2 and isinstance(args[0],str):
            button=QPushButton(args[0],self)
            super().addButton(button,args[1])
            return button
        return super().addButton(*args)


class QMenu(localized(W.QMenu,'setTitle')):
    def addMenu(self,*args):
        if len(args)==1 and isinstance(args[0],str):
            menu=QMenu(args[0],self);super().addMenu(menu);return menu
        return super().addMenu(*args)
    def addAction(self,*args,**kwargs):
        action=super().addAction(*args,**kwargs)
        if action is not None:
            text=next((arg for arg in args if isinstance(arg,str)),None)
            if text is not None:set_text(action,text)
        return action


class QMenuBar(W.QMenuBar):
    def addMenu(self,*args):
        if len(args)==1 and isinstance(args[0],str):
            menu=QMenu(args[0],self);super().addMenu(menu);return menu
        return super().addMenu(*args)


class QStatusBar(localized(W.QStatusBar)):
    def showMessage(self,text,timeout=0):
        self._loc_message=text;self._loc_deadline=time.monotonic()+timeout/1000 if timeout else None
        super().showMessage(tr(text),timeout)
    def clearMessage(self):self._loc_message=None;super().clearMessage()
    def _localize_status(self):
        if not self.currentMessage() or not getattr(self,'_loc_message',None):return
        deadline=self._loc_deadline;remaining=round((deadline-time.monotonic())*1000) if deadline else 0
        if deadline and remaining<=0:self.clearMessage()
        else:W.QStatusBar.showMessage(self,tr(self._loc_message),remaining)


class QMainWindow(localized(W.QMainWindow)):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setMenuBar(QMenuBar(self));self.setStatusBar(QStatusBar(self))


class QListWidgetItem(W.QListWidgetItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self._loc_sources={};self._loc_replaying=False;watch(self)
        source=next((arg for arg in args if isinstance(arg,str)),None)
        if source is not None:self.setText(source)
    def setText(self,text):
        if not getattr(self,'_loc_replaying',False):self._loc_sources[('setText',())]=text;text=tr(text)
        super().setText(text)


class QListWidget(localized(W.QListWidget)):
    def addItem(self,item):super().addItem(QListWidgetItem(item) if isinstance(item,str) else item)
    def addItems(self,items):
        for item in items:self.addItem(item)


class QPainter(G.QPainter):
    def drawText(self,*args):
        if args and isinstance(args[-1],str):args=(*args[:-1],tr(args[-1]))
        return super().drawText(*args)


class QMessageBox(localized(W.QMessageBox,'setText')):
    pass
for _method in ('information','warning','critical','question','about'):
    def _message(parent,title,text,*args,_method=_method,**kwargs):
        return getattr(W.QMessageBox,_method)(parent,tr(title),tr(text),*args,**kwargs)
    setattr(QMessageBox,_method,staticmethod(_message))


class QFileDialog(W.QFileDialog):pass
for _method in ('getOpenFileName','getOpenFileNames','getSaveFileName','getExistingDirectory'):
    def _file_dialog(parent=None,caption='',directory='',filter='',*args,_method=_method,**kwargs):
        # Native desktop dialogs may use the desktop language rather than the app language.
        kwargs['options']=kwargs.get('options',W.QFileDialog.Option(0))|W.QFileDialog.Option.DontUseNativeDialog
        if _method=='getExistingDirectory':return W.QFileDialog.getExistingDirectory(parent,tr(caption),directory,*((filter,) if filter else ()),*args,**kwargs)
        return getattr(W.QFileDialog,_method)(parent,tr(caption),directory,tr(filter),*args,**kwargs)
    setattr(QFileDialog,_method,staticmethod(_file_dialog))


class QInputDialog(W.QInputDialog):pass
for _method in ('getText','getInt','getDouble','getItem','getMultiLineText'):
    def _input(parent,title,label,*args,_method=_method,**kwargs):return getattr(W.QInputDialog,_method)(parent,tr(title),tr(label),*args,**kwargs)
    setattr(QInputDialog,_method,staticmethod(_input))
