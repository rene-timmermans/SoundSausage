# Kanaalgebonden tijdsbewerking — B06/B07, 0.22.0

Links/Rechts richten tijdsbewerkingen uitsluitend op de gekozen golf. Andere
samples houden exact dezelfde float32-bits en absolute frameposities. Bij
verlenging wordt het andere kanaal achteraan met nullen aangevuld; bij verkorting
krijgt het gekozen kanaal eindstilte. Beide blijft de gezamenlijke tijdsbewerking.
De opgeslagen stereo heeft één frameaantal; de opvulling is gewone audio. Een
volgende invoeging verschuift ook eerder toegevoegde stilte. Er is geen apart
verborgen kanaaleinde of nieuw projectformaat nodig.

Knippen/verwijderen sluiten het gat in de gekozen golf. Trimmen zet het gekozen
fragment op nul en vult de rest met stilte; het andere kanaal blijft staan.
Plakken vervangt een willekeurige selectieduur of voegt in bij de cursor; stereo-
klembordaudio levert het overeenkomstige kanaal, mono het enige kanaal. Mix Paste
telt op en verlengt zo nodig, zonder latere bestaande audio te verschuiven.
Toongeneratie, gegenereerde stilte, tijdrekken en effect-/convolutie-uitklank
gebruiken dezelfde regels. Preview speelt de andere golf op haar vaste tijdstippen.

Opnemen in één kanaal gebruikt mono, de bestaande samplerate en de gekozen
hardware-ingang. De hardware-ingang staat los van Links/Rechts als bestemming.
De bestemming wordt bij starten vastgelegd; veranderde documentrevisie of
kanaalkeuze laat de ruwe take beschikbaar voor herstel. Stop is één Undo-stap.

Gezamenlijke WAV-cues en ID3-hoofdstukken blijven bij één kanaal op hun tijdstip.
Klembordmarkeringen worden dan niet samengevoegd. De bestaande opschoning van
achterhaalde ID3-metingen en duurvernieuwing blijft gelden; Undo herstelt de ruwe
originele metadata. Beide blijft markeringen volgens de hele tijdas verplaatsen.

Nieuwe of veranderde audio wordt in blokken opgebouwd. Grote suffixbuffers
staan op schijf; de ongewijzigde prefix blijft gedeeld. Geen commit voordat
opbouw, annulering, piekvoorbereiding en metadata afgerond zijn. Projectwriter 5,
herstelversie 2 en DSP-ABI 7 blijven behouden.

Regressies vergelijken knippen/trimmen, korter/langer/invoegen, beide bestemmingen,
einde, samplerates en stereo-/monoklemborden met expliciete verwachte samples.
Echte DSP-proeven toetsen tijdrekken in beide richtingen, echo/galm en een
stereo-impulsrespons. Een grote schijfbuffer toetst annuleren na een blok,
behoud van Redo en metadatafouten vóór commit. WAV, project en crashherstel
bewaren de nieuwe audio en opvulling. GUI-proeven toetsen genereren, ingangen,
opnamebestemming, opslag, Undo en geblokkeerde kanaalkeuze tijdens opnemen.

## Definitieve verificatie en publicatie

[Workflow 43606249521](https://github.com/rene-timmermans/SoundSausage/actions/runs/43606249521)
is volledig groen: alle 501 tests zonder overslaan op Debian, Fedora en Arch.
Vier geïnstalleerde zelftests slagen op die drie distributies en Ubuntu 26.04 en
Rolling: gewone app/native plug-infixture, uitvoer, invoer en duplex.

Bron/tag 9d4aa0495bff2958175583641574b6e08a472c5a, tree
f2e469292fb826989d8612b07882ec8220d16aa0. Parent b6fc237e16dac186bc5b316e1cb31e66c97fc15f
bevat de eerste kanaalimplementatie; de laatste commit completeert de
zinsvertalingen in het opnamevenster en toetst live wisselen van taal.
De eerste bouw had drie distributies groen en is vóór publicatie door de
laatste bouw vervangen. De release wijst naar de definitief getoetste bron.

[Release 0.22.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.22.0)
heeft 8 assets: bron, controlesommen, Debian/Ubuntu, Fedora en Arch plus
bijbehorende debugpakketten. Namen, groottes, uploadstatus en digestmetadata,
tag en korte releasepunten zijn gecontroleerd. Zes definitieve joblogs hebben
geen onverwachte fouten of overgeslagen tests.

Lokaal 500 tests met 9 expliciete backend/native skips; daarna 34 definitieve
UI/i18n/layout/installatiecontroles na de laatste zinsvertaling. Vijftien
opnamevensters voor één kanaal passen in vijf talen en drie lettergroottes;
de tekst is ook visueel gecontroleerd. Catalogi: 1440 bronvormen, 0 ontbrekend.
De eerste lokale run werd in de uitvoeromgeving afgebroken; de herhaling slaagt.

Bewijs staat lokaal in build/release-0.22.0-receipt.json,
channels-source-{manifest,receipt,tree}.json, channels-full-tests.log,
channels-final-ui-tests.log, channels-recording-layout.json en
release-0.22.0-logs/*.log. B33 blijft de afzonderlijke fysieke controle vóór v1.0.
