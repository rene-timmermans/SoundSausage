"""About window with the same layout and information blocks as PixelPickle."""
import platform

import numpy
import PySide6
from PySide6.QtCore import Qt, qVersion
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from .i18n_widgets import QDialogButtonBox
from .i18n_widgets import QDialog, QLabel

from . import __version__
from .icons import mascot_icon
from .theme import colors
from .i18n import tr, Literal, install_language


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
        self.description = QLabel()
        self.reload_text()
        install_language().changed.connect(self.reload_text)
        self.description.setWordWrap(True)
        self.description.setOpenExternalLinks(True)
        self.description.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.description.setMinimumWidth(420)
        top.addWidget(self.description, 1)
        layout.addLayout(top)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        box.accepted.connect(self.accept)
        layout.addWidget(box)

    def reload_text(self, *_):
        url = "https://github.com/rene-timmermans/SoundSausage"
        c = colors()
        description = tr("Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.")
        author, credit = tr("Gemaakt door"), tr("met Codex (OpenAI)")
        license_title = tr("Licentie")
        license_text = tr("Vrije software onder de GNU General Public License, versie 3 of later.")
        components = tr("Gebouwd met Python {0}, Qt {1}, PySide6 {2}, NumPy {3}, C++, libsamplerate, Rubber Band en de VST3-interfaces (MIT).").format(platform.python_version(), qVersion(), PySide6.__version__, numpy.__version__)
        trademark = tr("VST is een handelsmerk van Steinberg Media Technologies GmbH.")
        self.description.setText(Literal(
            f"<h2 style='margin:0'>SoundSausage {__version__}</h2><p>{description}</p>"
            f"<p><b>{author}</b><br>René Timmermans<br>{credit}</p>"
            f"<p><b>{license_title}</b><br>{license_text}</p>"
            f"<p><b>Website</b><br><a style='color:{c.icon.name()}' href='{url}'>{url}</a></p>"
            f"<p style='color:{c.muted.name()}'>{components}</p><p>{trademark}</p>"))
