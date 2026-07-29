# Stufenplan

Der Bauplan des Projekts: was fertig ist, was noch kommt, und woran man erkennt, dass eine Stufe
fertig ist. Das *Warum* der technischen Entscheidungen steht in [decisions.md](decisions.md), das
*Wie* der Arbeit in [entwicklung.md](entwicklung.md).

Jede Stufe endet in einem lauffähigen, committeten Zustand.

## Zielbild

Ein Touchscreen-Kiosk für das Heimatmuseum Holm: historische Ortsfotos auf einer Karte, filterbar
über einen Zeitraum-Schieber, plus ein „Hilf mit"-Bereich, in dem Besucher fehlende Angaben
ergänzen. Vollständig offline auf einem Raspberry Pi, gesichert durch Einstecken eines USB-Sticks
und einen Knopfdruck.

```
┌──────────────┬────────────────────────────────────────┐
│ [Wappen]     │  1880 ├──●━━━━━━━━━━━━━━━●──┤ 1990     │
│ Bilder aus   │                                        │
│ unserem HOLM │                                        │
├──────────────┼────────────────────────────────────────┤
│  HILF MIT    │                                        │
│              │         Karte des Ortes                │
│  [Foto]      │         Fotos an ihrem Aufnahmeort     │
│  "Wo ist     │                                        │
│   das?"      │                                        │
│              │                                        │
│  [Karte][×]  │                                        │
└──────────────┴────────────────────────────────────────┘
```

Der Zeitschieber steht über der Karte, die er filtert — nicht über dem „Hilf mit"-Bereich. Das
Wappen führt die linke Spalte an und ist zugleich der Weg in den Admin-Bereich.

---

## Stand

| Stufe | Inhalt | Status |
|---|---|---|
| 0 | Repo-Gerüst, Entscheidungsdokumentation | ✅ |
| 1 | FastAPI + SQLite + Alembic + Docker | ✅ |
| 2 | Frontend-Gerüst, Offline-Karte, Entwicklungsumgebung | ✅ |
| 3 | Import-Pipeline: Hash-Dedup, EXIF, Thumbnails, Eingangsordner | ✅ |
| 4 | Abfrage-API: bbox + Zeitraum, Histogramm, Auslieferung | ✅ |
| 5 | Karte mit Foto-Markern und Clustering, Foto-Overlay | ✅ |
| 6 | Zeitschieber mit Jahrzehnt-Histogramm | ✅ |
| 7 | „Hilf mit": Verortung, Datierung, Ortssuche | ✅ |
| 7.5 | Sprachregelung, Textmodul, Entwicklerdoku | ✅ |
| 7.6 | Deutsche Texte im Backend nach Konvention ordnen | ✅ |
| 8 | Admin-Bereich mit Stapel-Upload | ✅ |
| 9 | Sicherung und Wiederherstellung auf USB | ✅ (Einhängen auf dem Pi offen, siehe unten) |
| **10** | **Kiosk-Deployment auf dem Pi** | **als Nächstes** |
| — | [Vorgemerkt](#vorgemerkt): Hausnummern, Import vom Stick | gewollt, nicht eingeplant |
| 11 | Ausbau nach Bedarf | offen |

Was in den fertigen Stufen entstanden ist, steht im [CHANGELOG](../CHANGELOG.md).

---

## Stufe 7.6 — Deutsche Texte im Backend nach Konvention ordnen ✅

Bestandsaufnahme nach der Sprachumstellung. Umgesetzt:

- **Query-Parameter englisch.** `?von=…&bis=…` heißt jetzt `?from_year=…&to_year=…` (nicht `from`,
  das ist in Python reserviert). Zieht sich durch bis in `TimeRange = { from, to }` im Frontend.
- **Faustregel eingeführt:** *Kann die Meldung im Kiosk oder im Admin-Bereich erscheinen? Dann
  Deutsch, sonst Englisch.* Damit wurden die `bbox`-Parsefehler und der Thumbnail-Größenfehler
  englisch, während 404, 409 und die Regionsprüfung deutsch blieben — sie erscheinen im
  Foto-Overlay bzw. im „Hilf mit"-Bereich.
- **OpenAPI-Beschreibungen englisch.** Sie stehen *in* der API und werden neben Feldnamen wie
  `open_count` gelesen.
- **CLI-Ausgaben bleiben deutsch.** Den Erstimport führt auch das Museumsteam aus.

Die Konventionstabellen in [CLAUDE.md](../CLAUDE.md) und [entwicklung.md](entwicklung.md) nennen die
Regel; ein Kommentar in `app/api/photos.py` erklärt sie an der Stelle, wo beide Sorten Meldungen
nebeneinander stehen.

Nicht angefasst und weiterhin richtig so: Fehlermeldungen an Besucher und Kuratoren, das
Import-Protokoll, die Ordnernamen `_erledigt`/`_problem` und die Datumsbeschriftungen. Letztere
sitzen architektonisch auf der falschen Seite für Mehrsprachigkeit — siehe
[adaption.md](adaption.md).

---

## Stufe 8 — Admin-Bereich mit Stapel-Upload

**Einstieg.** Ein Klick auf das Ortswappen über der linken oberen Ecke der Karte öffnet ein
Zahlenfeld mit großen Tasten; nach der PIN der Admin-Bereich. PIN statt Passwort, weil am
Touchscreen getippt wird. Token mit Ablauf, damit ein vergessener Login nicht über Nacht offen
bleibt.

> Ursprünglich war ein drei Sekunden langer Druck auf die untere linke Bildschirmecke geplant —
> für Besucher unsichtbar. Das sichtbare Wappen hat gewonnen: das Schloss ist die PIN, nicht das
> Versteck, und eine unsichtbare Geste ist etwas, das Ehrenamtliche sich merken müssten. Wer aus
> Neugier tippt, sieht ein Zahlenfeld und tippt „Zurück zur Karte".
>
> Eine vierstellige PIN sind zehntausend Möglichkeiten, die ein Skript in Sekunden durchprobiert
> hätte. Das Gegengewicht ist die Sperre nach fünf Fehlversuchen — sie macht aus Sekunden Jahre
> und ist damit der eigentliche Schutz, nicht die Länge der PIN.

**Fotopflege.** Liste mit Filter „unvollständig", Metadateneditor, Besucheränderungen sichten und
einzeln zurücknehmen, Import-Protokoll, Statusübersicht.

**Stapel-Upload.** Vor dem Hochladen lassen sich Ort und Jahr *optional* für den ganzen Stapel
angeben — bei Bildern von einer Kirchweih sind beide identisch, und das einmal statt vierzigmal
einzugeben ist der ganze Unterschied. Danach erscheint der Stapel als Tabelle:

```
┌──────┬──────────────────────────────────────┬──────────────┐
│ [▣]  │ Titel  Kirchweih 1932 Muehle         │              │
│ Bild │ Jahr   1932       Ort  Kirche        │ [Übernehmen] │
├──────┼──────────────────────────────────────┼──────────────┤
│ [▣]  │ Titel  Umzug_Hauptstrasse            │              │
│ Bild │ Jahr   1932       Ort  Kirche        │ [Übernehmen] │
└──────┴──────────────────────────────────────┴──────────────┘
                                        [ Alle übernehmen ]
```

Titel ist aus dem Dateinamen vorbelegt, Jahr und Ort aus den Stapelangaben; alles änderbar.
„Übernehmen" speichert die Zeile und entfernt sie aus der Liste, „Alle übernehmen" erledigt den Rest.

Die Fotos sind bereits **nach dem Hochladen** in der Datenbank, nicht erst nach „Übernehmen" — ein
geschlossener Browser darf keine Uploads kosten. Die Tabelle ist eine Nacharbeitsliste, keine
Warteschlange; was liegen bleibt, taucht im „Hilf mit"-Bereich auf. Dubletten werden im Ergebnis
benannt („3 waren schon da") statt still übersprungen.

**Fertig, wenn:** du am Touchscreen ohne Tastatur hinein- und wieder hinauskommst, einen Stapel
hochladen und dabei Ort und Jahr für alle setzen kannst, und ein Foto vollständig über die
Oberfläche pflegen kannst. ✅

Beim Bauen dazugekommen, weil es sonst still gebrochen wäre: Beim Bearbeiten heißt ein
**fehlendes** Feld „unverändert lassen" und ein **leeres** Feld „löschen". Ohne diesen Unterschied
ließe sich eine falsche Datierung nur durch eine andere ersetzen, nie durch „weiß man nicht" — und
das Foto käme nie wieder in den „Hilf mit"-Bereich. Zurücknehmen eines Besucherbeitrags wird
verweigert, sobald das Feld inzwischen von Hand bearbeitet wurde.

---

## Stufe 9 — Sicherung und Wiederherstellung auf USB

Bewusst eine gestaltete Funktion, kein Shell-Skript: Die Zielgruppe sind ältere Ehrenamtliche, die
das ein- bis zweimal im Jahr tun. Ein Skript bedeutet in der Praxis, dass es nie ausgeführt wird.

```
Stick einstecken
  ┌──────────────────────────────────────────────────┐
  │  ✓ USB-Stick erkannt:  SANDISK 32 GB             │
  │    28,4 GB frei — genug für 2.150 Fotos          │
  │        [   SICHERUNG  STARTEN   ]                │
  └──────────────────────────────────────────────────┘
        ↓
  │  Sichere Foto 340 von 2.150 …   ████░░░░░  16 %  │
        ↓
  ┌──────────────────────────────────────────────────┐
  │  ✓ Sicherung abgeschlossen                       │
  │    2.150 Fotos und alle Angaben gesichert        │
  │    Sie können den Stick jetzt abziehen.          │
  └──────────────────────────────────────────────────┘
```

Ohne Stick steht dort nur „Bitte USB-Stick einstecken" — kein Knopf, der ins Leere führt.

**Ordner statt ZIP** auf dem Stick: eine abgebrochene Sicherung ist dann teilweise brauchbar statt
komplett wertlos, und man kann sie an jedem Rechner öffnen. **Inkrementell** über die Hash-
Dateinamen: liegt der Name schon dort, ist es dasselbe Bild — die zweite Sicherung dauert Sekunden.
**`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Betrieb anzuhalten.

**Wiederherstellen** packt daneben aus und schaltet erst am Ende um; der bisherige Stand wird vorher
beiseitegelegt. Eine abgebrochene Wiederherstellung darf den laufenden Bestand nie zerstören.

**Erinnerung** statt Automatik: „Letzte Sicherung vor 34 Tagen", ab 30 Tagen rot.

*Bekannter Fallstrick:* Auf Pi OS Lite mountet nichts von selbst (udev-Regel nötig), und ein
Docker-Bind-Mount zeigt neu eingehängte Datenträger nur mit `rshared`-Propagation. Ohne das bleibt
der Stick im Container unsichtbar.

**Fertig, wenn:** jemand aus der Zielgruppe die Sicherung ohne Hilfe und ohne Anleitung schafft —
und die Wiederherstellung auf einem zweiten, leeren Gerät nachweislich funktioniert.

**Stand.** Die Funktion ist fertig und gegen einen echten eingehängten Datenträger erprobt:
sichern, inkrementell erneuern, zurückspielen, Beiseitelegen des bisherigen Stands. Zwei Punkte
der Abnahme brauchen das Gerät und wandern damit in Stufe 10:

- **Das Einhängen auf dem Pi.** udev-Regel und Skript liegen unter `deploy/pi/`, sind aber
  mangels Pi noch nicht gelaufen. Beschreibung in [betrieb.md](betrieb.md).
- **Der Bedienbarkeitstest mit der Zielgruppe** und die Wiederherstellung auf ein zweites,
  leeres Gerät.

Dazugekommen beim Bauen, weil es sonst still gebrochen wäre: Ein Laufwerk muss ein echter
Einhängepunkt **und** beschreibbar sein. Ohne das Erste liefe die Sicherung auf dieselbe SD-Karte,
gegen deren Ausfall sie schützt; ohne das Zweite fiele ein schreibgeschützter Stick erst auf,
nachdem jemand den Knopf gedrückt hat.

> Beim Bauen von Stufe 10 den Abschnitt [Vorgemerkt](#vorgemerkt) lesen: Der Import vom USB-Stick
> braucht dasselbe Erkennen und Einhängen, das hier vorbereitet ist.

---

## Stufe 10 — Kiosk-Deployment auf dem Pi

Raspberry Pi OS **Lite** plus **cage**, ein winziger Wayland-Compositor, der genau ein Programm im
Vollbild anzeigt. Robuster als der volle Desktop: nichts kann sich in den Vordergrund drängen, kein
Hintergrundbild blitzt beim Booten auf, keine Update-Hinweise, kein Bildschirmschoner.

Ablauf nach dem Einschalten (~20 s):

1. Docker startet, die Container laufen mit `restart: unless-stopped` von selbst hoch.
2. `photomap-kiosk.service` wartet auf `/api/health` — sonst begrüßt das Museum seine Besucher für
   ein paar Sekunden mit einer Fehlerseite.
3. `cage -- chromium --kiosk` startet, Mauszeiger ausgeblendet, Energiesparen aus, Browserprofil bei
   jedem Start frisch.
4. Stürzt Chromium ab, startet systemd ihn neu. Fällt der Strom aus, bootet der Pi in denselben
   Zustand.

Dazu ein **Leerlauf-Reset** im Frontend: nach einigen Minuten ohne Berührung schließt sich ein
offenes Foto, Karte und Zeitraum kehren zur Standardansicht zurück. Sonst steht das Gerät morgens
im Zustand des letzten Besuchers vom Vorabend.

Ergänzend `docs/betrieb.md` (SD-Klon, Wartungsausgang, Fehlersuche) und `update.sh` für das
Offline-Update vom Stick.

**Fertig, wenn:** der Pi nach einem Kaltstart ohne Tastatur von selbst in der Karte landet — und
nach einem gezogenen Netzstecker genauso wieder hochkommt.

---

## Vorgemerkt

Anders als Stufe 11: Diese sind gewollt, nur noch nicht eingeplant. Sie stehen hier mit dem, was
beim Aufgreifen sonst erst wieder herausgefunden werden müsste — und bleiben stehen, wenn sie
erledigt sind, weil die Notiz dann erzählt, was daran wirklich dran war.

### Hausnummern im Ortsindex

**Warum.** Die Verortung über die Ortssuche trifft heute die Straße, nicht das Haus. Ein Mühlenweg
von 800 m Länge bekommt für jedes Foto denselben Punkt — auf der Karte liegen sie übereinander, und
„hier war das" ist um bis zu 400 m falsch. Für ein Dorf, in dem man Häuser auseinanderhält, ist das
zu grob.

#### Die Gestaltungsentscheidung: Straße zuerst, dann die Nummer

Nicht eine flache Trefferliste aus Straßen *und* Hausnummern, sondern **zwei Schritte** — genau wie
bei der Datierung, wo erst das Jahrzehnt und dann optional das Jahr kommt:

```
"Mühlenweg" tippen  →  [Mühlenweg   Straße]
                       ↓ antippen
                       Welche Hausnummer?   (Pin liegt schon auf der Straße)
                       [1] [1a] [2] [3] [10] [12] …
                       [ Reicht so — Straße genügt ]
```

Drei Gründe, und der dritte wiegt am schwersten:

1. Eine flache Liste mit `MAX_RESULTS = 12` wäre nach vierzig Hausnummern des Mühlenwegs voll —
   die anderen Straßen fielen heraus.
2. Große Knöpfe statt einer langen Liste sind am Touchscreen für ältere Finger das Richtige.
3. **„Reicht so" muss eine vollwertige Antwort bleiben.** Nicht jedes Haus hat in OSM eine Nummer,
   und niemand weiß bei jedem Foto die Hausnummer. Ein Schritt, der sich überspringen lässt, ist
   ehrlicher als ein Zwang — dieselbe Überlegung wie bei „Ganze 1920er Jahre".

Zusätzlich, weil es fast nichts kostet: Enthält die Eingabe eine **Ziffer** („mühlenweg 12"), darf
die freie Suche Adressen direkt liefern. Wer die Nummer weiß, tippt sie.

#### Datenmodell

Adressen sind gewöhnliche `places`-Zeilen mit `kind = "adresse"` — derselbe Ladeweg, dieselbe
Suche, dieselbe API-Form. Dazu zwei neue, leere Spalten auf `Place`:

| Spalte | Inhalt | Warum |
|---|---|---|
| `street` | `"Mühlenweg"` | Verknüpfung zur Straße, ohne Präfixraterei am Namen |
| `housenumber` | `"12"`, `"1a"` | zum natürlichen Sortieren, siehe unten |

`name` bleibt der zusammengesetzte `"Mühlenweg 12"` — davon lebt die bestehende Suche.

**Eine Alembic-Migration**, kein Zusammenfassen mit der initialen: In `data/` liegen inzwischen
Fotos. Die `places`-Tabelle selbst wird aus `places.json` ohnehin neu gefüllt (`load_from_file`
löscht und lädt), aber die Migration muss trotzdem sauber laufen.

#### Bauskript

[`tiles/build-places.py`](../tiles/build-places.py), zwei Zeilen mehr in `ABFRAGEN`:

```python
('node["addr:housenumber"]["addr:street"]', "adresse"),
('way["addr:housenumber"]["addr:street"]', "adresse"),
```

**Der Fallstrick sitzt in der Sammelschleife.** Sie überspringt heute jedes Element ohne `name`:

```python
ort_name = (tags.get("name") or "").strip()
if not ort_name:
    continue          # ← hier fielen alle Adressen still heraus
```

Adressknoten haben keinen `name`. Es braucht einen eigenen Zweig, der ihn aus
`addr:street` + `addr:housenumber` baut, bevor diese Zeile greift. Wer das übersieht, bekommt eine
grün durchlaufende Abfrage und null Adressen.

Zweiter Punkt: `art_fuer(tags)` prüft `"highway" in tags` zuerst; ein Gebäude mit Adresse *und*
`highway` gibt es praktisch nicht, aber die Adressprüfung gehört trotzdem vor die anderen.

Die Mittelwertbildung über gleiche `(name, art)` darf bleiben: Adressknoten und Gebäudeumriss
desselben Hauses liegen Meter auseinander, ihr Mittel ist richtiger als beides einzeln.

#### Suche

[`app/services/places.py`](../backend/app/services/places.py):

- `KIND_ORDER` und `kind_rank` um `"adresse"` **ganz hinten** ergänzen.
- `search()` bekommt eine Bedingung: `kind = "adresse"` nur, wenn `any(c.isdigit() for c in term)`.
- Neu: `housenumbers(session, street: str) -> list[Place]`, sortiert **natürlich**.

**Natürliche Sortierung ist der klassische stille Fehler:** Alphabetisch kommt „10" vor „9" und
„1a" vor „2". Der Schlüssel ist `(führende Zahl, Rest)` — eine reine Funktion, die einen eigenen
Test verdient (`test_hausnummern_werden_natuerlich_sortiert`).

Neuer Endpunkt in [`app/api/places.py`](../backend/app/api/places.py):

```
GET /api/places/{id}/housenumbers   →  list[PlaceOut]
```

Über die Id der Straße, nicht über ihren Namen — der Name käme aus dem Browser zurück und wäre
Eingabe, keine Tatsache (dieselbe Regel wie beim Sicherungspfad).

#### Oberfläche

[`frontend/src/kiosk/LocationTask.tsx`](../frontend/src/kiosk/LocationTask.tsx): Nach dem Antippen
einer Straße die Hausnummern als Knopfraster, darunter „Reicht so". Der Pin sitzt sofort auf der
Straßenmitte — der zweite Schritt verschiebt ihn nur.

`t.location` in [`de.ts`](../frontend/src/texte/de.ts) bekommt `askHouseNumber`, `noHouseNumber`,
und `kinds` den Eintrag `adresse: "Adresse"`.

Der Admin-Metadateneditor profitiert ohne Zutun: `PlaceField` nutzt dieselbe freie Suche, und dort
tippt jemand mit Tastatur ohnehin gern „Mühlenweg 12".

#### Genauigkeit mitschreiben

`Photo.location_accuracy_m` und `LocationContribution.accuracy_m` gibt es seit Stufe 3, benutzt
werden sie nicht. Hier lohnt es: Straßenmitte ≈ 150 m, Hausnummer ≈ 15 m. Der Kurator sieht damit,
welche Angabe belastbar ist, ohne dass jemand es dazuschreiben muss.

#### Womit zu rechnen ist

- **Umfang.** Für eine Gemeinde dieser Größe einige hundert bis zweitausend Adressen — der Index
  verdoppelt bis verdreifacht sich. `places.json` bleibt unter einem Megabyte, die Suche über ein
  paar tausend Zeilen ist auf dem Pi weiterhin unmerklich.
- **Lücken.** Nicht jedes Haus ist in OSM erfasst. Eine Straße ohne Hausnummern muss den zweiten
  Schritt einfach überspringen, nicht leer dastehen.
- **`addr:place` statt `addr:street`.** Kommt bei Streusiedlungen vor. Beim ersten Bau prüfen, ob
  in Holm Adressen fehlen, die es geben müsste.

#### Tests, die den Fehlerfall beschreiben

```
test_adressen_verdraengen_die_strassen_nicht     # der Grund für die zwei Schritte
test_hausnummer_mit_ziffer_wird_direkt_gefunden
test_hausnummern_werden_natuerlich_sortiert      # 10 nach 9, 1a nach 1
test_strasse_ohne_hausnummern_bleibt_beantwortbar
test_hausnummer_setzt_die_genauigkeit
```

**Aufwand.** Vergleichbar mit der Ortssuche aus Stufe 7 — eine konzentrierte Sitzung, wenn
`make places` einmal mit Internet laufen kann.

### ~~„Weiß ich nicht" wechselt die Frage~~ ✅ erledigt

Umgesetzt in [`frontend/src/store/contribute.ts`](../frontend/src/store/contribute.ts). Der
Fallstrick war der vermutete: Läuft eine der beiden Fragen leer, muss das Laden auf die andere
zurückfallen — sonst stünde „Zurzeit ist alles vollständig" auf dem Schirm, während Hunderte Fotos
auf eine Jahreszahl warten. Der Rückfall greift jetzt bei jedem Laden, nicht nur beim Wechseln, und
behebt denselben Fehler auch nach einem abgegebenen Beitrag.

### Import vom USB-Stick im Admin-Bereich

**Was.** Im Admin-Bereich Bilder von einem eingesteckten Stick aufnehmen, im Ablauf so wie der
Stapel-Upload: Ort und Jahr optional für alles, danach dieselbe Nacharbeitstabelle.

**Warum.** Der Weg über den Browser setzt einen Rechner voraus. Wer mit einem Stick voller Scans vor
dem Kiosk steht, soll ihn einstecken können.

**Wo.** Das Fachliche ist fertig: `import_file()` nimmt einen Pfad,
[`import_directory()`](../backend/app/services/importer.py) ein ganzes Verzeichnis — genau das, was
hier gebraucht wird. Neu sind nur der Endpunkt, der ein Verzeichnis auf dem Stick statt
hochgeladener Dateien annimmt, und die Auswahl des Ordners in der Oberfläche.

**Reihenfolge.** Gehört hinter Stufe 9, nicht davor: Das Erkennen und Einhängen des Sticks
(udev-Regel, `rshared`-Propagation) wird dort ohnehin gebaut, und beides zweimal zu lösen wäre
verschenkt. Der Fortschrittsbalken der Sicherung passt ebenfalls.

**Achtung.** Der Stick ist fremdes Dateisystem: keine Datei darf verschoben oder gelöscht werden,
anders als im überwachten Eingangsordner. Nur lesen und kopieren.

---

## Stufe 11 — Ausbau nach Bedarf

Nichts davon ist eingeplant, alles ist naheliegend:

- **Perceptual Hash** gegen inhaltlich gleiche, aber unterschiedlich zugeschnittene Scans. Der
  SHA-256 erkennt die nicht.
- **Jahreszahl aus dem Dateinamen** raten (`Kirchweih_1932_Muehle.jpg`). Vorsicht: `IMG_1932.jpg`
  ist ein Kamerazähler. Nur als Vorschlag markieren, nie als Tatsache.
- **Historische Karte** als umschaltbares Overlay (Urkataster o. ä.).
- **Attract-Mode**: Diashow bei Leerlauf statt Standardansicht.
- **Rechte und Herkunft** pro Foto — im Museumskontext oft relevant.
- **Volltextsuche** über SQLite FTS5.
- **Read-Only-Overlay-Dateisystem** gegen SD-Korruption bei Stromausfall.

---

## Prüfungen, die durch alle Stufen gehen

- **Offline-Test (der wichtigste).** Netz trennen, Karte bewegen. In den DevTools darf keine Anfrage
  an eine fremde Herkunft stehen:
  ```js
  performance.getEntriesByType('resource')
    .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length  // 0
  ```
- **Unschärfe-Test.** Ein Foto „1920er" muss bei Auswahl 1925–1930 erscheinen. Der Fall, der bei
  naiver Datumsabfrage still falsch wird.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen — Kioske sterben
  an einem langsamen Leck im Frontend, nicht am Backend.
- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Wiederherstellung wirklich proben.** Auf ein zweites, leeres Gerät zurückspielen. Ein
  ungetestetes Backup ist kein Backup.
- **Bedienbarkeitstest mit der echten Zielgruppe.** Eine ehrenamtliche Person die Sicherung
  durchführen lassen, ohne zu helfen, und zusehen, wo sie stockt. Der aussagekräftigste Test des
  ganzen Projekts.

## Offene Punkte

- Displayauflösung und -orientierung des Museumsgeräts (beeinflusst die Layoutmaße)
- Rechte- und Herkunftsangaben pro Foto — im Museumskontext oft relevant, noch nicht spezifiziert
- Lizenz des Projekts
