# Ontwikkelroute

De huidige ontwikkelvolgorde versterkt eerst de audiobasis en werkt daarna de
resterende effecten en tools per groep af. Iedere afgeronde versie krijgt
releasepunten en geteste installatiepakketten.
De [afgesproken route en open punten](ONTWIKKELPLAN.md) blijven de leidraad.

## 1. Audiobasis — afgerond (0.6.0)

- [x] Geïntegreerd afspelen zonder een extern afspeelproces.
- [x] Keuze en onthouden van het uitvoerapparaat.
- [x] Cursor en meters volgen de door de audiolaag verwerkte frames.
- [x] Pauzeren, stoppen, lussen en apparaatverlies afhandelen.
- [x] Verschillende samplerates omzetten bij import en afspelen.
- [x] Samplerate van een golfvorm wijzigen met Undo/Redo.
- [x] Automatische controles met een virtueel audioapparaat.
- [x] Hoorbare controle op een fysiek geluidsapparaat.

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
De hoorbare controle uit fase 1 is bevestigd.

## 3. Dagelijkse werkwijze — afgerond in 0.8.0

- [x] Opnemen van mono/stereo met blijvende keuze van ingang.
- [x] Live golfvorm, meters en klok, pauze/hervatten en Stop als één Undo-stap.
- [x] Nieuwe golfvorm, invoegen/vervangen en nieuw blok op het gekozen spoor.
- [x] Behoud van de take bij apparaatverlies, schrijffout of geannuleerde verwerking.
- [x] Onderbroken opname apart herstellen; andere actieve instanties overslaan.
- [x] Opnemen → effect → multitrack → opslaan → heropenen → WAV-export toetsen.
- [x] Afspeelcursor na Stop behouden voor hervatten of opnemen op die positie.
- [x] Handleiding en praktische opnamevoorbeelden bijwerken.
- [x] Definitieve distributiecontroles en installatiepakketten voor 0.8.0.
- [x] Fysieke opname-/afspeelcontrole.

Alle 237 controles slagen in Debian, Fedora en Arch, inclusief de echte
virtuele in-/uitvoercontroles. De geïnstalleerde pakketten doorstaan gewone,
afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling.
[Release 0.8.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.8.0)
bevat de geteste installers. Opnemen, pauzeren/hervatten, terugluisteren, cursor
en meters zijn ook met een USB-microfoon in de praktijk bevestigd.
Ook de 160 MiB geheugencontrole bevat nu een opnamebestand en toevoegen aan de
editor; de extra resident geheugengroei bleef ongeveer 17 MiB in dat scenario.
Gelijktijdig opnemen en terugluisteren, punch-in/out en latencycompensatie blijven
vervolgmogelijkheden. De fysieke controle uit fase 1 is daarmee ook afgerond.

## 4. Effecten en tools — actief

Deze fase bestaat uit vijf groepen; elke groep krijgt een bruikbare release.

- [x] EQ en filters — gepubliceerd in 0.9.0.
- [x] Delay, echo en galm — gepubliceerd in 0.10.0.
- [x] Ruisreductie en klikverwijdering — gepubliceerd in 0.11.0.
- [ ] Tijd-/toonhoogtebewerking.
- [ ] Overige tools, waaronder vervorming en convolutie.

De eerste groep is afgerond in [release 0.9.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.9.0).
Alle 258 controles slagen in Debian, Fedora en Arch. De geïnstalleerde pakketten
doorstaan gewone, afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling.
Zie [EQ/filtercontroles](validation/filters.md).

De tweede groep is afgerond in [release 0.10.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.10.0).
Alle 284 controles slagen in Debian, Fedora en Arch. De geïnstalleerde pakketten
doorstaan gewone, afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling.
Zie [delay-/galmcontroles](validation/delay-reverb.md). Deze groep is afgerond.

[Release 0.11.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.11.0)
voegt restauratie toe. Alle 299 controles en pakketcontroles slagen op de ondersteunde
distributies. Drie van de vijf groepen zijn afgerond; tijd-/toonhoogte volgt.
Elke groep krijgt een afzonderlijke bruikbare release.
Amplitude is beschikbaar sinds 0.5.0 en dient ook als controle voor de nieuwe
audiobasis. Uitgebreide oude SES-compatibiliteit en externe plug-ins volgen later.
