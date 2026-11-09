# Bouwplan voor een native Linux-variant

Dit plan is opgesteld op basis van het [statische onderzoek](ANALYSE.md), vóór de prototypebouw. De gebruiker wil zo veel mogelijk oorspronkelijke functies en bediening behouden. Inmiddels bestaat een eerste golfvormeditor; zie [de actuele status](../docs/STATUS.md). De volledige effectinventaris en bediening blijven de doelomvang; de fasering hieronder beschrijft de bouwvolgorde.

Uitgangspunt na verduidelijking door de gebruiker: het oorspronkelijke Cool Edit Pro werkt niet op de Steam Deck. Een werkend origineel blijft geen voorwaarde voor de Linux-versie. De gebruiker heeft inmiddels wel een Windows 7-VM en zes referentiesessies beschikbaar gemaakt. Prototype 0.2 bevat multitrack en een begrensde import van die sessies; zie [het SES-onderzoek](../docs/SES-ONDERZOEK.md). Volledige compatibiliteit en klankgelijkheid blijven afzonderlijk te valideren.

**Werkplek**

De projectlocatie is `/home/deck/Documenten/Codex/CoolEdit/`. Na het wijzigen van de sessiewerkmap is de schrijftoegang succesvol getest en is de onderzoeksbundel naar `analysis/` gekopieerd. Alle bestanden uit het oorspronkelijke manifest zijn gecontroleerd met SHA-256. Bouwen en testen gebeurt voortaan binnen deze projectlocatie. De oorspronkelijke installatie- en setupbestanden blijven de referentiebronnen.

De huidige omgeving heeft een `c++`- en `pkg-config`-commando. CMake en Ninja zijn niet op `PATH` aangetroffen. Ontwikkelmetadata voor Qt6Widgets, Qt6Multimedia, libsndfile, PipeWire en PortAudio is niet gevonden via pkg-config. Dat bewijst niet dat hun runtimebibliotheken ontbreken. Er zijn geen pakketten geïnstalleerd of hostinstellingen veranderd.

**Technische basis — voorstel**

| Onderdeel | Voorgestelde invulling | Reden |
| --- | --- | --- |
| Taal en bouw | C++20, CMake, Ninja | Een native kern met expliciete audio- en geheugenmodellen |
| Desktopinterface | Qt 6 Widgets, eigen golfvorm- en tijdlijnwidgets | Menu's, werkbalken, dialogen, toetsenbordbediening en twee vertrouwde werkmodi |
| Audio op Linux | Een aparte backend op PipeWire | Opname en weergave buiten de GUI- en bestandsverwerking |
| Standaardaudioformaten | libsndfile plus een eigen adapter voor historische Cool Edit-WAV-varianten | Standaard-I/O delen en afwijkende schaal-/formaatregels expliciet houden |
| DSP | Een zelfstandige kern met getypeerde effectparameters en blokverwerking | Preview, toepassen en batch gebruiken dezelfde implementatie |
| Projecten | Een versieerbaar eigen projectmodel; SES-import als afzonderlijke adapter | Het nog onbekende binaire SES-formaat bepaalt niet de interne architectuur |

Qt biedt venster-, menu-, werkbalk- en dockcomponenten die dit desktopmodel ondersteunen. De keuze voor Qt is een ontwerpvoorstel. Zie de [officiële Qt-uitleg over hoofdvensters](https://doc.qt.io/qt-6/mainwindow.html).

PipeWire biedt streams met een verwerkingscallback en een optie om verwerking vanuit een realtime thread aan te roepen. De callback mag geen bestands-I/O, GUI-werk of blokkerende bewerkingen doen. Zie de [PipeWire-streamdocumentatie](https://docs.pipewire.org/group__pw__stream.html). Een alternatief voor een eerste audioadapter is Qt Multimedia; de huidige documentatie beschrijft zowel QIODevice- als callbackgebruik. De callbackvariant vereist een passende Qt-versie. Zie [QAudioSink](https://doc.qt.io/qt-6/qaudiosink.html). De backendkeuze moet in de eerste prototypefase op de doelmachine worden getoetst.

libsndfile kan meerdere audioformaten via één interface lezen en schrijven en normaliseert integer-PCM standaard bij float-I/O. Daarom moet de overgang naar Cool Edit's gevonden amplitudeschaal expliciet worden getest. Zie de [libsndfile-API](https://libsndfile.github.io/libsndfile/api.html). Ondersteuning voor alle 19 historische filters is hiermee nog niet aangetoond.

**De kern opdelen langs de waargenomen grenzen**

Een `AudioDocument` beheert bronmedia, kanaalinformatie en bewerkingen op individuele golfvormen. Gebruik frameposities als 64-bits gehele getallen en een intern halfopen selectiebereik. Een adapter vertaalt de oude inclusieve effectselecties. Daarmee kunnen afrondings- en eindpuntregels op één plek worden getest.

Een blokopslag met een tijdelijke werkomgeving en piekpiramides houdt lange bestanden bewerkbaar. Undo verwijst naar bewerkingsresultaten en blokken; elke stap kopieert niet het hele bestand. Dit is een nieuw ontwerp, geïnspireerd door de gevonden cache- en undo-instellingen. Crashherstel en atomair opslaan horen bij deze laag.

Een `Session` bevat tracks en clips met bronverwijzing, bronbereik, tijdpositie, gain, pan, envelopes, mute/solo en takes. Golfvormbewerkingen en clipbewerkingen moeten afzonderlijke, toetsbare betekenissen hebben. Mixdown, afspelen en opname gebruiken dezelfde tijdlijn- en mixerregels.

Een centrale commandolaag verbindt menu's, sneltoetsen, toolbars, undo, scripts en batch. De 193 gevonden statische menucommando's en de dynamische effectcommando's krijgen stabiele interne identifiers. Namen en oude scriptparameters worden vertaald via compatibiliteitstabellen.

Een effect beschrijft parameters, ondersteunde kanalen, benodigde toestand en eventuele verandering van duur of latency. Offline toepassen en preview gebruiken dezelfde DSP. Verwerking vindt plaats in audioblokken met aparte voortgang en annulering. Nieuwe Linux-effectmodules gebruiken een eigen interface; de afgeleide XFM-context is onderzoeksmateriaal en nog geen uitvoerbare plug-instandaard.

Een interne float32-schaal rond ±1 is een bruikbaar voorstel. Bij oude bestanden, oude presets, amplitudedrempels en exports komen expliciete conversies. De gevonden factoren 32768 en 256 maken een numerieke vergelijking noodzakelijk. Voorkom ongewenste clipping tussen bewerkingen; begrens en quantiseer volgens de gekozen uitvoerinstellingen.

**Bediening behouden**

Begin met dezelfde twee modi: Edit Waveform en Multitrack. Gebruik `ui-spec.json` als inventaris voor commando's, dialogen en controlteksten, en `shortcuts.json` als vertrekpunt voor de toetsenbordindeling. De gegevens zijn geen automatisch te renderen volledige UI: meerdere resources zijn varianten en sommige bediening wordt dynamisch opgebouwd.

Behoud herkenbare namen, de volgorde van veelgebruikte commando's, selectiegedrag, transport, meters, cuebeheer, zoom en de overgang tussen clip en golfvorm. Bevestig het muisgedrag en de werkelijke standaardwaarden aan de hand van de oorspronkelijke toepassing. De oude dialoogcoördinaten zijn dialoogeenheden; schaal tekst en controls passend voor het Linux-scherm.

Aanvulling van de gebruiker op 9 november 2026: de vormgeving moet het Linux-thema volgen, met belangrijke knoppen in de accentkleur, zoals in PixelPickle. Dit is toegepast in prototype 0.2.2; zie [thema en leesbaarheid](../docs/THEMA.md). De oorspronkelijke indeling en groene golfvormen blijven herkenbaar, terwijl vaste lichte werkbalkkleuren zijn vervangen door het Qt-desktoppalet.

Een menuoptie telt pas als ondersteund wanneer het bijbehorende gedrag werkt. Niet-geïmplementeerde functies mogen geen geslaagde bewerking suggereren. Houd de volledige functieinventaris als voortgangslijst bij.

**Bouwvolgorde en acceptatie**

| Fase | Werkend resultaat | Bewijs dat nodig is voor afronding |
| --- | --- | --- |
| 1. Referentie en contractspecificatie | Eenduidige selectie-, gain-, WAV- en basisprojectregels | Synthetische audiogevallen en toetsbare regels, onderbouwd met de statische analyse; vergelijking met oorspronkelijke uitvoer zodra die later beschikbaar is |
| 2. Golfvormeditor | WAV openen/opslaan, weergave, selectie, afspelen, opnemen, knippen/plakken/trimmen en undo | Audiogegevens overleven ongewijzigde roundtrip; edits treffen precies de bedoelde frames; undo herstelt de data |
| 3. Eerste effecten | Amplify, fades, normalize, invert, reverse, silence en channel mixer | Numerieke vergelijkingen op mono/stereo, stilte, DC, pieken, korte selecties en verschillend gebufferde verwerking |
| 4. Multitrack | Clips, tracks, verschuiven/trimmen, gain/pan, mute/solo, envelopes, takes, punch-in en mixdown | Analytisch controleerbare mixen; opslaan/heropenen behoudt posities en instellingen; opname laat playback stabiel |
| 5. Automatisering en formaatcompatibiliteit | SCP-subset uitbreiden tot meegeleverde scripts; standaardaudio en gedocumenteerde legacyvarianten | Vergelijking van de crossfadescripts; kanaalvolgorde, amplitudeschaal en selectieranden kloppen |
| 6. Volledige effectfamilies | EQ, filters, delay, modulatie, convolutie, reverb, restauratie en stretching | Per effect parameter- en luistervergelijkingen; impuls-/spectrum-/ruis- en tijdrekmetingen waar passend |
| 7. Projecten, externe effecten en overige bediening | SES-adapter, MIDI/SMPTE, externe plug-ins en resterende commandogroepen | Gerichte projectroundtrips en integratietests op de ondersteunde functies |
| 8. Distributie | Installeerbaar Linux-pakket en gedocumenteerde gegevenslocaties | Start, audio-apparaten en bewerken testen op een schone doelomgeving |

Het eigen Linux-projectmodel heeft tests voor opslaan en heropenen en bewaart audio in zelfstandige CELP-projecten. Een eerste SES-adapter ondersteunt de zes eenvoudige Pro 1.0-referenties met expliciete grenzen. Er zijn nog geen referenties voor complexere features om brede verliesvrije SES-compatibiliteit op te baseren; dit blokkeert de ontwikkeling van nieuwe Linux-projecten niet.

De eerste bruikbare editor is een tussenresultaat. Functiepariteit omvat ook de moeilijkere effectfamilies en oude workflows; hiervoor is aanzienlijk meer werk nodig dan de interface reconstrueren. Exacte planningsduur is zonder prototype en effectvergelijkingen niet onderbouwd.

**Gerichte vervolgstap**

De werkmap en onderzoeksbundel staan op de gewenste locatie. Een eerste native golfvormeditor is gebouwd en de gebruiker heeft afspelen op het apparaat bevestigd. De volgende bouwstappen kunnen voortgaan met synthetische audio, de aanwezige programmabestanden en de GUI-referentie. Hiervoor hoeft de gebruiker geen `.ses` aan te leveren.

Multitrack bevat inmiddels clips, tracks, volume/pan, mute/solo, fades, mixdown en een eigen versieerbaar projectformaat met roundtriptests. Een eerste subset van de oude `.ses`-indeling is uit de aangeleverde bestanden afgeleid. Verdere compatibiliteit en identieke effectuitvoer worden pas als bevestigd gerapporteerd als daar voldoende bewijs voor is.
