# Kanaalselectie en zoomen — 0.14.0

Tweeëntwintig nieuwe model- en Qt-controles toetsen slepen in één kanaal,
slepen over beide kanalen, kanaalkeuze, menu en sneltoetsen, selectie-export
naar mono, luistervoorbeelden, opnamevergrendeling, Undo/Redo en herstel.
De bestaande layoutcontroles blijven de twee compacte werkbalkrijen en de
ruimte voor audio bij verschillende venstergroottes bewaken.

De modelcontroles vergelijken het onbewerkte kanaal sample voor sample.
Ze omvatten Amplitude, EQ/filters, delay/echo/galm, restauratie, toonhoogte,
vervorming en een stereorespons bij convolutie. Channel Mixer gebruikt beide
ingangen en schrijft alleen de gekozen uitgang. Normalize analyseert alleen
het gekozen kanaal. Ook F2, annuleren, metadata, schijfopslag en oudere
herstelkopieën worden gecontroleerd. Duurwijzigingen op één stereokanaal
worden geweigerd voordat het document verandert.

De rendercontrole gebruikt een oplopend signaal bij 0,5 tot 16 samples per
schermkolom, inclusief de overgang van samples naar min/max-contouren.
Ze zoekt naar onbedoelde lege schermkolommen. Dit toetst de gemelde
onderbrekingen bij tussenliggende zoomniveaus. Clipweergave gebruikt dezelfde
verbonden contour. De geluidsdata verandert hierbij niet.

Alle 84 functie-iconen worden op 16, 24 en 48 pixels gecontroleerd op zichtbare
pixels en verschillende beelden, inclusief Zoom Full en Zoom to Selection.
Kanaalselectie en het Amplitude-menu zijn daarnaast als Qt-beelden bekeken.
De gewone installatie-selftest controleert nu ook het exact behouden kanaal
en herstel van de kanaalkeuze. Native DSP-ABI blijft 7; er zijn geen nieuwe
afhankelijkheden.

De volledige lokale suite doorstaat 344 controles; vier tests die een echte
audiobackend vereisen worden lokaal overgeslagen. De 22 nieuwe kanaal-/zoomtests,
de vijf bestaande layouttests en de gewone installatie-selftest slagen.
De distributiebouw doorstaat alle 344 controles in Debian, Fedora en Arch,
inclusief de echte virtuele audiobackendtests. De geïnstalleerde pakketten
doorstaan gewone, afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling.
De geverifieerde logs bevatten geen callback- of bufferfouten. Bewijs:
[distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43009152892).
[Release 0.14.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.14.0)
bevat de geteste pakketten, broncode en checksums.
