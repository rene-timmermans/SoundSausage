# Onderzoek voor SoundSausage

Het doel is zo veel mogelijk oorspronkelijke functies en bediening te behouden.

Een native Linux-herimplementatie lijkt technisch haalbaar. De aangeleverde installatie bevat een duidelijke scheiding tussen het hoofdprogramma, effecten en bestandsfilters. Er is genoeg informatie om de bediening en belangrijke interfaces te specificeren. Dit onderzoek bewijst nog geen identieke geluidsverwerking of compatibiliteit met bestaande projecten.

De REA-skills zijn gebruikt voor onderzoeksopzet, afbakening en bewijsrapportage. Er waren geen REA-MCP-tools verbonden. De daadwerkelijke analyse is uitgevoerd met de reeds aanwezige Ghidra 12.1.2, objdump, winedump en Python. Geen van de onderzochte Windows-programma's of plug-ins is gestart.

**Bronnen en identiteit**

| Onderdeel | Direct waargenomen |
| --- | --- |
| Installatiemateriaal | `/home/deck/CoolEdit`; 18 bestanden buiten sessiemetadata |
| Installer | `setup.exe`, 4.151.990 bytes, PE32/x86; niet als archief te openen met de aanwezige 7-Zip |
| Geïnstalleerde toepassing | `/home/deck/.wine/drive_c/coolpro/coolpro.exe`, 1.466.880 bytes, PE32/x86 |
| PE-tijdstempel hoofdprogramma | 18 juli 1997; een bestandsveld, geen onafhankelijk geverifieerde bouwdatum |
| Versievelden | Twee version-resources: onder andere `1, 97, 212,9` en `1, 0, 0, 2`; het precieze commerciële versielabel is hiermee niet eenduidig vastgesteld |
| Effecten | 32 `.xfm`-bestanden, Windows-DLL's |
| Audiofilters | 19 `.flt`-bestanden, Windows-DLL's |
| Overige onderdelen | 2 `.ax`-bestanden, `cooltips.exe`, `msvbvm50.dll`, WinHelp en vijf `.scp`-bestanden |

Bronnen: [inventaris](evidence/pe/inventory.json), [hoofdprogramma](evidence/pe/coolpro.exe.json), [installer](evidence/pe/setup.exe.json), [herkomst en controle](evidence/provenance.json). De SHA-256-hashes van alle 57 onderzochte PE-bestanden zijn vastgelegd en na de analyse opnieuw gecontroleerd.

Elf bestanden op het installatiemedium zijn leeg. Daaronder vallen `Manual/cep1man.pdf`, `Manual/license.txt`, alle aangetroffen voorbeeldaudio, `Robbie.pk` en de meegeleverde derde-partijdemo's. Die bestanden leveren geen documentatie, luistermateriaal of bruikbare piekcache op. Er is geen broncode aangetroffen in de geïnventariseerde mappen. De geïnstalleerde `coolpro.hlp` en de bijbehorende inhoudsopgave zijn wel gevuld; de helptekst zelf is in deze analyse niet gedecomprimeerd. De [inhoudsopgave](evidence/help-contents.txt) is bewaard.

**Opbouw van het programma**

`coolpro.exe` bevat 137 benoemde exports. De importtabel verwijst naar Win32-vensters en GDI, bestands- en threadfuncties, WinMM, shellfuncties en OLE. WinMM-imports omvatten `waveInOpen`, `waveOutOpen`, bufferfuncties, MIDI-invoer en MIDI-uitvoer. Dit onderbouwt de aanwezigheid van deze interfaces; de importtabel toont geen daadwerkelijke uitvoering.

Het hoofdprogramma importeert geen Visual Basic-runtime. `cooltips.exe` importeert juist `MSVBVM50.DLL`. De conclusie dat de audiotoepassing een native Windows-programma is en het tipsprogramma Visual Basic gebruikt, heeft hoge zekerheid op basis van de PE-structuur en imports. De oorspronkelijke programmeertaal is niet met broncode bevestigd.

De effectscanner op VA `0x004bf880` zoekt `*.xfm`, vraagt `QueryXfm` op en verwerkt modulebeschrijvingen. De bestandsfilterscanner op VA `0x004c0150` doet hetzelfde met `*.flt` en `QueryCoolFilter`. De statische code bevat caches `xfm.dat` en `flt.dat`; dit zijn modulecatalogi, geen aangetoonde sessieformaten. De gedecompileerde code beschrijft mogelijke uitvoering en is geen runtimewaarneming. Zie [gerichte decompilatie](evidence/coolpro-decompiled.txt).

| Laag | Aanwijzingen in de onderzochte bestanden | Gevolg voor Linux |
| --- | --- | --- |
| Bediening | Menu's, dialogen, accelerators, Win32/GDI-imports | Desktopinterface opnieuw implementeren met dezelfde werkmodi en commando's |
| Individuele golfvorm | Knippen, plakken, Mix Paste, selectie, conversie en effectaanroepen | Een eigen document- en bewerkingsmodel maken |
| Multitrack | Sessiemenu, clipbewerkingen, trackinstellingen, envelopes en `_MixDownThread@4` | Tijdlijn, clipreferenties, mixer en achtergrondwerk apart modelleren |
| Effecten | Modulemetadata, initialisatie, instellingen, verwerking en callbacks | Nieuwe native effecten achter een eigen interface |
| Bestands-I/O | Filterdetectie, openen, lezen, schrijven en metadatafuncties | Standaardformaten plus expliciete compatibiliteitsadapters |
| Opslag en undo | UI-instellingen voor cache, tempbestanden, undo en peakfiles | Onderzoek ondersteunt een model met blokopslag en piekcaches; exacte oorspronkelijke opslagstructuren zijn nog onbekend |
| Automatisering | Tekstuele `.scp`-scripts met selectie, commando's en parameters | Menu, sneltoets, batch en script op dezelfde commandolaag aansluiten |

De oorspronkelijke Win32-DLL's kunnen niet rechtstreeks als native Linux-plug-ins worden geladen. Een Linux-versie vraagt om nieuwe implementaties van de betreffende onderdelen. Dit onderzoek bevat geen oorspronkelijke C/C++-broncode.

**Effectinterface: een concreet gevolgde route**

Voor `Amplify.xfm` zijn de zes interfacefuncties gericht gedecompileerd. De exports en hun adressen zijn bovendien onafhankelijk met winedump gecontroleerd.

| Functie | VA in Amplify.xfm | Statische bevinding |
| --- | --- | --- |
| `QueryXfm` | `0x100011e0` | Schrijft categorie, naam, beschrijving, mogelijkheden, parameterbeschrijving en benodigde toestandsruimte |
| `XfmInit` | `0x10001350` | Initialiseert een toestand die via de hostcontext bereikbaar is |
| `XfmSetup` | `0x100013c0` | Opent Win32-dialoogresource 500 |
| `XfmDo` | `0x10001800` | Leest audioblokken, voert versterking/fadeverwerking uit en schrijft blokken terug |
| `XfmDestroy` | `0x10001390` | Verwerkt het afsluiten van de effecttoestand |
| `XfmUpdate` | `0x100013f0` | Werkt verwerkingsparameters bij, waaronder fadeverloop |

Bronnen: [Amplify-decompilatie](evidence/amplify-decompiled.txt), [exports](evidence/amplify-exports-winedump.txt), [lees-callback in assembler](evidence/amplify-read-callback-asm.txt), [schrijf-callback in assembler](evidence/amplify-write-callback-asm.txt).

De hostfunctie `_OpenXfmEx@24` op VA `0x004a7740` selecteert een effect en bereidt een context voor. `_DoXfm@16` op VA `0x004a7ba0` stelt het selectiebereik in en roept `XfmDo` aan. Dat vormt samen met de modulecode een gevolgde keten van host naar effect en audio-I/O.

De volgende contextvelden zijn **afgeleide veldbetekenissen** uit die code en assembler, geen gepubliceerde SDK-definitie:

| Byte-offset | Waarschijnlijke betekenis | Onderbouwing |
| --- | --- | --- |
| `0x00` | Kanaalaantal | Host vult mono/stereo in; effect onderscheidt 1 en 2 |
| `0x02` | Samplebreedte | Host behandelt 8, 16 en 32 |
| `0x04` | Bytes per audioframe | Host berekent samplebreedte / 8 maal kanaalaantal |
| `0x08` | Samplerate | Host vult de aangeboden rate in |
| `0x0c` | Handle naar effecttoestand | Effect gebruikt `GlobalLock` |
| `0x10`, `0x14` | Begin en inclusief einde van verwerking | Host vult bereik in; Amplify berekent lengte als einde minus begin plus één |
| `0x148`, `0x14c` | Lees- en schrijf-callback | Modulehulpfuncties doen indirecte aanroepen op deze offsets |
| `0x150`, `0x152` | I/O-vlaggen | Modulehulpfuncties combineren deze met aanroepvlaggen |
| `0x154` | Opaque host/audiohandle | Wordt als argument aan de callbacks doorgegeven |
| `0x19c` | Modulehandle | Host gebruikt deze voor `GetProcAddress` |

Dit is een aanknopingspunt voor verdere compatibiliteitsanalyse. Het is nog geen complete, geteste ABI. De precieze parametercodes, alle vlaggen en randgevallen zijn niet vastgesteld. Voor de Linux-kern heeft een nieuwe, expliciete interface met 64-bits frameposities de voorkeur.

**Bediening als herbruikbare specificatie**

De resources leveren 193 verschillende benoemde statische menucommando's en 123 acceleratorregels over vier tabellen op. Die 123 regels bevatten alternatieven en varianten; het zijn geen 123 verschillende gebruikersfuncties. Er zijn 117 dialoogtemplates uit toepassingsonderdelen en daarnaast vier uit de Visual Basic-runtime uitgelezen. Alle 121 templates zijn zonder parsefout verwerkt, inclusief control-ID's, teksten, stijlen en coördinaten in dialoogeenheden.

Dit is vastgelegd in [ui-spec.json](evidence/ui-spec.json), [leesbare menu's](evidence/menus.txt) en [sneltoetsregels](evidence/shortcuts.json). Het zijn statische resources. Sommige menuvarianten kunnen voor oudere of geïntegreerde uitvoeringsmodi zijn bedoeld; hun aanwezigheid bewijst niet dat ze in de huidige uitvoering zichtbaar zijn. Effectmenu's worden bovendien deels dynamisch opgebouwd en vallen niet volledig onder het aantal 193.

Er zijn aparte menu's voor golfvormbewerking (`COOLMENU`) en multitrack (`COOLMTM`). De resources bevatten onder meer:

- Golfvorm- en spectrale weergave, kanaalselectie, nauwkeurige selecties, zero crossings en zoom.
- Knippen/kopiëren/plakken, Mix Paste, trimmen, reverse, inverteren, sampletypeconversie en undo.
- Multitracksessies, clipgrenzen, splice/rejoin, takes, punch-in, crossfades, loop duplicate en mixdown.
- Trackvolume, pan, mute, solo, opnamekeuze en apparaatkeuze per track.
- Volume- en pan-envelopes, cue- en playlist, meters en meerdere tijdweergaven.
- Scripts/batch, favorieten, MIDI-triggering en SMPTE-instellingen.

Een representatief effectvenster is Amplify: 40 controls, met begin- en eindversterking, lineaire/logaritmische fades, links/rechts-koppeling, DC-bias, piekniveau, dB-weergave en preview. Dit biedt veel meer houvast dan alleen de naam van een effect. Klikgedrag, focus, muisinteractie en de werkelijk getoonde standaardwaarden vereisen nog observatie van de toepassing.

**Volledige aangetroffen effectinventaris**

De groepering hieronder is een interpretatie van namen en dialoogteksten. Alleen Amplify is in deze ronde op verwerkingscode gevolgd; gelijke namen betekenen nog geen identieke algoritmen.

| Groep | Modules |
| --- | --- |
| Niveau en kanalen | `Amplify`, `Normal`, `Envelope`, `Chanmix` |
| Dynamiek en vervorming | `Dynamics`, `Distort` |
| Vertraging, ruimte en modulatie | `Delay`, `Echo`, `Chamber`, `Reverb`, `Chorus`, `Flange`, `multitap`, `sweeper` |
| Filters, equalizers en convolutie | `Filter`, `Scifilt`, `Qfilt`, `Neweq`, `para`, `Dtmffilt`, `Convolve` |
| Restauratie | `Noclick`, `Nohiss`, `Nonoise` |
| Tijd en samplerate | `Resample`, `Stretch` |
| Generatie | `Noise`, `Tones`, `Dtmf`, `Wavesync` |
| Analyse | `Stats` |
| Externe effecten | `ami` |

`Stretch` biedt volgens de dialoog tijdrekken met behoud van toonhoogte, pitchshift met behoud van tempo en resampling. `Nonoise` bevat profielinvoer/-uitvoer, profielopname uit een selectie, FFT-grootte, precisie, smoothing en een optie om alleen de verwijderde ruis te behouden. `ami.xfm`, de `.ax`-exports en de helpinhoud wijzen op ActiveMovie/DirectX-integratie; die integratie is niet uitgevoerd.

**Bestanden en een belangrijke WAV-valkuil**

`wavepcm.flt` is gericht gedecompileerd. `QueryCoolFilter` op VA `0x10001010` identificeert Windows PCM/WAV. Het filter exporteert onder meer openen/lezen/zoeken, openen/schrijven/sluiten en functies voor aanvullende bestandsmetadata. De code van `FilterUnderstandsFormat` accepteert formaatcodes 1 en 3. Dat is een statische bevinding; er zijn geen bestanden door dit filter verwerkt.

De dialoog heet `32-bit Floating Point Formatting` en vermeldt letterlijk de varianten `24-bit (type 1 - 24.0)`, `32-bit (type 1 - 16.8)` en `32-bit (normalized) (type 3 - 0.24)`. Het leespad voor genormaliseerde floats vermenigvuldigt met 32768; het schrijfpad gebruikt 1/32768. Er zijn daarnaast factoren 1/256 en 256 in een ander conversiepad. De constanten zijn rechtstreeks uit het PE-bestand gelezen en aan de gedecompileerde aanroepen gekoppeld.

**Gevolg:** de historische floatvarianten moeten apart worden herkend en met referentiebestanden worden getest. Het label 24-bit mag hier niet zonder controle worden behandeld als een gebruikelijk gepakt 24-bits PCM-bestand. Ook de interne amplitudeschaal mag bij een nieuwe DSP-kern niet ongemerkt veranderen. Bron: [WAV-decompilatie](evidence/wavepcm-decompiled.txt) en [filterresources](evidence/pe/wavepcm.flt.json).

De overige filters omvatten onder andere AIFF, AU, IFF, VOC, raw PCM, ADPCM, tekst en oudere spraak-/samplerformaten. Hun exporttabellen zijn geïnventariseerd, hun decoders zijn niet inhoudelijk geverifieerd. Beschikbaarheid van een filter bewijst niet dat alle formaten op deze machine werken.

`.ses`-sessies worden door menu's en hostcode bevestigd, maar de binaire veldindeling is nog niet vastgesteld. Er zijn geen gevulde voorbeeldsessies aangetroffen in de opgegeven mappen. Ook het `.pk`-formaat is niet ontleed; het aangeleverde voorbeeld is leeg. Er kan dus nog geen betrouwbare projectimport of -export worden beloofd.

**Scripts**

De vijf `.scp`-bestanden zijn leesbare tekst. Voorbeelden gebruiken `Collection:`, `Title:`, `Description:`, `Mode:`, `Selected:`, `cmd:`, genummerde parameters en `End:`. `cfade.scp` combineert Amplify, Copy, Paste Special en Delete. De scripts bieden daardoor concrete workflows voor latere acceptatietests.

Selecties zijn uitgedrukt met een schaal en samplerate. De exacte betekenis van modi, afronding en selectie-eindpunten moet nog worden vergeleken met het originele programma. Er is een inventaris van scripttitels en commando's opgenomen in `ui-spec.json`; een scriptinterpreter is nog niet gebouwd.

**Zekerheid en resterende vragen**

| Conclusie | Zekerheid en grens |
| --- | --- |
| Native 32-bits Windows, modulaire XFM/FLT-opbouw | Hoog: PE-structuren, imports, exports en host/modulecode |
| Golfvorm- en multitrackbediening aanwezig | Hoog voor de aanwezige resources; werkelijk gedrag nog niet waargenomen |
| Effectverwerking via hostcontext en callbacks | Hoog voor de gevolgde Amplify-route; volledige ABI nog onvolledig |
| Bijzondere float-WAV-schaling | Hoog voor de gevonden code en constanten; interoperabiliteit nog niet getest |
| Opnieuw bouwen met herkenbare bediening | Technische inschatting op basis van de inventaris; geen gerealiseerd product |
| Identiek klinkende geavanceerde effecten | Onbekend; vooral restauratie, reverb en stretching vragen vergelijkende audiotests |
| `.ses` en `.pk` compatibiliteit | Onbekend; veldindelingen en roundtrips ontbreken |

Ghidra's automatische analyse van het hoofdprogramma bereikte de ingestelde limiet van 120 seconden. Gerichte exports zijn daarna wel gemaakt. De grote `WndProc` op VA `0x004964d0` kon niet binnen 25 seconden worden gedecompileerd. De Amplify- en WAV-filteranalyses zijn voltooid. Windows-importbibliotheken zijn niet mee geïmporteerd; Ghidra gebruikte een Windows-typearchief. Decompilertypen en veldnamen blijven gevolgtrekkingen. De volledige beperkingen en logs staan in [provenance.json](evidence/provenance.json).

Er zijn geen runtime-, opname-, latency-, luister-, numerieke DSP- of projectroundtriptests uitgevoerd. De volgende gerichte onderzoeksstap is een kleine referentieset met één golfvormbewerking, de drie float-WAV-varianten en een minimale multitracksessie. Daarmee worden juist de nog onzekere bestands- en bewerkingsregels toetsbaar.

Het [bouwplan](BOUWPLAN.md) beschrijft hoe deze bevindingen een Linux-implementatie kunnen sturen.
