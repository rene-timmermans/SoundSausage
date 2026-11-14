# Ruisreductie — B21, 0.23.0

De vaste profielstand blijft beschikbaar. De adaptieve stand begint met hetzelfde
ruisprofiel en volgt per frequentieband het veranderende achtergrondvermogen.
De aanpassingstijd is 0,05–5 s; korter volgt sneller en langer terughoudender.
Detailbehoud mengt een zachtere spectrale verzwakking bij, 0–100%. Meer behoud
laat ook meer achtergrond door. De beginwaarde in het venster is 50%; de DSP-
standaard blijft 0 zodat bestaande expliciete instellingen hun resultaat behouden.
Vast profiel met 0% detail gebruikt de eerdere verwerking.

De profielbestanden blijven versie 1 en veranderen niet door toepassen. Er is
geen nieuwe training of externe afhankelijkheid nodig. Een passend profiel is
verplicht; een volledig stil profiel of 0 dB reductie blijft een exacte bypass.
Dit is geen stemseparatie en herstelt geen ontbrekende broninformatie.

## Verwerking en bron

De profielgestuurde vermogensschatting gebruikt zachte signaalaanwezigheid met
vaste priors en recursieve middeling, geïnspireerd door Gerkmann/Hendriks,
[Unbiased MMSE-Based Noise Power Estimation](https://www.inf.uni-hamburg.de/en/inst/ab/sp/publications/paper-in-journals-pdf/2012-gerkmann-hendriks-ieee-transactions-on-audio-speech-and-language-processing.pdf),
2012, sectie IV ([DOI](https://doi.org/10.1109/TASL.2011.2180896)). Dit is een eigen
toepassing in de bestaande STFT-verwerking, geen claim dat het volledige
spraakverbeteringssysteem uit het artikel is gereproduceerd. Een lokale
spectrale-piekcontrole voorkomt dat de stagnatiecorrectie aangehouden smalle
tonen gemakkelijk als achtergrond leert. De extra detailweging is een eigen
afweging tussen onderdrukking en behoud.

Geen training op aangevulde randsamples; Preview en volledige verwerking
gebruiken dezelfde beginframes en toestand. De toestandsarrays hangen alleen
van FFT-grootte en kanalen af, niet van de bestandsduur. Grote resultaten staan
op schijf; voortgang en annuleren blijven beschikbaar. De bron blijft
ongewijzigd tot één commit. Metadata, kanaalkeuze, Undo/Redo, herhalen en
WAV-opslag volgen de bestaande documentroute. DSP-ABI 7/project 5/herstel 2 blijven
behouden. Klikverwijdering verandert niet.

## Meetproeven en regressies

Synthetische, deterministische proeven toetsen een oplopende en abrupt
veranderende achtergrond, dalende ruis, een zwakke toon, een aangehouden toon
en een korte aanslag. De stijgende-ruisproef vergelijkt met hetzelfde schone
signaal en verlangt minimaal 4 dB minder foutenergie dan het vaste profiel en
minimaal 6 dB verbetering tegenover de verstoorde bron. Detailbehoud wordt apart
getoetst op meer amplitude van een zwakke toon, terwijl achtergrondonderdrukking
blijft bestaan. Dit zijn resultaten van deze signalen, geen universele
kwaliteitsgarantie voor iedere opname.

Verdere regressies toetsen de snelheid van volgen, resterend stiltesignaal,
lang aangehouden tonen, transiënten, gekoppeld/ongekoppeld stereo en één kanaal,
prefixgelijkheid, blokgroottes, schoon+verwijderd=bron, profielimmutabiliteit,
F2, WAV-roundtrip, late annulering met Redo, ongeldige instellingen, korte/lege
selecties, samplerates 1–384 kHz en een grote schijfbuffer. GUI-controles toetsen
presets, activering van de tijdinstelling, Preview/toepassen en live taalwissel.
Vijf volledige handleidingen zijn bijgewerkt.

## Klikbare handleidingindex

Alle vijf manuals bevatten een statische Markdown-inhoudsopgave en expliciete
onderwerpankers, bruikbaar in GitHub en zonder internet. Een knop Inhoud in het
helpvenster springt terug naar de inhoudsopgave. De links zijn onderstreept en
blauw, met aangepaste tinten voor lichte en donkere achtergronden. Hoofdstukken
en losse effecten zijn geïndexeerd: 75 onderwerpen in Nederlands, 43 in Engels en 44
in Duits/Frans/Spaans. `python3 tools/index_manuals.py` werkt de index bij;
`--check` toetst of deze actueel is.

Qt’s Markdown-reader neemt lege HTML-ankers niet op in het document. De
helpweergave koppelt daarom dezelfde expliciete namen aan de werkelijke
kopblokken en gebruikt [scrollToAnchor](https://doc.qt.io/qt-6.8/qtextbrowser.html)
voor navigatie. Alle ankers, echte muisklikken, terugkeer, live taalwissel en
blauwe onderstreping bij themawissel worden getoetst. Externe websites openen
uitsluitend na een expliciete klik; indexnavigatie opent geen browser.

## Praktische grenzen

Adaptieve herkenning kan gewenst geluid als achtergrond leren, vooral bij
aanhoudende brede klanken, een onjuist profiel en zeer lage signaalniveaus.
Gebruik een langere aanpassingstijd of de vaste stand als klanken verdwijnen.
Hoger detailbehoud laat meer ruis achter. Beluister het verwijderde deel en
vergelijk het resultaat. Geen claim dat muziek of spraak geheel onveranderd
blijven. Alle extra ruisprofiel-/detailinstellingen zijn golfvormbewerkingen.

## Definitieve verificatie en publicatie

[Workflow 43610344308](https://github.com/rene-timmermans/SoundSausage/actions/runs/43610344308)
is volledig groen: alle 520 tests zonder overslaan op Debian, Fedora en Arch.
Vier geïnstalleerde zelftests slagen op die drie en Ubuntu 26.04/Rolling:
gewone app/native plug-infixture, uitvoer, invoer en duplex.

Bron/tag 2c0c45432b9164c498d3c86769c064ee96aed2c8, tree 47b08e28da93f47c9dacc00b721c033c1e9dbbb0,
parent 4b101d65fa817bb46e13d10353638e32f1a6280e. De
[release 0.23.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.23.0)
heeft 8 assets: bron, controlesommen, Debian/Ubuntu, Fedora en Arch plus bijbehorende
debugpakketten. Namen, groottes, uploadstatus en digestmetadata, tag en korte
releasepunten zijn gecontroleerd. Zes definitieve joblogs zonder onverwachte fouten.

Lokaal 516 volledige tests met 9 expliciete backend/native skips, daarna 30 definitieve
manual/i18n/layout/stagingcontroles na de extra indexopdracht. 1450 bronvormen,
0 ontbrekend. De gewone zelftest wacht in een synthetisch tweesecondenfragment
voldoende reactie na de ruissprong af; dezelfde eis van minstens halvering van
ruisenergie geldt, gemeten ongeveer 0.216 van de bronenergie in het laatste kwart.
Dit verandert geen opnamebediening of reactietijd van het effect.

Bewijs lokaal: build/release-0.23.0-receipt.json, noise-source-*.json,
noise-full-tests.log, noise-index-final-tests.log, noise-selftest.log,
manual-contents-preview.png, adaptive-noise-preview.png en release-0.23.0-logs/*.log.
B21 is afgerond; B23/B24 zijn de volgende stap. B33 blijft de afzonderlijke fysieke
controle vóór v1.0.
