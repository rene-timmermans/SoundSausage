# Delay, echo en galm

De drie effecten staan onder **Transform → Delay Effects**. Selecteer een
fragment of laat de selectie leeg om de hele golfvorm te bewerken. **Preview**
speelt maximaal de eerste acht seconden van het resultaat, inclusief een
eventuele uitklank. Een instelling wijzigen stopt het voorbeeld. **OK** past
toe als één Undo-stap; **Cancel** laat de opname intact. **Ctrl+Z** draait terug,
**Ctrl+Shift+Z** doet opnieuw en **F2** herhaalt de laatste instellingen.

## Delay — één vertraagde kopie

**Delay (left / mono)** bepaalt de vertraging van 1 tot 2.000 ms. Bij stereo
houdt **Same delay for both channels** de twee tijden gelijk. Schakel het uit
om **Right delay** afzonderlijk te kiezen. Mono gebruikt alleen de eerste tijd.

- **Single delay:** een enkele kopie na 250 ms.
- **Slapback:** een korte herhaling van 80 ms, bijvoorbeeld voor zang of gitaar.
- **Doubling:** 25 ms voor een verdubbelend effect.
- **Stereo widening:** verschillende tijden links en rechts; beschikbaar bij stereo.

Delay bevat één herhaling. Kies Echo voor een reeks afnemende herhalingen.

## Echo — herhalingen met feedback

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

## Reverb — galm

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

## Dry, Wet en uitgangsniveau

**Dry (original)** bepaalt het oorspronkelijke geluid. **Wet (effect)** bepaalt
de vertraagde kopieën of galm. Beide zijn afzonderlijke percentages en worden
bij elkaar opgeteld. Met Dry op nul hoor je alleen het effect; met Wet op nul
blijft alleen het oorspronkelijke geluid over.

**Output gain** regelt de versterking van het totale resultaat, van −24 tot
+24 dB. De effecten begrenzen pieken niet automatisch. Verlaag dit niveau als
de meters rood worden of bij luisteren vervorming optreedt. Het interne signaal
kan boven 0 dBFS komen; verlaag het vóór PCM-export.

## Een uitklank behouden

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
