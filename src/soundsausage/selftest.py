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
from .icons import application_icon, mascot_icon
from .resample import resample
from .manual import ManualDialog


def run(window):
    original = np.array([[.25, -.5], [.5, .125], [-.25, .375]], np.float32)
    doc = Document(original, 8000, dsp=window.document.dsp)
    doc.apply("channel_mix", matrix=((0, 1), (1, 0)))
    np.testing.assert_array_equal(doc.read(), original[:, ::-1])
    doc.undo()
    doc.apply("dynamics", points=((-96, -96), (0, 0)))
    np.testing.assert_array_equal(doc.read(), original)
    doc.apply("envelope", points=((0, 1), (1, 1)))
    doc.apply("normalize", target=.5, remove_dc=True)
    assert np.isfinite(doc.read()).all()
    assert not application_icon().pixmap(32, 32).isNull()
    assert not mascot_icon().pixmap(24, 24).isNull()
    assert resample(np.zeros((441, 2), np.float32), 44100, 48000).shape == (480, 2)
    with tempfile.TemporaryDirectory(prefix="soundsausage-selftest-") as folder:
        path = Path(folder)
        write_wav(path / "test.wav", doc.read(), doc.sample_rate, "float32")
        np.testing.assert_array_equal(read_wav(path / "test.wav").samples, doc.read())
        from . import storage
        from .recovery import Recovery, restore, discard
        previous_cache=os.environ.get("SOUNDSAUSAGE_CACHE_DIR")
        os.environ["SOUNDSAUSAGE_CACHE_DIR"]=str(path/"work")
        manager=None
        try:
            mapped=storage.seal(storage.copy_array(doc.view(),force_disk=True))
            assert isinstance(mapped,np.memmap)
            disk_doc=Document(mapped,8000,dsp=doc.dsp)
            disk_doc.apply("invert")
            empty_session=Session(8000,1,dsp=doc.dsp)
            manager=Recovery();manager.checkpoint(disk_doc,empty_session)
            recovered,_,_,_=restore(manager.owner,dsp=doc.dsp)
            np.testing.assert_array_equal(recovered.view(),disk_doc.view())
        finally:
            if manager is not None:manager.close()
            if previous_cache is None:os.environ.pop("SOUNDSAUSAGE_CACHE_DIR",None)
            else:os.environ["SOUNDSAUSAGE_CACHE_DIR"]=previous_cache
        session = Session(8000, dsp=doc.dsp)
        session.import_audio([(doc.read(), 8000, "Selftest")])
        save_project(session, path / "test.celp")
        np.testing.assert_array_equal(load_project(path / "test.celp", dsp=doc.dsp).render(), session.render())
    for cls in (ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog):
        dialog = cls(doc, window, no_audio=True)
        try:
            dialog.show()
            assert not dialog.grab().isNull()
            assert np.isfinite(dialog.preview_samples()).all()
        finally:
            dialog.reject()
            dialog.deleteLater()
    manual = ManualDialog(window)
    try:
        assert "Channel Mixer" in manual.browser.toPlainText()
        assert "Audio Hardware" in manual.browser.toPlainText()
    finally:
        manual.close()
        manual.deleteLater()
    print(f"SoundSausage {__version__}: selftest OK (DSP, audio files, projects, disk buffers, recovery, icons, effects, manual)")


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
