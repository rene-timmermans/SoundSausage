"""Small installation smoke test: native DSP, file round trips, widgets and icons."""
from pathlib import Path
import os
import tempfile

import numpy as np

from . import __version__
from .audio import read_wav, write_wav
from .document import Document
from .session import Session
from .project import save_project, load_project
from .amplitude_ui import ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog
from .space_ui import DelayDialog, EchoDialog, ReverbDialog
from .special_ui import DistortionDialog, ConvolutionDialog
from .time_pitch_ui import StretchDialog, PitchShiftDialog
from .restoration_ui import NoiseReductionDialog, ClickRemovalDialog
from .restoration import learn_profile
from .filters_ui import GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog
from .icons import application_icon, mascot_icon
from .resample import resample
from .manual import ManualDialog
from .sample_ui import SampleDialog
from .calibration_ui import CalibrationDialog
from .recording_ui import RecordDialog


def run(window):
    original = np.array([[.25, -.5], [.5, .125], [-.25, .375]], np.float32)
    doc = Document(original, 8000, dsp=window.document.dsp)
    doc.set_sample(1, 1, -.25)
    changed = original.copy(); changed[1, 1] = -.25
    np.testing.assert_array_equal(doc.read(), changed)
    doc.undo(); np.testing.assert_array_equal(doc.read(), original)
    doc.redo(); np.testing.assert_array_equal(doc.read(), changed)
    doc.undo()
    doc.apply("channel_mix", matrix=((0, 1), (1, 0)))
    np.testing.assert_array_equal(doc.read(), original[:, ::-1])
    doc.undo()
    doc.select_channels((1,))
    doc.apply("invert")
    np.testing.assert_array_equal(doc.read()[:, 0], original[:, 0])
    np.testing.assert_array_equal(doc.read()[:, 1], -original[:, 1])
    doc.undo()
    assert doc.selected_channels == (1,)
    doc.select_channels()
    doc.apply("dynamics", points=((-96, -96), (0, 0)))
    np.testing.assert_array_equal(doc.read(), original)
    doc.apply("envelope", points=((0, 1), (1, 1)))
    doc.apply("normalize", target=.5, remove_dc=True)
    assert np.isfinite(doc.read()).all()
    assert not application_icon().pixmap(32, 32).isNull()
    assert not mascot_icon().pixmap(24, 24).isNull()
    from .plugins import Helper
    helper=Helper()
    try:assert helper.request(dict(op='host_info'))['ready']
    finally:helper.close()
    from .trackfx import effect
    live_session=Session(8000,1,dsp=doc.dsp)
    live_session.import_audio([(original,8000,'Track insert check')])
    live_session.configure_track(live_session.selected_track,effects=(effect('gain',dict(initial=.5)),))
    np.testing.assert_array_equal(live_session.render(),original*.5)
    assert resample(np.zeros((441, 2), np.float32), 44100, 48000).shape == (480, 2)
    with tempfile.TemporaryDirectory(prefix="soundsausage-selftest-") as folder:
        path = Path(folder)
        write_wav(path / "test.wav", doc.read(), doc.sample_rate, "float32")
        np.testing.assert_array_equal(read_wav(path / "test.wav").samples, doc.read())
        from .media import write_mp3,read_mp3
        mp3_samples=np.zeros((2400,2),np.float32)
        write_mp3(path/'test.mp3',mp3_samples,48000,'mp3_192')
        mp3=read_mp3(path/'test.mp3')
        assert mp3.sample_rate==48000 and mp3.samples.shape==mp3_samples.shape
        from . import storage
        from .recovery import Recovery, restore, discard
        from .capture import Take,recover_take
        previous_cache=os.environ.get("SOUNDSAUSAGE_CACHE_DIR")
        os.environ["SOUNDSAUSAGE_CACHE_DIR"]=str(path/"work")
        manager=None
        try:
            mapped=storage.seal(storage.copy_array(doc.view(),force_disk=True))
            assert isinstance(mapped,np.memmap)
            disk_doc=Document(mapped,8000,dsp=doc.dsp)
            disk_doc.select_channels((1,))
            disk_doc.apply("invert")
            disk_doc.set_sample(1, 1, .0625)
            empty_session=Session(8000,1,dsp=doc.dsp)
            manager=Recovery();manager.checkpoint(disk_doc,empty_session)
            recovered,_,_,_=restore(manager.owner,dsp=doc.dsp)
            np.testing.assert_array_equal(recovered.view(),disk_doc.view())
            assert recovered.selected_channels == (1,)
            take=Take(8000,2,"Selftest input")
            take.append(original);take.checkpoint();take.finish()
            np.testing.assert_array_equal(recover_take(take.owner).samples,original)
            take.discard()
        finally:
            if manager is not None:manager.close()
            if previous_cache is None:os.environ.pop("SOUNDSAUSAGE_CACHE_DIR",None)
            else:os.environ["SOUNDSAUSAGE_CACHE_DIR"]=previous_cache
        session = Session(8000, dsp=doc.dsp)
        session.import_audio([(doc.read(), 8000, "Selftest")])
        before = session.render().copy()
        session.punch_audio(np.array([[.0625, -.125]], np.float32), session.selected_track, 1)
        punched = session.render().copy()
        np.testing.assert_array_equal(punched[[0, 2]], before[[0, 2]])
        np.testing.assert_array_equal(punched[1], [.0625, -.125])
        session.undo(); np.testing.assert_array_equal(session.render(), before)
        session.redo(); np.testing.assert_array_equal(session.render(), punched)
        save_project(session, path / "test.celp")
        np.testing.assert_array_equal(load_project(path / "test.celp", dsp=doc.dsp).render(), session.render())
        from .synchronization import calibration_probe, measure_latency
        probe, markers = calibration_probe(8000)
        measured = measure_latency(np.vstack((np.zeros((80, 2), np.float32), probe)), markers, 8000, 0)
        assert abs(measured['offset_ms'] + 10) < .2
        if os.environ.get('SOUNDSAUSAGE_TEST_VST3'):
            from .plugins import scan_plugin, PluginProcess
            from PySide6.QtTest import QTest
            registry = os.environ.get('SOUNDSAUSAGE_PLUGIN_REGISTRY')
            os.environ['SOUNDSAUSAGE_PLUGIN_REGISTRY'] = str(path/'plugins.json')
            processor = None
            try:
                entry = scan_plugin(os.environ['SOUNDSAUSAGE_TEST_VST3'])[0]
                processor = PluginProcess(dict(plugin_id=entry['id'], name=entry['name'],
                    fingerprint=entry['fingerprint'], values={'0':.25}), 8000)
                processor.open_editor()
                for _ in range(100):
                    QTest.qWait(20); snapshot = processor.snapshot()
                    if snapshot['editor_size'] == [400, 220]: break
                assert snapshot['editor_size'] == [400, 220]
                assert snapshot['info']['parameters'][0]['value'] == .75
                processor.close_editor()
                assert processor.snapshot()['editor_size'] is None
            finally:
                if processor is not None: processor.close()
                if registry is None: os.environ.pop('SOUNDSAUSAGE_PLUGIN_REGISTRY', None)
                else: os.environ['SOUNDSAUSAGE_PLUGIN_REGISTRY'] = registry
    pitch_source = np.sin(2*np.pi*440*np.arange(8000)/8000).astype(np.float32)[:, None]*.1
    shifted = doc.dsp.process_blocks("pitch_shift", pitch_source, 8000, semitones=12)
    assert shifted.shape == pitch_source.shape and np.isfinite(shifted).all()
    window.noise_profile = learn_profile(np.random.default_rng(5).normal(0, .01, (2000, 2)).astype(np.float32), 8000)
    with tempfile.TemporaryDirectory(prefix="soundsausage-ir-check-") as response_folder:
        response_path = Path(response_folder)/"Response.wav"
        write_wav(response_path, np.array([[1], [.25]], np.float32), 8000, "float32")
        for cls in (DistortionDialog, ConvolutionDialog, StretchDialog, PitchShiftDialog, NoiseReductionDialog, ClickRemovalDialog, DelayDialog, EchoDialog, ReverbDialog, GraphicEqualizerDialog, ParametricEqualizerDialog, FilterDialog, ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog):
            dialog = cls(doc, window, no_audio=True)
            try:
                if isinstance(dialog, ConvolutionDialog): dialog.use_impulse(response_path)
                if isinstance(dialog, (DelayDialog, EchoDialog, ReverbDialog)):
                    dialog.keep_tail.setChecked(True)
                    dialog.tail.setValue(.1)
                dialog.show()
                assert not dialog.grab().isNull()
                assert np.isfinite(dialog.preview_samples()).all()
            finally:
                dialog.reject()
                dialog.deleteLater()
    from .i18n import LANGUAGES,language,install_language,tr,catalogue
    previous_language=language()
    manual=ManualDialog(window)
    try:
        for code in LANGUAGES:
            install_language().set_language(code,persist=False)
            assert len(manual.browser.toPlainText().split())>3000
            assert tr('Channel Mixer') in manual.browser.toPlainText()
            assert tr('Audio Hardware') in manual.browser.toPlainText()
            assert tr('Edit Sample') in manual.browser.toPlainText()
            assert tr('Start Calibration') in manual.browser.toPlainText()
            assert 'LADSPA' in manual.browser.toPlainText()
            for cls in (CalibrationDialog, RecordDialog):
                dialog = cls(window)
                try:
                    dialog.show()
                    assert not dialog.grab().isNull()
                finally:
                    dialog.reject(); dialog.deleteLater()
            sample_dialog = SampleDialog(doc, 1, 1, window)
            try:
                sample_dialog.show()
                assert not sample_dialog.grab().isNull()
                assert sample_dialog.sample_edit() == (1, 1, float(doc.view(1, 2)[0, 1]))
            finally:
                sample_dialog.reject(); sample_dialog.deleteLater()
            assert len(catalogue(code))>1200
            assert code=='en' or install_language().qt_translator is not None, f'Missing Qt translation: {code}'
    finally:
        install_language().set_language(previous_language,persist=False)
        manual.close();manual.deleteLater()
    print(f"SoundSausage {__version__}: selftest OK (DSP, audio files, MP3, sample editing, projects, disk buffers, recovery, recording files, icons, effects, track inserts, isolated VST3 host, manual)")


def run_audio(window):
    """Exercise the selected real/virtual output with silence; do not record audio."""
    from PySide6.QtCore import QEventLoop, QTimer
    loop, errors, positions = QEventLoop(), [], []
    player = window.player
    player.failed.connect(errors.append)
    player.position.connect(positions.append)
    player.state_changed.connect(lambda state: loop.quit() if state == "Stopped" else None)
    timeout = QTimer()
    timeout.setSingleShot(True)
    timeout.timeout.connect(loop.quit)
    try:
        player.play(np.zeros((11025, 2), np.float32), 44100)
        if player.state != "Stopped":
            timeout.start(7000)
            loop.exec()
        if errors or player.state != "Stopped" or not positions or positions[-1] != 11025:
            raise RuntimeError("; ".join(errors) or "Audio output did not finish within seven seconds.")
        print(f"SoundSausage {__version__}: audio selftest OK ({player.output_description}, {player.format.sampleRate()} Hz)")
    finally:
        timeout.stop()
        player.shutdown()


def run_input(window):
    """Explicit short input check; never enabled by the ordinary selftest."""
    from PySide6.QtCore import QEventLoop,QTimer
    recorder=window.recorder
    loop=QEventLoop();errors=[];takes=[]
    recorder.failed.connect(errors.append)
    recorder.failed.connect(lambda message:loop.quit())
    recorder.finished.connect(takes.append)
    recorder.finished.connect(lambda take:loop.quit())
    # This check does not attach a take to the editor or keep microphone data.
    recorder.finished.disconnect(window.recording_finished)
    recorder.failed.disconnect(window.recording_failed)
    previous_cache=os.environ.get("SOUNDSAUSAGE_CACHE_DIR")
    timeout=QTimer();timeout.setSingleShot(True);timeout.timeout.connect(loop.quit)
    folder=tempfile.TemporaryDirectory(prefix="soundsausage-input-check-")
    try:
        os.environ["SOUNDSAUSAGE_CACHE_DIR"]=folder.name
        ok=recorder.start(48000,2,limit_seconds=.25,skip_start_ms=50)
        if ok and recorder.active:
            timeout.start(7000);loop.exec()
        if errors or recorder.active or not takes or not takes[0].frames:
            raise RuntimeError("; ".join(errors) or "Recording input did not produce audio within seven seconds.")
        assert np.isfinite(takes[0].samples).all()
        print(f"SoundSausage {__version__}: input selftest OK ({takes[0].description}, {takes[0].rate} Hz, {takes[0].channels} channels)")
    finally:
        timeout.stop();recorder.stop(keep=False)
        for take in takes:take.discard()
        folder.cleanup()
        if previous_cache is None:os.environ.pop("SOUNDSAUSAGE_CACHE_DIR",None)
        else:os.environ["SOUNDSAUSAGE_CACHE_DIR"]=previous_cache


def run_duplex(window,rate=48000):
    """Explicit simultaneous virtual/device output and input test with silent backing."""
    from PySide6.QtCore import QEventLoop,QTimer
    original_session,original_mode=window.session,window.mode
    original_error=window.error
    errors=[];observed=[];loop=QEventLoop()
    window.error=lambda title,message:errors.append(str(message))
    timeout=QTimer();timeout.setSingleShot(True);timeout.timeout.connect(loop.quit)
    def observe():observed.append((window.player.state,window.recorder.state))
    def pause():
        if window.recorder.state=='Recording':window.toggle_pause();observe()
    def resume():
        if window.recorder.state=='Paused':window.toggle_pause();observe()
    def finished(state):
        if state=='Stopped' and window.recorder.take is None:loop.quit()
    window.recorder.state_changed.connect(finished)
    try:
        window.session=Session(rate,2,dsp=window.document.dsp)
        window.session.import_audio([(np.zeros((rate*2,2),np.float32),rate,'Silent backing')])
        window.session.selected_track=window.session.tracks[1].id;window.set_mode('multitrack')
        window.session.select(0,0)
        if not window.start_recording(target='multitrack',rate=rate,channels=2,accompaniment=True):
            raise RuntimeError('; '.join(errors) or 'Duplex capture could not start.')
        # Some backends deliver queued input immediately. Exercise pause before
        # allowing a duration limit or an event-loop delay to finish that take.
        observe();pause();QTimer.singleShot(100,resume)
        QTimer.singleShot(450,window.stop_recording);timeout.start(7000);loop.exec()
        if window.recorder.active:window.stop_recording()
        clips=window.session.tracks[1].clips
        if errors or not clips or ('Playing','Recording') not in observed or ('Paused','Paused') not in observed:
            raise RuntimeError('; '.join(errors) or f'Duplex playback/pause/capture failed: {observed}')
        assert window.player.state=='Stopped' and not window.recording_busy
        assert len(window.session.media[clips[0].media_id].samples)>rate//5
        print(f'SoundSausage {__version__}: duplex selftest OK ({rate} Hz, simultaneous output/input, linked pause, take kept)')
    finally:
        timeout.stop();window.recorder.state_changed.disconnect(finished)
        window.player.stop()
        if window.recorder.active:window.recorder.stop(keep=False)
        if window.recording_busy:window.end_recording_view()
        window.session.mark_saved();window.session=original_session;window.error=original_error
        window.multitrack.set_session(original_session);window.set_mode(original_mode)
