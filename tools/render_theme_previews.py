"""Render real Qt windows with simulated desktop palettes; no desktop settings change."""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from soundsausage.theme import install_theme
from soundsausage.window import MainWindow


def preview_palette(app, dark, accent):
    palette = app.style().standardPalette()
    for role, value in {
        "Window": "#252a30" if dark else "#f0f1f3",
        "WindowText": "#ecf0f4" if dark else "#20252b",
        "Button": "#343b43" if dark else "#f7f8fa",
        "ButtonText": "#ecf0f4" if dark else "#20252b",
        "Base": "#171c22" if dark else "#ffffff",
        "Text": "#ecf0f4" if dark else "#20252b",
        "Highlight": accent, "Accent": accent, "HighlightedText": "#ffffff",
    }.items():
        palette.setColor(getattr(QPalette.ColorRole, role), QColor(value))
    return palette


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/theme-previews"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    app.setStyle("Fusion")
    install_theme(app)
    root = Path(__file__).resolve().parents[1]
    records = []
    for name, dark, accent in (("dark-teal", True, "#36c5ac"), ("light-purple", False, "#794bc4")):
        app.setPalette(preview_palette(app, dark, accent))
        for state, source in (("empty", None), ("waveform", root / "build/demo.wav"),
                              ("multitrack", root / "reference/vm-session-test/05-pan.ses")):
            window = MainWindow()
            if source and not window.load_path(source):
                raise RuntimeError(f"Could not load {source}")
            if state == "waveform":
                window.document.select(window.document.sample_rate, window.document.sample_rate * 2)
                window.document.apply("invert")
                window.refresh()
            elif state == "multitrack":
                window.session.choose_clip(window.session.tracks[1].clips[0].id)
                window.refresh()
            window.resize(1180, 720)
            window.show()
            app.processEvents()
            path = args.out / f"{name}-{state}.png"
            if not window.grab().save(str(path)):
                raise RuntimeError(f"Could not save {path}")
            records.append(dict(path=str(path), simulated_palette=name, accent=accent,
                                size=[window.width(), window.height()], state=state))
            window.document.mark_saved()
            window.session.mark_saved()
            window.close()
            window.deleteLater()
            app.processEvents()
    (args.out / "previews.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
