"""Small installation smoke test: native DSP, file round trips, widgets and icons."""
from pathlib import Path
import shutil
import tempfile

import numpy as np

from . import __version__
from .audio import read_wav, write_wav
from .document import Document
from .session import Session
from .project import save_project, load_project
from .amplitude_ui import ChannelMixerDialog, DynamicsDialog, EnvelopeDialog, NormalizeDialog
from .icons import application_icon, mascot_icon


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
    assert shutil.which("ffplay"), "ffplay is missing"
    with tempfile.TemporaryDirectory(prefix="soundsausage-selftest-") as folder:
        path = Path(folder)
        write_wav(path / "test.wav", doc.read(), doc.sample_rate, "float32")
        np.testing.assert_array_equal(read_wav(path / "test.wav").samples, doc.read())
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
    print(f"SoundSausage {__version__}: selftest OK (DSP, WAV, CELP, icons, amplitude dialogs)")
