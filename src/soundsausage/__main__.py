import argparse
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from .window import MainWindow
from .theme import install_theme
from .icons import application_icon


def main():
    parser = argparse.ArgumentParser(description="SoundSausage waveform and multitrack editor")
    parser.add_argument("waveform", nargs="?", help="WAV or .celp project to open")
    parser.add_argument("--multitrack", action="store_true", help="Start in multitrack view")
    parser.add_argument("--no-audio", action="store_true", help="Disable playback for headless or restricted environments")
    parser.add_argument("--screenshot", type=Path, help="Render the window to a PNG and exit; does not start audio")
    args = parser.parse_args()
    if args.screenshot:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([sys.argv[0]])
    app.setApplicationName("SoundSausage")
    app.setOrganizationName("SoundSausage")
    app.setWindowIcon(application_icon())
    app.setStyle("Fusion")
    install_theme(app)
    try:
        window = MainWindow(no_audio=args.no_audio or bool(args.screenshot))
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    if args.waveform and not window.load_path(args.waveform):
        return 1
    if args.multitrack:
        window.set_mode("multitrack")
    if not args.screenshot and app.platformName() != "offscreen" and app.primaryScreen():
        area = app.primaryScreen().availableGeometry()
        window.resize(min(1180, max(850, area.width() - 40)), min(720, max(540, area.height() - 50)))
    window.show()
    if args.screenshot:
        app.processEvents()
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        if not window.grab().save(str(args.screenshot)):
            raise RuntimeError("Could not save the screenshot.")
        window.document.mark_saved()
        window.session.mark_saved()
        window.close()
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
