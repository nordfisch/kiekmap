# Hinweise für Coding-Agents

Photomap ist ein Touchscreen-Kiosk für ein Heimatmuseum in **Holm** (Kreis Pinneberg): historische
Ortsfotos auf einer Karte, filterbar über einen Zeitraum-Schieber, plus ein „Hilf mit"-Bereich, in
dem Besucher fehlende Angaben ergänzen. Das Gerät läuft **offline** auf einem Raspberry Pi.

Lies zuerst [docs/decisions.md](docs/decisions.md) — dort steht, *warum* die Dinge so sind; und
[docs/architecture.md](docs/architecture.md) — dort, *woraus* das System besteht und wie die Teile
zusammenspielen. Diese Datei sagt, *wie* man hier arbeitet. Welche Datei sonst welche Frage
beantwortet, steht in [docs/index.md](docs/index.md).

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
| **Alles in einer Testdatei** — Namen, Docstrings, Kommentare | **Deutsch** |
| Oberflächentexte | Deutsch, in `frontend/src/text/de.ts` |
| Meldungen, die im Kiosk oder Admin-Bereich erscheinen können | Deutsch, direkt im Code |
| Meldungen, die nur beim Arbeiten gegen die API auftauchen | Englisch |
| API-Pfade, Query-Parameter, JSON-Felder, OpenAPI-Beschreibungen | Englisch |
| Ausgaben der CLI (`python -m app.cli …`) | Deutsch |
| Dokumentation (`docs/`, `README.md`, diese Datei) | Deutsch |
| Commit-Nachrichten | Deutsch |
| Werte in der Datenbank, die aus OSM stammen (`kind`: `strasse`, `flur` …) | Deutsch, wie geliefert |

**Faustregel für Meldungen:** *Kann diese Meldung im Kiosk oder im Admin-Bereich erscheinen? Dann
Deutsch, sonst Englisch.* Das entscheidet alle Grenzfälle ohne Einzelabwägung — ein 404 auf ein
gelöschtes Foto landet im Overlay des Besuchers (deutsch), eine kaputte `bbox` sieht nur, wer die
API selbst aufruft (englisch). Die CLI ist die Ausnahme: sie führt beim Erstbefüllen auch das
Museumsteam aus, nicht nur Entwickler.

**Testdateien sind die bewusste Ausnahme** von der Englisch-Regel, und zwar vollständig: Name,
Docstring und Kommentar. Ein Testname ist kein Bezeichner im üblichen Sinn, sondern ein
Spezifikationssatz — `test_scandatum_datiert_das_foto_nicht` sagt einem deutschsprachigen Leser
sofort, welche Zusage der Test schützt. Der Docstring darunter ist dessen Fortsetzung und trägt
das Warum („Das EXIF sagt 2019, das Foto ist historisch"). Beides zusammen ist die wertvollste
Dokumentation im Repo; englisch übersetzt verlöre sie an Schärfe. Klassennamen ebenso
(`class TestUeberlappung`).

Deutsche Beispiele in englischen Kommentaren sind erwünscht, wo sie den Fall erklären
(`so that "muhlenweg" finds the "Mühlenweg"`).

**Umlaute:** In deutschen Texten für Menschen normal schreiben (Mühlenweg). In deutscher Prosa
**im Quelltext** — Meldungen, Docstrings, Kommentare — sowie in Shell-Skripten und
Commit-Nachrichten werden sie umschrieben (`ue`, `oe`, `ae`, `ss`).

**Zitate und Datenwerte behalten ihre Umlaute.** `"Mühlenweg"` als Beispiel in einem englischen
Kommentar, `["Gebäude"]` als Einstellungswert, `"März"` in der Monatsliste von
`services/dates.py`: Das sind keine Prosa, sondern Gegenstände, über die der Text spricht. Ohne
Umlaut wären sie schlicht falsch — der Kiosk zeigte „Maerz".

Für deutsche Meldungen **im Python-Code, die auf dem Bildschirm landen können**, folgt daraus:
so formulieren, dass sie ohne Umlaut auskommen. Nicht „Sie koennen den Stick jetzt abziehen",
sondern „Der Stick kann jetzt abgezogen werden". Das ist bisher jedes Mal gelungen und liest sich
meist sogar besser, weil es zum Umformulieren zwingt.

Das `ss` ist die Ausnahme in der Ausnahme: „ausserhalb" ist gültiges Deutsch, „koennen" ist es
nicht. `ß` darf also ersetzt werden, die drei Umlaute nicht.

**`tiles/` gilt mit.** Die Bauskripte laufen zwar nur auf dem Entwicklungsrechner, sind aber
gewöhnlicher Quelltext dieses Repos — keine Fußnote, keine eigene Sprache.

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
seed/        Beispielbestand für Entwicklung und Test, Bilder noch nicht im Repo
```

## Kommandos

```bash
make dev          # Backend (8000) und Frontend (5173) mit Hot Reload
make test         # pytest und vitest
make lint         # ruff check und format --check
make tiles        # Offline-Karte, Schriften, Symbole für die Region
make places       # Ortsindex bauen und einlesen
make seed         # Beispielbestand aus seed/ herstellen (löscht den vorhandenen!)
make seed-save    # den laufenden Bestand nach seed/ sichern
make empty        # den ganzen Bestand löschen (fragt nach; vor einem Erstimport)
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
- **Die Lücken im Beispielbestand** (`seed/`) — Fotos ohne Jahr, ohne Ort, ein zurückgenommener
  Besucherbeitrag. Sie sind Absicht: Ohne sie hat der „Hilf mit"-Bereich nichts vorzulegen und
  ein Drittel des Programms wird nie geprüft.

## Stand

Fertig: Stufen 0–10 (Gerüst, Backend, Frontend, Import, Abfrage-API, Karte mit Markern,
Zeitschieber, „Hilf mit" mit Hausnummern, Sprachregelung, Admin-Bereich mit Stapel-Upload,
USB-Sicherung, Kiosk-Betrieb), dazu der Umbau des Verwaltungsmenüs, zwei Runden Nachbesserungen
an Verwaltung und Besucheransicht sowie die Auswertung von Metadaten und Ordnerstruktur beim
Import, mit der der Erstbestand von 929 Fotos eingelesen wurde. Was als Nächstes ansteht, steht im
Backlog.

**Alles unter `deploy/pi/` ist ungeprüft** — beim Bauen gab es kein Gerät. Syntax stimmt, gelaufen
ist nichts. Der erste Pi ist damit zugleich die Abnahme der Stufen 9 und 10; was zuerst hakt,
gehört nach [docs/operations.md](docs/operations.md).

Zum Entwickeln auf dem Mac `PHOTOMAP_MEDIA_DIR=/Volumes` setzen und ein Prüfvolumen mit `hdiutil`
anlegen — siehe ebenfalls [docs/operations.md](docs/operations.md).

Der Admin-Bereich braucht eine PIN: `cd backend && .venv/bin/python -m app.cli pin` erzeugt die
Zeile für die `.env`. Ohne sie sagt die Anmeldung das im Klartext, statt jede Eingabe abzulehnen.

**Was offen ist, steht in [docs/backlog.md](docs/backlog.md)** — 31 Punkte nach Verwaltung,
Besucher-Interface, Infrastruktur und Entwicklung geordnet, jeder mit dem, was beim Aufgreifen
sonst erst wieder herausgefunden werden müsste. Jeder trägt eine **feste Nummer**, unter der er
zitiert wird („Punkt 15"), dazu seine Art und seine Einordnung; die Übersichtstabelle oben in der
Datei sagt, was wirklich ansteht. **Nummern werden nie neu vergeben** — erledigte und aufgelöste
bleiben vergriffen, damit ein Zitat aus einer alten Notiz nicht auf etwas anderes zeigt. Wie das Vorhandene entstanden ist und was dabei anders kam
als geplant, steht in [docs/history.md](docs/history.md); was das Programm kann, im
Änderungsprotokoll [CHANGELOG.md](CHANGELOG.md).
