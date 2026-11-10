# Controle van lange bestanden — 0.7.0

De lokale volledige suite doorstaat 208 controles, waarvan twee echte
Qt-audiobackendcontroles in de beperkte hostomgeving worden overgeslagen.
De aanvullende opslagcontroles toetsen ook de weigering van te grote metadata;
de complete distributiesuite bevat daardoor 209 controles.

Gecontroleerd:

- Een stereo-opname van 136 MiB: WAV lezen, Amplitude, Undo/Redo, projectopslag,
  heropenen en een fragment mixen met behoud van bronmetadata.
- Alle Amplitude-bewerkingen bij blokgroottes van 1, 37, 256 en 10.000 frames,
  vergeleken met dezelfde verwerking als één geheel, inclusief Preview.
- Samplerateconversie met doorlopende filterstaat bij zeer kleine blokken.
- Annuleren tijdens verwerking, golfvormvoorbereiding, WAV- en projectopslag.
- Behoud van documentstand, selectie, geschiedenis, oude bestanden en opgeslagen status.
- Tekst, cues en labels bewaren; posities bij edits, trimmen, reverse en conversie;
  knippen/plakken met unieke cue-identifiers; RF64-header en lezen.
- Abrupt beëindigde aparte processen, opnieuw herstellen na een tweede crash,
  bestaande bronnen ongewijzigd, actieve instanties overslaan en padvalidatie.
- Echte Qt-vensters voor annuleren, de levensloop van herstelkopieën en navigatie
  voorbij de 32-bit framegrens; controle vanuit een losse installatiemap.

De [geheugenmeting](long-files-memory.json) volgt 160 MiB synthetische audio door
openen, Normalize, golfvorm, bewaren, multitrack, project-I/O, herstelkopie en
codering voor afspelen. De lokale extra resident geheugengroei bleef ongeveer
17 MiB boven de geladen toepassing. Dit resultaat geldt voor deze test; metadata,
kleine buffers, projectaantallen en de audiobackend beïnvloeden werkelijk gebruik.
De automatische regressiecontrole bewaakt voor dit scenario een marge van 80 MiB.

De distributiebouw voert de volledige suite, inclusief virtuele audio, opnieuw
uit en controleert de geïnstalleerde Debian/Ubuntu-, Fedora- en Arch-pakketten.
Een hoorbare controle op een fysiek geluidsapparaat blijft open.
