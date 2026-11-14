# Systeemgeluid opnemen — 0.25.0

## Bronkeuze en gedrag

Systeemgeluid (wat je hoort) staat in Audioapparaten en het opnamevenster.
De blijvende keuze is een systeembron, geen microfoon-ID. Iedere nieuwe take
vraagt de huidige systeemstandaard op en gebruikt de expliciet gerapporteerde
monitorbron. De afzonderlijke afspeelkeuze van SoundSausage verandert die bron
niet. Andere apps en begeleiding op dezelfde uitgang komen eveneens in de take.
De monitor volgt de servermixer; de fysieke luidsprekersterkte kan afwijken.

PulseAudio en de PulseAudio-ondersteuning van PipeWire leveren de uitgangsmonitor.
[pactl](https://github.com/pulseaudio/pulseaudio/blob/master/src/utils/pactl.c)
rapporteert de default_sink_name en de monitor_source van die uitgang in JSON.
Er wordt geen bronnaam geraden en niet op een standaardmicrofoon teruggevallen.
[parec](https://manpages.debian.org/trixie/pulseaudio-utils/parec.1.en.html)
levert raw float32 stereo op de aangevraagde samplerate en een expliciete kanaalkaart.
Mono-opname kiest links of rechts via het eerste ingangskanaal.

## Verwerking en fouten

Een apart proces levert audio via de gewone Recorder/Take-route, met blokken,
live meters, opnameduur, startcorrectie, hersteljournal en één documentbewerking.
[QProcess](https://doc.qt.io/qt-6/qprocess.html) wordt met losse argumenten gestart;
er is geen shell. Standaardfout wordt begrensd op 4 KiB en ongelezen uitvoer op
8 MiB gecontroleerd. Detectie heeft een timeout. Alleen opnemen start de stream.
Er worden geen globale audiomodules geladen, routes of standaardapparaten gewijzigd.

Pauzeren sluit de stream en wist ongelezen data; hervatten opent dezelfde monitor
opnieuw. Pauzetijd kan zo niet later uit een oude wachtrij in de take komen.
Een gemelde uitgangswissel of verlies stopt de take en bewaart complete frames.
De volgende opname bepaalt opnieuw de systeemstandaard. Wissel uitgangen tussen
takes. Ontbrekende server, monitor of hulpmiddelen geeft een vertaalde melding.

De pakketten vereisen pulseaudio-utils op Debian/Ubuntu/Fedora en libpulse op Arch.
Die clientpakketten werken ook met PipeWire; er wordt geen vervangende geluidsserver
als pakketafhankelijkheid verplicht. DSP-ABI 7, projectversie 5 en herstelversie 2
blijven behouden. De bestaande v1-todo B36b/B33 blijft open.

## Controledekking

Gerichte tests toetsen expliciete monitorselectie, andere standaarduitgangen,
ontbrekende bronnen/hulpmiddelen, JSON en timeouts, bronvoorkeur zonder microfoon,
stereo en mono-kanaalkeuze, beide vensters en annuleren van voorkeuren.
Een onafhankelijk producerproces toetst echte Qt-pullreads, exacte stopduur,
pauze zonder achterstallige audio, hervatfouten, complete frames bij procesverlies,
weggooien en behoud bij routewijzigingen. De editorroute toetst invoegen als één
Undo-stap, Redo en WAV-opslag.

Een aparte backendproef speelt twee verschillende tonen naar de standaarduitgang
en controleert hun kanaalverdeling in de opgenomen monitor op 44,1 en 48 kHz.
Die draait uitsluitend met de expliciete private audio-omgeving van de runners.
De geïnstalleerde pakketten voeren dezelfde tooncontrole uit met
`--system-audio-selftest`, naast de vier bestaande zelftests. De gewone zelftest
neemt geen systeemgeluid op en speelt geen toon af.

Definitieve distributie- en pakketresultaten volgen na verificatie van de release.
Een fysieke proef op de eigen uitgang blijft onderdeel van B33.
