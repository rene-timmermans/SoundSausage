# SoundSausage 0.24.0

SoundSausage is een golfvorm- en multitrackeditor voor Linux en bevindt zich in de testfase.

## Beschikbaar

- Mono/stereo opnemen via een gekozen microfoon of audio-interface.
- Nieuwe golfvorm, invoegen/vervangen in een golfvorm of nieuw blok op het gekozen spoor.
- Live golfvorm, ingangsniveaus, opnameklok, pauze/hervatten en stoppen als één Undo-stap.
- Onderbroken opnamen afzonderlijk herstellen zonder bestaande bestanden te overschrijven.
- WAV openen en opslaan: mono/stereo, PCM 8/16/24/32-bit en float32.
- MP3 openen, bewerken en importeren in multitrack; WAV of MP3 kiezen bij opslaan, selectie-export en eindmix.
- MP3-bitrates van 128, 192, 256 en 320 kb/s, met ID3-tekst en hoesafbeeldingen.
- ID3-hoofdstukken volgen knippen, trimmen, plakken, omkeren en tijdrekken; inhoudsopgave, selectie-export en Undo/Redo blijven samenhangend.
- Achterhaalde ReplayGain-, volume-, timing- en encodergegevens opschonen; actuele duur en nieuwe MP3-encoderinformatie bewaren.
- Ondersteunde WAV INFO-tekst naar MP3 meenemen; onbekende, misvormde en conflicterende velden vóór export melden.
- Opnamebegin eenmalig overslaan, 0–500 ms met onthouden keuze en korte fade-in; beginwaarde 50 ms.
- Twee dunne kanaalranden tussen links en rechts, begrensd tot het tekenvlak, ook bij live opname.
- De huidige golfvorm of sessie sluiten via Bestand → Sluiten of Ctrl+W, met een keuze voor niet-opgeslagen wijzigingen.
- Directe samplebewerking: zichtbare punten verslepen of exact invoeren, per kanaal en met Undo/Redo.
- Golfvorm tekenen met potloodknop of D: ook zonder losse punten, zoomafhankelijke groepen tot één seconde en één Undo-stap per sleepbeweging.
- Golfvormbewerking met selecties, knippen, plakken, Mix Paste, trimmen en undo/redo.
- Links/rechts apart kiezen door slepen, een zichtbare kanaalkeuze of sneltoetsen.
- Effecten, Preview, kopiëren en selectie-export op gekozen kanalen; het andere kanaal blijft behouden.
- Knippen, trimmen, invoegen, ongelijk plakken, uitklank, tijdrekken en opnemen op één kanaal, met blokverwerking en één Undo-stap.
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
- Adaptieve ruisschatting met instelbare aanpassingstijd, detailbehoud en presets voor wisselende achtergrond en fijne details.
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
- Herkenbaar programma-icoon met paarse achtergrond in hoofdvenster, losse vensters en taakbalk.
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

## Open punten en beoordeling

De [todo](TODO.md) bevat de actuele beoordeling, punt voor punt. Afgeronde en
bewust overgeslagen punten verdwijnen daaruit. Onderstaande eigenschappen
beschrijven de huidige ondersteuning; ze zijn niet automatisch bouwopdrachten
of voorwaarden voor v1.0.

## Bestandskeuzes en bediening

- MP3-uitvoer gebruikt de dichtstbijzijnde samplerate van 32/44,1/48 kHz en vereist ten minste 2 ms audio.
- MP3 comprimeert met kwaliteitsverlies; opnieuw opslaan kan extra detail verliezen. WAV vermijdt een extra MP3-compressiestap.
- De ingestelde eerste opnamemilliseconden worden verwijderd. Kies 0 ms om het volledige begin te bewaren.
- Opnamekalibratie vereist een herkenbaar loopbacksignaal; alleen betrouwbare resultaten worden bewaard. Korte/onstabiele klokmetingen rekken audio niet op.
- Een profiel hoort bij apparaten, rate, ingangskanaal en buffer; veranderde instellingen vragen een passende kalibratie.
- Een plug-in en zijn eigen externe bestanden blijven apart geïnstalleerd; gewijzigde/ontbrekende plug-ins worden gemeld.
- Import van oudere sessies ondersteunt nog geen automation of cues. Bewaren kan als zelfstandig project.
- Sessies bewaren audio op één samplerate; geïmporteerde audio wordt daarnaartoe omgezet.
- Grote bewerkingen vragen vrije schijfruimte voor bronkopieën, resultaten en Undo.

## Ondersteuning en grenzen

- Samplepunten verschijnen vanaf twee logische pixels per sample; het numerieke venster blijft bij ieder zoomniveau beschikbaar. Golfvorm tekenen vervangt de samples langs de getekende lijn; een groep beslaat maximaal één seconde, een hele beweging kan meerdere groepen raken.
- ID3-hoofdstukken gebruiken milliseconden; lege of door gedeeltelijk omkeren versnipperde hoofdstukken vervallen. Herkende verouderde metingen en niet-ondersteunde getimede ID3-velden vervallen na audioverandering. Nieuwe ReplayGain-metingen worden niet berekend; onbekende privévelden blijven letterlijk behouden.
- Stereo houdt een gezamenlijke tijdas. Bij knippen, verwijderen, invoegen, plakken, tijdrekken, uitklank en opname op één kanaal verschuift alleen dat kanaal; het andere blijft exact op zijn positie. Het kortere kanaal krijgt achteraan stilte, die bij opslaan onderdeel van de audio blijft.
- Trimmen op één kanaal zet alleen het gekozen fragment op tijdstip nul en vult de rest met stilte. Mix Paste kan op één kanaal voorbij het einde mengen. Gezamenlijke markers en hoofdstukken blijven bij zulke kanaalbewerkingen op hun tijdstip; bronmarkeringen worden bij plakken op één kanaal niet samengevoegd.
- VST3: één stereo-invoer/-uitvoerbus en float32. LV2/LADSPA: mono/stereo met evenveel in-/uitgangen. Geen VST2, Windows-plug-ins, MIDI-instrumenten of extra sidechains.
- Eigen vensters vereisen X11/XWayland; LV2 GTK-/Qt-adapters en MIDI/Atom-poorten ontbreken. Niet-ondersteunde vereiste functies worden gemeld.
- Compensatie vereist correct gerapporteerde algoritmische vertraging, maximaal tien seconden per spoor. Muzikale delay blijft intact.
- LV2-status met externe bestanden wordt niet als volledig bewaarbaar geaccepteerd.
- Punch-in/out vervangt één spoorinterval per take; herstel van een nog onbevestigde take biedt de ruwe opname aan om handmatig te plaatsen.
- Normalize, restauratie, tijd/toonhoogte, vervorming en convolutie blijven golfvormbewerkingen. Amplify, Channel Mixer, Dynamics, EQ, filters, delay, echo, galm en Invert zijn ook realtime spooreffecten.
- Starten, zoeken of bypass inschakelen begint met nieuw effectgeheugen. Spoorketens zijn begrensd tot zestien effecten en 60 seconden uitklank per spoor.
- Convolutie vereist een ongewijzigd responsbestand voor herhalen; stereo is kanaalgewijs.
- Impulsresponsen zijn begrensd tot 10 s / 524.288 uitvoersamples en 32 MiB per bestand.
- Tijd-/toonhoogtebewerking vraagt minimaal 50 ms (ten minste 64 samples) en analyseert de volledige selectie.
- Alle vijf offlinehandleidingen hebben blauwe onderwerpverwijzingen, een Inhoud-knop en Vorige/Volgende voor onderwerpen. Enter/F3/Shift+F3 blijven zoekresultaten volgen.
- Werkbalk- en afspeelknoppen zijn neutraal met leesbare accenticonen; een dun accentkader markeert de actieve keuze.
- Vaste en adaptieve ruisreductie beginnen met een passend ruisprofiel. Adaptief volgt wijzigingen in de achtergrond; snelle instellingen kunnen aangehouden geluiden als ruis leren. Detailbehoud laat ook meer achtergrond door; stemseparatie en herstel van ontbrekende details ontbreken.
- Click Removal behandelt korte geïsoleerde tikken, geen langdurige kraken of clipping.
- Offline uitklank kan automatisch tot een lage restpiek worden bepaald of handmatig tot 600 s; galmtijd tot 60 s. Automatisch bewaart vertraagde gebeurtenissen over stille gaten en reserveert alleen werkelijke uitvoer. Als de 600 s-grens nog hoorbare toestand bevat, blijft de bewerking onaangepast en volgt een melding. Realtime spoorketens houden hun afzonderlijke 60 s-grens.
- EQ en filters houden hun natuurlijke causale fase. Een selectieovergang van standaard 5 ms mengt binnen de selectie en bereidt het filter met maximaal 60 s voorafgaande audio voor; buitenliggende samples blijven exact. Kies 0 ms voor de eerdere directe verwerking. Zeer korte selecties kunnen geheel uit overgang bestaan.
- Dynamics gebruikt piekdetectie zonder vooruitblik.
- Multitrack blijft begrensd tot 24 uur, 32 sporen en 128 bronbestanden.
- Bijzondere metadata wordt letterlijk bewaard; afgeleide meetgegevens worden niet opnieuw berekend.
- Een eindmix voegt markers of tags uit verschillende bronnen nog niet samen.
- De audiobackend rapporteert de verwerkte frames; exacte fysieke luidsprekerlatentie en naadloos lussen zijn niet gegarandeerd.
- Uitvoer vereist een door Qt ondersteund mono-/stereoapparaat; multikanaals routering ontbreekt.
- Dithering en een markereditor ontbreken nog.

## Praktijkcontrole

- Virtuele in-/uitvoercontroles zijn geautomatiseerd; opname, pauze/hervatten en terugluisteren zijn ook met een USB-microfoon in de praktijk bevestigd.
- Virtuele loopback en onafhankelijke plug-infixtures toetsen synchronisatie; de nieuwe kalibratie-/punchroute en eigen vensters vragen ook fysieke praktijkcontrole vóór v1.0.

Zie de [projectbeschrijving](../README.md), [volume- en panlijnen](ENVELOPES.md) en
het [projectformaat](PROJECTFORMAAT.md) voor meer informatie.
