"""Searchable, nonmodal manual, bundled for offline use in installed packages."""
from pathlib import Path
from bisect import bisect_right

from PySide6.QtCore import QUrl, QEvent, QPoint
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut, QTextCursor, QTextDocument, QPalette, QColor, QTextCharFormat
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QDialog, QLineEdit, QPushButton, QLabel, QTextBrowser

from .icons import application_icon
from .i18n import language, install_language
from .manual_index import topics, CONTENTS_ANCHOR


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
        self.previous_button, self.next_button = QPushButton("Vorige"), QPushButton("Volgende")
        previous, following = self.previous_button, self.next_button
        previous.setToolTip('Previous topic'); following.setToolTip('Next topic')
        self.contents_button = QPushButton('Contents')
        self.contents_button.setAutoDefault(False)
        self.contents_button.clicked.connect(lambda: self.open_link(QUrl('#'+CONTENTS_ANCHOR)))
        previous.setAutoDefault(False)
        following.setAutoDefault(False)
        search.addWidget(self.search, 1)
        search.addWidget(self.contents_button)
        search.addWidget(previous)
        search.addWidget(following)
        layout.addLayout(search)
        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)
        self.browser.setOpenExternalLinks(False)
        self._formatting_links = False
        self._topic_index = -1
        self._topic_entries = []
        self._topic_positions = []
        self._navigating = False
        self.browser.verticalScrollBar().valueChanged.connect(self.update_topic_position)
        self.browser.installEventFilter(self)
        self.reload_language()
        install_language().changed.connect(self.reload_language)
        self.browser.anchorClicked.connect(self.open_link)
        layout.addWidget(self.browser, 1)
        self.search_status = QLabel("Ctrl+F: zoeken · F3: volgende treffer · Shift+F3: vorige treffer")
        self.search_status.setWordWrap(True)
        layout.addWidget(self.search_status)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        box.button(QDialogButtonBox.StandardButton.Close).setAutoDefault(False)
        box.rejected.connect(self.close)
        layout.addWidget(box)
        self.search.returnPressed.connect(self.find)
        following.clicked.connect(lambda: self.navigate_topic(1))
        previous.clicked.connect(lambda: self.navigate_topic(-1))
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
        markdown = manual_path().read_text(encoding='utf-8')
        self._topic_entries = []; self._topic_positions = []; self._topic_index = -1
        self._navigating = True
        self.browser.setMarkdown(markdown)
        # Qt's Markdown reader drops empty HTML anchors. Bind explicit names to
        # the rendered heading blocks as well, for Qt 6.8 and later alike.
        entries = iter(topics(markdown))
        block = self.browser.document().begin()
        while block.isValid():
            if block.blockFormat().headingLevel() in (2, 3, 4):
                entry = next(entries, None)
                if entry is not None:
                    cursor = QTextCursor(block)
                    cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
                    anchor = QTextCharFormat(); anchor.setAnchor(True); anchor.setAnchorNames([entry.anchor])
                    cursor.mergeCharFormat(anchor)
                    if entry.anchor != CONTENTS_ANCHOR:
                        self._topic_entries.append(entry)
                        self._topic_positions.append(block.position())
            block = block.next()
        self.format_links()
        scroll.setValue(round(position*scroll.maximum()))
        self._navigating = False
        self.update_topic_position()

    def update_topic_position(self, *_):
        if self._navigating:
            return
        position = self.browser.cursorForPosition(QPoint(0, 0)).position()
        self._topic_index = bisect_right(self._topic_positions, position)-1
        scroll = self.browser.verticalScrollBar()
        if scroll.maximum() and scroll.value() == scroll.maximum():
            self._topic_index = len(self._topic_entries)-1
        self.update_topic_buttons()

    def update_topic_buttons(self):
        self.previous_button.setEnabled(self._topic_index > 0)
        self.next_button.setEnabled(self._topic_index+1 < len(self._topic_entries))

    def navigate_topic(self, direction):
        index = self._topic_index+direction
        if 0 <= index < len(self._topic_entries):
            self.open_link(QUrl('#'+self._topic_entries[index].anchor))

    def eventFilter(self, obj, event):
        if obj is getattr(self, 'browser', None) and event.type() == QEvent.Type.PaletteChange:
            self.format_links()
        return super().eventFilter(obj, event)

    def format_links(self):
        if self._formatting_links:
            return
        self._formatting_links = True
        try:
            palette = self.browser.palette()
            blue = QColor('#79bfff' if palette.color(QPalette.ColorRole.Base).lightness() < 128 else '#0057b8')
            if any(palette.color(role) != blue for role in (QPalette.ColorRole.Link, QPalette.ColorRole.LinkVisited)):
                palette.setColor(QPalette.ColorRole.Link, blue)
                palette.setColor(QPalette.ColorRole.LinkVisited, blue)
                self.browser.setPalette(palette)
            ranges = []
            block = self.browser.document().begin()
            while block.isValid():
                fragment = block.begin()
                while not fragment.atEnd():
                    value = fragment.fragment()
                    if value.isValid() and value.charFormat().anchorHref():
                        ranges.append((value.position(), value.length()))
                    fragment += 1
                block = block.next()
            for start, length in ranges:
                cursor = QTextCursor(self.browser.document()); cursor.setPosition(start)
                cursor.setPosition(start+length, QTextCursor.MoveMode.KeepAnchor)
                style = QTextCharFormat(); style.setForeground(blue); style.setFontUnderline(True)
                cursor.mergeCharFormat(style)
        finally:
            self._formatting_links = False

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
            self._navigating = True
            self.browser.scrollToAnchor(url.fragment())
            self._navigating = False
            if url.fragment() == CONTENTS_ANCHOR:
                self._topic_index = -1
            else:
                index = next((i for i, entry in enumerate(self._topic_entries) if entry.anchor == url.fragment()), None)
                if index is not None:
                    self._topic_index = index
            self.update_topic_buttons()
        elif url.scheme() in ("https", "http"):
            QDesktopServices.openUrl(url)
