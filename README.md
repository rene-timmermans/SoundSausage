# SoundSausage

<img src="src/soundsausage/assets/soundsausage.png" width="64" alt="SoundSausage-icoon">

Audiobewerker voor Linux met een vertrouwde golfvorm- en multitrackweergave.
Bewerk losse opnamen of combineer meerdere sporen. De interface volgt je eigen
Linux-thema en accentkleur.

![SoundSausage in golfvormweergave](docs/screenshots/layout-previews/dark-waveform.png)

SoundSausage is in ontwikkeling. De huidige versie is prototype **0.4.1**.

## Wat het kan

- WAV-bestanden openen, bewerken en opslaan.
- Selecteren, knippen, kopiëren, plakken, mengen en trimmen, met ongedaan maken en opnieuw.
- Volume aanpassen, fades toepassen, normaliseren, omkeren en stilte toevoegen.
- Meerdere sporen combineren, clips verplaatsen en trimmen, met volume, pan, mute en solo.
- Volume- en panlijnen op clips tekenen en bewerken.
- Projecten opslaan als `.celp`, met alle gebruikte audio ingebed; een sessie exporteren als WAV.
- Eenvoudige oudere sessies (`.ses`) importeren.
- Inzoomen op de golfvorm, afspelen in een lus en frequenties analyseren.

Opnemen, geavanceerde effecten en volledige ondersteuning voor oude sessies volgen later.
Zie [status en beperkingen](docs/STATUS.md).

## Installeren en starten

Benodigd: Python 3.12–3.14, een C++20-compiler, Make en `ffplay` (uit FFmpeg).

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
Onder de tijdlijn staan het transport, de grote klok, selectie- en weergavetijden en de stereometer.
Met **Options → Show Toolbar Labels** toon je namen naast de werkbalkiconen. **F11** wisselt naar schermvullende weergave.

Meer uitleg: [volume- en panlijnen](docs/ENVELOPES.md) en [thema](docs/THEMA.md).

## Wat er nieuw is

**0.4.1** File → Close en Ctrl+W sluiten de huidige golfvorm of sessie, met een keuze voor niet-opgeslagen wijzigingen.

**0.4.0** Compacte werkbalken en gegroepeerde menu's, een groot werkvlak en een vaste onderrand met transport, klok, selectie-/weergavetijden en een stereometer met dB-schaal en clipindicatie.

## Techniek

Python met Qt 6/PySide6 voor de desktopinterface, NumPy voor audioverwerking en een eigen
C++20-kern voor effecten en het mengen van sporen. Afspelen verloopt voorlopig via FFmpeg/ffplay.
Projecten gebruiken een eigen [CELP-formaat](docs/PROJECTFORMAAT.md).
