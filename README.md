# SoundSausage

<img src="src/soundsausage/assets/soundsausage.png" width="64" alt="SoundSausage-icoon">

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Bewerk losse opnamen of combineer meerdere sporen. De interface volgt je eigen Linux-thema en accentkleur.

![SoundSausage in golfvormweergave](docs/screenshots/layout-previews/dark-waveform.png)

De huidige versie is **0.6.0**.

## Wat het kan

- WAV-bestanden openen, bewerken en opslaan.
- Selecteren, knippen, kopiëren, plakken, mengen en trimmen, met ongedaan maken en opnieuw.
- Volume aanpassen, fades toepassen, normaliseren, omkeren en stilte toevoegen.
- Stereokanalen mengen, dynamiek bewerken en een volumeverloop tekenen, met luistervoorbeelden.
- Meerdere sporen combineren, clips verplaatsen en trimmen, met volume, pan, mute en solo.
- Volume- en panlijnen op clips tekenen en bewerken.
- Projecten opslaan als `.celp`, met alle gebruikte audio ingebed; een sessie exporteren als WAV.
- Eenvoudige oudere sessies (`.ses`) importeren.
- Inzoomen op de golfvorm, afspelen in een lus en frequenties analyseren.

Opnemen, geavanceerde effecten en volledige ondersteuning voor oude sessies volgen later.
Zie [status en beperkingen](docs/STATUS.md).

## Installeren en starten

Benodigd: Python 3.12–3.14, een C++20-compiler, Make, Qt Multimedia en libsamplerate.
Op Arch is Qt Multimedia een aparte afhankelijkheid naast PySide6.

Installatiepakketten voor Debian/Ubuntu, Fedora en Arch staan bij de
[releases](https://github.com/rene-timmermans/SoundSausage/releases).
Zie [installeren](docs/INSTALLEREN.md) voor ondersteunde versies en installatiecommando's.
Handmatig bouwen vanuit de broncode:

```bash
git clone https://github.com/rene-timmermans/SoundSausage.git
cd SoundSausage
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
./run.sh
```

Het startscript bouwt de audiokern automatisch. Een voorbeeldproject openen:

```bash
./run.sh examples/demo-envelopes.celp
```

## Bediening

Wissel met **Tab** tussen golfvorm en multitrack. **Spatie** start en stopt het afspelen.
**Ctrl+W** sluit de huidige golfvorm of sessie; het programma blijft open. Bij niet-opgeslagen wijzigingen kun je opslaan, verwerpen of annuleren.
In multitrack sleep je WAV-bestanden op een spoor en verplaats of trim je clips met de muis.
Met **Volume Line** en **Pan Line** teken je de lijnen op een clip.

De effecten staan onder **Transform**; versterken en normaliseren vind je in **Amplitude**.
Daar staan ook **Channel Mixer**, **Dynamics Processing** en **Envelope**.
Effecten bewerken de selectie, of de hele golfvorm als er niets geselecteerd is.
Met **Preview** beluister je de instelling voordat je die toepast. Zie [Amplitude](docs/AMPLITUDE.md).
Onder de tijdlijn staan het transport, de grote klok, selectie- en weergavetijden en de stereometer.
Met **Options → Show Toolbar Labels** toon je namen naast de werkbalkiconen. **F11** wisselt naar schermvullende weergave.
Via **Options → Audio Hardware** kies je het uitvoerapparaat. Verschillende samplerates
worden bij import en plakken omgezet; **Edit → Convert Sample Rate** zet een golfvorm om.
Zie [audio-instellingen](docs/AUDIO.md) en de [ontwikkelvoortgang](docs/VOORTGANG.md).

Meer uitleg: [volume- en panlijnen](docs/ENVELOPES.md) en [thema](docs/THEMA.md).

## Wat er nieuw is

**0.6.0** Geïntegreerd afspelen met apparaatkeuze en een audioklok voor cursor en meters. Samplerateconversie bij import, plakken en golfvormbewerking. Zie de [releasepunten](docs/releases/0.6.0.md).

**0.5.0** De groep Amplitude is uitgebreid met Channel Mixer, Dynamics Processing en Envelope. Alle Amplitude-dialogen hebben een luistervoorbeeld; Normalize kan DC-offset verwijderen. Installatiepakketten zijn beschikbaar voor Debian/Ubuntu, Fedora en Arch. Zie de [releasepunten](docs/releases/0.5.0.md).

**0.4.1** File → Close en Ctrl+W sluiten de huidige golfvorm of sessie, met een keuze voor niet-opgeslagen wijzigingen.

**0.4.0** Compacte werkbalken en gegroepeerde menu's, een groot werkvlak en een vaste onderrand met transport, klok, selectie-/weergavetijden en een stereometer met dB-schaal en clipindicatie.

## Techniek

Python met Qt 6/PySide6 voor de desktopinterface, NumPy voor audioverwerking en een eigen
C++20-kern voor effecten en het mengen van sporen. Qt Multimedia verzorgt het afspelen;
libsamplerate verzorgt de samplerateconversie.
Projecten gebruiken een eigen [CELP-formaat](docs/PROJECTFORMAAT.md).

SoundSausage is beschikbaar onder [GPL-3.0-or-later](LICENSE): GNU GPL versie 3 of, naar keuze, een latere versie.
