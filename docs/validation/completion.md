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

De lokale volledige suite slaagt met 448 controles; acht expliciete tests voor
backend/native vensters zijn lokaal uitgeschakeld. De daarna toegevoegde LV2-
vensterfixture heeft zes geslaagde audio-/statustests en één expliciet uitgeschakelde
native UI-test. De huidige volledige kandidaat telt 449 controles. De gewone
installatiezelftest en de geïnstalleerde stagingcontrole slagen. De vijf talen
bevatten 1430 bronvormen zonder ontbrekende vertalingen. Twee definitieve
regressies toetsen ook de samengestelde punchtoelichting in alle vijf talen.

De nieuwste distributierondes wachten sinds 11 november op GitHub zonder
begonnen jobs. [Testronde](https://github.com/rene-timmermans/SoundSausage/actions/runs/43097870027).
Hierdoor zijn de nieuwe echte backendkalibratie, native LV2-vensterproef en
installatiepakketten nog niet definitief geverifieerd of gepubliceerd. De eerdere
VST3-X11-proef is wel op alle drie distributies geslaagd. De stabiele release
blijft 0.18.0. Fysieke kalibratie/punch en een echt extern plug-invenster vragen
nog praktijkbevestiging vóór v1.0.
