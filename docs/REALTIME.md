# Spooreffecten, VST3 en opnemen met begeleiding

## Een effectketen op een spoor

Open een multitracksessie en klik op **FX** naast de spoornaam, of kies
**Transform → Track Effects** voor het gekozen spoor. Kies een effect en druk
op **Add**. Het effectvenster gebruikt dezelfde instellingen en presets als de
golfvormeditor. **OK** voegt het effect toe; **Apply** past de instelling toe
terwijl het venster openblijft. De oorspronkelijke audio blijft behouden.

De keten ondersteunt Amplify, Channel Mixer, Dynamics, Graphic EQ, Parametric EQ,
Filters, Delay, Echo, Reverb, Invert en VST3-effecten. Een spoor heeft maximaal
zestien effecten. Een monobron wordt eerst naar stereo gekopieerd. Clipvolume,
panlijnen en fades werken vóór de spoorketen; spoorvolume en spoorpan erna.

- Dubbelklik op een effect, of kies **Edit**, om de instellingen te wijzigen.
- **Up / Down** verplaatst het effect. De volgorde kan het geluid veranderen.
- Het vinkje schakelt een effect tijdelijk uit. **Remove** verwijdert het.
- **Ctrl+Z / Ctrl+Shift+Z** maakt een wijziging ongedaan of voert haar opnieuw uit.
- **Tail after last clip** voegt 0–60 seconden toe om delay of galm te laten
  uitsterven. Zonder extra tijd eindigt het spoor op de laatste clipgrens;
  een langer ander spoor kan de bestaande uitklank nog laten horen.

De keten werkt tijdens afspelen en komt ook in Mix Down terecht. Volume, pan,
mute, solo en effectinstellingen kunnen tijdens luisteren veranderen. **Apply**
bevestigt een effectinstelling. Al naar het audioapparaat gestuurde audio speelt
nog met de vorige instelling. Bij opnieuw starten, zoeken of opnieuw inschakelen
begint het effectgeheugen leeg. Een gewijzigde interne effectinstelling kan de
uitklank opnieuw beginnen. Een VST3-parameterwijziging houdt dezelfde instantie.

Amplify gebruikt vaste versterking per kanaal; voor een verloop in de tijd
gebruik je de **Volume Line** van een clip. Normalize, ruisreductie, klikherstel,
Stretch, Pitch Shift, Distortion en Convolution blijven golfvormbewerkingen via
**Edit Copy in Waveform**. Een realtime keten verandert de bronbestanden niet.

## VST3-effecten toevoegen

1. Installeer een **64-bit Linux VST3-effect** en zoek de map met uitgang
   `.vst3`. Gebruik de Linux-uitgave van de maker.
2. Kies **VST3 Plug-in → Add** in Track Effects en klik **Add VST3 Bundle**.
3. Kies de bundelmap. Meerdere effecten uit dezelfde bundel worden afzonderlijk
   beschikbaar in de keuzelijst.
4. Kies het effect. Zoek de parameter op naam en wijzig de waarde. **Apply**
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

## Opnemen terwijl andere sporen spelen

1. Zet de begeleiding op één of meer sporen.
2. Kies een ander spoor en plaats de cursor waar de nieuwe take moet beginnen.
3. Druk **R**, kies de ingang en **New clip on…** als bestemming.
4. Vink **Play existing tracks while recording** aan. De bestaande sporen,
   inclusief hun effecten, spelen vanaf de cursor terwijl de nieuwe take wordt
   vastgelegd. De microfoon zelf wordt niet door de luidsprekers teruggespeeld.
5. **P** pauzeert beide; opnieuw **P** hervat beide. **Stop**, **Esc**, **Spatie**
   of opnieuw **R** stopt de begeleiding en bewaart de take als één Undo-stap.

Aan het einde van de begeleiding kan de opname doorgaan. Een opname met een
maximale duur stopt ook de begeleiding. **Discard Recording** verwijdert alleen
de nieuwe take. Gaat een apparaat of plug-in verloren, dan blijven de reeds
opgenomen samples behouden. Bestanden en sporen wijzigen tijdens opnemen is
vergrendeld. Voor een golfvormopname blijft de afzonderlijke opnamebediening gelden.

### De opnamepositie afstellen

De app koppelt de startpositie aan de afspeelklok en de vastgelegde invoerframes.
De fysieke in-/uitvoerroute kan extra vertraging hebben. Met **Recording position
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

## Nieuwe projecten bewaren en heropenen

**Save Session / Save Session As** bewaart de gebruikte audio, clips, lijnen,
spoorketens, volgorde, bypass, uitklanktijden en VST3-instellingen. **Open Session**
herstelt die bewerkbare sessie. **Mix Down Session** bewaart één WAV met dezelfde
spoorketens en de ingestelde uitklank. Het project blijft nodig om afzonderlijke
sporen verder te veranderen.

Nieuwe projecten gebruiken de bijgewerkte projectversie. Eerdere
SoundSausage-projectversies blijven te openen. Oudere appversies kunnen de nieuwe
spoorketens niet lezen; gebruik versie 0.15.0 of nieuwer om ze te heropenen.
Herstel na onverwacht afsluiten bewaart de ketens en plug-ininstellingen eveneens.
Een ontbrekende externe plug-in verhindert het herstellen van de bronopnamen niet.
