# Golfvorm tekenen — 0.20.0

## Bediening en bereik

De tekenmodus is bereikbaar met de potloodknop, Bewerken → Golfvorm tekenen en
D. Linkermuisknop tekent rechtstreeks, zonder een zichtbaar punt te moeten raken.
Shift blijft selecteren. De start bepaalt het kanaal; verticaal oversteken naar
het andere kanaal wijzigt die keuze niet. Samplepunten voor de eerdere losse
correctie verschijnen vanaf twee logische pixels in plaats van acht. Hun
markering schaalt mee; een kader toont het punt onder de muis.

DrawingStroke bewaart uitsluitend analytische groepen en hun lijnuiteinden.
De groepsgrootte is ceil(2 × zichtbare frames / logische tekenbreedte), met een
minimum van één sample en een maximum van sample_rate samples: één seconde.
Groepen zijn op deze grootte uitgelijnd. Eén beweging mag meerdere groepen
bestrijken. Tussen opeenvolgende muisposities wordt lineair geïnterpoleerd;
opnieuw geraakte groepen worden door het laatste verloop vervangen.
Samplewaarden blijven binnen −1 tot +1. Het betreft vervanging, geen verticale
verschuiving met behoud van de oude golfvorm.

Tijdens tekenen blijven document en Undo intact; het gemarkeerde vlak met lijn
is het voorbeeld. Loslaten bevestigt één transactie. Escape, focusverlies,
weergavewissel en uitschakelen annuleren. Opname blokkeert de bediening en
annuleert een actief voorbeeld. De bestaande exacte numerieke invoer blijft.

## Opslag en behoud

Document.draw_samples valideert alle bereiken, kanaal, duur en eindwaarden vóór
verwerking. Resultaten voor meerdere groepen worden vóór de commit opgebouwd.
Andere samples, het andere kanaal, selectie, cursor, metadata en tijdas blijven
behouden; ongewijzigde stukken worden met Undo gedeeld. Gelijke float32-resultaten
maken geen nieuwe geschiedenisstap. Grote gezamenlijke resultaten gaan naar
de bestaande schijfopslag, ook als de afzonderlijke groepen klein zijn.
Voortgang/annuleren en een allocatiefout laten het bronwerk intact.

## Controles

Zeven nieuwe tekencontroles toetsen zoomverhoudingen, de secondegrens per groep,
langere bewegingen, lineaire interpolatie, terugtekenen, amplitudebegrenzing,
documentranden, kanaalbehoud, metadata, Undo/Redo, no-op, ongeldige bereiken,
annuleren, schijffout en schijfopslag. GUI-controles tekenen zonder samplepunten,
controleren het voorbeeld en bevestigen één Undo-stap. Escape, moduswissel,
zoomen, opnemen en Shift-selectie zijn meegenomen.

Twee aanvullende samplecontroles toetsen de tweepixeldrempel, aangrenzende
punten, compacte markeringen en precies één gewijzigd sample bij minder zoom.
Alle achttien gerichte teken-/samplecontroles slagen lokaal. De gewone
installatiezelftest controleert tekenen, kanaalbehoud en Undo, en de nieuwe
handleidingsectie in alle vijf talen. De catalogi hebben 1434 bronvormen zonder
ontbrekende vertalingen. Het voorbeeld is visueel gecontroleerd.

De eerste volledige lokale run telde 460 tests met negen expliciet uitgeschakelde
backend-/nativevensterproeven en één stagingfout terwijl de handleidingen nog
werden bijgewerkt. De afzonderlijke stagingcontrole en de gewone zelftest slagen
met de complete vijf handleidingen. Een definitieve volledige run volgt met een
ongewijzigde bronstand; de distributiebouw schakelt de backendproeven wel in.

Definitieve volledige suite, distributiepakketten en publicatie worden na de
releasebouw hieronder vastgelegd.
