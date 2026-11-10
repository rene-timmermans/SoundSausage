# Onderzoek van de zes aangeleverde SES-bestanden

Bronnen: `00-leeg.ses` t/m `05-pan.ses`, op 9 november 2026 gemaakt met de referentietoepassing in een Windows 7-VM en onder `/home/deck/` geplaatst. Ongewijzigde kopieën staan in `reference/vm-session-test/`. De oorspronkelijke bestanden zijn niet gewijzigd of uitgevoerd. De interpreter gebruikt lokale byteanalyse en vergelijking; er is geen REA-MCP-server verbonden.

De referentiebestanden gebruiken sessieformaat versie **1.0**, met samplerate **44100 Hz** en een 16-bit sessie-instelling. De VM levert afzonderlijke referentiegevallen. Onze Linux-versie heeft de VM niet nodig om te werken.

**Rechtstreekse waarnemingen**

| Bestand | Omvang | Waargenomen inhoud |
| --- | --- | --- |
| `00-leeg.ses` | 194 bytes | Geen audiobestanden of clips; ongeldige lengte-/aantalwoorden in het lege trackgedeelte |
| `01-een-clip.ses` | 501 bytes | Eén verwijzing naar A, clip van 88200 frames vanaf frame 0 |
| `02-basis.ses` | 810 bytes | A vanaf 0; B vanaf frame 50809, ongeveer 1,1521315 seconde |
| `03-verplaatst.ses` | 810 bytes | B vanaf frame 88200, precies 2 seconden |
| `04-volume.ses` | 810 bytes | De verplaatsing blijft behouden; A heeft twee kanaalfactoren van 4,971643737252429 |
| `05-pan.ses` | 810 bytes | De voorgaande wijzigingen blijven behouden; B heeft links ongeveer 0,00001 en rechts 1 |

De varianten zijn cumulatief. De juiste geïsoleerde vergelijkingen zijn daarom 02→03 voor positie, 03→04 voor volume en 04→05 voor pan. Daarvoor hoeven de sessies niet opnieuw te worden gemaakt.

De factor in 04 komt volgens `20 × log10(factor)` overeen met **+13,93 dB**. Dit is een versterking van circa 497%, terwijl 50% amplitude circa −6,0206 dB zou zijn. Het andere ingestelde niveau is bruikbaar voor het onderzoek: er verandert een duidelijk herkenbaar paar doubles. Deze wijziging staat in het clip/blokgedeelte; de onderzochte trackrecords blijven gelijk.

De kleine linkerfactor in 05 komt overeen met ongeveer **−100 dB**. Helemaal rechts pannen bewaart in dit bestand dus een kleine linkerfactor. De importer behoudt deze verhouding. De aangeleverde 16-bit mixdown bevestigt de uiteindelijke kanaaluitvoer; deze resolutie kan de kleine linkerfactor zelf niet onderscheiden van volledige stilte.

**Vergelijking met de originele mixdown**

`02-basis-mix.wav` is een referentie-export uit de Windows-VM. De ongewijzigde kopie staat naast de sessies. Het is stereo PCM16 op 44100 Hz, 732484 bytes, met SHA-256 `15cc02f1130862a54855629bf48cfcb44aa29643319344b2569c9468bb92505f`.

| Meting | Resultaat |
| --- | --- |
| Linux-render van `02-basis.ses` | 183109 stereo-frames |
| Originele mixdown | 183110 stereo-frames |
| Gemeenschappelijke eerste 183109 frames | Iedere sample exact gelijk, links en rechts |
| Maximale fout en RMS-fout per kanaal | Beide exact 0 |
| PCM16-export van die frames | Alle audiobytes gelijk, onafhankelijk gelezen met Python `wave` |
| Extra origineel frame | Links 0, rechts 0; 1/44100 seconde, circa 0,022676 ms |

De vergelijking start bij frame 0 en gebruikt geen tijdverschuiving, resampling, gaincorrectie of foutmarge. Ook het overlappende deel van A en B is exact gelijk. Dit ondersteunt de huidige broninterpretatie, frameposities, mono-naar-stereo-duplicatie, kanaalvolgorde en optelling op eenheidsvolume voor deze sessie.

De bestanden hebben dus verschillende lengtes; ze zijn als geheel niet identiek. De oorzaak van het extra stille frame is niet vastgesteld. Dezelfde extra stilte is ook in de twee onderstaande exports aangetroffen. Het tijdlijnbeleid blijft gebaseerd op een exclusief einde. De basisvariant toetst geen gewijzigde versterking, andere panstanden, fades, clipping, dithering of effecten.

Het [machinerapport](../analysis/evidence/ses/mixdown-comparison.json) bevat de bronhashes, frameaantallen en foutmetingen. Een regressietest controleert zowel de exacte render als de PCM16-export en het ene extra stille referentieframe. Opnieuw vergelijken:

```bash
PYTHONPATH=src python3 tools/compare_ses_mix.py \
  reference/vm-session-test/02-basis.ses \
  reference/vm-session-test/02-basis-mix.wav \
  --out analysis/evidence/ses/mixdown-comparison.json
```

**Volume, pan en oversturing: prototype 0.2.1**

`04-volume-mix.wav` en `05-mix-down.wav` zijn aanvullende referentie-exports uit de VM. Beide zijn ongewijzigd gekopieerd vanuit `/home/deck/`. De tweede bestandsnaam wijkt af van het voorgestelde `05-pan-mix.wav`; de uitvoer is vergeleken met `05-pan.ses`.

| Referentie | Originele frames | Linux-frames | PCM16-audio na aanpassing |
| --- | --- | --- | --- |
| `04-volume-mix.wav` | 220501 | 220500 | Alle gemeenschappelijke audiobytes exact gelijk |
| `05-mix-down.wav` | 220501 | 220500 | Alle gemeenschappelijke audiobytes exact gelijk |

Beide bestanden zijn 882048 bytes en stereo PCM16 op 44100 Hz. Het laatste extra frame is in beide kanalen nul. Herkomst, SHA-256, metingen per clipsegment en de vergelijking met de eerdere standaardexport staan in [04-volume-mix-comparison.json](../analysis/evidence/ses/04-volume-mix-comparison.json) en [05-pan-mix-comparison.json](../analysis/evidence/ses/05-pan-mix-comparison.json).

Rechtstreekse waarneming: in het A-segment van beide referenties liggen de PCM-waarden tussen −32767 en +32767. De eerdere Linux-export begrensde tot −32768 en +32767 en week op 17840 negatieve samples per kanaal precies één PCM-stap af. Alle andere samples waren al gelijk. Het toepassen van symmetrische grenzen bij de PCM16-export verklaart alle verschillen, zonder wijziging van timing, versterking, pan of afronding.

De 16-bit **sessie-mixdown** gebruikt daarom vanaf 0.2.1 grenzen van −32767 en +32767. Gewone golfvormopslag gebruikt het volledige PCM-bereik, zodat bestaande −32768-samples behouden kunnen blijven. De interne float32-mix en float32-export behouden headroom: A piekt intern op circa 1,242911 door de geïmporteerde +13,93 dB. De tests toetsen beide exportformaten via de werkelijke GUI-actie en controleren dat exporteren de sessie niet verandert. Andere integerformaten zijn niet aangepast op basis van deze PCM16-voorbeelden.

In de panreferentie, vanaf frame 88200, zijn alle linker PCM-waarden nul en is rechts exact gelijk aan het oorspronkelijke rechterkanaal van B. De geïmporteerde kleine linkerfactor levert intern een piek van circa 0,000002; dat valt onder een halve 16-bit quantisatiestap en wordt bij export nul. Deze export bevestigt dus de 16-bit panuitvoer, maar bewijst niet zelfstandig de precieze −100 dB-vloer uit het SES-bestand. Tussenliggende panstanden zijn nog niet getoetst.

De conclusies gelden voor deze opnamen, de aangetroffen gain/panwaarden en PCM16-export. Overlappende versterkte clips, andere gainwaarden, envelopes, fades, dithering en de exacte oorspronkelijke float32-mixer zijn hiermee niet volledig vastgesteld. De verwerking van het extra eindframe blijft onverklaard.

Opnieuw vergelijken:

```bash
PYTHONPATH=src python3 tools/compare_ses_mix.py \
  reference/vm-session-test/04-volume.ses \
  reference/vm-session-test/04-volume-mix.wav \
  --out analysis/evidence/ses/04-volume-mix-comparison.json
PYTHONPATH=src python3 tools/compare_ses_mix.py \
  reference/vm-session-test/05-pan.ses \
  reference/vm-session-test/05-mix-down.wav \
  --out analysis/evidence/ses/05-pan-mix-comparison.json
```

**Afgeleide indeling**

Het bestand begint met acht bytes `COOLNESS`, gevolgd door een little-endian lengtewoord dat gelijk is aan bestandsomvang minus 12. Daarna volgen chunks zonder de gebruikelijke RIFF-padding op even grenzen. De sleutel `LISTFILE` is acht bytes lang; de andere aangetroffen sleutels zijn vier bytes lang.

| Chunk | Onderzochte gegevens |
| --- | --- |
| `hdr ` | Payload van 40 bytes; samplerate en aanvullende sessiewoorden/waarden |
| `vers` | Nulgetermineerde versieaanduiding |
| `stat` | Aanvullende toestand; niet volledig geïnterpreteerd |
| `trks` | Aantal plus records van 72 bytes bij niet-lege sessies |
| `LISTFILE` | `wav `-records met bestands-ID en een Windows-pad |
| `blk ` | Aantal plus cliprecords van 72 bytes |
| `envp` | Enveloperecords met volume- en panpunten |
| `cues` | In de zes voorbeelden leeg |

De volgende clipvelden zijn afgeleid uit consistente verschillen en vergelijking met de bekende bronaudio. Het zijn geen gepubliceerde SDK-definities:

| Byte-offset binnen een cliprecord | Afgeleide betekenis |
| --- | --- |
| `+0`, `+8` | Linker- en rechterkanaalfactor, beide float64 |
| `+32` | Positie op de tijdlijn, in frames |
| `+36` | Aantal frames |
| `+40` | Spoorindex |
| `+44` | Begin binnen de bronaudio, in frames |
| `+48` | Verwijzing naar het bestands-ID |
| `+52` | Blok-ID |

De positie van B verschilt bij 02→03 op absolute bestandsoffsets `0x20a`–`0x20c`. De dubbele kanaalfactoren van A beginnen in deze tweesporige bestanden op `0x1a2` en `0x1aa`. De linkerfactor van B staat op `0x1ea`. Andere recordvelden zijn onvolledig verklaard; de import staat alleen de geobserveerde standaardvlaggen toe.

De enveloperecords bevatten in deze voorbeelden constant volume 1 en constante panwaarde 0,5. Elke geobserveerde puntstructuur beslaat 24 bytes. De betekenis van alle extra velden en de interpolatieregels is niet vastgesteld. Veranderende of anders ingestelde envelopes worden daarom nog niet geïmporteerd.

**Lege sessie**

In `00-leeg.ses` zijn de gedeclareerde lengte en het aantal in `trks`, als signed 32-bit gelezen, respectievelijk −18356 en −255. De overige chunks, de totale lengte en de lege bestands-/clip-/envelopelijsten zijn wel aanwezig. De oorzaak van die ongeldige woorden is niet vastgesteld. De importer herkent uitsluitend deze aantoonbaar verder lege indeling, meldt de afwijking en maakt één leeg spoor. Er wordt geen oorspronkelijk aantal zichtbare sporen verondersteld.

**Bruikbare, begrensde import**

`legacy.py` importeert de zes referentiegevallen in het Linux-sessionmodel. Windows-paden worden niet als netwerk- of schijfpaden geopend: de WAV-bestanden worden op bestandsnaam gezocht naast de SES, of in een gekozen bronmap. De twee test-WAV's staan naast de bewaarde referentiekopieën.

Er wordt niet naar `.ses` teruggeschreven. Opslaan levert een zelfstandig `.celp` op met ingebedde audio. Onbekende chunks, niet-ondersteunde vlaggen, cues en niet-neutrale volume-/panenvelopes worden afgewezen in plaats van overgeslagen. Andere SES-varianten en volledige SES-functionaliteit zijn niet aangetoond.

De tests controleren de uitgelezen frameposities, de kanaalfactoren, bronverwijzingen, de lege-sessie-afwijking, ontbrekende audio, het weigeren van automation en behoud van de geïmporteerde mix bij conversie naar `.celp`. De basis-, volume- en panvariant hebben daarnaast de hierboven beschreven numerieke vergelijking met echte mixdowns uit de VM. Voor de overige varianten toetsen de tests voorlopig de eigen import-/mixregels.

Alle bronhashes, chunkoffsets en geïnterpreteerde waarden staan in [de SES-bewijsmap](../analysis/evidence/ses/summary.json); byteverschillen staan in [differences.json](../analysis/evidence/ses/differences.json). Volledige rapporten per bestand staan in dezelfde map.

Opnieuw inspecteren:

```bash
PYTHONPATH=src python3 tools/inspect_ses.py reference/vm-session-test --out analysis/evidence/ses
```
