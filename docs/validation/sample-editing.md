# Directe samplebewerking — 0.18.0

Bij minstens acht logische pixels per sample verschijnen vierkante punten en
sample-indexen vanaf nul. Slepen houdt één frame/kanaal vast; alleen een lokale
weergavekopie wijzigt totdat loslaten één documenttransactie bevestigt. Escape,
focusverlies en weergavewisselingen annuleren het voorbeeld. Shift behoudt
de gewone selectiebediening. Dubbelklik/rechtsklik en Bewerken → Sample
bewerken openen exacte invoer. Een andere weergave-eenheid verandert geen
waarde totdat deze wordt bewerkt. De invoer ondersteunt ook bestaande headroom.

Document.set_sample vervangt slechts één rij, deelt alle ongewijzigde stukken
met Undo en bewaart selectie, cursor, kanaalkeuze en metadata. NaN, oneindig,
float32-overloop en ongeldige posities/kanalen worden vóór de transactie
afgewezen. Gelijke float32-waarden wijzigen ook de Redo-geschiedenis niet.

Negen gerichte regressies toetsen beide kanalen, eerste/laatste frame, Undo/Redo,
opslagstatus, geen nevenwijzigingen, annuleren, Shift-selectie, opnamevergrendeling,
exacte invoer en weergavebereiken. Een schijfbestand deelt zijn backing en
reserveert voor de correctie slechts acht bytes; WAV float32 heropent exact.
Het nieuwe venster valt ook onder de vijf talen en drie lettergroottes van de
bestaande indelingscontrole. De installatiezelftest toetst samplebewerking,
Undo/Redo, herstel en het venster in vijf talen.

De lokale volledige suite slaagt met 414 controles en zes expliciet
uitgeschakelde backendtests. Daarna slagen de negen definitieve samplecontroles,
ook bij 150% schermschaal, inclusief het werkelijk typen van een waarde vóór OK.
De gewone installatiezelftest slaagt eveneens. Voorbeelden van golfvorm en
invoervenster zijn visueel gecontroleerd. Catalogus: 1293 bronvormen per taal,
geen ontbrekende vertalingen.

Alle 415 definitieve controles slagen zonder overslaan op Debian, Fedora en
Arch. De geïnstalleerde pakketten doorstaan de gewone, afspeel-, opname- en
duplexzelftest op vijf doelen, inclusief Ubuntu 26.04 en Rolling. De gewone
zelftest bevat de nieuwe samplebewerking, herstel en het vertaalde venster.
De zes distributie- en publicatielogs bevatten geen onverwachte callback-,
RuntimeError- of bufferfouten. Tag, geteste broncommit, releasepunten en acht
assets (naam, grootte, uploadstatus en digestmetadata) zijn gecontroleerd.
[Distributiebouw 0.18.0](https://github.com/rene-timmermans/SoundSausage/actions/runs/43078651988)
en [installatiepakketten](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.18.0).
