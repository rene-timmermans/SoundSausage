"""Rendered text must fit its paint boxes and translated dialog layouts."""
from collections import defaultdict
from contextlib import ExitStack
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import Qt,QPoint,QPointF,QRect,QRectF,QSettings,QTimer,QCoreApplication,QEvent
from PySide6.QtGui import QFont
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QLabel,QDialogButtonBox,QDialog,QWidget
from soundsausage.i18n import install_language,tr
from soundsausage.i18n_widgets import QPainter
from soundsausage.audio_devices import AudioDevices,AudioHardwareDialog
from soundsausage.document import Document
from soundsausage.window import MainWindow,AmplifyDialog
from soundsausage.amplitude_ui import ChannelMixerDialog,DynamicsDialog,EnvelopeDialog,NormalizeDialog
from soundsausage.filters_ui import GraphicEqualizerDialog,ParametricEqualizerDialog,FilterDialog
from soundsausage.space_ui import DelayDialog,EchoDialog,ReverbDialog
from soundsausage.restoration_ui import NoiseReductionDialog,ClickRemovalDialog
from soundsausage.time_pitch_ui import StretchDialog,PitchShiftDialog
from soundsausage.special_ui import DistortionDialog,ConvolutionDialog
from soundsausage.spectrum import SpectrumDialog
from soundsausage.about import AboutDialog
from soundsausage.manual import ManualDialog
from soundsausage.recording_ui import RecordDialog
from soundsausage.trackfx_ui import TrackEffectsDialog
from soundsausage.plugins_ui import PluginDialog
from soundsausage.sample_ui import SampleDialog
from soundsausage.calibration_ui import CalibrationDialog

EFFECTS=(AmplifyDialog,ChannelMixerDialog,DynamicsDialog,EnvelopeDialog,NormalizeDialog,
         GraphicEqualizerDialog,ParametricEqualizerDialog,FilterDialog,DelayDialog,EchoDialog,ReverbDialog,
         NoiseReductionDialog,ClickRemovalDialog,StretchDialog,PitchShiftDialog,DistortionDialog,ConvolutionDialog)
OTHERS=(AboutDialog,ManualDialog,AudioHardwareDialog,RecordDialog,TrackEffectsDialog,PluginDialog,SpectrumDialog,SampleDialog,CalibrationDialog)


def visible_label_errors(dialog):
    result=[]
    for label in dialog.findChildren(QLabel):
        if not label.isVisible() or not label.text():continue
        text=label.text()
        if '<' in text and '>' in text:continue
        if label.wordWrap():height=label.heightForWidth(label.width())
        else:
            height=label.fontMetrics().height()*len(text.splitlines())
            width=max(label.fontMetrics().horizontalAdvance(line.replace('&','')) for line in text.splitlines())
            if width>label.contentsRect().width()+2:result.append(('width',text,label.size().toTuple(),width))
        if height>label.height()+1:result.append(('height',text,label.size().toTuple(),height))
    return result


class TextLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.font=QFont(self.app.font());self.manager=install_language();self.manager.set_language('en',False)
        self.folder=tempfile.TemporaryDirectory();self.stack=ExitStack()
        self.stack.enter_context(patch.object(AudioDevices,'inputs',return_value=[]))
        self.stack.enter_context(patch.object(AudioDevices,'outputs',return_value=[]))
        self.stack.enter_context(patch('soundsausage.plugins_ui.read_registry',return_value={}))
        settings=QSettings(str(Path(self.folder.name)/'ui.ini'),QSettings.Format.IniFormat)
        self.data=np.column_stack((np.linspace(-.2,.2,8000),np.linspace(.1,-.1,8000))).astype(np.float32)
        self.window=MainWindow(Document(self.data,8000),no_audio=True,ui_settings=settings)
        self.window.show();self.app.processEvents();self.dialogs=[]

    def tearDown(self):
        for dialog in self.dialogs:dialog.reject();dialog.deleteLater()
        self.window.document.mark_saved();self.window.session.mark_saved()
        self.window.close();self.window.deleteLater()
        self.app.setFont(self.font);self.manager.set_language('en',False)
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);self.app.processEvents()
        self.stack.close();self.folder.cleanup()

    def settle(self):self.app.processEvents();QCoreApplication.sendPostedEvents(None,QEvent.Type.LayoutRequest);self.app.processEvents()

    def create(self,cls):
        w=self.window
        if cls in EFFECTS:dialog=cls(w.document,w,no_audio=True)
        elif cls is AudioHardwareDialog:dialog=cls(w.audio_devices,w)
        elif cls is TrackEffectsDialog:dialog=cls(w.multitrack,w.session.selected_track)
        elif cls is PluginDialog:dialog=cls(w.session,w)
        elif cls is SpectrumDialog:dialog=cls(self.data,8000,w)
        elif cls is SampleDialog:dialog=cls(w.document,0,0,w)
        else:dialog=cls(w)
        self.dialogs.append(dialog);return dialog

    def test_all_dialog_types_fit_labels_in_five_languages_and_three_fonts(self):
        for point in (9,11,14):
            self.app.setFont(QFont('DejaVu Sans',point));self.settle()
            for code in ('nl','en','de','fr','es'):
                self.manager.set_language(code,False)
                for cls in (*EFFECTS,*OTHERS):
                    with self.subTest(point=point,language=code,dialog=cls.__name__):
                        dialog=self.create(cls);dialog.show();self.settle()
                        self.assertFalse(dialog.grab().isNull())
                        self.assertEqual(visible_label_errors(dialog),[])
                        available=dialog.screen().availableGeometry()
                        self.assertLessEqual(dialog.size().width(),available.width())
                        self.assertLessEqual(dialog.size().height(),available.height())
                        for box in dialog.findChildren(QDialogButtonBox):
                            self.assertTrue(box.isVisible())
                            # Confirm/Cancel stay on screen even for scrollable forms.
                            pos=box.mapTo(dialog,QPointF(0,0).toPoint())
                            self.assertTrue(dialog.rect().contains(QRect(pos,box.size())))
                        dialog.reject();dialog.deleteLater();self.dialogs.remove(dialog)
                        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)

    def test_open_dialog_reflows_after_language_and_font_changes_without_parameter_changes(self):
        for cls in (DynamicsDialog,PitchShiftDialog,EchoDialog,ParametricEqualizerDialog,ConvolutionDialog):
            dialog=self.create(cls);dialog.show();self.settle()
            try:expected=dialog.settings()
            except ValueError:expected=None
            for point,code in ((11,'nl'),(14,'de'),(11,'fr'),(14,'es'),(9,'en')):
                self.app.setFont(QFont('DejaVu Sans',point));dialog.setFont(QFont('DejaVu Sans',point));self.manager.set_language(code,False);self.settle()
                self.assertEqual(visible_label_errors(dialog),[],(cls.__name__,point,code))
                if expected is not None:self.assertEqual(dialog.settings(),expected)
            dialog.reject()
        np.testing.assert_array_equal(self.window.document.read(),self.data)
        self.assertEqual(self.window.document.undo_stack,[])

    def test_recording_sync_and_punch_details_fit_with_an_available_device(self):
        from test_playback import Device
        from soundsausage.synchronization import save_calibration
        w=self.window;w.no_audio=False;w.set_mode('multitrack');w.session.select(8000,16000)
        with patch.object(w.audio_devices,'inputs',return_value=[Device('USB input',b'input')]), patch.object(w.audio_devices,'outputs',return_value=[Device()]):
            save_calibration(w.audio_devices,w.session.sample_rate,0,dict(offset_ms=-123.456,confidence=.99))
            for point in (9,11,14):
                self.app.setFont(QFont('DejaVu Sans',point))
                for code in ('nl','en','de','fr','es'):
                    self.manager.set_language(code,False)
                    dialog=self.create(RecordDialog);dialog.target.setCurrentIndex(dialog.target.findData('punch'))
                    dialog.show();self.settle()
                    self.assertEqual(visible_label_errors(dialog),[],(point,code))
                    dialog.reject();dialog.deleteLater();self.dialogs.remove(dialog)
        w.no_audio=True

    def test_painted_labels_are_inside_bounds_and_do_not_overlap(self):
        original=QPainter.drawText
        captures=defaultdict(list);errors=[]
        def record(painter,*args):
            device=painter.device()
            if len(args)==3 and isinstance(args[0],(QRect,QRectF)) and isinstance(device,QWidget) and args[-1]:
                area=QRectF(args[0]);text=tr(args[-1]);ink=painter.boundingRect(area,int(args[1]),text)
                clip=area.intersected(QRectF(device.rect()))
                if painter.hasClipping():clip=clip.intersected(painter.clipBoundingRect())
                if not clip.adjusted(-.6,-.6,.6,.6).contains(ink):errors.append((type(device).__name__,text,area.getRect(),ink.getRect()))
                captures[id(device)].append((text,ink))
            elif len(args)==2 and isinstance(args[0],QPointF) and isinstance(device,QWidget):
                ink=QRectF(painter.fontMetrics().tightBoundingRect(tr(args[-1]))).translated(args[0])
                if not QRectF(device.rect()).contains(ink):errors.append((type(device).__name__,args[-1],ink.getRect()))
                captures[id(device)].append((args[-1],ink))
            return original(painter,*args)
        with patch.object(QPainter,'drawText',record):
            for point in (9,11,14):
                self.app.setFont(QFont('DejaVu Sans',point));self.manager.set_language('nl',False);self.settle()
                for cls in (DynamicsDialog,EnvelopeDialog,GraphicEqualizerDialog,FilterDialog,SpectrumDialog):
                    dialog=self.create(cls);dialog.show();self.settle();captures.clear();errors.clear()
                    dialog.grab()
                    self.assertEqual(errors,[],(point,cls.__name__))
                    for labels in captures.values():
                        for index,(name,ink) in enumerate(labels):
                            for other,rect in labels[index+1:]:
                                intersection=ink.intersected(rect)
                                self.assertTrue(intersection.width()<1 or intersection.height()<1,(point,cls.__name__,name,other))
                    dialog.reject()
                self.window.transport.meter.setFont(QFont('DejaVu Sans',point))
                self.window.update_meters(np.array([[1.2,.25]],np.float32));self.settle();captures.clear();errors.clear()
                self.window.transport.meter.grab()
                self.assertEqual(errors,[])
                labels=next(iter(captures.values()))
                self.assertIn('L',[s for s,_ in labels]);self.assertIn('R',[s for s,_ in labels])
                for index,(name,ink) in enumerate(labels):
                    for other,rect in labels[index+1:]:
                        intersection=ink.intersected(rect)
                        self.assertTrue(intersection.width()<1 or intersection.height()<1,(point,name,other))

    def test_main_window_readouts_stay_inside_the_window_at_the_minimum_size(self):
        for point in (9,11,14):
            self.app.setFont(QFont('DejaVu Sans',point));self.manager.set_language('nl',False)
            other=MainWindow(Document(self.data,8000),no_audio=True,ui_settings=self.window.ui_settings)
            try:
                other.resize(850,540);other.show();self.settle()
                other.time_label.setFont(QFont('DejaVu Sans Mono',32))
                other.time_label.setText('23:59:59.999');self.settle()
                self.assertEqual(visible_label_errors(other),[])
                for field in (*other.fields.values(),*other.view_fields.values(),other.transport.meter):
                    origin=field.mapTo(other,QPointF(0,0).toPoint())
                    self.assertTrue(other.rect().contains(QRect(origin,field.size())),(point,type(field).__name__))
            finally:
                other.document.mark_saved();other.session.mark_saved();other.close();other.deleteLater();self.settle()

    def test_status_bar_menu_hides_information_and_remembers_the_choice(self):
        w=self.window;bar=w.status_line;action=w.actions['show_status'];menu=w.menus['options']
        self.assertTrue(bar.isVisible());before=w.centralWidget().height()
        menu.popup(w.mapToGlobal(w.rect().topLeft()+QPointF(20,20).toPoint()))
        self.settle();QTest.qWait(20)
        position=menu.actionGeometry(action).center()
        self.assertTrue(menu.rect().contains(position))
        # The QWindow overload delivers move events even when the offscreen
        # platform cannot generate them from QWidget's cursor repositioning.
        # A short pointer path also satisfies older QMenu's movement guard.
        surface=menu.windowHandle()
        for offset in range(8,0,-1):QTest.mouseMove(surface,position-QPoint(offset,0))
        self.assertIs(menu.actionAt(position),action)
        self.assertIs(menu.activeAction(),action)
        QTest.mouseClick(surface,Qt.MouseButton.LeftButton,pos=position);self.settle()
        self.assertFalse(action.isChecked());self.assertTrue(bar.isHidden())
        self.assertGreater(w.centralWidget().height(),before)
        self.assertFalse(w.ui_settings.value('ui/show_status_bar',True,type=bool))
        bar.showMessage('Playback',1000);w.refresh();self.manager.set_language('nl',False);w.set_mode('multitrack');self.settle()
        self.assertTrue(bar.isHidden());self.assertFalse(action.isChecked())
        other=MainWindow(no_audio=True,ui_settings=w.ui_settings)
        try:
            other.show();self.settle()
            self.assertTrue(other.status_line.isHidden());self.assertFalse(other.actions['show_status'].isChecked())
            other.actions['show_status'].trigger();self.settle()
            self.assertTrue(other.status_line.isVisible())
        finally:other.close();other.deleteLater()

    def test_scrollable_dialog_keeps_buttons_reachable_at_a_large_font(self):
        self.app.setFont(QFont('DejaVu Sans',24));self.manager.set_language('de',False)
        dialog=self.create(EchoDialog);expected=dialog.settings();dialog.show();self.settle()
        self.assertIsNotNone(dialog._content_scroll)
        scrollbar=dialog._content_scroll.verticalScrollBar()
        self.assertGreater(scrollbar.maximum(),0)
        for value in (0,scrollbar.maximum()):
            scrollbar.setValue(value);self.settle()
            self.assertEqual(dialog.settings(),expected)
            box=dialog.button_box
            origin=box.mapTo(dialog,QPointF(0,0).toPoint())
            self.assertTrue(dialog.rect().contains(QRect(origin,box.size())))
            self.assertTrue(box.button(QDialogButtonBox.StandardButton.Cancel).isVisible())

    def test_standard_file_message_and_progress_windows_fit_the_larger_font(self):
        from soundsausage.i18n_widgets import QFileDialog,QMessageBox,QProgressDialog
        self.app.setFont(QFont('DejaVu Sans',14));failures=[];seen=[]
        def inspect():
            for dialog in self.app.topLevelWidgets():
                if isinstance(dialog,QDialog) and dialog.isVisible():
                    self.settle();failures.extend(visible_label_errors(dialog));seen.append(dialog.windowTitle());dialog.reject()
        for code in ('nl','en','de','fr','es'):
            self.manager.set_language(code,False)
            QTimer.singleShot(0,inspect)
            QFileDialog.getOpenFileName(self.window,'Open a Waveform',self.folder.name,'Waveform audio (*.wav *.WAV);;All files (*)')
            QTimer.singleShot(0,inspect)
            QMessageBox.warning(self.window,'Recording',"No recording input is available. Connect a microphone or audio interface and check the system's audio settings.")
            progress=QProgressDialog('Verwerken','Annuleren',0,100,self.window)
            progress.setMinimumDuration(0);progress.setValue(50);progress.show();self.settle()
            failures.extend(visible_label_errors(progress));progress.close();progress.deleteLater()
        self.assertEqual(failures,[]);self.assertEqual(len(seen),10)

    def test_auxiliary_edit_windows_fit_the_larger_translated_font(self):
        self.app.setFont(QFont('DejaVu Sans',14));self.manager.set_language('de',False);w=self.window
        failures=[];seen=[]
        def inspect():
            for dialog in self.app.topLevelWidgets():
                if isinstance(dialog,QDialog) and dialog.isVisible():
                    self.settle();seen.append(dialog.windowTitle())
                    failures.extend(visible_label_errors(dialog));dialog.reject()
        for action in (w.new_document,w.new_session,w.select_range,w.convert_sample_rate,w.generate_tone,w.generate_silence):
            w.document.mark_saved();w.session.mark_saved()
            QTimer.singleShot(0,inspect);action();self.settle()
        w.insert_waveform();w.session.mark_saved()
        QTimer.singleShot(0,inspect);w.multitrack.properties();self.settle()
        clip=w.session.find_clip(w.session.selected_clip)[1]
        w.session.set_envelope(clip.id,'volume',((clip.source_start,1),(clip.source_end-1,1)))
        clip=w.session.find_clip(clip.id)[1]
        QTimer.singleShot(0,inspect);w.multitrack.timeline.edit_envelope_point(clip,'volume',0);self.settle()
        self.assertEqual(failures,[]);self.assertEqual(len(seen),8)
