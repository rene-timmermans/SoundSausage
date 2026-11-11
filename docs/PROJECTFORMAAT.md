# Native projectformaat, versie 4

Bestanden met extensie `.celp` zijn ZIP-archieven met `project.json` en de gebruikte audio als `media/<id>.wav`. Audio is ingebed als genormaliseerde float32-WAV en behoudt ook headroom boven ±1. Oorspronkelijke WAV-paden zijn niet nodig om het project te heropenen. Ongebruikte bronnen die alleen nog voor undo worden bewaard, worden niet opgeslagen.

`project.json` bevat:

| Sleutel | Betekenis |
| --- | --- |
| `format` | Vaste interne CELP-identificatie (automatisch beheerd) |
| `version` | Geheel getal 4 bij nieuw opslaan; versies 1, 2 en 3 worden ook gelezen |
| `sample_rate` | Gemeenschappelijke samplerate |
| `media` | Bron-ID, naam, frame-/kanaalaantal en de ingebedde bestandsnaam |
| `tracks` | Spoor-ID, naam, gain, pan, mute/solo, een lijst clips, `effects` en `tail_seconds` |

Elke clip heeft een eigen ID, media-ID, naam, `start`, `source_start`, `source_end`, `gain`, `pan`, `fade_in`, `fade_out`, `muted`, `volume_envelope` en `pan_envelope`. Posities en lengtes zijn gehele aantallen audioframes. Bronbereiken hebben een exclusief einde. De volledige bron blijft ingebed, ook na trimmen, zodat eerder verborgen audio weer zichtbaar gemaakt kan worden.

De twee envelopevelden zijn lijsten `[bronframe, waarde]`-paren, met maximaal 512 punten per lijn. Frames zijn geordend en uniek, vanaf 0 tot en met het laatste frame in de volledige bron. Een lege volumelijn is neutraal op 1; een lege panlijn op 0. Volume ondersteunt 0–2 en pan −1–1. De waarden worden lineair geïnterpoleerd; buiten het puntenbereik blijft de eerste of laatste waarde gelden. Volumefactor en panbalans worden boven op de bestaande gain/pan/fades toegepast. Zie [ENVELOPES.md](ENVELOPES.md) voor de bediening en precieze regels bij trimmen en bronvervanging.

Versie 1 heeft geen envelopevelden en wordt met neutrale lijnen geladen. Vanaf versie 2 zijn beide velden verplicht, ook wanneer ze leeg zijn. Envelopevelden in een als versie 1 gemarkeerd bestand worden afgewezen. Oudere versies weigeren formaatversie 2 bij openen, zodat ze de nieuwe punten niet stilzwijgend kunnen negeren. De projectbeschrijving is maximaal 32 MiB. Versie 3 bewaart ook bronmetadata in
de ingebedde WAV, staat RF64 voor grote bronnen toe en verwerkt ZIP-leden in
blokken. Oudere appversies weigeren versie 3, zodat metadata niet ongemerkt
verdwijnt. Openen en opslaan vragen werkruimte op schijf; zie [lange bestanden](LANGE_BESTANDEN.md).

De mixer gebruikt een lineaire balans: pan −1 geeft alleen links, +1 alleen rechts en 0 geeft unity aan beide kanten. Mono wordt eerst naar twee kanalen gekopieerd. Track- en clipinstellingen worden na elkaar toegepast. Solo selecteert de hoorbare sporen; mute blijft doorslaggevend. Fades zijn lineair, liggen binnen de clipduur en mogen samen niet langer zijn dan de clip.

Bij 16-bit sessie-mixdown wordt afgerond naar PCM en begrensd tot −32767 en +32767. De interne mix, ingebedde projectaudio en float32-mixdown bewaren headroom. De exclusieve framegrenzen bepalen de exportlengte.

Onbekende projectversies worden geweigerd. De lezer controleert aantallen, IDs, bronbereiken, audioformaten en de totale bronruimte. Audio wordt uit het archief gelezen; er worden geen projectpaden naar het bestandssysteem uitgepakt. Opslaan gebruikt een tijdelijk bestand naast het doel en atomair vervangen. Pas na een geslaagde vervanging wordt de sessie als opgeslagen gemarkeerd.

Dit is het eigen projectformaat van SoundSausage. De begrensde `.ses`-import is een aparte lezer; zie [oudere sessies importeren](SES.md).

Versie 4 bewaart per spoor maximaal zestien effecten en 0–60 seconden uitklank.
Een effect heeft een onveranderlijk ID, type, JSON-instellingen en een bypassvlag.
VST3-instellingen bevatten een plug-in-ID, inhoudsvingerafdruk, parameterwaarden
en maximaal 1 MiB componentstatus als base64. Een project bevat geen uitvoerbaar
plug-inpad; de lokaal toegevoegde plug-in bepaalt het pad. Ontbrekende plug-ins
verhinderen het openen van de audio en instellingen niet, maar worden bij
afspelen/export gemeld. De keuze om een effect uit te schakelen is expliciet.
Oudere projectversies laden met lege spoorketens; oudere apps weigeren versie 4
zodat effecten niet stilzwijgend verdwijnen.
