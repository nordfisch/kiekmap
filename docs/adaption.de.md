<!-- translated-from: docs/adaption.md -->
<!-- source-sha: 3120d9828b75c4159cea8168e6a1bc227d3ed5d483c188a390b3fd58378d0ad6 -->

# Kiekmap für einen anderen Ort oder eine andere Sprache

| Vorhaben | Aufwand |
|---|---|
| **Anderer deutschsprachiger Ort** | reine Konfiguration — kein Fork, kein Codeeingriff |
| **Andere Sprache** | eine Zeile in der `.env` — siehe unten |

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
  "maxZoom": 15,
  "streetChoice": 80
}
```

`streetChoice` ist die Anzahl der Straßen, die der „Hilf mit"-Bereich als Knöpfe zur Wahl stellt —
die dem `center` nächsten. Der Ortsindex darf weiter reichen; was darüber hinaus liegt, wird auf
der Karte angetippt. **Eine Anzahl und kein Radius**, weil sie das Knopfbudget unabhängig davon
hält, wie dicht ein Ort bebaut ist: 80 Straßen passen in zwei Fragen mit je höchstens zehn Knöpfen
(siehe [decisions.md](decisions.md), Punkt 24). Fehlt der Schlüssel, gilt 80.

**Der Wert ist zu prüfen, nicht zu übernehmen** — wie, steht in
[Schritt 3](#3-die-straßenauswahl-prüfen).

Die Datei beschreibt einen **Ort** und sonst nichts. Welche Jahrzehnte der „Hilf mit"-Bereich zur
Auswahl stellt, stand hier einmal mit — das gehört aber zur Sammlung und ergibt sich inzwischen aus
ihr: angeboten wird, was der Bestand umspannt, mindestens jedoch 1920er bis 2010er. Ein Museum, das
später ein Foto von 1890 datiert, bekommt den 1890er-Knopf von selbst dazu.

**Zur Länge des `name`.** Er steht als Überschrift im Kopfbereich, und dort passt er sich der Spalte
an: Je länger er ist, desto kleiner wird er gesetzt, damit er **auf einer Zeile bleibt**. Das geht
nicht unbegrenzt — kleiner als die Zeile „Bilder aus" darüber wird er nicht, und darunter bricht er
um. Nachgemessen am 16. August 2026:

| Länge des Namens | Auf einem 1024er Schirm | Auf einem 1920er |
|---|---|---|
| bis 12 Zeichen | einzeilig | einzeilig |
| 13 bis 16 Zeichen | bricht um | einzeilig |
| darüber | bricht um | bricht um |

„Holm" hat vier, „Klein Nordende" hat vierzehn. **Ein Umbruch ist kein Fehler**, sondern die
bewusste Rückfallebene — ein abgeschnittener Ortsname wäre schlimmer. Wer ihn vermeiden will, kürzt
den `name` („Klein Nordende" statt „Klein Nordende-Lieth"); der volle Name gehört ohnehin eher in
den Begrüßungstext als in die Überschrift.

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

### 2. Kartendaten und Ortsindex bauen

```bash
make tiles     # Vektorkacheln, Schriften und Symbole für die neue Region
make places    # Ortsindex aus OpenStreetMap
```

Beides braucht Internet und läuft auf dem Entwicklungsrechner, nicht auf dem Pi. Größenordnung für
eine Gemeinde mit 5 km Umkreis: 4–5 MB Kacheln, 14 MB Schriften und Symbole, rund achttausend Orte
(`places.json` ~1,5 MB).

Den größten Teil machen **Adressen** aus — für Holm 7686 von 8513 Einträgen. Sie machen die
Verortung haus- statt straßengenau; ohne sie bekäme jedes Foto einer 800 m langen Straße denselben
Punkt. Wer den Ortsindex klein halten will, kann die beiden `addr:`-Zeilen in
`tiles/build-places.py` auskommentieren; die Oberfläche überspringt den Hausnummernschritt dann
von allein.

`make tiles` legt `region.json` zusätzlich unter `data/` ab — dort liest das Backend sie und prüft
damit, ob eine Verortung aus dem „Hilf mit"-Bereich überhaupt in der Region liegt. **Ohne diese
Datei greift der Schutz nicht** (er lässt dann alles durch, statt grundlos abzulehnen).

### 3. Die Straßenauswahl prüfen

Der „Hilf mit"-Bereich fragt nach dem Ort eines Fotos, und der **Hauptweg dorthin sind Knöpfe**:
erst der Anfangsbuchstabe, dann die Straße, dann die Hausnummer. Ein Suchfeld gibt es dort nicht —
die Besucheransicht hat überhaupt kein Eingabefeld, weil am Kiosk keine Tastatur steht (siehe
[decisions.md](decisions.md), Punkt 24). Ob dieser Weg trägt, entscheidet sich am Ortsindex, und
das lässt sich vor dem ersten Besucher nachsehen.

**Woher die Straßen kommen.** Aus `make places`: Das Skript fragt einmal die Overpass-API nach
allem, was innerhalb der `bbox` liegt, und schreibt es in den Ortsindex. Wer diesen Schritt
auslässt, bekommt keinen Fehler — der Bereich sagt dann „Tippen Sie die Stelle bitte auf der Karte
an" und schaltet die Karte von sich aus scharf. Das ist ein funktionierender Notweg, aber eben ein
Notweg: Ohne Ortsindex ist auch die Hausnummer nicht zu haben, und jedes Foto einer 800 m langen
Straße bekäme denselben Punkt.

**Wie man nachsieht, ohne zu raten.** Ein Aufruf liefert genau die Liste, die der Baum bekommt:

```bash
curl -s localhost:8000/api/places/streets | python3 -c "
import json,sys
namen = [p['name'] for p in json.load(sys.stdin)]
print(f'{len(namen)} Strassen zur Wahl:')
print('  ' + ', '.join(namen))
"
```

Wer sie sich ansieht, weiß dreierlei: ob der Ortskern vollständig drin ist, wie viele Fremdorte
mitkommen, und ob `streetChoice` passt.

**Wie `streetChoice` zu wählen ist.** Der Wert entscheidet, wie viele Fragen bis zur Straße nötig
sind. Die Gruppen werden gerechnet, nicht aufgeschrieben: Aus höchstens zehn Knöpfen je Stufe
ergibt sich der Baum von selbst. Für Holm sieht das so aus:

| | |
|---|---|
| Straßen zur Wahl (`streetChoice` 80) | 80 |
| Knöpfe auf der ersten Stufe | 10 — `A` `B–D` `E` `F–G` `H` `I` `K–L` `M–R` `S` `T–Z` |
| davon direkt zur Straßenliste | 7 |
| mit einem Zwischenschritt | 3 — `A` (15), `H` (11), `I` (11) |

Zwei Fragen im Regelfall, drei im Ausnahmefall. **Das ist die Zielgröße.** Ein dichter bebauter Ort
braucht einen kleineren Wert, ein weitläufiger verträgt einen größeren — nachrechnen lässt sich das
mit derselben Abfrage oben: Kommen mehr als etwa hundert Straßen zusammen, gerät die dritte Stufe
zum Regelfall, und der Weg zur Hausnummer wird lang.

**Was schiefgehen kann, beides ohne Fehlermeldung:**

- **Die `bbox` ist zu eng gesetzt.** Der Ortsindex reicht nur so weit wie sie; Randstraßen fehlen
  dann ganz und stehen weder in der Suche noch auf einem Knopf.
- **Die `bbox` ist zu weit gesetzt.** Dann kommen Nachbardörfer mit — und weil `streetChoice` die
  *nächsten* nimmt, verdrängen deren Straßen die eigenen aus der Auswahl. In Holm liegen 486
  Straßen im Index und nur 80 auf den Knöpfen; wäre der Ausschnitt doppelt so groß, wären darunter
  Straßen, die kein Foto der Sammlung je zeigt.

Beides ist an der Liste oben zu sehen, bevor jemand davorsteht. Erwartet man einen Straßennamen
und findet ihn nicht, ist die `bbox` der erste Verdacht, nicht der Code.

### 4. Wappen einsetzen

**Mitgeliefert wird ein Platzhalter, kein Wappen** — ein schlichtes Schild aus
[`tools/build_logo.py`](../tools/build_logo.py). Warum kein echtes, steht in
[decisions.md](decisions.md), Punkt 21.

[`frontend/public/logo.png`](../frontend/public/logo.png) durch das eigene ersetzen — gleicher
Dateiname, sonst nichts. Das Bild liegt über der linken oberen Ecke der Karte und ist zugleich der
Weg in den Admin-Bereich. Im Code steht nirgends, was darauf zu sehen ist; die Beschriftung für
Vorlesewerkzeuge setzt sich aus `name` in der `region.json` zusammen.

Hochkant oder quer ist gleich, das Bild wird in ein Quadrat von 4,5 rem eingepasst. Sinnvoll sind
etwa 400 px Kantenlänge; PNG mit Transparenz sieht auf der Karte am besten aus.

> **Die ersetzte Datei nicht committen.** Sie trägt denselben Namen wie der Platzhalter, taucht
> also als geänderte Datei auf. Auf dem eigenen Gerät ist das richtig; in einem Repo, das jemand
> klonen kann, gibt sie das Wappen weiter — siehe unten.

#### Zum Recht: zwei Fragen, die oft zu einer verschmolzen werden

**Urheberrecht.** Ein Gemeindewappen ist nach § 5 Abs. 1 UrhG ein amtliches Werk und damit
gemeinfrei. Von dieser Seite ist nichts zu klären.

**Wappenrecht.** Davon unabhängig ist die *Führung* eines Wappens beschränkt: Es ist ein
Hoheitszeichen, die Gemeinde regelt seinen Gebrauch, geschützt über das Namensrecht (§ 12 BGB) und
die Vorschriften über Hoheitszeichen. Auch die Wikipedia weist auf ihren Wappenseiten
ausdrücklich darauf hin.

Daraus folgt zweierlei:

- **Auf dem eigenen Gerät** ist das Wappen des eigenen Ortes für ein Heimatmuseum in aller Regel
  unproblematisch — im Zweifel kurz bei der Gemeinde nachfragen.
- **In einem öffentlichen Repo ist es etwas anderes.** Wer das Repo veröffentlicht, gibt jede
  darin liegende Datei an jeden weiter, der sie klont. Eine Erlaubnis für das eigene Museum ist
  keine Erlaubnis für Dritte, und ein Hinweis oder eine Namensnennung ändert daran nichts: Hier
  geht es nicht um Zuschreibung, sondern um Erlaubnis.

Deshalb liegt in diesem Repo ein Platzhalter, und das Wappen bleibt eine lokale Datei — wie
`.env` und die gebaute Karte.

### 5. Sammlungsspezifisches prüfen

In der `.env`:

```bash
KIEKMAP_EXIF_DATE_MAX_YEAR=1990   # ab wann ein EXIF-Datum als Scandatum gilt
KIEKMAP_ADMIN_PIN_HASH=...        # PIN für den Admin-Bereich

# Angaben, die beim Import für jedes Foto gelten. Alle drei sind leer voreingestellt.
KIEKMAP_IMPORT_TAGS=["Gebäude"]                 # Schlagwörter für jedes importierte Foto
KIEKMAP_IMPORT_CREDIT=Sammlung Heimatmuseum Holm # Bildnachweis, wo die Datei niemanden nennt
KIEKMAP_IMPORT_PROVENANCE=Online-Archiv des Museums, Verzeichnis 01 Orte/
```

`exif_date_max_year` hochsetzen, falls die Sammlung auch echte Digitalfotos enthält — sonst
verlieren die ihr Aufnahmedatum. Heruntersetzen, wenn ausschließlich Scans erwartet werden. Wo
die Datei ihr Gerät nennt, entscheidet ohnehin das: Ein Scanner datiert nie, eine Kamera immer.
Der Wert greift nur für Dateien ohne Geräteangabe.

Die drei `IMPORT_`-Werte sind der Ort für das, was eine *Sammlung* ausmacht.
`KIEKMAP_IMPORT_TAGS` ist eine JSON-Liste; in Holm besteht der Bestand aus Gebäuden, anderswo
aus Trachten oder Schiffen. `KIEKMAP_IMPORT_PROVENANCE` wird wörtlich vor den Dateipfad im
Import-Ordner gesetzt und trägt darum sein eigenes Trennzeichen am Ende — so führt die
Herkunftsangabe eines Fotos zurück auf die Datei im eigenen Archiv.

Ob der Import die **Ordnernamen** auswertet, muss nirgends eingestellt werden: Ein Pfadteil gilt
als Straße, wenn der Ortsindex sie kennt. Ein Archiv, das nach Straße und Hausnummer abgelegt
ist, wird damit von selbst verortet; eines mit anderer Ablage bleibt einfach unberührt.

Den PIN-Hash erzeugt:

```bash
cd backend && .venv/bin/python -m app.cli pin
```

Die PIN selbst wird nirgends gespeichert. Ist `KIEKMAP_ADMIN_PIN_HASH` leer, sagt der
Admin-Bereich das im Klartext, statt jede Eingabe abzulehnen.

### 6. Alles zusammen prüfen

```bash
make dev
```

- Zeigt die Karte den richtigen Ort im richtigen Ausschnitt?
- Lässt sich die Karte nicht über die Region hinausschieben?
- Führen die Knöpfe im „Hilf mit"-Bereich in zwei bis drei Schritten zu einer echten Straße
  (siehe [Schritt 3](#3-die-straßenauswahl-prüfen))?
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

Ausgenommen sind kosmetische Reste: Kommentare im Backend nennen Holm, wo ein Beispiel den Fall
konkret macht. Das ist Dokumentation, keine Logik.

---

## Andere Sprache

Eine Einstellung, und sie steht dort, wo alle Einstellungen der Instanz stehen:

```bash
# .env
KIEKMAP_LANGUAGE=en
```

Danach den Dienst neu starten. **Ein neuer Bau ist nicht nötig** — das Frontend holt die Sprache
beim Start über `GET /api/config`. Zulässig sind `de` und `en`; ein anderer Wert bricht den Start
ab, statt still auf Deutsch zurückzufallen.

Umgestellt wird damit alles, was ein Mensch am Gerät liest: Besucheransicht, Verwaltung,
Fehlermeldungen der API, das Import-Protokoll, die Meldungen der Sicherung, die Datumsbeschriftung
und das Zahlenformat.

**Nicht umgestellt wird die Karte darunter.** Sie beschriftet ihre Orte in jeder Einstellung
deutsch, denn die Beschriftungssprache ist eine Eigenschaft des Ortes und nicht des Lesers — in
Holm heißt die Straße in jeder Sprache Mühlenweg. Für ein Museum außerhalb des deutschen
Sprachraums ist das die falsche Antwort, und es ist offene Arbeit:
[Issue #33](https://github.com/nordfisch/kiekmap/issues/33).

### Wo die Texte stehen

Zwei Kataloge, gleich gebaut:

| | Oberfläche | Backend |
|---|---|---|
| Ort | [`frontend/src/text/`](../frontend/src/text/) | [`backend/app/text/`](../backend/app/text/) |
| Deutsch | `de.ts` | `de.py` |
| Englisch | `en.ts` | `en.py` |

**Ein fehlender Eintrag bricht den Bau, nicht das Museum.** Im Frontend ist der Typ der Kataloge
`typeof de`, also lehnt `tsc` eine unvollständige Übersetzung ab. Im Backend sind es eingefrorene
Dataclasses, und eine fehlende Angabe ist ein `TypeError` beim Start.

### Eine dritte Sprache

Dieselbe Konstruktion trägt sie ohne Umbau: eine Datei je Katalog, ein Wert mehr in
`KIEKMAP_LANGUAGE`. Bei drei Sprachen lohnt sich allerdings ein Übersetzungsdienst — siehe
[decisions.md](decisions.md).

Die Sprache ist eine **Einstellung der Instanz, keine Wahl der Besucher**. Das Gerät steht in einem
Museum und spricht dessen Sprache. Ein Umschalter auf dem Touchscreen wäre eine Bedienungsfrage für
Besucher, die oft älter sind, und keine Erleichterung.

### Was in jeder Sprache deutsch bleibt

| Ort | Was | Warum |
|---|---|---|
| Ortsarten | `strasse`, `gebaeude`, `flur` … | Schlüssel aus `tiles/build-places.py`; angezeigt wird, was `t.location.kinds` daraus macht |
| Straßen- und Ortsnamen | aus OpenStreetMap | ein Eigenname wird nicht übersetzt |
| Ältere Einträge im Import-Protokoll | `ImportLog.message` | festgehalten, was das Gerät damals gesagt hat |
| `*.de.md` und `docs/archive/history.de.md` | Doku für Museum und Betrieb | als Übersetzung geführt, siehe [development.md](development.md#language) |

Die Ortsarten sind der einzige Fall, der nach einer Falle aussieht und keine ist: In der Datenbank
stehen deutsche Schlüsselwörter, angezeigt wird die Übersetzung. `en.ts` bildet dieselben Schlüssel
auf `"Street"`, `"Building"` und so weiter ab.

Das Import-Protokoll ist der zweite. Es berichtet, was bei einem Import geschah, und der Satz wurde
damals geschrieben und gespeichert. Neue Einträge folgen der eingestellten Sprache; die alten
bleiben, wie sie lauteten.

### Was englisch festgelegt ist und nicht mitwandert

Die Ordner `_done` und `_problem` im Eingang, der Sicherungsordner `kiekmap-backup/` samt allem
darin, und der `status` von `/health`. Die ersten beiden sind Namen im Dateisystem: Folgten sie der
Einstellung, müsste ein Umstellen Ordner umbenennen — auf dem Gerät und auf jedem schon
geschriebenen Stick. Der dritte ist ein Maschinenwert, den der Kiosk-Dienst liest.

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
