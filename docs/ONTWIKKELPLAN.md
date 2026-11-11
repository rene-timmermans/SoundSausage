# Afgesproken ontwikkelroute

De bouwvolgorde versterkt eerst de basis van SoundSausage. Daarna worden de
overige effecten en tools per groep afgemaakt. Iedere afgeronde stap krijgt
passende controles, een bijgewerkte handleiding en een release met pakketten.

## 1. Audiobasis

Geïntegreerd afspelen, keuze van uitvoerapparaat, synchronisatie van geluid,
cursor en meters, en omgaan met verschillende samplerates.

**Stand:** beschikbaar sinds 0.6.0 en automatisch gecontroleerd op de ondersteunde
distributies. De praktische opname-/afspeelcontrole met een USB-microfoon is bevestigd.

## 2. Langere bestanden en betrouwbare bewerkingen

**Afgerond in 0.7.0, met geteste installatiepakketten voor Debian/Ubuntu, Fedora en Arch.**

- [x] Audio in kleinere blokken verwerken.
- [x] De grens van 128 MiB vervangen door geschikte opslag voor grotere bestanden.
- [x] Afspelen, golfvormweergave en multitrack laten werken met die opslag.
- [x] Voortgang en annuleren bij langere bewerkingen toevoegen.
- [x] Annuleren laat audio, selectie en Undo/Redo intact.
- [x] Crashherstel toevoegen voor niet-opgeslagen werk.
- [x] Bestandsinformatie bij openen, bewerken en opslaan behouden waar ondersteund.
- [x] De bestaande Amplitude-effecten gebruiken om de nieuwe verwerking te toetsen.
- [x] Langere opnamen en herstel na onderbreking controleren.
- [x] De handleiding, beperkingen en releasepunten bijwerken.
- [x] Alle 210 controles en de geïnstalleerde pakketten op de ondersteunde distributies toetsen.

Een grotere limiet alleen is onvoldoende: grote bestanden moeten te openen,
bewerken, beluisteren en bewaren zijn zonder dat steeds de hele opname in het
geheugen nodig is. Bevestigde bewerkingen blijven één stap in Undo/Redo.

## 3. De dagelijkse werkwijze afronden — afgerond in 0.8.0

Openen, opnemen, bewerken, meerdere sporen combineren, opslaan, heropenen en
exporteren moeten samen soepel werken. De volledige keten krijgt controles
met echte geluidsapparaten, naast automatische tests.

- [x] Mono/stereo-opname met ingangskeuze en live overzicht.
- [x] Nieuwe golfvorm, invoegen/vervangen en opnemen op een spoor.
- [x] Pauzeren, veilig stoppen, annuleren en behoud bij apparaat-/schijffouten.
- [x] Herstel van een onderbroken take.
- [x] De hele keten van opname tot heropend project en WAV-eindmix automatisch toetsen.
- [x] De handleiding voor opname en dagelijks werken aanvullen.
- [x] Definitieve virtuele in-/uitvoer- en pakketcontroles voor 0.8.0.
- [x] Opnemen en terugluisteren met fysieke microfoon en uitvoer controleren.

De functionaliteit is in 0.8.0 gepubliceerd, met 237 geslaagde controles, geteste
pakketten en bevestigde fysieke opname-/afspeelcontrole. Gelijktijdig opnemen en afspelen, punch-in/out en automatische
latencycompensatie zijn vervolgmogelijkheden, geen huidige functies.

## 4. Overige effecten en tools — actief

Eerst EQ en filters, vervolgens delay en galm, daarna complexere functies zoals
ruisreductie en tijd-/toonhoogtebewerking. Iedere groep wordt bruikbaar afgerond.
Uitgebreide compatibiliteit met oudere sessies en externe plug-ins volgen later.

- [x] EQ en filters, met luistervoorbeeld en frequentierespons — 0.9.0, met geteste installatiepakketten.
- [x] Delay, echo en galm — 0.10.0, met geteste installatiepakketten.
- [ ] Ruisreductie en klikverwijdering.
- [ ] Tijd- en toonhoogtebewerking.
- [ ] Overige aangeboden tools, waaronder vervorming en convolutie.

Deze vijf groepen vullen de eerder afgeronde Amplitude-groep aan.

Iedere groep krijgt meetbare audiocontroles, Undo/Redo, bediening voor selecties
en lange bestanden, bijgewerkte uitleg en een geteste release.

## Open punten blijven zichtbaar

De actuele afvinklijst staat in [voortgang](VOORTGANG.md). Nog openstaande
controles worden bij een nieuwe fase meegenomen. Realtime spooreffecten, multikanaals routering en naadloze lussen gelden pas als
beschikbaar wanneer ze daadwerkelijk zijn gebouwd en gecontroleerd.

De handleiding blijft via Help en F1 bereikbaar en beschrijft alle beschikbare
functies. Korte GitHub-releasepunten noemen alleen toegevoegde functies en
work in progress. De programma's volgen dezelfde presentatiestijl als PixelPickle.
