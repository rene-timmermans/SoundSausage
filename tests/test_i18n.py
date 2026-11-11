"""End-to-end language switching, document integrity, persistence and offline help."""
import json
import contextlib
import io
import os
from pathlib import Path
import re
import string
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QSettings, QTimer, Qt, QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QLabel, QLineEdit, QToolButton
from soundsausage import i18n
from soundsausage.i18n import LANGUAGES, Literal, catalogue, install_language, tr
from soundsausage.i18n_widgets import QComboBox, QPushButton, QFileDialog, QMessageBox
from soundsausage.window import MainWindow
from soundsausage.document import Document
from soundsausage.amplitude_ui import NormalizeDialog, ChannelMixerDialog, DynamicsDialog, EnvelopeDialog
from soundsausage.filters_ui import GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog
from soundsausage.space_ui import DelayDialog, EchoDialog, ReverbDialog
from soundsausage.time_pitch_ui import StretchDialog, PitchShiftDialog
from soundsausage.special_ui import DistortionDialog, ConvolutionDialog
from soundsausage.restoration_ui import NoiseReductionDialog, ClickRemovalDialog
from soundsausage.about import AboutDialog
from soundsausage.manual import ManualDialog, manual_path

ROOT=Path(__file__).resolve().parents[1]


class LanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.manager=install_language();self.old_settings=self.manager.settings
        self.manager.settings=QSettings(str(Path(self.folder.name)/'language.ini'),QSettings.Format.IniFormat)
        self.manager.set_language('en',False)
        data=np.column_stack((np.linspace(-.2,.2,8000),np.linspace(.1,-.1,8000))).astype(np.float32)
        self.window=MainWindow(Document(data,8000),no_audio=True)
        self.window.show();self.app.processEvents()
        self.dialogs=[]

    def tearDown(self):
        for dialog in self.dialogs:dialog.close();dialog.deleteLater()
        self.manager.set_language('en',False);self.manager.settings=self.old_settings
        self.window.document.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater();self.app.processEvents();self.folder.cleanup()

    def switch(self,code):self.manager.set_language(code,False);self.app.processEvents()

    def test_options_language_actions_switch_existing_ui_and_keep_one_choice(self):
        expected={'nl':('Bestand','Taal'),'en':('File','Language'),'de':('Datei','Sprache'),'fr':('Fichier','Langue'),'es':('Archivo','Idioma')}
        for code,(file,lang) in expected.items():
            self.window.language_actions[code].trigger();self.app.processEvents()
            self.assertEqual(self.window.menus['file'].title().replace('&',''),file)
            self.assertEqual(self.window.menus['language'].title(),lang)
            self.assertEqual([k for k,a in self.window.language_actions.items() if a.isChecked()],[code])
            self.assertEqual(self.manager.settings.value('ui/language'),code)
            for key in ('open','save_as','record','normalize','convolution','zoom_selection'):
                self.assertEqual(self.window.actions[key].text(),tr(self.window.actions[key]._loc_sources[('setText',())]))
            self.assertIn(tr('Untitled'),self.window.windowTitle())

    def test_language_is_read_on_next_start_without_environment_override(self):
        self.manager.set_language('es')
        script="""from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from soundsausage.i18n import install_language,language,tr
import sys
app=QApplication([])
install_language(settings=QSettings(sys.argv[1],QSettings.Format.IniFormat))
print(language(),tr('Language'))
"""
        env=os.environ.copy();env.pop('SOUNDSAUSAGE_LANGUAGE',None)
        result=subprocess.run([sys.executable,'-c',script,self.manager.settings.fileName()],env=env,capture_output=True,text=True,check=True,timeout=15)
        self.assertEqual(result.stdout.strip(),'es Idioma')

    def test_open_manual_changes_language_and_remains_searchable_offline(self):
        self.window.open_manual();dialog=self.window._manual_dialog
        markers={'nl':'Taal kiezen','en':'Language and help','de':'Sprache und Hilfe','fr':'Langue et aide','es':'Idioma y ayuda'}
        for code,marker in markers.items():
            self.switch(code)
            self.assertIs(self.window._manual_dialog,dialog)
            text=dialog.browser.toPlainText();self.assertIn(marker,text)
            self.assertGreater(len(text.split()),3000)
            self.assertIn('VST3',text);self.assertIn('524',text)
            dialog.search.setText('VST3');dialog.find()
            self.assertEqual(dialog.browser.textCursor().selectedText(),'VST3')
            dialog.search.setText('zzmissing');dialog.find()
            self.assertEqual(dialog.search_status.text(),tr('Niet gevonden: zzmissing'))
            self.assertTrue(manual_path(code).is_file())
            self.assertEqual(dialog.windowTitle(),tr('Handleiding — SoundSausage'))

    def test_every_effect_dialog_translates_live_without_changing_parameters(self):
        classes=(NormalizeDialog,ChannelMixerDialog,DynamicsDialog,EnvelopeDialog,GraphicEqualizerDialog,ParametricEqualizerDialog,FilterDialog,DelayDialog,EchoDialog,ReverbDialog,StretchDialog,PitchShiftDialog,DistortionDialog,ConvolutionDialog,NoiseReductionDialog,ClickRemovalDialog)
        self.window.document.select_channels((1,));self.window.document.select(200,2400)
        for cls in classes:
            with self.subTest(dialog=cls.__name__):
                self.switch('en');dialog=cls(self.window.document,self.window,no_audio=True);self.dialogs.append(dialog)
                original=dialog.windowTitle()
                # Some effects need a profile/response before settings can validate.
                try:settings=dialog.settings()
                except ValueError:settings=None
                indices=[(x,x.currentIndex(),[x.itemData(i) for i in range(x.count())]) for x in dialog.findChildren(QComboBox)]
                for code in ('nl','de','fr','es','en'):
                    self.switch(code)
                    self.assertEqual(dialog.windowTitle(),tr(original))
                    self.assertEqual(dialog.preview_button.text(),tr('Preview'))
                    self.assertTrue(dialog.range_note.text().startswith(tr('Channels: Right (R). Applies to the selection, or the whole waveform if nothing is selected.\nPreview plays the first 8 seconds without changing the waveform.').split('\n')[0]))
                    if settings is not None:self.assertEqual(dialog.settings(),settings)
                    for combo,index,data in indices:
                        self.assertEqual(combo.currentIndex(),index)
                        self.assertEqual([combo.itemData(i) for i in range(combo.count())],data)
                dialog.reject();self.dialogs.remove(dialog);dialog.deleteLater()

    def test_qt_standard_buttons_and_dynamic_preview_caption_follow_language(self):
        dialog=NormalizeDialog(self.window.document,self.window,no_audio=True);self.dialogs.append(dialog)
        for code,cancel in {'nl':'Annuleren','en':'Cancel','de':'Abbrechen','fr':'Annuler','es':'Cancelar'}.items():
            self.switch(code)
            self.assertEqual(dialog.button_box.button(QDialogButtonBox.StandardButton.Cancel).text().replace('&',''),cancel)
            dialog.preview_state('Playing');self.assertEqual(dialog.preview_button.text(),tr('Stop Preview'))
            self.switch('en');self.assertEqual(dialog.preview_button.text(),'Stop Preview')
            dialog.preview_state('Stopped')

    def test_language_switch_preserves_audio_history_selection_and_audio_objects(self):
        window=self.window;doc=window.document
        doc.select_channels((1,));doc.select(100,800);doc.apply('invert');window.refresh()
        before=doc.read().copy();history=list(doc.undo_stack);selection=doc.selection
        player,recorder=window.player,window.recorder
        with patch.object(player,'stop') as stop,patch.object(recorder,'stop') as rec_stop:
            for code in LANGUAGES:
                self.switch(code)
                np.testing.assert_array_equal(doc.read(),before)
                self.assertEqual(doc.undo_stack,history);self.assertEqual(doc.selection,selection)
                self.assertEqual(doc.selected_channels,(1,));self.assertTrue(doc.dirty)
                self.assertIs(window.player,player);self.assertIs(window.recorder,recorder)
            stop.assert_not_called();rec_stop.assert_not_called()

    def test_user_names_and_foreign_device_plugin_values_are_not_translated(self):
        name='Normalize';self.window.document.path=Path('/tmp')/(name+'.wav');self.window.refresh()
        field=QLineEdit(name);combo=QComboBox();combo.addItem(Literal(name),'immutable-id')
        combo.currentIndexChanged.connect(lambda: self.fail('Retranslation changed the selected device'))
        for code in LANGUAGES:
            self.switch(code)
            self.assertEqual(field.text(),name);self.assertEqual(combo.currentText(),name)
            self.assertEqual(combo.currentData(),'immutable-id');self.assertIn(name+'.wav',self.window.windowTitle())
            self.assertEqual(tr(Literal('Channel Mixer')),'Channel Mixer')

    def test_about_localizes_description_and_keeps_brand_license_and_link(self):
        dialog=AboutDialog(self.window);self.dialogs.append(dialog)
        for code in LANGUAGES:
            self.switch(code);text=dialog.description.text()
            self.assertIn(tr('Gemaakt door'),text);self.assertIn('René Timmermans',text)
            self.assertIn('General Public License',text);self.assertIn('https://github.com/rene-timmermans/SoundSausage',text)
            self.assertIn('VST3',text)

    def test_dialogs_use_the_selected_language_and_preserve_file_filters(self):
        from PySide6.QtWidgets import QFileDialog as NativeFileDialog, QMessageBox as NativeMessageBox
        for code in ('nl','de','fr','es','en'):
            self.switch(code);seen=[]
            def inspect_file():
                for dialog in self.app.topLevelWidgets():
                    if isinstance(dialog,NativeFileDialog):
                        seen.append(dialog.windowTitle())
                        self.assertTrue(dialog.testOption(NativeFileDialog.Option.DontUseNativeDialog))
                        self.assertIn('*.wav',dialog.nameFilters()[0]);dialog.reject()
            QTimer.singleShot(0,inspect_file)
            QFileDialog.getOpenFileName(self.window,'Open WAV',self.folder.name,'Waveform audio (*.wav *.WAV);;All files (*)')
            self.assertEqual(seen,[tr('Open WAV')])
            def inspect_message():
                for dialog in self.app.topLevelWidgets():
                    if isinstance(dialog,NativeMessageBox):
                        seen.append(dialog.text());dialog.accept()
            QTimer.singleShot(0,inspect_message)
            QMessageBox.warning(self.window,'Recording','No recording input is available. Connect a microphone or audio interface and check the system\'s audio settings.')
            self.assertEqual(seen[-1],tr("No recording input is available. Connect a microphone or audio interface and check the system's audio settings."))

    def test_translated_menus_and_dialogs_render_with_the_desktop_palette(self):
        for code in LANGUAGES:
            self.switch(code);self.window.resize(1180,720);self.app.processEvents()
            bar=self.window.menuBar()
            self.assertLessEqual(max(bar.actionGeometry(a).right() for a in bar.actions()),bar.width())
            button=next(b for b in self.window.findChildren(QToolButton) if b.defaultAction() is self.window.actions['open'])
            self.assertTrue(button.property('primary'))
            self.assertFalse(self.window.grab().isNull())
            for text in ('Start Recording','Add effect tail after the selection','Normalize left / right equally'):
                label=QPushButton(text);label.show();self.app.processEvents()
                self.assertGreaterEqual(label.width(),label.fontMetrics().horizontalAdvance(tr(text)))
                label.close();label.deleteLater()

    def test_closed_windows_are_not_called_by_later_language_changes(self):
        other=MainWindow(no_audio=True)
        about=AboutDialog(other);manual=ManualDialog(other)
        other.close();other.deleteLater()
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
        self.app.processEvents()
        errors=io.StringIO()
        with contextlib.redirect_stderr(errors):
            self.switch('fr');self.switch('en')
        self.assertEqual(errors.getvalue(),'')

    def test_catalogues_are_complete_and_have_identical_placeholders(self):
        sys.path.insert(0,str(ROOT/'tools'))
        from build_translations import build
        self.assertEqual(build(),[])
        formatter=string.Formatter()
        fields=lambda s: sorted(field for _,field,_,_ in formatter.parse(s) if field is not None)
        for code in LANGUAGES:
            data=catalogue(code);self.assertEqual(set(data),set(catalogue('en')))
            self.assertGreater(len(data),1200)
            for source,target in data.items():
                self.assertEqual(fields(source),fields(target),(code,source))
                self.assertTrue(target.strip(),(code,source))
        for code in ('nl','de','fr','es'):
            self.switch(code)
            self.assertNotEqual(tr('Capture a profile with the same sample rate and channel count as this waveform.'),'Capture a profile with the same sample rate and channel count as this waveform.')
            self.assertEqual(tr('Selection Begin'),tr('Selection {0}').format(tr('Begin')))
