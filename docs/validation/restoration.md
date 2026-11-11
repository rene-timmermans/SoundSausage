# Restauratie — 0.11.0

Vijftien nieuwe controles meten ruisvermindering, klikinterpolatie, stereo,
profielen, dialoogbediening, blokgrenzen, Preview, Undo/F2 en annuleren.
Een test met een toon van 440 Hz en onafhankelijke constante witte ruis vereist
minstens 6 dB betere signaal-ruisverhouding; de lokale proef geeft ruim 9 dB.
Dit is een synthetische meting en geen kwaliteitsgarantie voor alle opnamen.
Het verwijderde signaal plus het schone resultaat reconstrueert de bron,
inclusief de randen. Nulreductie is bitgelijk aan de bron. Een schone sinus
blijft bij Click Removal ongewijzigd; ingevoegde korte impulsen worden hersteld.

Ruisreductie gebruikt een vaste STFT-grid, overlap-add met gewichtsnormalisatie,
gemiddeld profielvermogen, spectrale verzwakking en aflopende gain-smoothing.
Preview gebruikt ook de benodigde context ná zijn eindpunt, zodat het exact
hetzelfde prefix geeft. Het profiel is begrensd tot 30 seconden en 8192 FFT-
punten. De uitvoer gebruikt bij grote bestanden schijfopslag. De werkstaat
is onafhankelijk van de opnamelengte. De grote-uitvoertest overschrijdt de
geheugendrempel en controleert een memmapresultaat.

Click Removal vergelijkt lokale sprongen met de omliggende afgeleide, zoekt
tegengestelde randen van maximaal 2 ms en interpoleert tussen stabiele ankers.
Overlappende leescontext voorkomt verschillen op blokgrenzen. Dit is geen
herstelalgoritme voor langdurig gekraak of clipping. Profielbestanden zijn
begrensde, strikt gevalideerde JSON-data; mislukte opslag behoudt een bestaand
bestand. Er worden geen modules of scripts uit profielen uitgevoerd.

De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42994477512)
doorstaat alle 299 controles in Debian, Fedora en Arch. De geïnstalleerde
pakketten doorstaan gewone, afspeel- en opnamecontroles ook op Ubuntu 26.04
en Rolling. De logs bevatten geen callbackfouten.
[Release 0.11.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.11.0)
bevat de geteste pakketten, broncode en checksums. DSP-ABI blijft 7; de nieuwe spectrale verwerking
gebruikt de bestaande NumPy-afhankelijkheid.
