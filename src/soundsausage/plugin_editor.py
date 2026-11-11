"""Native plug-in window, created only inside the isolated helper process."""
import os


def key_message(event):
    # Steinberg keycodes.h, pinned with the other SDK interfaces. Ctrl maps to
    # kCommandKey (the VSTGUI Control modifier); Meta maps to kControlKey/Super.
    from PySide6.QtCore import Qt
    keys={Qt.Key.Key_Backspace:1,Qt.Key.Key_Tab:2,Qt.Key.Key_Clear:3,Qt.Key.Key_Return:4,
        Qt.Key.Key_Pause:5,Qt.Key.Key_Escape:6,Qt.Key.Key_Space:7,Qt.Key.Key_End:9,Qt.Key.Key_Home:10,
        Qt.Key.Key_Left:11,Qt.Key.Key_Up:12,Qt.Key.Key_Right:13,Qt.Key.Key_Down:14,
        Qt.Key.Key_PageUp:15,Qt.Key.Key_PageDown:16,Qt.Key.Key_Enter:19,Qt.Key.Key_Insert:21,
        Qt.Key.Key_Delete:22,Qt.Key.Key_Help:23,Qt.Key.Key_NumLock:52,Qt.Key.Key_ScrollLock:53,
        Qt.Key.Key_Shift:54,Qt.Key.Key_Control:55,Qt.Key.Key_Alt:56,Qt.Key.Key_Menu:58,Qt.Key.Key_Meta:77}
    key=event.key();virtual=keys.get(key,0)
    if Qt.Key.Key_F1<=key<=Qt.Key.Key_F12:virtual=40+key-Qt.Key.Key_F1
    elif Qt.Key.Key_F13<=key<=Qt.Key.Key_F24:virtual=65+key-Qt.Key.Key_F13
    elif 48<=key<=57 or 65<=key<=90:virtual=key-48+128
    text=event.text().encode('utf-16-le');character=int.from_bytes(text[:2],'little') if text else 0
    if character<32:character=0
    modifiers=event.modifiers()
    bits=sum(bit for flag,bit in ((Qt.KeyboardModifier.ShiftModifier,1),(Qt.KeyboardModifier.AltModifier,2),
                (Qt.KeyboardModifier.ControlModifier,4),(Qt.KeyboardModifier.MetaModifier,8)) if modifiers&flag)
    return character,virtual,bits


class Editor:
    def __init__(self, plugin, name):
        if not os.environ.get('DISPLAY'):
            raise ValueError('Custom plug-in windows require an X11 or XWayland display. Parameter controls remain available.')
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        from PySide6.QtWidgets import QApplication, QWidget
        from PySide6.QtCore import Qt
        self.app = QApplication.instance() or QApplication([])
        self.app.setApplicationName('SoundSausage');self.app.setDesktopFileName('soundsausage')
        self.app.setQuitOnLastWindowClosed(False)
        self.plugin = plugin
        self.sizing = False
        owner = self
        class Window(QWidget):
            def keyPressEvent(self,event):
                if hasattr(owner.plugin,'editor_key') and owner.plugin.editor_key(*key_message(event),True):event.accept()
                else:super().keyPressEvent(event)
            def keyReleaseEvent(self,event):
                if hasattr(owner.plugin,'editor_key') and owner.plugin.editor_key(*key_message(event),False):event.accept()
                else:super().keyReleaseEvent(event)
            def wheelEvent(self,event):
                if hasattr(owner.plugin,'editor_wheel') and owner.plugin.editor_wheel(event.angleDelta().y()/120):event.accept()
                else:super().wheelEvent(event)
            def focusInEvent(self,event):
                if hasattr(owner.plugin,'editor_focus'):owner.plugin.editor_focus(True)
                super().focusInEvent(event)
            def focusOutEvent(self,event):
                if hasattr(owner.plugin,'editor_focus'):owner.plugin.editor_focus(False)
                super().focusOutEvent(event)
            def resizeEvent(self, event):
                super().resizeEvent(event)
                if not owner.sizing and owner.plugin.editor_size():
                    ratio = self.devicePixelRatioF()
                    owner.plugin.resize_editor(round(self.width()*ratio),round(self.height()*ratio))
            def closeEvent(self, event):
                owner.plugin.close_editor()
                event.accept()
        self.window = Window()
        self.window.setWindowTitle(name)
        from .icons import application_icon
        self.window.setWindowIcon(application_icon())
        self.window.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        self.window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        try:
            plugin.open_editor(int(self.window.winId()), self.window.devicePixelRatioF())
            self.sync_size()
            self.window.show()
            self.app.processEvents()
        except Exception:
            self.window.close(); self.window.deleteLater()
            raise

    def sync_size(self):
        size = self.plugin.editor_size()
        if size:
            ratio = self.window.devicePixelRatioF()
            width,height = (max(1,round(n/ratio)) for n in size)
            if (width,height) != (self.window.width(),self.window.height()):
                self.sizing = True
                try:self.window.resize(width,height)
                finally:self.sizing = False

    def idle(self):
        self.app.processEvents()
        self.plugin.idle()
        self.sync_size()

    def close(self):
        self.window.close(); self.window.deleteLater(); self.app.processEvents()
        from PySide6.QtCore import QCoreApplication,QEvent
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
