# Vijf interfacetalen — 0.16.0

De interface ondersteunt Nederlands, Engels, Duits, Frans en Spaans. Dertien
nieuwe integratiecontroles toetsen de taalkeuze, exclusieve menumarkering,
QSettings en een nieuwe processtart, live vertalen van alle zestien effectvensters,
standaardknoppen, tijdelijke voorbeeldknoppen, bestandsfilters, meldingen en Over.
De geopende offline handleiding wisselt mee en blijft doorzoekbaar. Iedere
handleiding beschrijft bestanden, herstel, opnemen, selectie, alle effectgroepen,
multitrack, VST3, begeleiding, sneltoetsen en praktische grenzen.

De tests vergelijken audio, Undo, kanaalselectie, effectinstellingen, combowaarden
en audio-objecten vóór en na taalwissels. Bestandsnamen en externe namen blijven
behouden. Verwijderde vensters ontvangen geen latere taalcallbacks. Menu's en
knoppen worden ook gerenderd, met behoud van de desktopaccentkleur.

De catalogus bevat 1.250 bronvormen per taal. De catalogusbouwer controleert
ontbrekende teksten en overeenkomende placeholders. Technische eenheden,
sneltoetsen, bestandsgegevens en externe namen blijven letterlijk. Engelse
bronlabels zijn interne sleutels; bediening en projectgegevens hangen niet af
van de vertaalde zichtbare tekst. Qt-standaardteksten gebruiken de vertalingen
van de distributie.

Lokaal doorstaat de volledige suite 376 controles, waarvan zes expliciete
hardwarebackendcontroles worden overgeslagen. De gewone zelftest controleert
alle vijf catalogi, Qt-vertalingen en volledige handleidingen, ook vanuit de
geënsceneerde installatie. De distributiebouw doorstaat alle 376 controles in Debian, Fedora en Arch,
inclusief de zes virtuele audiobackendcontroles. De geïnstalleerde pakketten
slagen voor de gewone, afspeel-, opname- en duplexzelftest op alle vijf doelen,
inclusief Ubuntu 26.04 en Rolling. Alle vijf logs en de publicatielog zijn
gecontroleerd; er zijn geen onverwachte callback-, RuntimeError- of bufferfouten.
[Distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/43038246038)
en [release 0.16.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.0)
bevatten de controles en geteste installatiepakketten.
DSP-ABI 7 en projectformaat 4 blijven behouden.

Qt-vertaalpakketten: [Debian](https://packages.debian.org/trixie/qt6-translations-l10n),
[Fedora](https://packages.fedoraproject.org/pkgs/qt6-qttranslations/qt6-qttranslations/),
[Arch](https://archlinux.org/packages/extra/any/qt6-translations/).

Qt-vertalingen worden zowel op het door Qt gemelde pad als in de gedeelde
Qt6-datamappen gezocht. Een regressiecontrole simuleert een binding met een
niet-bestaand privaat pad. Dit dekt distributies die vertalingen apart in
`/usr/share/qt6/translations` installeren.

De Fedora-testcontainer installeert alle talen in plaats van uitsluitend Engels.
De Ubuntu-controles gebruiken de actuele kernel.org-mirror met de oorspronkelijke
Ubuntu-suites en archive-keyring. De pakketondertekening en alle controles blijven
actief. De mirrorhost wordt op de runner opgelost en in de container doorgegeven.
