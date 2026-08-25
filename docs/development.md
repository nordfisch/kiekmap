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

## Beispiele sind erfunden

Holmer **Koordinaten, Straßen und Hausnummern** gehören in Testdaten und Kommentare — sie
machen den Fall konkret. Holmer **Namen** nicht: keine Familien, keine Höfe, keine Firmen,
weder im Test noch im Kommentar noch in der Dokumentation.

Der Beispielbestand stellt den Kader, und er reicht für alles: **Gasthof Petersen**,
**Hof Sieveking**, **Familie Wendt**, **Familie Boysen**, **A. Brahms**, dazu **Timm**,
**Möller**, **Harms** und **Ohlsen**. Wer einen weiteren braucht, erfindet ihn und trägt ihn
hier ein.

**Der Grund ist nicht Vorsicht, sondern dass es nichts kostet.** Was ein Beispiel zeigen soll,
zeigt ein erfundener Name genauso: Dass eine Jahreszahl neben einem Namen der Archivstand ist
und kein Aufnahmedatum, hängt nicht daran, wer der Mensch war. Am 21. August 2026 sind so 87
Fundstellen in 15 Dateien ersetzt worden, ohne dass ein einziges Beispiel an Schärfe verlor.
Der Anlass steht in der
[history.md](history.md#punkt-64-abschnitt-1-die-namen-aus-dem-repo), Punkt 64, Abschnitt 1.

## Der Kopf jeder Quelldatei

Zwei Zeilen, über dem Docstring, unter einer etwaigen Shebang-Zeile:

```python
# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0
```

In `.ts` und `.tsx` mit `//` statt `#`. Von der Apache-Lizenz **nicht** verlangt — die gilt über
die [LICENSE](../LICENSE) für das ganze Repo. Sie stehen trotzdem da, weil sie das einzige sind,
was eine **einzeln kopierte Datei** überlebt: Wer `services/dates.py` in sein Projekt zieht,
nimmt sonst keine Spur mit. Siehe [licensing.md](licensing.md).

**Keine Prüfung erzwingt sie.** Neue Dateien bekommen sie von Hand; vergisst sie jemand, ist der
Schaden klein.

## Testen

```bash
make check         # alles: Stil, die fuenf Pruefungen, alle Tests -- das Ziel vor einem Commit
make test          # nur die Tests
make test-backend  # pytest
make test-frontend # Typecheck und vitest
make lint          # ruff
make docs-check    # nur die fuenf Pruefungen unten
```

**Fünf Prüfungen laufen neben den Tests, weil sie Dateien lesen, die kein Test je sieht:**

```bash
python3 tools/language_check.py   # hält sich der Quelltext an die Sprachregelung?
python3 tools/check_anchors.py    # zeigen die Verweise in docs/ noch irgendwohin?
                                  #   (auch zwischen Dateien, seit dem 15. August 2026)
python3 tools/check_settings.py   # erreicht jede Einstellung den Container?
python3 tools/check_numbers.py    # stimmt die Buchführung des Backlogs über seine Nummern?
python3 tools/build_register.py --check   # ist das Register der Historie noch vollständig?
```

Sie brauchen weder `venv` noch `node_modules` — reine Leser, `python3` aus dem System genügt.

**Und sie hängen im Git-Hook**, weil „von Hand" in der Praxis „gar nicht" hiess. `.githooks/pre-commit`
führt genau diese fünf aus, **nicht** die Testreihe: Die läuft ohnehin, vergessen wurden diese fünf,
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

Die fünfte kam am 21. August 2026 dazu, mit dem Register am Anfang von
[history.md](history.md). Sie ist eigentlich ein Erzeuger — `make register` schreibt die Tabelle,
`--check` sagt nur, dass sie nicht mehr stimmt. Beides braucht dieselbe Zusage: **jeder Abschnitt
der Historie nennt sein Datum in den ersten Zeilen darunter.** Wer das vergisst, erfährt es beim
Commit und nicht ein halbes Jahr später an einer Tabelle mit Lücken.

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
Karte zeigt einfach etwas anderes. Beim Bauen heißt das: Sobald in einer Komponente gerechnet,
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

## Die Abhängigkeiten sind festgenagelt

`backend/pyproject.toml` nennt nur untere Schranken (`fastapi>=0.115`); das Abbild installiert
stattdessen aus `backend/requirements.lock`. Ohne sie zöge ein Neubau in einem Jahr andere
Versionen als der heutige — und bei einem Gerät, das offline steht und einmal im Jahr angefasst
wird, fällt so etwas erst im Museum auf.

```bash
make lock        # die Lockdatei neu aufloesen (nach einer Aenderung an pyproject.toml)
make deps-lock   # das eigene venv auf diesen Stand bringen
```

**Die beiden gehören zusammen, und `make check` erzwingt das.** `tools/build_notices.py` liest
die Namen und Versionen aus der Lockdatei — sie *ist* die Liste dessen, was ins Abbild kommt —,
die Lizenztexte aber aus dem venv, denn nur ein installiertes Paket hat seine `LICENSE` auf der
Platte. Weichen die beiden ab, bricht der Lauf ab. Eine Hinweisdatei, die eine Version nennt, die
im Abbild nicht liegt, ist schlimmer als keine.

**`make deps-lock` entfernt dabei die Umgebungsmarker.** `greenlet` kommt über SQLAlchemy ins
Abbild, auf einem Mac aber nie — ohne die lokal installierte Lizenzdatei liesse sich der Hinweis
nicht schreiben. Umgekehrt wird `colorama` zwar mitinstalliert, erscheint aber in keiner
Hinweisdatei: Sein Marker gilt nur für Windows, und das Abbild ist Linux.

## Ein Release bauen

```bash
make version v=0.9.0                 # die Zahl setzen
git commit -am "chore: Version 0.9.0"
git tag -s v0.9.0 -m v0.9.0          # signiert, tag.gpgsign steht
make release nach=/Volumes/STICK/kiekmap-update
```

`tools/build_release.py` baut beide Abbilder, sichert sie als `abbilder.tar`, schreibt die
`version`-Datei daneben und nimmt auf Wunsch (`karte=1`) Kartendatei und Ortsindex mit — genau
den Ordner, den `deploy/pi/update.sh` erwartet.

**Es bricht ab bei schmutzigem Arbeitsbaum oder fehlendem Tag**, und dagegen gibt es kein
`--force`: Ein Stick, der zu keinem Commit gehört, ist ein Jahr später nicht mehr zuzuordnen — und
genau ein Jahr ist der Abstand, in dem so ein Gerät angefasst wird.

**Die `version`-Datei ist die Zeile, die von Hand vergessen wird.** Ohne sie bleibt
`KIEKMAP_VERSION` in der `.env` des Pi stehen, der nächste Start zieht das alte Abbild wieder
hoch, und das Gerät läuft mit der alten Software, ohne es irgendwo zu sagen.

## Branches und Merges

Zwei langlebige Branches, und `main` bedeutet etwas Bestimmtes:

| Branch | Bedeutung | Wer schreibt hinein |
|---|---|---|
| `main` | **Was im Museum läuft.** Jeder Commit darauf trägt einen Tag. | nur Merges aus `develop` |
| `develop` | Der Alltag. Vorgabe-Branch. | Merges aus `feature/*` und `fix/*` |
| `feature/<kurz>`, `fix/<kurz>` | kurzlebig, ein Thema | per Pull Request nach `develop`, danach gelöscht |

**Das ist nicht GitHub Flow**, auch wenn es so aussieht. GitHub Flow hat genau einen langlebigen
Branch und ist für Dienste gebaut, die mehrmals täglich ausliefern. Dieses Gerät steht offline und
wird ein- bis zweimal im Jahr vom Stick aktualisiert; da beantwortet ein eigener `main` eine Frage,
die im Museum wirklich gestellt wird: *Was läuft eigentlich auf dem Gerät?* Die Begründung steht in
[decisions.md](decisions.md).

**Kein `release/*`, kein `hotfix/*`.** Bei einem Betreuer ist das Ballast. Ein dringender Fehler
wird ein `fix/`-Branch, geht nach `develop` und von dort sofort nach `main` — dieselbe Straße,
nur schneller befahren.

### Squash-Merge ist hier abgeschaltet, und das hat einen Grund

`history.md` zitiert **Commits einzeln, mit Hash** — über achtzig Fundstellen. Ein Squash-Merge
fasst die Commits eines Zweigs zusammen und vernichtet damit genau die, auf die die Dokumentation
zeigt. Das ist kein Stilproblem, sondern ein Datenverlust in einer Datei, deren Wert an diesen
Verweisen hängt.

- `feature/*` → `develop`: **Rebase.** Linear, und jeder Commit bleibt einzeln erhalten.
- `develop` → `main`: **echter Merge-Commit.** Er hält das Release-Ereignis fest.

## Veröffentlichen

SemVer-Tags, Conventional Commits, ein gemeinsames Repo für Front- und Backend. Frontend und
Backend werden zusammen versioniert — bei einem Ein-Geräte-System ist getrennte Versionierung nur
Ballast, und die API-Kompatibilität ist dadurch garantiert.

### Eine Zahl, fünf Stellen

```bash
make version            # zeigt sie
make version v=0.8.0    # setzt sie ueberall
```

`tools/set_version.py` schreibt sie nach `frontend/package.json`, zweimal nach
`frontend/package-lock.json` (Wurzelpaket), nach `backend/pyproject.toml` und nach
`backend/app/__init__.py`. `make check` meldet, wenn eine davon ausschert.

**Die vierte ist die wichtigste und wäre am ehesten liegengeblieben:** `__version__` ist das, was
`/api/health` antwortet und was in der OpenAPI-Beschreibung steht — also die Version, die das
Gerät im Museum von sich behauptet. Stünde sie still, während der Image-Tag weiterzählt, gäbe die
API auf die eine Frage, für die es sie gibt, die falsche Antwort.

**Der Tag ist nicht die Quelle, die Dateien sind es.** Eine Prüfung gegen `git describe` wäre
genau in dem Fenster rot, in dem die Version schon erhöht, der Tag aber noch nicht gesetzt ist —
und dort läuft der Commit-Hook. Der Tag muss stattdessen passen.

**Alle Commits sind signiert** (SSH, nicht GPG), Tags ebenso — auch die 185 aus der Zeit vor dem
Schlüssel, rückwirkend am 25. August 2026 nachgeholt. Das ist ungewöhnlich, und die Abwägung
gehört deshalb aufgeschrieben.

**Der naheliegendste Einwand trägt nicht:** Eine SSH-Signatur hat **keinen eigenen Zeitstempel**;
im Commit stehen nur Schlüssel, Namensraum `git`, Hashverfahren und die Signatur. Rückwirkend zu
signieren behauptet also nichts nachweisbar Falsches.

**Ein Preis bleibt, und er ist zu kennen:** `allowed_signers` kennt `valid-after=`, und Git prüft
eine Signatur gegen den Zeitpunkt *ihrer Entstehung* — also gegen das Commit-Datum. Wer diesem
Schlüssel je eine Gültigkeitsspanne ab dem 25. August 2026 gibt, bekommt alle Commits davor als
ungültig gemeldet. Wer den Schlüssel wechselt, trägt den alten also **ohne** `valid-after` weiter
ein.

**Gemacht wurde es mit** `git rebase --root --exec` — `filter-repo` signiert nicht. Der Lauf
setzte das Committer-Datum aus dem Autor-Datum zurück, sonst hätten alle 188 Commits den 25. August
als Committer-Datum bekommen. Ein Commit hatte vorher zehn Sekunden Abstand zwischen beiden Daten;
die sind dabei verlorengegangen.

Das Museumsgerät ist offline. Der Updateweg dorthin (Image-Tarball auf einen USB-Stick) steht in
[operations.md](operations.md).
