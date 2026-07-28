# Hinweise für Coding-Agents

Photomap ist ein Touchscreen-Kiosk für ein Heimatmuseum in **Holm** (Kreis Pinneberg): historische
Ortsfotos auf einer Karte, filterbar über einen Zeitraum-Schieber, plus ein „Hilf mit"-Bereich, in
dem Besucher fehlende Angaben ergänzen. Das Gerät läuft **offline** auf einem Raspberry Pi.

Lies zuerst [docs/decisions.md](docs/decisions.md) — dort steht, *warum* die Dinge so sind. Diese
Datei sagt, *wie* man hier arbeitet.

## Die drei Dinge, die man hier falsch machen kann

Wer diese drei nicht kennt, baut etwas, das erst im Museum auffällt:

1. **Historische Fotos sind Scans.** Ihr EXIF trägt das Datum des Scans, nicht der Aufnahme, und
   nie GPS. Ein EXIF-Datum ab `exif_date_max_year` (1990) darf ein Foto deshalb **nicht** datieren
   — sonst läge es auf der Zeitleiste bei 2019 und gälte als datiert, würde also nie zur Korrektur
   vorgelegt. Siehe `backend/app/services/exif.py`.

2. **Datierungen sind Intervalle, keine Zeitpunkte.** „1920er" ist der Normalfall. Der Zeitfilter
   fragt auf **Überlappung** ab (`date_from <= bis AND date_to >= von`), nicht auf Enthaltensein.
   Bei der naheliegenden Abfrage verschwindet der Großteil des Bestands lautlos aus der Ansicht.
   Siehe `backend/app/services/dates.py` und `tests/test_dates.py`.

3. **Offline heißt wirklich offline.** Kein CDN, keine Schriftart aus dem Netz, keine externe API
   zur Laufzeit. Der Protomaps-Kartenstil verweist standardmäßig auf `protomaps.github.io` — die
   Schriften und Symbole liegen deshalb unter `frontend/public/basemaps/`. Prüfung: die Seite darf
   **null** Anfragen an eine fremde Herkunft absetzen.

## Sprachregelung

| Was | Sprache |
|---|---|
| Bezeichner (Variablen, Funktionen, Klassen, CSS-Klassen, Dateinamen) | **Englisch** |
| Code-Kommentare und Docstrings | **Englisch** |
| **Testnamen** (`def test_…`, `class Test…`, `it("…")`) | **Deutsch** |
| Oberflächentexte | Deutsch, in `frontend/src/texte/de.ts` |
| Fehlermeldungen, die Besucher oder Kuratoren lesen | Deutsch, direkt im Code |
| API-Pfade und JSON-Felder | Englisch |
| Dokumentation (`docs/`, `README.md`, diese Datei) | Deutsch |
| Commit-Nachrichten | Deutsch |
| Werte in der Datenbank, die aus OSM stammen (`kind`: `strasse`, `flur` …) | Deutsch, wie geliefert |

**Testnamen sind die bewusste Ausnahme** von der Englisch-Regel. Sie sind keine Bezeichner im
üblichen Sinn, sondern Spezifikationssätze: `test_scandatum_datiert_das_foto_nicht` sagt einem
deutschsprachigen Leser sofort, welche Zusage der Test schützt. Das ist hier die wertvollste
Dokumentation im Repo — englisch übersetzt verlöre sie an Schärfe. Klassennamen ebenso
(`class TestUeberlappung`).

Deutsche Beispiele in englischen Kommentaren sind erwünscht, wo sie den Fall erklären
(`so that "muhlenweg" finds the "Mühlenweg"`).

**Umlaute:** In deutschen Texten für Menschen normal schreiben (Mühlenweg). In Python-Quelltext,
Shell-Skripten und Commit-Nachrichten werden sie umschrieben (`ue`, `oe`, `ae`, `ss`).

## Aufbau

```
backend/     FastAPI + SQLite. Fotos, Metadaten, Import, API.
  app/api/       Endpunkte, ein Modul je Themenbereich
  app/services/  Fachlogik ohne HTTP-Bezug -- hier gehört das Denken hin
  app/models.py  SQLAlchemy-Tabellen
  app/schemas.py Pydantic-Formen der API
frontend/    React + Vite + MapLibre
  src/kiosk/     Besucheransicht
  src/admin/     Admin-Bereich (ab Stufe 8)
  src/store/     Zustand-Stores
  src/api/       Backend-Zugriff, Typen spiegeln app/schemas.py
tiles/       Skripte, die Offline-Karte und Ortsindex bauen (laufen auf dem Mac, nicht dem Pi)
deploy/      Docker Compose und die Einrichtung des Pi
data/        Laufzeitdaten, nicht im Repo
```

## Kommandos

```bash
make dev          # Backend (8000) und Frontend (5173) mit Hot Reload
make test         # pytest und vitest
make lint         # ruff check und format --check
make tiles        # Offline-Karte, Schriften, Symbole für die Region
make places       # Ortsindex bauen und einlesen
make prod         # alles in Containern, wie auf dem Pi
```

`make` ohne Ziel zeigt alle. Backend-Tests einzeln: `cd backend && .venv/bin/pytest -q`.

## Arbeitsweise

**Tests.** Jede fachliche Entscheidung bekommt einen Test, der den *Fehlerfall* beschreibt, nicht
nur den Erfolgsfall. Die wertvollsten Tests hier heißen `test_jahrzehnt_erscheint_bei_auswahl_
mittendrin` und `test_scandatum_datiert_das_foto_nicht` — beide decken Fehler ab, die still
passieren würden. Vor jedem Commit `make lint && make test`.

**Kommentare** erklären das *Warum*, nicht das *Was*. Ein Kommentar, der nur wiederholt, was der
Code sagt, wird gelöscht. Ein Kommentar, der einen Fallstrick benennt, ist Gold — davon gibt es
hier einige (`rshared`-Mount, Sprite-URL muss absolut sein, SQLite `+` ist Addition).

**Neue Entscheidungen** kommen nach `docs/decisions.md`, unten angehängt, mit Begründung.

**Zielgruppe im Blick behalten.** Besucher stehen vor einem Touchscreen, oft ältere Menschen.
Bedienelemente mindestens 48 px. Der Admin-Bereich wird ein- bis zweimal im Jahr von
Ehrenamtlichen benutzt — dort zählt Klartext mehr als Kompaktheit.

## Nichts Ortsspezifisches gehört in den Code

Der Ausschnitt kommt zur Laufzeit aus `tiles/region.json`, die Kartendatei und der Ortsindex sind
gebaute Artefakte. Deshalb braucht ein zweites Museum **keinen Fork**, sondern nur eine eigene
`region.json` und `.env`.

Diese Eigenschaft ist leicht zu zerstören und schwer zurückzugewinnen. Wer beim Arbeiten eine
Koordinate, einen Ortsnamen oder eine sammlungsabhängige Zahl in den Code schreiben will, gehört
sie stattdessen nach `region.json` oder in die Einstellungen. Testdaten sind ausgenommen — dort
sind Holmer Koordinaten erwünscht, weil sie den Fall konkret machen.

Vorgehen beim Adaptieren steht in [docs/adaption.md](docs/adaption.md); dort auch, was eine zweite
Sprache kosten würde und ab wann sich Modularisierung lohnt.

## Was man nicht anfassen soll

- **`data/`** — Laufzeitdaten. Nie ins Repo, nie im Test darauf zugreifen (Tests bekommen über die
  `settings`-Fixture ein temporäres Verzeichnis).
- **Dateinamen der Fotos** sind der SHA-256 ihres Inhalts. Daran hängen Dublettenerkennung,
  Cache-Header und die inkrementelle Sicherung.
- **`frontend/public/tiles/`** und **`frontend/public/basemaps/`** — erzeugt von `make tiles`.

## Stand

Fertig: Stufen 0–7 (Gerüst, Backend, Frontend, Import, Abfrage-API, Karte mit Markern,
Zeitschieber, „Hilf mit"). Offen: Admin-Bereich mit Stapel-Upload (8), USB-Sicherung (9),
Kiosk-Deployment auf dem Pi (10). Details im Änderungsprotokoll [CHANGELOG.md](CHANGELOG.md).
