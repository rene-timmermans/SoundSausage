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

## 4. Overige effecten en tools — afgerond in 0.13.0

Eerst EQ en filters, vervolgens delay en galm, daarna complexere functies zoals
ruisreductie en tijd-/toonhoogtebewerking. Iedere groep wordt bruikbaar afgerond.
Uitgebreide compatibiliteit met oudere sessies en externe plug-ins volgen later.

- [x] EQ en filters, met luistervoorbeeld en frequentierespons — 0.9.0, met geteste installatiepakketten.
- [x] Delay, echo en galm — 0.10.0, met geteste installatiepakketten.
- [x] Ruisreductie en klikverwijdering — 0.11.0, met geteste installatiepakketten.
- [x] Tijd- en toonhoogtebewerking — 0.12.0, met geteste installatiepakketten.
- [x] Vervorming en convolutie — 0.13.0, met geteste installatiepakketten.

Alle vijf groepen zijn beschikbaar met handleiding, luistervoorbeelden en geteste
installatiepakketten. Ze vullen de eerder afgeronde Amplitude-groep aan.
Spoorketens, Linux VST3, opname met begeleiding en volledige nieuwe projecten
zijn uitgewerkt in fase 5. Uitgebreidere import van oude sessies is geen vereiste
voor de huidige werkwijze.

Iedere groep krijgt meetbare audiocontroles, Undo/Redo, bediening voor selecties
en lange bestanden, bijgewerkte uitleg en een geteste release.

## Bediening na de effectgroepen

Versie 0.14.0 verfijnt de golfvormweergave tijdens zoomen en maakt links/rechts
afzonderlijk selecteerbaar voor effecten. Kanaalkeuze, Undo/Redo, herstel,
mono-export en de gedeelde stereotijdas horen bij deze uitbreiding. Alle
menufuncties krijgen eigen iconen; de beide zoomfuncties blijven herkenbaar.
De vijf effectgroepen blijven afgerond. Zie [voortgang](VOORTGANG.md).

## 5. Realtime mixen, opname met begeleiding en uitwisseling — afgerond in 0.15.0

- [x] Spooreffecten in kleine audioblokken tijdens afspelen; bewerkbare keten, bypass, Undo/Redo, projectopslag en dezelfde keten bij mixdown.
- [x] Bestaande sporen beluisteren tijdens opnemen op een nieuw blok; samen pauzeren/stoppen, veilige foutafhandeling en instelbare opnameverschuiving.
- [x] Externe Linux-effectplug-ins, met gewenste VST3-ondersteuning: vinden, parameters bewerken en in een spoorketen bewaren; ontbrekende plug-ins duidelijk melden.
- [x] Nieuwe SoundSausage-projecten volledig bewaren en heropenen, inclusief opnamen, spooreffecten en plug-ininstellingen.

Iedere uitbreiding krijgt audiocontroles, bijgewerkte offlinehandleiding en
installatiepakketten. Exacte ondersteuning van plug-informaten en oude
sessievarianten staat bij de functie; niet-ondersteunde gegevens worden gemeld.

Alle 363 controles en de geïnstalleerde pakketten zijn geverifieerd in de
[distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43017564061).
[Release 0.15.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.15.0)
bevat de installers. De fysieke duplexroute blijft afstelbaar met een proeftake;
eigen plug-invensters, meer formaten en automatische latency-/driftcompensatie
blijven vervolgmogelijkheden.

## Open punten blijven zichtbaar

De actuele afvinklijst staat in [voortgang](VOORTGANG.md). Nog openstaande
controles worden bij een nieuwe fase meegenomen. Realtime spooreffecten, multikanaals routering en naadloze lussen gelden pas als
beschikbaar wanneer ze daadwerkelijk zijn gebouwd en gecontroleerd.

De handleiding blijft via Help en F1 bereikbaar en beschrijft alle beschikbare
functies. Korte GitHub-releasepunten noemen alleen toegevoegde functies en
work in progress. De programma's volgen dezelfde presentatiestijl als PixelPickle.

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

## Afronding naar v1.0 — software 0.19.0 gebouwd

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

### Stand 0.19.0 — software afgerond

- [x] Eigen X11/XWayland-vensters met VST3-runloop, toetsenbord en statusopslag; LV2 X11-vensters en LADSPA-regelaars.
- [x] LV2/LADSPA-ontdekking, mono-/stereo-audio, parameters, status en ontbrekende effecten.
- [x] Gerapporteerde plug-invertraging compenseren bij afspelen en export, met behoud van muzikale delay.
- [x] Apparaatgebonden loopbackkalibratie, automatische klokmetingen en betrouwbare driftcorrectie; handmatig alternatief behouden.
- [x] Punch-in/out met voorloop, korte overgangen, exacte selectiegrenzen en behoud van originele bronnen.
- [x] Undo, projectversie 5 en herstelversie 2 bewaren punchgebieden; eerdere bestanden blijven leesbaar.
- [x] Alle vijf talen en volledige offlinehandleidingen bijwerken.
- [x] Volledige distributie-, native venster-, loopback- en geïnstalleerde pakketcontroles voor 0.19.0.
- [ ] Fysieke proeftake met de gebruikte in-/uitvoerroute: kalibratie, langere overdub, punch en heropenen.
- [ ] Eigen venster en status van een echte VST3-/LV2-plug-in in de praktijk bevestigen.
- [ ] Releasecandidate van v1.0 zonder bekende blokkerende fouten, daarna v1.0.

De B910-proef voor gewone opname en terugluisteren blijft bevestigd. De nieuwe
synchronisatie- en punchroute vraagt een aanvullende praktijktake; een virtuele
loopback vervangt geen controle van fysieke apparaatklokken. MIDI, Windows/VST2,
extra sidechains en LV2 GTK-/Qt-UI-adapters vallen buiten de huidige ondersteuning.
Een markereditor of eigen favorieten zijn geen blokkerende eis voor v1.0.

De broncontrole voor 0.19.0 slaagt met alle 451 tests en native zelftest op
Debian/Fedora/Arch, zonder overslaan. De definitieve pakketcontroles zijn eveneens geslaagd. [Broncontrole](https://github.com/rene-timmermans/SoundSausage/actions/runs/43265508881).

[Release 0.19.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.0)
is gepubliceerd: alle 451 definitieve tests en alle vier installatiezelftests
op vijf doelen slagen. De nieuwe plug-in- en opnamefuncties zijn softwarematig
afgerond. Alleen de genoemde fysieke praktijkproeven en releasecandidate blijven
open vóór v1.0. [Definitieve bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43268472763).

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

## Projectpresentatie op GitHub

- [x] Dezelfde hoofdindeling als PixelPickle: Wat het kan, Installeren, Taal, Wat er nieuw is en Licentie.
- [x] Mogelijkheden groeperen en installatie-/verwijdercommando's per distributie tonen.
- [x] Taalkeuze en vijf volledige handleidingen rechtstreeks bereikbaar maken.
- [x] Korte productwijzigingen per gepubliceerde release, met links naar de releasepagina's.
- [x] Bouwinstructies behouden in de installatiedocumentatie en alle verwijzingen controleren.


## Vervolg: beperkingen beoordelen

De [todo](TODO.md) is de actuele werklijst voor de beoordeling van de beperkingen
van 0.19.1. De oorspronkelijke volgorde en nummers blijven herkenbaar.
Per punt eerst het praktische probleem en gewenste gedrag bepalen; daarna
verbeteren of bewust behouden. Afgeronde of overgeslagen punten direct uit de
open lijst verwijderen, met een korte reden in het
[besluitenoverzicht](validation/beperkingen-keuzes.md).

De lijst start met B01, de bestaande directe samplebewerking. Dithering en de
markereditor krijgen aparte taken. Alle kandidaten bouwen is geen voorwaarde
voor v1.0; de fysieke proeven onder B33 en een releasecandidate blijven wel
onderdeel van de eerdere afspraak. Nieuwe functies krijgen passende controles,
volledige uitleg in alle vijf handleidingen en geteste installatiepakketten.
