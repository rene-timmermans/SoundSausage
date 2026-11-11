# SoundSausage — Handbuch

Version 0.17.1. Ein intuitiver, einfach zu bedienender Audioeditor mit allen Werkzeugen dort, wo man sie erwartet. Dieses Handbuch beschreibt die verfügbaren Arbeitsabläufe, Effekte und praktischen Grenzen.

## 1. Sprache und Hilfe

Unter **Optionen → Sprache** Nederlands, English, Deutsch, Français oder Español wählen. Menüs, Fenster, Hinweise und das geöffnete Handbuch wechseln sofort. Die Auswahl bleibt beim nächsten Start erhalten. Datei-, Spur- und Plug-in-Namen behalten ihre Schreibweise.

**Hilfe → Handbuch** oder **F1** öffnet dieses Handbuch ohne Internet neben dem Editor. **Strg+F** aktiviert die Suche; **F3** findet den nächsten, **Umschalt+F3** den vorherigen Treffer. Die Suchknöpfe setzen am anderen Ende fort. Nur angeklickte Weblinks benötigen Internet. **Über** zeigt Version, Autor, Lizenz, Website und Komponenten.

## 2. Schnellstart und Arbeitsbereich

Eine WAV- oder MP3-Datei mit **Datei → Öffnen** öffnen. **Leertaste** startet oder stoppt. Einen Abschnitt markieren, **Effekte → Amplitude → Normalisieren** wählen, mit **Vorschau** anhören und mit **OK** anwenden. **Strg+Z** macht die Änderung rückgängig. Mit **Speichern unter** ein separates Ergebnis speichern. Für mehrere Aufnahmen **Neue Mehrspursitzung** erstellen, WAVs oder MP3s importieren und mit **Abmischen** abschließen.

**Wellenform bearbeiten** bearbeitet eine Aufnahme; **Mehrspuransicht** kombiniert Clips. Mit **Tab**, oberen Knöpfen oder **Ansicht** wechseln; beide Dokumente bleiben verfügbar. Hinweise erklären die Knöpfe. **Werkzeugleistenbeschriftungen anzeigen** ergänzt Text, **Optionen → Statusleiste anzeigen** blendet die schmale Informationszeile ganz unten unter der Pegelanzeige ein oder aus. Sie zeigt Wiedergabestatus und Dateidaten; die Auswahl bleibt beim nächsten Start erhalten. **F11** schaltet Vollbild. Die Uhr folgt dem Audio; Auswahlfelder zeigen Anfang, Ende und Länge, Ansichtsfelder den sichtbaren Zeitraum. Rote Spitzen zeigen Übersteuerung, ein Stern ungespeicherte Änderungen.

Fenster und Diagrammskalen passen sich an die Schriftgröße des Desktops und die gewählte Sprache an. Ist ein Formular zu groß für den Bildschirm, durch die Einstellungen scrollen; die Schaltflächen zum Bestätigen und Abbrechen bleiben erreichbar.

Eine dünne horizontale Linie trennt links und rechts in der Stereowellenform und der Liveaufnahme.

## 3. Dateien, Projekte und Wiederherstellung

**Neu** erstellt eine leere Mono- oder Stereowellenform mit gewählter Abtastrate. **Öffnen** liest WAV und MP3. **Speichern** aktualisiert die Datei, **Speichern unter** wählt Name/Format, **Auswahl speichern** speichert nur ausgewählte Zeit und Kanäle. WAV unterstützt PCM 8/16/24/32 Bit und Float32. PCM16 eignet sich zum Austausch; Float32 erhält interne Spitzen über 0 dBFS. Höhere Bittiefe ersetzt keine verlorenen Details. Bei mehrdeutigen älteren 32-Bit-WAVs zwischen PCM und älterem Float wählen; Abbrechen lässt die Datei unverändert.

WAV-Texte, Cuepunkte und Beschriftungen bleiben erhalten. Cuepunkte folgen Bearbeitung, Einfügen und Auswahlexport; der Zieltitel bleibt erhalten. Recorderfelder werden wörtlich bewahrt und nach Effekten nicht neu berechnet. Zusätzliche Metadaten sind auf 16 MiB begrenzt. Größere Eingaben werden abgewiesen; ausgelassene Exportfelder benötigen Bestätigung. Die Mischung vereinigt keine Quellmarker. Große WAVs verwenden bei Bedarf RF64.

**Neue Mehrspursitzung**, **Sitzung öffnen**, **Sitzung speichern** und **Sitzung speichern unter** verwalten bearbeitbare Projekte. Ein SoundSausage-Projekt (`.celp`) enthält Audio, Clips, Linien, Spureinstellungen, Effektreihenfolge/Bypass/Nachklang und VST3-Einstellungen. Zusätzlich zur WAV das Projekt speichern, um einzelne Spuren zu behalten. Frühere SoundSausage-Projektversionen bleiben lesbar; Effektketten benötigen App 0.15.0 oder neuer. Alter `.ses`-Import ist begrenzt; zum Weiterarbeiten ein neues SoundSausage-Projekt verwenden.

**Schließen / Strg+W** schließt die aktuelle Wellenform; in Mehrspur heißt es **Sitzung schließen**. Bei Nachfrage speichern, verwerfen oder abbrechen. Andere Ansicht und Zwischenablage bleiben verfügbar. **Beenden / Strg+Q** beendet die Anwendung und fragt nach ungespeicherter Arbeit.

Lange Dateien werden blockweise auf Platte verarbeitet, ohne frühere 128-MiB-Grenze. Freien Platz für Quellkopien, Ergebnisse und Rückgängig-Verlauf vorhalten. Sitzungen sind auf 24 Stunden und 32 Spuren begrenzt. Lange Vorgänge zeigen Fortschritt und Abbrechen. Abbrechen erhält Audio, Auswahl, Verlauf und die bisherige Exportdatei. Ein angewandter Effekt ist ein Rückgängig-Schritt.

Nach unerwartetem Beenden den letzten Stand wiederherstellen, entfernen oder später öffnen. **Datei → Arbeit wiederherstellen** öffnet aufbewahrte Kopien. Originaldateien bleiben erhalten; Wellenform, Sitzung, Kanäle, Clips, Linien und Ketten kehren zurück, der Verlauf beginnt neu. Bestätigte Änderungen werden gesichert, Cursor/Auswahl etwa sekündlich. Aktive Instanzen werden übersprungen. Normales Speichern/bestätigtes Schließen räumt die eigene Kopie auf. Eigene Sicherungen behalten; bei Plattenfehlern kann der Stand älter sein.

### MP3 und WAV

MP3-Dateien über **Datei → Öffnen** laden, in Mehrspur importieren oder auf die Zeitleiste ziehen. Auswahl, Bearbeitung und Effekte arbeiten mit dem dekodierten Audio. **Speichern unter**, **Auswahl speichern** und **Abmischen** bieten WAV und MP3; die Dateiendung folgt dem Format. Speichern einer vorhandenen MP3 verwendet die gewählte MP3-Kodierung; Speichern unter kann eine WAV-Kopie erstellen.

MP3 bietet 128, 192, 256 und 320 kb/s. Höhere Bitraten benötigen mehr Speicher und erhalten meist mehr Details. MP3 ist verlustbehaftet: erneute Kompression kann weitere Details verlieren. WAV vermeidet einen weiteren MP3-Kompressionsschritt, stellt aber verlorene Informationen nicht wieder her. Float32-WAV eignet sich zum Weiterbearbeiten, PCM16 zum Austausch. MP3 verwendet die nächstliegende Abtastrate von 32.000, 44.100 oder 48.000 Hz bei gleicher Dauer; das Dokument behält seine Abtastrate. Auswahlen unter 2 ms als WAV speichern.

ID3-Texte und eingebettete Cover bleiben erhalten, auch über WAV und eingebettete Projekte. Die Dauerangabe wird aktualisiert; Kapitelpositionen, ReplayGain und andere abgeleitete Angaben werden nicht neu berechnet. Nicht unterstützte WAV-Marker/Dateidaten benötigen vor dem MP3-Export eine Bestätigung. Zusätzliche Metadaten bleiben auf 16 MiB begrenzt; die Mischung vereinigt nicht alle Spurmetadaten. Lange Umwandlungen zeigen Fortschritt und lassen sich abbrechen, ohne eine vorhandene Zieldatei zu ersetzen. Freien Speicher für Umwandlung und Bearbeitung vorsehen.

## 4. Wiedergabe, Zoom und Audiogeräte

**Leertaste** startet/stoppt, **P** pausiert/setzt fort, **Esc** stoppt. Eine Auswahl wird als Bereich abgespielt, sonst beginnt es am Cursor. **Schleife** wiederholt mit möglichem kurzem Übergang. **Pos1/Ende** gehen zum Anfang/Ende, Sprungknöpfe um fünf Sekunden. Navigation oder Wellenformbearbeitung stoppt die Wiedergabe. **Vergrößern / Verkleinern**, **Strg+Mausrad**, Mausrad und Scrollbalken navigieren. **Gesamtansicht / Strg+0** zeigt alles, **Auswahl vergrößern / Strg+Umschalt+A** füllt die Ansicht mit der Auswahl. Die Symbole unterscheiden sich. Nah werden Samples verbunden, weiter außen bleiben Minima/Maxima je Bildschirmspalte sichtbar.

Unter **Optionen → Audiogeräte** Ausgang oder **Systemstandard** wählen. Die Auswahl bleibt für Wiedergabe und Vorschau gespeichert. Der Puffer beträgt standardmäßig 100 ms: größer verträgt Unterbrechungen, kleiner reagiert schneller. Geräte können abweichen. Änderungen stoppen Wiedergabe/Vorschau. Bei Geräteverlust neu verbinden oder Ausgang wählen und starten. Bei Stille Systemlautstärke, Route, Stumm und Solo prüfen. Ausgabe-Abtastratenwandlung verändert die Aufnahme nicht.

## 5. Aufnehmen

Mikrofon/Interface anschließen, Eingang in **Audiogeräte** wählen und **R** drücken. Im Fenster Eingang, Ziel, Mono/Stereo, ersten Eingangskanal und Höchstdauer wählen. Neue Wellenform nimmt separat auf; Einfügen am Cursor/Auswahl ersetzen bearbeitet eine bestehende; Mehrspur fügt einen neuen Clip an der Cursorposition hinzu. Mono kann beide Stereokanäle speisen. Bestehende Wellenformen bestimmen Rate/Kanäle, andere Eingangsraten werden nach Stopp gewandelt. **Bis zum Stopp** läuft bis Stopp oder Speicherende.

**Aufnahme starten** öffnet erst jetzt das Mikrofon. Die Livewellenform zeigt die letzten 20 Sekunden, die Uhr die gesamte Aufnahmedauer, die Pegel den Eingang. **P** pausiert ohne Pausenzeit aufzunehmen. **Stopp**, **Esc**, **Leertaste** oder **R** behält die Aufnahme. Einfügen/Ersetzen oder ein neuer Mehrspurclip ist ein Rückgängig-Schritt; eine neue Wellenform muss noch gespeichert werden. **Aufnahme verwerfen** fragt vor Entfernen nur dieser Aufnahme. Schließen fragt nach Behalten, Verwerfen oder Fortsetzen. Andere Änderungen sind während Aufnahme gesperrt.

Der Eingang wird nicht über Lautsprecher wiedergegeben. Verstärkung am Interface/Mikrofon oder in Linux einstellen; bereits übersteuerter Eingang wird durch späteres Absenken nicht repariert. Geräteverlust stoppt und behält Audio, statt das Mikrofon zu wechseln. Aufnahmen werden blockweise geschrieben und etwa sekündlich gesichert. Wiederherstellung öffnet eine separate Wellenform. Wird die Umwandlung nach Stopp abgebrochen, bleibt die Aufnahme unter **Arbeit wiederherstellen** verfügbar; das alte Dokument bleibt unverändert.

**Am Anfang überspringen** entfernt die ersten Millisekunden einmal pro Aufnahme, um einen Einschaltknacks auszuschließen. Der Anfangswert beträgt 50 ms, einstellbar von 0 bis 500 ms und gespeichert. Bei 0 ms bleibt der gesamte Anfang erhalten; nach einem Schnitt folgt eine Einblendung von 5 ms. Entferntes Audio wird nicht aufgenommen. Uhr, Liveansicht, Pegel und Höchstdauer folgen dem behaltenen Audio. Pause/Fortsetzen wiederholt den Schnitt nicht. Bei Begleitwiedergabe berücksichtigt die Clipposition die entfernte Zeit und erhält die Ausrichtung.

## 6. Auswahl, Kanäle und Bearbeitung

Klicken setzt den Cursor, Ziehen einen Zeitbereich. In Stereo innerhalb L oder R für einen Kanal, über beide für Stereo ziehen. **Kanäle** oder **Bearbeiten → Kanäle auswählen** ändert Kanäle ohne Zeitverlust: **Alt+B / Alt+L / Alt+R** für beide/links/rechts. Umschalt-Klick erweitert mit gleicher Kanalwahl; Doppelklick wählt sichtbares Audio im angeklickten Kanal; **Strg+A** wählt die ganze Dauer dieser Kanäle. Mono hat einen Kanal. **Auswahl festlegen** gibt genaue Frames ein; 44.100 Frames sind bei 44.100 Hz eine Sekunde. **F4** verschiebt Grenzen nach innen zu Nulldurchgängen (links bei beiden).

**Ausschneiden / Strg+X** entfernt und kopiert, **Kopieren / Strg+C** kopiert, **Einfügen / Strg+V** ersetzt die Auswahl oder fügt am Cursor ein. **Einmischen / Strg+M** addiert Zwischenablageaudio dort und kann Spitzen erhöhen. **Entf** entfernt den Bereich; **Zuschneiden / Strg+T** behält nur ihn. **Strg+Z / Strg+Umschalt+Z** zurück/wiederholen. Einfügen wandelt die Rate, ohne die Zwischenablage zu ändern. Bei beiden Kanälen muss die Anzahl passen. Links/rechts kopieren oder Auswahlspeichern erzeugt Mono; normales Speichern erhält immer die ganze Stereowellenform.

Stereo hat eine gemeinsame Zeitachse. Längenänderungen (Schneiden/Löschen/Zuschneiden, Dehnen, Einfügen, Nachklang) benötigen beide Kanäle. Mono in einen Stereokanal einfügen muss den Bereich exakt ersetzen; gemischtes Einfügen muss in der bestehenden Dauer bleiben. **Stille** leert einen Kanal ohne den anderen zu verschieben. Tonhöhenverschiebung, Delay, Echo, Hall und Faltung können einen Kanal bei gleicher Dauer bearbeiten. Aufnahme in bestehendes Stereo benötigt beide Kanäle. Rückgängig/Wiederherstellung behalten die Kanalwahl.

## 7. Effekte anwenden

Wellenformeffekte unter **Effekte** bearbeiten die Auswahl/Kanäle oder ohne Zeitauswahl deren ganze Dauer. Der andere Kanal bleibt unverändert und in Stereo hörbar. **Vorschau** spielt höchstens die ersten acht Sekunden ohne Übernahme; erneut klicken, Einstellungen ändern oder schließen stoppt. **OK** übernimmt einen Rückgängig-Schritt; **Abbrechen** erhält die Wellenform. **F2 / Letzten Befehl wiederholen** wiederholt Einstellungen auf aktueller Auswahl/Kanälen. Normalisieren, Zeit/Tonhöhe und hochwertige Verzerrung analysieren vor der Vorschau die ganze Auswahl.

### Amplitude

**Verstärken / Blenden** nutzt Anfangs-/Endverstärkung: 100% unverändert, 50% halbe, 200% doppelte Amplitude. Links/rechts koppeln bindet Kanäle; gleiche Anfangs-/Endwerte ergeben feste Verstärkung, sonst eine Blende. Lineare Blenden erreichen null, logarithmische brauchen positive Endwerte. Presets bieten ±6 dB und Blenden. Direkte **Einblenden / Ausblenden** wenden sofort linear an. Beispiel: Einleitung auswählen, Einblenden wählen, vorhören und bestätigen.

**Kanalmischer** benötigt Stereo. Jeder Ausgang mischt Prozente von L/R; negative Werte kehren Eingangspolarität um, Ausgangsumkehr die Summe. Presets tauschen, kopieren eine Seite auf beide, mitteln zu Mono (weiterhin zwei Kanäle) oder bilden die Differenz. Mischen kann 0 dBFS überschreiten. Einzelkanalwahl ändert nur diesen Ausgang, kann aber beide Originale nutzen.

**Dynamikbearbeitung** ordnet Eingangs-dB Ausgangs-dB zu. Unter der Diagonale wird abgesenkt, darüber angehoben. Punkte klicken/ziehen, darunter genau eingeben; Rechtsklick, Punkt entfernen oder Entf löscht innere Punkte. Endpositionen bleiben fest. Attack steuert Spitzenreaktion, Release Erholung, Ausgangsverstärkung das Ergebnis. Stereokopplung hält gemeinsame Regelung. Für Sprache mit 3:1 über −18 dB beginnen. Kompressor reduziert laute, Gate/Expander leise Stellen, Begrenzer Spitzen. Kein Look-ahead: langsamer Attack lässt Transienten durch.

**Lautstärkeverlauf** zeichnet Verstärkung über 0–100% des Abschnitts mit 0–200% Amplitude (100% neutral). Punkte ziehen oder Positionen/Werte eingeben, innere entfernen. Presets bieten Ein-/Ausblenden, beides und mittige Absenkung. Logarithmische Interpolation benötigt positive Werte. Für ein lautes Wort Punkte darum setzen und absenken. Dies schreibt Audio; Mehrspur-Cliplinien bleiben getrennt bearbeitbar.

**Normalisieren** setzt den höchsten Peak mit einem Faktor auf das Ziel (Standard 98%). Wörter werden nicht gleich laut. Gemeinsames Normalisieren erhält Balance; entkoppelt hat jeder Kanal sein eigenes Ziel. Gleichspannungsentfernung zentriert zuerst, Stille bleibt still. Nach Mischen für PCM-Reserve nutzen. **Invertieren** kehrt Polarität, **Rückwärts** Zeit um, **Stille** setzt den Bereich auf null ohne Zeit zu entfernen. Diese Befehle wirken sofort.

### EQ und Filter

Unter **Filter** hat **Grafischer Equalizer** zehn Oktavbänder, 31,5 Hz–16 kHz, je −24…+24 dB. Bei niedriger Rate unbrauchbare Bänder sind aus. Linear setzt zurück, Bassanhebung stärkt Tiefen, Stimmpräsenz Sprache, sanfte Badewanne leicht Tiefen/Höhen. Die Kurve kombiniert überlappende Bänder und Ausgangsverstärkung (Anzeige −36…+36 dB). Anheben kann 0 dBFS überschreiten; Ausgang vor PCM-Export senken.

**Parametrischer Equalizer** hat fünf Glockenbänder plus Tiefen-/Höhen-Shelf, einzeln schaltbar. Frequenz wählt Mitte/Übergang, Verstärkung −24…+24 dB, höheres Q verengt die Glocke. Shelves haben feste weiche Übergänge ohne Q. Resonanz mit schmaler negativer Glocke, allgemeinen Klang mit breiter Glocke/Shelf und wenig Gain bearbeiten. Linear/Zurücksetzen nullt Verstärkungen; Sprachklarheit/Wärme bieten Startpunkte.

**Filter** bietet Hochpass (Rumpeln, Start 80 Hz), Tiefpass (Höhen mildern, Start 8 kHz), Bandpass und Kerbfilter. Hoch-/Tiefpass nutzen Butterworth 12/24/36/48 dB/Okt, etwa −3 dB am Übergang; steiler kann stärker nachschwingen. Bandpass/Kerbe nutzen Q. Telefon ist ein breiter Bandpass; 50/60-Hz-Kerben behandeln nur den Brummgrundton. Zurücksetzen lädt Rumpeln. Filterzustand bleibt zwischen Blöcken, startet aber am Auswahlbeginn leer; Länge bleibt, Phase ändert sich. Kurze harte Auswahl kann klicken; größeren Bereich wählen.

### Delay, Echo und Hall

**Verzögerungseffekte → Verzögerung** fügt eine Kopie nach 1–2.000 ms hinzu. Links/Mono steuert die erste Zeit; entkoppeln für rechte Zeit. Presets: einfache Verzögerung 250 ms, Slapback 80 ms, Verdopplung 25 ms, Stereoverbreiterung. **Echo** wiederholt über Rückkopplung (0–95%); höher klingt länger. Höhendämpfung verdunkelt Rückkopplungen, nicht die erste Kopie. Pingpong wechselt Stereo. Warmes Echo/lange Wiederholungen sind Startpunkte; hohe Rückkopplung kann Pegel aufbauen.

**Hall** nutzt Raumgröße für Reflexionsabstände, Abklingzeit für ungefähr RT60 (0,1–10 s), Vorverzögerung (0–250 ms) vor dem Effekt, Höhendämpfung und Stereobreite (0 gleicher Hall beidseitig, 100 volle Breite; bei Mono aus). Kleiner Raum, Studio, große Halle, lange Atmosphäre variieren Raum/Abklingen. Für Sprache wenig Effekt, kurze Zeit und etwas Vorverzögerung. Algorithmischer Hall, kein exaktes Saalmodell.

Original und Effekt sind unabhängige addierte Prozente; Ausgangsverstärkung (−24…+24 dB) skaliert ohne automatische Begrenzung. Standardlänge bleibt, spätere Wiederholungen enden abrupt. Nachklang fügt 0,01–60 s ein, verschiebt folgendes Wellenformaudio und spätere Cuepunkte. Letzte 10 ms blenden aus. Presets schalten Nachklang aus; danach einstellen. Extremes Echo kann mehr als 60 s brauchen; Rückkopplung/Zeit senken. Beispiel: 2 s Stimme + 3 s Nachklang ergibt 5 s. Ein einzelner Stereokanal kann keine Zeit hinzufügen.

### Rauschminderung und Klickreparatur

Reines Hintergrundrauschen auswählen (etwa halbe bis mehrere Sekunden), **Rauschprofil erfassen** wählen, dann zu reinigendes Audio auswählen und **Rauschminderung** öffnen. Erfassen im Fenster geht ebenfalls; es ändert kein Audio. Das Profil mittelt höchstens erste 30 s. Mindestdauer hängt von der Rate ab; Rate/Kanäle müssen passen. Bei einem Stereokanal wird der passende Profilkanal genutzt. Profil speichern/laden nutzt `.ssnoise`, ein Spektrum ohne Tonaufnahme. Nur für passende Aufstellung wiederverwenden.

Maximale Reduktion ist 0–36 dB, mit 6–12 dB beginnen. Empfindlichkeit behandelt mehr Hintergrund; Glättung beruhigt Regelung, kann nach Tönen Rauschen durchlassen. Stereokopplung erhält Balance. „Nur entferntes Rauschen behalten“ prüft entfernten Inhalt; vor sauberem Ergebnis ausschalten. Sanft/Ausgewogen sind Startpunkte. Für konstantes Zischen/Lüftung; trennt keine Stimmen, ersetzt keine Details. Übermaß oder musikalisches Profil kann schaden. Dauer/Cuepunkte bleiben; Offlineverarbeitung.

**Klickentfernung** verbindet intakte Samples um kurze einzelne Impulse. Höherer Schwellenfaktor ist vorsichtiger, niedrigerer Mindestsprung in dBFS findet leisere Klicks. Maximalbreite 0,02–2 ms. Vorsichtig, kleine/breitere Klicks sind Presets. Schlagzeug sorgfältig vorhören: Anschläge ähneln Schäden. Langes Knistern, Übersteuerung und beschädigte Randsamples brauchen andere Behandlung.

### Zeit und Tonhöhe

**Zeit/Tonhöhe → Zeitdehnung** ändert Dauer (25–400%) bei gleicher Tonhöhe: 200% verdoppelt, 50% halbiert. Tempofelder berechnen alte/neue BPM (120→100 ergibt 120%); keine Tempoerkennung. Innere Cuepunkte folgen der Skala, späteres Audio/Cuepunkte verschieben sich. Stereo braucht beide Kanäle. **Tonhöhenverschiebung** ändert −24…+24 Halbtöne bei gleicher Dauer/Cuepunkten; ±12 ist eine Oktave, 0,01 Halbton ein Cent. Formanterhalt kann Stimmen bewahren; bei Instrumenten vergleichen.

Fein (Standard) und Schnell nutzen Rubber Band offline. Stereo wird gemeinsam verarbeitet; extreme Änderungen können künstlich klingen. Für echte Änderungen mindestens 50 ms und 64 Samples nutzen. Neutral liefert exakt das Original, Ausgabe rundet auf Samples. Vorschau analysiert die ganze Auswahl vor höchstens acht Sekunden Wiedergabe; lange Dateien benötigen Zeit und Analysearbeitsspeicher. Fortschritt ist abbrechbar. Bei Mehrspur eine Wellenformkopie bearbeiten und zurückübernehmen; Linien skalieren, spätere Clips verschieben sich nicht automatisch.

### Spezialeffekte

**Spezial → Verzerrung** bietet weiches Clipping (Sättigung), hartes Clipping (scharfe Grenze), Wavefold (Spitzen falten), Bitcrush (2–16 Bit). Vorverstärkung 0–36 dB, Grenze 10–100%, Effektmischung Original/bearbeitet, Ausgang −24…+24 dB. Die Grenze formt nur den Effekt, nicht Original/Gesamtausgang. Weiche Wärme, Crunch, Wavefold, Bitcrush sind Presets. Hohe Qualität nutzt Oversampling gegen Aliasing (meist 4×, bei hohen Raten angepasst) und verarbeitet auch zur Vorschau alles; Standard ist schneller/rauer. Dauer/Cuepunkte bleiben, Stille bleibt still.

**Faltung** verwendet eine WAV-Impulsantwort von Filter, Box oder Raum. Antwort wählen, Original/Effekt einstellen und vorhören. Mono funktioniert je Kanal, Stereo braucht Stereoeingang und nutzt den passenden ausgewählten Kanal. Andere Raten werden gewandelt; Antwort nach Wandlung höchstens 10 Sekunden und 524.288 Samples, Datei höchstens 32 MiB. Leere/stille Antworten werden abgewiesen. Keine zusätzliche Nachklangblende. Energie-Normalisierung skaliert beide Antwortkanäle gemeinsam; bei kalibrierter Antwort ausschalten. Original 0%, Effekt 100% ergibt reinen Filter. Ganze Antwortausklang fügt Antwortlänge minus ein Sample hinzu und verschiebt späteres Audio/Cuepunkte. Sonst bleibt Länge. Antwort für F2 unverändert lassen, bei geändert/fehlend neu wählen.

## 8. Erzeugen, analysieren und umwandeln

**Erzeugen → Töne** fügt einen Sinus am Cursor ein oder ersetzt die Auswahl mit gewählter Dauer, Frequenz in Hz, Amplitude %. 440 Hz leise ausprobieren. **Erzeugen → Stille** fügt/ersetzt Stille gewählter Dauer; **Effekte → Stille** erhält dagegen die bestehende Dauer.

**Analysieren → Frequenzanalyse / Alt+Z** zeigt Frequenz gegen dBFS für gewählte Kanäle/Bereich (sonst ganze Aufnahme). Bei langen Bereichen wird ein begrenzter mittlerer Teil mit Hann-Fenster und gemittelter Kanalleistung genutzt. Spitzenfrequenz/Pegel stehen darunter. Einen kurzen Klang gezielt auswählen; kein laufender Spektrumanalysator. Schließen ändert kein Audio.

**Bearbeiten → Abtastrate umwandeln** wandelt die ganze Wellenform in gewählte Hz, Tonhöhe/Dauer bleiben mit Frame-Rundung (mindestens eins). Cursor/Auswahl folgen gleichen Zeiten. Rückgängig stellt Audio und Rate wieder her. Dies ändert das Dokument; automatische Wiedergabewandlung nur den Ausgabestrom.

## 9. Mehrspur und Automation

Sitzung mit Rate/Spuranzahl erstellen, WAV über Menü/Importknopf oder aus Dateiverwaltung hereinziehen. Raten werden gewandelt, mehrere Dateien auf folgende Spuren verteilt. **Fenster → Aktuelle Wellenform in Mehrspur einfügen** fügt die offene Wellenform ein. Spur hinzufügen/entfernen wirkt auf Auswahl; Rückgängig holt Gelöschtes zurück. Namen sind bearbeitbar. Stumm schaltet aus, Solo beschränkt auf Solospuren; Stumm gewinnt. Panorama −100 links, 0 Mitte, +100 rechts; Stereo dämpft eine Seite statt Kanäle zu kopieren.

In **Clips verschieben** Mitte ziehen zum Verschieben, Ränder zum Kürzen; Quelle bleibt zum Verlängern erhalten. Leere Zeitachse wählt Abspielbereich. **Clip duplizieren / Strg+D** teilt die Quelle; **Clip entfernen / Entf** entfernt den Clip, keine Quelldatei. Rechtsklick öffnet Befehle. **Clip-Eigenschaften** ändert Name, Zeit-/Quellgrenzen (Sekunden), Verstärkung, Panorama, Blenden, Stumm. Blenden müssen zusammen hineinpassen. Abbrechen erhält alles.

**Lautstärkekurve** und **Panoramakurve** zeichnen Punkte in Clips. Klicken fügt hinzu, Ziehen verschiebt, Rechts-/Doppelklick öffnet genaue Frames/Werte, Entfernen/Entf löscht Auswahl, Linie zurücksetzen neutralisiert. Esc bricht Ziehen ab. Lautstärke: unten 0%, Mitte 100%, oben 200%, multipliziert Clip-/Spurpegel und Blenden. Panorama: oben rechts, Mitte neutral, unten links, addiert sich zu Clip/Spur. Für volle Fahrt normales Panorama mittig. Punkte folgen Quelle beim Verschieben/Kürzen, werden gespeichert. Zum Verschieben zurück auf Clips verschieben.

Doppelklick oder **Kopie in Wellenform bearbeiten** öffnet eine Clipkopie für Offlineeffekte. **Fenster → Wellenform auf Clip anwenden** übernimmt ausdrücklich; bloßer Ansichtswechsel nicht. Sitzungs-Rückgängig stellt Audio/Linien her. Rate wird zurückgewandelt, Linien folgen neuer Länge, spätere Clips bewegen sich nicht: Überlappungen prüfen. **Sitzung abmischen / Abmischen** exportiert ganze Sitzung unabhängig von Auswahl, mit Stumm/Solo, Pegeln, Linien, Effekten und Nachklang. Sitzung speichern erhält das Projekt. Pegel/Pan/Stumm/Solo/Ketten sind beim Abspielen änderbar; Rückgängig/Ansichtswechsel stoppen.

## 10. Echtzeit-Spureffekte und VST3

**FX** an der Spur oder **Effekte → Spureffekte** öffnen. Effekt hinzufügen, Einstellungen/Preset wählen, OK fügt hinzu, Anwenden ändert bei offenem Fenster. Auf/Ab ändert Reihenfolge, Häkchen umgeht, Bearbeiten/Doppelklick bearbeitet, Entfernen löscht. Maximal 16 Effekte laufen oben nach unten nach Clippegel/Linien/Blenden, vor Spurpegel/Pan. Mono wird Stereo. Nachklang nach letztem Clip fügt 0–60 s hinzu. Ketten gelten für Wiedergabe, Mischung, Projekt und Wiederherstellung. Neustart/Suchen/Bypass leert Effektgedächtnis; interne Änderungen können Ausklang neu starten, VST3-Parameter behalten die Instanz.

Echtzeitketten unterstützen feste Verstärkung, Kanalmischer, Dynamik, grafischen/parametrischen EQ, Filter, Delay, Echo, Hall, Polaritätsumkehr und VST3. Für Verstärkungsverlauf die Lautstärkelinie verwenden. Normalisieren, Rausch-/Klickreparatur, Zeit/Tonhöhe, Verzerrung und Faltung bleiben offline. Anwenden aktualisiert beim Hören; bereits gepufferter Ton nutzt alte Werte. Quellen bleiben erhalten.

Einen **nativen 64-Bit Linux-VST3-Audioeffekt** installieren, VST3-Plug-in, dann **VST3-Bundle hinzufügen** wählen und `.vst3`-Ordner auswählen. Mehrere Effekte erscheinen einzeln. Parameternamen suchen, normalisierte 0–100%-Position ändern (50% ist nicht zwingend halbe Lautstärke). Diskrete haben Schritte, schreibgeschützte bleiben fest. Anwenden spielt auf der Spur, OK bestätigt/schließt. Eigener Plug-in-Editor wird nicht eingebettet. Unterstützt: ein Stereo-Ein-/Ausgangsbus, Float32. Keine VST2, Windows-VST, MIDI-Instrumente, Sidechains oder andere Formate. Fehlende Funktionen werden ohne Projektänderung gemeldet.

Plug-in-Verzögerung wird angezeigt, aber nicht zwischen Spuren ausgeglichen. Ein Hilfsprozess je Plug-in: Absturz, Zeitüberschreitung oder ungültiges Audio stoppt Wiedergabe und bewahrt Aufnahme. Projekte speichern Parameter und höchstens 1 MiB Zustand je Effekt, keinen Code oder externe Bibliotheken/Samples. Auf anderem Rechner passende Bundles installieren/hinzufügen. Fehlende/geänderte Versionen behalten Einstellungen; Wiedergabe/Export verlangt passenden Effekt oder bewusstes Umgehen. Kein stilles Weglassen.

## 11. Aufnahme mit Begleitspuren

Begleitclips auf Spuren setzen, andere Zielspur und Cursorposition wählen. **R** drücken, Eingang/neuen Clip wählen, „Vorhandene Spuren während Aufnahme abspielen“ aktivieren. Begleitung samt Effekten startet am Cursor, Eingang geht nicht an Lautsprecher. **P** pausiert beide; **Stopp/Esc/Leertaste/R** stoppt und behält die Aufnahme als einen Rückgängig-Schritt. Nach Begleitende kann Aufnahme weiterlaufen; Höchstdauer stoppt beide. Verwerfen entfernt nur die neue Aufnahme. Geräte-/Plug-in-Ausfall bewahrt Samples. Dokumentänderungen sind gesperrt.

„Aufnahmepositionsversatz“ verschiebt den Clip: negativ früher, positiv später. Bei 15 ms Verspätung −15 ms probieren. Bekannten Klick über echte Ein-/Ausgangsroute aufnehmen, Positionen vergleichen, Differenz eingeben und zweite Aufnahme prüfen. Nach Geräte-/Pufferwechsel neu messen. Audio vor Zeit null wird beim Einfügen gekürzt. Versatz bleibt gespeichert. Automatische physische Kalibrierung, Taktdriftkorrektur, Plug-in-Latenzausgleich und Punch-in/out sind in Arbeit. Vor langer Sitzung kurz testen.

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

Kein Eingang: Gerät/Kanal und Linux-Mikrofonpegel prüfen, neu verbinden und neue Aufnahme starten. Kein Ausgang: Route, Pegel, Stumm/Solo, Audiogeräte prüfen. Verzerrung/rote Peaks: Gesamtpegel senken, vor PCM normalisieren; gemischtes Einfügen/überlappende Clips addieren. Einfügen abgewiesen: Kanalanzahl oder genaue Mono-Ersatzlänge prüfen. Effekt aus: Wellenform/Kopie öffnen; Kanalmischer braucht Stereo, Zeitänderungen beide Kanäle. Punkte statt Clips: Clips verschieben wählen. Platte voll: Platz schaffen, keine aktiven Arbeitsdateien löschen. Defekte Wiederherstellung: Originale bleiben; Kopie nur bei Verzicht entfernen.

In Arbeit: eigene Plug-in-Editoren, weitere Formate, automatischer Latenz-/Driftausgleich, Punch-in/out, eigene Favoriten und Markereditor. Echtzeitketten, Linux-VST3 und Aufnahme mit Begleitung sind wie beschrieben verfügbar. Vor Beenden Projekt speichern. Updates: [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
