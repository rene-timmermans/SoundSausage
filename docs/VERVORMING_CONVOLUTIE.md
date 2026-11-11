# Vervorming en convolutie

**Transform → Special** bevat Distortion en Convolution. Beide bewerken een
selectie of, zonder selectie, de hele golfvorm. Preview laat de eerste acht
seconden horen. OK bevestigt één Undo-stap; Cancel laat de golfvorm intact.
Ctrl+Z draait terug, Ctrl+Shift+Z doet opnieuw en F2 herhaalt de instellingen.

## Distortion

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

## Convolution

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
