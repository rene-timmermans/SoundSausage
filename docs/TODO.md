# Open punten richting v1.0

Stand: 15 november 2026, SoundSausage 0.27.0 gepubliceerd en gecontroleerd.
0.27.1 is in voorbereiding: klikken tijdens afspelen verplaatst de afspeelpositie.

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

## B33 — fysieke praktijkcontrole

| Proef | Stand |
| --- | --- |
| Gewone B910/HDMI-opname, pauzeren/hervatten en terugluisteren | Bevestigd. |
| Afspelen in volledig scherm | Haperen verdwenen, fysiek bevestigd in 0.25.2. |
| Kalibratie met de eigen in-/uitgangsroute | Profiel opgeslagen en op schijf leesbaar; de wisselende melding in het opnamevenster nog controleren. |
| Langere overdub en klokdrift | Bijna drie minuten gemeten met 68 herkenbare meetpulsen. Kleine timingsprong bij hervatten nog controleren. |
| Punch-in/out, opslaan en heropenen | Bevestigd: alleen het interval vervangen; omliggende audio, referentiespoor en markeringen behouden. Opgeslagen sessie opnieuw ingelezen. |
| Systeemgeluid van de eigen hoofduitgang | Bevestigd: opnemen, pauzeren/hervatten, terugluisteren en WAV/MP3-export. Beide exports opnieuw geopend. |
| Echte VST3-/LV2-vensters, parameters en heropende plug-instatus | Open. |

## Afronden naar de eerste v1

1. B33 met de afgeronde app uitvoeren; reeds bevestigde proeven blijven bevestigd.
2. Een releasecandidate toetsen op dagelijkse workflow, vijf talen,
   offlinehandleidingen en Debian/Ubuntu-, Fedora- en Arch-pakketten.
3. Blokkerende fouten oplossen en v1.0 publiceren met korte releasepunten.

De handleidingen zijn via Help/F1 beschikbaar. Werk bij wijzigingen de klikbare
index bij met `python3 tools/index_manuals.py`. Een v1-datum volgt uit de proeven.
