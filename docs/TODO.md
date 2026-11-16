# Voortgang en vervolg

## Effectkeuze en expliciete selectie — 1.2.1 in uitvoering

De uitklaplijsten links kiezen alleen het actieve effect; een hoofdklik voert uit of opent de instellingen. De menuopdrachten en herhalen met F2 vereisen een expliciete tijdselectie. Zonder selectie wordt geen golfvormeffect toegepast; Ctrl+A kiest de volledige opname. Kanaalkeuze, instellingenvensters, Undo, opnamevergrendeling en werkbalkvoorkeuren blijven behouden. De vijf handleidingen en aanwijzingen beschrijven de bediening. Gerichte regressiecontroles en de distributiebouw worden afgerond. De 18 uitgestelde uitbreidingen blijven uitgesteld.


## Compactere werkruimte — 1.2.0 gepubliceerd

De algemene werkbalk bevat nu ook de markeringsknoppen. Golfvormgereedschappen staan samen onder Bewerken; clipgereedschappen verschijnen in multitrack. Ompolen, Achterstevoren en Stilte delen het submenu Golfvormbewerkingen met de linker effectgroep. De vaste optiebalk maakt plaats voor kanaalkeuze direct boven de golfvorm, een numerieke sampleknop tijdens tekenen en clipbediening boven de multitracktijdlijn. De twee verplaatsbare werkbalken behouden hun aan/uit-keuzes en voorkeuren. Bestaande indelingen worden overgenomen zonder de vroegere optiebalk. De vijf handleidingen beschrijven de bediening.

Alle **664 tests** slagen zonder overslaan op Debian, Fedora en Arch. Vijf geïnstalleerde zelftests slagen op elk van vijf doelen, inclusief Ubuntu 26.04 en Rolling. De acht releasebestanden, tag, bron en releasepunten zijn gecontroleerd. De catalogi bevatten 1551 bronvormen zonder ontbrekende vertaling; de handleidingindexen zijn actueel. Er staan geen open punten voor deze update. De 18 uitgestelde uitbreidingen blijven uitgesteld.

## Titelruimte in voortgangsvensters — afgerond in 1.1.2

Het gedeelde voortgangsvenster heeft voldoende ruimte voor de volledige programmatitel en de titelbalkknoppen. De minimale breedte volgt de titel- en inhoudslettergrootte, ook bij korte voortgangsteksten. Annuleren en de audioverwerking blijven gelijk. Gerichte controles voor annuleren, herstel en tekstuitlijning slagen. Alle **662 tests** slagen zonder overslaan op Debian, Fedora en Arch. Vijf geïnstalleerde zelftests slagen op vijf doelen, inclusief Ubuntu 26.04 en Rolling. De acht releasebestanden, tag, bron en releasepunten zijn gecontroleerd. Geen open punten voor deze correctie.

## Uitklapbare effectgroepen — afgerond in 1.1.1

- Effectgroepen op de linker werkbalk, met dezelfde opdrachten als het menu Effecten.
- Pijltje voor de lijst en hoofdicoon voor het laatst gebruikte effect; keuze per groep onthouden.
- Golfvormbewerkingen en Remaster rechtstreeks bereikbaar; spooreffecten in multitrack.
- Bestaande kanaalkeuze, Undo en opnamevergrendeling blijven gelden. Niet-beschikbare effecten zijn uitgeschakeld.
- Alle vijf handleidingen en vertalingen bijgewerkt.

Alle **662 tests** slagen zonder overslaan op Debian, Fedora en Arch. Vijf geïnstalleerde zelftests slagen op vijf doelen, inclusief Ubuntu 26.04 en Rolling. De acht releasebestanden, tag, bron en releasepunten zijn gecontroleerd. Er staan geen open punten voor deze update. De 18 uitgestelde uitbreidingen blijven uitgesteld.

## Werkbalkvernieuwing — afgerond in 1.1.0

- Algemene knoppen bovenaan, een horizontale gereedschapsoptiebalk daaronder en een aparte verticale gereedschapsbalk standaard links.
- Selecteren/tekenen voor golfvormen en clips verplaatsen/volume-/panlijnen voor multitrack, met passende opties en kanaalkeuze.
- Pictogramknoppen zonder vaste kaders, met accentkleur en herkenbare actieve, hover-, focus- en uitgeschakelde toestanden.
- Verplaatsen, herordenen, losmaken en vastzetten via zichtbare handgrepen.
- Afzonderlijke aan/uit-keuzes via **Beeld → Werkbalken**, met behoud van indeling, zichtbaarheid en werkbalkteksten bij herstart.
- Dubbele zoomgroep bovenaan verwijderd; de vier knoppen onderaan, menuopdrachten en sneltoetsen blijven beschikbaar.
- Alle vijf handleidingen en vertalingen bijgewerkt.

Alle **657 tests** slagen zonder overslaan op Debian, Fedora en Arch. Vijf geïnstalleerde zelftests slagen op vijf doelen, inclusief Ubuntu 26.04 en Rolling. De acht releasebestanden, tag, bron en releasepunten zijn gecontroleerd. Alle afgesproken werkbalkverbeteringen zijn afgerond; er staan geen open punten voor deze update. De 18 eerder uitgestelde uitbreidingen blijven uitgesteld.

## Afgeronde functionele basis

0.27.2 bevat correctie van gemeten opnameverschuivingen na pauzes,
een zelfstandig handleidingvenster en volledig vertaalde multitrackknoppen.
Klikken tijdens afspelen verplaatst de afspeelpositie. De VST3-host accepteert
optionele ongebruikte aansluitingen en bewaart de instellingen van TAL-Reverb-4.

B36b is functioneel uitgewerkt: markereditor voor golfvormen en sessies, met
Undo/Redo, bewaren/heropenen en WAV/MP3-export. De
[controles](validation/markers-and-remaster.md) leggen de dekking vast.
B23/B24 zijn afgerond in 0.24.0, B21 in 0.23.0 en B06/B07 in 0.22.0.
De overige 18 uitbreidingen blijven [uitgesteld](validation/beperkingen-keuzes.md)
en keren alleen na een nieuwe afspraak terug. Bronmarkers automatisch samenvoegen
in een eindmix blijft daaronder vallen (B31).

Remaster is aanvullend uitgewerkt op het expliciete verzoek voor pompende
muziekopnamen. De functie biedt instelbaar herstel en origineel/voorbeeld op gelijk
luistervolume. Numerieke proeven en een eerste luistervergelijking bevestigen verbetering.
De extra regeling voor korte volumedalingen is gepubliceerd in 0.27.0;
de luisterproeven op beide praktijkopnamen zijn positief en de balans is goed.
De regeling kan verder naar smaak worden afgesteld. Zie de
[controles](validation/remaster-short-drops.md). De oorspronkelijke bronbestanden blijven
bij de proeven ongewijzigd.

Remaster is praktisch goedgekeurd op beide voorbeeldopnamen. De venstergrootte
blijft bewaard; centraal starten is als gewenste werkwijze geaccepteerd. Deze
punten vragen geen verdere wijziging voor v1.0. De markerproef met toevoegen,
benoemen, verslepen, Undo/Redo, WAV-opslag en heropenen is eveneens bevestigd.

## B33 — fysieke praktijkcontrole afgerond

| Proef | Stand |
| --- | --- |
| Gewone B910/HDMI-opname, pauzeren/hervatten en terugluisteren | Bevestigd. |
| Afspelen in volledig scherm | Haperen verdwenen, fysiek bevestigd in 0.25.2. |
| Afspeelpositie aanklikken tijdens afspelen | Bevestigd na bijwerken naar 0.27.1: geluid, cursor en klok volgen de aangeklikte plek. |
| Kalibratie met de eigen in-/uitgangsroute | Bevestigd: de opgeslagen correctie van −47,821 ms wordt met B910, 48000 Hz, Stereo, ingangskanaal 1 en automatische synchronisatie teruggevonden. |
| Langere overdub en klokdrift | Bevestigd: lange opname met 68 herkenbare meetpulsen en herhaalproef in 0.27.2 met 24 betrouwbare pulsen. Rond de pauze circa 0,04 ms verschil, tegenover circa 10,7 ms in de vorige proef. Bron en opgeslagen resultaat ongewijzigd. |
| Punch-in/out, opslaan en heropenen | Bevestigd: alleen het interval vervangen; omliggende audio, referentiespoor en markeringen behouden. Opgeslagen sessie opnieuw ingelezen. |
| Systeemgeluid van de eigen hoofduitgang | Bevestigd: opnemen, pauzeren/hervatten, terugluisteren en WAV/MP3-export. Beide exports opnieuw geopend. |
| Echt plug-invenster, parameters en heropende plug-instatus | TAL-Reverb-4 (VST3) bevestigd: eigen venster, wijzigen, terugluisteren en behoud van waarden en geluid na bewaren/heropenen. LV2-vensters hebben automatische testdekking. |

## Eerste v1 afgerond

1. B33 is afgerond; reeds bevestigde proeven blijven bevestigd.
2. Een releasecandidate toetsen op dagelijkse workflow, vijf talen,
   offlinehandleidingen en Debian/Ubuntu-, Fedora- en Arch-pakketten.
   Afgerond op de geteste 0.27.2-basis. Het zelfstandige handleidingvenster is
   ook in de praktijk bevestigd, inclusief bediening naast de editor.
3. De definitieve 1.0.0-pakketten zijn gebouwd, getest, geïnstalleerd en
   gepubliceerd. Alle 640 tests slagen zonder overslaan op Debian/Fedora/Arch;
   vijf geïnstalleerde zelftests slagen op vijf doelen.

## Vervolgupdate 1.0.1 afgerond

- Begin, Einde en Lengte rechtsonder zijn uitgewerkt voor selectie en zichtbaar
  bereik. Invoer, grenzen, annuleren en behoud van audio/Undo zijn lokaal getoetst.
- De vijf handleidingen hebben een nieuw geïndexeerd onderwerp met voorbeelden.
- Alle 649 tests slagen zonder overslaan op Debian/Fedora/Arch. Vijf
  geïnstalleerde zelftests slagen op vijf doelen; pakketten en release zijn
  gepubliceerd en gecontroleerd. De afgesproken wijzigingen zijn afgerond.

De handleidingen zijn via Help/F1 beschikbaar. Werk bij wijzigingen de klikbare
index bij met `python3 tools/index_manuals.py`. De eerste stabiele versie is op
15 november 2026 gepubliceerd.
