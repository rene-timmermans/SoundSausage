# Ontwikkelroute

De huidige ontwikkelvolgorde versterkt eerst de audiobasis en werkt daarna de
resterende effecten en tools per groep af. Iedere afgeronde versie krijgt
releasepunten en geteste installatiepakketten.

## 1. Audiobasis — in verificatie (0.6.0)

- [x] Geïntegreerd afspelen zonder een extern afspeelproces.
- [x] Keuze en onthouden van het uitvoerapparaat.
- [x] Cursor en meters volgen de door de audiolaag verwerkte frames.
- [x] Pauzeren, stoppen, lussen en apparaatverlies afhandelen.
- [x] Verschillende samplerates omzetten bij import en afspelen.
- [x] Samplerate van een golfvorm wijzigen met Undo/Redo.
- [ ] Automatische controles met een virtueel audioapparaat.
- [ ] Hoorbare controle op een fysiek geluidsapparaat.

Lokaal slagen 181 controles; twee audiobackendcontroles vereisen een privaat
virtueel audioapparaat en worden in de distributiecontainers uitgevoerd.
De geheugenlimiet en verwerking van volledige buffers blijven onderdeel van fase 2.

## 2. Langere bestanden en betrouwbare bewerkingen — gepland

Verwerking en opslag in blokken, voortgang en annuleren, crashherstel en behoud
van bestandsmetadata. De huidige geheugenlimiet blijft tot deze fase van kracht.

## 3. Dagelijkse werkwijze — gepland

Opnemen en de volledige keten van openen, bewerken, multitrack, opslaan,
heropenen en exporteren toetsen.

## 4. Effecten en tools — gepland

EQ en filters, delay en galm, daarna restauratie en tijd-/toonhoogtebewerking.
Amplitude is beschikbaar sinds 0.5.0 en dient ook als controle voor de nieuwe
audiobasis. Uitgebreide oude SES-compatibiliteit en externe plug-ins volgen later.
