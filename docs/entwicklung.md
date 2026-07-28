# Entwicklung

Für Menschen, die an Photomap arbeiten. Warum die Dinge so sind, steht in
[decisions.md](decisions.md); was noch kommt, im [Stufenplan](stufenplan.md); wie man hier
arbeitet, hier.

## Einrichtung

Voraussetzungen: Python 3.12+, Node 18+ (empfohlen 22), Git. Optional Docker für den
Realitätscheck, `pmtiles` (via Homebrew) für den Kartenbau.

```bash
git clone <repo> && cd photomap
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
| Database-Tool | DB Browser for SQLite, oder `sqlite3 data/photomap.db` |
| HTTP-Client | `/api/docs` — interaktiv und immer aktuell, weil aus dem Code erzeugt |
| Docker | `make prod` |

Einstellungen: Interpreter auf `backend/.venv/bin/python`, `backend` als Sources Root markieren.

## Sprachregelung

**Bezeichner und Code-Kommentare auf Englisch. Alles Menschenlesbare auf Deutsch.**

Der Grund ist nicht Konvention um ihrer selbst willen: `def zeitraum(...) -> DatePrecision` erzeugt
an jeder Grenze zwischen eigenem Code und einer Bibliothek einen Bruch. Und Coding-Agents wie
spätere Mitstreiter stolpern über gemischten Code messbar häufiger.

Deutsch bleibt für: Oberflächentexte (`frontend/src/texte/de.ts`), Fehlermeldungen an Besucher und
Kuratoren, Dokumentation, Commit-Nachrichten. Deutsche Beispiele in englischen Kommentaren sind
erwünscht, wo sie den Fall erklären.

**Testnamen sind die Ausnahme und bleiben deutsch.** Sie sind keine Bezeichner im üblichen Sinn,
sondern Spezifikationssätze — `test_scandatum_datiert_das_foto_nicht` sagt sofort, welche Zusage
der Test schützt. Übersetzt verlöre das an Schärfe, und gerade diese Sätze sind die wertvollste
Dokumentation im Repo.

Umlaute werden in Python-Quelltext, Shell-Skripten und Commit-Nachrichten umschrieben
(`ue`, `oe`, `ae`, `ss`); in Texten für Menschen normal geschrieben.

## Testen

```bash
make test          # alles
make test-backend  # pytest
make test-frontend # Typecheck und vitest
make lint          # ruff
```

**Was getestet wird.** Nicht Abdeckung um der Zahl willen, sondern die Stellen, an denen ein Fehler
*still* passiert. Die drei wichtigsten Testklassen im Projekt:

- `test_dates.py::TestUeberlappung` — ein auf „1920er" datiertes Foto muss bei der Auswahl
  1925–1930 erscheinen. Bei naiver Datumsabfrage fällt es lautlos heraus.
- `test_importer.py::TestDatumAusExif` — das EXIF-Datum eines Scans darf das Foto nicht datieren.
- `test_watcher.py` — eine halb kopierte Datei darf nicht importiert werden.

Alle drei beschreiben Fehler, die im Museum aufgefallen wären, nicht in der Entwicklung.

**Fixtures.** `make_photo` erzeugt Datenbankzeilen ohne Dateien (schnell, für Abfragetests),
`sample_image` kopiert ein echtes Testbild (für die Import-Pipeline). Die Testbilder in
`backend/tests/fixtures/` decken bewusst die schwierigen Fälle ab: Scan ohne EXIF, Scan mit
Scandatum von 2019, hochkant über EXIF-Orientierung, CMYK-TIFF, Datei ohne Bild. Neu erzeugen mit
`python tests/fixtures/erzeuge_testbilder.py`.

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
```

**Faustregel:** Wenn sich etwas ohne HTTP testen lässt, gehört es nach `services/`.

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
[betrieb.md](betrieb.md).
