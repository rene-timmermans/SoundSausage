# Tijd en toonhoogte

**Transform → Time/Pitch** bevat Stretch en Pitch Shift. Ze bewerken de selectie
of, zonder selectie, de hele golfvorm. Preview analyseert eerst het volledige
bereik en speelt daarna maximaal acht seconden af. Het voorbeeld is hetzelfde
prefix als bij toepassen. Lange opnamen hebben daardoor ook voor Preview
analysetijd nodig. De voortgang is annuleerbaar; annuleren behoudt de opname.

## Stretch

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

## Pitch Shift

**Pitch change** kiest −24 tot +24 halve tonen. +12 is een octaaf omhoog;
−12 is een octaaf omlaag. Een fractie geeft fijnstemming: 0,01 halve toon is
één cent. De speelduur en cueposities blijven behouden.

**Preserve formants** helpt het karakter van zang of spraak te behouden bij een
toonhoogteverschuiving. Vergelijk beide standen bij instrumenten en grote
verschuivingen; het resultaat verschilt per opname.

## Kwaliteit en praktisch gebruik

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
