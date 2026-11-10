# Volume- en panlijnen

Met volume- en panlijnen verander je het volume en de stereobalans gedurende een clip. Je plaatst punten op de lijn; tussen de punten verloopt de verandering geleidelijk. De lijnen werken door in afspelen en mixdown en blijven samen met de audio bewaard in het project.

## Proberen

Open vanuit de projectmap het voorbeeld met ingebedde audio:

```bash
./run.sh examples/demo-envelopes.celp
```

Druk op **Spatie** om af te spelen. De eerste zes seconden demonstreren volumeveranderingen op spoor 1. Van zes tot twaalf seconden beweegt een toon op spoor 2 van links naar rechts.

## Een lijn bewerken

1. Kies **Volume Line** boven de tijdlijn. Klik in een clip om een punt toe te voegen en sleep het om tijd en volume te veranderen. Onder is 0%, midden 100% en boven 200%.
2. Kies **Pan Line** om de balans te tekenen. Boven is rechts, midden neutraal en onder links.
3. Klik met rechts bij een punt en kies **Edit Point…** om de positie in frames en de waarde in procenten precies in te voeren. Dubbelklikken op een punt opent hetzelfde venster.
4. Met **Remove Point** of **Delete** verwijder je het geselecteerde punt. In een lijnmodus blijft de clip zelf daarbij behouden.
5. **Esc** annuleert een lopende sleepbeweging. **Reset Line** maakt de gekozen lijn van de geselecteerde clip weer neutraal.
6. Gebruik **Ctrl+Z** en **Ctrl+Shift+Z** om lijnbewerkingen ongedaan te maken of opnieuw uit te voeren. Een sleepbeweging telt als één bewerking.
7. Kies **Move Clips** voor verplaatsen en trimmen. De clipkop kun je ook tijdens het bewerken van een lijn verslepen.

Een bevestigde wijziging stopt het afspelen. Druk opnieuw op Spatie om het resultaat te horen. Met **Ctrl+S** sla je de sessie op; **Mix Down…** exporteert de hele sessie als WAV. Een geselecteerd tijdbereik bepaalt alleen welk deel wordt afgespeeld.

| Voorbeeld | Afbeelding |
| --- | --- |
| Volumelijn met punten | [Volumelijn](screenshots/demo-volume-line-v03.png) |
| Panlijn van links naar rechts | [Panlijn](screenshots/demo-pan-line-v03.png) |

## Volume en balans

De volumelijn vermenigvuldigt het bestaande clipvolume, spoorvolume en eventuele fades. De neutrale waarde is 100%. Een lege lijn is neutraal; één punt stelt een constante waarde in. Voor het eerste punt en na het laatste punt blijft de waarde van dat eindpunt gelden.

De panlijn werkt boven op de gewone clip- en spoorpan. Zet beide gewone paninstellingen in het midden voor een volledige beweging van links naar rechts. Een al verzwakt kanaal wordt door de lijn niet opnieuw versterkt. Bij stereoaudio blijven links en rechts gescheiden; de panlijn kopieert geen geluid naar het andere kanaal.

De groene golfvorm toont de bronaudio. De lijnen veranderen het hoorbare resultaat zonder die bron te herschrijven.

## Verplaatsen, trimmen en opslaan

De punten blijven aan dezelfde plek in de bronaudio gekoppeld wanneer je een clip verplaatst. Bij trimmen blijven verborgen punten bewaard; verlengen maakt ze weer zichtbaar. Duplicaten delen de audio, maar kunnen elk hun eigen lijnen hebben.

Met **Apply Waveform to Clip** vervang je de audio van een clip door de bewerkte golfvorm. De lijn wordt naar de nieuwe lengte geschaald, met behoud van de waarden aan begin en einde. Undo herstelt zowel de vorige audio als de punten.

CELP-versie 2 bewaart beide lijnen. Oudere versie-1-projecten openen met neutrale lijnen. Zie [het projectformaat](PROJECTFORMAAT.md).

## Grenzen

- Elke lijn ondersteunt maximaal 512 punten.
- De mix wordt vóór afspelen berekend; wijzigingen tijdens lopend afspelen worden nog niet direct hoorbaar.
- De import van oudere `.ses`-bestanden ondersteunt nog geen veranderende volume- of panlijnen.
