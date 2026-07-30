# Umbau des Verwaltungsmenüs

> **Umgesetzt am 29. Juli 2026.** Der Plan steht unverändert; was beim Bauen dazukam, steht am
> Ende unter „Beim Bauen dazugekommen".

## Kontext

Der Admin-Bereich ist über die Stufen 8 bis 10 gewachsen, und das sieht man ihm an. Drei Dinge
stören konkret:

1. **Der Filter unter „Fotos" kennt nur „Unvollständig".** Wer die Fotos ohne Ort abarbeiten will,
   bekommt die ohne Jahr mit dazu — obwohl das zwei verschiedene Arbeiten sind.
2. **Die Übersicht ist eine Sackgasse.** Sie nennt sechs Zahlen, aber nur eine davon führt
   irgendwohin. Wer liest „4 ohne Ort", muss sich selbst zum Filter durchklicken.
3. **Die Menünamen überschneiden sich.** „Hochladen" und „Import" klingen beide nach dem Hereinholen
   von Bildern, dabei ist das zweite ein Protokoll. Und der USB-Import hängt als Nachtrag unter
   einer Trennlinie im Formular, obwohl er ein gleichwertiger Weg ist.

Ziel ist eine Verwaltung, in der ein Ehrenamtlicher, der zweimal im Jahr hier ist, von jeder Zahl
aus dorthin kommt, wo die Arbeit stattfindet.

**Vorab geklärt** (steht so im Code, nichts zu tun):
- Das Import-Protokoll wird von **allen vier** Wegen gefüllt — überwachter Ordner, CLI, Upload,
  Stick. Sie laufen alle durch `import_file()`, und die schreibt immer einen Eintrag.
- Die **Rücksicherung existiert vollständig** (`POST /api/admin/backup/restore`, Oberfläche unter
  „Sicherung" mit Rückfrage). Der bisherige Bestand wird beiseitegelegt, nicht gelöscht.

---

## 1. Menü

| heute | neu |
|---|---|
| Übersicht · Fotos · Hochladen · Beiträge · Import · Sicherung | **Übersicht · Fotos · Moderation · Importieren · Protokoll · Sicherung** |

Erst die Pflege des Bestands, dann das Hinzufügen, dann das Technische. „Beiträge" heißt
**Moderation**, „Import" heißt **Protokoll** (es steht nicht mehr in Konkurrenz zu „Importieren"),
„Hochladen" heißt **Importieren** (es deckt jetzt beide Wege ab).

`frontend/src/admin/AdminApp.tsx`: `SECTIONS`-Liste umsortieren, `Section`-Typ anpassen
(`upload` → `import`, `changes` → `moderation`). Beschriftungen in
`frontend/src/texte/de.ts` unter `admin.shell.sections`.

## 2. Fotos: Filter aufteilen

**Alle · Ohne Ort · Ohne Jahr · Versteckt** — „Unvollständig" fällt ersatzlos weg.

- `backend/app/api/admin.py`: `Selection = Literal["all", "incomplete", "hidden"]` wird zu
  `["all", "without_location", "without_date", "hidden"]`. In `list_photos()` die
  `or_(…)`-Bedingung durch zwei einzelne ersetzen (`Photo.lat.is_(None)` bzw.
  `Photo.date_from.is_(None)`).
- `frontend/src/api/admin.ts`: `Selection`-Typ mitziehen.
- `frontend/src/admin/PhotoCare.tsx`: `FILTERS`-Liste auf vier Einträge.

## 3. Übersicht: Zahlen werden Wege

Zwei Zeilen zu drei Kacheln, feste `grid-template-columns: repeat(3, 1fr)` statt `auto-fill` —
sonst ordnet der Browser sie je nach Breite um und die gewollte Zeilenaufteilung geht verloren.

```
Fotos insgesamt   →  Fotos, ungefiltert
auf der Karte     →  (kein Link)
Versteckt         →  Fotos, „Versteckt"

Ohne Ort          →  Fotos, „Ohne Ort"
Ohne Jahr         →  Fotos, „Ohne Jahr"
Beiträge          →  Moderation
```

`frontend/src/admin/Overview.tsx`: Die vorhandene `Figure`-Komponente bekommt ein optionales
`onClick`; mit Klick rendert sie ein `<button>`, ohne wie bisher ein `<div>`. Die Reihenfolge der
Kacheln ändert sich (Versteckt rutscht in Zeile 1). Der bisherige Knopf „Unvollständige ansehen"
entfällt — die Kacheln ersetzen ihn. Die Sicherungs-Erinnerung bleibt, wo sie ist.

Statt neuer Props für jedes Ziel bekommt `Overview` **einen** Prop
`onNavigate(section, filter?)`; `AdminApp` setzt daraufhin Abschnitt und Filter. Das ersetzt die
heutigen `onShowIncomplete` und `onShowBackup`.

`frontend/src/styles/admin.css`: `.figure` als Knopf gestalten (Rand, `:active`, mindestens 48 px
hoch), Griffigkeit wie bei den übrigen Bedienelementen.

## 4. Importieren: neue Maske

Heute steht das Formular für Jahr und Ort ganz oben — bevor gesagt ist, woher die Bilder kommen —
und der Stick hängt als Nachtrag unter einer Linie. Neu in drei Schritten:

```
Importieren

1. Woher kommen die Bilder?
   ┌───────────────────┐  ┌───────────────────┐
   │ Vom Rechner       │  │ Vom USB-Stick     │
   │ [Bilder wählen]   │  │ Scans2024 · 4 …   │
   │ 12 Bilder gewählt │  │ (Liste, wählbar)  │
   └───────────────────┘  └───────────────────┘

2. Gilt für alle Bilder (freiwillig)
   ┌─ Jahr ──────────────┐  ┌─ Ort ───────────────┐
   │ [1932]              │  │ [Straße suchen …]   │
   │ ☐ Ganzes Jahrzehnt  │  │                     │
   └─────────────────────┘  └─────────────────────┘

   [ Importieren ]
```

Zwei gleichrangige Kacheln, eine davon ausgewählt. Steckt kein Stick, steht in der rechten Kachel
„Bitte USB-Stick einstecken" — sie verschwindet nicht, sonst wüsste niemand, dass es den Weg gibt.

**Jahr und Ort für den ganzen Stapel bleiben, weiterhin freiwillig.** Sie sind der Grund, warum die
Quelle *davor* steht statt darunter: So werden sie **einmal** gefragt und gelten für beide Wege —
bei vierzig Bildern derselben Kirchweih ist das der ganze Unterschied (Entscheidung aus Stufe 8).
An ihrer Wirkung ändert sich nichts: Sie füllen nur, was der Import leer gelassen hat; was die
Datei selbst weiß, gewinnt. Im Backend erledigt das weiterhin `apply_batch_defaults()` in
`app/services/importer.py`, das sich beide Wege schon heute teilen.

**Nebeneinander, beide im Rahmen.** Jahr und Ort stehen als zwei gleich aussehende Blöcke
nebeneinander — je ein `<fieldset class="field__group">` mit `<legend>` auf der Rahmenlinie, so
wie der Ort es heute schon ist. Zweispaltiges Raster, das auf schmalem Schirm untereinander
bricht. Das Jahr bekommt damit dieselbe Wertigkeit wie der Ort statt eines nackten Eingabefelds.

**„Ganzes Jahrzehnt" nur bei vollen Jahrzehnten.** Im Jahr-Block steht unter der Zahl ein
Ankreuzfeld *Ganzes Jahrzehnt*. Es ist **ausgegraut, solange die Jahreszahl nicht durch zehn
teilbar ist**.

Das ist nicht nur Ordnung, es schließt eine stille Falle: `date_range()` in
`app/services/dates.py` **rundet ein Jahrzehnt ab**. Wer heute 1934 einträgt und „Jahrzehnt"
wählt, bekommt kommentarlos 1930–1939 gespeichert — die 4 verschwindet, ohne dass jemand es
merkt. Mit der Regel kann das nicht mehr passieren.

Zwei Feinheiten, die sonst genau diese Falle wieder aufmachen:

- Wird das Häkchen gesetzt (1920, Jahrzehnt) und die Zahl danach auf 1923 geändert, muss sich das
  Häkchen **selbst zurücknehmen** — nicht nur ausgrauen. Ein gesetztes, aber ausgegrautes Feld
  würde beim Absenden weiterhin `decade` schicken.
- Unter dem Feld ein kurzer Satz, warum es meist nicht wählbar ist („Nur bei vollen Jahrzehnten
  wie 1920 oder 1930"). Für jemanden, der zweimal im Jahr hier ist, ist ein grauer Knopf ohne
  Erklärung eine Sackgasse.

> **Zur Entscheidung:** Dieselbe Falle steckt im Metadaten-Editor
> (`admin/PhotoEditor.tsx`), wo „genaues Jahr / ganzes Jahrzehnt" heute für **jede** Jahreszahl
> wählbar ist. Ich würde die Regel dort gleich mitziehen — sonst gilt im selben Bereich zweierlei
> Recht. Falls das nicht gewollt ist: sagen, dann bleibt der Editor unberührt.

- `frontend/src/admin/BatchUpload.tsx` wird zu `ImportView.tsx`: hält die Quelle
  (`"computer" | "stick"`), die gewählten Dateien bzw. den gewählten Ordner, Jahr und Ort, und
  startet je nach Quelle `uploadPhoto()` in der Schleife oder `startStickImport()`.
- `frontend/src/admin/StickImport.tsx` schrumpft auf die **Ordnerauswahl**: die Abfrage der
  Ordnerliste (`fetchImportFolders`, Abfrageschleife) und deren Darstellung als wählbare Liste.
  Fortschritt und Ergebnis wandern in `ImportView`, weil sie jetzt für beide Wege gelten.

## 5. Nach dem Import: eine Regel für beide Wege

**Bis 30 aufgenommene Bilder die Nacharbeits-Tabelle, darüber nur die Zusammenfassung** mit einem
Sprung zu „Fotos, Ohne Ort". Das ist heute je Weg verschieden und der Grund, warum sich die beiden
Wege ungleich anfühlen.

Der Upload liefert seine Zeilen schon heute synchron zurück (`UploadResult.items`). Der
Stick-Import läuft dagegen als Auftrag im Faden und liefert nur einen Satz Text. Er muss die
aufgenommenen Fotos mitgeben:

- `backend/app/services/backup.py`: `JobStatus` bekommt ein Feld `items: list[dict] | None`,
  `Job.start()` einen Weg, es zu setzen (die Arbeitsfunktion gibt künftig `(Meldung, items)`
  zurück statt nur der Meldung).
- `backend/app/services/importer.py`: `import_from_folder()` sammelt die `ImportOutcome`s und gibt
  sie neben der Meldung zurück.
- `backend/app/api/backup.py`: baut daraus `UploadItem`-Objekte — **nur bis `REVIEW_LIMIT = 30`**,
  darüber bleibt `items` leer. So wandert keine Nutzlast über zweihundert Fotos durch den Status,
  der im Sekundentakt abgefragt wird.
- `backend/app/schemas.py`: `JobState` bekommt `items: list[UploadItem] | None`.
- Im Frontend entscheidet dieselbe Grenze über die Anzeige; die Konstante steht in
  `frontend/src/admin/ImportView.tsx` mit einem Kommentar, der auf die Backend-Konstante zeigt.

## 6. Protokoll, Sicherung

Nur die Umbenennung im Menü. `frontend/src/admin/ImportLog.tsx` bleibt inhaltlich, die Überschrift
im Inhalt wird von „Import-Protokoll" auf „Protokoll" angeglichen.

Bei der Sicherung ist nichts zu tun.

---

## Dateien

**Backend** — `app/api/admin.py` (Filterwerte), `app/api/backup.py` (Items im Auftrag,
`REVIEW_LIMIT`), `app/services/backup.py` (`JobStatus.items`), `app/services/importer.py`
(`import_from_folder` gibt Outcomes zurück), `app/schemas.py` (`JobState.items`).

**Frontend** — `admin/AdminApp.tsx` (Menü, Navigation), `admin/Overview.tsx` (verlinkte Kacheln),
`admin/PhotoCare.tsx` (vier Filter), `admin/BatchUpload.tsx` → `admin/ImportView.tsx` (neue Maske),
`admin/StickImport.tsx` (nur noch Ordnerauswahl), `api/admin.ts` (Typen), `texte/de.ts` (Namen),
`styles/admin.css` (Kachel-Knöpfe, Quellenauswahl).

## Prüfung

**Tests, die den Fehlerfall beschreiben** (deutsche Namen, wie im Repo üblich):

- `test_api_admin.py`: `test_filter_ohne_ort_zeigt_nicht_die_ohne_jahr` — der Grund für die
  Aufteilung; ein Foto mit Ort aber ohne Jahr darf im Ortsfilter nicht auftauchen.
- `test_import_stick.py`: `test_kleiner_stapel_liefert_die_zeilen_mit` und
  `test_grosser_stapel_liefert_keine_zeilen` — die Grenze, ab der der Status nicht mehr die halbe
  Sammlung mitschleppt.
- Neu `frontend/src/admin/jahr.test.ts` für die Jahrzehnt-Regel als reine Funktion
  (`decadeAllowed(year)` und das Zurücknehmen des Häkchens):
  `test_jahrzehnt_nur_bei_vollen_jahrzehnten`, `test_geaendertes_jahr_nimmt_das_haekchen_zurueck`
  — der Fall, der sonst still eine 1934 zur 1930er macht.

**Am laufenden System**, wie in den Stufen zuvor:

1. `make dev`, über das Wappen anmelden (PIN 4711 in der lokalen `.env`).
2. Übersicht: jede der fünf verlinkten Kacheln antippen und prüfen, dass Abschnitt **und** Filter
   stimmen.
3. Fotos: die vier Filter durchgehen, Trefferzahlen gegen `/api/admin/overview` halten.
4. Importieren: mit dem `hdiutil`-Prüfvolumen (siehe `docs/betrieb.md`) einen Ordner vom Stick
   aufnehmen — einmal mit wenigen Bildern (Tabelle muss kommen), einmal mit über 30 (nur
   Zusammenfassung). Danach prüfen, dass auf dem Stick nichts verschoben wurde.
5. `make lint && make test`, `npx tsc -b --noEmit`.

**Doku**: CHANGELOG unter „Geändert", und in `docs/kuratoren-anleitung.md` die Abschnittsnamen
nachziehen — dort stehen „Fotos hinzufügen" und „Was Besucher beigetragen haben" mit den alten
Menünamen.


---

## Beim Bauen dazugekommen

- **Die Sicherungs-Erinnerung** auf der Startseite verlinkte durch den Umbau versehentlich in die
  Fotoliste. Sie führt jetzt dorthin, wo sie hingehört: in den Abschnitt „Sicherung".
- **Die Dateiauswahl brauchte eine sichtbare Beschriftung.** Ohne sie stand in der Maske nur ein
  fast leerer Kasten — ein `input type="file"` zeigt von sich aus kaum etwas an.
- **Die Kuratoren-Anleitung war weiter als gedacht veraltet:** Sie beschrieb noch den alten Ablauf
  („Jahr und Ort ganz oben, dann Bilder auswählen") und trug zwei Platzhalter aus den Stufen 9 und
  10, die längst gebaut sind. Beides ist nachgezogen.
- **`ImportOutcome` bekam ein Feld `source`.** Für die Nacharbeits-Tabelle wird der Name der
  Quelldatei gebraucht; `path` war schon mit dem Ablageort belegt.
