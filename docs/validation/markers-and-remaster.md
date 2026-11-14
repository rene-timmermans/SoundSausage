# Markeringen en Remaster — 0.26.0

De markereditor en Remaster hebben geen nieuw DSP-ABI of nieuwe afhankelijkheid
nodig. De DSP-ABI blijft 7. Projectformaat 6 en herstelversie 3 bewaren nu ook
globale sessiemetadata; de lezers blijven oudere versies ondersteunen.

## Markeringen

De RIFF-cue/adtl-structuur volgt de
[IBM/Microsoft-specificatie](https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Docs/riffmci.pdf).
MP3-hoofdstukken en inhoudsopgaven volgen het
[ID3-hoofdstukaddendum](https://id3.org/id3v2-chapters-1.0).
De gerichte backendproeven controleren CRUD, exacte frames, bestaande tekensets,
onbekende chunks/notities, metadata-only Undo, hoofdstukeinden, milliseconderonding,
geldige geneste inhoudsopgaven bij meer dan 255 items en echte WAV-/MP3-roundtrips.
Project- en herstelproeven controleren bron-/sessiemetadata en achterwaartse lezing.

GUI-proeven controleren sneltoetsen, slepen/annuleren, eigenschappen, kanaalbehoud,
wisselen tussen sessie en golfvorm, opnamevergrendeling, lettergrootte/vijf talen,
letterlijke namen, alleen sessiemarkeringen in de eindmix en veilige exportweigering.
De bronmarkeringen van verschillende clips worden niet automatisch samengevoegd.

## Remaster

De eigen implementatie gebruikt harmonische/percussieve spectrale maskers op basis
van tijd-/frequentiemedianen, beschreven door
[FitzGerald, DAFx-10](https://www.dafx.de/paper-archive/2010/DAFx10/DerryFitzGerald_DAFx10_P15.pdf).
Een gekoppelde drumdetectie stuurt een begrensde verhoging van kort wegzakkende,
aanhoudende midden-/hoogenergie. Geen herstelversterking onder 180 Hz; een zachte
overgang loopt tot 600 Hz. Een constante eindverzwakking bewaakt samplepieken,
zonder extra dynamische compressie. Dit is geen true-peaklimiter of bronseparatie
met afzonderlijke exporteerbare instrumenten.

Een onafhankelijke synthetische proef mengt een 887-Hz-toon met 70-Hz-kicks en een
bekende kortdurende daling van de toon. De standaardinstelling vermindert de
gemeten lokale daling van ongeveer 3,3 naar 1,3 dB. Dit kwantificeert die proef;
het bewijst geen gelijkwaardige verbetering op iedere muziekmix. Opnames met
onbekende oorspronkelijke verwerking laten geen exacte reconstructie toe.

Tests controleren ook een constante toon, drums zonder wegzakken, alleen bas,
gekoppelde stereo, constante uitvoerreserve, blokonafhankelijkheid, volledige
analyse voor voorbeeldconsistentie, stilte/korte fragmenten/hoge rates, eindige
grote waarden, ongeldige invoer, annuleren tijdens analyse/render/uitvoer, één
kanaal, selectiegrenzen, markers, Undo/Redo, schijfopslag en lossless WAV-opslag.
De dialoogproeven controleren A/B, luistervolume, cursorpositie, cacheverversing,
annuleren, toepassen en vijf talen met grotere letters.

Analyse en uitvoer gebruiken tijdelijke schijfopslag voor grote reeksen; spectrale
batches zijn begrensd tot 64 frames. Het eerste luistervoorbeeld analyseert het
volledige bereik. Het bronbestand blijft bij het vergelijken onaangeroerd.

## Afronding

De gerichte lokale proeven slagen. De volledige distributiecontroles, geïnstalleerde
pakketten en publicatiestatus worden na de bouw hieronder vastgelegd.
De hoorbare Remaster-vergelijking op een fysieke uitgang blijft een praktijkproef;
numerieke signalen alleen beoordelen geen muzikale balans of luisterkwaliteit.
De overige B33-proeven blijven opgenomen in de [todo](../TODO.md).
