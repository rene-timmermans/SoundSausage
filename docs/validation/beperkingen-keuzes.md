# Keuzes bij het beperkingenoverzicht

De [open todo](../TODO.md) bevat uitsluitend nog te beoordelen of uit te voeren
punten. Dit overzicht bewaart de redenen voor afgevoerde punten; het is geen
tweede werklijst. Nummering volgt de 36 regels uit STATUS 0.19.1 bij aanvang van
de beoordeling op 12 november 2026. B36 is opgesplitst in dithering en een
markereditor. Afvoeren verandert geen bestandsformaat of ondersteunde functie.

## Afgevoerd bij het aanmaken van de todo — 12 november 2026

| Punt | Besluit en reden |
| --- | --- |
| B02 | MP3 blijft een formaat met kwaliteitsverlies. Opnieuw comprimeren hoort bij MP3-export; WAV is al beschikbaar om een extra MP3-compressiestap te vermijden. Geen herstelopdracht. |
| B05 | De instelbare startcorrectie voor opname behouden. Die is op verzoek toegevoegd tegen de beginklik; 0 ms bewaart het hele begin. Geen ontbrekende functie. |
| B12 | Alleen betrouwbare loopbackkalibratie en klokmetingen toepassen. Onherkenbare signalen en korte/onstabiele metingen afwijzen is gewenst gedrag. De fysieke controle blijft afzonderlijk open als B33. |
| B13 | Kalibratieprofielen aan apparaten, samplerate, ingangskanaal en buffer blijven koppelen. Bij gewijzigde instellingen is een passend profiel nodig; dit voorkomt onjuiste correctie. |
| B15 | Externe plug-ins blijven apart geïnstalleerd. Het melden van ontbrekende of gewijzigde plug-ins is gewenst gedrag. Bestanden die bij LV2-status horen, zijn afzonderlijk geregistreerd als B11. |
| B26 | Uitgebreidere import van oude sessies niet uitbreiden: er zijn geen bestaande sessiebestanden waarvoor dit nodig is. Volledig bewaren en heropenen van nieuwe projecten blijft de afspraak en is beschikbaar. De bestaande beperkte import blijft beschreven. |
| B27 | Eén samplerate per sessie behouden; geïmporteerde audio wordt omgezet. Dit is de gekozen mixwerkwijze, geen ontbrekende functie. |
| B28 | Vrije werkruimte blijft nodig voor bronnen, resultaten en Undo. Dit ruimtegebruik is verklaard in de documentatie over lange bestanden; het op zichzelf is geen fout. Concrete ruimteproblemen kunnen wel een nieuwe melding vormen. |
| B35 | De bevestigde USB-opname-/afspeelproef en geautomatiseerde in-/uitvoercontroles zijn bewijs van werking, geen beperking. Nieuwe fysieke synchronisatie-/punch-/plug-inproeven blijven open als B33. |

Alle negen punten zijn uit de open todo verwijderd. Hun relevante bediening,
voorwaarden en ondersteuning blijven in STATUS en de handleiding terug te vinden.

## Eerste inhoudelijke beoordeling — B01

De broncode van 0.19.1 bevestigt de drempel van acht logische pixels, het vaste sample en
kanaal tijdens slepen, het bereik −1 tot +1 en numerieke invoer bij elk zoomniveau.
De bestaande handleiding beschrijft dit in hoofdstuk 4. De eerdere opdracht
voor nauwkeurig herstel van losse tikjes is hiermee beschikbaar.

Besluit: de getekende lijn vervangt de samples. Bij uitzoomen groeit een groep
tot maximaal één seconde; een hele sleepbeweging mag meerdere groepen raken.
Er zijn geen aanwijsbare punten nodig in de tekenmodus. De bestaande exacte
invoer blijft beschikbaar.

B01 is afgerond in [0.20.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.20.0)
en uit de open todo verwijderd. Losse punten verschijnen vanaf twee logische
pixels; de nieuwe tekenmodus werkt bij ieder zoomniveau. Alle 460 controles
slagen op Debian/Fedora/Arch zonder overslaan, plus de vier installatiezelftests
op vijf doelen. Zie [tekencontrole](drawing.md).

## MP3-uitvoergrenzen behouden — B03

De uitvoerkeuzes blijven 128/192/256/320 kb/s bij de dichtstbijzijnde samplerate
van 32/44,1/48 kHz, met minstens 2 ms audio. B03 is als bewuste exportkeuze
uit de open todo verwijderd. Kortere fragmenten blijven als WAV te bewaren.
Lage MP3-samplerates worden geen nieuwe exportoptie zonder een concrete
behoefte aan compactere uitvoer en passende lagere bitratekeuzes.

De technische beoordeling gebruikt 96 synthetische encode-/decodeproeven:
negen rates, vier bestaande bitrates en mono/stereo, plus zeer korte fragmenten.
Bij lage rates verlaagt de gebruikte encoder de gevraagde bitrate in een deel
van de gevallen. Zeer korte invoer kan na decoderen langer zijn: één sample
wordt in de geteste route bijvoorbeeld 47 samples. De huidige uitvoergrenzen
vermijden die gevallen. Zie [onderbouwing](mp3-output-limits.md).

De software blijft 0.20.0; er is geen functionele wijziging of nieuwe release.
De technische voorwaarden blijven in STATUS en de vijf handleidingen staan.

## MP3-metadata — B04 afgerond in 0.21.0

Hoofdstukken volgen tijdlijnbewerkingen, selectie-export en plakken; inhoudsopgave,
Undo/Redo, projectopslag en herstel behouden de samenhang. Herkende achterhaalde
metingen en niet-ondersteunde tijdcodes vervallen. Tempo en toonsoort worden
alleen bij de relevante effecten ongeldig gemaakt. Gewone tags en hoes blijven
behouden; nieuwe duur en encoderinformatie worden uit de uitvoer bepaald.
ReplayGain opnieuw meten is niet toegevoegd; oude onbetrouwbare waarden worden
verwijderd. Onbekende privévelden blijven letterlijk behouden.

Ondersteunde WAV INFO-velden worden vertaald. Onbekende, ongeldige, conflicterende
velden en extra ID3-tags worden vóór export gemeld; weigeren behoudt het doel.
De vijf volledige handleidingen leggen de bediening en praktische grenzen uit.

B04 is na verificatie van [0.21.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.21.0)
uit de open todo verwijderd. Alle 486 controles slagen zonder overslaan op
Debian/Fedora/Arch en vier installatiezelftests op vijf doelen. Er blijven
25 deelpunten open, met B06 als volgende beoordeling. Zie de
[controledekking](id3-metadata.md).

## Redactionele correctie — B25

De vergelijking met niet nader gespecificeerde historische effecten vervalt.
Die heeft geen toetsbaar productdoel. De concrete eigenschap — piekdetectie
zonder vooruitblik — blijft beschreven; de uitbreiding B25 is voorlopig uitgesteld.


## Scope voor de eerste v1 — 14 november 2026

De gekozen v1-scope bestaat uit B06, B07, B21, B23, B24, B33 en B36b.
B06/B07 zijn afgerond in 0.22.0 en B21 in 0.23.0; vier punten blijven open.
B23/B24 en de markereditor B36b volgen. B33 volgt met de
functioneel afgeronde app, daarna een releasecandidate en de eerste v1.0.

De onderstaande **18 punten zijn voorlopig uitgesteld**, niet afgerond of
permanent afgewezen. Ze zijn uit de open todo verwijderd en vormen geen
voorwaarde voor v1.0. Opnieuw opnemen gebeurt alleen na een nieuwe afspraak.
De bestaande mogelijkheden en ondersteuningsgrenzen blijven beschreven.

| Punt | Voorlopig uitgestelde uitbreiding |
| --- | --- |
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
| B22 | Restauratie: bepalen of langdurig gekraak en herstel van clipping nodig zijn naast de bestaande korte tikverwijdering. |
| B25 | Dynamics: behoefte aan vooruitblik en andere detectiemethoden bepalen. |
| B29 | Multitrack: behoefte boven 24 uur, 32 sporen of 128 bronbestanden bepalen. |
| B30 | Bijzondere WAV- en recordergegevens: vaststellen welke afgeleide metingen opnieuw berekend of duidelijk afgehandeld moeten worden. |
| B31 | Eindmix: regels bepalen voor het meenemen en samenvoegen van markers en tags uit meerdere bronnen. |
| B32 | Afspelen: fysieke uitvoerlatentie en naadloos lussen afzonderlijk beoordelen en meetbaar toetsen. |
| B34 | Audio-uitvoer: behoefte aan meer dan twee kanalen en multikanaals routering bepalen. |
| B36a | Dithering: instellingen en gedrag bij uitvoer naar een lagere PCM-bitdiepte bepalen. |


## Kanaalbewerkingen — B06/B07 afgerond in 0.22.0

Alleen het gekozen kanaal verschuift bij knippen, verwijderen, trimmen, invoegen,
plakken, tijdrekken, uitklank, genereren en opname. Het andere houdt zijn samples
op de oorspronkelijke posities; kortere audio krijgt gewone opgeslagen eindstilte.
Trimmen zet het gekozen fragment op nul. Mix Paste kan voorbij het einde mengen
zonder latere audio te verschuiven. Gezamenlijke markers/hoofdstukken blijven
bij één kanaal staan; klembordmarkeringen worden alleen bij Beide samengevoegd.

B06/B07 zijn na verificatie van
[0.22.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.22.0)
uit de open todo verwijderd. De [onderbouwing](channel-timing.md) bevat controles,
metadata, opslag, annuleren en publicatie. Er blijven5 gekozen punten en18 uitgestelde
kandidaten. B21 is de volgende stap; B33 en RC blijven vóór v1.0 nodig.


## Ruisreductie — B21 afgerond in 0.23.0

De vaste profielroute blijft behouden. Adaptieve ruisschatting volgt veranderingen
in de achtergrond, met instelbare tijd en bescherming van zachte details. Hoger
detailbehoud laat meer ruis achter. Een profiel blijft nodig en ongeschikt profiel
of aangehouden brede klanken kunnen tot verwarring leiden. Dat zijn praktische
grenzen van de beschikbare verwerking; stemseparatie wordt niet toegevoegd.

De [controle](adaptive-noise.md) toetst ruisverandering, detail, stereo, bronbehoud,
Preview en opslag. Alle vijf handleidingen zijn bijgewerkt en op aanvullend
verzoek voorzien van klikbare blauwe inhoudsopgaven. B21 is na verificatie van
[0.23.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.23.0)
uit de open todo verwijderd. Er blijven4 gekozen punten, 18 uitgesteld en 15 afgehandeld.
B23/B24 volgen; B33 en RC blijven vóór v1.0 nodig.
