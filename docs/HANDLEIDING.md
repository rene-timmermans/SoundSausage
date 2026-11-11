# SoundSausage — handleiding

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Deze handleiding beschrijft de beschikbare functies van versie 0.14.0. De menunamen
staan zoals ze in het programma worden getoond. Open de handleiding met
**Help → Handleiding** of **F1**. Ze blijft naast de editor openstaan en werkt
zonder internet. Met **Ctrl+F** zoek je een onderwerp; **F3** gaat naar de volgende
treffer en **Shift+F3** naar de vorige.

## Snel beginnen

1. Kies **File → Open** en open een WAV-bestand.
2. Druk op **Spatie** om te luisteren en opnieuw op Spatie om te stoppen.
3. Sleep over de golfvorm om een fragment te selecteren.
4. Kies bijvoorbeeld **Transform → Amplitude → Normalize**. Luister met
   **Preview** en bevestig met **OK**.
5. Gebruik **Ctrl+Z** wanneer je de bewerking wilt terugdraaien.
6. Kies **File → Save As** om het resultaat onder een nieuwe naam te bewaren.

Voor meerdere opnamen tegelijk kies je **File → New Multitrack Session**.
Importeer de WAV-bestanden, verschuif de clips en maak een eindmix met **Mix Down**.

## 1. De werkruimte

SoundSausage heeft twee weergaven. **Edit Waveform View** bewerkt één opname.
**Multitrack View** combineert clips op meerdere sporen. Wissel met de knoppen
bovenaan, via **View**, of met **Tab**. De golfvorm en de multitracksessie kunnen
naast elkaar blijven bestaan; wisselen van weergave sluit ze niet.

Bovenaan staan menu's en werkbalken. Een korte aanwijzing verschijnt wanneer je
de muis boven een knop houdt. **Options → Show Toolbar Labels** toont ook namen
naast werkbalkiconen. **Options → Show Status Bar** toont of verbergt de statusbalk.
**F11** schakelt naar volledig scherm en terug.

Onderaan staan afspeelknoppen, de klok en de niveaumeters. **Sel** toont het begin,
einde en de lengte van de selectie. **View** toont het zichtbare tijdvak. De klok
volgt tijdens afspelen de audiopositie. Een rode piekindicatie betekent dat het
signaal boven het maximale uitvoerniveau komt: verlaag het volume of normaliseer.

Een sterretje voor de bestandsnaam betekent dat er wijzigingen zijn die nog
niet zijn opgeslagen. Een uitgeschakelde menuoptie kan bij de andere weergave
horen, een selectie vereisen of nog in ontwikkeling zijn.

## 2. Bestanden openen, bewaren en sluiten

### Losse opnamen

**File → New** maakt een lege golfvorm. Kies **Mono** voor één kanaal en **Stereo**
voor links/rechts. De samplerate bepaalt hoeveel audiopunten per seconde worden
bewaard. 44.100 en 48.000 Hz zijn gangbare keuzes.

**File → Open** opent een WAV-bestand. **Save** bewaart de huidige opname en
**Save As** kiest een andere naam of WAV-uitvoering. **Save Selection** schrijft
alleen het geselecteerde fragment naar een nieuw bestand.

Bij opslaan kun je PCM met 8, 16, 24 of 32 bits kiezen, of float32. 16-bit PCM is
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

### Projecten met meerdere sporen

**New Multitrack Session** maakt een sessie met een gekozen samplerate en aantal
sporen. **Open Session**, **Save Session** en **Save Session As** openen en bewaren
een volledig project. De gebruikte audio wordt in het project opgenomen, samen
met clipposities, spoorinstellingen en getekende lijnen.

| Bestand | Gebruik |
| --- | --- |
| WAV | Een losse opname of een afgemaakte eindmix |
| SoundSausage-project (`.celp`) | Een bewerkbaar project met meerdere sporen en de gebruikte audio |
| Oudere sessie (`.ses`) | Beperkte import; sla het resultaat daarna op als SoundSausage-project |

Een WAV-eindmix bevat geen afzonderlijk bewerkbare sporen. Bewaar daarom ook het
project wanneer je later verder wilt mixen.

### Sluiten

**File → Close** of **Ctrl+W** sluit de huidige golfvorm. In multitrack heet deze
optie **Close Session**. Het programma blijft open. Bij wijzigingen kun je
opslaan, verwerpen of annuleren. De andere weergave en het klembord blijven
beschikbaar. **File → Exit** of **Ctrl+Q** sluit de toepassing en vraagt ook naar
niet-opgeslagen wijzigingen.

### Lange opnamen en annuleren

Lange opnamen worden in kleine blokken verwerkt; de grens van 128 MiB is vervallen.
De app gebruikt een eigen werkmap op schijf. Zorg voor vrije schijfruimte voor
bronkopieën, nieuwe resultaten en Undo. Bij ruimtegebrek blijft het bestaande
werk behouden. Multitracksessies houden hun grens van 24 uur en 32 sporen.

Bij langere opdrachten verschijnt voortgang met **Annuleren**. Annuleren houdt
audio, selectie en Undo/Redo intact; bij opslaan blijft het vorige doelbestand
intact. Eén voltooid effect blijft één Undo-stap. Bij Preview wordt hoogstens acht
seconden resultaat voorbereid; Normalize analyseert wel de hele selectie.

### Werk herstellen

Na onverwacht afsluiten biedt SoundSausage de laatst vastgelegde stand aan.
Kies **Herstellen**, **Verwijderen** of **Later**. Met **File → Recover Work** kun
je bewaarde herstelkopieën later openen. Andere actieve instanties worden
overgeslagen. De oorspronkelijke bestanden blijven behouden. Golfvorm, sessie,
clipinstellingen en lijnen worden hersteld; Undo begint opnieuw.

Herstelkopieën volgen bevestigde wijzigingen; selectie en cursor volgen binnen
ongeveer een seconde. Bij ruimtegebrek meldt de statusbalk dat de herstelkopie
niet is bijgewerkt. Bewaar belangrijke opnamen zelf: herstel vervangt geen backup.
Na gewoon opslaan of bevestigd sluiten wordt de eigen kopie opgeruimd. Zie
[lange bestanden en herstel](https://github.com/rene-timmermans/SoundSausage/blob/main/docs/LANGE_BESTANDEN.md)
voor werkruimte en grenzen.

## 3. Luisteren en navigeren

**Spatie** start of stopt het afspelen. Met een selectie luister je naar dat
fragment; zonder selectie begint het afspelen bij de cursor. **P** pauzeert en
hervat. **Esc** stopt. **Loop** herhaalt het gekozen afspeelbereik. Lussen kunnen
nog een korte overgang hebben.

**Home** gaat naar het begin en **End** naar het einde. De navigatieknoppen laten
je ook vijf seconden terug of vooruit springen. Navigeren of een bevestigde
bewerking uitvoeren stopt lopend afspelen; start daarna opnieuw om het nieuwe
resultaat te horen.

Gebruik **Zoom In**, **Zoom Out**, **Zoom Full** en **Zoom to Selection** onder
**View**. **Ctrl+0** toont de hele opname; **Ctrl+Shift+A** vult de weergave met de
selectie. **Ctrl+muiswiel** zoomt rond de muispositie. De horizontale schuifbalk
verplaatst het zichtbare tijdvak.

### Het uitvoerapparaat kiezen

Open **Options → Audio Hardware**. Kies **System Default** om de systeemuitgang
te volgen of selecteer een specifiek apparaat. De keuze blijft bewaard.
Dezelfde uitgang wordt gebruikt voor normaal afspelen en effectvoorbeelden.

De **Playback buffer** staat standaard op 100 ms. Een grotere waarde verdraagt
onderbrekingen beter; een kleinere reageert sneller. De werkelijke buffer kan
per apparaat verschillen. Instellingen wijzigen stopt het afspelen en voorbeelden.

Als een gekozen apparaat verdwijnt, kies je opnieuw een beschikbare uitgang en
start je het afspelen. Controleer bij ontbrekend geluid ook het systeemvolume,
de systeemuitgang en eventuele Mute- of Solo-knoppen in multitrack.

## 3a. Opnemen

### Een opname maken

1. Sluit een microfoon of audio-interface aan. Kies de ingang onder
   **Options → Audio Hardware → Recording device**. De keuze blijft bewaard.
2. Druk op **R** of de ronde opnameknop. Controleer **Input** in het opnamevenster.
3. Kies **Destination**. **New waveform** maakt een losse opname. Bij een bestaande
   golfvorm kun je **Insert at cursor** kiezen, of **Replace selection** wanneer
   er een selectie is. In multitrack wordt een nieuw blok op het gekozen spoor
   toegevoegd, vanaf de cursor. Bestaande blokken blijven behouden.
4. Kies **Mono** of **Stereo**. **First input channel** kiest één ingang bij mono
   of de eerste van een opeenvolgend paar bij stereo. Een monoapparaat kan op
   beide stereokanalen worden opgenomen. Het invoegdoel bepaalt samplerate en,
   bij een bestaande golfvorm, kanaalaantal. Een andere apparaatrate wordt na
   Stop omgezet. **Maximum duration** kan automatisch stoppen; **Until Stop**
   blijft doorlopen totdat je zelf stopt of de schijf geen ruimte meer heeft.
5. Kies **Start Recording**. De live golfvorm toont de laatste twintig seconden;
   de grote klok toont de totale vastgelegde duur. De meters tonen het ingangsniveau.
6. **P** pauzeert en hervat. Pauzetijd komt niet in de opname. **Stop**, **Esc**,
   **Spatie** of de opnameknop stopt en bewaart de take in het gekozen doel.

Bij het invoegen of vervangen is de gehele opname één Undo-stap. Ook een nieuw
opgenomen blok in multitrack is met Undo te verwijderen. Een nieuwe golfvorm
is pas als bestand bewaard nadat je **Save** of **Save As** kiest.

**Discard Recording** verwijdert uitsluitend de lopende take en vraagt om een
bevestiging. Tijdens opname staan andere bewerkingen uit. Sluiten vraagt of de
opname moet worden gestopt en behouden, verworpen of doorgezet. Daarna gelden
de gewone vragen voor niet-opgeslagen werk.

### Ingang en herstel

De microfoon wordt pas geopend na **Start Recording**. SoundSausage speelt het
ingangssignaal niet door de luidsprekers. Bestaande sporen worden tijdens opnemen
nog niet afgespeeld. Neem de takes afzonderlijk op en combineer ze daarna in
multitrack. Voor luisteren gebruik je na Stop de gewone afspeelknoppen.

Is een specifiek gekozen USB-apparaat verdwenen, kies dan een beschikbare ingang.
Tijdens een opname leidt apparaatverlies niet naar een andere microfoon: de app
stopt en behoudt de vastgelegde audio. Het ingangsniveau regel je op de microfoon,
audio-interface of in de geluidsinstellingen van Linux. Verhoog het zo nodig
voordat je begint; vervorming door een overstuurde ingang is achteraf niet te herstellen.

Opnamen worden in blokken naar een eigen werkbestand geschreven. Er is voldoende
vrije schijfruimte nodig voor de take, het resultaat en Undo. De opname krijgt
ongeveer iedere seconde een herstelpunt. Na onverwacht afsluiten biedt de volgende
start de onderbroken opname apart aan. **File → Recover Work** kan dat later ook.
Herstellen opent de laatst vastgelegde audio als nieuwe golfvorm, zonder de
bronbestanden of de multitracksessie te overschrijven. Bij een schrijffout kan
het laatste herstelpunt iets ouder zijn dan de klok aangaf.

Annuleer je de verwerking ná Stop, bijvoorbeeld een langere omzetting, dan blijft
de take voor herstel bewaard. Het eerdere document is dan niet aangepast.

### Een dagelijkse werkwijze

Een bruikbare volgorde is: opnemen of WAV openen → een fragment selecteren →
eventueel Normalize, fade of een ander Amplitude-effect toepassen → opslaan →
in multitrack invoegen → verdere takes op een spoor opnemen → clips verschuiven
of hun volume/pan aanpassen → het project bewaren → een WAV-eindmix maken.
Bewaar het project ook als je later nog afzonderlijke sporen wilt veranderen.
Heropen het project om verder te werken; een eindmix bevat alleen de gecombineerde audio.

## 4. Selecteren en de golfvorm bewerken

Klik in de golfvorm om de cursor te plaatsen. Sleep met de linkermuisknop om een
fragment te selecteren. **Shift+klik** breidt de selectie vanaf het bestaande
begin uit en houdt de kanaalkeuze vast. **Ctrl+A** selecteert de hele duur in de
huidige kanaalkeuze.

**Edit → Set Selection** voert begin en einde precies in. Deze velden gebruiken
frames: bij 44.100 Hz zijn 44.100 frames één seconde. **F4** verplaatst de grenzen
van een selectie naar binnen, naar nuldoorgangen in het gekozen kanaal
(bij Both in links). Dat kan
een abrupte overgang verminderen; luister het resultaat altijd na.

| Opdracht | Wat gebeurt er? |
| --- | --- |
| Cut | Verwijdert de selectie en zet haar op het klembord |
| Copy | Kopieert de selectie zonder de opname te veranderen |
| Paste | Vervangt de selectie, of voegt bij de cursor in |
| Mix Paste | Mengt de klembordaudio met de bestaande audio vanaf de selectie of cursor |
| Delete Selection | Verwijdert het geselecteerde fragment |
| Trim | Houdt alleen de selectie over |
| Undo / Redo | Maakt de laatste bewerking ongedaan of voert haar opnieuw uit |

Plakken zet de samplerate zo nodig om. Het klembord blijft ongewijzigd. Bij Both
moet het aantal kanalen overeenkomen. Bij Left of Right kan mono-audio het
geselecteerde tijdvak van dat kanaal vervangen. Meer hierover staat hieronder.
Mix Paste kan luider uitvallen doordat twee signalen worden opgeteld.

## 4a. Links, rechts en stereo kiezen

Een stereogolfvorm heeft een linker kanaal **L** boven en een rechter kanaal
**R** onder. Je kunt hetzelfde tijdvak voor beide kanalen kiezen of slechts
één kanaal bewerken.

- Sleep binnen L om alleen links te selecteren, of binnen R voor alleen rechts.
- Sleep van de ene golf naar de andere om beide kanalen te selecteren.
- Kies boven de golfvorm **Channels → Both (L+R), Left (L) of Right (R)** om
  een bestaand tijdvak op andere kanalen te richten.
- Dezelfde keuze staat onder **Edit → Select Channels**. **Alt+B**, **Alt+L**
  en **Alt+R** kiezen beide, links en rechts.

Het geselecteerde kanaal heeft een gekleurd L/R-label. Een geselecteerd tijdvak
is alleen in de gekozen kanalen ingekleurd. **Shift** houdt bij het verlengen
van een selectie de kanaalkeuze vast. Dubbelklikken kiest het zichtbare tijdvak
in het aangeklikte kanaal. **Ctrl+A** selecteert de hele duur in de huidige
kanaalkeuze. Bij mono is er één kanaal en staat de extra keuze niet in beeld.

### Een effect op één kanaal

Kies bijvoorbeeld Right, selecteer een fragment en open Amplify / Fade of
Normalize. Het effectvenster vermeldt de gekozen kanalen. Met Preview hoor je
het resultaat in stereocontext: het andere kanaal blijft ongewijzigd. OK past
alleen het gekozen kanaal toe; Ctrl+Z herstelt de audio én de bijbehorende keuze.
F2 herhaalt de laatste instellingen op de kanalen die op dat moment gekozen zijn.

Zonder tijdselectie werkt een effect op de hele duur van het gekozen kanaal.
Normalize en Dynamics analyseren daarbij alleen dat kanaal. Channel Mixer kan
beide kanalen als invoer gebruiken, maar wijzigt alleen de gekozen uitgang.
Bij een stereo-ruisprofiel of stereo-impulsrespons wordt het bijbehorende kanaal
gebruikt. Frequentieanalyse volgt eveneens de gekozen kanalen.

Een stereobestand heeft een gedeelde tijdas. Kies **Both** voor bewerkingen die
de duur veranderen, zoals Stretch, knippen, verwijderen, trimmen of het toevoegen
van een uitklank. De uitklankopties zijn bij een enkel gekozen stereokanaal uit.
Delay, echo, galm en convolutie kunnen wel op één kanaal werken met behoud van
de bestaande lengte. Pitch Shift kan één kanaal wijzigen zonder duurverandering.
Met Silence kun je een fragment in één kanaal leegmaken terwijl de andere golf
precies blijft staan. Gezamenlijke cuepunten verschuiven niet door een bewerking
die slechts één kanaal omkeert.

### Kopiëren en bewaren

Copy en Save Selection leveren bij Left of Right mono-audio uit dat kanaal.
Save en Save As blijven de volledige stereogolfvorm bewaren. Je kunt mono-audio
in één stereokanaal plakken wanneer die precies de geselecteerde duur vervangt.
Mix Paste kan binnen de bestaande opnameduur op één kanaal mengen. Invoegen of
anders verlengen vereist Both. De niet-gekozen samples blijven exact behouden.

Opnemen in een bestaande stereogolfvorm vereist Both. Bij een enkel gekozen
kanaal kan Record een nieuwe golfvorm maken. De kanaalkeuze is tijdens opnemen
vergrendeld. Undo/Redo en herstel bewaren de keuze; oudere herstelkopieën openen
met beide kanalen gekozen. Afspelen blijft in de bestaande stereocontext.

### Zoomen en functie-iconen

**Zoom Full** toont de gehele opname; het vergrootglas heeft markeringen naar
de buitenste grenzen. **Zoom to Selection** vult het beeld met het geselecteerde
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
ongewijzigd en is bij Preview wel hoorbaar in de bestaande stereocontext. De opdrachten staan onder **Transform**. Voor effecten op een
multitrackclip gebruik je eerst **Edit Copy in Waveform**; verderop staat hoe je
het resultaat terugplaatst.

In de Amplitude-, EQ-, filter-, delay- en galmvensters speelt **Preview** de eerste acht seconden van het
resultaat zonder de opname te veranderen. Opnieuw klikken stopt het voorbeeld.
Een instelling wijzigen of het venster sluiten stopt het ook. **OK** past toe;
**Cancel** laat de opname zoals ze was. **Ctrl+Z** draait de toepassing terug.

**F2** of **Edit → Repeat Last Command** herhaalt het laatste golfvormeffect met
dezelfde instellingen op de nieuwe selectie en de huidige kanaalkeuze. Controleer
het tijdvak en de kanalen voordat je herhaalt.

### Amplify / Fade

Open **Transform → Amplitude → Amplify / Fade**. **Initial amplification** is de
versterking aan het begin; **Final amplification** die aan het einde. 100% houdt
het niveau gelijk, 50% halveert de amplitude en 200% verdubbelt haar.

**Lock left / right** houdt de kanalen gelijk. **Keep initial and final
amplification equal** geeft een constante versterking. Zet die optie uit voor
een fade. Lineaire fades kunnen tot stilte lopen; logaritmische fades vereisen
positieve begin- en eindwaarden. Presets bieden ongeveer +6 of −6 dB en fades.

Voorbeeld: selecteer het begin van een opname, kies **Fade In** als preset en
luister met Preview. Pas met OK toe. **Fade In** en **Fade Out** staan ook als
directe opdrachten onder Amplitude; deze passen onmiddellijk een lineaire fade toe.

### Channel Mixer

**Transform → Amplitude → Channel Mixer** is beschikbaar voor stereo. Voor elk
nieuw kanaal kies je hoeveel van het oorspronkelijke linker- en rechterkanaal
wordt gebruikt. Negatieve percentages keren de polariteit van een bijdrage om;
**Invert output polarity** keert het hele nieuwe kanaal om.

Presets wisselen links en rechts, kopiëren één kant naar beide kanten, middelen
beide kanalen naar mono of maken het verschil tussen links en rechts. De
mono-mix blijft een stereobestand met twee gelijke kanalen.

Voorbeeld: kies **Swap Left / Right** om omgekeerd aangesloten kanalen te wisselen.
Kies **Mono (L + R average)** om een gelijke mix op beide kanten te horen. Door
mengen kan het niveau stijgen; verlaag zo nodig de percentages.

### Dynamics Processing

**Transform → Amplitude → Dynamics Processing** verandert het verschil tussen
zachte en harde passages. De curve koppelt het ingangsniveau aan het gewenste
uitgangsniveau. Onder de diagonale lijn wordt een niveau zachter; erboven luider.

Klik in de curve om een punt toe te voegen en sleep om het te veranderen. De
velden onder de curve bieden precieze invoer. Rechtsklikken, **Remove Point**
of **Delete** verwijdert een binnenpunt. De horizontale eindposities staan vast.

| Instelling | Betekenis |
| --- | --- |
| Attack | Hoe snel de detector op een hogere piek reageert |
| Release | Hoe snel de regeling na een piek terugloopt |
| Output gain | Versterking of verzwakking van het resultaat |
| Link stereo channels | Beide kanalen krijgen dezelfde regeling, zodat hun onderlinge balans blijft bestaan |

Een **compressor** verkleint niveauverschillen boven een drempel. Een
**piekbegrenzer** temt harde pieken. Een **gate** of **expander** maakt zachte
passages zachter; deze verwijdert niet automatisch alle ruis.

Begin bijvoorbeeld met **Compressor (3:1 above −18 dB)** op een spraakfragment.
Luister of zachte woorden verstaanbaar blijven en harde woorden rustiger
klinken. Gebruik Output gain om het resultaat daarna op een passend niveau te
brengen. De piekbegrenzerpreset gebruikt een attack van nul; met een langzamere
attack kunnen korte pieken erdoorheen komen. Er is nog geen vooruitblik.

### Envelope

**Transform → Amplitude → Envelope** tekent een volumeverloop over het fragment.
De positie loopt van 0% aan het begin tot 100% aan het einde. Versterking loopt
van 0% voor stilte tot 200%; 100% is onveranderd. De gekozen kanalen volgen dezelfde lijn.

Klik en sleep punten, of wijzig positie en versterking onder de curve.
Binnenpunten kun je verwijderen. Presets bieden fades, een fade aan beide
kanten en een dip in het midden. Logaritmische interpolatie is alleen mogelijk
als alle versterkingswaarden positief zijn.

Voorbeeld: selecteer een passage met één te luid woord, plaats punten rond dat
woord en maak een dip. Preview helpt de overgang te beoordelen. Dit effect
wordt in de opname geschreven; de cliplijnen in multitrack blijven afzonderlijk
bewerkbaar.

### Normalize

**Transform → Amplitude → Normalize** brengt de hoogste piek naar het gekozen
percentage. Het standaarddoel is 98%. Dit verhoogt of verlaagt het hele fragment
met dezelfde factor; het maakt zachte en harde woorden niet onderling even luid.

**Normalize left / right equally** bewaart de stereobalans. Zonder deze koppeling
krijgt elk kanaal zijn eigen piekniveau. **Remove DC offset before normalizing**
haalt eerst een vaste verschuiving rond de middenlijn weg. Stilte blijft stilte.

Gebruik normaliseren bijvoorbeeld na het mengen of versterken om pieken weer
binnen een passend bereik te krijgen voordat je als PCM exporteert.

### Invert, Reverse en Silence

Deze opdrachten staan direct onder **Transform** en werken meteen:

- **Invert** keert de polariteit om. Het speelt de audio niet achteruit af.
- **Reverse** keert de tijdvolgorde van het fragment om.
- **Silence** maakt het fragment stil en houdt de lengte gelijk.

Gebruik Ctrl+Z om het resultaat terug te draaien. Gebruik Delete wanneer je een
fragment helemaal uit de tijdlijn van een golfvorm wilt verwijderen.

## 5a. EQ en filters

**Transform → Filters** biedt drie manieren om de klank van een golfvorm aan te
passen. Een selectie beperkt de bewerking tot dat fragment. Zonder selectie
wordt de hele opname bewerkt. **Preview** laat de eerste acht seconden van die
keuze horen. **OK** past toe, **Cancel** sluit zonder wijziging en **Ctrl+Z**
maakt de bewerking ongedaan. **F2** herhaalt de laatste instellingen.

### Graphic Equalizer

Tien vaste octaafbanden lopen van 31,5 Hz tot 16 kHz. Sleep een schuif omhoog
om dat gebied te versterken of omlaag om het te verzwakken. Het veld onder de
schuif voert de versterking in dB precies in, van −24 tot +24 dB.

**Flat** zet alles op nul. **Bass lift** versterkt het laag, **Voice presence**
benadrukt spraak en **Gentle smile** versterkt laag en hoog licht. **Reset**
herstelt Flat en zet Output gain op nul. De banden overlappen: de grafiek toont
de gezamenlijke werking, niet alleen de losse schuifstanden. Banden buiten het
bruikbare frequentiebereik van de opname staan uit en worden overgeslagen.

### Parametric Equalizer

Vijf bell-banden werken rond een instelbare middenfrequentie. Een **Low shelf**
past het laag onder zijn overgangsgebied aan; **High shelf** doet dat voor het
hoog. Het vinkje schakelt iedere band afzonderlijk in of uit.

- **Frequency:** middenfrequentie van een bell of het midden van een shelf-overgang.
- **Gain:** versterken of verzwakken, van −24 tot +24 dB.
- **Q:** breedte van een bell; een hogere Q behandelt een smaller gebied.
  Shelves hebben een vaste, gelijkmatig verlopende overgang; hun Q-veld staat uit.

Begin voor een scherpe resonantie met een smalle bell en negatieve Gain. Gebruik
voor een algemene klankaanpassing een bredere bell of shelf en kleine stappen.
**Voice clarity** en **Warmth** bieden begininstellingen. **Flat** of **Reset**
zet alle versterkingen op nul. Bij een lage samplerate staan de hogere banden
aanvankelijk uit; ze kunnen binnen het beschikbare bereik worden ingesteld.

### Filters

- **High-pass:** laat hoog door en verzwakt laag. Remove low rumble begint op 80 Hz.
- **Low-pass:** laat laag door en verzwakt hoog. Soften high frequencies begint op 8 kHz.
- **Band-pass:** laat het gebied rond de middenfrequentie door; een hogere Q maakt
  dat gebied smaller. Telephone band is een brede startinstelling, geen vaste
  combinatie van twee afsnijfrequenties.
- **Notch:** verzwakt een smal gebied rond de gekozen frequentie. De presets
  50 Hz notch en 60 Hz notch behandelen brom op die grondtoon. Eventuele
  boventonen vragen een aanvullende bewerking.

Low-pass en High-pass hebben een Butterworth-helling van **12, 24, 36 of
48 dB/oct**. Bij de afsnijfrequentie bedraagt de verzwakking ongeveer 3 dB.
Een steilere helling snijdt sterker af en kan meer uitslingering geven.
Band-pass en Notch gebruiken **Q** in plaats van de hellingkeuze.
**Reset** herstelt Remove low rumble en Output gain van nul.

### Niveau, grafiek en selecties

**Output gain** past het totale resultaat aan. Sterke EQ-versterking kan boven
0 dBFS uitkomen; verlaag Output gain vóór luisteren of PCM-export. De verwerking
knipt pieken niet automatisch af. De grafiek toont de gezamenlijke frequentie-
respons inclusief Output gain, binnen een weergave van −36 tot +36 dB.

Dezelfde instellingen gelden voor de gekozen kanalen, zonder ze te mengen.
Filtergeheugen loopt door tussen verwerkingsblokken, ook bij lange bestanden.
Iedere bewerking begint bij het begin van de selectie met leeg filtergeheugen
en houdt de bestaande lengte aan. Een heel korte of abrupt begrensde selectie
kan daardoor een hoorbare overgang geven; kies een ruimer fragment of pas het
effect op de hele opname toe. Filters verschuiven de fase en zijn geen
lineairefase-EQ. Cueposities blijven staan; recordermeetgegevens worden niet
opnieuw berekend.

Bij een lange bewerking toont de voortgang een annuleerknop. Annuleren behoudt
de oorspronkelijke golfvorm en Undo-geschiedenis. Voor een multitrackclip open
je eerst een bewerkkopie, pas je het effect toe en kies je Apply Waveform to Clip.
Deze effecten zijn nog geen realtime spooreffecten.

## 5b. Delay, echo en galm

De drie effecten staan onder **Transform → Delay Effects**. Selecteer een
fragment of laat de selectie leeg om de hele golfvorm te bewerken. **Preview**
speelt maximaal de eerste acht seconden van het resultaat, inclusief een
eventuele uitklank. Een instelling wijzigen stopt het voorbeeld. **OK** past
toe als één Undo-stap; **Cancel** laat de opname intact. **Ctrl+Z** draait terug,
**Ctrl+Shift+Z** doet opnieuw en **F2** herhaalt de laatste instellingen.

### Delay — één vertraagde kopie

**Delay (left / mono)** bepaalt de vertraging van 1 tot 2.000 ms. Bij stereo
houdt **Same delay for both channels** de twee tijden gelijk. Schakel het uit
om **Right delay** afzonderlijk te kiezen. Mono gebruikt alleen de eerste tijd.

- **Single delay:** een enkele kopie na 250 ms.
- **Slapback:** een korte herhaling van 80 ms, bijvoorbeeld voor zang of gitaar.
- **Doubling:** 25 ms voor een verdubbelend effect.
- **Stereo widening:** verschillende tijden links en rechts; beschikbaar bij stereo.

Delay bevat één herhaling. Kies Echo voor een reeks afnemende herhalingen.

### Echo — herhalingen met feedback

De tijdvelden werken hetzelfde als bij Delay. **Feedback** voert een deel van
de vertraagde kopie terug voor de volgende herhaling. Nul geeft één herhaling;
een hoger percentage geeft een langer verval, tot maximaal 95%.

**High-frequency damping** maakt volgende herhalingen doffer. De eerste
vertraagde kopie blijft ongewijzigd; demping zit in de terugkoppeling.
**Alternate repeats between left and right** laat herhalingen bij stereo
tussen de kanalen wisselen. Het oorspronkelijke geluid behoudt zijn kanalen.
Met verschillende vertragingstijden duurt iedere kant zijn eigen tijd.

**Repeating echo**, **Warm echo**, **Stereo ping pong** en **Long repeats**
geven begininstellingen. De pingpongpreset is alleen beschikbaar bij stereo.
**Reset** herstelt Repeating echo. Bij veel feedback kunnen herhalingen zich
opstapelen; zet Wet of Output gain lager wanneer het niveau te hoog wordt.

### Reverb — galm

- **Room size:** de afstand tussen reflecties. Een grotere waarde geeft meer
  spreiding in de tijd en een ruimer karakter; de nagalmtijd blijft apart instelbaar.
- **Decay (approx. RT60):** de richttijd waarin de galm ongeveer 60 dB afneemt,
  van 0,1 tot 10 seconden. Het precieze verval hangt ook van demping, frequentie
  en de opname af.
- **Predelay:** tijd vóór de galm, van 0 tot 250 ms. Het oorspronkelijke geluid
  wordt hierdoor niet vertraagd; extra voorvertraging houdt de aanslag duidelijk.
- **High-frequency damping:** hogere waarden laten het hoog eerder uitdoven.
- **Stereo width:** nul geeft dezelfde galm links en rechts; 100% gebruikt de
  volledige stereospreiding. Het oorspronkelijke stereobeeld blijft behouden.
  Het veld is bij mono uitgeschakeld.

**Small room**, **Studio**, **Large hall** en **Long ambient** zijn beginpunten.
**Reset** herstelt Small room. Voor verstaanbare spraak begin je met weinig Wet,
een korte Decay en wat Predelay. Voor een ruimer muzikaal effect kun je Decay
en Wet verhogen. Het is een zelfstandige algoritmische galm, geen exacte
nabootsing van een bepaalde zaal of een ander programma.

### Dry, Wet en uitgangsniveau

**Dry (original)** bepaalt het oorspronkelijke geluid. **Wet (effect)** bepaalt
de vertraagde kopieën of galm. Beide zijn afzonderlijke percentages en worden
bij elkaar opgeteld. Met Dry op nul hoor je alleen het effect; met Wet op nul
blijft alleen het oorspronkelijke geluid over.

**Output gain** regelt de versterking van het totale resultaat, van −24 tot
+24 dB. De effecten begrenzen pieken niet automatisch. Verlaag dit niveau als
de meters rood worden of bij luisteren vervorming optreedt. Het interne signaal
kan boven 0 dBFS komen; verlaag het vóór PCM-export.

### Een uitklank behouden

Standaard blijft de lengte gelijk. Herhalingen of galm na het einde van de
selectie vallen dan buiten het resultaat. Vink **Add effect tail after the
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
Feedback/Decay. Bij extreme echoinstellingen kan de natuurlijke uitklank langer
dan de maximale 60 seconden zijn; de aanwijzing meldt dit.

**Voorbeeld:** selecteer een korte stemopname, kies Echo → Warm echo en luister
met Preview. Vink Add effect tail aan, kies de voorgestelde tijd en bevestig.
Een stemopname van twee seconden met drie seconden uitklank wordt vijf seconden.
Gebruik Ctrl+Z om naar de oorspronkelijke lengte terug te gaan.

Lange opnamen worden in blokken verwerkt met doorlopend effectgeheugen. Een
geannuleerde bewerking laat audio, selectie, metadata en Undo/Redo intact.
Bij een multitrackclip open je eerst een bewerkkopie en plaats je het resultaat
terug met Apply Waveform to Clip. Controleer bij een verlengde clip de overlap
met volgende clips; die schuiven niet automatisch mee. Bestaande volume- en
panlijnen worden bij het terugplaatsen naar de nieuwe cliplengte geschaald.
De effecten zijn nog geen realtime spooreffecten.

## 5c. Ruisreductie en klikverwijdering

Deze effecten staan onder **Transform → Noise Reduction** en werken op een
selectie of, zonder selectie, de hele golfvorm. **Preview** laat maximaal acht
seconden horen. **OK** past toe, **Cancel** sluit zonder wijziging en **Ctrl+Z**
draait terug. **F2** herhaalt de instellingen, inclusief het gebruikte ruisprofiel.

### Een ruisprofiel opnemen

1. Zoek een stukje waarin alleen de ongewenste achtergrond hoorbaar is, zonder
   spraak of muziek. Een halve tot enkele seconden is meestal bruikbaar.
2. Selecteer dat stukje en kies **Capture Noise Profile**. Ook **Capture from
   selection** in het effectvenster kan dit doen. Er verandert nog geen audio.
3. Selecteer vervolgens het fragment dat je wilt schoonmaken, of hef de selectie
   op voor de hele opname. Open **Noise Reduction**.
4. Begin met **Gentle** of **Balanced**, luister met Preview en vergelijk met de
   oorspronkelijke opname door het venster te annuleren.

Een profiel beschrijft het gemiddelde frequentiebeeld van maximaal de eerste
30 seconden van de gekozen ruisselectie. De minimumduur hangt van de samplerate
af en wordt gemeld bij een te korte selectie. Het profiel blijft tijdens deze
appsessie beschikbaar. De samplerate moet overeenkomen. Het aantal kanalen
moet passen bij de gekozen kanalen. Bij Left of Right kan een stereoprofiel
het bijbehorende kanaal leveren; een monoprofilering kan op één kanaal werken.

**Save Profile** bewaart het als `.ssnoise`; **Load Profile** opent zo'n bestand.
Daarmee kun je een profiel later opnieuw gebruiken. Het bevat een ruisspectrum,
geen geluidsopname. Een profiel van een andere opstelling kan minder goed werken.

### Noise Reduction

- **Maximum noise reduction:** de maximale verzwakking in ruisgebieden, 0–36 dB.
  Begin met 6–12 dB; een hogere waarde kan ook zachte details aantasten.
- **Sensitivity:** hoeveel van het profiel als ruis wordt beschouwd. Meer
  gevoeligheid behandelt meer achtergrond, maar kan meer bijgeluiden geven.
- **Smoothing:** maakt de overgang van sterker naar zwakker onderdrukken rustiger.
  Een hoge waarde laat na een duidelijk geluid tijdelijk meer achtergrond door.
- **Link stereo channels:** gebruikt dezelfde verzwakking links en rechts om
  de balans te behouden. Zonder koppeling wordt ieder kanaal apart behandeld.
- **Keep removed noise only:** levert het verwijderde deel op in plaats van het
  schoongemaakte geluid. Luister hiermee of waardevolle spraak of muziek verdwijnt.
  Schakel dit weer uit vóór OK wanneer je de schoongemaakte opname wilt behouden.

Dit werkt vooral bij vrij constante ruis, zoals ventilatie of een gelijkmatige
sis. Het verwijdert geen afzonderlijke stemmen uit een mix en herstelt geen
ontbrekende details. Veranderende achtergrond, te sterke reductie of een profiel
met spraak/muziek kan hoorbare vervorming of een korrelige klank geven. De lengte
en cueposities blijven gelijk. De eerste acht seconden in Preview zijn hetzelfde
als de eerste acht seconden van de volledige bewerking.

### Click Removal

Dit effect zoekt korte, geïsoleerde sprongen die snel naar de omgeving terugkeren
en vervangt ze door een verbinding tussen de omliggende onbeschadigde samples.

- **Threshold multiplier:** een hogere waarde maakt de herkenning terughoudender;
  een lagere waarde vindt meer mogelijke tikken.
- **Minimum jump level:** de minimale sprongsterkte in dBFS. Een lagere waarde
  maakt ook zachtere tikken kandidaat.
- **Maximum click width:** de langste tik die mag worden hersteld, 0,02–2 ms.

De presets **Conservative**, **Small clicks** en **Wider clicks** zijn beginpunten.
Gebruik bij voorkeur een selectie rondom het probleem en luister met Preview.
Slagwerk en scherpe aanslagen kunnen op tikken lijken. Lange kraken, clipping
en beschadigde begin-/eindsamples worden hiermee niet betrouwbaar hersteld.
Behandel zulke plekken afzonderlijk en bewaar eerst een kopie.

Beide effecten werken met begrensde werkbuffers, ook bij lange opnamen. Annuleren
laat audio, selectie en Undo/Redo intact. Voor een multitrackclip open je eerst
een bewerkkopie en kies je na de bewerking Apply Waveform to Clip. Realtime
ruisonderdrukking tijdens opnemen of afspelen is hiermee niet beschikbaar.

## 5d. Tijd en toonhoogte

**Transform → Time/Pitch** bevat Stretch en Pitch Shift. Ze bewerken de selectie
of, zonder selectie, de hele golfvorm. Preview analyseert eerst het volledige
bereik en speelt daarna maximaal acht seconden af. Het voorbeeld is hetzelfde
prefix als bij toepassen. Lange opnamen hebben daardoor ook voor Preview
analysetijd nodig. De voortgang is annuleerbaar; annuleren behoudt de opname.

### Stretch

**New length** kiest de nieuwe lengte als percentage, van 25 tot 400%.
100% houdt de lengte gelijk, 200% maakt de opname tweemaal zo lang en 50%
halveert de speelduur. De toonhoogte blijft behouden. De getoonde tijden helpen
bij het instellen van een passend resultaat.

Met **From … BPM to … BPM** en **Set from tempo** bereken je de lengte op basis
van een bekend begintempo en gewenst eindtempo. Dit is geen automatische
tempodetectie. Van 120 naar 100 BPM wordt de lengte 120%. Een verhouding buiten
het beschikbare bereik wordt gemeld en verandert de instelling niet.

Cuepunten binnen het bewerkte bereik volgen de nieuwe tijdschaal. Audio en
cuepunten na de selectie schuiven mee met het verschil in lengte. De samplerate
van het bestand verandert niet. De selectie omvat na toepassen het resultaat.

### Pitch Shift

**Pitch change** kiest −24 tot +24 halve tonen. +12 is een octaaf omhoog;
−12 is een octaaf omlaag. Een fractie geeft fijnstemming: 0,01 halve toon is
één cent. De speelduur en cueposities blijven behouden.

**Preserve formants** helpt het karakter van zang of spraak te behouden bij een
toonhoogteverschuiving. Vergelijk beide standen bij instrumenten en grote
verschuivingen; het resultaat verschilt per opname.

### Kwaliteit en praktisch gebruik

**Fine** gebruikt de fijnere Rubber Band-engine en is de standaard. **Fast**
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

**OK** bevestigt één Undo-stap, **Cancel** laat de golfvorm intact. Met Ctrl+Z
en Ctrl+Shift+Z kun je terug en opnieuw. **F2** herhaalt dezelfde verhouding of
toonhoogte op een nieuwe selectie. Bewaren als WAV, projectopslag en herstel
houden het bewerkte resultaat vast.

Voor een multitrackclip open je eerst een bewerkkopie en kies je daarna Apply
Waveform to Clip. De cliplengte en bestaande volume-/panlijnen volgen het
nieuwe resultaat; volgende clips schuiven niet automatisch mee. Controleer de
overlap. Dit zijn nog geen realtime tempo- of toonhoogte-effecten op sporen.

## 5e. Vervorming en convolutie

**Transform → Special** bevat Distortion en Convolution. Beide bewerken een
selectie of, zonder selectie, de hele golfvorm. Preview laat de eerste acht
seconden horen. OK bevestigt één Undo-stap; Cancel laat de golfvorm intact.
Ctrl+Z draait terug, Ctrl+Shift+Z doet opnieuw en F2 herhaalt de instellingen.

### Distortion

Kies het gewenste karakter bij **Type**:

- **Soft clip:** rondt sterke uitslagen vloeiend af voor zachte verzadiging.
- **Hard clip:** snijdt uitslagen op de gekozen grens af voor scherpere vervorming.
- **Wavefold:** vouwt uitslagen buiten de grens terug en geeft extra boventonen.
- **Bit crush:** rondt amplitudes af op de gekozen bitdiepte, van 2 tot 16 bits.

**Drive** versterkt het signaal vóór de vervorming, 0–36 dB. **Ceiling** bepaalt
de amplitudegrens van het vervormde deel, 10–100%. **Effect mix** mengt dit deel
met de oorspronkelijke opname; nul geeft alleen de oorspronkelijke audio.
**Output gain** regelt het totale resultaat met −24 tot +24 dB. De Ceiling
begrenst dus niet automatisch het droge deel of het uiteindelijke uitgangsniveau.

De presets **Soft warmth**, **Crunch**, **Wavefold** en **Bit crush** zijn
beginpunten. Vergelijk met de oorspronkelijke opname en voorkom te hoge pieken.
De lengte en cueposities blijven gelijk. Stilte blijft stil.

**High quality** gebruikt oversampling om aliasing te verminderen. Bij gangbare
samplerates is dit viermaal; bij hogere rates wordt de factor aangepast. Dit
verwerkt ook voor Preview de hele selectie en kan langer duren. Zonder deze
optie is de verwerking sneller en kan een ruwere digitale klank ontstaan.
Bit crush gebruikt in zijn preset standaard geen oversampling.

### Convolution

Een impulsrespons beschrijft een filter, luidspreker, kabinet of akoestische
reactie. Convolution past zo'n reactie op de opname toe. Er zijn geen externe
plug-ins nodig; de respons zelf kies je als WAV-bestand.

1. Open Convolution en klik **Choose Impulse Response**.
2. Kies een geschikte WAV-respons. De naam, duur en kanalen verschijnen in het venster.
3. Stel **Dry** en **Wet** in en luister met Preview.
4. Kies eventueel **Keep full response tail** en bevestig met OK.

**Dry** regelt de oorspronkelijke opname; **Wet** regelt het geconvolveerde deel.
Beide worden opgeteld. Voor een zuiver filtereffect kun je Dry op nul en Wet op
100% zetten. **Output gain** regelt het totale niveau. Een respons kan frequenties
sterk versterken; verlaag het niveau als de uitvoermeters rood worden.

**Normalize impulse energy** schaalt de respons op zijn energie, met dezelfde
factor voor beide responskanalen. Schakel dit uit als de oorspronkelijke schaal
van een meetrespons behouden moet blijven. Het garandeert geen piekbegrenzing.

Een monorespons werkt op mono of op beide kanalen van stereo. Een stereorespons
werkt per kanaal op een stereogolfvorm; hij maakt van een monogolfvorm geen stereo
en bevat geen complete matrixroutering tussen kanalen. Een afwijkende samplerate
van de respons wordt automatisch omgezet. Bij Left of Right wordt het
bijbehorende kanaal van een stereorespons gebruikt. Een uitklank toevoegen
vraagt bij stereo Both.

Zonder **Keep full response tail** blijft de oorspronkelijke lengte gelijk.
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
Annuleren laat audio, selectie en Undo/Redo intact. Voor multitrack gebruik je een
bewerkclipkopie en Apply Waveform to Clip. Volgende clips verschuiven niet vanzelf
bij een langere clip; volume-/panlijnen volgen bij terugplaatsen de cliplengte.
Realtime spooreffecten en externe plug-ins blijven afzonderlijke uitbreidingen.

## 6. Tonen en stilte maken

**Generate → Tones** maakt een sinustoon. Stel **Duration** in seconden,
**Frequency** in Hz en **Amplitude** in procenten in. Zonder selectie wordt de
toon bij de cursor ingevoegd; met een selectie vervangt hij dat fragment. De
opgegeven duur bepaalt de lengte van het nieuwe geluid.

Een toon van bijvoorbeeld 440 Hz op een bescheiden niveau is bruikbaar om een
bewerking te proberen. Begin bij luisteren met een laag afspeelvolume.

**Generate → Silence** voegt een opgegeven duur aan stilte in of vervangt de
selectie door die hoeveelheid stilte. Dit verschilt van Transform → Silence,
dat de bestaande fragmentlengte altijd behoudt.

## 7. Frequenties analyseren

Selecteer een fragment en kies **Analyze → Frequency Analysis** of **Alt+Z**.
Zonder selectie wordt de opname als uitgangspunt genomen. De grafiek toont
frequenties van laag naar hoog en het bijbehorende niveau. Onderaan staat de
sterkste gevonden frequentie met het niveau in dBFS.

De analyse gebruikt bij lange fragmenten een begrensd deel rond het midden van
het gekozen bereik. Ze is een hulpmiddel voor tonen en spectrale verhoudingen,
geen doorlopende spectrummeter. Selecteer een korter fragment om een bepaalde
klank of toon te onderzoeken. Sluiten verandert de audio niet.

## 8. Meerdere sporen combineren

### Een sessie opbouwen

1. Kies **File → New Multitrack Session** en stel rate en aantal sporen in.
2. Gebruik **Import WAV** of **File → Import WAV into Multitrack**. Je kunt ook
   WAV-bestanden vanuit de bestandsbeheerder op de tijdlijn slepen.
3. Sleep clips in **Move Clips** naar de gewenste tijd en het gewenste spoor.
4. Stel volume, pan, Mute en Solo per spoor in.
5. Sla het project tussentijds op en luister naar de combinatie.
6. Kies **Mix Down** voor een eindmix.

Verschillende samplerates worden bij import naar de sessierate omgezet.
Met **Window → Insert Current Waveform in Multitrack** voeg je de open golfvorm
toe. Meerdere tegelijk geïmporteerde bestanden worden op opeenvolgende sporen
geplaatst. **+ Track** en **− Track** voegen een spoor toe of verwijderen het
geselecteerde spoor. Een verwijderd spoor met clips kun je met Undo herstellen.

### Clips en sporen aanpassen

Klik een clip om haar te kiezen. Sleep het midden om te verplaatsen en de
linker- of rechterrand om te trimmen. Trimmen bewaart de bron: opnieuw verlengen
kan eerder verborgen audio terughalen. In lege ruimte kun je een tijdbereik
selecteren voor afspelen.

**Duplicate Clip** of **Ctrl+D** maakt een kopie die dezelfde bron gebruikt.
**Remove Clip** of Delete verwijdert de geselecteerde clip wanneer **Move Clips**
actief is. De bronopname op schijf blijft behouden. Rechtsklikken op een clip
opent dezelfde opdrachten.

**Clip Properties** opent de eigenschappen. Daar stel je naam, tijdlijnpositie,
bronbegin en -einde, volume, pan, fades en clip-Mute precies in. Tijdwaarden zijn
in seconden. Fades moeten samen binnen de cliplengte passen. Annuleren laat de
clip ongewijzigd.

De spoornaam is bewerkbaar. **Mute** zet een spoor stil; **Solo** laat alleen
gekozen solosporen horen. Mute blijft doorslaggevend. Pan −100 is links, 0 is
midden en +100 is rechts. Bij een stereobron verzwakt pan één kant; het kopieert
het andere kanaal niet naar die kant.

### Volume Line en Pan Line

Kies boven de tijdlijn **Volume Line** of **Pan Line** en klik in een clip om
punten te plaatsen. Sleep de punten om tijd en waarde te wijzigen. De
volumelijn loopt van stilte onderaan via 100% in het midden tot 200% bovenaan.
Bij de panlijn is boven rechts, midden neutraal en onder links.

Rechtsklikken of dubbelklikken op een punt opent precieze invoer. Hier zijn de
puntposities in frames. **Remove Point** of Delete verwijdert alleen het
geselecteerde lijnpunt. **Reset Line** maakt de lijn weer neutraal. Esc annuleert
een lopende sleepbeweging. **Move Clips** keert terug naar verplaatsen en trimmen.

De volumelijn werkt boven op spoorvolume, clipvolume en fades. De panlijn werkt
boven op spoor- en clippan; zet die gewone paninstellingen in het midden voor
een volledige beweging van links naar rechts. Punten bewegen met de bronaudio
mee bij verplaatsen en blijven bij trimmen bewaard. De lijnen worden met het
project opgeslagen en werken door in afspelen en mixdown.

### Een effect op een clip toepassen

Dubbelklik een clip of kies **Edit Copy in Waveform** via de rechtermuisknop.
De kopie opent in de golfvormeditor. Pas daar het effect toe. Kies daarna
**Window → Apply Waveform to Clip** om het resultaat terug te plaatsen.

Gewoon terugschakelen naar multitrack past de kopie niet toe. Sluiten en
verwerpen laat de oorspronkelijke clip intact. Na toepassen kunnen de oude
audio en de lijnen met Undo in de sessie worden hersteld. Een veranderde
samplerate wordt bij terugplaatsen naar de sessierate omgezet.

### Opslaan en mixdown

**Save Session** bewaart het bewerkbare project. **Mix Down Session** of
**Mix Down** maakt één WAV van de hele sessie. Een tijdbereikselectie bepaalt
hierbij niet de exportlengte. Controleer Mute, Solo en de niveaus voordat je
exporteert: die instellingen werken door in het eindresultaat.

Een bevestigde wijziging stopt het afspelen; de mix wordt bij opnieuw starten
opnieuw berekend. Effecten reageren nog niet als realtime spooreffecten tijdens
lopend afspelen.

## 9. Een andere samplerate kiezen

**Edit → Convert Sample Rate** zet de hele golfvorm om. Kies het gewenste aantal
Hz en bevestig. Toonhoogte en speelduur blijven behouden, met afronding op hele
uitvoerframes. Zeer korte fragmenten houden minimaal één frame. Selectie en
cursor volgen dezelfde tijden. **Ctrl+Z** herstelt zowel de vorige audio als de
vorige rate.

Deze opdracht verandert de opname. Automatische omzetting voor een uitvoerapparaat
verandert alleen het afgespeelde signaal en laat de golfvorm zelf intact.

## 10. Favorieten, vensters en hulp

**Favorites** geeft snel toegang tot herhalen, normaliseren en fades. Eigen
favorietenlijsten kunnen nog niet worden samengesteld. **Window** wisselt
tussen beide weergaven en bevat de opdrachten om een golfvorm in te voegen of
naar een clip terug te plaatsen.

**Help → About** toont de versie, maker, licentie en website. De handleiding
blijft als afzonderlijk venster beschikbaar, zodat je de stappen in de editor
kunt volgen.

## 11. Sneltoetsen

| Toets | Functie |
| --- | --- |
| Ctrl+N / Ctrl+O | Nieuwe golfvorm of sessie / openen in de huidige weergave |
| Ctrl+S / Ctrl+Shift+S | Opslaan / opslaan als in de huidige weergave |
| Ctrl+Alt+N / Ctrl+Alt+O / Ctrl+Alt+S | Nieuwe sessie / sessie openen / sessie opslaan |
| Ctrl+W / Ctrl+Q | Huidige golfvorm of sessie sluiten / toepassing sluiten |
| Ctrl+Z / Ctrl+Shift+Z | Undo / Redo |
| Ctrl+X / Ctrl+C / Ctrl+V | Knippen / kopiëren / plakken in de golfvorm |
| Ctrl+M / Ctrl+T | Mix Paste / selectie behouden |
| Delete | Selectie, clip of lijnpunt verwijderen, afhankelijk van de actieve bewerking |
| Ctrl+A / F4 | Hele duur in gekozen kanalen / selectie naar nuldoorgangen aanpassen |
| Alt+B / Alt+L / Alt+R | Beide kanalen / links / rechts kiezen |
| Spatie / P / Esc | Afspelen of stoppen / pauzeren of hervatten / stoppen |
| R | Opname instellen; tijdens opnemen stoppen en de take behouden |
| Home / End | Naar begin / einde |
| + / − | Inzoomen / uitzoomen |
| Ctrl+0 / Ctrl+Shift+A | Hele opname tonen / selectie vullen |
| Ctrl+D | Clip dupliceren in multitrack |
| Tab / F11 | Golfvorm en multitrack wisselen / volledig scherm |
| F1 / F2 / Alt+Z | Handleiding / laatste effect herhalen / frequentieanalyse |

Bij tekstinvoer horen gewone typetoetsen bij het actieve veld. Klik weer in de
golfvorm of tijdlijn wanneer je daar een sneltoets wilt gebruiken.

## 12. Problemen en work in progress

- **Geen ingangsniveau:** controleer Input, het gekozen kanaal en het microfoonvolume
  in de geluidsinstellingen. Start een nieuwe take na het aansluiten van een apparaat.
- **Geen geluid:** controleer Audio Hardware, systeemvolume, Mute en Solo.
  Kies bij een verdwenen apparaat een beschikbare uitgang en start opnieuw.
- **Vervorming of rode pieken:** verlaag volume of versterking; opgetelde clips
  en Mix Paste kunnen samen boven het uitvoerniveau komen.
- **Plakken lukt niet:** controleer of bron en doel beide mono of beide stereo zijn.
- **Een effect is grijs:** open een golfvorm of een bewerkkopie; Channel Mixer
  vereist stereo. Stretch en bewerkingen die de duur veranderen vragen Both.
  De overige effecten vereisen een geopende golfvorm of bewerkkopie.
- **Lijnpunten in plaats van clips verplaatsen:** kies Move Clips.
- **Onvoldoende werkruimte:** maak schijfruimte vrij voor bronkopieën, resultaten
  en Undo. Verwijder geen werkbestanden terwijl SoundSausage actief is.
- **Een herstelkopie ontbreekt of is beschadigd:** de oorspronkelijke bestanden
  blijven beschikbaar. Verwijder de betreffende kopie alleen wanneer je die niet
  meer wilt bewaren.

Gelijktijdig opnemen en afspelen, een markereditor en realtime spooreffecten zijn nog in ontwikkeling.
Externe plug-ins en uitgebreidere sessiecompatibiliteit volgen later. Deze uitbreidingen zijn nog niet beschikbaar.

Bewaar een project voordat je de toepassing verlaat. De actuele voortgang en
nieuwe versies staan op de [SoundSausage-website](https://github.com/rene-timmermans/SoundSausage).
