# Lange opnamen, annuleren en herstel

Vanaf 0.7.0 gebruikt SoundSausage kleine audiobuffers in het werkgeheugen en
grotere buffers in een eigen werkmap op schijf. De eerdere grens van 128 MiB
vervalt. Openen, bewerken, samplerates omzetten, afspelen, golfvormweergave,
multitrack, projecten en export verwerken audio in blokken.

## Werkruimte

De werkmap staat onder `$XDG_DATA_HOME/SoundSausage/work`, of standaard onder
`~/.local/share/SoundSausage/work`. De map bevat eigen audiokopieën; de oorspronkelijke
opname blijft behouden totdat die expliciet wordt opgeslagen. Er moet voldoende
vrije ruimte zijn voor de bron, het nieuwe resultaat en bewaarde Undo-stappen.
Een project openen heeft tijdelijk extra schijfruimte nodig voor het uitpakken
van ingebedde audio. Mixdowns en samplerateconversie voor een uitvoerapparaat
kunnen eveneens eerst een resultaat op schijf voorbereiden.

Audiobuffers reserveren hun schijfruimte voordat ze worden beschreven. Bij
ruimtegebrek verschijnt een foutmelding; de bestaande documentstand blijft
beschikbaar. Undo bewaart maximaal vijftig bewerkingen. Grote buffers delen
ongewijzigde delen; bewerkte resultaten vragen extra schijfruimte. Voor kleine
buffers blijft het geheugenbudget voor de geschiedenis 256 MiB.

## Voortgang en annuleren

Bij langere opdrachten verschijnt voortgang met **Annuleren**. Analyse en
verwerking kunnen afzonderlijke voortgangsstappen hebben. Normalize meet eerst
het gehele bereik; een Preview speelt daarna maximaal acht seconden af.
Fades en envelopes gebruiken de volledige selectieduur, Dynamics houdt zijn
detectorstaat tussen blokken vast en samplerateconversie behoudt zijn filterstaat.

Een geannuleerde bewerking wijzigt audio, selectie, Undo/Redo en het laatst
herhaalbare effect niet. Een geannuleerde opslag laat het bestaande doelbestand
intact. Een afgerond effect blijft één Undo-stap, ongeacht de bestandslengte.

## Herstellen na onverwacht afsluiten

Na bevestigde wijzigingen legt SoundSausage de actuele golfvorm en sessie vast
in een aparte herstelkopie. Selectie- en cursorwijzigingen volgen binnen ongeveer
een seconde. Na onverwacht afsluiten verschijnt bij de volgende start een keuze:

- **Herstellen:** open de laatst vastgelegde stand, inclusief beide weergaven,
  clipinstellingen, lijnen en ondersteunde metadata.
- **Verwijderen:** verwijder deze herstelkopie.
- **Later:** behoud de kopie voor een volgende start of **File → Recover Work**.

Andere actieve appinstanties worden overgeslagen. Herstel schrijft geen
bronbestanden terug. Na herstel begint Undo opnieuw; de opname en sessie staan
wel op hun herstelde bewerkingsstand. Gewoon opslaan blijft nodig. Bevestigd
sluiten of alle wijzigingen opslaan ruimt de eigen herstelkopie op. Oude,
ongebruikte werkbuffers worden bij een volgende start opgeruimd.

Wanneer een herstelkopie niet kan worden bijgewerkt, meldt de statusbalk dit.
De laatste geslaagde kopie blijft bestaan. Herstel is geen vervanging voor een
backup en garandeert niet dat de laatste bewerking bij stroomuitval al op schijf
stond. Herstelinformatie is begrensd tot 64 MiB, los van de audiobuffers.

## Bestandsinformatie

WAV bewaart extra informatie naast de audio, tot samen 16 MiB. Tekstvelden en
andere extra velden blijven behouden. Cuepunten en bijbehorende labels volgen
knippen, invoegen, trimmen, omkeren en samplerateconversie; Undo herstelt ze.
Plakken neemt cuepunten en labels mee met nieuwe identifiers, zonder de titel
van het doelbestand te vervangen. Samplerloops en de tijdreferentie in Broadcast
Wave worden aangepast bij trimmen en samplerateconversie. Selectie-export neemt
alleen de cuepunten en loops binnen het fragment mee.

Andere bijzondere, positieafhankelijke of afgeleide velden worden letterlijk
bewaard; bijvoorbeeld eigen meetgegevens van een recorder worden na een effect
niet opnieuw berekend. Er is nog geen markereditor. Bestanden met meer dan
16 MiB metadata worden bij openen geweigerd. Als extra informatie niet voor
export beschikbaar is, vraagt de app eerst om een keuze om door te gaan.
Een multitrackproject bewaart bronmetadata; een WAV-eindmix krijgt geen
samengevoegde markers of tags uit alle sporen. Grote WAV-export gebruikt RF64
wanneer de gewone RIFF-bestandsgrens wordt overschreden.
