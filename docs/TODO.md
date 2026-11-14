# Open punten richting v1.0

Stand: 14 november 2026, SoundSausage 0.25.0.

Er blijven **twee gekozen punten**: B36b en B33. B23/B24 zijn
[afgerond in 0.24.0](validation/tails-and-boundaries.md), B21 in 0.23.0 en
B06/B07 in 0.22.0. De overige 18 uitbreidingen blijven voorlopig uitgesteld en
staan in het [besluitenoverzicht](validation/beperkingen-keuzes.md). Ze komen
alleen na een nieuwe afspraak terug. De technische ondersteuning en huidige
grenzen blijven beschreven in [STATUS](STATUS.md).

De vaste nummers blijven behouden. Werk elk gekozen punt af met passende
controles, Undo/Redo en opslag waar van toepassing, uitleg in alle vijf
handleidingen en geteste pakketten bij een functionele release. Werk na
handleidingwijzigingen de klikbare index bij met `python3 tools/index_manuals.py`.
Afgeronde punten verdwijnen uit deze open lijst; hun resultaat blijft bewaard.

## Nu uitwerken: B36b — markereditor

Markers toevoegen, verplaatsen, benoemen en verwijderen, met behoud bij bewerken,
Undo/Redo, opslaan en heropenen. De bestaande cue- en hoofdstukgegevens vormen
de basis; het samenvoegen van bronmarkers in een eindmix blijft het uitgestelde B31.
De softwarewijziging voor B36b is nog niet begonnen.

## De twee resterende punten

| Punt | Uitwerking |
| --- | --- |
| B36b | Markereditor: markers toevoegen, verplaatsen, benoemen en verwijderen, met behoud bij bewerken en opslaan. |
| B33 | De afgeronde app fysiek toetsen: kalibratie, langere overdub, punch/heropenen, systeemgeluid en echte VST3-/LV2-vensters met statusopslag. |

## Afronden naar de eerste v1

1. B36b functioneel afronden.
2. B33 uitvoeren met de afgeronde app; de gewone B910/HDMI-proef blijft al bevestigd.
3. Een releasecandidate bouwen en toetsen op dagelijkse workflow, vijf talen,
   offlinehandleidingen en pakketten voor Debian/Ubuntu, Fedora en Arch.
4. Gevonden blokkerende fouten oplossen en de eerste v1.0 publiceren met korte
   releasepunten en geteste installers.

B33 staat na de functionele punten zodat de praktijkcontrole de afgeronde app
betreft. Een concrete v1-datum volgt uit de resultaten van deze stappen.
