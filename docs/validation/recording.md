# Opname en dagelijkse keten — 0.8.0

De [distributiebouw](https://github.com/rene-timmermans/SoundSausage/actions/runs/42979261330)
doorstaat alle 237 controles in Debian, Fedora en Arch. Daaronder vallen vier echte
Qt-backendcontroles met private virtuele in-/uitvoer. De geïnstalleerde pakketten
doorstaan ook de gewone, afspeel- en opnamecontrole op Ubuntu 26.04 en Rolling.
Er zijn geen Python-callbackfouten in de geverifieerde logs. [Release 0.8.0](https://github.com/rene-timmermans/SoundSausage/releases/tag/v0.8.0)
bevat de geteste pakketten. Een fysieke opname-/afspeelcontrole blijft open.

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

Qt-statusmeldingen worden via expliciete slots zonder enumargument verwerkt.
De invoercontrole gebruikt beide publieke beschikbaarheids-API’s, zodat ook
Qt 6.8 bruikbaar is wanneer het leesapparaat zelf nul beschikbare bytes meldt.
De backendtests weigeren verborgen Python-callbackfouten.

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
