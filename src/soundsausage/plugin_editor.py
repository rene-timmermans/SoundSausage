"""Native plug-in window, created only inside the isolated helper process."""
import os


class Editor:
    def __init__(self, plugin, name):
        if not os.environ.get('DISPLAY'):
            raise ValueError('Custom plug-in windows require an X11 or XWayland display. Parameter controls remain available.')
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        from PySide6.QtWidgets import QApplication, QWidget
        from PySide6.QtCore import Qt
        self.app = QApplication.instance() or QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.plugin = plugin
        self.sizing = False
        owner = self
        class Window(QWidget):
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
        self.window.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
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
