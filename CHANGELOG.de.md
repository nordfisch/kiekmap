<!-- translated-from: CHANGELOG.md -->
<!-- source-sha: 3ceeb9548830f3fc5e53e96a6c67658e4ba084f6ad12d3c7597d674d8cba4a54 -->

# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [0.9.0] — 2. September 2026

**Das Gerät spricht zwei Sprachen, und die Dokumentation hat eine Adresse.** An der Arbeit eines
Museums mit seinen Fotos hat sich nichts geändert; geändert hat sich, wer Gerät und Dokumentation
lesen kann.

### Hinzugefügt

- **Deutsch oder Englisch, gesetzt über `KIEKMAP_LANGUAGE`** in der `.env`. Umgestellt werden
  Besucheransicht, Verwaltung, Meldungen, Import-Protokoll, Datumsbeschriftung und Zahlenformat.
  **Kein neuer Bau** — das Frontend holt die Sprache beim Start, die Einstellung lässt sich also auf
  dem Pi selbst ändern. Ein unbekannter Wert bricht den Start ab, statt still zurückzufallen. Ein
  Museum, das kein Deutsch spricht, braucht keinen Fork mehr. Siehe
  [Punkt 73](docs/developer/decisions.md)
- **Eine Doku-Website**, [nordfisch.github.io/kiekmap](https://nordfisch.github.io/kiekmap/), in
  beiden Sprachen und gebaut vom neuesten Tag: Das Museum liest die Doku zu der Fassung, die es
  betreibt. Siehe [Punkt 72](docs/developer/decisions.md)

### Geändert

- **Das Repository spricht Englisch; Deutsch wird als Übersetzung geführt.** Quelltext, Tests,
  Werkzeuge, CLI-Ausgabe, `Makefile`, Workflows, Issues und die Entwicklerdoku sind englisch. Was
  ein Museum liest — die vier Handbücher, das README, diese Datei — gibt es zweimal, und der
  Dateiname trägt die Regel: `operations.de.md` ist die deutsche Hälfte von `operations.md`.
  `check_translations.py` meldet, wenn eine Übersetzung von ihrer Quelle abgewichen ist,
  `language_check.py` prüft beide Seiten in jedem Format. Siehe
  [Punkt 71](docs/developer/decisions.md)
- **Die Dokumentation trennt sich nach Publikum**, und die Website veröffentlicht eine Hälfte.
  `docs/museum/` ist, was ein Museum braucht, um das Gerät zu benutzen, zu betreiben, zu übernehmen
  und weiterzugeben; `docs/developer/` wird im Repo gelesen, neben dem Code, den es beschreibt.
  Siehe [Punkt 75](docs/developer/decisions.md)
- **Die Historie ist abgeschlossen, die offene Arbeit steht in Issues.**
  [docs/developer/archive/history.de.md](docs/developer/archive/history.de.md) endet mit 0.8.0 und
  bleibt deutsch; ihr Nummernregister löst jedes „Punkt N" auf. `docs/backlog.md` ist weg. Was die
  Arbeit lehrt, wird ein Punkt in `decisions.md`. Siehe [Punkt 69](docs/developer/decisions.md)
- **Das Repository ist abgesichert**: Branch-Schutz für `main` und `develop`, Secret-Scanning,
  CodeQL und die private Sicherheitsmeldung statt einer Adresse in einer Datei
- **Vitest von 2 auf 3.** Nicht wegen einer Funktion: Vitest 2 brachte eigene, alte Kopien von
  `vite` und `esbuild` mit, und daran hingen fünf von sechs Dependabot-Meldungen

### Behoben

- **Die Bereitschaftsprüfung meldete, woran sie scheiterte.** `/health` ist der einzige Endpunkt,
  der ohne PIN antwortet, und er gab den Datenbankfehler wörtlich zurück. Die Ursache geht jetzt
  ins Protokoll, wo sie auch länger überlebt als eine curl-Antwort
- **Die englische Instanz zeigte auf zwei Wegen Deutsch:** die Kartenzuschreibung, die im
  Kartenstil statt im Textkatalog stand, und zwanzig Oberflächentexte, die gelesen wurden, bevor
  die Sprache aufgelöst war. Ein Test geht die Quellen jetzt mit dem TypeScript-Parser durch und
  schlägt bei jedem Zugriff außerhalb einer Funktion fehl

### Entfernt

- **Die SPDX-Kopfzeilen**, zwei Zeilen über jedem Docstring in 153 Dateien. Die Lizenz verlangt sie
  nicht, und keine Prüfung erzwang sie; `LICENSE` und `NOTICE` decken jede Weitergabe des Repos ab.
  Eine einzeln herauskopierte Datei trägt jetzt keinen Lizenzhinweis mehr — der Preis steht in
  [Punkt 70](docs/developer/decisions.md)

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
aus denen es entstand, stehen in [docs/developer/archive/history.de.md](docs/developer/archive/history.de.md) und in den Commits. Ab
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
  [docs/museum/adaption.de.md](docs/museum/adaption.de.md)
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

- **Acht Dateien, jede mit genau einer Frage**, erschlossen über [docs/museum/index.de.md](docs/museum/index.de.md)
- **Backlogpunkte tragen feste Nummern**, unter denen sie zitiert werden; eine Nummer wird nie neu
  vergeben
- **Die Historie hat ein Register** mit einer Zeile je Abschnitt und Datum, erzeugt und geprüft
