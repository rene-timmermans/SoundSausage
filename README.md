# SoundSausage

<img src="src/soundsausage/assets/soundsausage.png" width="64" alt="SoundSausage-icoon">

Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek waar je ze verwacht.

Bewerk losse opnamen of combineer meerdere sporen. De interface volgt je eigen Linux-thema en accentkleur.

![SoundSausage in golfvormweergave](docs/screenshots/layout-previews/dark-waveform.png)

De huidige versie is **0.27.0**.

## Wat het kan

**Werkruimte**

- Golfvormweergave voor één opname en multitrack voor meerdere sporen; wissel met **Tab** of de knoppen bovenaan.
- Compacte werkbalken en gegroepeerde menu's, met gereedschappen op vaste plekken en uitleg bij de knoppen.
- Inzoomen tot afzonderlijke samples, afspelen in een lus en een frequentieanalyse van het gekozen fragment.
- Transport, grote klok, selectie- en weergavetijden en een stereometer met dB-schaal en piekindicatie.
- Lichte en donkere Linux-thema's, de accentkleur van het bureaublad en vensters die met taal en lettergrootte meegroeien.

**Opnemen en bewerken**

- Mono of stereo opnemen via een microfoon of audio-interface, met keuze van ingang en uitgang, live golfvorm en niveaus.
- Systeemgeluid opnemen van de standaarduitgang, bijvoorbeeld muziek uit een browser, met Systeemgeluid (wat je hoort).
- Opnemen naar een nieuwe golfvorm, invoegen bij de cursor, een selectie vervangen of een nieuwe clip op een spoor maken.
- Pauzeren, hervatten en een take in één stap ongedaan maken; een kort opnamebegin overslaan om inschakeltikjes te vermijden.
- Selecteren, knippen, kopiëren, plakken, mengen en trimmen, met ongedaan maken en opnieuw.
- Links en rechts afzonderlijk knippen, plakken, tijdrekken en opnemen; het andere kanaal blijft op zijn plaats.
- Samplepunten verslepen of hun waarde exact invoeren om kleine tikjes plaatselijk te corrigeren.
- Met de potloodknop rechtstreeks op de golfvorm tekenen, ook bij minder vergroting, met één stap ongedaan maken.

- Markeringen toevoegen, benoemen, verplaatsen en bezoeken, met een markeringenlijst en behoud bij opslaan.

**Effecten en geluid**

- Remaster vermindert het wegzakken van stemmen en instrumenten bij sterke drums, met vergelijking op gelijk luistervolume en apart herstel voor korte volumedalingen.
- Versterken, fades, normaliseren en ompolen; kanaalmixer, dynamiekbewerking en een bewerkbaar volumeverloop.
- Grafische en parametrische EQ, hoog- en laagdoorlaat, banddoorlaat en notchfilters, met frequentiegrafieken.
- Delay, echo en galm, met presets, luistervoorbeelden en optionele uitklank.
- Ruisprofielen leren en bewaren, vaste of wisselende achtergrondruis verminderen met instelbaar detailbehoud, en korte tikken herstellen.
- Speelduur en toonhoogte onafhankelijk aanpassen, met formantbehoud voor zang.
- Soft clip, hard clip, wavefold en bit crush; convolutie met een impulsrespons.
- Effectinstellingen beluisteren voordat je ze toepast en bewerkingen ongedaan maken.

**Multitrack en plug-ins**

- Tot 32 sporen combineren; clips verplaatsen, trimmen en dupliceren, met volume, pan, mute en solo.
- Volume- en panlijnen tekenen op clips en realtime spoorketens bewerken, met volgorde, bypass en uitklank.
- Native Linux VST3-, LV2- en LADSPA-effecten gebruiken, met eigen plug-invensters waar ondersteund.
- Plug-ininstellingen in het project bewaren en gerapporteerde plug-invertraging automatisch compenseren bij afspelen en eindmix.
- Andere sporen beluisteren tijdens opnemen, met samen pauzeren en stoppen, opnamekalibratie en automatische klokdriftcorrectie.
- Punch-in/out: een passage opnieuw opnemen met voorloop en korte overgangen, met behoud van de oorspronkelijke audio.

**Bestanden en herstel**

- WAV en MP3 openen, bewerken en opslaan; kiezen tussen WAV en MP3 voor selectie-export en eindmix.
- Bestandsinformatie bewaren, waaronder ondersteunde WAV-labels en cuepunten en MP3-tekst en hoesafbeeldingen. Hoofdstukken volgen audiobewerkingen; verouderde MP3-meetgegevens vervallen.
- Projecten bewaren met de gebruikte audio, clips, lijnen en effecten; na heropenen blijven de sporen afzonderlijk bewerkbaar.
- Lange opnamen bewerken met opslag op schijf, voortgang en annuleren, en werk herstellen na onverwacht afsluiten.

**Hulp**

- Een volledige, doorzoekbare handleiding in vijf talen via **Help → Handleiding** en **F1**, ook zonder internet.
- Uitleg van alle beschikbare functies en effecten, hun instellingen en praktische voorbeelden.

Lees de [handleiding](docs/HANDLEIDING.md) voor de bediening en praktische uitleg.

## Installeren

Download het pakket voor jouw distributie bij de nieuwste
[release](https://github.com/rene-timmermans/SoundSausage/releases/latest).
De pakketbeheerder installeert de benodigde onderdelen automatisch mee; een compiler is niet nodig.
Daarna staat SoundSausage in het toepassingenmenu, of start je het met `soundsausage`.

Voer het installatiecommando uit in de downloadmap en vervang `<versie>` door het versienummer op het pakket.

| Distributie | Installeren | Verwijderen |
|---|---|---|
| Arch Linux | `sudo pacman -U ./soundsausage-<versie>-1-x86_64.pkg.tar.zst` | `sudo pacman -R soundsausage` |
| Debian 13, Ubuntu 26.04 of nieuwer | `sudo apt install ./soundsausage_<versie>-1_amd64.deb` | `sudo apt remove soundsausage` |
| Fedora | `sudo dnf install ./soundsausage-<versie>-1.*.x86_64.rpm` | `sudo dnf remove soundsausage` |

De pakketten zijn voor **x86-64 / amd64** en worden bij iedere release gebouwd, geïnstalleerd en getest.
Ubuntu 24.04 en Debian 12 worden niet ondersteund. Op Ubuntu moet de universe-pakketbron ingeschakeld zijn.
Zie [installeren](docs/INSTALLEREN.md) voor meer uitleg en bouwen vanuit de broncode.

## Taal

SoundSausage is er in het Nederlands, Engels, Duits, Frans en Spaans.
Kies een andere taal via **Opties → Taal**. Menu's, vensters en de geopende handleiding veranderen direct mee;
de keuze blijft bij de volgende start bewaard. De volledige handleidingen zijn ook rechtstreeks te lezen:
[Nederlands](docs/HANDLEIDING.md), [English](docs/manual/en.md), [Deutsch](docs/manual/de.md),
[Français](docs/manual/fr.md) en [Español](docs/manual/es.md).

## Wat er nieuw is

**[0.27.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.27.0)** Remaster herstelt ook diepe, korte volumedalingen, met een aparte instelling en preset.

**[0.26.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.26.0)** Remaster met origineel/voorbeeld-vergelijking en een markereditor voor golfvormen en sessies.

**[0.25.2](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.25.2)** Vloeiender afspelen in volledig scherm en bij grote golfvormvensters. De venstergrootte en positie blijven bij de volgende start behouden.

**[0.25.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.25.1)** Een lege werkruimte blijft leeg; de overbodige startmelding verschijnt niet meer over de golfvorm.

**[0.25.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.25.0)** Systeemgeluid opnemen van de standaarduitgang, met bronkeuze in Audioapparaten en het opnamevenster, stereo en pauzeren/hervatten.

**[0.24.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.24.0)** Automatische uitklank en langere galm/echo. Soepele selectieranden bij EQ en filters. Vorige/Volgende bladeren door handleidingonderwerpen; werkbalk- en afspeeliconen gebruiken de themakleur op neutrale knoppen.

**[0.23.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.23.0)** Adaptieve ruisreductie volgt wisselende achtergrondruis. Detailbehoud en nieuwe presets geven meer controle over zachte geluiden. Alle vijf handleidingen hebben een klikbare inhoudsopgave.

**[0.22.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.22.0)** Links en rechts afzonderlijk knippen, plakken, tijdrekken en opnemen. Het andere kanaal blijft op zijn plaats; gemengd plakken kan voorbij het einde.

**[0.21.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.21.0)** MP3-hoofdstukken volgen audiobewerkingen. Achterhaalde meetgegevens worden opgeschoond; WAV-bestandsinformatie wordt bij MP3-export duidelijk afgehandeld.

**[0.20.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.20.0)** Golfvormen rechtstreeks tekenen, ook bij minder vergroting. De zoom bepaalt hoeveel samples tegelijk veranderen, tot één seconde per groep. Afzonderlijke samplepunten verschijnen al bij minder ver inzoomen.

**[0.19.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.1)** Het programma-icoon met paarse achtergrond verschijnt ook in de titelbalk van het hoofdvenster en losse vensters.

**[0.19.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.19.0)** Eigen plug-invensters en LV2- en LADSPA-effecten. Automatische compensatie van plug-invertraging, opnamekalibratie en klokdriftcorrectie. Punch-in/out met voorloop, korte overgangen en behoud van de oorspronkelijke audio.

**[0.18.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.18.0)** Directe samplebewerking: punten verslepen of exacte waarden invoeren, per kanaal en met ongedaan maken.

**[0.17.2](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.2)** Twee dunne randen sluiten de linker golfvorm af en openen de rechter golfvorm, binnen de breedte van het tekenvlak.

**[0.17.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.1)** Volledig vertaalde WAV-/MP3-formaatkeuze bij opslaan. Het opnamevenster toont de instellingen die bij de gekozen bestemming horen.

**[0.17.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.17.0)** MP3 openen en bewerken, met WAV- of MP3-uitvoer voor opnamen, selecties en eindmixen. Tekst en hoesafbeeldingen blijven behouden. Een instelbaar opnamebegin overslaan met een korte fade-in.

**[0.16.2](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.2)** De astitels bij Dynamiekbewerking en Volumeverloop volgen de linkermarge van het venster.

**[0.16.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.1)** Leesbare grafiekassen, kanaallabels en tijdvelden bij grotere letters. Vensters passen zich aan taal en lettergrootte aan; de statusbalkkeuze blijft bewaard.

**[0.16.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.16.0)** Interface in vijf talen, met taalkeuze onder Opties. De doorzoekbare offline handleiding volgt de gekozen taal, ook als ze al openstaat.

**[0.15.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.15.0)** Realtime spoorketens met bypass en volgorde, Linux VST3-effecten met opgeslagen instellingen en opnemen met begeleiding. Samen pauzeren en dezelfde effecten bij afspelen en eindmix.

**[0.14.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.14.0)** Links en rechts afzonderlijk selecteren en bewerken, met kanaalkeuze en luistervoorbeelden. Een doorlopende golfvorm tijdens zoomen en verschillende zoomiconen.

**[0.13.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.13.0)** Vier vervormingsvormen met presets en instelbare menging. Convolutie met WAV-impulsresponsen en optionele uitklank.

**[0.12.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.12.0)** Speelduur aanpassen met behoud van toonhoogte en toonhoogte verschuiven met behoud van duur. Tempoverhouding, kwaliteitskeuze en formantbehoud voor zang.

**[0.11.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.11.0)** Ruisprofielen opnemen, bewaren en opnieuw gebruiken. Ruisreductie met stereokoppeling en een luistervoorbeeld, plus herstel van korte tikken.

**[0.10.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.10.0)** Delay met tijden per kanaal, echo met feedback, demping en stereopingpong, en galm met ruimtegrootte, nagalmtijd en stereobreedte. Presets, luistervoorbeelden en optionele uitklank.

**[0.9.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.9.0)** Grafische en parametrische EQ en hoogdoorlaat-, laagdoorlaat-, banddoorlaat- en notchfilters. Frequentiegrafieken, presets en luistervoorbeelden.

**[0.8.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.8.0)** Mono- en stereo-opname met ingangskeuze, live golfvorm en niveaus. Pauzeren, veilig stoppen, herstel van onderbroken opnamen en een afspeelcursor die na Stop op zijn positie blijft.

**[0.7.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.7.0)** Lange opnamen met opslag en verwerking in blokken, voortgang en annuleren. Herstel na onverwacht afsluiten en behoud van WAV-bestandsinformatie en cuepunten.

**[0.6.1](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.6.1)** Een volledige, doorzoekbare Nederlandstalige handleiding via Help en F1, ook zonder internet.

**[0.6.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.6.0)** Geïntegreerd afspelen met apparaatkeuze, pauzeren en synchronisatie van geluid, cursor en meters. Verschillende samplerates combineren en omzetten, met ongedaan maken.

**[0.5.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.5.0)** Kanaalmixer, Dynamiekbewerking en Volumeverloop, luistervoorbeelden bij alle Amplitude-effecten en DC-offset verwijderen bij normaliseren. Installatiepakketten voor Debian/Ubuntu, Fedora en Arch.

## Licentie

SoundSausage is vrije software onder de [GNU General Public License v3.0 of later](LICENSE).
