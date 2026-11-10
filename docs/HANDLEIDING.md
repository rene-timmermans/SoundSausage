# SoundSausage — handleiding

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Deze handleiding beschrijft de beschikbare functies van versie 0.6.1. De menunamen
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

Extra WAV-informatie, zoals markers en tekst, wordt nog niet bij elke export
bewaard. Als zulke gegevens aanwezig zijn, vraagt het programma eerst om een
keuze voordat ze bij opslaan worden weggelaten.

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

## 4. Selecteren en de golfvorm bewerken

Klik in de golfvorm om de cursor te plaatsen. Sleep met de linkermuisknop om een
fragment te selecteren. **Shift+klik** breidt de selectie vanaf het bestaande
begin uit. **Ctrl+A** selecteert alles.

**Edit → Set Selection** voert begin en einde precies in. Deze velden gebruiken
frames: bij 44.100 Hz zijn 44.100 frames één seconde. **F4** verplaatst de grenzen
van een selectie naar binnen, naar nuldoorgangen in het eerste kanaal. Dat kan
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

Plakken zet de samplerate zo nodig om. Het klembord blijft ongewijzigd. Het
aantal kanalen moet voor plakken nog wel gelijk zijn: mono en stereo worden
hierbij niet automatisch onderling omgezet. Mix Paste kan luider uitvallen
doordat twee signalen worden opgeteld.

## 5. Effecten toepassen

Een golfvormeffect werkt op de selectie. Zonder selectie wordt de hele opname
bewerkt. De opdrachten staan onder **Transform**. Voor effecten op een
multitrackclip gebruik je eerst **Edit Copy in Waveform**; verderop staat hoe je
het resultaat terugplaatst.

In de Amplitude-vensters speelt **Preview** de eerste acht seconden van het
resultaat zonder de opname te veranderen. Opnieuw klikken stopt het voorbeeld.
Een instelling wijzigen of het venster sluiten stopt het ook. **OK** past toe;
**Cancel** laat de opname zoals ze was. **Ctrl+Z** draait de toepassing terug.

**F2** of **Edit → Repeat Last Command** herhaalt het laatste golfvormeffect met
dezelfde instellingen op de nieuwe selectie. Controleer het geselecteerde
bereik voordat je herhaalt.

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
van 0% voor stilte tot 200%; 100% is onveranderd. Beide kanalen volgen dezelfde lijn.

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
| Ctrl+A / F4 | Alles selecteren / selectie naar nuldoorgangen aanpassen |
| Spatie / P / Esc | Afspelen of stoppen / pauzeren of hervatten / stoppen |
| Home / End | Naar begin / einde |
| + / − | Inzoomen / uitzoomen |
| Ctrl+0 / Ctrl+Shift+A | Hele opname tonen / selectie vullen |
| Ctrl+D | Clip dupliceren in multitrack |
| Tab / F11 | Golfvorm en multitrack wisselen / volledig scherm |
| F1 / F2 / Alt+Z | Handleiding / laatste effect herhalen / frequentieanalyse |

Bij tekstinvoer horen gewone typetoetsen bij het actieve veld. Klik weer in de
golfvorm of tijdlijn wanneer je daar een sneltoets wilt gebruiken.

## 12. Problemen en work in progress

- **Geen geluid:** controleer Audio Hardware, systeemvolume, Mute en Solo.
  Kies bij een verdwenen apparaat een beschikbare uitgang en start opnieuw.
- **Vervorming of rode pieken:** verlaag volume of versterking; opgetelde clips
  en Mix Paste kunnen samen boven het uitvoerniveau komen.
- **Plakken lukt niet:** controleer of bron en doel beide mono of beide stereo zijn.
- **Een effect is grijs:** open een golfvorm of een bewerkkopie; Channel Mixer
  vereist stereo. Een aantal andere effectgroepen is nog niet gebouwd.
- **Lijnpunten in plaats van clips verplaatsen:** kies Move Clips.
- **Een bestand is te groot:** er geldt nog een limiet van 128 MiB gedecodeerde
  audio. Dat is een geheugenmaat en kan afwijken van de bestandsgrootte op schijf.

Opnemen, langere bestanden met verwerking vanaf schijf, crashherstel, uitgebreid
behoud van bestandsinformatie en realtime spooreffecten zijn nog in ontwikkeling.
Ook EQ/filters, delay/galm, ruisreductie, tijd-/toonhoogtebewerking en externe
plug-ins volgen later. Uitgeschakelde opdrachten bieden daarvoor nog geen werking.

Bewaar een project voordat je de toepassing verlaat. De actuele voortgang en
nieuwe versies staan op de [SoundSausage-website](https://github.com/rene-timmermans/SoundSausage).
