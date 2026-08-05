# Photomap für einen anderen Ort oder eine andere Sprache

Die kurze Antwort vorweg:

| Vorhaben | Aufwand |
|---|---|
| **Anderer deutschsprachiger Ort** | reine Konfiguration — kein Fork, kein Codeeingriff |
| **Andere Sprache** | überschaubarer Umbau, siehe unten. Bis dahin ein Fork. |

Das ist kein Zufall, sondern eine Entscheidung, die sich durchzieht: **nichts Ortsspezifisches steht
im Code.** Der Ausschnitt wird zur Laufzeit aus `region.json` geholt, die Kartendatei ist ein
Artefakt, der Ortsindex kommt aus einem Bauskript. Wer daran etwas ändert, sollte diese Eigenschaft
erhalten — sie ist der Grund, warum ein zweites Museum keinen zweiten Zweig braucht.

---

## Anderer Ort

### 1. Region festlegen

Nur eine Datei: [`tiles/region.json`](../tiles/region.json).

```json
{
  "name": "Musterhausen",
  "bbox": [minLon, minLat, maxLon, maxLat],
  "center": [lon, lat],
  "defaultZoom": 14.8,
  "minZoom": 13,
  "maxZoom": 15
}
```

Die Datei beschreibt einen **Ort** und sonst nichts. Welche Jahrzehnte der „Hilf mit"-Bereich zur
Auswahl stellt, stand hier einmal mit — das gehört aber zur Sammlung und ergibt sich inzwischen aus
ihr: angeboten wird, was der Bestand umspannt, mindestens jedoch 1920er bis 2010er. Ein Museum, das
später ein Foto von 1890 datiert, bekommt den 1890er-Knopf von selbst dazu.

**Bounding Box ausrechnen.** Aus Mittelpunkt und gewünschtem Umkreis:

```bash
python3 -c "
import math
lat, lon, r = 53.62053, 9.67601, 5.0   # Mittelpunkt und Radius in km
dlat = r / 111.320
dlon = r / (111.320 * math.cos(math.radians(lat)))
print([round(x, 5) for x in (lon-dlon, lat-dlat, lon+dlon, lat+dlat)])
"
```

Großzügig wählen. Die `bbox` begrenzt zugleich, wie weit sich die Karte schieben lässt; zu eng
fällt erst am Kiosk auf, wenn jemand hinauszoomt. Die Kacheln werden ohnehin mit 10 % Rand gebaut.

**Zoomstufen bestimmen.** `defaultZoom` so wählen, dass der Ortskern das Bild füllt:

```bash
python3 -c "
import math
lat, kartenbreite_px, gewuenscht_km = 53.62, 1500, 3.0
mpp = 156543.03392 * math.cos(math.radians(lat))
for z in (13, 14, 14.5, 15, 15.5, 16):
    m = mpp / 2**z
    print(f'  z={z:<5} {kartenbreite_px*m/1000:5.2f} km breit')
"
```

Auf einem 1080p-Display ist die Kartenfläche etwa 1500 × 920 px breit. `minZoom` so, dass der ganze
Ausschnitt auf einmal sichtbar ist. `maxZoom` bleibt bei 15 — das ist die Grenze des
Protomaps-Tagesbuilds, darüber hinaus wird überzoomt und bleibt trotzdem scharf.

**Jahrzehnte** an die Sammlung anpassen: Ein Museum, dessen ältester Abzug von 1890 ist, gewinnt
nichts durch einen 1860er-Knopf.

### 2. Kartendaten und Ortsindex bauen

```bash
make tiles     # Vektorkacheln, Schriften und Symbole für die neue Region
make places    # Ortsindex aus OpenStreetMap
```

Beides braucht Internet und läuft auf dem Entwicklungsrechner, nicht auf dem Pi. Größenordnung für
eine Gemeinde mit 5 km Umkreis: 4–5 MB Kacheln, 14 MB Schriften und Symbole, rund achttausend Orte
(`places.json` ~1,5 MB).

Der Löwenanteil sind **Adressen** — für Holm 7686 von 8513 Einträgen. Sie machen die Verortung
haus- statt straßengenau; ohne sie bekäme jedes Foto einer 800 m langen Straße denselben Punkt. Wer
den Ortsindex klein halten will, kann die beiden `addr:`-Zeilen in `tiles/build-places.py`
auskommentieren; die Oberfläche überspringt den Hausnummernschritt dann von allein.

`make tiles` legt `region.json` zusätzlich unter `data/` ab — dort liest das Backend sie und prüft
damit, ob eine Verortung aus dem „Hilf mit"-Bereich überhaupt in der Region liegt. **Ohne diese
Datei greift der Schutz nicht** (er lässt dann alles durch, statt grundlos abzulehnen).

### 3. Wappen austauschen

[`frontend/public/logo.png`](../frontend/public/logo.png) durch das eigene ersetzen — gleicher
Dateiname, sonst nichts. Das Bild liegt über der linken oberen Ecke der Karte und ist zugleich der
Weg in den Admin-Bereich. Im Code steht nirgends, was darauf zu sehen ist; die Beschriftung für
Vorlesewerkzeuge setzt sich aus `name` in der `region.json` zusammen.

Hochkant oder quer ist gleich, das Bild wird in ein Quadrat von 4,5 rem eingepasst. Sinnvoll sind
etwa 400 px Kantenlänge; PNG mit Transparenz sieht auf der Karte am besten aus.

Ein Hinweis zum Recht: Gemeindewappen sind meist gemeinfrei im urheberrechtlichen Sinn, ihre
Führung ist davon aber unabhängig geregelt. Für ein Heimatmuseum am Ort ist das in aller Regel
unproblematisch — im Zweifel kurz bei der Gemeinde nachfragen. Das mitgelieferte Holmer Wappen
stammt aus der Wikipedia (Public Domain, Hans-Frieder Kühne).

### 4. Sammlungsspezifisches prüfen

In der `.env`:

```bash
PHOTOMAP_EXIF_DATE_MAX_YEAR=1990   # ab wann ein EXIF-Datum als Scandatum gilt
PHOTOMAP_ADMIN_PIN_HASH=...        # PIN für den Admin-Bereich

# Angaben, die beim Import für jedes Foto gelten. Alle drei sind leer voreingestellt.
PHOTOMAP_IMPORT_TAGS=["Gebäude"]                 # Schlagwörter für jedes importierte Foto
PHOTOMAP_IMPORT_CREDIT=Sammlung Heimatmuseum Holm # Bildnachweis, wo die Datei niemanden nennt
PHOTOMAP_IMPORT_PROVENANCE=Online-Archiv des Museums, Verzeichnis 01 Orte/
```

`exif_date_max_year` hochsetzen, falls die Sammlung auch echte Digitalfotos enthält — sonst
verlieren die ihr Aufnahmedatum. Herunterlassen, wenn ausschließlich Scans erwartet werden. Wo
die Datei ihr Gerät nennt, entscheidet ohnehin das: Ein Scanner datiert nie, eine Kamera immer.
Der Wert greift nur für Dateien ohne Geräteangabe.

Die drei `IMPORT_`-Werte sind der Ort für das, was eine *Sammlung* ausmacht.
`PHOTOMAP_IMPORT_TAGS` ist eine JSON-Liste; in Holm besteht der Bestand aus Gebäuden, anderswo
aus Trachten oder Schiffen. `PHOTOMAP_IMPORT_PROVENANCE` wird wörtlich vor den Dateipfad im
Import-Ordner gesetzt und trägt darum sein eigenes Trennzeichen am Ende — so führt die
Herkunftsangabe eines Fotos zurück auf die Datei im eigenen Archiv.

Ob der Import die **Ordnernamen** auswertet, muss nirgends eingestellt werden: Ein Pfadteil gilt
als Straße, wenn der Ortsindex sie kennt. Ein Archiv, das nach Straße und Hausnummer abgelegt
ist, wird damit von selbst verortet; eines mit anderer Ablage bleibt einfach unberührt.

Den PIN-Hash erzeugt:

```bash
cd backend && .venv/bin/python -m app.cli pin
```

Die PIN selbst wird nirgends gespeichert. Ist `PHOTOMAP_ADMIN_PIN_HASH` leer, sagt der
Admin-Bereich das im Klartext, statt jede Eingabe abzulehnen.

### 5. Prüfen

```bash
make dev
```

- Zeigt die Karte den richtigen Ort im richtigen Ausschnitt?
- Lässt sich die Karte nicht über die Region hinausschieben?
- Findet die Ortssuche im „Hilf mit"-Bereich lokale Straßennamen?
- **WLAN abschalten und die Karte bewegen** — Beschriftungen müssen sichtbar bleiben.

Der letzte Punkt ist der wichtigste. Prüfung ohne Hinsehen:

```js
performance.getEntriesByType('resource')
  .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length
// muss 0 sein
```

### Was dabei *nicht* zu tun ist

Kein Codeeingriff, kein Fork, kein neuer Zweig. Wer beim Anpassen feststellt, dass er doch Code
ändern muss, hat einen Fehler gefunden — dann gehört der Wert nach `region.json` oder in die `.env`,
nicht in eine Kopie des Projekts.

Ausgenommen sind kosmetische Reste: ein Kommentar in `app/api/places.py` und das Beispiel in der
OpenAPI-Beschreibung nennen Holm. Beides ist Dokumentation, keine Logik.

---

## Andere Sprache

Hier ist ein Fork heute noch der ehrliche Weg — nicht weil es viel Arbeit wäre, sondern weil an
einer Stelle eine bewusste Entscheidung im Weg steht.

### Was schon vorbereitet ist

Alle Oberflächentexte stehen in [`frontend/src/text/de.ts`](../frontend/src/text/de.ts), im Code
stehen nur Schlüssel. Eine zweite Sprache ist dort eine Datei:

```ts
// frontend/src/text/en.ts
export const t = { app: { title: "Pictures from our village", … } } as const;
```

Dazu ein Umschalter, wo `de` importiert wird — oder ein `index.ts`, das je nach Konfiguration das
eine oder andere Modul weiterreicht.

### Was im Weg steht: serverseitige Datumsbeschriftung

`date_label` (`"1920er"`, `"Juni 1955"`, `"Jahr unbekannt"`) wird **im Backend** gebildet, in
[`app/services/dates.py`](../backend/app/services/dates.py). Das war Absicht — das Frontend soll
keine Datumsarithmetik betreiben — ist aber für Mehrsprachigkeit die falsche Stelle.

Der Umbau, falls er ansteht:

1. `PhotoMarker` und `PhotoDetail` liefern statt `date_label` die Rohwerte, die ohnehin schon da
   sind: `date_from`, `date_to`, `date_precision`.
2. Die Formatierung wandert ins Frontend, neben die Textbausteine. Die Logik ist klein — fünf Fälle,
   nachzulesen in `format_label`.
3. `MONTH_NAMES` und `"Jahr unbekannt"` entfallen im Backend.

Das ist ein halber Tag, kein Projekt. Wer die Zweisprachigkeit von Anfang an braucht, sollte es
zuerst tun.

### Was sonst noch deutsch ist

| Ort | Was | Bemerkung |
|---|---|---|
| Fehlermeldungen der API | `HTTPException`-Texte | erreichen Besucher und Kuratoren direkt |
| Import-Protokoll | `ImportOutcome.message` | „Aufgenommen, es fehlt noch: Ort und Jahr" |
| Ordnernamen im Eingang | `_erledigt`, `_problem` | sieht das Museumsteam im Dateimanager |
| Ortsarten | `strasse`, `gebaeude`, `flur` … | kommen so aus `tiles/build-places.py`; die Anzeige übersetzt sie in `t.location.kinds` |
| Doku und Commit-Nachrichten | alles unter `docs/` | bewusst so, siehe [development.md](development.md) |

Die Ortsarten sind der einzige Fall, der nach einer Falle aussieht und keine ist: In der Datenbank
stehen deutsche Schlüsselwörter, aber angezeigt wird, was das Textmodul daraus macht. Eine
englische Fassung mappt dieselben Schlüssel auf `"Street"`, `"Building"` und so weiter.

---

## Wann Modularisierung sich lohnt

Solange es um **einen Ort je Installation** geht, ist der jetzige Zuschnitt der richtige: eine
Konfigurationsdatei, zwei Bauskripte, fertig. Mehr Struktur würde nur Arbeit erzeugen, die niemand
braucht.

Interessant wird es, sobald einer dieser Fälle eintritt:

- **Mehrere Orte auf einem Gerät** — etwa ein Kreismuseum mit mehreren Gemeinden. Dann bräuchte
  `region` einen Datenbankbezug statt einer Datei, und Fotos müssten einer Region zugeordnet werden.
- **Ein gemeinsamer Bestand, mehrere Kioske** — dann wäre das Backend zentral und nur das Frontend
  je Standort konfiguriert.
- **Regelmäßige Updates an mehrere Museen** — dann lohnt es, die Konfiguration vollständig aus dem
  Repo zu lösen, damit ein `git pull` nie eine Anpassung überschreibt.

Bis dahin gilt: Ein zweites Museum bekommt eine Kopie des Repos, ändert `region.json` und die
`.env`, baut Kacheln und Ortsindex, und ist fertig. Updates zieht es per `git pull` — die eigenen
Anpassungen liegen in Dateien, die dabei nicht kollidieren.
