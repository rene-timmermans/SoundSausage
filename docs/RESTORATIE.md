# Ruisreductie en klikverwijdering

Deze effecten staan onder **Transform → Noise Reduction** en werken op een
selectie of, zonder selectie, de hele golfvorm. **Preview** laat maximaal acht
seconden horen. **OK** past toe, **Cancel** sluit zonder wijziging en **Ctrl+Z**
draait terug. **F2** herhaalt de instellingen, inclusief het gebruikte ruisprofiel.

## Een ruisprofiel opnemen

1. Zoek een stukje waarin alleen de ongewenste achtergrond hoorbaar is, zonder
   spraak of muziek. Een halve tot enkele seconden is meestal bruikbaar.
2. Selecteer dat stukje en kies **Capture Noise Profile**. Ook **Capture from
   selection** in het effectvenster kan dit doen. Er verandert nog geen audio.
3. Selecteer vervolgens het fragment dat je wilt schoonmaken, of hef de selectie
   op voor de hele opname. Open **Noise Reduction**.
4. Begin met **Gentle** of **Balanced**, luister met Preview en vergelijk met de
   oorspronkelijke opname door het venster te annuleren.

Een profiel beschrijft het gemiddelde frequentiebeeld van maximaal de eerste
30 seconden van de gekozen ruisselectie. De minimumduur hangt van de samplerate
af en wordt gemeld bij een te korte selectie. Het profiel blijft tijdens deze
appsessie beschikbaar. De samplerate moet overeenkomen. Het aantal kanalen
moet passen bij de gekozen kanalen. Bij Left of Right kan een stereoprofiel
het bijbehorende kanaal leveren; een monoprofilering kan op één kanaal werken.

**Save Profile** bewaart het als `.ssnoise`; **Load Profile** opent zo'n bestand.
Daarmee kun je een profiel later opnieuw gebruiken. Het bevat een ruisspectrum,
geen geluidsopname. Een profiel van een andere opstelling kan minder goed werken.

## Noise Reduction

- **Maximum noise reduction:** de maximale verzwakking in ruisgebieden, 0–36 dB.
  Begin met 6–12 dB; een hogere waarde kan ook zachte details aantasten.
- **Sensitivity:** hoeveel van het profiel als ruis wordt beschouwd. Meer
  gevoeligheid behandelt meer achtergrond, maar kan meer bijgeluiden geven.
- **Smoothing:** maakt de overgang van sterker naar zwakker onderdrukken rustiger.
  Een hoge waarde laat na een duidelijk geluid tijdelijk meer achtergrond door.
- **Link stereo channels:** gebruikt dezelfde verzwakking links en rechts om
  de balans te behouden. Zonder koppeling wordt ieder kanaal apart behandeld.
- **Keep removed noise only:** levert het verwijderde deel op in plaats van het
  schoongemaakte geluid. Luister hiermee of waardevolle spraak of muziek verdwijnt.
  Schakel dit weer uit vóór OK wanneer je de schoongemaakte opname wilt behouden.

Dit werkt vooral bij vrij constante ruis, zoals ventilatie of een gelijkmatige
sis. Het verwijdert geen afzonderlijke stemmen uit een mix en herstelt geen
ontbrekende details. Veranderende achtergrond, te sterke reductie of een profiel
met spraak/muziek kan hoorbare vervorming of een korrelige klank geven. De lengte
en cueposities blijven gelijk. De eerste acht seconden in Preview zijn hetzelfde
als de eerste acht seconden van de volledige bewerking.

## Click Removal

Dit effect zoekt korte, geïsoleerde sprongen die snel naar de omgeving terugkeren
en vervangt ze door een verbinding tussen de omliggende onbeschadigde samples.

- **Threshold multiplier:** een hogere waarde maakt de herkenning terughoudender;
  een lagere waarde vindt meer mogelijke tikken.
- **Minimum jump level:** de minimale sprongsterkte in dBFS. Een lagere waarde
  maakt ook zachtere tikken kandidaat.
- **Maximum click width:** de langste tik die mag worden hersteld, 0,02–2 ms.

De presets **Conservative**, **Small clicks** en **Wider clicks** zijn beginpunten.
Gebruik bij voorkeur een selectie rondom het probleem en luister met Preview.
Slagwerk en scherpe aanslagen kunnen op tikken lijken. Lange kraken, clipping
en beschadigde begin-/eindsamples worden hiermee niet betrouwbaar hersteld.
Behandel zulke plekken afzonderlijk en bewaar eerst een kopie.

Beide effecten werken met begrensde werkbuffers, ook bij lange opnamen. Annuleren
laat audio, selectie en Undo/Redo intact. Voor een multitrackclip open je eerst
een bewerkkopie en kies je na de bewerking Apply Waveform to Clip. Realtime
ruisonderdrukking tijdens opnemen of afspelen is hiermee niet beschikbaar.
