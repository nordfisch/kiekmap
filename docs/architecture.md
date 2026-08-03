# Aufbau

Woraus das System besteht und wie die Teile ineinandergreifen. Diese Datei beantwortet **was gibt
es** — nicht *warum so* und nicht *wie arbeitet man daran*:

| Datei | Frage |
|---|---|
| **architecture.md** | *Was* gibt es, und wie greift es ineinander? |
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? |
| [development.md](development.md) | *Wie* arbeitet man daran? — Einrichtung, Tests, Konventionen |
| [history.md](history.md) | *Wie* ist es dazu gekommen? |
| [operations.md](operations.md) | Wie läuft das Gerät im Museum? |

Die vollständige Übersicht steht in [index.md](index.md).

Wo hier eine Entscheidung nur benannt wird, steht ihre Begründung in `decisions.md`. Die Ordner
listet `development.md` auf; hier stehen die Zusammenhänge.

---

## Das Ganze auf einen Blick

```
   ENTWICKLUNGSRECHNER (mit Internet)          MUSEUMSGERÄT (offline)
   ───────────────────────────────────         ──────────────────────────────────────────

   tiles/region.json                                    ┌──────────────┐
        │                                               │   Chromium   │  kein Container
        ├──► build-tiles.sh ──► map.pmtiles ────────┐   │  unter cage  │
        │      (OpenStreetMap)   basemaps/          │   └──────┬───────┘
        │                                           │          │ Port 80
        └──► build-places.py ──► places.json ───┐   │          ▼
               (Overpass)                       │   │   ┌──────────────┐
                                                │   └──►│    nginx     │  Container 1
                                                │       │  + Frontend  │
                                                │       └──┬────────┬──┘
                                                │          │        │ /api → Proxy
                                                │   Karte, │        ▼
                                                │   Seite  │  ┌──────────────┐
                                                └──────────┼─►│   FastAPI    │  Container 2
                                                           │  │  + Watcher   │
                                                           │  └──────┬───────┘
                                                           │         │
                                                           │         ▼
                                                           │   data/  (auf der SD-Karte)
                                                           │   ├── photomap.db   SQLite
                                                           │   ├── photos/       Originale
                                                           │   ├── thumbs/       Vorschauen
                                                           │   └── places.json ──┘ einmal eingelesen
```

Drei Prozesse, zwei davon in Containern. **Chromium ist bewusst keiner** — er läuft als
gewöhnliches Programm auf dem Pi und zeigt nur an, was die beiden anderen ausliefern.

---

## Die Bausteine

### Backend — FastAPI und SQLite

Der einzige Weg zu den Daten. Es hält die Datenbank, die Bilddateien und alle Regeln; das Frontend
kennt keine Datei und keine Tabelle, nur die API unter `/api`.

Innerhalb des Backends gilt eine Trennung, die die Testbarkeit trägt: `app/api/` prüft Parameter,
ruft einen Dienst und gibt ein Schema zurück — dünn. `app/services/` hält die Fachlogik **ohne
HTTP-Bezug**, und dort gehört das Denken hin. Alles, was sich ohne HTTP testen lässt, gehört
dorthin.

Beim Start (`lifespan` in `app/main.py`) geschehen zwei Dinge: Der Ortsindex wird eingelesen,
falls die Tabelle leer ist, und der **Eingangs-Watcher** beginnt zu laufen. Er ist ein Faden im
selben Prozess, kein eigener Dienst.

### Frontend — React, MapLibre und nginx

Eine Einzelseite mit zwei Ansichten. Es gibt **keinen Router**: `App.tsx` entscheidet anhand des
Zustands im `useAdmin`-Store, ob die Besucheransicht (`src/kiosk/`), das Zahlenfeld oder der
Verwaltungsbereich (`src/admin/`) gerendert wird. Für ein Gerät ohne Adressleiste wäre ein Router
Ballast — und eine URL, die jemand versehentlich stehen lässt, ein Risiko.

Im Betrieb liefert **nginx** die gebaute Seite aus und leitet `/api` an das Backend weiter. Beide
kommen damit von derselben Herkunft; die CORS-Einstellung im Backend ist nur für den
Vite-Entwicklungsserver da und greift auf dem Pi nie.

nginx tut hier aber mehr als ausliefern: Es beantwortet **HTTP-Range-Requests** auf die
Kartendatei. Genau deshalb braucht das Projekt keinen Tileserver — MapLibre liest über
`pmtiles://` einzelne Kachelbereiche aus einer statischen Datei. Die Konfiguration schaltet dafür
`gzip` an dieser Stelle ab; ein komprimierender oder puffernder Zwischenschritt würde das
zerstören.

### Kacheln und Ortsindex — gebaute Artefakte

Beide entstehen auf dem Entwicklungsrechner mit Internet und liegen **nicht** im Repo. Sie gehen
danach getrennte Wege, und das ist der Punkt, an dem sich die beiden Skripte unterscheiden:

| | erzeugt | landet in | Weg zur Laufzeit |
|---|---|---|---|
| `tiles/build-tiles.sh` | `map.pmtiles`, Schriften, Symbole | `frontend/public/` | wandert ins Frontend-Image, wird von nginx ausgeliefert |
| `tiles/build-places.py` | `places.json` | `data/` | wird vom Backend in die Tabelle `places` eingelesen |

Der Kartenstil verweist standardmäßig auf ein CDN. Schriften und Symbole werden deshalb
mitgeladen und liegen unter `frontend/public/basemaps/` — sonst hätte die Karte offline Flächen,
aber keine Beschriftung.

### Kiosk-Schicht auf dem Pi

Alles unter `deploy/pi/`, und alles davon **ungeprüft** (siehe [backlog.md](backlog.md)):
`setup-pi.sh` richtet ein frisches Gerät ein, `photomap-kiosk.service` wartet auf `/api/health`
und startet dann `cage` mit Chromium im Vollbild, `update.sh` spielt ein Update vom Stick ein, und
eine udev-Regel hängt USB-Sticks ein — auf Pi OS Lite gibt es keinen Automounter.

---

## Was wann entsteht

Die wichtigste Unterscheidung im ganzen Aufbau, weil sie festlegt, was ein zweites Museum tun muss
und was von selbst geschieht:

**Zur Bauzeit** (Entwicklungsrechner, Internet nötig): Kartendatei, Schriften, Symbole und
Ortsindex aus `tiles/region.json`. Dazu das Frontend-Bundle.

**Zur Laufzeit** (Gerät, offline): alles andere. Der Ausschnitt der Karte, der Ortsname im Titel
und die Zoomstufen werden **nicht** ins Bundle gebacken, sondern beim Start aus
`/tiles/region.json` geholt. Dieselbe Datei dient also zwei Zwecken: Sie steuert den Bau, und sie
konfiguriert die laufende Ansicht.

Daraus folgt die Eigenschaft, die das Projekt zusammenhält: **Nichts Ortsspezifisches steht im
Code.** Ein zweites Museum braucht keinen Fork, sondern eine eigene `region.json` und `.env`. Das
Vorgehen steht in [adaption.md](adaption.md).

---

## Wo der Zustand liegt

An drei Stellen, jede mit einer eigenen Aufgabe:

**SQLite** (`data/photomap.db`) hält alle Angaben — Fotos, Datierungen, Orte, Schlagwörter, das
Änderungsprotokoll, das Import-Protokoll und den Ortsindex. Im WAL-Modus, damit ein Stromausfall
höchstens die letzte Transaktion kostet. Schemaänderungen laufen über Alembic und werden beim
Containerstart angewendet.

**Das Dateisystem** (`data/photos/`, `data/thumbs/`) hält die Bilder. Der Dateiname ist der
**SHA-256 des Bildinhalts** — daran hängen gleich drei Dinge: die Dublettenerkennung beim Import,
die Cache-Header bei der Auslieferung und die inkrementelle Sicherung. Ein gleicher Name ist
dasselbe Bild, überall.

**Der Browser** hält nur das Admin-Token, in `sessionStorage`. Es stirbt mit dem Tab, auf dem Pi
also spätestens beim morgendlichen Neustart. Alles andere im Frontend ist flüchtiger Zustand in
Zustand-Stores (`src/store/`), einer je Bereich.

---

## Die Wege durch das System

### Ein Foto kommt herein

Vier Wege, ein Ziel — sie laufen alle durch `import_file()` in `app/services/importer.py`, und die
schreibt immer einen Eintrag ins Import-Protokoll:

1. **Überwachter Eingangsordner** — der Watcher nimmt auf, sobald eine Datei fertig geschrieben
   ist, und räumt sie danach nach `_erledigt/` oder `_problem/`. Gelöscht wird nie.
2. **Hochladen im Verwaltungsbereich** — der Weg für vierzig ausgesuchte Dateien.
3. **USB-Stick im Verwaltungsbereich** — der Weg für einen Ordner mit zweihundert Scans. **Auf dem
   Stick wird nichts verschoben und nichts gelöscht**, anders als im eigenen Eingangsordner.
4. **`python -m app.cli import`** — für den Erstbestand.

Der Import berechnet den Hash, legt Original und zwei Vorschaugrößen ab, liest EXIF und IPTC — und
verwirft dabei ein EXIF-Datum ab 1990 als Scandatum. Ohne diese Regel läge ein Foto von 1932 auf
der Zeitleiste bei 2019 und käme nie zur Korrektur.

### Ein Besucher trägt etwas bei

Der „Hilf mit"-Bereich holt sich über `/api/contribute/next` ein Foto, dem Ort oder Jahr fehlt.
Der Beitrag geht direkt in den Bestand — aber **nur in leere Felder**: Was ein Kurator eingetragen
hat, ist unantastbar, und Koordinaten außerhalb der Region werden abgewiesen. Jeder Beitrag
landet zugleich als Zeile in `changes` und lässt sich einzeln zurücknehmen, solange niemand das
Feld inzwischen von Hand bearbeitet hat.

Nach dem Beitrag stellt sich die Ansicht für die Dauer des Dankes auf dieses eine Foto ein — Karte
und Zeitschieber zusammen, gesteuert über ein Fokus-Signal im Kiosk-Store.

### Die Karte fragt Fotos ab

`/api/photos` nimmt einen Kartenausschnitt und optional einen Zeitraum. Zwei Dinge daran sind
nicht offensichtlich:

Der Zeitfilter fragt auf **Überlappung** der Intervalle ab, nicht auf Enthaltensein — ein auf
„1920er" datiertes Foto muss bei der Auswahl 1925–1930 erscheinen. Und die Antwort ist bewusst
schmal gehalten: Beschreibung, Schlagwörter und Herkunftsfelder kommen erst, wenn ein Foto
angetippt wird.

Im Frontend werden Fotos auf **derselben Stelle** vor dem Clustern zu einem Marker
zusammengefasst; supercluster sieht die Dubletten gar nicht. Ohne das lägen acht Fotos exakt
übereinander und nur das oberste wäre erreichbar.

### Sicherung, Wiederherstellung, Stick-Import

Diese drei teilen sich **einen** Auftrag (`Job` in `app/services/backup.py`). Sie laufen im Faden,
melden ihren Fortschritt, und es kann immer nur einer laufen — zwei gleichzeitige Schreibläufe auf
dieselbe SQLite-Datei wären eine Fehlerquelle ohne Not. Das Frontend fragt den Status im
Sekundentakt ab.

---

## Was an den Rändern zu wissen ist

**Die Offline-Zusage ist prüfbar und wird geprüft.** Die Seite darf **null** Anfragen an eine
fremde Herkunft absetzen. Der Einzeiler dafür steht in [development.md](development.md).

**Fremdschlüssel und Migrationen vertragen sich in SQLite schlecht.** Ein Tabellenneubau löscht
das Original, und mit eingeschalteter Prüfung räumt das ab, was daran hängt. `alembic/env.py`
schaltet sie deshalb für die Dauer einer Migration ab — im Betrieb bleibt sie an. Ein Test hält
das fest; die Geschichte dazu steht in [history.md](history.md).

**Der Pi hat keine Browser-Bedienung.** Kein Reload-Knopf, keine Adressleiste, keine Tastatur.
Deshalb lädt der Leerlauf nach fünf Minuten die Seite neu, statt nur den Zustand zurückzusetzen,
und deshalb lädt auch das Verlassen des Verwaltungsbereichs neu.

**Der Ortsindex kennt nur Straßen und Hausnummern.** Gebäude, Gewässer und Fluren stehen nicht
darin — für sie gibt es den Pin auf der Karte.
