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

Definitieve bouw- en publicatieresultaten worden na de distributiecontroles
hier aangevuld. B33 blijft de afzonderlijke fysieke controle vóór v1.0.
