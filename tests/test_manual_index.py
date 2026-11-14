"""Every offline/GitHub contents entry resolves, and actual blue links navigate."""
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt, QUrl, QPoint
from PySide6.QtGui import QPalette, QColor, QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage.i18n import install_language, tr
from soundsausage.manual import ManualDialog, manual_path
from soundsausage.manual_index import topics, index_manual, CONTENTS_ANCHOR, TITLES


ROOT = Path(__file__).resolve().parents[1]


def fragments(browser):
    block = browser.document().begin()
    while block.isValid():
        current = block.begin()
        while not current.atEnd():
            value = current.fragment()
            if value.isValid():
                yield value
            current += 1
        block = block.next()


class ManualIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.palette = QPalette(self.app.palette())
        self.manager = install_language(); self.manager.set_language('en', False)
        self.dialog = ManualDialog(); self.dialog.show(); self.app.processEvents()

    def tearDown(self):
        self.dialog.reject(); self.dialog.deleteLater(); self.app.processEvents()
        self.app.setPalette(self.palette); self.manager.set_language('en', False)

    def test_all_five_static_indexes_are_current_unique_and_have_no_broken_targets(self):
        for code in ('nl', 'en', 'de', 'fr', 'es'):
            text = manual_path(code).read_text(); entries = topics(text)
            names = [e.anchor for e in entries]
            links = re.findall(r'\]\(#(ss-topic-[a-z0-9-]+)\)', text)
            self.assertGreater(len(links), 35)
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(links, names[1:])
            self.assertEqual(entries[0].anchor, CONTENTS_ANCHOR)
            self.assertEqual(entries[0].title, TITLES[code])
            self.assertEqual(index_manual(text, code), text)
        result = subprocess.run([sys.executable, 'tools/index_manuals.py', '--check'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_every_rendered_topic_has_an_anchor_and_scrolls_in_all_languages(self):
        with patch('soundsausage.manual.QDesktopServices.openUrl') as external:
            for code in ('nl', 'en', 'de', 'fr', 'es'):
                self.manager.set_language(code, False); self.app.processEvents()
                entries = topics(manual_path(code).read_text())
                names = {n for fragment in fragments(self.dialog.browser) for n in fragment.charFormat().anchorNames()}
                self.assertEqual(names, {e.anchor for e in entries})
                blocks = []; block = self.dialog.browser.document().begin()
                while block.isValid():
                    if block.blockFormat().headingLevel() in (2, 3, 4): blocks.append(block)
                    block = block.next()
                self.assertEqual(len(blocks), len(entries))
                for entry, block in zip(entries, blocks):
                    self.dialog.open_link(QUrl('#'+entry.anchor)); self.app.processEvents()
                    rect = self.dialog.browser.cursorRect(QTextCursor(block))
                    self.assertGreaterEqual(rect.top(), -2, (code, entry.title, rect))
                    self.assertLess(rect.top(), self.dialog.browser.viewport().height())
                self.dialog.contents_button.click(); self.app.processEvents()
                self.assertEqual(self.dialog.contents_button.text(), tr('Contents'))
                self.assertLess(self.dialog.browser.verticalScrollBar().value(), 200)
            external.assert_not_called()

    def test_a_real_mouse_click_follows_the_contents_link_and_contents_returns(self):
        browser = self.dialog.browser
        link = next(f for f in fragments(browser) if f.charFormat().anchorHref() == '#ss-topic-amplitude')
        cursor = QTextCursor(browser.document()); cursor.setPosition(link.position())
        browser.setTextCursor(cursor); browser.ensureCursorVisible(); self.app.processEvents()
        pos = browser.cursorRect(cursor).center()+QPoint(4, 0)
        self.assertEqual(browser.anchorAt(pos), '#ss-topic-amplitude')
        before = browser.verticalScrollBar().value()
        with patch('soundsausage.manual.QDesktopServices.openUrl') as external:
            QTest.mouseClick(browser.viewport(), Qt.MouseButton.LeftButton, pos=pos); self.app.processEvents()
            destination = browser.verticalScrollBar().value()
            self.assertGreater(destination, before+100)
            external.assert_not_called()
        self.dialog.contents_button.click(); self.app.processEvents()
        self.assertLess(browser.verticalScrollBar().value(), destination)
        self.assertLess(browser.verticalScrollBar().value(), 200)

    def test_links_remain_blue_underlined_and_readable_after_theme_and_language_changes(self):
        for dark in (False, True):
            palette = QPalette(self.palette)
            palette.setColor(QPalette.ColorRole.Base, QColor('#131619' if dark else '#ffffff'))
            palette.setColor(QPalette.ColorRole.Text, QColor('#eeeeee' if dark else '#111111'))
            palette.setColor(QPalette.ColorRole.Link, QColor('#e90070'))
            self.app.setPalette(palette); self.app.processEvents()
            for code in ('en', 'nl'):
                self.manager.set_language(code, False); self.app.processEvents()
                links = [f.charFormat() for f in fragments(self.dialog.browser) if f.charFormat().anchorHref()]
                self.assertGreater(len(links), 35)
                for fmt in links:
                    color = fmt.foreground().color()
                    self.assertGreater(color.blue(), color.red())
                    self.assertGreater(color.blue(), color.green())
                    self.assertTrue(fmt.fontUnderline())
                    self.assertEqual(color.name(), '#79bfff' if dark else '#0057b8')

    def test_previous_next_walk_topics_without_search_and_stop_at_both_ends(self):
        for code in ('nl', 'en', 'de', 'fr', 'es'):
            self.manager.set_language(code, False); self.app.processEvents()
            self.dialog.contents_button.click(); self.app.processEvents()
            self.assertEqual(self.dialog.search.text(), '')
            self.assertFalse(self.dialog.previous_button.isEnabled())
            for index in range(len(self.dialog._topic_entries)):
                self.assertTrue(self.dialog.next_button.isEnabled())
                self.dialog.next_button.click(); self.app.processEvents()
                self.assertEqual(self.dialog._topic_index, index)
            self.assertFalse(self.dialog.next_button.isEnabled())
            for index in range(len(self.dialog._topic_entries)-2, -1, -1):
                self.assertTrue(self.dialog.previous_button.isEnabled())
                self.dialog.previous_button.click(); self.app.processEvents()
                self.assertEqual(self.dialog._topic_index, index)
            self.assertFalse(self.dialog.previous_button.isEnabled())

    def test_link_and_scroll_update_topic_navigation_while_f3_still_searches(self):
        dialog = self.dialog
        index = next(i for i, e in enumerate(dialog._topic_entries) if e.anchor == 'ss-topic-amplitude')
        dialog.open_link(QUrl('#ss-topic-amplitude')); self.assertEqual(dialog._topic_index, index)
        dialog.next_button.click(); self.assertEqual(dialog._topic_index, index+1)
        dialog.previous_button.click(); self.assertEqual(dialog._topic_index, index)
        dialog.search.setText('Normalize'); dialog.search.setFocus()
        QTest.keyClick(dialog.search, Qt.Key.Key_F3); self.app.processEvents()
        self.assertEqual(dialog.browser.textCursor().selectedText().casefold(), 'normalize')
        QTest.keyClick(dialog.search, Qt.Key.Key_F3, Qt.KeyboardModifier.ShiftModifier); self.app.processEvents()
        self.assertEqual(dialog.browser.textCursor().selectedText().casefold(), 'normalize')
        dialog.browser.verticalScrollBar().setValue(dialog.browser.verticalScrollBar().maximum())
        self.app.processEvents(); self.assertFalse(dialog.next_button.isEnabled())
