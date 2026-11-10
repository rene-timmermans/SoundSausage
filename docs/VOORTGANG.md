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

## 2. Langere bestanden en betrouwbare bewerkingen — afgerond in 0.7.0

- [x] Grote audiobuffers op schijf; de grens van 128 MiB vervalt.
- [x] WAV, Amplitude, samplerates, afspelen, multitrack en projecten in blokken.
- [x] Herbruikbare golfvormoverzichten en navigatie voorbij 32-bit frameposities.
- [x] Voortgang en annuleren; documentstand en bestaande bestanden blijven intact.
- [x] Herstel van golfvorm en sessie na onverwacht afsluiten, ook na een tweede crash.
- [x] WAV-tekst, cuepunten, labels en ondersteunde positiegegevens behouden.
- [x] Amplitude vergelijken bij verschillende blokgroottes, inclusief Dynamics en Normalize.
- [x] Lange bestanden, Undo/Redo, metadata en crashherstel automatisch toetsen.
- [x] Handleiding voor lange opnamen, werkruimte, annuleren en herstel.
- [x] Definitieve distributiecontroles en publicatie van installatiepakketten.

Alle 210 controles slagen in Debian, Fedora en Arch, inclusief virtuele audio.
De geïnstalleerde pakketten doorstaan de installatie- en stille audiocontrole ook
op Ubuntu 26.04 en Rolling. [Release 0.7.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.7.0)
bevat de installers en korte releasepunten.

Een gecontroleerde keten met 160 MiB audio bleef lokaal op ongeveer 17 MiB extra
resident werkgeheugen boven de geladen toepassing. Dit is een meetresultaat van
die synthetische opname, geen vaste bovengrens voor ieder project. Herstel begint
met een nieuwe Undo-geschiedenis. Bijzondere recordergegevens worden letterlijk
bewaard; afgeleide metingen worden niet opnieuw berekend. Zie
[lange bestanden en herstel](LANGE_BESTANDEN.md) voor ruimtegebruik en grenzen.
De hoorbare controle uit fase 1 blijft open.

## 3. Dagelijkse werkwijze — eerstvolgende fase

Opnemen en de volledige keten van openen, bewerken, multitrack, opslaan,
heropenen en exporteren toetsen.

## 4. Effecten en tools — gepland

EQ en filters, delay en galm, daarna restauratie en tijd-/toonhoogtebewerking.
Amplitude is beschikbaar sinds 0.5.0 en dient ook als controle voor de nieuwe
audiobasis. Uitgebreide oude SES-compatibiliteit en externe plug-ins volgen later.
