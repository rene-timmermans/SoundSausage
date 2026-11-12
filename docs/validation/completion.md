# Plug-ins, synchronisatie en punch-in/out — 0.19.0

## Plug-ininterfaces en isolatie

Een onafhankelijke C++-VST3-testplug-in maakt een echt X11-childvenster. De
proef controleert timers, file-descriptorcallbacks, resize, toetsenbord, gewijzigde
parameters en status na heropenen. De eigen view leeft in hetzelfde geïsoleerde
proces als de plug-in. IPlugFrame/IRunLoop, focus en content scaling volgen de
gepubliceerde VST3-interfaces; de gebruikte MIT-headers zijn gepind. De eerdere
native vensterproef slaagt op Debian, Fedora en Arch in run 43089037841.

Onafhankelijke LADSPA/LV2-C-fixtures controleren ontdekking, poorten, defaults,
mono-instanties per kanaal, stereo, parameters, LV2 portable status, bewaren en
herstellen. Lokale Caps- en Valve Speakers-effecten zijn eveneens geopend en
verwerkt. Verplichte niet-ondersteunde LV2-features/poorten en statusbestanden
worden expliciet geweigerd. LV2 X11-UI’s worden ondersteund; GTK-/Qt-adapters,
MIDI/Atom-verwerking en extra sidechains vallen buiten de implementatie.
De lokale sandbox kan geen X11- of audiosockets openen; die proeven worden
expliciet op normale distributierunners uitgevoerd.

## Verwerkingsvertraging

De mixer verwerkt per spoor vooruit in begrensde blokken, gooit alleen de
algoritmische beginvertraging weg en leest het gewenste aantal uitvoerframes.
De tests gebruiken een onafhankelijk vertraagd effect, inclusief een pas na
het eerste blok gemelde latency. Meerdere effecten, bypass, gewijzigde latency,
opaque status, zoeken en de laatste samples worden getoetst. Muzikale delay
blijft deel van het resultaat. Totale compensatie is maximaal tien seconden
per spoor; continu wisselende of ongeldige waarden geven een foutmelding.

## Kalibratie en relatieve klokken

DuplexClock gebruikt begrensde meetreeksen, een opwarmperiode, robuuste
uitschieterverwijdering en afzonderlijke pauzesegmenten. Drift wordt alleen bij
voldoende duur en significantie toegepast. Proeven bevatten verschillende rates,
400 ppm afwijking, jitter, uitschieters, pauzes en lange reeksen. Korte en
onbetrouwbare metingen rekken de opname niet op. De exacte lengteconversie
is onafhankelijk van de gebruikte blokgrootte en behoudt het laatste deel.

De loopbackmeting gebruikt vier unieke, zacht ingefade breedbandmarkers en
normaliseerde correlatie op het sterkste kanaal. Omgekeerde polariteit, verzwakking
en ruis worden getest; stilte, oversturing, dubbelzinnige echo’s en instabiele
timing worden afgewezen. Alleen geldige resultaten worden per apparaat/rate/
ingang/buffer opgeslagen. Annuleren of een fout bewaart een eerder goed profiel
en verwijdert diagnostische audio en hersteljournaal.

De GUI-proef controleert starten, meten, bewaren, annuleren, verlies van apparaten,
correcte plaatsing met kalibratie/beginuitsnede/drift, en exclusieve handmatige
instelling. De backendproef kalibreert via een private PulseAudio-monitorroute
en vergelijkt vervolgens de plaatsing van een echte Qt-opname van dezelfde
referentie. De route spreekt geen fysieke microfoon aan. Fysieke apparaatklokken
en commerciële plug-ins vragen daarnaast een praktijktest vóór v1.0.

## Punch en gegevensbehoud

Modeltests vergelijken de mix bitexact buiten de selectie, ook bij overlappende
clips, fades en automatisering. Oude bronnen blijven behouden achter bronrelatieve
punchgebieden. Een tijdelijke playbackgate verandert de sessie niet. Nieuwe audio,
maskers en clip vormen één transactie met Undo/Redo. Dubbele punches, trimmen,
verplaatsen, dupliceren, bronvervanging, bewaren/heropenen en crashherstel houden
de gegevens samen. Projectversie 5 leest 1–5, herstelversie 2 leest 1/2; ongeldige
metadata of een vals ouder versienummer worden afgewezen.

GUI-tests controleren selectiegrenzen, warmdraaien vóór afspelen, punch vanaf
nul ondanks beginuitsnede, voorloop, automatisch stoppen, vroeg stoppen zonder
sessiewijziging en één Undo-stap. De ruwe onafgemaakte take blijft herstelbaar.
Vensters worden in vijf talen en drie lettergroottes op tekstoverlap getoetst,
ook met verbonden apparaten en een lange kalibratietekst. De installatiezelftest
bevat punch, klokmeting en de nieuwe vensters in vijf talen; in CI opent hij ook
een native plug-invenster vanuit de geïnstalleerde host.

## Integratiestatus — 12 november 2026

Alle 451 controles slagen zonder overslaan op Debian, Fedora en Arch, inclusief
native VST3-/LV2-X11-vensters, de echte Qt/PulseAudio-loopbackkalibratie en de
nieuwe gesynchroniseerde opname. De aanvullende zelftest opent eveneens een
native editor en slaagt op alle drie distributies.
[Broncontrole](https://github.com/rene-timmermans/SoundSausage/actions/runs/43265508881).

De lokale volledige suite slaagde eerder met 448 tests en acht expliciete
backend-/vensterskips. Daarna zijn de LV2-UI-, inputformaat- en korte-driftproeven
toegevoegd. De 19 definitieve klok-/opname-/punchregressies slagen lokaal,
evenals de gewone zelftest en staginginstallatie. De vijf talen bevatten 1430
bronvormen zonder ontbrekende vertalingen. De vensters en samengestelde
punchtoelichting zijn in vijf talen en drie lettergroottes gecontroleerd.

Duurcorrectie vraagt ruim tien seconden bruikbare klokmetingen. Een regressie
voorkomt dat kortdurende schijndrift de opnamelengte verandert. Apparaten,
mono/stereo, native formaat, eerste kanaal en buffer bepalen het kalibratieprofiel.
De definitieve releasebouw doorstaat alle 451 tests zonder overslaan op Debian,
Fedora en Arch. De geïnstalleerde pakketten slagen voor de gewone, uitvoer-,
invoer- en duplexzelftest op alle vijf doelen, inclusief Ubuntu 26.04 en Rolling.
De gewone zelftest opent de native VST3-editor vanuit de geïnstalleerde host;
daarvoor zijn uitsluitend de normale Qt Core-/Gui-/Widgets-onderdelen nodig.
De testfixture blijft buiten de releaseassets.

Tag v0.19.0 verwijst naar de geteste broncommit
`571e7ca3e337df960df5d1c6090df04ae8695fdd`. De acht assets zijn gecontroleerd op
naam, grootte, uploadstatus en SHA256-digestmetadata; de korte releasepunten
komen overeen met de bron. De zes definitieve logs bevatten geen onverwachte
callback-, RuntimeError- of bufferfouten.
[Releasebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43268472763)
en [installatiepakketten](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.0).

De fysieke kalibratie-/punchroute en echte externe plug-ins vragen nog
praktijkbevestiging vóór v1.0. Gewone B910-opname en terugluisteren zijn eerder
bevestigd.

## Venstericonen — 0.19.1

De bestaande icooncontrole toetst nu de paarse achtergrond voor alle caption- en
taakbalkmaten bij zowel 1× als 2× schermschaal. Transparante buitenhoeken en de
vrijstaande Over-mascotte blijven afzonderlijk gecontroleerd. De zes gerichte
icoon-/Over-/stagingproeven slagen lokaal. De definitieve bouw slaagt opnieuw
met alle 451 tests op Debian/Fedora/Arch en vier geïnstalleerde zelftests op alle
vijf doelen. Tag, geteste broncommit en acht assets zijn geverifieerd; de vijf
offlinehandleidingen zijn bijgewerkt.
[Bouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43271010006)
en [release](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.1).
