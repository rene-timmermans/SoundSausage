# Tijd en toonhoogte — 0.12.0

Negen nieuwe controles toetsen duurverhoudingen van 0,25 tot 4, toonhoogte bij
−12, +7 en +12 halve tonen, Fine en Fast, stereobalans, stilte, exacte neutrale
verwerking, Preview-prefix, cueposities, Undo/Redo, annuleren en schijfopslag.
Een 440 Hz-toon behoudt zijn frequentie bij rek en komt bij een octaafverschuiving
op 220 of 880 Hz uit. De resulterende lengte is exact op hele uitvoerframes.
De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42996330974)
doorstaat alle 308 controles in Debian, Fedora en Arch. De geïnstalleerde pakketten
doorstaan gewone, afspeel- en opnamecontroles ook op Ubuntu 26.04 en Rolling.
De logs bevatten geen callback- of bufferfouten.
[Release 0.12.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.12.0)
bevat de geteste pakketten, broncode en checksums.

Rubber Band draait via zijn C API in offline-modus, met volledige analyse en
vaste invoerblokken van 4096 frames. Uitvoer wordt opgehaald tot maximaal het
gemelde beschikbare aantal, met een begrensde buffer. Preview voert dezelfde
analyse uit en levert hetzelfde prefix. Bij beëindigen of annuleren wordt
de native toestand altijd vrijgegeven. Grote resultaten staan op schijf.
Een tekort van meer dan één frame wordt als fout behandeld vóór bevestigen.

Een afzonderlijke lokale proef met 160 MiB synthetische stereo-audio en 110%
lengte gebruikte ongeveer 10,4 MiB extra resident geheugen en produceerde
23.068.672 frames. Dit betreft een stille proefopname en is geen universele
geheugengrens: analysemateriaal, native bibliotheek en duur beïnvloeden het gebruik.
Fine gebruikt R3, Fast R2; gekoppelde stereoverwerking en optioneel formantbehoud
volgen de [officiële integratierichtlijnen](https://breakfastquay.com/rubberband/integration.html).

De pakketten voegen Rubber Band toe als runtime-afhankelijkheid; de C API werkt
met zowel bibliotheekversie 3.3 als 4. Het programma blijft GPL-3.0-or-later.
