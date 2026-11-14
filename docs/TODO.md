# Open punten richting v1.0

Stand: 14 november 2026, SoundSausage 0.23.0.

Er blijven **vier gekozen punten**: B23, B24, B36b en B33. B21 is
[afgerond in 0.23.0](validation/adaptive-noise.md); B06/B07 in 0.22.0.
De overige 18 uitbreidingen blijven voorlopig uitgesteld en staan in het
[besluitenoverzicht](validation/beperkingen-keuzes.md). Ze komen alleen na een
nieuwe afspraak terug. De technische ondersteuning en huidige grenzen blijven
beschreven in [STATUS](STATUS.md).

De vaste nummers blijven behouden. Werk elk gekozen punt af met passende
controles, Undo/Redo en opslag waar van toepassing, uitleg in alle vijf
handleidingen en geteste pakketten bij een functionele release. Werk na
handleidingwijzigingen de klikbare index bij met `python3 tools/index_manuals.py`.
Afgeronde punten verdwijnen uit deze open lijst; hun resultaat blijft bewaard.

## Nu uitwerken: B23/B24 — uitklank en filterranden

Automatische uitklank en langere galm/echo beoordelen en uitwerken, met beheerste
feedback en ruimtegebruik. Daarna hoorbare overgangen aan selectieranden van
EQ/filters verbeteren en het gewenste fasegedrag bepalen. Realtime ketengrenzen
uit het uitgestelde B17 worden hiermee niet vanzelf opnieuw onderdeel van de scope.
De softwarewijziging voor B23/B24 is nog niet begonnen.

## De vier resterende punten

| Punt | Uitwerking |
| --- | --- |
| B23 | Automatische uitklank en langere galm/echo beoordelen en uitwerken, met beheerste feedback en ruimtegebruik. |
| B24 | Hoorbare selectieranden bij EQ/filters verbeteren en het gewenste fasegedrag bepalen. |
| B36b | Markereditor: markers toevoegen, verplaatsen, benoemen en verwijderen, met behoud bij bewerken en opslaan. |
| B33 | De afgeronde app fysiek toetsen: kalibratie, langere overdub, punch/heropenen en echte VST3-/LV2-vensters met statusopslag. |

## Afronden naar de eerste v1

1. B23/B24 en daarna B36b functioneel afronden.
2. B33 uitvoeren met de afgeronde app; de gewone B910/HDMI-proef blijft al bevestigd.
3. Een releasecandidate bouwen en toetsen op dagelijkse workflow, vijf talen,
   offlinehandleidingen en pakketten voor Debian/Ubuntu, Fedora en Arch.
4. Gevonden blokkerende fouten oplossen en de eerste v1.0 publiceren met korte
   releasepunten en geteste installers.

B33 staat na de functionele punten zodat de praktijkcontrole de afgeronde app
betreft. Een concrete v1-datum volgt uit de resultaten van deze stappen.
