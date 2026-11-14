# Uitklank, filterranden en bediening — 0.24.0

## B23: automatische en langere uitklank

Delay, echo en galm kunnen offline automatisch hun uitklank toevoegen. Handmatige
uitklank loopt van 0,01 tot 600 seconden; de galmtijd van 0,1 tot 60 seconden.
Automatisch volgt de interne effecttoestand, zodat een vertraagde echo na een
stil gat behouden blijft. De grens is 90 dB onder de referentiepiek, met een
absolute ondergrens van −140 dBFS. Een conservatieve toestandsgrens voorkomt
dat alleen een toevallig stil uitvoerblok het einde bepaalt. Controles gebeuren
per 100 ms; daarna volgt een stille marge met een laatste overgang van 10 ms.

Een nog te sterke toestand na 600 seconden geeft een melding en laat het
document intact. Stilte en een effectaandeel van nul voegen geen lege tijd toe.
Opslag groeit met de werkelijke uitvoer; er wordt geen tien minuten lange buffer
vooraf gereserveerd. Verwerking, voortgang en annuleren blijven blokgewijs.
Realtime spoorketens behouden hun afzonderlijke uitklankgrens van 60 seconden;
de uitgestelde capaciteitskeuze B17 verandert niet.

De bestaande galm gebruikt gedempte kamfilters en allpasses, met
`feedback = 10**(-3*delay/T60)`. De formule en structuren staan beschreven in
[Achieving Desired Reverberation Times](https://www.dsprelated.com/freebooks/pasp/Achieving_Desired_Reverberation_Times.html)
en [Artificial Reverberation](https://www.dsprelated.com/freebooks/pasp/Artificial_Reverberation.html).
De nieuwe stopbeslissing gebruikt een eigen conservatieve grens, geen garantie
op een identieke hoorbare uitklank voor ieder materiaal en iedere luisteromgeving.

## B24: selectieovergangen en fase

EQ en filters houden hun natuurlijke causale fase. Er komt geen afzonderlijke
lineaire- of nulfasemodus. De biquads blijven gebaseerd op de
[W3C Audio EQ Cookbook](https://www.w3.org/TR/audio-eq-cookbook/).

Bij een gedeeltelijke selectie bereidt voorafgaande audio de filtertoestand
voor. De benodigde context volgt uit de polen, begrensd op 60 seconden, en wordt
uit de oorspronkelijke audiostukken in blokken gelezen. Daarna mengt een
instelbare overgang binnen de selectie het resultaat met het origineel.
De standaard is 5 ms, instelbaar tot 100 ms. De eerste en laatste sample aan
een binnenliggende grens blijven exact origineel, evenals alle audio buiten
de selectie en het niet gekozen stereokanaal. Een heel korte selectie kan
volledig uit overgang bestaan. Een extreme smalbandige laagfrequente instelling
kan de contextgrens bereiken; een langere selectie of het hele bestand helpt.

Met 0 ms blijft de oorspronkelijke directe verwerking vanaf een lege toestand
beschikbaar. Het hele bestand behoudt de gewone continue filterroute. De
frequentiegrafiek toont de stationaire respons; de lokale overgang is daarvan
gescheiden. Realtime inserts houden hun doorlopende toestand en tonen geen
selectieovergangsveld. Bestaande effect- en projectinstellingen blijven leesbaar;
DSP-ABI 7, projectversie 5 en herstelversie 2 veranderen niet.

## Handleiding en pictogrammen

Vorige en Volgende volgen de hoofdstukken en onderwerpen in alle vijf talen.
Links en scrollen houden de huidige positie bij; bij de grenzen wordt de
betreffende knop uitgeschakeld. Enter, F3 en Shift+F3 blijven zoekresultaten
volgen. De blauwe inhoudsopgaven blijven ook op GitHub bruikbaar.

Werkbalk- en transportknoppen hebben neutrale achtergronden en pictogrammen in
de accentkleur. Een dun accentkader markeert een gekozen stand. De belangrijke
tekstknoppen en het Linux-desktoppalet behouden hun bestaande stijl.

## Controles

Gerichte proeven dekken late taps na twee seconden stilte, echo boven zestig
seconden, handmatige grenzen, automatisch einde, bitgelijke Preview-prefixen
en onafhankelijke blokgroottes. Opslag krijgt ook een proef met gedeeltelijke
systeemschrijfacties. Annuleren, limiet- en schijffouten bewaren de documentstand,
Redo en selectie. Uitklank is getoetst met kanaalkeuze, cueverschuiving, Undo/Redo,
WAV, projectopslag en herstel.

Filterproeven vergelijken het binnengebied met een doorlopend opgewarmd filter,
toetsen de overgang, exact bronbehoud buiten de selectie, korte selecties,
kanaalkeuze, Preview, de 0 ms-route en annuleren tijdens context of uitvoer.
GUI-proeven dekken de nieuwe velden, talen, layout, onderwerpknoppen, zoekactie,
neutrale knopvlakken en de gekleurde pictogrammen.

Lokaal slagen 542 tests met negen expliciete controles voor de distributierunners;
de gewone appzelftest slaagt eveneens. De definitieve
[workflow](https://github.com/rene-timmermans/SoundSausage/actions/runs/43615282659)
slaagt met alle zeven jobs. Alle 542 tests draaien zonder overslaan op Debian,
Fedora en Arch. Gewone app-, afspeel-, opname- en duplexzelftests slagen op de
geïnstalleerde pakketten op vijf doelen, inclusief Ubuntu 26.04 en Rolling.

[Release 0.24.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.24.0)
bevat de geteste Debian/Ubuntu-, Fedora- en Arch-pakketten, broncode en
controlelijsten. Tag, acht bestanden en korte releasepunten zijn geverifieerd.
De broncommit is `0bc6c662fcf6f54589222c203525aeafde8e4399`.
B23/B24 zijn uit de open todo verwijderd; B36b en de fysieke B33 blijven open.
Automatische virtuele proeven vervangen die fysieke controle niet.
