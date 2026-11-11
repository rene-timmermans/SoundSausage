"""Bounded input, complete frames, device loss and durable take lifetime."""
import gc
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QObject,Signal
from PySide6.QtMultimedia import QAudioFormat
from PySide6.QtWidgets import QApplication

from soundsausage.audio import AudioError
from soundsausage.audio_devices import AudioDevices,AudioHardwareDialog
from soundsausage.capture import Recorder,Take,input_format,decode_input,recover_take
from soundsausage.playback import QtAudio
from test_playback import Device,MemorySettings

ROOT=Path(__file__).resolve().parents[1]


class Source(QObject):
    stateChanged=Signal(object)
    readyRead=Signal()
    def __init__(self,device,fmt,parent):
        super().__init__(parent)
        self.fmt=fmt;self.pending=bytearray();self._state=QtAudio.State.StoppedState
        self._error=QtAudio.Error.NoError;self.limit=65536;self.reads=[]
    def setBufferSize(self,count):self.capacity=count
    def error(self):return self._error
    def state(self):return self._state
    def transition(self,state):self._state=state;self.stateChanged.emit(state)
    def start(self):self.transition(QtAudio.State.IdleState);return self
    def bytesAvailable(self):return len(self.pending)
    def read(self,count):
        self.reads.append(count);size=min(len(self.pending),count,self.limit)
        raw=bytes(self.pending[:size]);del self.pending[:size];return raw
    def push(self,raw):self.pending.extend(raw);self.transition(QtAudio.State.ActiveState);self.readyRead.emit()
    def suspend(self):self.transition(QtAudio.State.SuspendedState)
    def resume(self):self.transition(QtAudio.State.ActiveState)
    def stop(self):self.pending.clear();self.transition(QtAudio.State.StoppedState)


class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build')
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':self.folder.name});self.env.start()
        self.devices=AudioDevices(settings=MemorySettings());self.inputs=[Device('USB microphone',b'usb')]
        self.query=patch.object(self.devices,'inputs',side_effect=lambda:self.inputs);self.query.start()
        self.outputs=patch.object(self.devices,'outputs',return_value=[]);self.outputs.start()
        self.recorder=Recorder(devices=self.devices,source_factory=Source)
        self.takes=[];self.errors=[];self.blocks=[]
        self.recorder.finished.connect(self.takes.append);self.recorder.failed.connect(self.errors.append)
        self.recorder.samples.connect(lambda data,frames:self.blocks.append((data.copy(),frames)))
    def tearDown(self):
        self.recorder.stop(keep=False)
        for take in self.takes:take.discard()
        self.recorder.deleteLater();self.devices.deleteLater();self.app.processEvents()
        self.outputs.stop();self.query.stop();self.env.stop();gc.collect();self.folder.cleanup()

    def test_no_input_is_queried_or_opened_at_startup(self):
        self.recorder._source_changed()
        self.devices.inputs.assert_not_called();self.assertEqual(self.recorder.state,'Stopped')

    def test_partial_reads_join_exact_frames_and_stop_preserves_every_sample(self):
        self.assertTrue(self.recorder.start(48000,2))
        source=self.recorder.source;source.limit=7
        data=np.arange(80,dtype=np.float32).reshape(40,2)/100
        source.push(data.tobytes()[:13]);source.push(data.tobytes()[13:])
        self.recorder.stop()
        self.assertEqual(self.recorder.state,'Stopped');self.assertFalse(self.errors)
        self.assertEqual(len(self.takes),1)
        np.testing.assert_array_equal(self.takes[0].samples,data)
        self.assertLessEqual(max(source.reads),65536)
        self.assertEqual(self.blocks[-1][1],len(data))

    def test_qt68_input_device_may_report_zero_while_source_has_bytes(self):
        class ReadDevice(QObject):
            readyRead=Signal()
            def __init__(self,source):super().__init__(source);self.source=source
            def bytesAvailable(self):return 0
            def read(self,count):return self.source.read(count)
        class SeparateSource(Source):
            def start(self):
                self.proxy=ReadDevice(self);self.transition(QtAudio.State.IdleState);return self.proxy
            def push(self,raw):
                self.pending.extend(raw);self.transition(QtAudio.State.ActiveState);self.proxy.readyRead.emit()
        self.recorder._source_factory=SeparateSource
        self.recorder.start(48000,2)
        self.recorder.source.push(np.full((80,2),.25,np.float32).tobytes())
        self.assertEqual(self.recorder.take.frames,80)
        self.recorder.stop();np.testing.assert_array_equal(self.takes[0].samples,.25)

    def test_pause_clock_freezes_and_resume_preserves_order(self):
        self.recorder.start(48000,1)
        self.recorder.source.push(np.tile([.2,.8],(40,1)).astype(np.float32).tobytes())
        self.recorder.toggle_pause();self.assertEqual(self.recorder.state,'Paused')
        frames=self.recorder.take.frames
        self.recorder._drain();self.assertEqual(self.recorder.take.frames,frames)
        self.recorder.toggle_pause();self.assertEqual(self.recorder.state,'Recording')
        self.recorder.source.push(np.tile([.3,.9],(20,1)).astype(np.float32).tobytes())
        self.recorder.stop()
        np.testing.assert_allclose(self.takes[0].samples[:,0],[.2]*40+[.3]*20)

    def test_cancel_discards_only_the_take_and_a_stale_event_cannot_stop_a_new_take(self):
        self.recorder.start(48000,2);old=self.recorder.source
        old.push(np.ones((20,2),np.float32).tobytes());path=self.recorder.take.path
        self.recorder.stop(keep=False)
        self.assertFalse(path.exists());self.assertFalse(self.takes)
        self.recorder.start(48000,2)
        old.transition(QtAudio.State.StoppedState)
        self.assertEqual(self.recorder.state,'Recording');self.assertFalse(self.errors)

    def test_missing_chosen_device_and_hot_unplug_do_not_switch_microphones(self):
        self.devices.input_id=b'usb'.hex()
        self.inputs=[];self.assertFalse(self.recorder.start(48000,2));self.assertIn('No recording input',self.errors[-1])
        self.inputs=[Device('Another microphone',b'other')]
        self.assertFalse(self.recorder.start(48000,2));self.assertIn('selected recording input',self.errors[-1])
        self.inputs=[Device('USB microphone',b'usb')]
        self.recorder.start(48000,2);self.recorder.source.push(np.ones((20,2),np.float32).tobytes())
        self.inputs=[Device('Another microphone',b'other')];self.devices.inputs_changed.emit()
        self.assertEqual(self.recorder.state,'Stopped');self.assertIn('disconnected',self.errors[-1])
        np.testing.assert_array_equal(self.takes[-1].samples,1)

    def test_integer_format_fallback_and_channel_selection(self):
        self.inputs=[Device(supported={(44100,2,QAudioFormat.SampleFormat.Int16)})]
        self.recorder.start(48000,1,first_channel=1)
        self.assertEqual(self.recorder.format.sampleRate(),44100)
        self.recorder.source.push(np.array([[-32768,16384],[32767,-16384]],np.int16).tobytes())
        self.recorder.stop();np.testing.assert_array_equal(self.takes[0].samples[:,0],[.5,-.5])

    def test_unsigned_and_signed_32bit_input_and_native_mono_duplication(self):
        fmt=QAudioFormat();fmt.setSampleRate(48000);fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.UInt8)
        np.testing.assert_array_equal(decode_input(bytes((0,128,192)),fmt,2),[[-1,-1],[0,0],[.5,.5]])
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int32);fmt.setChannelCount(2)
        raw=np.array([[-2147483648,1073741824],[0,-1073741824]],np.int32).tobytes()
        np.testing.assert_array_equal(decode_input(raw,fmt,2),[[-1,.5],[0,-.5]])

    def test_nonfinite_input_stops_without_losing_preceding_complete_blocks(self):
        self.recorder.start(48000,2)
        self.recorder.source.push(np.full((10,2),.25,np.float32).tobytes())
        self.recorder.source.push(np.array([[np.nan,1]],np.float32).tobytes())
        self.assertEqual(self.recorder.state,'Stopped');self.assertTrue(self.errors)
        np.testing.assert_array_equal(self.takes[0].samples,.25)

    def test_disk_write_error_retains_the_preceding_take(self):
        self.recorder.start(48000,2)
        self.recorder.source.push(np.full((10,2),.25,np.float32).tobytes())
        with patch.object(self.recorder.take,'append',side_effect=OSError('disk full')):
            self.recorder.source.push(np.ones((10,2),np.float32).tobytes())
        self.assertEqual(self.recorder.state,'Stopped');self.assertIn('disk full',self.errors[-1])
        np.testing.assert_array_equal(self.takes[0].samples,.25)

    def test_duration_limit_stops_at_an_exact_complete_frame(self):
        self.recorder.start(48000,2,limit_seconds=.001)
        self.recorder.source.push(np.ones((100,2),np.float32).tobytes());self.app.processEvents()
        self.assertEqual(self.recorder.state,'Stopped');self.assertEqual(self.takes[0].frames,48)

    def test_start_skip_and_fade_are_independent_of_partial_reads(self):
        data=np.arange(2000,dtype=np.float32).reshape(1000,2)/2000
        expected=data[480:].copy()
        expected[:240]*=(np.arange(240,dtype=np.float32)/239)[:,None]
        for read_limit in (7,65536):
            with self.subTest(read_limit=read_limit):
                self.assertTrue(self.recorder.start(48000,2,skip_start_ms=10))
                source=self.recorder.source;source.limit=read_limit
                source.push(data.tobytes()[:13]);source.push(data.tobytes()[13:])
                self.recorder.stop()
                self.assertEqual(self.recorder.skipped_frames,480)
                self.assertEqual(self.takes[-1].frames,520)
                np.testing.assert_array_equal(self.takes[-1].samples,expected)
        self.assertFalse(self.errors)

    def test_start_skip_uses_device_rate_and_is_not_repeated_after_pause(self):
        self.inputs=[Device(supported={(44100,2,QAudioFormat.SampleFormat.Int16)})]
        self.assertTrue(self.recorder.start(48000,1,first_channel=1,skip_start_ms=1))
        self.recorder.source.push(np.tile([8192,16384],(60,1)).astype(np.int16).tobytes())
        self.recorder.toggle_pause();self.recorder.toggle_pause()
        self.recorder.source.push(np.tile([8192,16384],(300,1)).astype(np.int16).tobytes())
        self.recorder.stop()
        expected=np.full((316,1),.5,np.float32)
        expected[:220]*=(np.arange(220,dtype=np.float32)/219)[:,None]
        self.assertEqual(self.takes[-1].rate,44100)
        self.assertEqual(self.recorder.skipped_frames,44)
        np.testing.assert_array_equal(self.takes[-1].samples,expected)
        self.assertFalse(self.errors)

    def test_start_skip_is_excluded_from_duration_and_an_empty_take_is_discarded(self):
        self.recorder.start(48000,2,limit_seconds=.001,skip_start_ms=2)
        self.recorder.source.push(np.ones((100,2),np.float32).tobytes())
        self.assertEqual(self.recorder.take.frames,4)
        self.assertEqual(self.recorder.state,'Recording')
        self.recorder.source.push(np.ones((100,2),np.float32).tobytes());self.app.processEvents()
        self.assertEqual(self.recorder.state,'Stopped');self.assertEqual(self.takes[-1].frames,48)
        count=len(self.takes)
        self.recorder.start(48000,2,skip_start_ms=50);path=self.recorder.take.path
        self.recorder.source.push(np.ones((100,2),np.float32).tobytes());self.recorder.stop()
        self.assertEqual(len(self.takes),count);self.assertFalse(path.exists());self.assertFalse(self.errors)

    def test_invalid_start_skip_never_opens_the_input(self):
        with patch.object(self.devices,'input') as input_device:
            for skip in (-1,501,float('nan'),float('inf')):
                self.assertFalse(self.recorder.start(48000,2,skip_start_ms=skip))
                self.assertEqual(self.recorder.state,'Stopped')
            input_device.assert_not_called()

    def test_input_preferences_cancel_and_hotplug(self):
        self.devices.configure('',100,b'usb'.hex())
        dialog=AudioHardwareDialog(self.devices)
        self.assertEqual(dialog.input.currentData(),b'usb'.hex())
        dialog.input.setCurrentIndex(0);dialog.reject()
        self.assertEqual(self.devices.input_id,b'usb'.hex())
        self.inputs=[];dialog=AudioHardwareDialog(self.devices)
        self.assertIn('disconnected',dialog.input.currentText())
        self.inputs=[Device('Webcam',b'webcam')];self.devices.inputs_changed.emit()
        dialog.input.setCurrentIndex(1);dialog.accept()
        restored=AudioDevices(settings=self.devices.settings)
        self.assertEqual(restored.input_id,b'webcam'.hex());restored.deleteLater()


if __name__=='__main__':unittest.main()
