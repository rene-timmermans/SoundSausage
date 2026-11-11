# SoundSausage 0.15.0

SoundSausage is een golfvorm- en multitrackeditor voor Linux en bevindt zich in de testfase.

## Beschikbaar

- Mono/stereo opnemen via een gekozen microfoon of audio-interface.
- Nieuwe golfvorm, invoegen/vervangen in een golfvorm of nieuw blok op het gekozen spoor.
- Live golfvorm, ingangsniveaus, opnameklok, pauze/hervatten en stoppen als één Undo-stap.
- Onderbroken opnamen afzonderlijk herstellen zonder bestaande bestanden te overschrijven.
- WAV openen en opslaan: mono/stereo, PCM 8/16/24/32-bit en float32.
- De huidige golfvorm of sessie sluiten via File → Close of Ctrl+W, met een keuze voor niet-opgeslagen wijzigingen.
- Golfvormbewerking met selecties, knippen, plakken, Mix Paste, trimmen en undo/redo.
- Links/rechts apart kiezen door slepen, een zichtbare kanaalkeuze of sneltoetsen.
- Effecten, Preview, kopiëren en selectie-export op gekozen kanalen; het andere kanaal blijft behouden.
- Doorlopende golfvorm bij zoomen en afzonderlijke functie-iconen in menu's en werkbalken.
- Versterking, fades, normaliseren, omkeren, polariteit omkeren, tonen en stilte.
- Channel Mixer, Dynamics Processing en Envelope, met presets, bewerkbare curves en luistervoorbeelden.
- Grafische tienbands-EQ, vijf parametrische bell-banden en low/high shelf.
- Hoog-/laagdoorlaat met 12–48 dB/oct, banddoorlaat en notch met instelbare Q.
- EQ-presets, frequentierespons, uitgangsvolume en luistervoorbeelden.
- Delay met tijden per kanaal; Echo met feedback, demping en stereopingpong.
- Algoritmische galm met ruimtegrootte, nagalmtijd, voorvertraging en breedte.
- Uitklank van maximaal 60 seconden toevoegen, met behoud en verschuiven van cuepunten.
- Ruisprofielen opnemen/laden/bewaren, ruisreductie en korte tikken interpoleren.
- Lengte veranderen met behoud van toonhoogte, toonhoogte verschuiven met behoud van duur.
- Tempoverhouding, Fine/Fast-kwaliteit en formantbehoud; cuepunten volgen gewijzigde timing.
- Soft/hard clip, wavefold en bit crush, met menging en optionele oversampling.
- FFT-convolutie met WAV-responsen, energienormalisatie en optionele uitklank.
- DC-offset verwijderen bij normaliseren; onafhankelijke of gekoppelde stereokanalen waar van toepassing.
- Multitrack met maximaal 32 sporen, clips verplaatsen, trimmen en dupliceren.
- Volume, pan, mute/solo en bewerkbare volume- en panlijnen per clip.
- Realtime spooreffecten met volgorde, bypass, bewerkbare instellingen, uitklank en Undo/Redo.
- Linux VST3 in een apart hulpproces, met parameters en componentstatus in project en herstel.
- Opnemen met begeleiding, samen pauzeren/stoppen en een onthouden opnameverschuiving.
- Nieuwe projecten bewaren audio, clips, lijnen en spoorketens; mixdown gebruikt dezelfde ketens.
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

- Stereo heeft een gezamenlijke tijdas. Duurwijzigingen, knippen, verwijderen, trimmen en opname in de bestaande golfvorm vereisen Both.
- Op één stereokanaal plakken kan bij gelijke vervangingsduur; Mix Paste blijft binnen de bestaande lengte.

- Externe effecten ondersteunen native Linux VST3 met één stereo-invoer/-uitvoerbus en float32. Geen VST2, Windows-plug-ins, MIDI-instrumenten of extra sidechains.
- Plug-invensters gebruiken generieke parameters; eigen editors en automatische plug-inlatencycompensatie ontbreken.
- Een plug-in en zijn eigen externe bestanden blijven apart geïnstalleerd; gewijzigde/ontbrekende plug-ins worden gemeld.
- Normalize, restauratie, tijd/toonhoogte, vervorming en convolutie blijven golfvormbewerkingen. Amplify, Channel Mixer, Dynamics, EQ, filters, delay, echo, galm en Invert zijn ook realtime spooreffecten.
- Starten, zoeken of bypass inschakelen begint met nieuw effectgeheugen. Spoorketens zijn begrensd tot zestien effecten en 60 seconden uitklank per spoor.
- Convolutie vereist een ongewijzigd responsbestand voor herhalen; stereo is kanaalgewijs.
- Impulsresponsen zijn begrensd tot 10 s / 524.288 uitvoersamples en 32 MiB per bestand.
- Tijd-/toonhoogtebewerking vraagt minimaal 50 ms (ten minste 64 samples) en analyseert de volledige selectie.
- Ruisreductie richt zich op constante achtergrond; sterke instellingen kunnen zachte details aantasten.
- Click Removal behandelt korte geïsoleerde tikken, geen langdurige kraken of clipping.
- Galm en echo hebben begrensde, optionele uitklank; extreme feedback kan langer dan 60 seconden doorlopen.
- EQ en filters veranderen fase; korte selecties kunnen aan de randen een overgang geven.
- Dynamics gebruikt piekdetectie zonder vooruitblik. Exact dezelfde uitkomst als historische effecten is niet aangetoond.
- Import van oudere sessies ondersteunt nog geen automation of cues. Bewaren kan als zelfstandig project.
- Sessies bewaren audio op één samplerate; geïmporteerde audio wordt daarnaartoe omgezet.
- Grote bewerkingen vragen vrije schijfruimte voor bronkopieën, resultaten en Undo.
- Multitrack blijft begrensd tot 24 uur, 32 sporen en 128 bronbestanden.
- Bijzondere metadata wordt letterlijk bewaard; afgeleide meetgegevens worden niet opnieuw berekend.
- Een eindmix voegt markers of tags uit verschillende bronnen nog niet samen.
- De audiobackend rapporteert de verwerkte frames; exacte fysieke luidsprekerlatentie en naadloos lussen zijn niet gegarandeerd.
- Bestaande sporen kunnen tijdens een multitrackopname spelen. Punch-in/out, automatische fysieke latencykalibratie en driftcompensatie tussen apparaten ontbreken; opnamepositie is handmatig afstelbaar.
- Uitvoer vereist een door Qt ondersteund mono-/stereoapparaat; multikanaals routering ontbreekt.
- Virtuele in-/uitvoercontroles zijn geautomatiseerd; opname, pauze/hervatten en terugluisteren zijn ook met een USB-microfoon in de praktijk bevestigd.
- Dithering en een markereditor ontbreken nog.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
