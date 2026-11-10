# Thema en leesbaarheid — prototype 0.2.2

De interface combineert de vertrouwde Cool Edit-indeling met het eigen Linux-thema, met belangrijke knoppen in de accentkleur, zoals in [PixelPickle](https://github.com/rene-timmermans/pixelpickle).

De gemelde schermafbeelding toonde lichte werkbalken met lichte tekst, slecht leesbare selectielabels en vaste blauwgrijze panelen binnen een donker bureaublad. De oorzaak in het prototype was een vaste lichte stylesheet naast een overgenomen donker Qt-palet.

**Referentie**

De GitHub-hoofdpagina is bekeken. De afzonderlijke broncodepagina's konden via de webtool niet worden opgehaald. De lokaal geïnstalleerde `pixelpickle 1.0.4-1` kon wel worden gelezen onder `/usr/share/pixelpickle/pixelpickle/`: `__main__.py`, de werkbalkcode in `mainwindow.py` en de kleur-/icooncode in `icons.py`. Die versie gebruikt Fusion, het Qt-palet en accentkleurige lijniconen. Er is niet vastgesteld dat deze pakketversie identiek is aan de huidige GitHub-hoofdbranch.

De nieuwe Cool Edit-code gebruikt dezelfde ontwerpkeuzes: het Qt-desktoppalet als bron voor kleuren en een eigen kleine set vectoriconen. PixelPickle is geen runtime-afhankelijkheid.

**Gedrag**

- Venster, werkbalken, statusbalk, invoervelden en selectieteksten gebruiken bij elkaar passende achtergrond- en tekstkleuren uit het Qt-palet.
- Openen, Opslaan, Afspelen, WAV importeren en Mix Down krijgen een accentkleurige achtergrond wanneer de actie beschikbaar is. De actieve werkmodus krijgt dezelfde accentkleur.
- Andere werkbalkiconen gebruiken een leesbare variant van de accentkleur. Menu-iconen hebben een eigen kleurtoepassing, zodat een licht icoon van een gevulde knop niet verdwijnt op een licht menu.
- De tekst op gevulde knoppen wordt op contrast gekozen. Hover en indrukken behouden leesbare tekst. Uitgeschakelde acties blijven uitgeschakeld, met leesbare grijze teksten en iconen.
- Wijzigingen aan het Qt-desktoppalet verversen de kleuren en iconen tijdens het draaien. De gewone bediening volgt het systeemlettertype; de grote klok houdt een monospacelettertype.
- Grafieken houden een donkere achtergrond en groene audio. Assen buiten de grafiek volgen het thema. Selecties en geselecteerde clips gebruiken de accentkleur. In een lege golfvorm staat nog één nulpunt op de tijdas in plaats van een rij identieke `0.000`-labels.
- Volume-/panpijltjes gebruiken de native spinboxweergave. Het extra-actiesknopje van een volle werkbalk heeft een zichtbaar chevron-icoon in de accentkleur.

De numerieke audioregels en projectbestanden zijn door deze interfacewijziging niet aangepast.

**Controle**

De GUI-regressietests wijzigen het palet van hetzelfde venster tussen licht/paars, donker/turquoise en licht/geel. Ze controleren werkelijk gerenderde achtergrondpixels, de actieve werkmodus, zichtbare modusteksten, menu-iconen, hovercontrast en het uitgeschakeld blijven van niet-beschikbare acties. De controles richten zich op minimaal 4,5:1 tekstcontrast op belangrijke knoppen en de klok, en 3:1 voor de getoetste inactieve labels en menu-iconen. Dit is geen volledige toegankelijkheidsaudit.

Zes echte Qt-weergaven op 1180 × 720 pixels zijn gerenderd: leeg, golfvorm met selectie en multitrack met geselecteerde clip, elk in twee nagebootste desktoppaletten. Die maat past binnen de gebruikelijke liggende Steam Deck-resolutie; het zijn offscreen-weergaven, geen nieuwe fysieke afspeeltest. De kleuren zijn voorbeelden: de gewone start gebruikt het palet dat Qt van de desktop ontvangt.

| Weergave | Donker/turquoise | Licht/paars |
| --- | --- | --- |
| Leeg | [PNG](screenshots/theme-previews/dark-teal-empty.png) | [PNG](screenshots/theme-previews/light-purple-empty.png) |
| Golfvorm | [PNG](screenshots/theme-previews/dark-teal-waveform.png) | [PNG](screenshots/theme-previews/light-purple-waveform.png) |
| Multitrack | [PNG](screenshots/theme-previews/dark-teal-multitrack.png) | [PNG](screenshots/theme-previews/light-purple-multitrack.png) |

Opnieuw maken, vanuit de projectmap:

```bash
PYTHONPATH=src python3 tools/render_theme_previews.py
make test
```

De previewtool verandert alleen het palet van zijn eigen offscreen-proces en schrijft PNG's in `build/theme-previews/`. De golfvormbewerking voor de preview gebeurt op een geopende kopie; bronbestanden worden niet overschreven.
