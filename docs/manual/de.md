# SoundSausage — Handbuch

Version 0.23.0. Ein intuitiver, einfach zu bedienender Audioeditor mit allen Werkzeugen dort, wo man sie erwartet. Dieses Handbuch beschreibt die verfügbaren Arbeitsabläufe, Effekte und praktischen Grenzen.

<!-- soundsausage-contents:start -->
<a id="ss-contents"></a>

## Inhalt

Ein Thema anklicken, um direkt dorthin zu springen. Die Schaltfläche Inhalt führt zurück.

- [1. Sprache und Hilfe](#ss-topic-1-sprache-und-hilfe)
- [2. Schnellstart und Arbeitsbereich](#ss-topic-2-schnellstart-und-arbeitsbereich)
- [3. Dateien, Projekte und Wiederherstellung](#ss-topic-3-dateien-projekte-und-wiederherstellung)
  - [MP3 und WAV](#ss-topic-mp3-und-wav)
  - [MP3-Metadaten nach dem Bearbeiten](#ss-topic-mp3-metadaten-nach-dem-bearbeiten)
- [4. Wiedergabe, Zoom und Audiogeräte](#ss-topic-4-wiedergabe-zoom-und-audiogerate)
- [5. Aufnehmen](#ss-topic-5-aufnehmen)
- [6. Auswahl, Kanäle und Bearbeitung](#ss-topic-6-auswahl-kanale-und-bearbeitung)
  - [Einzelne Samples bearbeiten](#ss-topic-einzelne-samples-bearbeiten)
  - [Wellenform zeichnen](#ss-topic-wellenform-zeichnen)
- [7. Effekte anwenden](#ss-topic-7-effekte-anwenden)
  - [Amplitude](#ss-topic-amplitude)
    - [Verstärken / Blenden](#ss-topic-verstarken-blenden)
    - [Kanalmischer](#ss-topic-kanalmischer)
    - [Dynamikbearbeitung](#ss-topic-dynamikbearbeitung)
    - [Lautstärkeverlauf](#ss-topic-lautstarkeverlauf)
    - [Normalisieren](#ss-topic-normalisieren)
    - [Invertieren, Rückwärts und Stille](#ss-topic-invertieren-ruckwarts-und-stille)
  - [EQ und Filter](#ss-topic-eq-und-filter)
    - [Grafischer Equalizer](#ss-topic-grafischer-equalizer)
    - [Parametrischer Equalizer](#ss-topic-parametrischer-equalizer)
    - [Filter](#ss-topic-filter)
  - [Delay, Echo und Hall](#ss-topic-delay-echo-und-hall)
    - [Verzögerungseffekte → Verzögerung](#ss-topic-verzogerungseffekte-verzogerung)
    - [Echo](#ss-topic-echo)
    - [Hall](#ss-topic-hall)
  - [Rauschminderung und Klickreparatur](#ss-topic-rauschminderung-und-klickreparatur)
    - [Rauschschätzung → Festes Rauschprofil](#ss-topic-rauschschatzung-festes-rauschprofil)
    - [Klickentfernung](#ss-topic-klickentfernung)
  - [Zeit und Tonhöhe](#ss-topic-zeit-und-tonhohe)
    - [Zeit/Tonhöhe → Zeitdehnung](#ss-topic-zeit-tonhohe-zeitdehnung)
    - [Tonhöhenverschiebung](#ss-topic-tonhohenverschiebung)
  - [Spezialeffekte](#ss-topic-spezialeffekte)
    - [Spezial → Verzerrung](#ss-topic-spezial-verzerrung)
    - [Faltung](#ss-topic-faltung)
- [8. Erzeugen, analysieren und umwandeln](#ss-topic-8-erzeugen-analysieren-und-umwandeln)
- [9. Mehrspur und Automation](#ss-topic-9-mehrspur-und-automation)
- [10. Echtzeit-Spureffekte, Plug-ins und Aufnahme](#ss-topic-10-echtzeit-spureffekte-plug-ins-und-aufnahme)
  - [VST3, LV2 und LADSPA](#ss-topic-vst3-lv2-und-ladspa)
  - [Automatischer Plug-in-Latenzausgleich](#ss-topic-automatischer-plug-in-latenzausgleich)
  - [Aufnahme mit Begleitung und Synchronisierung](#ss-topic-aufnahme-mit-begleitung-und-synchronisierung)
  - [Punch-in/out](#ss-topic-punch-in-out)
- [11. Aufnahme mit Begleitspuren](#ss-topic-11-aufnahme-mit-begleitspuren)
- [12. Tastenkürzel, Favoriten und Probleme](#ss-topic-12-tastenkurzel-favoriten-und-probleme)

<!-- soundsausage-contents:end -->

<a id="ss-topic-1-sprache-und-hilfe"></a>

## 1. Sprache und Hilfe

Unter **Optionen → Sprache** Nederlands, English, Deutsch, Français oder Español wählen. Menüs, Fenster, Hinweise und das geöffnete Handbuch wechseln sofort. Die Auswahl bleibt beim nächsten Start erhalten. Datei-, Spur- und Plug-in-Namen behalten ihre Schreibweise.

**Hilfe → Handbuch** oder **F1** öffnet dieses Handbuch ohne Internet neben dem Editor. **Strg+F** aktiviert die Suche; **F3** findet den nächsten, **Umschalt+F3** den vorherigen Treffer. Die Suchknöpfe setzen am anderen Ende fort. Nur angeklickte Weblinks benötigen Internet. **Über** zeigt Version, Autor, Lizenz, Website und Komponenten.

<a id="ss-topic-2-schnellstart-und-arbeitsbereich"></a>

## 2. Schnellstart und Arbeitsbereich

Das Programmsymbol mit violettem Hintergrund erscheint in den Fenstertitelleisten und der Taskleiste. **Hilfe → Über** zeigt das freigestellte Maskottchen neben den Programminformationen.

Eine WAV- oder MP3-Datei mit **Datei → Öffnen** öffnen. **Leertaste** startet oder stoppt. Einen Abschnitt markieren, **Effekte → Amplitude → Normalisieren** wählen, mit **Vorschau** anhören und mit **OK** anwenden. **Strg+Z** macht die Änderung rückgängig. Mit **Speichern unter** ein separates Ergebnis speichern. Für mehrere Aufnahmen **Neue Mehrspursitzung** erstellen, WAVs oder MP3s importieren und mit **Abmischen** abschließen.

**Wellenform bearbeiten** bearbeitet eine Aufnahme; **Mehrspuransicht** kombiniert Clips. Mit **Tab**, oberen Knöpfen oder **Ansicht** wechseln; beide Dokumente bleiben verfügbar. Hinweise erklären die Knöpfe. **Werkzeugleistenbeschriftungen anzeigen** ergänzt Text, **Optionen → Statusleiste anzeigen** blendet die schmale Informationszeile ganz unten unter der Pegelanzeige ein oder aus. Sie zeigt Wiedergabestatus und Dateidaten; die Auswahl bleibt beim nächsten Start erhalten. **F11** schaltet Vollbild. Die Uhr folgt dem Audio; Auswahlfelder zeigen Anfang, Ende und Länge, Ansichtsfelder den sichtbaren Zeitraum. Rote Spitzen zeigen Übersteuerung, ein Stern ungespeicherte Änderungen.

Fenster und Diagrammskalen passen sich an die Schriftgröße des Desktops und die gewählte Sprache an. Ist ein Formular zu groß für den Bildschirm, durch die Einstellungen scrollen; die Schaltflächen zum Bestätigen und Abbrechen bleiben erreichbar.

Zwei dünne horizontale Linien markieren die Unterkante des linken und die Oberkante des rechten Kanals. Sie enden an den Seiten des Wellenformbereichs, auch bei der Liveaufnahme.

<a id="ss-topic-3-dateien-projekte-und-wiederherstellung"></a>

## 3. Dateien, Projekte und Wiederherstellung

**Neu** erstellt eine leere Mono- oder Stereowellenform mit gewählter Abtastrate. **Öffnen** liest WAV und MP3. **Speichern** aktualisiert die Datei, **Speichern unter** wählt Name/Format, **Auswahl speichern** speichert nur ausgewählte Zeit und Kanäle. WAV unterstützt PCM 8/16/24/32 Bit und Float32. PCM16 eignet sich zum Austausch; Float32 erhält interne Spitzen über 0 dBFS. Höhere Bittiefe ersetzt keine verlorenen Details. Bei mehrdeutigen älteren 32-Bit-WAVs zwischen PCM und älterem Float wählen; Abbrechen lässt die Datei unverändert.

WAV-Texte, Cuepunkte und Beschriftungen bleiben erhalten. Cuepunkte folgen Bearbeitung, Einfügen und Auswahlexport; der Zieltitel bleibt erhalten. Recorderfelder werden wörtlich bewahrt und nach Effekten nicht neu berechnet. Zusätzliche Metadaten sind auf 16 MiB begrenzt. Größere Eingaben werden abgewiesen; ausgelassene Exportfelder benötigen Bestätigung. Die Mischung vereinigt keine Quellmarker. Große WAVs verwenden bei Bedarf RF64.

**Neue Mehrspursitzung**, **Sitzung öffnen**, **Sitzung speichern** und **Sitzung speichern unter** verwalten bearbeitbare Projekte. Ein SoundSausage-Projekt (`.celp`) enthält Audio, Clips, Linien, Spureinstellungen, Effektreihenfolge/Bypass/Nachklang und VST3-Einstellungen. Zusätzlich zur WAV das Projekt speichern, um einzelne Spuren zu behalten. Frühere SoundSausage-Projektversionen bleiben lesbar; neu gespeicherte Projekte benötigen App 0.19.0 oder neuer. Alter `.ses`-Import ist begrenzt; zum Weiterarbeiten ein neues SoundSausage-Projekt verwenden.

**Schließen / Strg+W** schließt die aktuelle Wellenform; in Mehrspur heißt es **Sitzung schließen**. Bei Nachfrage speichern, verwerfen oder abbrechen. Andere Ansicht und Zwischenablage bleiben verfügbar. **Beenden / Strg+Q** beendet die Anwendung und fragt nach ungespeicherter Arbeit.

Lange Dateien werden blockweise auf Platte verarbeitet, ohne frühere 128-MiB-Grenze. Freien Platz für Quellkopien, Ergebnisse und Rückgängig-Verlauf vorhalten. Sitzungen sind auf 24 Stunden und 32 Spuren begrenzt. Lange Vorgänge zeigen Fortschritt und Abbrechen. Abbrechen erhält Audio, Auswahl, Verlauf und die bisherige Exportdatei. Ein angewandter Effekt ist ein Rückgängig-Schritt.

Nach unerwartetem Beenden den letzten Stand wiederherstellen, entfernen oder später öffnen. **Datei → Arbeit wiederherstellen** öffnet aufbewahrte Kopien. Originaldateien bleiben erhalten; Wellenform, Sitzung, Kanäle, Clips, Linien und Ketten kehren zurück, der Verlauf beginnt neu. Bestätigte Änderungen werden gesichert, Cursor/Auswahl etwa sekündlich. Aktive Instanzen werden übersprungen. Normales Speichern/bestätigtes Schließen räumt die eigene Kopie auf. Eigene Sicherungen behalten; bei Plattenfehlern kann der Stand älter sein.

<a id="ss-topic-mp3-und-wav"></a>

### MP3 und WAV

MP3-Dateien über **Datei → Öffnen** laden, in Mehrspur importieren oder auf die Zeitleiste ziehen. Auswahl, Bearbeitung und Effekte arbeiten mit dem dekodierten Audio. **Speichern unter**, **Auswahl speichern** und **Abmischen** bieten WAV und MP3; die Dateiendung folgt dem Format. Speichern einer vorhandenen MP3 verwendet die gewählte MP3-Kodierung; Speichern unter kann eine WAV-Kopie erstellen.

MP3 bietet 128, 192, 256 und 320 kb/s. Höhere Bitraten benötigen mehr Speicher und erhalten meist mehr Details. MP3 ist verlustbehaftet: erneute Kompression kann weitere Details verlieren. WAV vermeidet einen weiteren MP3-Kompressionsschritt, stellt aber verlorene Informationen nicht wieder her. Float32-WAV eignet sich zum Weiterbearbeiten, PCM16 zum Austausch. MP3 verwendet die nächstliegende Abtastrate von 32.000, 44.100 oder 48.000 Hz bei gleicher Dauer; das Dokument behält seine Abtastrate. Diese Abtastraten passen zu allen vier angebotenen MP3-Bitraten; bei niedrigeren Abtastraten kann der Encoder eine niedrigere Bitrate als angefordert verwenden. Die Mindestdauer von 2 ms vermeidet, dass sehr kurze Fragmente nach dem MP3-Decodieren länger werden. Auswahlen unter 2 ms als WAV speichern.

<a id="ss-topic-mp3-metadaten-nach-dem-bearbeiten"></a>

### MP3-Metadaten nach dem Bearbeiten

Titel, Künstler, Album, Kommentare und Cover bleiben erhalten, auch über WAV und SoundSausage-Projekte. Die Dauer wird aktualisiert. Gewöhnliche Tags und vorhandene Kennungen bleiben bei der Zieldatei.

**Kapitel** folgen den Bearbeitungen automatisch. Löschen verschiebt spätere Kapitel zurück, Einfügen verschiebt sie nach vorn. Trimmen und Auswahlexport behalten überlappende Kapitel relativ zum erhaltenen Ausschnitt. Leere und vollständig entfernte Kapitel entfallen; das Inhaltsverzeichnis behält gültige Verweise. Einfügen übernimmt Kapitelnamen und Hierarchie des Ausschnitts, während allgemeine Tags der Zieldatei erhalten bleiben. Zeitdehnung passt die Kapitelgrenzen an; eine Abtastratenänderung erhält ihre Millisekundenzeiten. Rückgängig stellt auch die ursprünglichen Metadaten wieder her.

Kapitel sind auf eine Millisekunde genau; auf null Dauer gerundete Reste entfallen. Umkehren spiegelt Kapitel vollständig innerhalb des Bereichs. Ein teilweise umgekehrtes Kapitel, das getrennte Audioteile beschreiben würde, entfällt; Kapitel um den gesamten umgekehrten Bereich bleiben erhalten.

**Messwerte** können nach einer Audiobearbeitung veraltet sein. Erkannte ReplayGain-, R128-, MP3Gain- und Spitzenwerte, Fingerabdrücke, relative Lautstärkeanpassungen und alte Encoderangaben werden entfernt. Nicht unterstützte zeitgebundene Angaben wie synchronisierte Liedtexte, alte Suchindizes und Synchronisationspositionen entfallen ebenfalls. ReplayGain wird nicht neu berechnet. Eine Tempoänderung entfernt den vorhandenen BPM-Wert; eine Tonhöhenänderung entfernt die vorhandene Tonart. Andere Bearbeitungen erhalten diese beiden Werte. Gewöhnliche Liedtexte ohne Zeitcodes und unbekannte private Felder bleiben unverändert. Erneutes MP3-Codieren entfernt ebenfalls alte Messwerte und Dateipositionen, da Kompression Audio und Dateiaufbau verändert. Encoderangaben stammen aus der tatsächlich neu geschriebenen Datei.

**WAV nach MP3:** unterstützte INFO-Felder für Titel, Künstler, Album, Genre, Datum, Titelnummer, Urheberrecht und Kommentare werden übernommen. Vorhandene ID3-Werte haben Vorrang. Nicht unterstützte Felder, fehlerhafte INFO-Daten und widersprüchliche Werte werden vor dem Export gemeldet. **Nein** bricht ab und erhält eine vorhandene Zieldatei; **Ja** setzt mit den aufgeführten Auslassungen fort. Zusätzliche ID3-Tags in einer WAV-Datei werden vor dem Weglassen ebenfalls aufgeführt. Alte Softwareangaben werden durch die neuen Encoderangaben ersetzt. Nicht unterstützte WAV-Marker und andere Dateidaten erfordern diese Entscheidung ebenfalls.

Zusätzliche Metadaten bleiben auf 16 MiB begrenzt. Unlesbare eingebettete WAV-ID3-Daten bleiben unverändert; MP3-Export meldet einen Fehler und erhält das Ziel. Die Mischung vereinigt nicht alle Spurmetadaten. Lange Umwandlungen zeigen Fortschritt und sind abbrechbar; freien Speicher für Umwandlung und Bearbeitung vorsehen.


<a id="ss-topic-4-wiedergabe-zoom-und-audiogerate"></a>

## 4. Wiedergabe, Zoom und Audiogeräte

**Leertaste** startet/stoppt, **P** pausiert/setzt fort, **Esc** stoppt. Eine Auswahl wird als Bereich abgespielt, sonst beginnt es am Cursor. **Schleife** wiederholt mit möglichem kurzem Übergang. **Pos1/Ende** gehen zum Anfang/Ende, Sprungknöpfe um fünf Sekunden. Navigation oder Wellenformbearbeitung stoppt die Wiedergabe. **Vergrößern / Verkleinern**, **Strg+Mausrad**, Mausrad und Scrollbalken navigieren. **Gesamtansicht / Strg+0** zeigt alles, **Auswahl vergrößern / Strg+Umschalt+A** füllt die Ansicht mit der Auswahl. Die Symbole unterscheiden sich. Nah werden Samples verbunden, weiter außen bleiben Minima/Maxima je Bildschirmspalte sichtbar.

Unter **Optionen → Audiogeräte** Ausgang oder **Systemstandard** wählen. Die Auswahl bleibt für Wiedergabe und Vorschau gespeichert. Der Puffer beträgt standardmäßig 100 ms: größer verträgt Unterbrechungen, kleiner reagiert schneller. Geräte können abweichen. Änderungen stoppen Wiedergabe/Vorschau. Bei Geräteverlust neu verbinden oder Ausgang wählen und starten. Bei Stille Systemlautstärke, Route, Stumm und Solo prüfen. Ausgabe-Abtastratenwandlung verändert die Aufnahme nicht.

<a id="ss-topic-5-aufnehmen"></a>

## 5. Aufnehmen

Mikrofon/Interface anschließen, Eingang in **Audiogeräte** wählen und **R** drücken. Im Fenster Eingang, Ziel, Mono/Stereo, ersten Eingangskanal und Höchstdauer wählen. Neue Wellenform nimmt separat auf; Einfügen am Cursor/Auswahl ersetzen bearbeitet eine bestehende; Mehrspur fügt einen neuen Clip an der Cursorposition hinzu. Mono kann beide Stereokanäle speisen. Bestehende Wellenformen bestimmen Rate/Kanäle, andere Eingangsraten werden nach Stopp gewandelt. **Bis zum Stopp** läuft bis Stopp oder Speicherende.

**Aufnahme starten** öffnet erst jetzt das Mikrofon. Die Livewellenform zeigt die letzten 20 Sekunden, die Uhr die gesamte Aufnahmedauer, die Pegel den Eingang. **P** pausiert ohne Pausenzeit aufzunehmen. **Stopp**, **Esc**, **Leertaste** oder **R** behält die Aufnahme. Einfügen/Ersetzen oder ein neuer Mehrspurclip ist ein Rückgängig-Schritt; eine neue Wellenform muss noch gespeichert werden. **Aufnahme verwerfen** fragt vor Entfernen nur dieser Aufnahme. Schließen fragt nach Behalten, Verwerfen oder Fortsetzen. Andere Änderungen sind während Aufnahme gesperrt.

Der Eingang wird nicht über Lautsprecher wiedergegeben. Verstärkung am Interface/Mikrofon oder in Linux einstellen; bereits übersteuerter Eingang wird durch späteres Absenken nicht repariert. Geräteverlust stoppt und behält Audio, statt das Mikrofon zu wechseln. Aufnahmen werden blockweise geschrieben und etwa sekündlich gesichert. Wiederherstellung öffnet eine separate Wellenform. Wird die Umwandlung nach Stopp abgebrochen, bleibt die Aufnahme unter **Arbeit wiederherstellen** verfügbar; das alte Dokument bleibt unverändert.

**Am Anfang überspringen** entfernt die ersten Millisekunden einmal pro Aufnahme, um einen Einschaltknacks auszuschließen. Der Anfangswert beträgt 50 ms, einstellbar von 0 bis 500 ms und gespeichert. Bei 0 ms bleibt der gesamte Anfang erhalten; nach einem Schnitt folgt eine Einblendung von 5 ms. Entferntes Audio wird nicht aufgenommen. Uhr, Liveansicht, Pegel und Höchstdauer folgen dem behaltenen Audio. Pause/Fortsetzen wiederholt den Schnitt nicht. Bei Begleitwiedergabe berücksichtigt die Clipposition die entfernte Zeit und erhält die Ausrichtung.

<a id="ss-topic-6-auswahl-kanale-und-bearbeitung"></a>

## 6. Auswahl, Kanäle und Bearbeitung

Klicken setzt den Cursor, Ziehen einen Zeitbereich. In Stereo innerhalb L oder R für einen Kanal, über beide für Stereo ziehen. **Kanäle** oder **Bearbeiten → Kanäle auswählen** ändert Kanäle ohne Zeitverlust: **Alt+B / Alt+L / Alt+R** für beide/links/rechts. Umschalt-Klick erweitert mit gleicher Kanalwahl; Doppelklick wählt sichtbares Audio im angeklickten Kanal; **Strg+A** wählt die ganze Dauer dieser Kanäle. Mono hat einen Kanal. **Auswahl festlegen** gibt genaue Frames ein; 44.100 Frames sind bei 44.100 Hz eine Sekunde. **F4** verschiebt Grenzen nach innen zu Nulldurchgängen (links bei beiden).

**Ausschneiden / Strg+X** entfernt und kopiert, **Kopieren / Strg+C** kopiert, **Einfügen / Strg+V** ersetzt die Auswahl oder fügt am Cursor ein. **Einmischen / Strg+M** addiert Zwischenablageaudio dort und kann Spitzen erhöhen. **Entf** entfernt den Bereich; **Zuschneiden / Strg+T** behält nur ihn. **Strg+Z / Strg+Umschalt+Z** zurück/wiederholen. Einfügen wandelt die Rate, ohne die Zwischenablage zu ändern. Bei beiden Kanälen muss die Anzahl passen. Links/rechts kopieren oder Auswahlspeichern erzeugt Mono; normales Speichern erhält immer die ganze Stereowellenform.

Stereo behält eine gemeinsame Zeitachse. Mit **Links** oder **Rechts** verschieben Ausschneiden/Löschen, Einfügen, unterschiedlich langes Ersetzen, Zeitdehnung, erzeugte Töne/Stille und Nachklang nur den gewählten Kanal. Der andere behält seine Samples an den ursprünglichen Zeitpunkten. Der kürzere Kanal wird am Ende mit Stille aufgefüllt. **Beide** verschiebt beide Kanäle und gemeinsame Markierungen; **Effekte → Stille** leert Audio ohne Verschiebung.

Beispiel: Sekunden 2–3 links löschen. Späteres linkes Audio rückt eine Sekunde vor, am Ende folgt eine Sekunde Stille; rechts bleibt alles stehen. **Zuschneiden** setzt nur den gewählten Abschnitt des gewählten Kanals an den Anfang und füllt den Rest mit Stille. Die Auffüllung ist gewöhnliches Audio, bleibt beim Speichern/Öffnen erhalten und wird bei späteren Einfügungen mitverschoben. Unerwünschte Endstille mit Beide entfernen. Gemeinsame Cuepunkte und MP3-Kapitel behalten bei Einzelkanalbearbeitung ihre Zeitpunkte; ihre Bedeutung danach prüfen.

Eine Mono-Zwischenablage kann kürzere oder längere Bereiche ersetzen oder am Cursor eingefügt werden. Stereo liefert den entsprechenden linken/rechten Kanal. Die Abtastrate wird bei Bedarf gewandelt. Markierungen/Kapitel aus der Zwischenablage werden nur bei Beide zusammengeführt; beim Einzelkanal bleiben die gemeinsamen Zielmarkierungen. **Einmischen** addiert ab Auswahlbeginn/Cursor ohne späteres Audio zu verschieben und darf über das Ende hinausgehen; der andere Kanal erhält Endstille.

Für eine Einzelkanalaufnahme Links/Rechts wählen, **R** drücken und **Am Cursor einfügen** oder **Auswahl ersetzen** wählen. Die Aufnahme verwendet Mono und die Wellenformrate. **Erster Eingangskanal** wählt den Hardwareeingang unabhängig vom linken/rechten Ziel. Stopp übernimmt einen Bearbeitungsschritt, verschiebt nur diesen Kanal und füllt bei Bedarf auf. Neue Wellenform bleibt verfügbar. Die Kanalwahl ist während der Aufnahme gesperrt; bei fehlgeschlagener/abgebrochener Endverarbeitung bleibt die Aufnahme unter Arbeit wiederherstellen. Rückgängig/Wiederholen stellt Audio, Auffüllung, Metadaten und Kanalwahl wieder her; Wiederherstellung bewahrt das bearbeitete Stereoaudio.

<a id="ss-topic-einzelne-samples-bearbeiten"></a>

### Einzelne Samples bearbeiten

Mit **+** oder **Strg+Mausrad** einzoomen, bis quadratische Samplepunkte erscheinen (mindestens zwei logische Bildschirmpixel Abstand). Die horizontale Achse zeigt dann Sample-Indizes ab 0. Einen Punkt vertikal ziehen, um nur dieses Sample in diesem Kanal zu ändern. Die Sampleposition bleibt fest, auch wenn der Zeiger andere Punkte oder Kanäle überquert. Ziehen zeigt eine Vorschau; Loslassen bestätigt, **Escape** bricht ab. **Umschalt+Ziehen** wählt weiterhin Audio aus.

Doppel- oder Rechtsklick auf einen Punkt öffnet **Sample bearbeiten**. **Bearbeiten → Sample bearbeiten** ist bei jeder Zoomstufe verfügbar. Das Fenster beginnt am Cursor und im ersten gewählten Kanal; Index und Kanal sind einstellbar. Werte normalisiert oder als 8, 16 oder 24 Bit mit Vorzeichen anzeigen. Null ist Stille; −1/+1 sind der normale Vollpegel. −16384 in der 16-Bit-Anzeige entspricht beispielsweise −0,5 normalisiert. Ein anderer Anzeigebereich ändert weder Audio noch Dateiformat. **OK** übernimmt einen Wert; **Abbrechen** erhält das Original.

Jedes abgeschlossene Ziehen und jeder bestätigte Wert ist ein Schritt Rückgängig/Wiederherstellen. Alle anderen Samples, der andere Kanal, Dauer und Metadaten bleiben erhalten. Ziehen ist auf −1 … +1 begrenzt; bestehende Float-Pegel darüber bleiben numerisch verfügbar. Wiedergabe stoppt beim Bearbeitungsbeginn; während der Aufnahme ist Bearbeiten gesperrt. Mehrspurclips über eine Wellenformkopie bearbeiten und ausdrücklich auf den Clip anwenden. Nach jeder Korrektur hören; bei mehreren betroffenen Samples die Punkte einzeln dem umgebenden Verlauf annähern. Ein abrupter Sprung auf null kann selbst klicken. WAV float32 bewahrt die internen Werte exakt; MP3-Speichern komprimiert die gesamte Datei erneut verlustbehaftet.

<a id="ss-topic-wellenform-zeichnen"></a>

### Wellenform zeichnen

**Bearbeiten → Wellenform zeichnen** einschalten, **D** drücken oder die Stiftschaltfläche neben den Zoomknöpfen verwenden. Mit der linken Maustaste direkt auf der Wellenform zeichnen; einzelne Samplepunkte müssen nicht getroffen werden. Die gezeichnete Linie ersetzt Samplewerte innerhalb −1 bis +1; die ursprüngliche Wellenform wird nicht vertikal verschoben.

Der Zoom bestimmt die Gruppengröße: ungefähr zwei logische Bildschirmpixel Audio, auf ganze Samples aufgerundet. Stark vergrößert ändert sich ein Sample, weiter herausgezoomt ändern sich mehrere gemeinsam. Jede Gruppe umfasst höchstens eine Sekunde. Eine längere Bewegung darf mehrere Gruppen und insgesamt mehr als eine Sekunde ändern. Aufeinanderfolgende Zeigerpositionen werden geradlinig verbunden; erneutes Zeichnen über einer Gruppe ersetzt die vorherige Zeichnung.

Der Anfangskanal bleibt fest, auch beim Überqueren des anderen Kanals. Andere Samples, der andere Kanal, Dauer und Metadaten bleiben erhalten. Markierte Gruppen und die neue Linie zeigen eine Vorschau. Loslassen bestätigt die gesamte Bewegung als einen Rückgängig-Schritt. **Escape**, Fokusverlust, Zoomen oder Ausschalten des Zeichenmodus verwirft die Vorschau. **Umschalt+Ziehen** wählt weiterhin Audio aus; **D** erneut drücken für die normale Bedienung. Während einer Aufnahme ist Zeichnen gesperrt. Für präzise Reparaturen einzoomen: herausgezoomtes Zeichnen ersetzt auch feine Details in der betroffenen Gruppe. Danach anhören und bei Bedarf **Strg+Z** nutzen. Bei Mehrspur eine Wellenformkopie bearbeiten und auf den Clip anwenden.

<a id="ss-topic-7-effekte-anwenden"></a>

## 7. Effekte anwenden

Wellenformeffekte unter **Effekte** bearbeiten die Auswahl/Kanäle oder ohne Zeitauswahl deren ganze Dauer. Der andere Kanal bleibt unverändert und in Stereo hörbar. **Vorschau** spielt höchstens die ersten acht Sekunden ohne Übernahme; erneut klicken, Einstellungen ändern oder schließen stoppt. **OK** übernimmt einen Rückgängig-Schritt; **Abbrechen** erhält die Wellenform. **F2 / Letzten Befehl wiederholen** wiederholt Einstellungen auf aktueller Auswahl/Kanälen. Normalisieren, Zeit/Tonhöhe und hochwertige Verzerrung analysieren vor der Vorschau die ganze Auswahl.

<a id="ss-topic-amplitude"></a>

### Amplitude

<a id="ss-topic-verstarken-blenden"></a>

#### Verstärken / Blenden

**Verstärken / Blenden** nutzt Anfangs-/Endverstärkung: 100% unverändert, 50% halbe, 200% doppelte Amplitude. Links/rechts koppeln bindet Kanäle; gleiche Anfangs-/Endwerte ergeben feste Verstärkung, sonst eine Blende. Lineare Blenden erreichen null, logarithmische brauchen positive Endwerte. Presets bieten ±6 dB und Blenden. Direkte **Einblenden / Ausblenden** wenden sofort linear an. Beispiel: Einleitung auswählen, Einblenden wählen, vorhören und bestätigen.

<a id="ss-topic-kanalmischer"></a>

#### Kanalmischer

**Kanalmischer** benötigt Stereo. Jeder Ausgang mischt Prozente von L/R; negative Werte kehren Eingangspolarität um, Ausgangsumkehr die Summe. Presets tauschen, kopieren eine Seite auf beide, mitteln zu Mono (weiterhin zwei Kanäle) oder bilden die Differenz. Mischen kann 0 dBFS überschreiten. Einzelkanalwahl ändert nur diesen Ausgang, kann aber beide Originale nutzen.

<a id="ss-topic-dynamikbearbeitung"></a>

#### Dynamikbearbeitung

**Dynamikbearbeitung** ordnet Eingangs-dB Ausgangs-dB zu. Unter der Diagonale wird abgesenkt, darüber angehoben. Punkte klicken/ziehen, darunter genau eingeben; Rechtsklick, Punkt entfernen oder Entf löscht innere Punkte. Endpositionen bleiben fest. Attack steuert Spitzenreaktion, Release Erholung, Ausgangsverstärkung das Ergebnis. Stereokopplung hält gemeinsame Regelung. Für Sprache mit 3:1 über −18 dB beginnen. Kompressor reduziert laute, Gate/Expander leise Stellen, Begrenzer Spitzen. Kein Look-ahead: langsamer Attack lässt Transienten durch.

<a id="ss-topic-lautstarkeverlauf"></a>

#### Lautstärkeverlauf

**Lautstärkeverlauf** zeichnet Verstärkung über 0–100% des Abschnitts mit 0–200% Amplitude (100% neutral). Punkte ziehen oder Positionen/Werte eingeben, innere entfernen. Presets bieten Ein-/Ausblenden, beides und mittige Absenkung. Logarithmische Interpolation benötigt positive Werte. Für ein lautes Wort Punkte darum setzen und absenken. Dies schreibt Audio; Mehrspur-Cliplinien bleiben getrennt bearbeitbar.

<a id="ss-topic-normalisieren"></a>

#### Normalisieren

**Normalisieren** setzt den höchsten Peak mit einem Faktor auf das Ziel (Standard 98%). Wörter werden nicht gleich laut. Gemeinsames Normalisieren erhält Balance; entkoppelt hat jeder Kanal sein eigenes Ziel. Gleichspannungsentfernung zentriert zuerst, Stille bleibt still. Nach Mischen für PCM-Reserve nutzen.

<a id="ss-topic-invertieren-ruckwarts-und-stille"></a>

#### Invertieren, Rückwärts und Stille

**Invertieren** kehrt Polarität, **Rückwärts** Zeit um, **Stille** setzt den Bereich auf null ohne Zeit zu entfernen. Diese Befehle wirken sofort.

<a id="ss-topic-eq-und-filter"></a>

### EQ und Filter

<a id="ss-topic-grafischer-equalizer"></a>

#### Grafischer Equalizer

Unter **Filter** hat **Grafischer Equalizer** zehn Oktavbänder, 31,5 Hz–16 kHz, je −24…+24 dB. Bei niedriger Rate unbrauchbare Bänder sind aus. Linear setzt zurück, Bassanhebung stärkt Tiefen, Stimmpräsenz Sprache, sanfte Badewanne leicht Tiefen/Höhen. Die Kurve kombiniert überlappende Bänder und Ausgangsverstärkung (Anzeige −36…+36 dB). Anheben kann 0 dBFS überschreiten; Ausgang vor PCM-Export senken.

<a id="ss-topic-parametrischer-equalizer"></a>

#### Parametrischer Equalizer

**Parametrischer Equalizer** hat fünf Glockenbänder plus Tiefen-/Höhen-Shelf, einzeln schaltbar. Frequenz wählt Mitte/Übergang, Verstärkung −24…+24 dB, höheres Q verengt die Glocke. Shelves haben feste weiche Übergänge ohne Q. Resonanz mit schmaler negativer Glocke, allgemeinen Klang mit breiter Glocke/Shelf und wenig Gain bearbeiten. Linear/Zurücksetzen nullt Verstärkungen; Sprachklarheit/Wärme bieten Startpunkte.

<a id="ss-topic-filter"></a>

#### Filter

**Filter** bietet Hochpass (Rumpeln, Start 80 Hz), Tiefpass (Höhen mildern, Start 8 kHz), Bandpass und Kerbfilter. Hoch-/Tiefpass nutzen Butterworth 12/24/36/48 dB/Okt, etwa −3 dB am Übergang; steiler kann stärker nachschwingen. Bandpass/Kerbe nutzen Q. Telefon ist ein breiter Bandpass; 50/60-Hz-Kerben behandeln nur den Brummgrundton. Zurücksetzen lädt Rumpeln. Filterzustand bleibt zwischen Blöcken, startet aber am Auswahlbeginn leer; Länge bleibt, Phase ändert sich. Kurze harte Auswahl kann klicken; größeren Bereich wählen.

<a id="ss-topic-delay-echo-und-hall"></a>

### Delay, Echo und Hall

<a id="ss-topic-verzogerungseffekte-verzogerung"></a>

#### Verzögerungseffekte → Verzögerung

**Verzögerungseffekte → Verzögerung** fügt eine Kopie nach 1–2.000 ms hinzu. Links/Mono steuert die erste Zeit; entkoppeln für rechte Zeit. Presets: einfache Verzögerung 250 ms, Slapback 80 ms, Verdopplung 25 ms, Stereoverbreiterung.

<a id="ss-topic-echo"></a>

#### Echo

**Echo** wiederholt über Rückkopplung (0–95%); höher klingt länger. Höhendämpfung verdunkelt Rückkopplungen, nicht die erste Kopie. Pingpong wechselt Stereo. Warmes Echo/lange Wiederholungen sind Startpunkte; hohe Rückkopplung kann Pegel aufbauen.

<a id="ss-topic-hall"></a>

#### Hall

**Hall** nutzt Raumgröße für Reflexionsabstände, Abklingzeit für ungefähr RT60 (0,1–10 s), Vorverzögerung (0–250 ms) vor dem Effekt, Höhendämpfung und Stereobreite (0 gleicher Hall beidseitig, 100 volle Breite; bei Mono aus). Kleiner Raum, Studio, große Halle, lange Atmosphäre variieren Raum/Abklingen. Für Sprache wenig Effekt, kurze Zeit und etwas Vorverzögerung. Algorithmischer Hall, kein exaktes Saalmodell.

Original und Effekt sind unabhängige addierte Prozente; Ausgangsverstärkung (−24…+24 dB) skaliert ohne automatische Begrenzung. Standardlänge bleibt, spätere Wiederholungen enden abrupt. Nachklang fügt 0,01–60 s ein, verschiebt folgendes Wellenformaudio und spätere Cuepunkte. Letzte 10 ms blenden aus. Presets schalten Nachklang aus; danach einstellen. Extremes Echo kann mehr als 60 s brauchen; Rückkopplung/Zeit senken. Beispiel: 2 s Stimme + 3 s Nachklang ergibt 5 s. Einzelkanal-Nachklang verschiebt nur diesen Kanal; gemeinsame Cuepunkte bleiben stehen.

<a id="ss-topic-rauschminderung-und-klickreparatur"></a>

### Rauschminderung und Klickreparatur

Reines Hintergrundrauschen auswählen (etwa halbe bis mehrere Sekunden), **Rauschprofil erfassen** wählen, dann zu reinigendes Audio auswählen und **Rauschminderung** öffnen. Erfassen im Fenster geht ebenfalls; es ändert kein Audio. Das Profil mittelt höchstens erste 30 s. Mindestdauer hängt von der Rate ab; Rate/Kanäle müssen passen. Bei einem Stereokanal wird der passende Profilkanal genutzt. Profil speichern/laden nutzt `.ssnoise`, ein Spektrum ohne Tonaufnahme. Nur für passende Aufstellung wiederverwenden.

<a id="ss-topic-rauschschatzung-festes-rauschprofil"></a>

#### Rauschschätzung → Festes Rauschprofil

**Rauschschätzung → Festes Rauschprofil** eignet sich für gleichmäßiges Zischen oder Lüftung. **Adaptive Rauschverfolgung** beginnt mit demselben reinen Rauschprofil und folgt Änderungen von Pegel und Spektrum. Beide Modi benötigen ein passendes Profil; ein stilles Profil hat keine Wirkung. Die Bearbeitung verändert das gespeicherte Profil nicht.

**Anpassungszeit**, 0,05–5 Sekunden, ist nur adaptiv aktiv. Kürzer reagiert schneller, kann aber anhaltende Klänge als Rauschen lernen; länger folgt vorsichtiger. Bei 0,15 s beginnen. **Detailschutz**, 0–100%, erhält mehr leise Klänge und lässt mehr Hintergrund übrig; Anfangswert 50%. Fest mit 0% verwendet die bisherige Absenkung. Fehlende Quelldetails werden nicht wiederhergestellt. Maximale Reduktion bleibt 0–36 dB (mit 6–12 dB beginnen; 0 erhält das Original exakt), Empfindlichkeit bestimmt die Rauschmenge, Glättung verlangsamt stärkeres Absenken nach Klängen. Stereokopplung erhält die Balance; ohne sie werden Kanäle getrennt verarbeitet.

Presets: **Sanft** 6 dB/65% Detailschutz, **Ausgewogen** 12 dB/50%, **Stark** 24 dB/15%, **Wechselnder Hintergrund** adaptiv 12 dB/50% bei 0,15 s und **Feine Details** fest 6 dB/90%. Die ersten drei sind ebenfalls fest. Bei einer Stimme mit lauter werdendem Lüfter zunächst den Lüfter allein erfassen, dann Stimme und Wechselnder Hintergrund wählen. Detailschutz erhöhen, wenn leise Wörter oder Ausklänge verschwinden. Für anhaltende Klänge Anpassungszeit verlängern oder Fest verwenden. **Nur entferntes Rauschen behalten** macht den entfernten Teil hörbar; vor sauberer Anwendung ausschalten.

Adaptive Schätzung kann gewünschte Klänge mit Rauschen verwechseln, besonders anhaltende breite Klänge, sehr leise Signale oder ein Profil mit Sprache/Musik. Sie trennt keine Stimmen und ersetzt keine verlorenen Informationen. Vorschau und volle Bearbeitung haben denselben Anfang. Länge, Cuepositionen und der nicht gewählte Stereokanal bleiben fest. Rückgängig stellt das Original her; F2 wiederholt Modus, Zeit, Detailschutz und Profil. Große Dateien brauchen begrenzten Arbeitsspeicher; Abbruch übernimmt kein Teilergebnis.

<a id="ss-topic-klickentfernung"></a>

#### Klickentfernung

**Klickentfernung** verbindet intakte Samples um kurze einzelne Impulse. Höherer Schwellenfaktor ist vorsichtiger, niedrigerer Mindestsprung in dBFS findet leisere Klicks. Maximalbreite 0,02–2 ms. Vorsichtig, kleine/breitere Klicks sind Presets. Schlagzeug sorgfältig vorhören: Anschläge ähneln Schäden. Langes Knistern, Übersteuerung und beschädigte Randsamples brauchen andere Behandlung.

<a id="ss-topic-zeit-und-tonhohe"></a>

### Zeit und Tonhöhe

<a id="ss-topic-zeit-tonhohe-zeitdehnung"></a>

#### Zeit/Tonhöhe → Zeitdehnung

**Zeit/Tonhöhe → Zeitdehnung** ändert Dauer (25–400%) bei gleicher Tonhöhe: 200% verdoppelt, 50% halbiert. Tempofelder berechnen alte/neue BPM (120→100 ergibt 120%); keine Tempoerkennung. Bei Beide folgen Cuepunkte der Skala und spätere Audio-/Cuepositionen verschieben sich. Links/Rechts verschiebt nur diesen Kanal; gemeinsame Cuepunkte bleiben stehen.

<a id="ss-topic-tonhohenverschiebung"></a>

#### Tonhöhenverschiebung

**Tonhöhenverschiebung** ändert −24…+24 Halbtöne bei gleicher Dauer/Cuepunkten; ±12 ist eine Oktave, 0,01 Halbton ein Cent. Formanterhalt kann Stimmen bewahren; bei Instrumenten vergleichen.

Fein (Standard) und Schnell nutzen Rubber Band offline. Stereo wird gemeinsam verarbeitet; extreme Änderungen können künstlich klingen. Für echte Änderungen mindestens 50 ms und 64 Samples nutzen. Neutral liefert exakt das Original, Ausgabe rundet auf Samples. Vorschau analysiert die ganze Auswahl vor höchstens acht Sekunden Wiedergabe; lange Dateien benötigen Zeit und Analysearbeitsspeicher. Fortschritt ist abbrechbar. Bei Mehrspur eine Wellenformkopie bearbeiten und zurückübernehmen; Linien skalieren, spätere Clips verschieben sich nicht automatisch.

<a id="ss-topic-spezialeffekte"></a>

### Spezialeffekte

<a id="ss-topic-spezial-verzerrung"></a>

#### Spezial → Verzerrung

**Spezial → Verzerrung** bietet weiches Clipping (Sättigung), hartes Clipping (scharfe Grenze), Wavefold (Spitzen falten), Bitcrush (2–16 Bit). Vorverstärkung 0–36 dB, Grenze 10–100%, Effektmischung Original/bearbeitet, Ausgang −24…+24 dB. Die Grenze formt nur den Effekt, nicht Original/Gesamtausgang. Weiche Wärme, Crunch, Wavefold, Bitcrush sind Presets. Hohe Qualität nutzt Oversampling gegen Aliasing (meist 4×, bei hohen Raten angepasst) und verarbeitet auch zur Vorschau alles; Standard ist schneller/rauer. Dauer/Cuepunkte bleiben, Stille bleibt still.

<a id="ss-topic-faltung"></a>

#### Faltung

**Faltung** verwendet eine WAV-Impulsantwort von Filter, Box oder Raum. Antwort wählen, Original/Effekt einstellen und vorhören. Mono funktioniert je Kanal, Stereo braucht Stereoeingang und nutzt den passenden ausgewählten Kanal. Andere Raten werden gewandelt; Antwort nach Wandlung höchstens 10 Sekunden und 524.288 Samples, Datei höchstens 32 MiB. Leere/stille Antworten werden abgewiesen. Keine zusätzliche Nachklangblende. Energie-Normalisierung skaliert beide Antwortkanäle gemeinsam; bei kalibrierter Antwort ausschalten. Original 0%, Effekt 100% ergibt reinen Filter. Ganze Antwortausklang fügt Antwortlänge minus ein Sample hinzu und verschiebt späteres Audio/Cuepunkte. Sonst bleibt Länge. Antwort für F2 unverändert lassen, bei geändert/fehlend neu wählen.

<a id="ss-topic-8-erzeugen-analysieren-und-umwandeln"></a>

## 8. Erzeugen, analysieren und umwandeln

**Erzeugen → Töne** fügt einen Sinus am Cursor ein oder ersetzt die Auswahl mit gewählter Dauer, Frequenz in Hz, Amplitude %. 440 Hz leise ausprobieren. **Erzeugen → Stille** fügt/ersetzt Stille gewählter Dauer; **Effekte → Stille** erhält dagegen die bestehende Dauer.

**Analysieren → Frequenzanalyse / Alt+Z** zeigt Frequenz gegen dBFS für gewählte Kanäle/Bereich (sonst ganze Aufnahme). Bei langen Bereichen wird ein begrenzter mittlerer Teil mit Hann-Fenster und gemittelter Kanalleistung genutzt. Spitzenfrequenz/Pegel stehen darunter. Einen kurzen Klang gezielt auswählen; kein laufender Spektrumanalysator. Schließen ändert kein Audio.

**Bearbeiten → Abtastrate umwandeln** wandelt die ganze Wellenform in gewählte Hz, Tonhöhe/Dauer bleiben mit Frame-Rundung (mindestens eins). Cursor/Auswahl folgen gleichen Zeiten. Rückgängig stellt Audio und Rate wieder her. Dies ändert das Dokument; automatische Wiedergabewandlung nur den Ausgabestrom.

<a id="ss-topic-9-mehrspur-und-automation"></a>

## 9. Mehrspur und Automation

Sitzung mit Rate/Spuranzahl erstellen, WAV über Menü/Importknopf oder aus Dateiverwaltung hereinziehen. Raten werden gewandelt, mehrere Dateien auf folgende Spuren verteilt. **Fenster → Aktuelle Wellenform in Mehrspur einfügen** fügt die offene Wellenform ein. Spur hinzufügen/entfernen wirkt auf Auswahl; Rückgängig holt Gelöschtes zurück. Namen sind bearbeitbar. Stumm schaltet aus, Solo beschränkt auf Solospuren; Stumm gewinnt. Panorama −100 links, 0 Mitte, +100 rechts; Stereo dämpft eine Seite statt Kanäle zu kopieren.

In **Clips verschieben** Mitte ziehen zum Verschieben, Ränder zum Kürzen; Quelle bleibt zum Verlängern erhalten. Leere Zeitachse wählt Abspielbereich. **Clip duplizieren / Strg+D** teilt die Quelle; **Clip entfernen / Entf** entfernt den Clip, keine Quelldatei. Rechtsklick öffnet Befehle. **Clip-Eigenschaften** ändert Name, Zeit-/Quellgrenzen (Sekunden), Verstärkung, Panorama, Blenden, Stumm. Blenden müssen zusammen hineinpassen. Abbrechen erhält alles.

**Lautstärkekurve** und **Panoramakurve** zeichnen Punkte in Clips. Klicken fügt hinzu, Ziehen verschiebt, Rechts-/Doppelklick öffnet genaue Frames/Werte, Entfernen/Entf löscht Auswahl, Linie zurücksetzen neutralisiert. Esc bricht Ziehen ab. Lautstärke: unten 0%, Mitte 100%, oben 200%, multipliziert Clip-/Spurpegel und Blenden. Panorama: oben rechts, Mitte neutral, unten links, addiert sich zu Clip/Spur. Für volle Fahrt normales Panorama mittig. Punkte folgen Quelle beim Verschieben/Kürzen, werden gespeichert. Zum Verschieben zurück auf Clips verschieben.

Doppelklick oder **Kopie in Wellenform bearbeiten** öffnet eine Clipkopie für Offlineeffekte. **Fenster → Wellenform auf Clip anwenden** übernimmt ausdrücklich; bloßer Ansichtswechsel nicht. Sitzungs-Rückgängig stellt Audio/Linien her. Rate wird zurückgewandelt, Linien folgen neuer Länge, spätere Clips bewegen sich nicht: Überlappungen prüfen. **Sitzung abmischen / Abmischen** exportiert ganze Sitzung unabhängig von Auswahl, mit Stumm/Solo, Pegeln, Linien, Effekten und Nachklang. Sitzung speichern erhält das Projekt. Pegel/Pan/Stumm/Solo/Ketten sind beim Abspielen änderbar; Rückgängig/Ansichtswechsel stoppen.

<a id="ss-topic-10-echtzeit-spureffekte-plug-ins-und-aufnahme"></a>

## 10. Echtzeit-Spureffekte, Plug-ins und Aufnahme

**FX** an der Spur oder **Effekte → Spureffekte** öffnen. Effekt hinzufügen, Einstellungen/Preset wählen und mit OK bestätigen oder mit Anwenden bei offenem Fenster ändern. Bearbeiten/Doppelklick öffnet die Einstellungen erneut. Auf/Ab ändert die Reihenfolge, das Häkchen umgeht den Effekt, Entfernen löscht ihn. Änderungen haben Rückgängig/Wiederholen. Maximal sechzehn Effekte laufen nach Clippegel/Linien/Blenden und vor Spurpegel/Pan. Mono wird Stereo. Nachklang nach letztem Clip fügt 0–60 Sekunden hinzu. Wiedergabe und Mischung verwenden dieselbe Kette; die Quellen bleiben erhalten.

Verfügbar sind feste Verstärkung, Kanalmischer, Dynamik, grafischer/parametrischer EQ, Filter, Delay, Echo, Hall, Polaritätsumkehr und externe Plug-ins. Anwenden aktualisiert beim Hören; bereits gepuffertes Audio nutzt alte Werte. Neustart, Suchen und Bypasswechsel leeren das Effektgedächtnis. Normalisieren, Restaurierung, Zeit/Tonhöhe, Verzerrung und Faltung bleiben Wellenformbearbeitungen über Kopie in Wellenform bearbeiten. Für veränderlichen Clippegel die Lautstärkelinie verwenden.

<a id="ss-topic-vst3-lv2-und-ladspa"></a>

### VST3, LV2 und LADSPA

Einen **nativen 64-Bit-Linux-Audioeffekt** installieren. In Spureffekte **Externes Plug-in → Hinzufügen**, Format und **Plug-in hinzufügen** wählen. Ein `.vst3`-Bündel, `.lv2`-Bündel oder eine LADSPA-Bibliothek (`.so`) auswählen. Enthaltene Effekte erscheinen einzeln. Effekt wählen, Parameter suchen und normalisierte Position 0–100 % ändern: 50 % bedeutet nicht unbedingt halbe Lautstärke. Diskrete Parameter haben Schritte, schreibgeschützte bleiben fest. Anwenden spielt auf der Spur; OK bestätigt/schließt.

**Plug-in-Fenster öffnen** öffnet einen unterstützten eigenen VST3-/LV2-Editor. Seine Parameter und speicherbaren Zustände werden beim Bestätigen übernommen. Eigene Fenster benötigen **X11 oder XWayland**. Fehlt der Editor oder wird er nicht unterstützt, bleiben allgemeine Parameterregler verfügbar. LADSPA verwendet immer diese Regler. LV2-Editoren mit erforderlichem GTK-/Qt-Adapter werden nicht eingebettet.

VST3 unterstützt einen Stereo-Ein-/Ausgangsbus mit Float32. LV2/LADSPA unterstützen Mono-/Stereoeffekte mit gleich vielen Ein-/Ausgängen; Monoeffekte erhalten pro Stereokanal eine eigene Instanz. MIDI-Instrumente, zusätzliche Sidechains, VST2 und Windows-Plug-ins fehlen. Nicht unterstützte erforderliche LV2-Funktionen/Anschlusstypen werden gemeldet; MIDI/Atom-Verarbeitung fehlt. LV2-Zustände mit externen Dateien lassen sich nicht vollständig speichern und erzeugen eine Meldung. Dafür einen Effekt mit eigenständig speicherbarem Zustand wählen.

Jedes Plug-in läuft in einem getrennten Hilfsprozess. Absturz, Zeitüberschreitung oder ungültiges Audio stoppen die Wiedergabe; aufgezeichnete Samples bleiben erhalten. Projekte speichern Parameter und höchstens 1 MiB Zustand je Effekt. Plug-in, Bibliotheken und externe Samples separat installieren. Auf anderen Rechnern dieselbe Version hinzufügen. Fehlende/geänderte Plug-ins werden gemeldet; Wiedergabe/Export verlangen den passenden Effekt oder bewusstes Umgehen.

<a id="ss-topic-automatischer-plug-in-latenzausgleich"></a>

### Automatischer Plug-in-Latenzausgleich

Gemeldete algorithmische Verarbeitungsverzögerung wird je Spur bei Wiedergabe und Mischung ausgeglichen. Kettenverzögerungen werden addiert; Bypass-/Einstellungsänderungen aktualisieren die Verarbeitung. Zeitpositionen und Mischlänge bleiben gleich. Musikalisches Echo, Vorverzögerung und Hall bleiben hörbar. Der Ausgleich benötigt korrekte Plug-in-Meldungen und ist auf zehn Sekunden je Spur begrenzt. Ungültige oder ständig wechselnde Latenz wird gemeldet.

<a id="ss-topic-aufnahme-mit-begleitung-und-synchronisierung"></a>

### Aufnahme mit Begleitung und Synchronisierung

Begleitclips auf Spuren platzieren, Zielspur und Cursor wählen. **R** drücken, Eingang und neues Clipziel wählen und **Vorhandene Spuren während der Aufnahme wiedergeben** aktivieren. Die Spuren spielen mit Effekten; der Eingang wird nicht über Lautsprecher zurückgespielt. **P** pausiert/setzt beide fort; **Stopp/Esc/Leertaste/R** behält die Aufnahme als einen Rückgängig-Schritt. Verwerfen entfernt nur diese Aufnahme. Geräte-/Plug-in-Ausfall bewahrt aufgezeichnetes Audio.

**Automatische Synchronisierung** koppelt die Position an die Wiedergabeuhr und misst die Abweichung der Ein-/Ausgangstakte. Bei ausreichend langer, zuverlässiger Messung wird nach Stopp die Dauer leicht korrigiert. Kurze/instabile Messungen dehnen die Aufnahme nicht. Die Dauerkorrektur benötigt über zehn Sekunden brauchbare Taktmessungen. Der physische Signalweg wird damit nicht gemessen.

Dafür **Optionen → Aufnahme kalibrieren** oder die Kalibrierungsschaltfläche im Aufnahmefenster wählen. Dieselben Geräte, Abtastrate, Mono/Stereo, ersten Eingangskanal und Puffer wie bei der Aufnahme einstellen. Ausgang und Eingang mit geeignetem Loopback-Kabel verbinden. Ein Mikrofon vor einem Lautsprecher misst auch die akustische Laufzeit. Mit niedrigem Pegel beginnen. **Kalibrierung starten** spielt etwa sechs Sekunden leise Impulse ohne Eingangsmonitoring. Nur zuverlässige Ergebnisse werden gespeichert. Stille, Übersteuerung, mehrdeutige Signale oder instabile Zeiten lassen ein früheres gutes Profil unverändert. Mit kurzer Aufnahme prüfen; bei Geräte-/Einstellungswechsel erneut kalibrieren.

Die automatische Synchronisierung verwendet das passende Geräteprofil. Ohne Profil funktioniert der Taktausgleich, aber physische Verzögerung kann bleiben. Alternativ automatisch ausschalten und **Aufnahmeposition verschieben** verwenden: negativ früher, positiv später; −15 ms korrigiert 15 ms verspätetes Audio. Automatische und manuelle Korrektur schließen sich aus.

<a id="ss-topic-punch-in-out"></a>

### Punch-in/out

Zielspur und Zeitbereich am Mehrspurlineal oder über **Bearbeiten → Auswahl festlegen** wählen. **Optionen → Punch-in/out** oder **Shift+R** öffnen. Eingang, Synchronisierung, **Vorlauf** (2 s) und **Überblendung** (5 ms) einstellen. Die Auswahl bestimmt die Aufnahmegrenzen; Begleitung ist aktiv.

Der Eingang läuft vor der Wiedergabe warm. Im Vorlauf spielt das Original; innerhalb der Auswahl wird nur die Zielspur stummgeschaltet, während die neue Passage aufgenommen wird. Andere Spuren spielen weiter. Nach kurzer Synchronisierungsnachlaufzeit stoppt die Aufnahme automatisch. Nur korrigiertes Audio innerhalb der Auswahl wird als neuer Clip eingefügt.

Überblendungen mischen Alt/Neu innerhalb der Grenzen, höchstens 100 ms. Audio außerhalb bleibt erhalten. Alte Clips behalten ihre Quellen und werden im Punch-Bereich verdeckt. Strg+Z stellt alles in einem Schritt wieder her. Am alten Clip **Überdecktes Audio wiederherstellen** wählen, um alle seine Abdeckungen zu entfernen; neue Aufnahme löschen/stummschalten, damit nicht beide gleichzeitig spielen. Früher Stopp behält nur den tatsächlich aufgenommenen Abschnitt im Intervall. Stopp vor dem Intervall ändert die Sitzung nicht; die rohe Aufnahme bleibt unter **Datei → Arbeit wiederherstellen**. Wiederherstellung einer unbestätigten Aufnahme bietet die Rohaufnahme samt Vor-/Nachlauf zur manuellen Platzierung. Abgeschlossene Punch-Bereiche bleiben im Projekt und in der Absturzwiederherstellung erhalten.

**Sitzung speichern / Sitzung speichern unter** bewahrt Audio, Clips, Linien, Ketten, Plug-in-Zustände und Punch-Bereiche. Sitzung öffnen stellt sie wieder her; Mischung exportiert WAV/MP3 mit denselben Effekten. Das Projekt für getrennte Spuren behalten. Neu gespeicherte Projekte benötigen SoundSausage **0.19.0 oder neuer**; frühere Projektversionen bleiben lesbar. Fehlende Plug-ins verhindern das Öffnen/Wiederherstellen der Quellen nicht.

<a id="ss-topic-11-aufnahme-mit-begleitspuren"></a>

## 11. Aufnahme mit Begleitspuren

Begleitclips auf Spuren setzen, andere Zielspur und Cursorposition wählen. **R** drücken, Eingang/neuen Clip wählen, „Vorhandene Spuren während Aufnahme abspielen“ aktivieren. Begleitung samt Effekten startet am Cursor, Eingang geht nicht an Lautsprecher. **P** pausiert beide; **Stopp/Esc/Leertaste/R** stoppt und behält die Aufnahme als einen Rückgängig-Schritt. Nach Begleitende kann Aufnahme weiterlaufen; Höchstdauer stoppt beide. Verwerfen entfernt nur die neue Aufnahme. Geräte-/Plug-in-Ausfall bewahrt Samples. Dokumentänderungen sind gesperrt.

„Aufnahmepositionsversatz“ verschiebt den Clip: negativ früher, positiv später. Bei 15 ms Verspätung −15 ms probieren. Bekannten Klick über echte Ein-/Ausgangsroute aufnehmen, Positionen vergleichen, Differenz eingeben und zweite Aufnahme prüfen. Nach Geräte-/Pufferwechsel neu messen. Audio vor Zeit null wird beim Einfügen gekürzt. Versatz bleibt gespeichert. Automatische physische Kalibrierung, Taktdriftkorrektur, Plug-in-Latenzausgleich und Punch-in/out sind in Arbeit. Vor langer Sitzung kurz testen.

<a id="ss-topic-12-tastenkurzel-favoriten-und-probleme"></a>

## 12. Tastenkürzel, Favoriten und Probleme

**Favoriten** bietet Wiederholen, Normalisieren und Blenden; eigene Listen noch nicht. **Fenster** wechselt Ansichten und überträgt Wellenformen/Clips. Häufige Kürzel folgen. Bei Texteingabe gehören Tasten dem Feld; vor Transport-/Bearbeitungskürzeln in Wellenform/Zeitachse klicken.

| Tasten | Funktion |
| --- | --- |
| Strg+N / Strg+O | Neu / Öffnen in aktueller Ansicht |
| Strg+S / Strg+Umschalt+S | Speichern / Speichern unter |
| Strg+Alt+N / Strg+Alt+O / Strg+Alt+S | Sitzung neu / öffnen / speichern |
| Strg+W / Strg+Q | Dokument schließen / Beenden |
| Strg+Z / Strg+Umschalt+Z | Rückgängig / Wiederherstellen |
| Strg+X / Strg+C / Strg+V | Ausschneiden / Kopieren / Einfügen |
| Strg+M / Strg+T / Entf | Gemischt einfügen / Zuschneiden / Entfernen |
| Strg+A / F4 | Ganze Dauer / Nulldurchgänge |
| Alt+B / Alt+L / Alt+R | Beide / links / rechts |
| Leertaste / P / Esc / R | Start-Stopp / Pause / Stopp / Aufnahme |
| Pos1 / Ende / + / − | Anfang / Ende / vergrößern / verkleinern |
| Strg+0 / Strg+Umschalt+A | Gesamt- / Auswahlzoom |
| Strg+D / Tab / F11 | Clip duplizieren / Ansicht / Vollbild |
| F1 / F2 / Alt+Z | Handbuch / Effekt wiederholen / Frequenzanalyse 

Kein Eingang: Gerät/Kanal und Linux-Mikrofonpegel prüfen, neu verbinden und neue Aufnahme starten. Kein Ausgang: Route, Pegel, Stumm/Solo, Audiogeräte prüfen. Verzerrung/rote Peaks: Gesamtpegel senken, vor PCM normalisieren; gemischtes Einfügen/überlappende Clips addieren. Einfügen abgewiesen: Kanalanzahl der Zwischenablage prüfen. Effekt aus: Wellenform/Kopie öffnen; Kanalmischer braucht Stereo; zu bearbeitende Kanäle wählen. Punkte statt Clips: Clips verschieben wählen. Platte voll: Platz schaffen, keine aktiven Arbeitsdateien löschen. Defekte Wiederherstellung: Originale bleiben; Kopie nur bei Verzicht entfernen.

In Arbeit: eigene Favoriten und Markereditor. Echtzeitketten, Linux-VST3 und Aufnahme mit Begleitung sind wie beschrieben verfügbar. Vor Beenden Projekt speichern. Updates: [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
