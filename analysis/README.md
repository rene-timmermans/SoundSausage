# Cool Edit Pro — onderzoeksmap

Begin bij [ANALYSE.md](ANALYSE.md) voor de bevindingen en [BOUWPLAN.md](BOUWPLAN.md) voor het voorstel voor een Linux-implementatie.

Dit is de statische onderzoeksbundel, opgesteld vóór de prototypebouw. De eerste Linux-editor staat inmiddels in de bovenliggende projectmap; zie [de projectinstructies](../README.md) en [de actuele status](../docs/STATUS.md). De oorspronkelijke Windows-programma's zijn niet uitgevoerd. Het onderzoek volgt de REA-skills; een REA-MCP-server was niet verbonden. Ghidra, objdump, winedump en de bijgevoegde Python-tools zijn daadwerkelijk gebruikt.

De permanente projectlocatie is nu `/home/deck/Documenten/Codex/CoolEdit/`; deze onderzoeksbundel staat in de submap `analysis/`. Na het wijzigen van de sessiewerkmap is de schrijftoegang succesvol getest. Alle 86 bestanden uit het oorspronkelijke manifest zijn na het kopiëren met SHA-256 gecontroleerd.

De eerdere analyse vond plaats in `/tmp/cooledit-analysis/`. De oorspronkelijke herkomstregistratie blijft bewaard; [workspace-relocation.json](evidence/workspace-relocation.json) legt de overgang naar de huidige werkmap vast.

| Bestand/map | Inhoud |
| --- | --- |
| `ANALYSE.md` | Bevindingen, bronverwijzingen, zekerheid en beperkingen |
| `BOUWPLAN.md` | Architectuurvoorstel, bouwvolgorde en acceptatiecriteria |
| `evidence/provenance.json` | Bronhashes, toolversies, controles en dekkingsgrenzen |
| `evidence/pe/inventory.json` | Volledige module- en mediuminventaris |
| `evidence/pe/*.json` | PE-headers, imports, exports en UI-resourcegegevens per bestand |
| `evidence/ui-spec.json` | Menu's, dialoogcontrols en hun posities, sneltoetsen en scriptinventaris |
| `evidence/menus.txt` | Leesbare statische menucommando's |
| `evidence/shortcuts.json` | Acceleratorregels met bijbehorende menuverwijzingen |
| `evidence/*-decompiled.txt` | Gerichte decompileruitvoer; interpretatie, geen oorspronkelijke broncode |
| `evidence/*-asm.txt` | Assembler van de gevolgde effectcallbacks |
| `evidence/*-winedump.txt` | Onafhankelijke controle van drie exporttabellen |
| `evidence/ghidra-*.log` | Analyse- en scriptlogs, inclusief timeouts |
| `tools/inspect_pe.py` | PE32-reader met alleen Python-standaardbibliotheek |
| `tools/build_ui_spec.py` | Export van UI-specificatie en scriptcommando's |
| `tools/FocusExport.java` | Ghidra-script voor geselecteerde functies en kruisverwijzingen |

De eigen PE-reader is op 162 benoemde exports inclusief RVA's en ordinalen vergeleken met winedump: alle kwamen overeen. De 57 PE-bronhashes waren na analyse ongewijzigd. Dit controleert de inventarisatie; het is geen functionele test van de audiotoepassing.

De Python-inventaris kan vanuit deze map opnieuw worden gemaakt, bijvoorbeeld naar een aparte uitvoermap:

```bash
python3 tools/inspect_pe.py \
  --installed /home/deck/.wine/drive_c/coolpro \
  --media /home/deck/CoolEdit \
  --out /tmp/cooledit-recheck/evidence/pe
python3 tools/build_ui_spec.py \
  --installed /home/deck/.wine/drive_c/coolpro \
  --evidence /tmp/cooledit-recheck/evidence
```

Deze commando's lezen de originelen en schrijven alleen naar de gekozen uitvoermap. Ghidra is niet nodig voor deze twee scripts. De reader is gemaakt voor de aanwezige PE32-bestanden, niet als algemene parser voor willekeurige bestandsformaten.

De gebruikte headless Ghidra-aanroepen, doelpaden en geselecteerde functies zijn terug te vinden in de consolelogs. Ghidra gebruikte tijdelijke eigen instellingen/cache en tijdelijke projecten onder `/tmp`. De tijdelijke projecten zijn na voltooiing verwijderd. Er zijn geen bestaande Ghidra-projecten gewijzigd.
