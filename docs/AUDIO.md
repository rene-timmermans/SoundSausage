# Opnemen, afspelen en samplerates

SoundSausage speelt audio rechtstreeks af via Qt Multimedia. Een extern
afspeelprogramma is niet nodig. De gewone golfvorm, multitrackmix en
effectvoorbeelden gebruiken dezelfde audio-uitvoer. Opname gebruikt Qt audio-invoer
met een eigen keuze voor microfoon of audio-interface; zie [opnemen](OPNEMEN.md).

## Audio Hardware

Onder **Options → Audio Hardware** kies je **System Default** of een specifiek
uitvoerapparaat. De keuze blijft bewaard voor de volgende start. Wanneer een
specifiek gekozen apparaat ontbreekt, verschijnt een melding; de toepassing
schakelt dan niet stilzwijgend naar een andere uitgang.

De afspeelbuffer kan tussen 20 en 500 ms liggen. Een grotere buffer verdraagt
onderbrekingen beter; een kleinere reageert sneller. Het apparaat kan intern een
andere buffergrootte gebruiken. De instelling wijzigen stopt lopend afspelen en
effectvoorbeelden. Een verdwenen of gewijzigd uitvoerapparaat stopt het afspelen
met een melding; kies daarna de gewenste uitgang en start opnieuw.

**Spatie** start/stopt, **P** pauzeert/hervat en **Esc** stopt. Stoppen gooit de
resterende afspeelbuffer weg. De cursor en niveaumeters volgen de verwerkte
audioframes die de audiobackend rapporteert. Dit geeft geen garantie voor
exacte luidsprekerlatentie: de geluidsserver en hardware hebben hun eigen
buffering. Lussen worden na het uitspelen opnieuw gestart; naadloze overgangen
zijn nog niet gegarandeerd.

## Ingang kiezen

**Recording device** in Audio Hardware bewaart de gekozen ingang. Een specifiek
gekozen apparaat wordt bij ontbreken niet door een andere microfoon vervangen.
Opname begint uitsluitend na Start Recording. Mono/stereo en het eerste ingangskanaal
worden in het opnamevenster gekozen. De live klok telt vastgelegde frames;
pauzetijd wordt uitgesloten. Een take wordt pas na Stop in het document of spoor
bevestigd, met één Undo-stap. Bestaande sporen worden tijdens opnemen nog niet afgespeeld.

## Verschillende samplerates

WAV-bestanden met verschillende samplerates kunnen in dezelfde sessie worden
geïmporteerd. De audio wordt naar de sessierate omgezet. Een nieuwe, nog niet
vast ingestelde sessie neemt de rate van het eerste bestand over. Plakken en
Mix Paste zetten audio naar de rate van de golfvorm om. De bronbestanden en het
klembord blijven daarbij ongewijzigd. Een bewerkte clipkopie met een andere
rate wordt bij toepassen naar de sessierate teruggezet.

**Edit → Convert Sample Rate** zet een volledige golfvorm om. De toonhoogte en
speelduur blijven behouden, met afronding op een uitvoerframe (minimaal één
frame voor een niet-leeg fragment).
Selectie en cursor blijven op dezelfde tijden staan. Undo/Redo herstelt zowel
de samplerate als de audiodata. Ondersteunde rates lopen van 1.000 tot 384.000 Hz.

De conversie gebruikt de bandbegrensde sinc-converter van libsamplerate, met een
stilte-aanname buiten het fragment. Korte fragmenten kunnen daardoor een
andere randvorm of piekwaarde krijgen. De converter houdt filterstaat tussen
blokken vast; lange resultaten kunnen op schijf worden voorbereid.

Voor afspelen kiest SoundSausage een ondersteund mono-/stereoformaat. Zo nodig
worden samplerate, kanaalaantal en sampletype alleen voor de uitvoer omgezet.
De golfvorm zelf verandert daarbij niet. Oversturing wordt bij uitvoer begrensd;
de interne bewerking houdt haar extra versterkingsruimte.

## Installatiecontrole

`soundsausage --selftest` controleert bestanden, audiokern, conversie en vensters
zonder een audioapparaat te openen. `soundsausage --audio-selftest` controleert
de geselecteerde uitgang met een kort stil signaal; er wordt niets opgenomen.

De pakketbouw test afspelen met een privaat virtueel audioapparaat, inclusief
pauzeren, hervatten, afspeeltijd en lussen. Een hoorbare controle op echte
hardware blijft een aparte stap. Lange bestanden gebruiken verwerking vanaf
schijf; zie [werkruimte en herstel](LANGE_BESTANDEN.md). Realtime spooreffecten
volgen later; zie [voortgang](VOORTGANG.md).

`soundsausage --input-selftest` opent de geselecteerde ingang kort, controleert
of er frames binnenkomen en verwijdert de testopname. Alleen die expliciete
optie start een opname; de gewone selftest opent geen microfoon. De pakketbouw
controleert opname, pauzeren/hervatten en stoppen tegen een private virtuele ingang.
De fysieke opname-/afspeelcontrole blijft een afzonderlijk open punt.

Technische referenties: [Qt audio-uitvoer](https://doc.qt.io/qt-6.8/qaudiosink.html),
[Qt audio-invoer](https://doc.qt.io/qt-6.8/qaudiosource.html),
[Qt apparaatformaten](https://doc.qt.io/qt-6.8/qaudiodevice.html) en
[libsamplerate-conversie](https://libsndfile.github.io/libsamplerate/api_full.html).
