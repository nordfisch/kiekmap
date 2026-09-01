<!-- translated-from: CHANGELOG.md -->
<!-- source-sha: b9753082f2bb31c882d4255f987adc268fcec0f480fa9adf741cc8fef4d322b7 -->

# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [Unveröffentlicht]

### Hinzugefügt

- **Das Repo ist öffentlich** — `github.com/nordfisch/kiekmap`, Apache-2.0, dazu die private
  Sicherheitsmeldung bei GitHub, Branch-Schutz für `main` und `develop`, Secret-Scanning und ein
  Abzeichen im README

### Geändert

- **Das Repository spricht Englisch; Deutsch ist eine Übersetzung und wird als solche geführt.**
  Die Sprachgrenze verlief bisher nach Publikum durch das Repo; sie verläuft jetzt zwischen dem
  Repo und dem, was daraus veröffentlicht wird. `operations.de.md` ist deutsch, `operations.md`
  englisch — der Dateiname trägt die Regel, es gibt keine Liste zu pflegen. Issues, Labels,
  Commit-Nachrichten ab dem 30. August 2026 und jeder Testname sind englisch. Siehe
  [Punkt 71](docs/decisions.md)
- **`docs/archive/history.de.md` ist abgeschlossen, und eine Nachfolgerin gibt es nicht.** Sie endet am
  25. August 2026 mit v0.8.0 und bleibt deutsch. Was die Arbeit lehrt, wird ein Punkt in
  `decisions.md`; wie sie verlief, steht in den Commits und den geschlossenen Issues
- **Die offenen Punkte sind GitHub-Issues**, `docs/backlog.md` ist weg. Das **Nummernregister**
  steht jetzt in `history.de.md` und löst jedes „Punkt N" auf — die offenen auf ihr Issue, die
  übrigen auf den Abschnitt unter ihrem Datum. Zu Issue-Nummern konnten sie nicht werden, weil
  GitHub einen Zähler mit den Pull Requests teilt; „Punkt 15" wurde Issue #18. Siehe
  [Punkt 69](docs/decisions.md)
- **Die Entwicklerdoku ist englisch** — `architecture`, `development`, `decisions`, `CONTRIBUTING`
  und `CLAUDE.md`, rund 24.000 Wörter. `decisions.md` ist vorher zusammengefasst worden: alle 67
  Punkte bleiben, der Text ist ein Drittel kürzer
- **Der `0.8.0`-Block unten ist zusammengefasst**, nach Bereichen geordnet statt nach
  Arbeitsschritt. Das Kleinteilige steht in `history.de.md` und in den Commits
- **`tools/language_check.py` prüft beide Seiten** und jedes Format, nicht nur `.py`, `.ts` und
  `.tsx`: deutsche Doku auf umschriebene Umlaute, englische auf deutsche Absätze, dazu die
  Kommentare von CSS, Dockerfiles, Shell-Skripten und Konfigurationsdateien
- **`tools/check_anchors.py` liest auch `CLAUDE.md` und `CONTRIBUTING.md`**
- **Die Zahl vor einer Liste ist weg**, wo die Liste direkt darunter steht. Vier Dateien sagten
  „fünf" und zählten sechs auf; eine Zahl in Prosa altert still. Siehe
  [Punkt 59](docs/decisions.md)
- **Vitest von 2 auf 3.** Nicht wegen einer Funktion: Vitest 2 brachte eigene, alte Kopien von
  `vite` und `esbuild` mit, und daran hingen fünf von sechs Dependabot-Meldungen

### Entfernt

- **Die SPDX-Kopfzeilen sind aus jeder Quelldatei weg.** Zwei Zeilen Lizenzbuchführung über jedem
  Docstring; die Lizenz verlangt sie nicht, und keine Prüfung erzwang sie. `LICENSE` und `NOTICE`
  decken jede Weitergabe des Repos ab. Eine einzeln herauskopierte Datei trägt danach keinen
  Hinweis mehr — der Preis steht in [Punkt 70](docs/decisions.md)

## [0.8.0] — 2026-08-25

Die erste bezifferte Fassung. **Kein Meilenstein der Funktion**, sondern der Punkt, an dem das
Projekt sich selbst festhalten kann: eine Versionsnummer an einem Ort, festgenagelte
Abhängigkeiten, ein Releaseprozess, geprüfte Herkunft jedes Commits.

**Warum 0.8 und nicht 1.0:** `1.0.0` sagt unter SemVer eine stabile öffentliche Schnittstelle zu.
Alles unter `deploy/pi/` ist bis heute ungeprüft, und die Abnahme auf dem ersten Gerät steht aus.
Die `1.0.0` wird danach vergeben — siehe
[Issue #18](https://github.com/nordfisch/kiekmap/issues/18).

**Dieser Block ist nach Bereichen geordnet, nicht nach Hinzugefügt, Geändert und Behoben.** Vor
0.8.0 gab es keine Fassung, gegen die sich etwas geändert hätte; alles hier ist neu. Die Schritte,
aus denen es entstand, stehen in [docs/archive/history.de.md](docs/archive/history.de.md) und in den Commits. Ab
0.9.0 gelten wieder die drei Rubriken.

### Karte und Zeitleiste

- Historische Fotos als Vorschaubilder an ihrem Aufnahmeort, auf einer **offline gelesenen
  Vektorkarte**. Dichtes wird ein Kreis mit Anzahl; Fotos an derselben Stelle bilden einen Stapel
  zum Durchblättern
- Ein eigener Kartenstil, **„Papier"**: nichts auf der Karte ist so gesättigt wie ein Foto
- **Ein Zeitschieber mit drei Anfassern** — die beiden Enden und der ganze Bereich. Die Achse zeigt
  immer den ganzen Bestand, dieselbe Stelle bedeutet damit immer dasselbe Jahr
- **Der Zeitfilter fragt auf Überlappung ab.** Ein auf „1920er" datiertes Foto erscheint auch bei
  der Auswahl 1925–1930; bei der naheliegenden Abfrage verschwände der Großteil des Bestands
- **Ein Schalter für die Fotos ohne Jahr**, anfangs an. Ein undatiertes Foto überlappt keinen
  Zeitraum und fiele sonst aus jeder Auswahl — bei diesem Bestand zwei Drittel
- **Eine Detailansicht in voller Größe** mit Titel, Beschreibung, Adresse, Bildnachweis, der kurzen
  SHA-256 und einem Stift, der nach der PIN in die Bearbeitung führt

### „Hilf mit"

- **Drei Fragen an den Besucher:** „Wo ist das?", „Wann war das?" und danach „Welche Hausnummer?"
- **Kein einziges Eingabefeld, keine Tastatur.** Straße über Anfangsbuchstabe und Knöpfe, Datierung
  über Jahrzehnt und dann Jahr, Hausnummer über Abschnitt und Raster
- **Besucherbeiträge landen sofort im Bestand, aber nur in leeren Feldern.** Kuratierte Angaben
  sind unantastbar, Koordinaten außerhalb der Region werden abgewiesen
- **Nach einem Beitrag kommt dasselbe Foto mit der anderen Frage**, solange ihm etwas fehlt
- **Der Kartentipp ist erst nach Ansage scharf** — vorher setzte ein Suchender versehentlich einen
  Punkt
- **Läuft eine Frage leer, fällt der Bereich auf die andere zurück.** Ist nichts mehr zu ergänzen,
  verschwindet er und die Karte nimmt die volle Breite

### Verwaltung

- **Zugang über das Ortswappen und eine PIN**, in einer Sitzung mit Ablauf. Die Sperre nach fünf
  Fehlversuchen ist es, was vier Ziffern vertretbar macht
- **Eine Übersicht, in der jede Zahl ein Weg ist**, darunter der Betrieb: Tage seit Sicherung,
  Import und letztem Beitrag
- **Eine Fotoliste mit den Filtern „Ohne Ort" und „Ohne Jahr"**, Suche und Seitenblättern. Verorten
  und Datieren sind zwei Arbeiten
- **Ein Metadateneditor.** Ein **fehlendes** Feld heißt „unverändert lassen", ein **leeres** heißt
  „löschen" — sonst ließe sich eine falsche Datierung nur ersetzen, nie herausnehmen
- **Moderation:** Besucherbeiträge einzeln zurücknehmen, außer das Feld wurde inzwischen von Hand
  bearbeitet
- **Löschen heißt: aus der Ausstellung nehmen.** Datei und Zeile bleiben und lassen sich
  wiederherstellen
- **Ein Stapel-Import mit Nacharbeits-Tabelle.** Die Fotos sind schon nach dem Hochladen
  gespeichert — ein geschlossener Browser darf keine Uploads kosten

### Import

- **Vier Wege, eine Pipeline:** überwachter Eingangsordner, CLI, Hochladen im Browser und
  USB-Stick. SHA-256 als Dateiname und Dublettenschutz, EXIF, IPTC und XMP, zwei Vorschaugrößen,
  Ausrichtung, CMYK-Umwandlung, JPEG, TIFF und MPO
- **Ob ein EXIF-Datum das Foto datiert, entscheidet das Gerät.** Wo die Datei keines nennt, gilt
  `exif_date_max_year`: ein Datum ab 1990 ist das des Scans, nicht der Aufnahme
- **Der Pfad wird ausgewertet.** Aus `Hauptstraße/14 Gasthof Petersen/` werden Ort, Titel,
  Ortsbezeichnung und Schlagwörter; die Straße erkennt der Ortsindex, nicht ein Ordnername
- **Der Archivordner schlägt die EXIF-Koordinate**, sobald er eine Hausnummer nennt. Gemessen: 278
  von 413 EXIF-verorteten Fotos teilten ihre Koordinate mit einem anderen — solche Werte sind
  eingetragen, nicht gemessen
- **Verworfen wird, was wie eine Auskunft aussieht und keine ist:** „OLYMPUS DIGITAL CAMERA" als
  Titel, „unbekannt" als Fotograf, der Name der Scannersoftware
- **Ein Ortsindex aus OpenStreetMap**, nur Straßen und Hausnummern. Gleichnamige Straßen werden
  räumlich getrennt, Nummern natürlich sortiert, und die Suche findet „Mühlenweg" ohne Umlaut
- **Werkzeuge für den Erstimport:** `empty`, `dubletten` und `tools/to_jpeg.py`
- **Der Bestand steht bei 1324 Fotos** aus zwei Archivständen; 45 Dubletten sind aus der
  Ausstellung genommen, 1275 stehen auf der Karte

### Sicherung

- **Auf USB-Stick: Stick einstecken, ein Knopf, Fortschrittsbalken.** Ein Ordner statt eines
  Archivs, damit eine abgebrochene Sicherung teilweise brauchbar bleibt; der zweite Lauf schreibt
  nur, was dazugekommen ist
- **Als Ziel gelten nur echte, beschreibbare Einhängepunkte** — sonst liefe die Sicherung auf
  dieselbe SD-Karte, gegen deren Ausfall sie schützt
- **Wiederherstellen kopiert erst daneben und schaltet zuletzt um.** Der bisherige Stand wandert
  beiseite und wird nie gelöscht; eine Sicherung von einer neueren Fassung wird abgelehnt, bevor
  etwas ersetzt ist
- **Auch als eine ZIP-Datei** für den Fall ohne Stick, zurückgespielt über den Eingangsordner
- **Eine Erinnerung auf der Übersicht**, ab 30 Tagen rot

### Kiosk-Betrieb auf dem Pi

- **`setup-pi.sh` richtet einen frischen Raspberry Pi ein**, `kiekmap-kiosk.service` startet
  Chromium unter cage im Vollbild, sobald `/api/health` antwortet, mit frischem Profil und Neustart
  nach einem Absturz
- **`update.sh` spielt ein Update vom USB-Stick ein**, ohne den Bestand anzufassen
- **Leerlauf-Reset nach fünf Minuten.** Der Kiosk hat keinen Reload-Knopf, keine Adressleiste und
  keine Tastatur — ein verhakter Zustand bliebe sonst bis zum Netzstecker stehen
- **Die Karte zeichnet erst neu, wenn die Kamera zur Ruhe kommt.** Auf dem Pi ist das der
  Unterschied zwischen ruckeln und nicht ruckeln
- **`99-kiekmap-usb.rules` und `kiekmap-usb-mount`** hängen Sticks auf Pi OS Lite ein, das keinen
  Automounter hat. `make prod-mac` fährt denselben Containerbetrieb auf einem Mac

### Nichts Ortsspezifisches im Code

- **Kartenausschnitt, Jahrzehnte und Straßenauswahl kommen aus `tiles/region.json`**; Karte und
  Ortsindex sind gebaute Artefakte. Ein zweites Museum braucht keinen Fork — siehe
  [docs/adaption.de.md](docs/adaption.de.md)
- **Das Ortswappen ist eine austauschbare Datei**; im Repo liegt ein Platzhalter, denn ein
  Hoheitszeichen darf nicht an jeden weitergegeben werden, der ein Repo klont
- **Drei Import-Einstellungen**, alle leer voreingestellt
- **Der Beispielbestand ist erfunden.** 18 gezeichnete Bilder mit ausgedachten Menschen; echt sind
  nur Straßennamen und Koordinaten, und seine Lücken sind Absicht

### Werkzeug und Prüfungen

- **`make check` vor jedem Commit:** Stil, die Prüfungen daneben, alle Tests. Dazu ein Git-Hook für
  die schnellen und derselbe Lauf bei jedem Pull Request
- **Die Prüfungen lesen Dateien, die kein Test je sieht:** die Sprachregelung, die Verweise in
  `docs/`, den Weg jeder Einstellung in den Container, die Buchführung über die Backlognummern, das
  Register der Historie und die Versionsnummer an ihren fünf Stellen
- **Eine Versionsnummer an einem Ort.** `make version v=0.8.0` schreibt sie an alle fünf
- **Die Backend-Abhängigkeiten sind festgenagelt** in `backend/requirements.lock`; das Abbild
  installiert daraus
- **`make release` baut den Update-Stick** und bricht ab bei schmutzigem Arbeitsbaum oder fehlendem
  Tag

### Herkunft, Lizenz, Veröffentlichung

- **Jeder Commit und jedes Tag ist signiert** (SSH), auch die aus der Zeit vor dem Schlüssel. Bäume,
  Betreffzeilen und Autor-Daten sind unverändert geblieben
- **Zwei Branches:** `develop` für den Alltag, `main` für den Stand, der im Museum läuft. Squash und
  Rebase sind abgeschaltet — die Doku zitiert Commits mit Hash
- **Apache-Lizenz 2.0**, Copyright 2026 Kalle Erlhoff. Der Fotobestand des Museums ist ausdrücklich
  nicht erfasst
- **Die Lizenzhinweise der mitgelieferten Pakete reisen mit**, als `THIRD-PARTY.txt` neben jedem
  Artefakt. Die Karte nennt neben OpenStreetMap die ODbL
- **Beispiele nennen keine Namen aus dem Holmer Bestand**, sondern den erfundenen Kader aus `seed/`
- **`CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`, `AUTHORS`** und Meldungsvorlagen.
  Sicherheitsmeldungen laufen über die private Meldung bei GitHub, damit keine Adresse im Repo steht

### Dokumentation

- **Acht Dateien, jede mit genau einer Frage**, erschlossen über [docs/index.de.md](docs/index.de.md)
- **Backlogpunkte tragen feste Nummern**, unter denen sie zitiert werden; eine Nummer wird nie neu
  vergeben
- **Die Historie hat ein Register** mit einer Zeile je Abschnitt und Datum, erzeugt und geprüft
