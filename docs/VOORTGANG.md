# Ontwikkelroute

## Actuele stand richting v1.0 — 14 november 2026

SoundSausage 0.25.2 corrigeert haperend afspelen bij volledig scherm en grote
vensters. De golfvorm krijgt een herbruikbaar beeld; zoomen en formaatwisselingen
bereiden piekgegevens tijdens afspelen op de achtergrond voor. Cursor en meters
worden maximaal dertigmaal per seconde getekend; de audioklok blijft onafhankelijk.
De lege werkruimte blijft leeg.

Lokale gerichte controles en de nieuwe weergaveregressies slagen. De volledige
pakket- en audiocontroles moeten vóór publicatie nog slagen. Zie de
[controlebeschrijving](validation/fullscreen-playback.md).

Er blijven twee gekozen v1-punten: **B36b en B33**. De overige 18 blijven uitgesteld.
Daarna volgen een releasecandidate en v1.0. De [todo](TODO.md) en het
[ontwikkelplan](ONTWIKKELPLAN.md) blijven leidend.

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

## 4. Effecten en tools — afgerond in 0.13.0

Deze fase bestaat uit vijf groepen; elke groep krijgt een bruikbare release.

- [x] EQ en filters — gepubliceerd in 0.9.0.
- [x] Delay, echo en galm — gepubliceerd in 0.10.0.
- [x] Ruisreductie en klikverwijdering — gepubliceerd in 0.11.0.
- [x] Tijd-/toonhoogtebewerking — gepubliceerd in 0.12.0.
- [x] Vervorming en convolutie — gepubliceerd in 0.13.0.

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
distributies. Deze groep is afgerond.

[Release 0.12.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.12.0)
voegt tijd- en toonhoogtebewerking toe. Alle 308 controles en de geïnstalleerde
pakketten slagen op de ondersteunde distributies. Deze groep is afgerond.

[Release 0.13.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.13.0)
rondt de vijfde groep af met vervorming en convolutie. Alle 322 controles slagen
in Debian, Fedora en Arch; de geïnstalleerde pakketten doorstaan gewone, afspeel-
en opnamecontroles ook op Ubuntu 26.04 en Rolling. Alle vijf afgesproken groepen
zijn nu beschikbaar, met bijgewerkte handleiding en installatiepakketten.
Elke groep krijgt een afzonderlijke bruikbare release.
Amplitude is beschikbaar sinds 0.5.0 en dient ook als controle voor de nieuwe
audiobasis. Uitgebreide oude SES-compatibiliteit en externe plug-ins volgen later.

## Bediening en golfvormweergave — 0.14.0

- [x] Doorlopende min/max-contour bij tussenliggende zoomniveaus, ook op clips.
- [x] Links/rechts kiezen door slepen en Both/Left/Right, met menu en sneltoetsen.
- [x] Effecten en luistervoorbeelden met exact behoud van het andere kanaal.
- [x] Kanaalkeuze in Undo/Redo en herstel; kopiëren en export van één kanaal.
- [x] Gedeelde stereotiming bewaken bij knippen, uitklank en opname.
- [x] Verschillende zoomiconen en eigen iconen voor alle menufuncties.
- [x] Volledige handleiding aanvullen.
- [x] Distributiecontroles en installatiepakketten voor 0.14.0.

De vijf effectgroepen blijven afgerond. Deze versie verfijnt de dagelijkse
bediening. Zie [kanaalselectie](KANAALSELECTIE.md) en de
[regressiecontroles](validation/channel-zoom.md).

[Release 0.14.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.14.0)
bevat de geteste installers. Alle 344 controles slagen in Debian, Fedora en
Arch; de geïnstalleerde pakketten doorstaan gewone, afspeel- en opnamecontroles
ook op Ubuntu 26.04 en Rolling. De geverifieerde logs bevatten geen callback-
of bufferfouten.

## 5. Realtime mixen en uitwisseling — afgerond in 0.15.0

- [x] Realtime spooreffecten en een keten per spoor.
- [x] Mixen in kleine blokken zonder de hele sessie vooraf te berekenen.
- [x] Gelijktijdig opnemen en bestaande sporen beluisteren.
- [x] Externe Linux-effectplug-ins en herstel van hun instellingen.
- [x] Nieuwe projecten volledig opslaan/heropenen met opnamen, spooreffecten en plug-ininstellingen.
- [x] Handleiding en automatische audiocontroles.
- [x] Installatiepakketten en distributiecontroles voor 0.15.0.

De externe host ondersteunt native Linux VST3-stereoeffecten met een generiek
parametervenster. De uitgebreide sessietaak richt zich op nieuwe projecten:
audio, opnamen, ketens en plug-instatus worden samen bewaard en heropend.
Uitbreiding van oude importvarianten hoort niet bij deze stap.

Alle 363 controles slagen in Debian, Fedora en Arch, inclusief virtuele
audiobackend- en duplexcontroles. De geïnstalleerde pakketten doorstaan de
gewone, afspeel-, opname- en duplexzelftest ook op Ubuntu 26.04 en Rolling.
De geverifieerde logs bevatten geen callback- of RingBuffer-fouten.
[Release 0.15.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.15.0)
bevat de geteste installatiepakketten. Zie [realtime-/plug-incontroles](validation/realtime-plugins.md).
Eigen plug-invensters, meer formaten, automatische latency-/driftcompensatie en
punch-in/out blijven vervolgmogelijkheden.

## Meertalige bediening — 0.16.0

- [x] Nederlands, Engels, Duits, Frans en Spaans.
- [x] Taalkeuze onder Opties, direct toepassen en onthouden.
- [x] Geopende effectvensters, meldingen en bediening vertalen zonder modelwijzigingen.
- [x] Volledige offline handleidingen in alle vijf talen, inclusief live wisselen en zoeken.
- [x] Taalregressies en behoud van audio, kanaalkeuze, instellingen en Undo toetsen.
- [x] Definitieve distributiecontroles en publicatie van installatiepakketten.

De effectgroepen en realtime functies blijven afgerond. Eigen plug-invensters,
meer formaten, automatische latency-/driftcompensatie en punch-in/out blijven open.
De fysieke duplexroute en handmatige opnameverschuiving vragen nog een proeftake;
de gewone B910-opname-/afspeelcontrole is eerder bevestigd.

[Release 0.16.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.0)
bevat de installers en broncode. Alle 376 controles slagen in Debian, Fedora
en Arch. De geïnstalleerde pakketten doorstaan gewone, afspeel-, opname- en
duplexzelftests op alle vijf doelen, inclusief Ubuntu 26.04 en Rolling.
Zie [taalcontroles](validation/languages.md).

## Tekstuitlijning en vensterindeling — 0.16.1

- [x] Grafiekassen, meterlabels en tijdvelden aanpassen aan de lettergrootte.
- [x] Golfvormschalen, spoorkoppen, cliptitels en opnameklokken laten meeschalen.
- [x] Effect- en instellingenvensters in alle vijf talen controleren; grote formulieren laten scrollen met bereikbare bevestigingsknoppen.
- [x] Statusbalkkeuze functioneel controleren en bij herstart behouden.
- [x] De vijf handleidingen aanvullen en regressiecontroles toevoegen.
- [x] Definitieve distributiecontroles en installatiepakketten voor 0.16.1.

Zie [tekst- en venstercontroles](validation/text-layout.md). De bestaande
vervolgpunten voor plug-ins en opname blijven behouden.

[Release 0.16.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.1)
bevat de geteste installatiepakketten. Alle 384 controles slagen in Debian,
Fedora en Arch. De geïnstalleerde pakketten doorstaan de gewone, afspeel-,
opname- en duplexzelftest ook op Ubuntu 26.04 en Rolling.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43058515142).

## Linkermarge van astitels — 0.16.2

- [x] Titels boven de curves van Dynamiekbewerking en Volumeverloop links uitlijnen met de overige vensterinhoud.
- [x] Afzonderlijke ruimte voor de aswaarden en de titel behouden; bestaande controles op afsnijding en overlap slagen bij 9, 11 en 14 punten.
- [x] Distributiecontroles en installatiepakketten voor 0.16.2.

[Release 0.16.2](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.2)
bevat de geteste installatiepakketten. Alle 384 controles slagen in Debian,
Fedora en Arch. Gewone, afspeel-, opname- en duplexzelftests slagen na installatie
op alle vijf doelen, inclusief Ubuntu 26.04 en Rolling.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43061345129).

## Opnamebegin en MP3 — 0.17.0

- [x] Eerste opnamemilliseconden instelbaar overslaan, met korte fade-in, onthouden keuze en correcte klok/limiet.
- [x] Blokgrenzen, pauze/hervatten, apparaat-samplerate, Undo en timing met begeleiding toetsen.
- [x] Dunne scheidingslijn tussen links en rechts in golfvorm en live opname.
- [x] MP3 openen/bewerken/importeren en WAV of MP3 kiezen voor opslag, selecties en eindmix.
- [x] ID3-tekst en hoesafbeeldingen behouden; encoderkeuze in herstel en audio in projecten bewaren.
- [x] Voortgang/annuleren, atomaire opslag, fouten en vertaalde formaatkeuze toetsen.
- [x] Vijf offlinehandleidingen en installatieafhankelijkheden bijwerken.
- [x] Praktijkbestanden en definitieve distributiecontroles/installatiepakketten voor 0.17.0 verifiëren.

Zie [opname- en MP3-controles](validation/recording-mp3.md). De bestaande
vervolgpunten voor plug-ins, latency-/driftcompensatie en punch-in/out blijven staan.

Alle 406 controles en de vier geïnstalleerde zelftests op vijf distributiedoelen
slagen voor [0.17.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.0).
De 38 praktijkbestanden zijn geopend, bewerkt en als WAV en MP3 heropend, met
behoud van de originelen.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43070491299).

## Formaatkeuze en opnamevenster — 0.17.1

- [x] De volledige WAV-/MP3-filterlijst in alle vijf talen tonen en de voorkeuze laten overeenkomen.
- [x] Het label van de opnameverschuiving samen met het invoerveld verbergen buiten multitrack.
- [x] Definitieve distributiecontroles en installatiepakketten voor 0.17.1.

[Release 0.17.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.1)
bevat de definitieve installatiepakketten. Alle 406 controles slagen in Debian,
Fedora en Arch; de vier geïnstalleerde zelftests slagen op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43071990484).

## Kanaalranden — 0.17.2

- [x] Onderkant links en bovenkant rechts met twee dunne lijnen begrenzen, binnen de breedte van het tekenvlak.
- [x] Dezelfde afbakening in de live opnameweergave, met een smalle tussenruimte.
- [x] Visuele controle, bestaande selectie-/opname-/indelingscontroles en vijf handleidingen bijwerken.
- [x] Definitieve distributiecontroles en installatiepakketten voor 0.17.2.

[Release 0.17.2](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.2)
bevat de definitieve installatiepakketten. Alle 406 controles slagen in Debian,
Fedora en Arch; de vier geïnstalleerde zelftests slagen op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43075533132).

## Directe samplebewerking — 0.18.0

- [x] Samplepunten bij sterke vergroting en vaste samplepositie tijdens verticaal slepen.
- [x] Exacte invoer per index/kanaal, genormaliseerd of in 8-/16-/24-bitweergave.
- [x] Eén Undo-stap per correctie; omliggende samples, het andere kanaal en metadata behouden.
- [x] Annuleren, selectie met Shift en vergrendeling tijdens opnemen.
- [x] Vijf interfacetalen en offlinehandleidingen bijwerken.
- [x] Definitieve controles en installatiepakketten voor 0.18.0.

[Release 0.18.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.18.0)
bevat de definitieve installatiepakketten. Alle 415 controles slagen in Debian,
Fedora en Arch; de vier geïnstalleerde zelftests slagen op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43078651988).

## Afronding naar v1.0 — software afgerond in 0.19.0

- [x] Eigen Linux VST3-plug-invensters, met parameter-/statusopslag en crashisolatie.
- [x] LV2- en LADSPA-audio-effecten toevoegen, met betrouwbare ontdekking en project-/herstelopslag.
- [x] Automatische compensatie van plug-invertraging bij afspelen en export.
- [x] Kalibratie van de opnamevertraging en compensatie van klokdrift tussen in- en uitvoer.
- [x] Punch-in/out met voorloop en precies begrensde opnamen, Undo en herstel.
- [x] Vijf talen, volledige offlinehandleidingen en distributiecontroles bijwerken.
- [ ] Releasecandidate en fysieke praktijkcontrole vóór v1.0.

V1.0 volgt wanneer deze functies, de dagelijkse werkwijze en de pakketten
geen bekende blokkerende fouten hebben. De vaste apparaat-/plug-incombinaties
worden in de praktijk gecontroleerd; een kalenderdatum volgt uit die resultaten.

### Integratie 0.19.0 — 12 november 2026

Alle 451 controles slagen zonder overslaan op Debian, Fedora en Arch, inclusief
echte Qt/PulseAudio-loopbackkalibratie, automatisch geplaatste opname, native
VST3-/LV2-X11-vensters en de aanvullende native installatiezelftest.
[Broncontrole](https://github.com/rene-timmermans/SoundSausage/actions/runs/43265508881).
De vijf offlinehandleidingen en 1430 bronvormen zijn volledig bijgewerkt.

Duurcorrectie vereist ruim tien seconden bruikbare klokmetingen; kortdurende
backendscheduling verandert de opnamelengte niet. Apparaatkalibratie blijft ook
bij korte opnamen actief. Profielen onderscheiden mono/stereo en het werkelijke
native formaat. Punch-in/out bewaart de oorspronkelijke clips, projectgegevens
en herstelpunten, met één Undo-stap en precies begrensde nieuwe audio.

[Release 0.19.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.0)
is gepubliceerd met geteste installatiepakketten. Alle 451 definitieve tests
slagen zonder overslaan in Debian, Fedora en Arch. De vier geïnstalleerde
zelftests, inclusief native plug-invenster, slagen op alle vijf doelen: Debian,
Fedora, Arch, Ubuntu 26.04 en Ubuntu Rolling. Tag, geteste broncommit, korte
releasepunten en acht assets zijn geverifieerd.
[Definitieve releasebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43268472763).
De volledige [controledekking](validation/completion.md) beschrijft de grenzen.

Vóór v1.0 blijven fysieke kalibratie/overdub/punch en een echte externe plug-in
met eigen venster nodig, gevolgd door een releasecandidate. De gewone B910-
opname-/afspeelproef blijft bevestigd. Zie het [ontwikkelplan](ONTWIKKELPLAN.md).

## Venstericonen — 0.19.1

- [x] Paarse programmategel op alle iconenmaten, ook in titelbalken en losse vensters.
- [x] De vrijstaande mascotte in Over behouden; transparante buitenhoeken blijven intact.
- [x] Vijf offlinehandleidingen bijwerken.
- [x] Bestaande icoon-/Over- en installatiecontroles, definitieve pakketten en publicatie.

[Release 0.19.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.1)
is gepubliceerd met geteste pakketten. Alle 451 controles slagen zonder overslaan
op Debian/Fedora/Arch; de vier installatiezelftests slagen op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling. Kleine en grote venstericonen gebruiken de
paarse tegel; de mascotte binnen Over blijft vrijstaand.
[Definitieve bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43271010006).

## GitHub-projectpagina

De projectpagina groepeert de mogelijkheden onder werkruimte, opname/bewerking,
effecten, multitrack/plug-ins, bestanden/herstel en hulp. De vijf hoofdsecties
zijn Wat het kan, Installeren, Taal, Wat er nieuw is en Licentie.
De installatietabel bevat pakket- en verwijdercommando's voor Arch, Debian/Ubuntu
en Fedora. Het versieoverzicht linkt naar alle 21 gepubliceerde releases.
Bouwinstructies staan bij de uitgebreidere installatiedocumentatie.
De secties, lokale verwijzingen, releaselinks en pakketnamen zijn gecontroleerd.
Appversie 0.19.1 en de resterende praktijkproeven voor v1.0 blijven het uitgangspunt.


## Beperkingen punt voor punt beoordelen

De [open todo](TODO.md) volgt de oorspronkelijke 36 punten met vaste nummers.
Dithering en de markereditor zijn afzonderlijke taken, B36a en B36b.
Negen regels zijn afgevoerd als bewuste werking, formaatkenmerk, al bevestigde
controle of eerder uitgesloten uitbreiding. De
[besluiten en redenen](validation/beperkingen-keuzes.md) blijven bewaard.
Bij aanvang zijn er 28 open deelpunten, met B01 als eerste inhoudelijke beoordeling.
Voor B01 is een tekenmodus gebouwd: samples vervangen door de getekende lijn,
ook uitgezoomd zonder losse punten. Maximaal één seconde per geraakt groepje;
een hele beweging mag meerdere groepen wijzigen. Voorbeeld, annuleren en één
Undo-stap behouden tijdas, metadata en het andere kanaal. Losse punten verschijnen
vanaf twee logische pixels per sample. De definitieve publicatie is afgerond in 0.20.0.

De technische documentatie onderscheidt bediening, ondersteuningsgrenzen en praktijkcontrole.
De vergelijking met historische effecten is verwijderd; het concrete ontbreken
van vooruitblik bij Dynamics blijft ter beoordeling. De softwaretaken van
0.19.0 zijn ook in de eerdere v1.0-checklist als afgerond gemarkeerd.
De todo is aangemaakt en B01 is afgerond in 0.20.0. Er blijven 27 open
deelpunten over, met B03 (MP3-uitvoergrenzen) als volgende beoordeling.
Fysieke kalibratie-/overdub-/punch- en echte plug-inproeven blijven nodig vóór
v1.0. Overige kandidaten worden pas na hun beoordeling uitvoeringswerk.


## Golfvorm tekenen — 0.20.0

- [x] Potloodknop, Bewerken → Golfvorm tekenen en D, ook zonder losse samplepunten.
- [x] Getekende lijn als samplewaarden, zoomafhankelijke groepen tot één seconde per groep.
- [x] Kanaalbehoud, voorbeeld, annuleren en één Undo-stap per hele beweging.
- [x] Eerder zichtbare losse punten met compacte markering en kader onder de muis.
- [x] Vijf volledige handleidingen en catalogi bijwerken.
- [x] Definitieve bron-, installatie- en publicatiecontroles.

[Release 0.20.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.20.0)
is gepubliceerd met geteste pakketten. Alle 460 controles slagen zonder overslaan
op Debian/Fedora/Arch; de vier installatiezelftests slagen op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling. Tag, bron, korte releasepunten en acht assets
zijn gecontroleerd. B01 is uit de [todo](TODO.md) verwijderd; B03 staat klaar
voor beoordeling. De eerdere fysieke v1.0-proeven blijven open onder B33.
[Definitieve bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43296981861).


## MP3-uitvoergrenzen — B03 beoordeeld

De bestaande MP3-uitvoer blijft 128/192/256/320 kb/s bij de dichtstbijzijnde
32/44,1/48 kHz en minimaal 2 ms audio. Lage rates kunnen een lagere bitrate
opleveren dan gevraagd; zeer korte fragmenten kunnen bij decoderen langer
worden. Een matrix met 96 synthetische codecproeven en de twee bestaande
rate-/bitratecontroles onderbouwt het behoud van de huidige grenzen.

B03 is uit de open todo verwijderd en als bewuste bestandskeuze vastgelegd.
Er blijven 26 deelpunten open, met B04 (MP3-metadata) als volgende beoordeling.
De vijf handleidingen leggen de keuze uit. Appversie 0.20.0 blijft
actueel; er is geen functionele wijziging of nieuwe pakketrelease.
Zie [MP3-uitvoercontrole](validation/mp3-output-limits.md).


## MP3-metadata — B04 afgerond in 0.21.0

Hoofdstukken volgen verwijderen, invoegen, trimmen, omkeren, tijdrekken en
selectie-export. Plakken neemt hoofdstukken met nieuwe identificaties en hun
inhoudsopgave mee; algemene bestandstags van de bestemming blijven behouden.
Bekende achterhaalde volumemetingen, vingerafdrukken, encodergegevens en
niet-ondersteunde tijdcodes vervallen bij audioverandering. MP3-export vernieuwt
duur en encoderinformatie en maakt oude byteposities ongeldig. Er worden geen
nieuwe ReplayGain-metingen berekend. Gewone tags en hoesafbeeldingen blijven.

Ondersteunde WAV INFO-velden worden expliciet vertaald. Onbekende, misvormde
of conflicterende velden worden vooraf vermeld; weigeren bewaart het bestaande
doelbestand. Undo, annuleren, fouten, projectopslag en herstel horen bij de
controles. De vijf volledige handleidingen en de installatiezelftest zijn
bijgewerkt; de catalogi bevatten 1435 bronvormen zonder ontbrekende vertalingen.
[Release 0.21.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.21.0)
is gepubliceerd en geverifieerd. Alle 486 controles slagen zonder overslaan
op Debian, Fedora en Arch. Vier installatiezelftests slagen op die drie doelen
en Ubuntu 26.04/Rolling; tag, bron, korte releasepunten en acht assets zijn
gecontroleerd. De duplexzelftest wacht op echte invoer en heeft een regressie
voor vertraagde aanlevering. B04 is uit de todo verwijderd; er blijven 25 punten
open, met B06 als volgende beoordeling. B33 blijft fysiek te controleren.
[Definitieve bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43600100211).


## Scope naar de eerste v1 vastgelegd

De open lijst is beperkt tot de zeven gekozen punten. Achttien uitbreidingen
zijn uitgesteld en met hun oorspronkelijke nummers bewaard in het besluiten-
overzicht. Er zijn geen functies of technische ondersteuningsgrenzen gewijzigd.
De markereditor behoort nu expliciet tot de v1-route; dithering is uitgesteld.
De gewone B910/HDMI-proef blijft bevestigd; B33 vraagt de aanvullende fysieke
synchronisatie-, punch- en plug-inproeven op de afgeronde app.

Deze stap wijzigt uitsluitend planning en overdracht. Appversie 0.21.0 en de
bestaande geteste pakketten blijven actueel.


## Kanaalduur en plakken — B06/B07 afgerond in 0.22.0

- [x] Knippen, verwijderen en trimmen per kanaal; het andere behoudt zijn positie.
- [x] Korter/langer plakken, invoegen en mengen voorbij het einde, met eindstilte.
- [x] Tijdrekken, effect-/convolutie-uitklank, tonen/stilte en opname op één kanaal.
- [x] Gezamenlijke markeringen behouden; metadataopschoning en Undo blijven atomair.
- [x] Blokverwerking, annuleren, WAV/project/herstel, opname- en generatiebediening.
- [x] Vijf handleidingen en vertalingen, inclusief live taalwissel in het opnamevenster.
- [x] Distributiecontroles, installatiepakketten, tag en korte releasepunten geverifieerd.

[0.22.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.22.0)
bevat de installers. Alle 501 tests slagen zonder overslaan op Debian/Fedora/Arch.
Vier geïnstalleerde zelftests slagen op vijf doelen, inclusief Ubuntu 26.04 en
Rolling. Alle 7 jobs van [de bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43606249521)
zijn groen; tag, bron, releasepunten en 8 assets zijn gecontroleerd.

Lokaal 500 volledige controles met 9 expliciete backend/native skips; na de laatste
taalcorrectie 34 gerichte UI/i18n/layout/installatiecontroles groen. Daarnaast 15
opnamevensters voor één kanaal in vijf talen en drie lettergroottes gecontroleerd.
De definitieve distributiebouw bevat ook de nieuwe taalwisselregressie en draait
alle 501 tests. Catalogi: 1440 bronvormen, 0 ontbrekend. Zie de
[onderbouwing](validation/channel-timing.md).

B06/B07 zijn uit de open todo verwijderd. B21 volgt; de overige 18 uitgestelde
kandidaten blijven buiten de afgesproken route. B33 en de releasecandidate
blijven nodig vóór v1.0.


## Ruisreductie en handleidingindex — B21 afgerond in 0.23.0

- [x] Profielgestuurde adaptieve ruisschatting en instelbare aanpassingstijd.
- [x] Detailbehoud met expliciete afweging tussen zachte klanken en resterende ruis.
- [x] Presets Wisselende achtergrond en Fijne details; vaste profielstand behouden.
- [x] Meetproeven op wisselende ruis, spectrum, zachte tonen, aangehouden tonen en aanslagen.
- [x] Kanaalbehoud, stereo, Preview, verwijderd deel, blokken, annuleren, Undo en herhalen.
- [x] Vijf volledige handleidingen met klikbare blauwe inhoudsopgaven en Inhoud-knop.
- [x] Alle onderwerpankers, echte muisklikken, thema-/taalwissel en pakketten getoetst.
- [x] Distributiebouw, tag, korte releasepunten en 8 assets geverifieerd.

[0.23.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.23.0)
bevat de installers. Alle 520 tests slagen zonder overslaan op Debian/Fedora/Arch.
Vier geïnstalleerde zelftests slagen op vijf doelen incl Ubuntu 26.04/Rolling.
Alle 7 jobs van [de bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43610344308)
zijn groen. Tag/bron/body en assets op naam, grootte, uploadstatus en digestmetadata
gecontroleerd; zes definitieve logs zonder onverwachte fouten.

Lokaal 516 volledige tests (9 expliciete backend/native skips) en na het indexwerk
30 gerichte manual/i18n/layout/installatiecontroles groen. 1450 bronvormen,
0 ontbrekend. Index: 75 onderwerpen Nederlands, 43 Engels, 44 Duits/Frans/Spaans.
Geen nieuwe afhankelijkheden of profiel-/projectformaatwijziging.
Zie de [onderbouwing](validation/adaptive-noise.md). B21 is uit de open todo;
B23/B24 volgen. De 18 uitgestelde kandidaten blijven buiten de route.


## Uitklank, filterranden en bediening — 0.24.0

B23/B24 zijn afgerond met automatische uitklank, handmatig tot 600 seconden en
galmtijd tot 60 seconden. EQ en filters hebben instelbare selectieovergangen met
voorbereiding uit voorgaande audio; hun natuurlijke causale fase blijft behouden.
Vorige/Volgende bladeren door handleidingonderwerpen. Pictogramknoppen hebben
neutrale vlakken met accentkleurige iconen. Alle 542 controles en de vier
geïnstalleerde zelftests op vijf doelen slagen. Zie
[uitklank en filterranden](validation/tails-and-boundaries.md).

## Systeemgeluid — 0.25.0

De standaarduitgang van Linux is als opnamebron beschikbaar, ook zonder microfoon.
Iedere nieuwe take bepaalt de actuele uitgang. Stereo, mono-kanaalkeuze, pauze,
hervatten, veilige take-opslag, Undo/Redo en de gewone WAV-/MP3-werkwijze blijven
beschikbaar. De clienthulpmiddelen worden met de installatiepakketten meegeleverd.
Een ontbrekende uitgang of verbinding geeft een melding zonder microfoonfallback.

Alle 555 tests slagen zonder overslaan op Debian, Fedora en Arch. De vijf
geïnstalleerde zelftests slagen op de drie distributies en beide Ubuntu-doelen.
[Release 0.25.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.25.0)
bevat de geteste pakketten. De [controledekking](validation/system-audio.md)
beschrijft de toonproef, bronkeuze en foutafhandeling. De fysieke proef van de
eigen hoofduitgang blijft bij B33; B36b is de volgende functionele stap.


## Lege werkruimte en golfvorm — 0.25.1

De overbodige startmelding verschijnt niet meer over de golfvorm, ook bij
selectiezoom en tekenen. De lege werkruimte blijft volledig leeg. De 49 gerichte
layout-, kanaal-, teken-, opname-, taal- en installatiecontroles slagen. De
visuele controle dekt vijf talen met een lege werkruimte en met geselecteerde
stereo-audio, zowel met als zonder tekenmodus.

De [workflow](https://github.com/rene-timmermans/SoundSausage/actions/runs/43620756892)
slaagt met alle zeven jobs, alle 555 tests zonder overslaan op Debian/Fedora/Arch
en vijf geïnstalleerde zelftests op vijf doelen. Bron en tag:
`61faeaba00734e05b353347d9369c566d65f69bc`. De acht releasebestanden en korte
releasepunten zijn geverifieerd. De v1-route blijft ongewijzigd.

## Afspelen in volledig scherm — 0.25.2

De gevulde min/max-polygonen zijn vervangen door verticale piekspannen met
verbonden contouren. Een cache ter grootte van het tekenvlak voorkomt dat de
hele golfvorm bij iedere cursorstap opnieuw wordt opgebouwd. Bij afspelen
bereidt één achtergrondtaak nieuwe piekgegevens voor; achterhaalde resultaten
worden verworpen. Audio wordt vóór de weergavepositie aangevuld. Selecties,
audioveranderingen, thema, lettergrootte en formaat vernieuwen het beeld.

Een afzonderlijke audioproef schakelt met F11, vergroot naar 4K en zoomt terwijl
stereotonen worden afgespeeld en op een private uitgangsmonitor worden opgenomen.
De proef controleert het opgenomen geluid op interne stiltes. Publicatie en
installatiecontroles worden na de definitieve bouw vastgelegd.
