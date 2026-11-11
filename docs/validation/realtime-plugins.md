# Realtime spoorketens, VST3 en duplex — 0.15.0

Negentien aanvullende controles toetsen stateful effecten, volgorde/bypass,
uitklank, Undo/Redo, live wijzigingen, bronbehoud, projectopslag en herstel.
Tien interne effecten leveren sample voor sample dezelfde uitkomst als de
bestaande offlineverwerking, ook met blokken van 377 frames. Gedeeltelijke
PCM-writes en omzetting van 8 kHz naar 48 kHz behouden lengte en kanaalindeling.
Afspelen vraagt geen volledige sessierender; de producentqueue is begrensd.
De bestaande lange-bestanden-/geheugencontroles blijven slagen.

Een afzonderlijk gecompileerde VST3-testplug-in gebruikt de publieke VST3 ABI:
module-entry, factory, component, controller, stereobussen, genormaliseerde
parameterqueues en binaire componentstatus. Tests toetsen bundeldetectie, audio,
statusherstel zonder parameters opnieuw te sturen, bewaren/heropenen, recovery,
live parameterwijzigingen met dezelfde helper en de generieke bediening.
Een opzettelijke abort en een vastgelopen process-call stoppen alleen de helper.
Ontbrekende of gewijzigde plug-ins blijven herkenbaar in het geladen project en
worden niet stilzwijgend overgeslagen bij mixdown. Een project kan geen eigen
uitvoerbaar bibliotheekpad aanleveren.

Duplexcontroles toetsen gelijktijdig afspelen/opnemen, samen pauzeren en hervatten,
opnameverschuiving, Undo en behoud van een take bij uitvoerverlies. Twee expliciete
backendtests gebruiken een private virtuele PulseAudio-invoer en -uitvoer bij
48 kHz en een afwijkende sessierate van 44,1 kHz. Een regressieproef met een vooraf gevulde invoerbuffer toetst dat de pauzetest
niet afhankelijk is van de snelheid waarmee een backend zijn eerste frames levert.
De nieuwe duplex-selftest
controleert ook geïnstalleerde pakketten. De gewone selftest opent geen
microfoon en controleert de laadbaarheid van de geïsoleerde VST3-host.

De volledige lokale suite doorstaat 363 controles; zes expliciete backendtests
worden lokaal overgeslagen. Distributiecontroles worden vóór publicatie uitgevoerd.
De eerdere fysieke USB-test geldt voor gewone opname/weergave. De nieuwe
duplexroute en fysieke offset moeten met de gekozen interface worden beluisterd
en afgesteld. Er is geen automatische kalibratie of garantie voor apparaatdrift.
Plug-ins met eigen vereiste hostuitbreidingen zijn niet universeel ondersteund.
Eigen plug-invensters en automatische plug-inlatencycompensatie ontbreken.

VST3-interfacebron: [Steinberg interfaces](https://github.com/steinbergmedia/vst3_pluginterfaces),
commit `4f547e8e102b47de4a8b8aaf343c73b700786372`, MIT. Herkomst en één lokale
format-typecorrectie staan in third_party/vst3/ORIGIN.md. DSP-ABI blijft 7; de
VST3-brug is een afzonderlijke bibliotheek. Projectformaat 4 bewaart de ketens,
oudere projectformaten blijven leesbaar.
