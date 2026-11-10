# Controle van lange bestanden — 0.7.0

De lokale volledige suite doorstaat 208 controles, waarvan twee echte
Qt-audiobackendcontroles in de beperkte hostomgeving worden overgeslagen.
De aanvullende opslagcontroles toetsen ook de weigering van te grote metadata;
de complete distributiesuite bevat, met een controle van een gekoppelde werkmap,
210 controles.

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

De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42895623340)
doorstaat alle 210 controles in Debian, Fedora en Arch, inclusief virtuele audio.
De geïnstalleerde pakketten doorstaan ook de gewone en stille audiocontrole op
Ubuntu 26.04 en Ubuntu Rolling. [Release 0.7.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.7.0)
bevat de gecontroleerde pakketten.
Een hoorbare controle op een fysiek geluidsapparaat blijft open.
