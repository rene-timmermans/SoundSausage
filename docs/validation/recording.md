# Opname en dagelijkse keten — 0.8.0

Lokaal doorstaat de suite 237 controles, met vier echte audiobackendcontroles
overgeslagen. De beperkte ontwikkelomgeving kan de fysieke audioserver niet
openen. De pakketbouw gebruikt private virtuele in-/uitvoer voor die controles.

Gecontroleerd zijn begrensde reads en complete frames, genormaliseerde float- en
integerinvoer, mono/stereokanalen, pauze/hervatten, apparaatverlies, oude callbacks,
duurbegrenzing, afgebroken/partiële schijfwrites en herstel na procesbeëindiging.
De hersteljournalen bewaren uitsluitend een duurzaam geschreven prefix. Langzame
checkpointschrijvers blokkeren de Qt-interface niet. Andere appinstanties worden
overgeslagen. Oorspronkelijke opnamen blijven behouden.

De echte Qt-editor doorloopt opnemen, een Amplitude-effect toepassen, WAV bewaren,
in multitrack invoegen, een volgende take opnemen, clips instellen, project bewaren,
heropenen en een WAV-eindmix schrijven. Controle op Undo, behoud bij annuleren,
klok/meters, terugzetten van acties en bevestigen van het juiste vervangingsdoel
maakt deel uit van dezelfde workflow.

De 160 MiB geheugencontrole omvat ook het schrijven van een opnamebestand en het
toevoegen aan het document. De lokale extra resident geheugengroei bleef ongeveer
17 MiB in dit scenario. Dit is een meetresultaat, geen grens voor elk project.

## Nog te bevestigen op fysieke hardware

- Kies een echte USB-microfoon of audio-interface onder Audio Hardware.
- Neem enkele seconden spraak op, pauzeer en hervat, en stop de take.
- Luister terug; controleer geluid, cursor, meters en de uitgesloten pauzetijd.
- Bewaar als WAV en heropen die om het resultaat opnieuw te beluisteren.

Deze praktische controle blijft open totdat het resultaat bekend is. Gelijktijdig
opnemen en afspelen, punch-in/out en automatische latencycompensatie zijn nog geen
onderdeel van de beschikbare functies.
