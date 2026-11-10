"""Render the actual desktop layout, including native Qt menus, offscreen."""
import argparse
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication

from soundsausage.theme import install_theme
from soundsausage.window import MainWindow
from render_theme_previews import preview_palette


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/layout-previews"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    app = QApplication([])
    app.setStyle("Fusion")
    install_theme(app)
    for name, dark, accent in (("dark", True, "#36c5ac"), ("light", False, "#794bc4")):
        app.setPalette(preview_palette(app, dark, accent))
        for state, source in (("empty", None), ("waveform", root / "build/demo.wav"),
                              ("multitrack", root / "examples/demo-envelopes.celp"),
                              ("pan-line", root / "examples/demo-envelopes.celp")):
            window = MainWindow()
            if source and not window.load_path(source):
                raise RuntimeError(f"Could not open {source}")
            if state == "waveform":
                window.document.select(44100, 88200)
                window.refresh()
            elif state in ("multitrack", "pan-line"):
                index = 1 if state == "pan-line" else 0
                window.session.choose_clip(window.session.tracks[index].clips[0].id)
                window.multitrack.set_envelope_mode("pan" if state == "pan-line" else "volume")
                window.refresh()
            window.resize(1180, 720)
            window.show()
            app.processEvents()
            path = args.out / f"{name}-{state}.png"
            if not window.grab().save(str(path)):
                raise RuntimeError(f"Could not save {path}")
            print(path)
            if state == "empty":
                top, amplitude = window.menus["transform"], window.menus["amplitude"]
                action = top.menuAction()
                position = window.menuBar().actionGeometry(action).bottomLeft()
                top.popup(window.menuBar().mapToGlobal(position + QPoint(0, 1)))
                top.setActiveAction(amplitude.menuAction())
                app.processEvents()
                item = top.actionGeometry(amplitude.menuAction())
                amplitude.popup(top.mapToGlobal(item.topRight() + QPoint(1, 0)))
                app.processEvents()
                # Menus are native top-level widgets and are not part of grab().
                # Composite their actual Qt renders at their real popup positions.
                image = window.grab()
                painter = QPainter(image)
                for popup in (top, amplitude):
                    painter.drawPixmap(window.mapFromGlobal(popup.pos()), popup.grab())
                painter.end()
                menu_path = args.out / f"{name}-amplitude-menu.png"
                if not image.save(str(menu_path)):
                    raise RuntimeError(f"Could not save {menu_path}")
                print(menu_path)
                amplitude.close()
                top.close()
            window.document.mark_saved()
            window.session.mark_saved()
            window.close()
            window.deleteLater()
            app.processEvents()


if __name__ == "__main__":
    main()
