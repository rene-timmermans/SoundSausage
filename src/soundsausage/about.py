"""About window with the same layout and information blocks as PixelPickle."""
import platform

import numpy
import PySide6
from PySide6.QtCore import Qt, qVersion
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox

from . import __version__
from .icons import mascot_icon
from .theme import colors


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Over SoundSausage")
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.mascot = QLabel()
        self.mascot.setObjectName("AboutMascot")
        self.mascot.setPixmap(mascot_icon().pixmap(96, 96))
        self.mascot.setAlignment(Qt.AlignmentFlag.AlignTop)
        top.addWidget(self.mascot)
        url = "https://github.com/rene-timmermans/SoundSausage"
        palette = colors()
        self.description = QLabel(
            f"<h2 style='margin:0'>SoundSausage {__version__}</h2>"
            "<p>Een vertrouwde audiobewerker voor golfvormen en meerdere sporen.</p>"
            "<p><b>Gemaakt door</b><br>René Timmermans<br>met Codex (OpenAI)</p>"
            "<p><b>Licentie</b><br>Vrije software onder de GNU General Public License, versie 3 of later.</p>"
            f"<p><b>Website</b><br><a style='color:{palette.icon.name()}' href='{url}'>{url}</a></p>"
            f"<p style='color:{palette.muted.name()}'>Gebouwd met Python {platform.python_version()}, Qt {qVersion()}, "
            f"PySide6 {PySide6.__version__}, NumPy {numpy.__version__}, C++ en libsamplerate.</p>")
        self.description.setWordWrap(True)
        self.description.setOpenExternalLinks(True)
        self.description.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.description.setMinimumWidth(420)
        top.addWidget(self.description, 1)
        layout.addLayout(top)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        box.accepted.connect(self.accept)
        layout.addWidget(box)
