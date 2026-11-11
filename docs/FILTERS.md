# EQ en filters

**Transform → Filters** biedt drie manieren om de klank van een golfvorm aan te
passen. Een selectie beperkt de bewerking tot dat fragment. Zonder selectie
wordt de hele opname bewerkt. **Preview** laat de eerste acht seconden van die
keuze horen. **OK** past toe, **Cancel** sluit zonder wijziging en **Ctrl+Z**
maakt de bewerking ongedaan. **F2** herhaalt de laatste instellingen.

## Graphic Equalizer

Tien vaste octaafbanden lopen van 31,5 Hz tot 16 kHz. Sleep een schuif omhoog
om dat gebied te versterken of omlaag om het te verzwakken. Het veld onder de
schuif voert de versterking in dB precies in, van −24 tot +24 dB.

**Flat** zet alles op nul. **Bass lift** versterkt het laag, **Voice presence**
benadrukt spraak en **Gentle smile** versterkt laag en hoog licht. **Reset**
herstelt Flat en zet Output gain op nul. De banden overlappen: de grafiek toont
de gezamenlijke werking, niet alleen de losse schuifstanden. Banden buiten het
bruikbare frequentiebereik van de opname staan uit en worden overgeslagen.

## Parametric Equalizer

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

## Filters

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

## Niveau, grafiek en selecties

**Output gain** past het totale resultaat aan. Sterke EQ-versterking kan boven
0 dBFS uitkomen; verlaag Output gain vóór luisteren of PCM-export. De verwerking
knipt pieken niet automatisch af. De grafiek toont de gezamenlijke frequentie-
respons inclusief Output gain, binnen een weergave van −36 tot +36 dB.

Dezelfde instellingen gelden voor links en rechts, zonder kanalen te mengen.
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
