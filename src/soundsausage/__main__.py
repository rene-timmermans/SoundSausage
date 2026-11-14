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
    parser.add_argument("waveform", nargs="?", help="WAV, MP3 or SoundSausage project to open")
    parser.add_argument("--multitrack", action="store_true", help="Start in multitrack view")
    parser.add_argument("--no-audio", action="store_true", help="Disable playback and recording for headless or restricted environments")
    parser.add_argument("--selftest", action="store_true", help="Check the installation without playing audio, then exit")
    parser.add_argument("--audio-selftest", action="store_true", help="Check the selected audio output with silence, then exit")
    parser.add_argument("--duplex-selftest", action="store_true", help="Check simultaneous silent playback and recording, then exit")
    parser.add_argument("--input-selftest", action="store_true", help="Check the selected input by briefly recording and discarding audio, then exit")
    parser.add_argument("--system-audio-selftest", action="store_true", help="Play two short tones and check recording of the default system output, then exit")
    parser.add_argument("--screenshot", type=Path, help="Render the window to a PNG and exit; does not start audio")
    args = parser.parse_args()
    if args.screenshot or args.selftest or args.audio_selftest or args.input_selftest or args.duplex_selftest or args.system_audio_selftest:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([sys.argv[0]])
    app.setApplicationName("SoundSausage")
    app.setDesktopFileName("soundsausage")
    app.setOrganizationName("SoundSausage")
    app.setWindowIcon(application_icon())
    app.setStyle("Fusion")
    install_theme(app)
    try:
        window = MainWindow(no_audio=args.no_audio or bool(args.screenshot) or args.selftest or args.audio_selftest or args.input_selftest or args.duplex_selftest or args.system_audio_selftest)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    if args.selftest or args.audio_selftest or args.input_selftest or args.duplex_selftest or args.system_audio_selftest:
        from .selftest import run, run_audio, run_input, run_duplex, run_system_audio
        try:
            if args.selftest:
                run(window)
            if args.audio_selftest:
                run_audio(window)
            if args.input_selftest:
                run_input(window)
            if args.duplex_selftest:
                run_duplex(window)
            if args.system_audio_selftest:
                run_system_audio(window)
            return 0
        except Exception as error:
            print(f"SoundSausage selftest failed: {error}", file=sys.stderr)
            return 1
        finally:
            window.document.mark_saved()
            window.session.mark_saved()
            window.close()
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
    window.enable_recovery()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
