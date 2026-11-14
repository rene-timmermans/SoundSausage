# Remaster: korte volumedalingen — 0.27.0

De aparte instelling Herstel korte volumedalingen ondersteunt 0–18 dB;
0 schakelt de nieuwe route uit. De preset Korte volumedalingen combineert
Sterk herstel met 12 dB herstelruimte voor korte gaten. Bestaande presets
en de uitkomst met 0 dB blijven behouden. ABI 7, projectformaat 6 en
herstelversie 3 veranderen niet; er zijn geen nieuwe afhankelijkheden.

## Verwerking

De gewone spectrale regeling volgt een waarde per FFT-hop. Voor diepere,
kortere dalingen gebruikt de extra route gekoppelde stereo-RMS over 4 ms,
bemonsterd per circa 1 ms. Een kandidaat moet aan beide kanten door voldoende
signaal worden ondersteund en samengaan met de bestaande drumdetectie.
De herstelroute accepteert korte intervallen van ongeveer 6–120 ms, met een
minimumdaling van 4 dB. Stilte en een geleidelijke uitfade krijgen geen
kunstmatige invulling.

Een complementaire midden-/hoogcomponent bewaart de laagste bas. De nieuwe
regeling vervangt de gewone correctie alleen waar sterker herstel nodig is;
de twee versterkingen worden niet opgeteld. Het herstel volgt een korte,
gladde envelop en wordt meteen begrensd als het oorspronkelijke signaal
terugkeert. Eén constante eindverzwakking bewaakt het gekozen sampleplafond.
Dit is geen true-peaklimiter of reconstructie van ontbrekende instrumenten.

Alle grote reeksen kunnen op schijf staan. Analyse, detectie, regeling en
uitvoer werken in begrensde blokken en geven voortgang/annuleren door.
Het eerste luistervoorbeeld verwerkt de volledige selectie voor dezelfde
piekruimte als toepassen; A/B en verplaatsen hergebruiken dat resultaat.

## Controles

Negen nieuwe backendproeven behandelen diepe korte dips tegenover Sterk herstel,
uitgeschakelde route, drums zonder dips, een geleidelijke uitfade en lange pauze,
overshoot na herstel, blokonafhankelijkheid, exacte voorbeeldprefix, stilte/korte
audio/hoge rates/grote eindige waarden, piekruimte, foutieve instellingen,
annuleren, één kanaal, Undo/Redo en schijfopslag. De bestaande dialoogproef
controleert ook kiezen en verlaten van de nieuwe preset. De installatiezelftest
voert de nieuwe route uit en opent het Remaster-venster.

In een volledig verwerkt lokaal muziekbestand daalt een korte middengebieddip
van circa 12 naar 4 dB; meerdere diepe dips krijgen ongeveer 6–8 dB meer
ondersteuning. Dit zijn metingen van een specifieke passage, geen garantie
voor andere muziek. De originele opname is via SHA256 ongewijzigd bevestigd.
De luistervergelijking moet nog bevestigen hoe natuurlijk de nieuwe stand klinkt.

Alle vijf offlinehandleidingen beschrijven de instelling, preset, vergelijken
vanaf het origineel en praktische grenzen. Catalogi: 1537 bronvormen zonder
ontbrekende vertaling; de onderwerpindexen blijven actueel.

## Distributiebouw

Alle **619 tests** slagen zonder overslaan op Debian, Fedora en Arch. De vijf
geïnstalleerde zelftests (gewoon, uitvoer, invoer, duplex, systeemgeluid) slagen
op vijf doelen: Debian, Fedora, Arch, Ubuntu 26.04 en Ubuntu Rolling.
De bestaande volledig-scherm-/4K-/GUI-blokkeerproef en plug-incontroles blijven groen.

[Workflow 43643203413](https://github.com/rene-timmermans/SoundSausage/actions/runs/43643203413)
is in de eerste poging volledig groen. Bron/tag: `7226f9ced19bb887f0c778b55dc1525f357c3237`.
De [release 0.27.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.27.0)
bevat Debian/Ubuntu-, Fedora- en Arch-pakketten, bronarchief, debugpakketten en
SHA256SUMS: acht bestanden. Namen, groottes, uploadstatus en SHA256-digestmetadata
zijn gecontroleerd; tag en korte releasepunten komen overeen met de geteste bron.
De fysieke [v1-proeven](../TODO.md) blijven open voor de onderdelen die nog niet
in de praktijk zijn bevestigd, waaronder het beluisteren van de nieuwe herstelstand.
