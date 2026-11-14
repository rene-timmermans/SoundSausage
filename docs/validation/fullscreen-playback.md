# Afspelen in volledig scherm — 0.25.2

## Oorzaak en correctie

Het opnieuw vullen van een grote, complexe min/max-polygoon blokkeerde de
GUI-thread, die ook de uitvoerbuffer aanvult. Bij een volledig golfvormoverzicht
kon één beeld langer duren dan de ingestelde audiobuffer.

Verticale piekspannen met verbonden contouren vervangen die polygoon in de
gewone golfvorm en clipweergave. De gewone golfvorm bewaart één beeld ter grootte
van het huidige tekenvlak, inclusief de pixelschaal van het scherm. Alleen de
cursor wordt opnieuw getekend. Audioveranderingen, selectie, kanaalkeuze, thema,
lettertype, taal, vergroting en formaat maken het beeld ongeldig.

Tijdens afspelen bereidt maximaal één achtergrondtaak nieuwe piekgegevens voor.
De eerste formaatweergave wordt getekend vóór die taak begint; de taak staat
regelmatig Python-tijd af aan de GUI. Een achterhaald resultaat wordt niet
gebruikt en veroorzaakt voorbereiding van de nieuwste weergave. Het vorige
piekoverzicht kan tijdens het voorbereiden kort zichtbaar blijven. Er is geen
extra kopie van het volledige geluidsbestand. Een eigen Qt-audiothread bezit de uitgang, vult begrensde PCM-blokken aan en
leest de verwerkte audioklok. Alleen deze thread roept de Qt-audio-objecten aan.
De GUI leest de gerapporteerde klok en verzonden bytes; zij hoeft de buffer niet
te voeden. Start, pauze, hervatten, stoppen en lussen gebruiken dezelfde threadgrens.
De klok wordt vóór de positie-uitzending bijgewerkt; de weergave wordt begrensd op dertig beelden per
seconde. Het model blijft iedere audiopositie ontvangen, inclusief de exacte
pauze- en stoppositie. De ingestelde audiobuffer wordt niet vergroot.

## Metingen en regressies

Met een stereo-WAV van ongeveer vijf minuten bedroeg de herhaalde weergave op
de lokale meetmachine circa 119 ms bij 1920×1080 en 1162 ms bij 3840×2160.
Met het hergebruikte beeld was dit circa 3 ms en 10 ms. Dit zijn metingen van
die machine en weergave, geen vaste prestatietoezegging voor alle apparaten.

Gerichte controles toetsen continuïteit bij de overgang tussen samples en
piekoverzicht, links/rechts-selectie, tekenen, samplebewerking, Undo, live thema,
het wissen van de vorige cursor, audio-/selectieaanpassingen en een lege
werkruimte. Achtergrondproeven blokkeren een taak opzettelijk, veranderen
vensterformaat en document en controleren dat slechts één taak loopt en het
verkeerde resultaat wordt verworpen. Een mislukte voorbereiding blijft begrensd.
Een audiobufferproef controleert dat de buffer vóór weergavecallbacks wordt gevuld.

De zelfstandige backendproef draait via X11 en een expliciete private audiobron.
Zij speelt een vijf minuten lange synthetische stereogolfvorm met twee tonen af,
schakelt F11, vergroot het venster tot 4K en verandert de vergroting. De opgenomen
uitgangsmonitor moet op beide kanalen iedere interne 5ms-groep geluid bevatten.
De proef blokkeert de GUI ook opzettelijk 180 ms, langer dan de ingestelde
100ms-uitvoerbuffer. Aanvullende threadproeven toetsen doorlopende exacte PCM,
eigendom van alle sink-aanroepen, pauze/hervatten, stop/herstart en schrijffouten.
De oorspronkelijke audiofile wordt hiervoor niet gepubliceerd of aangepast.

## Vensterafmetingen

Een normale afsluiting bewaart de Qt-venstergeometrie, inclusief de normale
afmetingen achter een volledig-scherm- of gemaximaliseerde stand. Bij starten
worden afmetingen, positie en stand hersteld; Qt past de geometrie aan beschikbare
schermen aan. Ontbrekende of ongeldige voorkeuren gebruiken de gewone beginafmetingen.
Annuleren van afsluiten overschrijft de opgeslagen geometrie niet. Screenshot-
en installatiezelftests veranderen de persoonlijke venstergeometrie niet.

Twee afzonderlijke tests controleren bewaren/heropenen met een nieuwe
voorkeureninstantie en annuleren/ongeldige gegevens. Alle vijf handleidingen
beschrijven het onthouden van de afmetingen en het wisselen met F11.

## Distributiecontrole

De releasebouw voert alle tests uit op Debian, Fedora en Arch, inclusief de
private audioproef. Daarna volgen installatie en de vijf gewone/audio-/input-/
duplex-/systeemgeluidzelftests op vijf doelen, inclusief Ubuntu 26.04 en Rolling.
DSP-ABI 7, projectformaat 5 en herstelversie 2 blijven behouden. De twee open
v1-punten B36b en B33 blijven behouden; fysieke controle op de eigen uitgang
blijft onderdeel van B33.
