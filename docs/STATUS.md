# SoundSausage 0.9.0

SoundSausage is een golfvorm- en multitrackeditor voor Linux en bevindt zich in de testfase.

## Beschikbaar

- Mono/stereo opnemen via een gekozen microfoon of audio-interface.
- Nieuwe golfvorm, invoegen/vervangen in een golfvorm of nieuw blok op het gekozen spoor.
- Live golfvorm, ingangsniveaus, opnameklok, pauze/hervatten en stoppen als één Undo-stap.
- Onderbroken opnamen afzonderlijk herstellen zonder bestaande bestanden te overschrijven.
- WAV openen en opslaan: mono/stereo, PCM 8/16/24/32-bit en float32.
- De huidige golfvorm of sessie sluiten via File → Close of Ctrl+W, met een keuze voor niet-opgeslagen wijzigingen.
- Golfvormbewerking met selecties, knippen, plakken, Mix Paste, trimmen en undo/redo.
- Versterking, fades, normaliseren, omkeren, polariteit omkeren, tonen en stilte.
- Channel Mixer, Dynamics Processing en Envelope, met presets, bewerkbare curves en luistervoorbeelden.
- Grafische tienbands-EQ, vijf parametrische bell-banden en low/high shelf.
- Hoog-/laagdoorlaat met 12–48 dB/oct, banddoorlaat en notch met instelbare Q.
- EQ-presets, frequentierespons, uitgangsvolume en luistervoorbeelden.
- DC-offset verwijderen bij normaliseren; onafhankelijke of gekoppelde stereokanalen waar van toepassing.
- Multitrack met maximaal 32 sporen, clips verplaatsen, trimmen en dupliceren.
- Volume, pan, mute/solo en bewerkbare volume- en panlijnen per clip.
- Zelfstandige projecten met ingebedde audio en WAV-mixdown.
- Beperkte import van eenvoudige oudere sessies (`.ses`).
- Qt-interface die het Linux-thema en de accentkleur volgt.
- Compacte werkbalken, gegroepeerde menu's en een grijs werkvlak zolang er geen audio openstaat.
- Transport en grote klok onderaan, met selectie-/weergavetijden en een brede stereometer met dB-schaal.
- Geïntegreerd afspelen, blijvende apparaat-/bufferkeuze en een cursor die de verwerkte audiotijd volgt.
- Samplerates omzetten bij import, plakken, clipkopieën toepassen en gehele golfvormen, met Undo/Redo.
- Lange bestanden met blokverwerking, opslag op schijf en herbruikbare golfvormoverzichten.
- Voortgang en annuleren zonder gedeeltelijk bevestigde bewerkingen of opslag.
- Herstel van golfvorm en sessie na onverwacht afsluiten; Undo begint na herstel opnieuw.
- WAV-tekst, cuepunten, labels en ondersteunde positiegegevens bewaren en aanpassen.
- Doorzoekbare Nederlandstalige handleiding via Help en F1, ook zonder internet.

## Beperkingen

- Tijd-/toonhoogte-effecten, galm, ruisreductie en externe plug-ins zijn nog niet beschikbaar.
- Amplitude-, EQ- en filtereffecten bewerken de golfvorm; voor een multitrackclip open je eerst een bewerkkopie. Het zijn nog geen realtime spooreffecten.
- EQ en filters veranderen fase; korte selecties kunnen aan de randen een overgang geven.
- Dynamics gebruikt piekdetectie zonder vooruitblik. Exact dezelfde uitkomst als historische effecten is niet aangetoond.
- Nog niet beschikbare effecten staan uitgeschakeld in de menu's.
- SES-import ondersteunt nog geen automation of cues. Opslaan gebeurt als CELP.
- Sessies bewaren audio op één samplerate; geïmporteerde audio wordt daarnaartoe omgezet.
- Grote bewerkingen vragen vrije schijfruimte voor bronkopieën, resultaten en Undo.
- Multitrack blijft begrensd tot 24 uur, 32 sporen en 128 bronbestanden.
- Bijzondere metadata wordt letterlijk bewaard; afgeleide meetgegevens worden niet opnieuw berekend.
- Een eindmix voegt markers of tags uit verschillende bronnen nog niet samen.
- De audiobackend rapporteert de verwerkte frames; exacte fysieke luidsprekerlatentie en naadloos lussen zijn niet gegarandeerd.
- Bestaande sporen worden tijdens opname nog niet afgespeeld; punch-in/out en automatische latencycompensatie ontbreken.
- Uitvoer vereist een door Qt ondersteund mono-/stereoapparaat; multikanaals routering ontbreekt.
- Virtuele in-/uitvoercontroles zijn geautomatiseerd; opname, pauze/hervatten en terugluisteren zijn ook met een USB-microfoon in de praktijk bevestigd.
- Dithering en een markereditor ontbreken nog.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
