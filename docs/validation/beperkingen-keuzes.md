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
| B15 | Externe plug-ins blijven apart geïnstalleerd. Het melden van ontbrekende of gewijzigde plug-ins is gewenst gedrag. Bestanden die bij LV2-status horen, blijven afzonderlijk open als B11. |
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

## Redactionele correctie — B25

De vergelijking met niet nader gespecificeerde historische effecten vervalt.
Die heeft geen toetsbaar productdoel. De concrete eigenschap — piekdetectie
zonder vooruitblik — blijft beschreven en staat nog ter beoordeling in B25.
