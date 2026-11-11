# Opnamebegin, stereoscheiding en MP3 — 0.17.0

## Opname

De eerste ingestelde milliseconden worden één keer per take in volledige
invoerframes verwijderd, vóór decodering en opslag. Bij een niet-nul uitsnede
volgt 5 ms fade-in over blokgrenzen. De apparaatrate bepaalt het aantal frames;
begeleiding en opnameklok gebruiken de bewaarde audio en de bijbehorende timing.
Pauze/hervatten herhaalt de uitsnede niet. Een lege take wordt verwijderd;
herstel bewaart uitsluitend de reeds vastgelegde audio.

Zeven nieuwe controles toetsen gedeeltelijke reads, onvolledige invoerframes,
native/gevraagde samplerates, fade-in, pauze, exacte duur, lege takes, ongeldige
instellingen, voorkeuren, live meters, invoegen/Undo en begeleiding bij een
44,1 kHz sessie met 48 kHz invoer. De begeleidingsproef bevat zowel direct
beschikbare invoer als invoer na het verlopen van de bijbehorende afspeeltijd.
De geïnstalleerde invoerzelftest gebruikt eveneens de uitsnede.

Een cosmetische lijn van één schermpixel scheidt de stereokanalen over de
volle breedte van de golfvorm en de live opnameweergave. De bestaande controles
op kanaalselectie en golfvormcontinuïteit blijven actief.

## MP3

Vijftien nieuwe codec-/GUI-controles behandelen echte MP3-encodering en decodering,
mono/stereo, de vier bitrates, VBR-import, Unicode/bijzondere bestandsnamen,
samplerates, zeer korte selecties, metadata, hoesafbeeldingen, schijfopslag,
annuleren en fouten. Ze toetsen ook vertaalde bestandsfilters en juiste
extensies, bevestiging bij een bestaand aangepast doel, behoud van niet-opgeslagen
werk, selectie-export, eindmix, crashherstel en zelfstandige projecten.

De tests vergelijken audio met een onafhankelijk bekend signaal. MP3 is
verliesgevend; PCM-uitvoer wordt exact vergeleken, MP3 wordt op lengte, kanalen,
samplerate en signaalafwijking gecontroleerd. De codec schrijft eerst naar eigen
werkruimte en vervangt een bestaand doel pas na geslaagde conversie en opslag.
Annuleren ruimt tijdelijke bestanden op en beëindigt het codecproces.

De omzetting gebruikt [FFmpeg](https://ffmpeg.org/ffmpeg.html); ID3 wordt verwerkt
met [Mutagen](https://mutagen.readthedocs.io/en/latest/api/id3.html).
Grote audio blijft op schijf en wordt in blokken verwerkt. De oorspronkelijke
bronbestanden worden alleen gewijzigd wanneer ze expliciet als opslagdoel zijn
gekozen. De gewone installatiezelftest bevat een MP3-rondgang.

## Praktijkbestanden en regressies

Alle 38 bestanden uit de privétestset zijn geopend, in volume aangepast en
ingekort, als WAV én MP3 opgeslagen en opnieuw geopend. Dit omvat twaalf
bestanden met een tracknummer vóór de artiestnaam, 44,1/48 kHz, verschillende
bitrates, VBR, Unicode, bijzondere tekens en een grote hoesafbeelding.
WAV-uitvoer is exact gelijk aan het bewerkte audiosignaal. MP3-uitvoer behoudt
het aantal frames; de gemeten signaal-afwijkingsverhouding ligt tussen 29,37 en
46,90 dB. Tekstvelden en de hoesafbeelding zijn gecontroleerd. Alle oorspronkelijke
bestanden zijn vóór en na de proef met SHA-256 vergeleken en ongewijzigd.
De audiobestanden, namen en gedetailleerde privéreceipts worden niet gepubliceerd.

Lokaal slagen alle 406 controles; zes expliciete audiobackendcontroles worden
lokaal overgeslagen. De catalogus bevat 1.279 bronvormen per taal en de vijf
offlinehandleidingen behandelen de nieuwe bediening. De definitieve
distributiebouw en installatiecontroles worden vóór publicatie uitgevoerd.
DSP-ABI 7 en projectformaat 4 blijven behouden.
