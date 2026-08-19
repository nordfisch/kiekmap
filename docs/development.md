# Entwicklung

Für Menschen, die an Kiekmap arbeiten. Warum die Dinge so sind, steht in
[decisions.md](decisions.md); woraus es besteht, in [architecture.md](architecture.md); wie es
dazu gekommen ist, in [history.md](history.md); was noch kommt, im [backlog.md](backlog.md); wie
man hier arbeitet, hier.

## Einrichtung

Voraussetzungen: Python 3.12+, Node 18+ (empfohlen 22), Git. Optional Docker für den
Realitätscheck, `pmtiles` (via Homebrew) für den Kartenbau.

```bash
git clone <repo> && cd kiekmap
make dev
```

`make dev` legt beim ersten Aufruf die Python-Umgebung an, installiert die Node-Pakete und startet
beides. Backend auf **8000** (Doku unter `/api/docs`), Frontend auf **5173**. Vite leitet `/api`
weiter, sodass in Entwicklung und Betrieb dieselben relativen Pfade gelten.

**Die Karte fehlt noch.** Ohne sie zeigt das Frontend „Die Region konnte nicht geladen werden":

```bash
make tiles     # Kacheln, Schriften und Symbole für die Region aus tiles/region.json
make places    # Ortsindex für die Ortssuche (fragt einmalig Overpass)
```

`make tiles` lädt rund 19 MB und dauert eine Minute. Beides braucht Internet und läuft auf dem
Entwicklungsrechner — auf den Pi kommt nur das Ergebnis.

Testdaten:

```bash
cd backend && .venv/bin/python -m app.cli import tests/fixtures
```

## Entwicklungsumgebung

**PyCharm Professional** deckt alles in einem Fenster ab. Alternativ **PyCharm Community** fürs
Backend plus **WebStorm** fürs Frontend — WebStorm ist für nicht-kommerzielle Nutzung kostenlos,
eine „Community"-Ausgabe gibt es nicht. Was in der Community-Variante fehlt und wie man es ersetzt:

| fehlt | Ersatz |
|---|---|
| Database-Tool | DB Browser for SQLite, oder `sqlite3 data/kiekmap.db` |
| HTTP-Client | `/api/docs` — interaktiv und immer aktuell, weil aus dem Code erzeugt |
| Docker | `make prod` |

Einstellungen: Interpreter auf `backend/.venv/bin/python`, `backend` als Sources Root markieren.

## Sprachregelung

**Bezeichner und Code-Kommentare auf Englisch. Alles Menschenlesbare auf Deutsch.**

Der Grund ist nicht Konvention um ihrer selbst willen: `def zeitraum(...) -> DatePrecision` erzeugt
an jeder Grenze zwischen eigenem Code und einer Bibliothek einen Bruch. Und Coding-Agents wie
spätere Mitstreiter stolpern über gemischten Code messbar häufiger.

Deutsch bleibt für: Oberflächentexte (`frontend/src/text/de.ts`), Meldungen an Besucher und
Kuratoren, CLI-Ausgaben, Dokumentation, Commit-Nachrichten. Deutsche Beispiele in englischen
Kommentaren sind erwünscht, wo sie den Fall erklären.

**Für Meldungen gilt eine Faustregel:** *Kann sie im Kiosk oder im Admin-Bereich erscheinen? Dann
Deutsch, sonst Englisch.*

| Meldung | Wer sieht sie | Sprache |
|---|---|---|
| „Dieses Foto hat inzwischen schon eine Angabe bekommen." | Besucher am Kiosk | Deutsch |
| „Kein Foto mit der Nummer 42" | Besucher im Foto-Overlay | Deutsch |
| „Aufgenommen, es fehlt noch: Ort und Jahr" | Kurator im Import-Protokoll | Deutsch |
| `bbox is inverted: min must be smaller than max` | nur wer die API selbst aufruft | Englisch |
| `No thumbnail size 999; available sizes are [240, 1200]` | dito | Englisch |
| OpenAPI-`summary`/`description` unter `/api/docs` | Entwickler, neben `open_count` & Co. | Englisch |

Die CLI ist die Ausnahme von der Ausnahme: `python -m app.cli import` führt beim Erstbefüllen auch
das Museumsteam aus, deshalb bleiben ihre Ausgaben deutsch.

**Testdateien sind die Ausnahme und bleiben ganz deutsch** — Name, Docstring, Kommentar. Ein
Testname ist kein Bezeichner im üblichen Sinn, sondern ein Spezifikationssatz:
`test_scandatum_datiert_das_foto_nicht` sagt sofort, welche Zusage der Test schützt, und der
Docstring darunter trägt das Warum. Übersetzt verlöre das an Schärfe, und gerade diese Sätze sind
die wertvollste Dokumentation im Repo.

Umlaute werden in deutscher Prosa im Quelltext, in Shell-Skripten und in Commit-Nachrichten
umschrieben (`ue`, `oe`, `ae`, `ss`); in Texten für Menschen normal geschrieben. **Zitate und
Datenwerte behalten sie**: `"Mühlenweg"` als Beispiel in einem Kommentar, `["Gebäude"]` als
Einstellungswert, `"März"` in der Monatsliste — ohne Umlaut wären sie schlicht falsch.

Ob eine Datei sich daran hält, beantwortet `python tools/language_check.py`.

## Testen

```bash
make check         # alles: Stil, die vier Pruefungen, alle Tests -- das Ziel vor einem Commit
make test          # nur die Tests
make test-backend  # pytest
make test-frontend # Typecheck und vitest
make lint          # ruff
make docs-check    # nur die vier Pruefungen unten
```

**Vier Prüfungen laufen neben den Tests, weil sie Dateien lesen, die kein Test je sieht:**

```bash
python3 tools/language_check.py   # hält sich der Quelltext an die Sprachregelung?
python3 tools/check_anchors.py    # zeigen die Verweise in docs/ noch irgendwohin?
                                  #   (auch zwischen Dateien, seit dem 15. August 2026)
python3 tools/check_settings.py   # erreicht jede Einstellung den Container?
python3 tools/check_numbers.py    # stimmt die Buchführung des Backlogs über seine Nummern?
```

Sie brauchen weder `venv` noch `node_modules` — reine Leser, `python3` aus dem System genügt.

**Und sie hängen im Git-Hook**, weil „von Hand" in der Praxis „gar nicht" hiess. `.githooks/pre-commit`
führt genau diese vier aus, **nicht** die Testreihe: Die läuft ohnehin, vergessen wurden diese vier,
und zusammen brauchen sie unter einer Sekunde. Einzuschalten ist er einmal je Klon, umgehen lässt
er sich mit `--no-verify`:

```bash
git config core.hooksPath .githooks
```

Die dritte gibt es seit dem 14. August 2026, und sie hat einen Anlass: Die Compose-Datei reichte
nur vier von acht Einstellungen durch, die übrigen fielen im Container still auf ihre Vorgabe
zurück. Ein Import verlor dadurch Schlagwort, Bildnachweis und Herkunft — **ohne Fehlermeldung,
und mit 393 grünen Tests daneben**, denn eine Compose-Datei wird von keinem Test angefasst. Sie
prüft auch die Gegenrichtung: ein Name in `docker-compose.yml` oder `deploy/.env.example`, den es
in `config.py` nicht gibt, wirkt folgenlos und fällt sonst niemandem auf.

Die vierte kam am 19. August 2026 dazu und hat ebenfalls einen: Ein Punkt, der in die Historie
zieht, verlangt vier Bearbeitungen an drei Stellen — Tabellenzeile weg, Abschnitt weg, Nummer in
die Liste der vergriffenen, Zahlwort davor erhöhen. An einem Tag ist das viermal passiert. Sie
prüft die Zusage nach, die der Backlog über sich selbst macht: Jede je vergebene Nummer ist
entweder offen oder vergriffen — keine Lücke, kein Überhang, keine zweimal. **Was sie ausdrücklich
nicht tut, ist Zahlen im Fliesstext nachzählen**; warum das falsch wäre, steht in
[decisions.md](decisions.md), Punkt 59.

**Was getestet wird.** Nicht Abdeckung um der Zahl willen, sondern die Stellen, an denen ein Fehler
*still* passiert. Die drei wichtigsten Testklassen im Projekt:

- `test_dates.py::TestUeberlappung` — ein auf „1920er" datiertes Foto muss bei der Auswahl
  1925–1930 erscheinen. Bei naiver Datumsabfrage fällt es lautlos heraus.
- `test_importer.py::TestDatumAusExif` — das EXIF-Datum eines Scans darf das Foto nicht datieren.
- `test_foldermeta.py` — was der Ordnername sagt, und wo er nicht geraten werden darf. Aus
  „10 H Brahms" darf keine Hausnummer 10h werden, aus dem Ordner „2" keine Straße „Kolonie
  Autal 2", und eine Straße ohne Hausnummer darf nicht mittig verortet werden.
- `test_watcher.py` — eine halb kopierte Datei darf nicht importiert werden.

Alle beschreiben Fehler, die im Museum aufgefallen wären, nicht in der Entwicklung — und drei
davon sind beim echten Erstimport tatsächlich aufgetreten, bevor sie Test wurden.

**Im Frontend folgt daraus, dass keine Komponente einen Test hat** — und das ist kein Rückstand,
sondern die Regel: *Jede Entscheidung wandert in eine reine Funktion und bekommt dort ihren Test,
das Rendern bekommt keinen.* Wo die Funktion wohnt, ist gleichgültig; `PhotoLayer.test.ts` prüft
`buildIndex` aus einer `.tsx`-Datei, ohne etwas zu rendern.

Der Grund ist derselbe wie oben: Eine falsch gezeichnete Schaltfläche sieht falsch aus, dafür
braucht es einen Blick und keinen Test. Ein falsch gerundetes Jahr sieht nach nichts aus — die
Karte zeigt einfach etwas anderes. Beim Bauen heisst das: Sobald in einer Komponente gerechnet,
sortiert oder entschieden wird, gehört das in ein Modul daneben. Kein jsdom, keine Testing
Library; warum, steht in [decisions.md](decisions.md), Punkt 60.

**Der Offline-Test ist die wichtigste Prüfung des Projekts** und lässt sich nicht automatisieren:
Netz trennen, Karte bewegen, Fotos öffnen, einen Beitrag abgeben — und danach in den DevTools
nachsehen, dass keine Anfrage an eine fremde Herkunft gegangen ist.

```js
performance.getEntriesByType('resource')
  .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length  // 0
```

**Fixtures.** `make_photo` erzeugt Datenbankzeilen ohne Dateien (schnell, für Abfragetests),
`sample_image` kopiert ein echtes Testbild (für die Import-Pipeline). Die Testbilder in
`backend/tests/fixtures/` decken bewusst die schwierigen Fälle ab: Scan ohne EXIF, Scan mit
Scandatum von 2019, hochkant über EXIF-Orientierung, CMYK-TIFF, Datei ohne Bild. Neu erzeugen mit
`python tests/fixtures/build_test_images.py`.

Jeder Test bekommt über die `settings`-Fixture ein eigenes temporäres Datenverzeichnis. Niemals im
Test auf `data/` zugreifen.

## Datenbank

SQLite mit WAL-Journal. Schemaänderungen laufen über Alembic:

```bash
make revision m="Beschreibung"   # Migration aus den Modellen erzeugen
make migrate                     # anwenden
```

Migrationen laufen beim Containerstart automatisch (`backend/docker-entrypoint.sh`) — auf dem Pi
soll niemand daran denken müssen. Die erzeugte Migration immer durchlesen: SQLite kann Spalten
nicht ändern, Alembic baut die Tabelle dann neu (`render_as_batch`), und dabei gehen Details
verloren, wenn man nicht hinsieht.

> **Der Verlauf fängt bei einem Anfangsschema an, und das bleibt so.** Am 3. August 2026 wurden
> die drei vorhandenen Revisionen zusammengelegt, weil noch kein Gerät im Feld war. **Ab dem
> ersten Pi ist das nicht mehr erlaubt** — dann ist die Kette der Migrationen der einzige Weg, auf
> dem die Daten eines Museums eine Schemaänderung überleben. Siehe [decisions.md](decisions.md),
> Punkt 17.

Was beim Neubau einer Tabelle schiefgehen kann, ist einmal schiefgegangen und kostete alle
Besucherbeiträge: `app/db.py` schaltet `PRAGMA foreign_keys=ON` für *jede* Engine des Prozesses
ein, auch für die von Alembic, und der Neubau löscht das Original. `alembic/env.py` schaltet die
Prüfung deshalb für die Dauer einer Migration ab. `tests/test_migrations.py` bewacht das — wer
dort etwas ändert, sollte die Gegenprobe machen: mit `foreign_keys=ON` muss der Test rot sein.

## Beispielbestand

```bash
make seed        # Bestand aus seed/ herstellen — loescht den vorhandenen!
make seed-save   # den laufenden Bestand nach seed/ sichern
make empty       # alles loeschen, ohne Ersatz — der Schritt vor einem Erstimport
```

Sechzehn echte Aufnahmen aus Holm, bewusst lückenhaft: Fotos ohne Jahr, ohne Ort, gestaffelte
Textlängen, gelöschte Fotos, Besucherbeiträge samt einem zurückgenommenen. Ohne diese Lücken prüft
der Bestand die Hälfte des Programms nicht — der „Hilf mit"-Bereich hätte nichts vorzulegen.

**Alles in diesem Bestand ist erfunden** — gezeichnete Bilder, ausgedachte Menschen, erzeugt
von [../tools/build_seed.py](../tools/build_seed.py). Echt sind nur Straßennamen und
Koordinaten, und das muss so sein: Ohne sie zeigt die Karte nichts und die Ortssuche findet
nichts. Die echten Aufnahmen gehören dem Museum und liegen nicht im Repo. Alles Weitere in
[../seed/README.md](../seed/README.md).

## Einen Archivstand aufnehmen

Wenn das Museum einen neuen Stand schickt, stehen zwei Schritte vor dem Import — und beide sind
einmal übersprungen worden, mit Folgen.

**Erstens: alles wird JPEG.**

```bash
python3 tools/to_jpeg.py "~/Museum/Neuer Stand" "~/Museum/Neuer Stand zwecks Import/Straßen"
```

Der Baum wird kopiert, die Quelle bleibt unangetastet. TIFF, PNG und WEBP werden umgewandelt, JPEG
durchgereicht. **Die Einstellung darin ist gemessen und wird nicht nachjustiert** — warum, steht in
[decisions.md](decisions.md), Punkt 46. Der Zielordner heißt `Straßen`, damit die Herkunft dieselbe
Form bekommt wie beim Erstbestand (`KIEKMAP_IMPORT_PROVENANCE` setzt den Vorsatz davor).

**Zweitens: nachzählen, was wirklich neu ist.** Auch ein Stand, der als Differenz geliefert wurde,
enthält Bilder, die längst im Bestand stehen — der Vergleich lief über Bytes, und die ändern sich
schon, wenn jemand die Metadaten neu schreibt. Am 16. August 2026 waren das **223 von 619 Dateien**.
[decisions.md](decisions.md), Punkt 47, beschreibt den Weg: erst pixelgenau bei gleichen
Kantenlängen, dann grob über verkleinerte Graustufenbilder.

Erst danach `python -m app.cli import <ordner>`. Vorher eine Kopie von `data/` ziehen, **mit den
`-wal`- und `-shm`-Dateien** — ohne sie ist die Kopie auf dem Stand des letzten Checkpoints.

## Aufbau

```
backend/app/
  api/        Endpunkte. Dünn: Parameter prüfen, Service rufen, Schema zurückgeben.
  services/   Fachlogik ohne HTTP-Bezug. Hier gehört das Denken hin, hier testet es sich leicht.
  models.py   SQLAlchemy-Tabellen
  schemas.py  Pydantic-Formen der API
  config.py   Alle Pfade hängen an data_dir
frontend/src/
  kiosk/      Besucheransicht
  admin/      Admin-Bereich
  store/      Zustand-Stores, einer je Bereich
  api/        Backend-Zugriff; die Typen spiegeln backend/app/schemas.py
  texte/      Oberflächentexte
seed/         Beispielbestand: Bilddateien und seed.json
```

**Faustregel:** Wenn sich etwas ohne HTTP testen lässt, gehört es nach `services/`.

Das ist die Ordnerliste. Wie die Teile zusammenspielen — welche Daten wann wohin fließen, was zur
Bauzeit entsteht und was zur Laufzeit —, steht in [architecture.md](architecture.md).

## Am laufenden System prüfen

Erfahrungen aus den letzten Umbauten, damit sie nicht zweimal gemacht werden müssen:

- **Die Admin-PIN ist lokal 4711**, und in die Verwaltung führt ein Klick auf das Wappen
  (`.admin-gate`). Eine eigene PIN erzeugt `python -m app.cli pin`.
- **Ein Klick auf die Karte setzt bei laufender Ortsfrage einen Pin.** Zum Zoomen deshalb die
  Bedienelemente oder das Mausrad nehmen — sonst legt man beim Prüfen versehentlich einen
  Besucherbeitrag an, den nachher jemand in der Moderation zurücknehmen muss.
- Für den Import einen Prüfstick anlegen statt einen echten zu suchen:
  ```bash
  hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK teststick.dmg && hdiutil attach teststick.dmg
  ```
  Dazu `KIEKMAP_MEDIA_DIR=/Volumes` in `backend/.env` — steht dort schon.

Wer die Ansicht über einen Browser fernsteuert (Coding-Agents tun das):

- Dienste über die Vorschau-Werkzeuge starten (`backend`, `frontend` aus `.claude/launch.json`),
  nicht über die Shell.
- Der Screenshot-Kompositor zeichnet nach einer Navigation oft verkleinert. Ein Setzen der
  Fenstergröße erzwingt einen sauberen Neuaufbau.
- Zustand geht zwischen zwei Aufrufen der JavaScript-Konsole verloren. Einen Ablauf deshalb **in
  einem** Aufruf durchspielen — anmelden, klicken, messen.

## Was leicht schiefgeht

Fallstricke, die Zeit gekostet haben und im Code kommentiert sind:

- **Sprite-URL muss absolut sein** — MapLibre lehnt relative Pfade ab, Glyphen aber nicht.
- **SQLite: `+` ist Addition, nicht Verkettung.** `substr(x,1,3) + '0'` ergibt 193, nicht „1930".
- **SQLAlchemy: `/` ist echte Division.** `1932/10` ist 193.2; ohne Cast wird daraus wieder 1932.
- **Zeigerereignisse kommen schneller als React rendert.** Der gezogene Slider-Griff steht deshalb
  in einem Ref, nicht nur im State — sonst bleibt er bei einer zügigen Wischbewegung kleben.
- **Docker-Bind-Mounts zeigen keine später eingehängten Datenträger** ohne `rshared`-Propagation.
  Betrifft die USB-Sicherung in Stufe 9.
- **Overpass lehnt den Standard-User-Agent von `urllib` ab** (HTTP 406).

## Für einen anderen Ort

Nichts Ortsspezifisches steht im Code — der Ausschnitt kommt zur Laufzeit aus `tiles/region.json`,
Kartendatei und Ortsindex sind gebaute Artefakte. Ein zweites Museum braucht deshalb keinen Fork,
sondern eine eigene `region.json` und `.env`.

Diese Eigenschaft ist leicht zu zerstören: Wer eine Koordinate, einen Ortsnamen oder eine
sammlungsabhängige Zahl in den Code schreiben möchte, gehört sie stattdessen in die Konfiguration.
Testdaten sind ausgenommen.

Das vollständige Vorgehen — Bounding Box ausrechnen, Zoomstufen bestimmen, Kacheln und Ortsindex
bauen, prüfen — steht in [adaption.md](adaption.md). Dort auch, was eine zweite Sprache kosten
würde und ab wann sich Modularisierung lohnt.

## Veröffentlichen

SemVer-Tags, Conventional Commits, ein gemeinsames Repo für Front- und Backend. Frontend und
Backend werden zusammen versioniert — bei einem Ein-Geräte-System ist getrennte Versionierung nur
Ballast, und die API-Kompatibilität ist dadurch garantiert.

Das Museumsgerät ist offline. Der Updateweg dorthin (Image-Tarball auf einen USB-Stick) steht in
[operations.md](operations.md).
