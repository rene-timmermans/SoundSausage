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

## Afronding naar v1.0 — actief

- [ ] Eigen Linux VST3-plug-invensters, met parameter-/statusopslag en crashisolatie.
- [ ] LV2- en LADSPA-audio-effecten toevoegen, met betrouwbare ontdekking en project-/herstelopslag.
- [ ] Automatische compensatie van plug-invertraging bij afspelen en export.
- [ ] Kalibratie van de opnamevertraging en compensatie van klokdrift tussen in- en uitvoer.
- [ ] Punch-in/out met voorloop en precies begrensde opnamen, Undo en herstel.
- [ ] Vijf talen, volledige offlinehandleidingen en distributiecontroles bijwerken.
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
