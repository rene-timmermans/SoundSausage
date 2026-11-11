# Delay, echo en galm — 0.10.0

De 26 nieuwe DSP- en Qt-controles toetsen:

- Precieze posities en niveaus van de eerste vertraging, onafhankelijke tijden
  per kanaal en geometrisch afnemende echoherhalingen.
- Stereopingpong zonder kanaalvolgordefout, mono, nulfeedback en de eerste
  samples van de eenpolige demping in het feedbackpad.
- Galmvoorvertraging als exacte verschuiving van alleen het effect, spreiding
  tussen stereokanalen en identieke galmkanalen bij breedte nul.
- Een energievervalmeting met regressie tussen −5 en −35 dB. Zonder demping
  ligt de daaruit afgeleide RT60 binnen 12% van 0,5, 1,5 en 3 seconden.
- Minder hoogfrequente energie in de late galm bij hogere demping, en langere
  afstand tot de eerste reflectie bij een grotere ruimte.
- Bitgelijke verwerking bij blokgroottes 1, 127 en grote blokken; Preview is
  hetzelfde prefix, ook wanneer die midden in een uitklank eindigt.
- Uitklank als ingevoegde tijd, behoud van cuepunten in de selectie,
  verschuiven van latere cuepunten, Undo/Redo/F2 en herstel van instellingen.
- WAV- en projectopslag, heropenen en herstel met identieke effectaudio.
- Een bewerkkopie terugplaatsen als verlengde clip, behoud van volgende
  clipposities en sessie-Undo.
- Ongeldige instellingen, float32-overflow en annuleren zonder gedeeltelijke
  wijziging; schijfopslag voor grote uitvoer en begrensde effectstaat.
- Echte dialogen, presets, Reset, kanaalkeuze, preview-stop, mono en
  blokkeren tijdens opname of in multitrack.

De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42988304414)
doorstaat alle 284 controles in Debian, Fedora en Arch, inclusief vier echte
virtuele Qt-audiobackendtests. De geïnstalleerde pakketten doorstaan gewone,
afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling. In de geverifieerde
logs zijn geen Python-callbackfouten gevonden. De 160 MiB-keten bevat naast EQ en
filters nu ook Echo en Reverb en bewaakt de resident geheugengroei op minder
dan 80 MiB boven de toepassing. Dit is een scenariocontrole, geen bovengrens
voor iedere opname, samplerate of combinatie van instellingen.

Native DSP-ABI 7 voegt twee kernels toe met caller-owned vertragingslijnen.
Galm gebruikt acht parallelle gedempte combfilters en vier echte Schroeder-
allpasses per kanaal; feedback volgt g=10^(−3·vertraging/RT60). Iedere comb
normaliseert zijn ingang met √(1−g²). De structuren zijn beschreven in Julius O.
Smiths [Physical Audio Signal Processing](https://www.dsprelated.com/freebooks/pasp/Artificial_Reverberation.html).
Voorvertraging en effectgeheugen zijn onafhankelijk van verwerkingsblokken.
Een optionele uitklank is expliciet begrensd tot 60 seconden, met de laatste
10 ms aflopend naar stilte; voorgestelde tijden zijn richtwaarden.

[Release 0.10.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.10.0)
bevat de geteste installatiepakketten voor Debian/Ubuntu, Fedora en Arch, de
broncode en checksums.
