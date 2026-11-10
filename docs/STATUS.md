# SoundSausage 0.7.0

SoundSausage is een golfvorm- en multitrackeditor voor Linux en bevindt zich in de testfase.

## Beschikbaar

- WAV openen en opslaan: mono/stereo, PCM 8/16/24/32-bit en float32.
- De huidige golfvorm of sessie sluiten via File → Close of Ctrl+W, met een keuze voor niet-opgeslagen wijzigingen.
- Golfvormbewerking met selecties, knippen, plakken, Mix Paste, trimmen en undo/redo.
- Versterking, fades, normaliseren, omkeren, polariteit omkeren, tonen en stilte.
- Channel Mixer, Dynamics Processing en Envelope, met presets, bewerkbare curves en luistervoorbeelden.
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

- Opnemen, tijd-/toonhoogte-effecten, galm, filters, ruisreductie en externe plug-ins zijn nog niet beschikbaar.
- Amplitude-effecten bewerken de golfvorm; voor een multitrackclip open je eerst een bewerkkopie. Het zijn nog geen realtime spooreffecten.
- Dynamics gebruikt piekdetectie zonder vooruitblik. Exact dezelfde uitkomst als historische effecten is niet aangetoond.
- Nog niet beschikbare effecten staan uitgeschakeld in de menu's.
- SES-import ondersteunt nog geen automation of cues. Opslaan gebeurt als CELP.
- Sessies bewaren audio op één samplerate; geïmporteerde audio wordt daarnaartoe omgezet.
- Grote bewerkingen vragen vrije schijfruimte voor bronkopieën, resultaten en Undo.
- Multitrack blijft begrensd tot 24 uur, 32 sporen en 128 bronbestanden.
- Bijzondere metadata wordt letterlijk bewaard; afgeleide meetgegevens worden niet opnieuw berekend.
- Een eindmix voegt markers of tags uit verschillende bronnen nog niet samen.
- De audiobackend rapporteert de verwerkte frames; exacte fysieke luidsprekerlatentie en naadloos lussen zijn niet gegarandeerd.
- Uitvoer vereist een door Qt ondersteund mono-/stereoapparaat; multikanaals routering ontbreekt.
- Virtuele audiocontroles zijn geautomatiseerd; een hoorbare controle op fysieke hardware staat nog open.
- Dithering en een markereditor ontbreken nog.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
