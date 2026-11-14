# Open punten richting v1.0

Stand: 14 november 2026, SoundSausage 0.21.0.

De scope voor de eerste v1 bestaat uit **zeven punten**: B06, B07, B21, B23,
B24, B33 en B36b. De overige uitbreidingen zijn voorlopig uitgesteld en staan
in het [besluitenoverzicht](validation/beperkingen-keuzes.md). Ze worden alleen
na een nieuwe afspraak opnieuw opgenomen. De technische ondersteuning en
huidige grenzen blijven beschreven in [STATUS](STATUS.md).

De vaste nummers blijven behouden. Werk elk gekozen punt af met passende
controles, Undo/Redo en opslag waar van toepassing, bijgewerkte uitleg in alle
vijf handleidingen en geteste pakketten bij een functionele release.
Afgeronde punten verdwijnen uit deze open lijst; hun resultaat blijft bewaard.

## Nu uitwerken: B06 en B07 — kanaalbewerkingen

De implementatie voor 0.22.0 is gereed voor verificatie. Alleen het gekozen
kanaal verschuift; het andere behoudt zijn samples en posities. Het kortere
kanaal krijgt achteraan stilte. Dezelfde regels gelden voor knippen, trimmen,
invoegen, plakken, tijdrekken, uitklank, genereren en opnemen. Zie de
[uitwerking en controles](validation/channel-timing.md).

B06/B07 blijven open tot de distributiecontroles en publicatie afgerond zijn.
Daarna volgt B21; de overige gekozen punten blijven hieronder staan.

## De zeven gekozen punten

| Punt | Uitwerking |
| --- | --- |
| B06 | Knippen, verwijderen, trimmen, duurwijzigingen en opname op één stereokanaal; het gedrag en de uitlijning van beide kanalen vastleggen. |
| B07 | Plakken op één kanaal met verschillende lengtes en Mix Paste voorbij de bestaande lengte, met passende opvulling en kanaaluitlijning. |
| B21 | Ruisreductie voor wisselende achtergrondruis en beter behoud van zachte details. |
| B23 | Automatische uitklank en langere galm/echo beoordelen en uitwerken, met beheerste feedback en ruimtegebruik. |
| B24 | Hoorbare selectieranden bij EQ/filters verbeteren en het gewenste fasegedrag bepalen. |
| B36b | Markereditor: markers toevoegen, verplaatsen, benoemen en verwijderen, met behoud bij bewerken en opslaan. |
| B33 | De afgeronde app fysiek toetsen: kalibratie, langere overdub, punch/heropenen en echte VST3-/LV2-vensters met statusopslag. |

## Afronden naar de eerste v1

1. B06/B07, daarna B21, B23/B24 en B36b functioneel afronden.
2. B33 uitvoeren met de afgeronde app; de gewone B910/HDMI-proef blijft al bevestigd.
3. Een releasecandidate bouwen en toetsen op de dagelijkse workflow, vijf talen,
   offlinehandleidingen en installatiepakketten voor Debian/Ubuntu, Fedora en Arch.
4. Gevonden blokkerende fouten oplossen en de eerste v1.0 publiceren met korte
   releasepunten en geteste installers.

B33 staat na de functionele punten zodat de praktijkcontrole de afgeronde app
betreft. Een concrete v1-datum volgt uit de resultaten van deze stappen.
