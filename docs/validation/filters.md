# EQ en filters — 0.9.0

De DSP- en Qt-controles toetsen de volledige EQ/filterketen:

- Bell-versterking op de middenfrequentie, tegengestelde bell-curves en shelf-
  eindpunten, middenfrequentie en monotoniciteit.
- Butterworth-afsnijding van ongeveer −3,0103 dB bij alle vier hellingen;
  toenemende verzwakking buiten de doorlaatband.
- Banddoorlaat en notch op hun middenfrequentie, inclusief DC-gedrag.
- Gemeten sinusversterking en de FFT van de native impulsrespons vergeleken
  met de complexe overdrachtsfunctie.
- Bitgelijke resultaten bij blokgroottes 1, 127 en een volledig blok, voor
  mono en stereo; Preview is een gelijk prefix van de volledige bewerking.
- Onafhankelijke stereostaat, exacte vlakke EQ, lage samplerates en frequenties
  nabij de grenzen; ongeldige of instabiele instellingen worden geweigerd.
- Selectie, behouden cueposities, Undo/Redo, F2, annuleren en float32-overflow
  zonder gedeeltelijke documentwijziging.
- Daadwerkelijke Qt-dialogen, presets, Reset, frequentiebereik, moduskeuze,
  blokkeren tijdens opname, modaal toepassen/annuleren en stoppen van Preview.

De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42983592249)
doorstaat alle 258 controles in Debian, Fedora en Arch, inclusief vier echte
Qt-audiobackendtests. De geïnstalleerde pakketten doorstaan gewone, afspeel- en
opnamecontroles ook op Ubuntu 26.04 en Rolling. Geen Python-callbackfouten zijn
in de geverifieerde logs gevonden. De
160 MiB-keten bevat nu ook tienbands-EQ en een 48 dB/oct-filter. De afzonderlijke
lokale meting bleef op ongeveer 20 MiB extra resident geheugen boven de geladen
toepassing; dit is een scenarioresultaat, geen universele geheugenlimiet.

De coëfficiënten volgen het [W3C Audio EQ Cookbook](https://www.w3.org/TR/audio-eq-cookbook/).
De C++-kernel gebruikt DSP-ABI 6, dubbelprecieze transposed direct form II en
aparte toestand per sectie/kanaal. De toestand leeft door over blokgrenzen en
begint opnieuw bij het begin van iedere selectie. Verwerking houdt de lengte
aan en is faseveranderend. Shelves gebruiken monotone slope S=1. Graphic EQ
gebruikt vaste Q=√2; overlappende banden beïnvloeden samen de responscurve.

[Release 0.9.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.9.0)
bevat de geteste installatiepakketten voor Debian/Ubuntu, Fedora en Arch, de
broncode en checksums.
