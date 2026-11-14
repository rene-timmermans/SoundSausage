# MP3-metadata — B04, 0.21.0

## Gedrag

Hoofdstukintervallen volgen verwijderen, invoegen, trimmen, selectie-export,
omkeren en tijdrekken. Samplerateomzetting behoudt hun milliseconden. Plakken
neemt hoofdstukken en hun hiërarchie mee met unieke identificaties; algemene
tags van de bestemming blijven behouden. De inhoudsopgave verliest verwijzingen
naar verdwenen hoofdstukken en volgt de nieuwe volgorde. Lege, geheel
verwijderde en niet meer aaneengesloten gedeeltelijk omgekeerde hoofdstukken
vervallen. Grenzen onder één milliseconde kunnen tot nul worden afgerond.

Titel, artiest, album, opmerkingen, hoes en gewone identificaties blijven
behouden. Bekende achterhaalde meetwaarden worden verwijderd: ReplayGain,
R128, MP3Gain, AccurateRip, akoestische vingerafdrukken, relatieve volumegegevens
en oude encoderinformatie. Niet ondersteunde getimede velden, zoals SYLT,
ETCO, SYTC, POSS en oude indexen, vervallen na audioverandering. Onbekende
privévelden blijven letterlijk behouden. ReplayGain wordt niet opnieuw gemeten. BPM en toonsoort vervallen
alleen bij respectievelijk tempo- en toonhoogteverandering, ook gecombineerd
in Stretch; gewone volume- of samplebewerkingen behouden die twee velden.

MP3 opnieuw coderen verwijdert eveneens oude metingen en bestandposities;
de nieuwe encoderinformatie komt uit het werkelijk gecodeerde bestand.
Hoofdstukken gebruiken tijdgrenzen en onbekende byteoffsets. De duur wordt
opnieuw uit frames en samplerate bepaald.

WAV INFO-velden voor titel, artiest, album, genre, datum, tracknummer,
auteursrecht en opmerkingen worden expliciet naar ID3 vertaald. UTF-8 en
Windows-1252-tekst zijn ondersteund. Bestaande ID3 heeft voorrang. Onbekende,
misvormde en conflicterende velden verschijnen in de bestaande exportkeuze.
Extra ID3-tags in een WAV worden eveneens als weglating gemeld.
Weigeren wijzigt het doelbestand niet. Encoderinformatie ISFT wordt vernieuwd;
dit voorkomt dat de intern gedecodeerde WAV een verliesmelding veroorzaakt.
Onleesbare embedded WAV-ID3 blijft opaque; MP3-export ervan meldt een fout.

## Onderbouwing en opslag

CHAP gebruikt milliseconden en kan byteoffsets als onbekend markeren; CTOC
verwijst naar hoofdstuk- en inhoudsopgave-identificaties. Zie de
[ID3-hoofdstukspecificatie](https://id3.org/id3v2-chapters-1.0).
Het wissen van herkende bestandafhankelijke frames sluit aan op de standaard-
aanwijzingen bij gewijzigde bestanden in
[ID3v2.4, default flags](https://id3.org/id3v2.4.0-frames).
De implementatie gebruikt de [Mutagen ID3-interface](https://mutagen.readthedocs.io/en/latest/user/id3.html).

De nieuwe module werkt op afzonderlijk geladen tags; oorspronkelijke bytes
blijven beschikbaar voor Undo. Document._commit verwerkt metadata vóór het
wijzigen van audio, geschiedenis of opslagstatus. Een metadatafout of
annulering laat de vorige toestand intact. Er zijn geen nieuwe project- of
herstelvelden: projectversie 5, herstelversie 2 en DSP-ABI 7 blijven gelijk.

De inhoudsopgave gebruikt een iteratieve traversal met lineair werk, zonder
recursie; ontbrekende verwijzingen, dode takken en cycli worden verwijderd.
Bij plakken krijgen alle ingevoegde elementen verse identificaties. Nieuwe
groepsniveaus houden iedere CTOC onder de grens van 255 kinderen. De bestaande
totale metadatalimiet van 16 MiB blijft gelden.

## Controles

25 nieuwe controles toetsen hoofdstukgrenzen bij invoegen, wissen, crop,
omkeren, tijdrekken, uitklank en samplerateomzetting; plakken met botsende IDs;
een inhoudsopgave boven 255 kinderen; ontbrekende/cyclische verwijzingen;
millisecondenafronding en lege documenten. Verder worden tekst/hoes/gewone tags,
herkende metingen in hoofdstuksubframes, Undo/Redo, no-op, fout en annulering
gecontroleerd. Echte MP3-/WAV-uitvoer, INFO-tekst, datumvalidatie, conflicten,
projectopslag, herstel en de feitelijke GUI-keuze zijn meegenomen.

Alle 58 gerichte metadata-, MP3-, sample- en tekencontroles slagen lokaal.
De gewone installatiezelftest controleert bewerken, Undo/Redo en echte
MP3-hoofdstukken met opgeschoonde metingen. Vijf volledige handleidingen en
1435 bronvormen zijn bijgewerkt, zonder ontbrekende vertalingen.

Definitieve volledige suite, distributiecontroles en publicatie worden na
afronding van de releasebouw vastgelegd. B04 blijft tot die verificatie open.


## Betrouwbare duplexzelftest

De eerste Fedora-bouw meldde bij 44,1 kHz te weinig opgenomen audio. De
zelftest stopte op een vaste 450 ms wandkloktijd, terwijl het starten van de
invoer op een drukke runner varieert. De proef wacht nu op 300 ms werkelijk
ontvangen audio, met behoud van de zeven-secondenlimiet, gekoppelde pauze/
hervatten en de bestaande eis voor de uiteindelijke opnamelengte. Een nieuwe
regressie levert invoer pas na 650 ms aan. De proef met direct klaarstaande
invoer blijft eveneens bestaan. Dit verandert uitsluitend de expliciete
zelftest, niet de opnamebediening van de app.
