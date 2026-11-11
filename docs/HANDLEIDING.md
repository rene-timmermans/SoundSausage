# SoundSausage — handleiding

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Deze handleiding beschrijft de beschikbare functies van versie 0.17.2. De menunamen
staan zoals ze in het programma worden getoond. Open de handleiding met
**Help → Handleiding** of **F1**. Ze blijft naast de editor openstaan en werkt
zonder internet. Met **Ctrl+F** zoek je een onderwerp; **F3** gaat naar de volgende
treffer en **Shift+F3** naar de vorige.

## Taal kiezen

Kies **Opties → Taal** en vervolgens **Nederlands**, **English**, **Deutsch**,
**Français** of **Español**. Menu’s, vensters, aanwijzingen en de geopende
handleiding wisselen meteen mee. De keuze blijft bij de volgende start bewaard.
Bestandsnamen, zelfgekozen spoornamen en namen van externe plug-ins blijven
behouden. Alle vijf handleidingen zijn ook zonder internet beschikbaar.

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

## 1. De werkruimte

SoundSausage heeft twee weergaven. **Golfvorm bewerken** bewerkt één opname.
**Multitrackweergave** combineert clips op meerdere sporen. Wissel met de knoppen
bovenaan, via **Beeld**, of met **Tab**. De golfvorm en de multitracksessie kunnen
naast elkaar blijven bestaan; wisselen van weergave sluit ze niet. Twee dunne
horizontale lijnen begrenzen de kanalen: de onderrand van links en de bovenrand
van rechts. Ze lopen alleen binnen het tekenvlak, ook bij live opname.

Bovenaan staan menu's en werkbalken. Een korte aanwijzing verschijnt wanneer je
de muis boven een knop houdt. **Opties → Werkbalkteksten tonen** toont ook namen
naast werkbalkiconen. **Opties → Statusbalk tonen** toont of verbergt de smalle
informatieregel helemaal onderaan, onder de niveaumeter. Die regel toont de
afspeelstatus en bestandsgegevens. De keuze blijft bij de volgende start bewaard.
**F11** schakelt naar volledig scherm en terug.

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

## 2. Bestanden openen, bewaren en sluiten

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
samplerate. Selecties korter dan 2 ms kunnen als WAV worden bewaard. Langere
opdrachten tonen voortgang en zijn te annuleren; een mislukte of afgebroken
opslag vervangt het bestaande doelbestand niet. Er is vrije schijfruimte nodig
voor de omzetting en de bewerkte audio.

ID3-tekst en ingesloten hoesafbeeldingen blijven bij MP3-opslag behouden, ook
na een tussenstap via WAV of een SoundSausage-project. De opgeslagen duur wordt
bijgewerkt. MP3-hoofdstukposities, ReplayGain en andere afgeleide velden worden
niet opnieuw berekend. WAV-cuepunten en andere gegevens die MP3 niet kan
bewaren, worden vóór export gemeld. De totale extra bestandsinformatie blijft
begrensd tot 16 MiB. Een eindmix neemt geen bestandsinformatie uit alle sporen samen.

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

### Sluiten

**Bestand → Sluiten** of **Ctrl+W** sluit de huidige golfvorm. In multitrack heet deze
optie **Sessie sluiten**. Het programma blijft open. Bij wijzigingen kun je
opslaan, verwerpen of annuleren. De andere weergave en het klembord blijven
beschikbaar. **Bestand → Afsluiten** of **Ctrl+Q** sluit de toepassing en vraagt ook naar
niet-opgeslagen wijzigingen.

### Lange opnamen en annuleren

Lange opnamen worden in kleine blokken verwerkt; de grens van 128 MiB is vervallen.
De app gebruikt een eigen werkmap op schijf. Zorg voor vrije schijfruimte voor
bronkopieën, nieuwe resultaten en Ongedaan maken. Bij ruimtegebrek blijft het bestaande
werk behouden. Multitracksessies houden hun grens van 24 uur en 32 sporen.

Bij langere opdrachten verschijnt voortgang met **Annuleren**. Annuleren houdt
audio, selectie en Ongedaan maken/Redo intact; bij opslaan blijft het vorige doelbestand
intact. Eén voltooid effect blijft één Ongedaan maken-stap. Bij Voorbeeld wordt hoogstens acht
seconden resultaat voorbereid; Normaliseren analyseert wel de hele selectie.

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

## 3a. Opnemen

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

### Een dagelijkse werkwijze

Een bruikbare volgorde is: opnemen of WAV openen → een fragment selecteren →
eventueel Normaliseren, fade of een ander Amplitude-effect toepassen → opslaan →
in multitrack invoegen → verdere takes op een spoor opnemen → clips verschuiven
of hun volume/pan aanpassen → het project bewaren → een WAV-eindmix maken.
Bewaar het project ook als je later nog afzonderlijke sporen wilt veranderen.
Heropen het project om verder te werken; een eindmix bevat alleen de gecombineerde audio.

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

Een stereobestand heeft een gedeelde tijdas. Kies **Beide** voor bewerkingen die
de duur veranderen, zoals Tijdsduur aanpassen, knippen, verwijderen, trimmen of het toevoegen
van een uitklank. De uitklankopties zijn bij een enkel gekozen stereokanaal uit.
Vertraging, echo, galm en convolutie kunnen wel op één kanaal werken met behoud van
de bestaande lengte. Toonhoogte verschuiven kan één kanaal wijzigen zonder duurverandering.
Met Stilte kun je een fragment in één kanaal leegmaken terwijl de andere golf
precies blijft staan. Gezamenlijke cuepunten verschuiven niet door een bewerking
die slechts één kanaal omkeert.

### Kopiëren en bewaren

Kopiëren en Selectie opslaan leveren bij Links of Rechts mono-audio uit dat kanaal.
Opslaan en Opslaan als blijven de volledige stereogolfvorm bewaren. Je kunt mono-audio
in één stereokanaal plakken wanneer die precies de geselecteerde duur vervangt.
Gemengd plakken kan binnen de bestaande opnameduur op één kanaal mengen. Invoegen of
anders verlengen vereist Beide. De niet-gekozen samples blijven exact behouden.

Opnemen in een bestaande stereogolfvorm vereist Beide. Bij een enkel gekozen
kanaal kan Opnemen een nieuwe golfvorm maken. De kanaalkeuze is tijdens opnemen
vergrendeld. Ongedaan maken/Redo en herstel bewaren de keuze; oudere herstelkopieën openen
met beide kanalen gekozen. Afspelen blijft in de bestaande stereocontext.

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

### Normaliseren

**Effecten → Amplitude → Normaliseren** brengt de hoogste piek naar het gekozen
percentage. Het standaarddoel is 98%. Dit verhoogt of verlaagt het hele fragment
met dezelfde factor; het maakt zachte en harde woorden niet onderling even luid.

**Links en rechts gelijk normaliseren** bewaart de stereobalans. Zonder deze koppeling
krijgt elk kanaal zijn eigen piekniveau. **DC-offset verwijderen vóór normaliseren**
haalt eerst een vaste verschuiving rond de middenlijn weg. Stilte blijft stilte.

Gebruik normaliseren bijvoorbeeld na het mengen of versterken om pieken weer
binnen een passend bereik te krijgen voordat je als PCM exporteert.

### Ompolen, Achterstevoren en Stilte

Deze opdrachten staan direct onder **Effecten** en werken meteen:

- **Ompolen** keert de polariteit om. Het speelt de audio niet achteruit af.
- **Achterstevoren** keert de tijdvolgorde van het fragment om.
- **Stilte** maakt het fragment stil en houdt de lengte gelijk.

Gebruik Ctrl+Z om het resultaat terug te draaien. Gebruik Verwijderen wanneer je een
fragment helemaal uit de tijdlijn van een golfvorm wilt verwijderen.

## 5a. EQ en filters

**Effecten → Filters** biedt drie manieren om de klank van een golfvorm aan te
passen. Een selectie beperkt de bewerking tot dat fragment. Zonder selectie
wordt de hele opname bewerkt. **Voorbeeld** laat de eerste acht seconden van die
keuze horen. **OK** past toe, **Annuleren** sluit zonder wijziging en **Ctrl+Z**
maakt de bewerking ongedaan. **F2** herhaalt de laatste instellingen.

### Grafische equalizer

Tien vaste octaafbanden lopen van 31,5 Hz tot 16 kHz. Sleep een schuif omhoog
om dat gebied te versterken of omlaag om het te verzwakken. Het veld onder de
schuif voert de versterking in dB precies in, van −24 tot +24 dB.

**Vlak** zet alles op nul. **Lage tonen versterken** versterkt het laag, **Stempresentie**
benadrukt spraak en **Lichte glimlachcurve** versterkt laag en hoog licht. **Herstellen**
herstelt Vlak en zet Uitgangsversterking op nul. De banden overlappen: de grafiek toont
de gezamenlijke werking, niet alleen de losse schuifstanden. Banden buiten het
bruikbare frequentiebereik van de opname staan uit en worden overgeslagen.

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

### Niveau, grafiek en selecties

**Uitgangsversterking** past het totale resultaat aan. Sterke EQ-versterking kan boven
0 dBFS uitkomen; verlaag Uitgangsversterking vóór luisteren of PCM-export. De verwerking
knipt pieken niet automatisch af. De grafiek toont de gezamenlijke frequentie-
respons inclusief Uitgangsversterking, binnen een weergave van −36 tot +36 dB.

Dezelfde instellingen gelden voor de gekozen kanalen, zonder ze te mengen.
Filtergeheugen loopt door tussen verwerkingsblokken, ook bij lange bestanden.
Iedere bewerking begint bij het begin van de selectie met leeg filtergeheugen
en houdt de bestaande lengte aan. Een heel korte of abrupt begrensde selectie
kan daardoor een hoorbare overgang geven; kies een ruimer fragment of pas het
effect op de hele opname toe. Filters verschuiven de fase en zijn geen
lineairefase-EQ. Cueposities blijven staan; recordermeetgegevens worden niet
opnieuw berekend.

Bij een lange bewerking toont de voortgang een annuleerknop. Annuleren behoudt
de oorspronkelijke golfvorm en Ongedaan maken-geschiedenis. Voor een multitrackclip open
je eerst een bewerkkopie, pas je het effect toe en kies je Golfvorm op clip toepassen.
Dezelfde EQ- en filterinstellingen zijn ook beschikbaar via **Spooreffecten**;
zie hoofdstuk 8a.

## 5b. Vertraging, echo en galm

De drie effecten staan onder **Effecten → Vertragingseffecten**. Selecteer een
fragment of laat de selectie leeg om de hele golfvorm te bewerken. **Voorbeeld**
speelt maximaal de eerste acht seconden van het resultaat, inclusief een
eventuele uitklank. Een instelling wijzigen stopt het voorbeeld. **OK** past
toe als één Ongedaan maken-stap; **Annuleren** laat de opname intact. **Ctrl+Z** draait terug,
**Ctrl+Shift+Z** doet opnieuw en **F2** herhaalt de laatste instellingen.

### Vertraging — één vertraagde kopie

**Vertraging (links / mono)** bepaalt de vertraging van 1 tot 2.000 ms. Bij stereo
houdt **Gelijke vertraging voor beide kanalen** de twee tijden gelijk. Schakel het uit
om **Vertraging rechts** afzonderlijk te kiezen. Mono gebruikt alleen de eerste tijd.

- **Enkele vertraging:** een enkele kopie na 250 ms.
- **Korte terugkaatsing:** een korte herhaling van 80 ms, bijvoorbeeld voor zang of gitaar.
- **Verdubbeling:** 25 ms voor een verdubbelend effect.
- **Stereoverbreding:** verschillende tijden links en rechts; beschikbaar bij stereo.

Vertraging bevat één herhaling. Kies Echo voor een reeks afnemende herhalingen.

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

### Galm — galm

- **Ruimtegrootte:** de afstand tussen reflecties. Een grotere waarde geeft meer
  spreiding in de tijd en een ruimer karakter; de nagalmtijd blijft apart instelbaar.
- **Nagalmtijd (ongeveer RT60):** de richttijd waarin de galm ongeveer 60 dB afneemt,
  van 0,1 tot 10 seconden. Het precieze verval hangt ook van demping, frequentie
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

### Droog, Effect en uitgangsniveau

**Droog (origineel)** bepaalt het oorspronkelijke geluid. **Nat (effect)** bepaalt
de vertraagde kopieën of galm. Beide zijn afzonderlijke percentages en worden
bij elkaar opgeteld. Met Droog op nul hoor je alleen het effect; met Effect op nul
blijft alleen het oorspronkelijke geluid over.

**Uitgangsversterking** regelt de versterking van het totale resultaat, van −24 tot
+24 dB. De effecten begrenzen pieken niet automatisch. Verlaag dit niveau als
de meters rood worden of bij luisteren vervorming optreedt. Het interne signaal
kan boven 0 dBFS komen; verlaag het vóór PCM-export.

### Een uitklank behouden

Standaard blijft de lengte gelijk. Herhalingen of galm na het einde van de
selectie vallen dan buiten het resultaat. Vink **Toevoegen effect tail after the
selection** aan om extra tijd toe te voegen en stel de duur in, van 0,01 tot
60 seconden. De aanwijzing Suggested tail helpt bij een keuze; verander de
duur zo nodig na het kiezen van een preset. De presets schakelen de extra tijd
steeds uit, zodat een preset niet ongemerkt de opname verlengt.

Bij toevoegen van een uitklank schuift audio ná de selectie vooruit met die
duur. Het effect begint met leeg geheugen aan het begin van de selectie en
loopt niet door in de volgende oorspronkelijke audio. Cuepunten binnen de
selectie blijven staan; latere cuepunten schuiven met de volgende audio mee.
De selectie omvat na toepassen het volledige resultaat, inclusief de uitklank.
De laatste 10 ms van de toegevoegde tijd lopen af naar stilte. Een te korte
duur kan nog hoorbare herhalingen afkappen; gebruik meer tijd of minder
Terugkoppeling/Decay. Bij extreme echoinstellingen kan de natuurlijke uitklank langer
dan de maximale 60 seconden zijn; de aanwijzing meldt dit.

**Voorbeeld:** selecteer een korte stemopname, kies Echo → Warme echo en luister
met Voorbeeld. Vink Toevoegen effect tail aan, kies de voorgestelde tijd en bevestig.
Een stemopname van twee seconden met drie seconden uitklank wordt vijf seconden.
Gebruik Ctrl+Z om naar de oorspronkelijke lengte terug te gaan.

Lange opnamen worden in blokken verwerkt met doorlopend effectgeheugen. Een
geannuleerde bewerking laat audio, selectie, metadata en Ongedaan maken/Redo intact.
Bij een multitrackclip open je eerst een bewerkkopie en plaats je het resultaat
terug met Golfvorm op clip toepassen. Controleer bij een verlengde clip de overlap
met volgende clips; die schuiven niet automatisch mee. Bestaande volume- en
panlijnen worden bij het terugplaatsen naar de nieuwe cliplengte geschaald.
Vertraging, Echo en Galm zijn ook beschikbaar via **Spooreffecten**; zie hoofdstuk 8a.

## 5c. Ruisreductie en klikverwijdering

Deze effecten staan onder **Effecten → Ruisreductie** en werken op een
selectie of, zonder selectie, de hele golfvorm. **Voorbeeld** laat maximaal acht
seconden horen. **OK** past toe, **Annuleren** sluit zonder wijziging en **Ctrl+Z**
draait terug. **F2** herhaalt de instellingen, inclusief het gebruikte ruisprofiel.

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

### Ruisreductie

- **Maximale ruisreductie:** de maximale verzwakking in ruisgebieden, 0–36 dB.
  Begin met 6–12 dB; een hogere waarde kan ook zachte details aantasten.
- **Gevoeligheid:** hoeveel van het profiel als ruis wordt beschouwd. Meer
  gevoeligheid behandelt meer achtergrond, maar kan meer bijgeluiden geven.
- **Egalisatie:** maakt de overgang van sterker naar zwakker onderdrukken rustiger.
  Een hoge waarde laat na een duidelijk geluid tijdelijk meer achtergrond door.
- **Stereokanalen koppelen:** gebruikt dezelfde verzwakking links en rechts om
  de balans te behouden. Zonder koppeling wordt ieder kanaal apart behandeld.
- **Keep removed noise only:** levert het verwijderde deel op in plaats van het
  schoongemaakte geluid. Luister hiermee of waardevolle spraak of muziek verdwijnt.
  Schakel dit weer uit vóór OK wanneer je de schoongemaakte opname wilt behouden.

Dit werkt vooral bij vrij constante ruis, zoals ventilatie of een gelijkmatige
sis. Het verwijdert geen afzonderlijke stemmen uit een mix en herstelt geen
ontbrekende details. Veranderende achtergrond, te sterke reductie of een profiel
met spraak/muziek kan hoorbare vervorming of een korrelige klank geven. De lengte
en cueposities blijven gelijk. De eerste acht seconden in Voorbeeld zijn hetzelfde
als de eerste acht seconden van de volledige bewerking.

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

## 5d. Tijd en toonhoogte

**Effecten → Tijd/toonhoogte** bevat Tijdsduur aanpassen en Toonhoogte verschuiven. Ze bewerken de selectie
of, zonder selectie, de hele golfvorm. Voorbeeld analyseert eerst het volledige
bereik en speelt daarna maximaal acht seconden af. Het voorbeeld is hetzelfde
prefix als bij toepassen. Lange opnamen hebben daardoor ook voor Voorbeeld
analysetijd nodig. De voortgang is annuleerbaar; annuleren behoudt de opname.

### Tijdsduur aanpassen

**Nieuw length** kiest de nieuwe lengte als percentage, van 25 tot 400%.
100% houdt de lengte gelijk, 200% maakt de opname tweemaal zo lang en 50%
halveert de speelduur. De toonhoogte blijft behouden. De getoonde tijden helpen
bij het instellen van een passend resultaat.

Met **Van … BPM to … BPM** en **Uit tempo instellen** bereken je de lengte op basis
van een bekend begintempo en gewenst eindtempo. Dit is geen automatische
tempodetectie. Van 120 naar 100 BPM wordt de lengte 120%. Een verhouding buiten
het beschikbare bereik wordt gemeld en verandert de instelling niet.

Cuepunten binnen het bewerkte bereik volgen de nieuwe tijdschaal. Audio en
cuepunten na de selectie schuiven mee met het verschil in lengte. De samplerate
van het bestand verandert niet. De selectie omvat na toepassen het resultaat.

### Toonhoogte verschuiven

**Pitch change** kiest −24 tot +24 halve tonen. +12 is een octaaf omhoog;
−12 is een octaaf omlaag. Een fractie geeft fijnstemming: 0,01 halve toon is
één cent. De speelduur en cueposities blijven behouden.

**Formanten behouden** helpt het karakter van zang of spraak te behouden bij een
toonhoogteverschuiving. Vergelijk beide standen bij instrumenten en grote
verschuivingen; het resultaat verschilt per opname.

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

## 5e. Vervorming en convolutie

**Effecten → Speciaal** bevat Vervorming en Convolutie. Beide bewerken een
selectie of, zonder selectie, de hele golfvorm. Voorbeeld laat de eerste acht
seconden horen. OK bevestigt één Ongedaan maken-stap; Annuleren laat de golfvorm intact.
Ctrl+Z draait terug, Ctrl+Shift+Z doet opnieuw en F2 herhaalt de instellingen.

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
vraagt bij stereo Beide.

Zonder **Volledige uitklank behouden** blijft de oorspronkelijke lengte gelijk.
Met de optie wordt de volledige uitklank van de respons toegevoegd, precies de
responslengte min één sample. Audio en cuepunten ná de selectie schuiven daardoor
vooruit; cuepunten binnen de oorspronkelijke selectie blijven staan. De uitklank
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

## 7. Frequenties analyseren

Selecteer een fragment en kies **Analyseren → Frequentieanalyse** of **Alt+Z**.
Zonder selectie wordt de opname als uitgangspunt genomen. De grafiek toont
frequenties van laag naar hoog en het bijbehorende niveau. Onderaan staat de
sterkste gevonden frequentie met het niveau in dBFS.

De analyse gebruikt bij lange fragmenten een begrensd deel rond het midden van
het gekozen bereik. Ze is een hulpmiddel voor tonen en spectrale verhoudingen,
geen doorlopende spectrummeter. Selecteer een korter fragment om een bepaalde
klank of toon te onderzoeken. Sluiten verandert de audio niet.

## 8. Meerdere sporen combineren

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

### Een effect op een clip toepassen

Dubbelklik een clip of kies **Kopie in golfvorm bewerken** via de rechtermuisknop.
De kopie opent in de golfvormeditor. Pas daar het effect toe. Kies daarna
**Venster → Golfvorm op clip toepassen** om het resultaat terug te plaatsen.

Gewoon terugschakelen naar multitrack past de kopie niet toe. Sluiten en
verwerpen laat de oorspronkelijke clip intact. Na toepassen kunnen de oude
audio en de lijnen met Ongedaan maken in de sessie worden hersteld. Een veranderde
samplerate wordt bij terugplaatsen naar de sessierate omgezet.

### Opslaan en mixdown

**Sessie opslaan** bewaart het bewerkbare project. **Sessie mixen** of
**Eindmix maken** maakt één WAV van de hele sessie. Een tijdbereikselectie bepaalt
hierbij niet de exportlengte. Controleer Dempen, Solo en de niveaus voordat je
exporteert: die instellingen werken door in het eindresultaat.

Volume, pan, mute, solo en spoorketens kunnen tijdens het luisteren veranderen.
Dezelfde spoorketen wordt bij mixdown gebruikt. Ongedaan maken/Redo en wisselen van weergave
stoppen het afspelen. De bronopnamen blijven behouden.

## 8a. Spooreffecten, VST3 en opnemen met begeleiding

### Een effectketen op een spoor

Openen een multitracksessie en klik op **FX** naast de spoornaam, of kies
**Effecten → Spooreffecten** voor het gekozen spoor. Kies een effect en druk
op **Toevoegen**. Het effectvenster gebruikt dezelfde instellingen en presets als de
golfvormeditor. **OK** voegt het effect toe; **Toepassen** past de instelling toe
terwijl het venster openblijft. De oorspronkelijke audio blijft behouden.

De keten ondersteunt Versterken, Kanalenmixer, Dynamiek, Grafische EQ, Parametrische EQ,
Filters, Vertraging, Echo, Galm, Ompolen en VST3-effecten. Een spoor heeft maximaal
zestien effecten. Een monobron wordt eerst naar stereo gekopieerd. Clipvolume,
panlijnen en fades werken vóór de spoorketen; spoorvolume en spoorpan erna.

- Dubbelklik op een effect, of kies **Bewerken**, om de instellingen te wijzigen.
- **Omhoog / Omlaag** verplaatst het effect. De volgorde kan het geluid veranderen.
- Het vinkje schakelt een effect tijdelijk uit. **Verwijderen** verwijdert het.
- **Ctrl+Z / Ctrl+Shift+Z** maakt een wijziging ongedaan of voert haar opnieuw uit.
- **Uitklank na laatste clip** voegt 0–60 seconden toe om delay of galm te laten
  uitsterven. Zonder extra tijd eindigt het spoor op de laatste clipgrens;
  een langer ander spoor kan de bestaande uitklank nog laten horen.

De keten werkt tijdens afspelen en komt ook in Eindmix maken terecht. Volume, pan,
mute, solo en effectinstellingen kunnen tijdens luisteren veranderen. **Toepassen**
bevestigt een effectinstelling. Al naar het audioapparaat gestuurde audio speelt
nog met de vorige instelling. Bij opnieuw starten, zoeken of opnieuw inschakelen
begint het effectgeheugen leeg. Een gewijzigde interne effectinstelling kan de
uitklank opnieuw beginnen. Een VST3-parameterwijziging houdt dezelfde instantie.

Versterken gebruikt vaste versterking per kanaal; voor een verloop in de tijd
gebruik je de **Volumelijn** van een clip. Normaliseren, ruisreductie, klikherstel,
Tijdsduur aanpassen, Toonhoogte verschuiven, Vervorming en Convolutie blijven golfvormbewerkingen via
**Kopie in golfvorm bewerken**. Een realtime keten verandert de bronbestanden niet.

### VST3-effecten toevoegen

1. Installeer een **64-bit Linux VST3-effect** en zoek de map met uitgang
   `.vst3`. Gebruik de Linux-uitgave van de maker.
2. Kies **VST3-plug-in → Toevoegen** in Spooreffecten en klik **VST3-bundel toevoegen**.
3. Kies de bundelmap. Meerdere effecten uit dezelfde bundel worden afzonderlijk
   beschikbaar in de keuzelijst.
4. Kies het effect. Zoek de parameter op naam en wijzig de waarde. **Toepassen**
   laat de gewijzigde instelling op het spoor horen; **OK** bevestigt en sluit.

Het parametervenster gebruikt een genormaliseerde schaal van 0–100%. Dit is de
positie binnen het bereik van de plug-in: 50% betekent niet automatisch 50%
volume. Discrete parameters krijgen passende stappen. Alleen-lezen parameters
kunnen niet worden veranderd. De oorspronkelijke eigen vensters van plug-ins
zijn nog niet ingebed.

Ondersteund zijn native Linux VST3-audio-effecten met één stereo-invoerbus,
één stereo-uitvoerbus en 32-bit floatverwerking. MIDI-instrumenten, extra
sidechains, VST2, Windows-VST's en andere plug-informaten vallen hierbuiten.
Sommige effecten vereisen extra hostfuncties en kunnen niet openen. De app meldt
dat en verandert het project niet. Een gerapporteerde plug-invertraging staat
in het venster; die wordt nog niet automatisch tussen sporen gecompenseerd.

Plug-ins draaien in een afzonderlijk hulpproces. Als een plug-in stopt,
onbruikbare audio terugstuurt of niet meer antwoordt, stopt het afspelen met een
melding. Tijdens opname met begeleiding blijft de vastgelegde take behouden.
De rest van de app en de bronopnamen blijven beschikbaar. Dit maakt een niet
passende plug-in nog niet geschikt voor realtime gebruik.

Een project bewaart de parameterwaarden en maximaal 1 MiB status per VST3-effect.
De plug-in en eventuele eigen bibliotheken, samples of responsbestanden blijven
apart geïnstalleerd. Op een andere computer voeg je dezelfde bundel toe. Bij een
ontbrekende of gewijzigde versie blijven de opgeslagen instellingen bestaan;
afspelen en export vragen om een passende plug-in of om bewust uitschakelen van
het effect. Opnieuw toevoegen van een gewijzigde bundel maakt die versie
beschikbaar als nieuwe keuze. Er wordt niet stilzwijgend zonder het effect gemixt.

### Opnemen terwijl andere sporen spelen

1. Zet de begeleiding op één of meer sporen.
2. Kies een ander spoor en plaats de cursor waar de nieuwe take moet beginnen.
3. Druk **R**, kies de ingang en **Nieuw clip on…** als bestemming.
4. Vink **Bestaande sporen afspelen tijdens opnemen** aan. De bestaande sporen,
   inclusief hun effecten, spelen vanaf de cursor terwijl de nieuwe take wordt
   vastgelegd. De microfoon zelf wordt niet door de luidsprekers teruggespeeld.
5. **P** pauzeert beide; opnieuw **P** hervat beide. **Stoppen**, **Esc**, **Spatie**
   of opnieuw **R** stopt de begeleiding en bewaart de take als één Ongedaan maken-stap.

Aan het einde van de begeleiding kan de opname doorgaan. Een opname met een
maximale duur stopt ook de begeleiding. **Opname verwerpen** verwijdert alleen
de nieuwe take. Gaat een apparaat of plug-in verloren, dan blijven de reeds
opgenomen samples behouden. Bestanden en sporen wijzigen tijdens opnemen is
vergrendeld. Voor een golfvormopname blijft de afzonderlijke opnamebediening gelden.

#### De opnamepositie afstellen

De app koppelt de startpositie aan de afspeelklok en de vastgelegde invoerframes.
De fysieke in-/uitvoerroute kan extra vertraging hebben. Met **Opnemen position
offset** verschuif je het nieuwe blok: negatief is eerder, positief later.
Een waarde van −15 ms corrigeert bijvoorbeeld een take die 15 ms te laat staat.
De instelling wordt onthouden; de opgenomen bron zelf blijft behouden.

Neem een bekende testklik via de gebruikte in-/uitvoerroute op en vergelijk de
klikposities. Vul het gemeten verschil in en controleer met een tweede take.
Gebruik bij een andere geluidsinterface of andere bufferinstelling een nieuwe
meting. Als de verschuiving vóór tijd nul komt, wordt het deel vóór nul bij het
invoegen weggelaten; de oorspronkelijke take blijft bij een mislukte verwerking
voor herstel beschikbaar.

Automatische fysieke latencykalibratie, compensatie van plug-invertraging,
correctie van klokdrift tussen verschillende apparaten en punch-in/out zijn
vervolgstappen. Nauwkeurige gelijkloop over lange takes hangt ook van de gebruikte
apparaatklokken af. Controleer de gekozen in-/uitvoerroute met een korte proeftake.

### Nieuwe projecten bewaren en heropenen

**Sessie opslaan / Sessie opslaan als** bewaart de gebruikte audio, clips, lijnen,
spoorketens, volgorde, bypass, uitklanktijden en VST3-instellingen. **Sessie openen**
herstelt die bewerkbare sessie. **Sessie mixen** bewaart één WAV met dezelfde
spoorketens en de ingestelde uitklank. Het project blijft nodig om afzonderlijke
sporen verder te veranderen.

Nieuwe projecten gebruiken de bijgewerkte projectversie. Eerdere
SoundSausage-projectversies blijven te openen. Oudere appversies kunnen de nieuwe
spoorketens niet lezen; gebruik versie 0.16.0 of nieuwer om ze te heropenen.
Herstel na onverwacht afsluiten bewaart de ketens en plug-ininstellingen eveneens.
Een ontbrekende externe plug-in verhindert het herstellen van de bronopnamen niet.

## 9. Een andere samplerate kiezen

**Bewerken → Samplerate omzetten** zet de hele golfvorm om. Kies het gewenste aantal
Hz en bevestig. Toonhoogte en speelduur blijven behouden, met afronding op hele
uitvoerframes. Zeer korte fragmenten houden minimaal één frame. Selectie en
cursor volgen dezelfde tijden. **Ctrl+Z** herstelt zowel de vorige audio als de
vorige rate.

Deze opdracht verandert de opname. Automatische omzetting voor een uitvoerapparaat
verandert alleen het afgespeelde signaal en laat de golfvorm zelf intact.

## 10. Favorieten, vensters en hulp

**Favorieten** geeft snel toegang tot herhalen, normaliseren en fades. Eigen
favorietenlijsten kunnen nog niet worden samengesteld. **Venster** wisselt
tussen beide weergaven en bevat de opdrachten om een golfvorm in te voegen of
naar een clip terug te plaatsen.

**Help → Over** toont de versie, maker, licentie en website. De handleiding
blijft als afzonderlijk venster beschikbaar, zodat je de stappen in de editor
kunt volgen.

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

## 12. Problemen en work in progress

- **Geen ingangsniveau:** controleer Ingang, het gekozen kanaal en het microfoonvolume
  in de geluidsinstellingen. Start een nieuwe take na het aansluiten van een apparaat.
- **Geen geluid:** controleer Audioapparaten, systeemvolume, Dempen en Solo.
  Kies bij een verdwenen apparaat een beschikbare uitgang en start opnieuw.
- **Vervorming of rode pieken:** verlaag volume of versterking; opgetelde clips
  en Gemengd plakken kunnen samen boven het uitvoerniveau komen.
- **Plakken lukt niet:** controleer of bron en doel beide mono of beide stereo zijn.
- **Een effect is grijs:** open een golfvorm of een bewerkkopie; Kanalenmixer
  vereist stereo. Tijdsduur aanpassen en bewerkingen die de duur veranderen vragen Beide.
  De overige effecten vereisen een geopende golfvorm of bewerkkopie.
- **Lijnpunten in plaats van clips verplaatsen:** kies Clips verplaatsen.
- **Onvoldoende werkruimte:** maak schijfruimte vrij voor bronkopieën, resultaten
  en Ongedaan maken. Verwijder geen werkbestanden terwijl SoundSausage actief is.
- **Een herstelkopie ontbreekt of is beschadigd:** de oorspronkelijke bestanden
  blijven beschikbaar. Verwijder de betreffende kopie alleen wanneer je die niet
  meer wilt bewaren.

Eigen plug-invensters, meer plug-informaten, automatische latency-/driftcompensatie,
punch-in/out en een markereditor zijn vervolgmogelijkheden. Realtime spoorketens,
Linux VST3 en opname met begeleiding zijn beschikbaar zoals in hoofdstuk 8a beschreven.

Bewaar een project voordat je de toepassing verlaat. De actuele voortgang en
nieuwe versies staan op de [SoundSausage-website](https://github.com/rene-timmermans/SoundSausage).
