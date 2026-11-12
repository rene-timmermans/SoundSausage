# Open punten

Stand: 12 november 2026, SoundSausage 0.20.0.

Deze lijst wordt punt voor punt beoordeeld, in de volgorde van het oorspronkelijke
beperkingenoverzicht. Een vermelding is een onderzoeksvraag, geen toezegging dat
de functie wordt gebouwd of een voorwaarde voor v1.0. Eerst het praktische
probleem bepalen, daarna kiezen: verbeteren of behouden en afvoeren.

Afgeronde en bewust overgeslagen punten verdwijnen direct uit deze open lijst.
De reden blijft kort bewaard in het [besluitenoverzicht](validation/beperkingen-keuzes.md).
De nummers B01–B36 blijven gelijk aan de oorspronkelijke volgorde; B36 is in
twee afzonderlijke functies gesplitst. De technische ondersteuning staat in
[STATUS](STATUS.md), de bediening in de [handleiding](HANDLEIDING.md).

## Nu beoordelen: B03 — MP3-uitvoergrenzen

MP3-uitvoer kiest momenteel de dichtstbijzijnde samplerate van 32/44,1/48 kHz
en vereist minstens 2 ms audio. Kortere fragmenten kunnen als WAV worden bewaard.
De gebruikte encoder ondersteunt ook 8/11,025/12/16/22,05/24 kHz; die zijn nog
geen uitvoerkeuze in SoundSausage.

**Voorstel:** huidige grenzen behouden en dit punt afvoeren, tenzij lagere rates
voor bijvoorbeeld spraak gewenst zijn. De keuze staat nog open. De vormgeving
van deze keuze en eventuele wijziging volgt pas na dat besluit.

## Daarna, in volgorde

Alle onderstaande punten staan op **nog beoordelen**. Per punt worden nut,
gewenst gedrag en omvang bepaald voordat de uitvoering begint.

| Punt | Onderwerp en te beoordelen vervolgstap |
| --- | --- |
| B04 | MP3-metadata: hoofdstukposities en afgeleide ID3-gegevens bijwerken of expliciet afhandelen; de keuze voor niet-overdraagbare WAV-informatie beoordelen. |
| B06 | Kanaalgebonden knippen, verwijderen, trimmen, duurwijzigingen en opname: eerst bepalen hoe links en rechts op dezelfde tijdas moeten blijven aansluiten. |
| B07 | Plakken op één kanaal met een andere duur en Mix Paste voorbij de bestaande lengte: gewenste opvulling en kanaaluitlijning bepalen. |
| B08 | Plug-inbereik: bepalen welke extra busindelingen, sampleformaten, sidechains of plug-informaten nodig zijn. VST2, Windows-plug-ins en MIDI zijn afzonderlijke keuzes. |
| B09 | Eigen plug-invensters: nut van LV2 GTK-/Qt-adapters en ondersteuning buiten X11/XWayland bepalen. MIDI-/Atom-poorten afzonderlijk beoordelen. |
| B10 | Latencycompensatie: de grens van tien seconden beoordelen en omgaan met onjuiste of veranderende plug-inmeldingen onderzoeken. |
| B11 | LV2-status met externe bestanden: onderzoeken hoe bestanden veilig kunnen worden meegenomen en paden bij heropenen hersteld. |
| B14 | Punch-in/out: behoefte aan meerdere intervallen per take bepalen; automatische plaatsing bij herstel van een onbevestigde take beoordelen. |
| B16 | Meer realtime effecten: per bestaande golfvormbewerking bepalen of realtime gebruik nuttig en technisch passend is. |
| B17 | Effectgeheugen bij starten, zoeken en bypass; grenzen van zestien effecten en 60 seconden uitklank. Gewenste overgangen en capaciteit beoordelen. |
| B18 | Convolutie: responsbestanden beschikbaar houden voor herhalen; behoefte aan andere stereoroutering bepalen. |
| B19 | Convolutie: behoefte aan responsen boven 10 s, 524.288 uitvoersamples of 32 MiB bepalen en het ruimtegebruik beoordelen. |
| B20 | Tijd-/toonhoogtebewerking: nut van fragmenten onder 50 ms/64 samples en verwerking zonder volledige selectieanalyse beoordelen. |
| B21 | Ruisreductie: behoefte aan wisselende achtergrondruis en betere bescherming van zachte details bepalen. |
| B22 | Restauratie: bepalen of langdurig gekraak en herstel van clipping nodig zijn naast de bestaande korte tikverwijdering. |
| B23 | Galm en echo: gewenste automatische uitklank en gedrag boven 60 seconden beoordelen, met begrensde feedback. |
| B24 | EQ en filters: hoorbare selectieranden onderzoeken; behoefte aan andere fase-eigenschappen bepalen. |
| B25 | Dynamics: behoefte aan vooruitblik en andere detectiemethoden bepalen. |
| B29 | Multitrack: behoefte boven 24 uur, 32 sporen of 128 bronbestanden bepalen. |
| B30 | Bijzondere metadata: vaststellen welke afgeleide metingen opnieuw berekend of duidelijk afgehandeld moeten worden. |
| B31 | Eindmix: regels bepalen voor het meenemen en samenvoegen van markers en tags uit meerdere bronnen. |
| B32 | Afspelen: fysieke uitvoerlatentie en naadloos lussen afzonderlijk beoordelen en meetbaar toetsen. |
| B33 | Praktijkcontrole vóór v1.0: fysieke kalibratie, langere overdub, punch en heropenen; echte VST3-/LV2-vensters en statusopslag bevestigen. Bestaande virtuele controles blijven aanvullend bewijs. |
| B34 | Audio-uitvoer: behoefte aan meer dan twee kanalen en multikanaals routering bepalen. |
| B36a | Dithering: instellingen en gedrag bij uitvoer naar een lagere PCM-bitdiepte bepalen. |
| B36b | Markereditor: markers toevoegen, verplaatsen, benoemen en verwijderen; bediening en opslag bepalen. |

Voor B33 blijven de eerder afgesproken fysieke proeven nodig vóór v1.0.
De andere kandidaten krijgen pas na beoordeling een uitvoeringsbesluit; optionele
uitbreidingen houden een bruikbare v1.0 niet automatisch tegen. Na ieder
afgehandeld punt wordt het volgende open nummer de actieve bespreking.
