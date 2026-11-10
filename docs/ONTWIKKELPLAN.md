# Afgesproken ontwikkelroute

De bouwvolgorde versterkt eerst de basis van SoundSausage. Daarna worden de
overige effecten en tools per groep afgemaakt. Iedere afgeronde stap krijgt
passende controles, een bijgewerkte handleiding en een release met pakketten.

## 1. Audiobasis

Geïntegreerd afspelen, keuze van uitvoerapparaat, synchronisatie van geluid,
cursor en meters, en omgaan met verschillende samplerates.

**Stand:** beschikbaar sinds 0.6.0 en automatisch gecontroleerd op de ondersteunde
distributies. Een hoorbare controle op fysieke geluidsapparaten blijft open.

## 2. Langere bestanden en betrouwbare bewerkingen

**Gebouwd voor 0.7.0; eindcontrole en pakketpublicatie lopen.**

- [x] Audio in kleinere blokken verwerken.
- [x] De grens van 128 MiB vervangen door geschikte opslag voor grotere bestanden.
- [x] Afspelen, golfvormweergave en multitrack laten werken met die opslag.
- [x] Voortgang en annuleren bij langere bewerkingen toevoegen.
- [x] Annuleren laat audio, selectie en Undo/Redo intact.
- [x] Crashherstel toevoegen voor niet-opgeslagen werk.
- [x] Bestandsinformatie bij openen, bewerken en opslaan behouden waar ondersteund.
- [x] De bestaande Amplitude-effecten gebruiken om de nieuwe verwerking te toetsen.
- [x] Langere opnamen en herstel na onderbreking controleren.
- [ ] De handleiding, beperkingen en releasepunten bijwerken.

Een grotere limiet alleen is onvoldoende: grote bestanden moeten te openen,
bewerken, beluisteren en bewaren zijn zonder dat steeds de hele opname in het
geheugen nodig is. Bevestigde bewerkingen blijven één stap in Undo/Redo.

## 3. De dagelijkse werkwijze afronden

Openen, opnemen, bewerken, meerdere sporen combineren, opslaan, heropenen en
exporteren moeten samen soepel werken. De volledige keten krijgt controles
met echte geluidsapparaten, naast automatische tests.

## 4. Overige effecten en tools

Eerst EQ en filters, vervolgens delay en galm, daarna complexere functies zoals
ruisreductie en tijd-/toonhoogtebewerking. Iedere groep wordt bruikbaar afgerond.
Uitgebreide compatibiliteit met oudere sessies en externe plug-ins volgen later.

## Open punten blijven zichtbaar

De actuele afvinklijst staat in [voortgang](VOORTGANG.md). Nog openstaande
controles worden bij een nieuwe fase meegenomen. Opnemen, realtime
spooreffecten, multikanaals routering en naadloze lussen gelden pas als
beschikbaar wanneer ze daadwerkelijk zijn gebouwd en gecontroleerd.

De handleiding blijft via Help en F1 bereikbaar en beschrijft alle beschikbare
functies. Korte GitHub-releasepunten noemen alleen toegevoegde functies en
work in progress. De programma's volgen dezelfde presentatiestijl als PixelPickle.
