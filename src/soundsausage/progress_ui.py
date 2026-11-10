"""A shared cancelable progress dialog around offline audio operations."""
from functools import wraps
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QProgressDialog

from .errors import OperationCancelled
from .operations import operation, _current


def long_operation(function):
    @wraps(function)
    def run(parent, *args, **kwargs):
        if _current.get() is not None:
            return function(parent, *args, **kwargs)
        started=time.monotonic()
        dialog=None
        def update(done,total,label):
            nonlocal dialog
            if dialog is None and time.monotonic()-started < .2:
                return True
            if dialog is None:
                dialog=QProgressDialog(label,"Annuleren",0,1000,parent)
                dialog.setWindowTitle("SoundSausage")
                dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
                dialog.setAutoClose(False);dialog.setAutoReset(False)
                dialog.setMinimumDuration(0);dialog.show()
            dialog.setLabelText(label)
            dialog.setValue(min(1000, int(done*1000//max(1,total))))
            QApplication.processEvents()
            return not dialog.wasCanceled()
        try:
            with operation(update):
                return function(parent,*args,**kwargs)
        except OperationCancelled:
            return False
        finally:
            if dialog is not None:
                dialog.close();dialog.deleteLater()
    return run
