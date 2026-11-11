# Opnemen en dagelijks werken

Druk op **R** of de opnameknop en kies de ingang en bestemming. **New waveform**
maakt een losse opname. **Insert at cursor** voegt de take op de huidige cursor
in; **Replace selection** vervangt de selectie. In multitrack ontstaat een nieuw
blok op het gekozen spoor, zonder andere blokken te verwijderen.

**Mono** gebruikt één ingangskanaal, **Stereo** een opeenvolgend paar. Met **First
input channel** kies je het eerste kanaal. Een monoapparaat kan op twee identieke
stereokanalen worden opgenomen. De app probeert het gewenste formaat en kiest
zo nodig een ondersteunde apparaatrate. Na Stop wordt de take naar de rate van
het doel omgezet. De verwerking gebruikt begrensde blokken en opslag op schijf.

**Start Recording** opent de microfoon. De klok en meters volgen vastgelegde
frames, de live golfvorm toont twintig seconden. **P** pauzeert en hervat. **Stop**,
**Esc**, **Spatie** of opnieuw **R** houdt de take als één Undo-stap. **Discard
Recording** verwijdert alleen deze take. Sluiten vraagt eerst naar de opname.

De gekozen ingang wordt onder **Options → Audio Hardware** onthouden. Een
losgekoppelde USB-microfoon wordt niet ongemerkt door een andere ingang vervangen.
Het reeds vastgelegde deel blijft behouden bij apparaatverlies of een schrijffout.
De eigen take krijgt ongeveer iedere seconde een duurzaam herstelpunt; de
schrijfcontrole draait buiten de interface. Bij de volgende start kan SoundSausage de
opname aanbieden, of kies **File → Recover Work**. Annuleren van de verwerking
na Stop bewaart de take eveneens voor herstel.

Het ingangssignaal wordt niet door de speakers gespeeld. Gelijktijdig opnemen
en de sessie terugluisteren, punch-in/out en automatische latencycompensatie
zijn nog niet beschikbaar. Neem takes afzonderlijk op en combineer ze daarna.
Bij meerdere kanalen is opname beperkt tot één mono- of stereopaar per take.

Een complete werkwijze:

1. Neem een take op of open een WAV-bestand.
2. Selecteer een fragment en werk volume of overgangen bij met Amplitude.
3. Bewaar de golfvorm; voeg die in multitrack in.
4. Neem volgende takes op een spoor op. Verplaats clips en stel volume/pan/lijnen in.
5. Bewaar het project en heropen het om de afzonderlijke sporen verder te bewerken.
6. Maak met Mix Down een WAV-eindmix. De opgeslagen bronopnamen blijven behouden.

Opname en afspelen zijn automatisch controleerbaar met een private virtuele
audiobackend. De praktijktest met een fysieke microfoon en luidsprekers blijft
apart zichtbaar in [voortgang](VOORTGANG.md). De volledige uitleg staat ook
offline in **Help → Handleiding / F1**.
