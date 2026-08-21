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
- **Die Lücken im Beispielbestand** (`seed/`) — Fotos ohne Jahr, ohne Ort, zwei nur straßengenaue,
  ein zurückgenommener Besucherbeitrag. Sie sind Absicht: Ohne sie hat der „Hilf mit"-Bereich
  nichts vorzulegen und ein Drittel des Programms wird nie geprüft. `tools/build_seed.py` zählt
  sie nach jedem Lauf und **bricht ab, wenn eine fehlt** — wer eine neue Frage baut, gibt ihr
  dort ihren Vorrat.

## Stand

Fertig: Stufen 0–10 (Gerüst, Backend, Frontend, Import, Abfrage-API, Karte mit Markern,
Zeitschieber, „Hilf mit" mit Hausnummern, Sprachregelung, Admin-Bereich mit Stapel-Upload,
USB-Sicherung, Kiosk-Betrieb), dazu der Umbau des Verwaltungsmenüs, zwei Runden Nachbesserungen
an Verwaltung und Besucheransicht sowie die Auswertung von Metadaten und Ordnerstruktur beim
Import, mit der der Erstbestand von 929 Fotos eingelesen wurde. Zuletzt das **Nachschärfen der
Verortung**: Ein Foto, das nur seine Straße kennt, lässt sich in der Detailansicht und im
„Hilf mit"-Bereich auf eine Hausnummer bringen — dort als dritte, nachrangige Frage, mit den
Nummern der Straße auf der Karte; danach das Nachziehen des neueren Archivstands auf **1324
Fotos**. Was als Nächstes ansteht, steht im Backlog.

Am **11. und 12. August 2026** ist der **Erstbestand bereinigt** worden — Punkt 41, in zwei Runden
und ohne das Sprachmodell, das dafür vorgesehen war.

*Verortung:* 72 Fotos aus Straßenordnern verortet, 57 verschwundene Hausnummern über die
Nachbarnummer nachgeschärft, 349 von einer eingetragenen EXIF-Koordinate auf ihre Archivadresse
gesetzt. **924 von 929 Fotos stehen auf der Karte**, vorher 852.

*Textfelder:* 815 Titel vom Adressabklatsch befreit, 62 Beschreibungen aus Titeln und
Fotorückseiten gehoben, 23 Archivsignaturen an die Herkunft, 52 Fotos aus ihrem eigenen Text
datiert. **Der Zeitschieber läuft jetzt von 1880 bis 2030** statt von 2010 bis 2025.

Dabei haben sich vier Regeln ergeben (`docs/decisions.md`, Punkt 34 bis 37): der Archivordner
schlägt die EXIF-Koordinate; die Hausnummer wird vor dem Jahr gefragt; Archivinterna gehören in die
Herkunft und nicht in die Beschreibung; und eine Jahreszahl im Text datiert nur dann das Foto, wenn
ein Datumswort davorsteht.

Am **14. August 2026** ist der **Containerbetrieb geprüft** worden — Punkt 17, auf dem Mac. Beide
Abbilder bauen, nginx liefert die Karte kachelweise aus, die Seite fragt null fremde Herkünfte an,
der Schemastand wird beim Start nachgezogen. **Zwei Fehler kamen dabei heraus, beide still:** Die
`.env` erreichte den Container nur zur Hälfte, weshalb ein Import Schlagwort, Bildnachweis und
Herkunft verlor (behoben mit `env_file` statt einer Aufzählung). Und ein Symlink unter `/media`
galt als Datenträger, weshalb die Sicherung in das Verzeichnis lief, das sie sichert —
`docs/decisions.md`, Punkt 40.

Am **15. August 2026** ist das Projekt von seinem Arbeitsnamen auf **Kiekmap** umbenannt worden —
Punkt 48. Klein im Code und in Pfaden, `KIEKMAP_` als Präfix der Einstellungen, für Besucher
unsichtbar. Warum der Name keinen Ort nennt, steht in `docs/decisions.md`, Punkt 41. **Sicherungen
von davor werden nicht mehr erkannt**, weil der Name im Ordner und im Archivnamen steht.

Ebenfalls am **15. August 2026**: Eine **zurückgespielte Sicherung bringt ihr Schema jetzt selbst
auf Stand** — Punkt 47, der Fehler, der zwei Tage lang jeden Besucherbeitrag scheitern ließ. Der
Neustart im Handbuch entfällt; eine Sicherung von einer neueren Programmversion wird abgelehnt,
bevor etwas ersetzt ist. `docs/decisions.md`, Punkt 42.

Am **16. August 2026** ist der **neuere Archivstand nachgezogen** worden — Punkt 52. **Der Bestand
steht bei 1324 Fotos**, 1320 davon auf der Karte; der Zeitschieber läuft von 1884 bis 2024.

**Der gelieferte Diff war keiner.** Von 619 Dateien zeigten **223 ein Bild, das schon im Bestand
stand** — das Museum hatte seinen Bestand durch ExifTool laufen lassen, wodurch sich in jeder Datei
die Metadaten und damit der SHA-256 änderten. Wer einen so gelieferten Stand importiert, legt
Dubletten an. Vor jedem Import eines Diffs wird deshalb über den **Bildinhalt** nachgezählt, nicht
über Bytes: `docs/decisions.md`, Punkt 47.

Der Wert des neuen Stands liegt nicht in den Dateien, sondern in den Feldern: 41 Titel und
Beschreibungen sind auf vorhandene Fotos übernommen worden. Ein blindes Übernehmen hätte
22-mal „Intel(R) JPEG Library" zurückgeholt, das Punkt 41 entfernt hatte — **das Archiv führt Titel
und Beschreibung als dasselbe Feld.** Ungehoben bleibt das XMP: 251 der neuen Dateien tragen dort
eine Ortsangabe, und `services/exif.py` liest kein XMP (Punkt 55 im Backlog).

Die Umwandlung nach JPEG liegt jetzt als `tools/to_jpeg.py` im Repo, mit einer am Erstbestand
**gemessenen** Einstellung — `docs/decisions.md`, Punkt 46. Sie ist nicht nachzujustieren: Zwei
Läufe über dieselbe Datei müssen denselben SHA-256 ergeben, sonst kommt beim nächsten Archivstand
jedes vorhandene Bild ein zweites Mal herein.

Direkt danach fiel auf, dass **323 der 395 neuen Fotos den Adressabklatsch im Titel trugen**, den
Punkt 41 an 815 Titeln von Hand entfernt hatte: Die Bereinigung hatte den Bestand aufgeräumt und
die Ursache im Import stehen lassen. Drei Regeln sind deshalb dorthin gewandert — der Ordnertitel
ist der Zusatz und nicht die Adresse, ein Titel gilt ab 60 Zeichen als Bildunterschrift (gemessen:
kein handgesetzter Titel überschreitet 58), und der Name der Scannersoftware landet in keinem der
beiden Felder. `docs/decisions.md`, Punkt 48. **Was von Hand aufgeräumt wird, gehört danach als
Regel dorthin, wo es entstanden ist** — sonst zählt man dieselbe Arbeit in Monaten.

Dabei hat der Trockenlauf zwei Fotos gefangen, die auf das Jahr ihres eigenen Abrisses datiert
worden wären („ca. 1970 wurde dieses Haus abgerissen"). Punkt 37 sagt, eine Jahreszahl datiere nur
mit einem Datumswort davor — das Wort davor sagt aber nur, *dass* es ein Datum ist, nicht *wovon*.
`docs/decisions.md`, Punkt 49.

Am selben Tag ist **Punkt 42** erledigt worden, die Dubletten. Ein Differenzhash über die
Vorschaubilder fand **44 Gruppen über 95 Fotos**; die Schwelle ist an sechzig durchgeblätterten
Paaren angesehen, nicht gewählt. **Vollautomatisch wäre falsch gewesen:** Bei einem Paar trägt die
*kleinere* Fassung den Bildtext, auf einem von drei sonst gleichen Bildern steht ein Lastwagen, und
dreimal stand dasselbe Bild an zwei verschiedenen Adressen — eine davon falsch, und ohne die
Dublettensuche hätte das niemand nebeneinander gesehen. Nach der Vorlage beim Museum sind 45 Fotos
aus der Ausstellung genommen; **der Bestand steht bei 1279 sichtbaren Fotos**. Der Finder liegt als
`services/similar.py` im Repo (`python -m app.cli dubletten`) und schreibt nichts.
`docs/decisions.md`, Punkt 54.

Danach lag der **Gesamtbestand des Archivs** vor, und zwei Fragen sind damit beantwortet. **Der
gelieferte Diff war vollständig** — von 1322 Dateien unter `Straßen` sind 1034 byte-identisch bei
uns, die übrigen 288 restlos erklärt, keine einzige unbekannt. Und **das XMP wird nicht gelesen**:
`dc:creator` sagt „unbekannt", `dc:description` liefert Kategorien wie „Gebäude", und beim Ort
bleiben nach Abzug des Bekannten eine Handvoll brauchbarer Hausnummern. Punkt 55 ist damit
aufgelöst — `docs/decisions.md`, Punkt 53. **Erst messen, dann bauen** heißt auch, dass die Messung
etwas anderes findet als das Gesuchte: Sie fand einen Ordner, der seine Straße wiederholt.

**Alles unter `deploy/pi/` ist weiterhin ungeprüft** — beim Bauen gab es kein Gerät. Syntax stimmt,
gelaufen ist nichts. Der erste Pi ist damit zugleich die Abnahme der Stufen 9 und 10; was zuerst
hakt, gehört nach [docs/operations.md](docs/operations.md). Ungeprüft bleiben auch die zwei Dinge,
die auf einem Mac nicht zu prüfen sind: der **USB-Weg der Sicherung** (`rshared`, Punkt 18) und das
Verhalten nach **Neustart und Stromausfall** (Punkt 15).

Zum Entwickeln auf dem Mac `KIEKMAP_MEDIA_DIR=/Volumes` setzen und ein Prüfvolumen mit `hdiutil`
anlegen — siehe ebenfalls [docs/operations.md](docs/operations.md). Den Containerbetrieb dort fährt
`make prod-mac`.

Der Admin-Bereich braucht eine PIN: `cd backend && .venv/bin/python -m app.cli pin` erzeugt die
Zeile für die `.env`. Ohne sie sagt die Anmeldung das im Klartext, statt jede Eingabe abzulehnen.

Am **18. August 2026** ist der **Erstbestand durchgesehen** worden — Punkt 1, der älteste offene
Eintrag, in zehn Schritte zerlegt und abgearbeitet. Fünf davon standen vorher nicht im Backlog,
sondern kamen beim Nachmessen heraus. **Der Bestand steht bei 749 Fotos ohne Jahr** statt 804,
17 davon monatsgenau und 35 jahrzehntgenau statt 3 und 5.

Die Bereinigungsrunde vom 11./12. August hatte im Text nur nach **vierstelligen Jahreszahlen**
gesucht — „80er Jahre", „Winter 63" und „Foto aus der Nachkriegszeit" liefen ihr durch, und das war
die größere Hälfte. Derselbe Fehler ist mir dabei noch einmal unterlaufen, eine Ebene tiefer:
„Notiz: Schule 78" stand undatiert da, während „Notiz: 1978" an drei Nachbarfotos längst als
Datierung galt. **Bei einer Suche nach Mustern bestimmt die Form des Musters den Befund, nicht der
Bestand** — `docs/decisions.md`, Punkt 56.

Was bleibt, ist Kuratieren und kein Backlogpunkt mehr: 942 Fotos ohne Beschreibung, 310 ohne Titel,
4 ohne Ort. Das schreibt, wer das Bild ansieht und den Ort kennt.

Am **19. August 2026** ist der **Code von aussen geprüft** worden — Punkt 39. Alles grün: 428
Backend- und 173 Frontend-Tests, Typprüfung, Formatierung und die drei Prüfskripte. Kein
Fachfehler; die Stellen, die dieses Projekt eigen machen, halten, was sie zusagen, und die Tests
prüfen wirklich, was ihre Namen versprechen.

**Drei stille Fehler kamen heraus**, keiner davon beim Benutzen zu bemerken: Der Eingangs-Watcher
schreibt einen ganzen Durchgang erst am Ende fest, während er jede Datei schon vorher nach
`_erledigt/` schiebt — eine Ausnahme mittendrin verliert die Fotos davor samt Protokoll. Zeitstempel
gehen ohne Zeitzonenmarker hinaus und werden im Browser als Ortszeit gelesen. Und ein Fehler beim
Rendern hinterlässt einen weissen Bildschirm, den kein Leerlauf-Neustart mehr heilt, weil der mit
abstürzt. **Alle drei sind noch am selben Tag behoben worden**, jeder mit Test und im Browser
nachgemessen. Zwei Regeln sind dabei entstanden: Die Fehlergrenze räumt ihren Zeitgeber
**nicht** auf, weil React sie nach dem Fangen mitnimmt und der Aufräumreflex genau die
Selbstheilung löschte (`docs/decisions.md`, Punkt 57). Und gespeichert wird UTC,
hinausgeschrieben mit Zonenmarker — **ausser dem EXIF-Datum**, das die Wanduhrzeit eines
Scanners ist und keine Zone kennt (Punkt 58).

Dazu **Punkt 61**, zwei Regeln an zwei Orten — und beide lagen anders als notiert: Die
Zuordnung MIME-Typ zu Dateiendung stand an *drei* Stellen, eine davon rechnete auf dem
String; sie heisst jetzt `suffix_for_mime`, und ihr Test prüft die Tabelle gegen sich selbst
statt Beispiele. Die drei Datumsformate dagegen waren **keine** Doppelung: Jedes lässt etwas
anderes weg, und Zusammenlegen hätte gekostet statt gespart. Sie liegen jetzt beieinander,
mit dem Grund dabei. **Ein Backlogeintrag ist eine Notiz, kein Befund** — beide Hälften sahen
beim Aufgreifen anders aus als beim Aufschreiben.

Und **Punkt 62**: Die Prüfungen laufen jetzt an einem Ort — `make check` bündelt Stil,
Prüfungen und Tests, der Hook unter `.githooks/pre-commit` nimmt nur die vier schnellen. Eine
vierte Prüfung zählt die Buchführung des Backlogs über seine eigenen Nummern nach. **Zahlen im
Fliesstext zählt sie ausdrücklich nicht**: Von vier Fundstellen im Repo darf keine einzige
berichtigt werden — zwei sind Zitate, zwei meinen Punkte auf einer Karte, eine ist ein Satz in
der Historie, der an seinem Datum stimmte. `docs/decisions.md`, Punkt 59.

Zuletzt **Punkt 63**, aufgelöst statt erledigt: Das Frontend hat keinen Komponententest, und
das ist die Regel, kein Rückstand — *jede Entscheidung wandert in eine reine Funktion und
bekommt dort ihren Test, das Rendern bekommt keinen.* Gemessen hielt die Praxis längst: Jedes
`useMemo` in einer Komponente ruft eine importierte reine Funktion auf. Eine Lücke fand sich
beim Nachsehen doch — der Zeitschieber rechnete die Fingerposition selbst in ein Jahr um, und
ein Rundungsfehler dort wählt 1931 statt 1932, ohne dass etwas falsch *aussieht*.
`docs/decisions.md`, Punkt 60.

Am **20. August 2026** ist die **Lizenzfrage beantwortet** worden — Punkt 23. Das Projekt steht
unter **Apache-2.0**, Copyright Kalle Erlhoff; ausschlaggebend war §4.2, weil das Projekt zum
Übernehmen gebaut ist und eine missratene Übernahme sichtbar eine Übernahme bleiben soll
(`docs/decisions.md`, Punkt 62). Von 169 Fremdpaketen ist keines Copyleft — der Satz im README
stimmte, er war nur nie geprüft.

**Die Arbeit lag nicht bei der Wahl, sondern beim Nachzählen.** Das gebaute Frontend trug
**zwei** Lizenzhinweise für siebenunddreissig Pakete; MIT verlangt den Vermerk in *jeder*
Kopie. `make notices` erzeugt die `THIRD-PARTY.txt` jetzt je Artefakt, `make check` merkt,
wenn sie veraltet. Dazu zwei kleinere Lücken: die Kartensymbole reisten ohne Lizenztext, und
die Karte nannte die ODbL nicht. **Was weitergegeben werden darf, steht jetzt in
`docs/licensing.md`** — auch, dass der Fotobestand nicht erfasst ist und dass die Tabelle
`places` aus OpenStreetMap stammt und in jeder Sicherung mitfährt.

Zum Schluss **Punkt 60**: `services/backup.py` mit seinen 938 Zeilen ist ein Paket aus zehn
Modulen geworden, geschnitten entlang der Kommentarbalken, die schon darin standen. Die
Bedingung stand vor dem Zuschnitt: **Die Tests dürfen sich nicht ändern**, sonst ist der
Beweis weg, dass nichts kaputtging. `__init__.py` ist die Tür, `from app.services import
backup` heisst weiterhin dasselbe — geändert haben sich **sechs Zeilen** in 1814 Zeilen
Testcode, alle sechs Ziele eines `monkeypatch`. `docs/decisions.md`, Punkt 61.

Der zweite trägt die Lehre: Er war schon einmal angefasst und an der Stelle, wo er auffiel,
**umgangen** worden — die Übersichtskacheln senden seither Tage statt Zeitstempel, mit einem
Kommentar, der die Ursache genau benennt. Vier Wochen las ihn niemand. **Wer ein Symptom beseitigt,
verliert den Anlass, nach den übrigen zu suchen.** `docs/history.md`, „Punkt 39: der Durchgang von
aussen".

**Was offen ist, steht in [docs/backlog.md](docs/backlog.md)** — nach Verwaltung,
Besucher-Interface, Infrastruktur und Entwicklung geordnet, jeder mit dem, was beim Aufgreifen
sonst erst wieder herausgefunden werden müsste. Jeder trägt eine **feste Nummer**, unter der er
zitiert wird („Punkt 15"), dazu seine Art und seine Einordnung; die Übersichtstabelle oben in der
Datei sagt, was wirklich ansteht. **Nummern werden nie neu vergeben** — erledigte und aufgelöste
bleiben vergriffen, damit ein Zitat aus einer alten Notiz nicht auf etwas anderes zeigt. Wie das Vorhandene entstanden ist und was dabei anders kam
als geplant, steht in [docs/history.md](docs/history.md); was das Programm kann, im
Änderungsprotokoll [CHANGELOG.md](CHANGELOG.md).
