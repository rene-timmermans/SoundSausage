# Open punten richting v1.0

Stand: 14 november 2026, volgende build 0.26.0.

B36b is functioneel uitgewerkt: markereditor voor golfvormen en sessies, met
Undo/Redo, bewaren/heropenen en WAV/MP3-export. De
[controles](validation/markers-and-remaster.md) leggen de dekking vast.
B23/B24 zijn afgerond in 0.24.0, B21 in 0.23.0 en B06/B07 in 0.22.0.
De overige 18 uitbreidingen blijven [uitgesteld](validation/beperkingen-keuzes.md)
en keren alleen na een nieuwe afspraak terug. Bronmarkers automatisch samenvoegen
in een eindmix blijft daaronder vallen (B31).

Remaster is aanvullend uitgewerkt op het expliciete verzoek voor pompende
muziekopnamen. De functie biedt instelbaar herstel en origineel/voorbeeld op gelijk
luistervolume. Numerieke proeven bevestigen beperkt herstel; de muzikale uitkomst
vraagt de onderstaande luistercontrole. De oorspronkelijke bronbestanden blijven
bij de proeven ongewijzigd.

## B33 — fysieke praktijkcontrole

| Proef | Stand |
| --- | --- |
| Gewone B910/HDMI-opname, pauzeren/hervatten en terugluisteren | Bevestigd. |
| Afspelen in volledig scherm | Haperen verdwenen, fysiek bevestigd in 0.25.2. |
| Vensterafmetingen na afsluiten/herstarten | Automatisch gecontroleerd; fysiek nog bevestigen. |
| Kalibratie met de eigen in-/uitgangsroute | Open. |
| Langere overdub en klokdrift | Open. |
| Punch-in/out, opslaan en heropenen | Open. |
| Systeemgeluid van de eigen hoofduitgang | Open. |
| Echte VST3-/LV2-vensters, parameters en heropende plug-instatus | Open. |
| Remaster: origineel/voorbeeld bij drums én rustig fragment | Open, op de twee aangeleverde opnamen. |
| Markerbediening in de dagelijkse workflow | Open, samen met de nieuwe build. |

## Afronden naar de eerste v1

1. De 0.26.0-build afronden met volledige tests en geïnstalleerde pakketten.
2. B33 met de afgeronde app uitvoeren; reeds bevestigde proeven blijven bevestigd.
3. Een releasecandidate toetsen op dagelijkse workflow, vijf talen,
   offlinehandleidingen en Debian/Ubuntu-, Fedora- en Arch-pakketten.
4. Blokkerende fouten oplossen en v1.0 publiceren met korte releasepunten.

De handleidingen zijn via Help/F1 beschikbaar. Werk bij wijzigingen de klikbare
index bij met `python3 tools/index_manuals.py`. Een v1-datum volgt uit de proeven.
