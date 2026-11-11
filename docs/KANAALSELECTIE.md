# Links, rechts en stereo selecteren

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

## Een effect op één kanaal

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

## Kopiëren en bewaren

Copy en Save Selection leveren bij Left of Right mono-audio uit dat kanaal.
Save en Save As blijven de volledige stereogolfvorm bewaren. Je kunt mono-audio
in één stereokanaal plakken wanneer die precies de geselecteerde duur vervangt.
Mix Paste kan binnen de bestaande opnameduur op één kanaal mengen. Invoegen of
anders verlengen vereist Both. De niet-gekozen samples blijven exact behouden.

Opnemen in een bestaande stereogolfvorm vereist Both. Bij een enkel gekozen
kanaal kan Record een nieuwe golfvorm maken. De kanaalkeuze is tijdens opnemen
vergrendeld. Undo/Redo en herstel bewaren de keuze; oudere herstelkopieën openen
met beide kanalen gekozen. Afspelen blijft in de bestaande stereocontext.

## Zoomen en functie-iconen

**Zoom Full** toont de gehele opname; het vergrootglas heeft markeringen naar
de buitenste grenzen. **Zoom to Selection** vult het beeld met het geselecteerde
tijdvak; het vergrootglas bevat een gemarkeerd selectievak. De knoppen hebben
verschillende iconen en aanwijzingen bij de muis.

De golfvorm blijft bij tussenliggende zoomniveaus doorlopend. Dichtbij worden
afzonderlijke samples met elkaar verbonden. Verder uitgezoomd toont de app de
minimale en maximale uitslagen per schermkolom, met behoud van pieken. Dit werkt
ook op multitrackclips en verandert de geluidsdata niet. Functies in de menu's
hebben eigen iconen die het Linux-palet en de accentkleur volgen.
