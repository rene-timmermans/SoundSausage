# Prototype 0.1 — gearchiveerde status van 9 november 2026

Het eerste native Linux-prototype staat in `/home/deck/Documenten/Codex/CoolEdit/`. De C++-DSP-kern is daadwerkelijk gecompileerd en de Qt-interface is gerenderd en getest. De aangeleverde GUI-afbeelding `/home/deck/01.jpg` is gebruikt als visuele referentie voor de grijze bediening, zwarte stereoweergave, groene golfvormen, transportpositie en grote klok.

Dit is een eerste golfvormeditor. Het is nog geen volledige vervanging van Cool Edit Pro.

| Onderdeel | Huidige toestand |
| --- | --- |
| Native desktop | Qt 6-interface via PySide6; geen browser of Wine nodig |
| Audiokern | Eigen C++20-library, geladen via een getypeerde C-interface |
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
| Bestandsveiligheid | Schrijven naar een tijdelijk bestand naast het doel en atomair vervangen; een schrijffout laat het bestaande bestand behouden |
| Nog te bouwen | Opnemen, multitrack, SES/PK, SCP-interpreter, geavanceerde effecten en externe plug-ins |

De keuze voor de eerste interface is aangepast aan de beschikbare omgeving: PySide6 6.11.1 en NumPy 2.5.1 zijn al aanwezig. Qt-ontwikkelheaders en CMake zijn voor deze bootstrap niet nodig. De C++-kern wordt met de aanwezige GCC 16.1.1 en Make gebouwd. Er zijn geen pakketten geïnstalleerd of systeeminstellingen gewijzigd.

Afspelen gebruikt voorlopig de aanwezige `ffplay`. De adapter streamt eigen float32-audioblokken naar een apart proces, zodat een onbereikbare audioserver de GUI niet blokkeert. De geplande directe Linux-audiobackend blijft een vervolgstap. De playhead en meters zijn tijdgebaseerde indicaties; ze volgen nog geen exact gerapporteerde hardwareklok.

**Getest**

38 geautomatiseerde tests slaagden. De uitvoer staat in [build/test-results-v01.log](validation/test-results-v01.log). De relevante controles waren:

- Ondertekende 24-bit waarden, kanaalvolgorde, lege bestanden, oneven datalengtes en float-headroom.
- 16-bit PCM-export onafhankelijk teruggelezen met Python's standaard `wave`-module.
- Extensible PCM32, de expliciete interpretatie van oude float32 en het afwijzen van de afwijkende float24-container.
- Selectiebereiken, stereo-reverse, cut/paste, mix aan het einde, trim, undo/redo, ongeldige instellingen en herhalen op een nieuwe selectie.
- Een bestaande uitvoer behouden bij een gesimuleerde fout tijdens atomair opslaan.
- Muisselectie en knippen/undo via echte Qt-toetsevents, GUI-export en weigering van metadata-verlies zonder gebruikerskeuze.
- Spectrumanalyse van een bekende toon en stereo in tegenfase.
- Echte raw-audiostreaming naar ffplay met SDL's dummy-audioapparaat; fysieke audio en de hostaudioserver worden daarbij niet gebruikt.

De toepassing is headless gestart, heeft de zelf gegenereerde demo-WAV geopend en heeft [een echte Qt-screenshot](screenshots/prototype.png) geschreven. Het venster sluit daarna weer. De gegenereerde demo gebruikt geen meegeleverde of andere bestaande opname.

**Praktische grenzen**

Per document geldt maximaal 128 MiB gedecodeerde float32-audio. Het documentmodel deelt ongewijzigde blokken tussen bewerkingen, maar laden, renderen, opslaan en bepaalde effecten gebruiken nog tijdelijke buffers. De toepassing heeft nog geen volledige opslag op schijf voor zeer lange opnamen en geen crashherstel.

32-bit integer-PCM wordt voor bewerking naar float32 omgezet; de laagste integerbits kunnen daardoor verloren gaan. PCM-uitvoer begrenst waarden tot het bereik van dat uitvoerformaat. Float32-uitvoer bewaart waarden boven het nominale ±1-bereik. Quantisatie naar integer-PCM gebruikt nog geen dithering.

De WAV-writer bewaart audiogegevens en formaatvelden. Aanvullende chunks, zoals cues en tekstmetadata, worden nog niet behouden. Wanneer zo'n bestand is geopend vraagt de GUI dit concreet te bevestigen vóór opslaan. Historische float32 wordt standaard als genormaliseerde float32 uitgevoerd; de aparte importkeuze vermeldt die conversie.

Het interne klembord accepteert momenteel alleen audio met dezelfde samplerate en hetzelfde kanaalaantal. Er is nog geen gedeeld systeemklembord of automatische resampling. Effecten zonder actieve selectie werken op de hele golfvorm. Mix Paste mengt vanaf het begin van de selectie of vanaf de cursor en verlengt zo nodig het document.

De FFT gebruikt maximaal 262.144 frames uit het midden van de gekozen selectie; bij geen selectie geldt de hele golfvorm als gekozen bereik. De analyse toont de werkelijk gebruikte vensterlengte. Zero-crossingselectie gebruikt het eerste kanaal. Deze bewerkingsregels zijn expliciet prototypegedrag; ze zijn nog niet allemaal vergeleken met de oorspronkelijke applicatie.

De gebruiker heeft op 9 november 2026 bevestigd dat geluid op het eigen apparaat werkt. Dat is een praktijktest van de gebruiker. De geautomatiseerde afspeeltest gebruikte alleen een dummy-apparaat, omdat de sandbox geen verbinding met de hostaudioserver toeliet. Microfoonopname en geluidsmatige gelijkheid met het origineel zijn nog niet bevestigd.

**Vervolg**

De gebruiker heeft verduidelijkt dat het oorspronkelijke Cool Edit Pro op de Steam Deck niet werkt. Dat is de aanleiding voor deze Linux-versie. De bouw mag daarom geen werkende Windows-installatie of door de gebruiker aangemaakte `.ses` vereisen. Er wordt niet van uitgegaan dat de gebruiker het origineel kan starten of referentie-uitvoer kan genereren.

We bouwen verder met de reeds beschikbare statische analyse, de aangeleverde GUI-afbeelding en zelf gegenereerde audio voor functionele tests. Multitrack en het opslaan van nieuwe Linux-projecten kunnen een eigen versieerbaar projectformaat gebruiken. Import van oude `.ses`-projecten is een afzonderlijke compatibiliteitsfunctie; een origineel voorbeeld zou daarvoor later nuttig zijn, maar is geen voorwaarde voor verdere ontwikkeling. De volledige doelomvang uit het [bouwplan](../analysis/BOUWPLAN.md) blijft behouden. Exacte gelijkheid met het oorspronkelijke gedrag blijft onbevestigd waar uitvoervergelijkingen ontbreken.
