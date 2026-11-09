# Prototype 0.3.0 — 9 november 2026

SoundSausage, de native Linux-editor, staat in `/home/deck/Documenten/Codex/CoolEdit/`. Versie 0.3.0 voegt bewerkbare volume- en panlijnen op multitrackclips toe, inclusief audioverwerking, undo/redo en projectopslag. De interface volgt sinds 0.2.2 het Linux-thema met belangrijke knoppen in de accentkleur. De aangeleverde Cool Edit-afbeeldingen blijven de referentie voor de indeling, groene golfvormen, transportpositie en grote klok. De [status van versie 0.1](STATUS-0.1.md) is bewaard.

Dit is een golfvorm- en multitrackprototype. Het is nog geen volledige vervanging van Cool Edit Pro.

| Onderdeel | Huidige toestand |
| --- | --- |
| Native desktop | Qt 6-interface via PySide6; geen browser of Wine nodig |
| Thema | Licht/donker en accentkleur via het Qt-desktoppalet, ook tijdens het draaien; leesbare tekst-/achtergrondparen en eigen vectoriconen |
| Audiokern | Eigen C++20-library met effecten en een stereo-mixer, geladen via een getypeerde C-interface |
| WAV | Openen/opslaan: mono/stereo PCM 8/16/24/32 en genormaliseerde float32 |
| Oude type-1 float32 | Expliciete interpretatiekeuze; omzetting met de gevonden schaalfactor; geen vergelijking met uitvoer uit het origineel uitgevoerd |
| Oude type-1 float24 | Afwijkende container wordt herkend als niet ondersteund; geen stille interpretatie als gewone 24-bit PCM |
| Bewerken | Selectie met muis of exacte framegrenzen; knippen, kopiëren, plakken, Mix Paste, verwijderen en trimmen |
| Geschiedenis | Undo/redo; tot 50 bewerkingen, met gedeelde ongewijzigde audioblokken en een geheugenbudget voor geschiedenis |
| Effecten | Versterking, afzonderlijke begin/eindwaarden, lineaire/logaritmische fades, normalize, reverse, invert en silence |
| Generatie | Sinustoon en stilte, met ingestelde duur |
| Analyse | FFT-spectrum met Hann-window en kanaalvermogensgemiddelde |
| Weergave | Stereo/mono, zoom, scroll, selectietijden, klok en indicatieve niveaumeters |
| Afspelen | Asynchrone ffplay-adapter; play/stop, pause en loop |
| Multitrack | Tot 32 sporen; clips importeren, verplaatsen tussen sporen, trimmen, dupliceren en verwijderen |
| Mixinstellingen | Track- en clipvolume/pan, mute/solo en lineaire clipfades; geen interne clipping |
| Clipautomation | Volume- en panpunten tekenen, slepen, exact instellen, verwijderen/resetten, undo/redo; C++-verwerking per audioframe |
| Projecten | Zelfstandige `.celp` versie 2 met JSON, automation en ingebedde float32-WAV's; versie 1 blijft leesbaar |
| Clipbewerking | Dubbelklik opent een kopie in golfvormweergave; Apply Waveform to Clip past bewust de clip aan, met undo |
| Mixdown | De gehele sessie als WAV exporteren; PCM16 gebruikt de symmetrische grenzen uit de originele referentiemixen; selectie bepaalt alleen de afspeelrange |
| Oude sessies | De zes aangeleverde Pro 1.0-voorbeelden kunnen worden geïmporteerd; onbekende features worden geweigerd |
| Bestandsveiligheid | Schrijven naar een tijdelijk bestand naast het doel en atomair vervangen; een schrijffout laat het bestaande bestand behouden |
| Nog te bouwen | Opnemen, ruimere SES/PK-ondersteuning, SES-automationmapping, spoorautomation, SCP-interpreter, geavanceerde effecten en externe plug-ins |

De keuze voor de eerste interface is aangepast aan de beschikbare omgeving: PySide6 6.11.1 en NumPy 2.5.1 zijn al aanwezig. Qt-ontwikkelheaders en CMake zijn voor deze bootstrap niet nodig. De C++-kern wordt met de aanwezige GCC 16.1.1 en Make gebouwd. Er zijn geen pakketten geïnstalleerd of systeeminstellingen gewijzigd.

Afspelen gebruikt voorlopig de aanwezige `ffplay`. De adapter streamt eigen float32-audioblokken naar een apart proces, zodat een onbereikbare audioserver de GUI niet blokkeert. De geplande directe Linux-audiobackend blijft een vervolgstap. De playhead en meters zijn tijdgebaseerde indicaties; ze volgen nog geen exact gerapporteerde hardwareklok.

**Getest**

111 geautomatiseerde tests slagen. De uitvoer staat in [build/test-results-envelopes.log](validation/test-results-soundsausage.log). De relevante controles zijn:

- Ondertekende 24-bit waarden, kanaalvolgorde, lege bestanden, oneven datalengtes en float-headroom.
- 16-bit PCM-export onafhankelijk teruggelezen met Python's standaard `wave`-module.
- Extensible PCM32, de expliciete interpretatie van oude float32 en het afwijzen van de afwijkende float24-container.
- Selectiebereiken, stereo-reverse, cut/paste, mix aan het einde, trim, undo/redo, ongeldige instellingen en herhalen op een nieuwe selectie.
- Een bestaande uitvoer behouden bij een gesimuleerde fout tijdens atomair opslaan.
- Muisselectie en knippen/undo via echte Qt-toetsevents, GUI-export en weigering van metadata-verlies zonder gebruikerskeuze.
- Spectrumanalyse van een bekende toon en stereo in tegenfase.
- Echte raw-audiostreaming naar ffplay met SDL's dummy-audioapparaat; fysieke audio en de hostaudioserver worden daarbij niet gebruikt.
- Mixen van overlappende mono/stereoclips, headroom, pan, mute/solo en identieke fades bij gedeeltelijke renders.
- Projectroundtrips met exacte brondata en mix, ontbrekende/ongeldige audioverwijzingen, toekomstige versies en behoud van het bestaande project bij een schrijffout.
- Werkelijke Qt-muisevents voor clipverplaatsing en trimmen, undo per modus, spoorvolume en expliciete golfvormkopieën terugzetten in clips.
- Import van de zes echte SES-bestanden, frameposities, +13,93 dB, de −100 dB panvloer, de afwijkende lege trackmetadata en weigering van niet-ondersteunde automation.
- Vergelijking met de originele `02-basis-mix.wav`: alle 183109 gemeenschappelijke stereo-frames en de geëxporteerde PCM16-audiobytes zijn exact gelijk. De originele export bevat één extra stil frame; de bestanden zijn dus niet geheel identiek. Zie [de meting en dekkingsgrenzen](SES-ONDERZOEK.md).
- De echte GUI-export van `04-volume.ses` en `05-pan.ses` levert voor alle 220500 gemeenschappelijke frames dezelfde PCM16-audiobytes als de VM. De referenties hebben één extra stil eindframe. Float32-export en de interne mix behouden headroom. De aanpassing betreft uitsluitend de negatieve begrenzing van 16-bit sessie-mixdowns.
- Behoud van de volledige geïmporteerde gain/pan-precisie bij openen en ongewijzigd accepteren van het propertiesvenster.
- Werkelijk gerenderde kleuren bij live wisselen tussen lichte en donkere paletten en verschillende accentkleuren, contrast bij hover en uitgeschakelde acties, zichtbare menu-iconen en de actieve modus met behoud van knopteksten.
- Automationsamples vergeleken met handberekende waarden, mono/stereo, gecombineerde gain/pan/fades, identieke gedeeltelijke renders, brongebonden punten bij verplaatsen/trimmen en herstel via undo.
- Echte Qt-puntgebaren, exact invoervenster, Esc/Delete, één undo per sleepbeweging, resetten en headerverplaatsing in lijnmodus; export/projectopslag en het doorgeven van de geautomatiseerde selectie aan de afspeeladapter.
- CELP-versie-2-roundtrips, versie-1-migratie, weigering van ongeldige punten of ontbrekende envelopevelden, en begrensde puntremapping bij bronvervanging.

De toepassing is headless gestart met de demo-WAV, de ingebedde multitrackdemo, `02-basis.ses` en `05-pan.ses`. De huidige themaweergaven staan in [THEMA.md](THEMA.md): zes echte Qt-screenshots met nagebootste lichte en donkere paletten, op 1180 × 720 pixels. De eerdere screenshots van [golfvormbewerking](screenshots/prototype.png), [multitrack](screenshots/multitrack-v02.png) en [de SES-import](screenshots/imported-ses-v02.png) zijn bewaard. De demo is synthetisch. De SES-bestanden zijn door de gebruiker in de VM gemaakt; de originele programmabestanden zijn door de agent niet uitgevoerd.

De nieuwe [automationsdemo](ENVELOPES.md) bevat een volumeclip en een panclip, met twee nieuwe Qt-screenshots. De demo-mix en aaneengevoegde gedeeltelijke renders zijn exact gelijk. Het bestaande `Untitled.celp` van de gebruiker is alleen gelezen en blijft ongewijzigd.

**Praktische grenzen**

Per document geldt maximaal 128 MiB gedecodeerde float32-audio. Het documentmodel deelt ongewijzigde blokken tussen bewerkingen, maar laden, renderen, opslaan en bepaalde effecten gebruiken nog tijdelijke buffers. De toepassing heeft nog geen volledige opslag op schijf voor zeer lange opnamen en geen crashherstel.

Een sessie ondersteunt maximaal 32 sporen, 4096 clips en 128 bronitems. De brondata inclusief undo blijft begrensd tot 128 MiB; duplicaten kunnen dezelfde bron delen. Per mix/render geldt eveneens 128 MiB. Lange lege tijdlijnen kunnen worden bewerkt, maar voor afspelen kan dan een kortere tijdrange nodig zijn. De mixer berekent de gekozen range vóór afspelen; er is nog geen continue schijfstreaming of live verwerking van wijzigingen tijdens playback.

Per clip zijn maximaal 512 punten per volume- of panlijn beschikbaar. De audiogegevens blijven tijdens slepen ongewijzigd; bevestigen met loslaten maakt één undo-stap en stopt lopend afspelen. De volumelijn is een factor boven op gain/fades en de panlijn een aanvullende balans boven op clip-/spoorpan. Native clipautomation is nog niet vergeleken met oorspronkelijke SES-automation. De brongebonden coördinaten en remapping bij bronvervanging staan in [ENVELOPES.md](ENVELOPES.md).

Alle bronnen in een sessie moeten dezelfde samplerate gebruiken. De eerste import in de aanvankelijke, onopgeslagen lege sessie neemt de bronrate over. Een expliciet ingestelde of opgeslagen sessierate blijft vast. Automatische resampling is nog niet beschikbaar. De lineaire pan/balansregel staat in de [projectformaatbeschrijving](PROJECTFORMAAT.md); gelijkheid met het oorspronkelijke pan-algoritme is niet aangetoond.

32-bit integer-PCM wordt voor bewerking naar float32 omgezet; de laagste integerbits kunnen daardoor verloren gaan. PCM-uitvoer begrenst waarden tot het bereik van dat uitvoerformaat. De 16-bit sessie-mixdown gebruikt vanaf 0.2.1 grenzen van −32767 en +32767, zoals de aangeleverde oorspronkelijke exports. Gewone golfvormopslag gebruikt het volledige PCM-bereik. Float32-uitvoer bewaart waarden boven het nominale ±1-bereik. Quantisatie naar integer-PCM gebruikt nog geen dithering.

De WAV-writer bewaart audiogegevens en formaatvelden. Aanvullende chunks, zoals cues en tekstmetadata, worden nog niet behouden. Wanneer zo'n bestand is geopend vraagt de GUI dit concreet te bevestigen vóór opslaan. Historische float32 wordt standaard als genormaliseerde float32 uitgevoerd; de aparte importkeuze vermeldt die conversie.

Het interne klembord accepteert momenteel alleen audio met dezelfde samplerate en hetzelfde kanaalaantal. Er is nog geen gedeeld systeemklembord of automatische resampling. Effecten zonder actieve selectie werken op de hele golfvorm. Mix Paste mengt vanaf het begin van de selectie of vanaf de cursor en verlengt zo nodig het document.

De FFT gebruikt maximaal 262.144 frames uit het midden van de gekozen selectie; bij geen selectie geldt de hele golfvorm als gekozen bereik. De analyse toont de werkelijk gebruikte vensterlengte. Zero-crossingselectie gebruikt het eerste kanaal. Deze bewerkingsregels zijn expliciet prototypegedrag; ze zijn nog niet allemaal vergeleken met de oorspronkelijke applicatie.

De gebruiker heeft op 9 november 2026 bevestigd dat geluid op het eigen apparaat werkt. Dat is een praktijktest van de gebruiker. De geautomatiseerde afspeeltest gebruikte alleen een dummy-apparaat, omdat de sandbox geen verbinding met de hostaudioserver toeliet. De basis-, volume- en pan-mixdown zijn inmiddels numeriek vergeleken met het origineel, met bovenstaand resultaat. Microfoonopname en gelijkheid voor andere instellingen en effecten zijn nog niet bevestigd.

**Vervolg**

De gebruiker heeft verduidelijkt dat het oorspronkelijke Cool Edit Pro op de Steam Deck niet werkt. Dat is de aanleiding voor deze Linux-versie. De gebruiker heeft inmiddels een Windows 7-VM met het origineel gestart en zes referentiesessies geleverd. Die zijn ongewijzigd bewaard en [onderzocht](SES-ONDERZOEK.md). De app blijft onafhankelijk van die VM.

Drie mixdowns uit de VM zijn vergeleken. Verdere referenties met fades en envelopes kunnen de volgende onderdelen toetsen. De huidige SES-import accepteert alleen de onderzochte Pro 1.0-indeling met neutrale envelopes en standaardvlaggen. Onbekende chunks, cues en automation worden niet stilzwijgend overgeslagen. Er wordt niet naar SES teruggeschreven; bewaren gebeurt als CELP. De volledige doelomvang uit het [bouwplan](../analysis/BOUWPLAN.md) blijft behouden. Exacte gelijkheid met het oorspronkelijke geluid blijft onbevestigd waar uitvoervergelijkingen ontbreken.
