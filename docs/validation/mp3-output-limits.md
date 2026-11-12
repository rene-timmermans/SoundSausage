# MP3-uitvoergrenzen — B03

## Besluit

De bestaande uitvoerkeuzes blijven behouden: 128, 192, 256 of 320 kb/s bij de
dichtstbijzijnde samplerate van 32/44,1/48 kHz, met minstens 2 ms audio.
Deze combinatie ondersteunt de aangeboden bitrates en vermijdt problematische
zeer korte fragmenten. B03 is als bewuste exportkeuze uit de open todo verwijderd.
WAV blijft beschikbaar voor kortere fragmenten. De app blijft versie 0.20.0;
deze beoordeling verandert geen audioverwerking, interface of installatiepakket.

## Methode

De lokale FFmpeg/libmp3lame-encoder is met synthetische 440 Hz-audio onderzocht.
Voor iedere combinatie van negen ondersteunde samplerates, vier bestaande
bitrates en mono/stereo is een kwart seconde audio als float32-WAV geschreven,
naar MP3 gecodeerd en weer naar float32-WAV gedecodeerd. Mutagen leest de
werkelijke samplerate en bitrate; het aantal gedecodeerde frames wordt met de
bron vergeleken. Dat zijn 72 combinaties.

Daarnaast zijn bij 8/32/44,1/48 kHz, 192 kb/s en mono/stereo fragmenten van
één sample, ongeveer 1 ms en minimaal 2 ms onderzocht: 24 extra proeven.
Deze proeven spreken de encoder rechtstreeks aan, ook buiten de huidige
SoundSausage-uitvoerkeuzes. Een afwijking buiten dat bereik is een onderzoeks-
resultaat en geen fout in de gepubliceerde app.

## Uitkomst

| Controle | Resultaat |
| --- | --- |
| Normale fragmenten, 72 combinaties | Allemaal te decoderen, met het oorspronkelijke aantal frames. |
| Huidige rates, 24 normale combinaties | Gevraagde samplerate en bitrate komen overeen met de uitvoer. |
| Lagere rates, 48 normale combinaties | In 42 gevallen is de werkelijke bitrate lager dan gevraagd. |
| Zeer korte fragmenten, 24 combinaties | 15 worden langer; één bestand bij 8 kHz/stereo is niet te decoderen. |
| Minimaal 2 ms bij de drie huidige rates, mono/stereo | Alle zes behouden het aantal frames. |

Bij 8/11,025/12 kHz levert deze encoder voor de huidige bitratekeuzes 64 kb/s.
Bij 16/22,05/24 kHz blijven 128 kb/s behouden, terwijl de hogere keuzes 160 kb/s
opleveren. Alleen lage samplerates toevoegen zou dus andere bitratekeuzes of
een zichtbare afhandeling vereisen. Bij zeer korte audio kan bijvoorbeeld één
sample als 47 samples terugkomen. Een lagere rate vraagt ook een afzonderlijke
beoordeling van de minimale fragmentduur.

De bestaande controles voor mono/stereo, alle vier bitrates, rateconversie en
het weigeren van fragmenten onder 2 ms slagen. De twee gerichte tests blijven
ongewijzigd. Er zijn geen nieuwe regressietests nodig voor deze documentatiestap.

## Dekking en vervolg

De codecproeven zijn lokaal uitgevoerd; dit is geen nieuwe codeccontrole op
alle distributies. De eerdere releasecontroles van 0.20.0 blijven geldig voor
de ongewijzigde software. Er zijn geen persoonlijke muziekbestanden gebruikt.
De technische voorwaarden blijven in STATUS en alle vijf handleidingen staan.
Onderzoeksgegevens worden lokaal bewaard in `build/mp3-limits-probe/` en de
testuitvoer in `build/mp3-limits-tests.log`.

De volgende inhoudelijke beoordeling is B04: hoofdstukposities, ReplayGain,
overige afgeleide metadata en de WAV-naar-MP3-keuze.
