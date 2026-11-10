# Ontwikkelroute

De huidige ontwikkelvolgorde versterkt eerst de audiobasis en werkt daarna de
resterende effecten en tools per groep af. Iedere afgeronde versie krijgt
releasepunten en geteste installatiepakketten.
De [afgesproken route en open punten](ONTWIKKELPLAN.md) blijven de leidraad.

## 1. Audiobasis — automatisch gecontroleerd (0.6.0)

- [x] Geïntegreerd afspelen zonder een extern afspeelproces.
- [x] Keuze en onthouden van het uitvoerapparaat.
- [x] Cursor en meters volgen de door de audiolaag verwerkte frames.
- [x] Pauzeren, stoppen, lussen en apparaatverlies afhandelen.
- [x] Verschillende samplerates omzetten bij import en afspelen.
- [x] Samplerate van een golfvorm wijzigen met Undo/Redo.
- [x] Automatische controles met een virtueel audioapparaat.
- [ ] Hoorbare controle op een fysiek geluidsapparaat.

In Debian, Fedora en Arch slagen alle 183 controles, inclusief de twee echte
audiobackendcontroles. De geïnstalleerde pakketten doorstaan de gewone en stille
audiocontrole ook op Ubuntu 26.04 en Ubuntu Rolling.
De geheugenlimiet en verwerking van volledige buffers blijven onderdeel van fase 2.

## Handleiding en presentatie — 0.6.1

De handleiding beschrijft alle beschikbare functies en effecten, met voorbeelden.
Ze is via Help → Handleiding en F1 bereikbaar, doorzoekbaar en zonder internet
te lezen. De presentatie volgt PixelPickle; GitHub-releases bevatten korte
toegevoegde functies en work in progress. Nieuwe functies krijgen steeds een
bijgewerkte uitleg in de handleiding.

## 2. Langere bestanden en betrouwbare bewerkingen — eerstvolgend

Verwerking en opslag in blokken, voortgang en annuleren, crashherstel en behoud
van bestandsmetadata. De huidige geheugenlimiet blijft tot deze fase van kracht.
Deze fase volgt op het afronden van de handleiding en release 0.6.1.

## 3. Dagelijkse werkwijze — gepland

Opnemen en de volledige keten van openen, bewerken, multitrack, opslaan,
heropenen en exporteren toetsen.

## 4. Effecten en tools — gepland

EQ en filters, delay en galm, daarna restauratie en tijd-/toonhoogtebewerking.
Amplitude is beschikbaar sinds 0.5.0 en dient ook als controle voor de nieuwe
audiobasis. Uitgebreide oude SES-compatibiliteit en externe plug-ins volgen later.
