# Open punten richting v1.0

Stand: 14 november 2026, SoundSausage 0.22.0.

Er blijven **vijf gekozen punten**: B21, B23, B24, B36b en B33. B06 en B07 zijn
[afgerond in 0.22.0](validation/channel-timing.md). De overige 18 uitbreidingen
blijven voorlopig uitgesteld en staan in het
[besluitenoverzicht](validation/beperkingen-keuzes.md). Ze komen alleen na een
nieuwe afspraak terug. De technische ondersteuning en huidige grenzen blijven
beschreven in [STATUS](STATUS.md).

De vaste nummers blijven behouden. Werk elk gekozen punt af met passende
controles, Undo/Redo en opslag waar van toepassing, bijgewerkte uitleg in alle
vijf handleidingen en geteste pakketten bij een functionele release.
Afgeronde punten verdwijnen uit deze open lijst; hun resultaat blijft bewaard.

## Nu uitwerken: B21 — ruisreductie

Ruisreductie uitbreiden voor wisselende achtergrondruis en beter behoud van
zachte details. De bestaande profielbewerking en luistervoorbeelden blijven
beschikbaar. Gewenste instellingen toetsen op ruis, zachte signalen, transiënten,
stereo, kanaalkeuze, annuleren en Undo; daarna de vijf handleidingen en pakketten
bijwerken. De softwarewijziging voor B21 is nog niet begonnen.

## De vijf resterende punten

| Punt | Uitwerking |
| --- | --- |
| B21 | Ruisreductie voor wisselende achtergrondruis en beter behoud van zachte details. |
| B23 | Automatische uitklank en langere galm/echo beoordelen en uitwerken, met beheerste feedback en ruimtegebruik. |
| B24 | Hoorbare selectieranden bij EQ/filters verbeteren en het gewenste fasegedrag bepalen. |
| B36b | Markereditor: markers toevoegen, verplaatsen, benoemen en verwijderen, met behoud bij bewerken en opslaan. |
| B33 | De afgeronde app fysiek toetsen: kalibratie, langere overdub, punch/heropenen en echte VST3-/LV2-vensters met statusopslag. |

## Afronden naar de eerste v1

1. B21, daarna B23/B24 en B36b functioneel afronden.
2. B33 uitvoeren met de afgeronde app; de gewone B910/HDMI-proef blijft al bevestigd.
3. Een releasecandidate bouwen en toetsen op de dagelijkse workflow, vijf talen,
   offlinehandleidingen en installatiepakketten voor Debian/Ubuntu, Fedora en Arch.
4. Gevonden blokkerende fouten oplossen en de eerste v1.0 publiceren met korte
   releasepunten en geteste installers.

B33 staat na de functionele punten zodat de praktijkcontrole de afgeronde app
betreft. Een concrete v1-datum volgt uit de resultaten van deze stappen.
