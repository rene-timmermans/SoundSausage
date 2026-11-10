# SoundSausage 0.5.0

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
- Zelfstandige CELP-projecten met ingebedde audio en WAV-mixdown.
- Beperkte import van eenvoudige oudere sessies (`.ses`).
- Qt-interface die het Linux-thema en de accentkleur volgt.
- Compacte werkbalken, gegroepeerde menu's en een grijs werkvlak zolang er geen audio openstaat.
- Transport en grote klok onderaan, met selectie-/weergavetijden en een brede stereometer met dB-schaal.

## Beperkingen

- Opnemen, tijd-/toonhoogte-effecten, galm, filters, ruisreductie en externe plug-ins zijn nog niet beschikbaar.
- Amplitude-effecten bewerken de golfvorm; voor een multitrackclip open je eerst een bewerkkopie. Het zijn nog geen realtime spooreffecten.
- Dynamics gebruikt piekdetectie zonder vooruitblik. Exact dezelfde uitkomst als historische effecten is niet aangetoond.
- Nog niet beschikbare effecten staan uitgeschakeld in de menu's.
- SES-import ondersteunt nog geen automation of cues. Opslaan gebeurt als CELP.
- Audio binnen een sessie moet dezelfde samplerate hebben; automatisch omzetten ontbreekt.
- Audio wordt in het geheugen verwerkt, met maximaal 128 MiB gedecodeerde brondata.
  Lange opnamen en continue streaming vanaf schijf worden nog niet ondersteund.
- WAV-metadata zoals cues en tekst blijft bij opslaan nog niet behouden.
- Afspelen gebruikt voorlopig ffplay; de cursor en niveaumeters zijn indicatief.
- Crashherstel en dithering ontbreken nog.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
