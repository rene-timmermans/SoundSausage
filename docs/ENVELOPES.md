# Volume- en panlijnen — prototype 0.3.0

Multitrackclips hebben nu bewerkbare volume- en panlijnen. De punten sturen de C++-mixer per audioframe; afspelen en WAV-export gebruiken dezelfde render. Punten en hun volledige precisie worden in het zelfstandige CELP-project opgeslagen.

## Proberen

Een demonstratie met ingebedde audio staat in `build/demo-envelopes.celp`:

```bash
cd SoundSausage
PYTHONPATH=src python3 tools/make_envelope_demo.py
./run.sh build/demo-envelopes.celp
```

Druk na openen op **Spatie**. De eerste zes seconden demonstreren volumeveranderingen op spoor 1. Van zes tot twaalf seconden beweegt een toon op spoor 2 van links naar rechts. De gewone start gebruikt je desktopthema. De onderstaande afbeeldingen gebruiken een nagebootst donker palet met turquoise accent.

1. Kies **Volume Line** boven de tijdlijn. Klik binnen een clip om een punt toe te voegen en sleep een punt om tijd en volume te veranderen. Onder is 0%, midden 100% en boven 200%.
2. Kies **Pan Line** om de balans te tekenen. Boven is rechts, midden neutraal en onder links. Voor de demo selecteer je hiervoor de clip op spoor 2.
3. Klik met rechts bij een punt voor **Edit Point…** of **Remove Point**. Het venster stelt een exact frame binnen de clip en een waarde in procenten in. Dubbelklikken op een bestaand punt opent hetzelfde venster.
4. **Delete** verwijdert het geselecteerde punt. In een lijnmodus wordt een clip daarmee niet verwijderd. **Esc** annuleert een lopende sleepbeweging.
5. **Reset Line** maakt de gekozen lijn van de geselecteerde clip weer neutraal. Deze actie is ook ongedaan te maken.
6. **Ctrl+Z** en **Ctrl+Shift+Z** herstellen en herhalen lijnbewerkingen. Een sleepbeweging telt als één bewerking, ook als je veel tussenposities probeert.
7. Kies **Move Clips** voor het gewone verplaatsen en trimmen. De clipkop kan ook in een lijnmodus worden versleept. In Move Clips worden bestaande volumelijnen geel en panlijnen paars getoond; de actieve bewerkbare lijn gebruikt je accentkleur.
8. **Ctrl+S** bewaart de sessie met ingebedde audio en punten. **Mix Down…** exporteert de hoorbare mix. Een geselecteerde tijdrange bepaalt de afspeelrange; mixdown exporteert de hele sessie.

Tijdens slepen verandert de zichtbare lijn alvast. De audiogegevens en undo-geschiedenis veranderen pas bij loslaten. Een bevestigde sessiebewerking stopt het huidige afspelen; druk daarna op Spatie om de gewijzigde clip te horen. Er is nog geen verwerking van zulke wijzigingen tijdens lopend afspelen.

| Voorbeeld | Afbeelding |
| --- | --- |
| Volumelijn met punten | [Qt-screenshot](screenshots/demo-volume-line-v03.png) |
| Panlijn van links naar rechts | [Qt-screenshot](screenshots/demo-pan-line-v03.png) |

## Mixregels

Volume is een lineaire amplitudefactor van 0 tot 2. De neutrale waarde is 1, getoond als 100%. De lijn vermenigvuldigt het bestaande clipvolume, spoorvolume en eventuele clipfades.

Pan is een aanvullende lineaire balans van −1 tot +1. Neutraal, 0, laat de bestaande clip- en spoorpan behouden. Een positieve waarde verlaagt links met factor `1 − pan`; een negatieve waarde verlaagt rechts met factor `1 + pan`. Deze balans wordt boven op de bestaande kanaalfactoren toegepast. Bij een clip met een bestaande sterke panstand kan de lijn het al verzwakte kanaal dus niet opnieuw versterken. Zet voor een volledige beweging van links naar rechts de gewone clip- en spoorpan op het midden. Stereo houdt links en rechts gescheiden; er wordt geen kanaal naar het andere gekopieerd.

Tussen punten wordt lineair geïnterpoleerd in amplitude respectievelijk balans. Voor het eerste punt en na het laatste punt blijft de grenswaarde gelden. Eén punt maakt een constante lijn; een lege lijn is neutraal. De interne mix behoudt headroom. Voor PCM-export blijven de bestaande formaat- en begrenzingsregels gelden.

De groene golfvorm blijft de bronaudio tonen. De lijn is een bewerkbare laag erboven; de bron wordt niet herschreven.

## Posities en projecten

Punten gebruiken gehele frames in de volledige bronaudio van de clip. Verplaatsen verandert hun positie ten opzichte van de audio niet. Trimt men een clip, dan blijven de verborgen punten bewaard en wordt de waarde bij de nieuwe rand uit dezelfde curve berekend. Het terug zichtbaar maken van bronmateriaal herstelt daardoor ook de bijbehorende lijn.

Dupliceren deelt de bron, maar elke clip kan zijn eigen lijnen krijgen. Bij **Apply Waveform to Clip** wordt het zichtbare stuk van de lijn naar de nieuwe audiolengte geschaald, met behoud van de waarden aan begin en einde. Punten die daarbij op hetzelfde frame terechtkomen worden samengevoegd. Een vervanging door één frame gebruikt de oorspronkelijke beginwaarde. Undo herstelt zowel de vorige bron als de punten.

Elke lijn ondersteunt maximaal 512 punten. Punten moeten geordend, uniek en binnen de volledige bronaudio liggen. Waarden buiten het ondersteunde bereik, ongeldige frames en niet-eindige getallen worden afgewezen. De projectbeschrijving blijft begrensd tot 2 MiB.

Nieuwe bestanden gebruiken **CELP versie 2**. Projecten van versie 1 blijven te openen met neutrale lijnen. Oudere prototypes die alleen versie 1 kennen weigeren een versie-2-bestand bij openen. Zie [PROJECTFORMAAT.md](PROJECTFORMAAT.md).

## Controle en grenzen

De 111 geautomatiseerde tests slagen; zie [de testuitvoer](validation/test-results-envelopes.log). Toegevoegd zijn controles met handmatig berekende samples, stereo zonder kanaaloverspraak, volume/pan samen met bestaande gain en fades, exact gelijke gedeeltelijke renders, trimmen/terughalen, verplaatsen, dupliceren, bronvervanging, één-frameclips en ongeldige punten.

De GUI-tests gebruiken echte Qt-muisevents voor puntbewerkingen, annuleren met Esc, verwijderen met Delete, exacte invoer en verplaatsen via de clipkop. Ze controleren één undo per sleepbeweging, behoud bij opslaan/heropenen en daadwerkelijk doorgeven van de geautomatiseerde selectie aan de afspeeladapter. Die laatste controle onderschept het afspeelverzoek; er wordt daarbij geen fysiek audioapparaat gebruikt. Float32-mixdown wordt teruggelezen en vergeleken. De drie eerder aangeleverde oorspronkelijke PCM16-mixdowns blijven hun exacte gemeenschappelijke audio behouden.

Het bestaande gebruikersproject is alleen gelezen en was daarna byte voor byte ongewijzigd. De demo-mix is onafhankelijk van de GUI opnieuw geladen; aaneengevoegde gedeeltelijke renders zijn exact gelijk aan de volledige demo-render. Twee echte Qt-screenshots zijn op 1180 × 720 pixels gemaakt.

Deze lijnen zijn nieuwe native functionaliteit. Hun interpolatie en gedrag zijn nog niet met een oorspronkelijke automation-export vergeleken. De SES-import blijft daarom niet-neutrale automation weigeren totdat broncoördinaten, puntvelden en interpolatie van dat formaat zijn gevalideerd. Er wordt niet naar SES teruggeschreven.

De demo opnieuw genereren, met voorbeelden:

```bash
PYTHONPATH=src python3 tools/make_envelope_demo.py --screenshots
```
