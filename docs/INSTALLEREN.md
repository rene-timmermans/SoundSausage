# Installeren

Download het pakket voor je distributie bij de
[releases](https://github.com/rene-timmermans/SoundSausage/releases).
De pakketten zijn voor **x86-64 / amd64**. De pakketbeheerder installeert Python,
Qt/PySide6 inclusief Multimedia en vertalingen, NumPy, libsamplerate en Rubber Band als afhankelijkheden; een compiler is niet nodig.

## Debian en Ubuntu

Het `.deb`-pakket is voor Debian 13 en Ubuntu 26.04 of nieuwer, met PySide6 6.8
of nieuwer uit de distributie. Ubuntu 24.04 en Debian 12 worden hiermee niet
ondersteund. Op Ubuntu moet de universe-pakketbron ingeschakeld zijn.

```bash
sudo apt install ./soundsausage_0.16.2-1_amd64.deb
```

## Fedora

Gebruik het `.rpm`-pakket voor de huidige Fedora-versie:

```bash
sudo dnf install ./soundsausage-0.16.2-1*.x86_64.rpm
```

## Arch Linux

Werk Arch eerst normaal bij en installeer dan het pakket:

```bash
sudo pacman -U ./soundsausage-0.16.2-1-x86_64.pkg.tar.zst
```

## Starten en controleren

Start **SoundSausage** via het toepassingenmenu of met `soundsausage`.
`soundsausage --selftest` controleert de installatie zonder geluid af te spelen.
`soundsausage --audio-selftest` controleert de ingestelde uitgang met een stil signaal.
Een nieuw pakket met dezelfde naam werkt een eerdere versie bij.

Elke release bevat de broncode en `SHA256SUMS`. De bouw controleert alle tests,
installeert de pakketten in Debian, Ubuntu, Fedora en Arch en controleert daar
de audiokern, bestandsopslag, iconen en effectvensters.

## Zelf bouwen

Zie de [README](../README.md) voor bouwen vanuit de broncode. De pakketdefinities
staan in `packaging/`. Een nieuwe versie krijgt releasepunten in
`docs/releases/<versie>.md`; na een versie-update op `main` bouwt GitHub Actions
de pakketten en publiceert ze bij de tag `v<versie>`, zodra alle controles slagen.
Bestaande releases worden niet overschreven.
