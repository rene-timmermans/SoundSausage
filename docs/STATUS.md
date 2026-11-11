# SoundSausage 0.19.0

SoundSausage is een golfvorm- en multitrackeditor voor Linux en bevindt zich in de testfase.

## Beschikbaar

- Mono/stereo opnemen via een gekozen microfoon of audio-interface.
- Nieuwe golfvorm, invoegen/vervangen in een golfvorm of nieuw blok op het gekozen spoor.
- Live golfvorm, ingangsniveaus, opnameklok, pauze/hervatten en stoppen als één Undo-stap.
- Onderbroken opnamen afzonderlijk herstellen zonder bestaande bestanden te overschrijven.
- WAV openen en opslaan: mono/stereo, PCM 8/16/24/32-bit en float32.
- MP3 openen, bewerken en importeren in multitrack; WAV of MP3 kiezen bij opslaan, selectie-export en eindmix.
- MP3-bitrates van 128, 192, 256 en 320 kb/s, met ID3-tekst en hoesafbeeldingen.
- Opnamebegin eenmalig overslaan, 0–500 ms met onthouden keuze en korte fade-in; beginwaarde 50 ms.
- Twee dunne kanaalranden tussen links en rechts, begrensd tot het tekenvlak, ook bij live opname.
- De huidige golfvorm of sessie sluiten via Bestand → Sluiten of Ctrl+W, met een keuze voor niet-opgeslagen wijzigingen.
- Directe samplebewerking: zichtbare punten verslepen of exact invoeren, per kanaal en met Undo/Redo.
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
- Linux VST3, LV2 en LADSPA in aparte hulpprocessen, met parameters en bewaarbare status in project en herstel.
- Eigen X11/XWayland-vensters voor ondersteunde VST3- en LV2-effecten; algemene parameterregelaars als alternatief.
- Automatische compensatie van gerapporteerde plug-invertraging tijdens afspelen en mixdown.
- Apparaatgebonden opnamekalibratie, automatische klokdriftcorrectie en een handmatig alternatief.
- Punch-in/out binnen een selectie, met voorloop, korte overgangen, Undo en behoud van originele clips.
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
- Interface in Nederlands, Engels, Duits, Frans en Spaans, direct wisselbaar via Opties → Taal.
- Onthouden taalkeuze, inclusief menu’s, effectvensters, meldingen en standaarddialoogknoppen.
- Volledige doorzoekbare handleiding in alle vijf talen via Help en F1, ook zonder internet.
- Grafiekassen, kanaallabels, tijdvelden en spoorbediening passen zich aan de lettergrootte aan.
- Vertaalde vensters groeien met hun inhoud; grote formulieren krijgen een scrollgebied met bereikbare bevestigingsknoppen.
- De keuze voor de onderste statusregel blijft bij de volgende start bewaard.

## Beperkingen

- Samplepunten verschijnen vanaf acht logische pixels per sample. Slepen wijzigt één punt binnen −1 tot +1; het numerieke venster blijft ook bij minder vergroting beschikbaar.

- MP3 comprimeert met kwaliteitsverlies; opnieuw opslaan kan extra detail verliezen. WAV vermijdt een extra MP3-compressiestap.
- MP3-uitvoer gebruikt de dichtstbijzijnde samplerate van 32/44,1/48 kHz en vereist ten minste 2 ms audio.
- MP3-hoofdstukposities, ReplayGain en andere afgeleide ID3-gegevens worden niet opnieuw berekend. Niet-ondersteunde WAV-bestandsinformatie vereist een keuze vóór MP3-export.
- De ingestelde eerste opnamemilliseconden worden verwijderd. Kies 0 ms om het volledige begin te bewaren.
- Stereo heeft een gezamenlijke tijdas. Duurwijzigingen, knippen, verwijderen, trimmen en opname in de bestaande golfvorm vereisen beide kanalen.
- Op één stereokanaal plakken kan bij gelijke vervangingsduur; Mix Paste blijft binnen de bestaande lengte.

- VST3: één stereo-invoer/-uitvoerbus en float32. LV2/LADSPA: mono/stereo met evenveel in-/uitgangen. Geen VST2, Windows-plug-ins, MIDI-instrumenten of extra sidechains.
- Eigen vensters vereisen X11/XWayland; LV2 GTK-/Qt-adapters en MIDI/Atom-poorten ontbreken. Niet-ondersteunde vereiste functies worden gemeld.
- Compensatie vereist correct gerapporteerde algoritmische vertraging, maximaal tien seconden per spoor. Muzikale delay blijft intact.
- LV2-status met externe bestanden wordt niet als volledig bewaarbaar geaccepteerd.
- Opnamekalibratie vereist een herkenbaar loopbacksignaal; alleen betrouwbare resultaten worden bewaard. Korte/onstabiele klokmetingen rekken audio niet op.
- Een profiel hoort bij apparaten, rate, ingangskanaal en buffer; veranderde instellingen vragen een passende kalibratie.
- Punch-in/out vervangt één spoorinterval per take; herstel van een nog onbevestigde take biedt de ruwe opname aan om handmatig te plaatsen.
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
- Virtuele loopback en onafhankelijke plug-infixtures toetsen synchronisatie; de nieuwe kalibratie-/punchroute en eigen vensters vragen ook fysieke praktijkcontrole vóór v1.0.
- Uitvoer vereist een door Qt ondersteund mono-/stereoapparaat; multikanaals routering ontbreekt.
- Virtuele in-/uitvoercontroles zijn geautomatiseerd; opname, pauze/hervatten en terugluisteren zijn ook met een USB-microfoon in de praktijk bevestigd.
- Dithering en een markereditor ontbreken nog.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
