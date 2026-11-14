# SoundSausage — handleiding

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Deze handleiding beschrijft de beschikbare functies van versie 0.27.0. De menunamen
staan zoals ze in het programma worden getoond. Open de handleiding met
**Help → Handleiding** of **F1**. Ze blijft naast de editor openstaan en werkt
zonder internet. Met **Ctrl+F** zoek je een onderwerp; **F3** gaat naar de volgende
treffer en **Shift+F3** naar de vorige. Enter herhaalt de zoekopdracht; zoeken gaat
bij het einde verder vanaf het begin. **Vorige** en **Volgende** springen naar
het vorige of volgende onderwerp, ook zonder zoekterm. Bij het eerste en laatste
onderwerp is de betreffende knop grijs. **Inhoud** brengt je terug naar de index.

<!-- soundsausage-contents:start -->
<a id="ss-contents"></a>

## Inhoudsopgave

Klik op een onderwerp om er direct naartoe te gaan. Inhoud brengt je terug; Vorige en Volgende bladeren door onderwerpen. F3 en Shift+F3 volgen zoekresultaten.

- [Taal kiezen](#ss-topic-taal-kiezen)
- [Snel beginnen](#ss-topic-snel-beginnen)
- [1. De werkruimte](#ss-topic-1-de-werkruimte)
- [2. Bestanden openen, bewaren en sluiten](#ss-topic-2-bestanden-openen-bewaren-en-sluiten)
  - [Losse opnamen](#ss-topic-losse-opnamen)
  - [MP3 openen en bewaren](#ss-topic-mp3-openen-en-bewaren)
  - [MP3-bestandsinformatie na bewerken](#ss-topic-mp3-bestandsinformatie-na-bewerken)
  - [Projecten met meerdere sporen](#ss-topic-projecten-met-meerdere-sporen)
  - [Sluiten](#ss-topic-sluiten)
  - [Lange opnamen en annuleren](#ss-topic-lange-opnamen-en-annuleren)
  - [Werk herstellen](#ss-topic-werk-herstellen)
- [3. Luisteren en navigeren](#ss-topic-3-luisteren-en-navigeren)
  - [Het uitvoerapparaat kiezen](#ss-topic-het-uitvoerapparaat-kiezen)
- [3a. Opnemen](#ss-topic-3a-opnemen)
  - [Een opname maken](#ss-topic-een-opname-maken)
  - [Het opnamebegin overslaan](#ss-topic-het-opnamebegin-overslaan)
  - [Systeemgeluid opnemen (wat je hoort)](#ss-topic-systeemgeluid-opnemen-wat-je-hoort)
  - [Ingang en herstel](#ss-topic-ingang-en-herstel)
  - [Een dagelijkse werkwijze](#ss-topic-een-dagelijkse-werkwijze)
- [4. Selecteren en de golfvorm bewerken](#ss-topic-4-selecteren-en-de-golfvorm-bewerken)
- [4a. Links, rechts en stereo kiezen](#ss-topic-4a-links-rechts-en-stereo-kiezen)
  - [Een effect op één kanaal](#ss-topic-een-effect-op-een-kanaal)
  - [Duur veranderen op één kanaal](#ss-topic-duur-veranderen-op-een-kanaal)
  - [Kopiëren, plakken en bewaren](#ss-topic-kopieren-plakken-en-bewaren)
  - [Opnemen in één kanaal](#ss-topic-opnemen-in-een-kanaal)
  - [Zoomen en functie-iconen](#ss-topic-zoomen-en-functie-iconen)
  - [Afzonderlijke samples bewerken](#ss-topic-afzonderlijke-samples-bewerken)
  - [Golfvorm tekenen](#ss-topic-golfvorm-tekenen)
- [4b. Markeringen](#ss-topic-4b-markeringen)
- [5. Effecten toepassen](#ss-topic-5-effecten-toepassen)
  - [Remaster](#ss-topic-remaster)
    - [Welke Remaster-stand kiezen?](#ss-topic-welke-remaster-stand-kiezen)
    - [Wat gebeurt er met het geluid?](#ss-topic-wat-gebeurt-er-met-het-geluid)
    - [Wat veranderen de Remaster-instellingen?](#ss-topic-wat-veranderen-de-remaster-instellingen)
    - [Remaster vergelijken en toepassen](#ss-topic-remaster-vergelijken-en-toepassen)
    - [Wat kun je van Remaster verwachten?](#ss-topic-wat-kun-je-van-remaster-verwachten)
  - [Versterken / vervagen](#ss-topic-versterken-vervagen)
  - [Kanalenmixer](#ss-topic-kanalenmixer)
  - [Dynamiekbewerking](#ss-topic-dynamiekbewerking)
  - [Volumeverloop](#ss-topic-volumeverloop)
  - [Normaliseren](#ss-topic-normaliseren)
  - [Ompolen, Achterstevoren en Stilte](#ss-topic-ompolen-achterstevoren-en-stilte)
- [5a. EQ en filters](#ss-topic-5a-eq-en-filters)
  - [Grafische equalizer](#ss-topic-grafische-equalizer)
  - [Parametrische equalizer](#ss-topic-parametrische-equalizer)
  - [Filters](#ss-topic-filters)
  - [Niveau, grafiek en selecties](#ss-topic-niveau-grafiek-en-selecties)
- [5b. Vertraging, echo en galm](#ss-topic-5b-vertraging-echo-en-galm)
  - [Vertraging — één vertraagde kopie](#ss-topic-vertraging-een-vertraagde-kopie)
  - [Echo — herhalingen met feedback](#ss-topic-echo-herhalingen-met-feedback)
  - [Galm — galm](#ss-topic-galm-galm)
  - [Droog, Effect en uitgangsniveau](#ss-topic-droog-effect-en-uitgangsniveau)
  - [Een uitklank behouden](#ss-topic-een-uitklank-behouden)
- [5c. Ruisreductie en klikverwijdering](#ss-topic-5c-ruisreductie-en-klikverwijdering)
  - [Een ruisprofiel opnemen](#ss-topic-een-ruisprofiel-opnemen)
  - [Ruisreductie](#ss-topic-ruisreductie)
  - [Klikverwijdering](#ss-topic-klikverwijdering)
- [5d. Tijd en toonhoogte](#ss-topic-5d-tijd-en-toonhoogte)
  - [Tijdsduur aanpassen](#ss-topic-tijdsduur-aanpassen)
  - [Toonhoogte verschuiven](#ss-topic-toonhoogte-verschuiven)
  - [Kwaliteit en praktisch gebruik](#ss-topic-kwaliteit-en-praktisch-gebruik)
- [5e. Vervorming en convolutie](#ss-topic-5e-vervorming-en-convolutie)
  - [Vervorming](#ss-topic-vervorming)
  - [Convolutie](#ss-topic-convolutie)
- [6. Tonen en stilte maken](#ss-topic-6-tonen-en-stilte-maken)
- [7. Frequenties analyseren](#ss-topic-7-frequenties-analyseren)
- [8. Meerdere sporen combineren](#ss-topic-8-meerdere-sporen-combineren)
  - [Een sessie opbouwen](#ss-topic-een-sessie-opbouwen)
  - [Clips en sporen aanpassen](#ss-topic-clips-en-sporen-aanpassen)
  - [Volumelijn en Panlijn](#ss-topic-volumelijn-en-panlijn)
  - [Een effect op een clip toepassen](#ss-topic-een-effect-op-een-clip-toepassen)
  - [Opslaan en mixdown](#ss-topic-opslaan-en-mixdown)
- [8a. Spooreffecten, plug-ins en opname met begeleiding](#ss-topic-8a-spooreffecten-plug-ins-en-opname-met-begeleiding)
  - [Spooreffecten](#ss-topic-spooreffecten)
  - [VST3, LV2 en LADSPA toevoegen](#ss-topic-vst3-lv2-en-ladspa-toevoegen)
  - [Automatische plug-invertraging](#ss-topic-automatische-plug-invertraging)
  - [Opnemen met begeleiding en synchronisatie](#ss-topic-opnemen-met-begeleiding-en-synchronisatie)
  - [Punch-in/out: alleen een passage opnieuw opnemen](#ss-topic-punch-in-out-alleen-een-passage-opnieuw-opnemen)
  - [Sessies bewaren en heropenen](#ss-topic-sessies-bewaren-en-heropenen)
- [9. Een andere samplerate kiezen](#ss-topic-9-een-andere-samplerate-kiezen)
- [10. Favorieten, vensters en hulp](#ss-topic-10-favorieten-vensters-en-hulp)
- [11. Sneltoetsen](#ss-topic-11-sneltoetsen)
- [12. Problemen en work in progress](#ss-topic-12-problemen-en-work-in-progress)

<!-- soundsausage-contents:end -->

<a id="ss-topic-taal-kiezen"></a>

## Taal kiezen

Kies **Opties → Taal** en vervolgens **Nederlands**, **English**, **Deutsch**,
**Français** of **Español**. Menu’s, vensters, aanwijzingen en de geopende
handleiding wisselen meteen mee. De keuze blijft bij de volgende start bewaard.
Bestandsnamen, zelfgekozen spoornamen en namen van externe plug-ins blijven
behouden. Alle vijf handleidingen zijn ook zonder internet beschikbaar.

<a id="ss-topic-snel-beginnen"></a>

## Snel beginnen

1. Kies **Bestand → Openen** en open een WAV- of MP3-bestand.
2. Druk op **Spatie** om te luisteren en opnieuw op Spatie om te stoppen.
3. Sleep over de golfvorm om een fragment te selecteren.
4. Kies bijvoorbeeld **Effecten → Amplitude → Normaliseren**. Luister met
   **Voorbeeld** en bevestig met **OK**.
5. Gebruik **Ctrl+Z** wanneer je de bewerking wilt terugdraaien.
6. Kies **Bestand → Opslaan als** om het resultaat onder een nieuwe naam te bewaren.

Voor meerdere opnamen tegelijk kies je **Bestand → Nieuwe multitracksessie**.
Importeer de WAV- of MP3-bestanden, verschuif de clips en maak een eindmix met **Eindmix maken**.

<a id="ss-topic-1-de-werkruimte"></a>

## 1. De werkruimte

Het programma-icoon met paarse achtergrond herken je in de titelbalken en de taakbalk. **Help → Over** toont de losse mascotte naast de programma-informatie.

SoundSausage heeft twee weergaven. **Golfvorm bewerken** bewerkt één opname.
**Multitrackweergave** combineert clips op meerdere sporen. Wissel met de knoppen
bovenaan, via **Beeld**, of met **Tab**. De golfvorm en de multitracksessie kunnen
naast elkaar blijven bestaan; wisselen van weergave sluit ze niet. Twee dunne
horizontale lijnen begrenzen de kanalen: de onderrand van links en de bovenrand
van rechts. Ze lopen alleen binnen het tekenvlak, ook bij live opname.

Werkbalk- en afspeelknoppen hebben een neutrale achtergrond met pictogrammen in de
themakleur. Een dun gekleurd kader toont de actieve keuze.

Bovenaan staan menu's en werkbalken. Een korte aanwijzing verschijnt wanneer je
de muis boven een knop houdt. **Opties → Werkbalkteksten tonen** toont ook namen
naast werkbalkiconen. **Opties → Statusbalk tonen** toont of verbergt de smalle
informatieregel helemaal onderaan, onder de niveaumeter. Die regel toont de
afspeelstatus en bestandsgegevens. De keuze blijft bij de volgende start bewaard.
**F11** schakelt naar volledig scherm en terug. De venstergrootte, positie en volledig-scherm- of gemaximaliseerde stand blijven
bij de volgende start behouden. Een verdwenen beeldscherm wordt opgevangen door
het venster terug op een beschikbaar scherm te plaatsen.
Tijdens afspelen volgt de cursor de audioklok. De golfvorm wordt hergebruikt;
bij zoomen en wisselen van vensterformaat worden nieuwe piekgegevens op de
achtergrond voorbereid. Het vorige overzicht kan daarbij heel kort blijven staan.


Vensters en grafiekschalen passen zich aan de gekozen taal en de lettergrootte
van het bureaublad aan. Past een formulier niet op het scherm, scroll dan door
de instellingen; de knoppen om te bevestigen of annuleren blijven bereikbaar.

Onderaan staan afspeelknoppen, de klok en de niveaumeters. **Sel** toont het begin,
einde en de lengte van de selectie. **Beeld** toont het zichtbare tijdvak. De klok
volgt tijdens afspelen de audiopositie. Een rode piekindicatie betekent dat het
signaal boven het maximale uitvoerniveau komt: verlaag het volume of normaliseer.

Een sterretje voor de bestandsnaam betekent dat er wijzigingen zijn die nog
niet zijn opgeslagen. Een uitgeschakelde menuoptie kan bij de andere weergave
horen, een selectie vereisen of nog in ontwikkeling zijn.

<a id="ss-topic-2-bestanden-openen-bewaren-en-sluiten"></a>

## 2. Bestanden openen, bewaren en sluiten

<a id="ss-topic-losse-opnamen"></a>

### Losse opnamen

**Bestand → Nieuw** maakt een lege golfvorm. Kies **Mono** voor één kanaal en **Stereo**
voor links/rechts. De samplerate bepaalt hoeveel audiopunten per seconde worden
bewaard. 44.100 en 48.000 Hz zijn gangbare keuzes.

**Bestand → Openen** opent een WAV- of MP3-bestand. **Opslaan** bewaart de huidige opname en
**Opslaan als** kiest een andere naam en de uitvoering WAV of MP3. **Selectie opslaan** schrijft
alleen het geselecteerde fragment naar een nieuw bestand.

Bij WAV opslaan kun je PCM met 8, 16, 24 of 32 bits kiezen, of float32. 16-bit PCM is
een praktische uitwisselkeuze; float32 bewaart ook interne pieken boven het
gewone uitvoerniveau. Een grotere bitdiepte herstelt geen detail dat al eerder
uit een opname is verdwenen.

Sommige oudere 32-bit WAV-bestanden hebben een dubbelzinnige beschrijving.
SoundSausage vraagt dan of het om gehele PCM-waarden of oudere floatwaarden gaat.
Kies de uitvoering die bij het bestand hoort; annuleren laat het bestand intact.

WAV-informatie zoals tekst, cuepunten en labels blijft behouden. Cuepunten volgen
bewerkingen en selectie-export. Plakken neemt cuepunten en labels mee; de titel
van het doelbestand blijft behouden. Extra velden hebben samen een grens van
16 MiB; bestanden met meer extra informatie worden bij openen geweigerd.
Ontbrekende informatie wordt vóór export gemeld, met een keuze om te stoppen. Bijzondere velden van recorders worden letterlijk bewaard en worden
na een effect niet opnieuw berekend. Een eindmix voegt geen markers uit alle
sporen samen. Grote WAV-export gebruikt waar nodig RF64.

<a id="ss-topic-mp3-openen-en-bewaren"></a>

### MP3 openen en bewaren

MP3-bestanden zijn net als WAV te selecteren, knippen, mengen en met effecten te
bewerken. **Audio in multitrack importeren** en slepen naar de tijdlijn werken met
beide bestandstypen. Bij **Opslaan als**, **Selectie opslaan** en **Eindmix maken**
kies je onder het bestandstype **WAV** of **MP3**. De bestandsuitgang volgt die
keuze. Opslaan van een bestaande MP3 gebruikt het eerder gekozen MP3-formaat;
met Opslaan als kun je daarvan een WAV-kopie maken.

Voor MP3 zijn 128, 192, 256 en 320 kb/s beschikbaar. Een hogere bitrate geeft
grotere bestanden en doorgaans meer detail. MP3 slaat audio met kwaliteitsverlies
op; opnieuw comprimeren kan meer detail verliezen. Een WAV-kopie voorkomt een
extra MP3-compressiestap, maar herstelt geen eerder verloren informatie. Kies
WAV float32 voor verdere bewerking, of WAV PCM16 voor eenvoudige uitwisseling.

MP3-uitvoer gebruikt de dichtstbijzijnde samplerate van 32.000, 44.100 of
48.000 Hz. De speelduur blijft behouden; het document blijft op zijn eigen
samplerate. Dit ratebereik past bij alle vier aangeboden MP3-bitrates; bij
lagere rates kan de encoder een lagere bitrate gebruiken dan gevraagd. De grens
van 2 ms vermijdt zeer korte fragmenten die na MP3-decodering langer worden.
Selecties korter dan 2 ms kunnen als WAV worden bewaard. Langere
opdrachten tonen voortgang en zijn te annuleren; een mislukte of afgebroken
opslag vervangt het bestaande doelbestand niet. Er is vrije schijfruimte nodig
voor de omzetting en de bewerkte audio.

<a id="ss-topic-mp3-bestandsinformatie-na-bewerken"></a>

### MP3-bestandsinformatie na bewerken

Titel, artiest, album, opmerkingen en ingesloten hoesafbeeldingen blijven
behouden, ook via WAV en een SoundSausage-project. De opgeslagen duur wordt
bijgewerkt. Gewone tags en bestaande identificaties blijven bij hun bestand.

**Hoofdstukken** volgen de tijdlijn automatisch. Knippen en verwijderen
schuiven latere hoofdstukken terug; invoegen schuift ze vooruit. Trimmen en
selectie-export houden overlappende hoofdstukken over en maken hun tijden
relatief aan het bewaarde fragment. Helemaal verwijderde en lege hoofdstukken
vervallen; de inhoudsopgave verwijst daarna alleen naar bestaande onderdelen.
Plakken neemt de hoofdstukken en hoofdstuknamen uit het fragment mee, met
behoud van de algemene bestandsinformatie van de bestemming. Bij tijdrekken
volgen de grenzen de nieuwe duur. Samplerateomzetting behoudt hun tijd in
milliseconden. **Ongedaan maken** herstelt ook de oorspronkelijke tags.

Hoofdstukken zijn tot milliseconden nauwkeurig. Een restant dat na afronding
geen duur heeft vervalt. Omkeren spiegelt hoofdstukken die volledig binnen het
omgekeerde gebied liggen. Hoofdstukken die door gedeeltelijk omkeren uit losse
stukken zouden bestaan vervallen, zodat de opgeslagen grenzen niet misleiden.
Hoofdstukken die het hele omgekeerde gebied omvatten blijven bestaan.

**Meetgegevens** kunnen na een bewerking niet meer bij het geluid passen.
Daarom vervallen herkende ReplayGain-, R128-, MP3Gain- en piekwaarden,
vingerafdrukken, volumeaanpassingen en oude encodergegevens na audioverandering.
Niet-ondersteunde getimede informatie, zoals gesynchroniseerde songteksten,
oude zoekindexen en synchronisatieposities, vervalt eveneens. Er wordt geen
nieuwe ReplayGain-meting uitgevoerd. Bij een tempowijziging vervalt de bestaande
BPM-waarde; bij een toonhoogtewijziging vervalt de bestaande toonsoort. Andere
bewerkingen behouden deze twee waarden. Gewone songteksten zonder tijdcodes en
onbekende privévelden blijven letterlijk behouden. Bij opnieuw opslaan als
MP3 worden oude metingen en bestandposities ook opgeschoond, omdat compressie
het geluid en de indeling kan veranderen. De nieuwe encoderinformatie wordt
uit het werkelijk geschreven MP3-bestand overgenomen.

**WAV naar MP3:** ondersteunde INFO-tekst voor titel, artiest, album, genre,
datum, tracknummer, auteursrecht en opmerkingen wordt meegenomen. Bestaande
ID3-gegevens hebben voorrang. Niet-ondersteunde velden, ongeldige INFO-inhoud
en conflicterende waarden worden vóór export gemeld. Kies **Nee** om te
annuleren en het bestaande doelbestand te bewaren, of **Ja** om met de genoemde
weglatingen door te gaan. Bevat een WAV meerdere ID3-tags, dan wordt ook
het weglaten van extra tags vooraf gemeld. Oude software-informatie wordt vervangen door de
nieuwe encoderinformatie. Ondersteunde WAV-cuepunten worden MP3-hoofdstukken. Andere niet-ondersteunde
bestandsinformatie valt onder deze keuze.

De totale extra bestandsinformatie blijft begrensd tot 16 MiB. Onleesbare
ID3-informatie in een WAV blijft als ruwe informatie bewaard; MP3-export meldt
daarvan een fout en laat een bestaand doel intact. Een eindmix neemt geen
bestandsinformatie uit alle sporen samen.

<a id="ss-topic-projecten-met-meerdere-sporen"></a>

### Projecten met meerdere sporen

**Nieuwe multitracksessie** maakt een sessie met een gekozen samplerate en aantal
sporen. **Sessie openen**, **Sessie opslaan** en **Sessie opslaan als** openen en bewaren
een volledig project. De gebruikte audio wordt in het project opgenomen, samen
met clipposities, spoorinstellingen en getekende lijnen.

| Bestand | Gebruik |
| --- | --- |
| WAV | Een losse opname of een afgemaakte eindmix |
| MP3 | Een compacte opname of eindmix, met kwaliteitsverlies |
| SoundSausage-project (`.celp`) | Een bewerkbaar project met meerdere sporen en de gebruikte audio |
| Oudere sessie (`.ses`) | Beperkte import; sla het resultaat daarna op als SoundSausage-project |

Een WAV- of MP3-eindmix bevat geen afzonderlijk bewerkbare sporen. Bewaar daarom ook het
project wanneer je later verder wilt mixen.

<a id="ss-topic-sluiten"></a>

### Sluiten

**Bestand → Sluiten** of **Ctrl+W** sluit de huidige golfvorm. In multitrack heet deze
optie **Sessie sluiten**. Het programma blijft open. Bij wijzigingen kun je
opslaan, verwerpen of annuleren. De andere weergave en het klembord blijven
beschikbaar. **Bestand → Afsluiten** of **Ctrl+Q** sluit de toepassing en vraagt ook naar
niet-opgeslagen wijzigingen.

<a id="ss-topic-lange-opnamen-en-annuleren"></a>

### Lange opnamen en annuleren

Lange opnamen worden in kleine blokken verwerkt; de grens van 128 MiB is vervallen.
De app gebruikt een eigen werkmap op schijf. Zorg voor vrije schijfruimte voor
bronkopieën, nieuwe resultaten en Ongedaan maken. Bij ruimtegebrek blijft het bestaande
werk behouden. Multitracksessies houden hun grens van 24 uur en 32 sporen.

Bij langere opdrachten verschijnt voortgang met **Annuleren**. Annuleren houdt
audio, selectie en Ongedaan maken/Redo intact; bij opslaan blijft het vorige doelbestand
intact. Eén voltooid effect blijft één Ongedaan maken-stap. Bij Voorbeeld wordt hoogstens acht
seconden resultaat voorbereid; Normaliseren analyseert wel de hele selectie.

<a id="ss-topic-werk-herstellen"></a>

### Werk herstellen

Na onverwacht afsluiten biedt SoundSausage de laatst vastgelegde stand aan.
Kies **Herstellen**, **Verwijderen** of **Later**. Met **Bestand → Werk herstellen** kun
je bewaarde herstelkopieën later openen. Andere actieve instanties worden
overgeslagen. De oorspronkelijke bestanden blijven behouden. Golfvorm, sessie,
clipinstellingen en lijnen worden hersteld; Ongedaan maken begint opnieuw.

Herstelkopieën volgen bevestigde wijzigingen; selectie en cursor volgen binnen
ongeveer een seconde. Bij ruimtegebrek meldt de statusbalk dat de herstelkopie
niet is bijgewerkt. Bewaar belangrijke opnamen zelf: herstel vervangt geen backup.
Na gewoon opslaan of bevestigd sluiten wordt de eigen kopie opgeruimd. Zie
[lange bestanden en herstel](https://github.com/rene-timmermans/SoundSausage/blob/main/docs/LANGE_BESTANDEN.md)
voor werkruimte en grenzen.

<a id="ss-topic-3-luisteren-en-navigeren"></a>

## 3. Luisteren en navigeren

**Spatie** start of stopt het afspelen. Met een selectie luister je naar dat
fragment; zonder selectie begint het afspelen bij de cursor. **P** pauzeert en
hervat. **Esc** stopt. **Herhalen** herhaalt het gekozen afspeelbereik. Lussen kunnen
nog een korte overgang hebben.

**Home** gaat naar het begin en **Einde** naar het einde. De navigatieknoppen laten
je ook vijf seconden terug of vooruit springen. Navigeren of een bevestigde
bewerking uitvoeren stopt lopend afspelen; start daarna opnieuw om het nieuwe
resultaat te horen.

Gebruik **Inzoomen**, **Uitzoomen**, **Volledig overzicht** en **Inzoomen op selectie** onder
**Beeld**. **Ctrl+0** toont de hele opname; **Ctrl+Shift+A** vult de weergave met de
selectie. **Ctrl+muiswiel** zoomt rond de muispositie. De horizontale schuifbalk
verplaatst het zichtbare tijdvak.

<a id="ss-topic-het-uitvoerapparaat-kiezen"></a>

### Het uitvoerapparaat kiezen

Openen **Opties → Audioapparaten**. Kies **Systeemstandaard** om de systeemuitgang
te volgen of selecteer een specifiek apparaat. De keuze blijft bewaard.
Dezelfde uitgang wordt gebruikt voor normaal afspelen en effectvoorbeelden.

De **Afspeelbuffer** staat standaard op 100 ms. Een grotere waarde verdraagt
onderbrekingen beter; een kleinere reageert sneller. De werkelijke buffer kan
per apparaat verschillen. Instellingen wijzigen stopt het afspelen en voorbeelden.

Als een gekozen apparaat verdwijnt, kies je opnieuw een beschikbare uitgang en
start je het afspelen. Controleer bij ontbrekend geluid ook het systeemvolume,
de systeemuitgang en eventuele Dempen- of Solo-knoppen in multitrack.

<a id="ss-topic-3a-opnemen"></a>

## 3a. Opnemen

<a id="ss-topic-een-opname-maken"></a>

### Een opname maken

1. Sluit een microfoon of audio-interface aan. Kies de ingang onder
   **Opties → Audioapparaten → Opnameapparaat**. De keuze blijft bewaard.
2. Druk op **R** of de ronde opnameknop. Controleer **Ingang** in het opnamevenster.
3. Kies **Bestemming**. **Nieuwe golfvorm** maakt een losse opname. Bij een bestaande
   golfvorm kun je **Invoegen bij cursor** kiezen, of **Selectie vervangen** wanneer
   er een selectie is. In multitrack wordt een nieuw blok op het gekozen spoor
   toegevoegd, vanaf de cursor. Bestaande blokken blijven behouden.
4. Kies **Mono** of **Stereo**. **Eerste invoerkanaal** kiest één ingang bij mono
   of de eerste van een opeenvolgend paar bij stereo. Een monoapparaat kan op
   beide stereokanalen worden opgenomen. Het invoegdoel bepaalt samplerate en,
   bij een bestaande golfvorm, kanaalaantal. Een andere apparaatrate wordt na
   Stoppen omgezet. **Maximale duur** kan automatisch stoppen; **Tot stoppen**
   blijft doorlopen totdat je zelf stopt of de schijf geen ruimte meer heeft.
5. Kies **Opname starten**. De live golfvorm toont de laatste twintig seconden;
   de grote klok toont de totale vastgelegde duur. De meters tonen het ingangsniveau.
6. **P** pauzeert en hervat. Pauzetijd komt niet in de opname. **Stoppen**, **Esc**,
   **Spatie** of de opnameknop stopt en bewaart de take in het gekozen doel.

Bij het invoegen of vervangen is de gehele opname één Ongedaan maken-stap. Ook een nieuw
opgenomen blok in multitrack is met Ongedaan maken te verwijderen. Een nieuwe golfvorm
is pas als bestand bewaard nadat je **Opslaan** of **Opslaan als** kiest.

**Opname verwerpen** verwijdert uitsluitend de lopende take en vraagt om een
bevestiging. Tijdens opname staan andere bewerkingen uit. Sluiten vraagt of de
opname moet worden gestopt en behouden, verworpen of doorgezet. Daarna gelden
de gewone vragen voor niet-opgeslagen werk.

<a id="ss-topic-het-opnamebegin-overslaan"></a>

### Het opnamebegin overslaan

**Begin overslaan** in het opnamevenster verwijdert eenmalig de eerste
milliseconden om een inschakelklik buiten de opname te houden. De beginwaarde is
50 ms; kies een waarde van 0 tot 500 ms. De keuze blijft bewaard. Met **0 ms**
wordt het volledige begin opgenomen. Bij een uitsnede volgt een fade-in van
5 ms om een harde overgang te vermijden.

Het overgeslagen geluid komt niet in de opname. De klok, golfvorm, meters en
**Maximale duur** volgen de bewaarde audio. Pauzeren en hervatten herhalen de
uitsnede niet. Bij opname met begeleiding wordt de uitgesneden tijd in de
clippositie meegenomen, zodat het overgebleven geluid op zijn plaats blijft.

<a id="ss-topic-systeemgeluid-opnemen-wat-je-hoort"></a>

### Systeemgeluid opnemen (wat je hoort)

Kies **Opties → Audioapparaten → Opnameapparaat → Systeemgeluid (wat je hoort)** om
de standaarduitgang van Linux op te nemen. Dezelfde keuze staat onder **Ingang**
in het opnamevenster. Er wordt geen microfoon gebruikt. De bron blijft onthouden.

1. Kies in de geluidsinstellingen van Linux de uitgang waarop de gewenste app afspeelt.
2. Speel bijvoorbeeld muziek uit een browser af, druk in SoundSausage op **R** en kies Systeemgeluid.
3. Kies **Stereo** om links en rechts te bewaren, of **Mono** met ingangskanaal 1 voor links of 2 voor rechts.
4. Start de opname. **P** pauzeert/hervat zonder de pauzetijd mee te nemen; **Stop** bewaart de opname. Bewerk en bewaar daarna als WAV of MP3.

Een nieuwe opname bepaalt de actuele standaarduitgang. Die kan verschillen van
het afspeelapparaat dat afzonderlijk in SoundSausage is gekozen. Alleen geluid
op die ene uitgang wordt opgenomen; apps op een andere uitgang ontbreken.
Ook SoundSausage-begeleiding die op dezelfde uitgang afspeelt komt in de opname.
De teruggelezen niveaus volgen de audiomixer en kunnen afwijken van de fysieke
luidsprekersterkte. Invoer wordt niet opnieuw via de luidsprekers afgespeeld.

Deze bron werkt met PulseAudio of de PulseAudio-ondersteuning van PipeWire.
De installatiepakketten nemen de benodigde clienthulpmiddelen mee. Een ontbrekende
uitgang, verbinding of hulpmiddel geeft een melding; er wordt niet op een microfoon
teruggevallen. Wissel de standaarduitgang tussen opnamen. Als een uitgangswissel
of verlies tijdens opnemen wordt gemeld, blijft de reeds opgenomen take bewaard.
Stop, herstel de route en start opnieuw. De gewone keuze **Systeemstandaard** blijft
de standaardmicrofoon of audio-ingang, en verschilt dus van **Systeemgeluid**.

<a id="ss-topic-ingang-en-herstel"></a>

### Ingang en herstel

De microfoon wordt pas geopend na **Opname starten**. SoundSausage speelt het
ingangssignaal niet door de luidsprekers. In multitrack kan **Bestaande sporen afspelen tijdens opnemen** de bestaande sporen laten horen. **P** pauzeert/hervat dan
opname én begeleiding. Zie hoofdstuk 8a voor de complete werkwijze en het
afstellen van de opnamepositie.

Is een specifiek gekozen USB-apparaat verdwenen, kies dan een beschikbare ingang.
Tijdens een opname leidt apparaatverlies niet naar een andere microfoon: de app
stopt en behoudt de vastgelegde audio. Het ingangsniveau regel je op de microfoon,
audio-interface of in de geluidsinstellingen van Linux. Verhoog het zo nodig
voordat je begint; vervorming door een overstuurde ingang is achteraf niet te herstellen.

Opnamen worden in blokken naar een eigen werkbestand geschreven. Er is voldoende
vrije schijfruimte nodig voor de take, het resultaat en Ongedaan maken. De opname krijgt
ongeveer iedere seconde een herstelpunt. Na onverwacht afsluiten biedt de volgende
start de onderbroken opname apart aan. **Bestand → Werk herstellen** kan dat later ook.
Herstellen opent de laatst vastgelegde audio als nieuwe golfvorm, zonder de
bronbestanden of de multitracksessie te overschrijven. Bij een schrijffout kan
het laatste herstelpunt iets ouder zijn dan de klok aangaf.

Annuleer je de verwerking ná Stoppen, bijvoorbeeld een langere omzetting, dan blijft
de take voor herstel bewaard. Het eerdere document is dan niet aangepast.

<a id="ss-topic-een-dagelijkse-werkwijze"></a>

### Een dagelijkse werkwijze

Een bruikbare volgorde is: opnemen of WAV openen → een fragment selecteren →
eventueel Normaliseren, fade of een ander Amplitude-effect toepassen → opslaan →
in multitrack invoegen → verdere takes op een spoor opnemen → clips verschuiven
of hun volume/pan aanpassen → het project bewaren → een WAV-eindmix maken.
Bewaar het project ook als je later nog afzonderlijke sporen wilt veranderen.
Heropen het project om verder te werken; een eindmix bevat alleen de gecombineerde audio.

<a id="ss-topic-4-selecteren-en-de-golfvorm-bewerken"></a>

## 4. Selecteren en de golfvorm bewerken

Klik in de golfvorm om de cursor te plaatsen. Sleep met de linkermuisknop om een
fragment te selecteren. **Shift+klik** breidt de selectie vanaf het bestaande
begin uit en houdt de kanaalkeuze vast. **Ctrl+A** selecteert de hele duur in de
huidige kanaalkeuze.

**Bewerken → Selectie instellen** voert begin en einde precies in. Deze velden gebruiken
frames: bij 44.100 Hz zijn 44.100 frames één seconde. **F4** verplaatst de grenzen
van een selectie naar binnen, naar nuldoorgangen in het gekozen kanaal
(bij Beide in links). Dat kan
een abrupte overgang verminderen; luister het resultaat altijd na.

| Opdracht | Wat gebeurt er? |
| --- | --- |
| Knippen | Verwijdert de selectie en zet haar op het klembord |
| Kopiëren | Kopieert de selectie zonder de opname te veranderen |
| Plakken | Vervangt de selectie, of voegt bij de cursor in |
| Gemengd plakken | Mengt de klembordaudio met de bestaande audio vanaf de selectie of cursor |
| Selectie verwijderen | Verwijdert het geselecteerde fragment |
| Trimmen | Houdt alleen de selectie over |
| Ongedaan maken / Opnieuw uitvoeren | Maakt de laatste bewerking ongedaan of voert haar opnieuw uit |

Plakken zet de samplerate zo nodig om. Het klembord blijft ongewijzigd. Bij Beide
moet het aantal kanalen overeenkomen. Bij Links of Rechts kan mono-audio het
geselecteerde tijdvak van dat kanaal vervangen. Meer hierover staat hieronder.
Gemengd plakken kan luider uitvallen doordat twee signalen worden opgeteld.

<a id="ss-topic-4a-links-rechts-en-stereo-kiezen"></a>

## 4a. Links, rechts en stereo kiezen

Een stereogolfvorm heeft een linker kanaal **L** boven en een rechter kanaal
**R** onder. Je kunt hetzelfde tijdvak voor beide kanalen kiezen of slechts
één kanaal bewerken.

- Sleep binnen L om alleen links te selecteren, of binnen R voor alleen rechts.
- Sleep van de ene golf naar de andere om beide kanalen te selecteren.
- Kies boven de golfvorm **Kanalen → Beide (L+R), Links (L) of Rechts (R)** om
  een bestaand tijdvak op andere kanalen te richten.
- Dezelfde keuze staat onder **Bewerken → Kanalen selecteren**. **Alt+B**, **Alt+L**
  en **Alt+R** kiezen beide, links en rechts.

Het geselecteerde kanaal heeft een gekleurd L/R-label. Een geselecteerd tijdvak
is alleen in de gekozen kanalen ingekleurd. **Shift** houdt bij het verlengen
van een selectie de kanaalkeuze vast. Dubbelklikken kiest het zichtbare tijdvak
in het aangeklikte kanaal. **Ctrl+A** selecteert de hele duur in de huidige
kanaalkeuze. Bij mono is er één kanaal en staat de extra keuze niet in beeld.

<a id="ss-topic-een-effect-op-een-kanaal"></a>

### Een effect op één kanaal

Kies bijvoorbeeld Rechts, selecteer een fragment en open Versterken / vervagen of
Normaliseren. Het effectvenster vermeldt de gekozen kanalen. Met Voorbeeld hoor je
het resultaat in stereocontext: het andere kanaal blijft ongewijzigd. OK past
alleen het gekozen kanaal toe; Ctrl+Z herstelt de audio én de bijbehorende keuze.
F2 herhaalt de laatste instellingen op de kanalen die op dat moment gekozen zijn.

Zonder tijdselectie werkt een effect op de hele duur van het gekozen kanaal.
Normaliseren en Dynamiek analyseren daarbij alleen dat kanaal. Kanalenmixer kan
beide kanalen als invoer gebruiken, maar wijzigt alleen de gekozen uitgang.
Bij een stereo-ruisprofiel of stereo-impulsrespons wordt het bijbehorende kanaal
gebruikt. Frequentieanalyse volgt eveneens de gekozen kanalen.

<a id="ss-topic-duur-veranderen-op-een-kanaal"></a>

### Duur veranderen op één kanaal

Bij **Links** of **Rechts** verschuift alleen het gekozen kanaal door knippen,
verwijderen, plakken, tijdrekken, tonen/stilte invoegen of een uitklank toevoegen.
Het andere kanaal behoudt exact zijn samples op de oorspronkelijke tijdstippen.
Het kortere kanaal krijgt achteraan stilte zodat beide even lang blijven.
Bij **Beide** verschuiven de twee kanalen en gezamenlijke markeringen samen.
Met **Stilte** onder Effecten blijft ook het gekozen kanaal op zijn plaats.

Voorbeeld: verwijder seconde 2–3 uit Links. De latere linker audio schuift één
seconde naar voren en Links krijgt achteraan één seconde stilte. Rechts blijft
staan. Voeg op dezelfde positie twee seconden toe en alleen de latere linker
audio schuift twee seconden op; Rechts krijgt zo nodig achteraan stilte.
**Trimmen** zet alleen het gekozen fragment van het gekozen kanaal op tijdstip
nul en vult de rest met stilte. De andere golf blijft op haar plaats.

De opvulling is gewone audio en blijft bij opslaan en heropenen bewaard. Een latere
invoeging verschuift ook die stilte; verwijder ongewenste eindstilte met Beide
gekozen. Gezamenlijke cuepunten en MP3-hoofdstukken blijven bij bewerken van
één kanaal op hun tijdstippen staan. Controleer hun betekenis na een verschuiving.
Undo/Redo herstelt de audio, opvulling, metadata en kanaalkeuze.

<a id="ss-topic-kopieren-plakken-en-bewaren"></a>

### Kopiëren, plakken en bewaren

Kopiëren en Selectie opslaan leveren bij Links of Rechts mono-audio. Opslaan en
Opslaan als bewaren de volledige stereogolfvorm. Mono-audio kan in één kanaal
worden ingevoegd of een korter of langer tijdvak vervangen. Bij een stereoklembord
wordt het overeenkomstige linker- of rechterkanaal gebruikt. De samplerate wordt
zo nodig omgezet. Markeringen en hoofdstukken uit het klembord worden alleen bij
Beide samengevoegd; bij één kanaal blijven de bestaande gezamenlijke markeringen staan.

**Gemengd plakken** telt op vanaf het begin van de selectie of de cursor, zonder
latere audio te verschuiven. Het kan voorbij het einde doorlopen; het andere
kanaal wordt dan achteraan met stilte aangevuld. De optelling kan luider uitvallen.

<a id="ss-topic-opnemen-in-een-kanaal"></a>

### Opnemen in één kanaal

Kies Links of Rechts en druk **R**. Kies **Invoegen bij cursor** of **Selectie vervangen**.
De opname gebruikt mono en de bestaande samplerate. **Eerste ingangskanaal** kiest de
hardware-ingang; die staat los van de linker- of rechterbestemming. Na Stoppen
verschuift alleen het gekozen kanaal en wordt zo nodig achteraan stilte toegevoegd.
Een nieuwe golfvorm blijft als aparte bestemming beschikbaar. Tijdens opnemen
is de kanaalkeuze vergrendeld. Een nog niet toegepaste take blijft bij een fout of
annulering beschikbaar onder Werk herstellen. Afspelen blijft in stereocontext.

<a id="ss-topic-zoomen-en-functie-iconen"></a>

### Zoomen en functie-iconen

**Volledig overzicht** toont de gehele opname; het vergrootglas heeft markeringen naar
de buitenste grenzen. **Inzoomen op selectie** vult het beeld met het geselecteerde
tijdvak; het vergrootglas bevat een gemarkeerd selectievak. De knoppen hebben
verschillende iconen en aanwijzingen bij de muis.

De golfvorm blijft bij tussenliggende zoomniveaus doorlopend. Dichtbij worden
afzonderlijke samples met elkaar verbonden. Verder uitgezoomd toont de app de
minimale en maximale uitslagen per schermkolom, met behoud van pieken. Dit werkt
ook op multitrackclips en verandert de geluidsdata niet. Functies in de menu's
hebben eigen iconen die het Linux-palet en de accentkleur volgen.

<a id="ss-topic-afzonderlijke-samples-bewerken"></a>

### Afzonderlijke samples bewerken

Zoom met **+** of **Ctrl+muiswiel** in op een tikje totdat de vierkante
samplepunten zichtbaar zijn (vanaf twee logische schermpixels tussen samples). De as
onder de golfvorm toont dan sample-indexen, geteld vanaf 0. Sleep een punt
verticaal om uitsluitend die sample in dat kanaal te wijzigen. De horizontale
positie blijft vast; ook wanneer de muis andere punten of het andere kanaal
passeert. Tijdens het slepen zie je een voorbeeld; loslaten bevestigt de
correctie. **Escape** annuleert zonder iets te wijzigen. Met **Shift+slepen**
kun je ook tussen de samplepunten gewoon audio selecteren.

Dubbelklik of klik met rechts op een punt voor **Sample bewerken**. Je kunt
ook **Bewerken → Sample bewerken** kiezen, ongeacht het zoomniveau. Het venster
begint bij de cursor en het eerste gekozen kanaal; sample-index en kanaal zijn
aanpasbaar. Voer de waarde genormaliseerd in, of toon die als 8-, 16- of 24-bit
met teken. Nul is stilte; −1 en +1 zijn het normale volledige uitvoerniveau.
Bijvoorbeeld: −16384 in de 16-bitweergave is −0,5 genormaliseerd. Wisselen van
weergavebereik verandert de audio of het bestandsformaat niet. **OK** past de
waarde toe; **Annuleren** behoudt het origineel.

Elke sleepbeweging of bevestigde waarde vormt één stap **Ongedaan maken** /
**Opnieuw**. Alle andere samples, het andere kanaal, duur en metadata blijven
behouden. Slepen is begrensd tot −1 … +1; bestaande pieken boven dit bereik
blijven numeriek beschikbaar. Tijdens opnemen is samplebewerking geblokkeerd;
bij het beginnen van een correctie stopt afspelen. Bewerk een multitrackclip
via de golfvormkopie en pas die daarna expliciet toe op de clip.

Beluister het korte fragment na iedere correctie. Voor een tikje van meerdere
samples kun je de betrokken punten één voor één naar het verloop van de
omliggende golf brengen. Een grote sprong naar nul kan zelf een tik veroorzaken.
Bewaar bij voorkeur als WAV float32 om de interne correctie exact te behouden;
MP3 opnieuw opslaan comprimeert het gehele bestand opnieuw met kwaliteitsverlies.

<a id="ss-topic-golfvorm-tekenen"></a>

### Golfvorm tekenen

Schakel **Bewerken → Golfvorm tekenen** in, druk op **D** of gebruik de
potloodknop naast de zoomknoppen. Teken met de linkermuisknop rechtstreeks op de
golfvorm; afzonderlijke samplepunten raken is niet nodig. De getekende lijn
vervangt de samplewaarden, binnen −1 tot +1. Dit verschuift de bestaande golf
niet: het verloop onder de lijn wordt opnieuw getekend.

De zoom bepaalt de grootte van een groep: ongeveer twee logische schermpixels
audio per groep, afgerond naar hele samples. Bij sterke vergroting verandert
één sample; verder uitgezoomd veranderen meerdere samples samen. Een groep
beslaat nooit meer dan één seconde audio. Een langere sleepbeweging kan meerdere
groepen raken en dus in totaal meer dan één seconde wijzigen. Tussen opeenvolgende
muisposities wordt het getekende verloop met rechte lijnen verbonden; bij opnieuw
over hetzelfde stukje tekenen telt de laatste beweging.

Het kanaal waarin je begint blijft vast, ook als de muis het andere kanaal
passeert. Andere samples, het andere kanaal, duur en metadata blijven behouden.
Tijdens tekenen toont een gemarkeerd vlak de betrokken groepjes met de nieuwe
lijn. Loslaten bevestigt de hele beweging als één **Ongedaan maken**-stap.
**Escape**, focusverlies, zoomen of uitschakelen van de tekenmodus annuleert
het voorbeeld. **Shift+slepen** blijft audio selecteren; druk opnieuw op **D**
om terug te keren naar de gewone bediening. Tijdens opnemen is tekenen geblokkeerd.

Zoom voldoende in voor nauwkeurig herstel: een uitgezoomde correctie vervangt
ook de kleine details binnen het geraakte groepje. Beluister het resultaat en
gebruik zo nodig **Ctrl+Z**. Voor een multitrackclip bewerk je de golfvormkopie
en pas je die daarna toe op de clip.

<a id="ss-topic-4b-markeringen"></a>

## 4b. Markeringen

Druk **M** om bij de cursor een markering toe te voegen. Open **Bewerken → Markeringenlijst** met **Ctrl+Shift+M** om markeringen te benoemen, verplaatsen, verwijderen of met **Ga naar** te bezoeken. **Alt+Links/Rechts** springt naar de vorige/volgende markering. Dubbelklik op een vlag boven de golfvorm voor de eigenschappen. Versleep een vlag voor een nieuwe positie; **Escape** annuleert het slepen. Loslaten maakt één stap voor **Ongedaan maken**.

De eigenschappen bieden een tijd in seconden en een exact sampleframe. Nieuwe namen mogen maximaal 256 tekens bevatten, zonder besturingstekens. Bestaande MP3-hoofdstukken hebben eventueel ook een eindpositie; die moet na het begin en binnen de opname liggen. Nieuwe markeringen zijn punten, geen nieuwe hoofdstukbereiken.

Golfvormmarkeringen gelden voor beide kanalen. Tijdwijzigingen met **Beide** verplaatsen ze mee; bij bewerken van één kanaal blijven ze op hun gedeelde positie. Verplaatsen en benoemen verandert geen samples. In multitrack blijven sessiemarkeringen op hun absolute tijdlijnpositie als clips verschuiven. Ze mogen voorbij de laatste clip staan, maar verlengen de eindmix niet. Bronmarkeringen blijven bij de bron bewaard; de eindmix bevat alleen eigen sessiemarkeringen binnen de audioduur. Bronmarkeringen worden niet automatisch samengevoegd.

WAV bewaart cuepunten en labels. Bij MP3-export worden deze hoofdstukken met millisecondenposities; WAV-posities blijven op sampleframes nauwkeurig. Projecten en crashherstel bewaren sessiemarkeringen, inclusief Undo/Redo tijdens het werken. Nieuw opgeslagen projecten vereisen **0.26.0 of nieuwer**; oudere projecten blijven leesbaar. Maximaal 4096 markeringen zijn bewerkbaar. Afwijkende cuegegevens blijven bewaard, maar worden geweigerd als veilig bewerken niet mogelijk is. Een bestaande WAV-tekenset kan de beschikbare naamtekens beperken.

<a id="ss-topic-5-effecten-toepassen"></a>

## 5. Effecten toepassen

Een golfvormeffect werkt op het gekozen tijdvak en de gekozen kanalen. Zonder
tijdselectie wordt de hele duur van die kanalen bewerkt. Het andere kanaal blijft
ongewijzigd en is bij Voorbeeld wel hoorbaar in de bestaande stereocontext. De opdrachten staan onder **Effecten**. Voor effecten op een
multitrackclip gebruik je eerst **Kopie in golfvorm bewerken**; verderop staat hoe je
het resultaat terugplaatst.

In de Amplitude-, EQ-, filter-, delay- en galmvensters speelt **Voorbeeld** de eerste acht seconden van het
resultaat zonder de opname te veranderen. Opnieuw klikken stopt het voorbeeld.
Een instelling wijzigen of het venster sluiten stopt het ook. **OK** past toe;
**Annuleren** laat de opname zoals ze was. **Ctrl+Z** draait de toepassing terug.

**F2** of **Bewerken → Laatste opdracht herhalen** herhaalt het laatste golfvormeffect met
dezelfde instellingen op de nieuwe selectie en de huidige kanaalkeuze. Controleer
het tijdvak en de kanalen voordat je herhaalt.

<a id="ss-topic-remaster"></a>

### Remaster

Open **Effecten → Remaster…** wanneer stemmen of instrumenten bij drumslagen kort wegzakken, of een mix hoorbare korte volume-cuts bevat. Remaster zoekt zulke dalingen en versterkt de nog aanwezige details plaatselijk. Het werkt op de selectie of, zonder selectie, op de hele golfvorm.

<a id="ss-topic-welke-remaster-stand-kiezen"></a>

#### Welke Remaster-stand kiezen?

| Stand | Pompeffect verminderen / Maximaal herstel | Drumdrempel / Hersteltijd | Herstel korte volumedalingen |
| --- | --- | --- | --- |
| Voorzichtig herstel | 35% / 2 dB | 4 dB / 160 ms | 0 dB: uit |
| Evenwichtig herstel | 60% / 4 dB | 3 dB / 180 ms | 0 dB: uit |
| Sterk herstel | 90% / 6 dB | 2 dB / 240 ms | 0 dB: uit |
| Korte volumedalingen | 90% / 6 dB | 2 dB / 240 ms | 12 dB |

Begin met **Evenwichtig herstel** bij licht pompen. **Voorzichtig herstel** verandert minder. **Sterk herstel** laat meer herstel toe en reageert op zwakkere drumaanzetten. **Korte volumedalingen** heeft dezelfde gewone instellingen als Sterk herstel en schakelt daarnaast de snellere regeling voor diepe, korte gaten in. Een hogere sterkte alleen schakelt die extra regeling niet in.

Een preset verandert alleen de vijf instellingen in de tabel. Uitvoerplafond, luisterpositie en de keuze voor gelijk luistervolume blijven op hun huidige waarde staan. Het uitvoerplafond begint bij −1 dBFS. **Aangepast** behoudt de huidige waarden. Handmatig wijzigen van een herstelinstelling of het uitvoerplafond kiest deze stand; de luisterpositie en volumevergelijking doen dat niet.

<a id="ss-topic-wat-gebeurt-er-met-het-geluid"></a>

#### Wat gebeurt er met het geluid?

Het gewone herstel schat welke delen van het midden en hoog aanhoudend klinken, bijvoorbeeld zang, gitaar of een synthesizer. Het vergelijkt hun niveau met de omgeving en zoekt korte tekorten rond gedetecteerde bas- of percussieaanzetten. Alleen het gevonden tekort krijgt begrensde versterking; het vormt geen afzonderlijke zang- of instrumentensporen.

De extra regeling voor korte volumedalingen meet het midden en hoog over ongeveer **4 ms**, met een nieuwe meting per circa **1 ms**. Ze vergelijkt de **20–80 ms vóór en na** een mogelijke dip. Beide kanten moeten voldoende geluid bevatten. De regeling zoekt dalingen van ongeveer **6–120 ms** en ten minste **4 dB**, gekoppeld aan drumdetectie. Zo worden lange pauzes, zeer stille passages en geleidelijke fades zo veel mogelijk overgeslagen.

Bij een geschikt gat vervangt de snellere regeling plaatselijk het gewone herstel. De twee versterkingen worden niet opgeteld. Een korte, vloeiende overgang en snelle terugregeling beperken uitschieters zodra het geluid terugkomt. De extra regeling heeft eigen snelle reactietijden; **Hersteltijd** in het venster bepaalt hoe lang de drumdetectie blijft meetellen.

Bas onder circa **180 Hz** krijgt geen herstelversterking; de overgang naar midden/hoog loopt tot ongeveer **600 Hz**. Met **Beide** delen links en rechts dezelfde regeling. Met **Links/Rechts** wordt alleen dat kanaal bewerkt. Speelduur, samplerate en markerposities blijven gelijk.

<a id="ss-topic-wat-veranderen-de-remaster-instellingen"></a>

#### Wat veranderen de Remaster-instellingen?

| Instelling | Werking en verwachting |
| --- | --- |
| Pompeffect verminderen | 0–100%; schaalt de sterkte van beide herstelregelingen. Een percentage is geen garantie dat zoveel van de oorspronkelijke mix wordt hersteld. Bij 0% zijn beide herstelregelingen uit; het uitvoerplafond blijft werken. |
| Maximaal herstel | 0–9 dB; begrenst het gewone herstel vóór de sterkteschaal en vloeiende regeling. 0 dB zet alleen het gewone herstel uit. |
| Herstel korte volumedalingen | 0–18 dB; aparte grens voor snelle gaten, vóór de sterkteschaal. 0 dB zet deze extra regeling uit. Begin bij diepe cuts met 12 dB en wijzig in kleine stappen. |
| Drumdrempel | 0–12 dB; lager laat meer aanzetten meetellen, hoger beperkt het herstel tot sterkere aanzetten. Dit beïnvloedt ook wanneer de extra korte-dipregeling mag ingrijpen. |
| Hersteltijd | 50–500 ms; langer laat de drumdetectie langer doorwerken na een aanzet. Dit verandert niet de vaste snelle meetvensters van het extra herstel. |
| Uitvoerplafond | −12 tot 0 dBFS; standaard −1 dBFS. Als nodig verlaagt één constante factor het hele bewerkte bereik om samplepieken onder dit plafond te houden. Rustige passages worden daarbij niet automatisch naar het plafond opgetrokken. Het is geen true-peaklimiter. |
| Voorbeeld vanaf | Luisterpositie in seconden binnen het bewerkingsbereik. Verplaatsen verandert alleen het luisterfragment. |

**12 dB herstelruimte betekent geen vaste verhoging van 12 dB.** Bij de presetsterkte van 90% is de nominale bovengrens voor de snelle herstelregeling 10,8 dB. Detectie, gevonden tekort, frequentiebereik en vloeiende overgangen kunnen de werkelijke correctie kleiner maken. Ook de constante eindverzwakking beïnvloedt het uiteindelijke niveau.

<a id="ss-topic-remaster-vergelijken-en-toepassen"></a>

#### Remaster vergelijken en toepassen

1. Open de oorspronkelijke opname. Gebruik bij voorkeur de hele golfvorm voor één gezamenlijk eindniveau. Bij een selectie laat je ongeveer een seconde context aan beide kanten staan en controleer je de overgangen na toepassen.
2. Zet de cursor bij een probleemfragment en open Remaster. Kies een preset; gebruik **Korte volumedalingen** als Sterk herstel nog korte cuts overlaat.
3. Vergelijk **Origineel** en **Voorbeeld** met **Luistervolume van origineel en voorbeeld gelijkmaken** aan. Beide spelen maximaal acht seconden vanaf de gekozen positie. De gelijkmaking gebruikt het gemiddelde niveau (RMS) van het luisterfragment en verandert het opgeslagen resultaat niet.
4. Luister ook naar een rustige passage en het einde. Verlaag sterkte of herstelruimte als instrumenten te fel worden, ruis opvalt of natuurlijke accenten verdwijnen.
5. **OK** past toe; **Annuleren** laat de golfvorm intact. **Ctrl+Z** herstelt het origineel. Vergelijk presets steeds vanaf dat origineel; opnieuw toepassen en **F2** verwerken het huidige geluid nogmaals. Bewaar met **Opslaan als** eventueel een nieuwe WAV.

Het eerste luistervoorbeeld analyseert het hele bereik, met voortgang en annuleren. Alleen de luisterpositie of volumevergelijking wijzigen hergebruikt de berekening. Na afloop kan de opname als geheel zachter zijn door de gereserveerde piekruimte, terwijl de korte terugvallen minder hoorbaar zijn.

<a id="ss-topic-wat-kun-je-van-remaster-verwachten"></a>

#### Wat kun je van Remaster verwachten?

Een passende opname kan gelijkmatiger klinken doordat nog aanwezige stemmen en instrumenten bij drums minder wegzakken. Een schone mix kan weinig veranderen. Niet elke dip voldoet aan de detectievoorwaarden; sterke of langere terugvallen kunnen blijven bestaan. Bewuste muzikale cuts kunnen juist onterecht worden verzacht.

Sterke instellingen kunnen klankkleur, balans en natuurlijke dynamiek veranderen of bestaande ruis/vervorming hoorbaarder maken. Remaster reconstrueert geen volledig ontbrekend instrument, verwijdert geen clipping en herstelt geen verloren MP3-detail. Stilte of een uitfade wordt niet met nieuwe muziek ingevuld. Beluister de vergelijking op gelijk gemiddeld niveau en beoordeel ook het muzikale resultaat.

| Bewerking | Doel en verschil |
| --- | --- |
| Versterken / vervagen | Past een gekozen versterking of fade toe; zoekt geen plaatselijke volumegaten. |
| Normaliseren | Past het hele bereik met één factor aan op de gekozen piek; korte niveauverschillen binnen dat bereik blijven bestaan. |
| Dynamiekbewerking | Verandert het niveau volgens de ingestelde dynamiekcurve en detectietijden; zoekt geen korte gaten met geluid vóór en na de dip als referentie. |
| Remaster | Zoekt geschikte, tijdelijk wegzakkende delen van midden/hoog en probeert die plaatselijk te herstellen. |

Remaster is een golfvormbewerking. Het staat niet in de realtime spoorketen.

<a id="ss-topic-versterken-vervagen"></a>

### Versterken / vervagen

Openen **Effecten → Amplitude → Versterken / vervagen**. **Beginversterking** is de
versterking aan het begin; **Eindversterking** die aan het einde. 100% houdt
het niveau gelijk, 50% halveert de amplitude en 200% verdubbelt haar.

**Links en rechts koppelen** houdt de kanalen gelijk. **Begin- en eindversterking gelijk houden** geeft een constante versterking. Zet die optie uit voor
een fade. Lineaire fades kunnen tot stilte lopen; logaritmische fades vereisen
positieve begin- en eindwaarden. Presets bieden ongeveer +6 of −6 dB en fades.

Voorbeeld: selecteer het begin van een opname, kies **Invloeien** als preset en
luister met Voorbeeld. Pas met OK toe. **Invloeien** en **Uitvloeien** staan ook als
directe opdrachten onder Amplitude; deze passen onmiddellijk een lineaire fade toe.

<a id="ss-topic-kanalenmixer"></a>

### Kanalenmixer

**Effecten → Amplitude → Kanalenmixer** is beschikbaar voor stereo. Voor elk
nieuw kanaal kies je hoeveel van het oorspronkelijke linker- en rechterkanaal
wordt gebruikt. Negatieve percentages keren de polariteit van een bijdrage om;
**Uitgangspolariteit omkeren** keert het hele nieuwe kanaal om.

Presets wisselen links en rechts, kopiëren één kant naar beide kanten, middelen
beide kanalen naar mono of maken het verschil tussen links en rechts. De
mono-mix blijft een stereobestand met twee gelijke kanalen.

Voorbeeld: kies **Links en rechts wisselen** om omgekeerd aangesloten kanalen te wisselen.
Kies **Mono (gemiddelde L + R)** om een gelijke mix op beide kanten te horen. Door
mengen kan het niveau stijgen; verlaag zo nodig de percentages.

<a id="ss-topic-dynamiekbewerking"></a>

### Dynamiekbewerking

**Effecten → Amplitude → Dynamiekbewerking** verandert het verschil tussen
zachte en harde passages. De curve koppelt het ingangsniveau aan het gewenste
uitgangsniveau. Onder de diagonale lijn wordt een niveau zachter; erboven luider.

Klik in de curve om een punt toe te voegen en sleep om het te veranderen. De
velden onder de curve bieden precieze invoer. Rechtsklikken, **Punt verwijderen**
of **Verwijderen** verwijdert een binnenpunt. De horizontale eindposities staan vast.

| Instelling | Betekenis |
| --- | --- |
| Aanspreektijd | Hoe snel de detector op een hogere piek reageert |
| Hersteltijd | Hoe snel de regeling na een piek terugloopt |
| Uitgangsversterking | Versterking of verzwakking van het resultaat |
| Stereokanalen koppelen | Beide kanalen krijgen dezelfde regeling, zodat hun onderlinge balans blijft bestaan |

Een **compressor** verkleint niveauverschillen boven een drempel. Een
**piekbegrenzer** temt harde pieken. Een **gate** of **expander** maakt zachte
passages zachter; deze verwijdert niet automatisch alle ruis.

Begin bijvoorbeeld met **Compressor (3:1 boven −18 dB)** op een spraakfragment.
Luister of zachte woorden verstaanbaar blijven en harde woorden rustiger
klinken. Gebruik Uitgangsversterking om het resultaat daarna op een passend niveau te
brengen. De piekbegrenzerpreset gebruikt een attack van nul; met een langzamere
attack kunnen korte pieken erdoorheen komen. Er is nog geen vooruitblik.

<a id="ss-topic-volumeverloop"></a>

### Volumeverloop

**Effecten → Amplitude → Volumeverloop** tekent een volumeverloop over het fragment.
De positie loopt van 0% aan het begin tot 100% aan het einde. Versterking loopt
van 0% voor stilte tot 200%; 100% is onveranderd. De gekozen kanalen volgen dezelfde lijn.

Klik en sleep punten, of wijzig positie en versterking onder de curve.
Binnenpunten kun je verwijderen. Presets bieden fades, een fade aan beide
kanten en een dip in het midden. Logaritmische interpolatie is alleen mogelijk
als alle versterkingswaarden positief zijn.

Voorbeeld: selecteer een passage met één te luid woord, plaats punten rond dat
woord en maak een dip. Voorbeeld helpt de overgang te beoordelen. Dit effect
wordt in de opname geschreven; de cliplijnen in multitrack blijven afzonderlijk
bewerkbaar.

<a id="ss-topic-normaliseren"></a>

### Normaliseren

**Effecten → Amplitude → Normaliseren** brengt de hoogste piek naar het gekozen
percentage. Het standaarddoel is 98%. Dit verhoogt of verlaagt het hele fragment
met dezelfde factor; het maakt zachte en harde woorden niet onderling even luid.

**Links en rechts gelijk normaliseren** bewaart de stereobalans. Zonder deze koppeling
krijgt elk kanaal zijn eigen piekniveau. **DC-offset verwijderen vóór normaliseren**
haalt eerst een vaste verschuiving rond de middenlijn weg. Stilte blijft stilte.

Gebruik normaliseren bijvoorbeeld na het mengen of versterken om pieken weer
binnen een passend bereik te krijgen voordat je als PCM exporteert.

<a id="ss-topic-ompolen-achterstevoren-en-stilte"></a>

### Ompolen, Achterstevoren en Stilte

Deze opdrachten staan direct onder **Effecten** en werken meteen:

- **Ompolen** keert de polariteit om. Het speelt de audio niet achteruit af.
- **Achterstevoren** keert de tijdvolgorde van het fragment om.
- **Stilte** maakt het fragment stil en houdt de lengte gelijk.

Gebruik Ctrl+Z om het resultaat terug te draaien. Gebruik Verwijderen wanneer je een
fragment helemaal uit de tijdlijn van een golfvorm wilt verwijderen.

<a id="ss-topic-5a-eq-en-filters"></a>

## 5a. EQ en filters

**Effecten → Filters** biedt drie manieren om de klank van een golfvorm aan te
passen. Een selectie beperkt de bewerking tot dat fragment. Zonder selectie
wordt de hele opname bewerkt. **Voorbeeld** laat de eerste acht seconden van die
keuze horen. **OK** past toe, **Annuleren** sluit zonder wijziging en **Ctrl+Z**
maakt de bewerking ongedaan. **F2** herhaalt de laatste instellingen.

<a id="ss-topic-grafische-equalizer"></a>

### Grafische equalizer

Tien vaste octaafbanden lopen van 31,5 Hz tot 16 kHz. Sleep een schuif omhoog
om dat gebied te versterken of omlaag om het te verzwakken. Het veld onder de
schuif voert de versterking in dB precies in, van −24 tot +24 dB.

**Vlak** zet alles op nul. **Lage tonen versterken** versterkt het laag, **Stempresentie**
benadrukt spraak en **Lichte glimlachcurve** versterkt laag en hoog licht. **Herstellen**
herstelt Vlak en zet Uitgangsversterking op nul. De banden overlappen: de grafiek toont
de gezamenlijke werking, niet alleen de losse schuifstanden. Banden buiten het
bruikbare frequentiebereik van de opname staan uit en worden overgeslagen.

<a id="ss-topic-parametrische-equalizer"></a>

### Parametrische equalizer

Vijf bell-banden werken rond een instelbare middenfrequentie. Een **Laagplateau**
past het laag onder zijn overgangsgebied aan; **Hoogplateau** doet dat voor het
hoog. Het vinkje schakelt iedere band afzonderlijk in of uit.

- **Frequentie:** middenfrequentie van een bell of het midden van een shelf-overgang.
- **Versterking:** versterken of verzwakken, van −24 tot +24 dB.
- **Q:** breedte van een bell; een hogere Q behandelt een smaller gebied.
  Shelves hebben een vaste, gelijkmatig verlopende overgang; hun Q-veld staat uit.

Begin voor een scherpe resonantie met een smalle bell en negatieve Versterking. Gebruik
voor een algemene klankaanpassing een bredere bell of shelf en kleine stappen.
**Spraakhelderheid** en **Warmte** bieden begininstellingen. **Vlak** of **Herstellen**
zet alle versterkingen op nul. Bij een lage samplerate staan de hogere banden
aanvankelijk uit; ze kunnen binnen het beschikbare bereik worden ingesteld.

<a id="ss-topic-filters"></a>

### Filters

- **Hoogdoorlaat:** laat hoog door en verzwakt laag. Laag gerommel verwijderen begint op 80 Hz.
- **Laagdoorlaat:** laat laag door en verzwakt hoog. Hoge tonen verzachten begint op 8 kHz.
- **Banddoorlaat:** laat het gebied rond de middenfrequentie door; een hogere Q maakt
  dat gebied smaller. Telefoonband is een brede startinstelling, geen vaste
  combinatie van twee afsnijfrequenties.
- **Sperfilter:** verzwakt een smal gebied rond de gekozen frequentie. De presets
  50 Hz notch en 60 Hz notch behandelen brom op die grondtoon. Eventuele
  boventonen vragen een aanvullende bewerking.

Laagdoorlaat en Hoogdoorlaat hebben een Butterworth-helling van **12, 24, 36 of
48 dB/oct**. Bij de afsnijfrequentie bedraagt de verzwakking ongeveer 3 dB.
Een steilere helling snijdt sterker af en kan meer uitslingering geven.
Banddoorlaat en Sperfilter gebruiken **Q** in plaats van de hellingkeuze.
**Herstellen** herstelt Laag gerommel verwijderen en Uitgangsversterking van nul.

<a id="ss-topic-niveau-grafiek-en-selecties"></a>

### Niveau, grafiek en selecties

**Uitgangsversterking** past het totale resultaat aan. Sterke EQ-versterking kan boven
0 dBFS uitkomen; verlaag Uitgangsversterking vóór luisteren of PCM-export. De verwerking
knipt pieken niet automatisch af. De grafiek toont de gezamenlijke frequentie-
respons inclusief Uitgangsversterking, binnen een weergave van −36 tot +36 dB.

Dezelfde instellingen gelden voor de gekozen kanalen, zonder ze te mengen.
**Selectieovergang** mengt binnen de randen van een gedeeltelijke selectie tussen
origineel en gefilterd geluid, standaard 5 ms, instelbaar van 0–100 ms. De eerste en
laatste sample bij een grens met ongewijzigde audio blijven exact gelijk aan de
bron. Audio buiten de selectie verandert niet. Bij een heel kort fragment kan
de overgang het hele fragment innemen; kies 0 ms voor directe bewerking.

Bij een overgang wordt het filter eerst voorbereid met voorafgaande audio,
afhankelijk van het verval van het filter en tot maximaal 60 seconden. Dit gebeurt
in blokken zonder die audio te wijzigen. Filtergeheugen loopt daarna door tussen
blokken. Bij 0 ms begint een gedeeltelijke selectie zoals voorheen met leeg
geheugen; de hele opname gebruikt eveneens de gewone doorlopende verwerking.
De lengte en cueposities blijven gelijk; eerdere Undo herstelt de bron.

Het natuurlijke causale faseverloop blijft behouden. Dit is geen lineairefase-
of fasevrije EQ: frequenties kunnen verschillend in tijd reageren. De grafiek
toont de stationaire amplituderespons; de korte mengovergang aan de selectierand
staat daar los van. Bij extreme smalle lage filters kan voorbereiding begrensd
zijn; kies een ruimer fragment of pas de hele opname toe. In realtime
spooreffecten loopt de bestaande filtertoestand door; daar is deze selectie-
instelling niet nodig. Bijzondere recordermeetgegevens worden niet herberekend.

Bij een lange bewerking toont de voortgang een annuleerknop. Annuleren behoudt
de oorspronkelijke golfvorm en Ongedaan maken-geschiedenis. Voor een multitrackclip open
je eerst een bewerkkopie, pas je het effect toe en kies je Golfvorm op clip toepassen.
Dezelfde EQ- en filterinstellingen zijn ook beschikbaar via **Spooreffecten**;
zie hoofdstuk 8a.

<a id="ss-topic-5b-vertraging-echo-en-galm"></a>

## 5b. Vertraging, echo en galm

De drie effecten staan onder **Effecten → Vertragingseffecten**. Selecteer een
fragment of laat de selectie leeg om de hele golfvorm te bewerken. **Voorbeeld**
speelt maximaal de eerste acht seconden van het resultaat, inclusief een
eventuele uitklank. Een instelling wijzigen stopt het voorbeeld. **OK** past
toe als één Ongedaan maken-stap; **Annuleren** laat de opname intact. **Ctrl+Z** draait terug,
**Ctrl+Shift+Z** doet opnieuw en **F2** herhaalt de laatste instellingen.

<a id="ss-topic-vertraging-een-vertraagde-kopie"></a>

### Vertraging — één vertraagde kopie

**Vertraging (links / mono)** bepaalt de vertraging van 1 tot 2.000 ms. Bij stereo
houdt **Gelijke vertraging voor beide kanalen** de twee tijden gelijk. Schakel het uit
om **Vertraging rechts** afzonderlijk te kiezen. Mono gebruikt alleen de eerste tijd.

- **Enkele vertraging:** een enkele kopie na 250 ms.
- **Korte terugkaatsing:** een korte herhaling van 80 ms, bijvoorbeeld voor zang of gitaar.
- **Verdubbeling:** 25 ms voor een verdubbelend effect.
- **Stereoverbreding:** verschillende tijden links en rechts; beschikbaar bij stereo.

Vertraging bevat één herhaling. Kies Echo voor een reeks afnemende herhalingen.

<a id="ss-topic-echo-herhalingen-met-feedback"></a>

### Echo — herhalingen met feedback

De tijdvelden werken hetzelfde als bij Vertraging. **Terugkoppeling** voert een deel van
de vertraagde kopie terug voor de volgende herhaling. Nul geeft één herhaling;
een hoger percentage geeft een langer verval, tot maximaal 95%.

**Demping van hoge tonen** maakt volgende herhalingen doffer. De eerste
vertraagde kopie blijft ongewijzigd; demping zit in de terugkoppeling.
**Herhalingen afwisselen tussen links en rechts** laat herhalingen bij stereo
tussen de kanalen wisselen. Het oorspronkelijke geluid behoudt zijn kanalen.
Met verschillende vertragingstijden duurt iedere kant zijn eigen tijd.

**Herhalende echo**, **Warme echo**, **Stereo-pingpong** en **Lange herhalingen**
geven begininstellingen. De pingpongpreset is alleen beschikbaar bij stereo.
**Herstellen** herstelt Herhalende echo. Bij veel feedback kunnen herhalingen zich
opstapelen; zet Effect of Uitgangsversterking lager wanneer het niveau te hoog wordt.

<a id="ss-topic-galm-galm"></a>

### Galm — galm

- **Ruimtegrootte:** de afstand tussen reflecties. Een grotere waarde geeft meer
  spreiding in de tijd en een ruimer karakter; de nagalmtijd blijft apart instelbaar.
- **Nagalmtijd (ongeveer RT60):** de richttijd waarin de galm ongeveer 60 dB afneemt,
  van 0,1 tot 60 seconden. Het precieze verval hangt ook van demping, frequentie
  en de opname af.
- **Voorvertraging:** tijd vóór de galm, van 0 tot 250 ms. Het oorspronkelijke geluid
  wordt hierdoor niet vertraagd; extra voorvertraging houdt de aanslag duidelijk.
- **Demping van hoge tonen:** hogere waarden laten het hoog eerder uitdoven.
- **Stereobreedte:** nul geeft dezelfde galm links en rechts; 100% gebruikt de
  volledige stereospreiding. Het oorspronkelijke stereobeeld blijft behouden.
  Het veld is bij mono uitgeschakeld.

**Kleine ruimte**, **Studio**, **Grote zaal** en **Lange sfeerklank** zijn beginpunten.
**Herstellen** herstelt Kleine ruimte. Voor verstaanbare spraak begin je met weinig Effect,
een korte Decay en wat Voorvertraging. Voor een ruimer muzikaal effect kun je Decay
en Effect verhogen. Het is een zelfstandige algoritmische galm, geen exacte
nabootsing van een bepaalde zaal of een ander programma.

<a id="ss-topic-droog-effect-en-uitgangsniveau"></a>

### Droog, Effect en uitgangsniveau

**Droog (origineel)** bepaalt het oorspronkelijke geluid. **Nat (effect)** bepaalt
de vertraagde kopieën of galm. Beide zijn afzonderlijke percentages en worden
bij elkaar opgeteld. Met Droog op nul hoor je alleen het effect; met Effect op nul
blijft alleen het oorspronkelijke geluid over.

**Uitgangsversterking** regelt de versterking van het totale resultaat, van −24 tot
+24 dB. De effecten begrenzen pieken niet automatisch. Verlaag dit niveau als
de meters rood worden of bij luisteren vervorming optreedt. Het interne signaal
kan boven 0 dBFS komen; verlaag het vóór PCM-export.

<a id="ss-topic-een-uitklank-behouden"></a>

### Een uitklank behouden

Standaard blijft de lengte gelijk. Vink **Extra uitklank na selectie** aan om de
resterende vertraging, echo of galm toe te voegen. **Automatische uitklankduur**
staat klaar om de duur zelf te bepalen. Schakel deze optie uit om een handmatige
tijd van 0,01–600 seconden te kiezen. Een galmtijd (ongeveer RT60) kan 0,1–60 s zijn.
Presets schakelen extra uitklank uit; kies de gewenste uitklank daarna.

Automatisch volgt het resterende effectgeheugen, ook wanneer een late echo pas
na een stil gat klinkt. De controle gebeurt in stappen van 100 ms. Als de
restpiek laag genoeg is, volgt een korte rustige afloop; de laatste 10 ms worden
naar stilte uitgefade. Het criterium is ongeveer 90 dB onder de referentiepiek,
met een absolute ondergrens van −140 dBFS. Voor extreem zachte uitklank die je
volledig wilt bewaren kun je de handmatige duur kiezen. Stilte of 0% Effect
voegt automatisch geen lege tijd toe. Bij 600 s nog hoorbare effecttoestand volgt
een melding; de oorspronkelijke audio en Undo blijven intact. Kies dan een
lagere terugkoppeling/galmtijd of een handmatige duur.

Alleen gekozen kanalen schuiven door een toegevoegde uitklank. Bij Beide schuiven
latere cuepunten mee; bij Links of Rechts blijven de gezamenlijke cuepunten
staan en wordt het andere kanaal zo nodig achteraan met stilte aangevuld.
De selectie omvat het volledige resultaat. Een luistervoorbeeld dat in de
uitklank valt kan eerst die uitklank moeten bepalen; het blijft hetzelfde
begin als bij volledig toepassen. Lange resultaten groeien in de werkruimte
zonder vooraf 600 s te reserveren en kunnen worden geannuleerd.

**Voorbeeld:** selecteer een korte stemopname, kies Echo → Warme echo en luister
met Voorbeeld. Vink Extra uitklank aan en laat de duur automatisch bepalen. Voor precies drie
seconden: schakel Automatische uitklankduur uit, kies 3 s en bevestig.
Een stemopname van twee seconden met drie seconden uitklank wordt vijf seconden.
Gebruik Ctrl+Z om naar de oorspronkelijke lengte terug te gaan.

Lange opnamen worden in blokken verwerkt met doorlopend effectgeheugen. Een
geannuleerde bewerking laat audio, selectie, metadata en Ongedaan maken/Redo intact.
Bij een multitrackclip open je eerst een bewerkkopie en plaats je het resultaat
terug met Golfvorm op clip toepassen. Controleer bij een verlengde clip de overlap
met volgende clips; die schuiven niet automatisch mee. Bestaande volume- en
panlijnen worden bij het terugplaatsen naar de nieuwe cliplengte geschaald.
Vertraging, Echo en Galm zijn ook beschikbaar via **Spooreffecten**; zie hoofdstuk 8a.

<a id="ss-topic-5c-ruisreductie-en-klikverwijdering"></a>

## 5c. Ruisreductie en klikverwijdering

Deze effecten staan onder **Effecten → Ruisreductie** en werken op een
selectie of, zonder selectie, de hele golfvorm. **Voorbeeld** laat maximaal acht
seconden horen. **OK** past toe, **Annuleren** sluit zonder wijziging en **Ctrl+Z**
draait terug. **F2** herhaalt de instellingen, inclusief het gebruikte ruisprofiel.

<a id="ss-topic-een-ruisprofiel-opnemen"></a>

### Een ruisprofiel opnemen

1. Zoek een stukje waarin alleen de ongewenste achtergrond hoorbaar is, zonder
   spraak of muziek. Een halve tot enkele seconden is meestal bruikbaar.
2. Selecteer dat stukje en kies **Ruisprofiel vastleggen**. Ook **Uit selectie vastleggen** in het effectvenster kan dit doen. Er verandert nog geen audio.
3. Selecteer vervolgens het fragment dat je wilt schoonmaken, of hef de selectie
   op voor de hele opname. Openen **Ruisreductie**.
4. Begin met **Zacht** of **Gebalanceerd**, luister met Voorbeeld en vergelijk met de
   oorspronkelijke opname door het venster te annuleren.

Een profiel beschrijft het gemiddelde frequentiebeeld van maximaal de eerste
30 seconden van de gekozen ruisselectie. De minimumduur hangt van de samplerate
af en wordt gemeld bij een te korte selectie. Het profiel blijft tijdens deze
appsessie beschikbaar. De samplerate moet overeenkomen. Het aantal kanalen
moet passen bij de gekozen kanalen. Bij Links of Rechts kan een stereoprofiel
het bijbehorende kanaal leveren; een monoprofilering kan op één kanaal werken.

**Profiel opslaan** bewaart het als `.ssnoise`; **Profiel laden** opent zo'n bestand.
Daarmee kun je een profiel later opnieuw gebruiken. Het bevat een ruisspectrum,
geen geluidsopname. Een profiel van een andere opstelling kan minder goed werken.

<a id="ss-topic-ruisreductie"></a>

### Ruisreductie

Beide standen beginnen met een passend profiel van een stukje waarin alleen
achtergrondruis hoorbaar is. Selecteer daarna het geluid dat je wilt schoonmaken.
Een leeg of stil profiel voegt geen ruisonderdrukking toe. Het opgeslagen profiel
blijft ongewijzigd tijdens het bewerken; de aanpassing geldt alleen voor deze bewerking.

- **Ruis bepalen → Vast ruisprofiel:** voor een gelijkmatige sis of ventilatie.
  Het opgenomen frequentiebeeld blijft tijdens het fragment gelijk.
- **Ruis bepalen → Adaptieve ruisdetectie:** voor achtergronden die in niveau of
  frequentiebeeld veranderen. De schatting volgt de opname vanaf het profiel.
- **Tijd voor ruisaanpassing:** 0,05–5 seconden, alleen beschikbaar bij adaptief.
  Korter reageert sneller op wisselingen; langer volgt voorzichtiger. Begin bij
  0,15 s. Bij lang aangehouden geluiden helpt een langere tijd of Vast ruisprofiel.
- **Maximale ruisreductie:** 0–36 dB. Begin met 6–12 dB; hogere waarden kunnen
  zachte details aantasten. Bij 0 dB blijft de opname exact gelijk.
- **Gevoeligheid:** meer gevoeligheid behandelt meer achtergrond als ruis.
- **Egalisatie:** maakt de overgang naar sterker onderdrukken rustiger. Een hoge
  waarde laat na een duidelijk geluid tijdelijk meer achtergrond door.
- **Detailbehoud:** 0–100%. Hoger ontziet meer zacht geluid, met meer resterende
  achtergrond. De beginwaarde is 50%. Vast ruisprofiel met 0% gebruikt de eerdere
  verzwakking; een hoge waarde herstelt geen details die al in de bron ontbreken.
- **Stereokanalen koppelen:** gebruikt dezelfde verzwakking links en rechts om
  de balans te behouden. Zonder koppeling wordt ieder kanaal apart behandeld.
- **Alleen verwijderde ruis behouden:** levert het verwijderde deel op in plaats
  van het schoongemaakte geluid. Luister of waardevolle spraak of muziek verdwijnt;
  schakel dit weer uit vóór OK om het schone resultaat te bewaren.

| Preset | Reductie | Detailbehoud | Stand / aanpassingstijd |
| --- | --- | --- | --- |
| Zacht | 6 dB | 65% | Vast |
| Gebalanceerd | 12 dB | 50% | Vast |
| Sterk | 24 dB | 15% | Vast |
| Wisselende achtergrond | 12 dB | 50% | Adaptief, 0,15 s |
| Fijne details | 6 dB | 90% | Vast |

**Voorbeeld:** leg een halve tot enkele seconden ventilatieruis vast. Selecteer
vervolgens een stemopname waarin de ventilatie harder wordt. Kies **Wisselende
achtergrond**, luister met Voorbeeld en beluister ook het verwijderde deel.
Verhoog Detailbehoud als zachte woorden of uitklanken verdwijnen. Verleng de
aanpassingstijd of kies Vast wanneer lang aangehouden klanken achteruitgaan.
Schakel Alleen verwijderde ruis behouden uit en bevestig met OK.

Automatische herkenning kan ruis en gewenst geluid verwarren, vooral bij lange
brede klanken, een profiel met spraak/muziek of zeer lage signaalniveaus. Dit
scheidt geen afzonderlijke stemmen uit een mix en herstelt geen ontbrekende
informatie. Begin met bescheiden instellingen en luister na. De lengte,
kanaalposities en cuepunten blijven gelijk. Voorbeeld is hetzelfde begin als
bij volledige verwerking. Ctrl+Z herstelt de opname; F2 herhaalt ook de gekozen
stand, aanpassingstijd, detailinstelling en het profiel. Op één kanaal blijft de
andere golf exact behouden. Lange bestanden worden met begrensd werkgeheugen
verwerkt; annuleren past geen gedeeltelijk resultaat toe.

<a id="ss-topic-klikverwijdering"></a>

### Klikverwijdering

Dit effect zoekt korte, geïsoleerde sprongen die snel naar de omgeving terugkeren
en vervangt ze door een verbinding tussen de omliggende onbeschadigde samples.

- **Threshold multiplier:** een hogere waarde maakt de herkenning terughoudender;
  een lagere waarde vindt meer mogelijke tikken.
- **Minimaal sprongniveau:** de minimale sprongsterkte in dBFS. Een lagere waarde
  maakt ook zachtere tikken kandidaat.
- **Maximale klikduur:** de langste tik die mag worden hersteld, 0,02–2 ms.

De presets **Terughoudend**, **Kleine klikjes** en **Langere klikken** zijn beginpunten.
Gebruik bij voorkeur een selectie rondom het probleem en luister met Voorbeeld.
Slagwerk en scherpe aanslagen kunnen op tikken lijken. Lange kraken, clipping
en beschadigde begin-/eindsamples worden hiermee niet betrouwbaar hersteld.
Behandel zulke plekken afzonderlijk en bewaar eerst een kopie.

Beide effecten werken met begrensde werkbuffers, ook bij lange opnamen. Annuleren
laat audio, selectie en Ongedaan maken/Redo intact. Voor een multitrackclip open je eerst
een bewerkkopie en kies je na de bewerking Golfvorm op clip toepassen. Realtime
ruisonderdrukking tijdens opnemen of afspelen is hiermee niet beschikbaar.

<a id="ss-topic-5d-tijd-en-toonhoogte"></a>

## 5d. Tijd en toonhoogte

**Effecten → Tijd/toonhoogte** bevat Tijdsduur aanpassen en Toonhoogte verschuiven. Ze bewerken de selectie
of, zonder selectie, de hele golfvorm. Voorbeeld analyseert eerst het volledige
bereik en speelt daarna maximaal acht seconden af. Het voorbeeld is hetzelfde
prefix als bij toepassen. Lange opnamen hebben daardoor ook voor Voorbeeld
analysetijd nodig. De voortgang is annuleerbaar; annuleren behoudt de opname.

<a id="ss-topic-tijdsduur-aanpassen"></a>

### Tijdsduur aanpassen

**Nieuw length** kiest de nieuwe lengte als percentage, van 25 tot 400%.
100% houdt de lengte gelijk, 200% maakt de opname tweemaal zo lang en 50%
halveert de speelduur. De toonhoogte blijft behouden. De getoonde tijden helpen
bij het instellen van een passend resultaat.

Met **Van … BPM to … BPM** en **Uit tempo instellen** bereken je de lengte op basis
van een bekend begintempo en gewenst eindtempo. Dit is geen automatische
tempodetectie. Van 120 naar 100 BPM wordt de lengte 120%. Een verhouding buiten
het beschikbare bereik wordt gemeld en verandert de instelling niet.

Bij Beide volgen cuepunten binnen het bewerkte bereik de nieuwe tijdschaal;
latere audio en cuepunten schuiven mee met het verschil in lengte. Bij Links
of Rechts verschuift alleen de gekozen audio en blijven gezamenlijke cuepunten staan. De samplerate
van het bestand verandert niet. De selectie omvat na toepassen het resultaat.

<a id="ss-topic-toonhoogte-verschuiven"></a>

### Toonhoogte verschuiven

**Pitch change** kiest −24 tot +24 halve tonen. +12 is een octaaf omhoog;
−12 is een octaaf omlaag. Een fractie geeft fijnstemming: 0,01 halve toon is
één cent. De speelduur en cueposities blijven behouden.

**Formanten behouden** helpt het karakter van zang of spraak te behouden bij een
toonhoogteverschuiving. Vergelijk beide standen bij instrumenten en grote
verschuivingen; het resultaat verschilt per opname.

<a id="ss-topic-kwaliteit-en-praktisch-gebruik"></a>

### Kwaliteit en praktisch gebruik

**Nauwkeurig** gebruikt de fijnere Rubber Band-engine en is de standaard. **Snel**
gebruikt een snellere verwerking, bruikbaar wanneer rekentijd belangrijker is.
Beide werken offline op de golfvorm. Stereo wordt gezamenlijk verwerkt om de
samenhang tussen kanalen te behouden. Extreme rek of toonhoogteverschuiving kan
nog steeds kunstmatig klinken, vooral bij scherpe aanslagen of complete mixes.

Gebruik minimaal 50 ms audio, met ten minste 64 samples bij lage samplerates.
Kortere selecties worden bij een echte wijziging geweigerd. De neutrale
instelling geeft de oorspronkelijke audio exact terug. De uitvoerduur wordt
afgerond op hele samples. Rubber Band verwerkt audio in kleine blokken;
grote resultaten staan op schijf. De volledige analyse vraagt daarnaast
geheugen voor informatie over het verloop van de opname.

**OK** bevestigt één Ongedaan maken-stap, **Annuleren** laat de golfvorm intact. Met Ctrl+Z
en Ctrl+Shift+Z kun je terug en opnieuw. **F2** herhaalt dezelfde verhouding of
toonhoogte op een nieuwe selectie. Bewaren als WAV, projectopslag en herstel
houden het bewerkte resultaat vast.

Voor een multitrackclip open je eerst een bewerkkopie en kies je daarna Toepassen
Golfvorm to Clip. De cliplengte en bestaande volume-/panlijnen volgen het
nieuwe resultaat; volgende clips schuiven niet automatisch mee. Controleer de
overlap. Dit zijn nog geen realtime tempo- of toonhoogte-effecten op sporen.

<a id="ss-topic-5e-vervorming-en-convolutie"></a>

## 5e. Vervorming en convolutie

**Effecten → Speciaal** bevat Vervorming en Convolutie. Beide bewerken een
selectie of, zonder selectie, de hele golfvorm. Voorbeeld laat de eerste acht
seconden horen. OK bevestigt één Ongedaan maken-stap; Annuleren laat de golfvorm intact.
Ctrl+Z draait terug, Ctrl+Shift+Z doet opnieuw en F2 herhaalt de instellingen.

<a id="ss-topic-vervorming"></a>

### Vervorming

Kies het gewenste karakter bij **Type**:

- **Zacht begrenzen:** rondt sterke uitslagen vloeiend af voor zachte verzadiging.
- **Hard begrenzen:** snijdt uitslagen op de gekozen grens af voor scherpere vervorming.
- **Golfvouwen:** vouwt uitslagen buiten de grens terug en geeft extra boventonen.
- **Bitdiepte verlagen:** rondt amplitudes af op de gekozen bitdiepte, van 2 tot 16 bits.

**Aansturing** versterkt het signaal vóór de vervorming, 0–36 dB. **Bovengrens** bepaalt
de amplitudegrens van het vervormde deel, 10–100%. **Effectmenging** mengt dit deel
met de oorspronkelijke opname; nul geeft alleen de oorspronkelijke audio.
**Uitgangsversterking** regelt het totale resultaat met −24 tot +24 dB. De Bovengrens
begrenst dus niet automatisch het droge deel of het uiteindelijke uitgangsniveau.

De presets **Zachte warmte**, **Krakende vervorming**, **Golfvouwen** en **Bitdiepte verlagen** zijn
beginpunten. Vergelijk met de oorspronkelijke opname en voorkom te hoge pieken.
De lengte en cueposities blijven gelijk. Stilte blijft stil.

**High quality** gebruikt oversampling om aliasing te verminderen. Bij gangbare
samplerates is dit viermaal; bij hogere rates wordt de factor aangepast. Dit
verwerkt ook voor Voorbeeld de hele selectie en kan langer duren. Zonder deze
optie is de verwerking sneller en kan een ruwere digitale klank ontstaan.
Bitdiepte verlagen gebruikt in zijn preset standaard geen oversampling.

<a id="ss-topic-convolutie"></a>

### Convolutie

Een impulsrespons beschrijft een filter, luidspreker, kabinet of akoestische
reactie. Convolutie past zo'n reactie op de opname toe. Er zijn geen externe
plug-ins nodig; de respons zelf kies je als WAV-bestand.

1. Openen Convolutie en klik **Impulsrespons kiezen**.
2. Kies een geschikte WAV-respons. De naam, duur en kanalen verschijnen in het venster.
3. Stel **Droog** en **Effect** in en luister met Voorbeeld.
4. Kies eventueel **Volledige uitklank behouden** en bevestig met OK.

**Droog** regelt de oorspronkelijke opname; **Effect** regelt het geconvolveerde deel.
Beide worden opgeteld. Voor een zuiver filtereffect kun je Droog op nul en Effect op
100% zetten. **Uitgangsversterking** regelt het totale niveau. Een respons kan frequenties
sterk versterken; verlaag het niveau als de uitvoermeters rood worden.

**Impulsenergie normaliseren** schaalt de respons op zijn energie, met dezelfde
factor voor beide responskanalen. Schakel dit uit als de oorspronkelijke schaal
van een meetrespons behouden moet blijven. Het garandeert geen piekbegrenzing.

Een monorespons werkt op mono of op beide kanalen van stereo. Een stereorespons
werkt per kanaal op een stereogolfvorm; hij maakt van een monogolfvorm geen stereo
en bevat geen complete matrixroutering tussen kanalen. Een afwijkende samplerate
van de respons wordt automatisch omgezet. Bij Links of Rechts wordt het
bijbehorende kanaal van een stereorespons gebruikt. Een uitklank toevoegen
verschuift alleen de gekozen kanalen; het andere kanaal blijft op zijn plaats.

Zonder **Volledige uitklank behouden** blijft de oorspronkelijke lengte gelijk.
Met de optie wordt de volledige uitklank van de respons toegevoegd, precies de
responslengte min één sample. De gekozen audio ná de selectie schuift daardoor
vooruit. Bij Beide volgen latere cuepunten; bij Links of Rechts blijven ze staan.
Cuepunten binnen de oorspronkelijke selectie blijven staan. De uitklank
krijgt geen extra automatische fade, zodat ook exacte filterresponsen behouden
blijven. Controleer het einde wanneer de respons zelf abrupt stopt.

De respons mag na omzetting maximaal 10 seconden én 524.288 samples lang zijn;
het WAV-bestand mag maximaal 32 MiB zijn. Bij hoge samplerates kan de samplegrens
de beschikbare duur beperken. Kies een kortere respons of werk op een lagere
samplerate. Een lege of volledig stille respons wordt geweigerd.

Bewaar het gekozen responsbestand ongewijzigd om **F2** later te kunnen gebruiken.
Herhalen controleert of het bestand nog aanwezig is en dezelfde inhoud heeft.
Bij een gewijzigd of verdwenen bestand blijft de golfvorm intact; kies de respons
opnieuw in het venster. Het al bewerkte geluid blijft wel met WAV, project en
herstelkopie bewaard, ook zonder het responsbestand.

Grote audio wordt in blokken verwerkt en de werkstaat van convolutie is begrensd.
Annuleren laat audio, selectie en Ongedaan maken/Redo intact. Voor multitrack gebruik je een
bewerkclipkopie en Golfvorm op clip toepassen. Volgende clips verschuiven niet vanzelf
bij een langere clip; volume-/panlijnen volgen bij terugplaatsen de cliplengte.
Via **Spooreffecten** zijn andere realtime spooreffecten en VST3 beschikbaar;
Vervorming en Convolutie blijven golfvormbewerkingen.

<a id="ss-topic-6-tonen-en-stilte-maken"></a>

## 6. Tonen en stilte maken

**Genereren → Tonen** maakt een sinustoon. Stel **Duur** in seconden,
**Frequentie** in Hz en **Amplitude** in procenten in. Zonder selectie wordt de
toon bij de cursor ingevoegd; met een selectie vervangt hij dat fragment. De
opgegeven duur bepaalt de lengte van het nieuwe geluid.

Een toon van bijvoorbeeld 440 Hz op een bescheiden niveau is bruikbaar om een
bewerking te proberen. Begin bij luisteren met een laag afspeelvolume.

**Genereren → Stilte** voegt een opgegeven duur aan stilte in of vervangt de
selectie door die hoeveelheid stilte. Dit verschilt van Effecten → Stilte,
dat de bestaande fragmentlengte altijd behoudt.

<a id="ss-topic-7-frequenties-analyseren"></a>

## 7. Frequenties analyseren

Selecteer een fragment en kies **Analyseren → Frequentieanalyse** of **Alt+Z**.
Zonder selectie wordt de opname als uitgangspunt genomen. De grafiek toont
frequenties van laag naar hoog en het bijbehorende niveau. Onderaan staat de
sterkste gevonden frequentie met het niveau in dBFS.

De analyse gebruikt bij lange fragmenten een begrensd deel rond het midden van
het gekozen bereik. Ze is een hulpmiddel voor tonen en spectrale verhoudingen,
geen doorlopende spectrummeter. Selecteer een korter fragment om een bepaalde
klank of toon te onderzoeken. Sluiten verandert de audio niet.

<a id="ss-topic-8-meerdere-sporen-combineren"></a>

## 8. Meerdere sporen combineren

<a id="ss-topic-een-sessie-opbouwen"></a>

### Een sessie opbouwen

1. Kies **Bestand → Nieuwe multitracksessie** en stel rate en aantal sporen in.
2. Gebruik **Audio importeren** of **Bestand → Audio in multitrack importeren**. Je kunt ook
   WAV- of MP3-bestanden vanuit de bestandsbeheerder op de tijdlijn slepen.
3. Sleep clips in **Clips verplaatsen** naar de gewenste tijd en het gewenste spoor.
4. Stel volume, pan, Dempen en Solo per spoor in.
5. Sla het project tussentijds op en luister naar de combinatie.
6. Kies **Eindmix maken** voor een eindmix.

Verschillende samplerates worden bij import naar de sessierate omgezet.
Met **Venster → Huidige golfvorm in multitrack invoegen** voeg je de open golfvorm
toe. Meerdere tegelijk geïmporteerde bestanden worden op opeenvolgende sporen
geplaatst. **+ Spoor** en **− Spoor** voegen een spoor toe of verwijderen het
geselecteerde spoor. Een verwijderd spoor met clips kun je met Ongedaan maken herstellen.

<a id="ss-topic-clips-en-sporen-aanpassen"></a>

### Clips en sporen aanpassen

Klik een clip om haar te kiezen. Sleep het midden om te verplaatsen en de
linker- of rechterrand om te trimmen. Trimmen bewaart de bron: opnieuw verlengen
kan eerder verborgen audio terughalen. In lege ruimte kun je een tijdbereik
selecteren voor afspelen.

**Clip dupliceren** of **Ctrl+D** maakt een kopie die dezelfde bron gebruikt.
**Clip verwijderen** of Verwijderen verwijdert de geselecteerde clip wanneer **Clips verplaatsen**
actief is. De bronopname op schijf blijft behouden. Rechtsklikken op een clip
opent dezelfde opdrachten.

**Clipeigenschappen** opent de eigenschappen. Daar stel je naam, tijdlijnpositie,
bronbegin en -einde, volume, pan, fades en clip-Dempen precies in. Tijdwaarden zijn
in seconden. Fades moeten samen binnen de cliplengte passen. Annuleren laat de
clip ongewijzigd.

De spoornaam is bewerkbaar. **Dempen** zet een spoor stil; **Solo** laat alleen
gekozen solosporen horen. Dempen blijft doorslaggevend. Pan −100 is links, 0 is
midden en +100 is rechts. Bij een stereobron verzwakt pan één kant; het kopieert
het andere kanaal niet naar die kant.

<a id="ss-topic-volumelijn-en-panlijn"></a>

### Volumelijn en Panlijn

Kies boven de tijdlijn **Volumelijn** of **Panlijn** en klik in een clip om
punten te plaatsen. Sleep de punten om tijd en waarde te wijzigen. De
volumelijn loopt van stilte onderaan via 100% in het midden tot 200% bovenaan.
Bij de panlijn is boven rechts, midden neutraal en onder links.

Rechtsklikken of dubbelklikken op een punt opent precieze invoer. Hier zijn de
puntposities in frames. **Punt verwijderen** of Verwijderen verwijdert alleen het
geselecteerde lijnpunt. **Lijn herstellen** maakt de lijn weer neutraal. Esc annuleert
een lopende sleepbeweging. **Clips verplaatsen** keert terug naar verplaatsen en trimmen.

De volumelijn werkt boven op spoorvolume, clipvolume en fades. De panlijn werkt
boven op spoor- en clippan; zet die gewone paninstellingen in het midden voor
een volledige beweging van links naar rechts. Punten bewegen met de bronaudio
mee bij verplaatsen en blijven bij trimmen bewaard. De lijnen worden met het
project opgeslagen en werken door in afspelen en mixdown.

<a id="ss-topic-een-effect-op-een-clip-toepassen"></a>

### Een effect op een clip toepassen

Dubbelklik een clip of kies **Kopie in golfvorm bewerken** via de rechtermuisknop.
De kopie opent in de golfvormeditor. Pas daar het effect toe. Kies daarna
**Venster → Golfvorm op clip toepassen** om het resultaat terug te plaatsen.

Gewoon terugschakelen naar multitrack past de kopie niet toe. Sluiten en
verwerpen laat de oorspronkelijke clip intact. Na toepassen kunnen de oude
audio en de lijnen met Ongedaan maken in de sessie worden hersteld. Een veranderde
samplerate wordt bij terugplaatsen naar de sessierate omgezet.

<a id="ss-topic-opslaan-en-mixdown"></a>

### Opslaan en mixdown

**Sessie opslaan** bewaart het bewerkbare project. **Sessie mixen** of
**Eindmix maken** maakt één WAV van de hele sessie. Een tijdbereikselectie bepaalt
hierbij niet de exportlengte. Controleer Dempen, Solo en de niveaus voordat je
exporteert: die instellingen werken door in het eindresultaat.

Volume, pan, mute, solo en spoorketens kunnen tijdens het luisteren veranderen.
Dezelfde spoorketen wordt bij mixdown gebruikt. Ongedaan maken/Redo en wisselen van weergave
stoppen het afspelen. De bronopnamen blijven behouden.

<a id="ss-topic-8a-spooreffecten-plug-ins-en-opname-met-begeleiding"></a>

## 8a. Spooreffecten, plug-ins en opname met begeleiding

<a id="ss-topic-spooreffecten"></a>

### Spooreffecten

Klik op **FX** naast een spoor of kies **Effecten → Spooreffecten**. Kies een effect en druk op **Toevoegen**. **OK** bevestigt; **Toepassen** verandert de instelling terwijl het venster openblijft. Dubbelklik of **Bewerken** opent de instellingen opnieuw. **Omhoog/Omlaag** verandert de volgorde; het vinkje schakelt een effect tijdelijk uit. **Verwijderen** haalt het uit de keten. Wijzigingen hebben Undo/Redo.

Een keten bevat maximaal zestien effecten: vaste versterking, kanaalmixer, dynamiek, grafische/parametrische EQ, filters, vertraging, echo, galm, ompolen en externe plug-ins. Clipvolume, lijnen en fades werken vóór de keten; spoorvolume en spoorpan erna. Mono wordt eerst stereo. Met **Uitklank na laatste clip** voeg je maximaal zestig seconden toe. Afspelen en eindmix gebruiken dezelfde keten. De bronnen blijven behouden.

**Toepassen** werkt tijdens luisteren; al naar het apparaat gestuurde audio behoudt de vorige instelling. Starten, zoeken en bypasswissels beginnen met nieuw effectgeheugen. Voor normaliseren, restauratie, tijd/toonhoogte, vervorming en convolutie gebruik je **Kopie in golfvorm bewerken**. Een volumeverloop teken je met **Volumelijn** op de clip.

<a id="ss-topic-vst3-lv2-en-ladspa-toevoegen"></a>

### VST3, LV2 en LADSPA toevoegen

1. Installeer een native **64-bit Linux-audio-effect**.
2. Kies **Externe plug-in** in Spooreffecten en klik **Toevoegen**.
3. Kies het formaat en **Plug-in toevoegen**: een `.vst3`-bundel, `.lv2`-bundel of LADSPA-bibliotheek (`.so`). Effecten uit dezelfde bundel verschijnen afzonderlijk.
4. Kies het effect. Zoek een parameter op naam en wijzig de genormaliseerde positie van 0–100%. Vijftig procent betekent niet automatisch half volume. Discrete parameters hebben stappen; alleen-lezen parameters blijven vast.
5. **Toepassen** laat de instelling op het spoor horen; **OK** bevestigt en sluit.

Met **Plug-invenster openen** gebruik je het eigen venster van een ondersteunde VST3- of LV2-plug-in. Parameters en bewaarbare status uit dat venster worden meegenomen bij bevestigen. De eigen vensters vereisen **X11 of XWayland**. Bij een ontbrekend of niet-ondersteund venster blijven de algemene parameterregelaars beschikbaar. LADSPA gebruikt deze regelaars altijd. LV2-vensters die een GTK-/Qt-adapter vereisen, worden niet ingebed.

VST3 ondersteunt één stereo-invoerbus en één stereo-uitvoerbus met float32-verwerking. LV2 en LADSPA ondersteunen mono- en stereo-effecten met evenveel in- en uitgangen; een mono-effect krijgt per stereokanaal een eigen instantie. MIDI-instrumenten, extra sidechains, VST2 en Windows-plug-ins worden niet ondersteund. Verplichte LV2-functies of poorttypen die niet beschikbaar zijn, worden gemeld; MIDI/Atom-verwerking ontbreekt. LV2-status die externe bestanden vereist, kan niet volledig worden opgeslagen en geeft een melding. Kies daarvoor een effect met zelfstandig bewaarbare status.

Plug-ins draaien in een apart hulpproces. Een crash, vastloper of ongeldige audio stopt het afspelen met een melding; de vastgelegde opname blijft bewaard. Projecten bewaren parameters en maximaal 1 MiB status per effect. De plug-in en eigen bibliotheken, samples of responsbestanden blijven apart geïnstalleerd. Voeg op een andere computer dezelfde versie toe. Ontbrekende of gewijzigde plug-ins worden gemeld; afspelen/export vraagt om het passende effect of bewust uitschakelen.

<a id="ss-topic-automatische-plug-invertraging"></a>

### Automatische plug-invertraging

Gerapporteerde **verwerkingsvertraging** van plug-ins wordt automatisch per spoor gecompenseerd, tijdens afspelen en eindmix. Vertragingen in een keten worden opgeteld; bypass en gewijzigde instellingen worden opnieuw verwerkt. De tijdlijn en mixduur blijven gelijk. Een muzikale echo, voorvertraging of galm blijft hoorbaar: deze hoort bij het effect. Compensatie vereist een juiste melding door de plug-in en is begrensd tot tien seconden per spoor. Een ongeldige of voortdurend veranderende vertraging geeft een melding.

<a id="ss-topic-opnemen-met-begeleiding-en-synchronisatie"></a>

### Opnemen met begeleiding en synchronisatie

Zet begeleiding op sporen, kies het doelspoor en plaats de cursor. Druk **R**, kies ingang en nieuwe clip als bestemming en vink **Bestaande sporen afspelen tijdens opnemen** aan. De bestaande sporen spelen met effecten; de ingang wordt niet via de luidsprekers teruggespeeld. **P** pauzeert/hervat beide; **Stoppen/Esc/Spatie/R** houdt de take als één Undo-stap. **Opname verwerpen** verwijdert alleen de nieuwe take. Bij apparaat- of plug-inverlies blijft vastgelegde audio behouden.

**Automatische synchronisatie** koppelt de opnamepositie aan de afspeelklok en meet het verschil tussen de in- en uitvoerklokken. Bij voldoende lange, betrouwbare metingen wordt de opnamelengte na Stop voorzichtig gecorrigeerd. Een korte of onstabiele meting rekt de take niet op. Duurcorrectie vraagt ruim tien seconden bruikbare klokmetingen. Dit vervangt geen meting van de fysieke in-/uitvoerroute.

Voor die route kies je **Opties → Opname kalibreren**, of de kalibratieknop in het opnamevenster:

1. Kies dezelfde apparaten, samplerate, mono/stereo, eerste ingangskanaal en buffer als voor de opname.
2. Verbind uitgang en ingang met een geschikte loopbackkabel. Een microfoon bij een luidspreker kan ook; dan telt de akoestische looptijd mee. Begin met een laag niveau.
3. Klik **Kalibratie starten**. Ongeveer zes seconden zachte testpulsen meten de verbinding. De ingang wordt niet teruggespeeld.
4. Alleen een betrouwbaar resultaat wordt opgeslagen. Bij stilte, oversturing, onduidelijke signalen of instabiele timing volgt een melding; een eerdere goede kalibratie blijft bestaan.
5. Controleer de plaatsing met een korte proeftake. Gebruik na wijziging van apparaat, samplerate, ingang of buffer een passende nieuwe kalibratie.

Het profiel hoort bij de gekozen apparaatcombinatie en instellingen. Automatische synchronisatie past de opgeslagen routecorrectie toe. Zonder profiel blijft kloksynchronisatie beschikbaar, maar kan fysieke vertraging overblijven. Als alternatief schakel je automatisch uit en gebruik je **Opnamepositie verschuiven**: negatief is eerder, positief later. Een take die 15 ms te laat staat vraagt bijvoorbeeld −15 ms. Handmatige en automatische correctie worden niet bij elkaar opgeteld.

<a id="ss-topic-punch-in-out-alleen-een-passage-opnieuw-opnemen"></a>

### Punch-in/out: alleen een passage opnieuw opnemen

1. Open Multitrack, kies het doelspoor en selecteer het gewenste tijdvak op de tijdlijn of met **Bewerken → Selectie instellen**.
2. Kies **Opties → Punch-in/out** of **Shift+R**. In het opnamevenster staat **Punch-in/out in selectie**.
3. Stel ingang, synchronisatie, **Voorloop** (standaard 2 s) en **Overgang** (standaard 5 ms) in. De selectie bepaalt de opnamegrenzen; begeleiding is ingeschakeld.
4. Start. De ingang warmt eerst op; daarna speelt de oorspronkelijke passage tijdens de voorloop. Binnen het gekozen interval wordt alleen het doelspoor gedempt, terwijl de nieuwe take wordt opgenomen. Andere sporen blijven spelen.
5. Na het interval stopt de opname automatisch, met een korte afronding voor synchronisatie. Alleen de gecorrigeerde audio binnen de selectie komt als nieuwe clip op het spoor.

Een korte overgang mengt oud en nieuw binnen de selectiegrenzen, maximaal 100 ms. Audio buiten het interval blijft behouden. De oorspronkelijke clips blijven eveneens bewaard: een punch dekt hun betreffende gedeelte af. **Ctrl+Z** herstelt de vorige situatie in één stap. Selecteer de oude clip en kies **Afgedekte audio herstellen** om zijn afdekking op te heffen; verwijder of demp de nieuwe take als die anders tegelijk hoorbaar wordt. Deze opdracht herstelt alle afgedekte gebieden van de gekozen clip.

Vroeg stoppen bewaart alleen het werkelijk opgenomen deel binnen het interval. Stoppen vóór het interval verandert de sessie niet; de ruwe take blijft beschikbaar via **Bestand → Werk herstellen**. Herstel van een nog niet bevestigde opname biedt de ruwe take aan, inclusief eventuele voor-/naloop, zodat je die zelf kunt plaatsen. Een voltooide punch wordt met zijn afdekking in project en crashherstel bewaard.

<a id="ss-topic-sessies-bewaren-en-heropenen"></a>

### Sessies bewaren en heropenen

**Sessie opslaan / Sessie opslaan als** bewaart gebruikte audio, clips, lijnen, spoorketens, plug-ininstellingen en punchgebieden. **Sessie openen** herstelt deze bewerkbare sessie. **Eindmix maken** maakt een WAV of MP3 met dezelfde effecten. Bewaar het project om afzonderlijke sporen te kunnen blijven veranderen. Nieuwe projecten vereisen SoundSausage **0.26.0 of nieuwer**; eerdere projectversies blijven leesbaar. Een ontbrekende plug-in verhindert het openen en herstellen van de bronnen niet.

<a id="ss-topic-9-een-andere-samplerate-kiezen"></a>

## 9. Een andere samplerate kiezen

**Bewerken → Samplerate omzetten** zet de hele golfvorm om. Kies het gewenste aantal
Hz en bevestig. Toonhoogte en speelduur blijven behouden, met afronding op hele
uitvoerframes. Zeer korte fragmenten houden minimaal één frame. Selectie en
cursor volgen dezelfde tijden. **Ctrl+Z** herstelt zowel de vorige audio als de
vorige rate.

Deze opdracht verandert de opname. Automatische omzetting voor een uitvoerapparaat
verandert alleen het afgespeelde signaal en laat de golfvorm zelf intact.

<a id="ss-topic-10-favorieten-vensters-en-hulp"></a>

## 10. Favorieten, vensters en hulp

**Favorieten** geeft snel toegang tot herhalen, normaliseren en fades. Eigen
favorietenlijsten kunnen nog niet worden samengesteld. **Venster** wisselt
tussen beide weergaven en bevat de opdrachten om een golfvorm in te voegen of
naar een clip terug te plaatsen.

**Help → Over** toont de versie, maker, licentie en website. De handleiding
blijft als afzonderlijk venster beschikbaar, zodat je de stappen in de editor
kunt volgen.

<a id="ss-topic-11-sneltoetsen"></a>

## 11. Sneltoetsen

| Toets | Functie |
| --- | --- |
| Ctrl+N / Ctrl+O | Nieuwe golfvorm of sessie / openen in de huidige weergave |
| Ctrl+S / Ctrl+Shift+S | Opslaan / opslaan als in de huidige weergave |
| Ctrl+Alt+N / Ctrl+Alt+O / Ctrl+Alt+S | Nieuwe sessie / sessie openen / sessie opslaan |
| Ctrl+W / Ctrl+Q | Huidige golfvorm of sessie sluiten / toepassing sluiten |
| Ctrl+Z / Ctrl+Shift+Z | Ongedaan maken / Opnieuw uitvoeren |
| Ctrl+X / Ctrl+C / Ctrl+V | Knippen / kopiëren / plakken in de golfvorm |
| Ctrl+M / Ctrl+T | Gemengd plakken / selectie behouden |
| Verwijderen | Selectie, clip of lijnpunt verwijderen, afhankelijk van de actieve bewerking |
| Ctrl+A / F4 | Hele duur in gekozen kanalen / selectie naar nuldoorgangen aanpassen |
| Alt+B / Alt+L / Alt+R | Beide kanalen / links / rechts kiezen |
| Spatie / P / Esc | Afspelen of stoppen / pauzeren of hervatten / stoppen |
| R | Opname instellen; tijdens opnemen stoppen en de take behouden |
| Home / Einde | Naar begin / einde |
| + / − | Inzoomen / uitzoomen |
| Ctrl+0 / Ctrl+Shift+A | Hele opname tonen / selectie vullen |
| Ctrl+D | Clip dupliceren in multitrack |
| Tab / F11 | Golfvorm en multitrack wisselen / volledig scherm |
| F1 / F2 / Alt+Z | Handleiding / laatste effect herhalen / frequentieanalyse |

Bij tekstinvoer horen gewone typetoetsen bij het actieve veld. Klik weer in de
golfvorm of tijdlijn wanneer je daar een sneltoets wilt gebruiken.

<a id="ss-topic-12-problemen-en-work-in-progress"></a>

## 12. Problemen en work in progress

- **Geen ingangsniveau:** controleer Ingang, het gekozen kanaal en het microfoonvolume
  in de geluidsinstellingen. Start een nieuwe take na het aansluiten van een apparaat.
- **Geen geluid:** controleer Audioapparaten, systeemvolume, Dempen en Solo.
  Kies bij een verdwenen apparaat een beschikbare uitgang en start opnieuw.
- **Vervorming of rode pieken:** verlaag volume of versterking; opgetelde clips
  en Gemengd plakken kunnen samen boven het uitvoerniveau komen.
- **Plakken lukt niet:** bij Beide moet het kanaalaantal passen. Kies Links of Rechts
  om mono-audio in één stereokanaal te plakken.
- **Een effect is grijs:** open een golfvorm of een bewerkkopie; Kanalenmixer
  vereist stereo. Tijdsbewerkingen volgen de gekozen kanalen; kies Beide om stereo samen te verschuiven.
  De overige effecten vereisen een geopende golfvorm of bewerkkopie.
- **Lijnpunten in plaats van clips verplaatsen:** kies Clips verplaatsen.
- **Onvoldoende werkruimte:** maak schijfruimte vrij voor bronkopieën, resultaten
  en Ongedaan maken. Verwijder geen werkbestanden terwijl SoundSausage actief is.
- **Een herstelkopie ontbreekt of is beschadigd:** de oorspronkelijke bestanden
  blijven beschikbaar. Verwijder de betreffende kopie alleen wanneer je die niet
  meer wilt bewaren.

Zelfgekozen favorieten blijven een vervolgmogelijkheid. Spooreffecten, VST3/LV2/LADSPA, synchronisatie en punch-in/out zijn beschikbaar zoals in hoofdstuk 8a beschreven.

Bewaar een project voordat je de toepassing verlaat. De actuele voortgang en
nieuwe versies staan op de [SoundSausage-website](https://github.com/rene-timmermans/SoundSausage).
