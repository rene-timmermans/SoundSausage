# Opnemen en dagelijks werken

Druk op **R** of de opnameknop en kies de ingang en bestemming. **Nieuwe golfvorm**
maakt een losse opname. **Invoegen bij cursor** voegt de take op de huidige cursor
in; **Selectie vervangen** vervangt de selectie. In multitrack ontstaat een nieuw
blok op het gekozen spoor, zonder andere blokken te verwijderen.

**Mono** gebruikt één ingangskanaal, **Stereo** een opeenvolgend paar. Met **Eerste invoerkanaal** kies je het eerste kanaal. Een monoapparaat kan op twee identieke
stereokanalen worden opgenomen. De app probeert het gewenste formaat en kiest
zo nodig een ondersteunde apparaatrate. Na Stop wordt de take naar de rate van
het doel omgezet. De verwerking gebruikt begrensde blokken en opslag op schijf.

**Begin overslaan** verwijdert eenmalig de eerste 0–500 ms, met 50 ms als
beginwaarde en een fade-in van 5 ms. Daarmee kan een inschakelklik buiten de
opname blijven. Kies 0 ms om het volledige begin te bewaren. De keuze blijft
bewaard; pauzeren en hervatten herhalen de uitsnede niet. Klok, meters en maximale
duur tellen alleen de bewaarde audio. Met begeleiding telt de uitsnede mee in
de clippositie. Twee dunne horizontale lijnen begrenzen de stereokanalen binnen het tekenvlak: de onderrand van links en de bovenrand van rechts.

**Opname starten** opent de microfoon. De klok en meters volgen vastgelegde
frames, de live golfvorm toont twintig seconden. **P** pauzeert en hervat. **Stoppen**,
**Esc**, **Spatie** of opnieuw **R** houdt de take als één Undo-stap. **Opname verwerpen** verwijdert alleen deze take. Sluiten vraagt eerst naar de opname.

De gekozen ingang wordt onder **Opties → Audioapparaten** onthouden. Een
losgekoppelde USB-microfoon wordt niet ongemerkt door een andere ingang vervangen.
Het reeds vastgelegde deel blijft behouden bij apparaatverlies of een schrijffout.
De eigen take krijgt ongeveer iedere seconde een duurzaam herstelpunt; de
schrijfcontrole draait buiten de interface. Bij de volgende start kan SoundSausage de
opname aanbieden, of kies **Bestand → Werk herstellen**. Annuleren van de verwerking
na Stop bewaart de take eveneens voor herstel.

Het ingangssignaal wordt niet door de speakers gespeeld. In multitrack kan
**Bestaande sporen afspelen tijdens opnemen** de begeleiding afspelen, inclusief
spooreffecten. **P** pauzeert/hervat beide; Stop bewaart de nieuwe take.
**Opnamepositie verschuiven** stelt de plaatsing van de take af. Punch-in/out en
automatische latencycompensatie blijven vervolgstappen. Zie
[spooreffecten en opname met begeleiding](REALTIME.md) voor bediening en kalibratie.
Bij meerdere kanalen is opname beperkt tot één mono- of stereopaar per take.

Een complete werkwijze:

1. Neem een take op of open een WAV- of MP3-bestand.
2. Selecteer een fragment en werk volume of overgangen bij met Amplitude.
3. Bewaar de golfvorm; voeg die in multitrack in.
4. Neem volgende takes op een spoor op. Verplaats clips en stel volume/pan/lijnen in.
5. Bewaar het project en heropen het om de afzonderlijke sporen verder te bewerken.
6. Maak met Eindmix maken een WAV- of MP3-eindmix. De opgeslagen bronopnamen blijven behouden.

Opname en afspelen zijn automatisch controleerbaar met een private virtuele
audiobackend. De bevestigde praktijktest met een fysieke USB-microfoon en uitvoer staat
ook in [voortgang](VOORTGANG.md). De volledige uitleg staat ook
offline in **Help → Handleiding / F1**.
