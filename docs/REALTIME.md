# Spooreffecten, plug-ins en opname met begeleiding

### Spooreffecten

Klik op **FX** naast een spoor of kies **Effecten → Spooreffecten**. Kies een effect en druk op **Toevoegen**. **OK** bevestigt; **Toepassen** verandert de instelling terwijl het venster openblijft. Dubbelklik of **Bewerken** opent de instellingen opnieuw. **Omhoog/Omlaag** verandert de volgorde; het vinkje schakelt een effect tijdelijk uit. **Verwijderen** haalt het uit de keten. Wijzigingen hebben Undo/Redo.

Een keten bevat maximaal zestien effecten: vaste versterking, kanaalmixer, dynamiek, grafische/parametrische EQ, filters, vertraging, echo, galm, ompolen en externe plug-ins. Clipvolume, lijnen en fades werken vóór de keten; spoorvolume en spoorpan erna. Mono wordt eerst stereo. Met **Uitklank na laatste clip** voeg je maximaal zestig seconden toe. Afspelen en eindmix gebruiken dezelfde keten. De bronnen blijven behouden.

**Toepassen** werkt tijdens luisteren; al naar het apparaat gestuurde audio behoudt de vorige instelling. Starten, zoeken en bypasswissels beginnen met nieuw effectgeheugen. Voor normaliseren, restauratie, tijd/toonhoogte, vervorming en convolutie gebruik je **Kopie in golfvorm bewerken**. Een volumeverloop teken je met **Volumelijn** op de clip.

### VST3, LV2 en LADSPA toevoegen

1. Installeer een native **64-bit Linux-audio-effect**.
2. Kies **Externe plug-in** in Spooreffecten en klik **Toevoegen**.
3. Kies het formaat en **Plug-in toevoegen**: een `.vst3`-bundel, `.lv2`-bundel of LADSPA-bibliotheek (`.so`). Effecten uit dezelfde bundel verschijnen afzonderlijk.
4. Kies het effect. Zoek een parameter op naam en wijzig de genormaliseerde positie van 0–100%. Vijftig procent betekent niet automatisch half volume. Discrete parameters hebben stappen; alleen-lezen parameters blijven vast.
5. **Toepassen** laat de instelling op het spoor horen; **OK** bevestigt en sluit.

Met **Plug-invenster openen** gebruik je het eigen venster van een ondersteunde VST3- of LV2-plug-in. Parameters en bewaarbare status uit dat venster worden meegenomen bij bevestigen. De eigen vensters vereisen **X11 of XWayland**. Bij een ontbrekend of niet-ondersteund venster blijven de algemene parameterregelaars beschikbaar. LADSPA gebruikt deze regelaars altijd. LV2-vensters die een GTK-/Qt-adapter vereisen, worden niet ingebed.

VST3 ondersteunt één stereo-invoerbus en één stereo-uitvoerbus met float32-verwerking. LV2 en LADSPA ondersteunen mono- en stereo-effecten met evenveel in- en uitgangen; een mono-effect krijgt per stereokanaal een eigen instantie. MIDI-instrumenten, extra sidechains, VST2 en Windows-plug-ins worden niet ondersteund. Verplichte LV2-functies of poorttypen die niet beschikbaar zijn, worden gemeld; MIDI/Atom-verwerking ontbreekt. LV2-status die externe bestanden vereist, kan niet volledig worden opgeslagen en geeft een melding. Kies daarvoor een effect met zelfstandig bewaarbare status.

Plug-ins draaien in een apart hulpproces. Een crash, vastloper of ongeldige audio stopt het afspelen met een melding; de vastgelegde opname blijft bewaard. Projecten bewaren parameters en maximaal 1 MiB status per effect. De plug-in en eigen bibliotheken, samples of responsbestanden blijven apart geïnstalleerd. Voeg op een andere computer dezelfde versie toe. Ontbrekende of gewijzigde plug-ins worden gemeld; afspelen/export vraagt om het passende effect of bewust uitschakelen.

### Automatische plug-invertraging

Gerapporteerde **verwerkingsvertraging** van plug-ins wordt automatisch per spoor gecompenseerd, tijdens afspelen en eindmix. Vertragingen in een keten worden opgeteld; bypass en gewijzigde instellingen worden opnieuw verwerkt. De tijdlijn en mixduur blijven gelijk. Een muzikale echo, voorvertraging of galm blijft hoorbaar: deze hoort bij het effect. Compensatie vereist een juiste melding door de plug-in en is begrensd tot tien seconden per spoor. Een ongeldige of voortdurend veranderende vertraging geeft een melding.

### Opnemen met begeleiding en synchronisatie

Zet begeleiding op sporen, kies het doelspoor en plaats de cursor. Druk **R**, kies ingang en nieuwe clip als bestemming en vink **Bestaande sporen afspelen tijdens opnemen** aan. De bestaande sporen spelen met effecten; de ingang wordt niet via de luidsprekers teruggespeeld. **P** pauzeert/hervat beide; **Stoppen/Esc/Spatie/R** houdt de take als één Undo-stap. **Opname verwerpen** verwijdert alleen de nieuwe take. Bij apparaat- of plug-inverlies blijft vastgelegde audio behouden.

**Automatische synchronisatie** koppelt de opnamepositie aan de afspeelklok en meet het verschil tussen de in- en uitvoerklokken. Bij voldoende lange, betrouwbare metingen wordt de opnamelengte na Stop voorzichtig gecorrigeerd. Een korte of onstabiele meting rekt de take niet op. Dit vervangt geen meting van de fysieke in-/uitvoerroute.

Voor die route kies je **Opties → Opname kalibreren**, of de kalibratieknop in het opnamevenster:

1. Kies dezelfde apparaten, samplerate, eerste ingangskanaal en buffer als voor de opname.
2. Verbind uitgang en ingang met een geschikte loopbackkabel. Een microfoon bij een luidspreker kan ook; dan telt de akoestische looptijd mee. Begin met een laag niveau.
3. Klik **Kalibratie starten**. Ongeveer zes seconden zachte testpulsen meten de verbinding. De ingang wordt niet teruggespeeld.
4. Alleen een betrouwbaar resultaat wordt opgeslagen. Bij stilte, oversturing, onduidelijke signalen of instabiele timing volgt een melding; een eerdere goede kalibratie blijft bestaan.
5. Controleer de plaatsing met een korte proeftake. Gebruik na wijziging van apparaat, samplerate, ingang of buffer een passende nieuwe kalibratie.

Het profiel hoort bij de gekozen apparaatcombinatie en instellingen. Automatische synchronisatie past de opgeslagen routecorrectie toe. Zonder profiel blijft kloksynchronisatie beschikbaar, maar kan fysieke vertraging overblijven. Als alternatief schakel je automatisch uit en gebruik je **Opnamepositie verschuiven**: negatief is eerder, positief later. Een take die 15 ms te laat staat vraagt bijvoorbeeld −15 ms. Handmatige en automatische correctie worden niet bij elkaar opgeteld.

### Punch-in/out: alleen een passage opnieuw opnemen

1. Open Multitrack, kies het doelspoor en selecteer het gewenste tijdvak op de tijdlijn of met **Bewerken → Selectie instellen**.
2. Kies **Opties → Punch-in/out** of **Shift+R**. In het opnamevenster staat **Punch-in/out in selectie**.
3. Stel ingang, synchronisatie, **Voorloop** (standaard 2 s) en **Overgang** (standaard 5 ms) in. De selectie bepaalt de opnamegrenzen; begeleiding is ingeschakeld.
4. Start. De ingang warmt eerst op; daarna speelt de oorspronkelijke passage tijdens de voorloop. Binnen het gekozen interval wordt alleen het doelspoor gedempt, terwijl de nieuwe take wordt opgenomen. Andere sporen blijven spelen.
5. Na het interval stopt de opname automatisch, met een korte afronding voor synchronisatie. Alleen de gecorrigeerde audio binnen de selectie komt als nieuwe clip op het spoor.

Een korte overgang mengt oud en nieuw binnen de selectiegrenzen, maximaal 100 ms. Audio buiten het interval blijft behouden. De oorspronkelijke clips blijven eveneens bewaard: een punch dekt hun betreffende gedeelte af. **Ctrl+Z** herstelt de vorige situatie in één stap. Selecteer de oude clip en kies **Afgedekte audio herstellen** om zijn afdekking op te heffen; verwijder of demp de nieuwe take als die anders tegelijk hoorbaar wordt. Deze opdracht herstelt alle afgedekte gebieden van de gekozen clip.

Vroeg stoppen bewaart alleen het werkelijk opgenomen deel binnen het interval. Stoppen vóór het interval verandert de sessie niet; de ruwe take blijft beschikbaar via **Bestand → Werk herstellen**. Herstel van een nog niet bevestigde opname biedt de ruwe take aan, inclusief eventuele voor-/naloop, zodat je die zelf kunt plaatsen. Een voltooide punch wordt met zijn afdekking in project en crashherstel bewaard.

### Sessies bewaren en heropenen

**Sessie opslaan / Sessie opslaan als** bewaart gebruikte audio, clips, lijnen, spoorketens, plug-ininstellingen en punchgebieden. **Sessie openen** herstelt deze bewerkbare sessie. **Eindmix maken** maakt een WAV of MP3 met dezelfde effecten. Bewaar het project om afzonderlijke sporen te kunnen blijven veranderen. Nieuwe projecten vereisen SoundSausage **0.19.0 of nieuwer**; eerdere projectversies blijven leesbaar. Een ontbrekende plug-in verhindert het openen en herstellen van de bronnen niet.

