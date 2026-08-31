# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [Unveröffentlicht]

### Hinzugefügt

- **Das Repo ist öffentlich** — `github.com/nordfisch/kiekmap`, Apache-2.0. Dazu die private
  Sicherheitsmeldung, auf die `SECURITY.md` verweist und die es nur auf öffentlichen Repos gibt,
  Branch-Schutz für `main` und `develop`, Secret-Scanning mit Push-Schutz, und ein Abzeichen im
  README, das den Zustand der Prüfungen zeigt

### Geändert

- **`docs/history.md` ist abgeschlossen, und eine Nachfolgerin gibt es nicht.** Sie endet am
  25. August 2026 mit v0.8.0 und bleibt deutsch. Was die Arbeit lehrt, wird künftig ein Punkt in
  `decisions.md` mit kurzer Begründung; wie sie verlief, steht in den Commits und den geschlossenen
  Issues. Ein neuer Abschnitt in der Historie macht `build_register.py --check` rot
- **Die Entwicklerdoku ist englisch.** `architecture`, `development`, `decisions`, `CONTRIBUTING`
  und `CLAUDE.md` — rund 24.000 Wörter. `decisions.md` ist vorher zusammengefasst worden: alle 67
  Punkte bleiben, der Text ist ein Drittel kürzer. Weg sind Herkunfts- und Umsetzungsgeschichte,
  die Buchführung der Bereinigungsläufe und die am Holmer Bestand gemessenen Stückzahlen. Zwei Punkte sind zu Verweisen geworden und behalten ihre
  Nummer, damit ältere Zitate weiter auflösen
- **Der `0.8.0`-Block im CHANGELOG ist von 250 auf 55 Einträge zusammengefasst**, gruppiert nach
  Bereichen statt nach Arbeitsschritt. Das Kleinteilige steht in `history.md` und in den Commits
- **Die Sprachgrenze verläuft jetzt nach Publikum, nicht nach Dateityp.** Deutsch bleibt, was
  Besucher, Museumsteam und Betreiber lesen: Oberfläche, CLI, `usermanual`, `operations`,
  `adaption`, README, CHANGELOG, Issues und die Testdateien. Englisch wird, was Entwickler lesen:
  Bezeichner, Kommentare, `architecture`, `development`, `decisions`, `CONTRIBUTING`, `CLAUDE.md`
  und ab dem 30. August 2026 die Commit-Nachrichten. Die Übersetzung folgt schrittweise; die Regel
  gilt ab sofort. Siehe [Punkt 68](docs/decisions.md)
- **Die Zahl vor den Prüfungen ist weg**, wo direkt darunter die Liste steht. Vier Dateien sagten
  „fünf" und zählten sechs auf; eine Zahl in Prosa altert still. Siehe
  [Punkt 59](docs/decisions.md)
- **`tools/language_check.py` prüft beide Seiten.** Statt einer Prosaliste zwei: deutsche Doku wird
  auf umschriebene Umlaute geprüft, englische auf deutsche Absätze. Dazu Schreibregeln für
  Dokumentation in beiden Sprachen, in [CLAUDE.md](CLAUDE.md)
- **`tools/check_anchors.py` liest auch `CLAUDE.md` und `CONTRIBUTING.md`.** Zwei Dateien, in die
  andere hineinverweisen und deren Überschriften bis dahin niemand nachhielt
- **Vitest von 2 auf 3.** Nicht wegen einer neuen Funktion, sondern weil Vitest 2 seine eigenen,
  alten Kopien von `vite` und `esbuild` mitbrachte — daran hingen fünf von sechs
  Dependabot-Meldungen. Im Baum liegt jetzt je eine Fassung. Ausgeliefert war nichts davon; die
  189 Tests laufen unverändert

## [0.8.0] — 2026-08-25

Die erste bezifferte Fassung. Sie ist **kein Meilenstein der Funktion**, sondern der Punkt, an dem
das Projekt sich selbst festhalten kann: eine Versionsnummer an einem Ort, festgenagelte
Abhängigkeiten, ein Releaseprozess, geprüfte Herkunft jedes Commits.

**Warum 0.8 und nicht 1.0:** `1.0.0` sagt unter SemVer eine stabile öffentliche Schnittstelle zu.
Alles unter `deploy/pi/` ist bis heute ungeprüft, und die Abnahme auf dem ersten Gerät steht aus.
Die `1.0.0` wird danach vergeben — siehe [Punkt 15](docs/backlog.md).

**Dieser Block ist nach Bereichen geordnet, nicht nach Hinzugefügt, Geändert und Behoben.** Vor
0.8.0 gab es keine Fassung, gegen die sich etwas geändert oder in der sich etwas beheben ließe;
alles hier ist neu. Die 250 Einzelschritte, aus denen es entstand, stehen in
[docs/history.md](docs/history.md) und in den Commits. Ab 0.9.0 gelten wieder die drei Rubriken.

### Karte und Zeitleiste

- Historische Fotos als Vorschaubilder an ihrem Aufnahmeort, auf einer **offline gelesenen
  Vektorkarte**. Bei hoher Dichte fasst supercluster sie zu einem Kreis mit Anzahl zusammen; Fotos
  an derselben Stelle bilden einen Stapel, der sich im Vollbild durchblättern lässt
- Eigener Kartenstil **„Papier"** in den Farben der Oberfläche. Regel beim Aussuchen: nichts auf
  der Karte darf so gesättigt sein wie ein Foto. Ohne Geschäfte, Hausnummern und Autobahnschilder
- **Zeitschieber als Trimmer mit drei Anfassern** — die beiden Enden und der ganze Bereich. Die
  Achse zeigt immer den ganzen Bestand, die Balken darunter den sichtbaren Ausschnitt; dieselbe
  Stelle des Schiebers bedeutet damit immer dasselbe Jahr
- **Der Zeitfilter fragt auf Überlappung ab.** Ein auf „1920er" datiertes Foto erscheint auch bei
  der Auswahl 1925–1930. Bei der naheliegenden Abfrage verschwände der Großteil des Bestands
- **Ein Schalter für die Fotos ohne Jahr**, neben dem Zeitschieber, anfangs an. Ein undatiertes
  Foto überlappt keinen Zeitraum und fiele sonst aus jeder Auswahl heraus — bei diesem Bestand
  zwei Drittel der Sammlung
- **Detailansicht in voller Größe** mit Titel, Beschreibung, Adresse und Bildnachweis. Darunter
  die ersten acht Zeichen des SHA-256, die auch die Fotosuche der Verwaltung findet, und ein
  Stift, der nach der PIN direkt in die Bearbeitung dieses Fotos führt

### „Hilf mit"

- **Drei Fragen an den Besucher:** „Wo ist das?", „Wann war das?" und — nachrangig — „Welche
  Hausnummer?". Ein Foto irgendwohin zu setzen ist mehr wert, als eines von der Straßenmitte an
  sein Haus zu rücken
- **Kein einziges Eingabefeld, keine Tastatur.** Straße über Anfangsbuchstabe und Knopfliste,
  Datierung über Jahrzehnt und dann Jahr, Hausnummer über Abschnitt und Knopfraster. Ein Suchfeld
  ohne Tastatur sieht aus wie ein defektes Bedienelement
- **Besucherbeiträge landen sofort im Bestand, aber nur in leeren Feldern.** Kuratierte Angaben
  sind unantastbar, Koordinaten außerhalb der Region werden abgewiesen
- **Nach einem Beitrag kommt dasselbe Foto mit der anderen Frage**, solange ihr etwas fehlt. Wer
  gerade gesagt hat, wann das war, kennt das Foto und schaut es an
- **Der Kartentipp ist erst nach Ansage scharf.** Ein Knopf „Auf der Karte zeigen" führt dorthin;
  vorher setzte jeder Tipp auf eine freie Fläche einen Punkt, auch der eines Suchenden
- **Läuft eine Frage leer, fällt der Bereich auf die andere zurück.** Ist gar nichts mehr zu
  ergänzen, verschwindet er und die Karte nimmt die volle Breite

### Verwaltung

- **Zugang über das Ortswappen und eine PIN** auf einem Zahlenfeld mit großen Tasten, Sitzung mit
  Ablauf. Die Sperre nach fünf Fehlversuchen ist der eigentliche Schutz einer vierstelligen PIN —
  sie macht aus Sekunden Jahre. `python -m app.cli pin` erzeugt den Hash für die `.env`
- **Eine Übersicht, in der jede Zahl ein Weg ist:** Fotos insgesamt, Ohne Ort, Ohne Jahr, Gelöscht,
  Beiträge — jede führt in die passende Liste. Darunter der Betrieb: Tage seit Sicherung, Import
  und letztem Beitrag
- **Fotoliste mit den Filtern „Ohne Ort" und „Ohne Jahr"**, Suche und Seitenblättern. Verorten und
  Datieren sind zwei Arbeiten; wer die eine macht, will die andere nicht dazwischen
- **Metadateneditor.** Ein **fehlendes** Feld heißt „unverändert lassen", ein **leeres** heißt
  „löschen" — sonst ließe sich eine falsche Datierung nur ersetzen, nie herausnehmen
- **Moderation:** Besucherbeiträge einzeln zurücknehmen. Nicht mehr, wenn das Feld inzwischen von
  Hand bearbeitet wurde; das würde die Arbeit des Kurators mit wegwerfen
- **Löschen heißt: aus der Ausstellung nehmen.** Datei und Datenbankzeile bleiben, „Wiederherstellen"
  holt beides zurück. Gelöschte Fotos zählen in keiner Kachel mit
- **Stapel-Import mit Nacharbeits-Tabelle.** Jahr, Ort, Bildnachweis und Schlagwort gelten für den
  ganzen Stapel. Die Fotos sind schon nach dem Hochladen in der Datenbank — ein geschlossener
  Browser darf keine Uploads kosten

### Import

- **Vier Wege, eine Pipeline:** überwachter Eingangsordner, CLI, Hochladen im Browser und
  USB-Stick. SHA-256 als Dateiname und Dublettenschutz, EXIF, IPTC und XMP, zwei Vorschaugrößen,
  Beachtung der Ausrichtung, CMYK-Umwandlung, JPEG, TIFF und MPO
- **Ob ein EXIF-Datum das Foto datiert, entscheidet das Gerät.** Ein Scanner datiert nichts, eine
  Kamera datiert auch nach 1990. Wo die Datei kein Gerät nennt, gilt `exif_date_max_year`: ein
  Datum ab 1990 ist das des Scans, nicht der Aufnahme
- **Der Pfad wird ausgewertet.** Aus `Hauptstraße/14 Gasthof Petersen/` werden Ort, Titel,
  Ortsbezeichnung und Schlagwörter. Die Straße erkennt der Ortsindex, nicht ein Ordner namens
  „Straßen" — es steht damit nichts Ortsspezifisches im Code
- **Der Archivordner schlägt die EXIF-Koordinate**, sobald er eine Hausnummer nennt. Gemessen:
  278 von 413 EXIF-verorteten Fotos teilten ihre Koordinate mit einem anderen. Solche Werte sind
  eingetragen, nicht gemessen
- **Verworfen wird, was wie eine Auskunft aussieht und keine ist:** „OLYMPUS DIGITAL CAMERA" als
  Titel, „unbekannt" als Fotograf, der Name der Scannersoftware, ein Ordner „00". Übernommen
  stünde das im Kiosk unter dem Bild
- **Ortsindex aus OpenStreetMap**, nur Straßen und Hausnummern. Gleichnamige Straßen werden
  räumlich getrennt, Hausnummern natürlich sortiert (1, 1a, 2, 9, 10), die Suche findet
  „Mühlenweg" auch ohne Umlaut und läuft ohne Internet
- **Werkzeuge für den Erstimport:** `python -m app.cli empty` leert den Bestand und will dafür die
  Anzahl der Fotos getippt haben, `python -m app.cli dubletten` findet dasselbe Bild mehrfach über
  einen Differenzhash, `tools/to_jpeg.py` stellt aus einem Archivordner JPEG-Kopien her
- **Der Bestand steht bei 1324 Fotos** aus zwei Archivständen, durchgesehen und bereinigt; 45
  Dubletten sind aus der Ausstellung genommen, 1275 stehen auf der Karte

### Sicherung

- **Auf USB-Stick: Stick einstecken, ein Knopf, Fortschrittsbalken.** Ein Ordner statt eines
  Archivs — eine abgebrochene Sicherung ist so teilweise brauchbar statt wertlos. Die zweite
  Sicherung schreibt nur, was dazugekommen ist. `VACUUM INTO` schreibt die Datenbank konsistent
  heraus, ohne den Kiosk anzuhalten
- **Als Ziel gelten nur echte, beschreibbare Einhängepunkte** — sonst liefe die Sicherung auf
  dieselbe SD-Karte, gegen deren Ausfall sie schützt
- **Wiederherstellen kopiert erst daneben und schaltet zuletzt um.** Der bisherige Stand wandert
  nach `data/vorher-<Datum>/` und wird nie gelöscht. Das Schema zieht sich selbst nach; eine
  Sicherung von einer neueren Programmfassung wird abgelehnt, bevor etwas ersetzt ist
- **Auch als eine ZIP-Datei**, im Strom und unkomprimiert erzeugt, für den Fall ohne Stick.
  Zurückspielen geht über den Eingangsordner, mit Rückfrage — von selbst passiert dort nichts
- **Erinnerung auf der Übersicht**, ab 30 Tagen rot

### Kiosk-Betrieb auf dem Pi

- **`deploy/pi/setup-pi.sh` richtet einen frischen Raspberry Pi ein**, `kiekmap-kiosk.service`
  startet cage mit Chromium im Vollbild, sobald `/api/health` antwortet. Frisches Browserprofil bei
  jedem Start, Neustart durch systemd nach einem Absturz
- **`deploy/pi/update.sh` spielt ein Update vom USB-Stick ein**, ohne den Bestand anzufassen
- **Leerlauf-Reset nach fünf Minuten**: Die Seite lädt neu. Im Kiosk gibt es keinen Reload-Knopf,
  keine Adressleiste und keine Tastatur — ein verhakter Zustand bliebe sonst bis zum Netzstecker
  stehen. Ein Absturz der Oberfläche zeigt einen deutschen Satz und lädt genau einmal von selbst
  neu
- **Die Karte zeichnet ihre Marker nur neu, wenn die Kamera zur Ruhe kommt** und sich die sichtbaren
  Gruppen wirklich geändert haben. Auf dem Pi ist das der Unterschied zwischen ruckeln und nicht
  ruckeln
- **`99-kiekmap-usb.rules` und `kiekmap-usb-mount`** hängen Sticks auf Pi OS Lite ein — dort gibt
  es keinen Automounter. `deploy/docker-compose.mac.yml` und `make prod-mac` fahren denselben
  Containerbetrieb auf einem Mac

### Nichts Ortsspezifisches im Code

- **Kartenausschnitt, Jahrzehnte und Straßenauswahl kommen aus `tiles/region.json`**, Karte und
  Ortsindex sind gebaute Artefakte. Ein zweites Museum braucht keinen Fork, sondern eine eigene
  `region.json` und `.env`. Der Weg dorthin steht in [docs/adaption.md](docs/adaption.md)
- **Das Ortswappen ist eine austauschbare Datei** unter `frontend/public/logo.png`; im Repo liegt
  ein Platzhalter. Ein Hoheitszeichen darf nicht an jeden weitergegeben werden, der ein Repo klont
- **Drei Import-Einstellungen**, alle leer voreingestellt: `KIEKMAP_IMPORT_TAGS`,
  `KIEKMAP_IMPORT_CREDIT` und `KIEKMAP_IMPORT_PROVENANCE`
- **Der Beispielbestand ist erfunden.** 18 gezeichnete Bilder aus `tools/build_seed.py`, dazu
  ausgedachte Menschen und Bildnachweise; echt sind nur Straßennamen und Koordinaten. Seine Lücken
  sind Absicht, und der Generator bricht ab, wenn eine fehlt

### Werkzeug und Prüfungen

- **`make check` vor jedem Commit:** Stil, die Prüfungen daneben, alle Tests. Dazu ein Git-Hook
  unter `.githooks/` für die schnellen, und derselbe Lauf als GitHub-Actions-Ablauf bei jedem Pull
  Request
- **Sechs Prüfungen lesen Dateien, die kein Test je sieht:** die Sprachregelung, die Verweise in
  `docs/`, den Weg jeder Einstellung in den Container, die Buchführung des Backlogs über seine
  Nummern, das Register der Historie und die Versionsnummer an ihren fünf Stellen
- **Eine Versionsnummer an einem Ort.** `make version v=0.8.0` schreibt sie an alle fünf Stellen.
  Bisher standen sie auf `0.1.0` — darunter `__version__`, das `/api/health` meldet
- **Die Backend-Abhängigkeiten sind festgenagelt.** `backend/requirements.lock` nennt 28 Pakete mit
  genauer Version; das Abbild installiert daraus
- **`make release` baut den Update-Stick** — beide Abbilder, `abbilder.tar`, die `version`-Datei
  und auf Wunsch Karte und Ortsindex. Bricht ab bei schmutzigem Arbeitsbaum oder fehlendem Tag

### Herkunft, Lizenz, Veröffentlichung

- **Alle 188 Commits tragen eine Identität und sind signiert** (SSH), Tags ebenso — auch die aus
  der Zeit vor dem Schlüssel. Bäume, Betreffzeilen und Autor-Daten sind unverändert geblieben
- **Zwei Branches:** `develop` für den Alltag, `main` für den Stand, der im Museum läuft. Squash
  und Rebase sind abgeschaltet — die Dokumentation zitiert Commits einzeln mit Hash
- **Apache-Lizenz 2.0**, Copyright 2026 Kalle Erlhoff. `LICENSE` und `NOTICE` gelten für Code,
  Dokumentation und die Beispielbilder; der Fotobestand des Museums ist ausdrücklich nicht erfasst
- **Die Lizenzhinweise der mitgelieferten Pakete reisen mit.** `make notices` erzeugt zu jedem
  Artefakt eine `THIRD-PARTY.txt` mit den vollen Texten. Die Karte nennt neben OpenStreetMap auch
  die Datenlizenz ODbL
- **Beispiele nennen keine Namen aus dem Holmer Bestand**, sondern den erfundenen Kader aus `seed/`
- **`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS`** und Meldungsvorlagen unter
  `.github/`. Sicherheitsmeldungen laufen über die private Meldung bei GitHub, damit keine Adresse
  im Klartext im Repo steht

### Dokumentation

- **Neun Dateien, jede mit genau einer Frage**, erschlossen über [docs/index.md](docs/index.md):
  `architecture` (woraus es besteht), `decisions` (warum es so ist), `history` (wie es dazu kam),
  `development` (wie man daran arbeitet), `backlog` (was fehlt), `adaption` und `licensing` (für
  ein zweites Museum), `operations` und `usermanual` (für den Betrieb)
- **Backlogpunkte tragen feste Nummern**, unter denen sie zitiert werden. Nummern werden nie neu
  vergeben, auch nicht nach dem Erledigen
- **Die Historie hat ein Register** mit einer Zeile je Abschnitt und Datum, erzeugt und geprüft
