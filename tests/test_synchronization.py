"""Clock drift, loopback confidence, profile identity and exact corrected lengths."""
import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication

from soundsausage.synchronization import DuplexClock,calibration_probe,measure_latency,save_calibration,read_calibration
from soundsausage.resample import resample_frames
from soundsausage.audio_devices import AudioDevices
from test_playback import Device,MemorySettings


class SynchronizationTests(unittest.TestCase):
    def test_different_rates_drift_jitter_pause_jumps_and_outliers(self):
        clock=DuplexClock(48000,44100);rng=np.random.default_rng(5);ratio=1/1.0004;anchor=123.4
        for i in range(7000):
            if i==3500:clock.new_segment()
            x=round(i*.1*48000*1.0004)
            y=anchor+ratio*x*44100/48000+(500 if i>=3500 else 0)+rng.normal(0,2)
            if i%13==0:y+=2200
            clock.observe(x,y)
        result=clock.result()
        self.assertTrue(result.reliable);self.assertTrue(result.drift_measured)
        self.assertAlmostEqual(result.ratio,ratio,delta=1e-7)
        self.assertAlmostEqual(result.anchor,anchor,delta=2)
        self.assertLessEqual(len(clock.points),4096)

    def test_short_and_unstable_clocks_keep_the_fallback_without_stretching(self):
        clock=DuplexClock(48000,48000)
        for i in range(10):clock.observe(i*480,i*480+12)
        self.assertEqual((clock.result(42).anchor,clock.result(42).ratio,clock.result(42).reliable),(42,1,False))
        clock=DuplexClock(48000,48000)
        for i in range(100):clock.observe(i*4800,i*4800*1.03)
        self.assertFalse(clock.result(42).reliable)

    def test_equal_clocks_do_not_add_unnecessary_sample_rate_conversion(self):
        clock=DuplexClock(44100,44100)
        for i in range(1000):clock.observe(i*441,50+i*441+(1 if i%2 else -1))
        result=clock.result();self.assertTrue(result.reliable)
        self.assertEqual(result.ratio,1);self.assertFalse(result.drift_measured)
        self.assertAlmostEqual(result.anchor,50,delta=.1)

    def test_short_apparent_drift_keeps_recorded_duration_unchanged(self):
        clock=DuplexClock(48000,48000)
        for i in range(400):clock.observe(i*480,300+i*480*1.002)
        result=clock.result();self.assertTrue(result.reliable)
        self.assertFalse(result.drift_measured);self.assertEqual(result.ratio,1)

    def test_loopback_measurement_finds_gain_inverted_noisy_stereo_input(self):
        rate=48000;probe,markers=calibration_probe(rate);delay=137
        rng=np.random.default_rng(2)
        captured=rng.normal(0,.0001,(len(probe)+rate//2,2)).astype(np.float32)
        captured[delay:delay+len(probe),1]-=probe[:,0]*.6
        original=captured.copy();result=measure_latency(captured,markers,rate,51.25)
        self.assertAlmostEqual(result['offset_ms'],-(delay+51.25)*1000/rate,delta=.02)
        self.assertGreater(result['confidence'],.99)
        np.testing.assert_array_equal(captured,original)

    def test_silence_noise_clipping_and_ambiguous_echoes_are_rejected(self):
        rate=8000;probe,markers=calibration_probe(rate)
        rng=np.random.default_rng(7)
        for signal in (np.zeros_like(probe),rng.normal(0,.01,probe.shape).astype(np.float32),probe*20):
            with self.assertRaises(ValueError):measure_latency(signal,markers,rate)
        echoes=np.zeros((len(probe)+rate,2),np.float32)
        echoes[:len(probe)]+=probe;echoes[rate//5:rate//5+len(probe)]+=probe
        with self.assertRaises(ValueError):measure_latency(echoes,markers,rate)

    def test_fractional_duration_conversion_is_frame_exact_and_block_independent(self):
        source=(np.sin(2*np.pi*440*np.arange(48000)/48000)*.2).astype(np.float32)[:,None]
        a=resample_frames(source,48017,48000,block_frames=257)
        b=resample_frames(source,48017,48000,block_frames=4096)
        self.assertEqual(a.shape,(48017,1));np.testing.assert_array_equal(a,b)
        self.assertTrue(np.isfinite(a).all());self.assertGreater(float(np.abs(a[-32:]).max()),.15)
        np.testing.assert_array_equal(resample_frames(source,len(source),48000),source)


class CalibrationProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_profiles_follow_actual_devices_rates_channels_and_buffer_settings(self):
        settings=MemorySettings();devices=AudioDevices(settings=settings)
        try:
            with patch.object(devices,'inputs',return_value=[Device('Input',b'input')]),patch.object(devices,'outputs',return_value=[Device()]):
                self.assertIsNone(read_calibration(devices,48000))
                save_calibration(devices,48000,0,dict(offset_ms=-23.75,confidence=.98))
                self.assertEqual(read_calibration(devices,48000)['offset_ms'],-23.75)
                self.assertIsNone(read_calibration(devices,48000,channels=2))
                self.assertIsNone(read_calibration(devices,44100))
                self.assertIsNone(read_calibration(devices,48000,1))
                devices.configure(devices.output_id,120,devices.input_id)
                self.assertIsNone(read_calibration(devices,48000))
        finally:devices.deleteLater()

    def test_profile_is_not_reused_for_a_different_native_input_layout(self):
        from PySide6.QtMultimedia import QAudioFormat
        device=Device('Mono preferred',b'input',supported={(48000,1,QAudioFormat.SampleFormat.Float)})
        device.isFormatSupported=lambda fmt:fmt.sampleRate()==48000 and fmt.channelCount() in (1,2) and fmt.sampleFormat()==QAudioFormat.SampleFormat.Float
        devices=AudioDevices(settings=MemorySettings())
        try:
            with patch.object(devices,'inputs',return_value=[device]),patch.object(devices,'outputs',return_value=[Device()]):
                save_calibration(devices,48000,0,dict(offset_ms=-10),channels=1)
                self.assertIsNotNone(read_calibration(devices,48000,channels=1))
                self.assertIsNone(read_calibration(devices,48000,channels=2))
        finally:devices.deleteLater()
