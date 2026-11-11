"""Searchable, nonmodal manual, bundled for offline use in installed packages."""
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut, QTextCursor, QTextDocument, QPalette
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QDialog, QLineEdit, QPushButton, QLabel, QTextBrowser

from .icons import application_icon
from .theme import colors, readable
from .i18n import language, install_language


def manual_path(code=None):
    code=code or language()
    docs=Path(__file__).resolve().parents[2]/'docs'
    return docs/'HANDLEIDING.md' if code=='nl' else docs/'manual'/(code+'.md')


class ManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Handleiding — SoundSausage")
        self.setWindowIcon(application_icon())
        self.resize(850, 680)
        self.setMinimumSize(550, 400)
        layout = QVBoxLayout(self)
        search = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Zoeken in de handleiding…")
        self.search.setAccessibleName("Zoeken in de handleiding")
        previous, following = QPushButton("Vorige"), QPushButton("Volgende")
        previous.setAutoDefault(False)
        following.setAutoDefault(False)
        search.addWidget(self.search, 1)
        search.addWidget(previous)
        search.addWidget(following)
        layout.addLayout(search)
        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)
        self.browser.setOpenExternalLinks(False)
        c = colors()
        palette = self.browser.palette()
        palette.setColor(QPalette.ColorRole.Link, readable(c.accent, c.base))
        self.browser.setPalette(palette)
        self.reload_language()
        install_language().changed.connect(self.reload_language)
        self.browser.anchorClicked.connect(self.open_link)
        layout.addWidget(self.browser, 1)
        self.search_status = QLabel("Ctrl+F: zoeken · F3: volgende · Shift+F3: vorige")
        layout.addWidget(self.search_status)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        box.button(QDialogButtonBox.StandardButton.Close).setAutoDefault(False)
        box.rejected.connect(self.close)
        layout.addWidget(box)
        self.search.returnPressed.connect(self.find)
        following.clicked.connect(lambda: self.find())
        previous.clicked.connect(lambda: self.find(True))
        self._shortcuts = []
        for keys, callback in (("Ctrl+F", self.focus_search), ("F3", self.find), ("Shift+F3", lambda: self.find(True))):
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)

    def focus_search(self):
        self.search.setFocus()
        self.search.selectAll()

    def reload_language(self,*_):
        scroll=self.browser.verticalScrollBar()
        position=scroll.value()/max(1,scroll.maximum())
        self.browser.setMarkdown(manual_path().read_text(encoding='utf-8'))
        scroll.setValue(round(position*scroll.maximum()))

    def find(self, backwards=False):
        term = self.search.text().strip()
        if not term:
            self.focus_search()
            return
        flags = QTextDocument.FindFlag.FindBackward if backwards else QTextDocument.FindFlag(0)
        found = self.browser.find(term, flags)
        if not found:
            self.browser.moveCursor(QTextCursor.MoveOperation.End if backwards else QTextCursor.MoveOperation.Start)
            found = self.browser.find(term, flags)
        self.search_status.setText(f"Gevonden: {term}" if found else f"Niet gevonden: {term}")

    def open_link(self, url):
        if url.isRelative() and url.fragment():
            self.browser.scrollToAnchor(url.fragment())
        elif url.scheme() in ("https", "http"):
            QDesktopServices.openUrl(url)
