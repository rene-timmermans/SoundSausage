"""Create a standalone automation demo and optionally render real Qt previews."""
import argparse
import os
from pathlib import Path

import numpy as np

from soundsausage.audio import tone, write_wav
from soundsausage.project import save_project
from soundsausage.session import Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = root / "build"
    build.mkdir(exist_ok=True)
    rate, seconds = 44100, 6
    session = Session(rate, 2)
    volume = session.import_audio([(tone(seconds, rate, 1, 220, .20), rate, "Volume demonstration")],
                                  session.tracks[0].id, 0)[0]
    pan = session.import_audio([(tone(seconds, rate, 1, 440, .20), rate, "Left to right")],
                               session.tracks[1].id, seconds * rate)[0]
    session.set_envelope(volume, "volume", ((0, 0), (round(.7 * rate), 1), (round(1.6 * rate), .5),
        (round(2.5 * rate), 1.5), (round(3.5 * rate), .6), (5 * rate, 1), (seconds * rate - 1, 0)))
    session.set_envelope(pan, "pan", ((0, -1), (round(1.5 * rate), -1), (3 * rate, 0),
        (round(4.5 * rate), 1), (seconds * rate - 1, 1)))
    session.configure_track(session.tracks[0].id, name="Volume line")
    session.configure_track(session.tracks[1].id, name="Pan line")
    project = build / "demo-envelopes.celp"
    save_project(session, project)
    mix = build / "demo-envelopes-mix.wav"
    write_wav(mix, session.render(), rate, "float32")
    print(project)
    print(mix)
    if args.screenshots:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication
        from soundsausage.theme import install_theme
        from soundsausage.window import MainWindow
        from render_theme_previews import preview_palette
        app = QApplication([])
        app.setStyle("Fusion")
        install_theme(app)
        app.setPalette(preview_palette(app, True, "#36c5ac"))
        window = MainWindow()
        if not window.load_session_path(project):
            raise RuntimeError("Could not open the automation demo.")
        window.resize(1180, 720)
        window.show()
        for kind, clip in (("volume", volume), ("pan", pan)):
            window.session.choose_clip(clip)
            window.multitrack.set_envelope_mode(kind)
            window.refresh()
            app.processEvents()
            screenshot = build / f"demo-{kind}-line-v03.png"
            if not window.grab().save(str(screenshot)):
                raise RuntimeError(f"Could not save {screenshot}")
            print(screenshot)
        window.document.mark_saved()
        window.session.mark_saved()
        window.close()


if __name__ == "__main__":
    main()
