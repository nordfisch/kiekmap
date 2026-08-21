# Hinweise für Coding-Agents

Kiekmap ist ein Touchscreen-Kiosk für ein Heimatmuseum in **Holm** (Kreis Pinneberg): historische
Ortsfotos auf einer Karte, filterbar über einen Zeitraum-Schieber, plus ein „Hilf mit"-Bereich, in
dem Besucher fehlende Angaben ergänzen. Das Gerät läuft **offline** auf einem Raspberry Pi.

Lies zuerst [docs/decisions.md](docs/decisions.md) — dort steht, *warum* die Dinge so sind; und
[docs/architecture.md](docs/architecture.md) — dort, *woraus* das System besteht und wie die Teile
zusammenspielen. Diese Datei sagt, *wie* man hier arbeitet. Welche Datei sonst welche Frage
beantwortet, steht in [docs/index.md](docs/index.md).

## Die drei Dinge, die man hier falsch machen kann

Wer diese drei nicht kennt, baut etwas, das erst im Museum auffällt:

1. **Historische Fotos sind Scans.** Ihr EXIF trägt das Datum des Scans, nicht der Aufnahme. Ein
   EXIF-Datum ab `exif_date_max_year` (1990) darf ein Foto deshalb **nicht** datieren — sonst läge
   es auf der Zeitleiste bei 2019 und gälte als datiert, würde also nie zur Korrektur vorgelegt.
   Siehe `backend/app/services/exif.py`.

   **Eine EXIF-Koordinate ist deshalb aber nicht automatisch falsch — und nicht automatisch
   gemessen.** 413 Fotos des Erstbestands trugen eine, und 278 davon teilten sie sich mit einem
   anderen Foto: eingetragene Werte, keine Messungen. Wer eine Koordinate aus einer Datei gegen
   eine andere Quelle abwägen will, zählt erst nach, ob sie sich wiederholt. Siehe
   `docs/decisions.md`, Punkt 34.

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

**Faustregel für Meldungen:** *Kann sie im Kiosk oder im Admin-Bereich erscheinen? Dann Deutsch,
sonst Englisch.* Das entscheidet alle Grenzfälle. Die CLI ist die Ausnahme — sie führt beim
Erstbefüllen auch das Museumsteam aus.

**Testdateien sind vollständig deutsch**, Name und Docstring und Kommentar. Ein Testname ist kein
Bezeichner, sondern ein Spezifikationssatz: `test_scandatum_datiert_das_foto_nicht` sagt sofort,
welche Zusage der Test schützt. Klassennamen ebenso (`class TestUeberlappung`).

**Umlaute:** in Texten für Menschen normal (Mühlenweg); in deutscher Prosa **im Quelltext**, in
Shell-Skripten und in Commit-Nachrichten umschrieben (`ue`, `oe`, `ae`, `ss`). Daraus folgt eine
Schreibgewohnheit für deutsche Meldungen im Code: **so formulieren, dass sie ohne Umlaut
auskommen** — nicht „Sie koennen den Stick abziehen", sondern „Der Stick kann abgezogen werden".

**Zitate und Datenwerte behalten ihre Umlaute** — `"Mühlenweg"` als Beispiel in einem englischen
Kommentar, `["Gebäude"]` als Einstellungswert, `"März"` in `services/dates.py`. Das ist keine
Prosa, sondern der Gegenstand, über den der Text spricht; ohne Umlaut wäre es schlicht falsch.
`ß` darf zu `ss` werden, die drei Umlaute nicht.

**`tiles/` gilt mit**, und `tools/` auch. Beide laufen nur auf dem Entwicklungsrechner, sind aber
gewöhnlicher Quelltext dieses Repos.

Warum die Regel so lautet und wo ihre Grenzfälle liegen, steht ausführlich in
[docs/development.md](docs/development.md). Ob eine Datei sich daran hält, beantwortet
`python3 tools/language_check.py`.

## Aufbau

Der Verzeichnisbaum steht in [docs/architecture.md](docs/architecture.md); hier nur, was man ihm
nicht ansieht:

- **`backend/app/services/` ist der Ort für Fachlogik ohne HTTP-Bezug** — dort gehört das Denken
  hin. `app/api/` prüft Parameter, ruft einen Dienst, gibt ein Schema zurück, und bleibt dünn.
- **`frontend/src/api/` spiegelt `app/schemas.py`.** Wer dort ein Feld ändert, ändert es hier mit.
- **`tiles/` läuft auf dem Entwicklungsrechner, nie auf dem Pi.** Karte und Ortsindex sind gebaute
  Artefakte und liegen nicht im Repo.
- **`data/` ist Laufzeitdaten** und wird nie versioniert; `seed/` ist der erfundene
  Beispielbestand für Entwicklung und Test.

## Kommandos

```bash
make dev          # Backend (8000) und Frontend (5173) mit Hot Reload
make check        # alles vor einem Commit: Stil, die vier Prüfungen, alle Tests
make test         # nur die Tests -- pytest und vitest
make lint         # ruff check und format --check
make docs-check   # nur die vier Prüfungen
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
passieren würden. **Vor jedem Commit `make check`.**

**Vier Prüfungen laufen neben den Tests**, weil sie Dateien lesen, die kein Test je sieht:
`tools/language_check.py` (Sprachregelung), `tools/check_anchors.py` (Verweise in `docs/`),
`tools/check_settings.py` (erreicht jede Einstellung den Container?) und
`tools/check_numbers.py` (stimmt die Buchführung des Backlogs über seine Nummern?). Alle vier
mit `python3`, ohne venv; `make check` und der Hook unter `.githooks/` führen sie aus. Näheres
in [docs/development.md](docs/development.md).

**Kommentare** erklären das *Warum*, nicht das *Was*. Ein Kommentar, der nur wiederholt, was der
Code sagt, wird gelöscht. Ein Kommentar, der einen Fallstrick benennt, ist Gold — davon gibt es
hier einige (`rshared`-Mount, Sprite-URL muss absolut sein, SQLite `+` ist Addition).

**Ein erledigter Punkt wird an drei Stellen vermerkt, nicht an neun:** was das Programm jetzt
kann, in den [CHANGELOG](CHANGELOG.md); wie es dazu kam, ans Ende von
[docs/history.md](docs/history.md); der Punkt selbst raus aus
[docs/backlog.md](docs/backlog.md), seine Nummer in die Vergriffen-Liste. Kam dabei eine
Entscheidung heraus, kommt sie als neuer Punkt nach [docs/decisions.md](docs/decisions.md), mit
Begründung. **Diese Datei hier gehört nicht dazu** — sie sagt, wie man arbeitet, nicht was
geschehen ist.

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

**Namen aus dem Bestand sind davon ausgenommen: Beispiele sind erfunden.** Koordinaten, Straßen
und Hausnummern ja — Familien-, Hof- und Firmennamen nein, weder im Test noch im Kommentar noch in
der Doku. Der Beispielbestand hat dafür einen Kader, und er reicht: **Gasthof Petersen**,
**Hof Sieveking**, **Familie Wendt**, **Familie Boysen**, **A. Brahms**, dazu **Timm**, **Möller**,
**Harms** und **Ohlsen**. Was ein Beispiel zeigen soll, zeigt ein erfundener Name genauso — dass
eine Jahreszahl neben einem Namen der Archivstand ist und kein Aufnahmedatum, hängt nicht am Namen.
Der Bestand steht in `data/` und geht nie ins Repo; seine Menschen auch nicht.

Vorgehen beim Adaptieren steht in [docs/adaption.md](docs/adaption.md); dort auch, was eine zweite
Sprache kosten würde und ab wann sich Modularisierung lohnt.

## Was man nicht anfassen soll

- **`data/`** — Laufzeitdaten. Nie ins Repo, nie im Test darauf zugreifen (Tests bekommen über die
  `settings`-Fixture ein temporäres Verzeichnis).
- **Dateinamen der Fotos** sind der SHA-256 ihres Inhalts. Daran hängen Dublettenerkennung,
  Cache-Header und die inkrementelle Sicherung.
- **`frontend/public/tiles/`** und **`frontend/public/basemaps/`** — erzeugt von `make tiles`.
- **Die Qualitätseinstellung in `tools/to_jpeg.py`** — sie ist am Erstbestand gemessen, nicht
  gewählt. Zwei Läufe über dieselbe Datei müssen denselben SHA-256 ergeben; nachjustiert kommt
  beim nächsten Archivstand jedes vorhandene Bild ein zweites Mal herein.
- **Die Lücken im Beispielbestand** (`seed/`) — Fotos ohne Jahr, ohne Ort, zwei nur straßengenaue,
  ein zurückgenommener Besucherbeitrag. Sie sind Absicht: Ohne sie hat der „Hilf mit"-Bereich
  nichts vorzulegen und ein Drittel des Programms wird nie geprüft. `tools/build_seed.py` zählt
  sie nach jedem Lauf und **bricht ab, wenn eine fehlt** — wer eine neue Frage baut, gibt ihr
  dort ihren Vorrat.

## Stand

Was gebaut ist, sagt das [Änderungsprotokoll](CHANGELOG.md); wie es dazu kam und was dabei anders
lief als geplant, [docs/history.md](docs/history.md); was offen ist,
[docs/backlog.md](docs/backlog.md). Hier steht nur, was man beim Arbeiten **falsch annehmen
würde**, wenn es nicht dastünde.

**Stufe 0 bis 10 ist fertig** und im Museum im Einsatz — Backend, Karte, Zeitschieber, „Hilf mit",
Verwaltung, Sicherung, Kiosk-Betrieb. Der Erstbestand ist eingelesen, bereinigt und durchgesehen.

**Aber: Alles unter `deploy/pi/` ist ungeprüft.** Es wurde ohne Gerät gebaut; die Syntax stimmt,
gelaufen ist nichts. Der erste Pi ist zugleich die Abnahme. Ungeprüft sind aus demselben Grund der
**USB-Weg der Sicherung** und das Verhalten nach **Neustart und Stromausfall** — beides ist auf
einem Mac nicht zu prüfen. Die Container dagegen sind geprüft, wenn auch nur dort.

**Sicherungen von vor dem 15. August 2026 werden nicht erkannt.** Der Projektname steckt im
Ordner- und Archivnamen, und das Projekt hiess vorher anders.

**Zum Entwickeln auf dem Mac** `KIEKMAP_MEDIA_DIR=/Volumes` setzen und ein Prüfvolumen mit
`hdiutil` anlegen — siehe [docs/operations.md](docs/operations.md). Den Containerbetrieb fährt dort
`make prod-mac`.

**Der Verwaltungsbereich braucht eine PIN:** `cd backend && .venv/bin/python -m app.cli pin`
erzeugt die Zeile für die `.env`. Ohne sie sagt die Anmeldung das im Klartext, statt jede Eingabe
abzulehnen.

**Jeder Backlogpunkt trägt eine feste Nummer**, unter der er zitiert wird („Punkt 15"). **Nummern
werden nie neu vergeben** — erledigte und aufgelöste bleiben vergriffen, damit ein Zitat aus einer
alten Notiz nicht auf etwas anderes zeigt. `tools/check_numbers.py` rechnet das nach.

**Was kein Backlogpunkt mehr ist, sondern Kuratieren:** Fotos ohne Beschreibung, ohne Titel, ohne
Ort. Das schreibt, wer das Bild ansieht und den Ort kennt — kein Programm.
