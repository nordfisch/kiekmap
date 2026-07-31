# Besucheransicht: Fehler und Verbesserungen

Sechs Punkte, die beim Durchsehen der Kioskansicht aufgefallen sind — ein handfester Fehler, zwei
Sackgassen in der Bedienung und drei Verbesserungen. Die Liste ist vollständig.

---

## Wie dieser Plan abgearbeitet wird

**Diese Datei wird als `docs/besucheransicht.md` ins Repo gelegt und als Erstes committet**, wie
schon die Pläne für die Hausnummern und das Verwaltungsmenü — damit sie einen Kontextverlust
überlebt. Die Häkchen unten werden im Repo mitgeführt: Wer nach einem Reset wieder aufsetzt, liest
sie und macht dort weiter.

**Wo stehe ich?** `git log --oneline` gegen die Tabelle halten. Jeder Schritt ist genau ein Commit
mit der dort genannten Nachricht; was committet ist, ist fertig **und** geprüft.

**Vor jedem Commit:** `make lint && make test` und `npx tsc -b --noEmit` (im Ordner `frontend`).
Commit-Nachrichten deutsch, ohne Umlaute, mit `Co-Authored-By: Claude Opus 5`.

**Zum Prüfen am laufenden System** (die Erfahrungen aus den letzten Sitzungen, damit sie nicht
zweimal gemacht werden müssen):

- Dienste über `preview_start` mit den Namen `backend` und `frontend`, nicht über die Shell.
- Admin-PIN lokal **4711**; in die Verwaltung führt ein Klick auf `.admin-gate` (das Wappen).
- Der Screenshot-Kompositor zeichnet nach einer Navigation oft verkleinert — ein `resize_window`
  erzwingt einen sauberen Neuaufbau.
- Zustand geht zwischen zwei `javascript_tool`-Aufrufen verloren; einen Ablauf deshalb **in einem**
  Aufruf durchspielen (anmelden, klicken, messen).
- **Ein Klick auf die Karte setzt bei laufender Ortsfrage einen Pin.** Zum Zoomen die
  Bedienelemente oder das Mausrad nehmen, sonst legt man versehentlich einen Besucherbeitrag an.
- Prüfstick für den Import: `hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK …`, dazu
  `PHOTOMAP_MEDIA_DIR=/Volumes` in `backend/.env` (steht dort schon).

## Reihenfolge und Abhängigkeiten

| # | Schritt | hängt ab von | Commit | erledigt |
|---|---|---|---|---|
| 0 | Plan ins Repo | — | `docs: Plan fuer die Besucheransicht` | ☑ |
| 1 | **Punkt 2** — Trennlinien weg, Titel größer, „Hilf mit" angeglichen | — | `style(kiosk): Ruhigeres Bild in der Besucheransicht` | ☑ |
| 2 | **Punkt 1** — feste Zeitachse, Schieber bleibt in seinem Feld | — | `fix(kiosk): Zeitachse spannt ueber den ganzen Bestand` | ☑ |
| 3 | **Punkt 3** — „Wann war das?", Jahrzehnte aus dem Bestand | 2 | `refactor(kiosk): Jahrzehnte kommen aus dem Bestand` | ☑ |
| 4 | **Punkt 4** — Bereich springt nach oben, Beitrag wird sichtbar | 2 | `feat(kiosk): Der eigene Beitrag wird sofort sichtbar` | ☑ |
| 5 | **Punkt 5** — Fotos am selben Ort als ein Stapel | — | `feat(kiosk): Fotos am selben Ort blaetterbar` | ☑ |
| 6 | **Punkt 6** — Vorschaubild im Beitragsbereich öffnet das Vollbild | 5 | `feat(kiosk): Foto im Beitragsbereich gross ansehen` | ☑ |
| 7 | Abschluss: CHANGELOG, `docs/kuratoren-anleitung.md`, Durchgang über alles | 1–6 | `docs: Aenderungen an der Besucheransicht` | ☑ |

**Warum diese Reihenfolge:**

- **Punkt 2 zuerst**, weil es die kleinste, isolierteste Änderung ist — reines CSS und drei Texte.
  Danach sieht bei jeder weiteren Prüfung schon alles so aus, wie es aussehen soll.
- **Punkt 1 ist das Fundament.** Es führt `collection_from`/`collection_to` ein — die Spanne des
  Bestands. Punkt 3 leitet daraus die Jahrzehnte ab, Punkt 4 braucht sie als „ganz auf".
  **Beide sind ohne Punkt 1 nicht baubar.**
- **Punkt 5 vor Punkt 6:** Punkt 5 baut `openPhotoId` zu `openStack`/`openIndex` um. Punkt 6 hängt
  sich an `openPhoto()` — das lohnt erst, wenn diese Schnittstelle ihre endgültige Form hat.
- **Punkt 4 und Punkt 5 greifen ineinander**, ohne sich zu bedingen: Punkt 5 sortiert die
  Kartenabfrage nach `updated_at`, wodurch das eben ergänzte Foto im Stapel obenauf liegt — genau
  dort, wohin Punkt 4 die Karte fährt. Wer 5 vor 4 baut, verliert nichts; die Reihenfolge oben ist
  nur die bequemere.

**Falls unterwegs Schluss ist:** Ein angefangener Schritt wird nicht halb committet. Entweder er
ist fertig und geprüft, oder er beginnt beim nächsten Mal von vorn — bei dieser Größe kostet das
weniger, als einen halben Zustand zu verstehen.

---

## Punkt 1 — Der Zeitschieber läuft aus seinem Feld

### Was passiert

Nach dem Hineinzoomen auf das Fotopaar am Friedhofsweg (beide „1950er") steht auf der Skala
**1950–1960**, in der Auswahl aber weiterhin **1920 bis 2019**. Die Elemente rechnen ihre Position
in Prozent der neuen Achse aus:

```
.timeline__selected   left: -300%  right: -590%   →  x = -2373 … 6557 px
.timeline__handle     left: -300%                 →  x = -2400 px  (ausserhalb des Bildschirms)
.app__title                                       →  x =     0 …  288 px
```

Der Auswahlbalken ist 8930 px breit und läuft quer über Wappen und Titel. Geklammert wird nirgends
— weder im Code noch per CSS.

### Ursache

`fullRange` (die Achse) kommt aus dem Histogramm des **sichtbaren Ausschnitts** und ändert sich bei
jedem Zoom; `timeRange` (die Auswahl) wird bewusst nicht mitgezogen
(`store/kiosk.ts:127` — „A selection already made stays untouched"). Sobald der neue Ausschnitt
eine engere Zeitspanne hat als die Auswahl, zeigt der Schieber ins Nichts.

Das ist kein Randfall: Es passiert bei jedem Hineinzoomen in einen Bereich, dessen Fotos aus
weniger Jahrzehnten stammen als der Gesamtbestand — im Museum also ständig.

### Entscheidung (mit dem Nutzer geklärt): feste Achse

Die Achse spannt künftig über den **ganzen Bestand** und steht still. Nur die Balken darunter
zeigen, was im sichtbaren Ausschnitt liegt.

Damit verschwindet nicht nur der Fehler, sondern auch die Ursache dahinter: Heute bedeutet dieselbe
Stelle des Schiebers nach jedem Zoom ein anderes Jahr. Für jemanden, der einmal im Leben davorsteht,
ist ein Bedienelement, das seine Bedeutung unter der Hand ändert, kaum zu durchschauen. Und eine
leere Achse mit einem einzelnen Balken bei 1950 sagt etwas, das die mitskalierende Achse verschweigt:
*hier gibt es nur Fotos aus den 1950ern.*

Am Verhalten der Karte ändert sich dabei **nichts**: `queryTimeFilter()` schickt keinen Zeitfilter,
solange die Auswahl die ganze Spanne abdeckt — vorher wie nachher.

### Änderungen

**Backend** — `app/api/photos.py`, `histogram()`

`earliest`/`latest` heißen künftig **`collection_from` / `collection_to`** und werden **ohne den
Kartenausschnitt** berechnet: `min()` über `date_from` und `max()` über `date_to` aller
veröffentlichten, datierten Fotos. Zwei Aggregate mehr je Abfrage.

Die Umbenennung gehört dazu: `earliest` an einer Histogramm-Antwort liest sich wie „das früheste
dieser Balken", und genau das ist es dann nicht mehr. `undated` bleibt ausschnittsbezogen — es sagt
aus, was gerade nicht auf der Karte ist.

`app/schemas.py`: `Histogram` entsprechend.

**Frontend**

- `api/client.ts` — `Histogram`-Typ nachziehen.
- `store/kiosk.ts`, `loadHistogram()` — `fullRange` aus den neuen Feldern. Der Kommentar bei
  `timeRange: timeRange ?? span` wird angepasst: Die Spanne ändert sich beim Verschieben der Karte
  jetzt gar nicht mehr.
- **Neu `kiosk/zeitachse.ts`** — die Rechnung, die gebrochen ist, als reine Funktionen:
  `axisBounds(fullRange)` (das heutige `roundToDecade`-Paar), `fraction(year, bounds)` **auf 0…1
  geklammert** und `clampRange(range, bounds)`.
- `kiosk/TimeSlider.tsx` — benutzt sie. Die Klammer auf 0…1 ist der bauliche Riegel: Selbst wenn
  Achse und Auswahl je wieder auseinanderlaufen, kann kein Element mehr aus seiner Zelle laufen.
- `store/kiosk.ts`, `setTimeRange()` — `clampRange()` beim Setzen, damit der Zustand gar nicht erst
  ungültig wird.

**Der leere Ausschnitt.** Heute wird der ganze Schieber durch einen Satz ersetzt, sobald der
Ausschnitt keine datierten Fotos enthält (`TimeSlider.tsx:116`). Mit fester Achse bleibt er stehen
und zeigt eine leere Fläche — die Ansicht springt nicht mehr zwischen zwei Bauformen. Der Satz
„Für diesen Ausschnitt gibt es keine datierten Fotos." rutscht in die Kopfzeile, an die Stelle von
„4 Fotos ohne Jahr", wenn es auch keine undatierten gibt. Nur bei **leerem Bestand** (kein einziges
datiertes Foto) bleibt die heutige Ersatzanzeige.

### Prüfung

- `backend/tests/test_api_photos.py`: `test_spanne_ignoriert_den_kartenausschnitt` — ein Foto
  ausserhalb der `bbox` muss die Achse trotzdem aufspannen. Das ist der ganze Punkt.
- Neu `frontend/src/kiosk/zeitachse.test.ts`:
  `test_auswahl_ausserhalb_der_achse_bleibt_im_bild` (der Fehler von oben, als Rechnung),
  `test_jahrzehnte_runden_die_achse_auf`.
- `frontend/src/store/kiosk.test.ts`: `test_zoomen_veraendert_die_achse_nicht`.
- Am laufenden System: auf das Paar am Friedhofsweg zoomen und nachmessen, dass kein Element des
  Schiebers links von seiner Zelle (x ≥ 288 px) liegt; danach wieder herauszoomen und prüfen, dass
  die Auswahl unverändert dasteht.

---

## Punkt 2 — Ruhigeres Bild: Trennlinien weg, Titel größer

### Kontext

Die vier Bereiche sind heute durch Rahmenlinien getrennt, und der Titelbereich steht neben einem
Wappen, das anderthalbmal so hoch ist wie die Schrift daneben. Beides gibt der Ansicht mehr
Formular als Ausstellung.

### Änderungen

**Alle vier Trennlinien fallen** (`styles/global.css`): `.app__title` verliert `border-right` und
`border-bottom`, `.timeline` ihr `border-bottom`, `.help-panel` ihr `border-right`. Die Bereiche
unterscheiden sich danach nur noch durch den Papierton gegen die Karte — das ist die einzige
Kante, die eine Aufgabe hat.

**Der Titel neben dem Wappen** (`texte/de.ts`, `styles/global.css`):

| | heute | neu |
|---|---|---|
| `t.app.titleLead` | „Bilder aus unserem" | **„Bilder aus"** |
| `.app__heading-lead` | 0,95 rem | **1,15 rem** |
| `.app__heading-place` | 1,6 rem | **1,9 rem** |

Zusammen mit `line-height: 1.15` ergeben die beiden Zeilen dann rund 63 px — genau die Höhe des
Wappens (3,5 rem). Beim Umsetzen nachgemessen, nicht geschätzt.

**„Hilf mit" bekommt dieselbe Form wie „Bilder aus".** Die beiden Regeln stehen als **eine**
Selektorgruppe in `global.css`, damit sie nicht wieder auseinanderlaufen:

```css
.app__heading-lead,
.help-panel__title {
  font-size: 1.15rem;
  font-weight: 400;
  color: var(--muted);
}
```

> **Eine Folge, die ich benenne, ohne sie zu ändern:** „Hilf mit" steht heute in Akzentbraun und
> 1,4 rem — es ist der einzige Blickfang der linken Spalte. Nach der Angleichung ist es eine
> stille graue Zeile wie „Bilder aus". Wenn der Beitragsbereich seinen Zug auf das Auge behalten
> soll, wäre das die Stelle, an der er ihn verliert.

### Prüfung

Am laufenden System: Titelzeilen und Wappen nachmessen (beide Zeilen zusammen ≈ Wappenhöhe), und
prüfen, dass keine der vier Kanten mehr eine Linie zeichnet. Screenshot in 1280 × 800 und in der
Auflösung des Museumsgeräts, sobald sie feststeht.

---

## Vorgemerkt — Zeitschieber aufräumen (optional, später)

Zurückgestellt auf Wunsch des Nutzers; hier festgehalten, damit es nicht verlorengeht:

- Die Kopfzeile über dem Schieber soll weg — sowohl „1920 bis 2019" als auch „x Fotos ohne Jahr".
- **Vorher zu klären:** Mit der Kopfzeile verschwindet die einzige Stelle, an der der gewählte
  Zeitraum als Zahl steht. Bleibt es bei der Skala unter dem Schieber (die beiden Enden der
  Achse), oder tragen die Griffe ihre Jahreszahl mit sich?
- **Daran hängt eine zweite Frage:** Ohne Kopfzeile braucht die obere Zeile weniger als die
  heutigen 9 rem. Schrumpft sie auf etwa 6,5 rem, gewinnt die Karte die Differenz.
- Aus Punkt 1 kommt hinzu: Der Satz „Für diesen Ausschnitt gibt es keine datierten Fotos." ist
  dort in die Kopfzeile eingeplant. Fällt sie, muss er woanders hin — oder ganz weg, denn die
  Karte sagt mit „Hier gibt es noch keine Fotos im gewählten Zeitraum." ohnehin dasselbe.

---

## Punkt 3 — Datierungsfrage und Jahrzehnte

### Was gewünscht ist

- `t.help.askDate`: „Von wann ist dieses Bild?" → **„Wann war das?"** — dieselbe knappe Form wie
  „Wo ist das?" bei der Ortsfrage.
- Zur Auswahl stehen die Jahrzehnte **1920er bis 2010er** statt heute 1860er bis 1990er.

### Der eigentliche Fund: die Angabe steht am falschen Ort

`firstDecade`/`lastDecade` stehen heute in `tiles/region.json`. Dort beschreibt jeder andere
Schlüssel Geografie — `bbox`, `center`, Zoomstufen — und die Datei wird vom Kartenbau gelesen. Was
die Sammlung umspannt, hat damit nichts zu tun. Genau diese Fehlablage zog beim Ändern zweier
Jahreszahlen den Kartenbau und einen Netzzugang hinter sich her.

**Die Angabe verschwindet deshalb ersatzlos aus `region.json`.** Damit ist die Datei wieder das,
was sie sein soll: die Beschreibung eines Ortes.

*(Der zuvor hier eingeplante Umbau — `make region`, ein eigenes Verteilskript, eine Baumarke — ist
gestrichen. Er hätte den falschen Ort bequemer erreichbar gemacht, statt ihn zu räumen. Die übrigen
Laufzeitschlüssel in `region.json` teilen die Verflechtung zwar weiterhin, sie ändern sich aber nur
beim Einrichten, wenn ohnehin Kacheln gebaut werden.)*

### Woher die Jahrzehnte stattdessen kommen

**Aus dem Bestand, mit einem garantierten Mindestfenster.** Angeboten wird die Vereinigung aus:

- der Spanne, die die Sammlung tatsächlich umfasst — dieselbe Zahl, die Punkt 1 als
  `collection_from`/`collection_to` einführt, auf Jahrzehnte gerundet, und
- dem festen Fenster **1920er bis 2010er**.

Für Holm heißt das heute genau 1920er…2010er. Findet sich später ein Foto von 1890, wächst die
Reihe nach vorn, sobald das Team es im Editor datiert hat — von selbst, ohne dass jemand eine
Einstellung sucht.

```ts
// frontend/src/region.ts -- ersetzt DEFAULT_DECADES
export const MINIMUM_DECADES = { first: 1920, last: 2010 };
```

Das ist kein sammlungsabhängiger Wert im Code, sondern die Untergrenze für alle: Ein Kiosk ohne
datiertes Foto hätte sonst überhaupt keinen Knopf, und ein Bestand, der zufällig nur die 1950er
umfasst, ließe einen Besucher nicht sagen, was er weiß. `DEFAULT_DECADES` (1860/1990) steht heute
schon als genau so ein Fallwert dort — er bekommt nur eine klarere Rolle und passendere Zahlen.

### Änderungen

- `frontend/src/texte/de.ts` — `help.askDate`.
- `tiles/region.json` — `firstDecade`/`lastDecade` samt ihrem Absatz im `$kommentar` entfernen.
- `frontend/src/region.ts` — `DEFAULT_DECADES` → `MINIMUM_DECADES`; die beiden optionalen Felder
  fallen aus dem `Region`-Typ.
- **Neu `frontend/src/kiosk/jahrzehnte.ts`** — `offeredDecades(collection: TimeRange | null)` als
  reine Funktion: runden, vereinigen, aufzählen.
- `frontend/src/kiosk/DateTask.tsx` — nimmt die Liste von dort und die Spanne aus
  `useKiosk(s => s.fullRange)`. **Die `region`-Eigenschaft entfällt** — sie war nur für die
  Jahrzehnte da. `HelpPanel` reicht sie dann ebenfalls nicht mehr durch, und `App.tsx` übergibt sie
  nicht mehr.
- `docs/adaption.md` — der Absatz über `firstDecade`/`lastDecade` wird zu einem Satz darüber, dass
  sich die Auswahl aus dem Bestand ergibt.

> **Reihenfolge:** Dieser Punkt setzt Punkt 1 voraus — die Spanne des Bestands entsteht dort.

### Prüfung

- Neu `frontend/src/kiosk/jahrzehnte.test.ts`:
  `test_leerer_bestand_zeigt_das_mindestfenster`,
  `test_aelteres_foto_erweitert_die_reihe_nach_vorn` (Bestand ab 1890 → erster Knopf 1890er),
  `test_bestand_innerhalb_des_fensters_aendert_nichts`.
- Am laufenden System: „Hilf mit" → die Frage lautet „Wann war das?", darunter zehn Knöpfe von
  1920er bis 2010er. Ein Jahrzehnt wählen, ein Jahr, und in der Verwaltung nachsehen, dass die
  Datierung ankommt.

---

## Punkt 4 — Der Beitrag wird sichtbar

### Kontext

Heute endet ein Beitrag mit einem Dank und einem Nachladen von Markern und Histogramm. Ob das
Foto danach wirklich zu sehen ist, hängt davon ab, wo die Karte gerade steht — meist ist es das
nicht. Und der „Hilf mit"-Bereich bleibt beim nächsten Foto dort stehen, wo der Finger ihn zuletzt
hingeschoben hat.

### 4a — Der Bereich springt nach oben

`HelpPanel.tsx` bekommt eine Referenz auf `<aside className="help-panel">` (die Spalte scrollt
selbst, `overflow-y: auto`) und setzt `scrollTop` auf 0, sobald sich **Foto, Frage oder
Dank-Zustand** ändern. Damit sind alle drei genannten Fälle abgedeckt: abgeschlossen, weggetippt
(„Weiß ich nicht") und der Wechsel der Fragestellung.

*(Die Zwischenschritte innerhalb einer Aufgabe — „Andere Straße", „Anderes Jahrzehnt" — lassen den
Bereich stehen. Dort bleibt der Blick ohnehin an derselben Stelle.)*

### 4b — Die Ansicht rechts stellt sich auf das Foto ein

**Die Angaben kommen aus erster Hand:** `postLocation()` und `postDate()` geben das aktualisierte
`PhotoDetail` zurück; `contribute()` in `store/contribute.ts` wirft es heute weg. Künftig reicht es
das Foto an den Kiosk-Store weiter, statt dass irgendwo Ort oder Jahr nachgeraten werden.

Eine neue Aktion `showPhoto(photo)` in `store/kiosk.ts` stellt daraufhin **beides** ein — Karte und
Schieber —, und zwar nur für die Dauer des Dankes. Welcher der beiden Wege den Beitrag ausgelöst
hat, spielt dabei keine Rolle; entschieden wird allein nach dem Foto, wie es jetzt dasteht:

| Das Foto hat … | Karte | Zeitraum |
|---|---|---|
| Ort **und** Jahr | 100 m um den Ort | das **Jahrzehnt** des Jahres (1932 → 1930–1939) |
| Ort, **kein** Jahr | 100 m um den Ort | **ganz auf**, also die volle Spanne |
| keinen Ort | nichts | nichts |

Die mittlere Zeile ist nicht nur Aufräumen, sie deckt eine falsche Zusage ab: Undatierte Fotos
stehen auf der Karte, **solange kein Zeitfilter aktiv ist** (`_viewport_filters` in
`app/api/photos.py` prüft das Datum nur bei gesetztem Zeitraum). Wer den Schieber eingeengt hat und
dann ein undatiertes Foto verortet, bekäme sonst eine leere Stelle zu sehen — unter dem Satz „Das
Foto ist jetzt auf der Karte".

Die letzte Zeile ebenso: Ein Foto ohne Ort ist auf keiner Karte zu finden. Den Schieber trotzdem
zu verstellen, würde nur andere Fotos ausblenden, ohne dass etwas sichtbar würde.

**Beides kehrt zurück, und zwar zusammen.** Der Zoom und die Schieberstellung halten genau so lange
wie der Dank (2,2 s); danach fährt die Karte dorthin zurück, wo der Besucher vorher war, und der
Zeitraum auf den Wert, den er vorher hatte. Nichts von dem, was der Besucher selbst eingestellt
hat, geht dabei verloren — und die nächste Frage („Wo ist das?") steht nicht vor einer Karte auf
100 m Radius, aus der man sich mit zwei Fingern erst wieder herausarbeiten müsste.

Für die zwei Sekunden ist das Verstellen des Schiebers zugleich eine Auskunft: Wer eben „1932"
getippt hat, sieht die Griffe auf die 1930er springen und sein Foto darin auftauchen.

### Bauform

Die Karte gehört `MapView`, der Zustand dem Store — die Brücke ist ein Signal, wie beim
Leerlauf-Rücksprung, der aus demselben Grund in `MapView` wohnt:

- `store/kiosk.ts` — ein **Fokus** als ein Stück Zustand, nicht zwei:
  ```ts
  focus: { lat, lon, radiusM, seq } | null;   // wohin die Karte
  rangeBefore: TimeRange | null;              // was der Besucher eingestellt hatte
  ```
  `showPhoto(photo)` legt den bisherigen Zeitraum in `rangeBefore` ab, setzt den neuen und den
  Fokus. `releaseFocus()` nimmt **beides zusammen** zurück. Das `seq` sorgt dafür, dass zweimal
  derselbe Ort auch zweimal auslöst.
- `store/contribute.ts` — `contribute()` ruft `showPhoto(aktualisiertesFoto)`; der Dank-Zeitgeber,
  der ohnehin schon `thanks` zurücknimmt und die nächste Aufgabe lädt, ruft dabei
  `releaseFocus()`. Beide Verstellungen leben damit exakt so lange wie der Dank, ohne einen
  zweiten Zeitgeber — und enden im selben Wimpernschlag.
- `kiosk/MapView.tsx` — ein Effekt auf `focus`: Kamera merken, `fitBounds` auf das 200-m-Quadrat;
  die **Aufräumfunktion** des Effekts fährt zur gemerkten Kamera zurück. Mit demselben
  `disposed`-Riegel wie beim `load`-Rückruf, sonst bewegt sie eine bereits entfernte Karte.
- **Neu `kiosk/fokus.ts`** — die Entscheidungen als reine Funktionen:
  `decadeOf(dateFrom)`, `rangeForPhoto(photo, fullRange)` (die Tabelle oben) und
  `boundsAround(lat, lon, radiusM)`.
- `reset()` (Leerlauf) löscht Fokus und `rangeBefore` mit — sonst spielte ein Rücksprung mitten im
  Dank einen alten Zeitraum zurück.

> **Die Rückgabe muss auch dann stimmen, wenn zweimal hintereinander beigetragen wird.** Der
> Dank-Zeitgeber wird beim zweiten Beitrag neu gesetzt (`showThanks` löscht den alten) — `showPhoto`
> darf `rangeBefore` deshalb **nur füllen, wenn es leer ist**. Sonst merkt sich der zweite Aufruf
> den Zeitraum des ersten Fokus, und der Besucher bekommt am Ende ein Jahrzehnt zurück, das er nie
> eingestellt hat.

> Die Kacheln reichen bis Zoom 15; 100 m Radius liegt darüber. MapLibre skaliert Vektorkacheln
> dabei sauber hoch, die Beschriftungen werden aber groß. Beim Umsetzen anzusehen — falls es
> unruhig wirkt, ist der Radius die Stellschraube, nicht die Bauform.

### Prüfung

- Neu `frontend/src/kiosk/fokus.test.ts`:
  `test_foto_mit_jahr_stellt_den_schieber_auf_das_jahrzehnt`,
  `test_foto_ohne_jahr_oeffnet_den_schieber_ganz` (der Fall mit der falschen Zusage),
  `test_foto_ohne_ort_laesst_die_ansicht_stehen`.
- `frontend/src/store/kiosk.test.ts`: `test_zweiter_beitrag_gibt_den_urspruenglichen_zeitraum_zurueck`
  — die Falle mit dem doppelt gemerkten Zeitraum.
- Am laufenden System, beide Wege: ein Foto verorten und zusehen, dass die Karte hinfährt, der
  Marker dort steht, der Schieber sich stellt — und dass **beide** nach dem Dank zurückkehren.
  Dann ein Foto datieren und prüfen, dass der Schieber auf dem Jahrzehnt der eben getippten Zahl
  steht. Dazu der Fall aus der mittleren Zeile: Schieber auf ein Jahrzehnt stellen, dann ein
  undatiertes Foto verorten — der Schieber muss ganz aufgehen, das Foto sichtbar werden, und
  danach muss das eingestellte Jahrzehnt wieder dastehen.
- Nach jedem Wechsel prüfen, dass der „Hilf mit"-Bereich oben steht: dazu vorher weit nach unten
  scrollen (Ortssuche mit vielen Treffern) und dann „Weiß ich nicht" tippen.

---

## Punkt 5 — Fotos am selben Ort

### Was heute passiert

Am Gasthof Petersen liegen acht Fotos auf **identischen** Koordinaten. `CLUSTER_MAXZOOM = 17` in
`kiosk/PhotoLayer.tsx` heißt: Ab Zoom 18 fasst supercluster nichts mehr zusammen — die acht werden
zu acht Markern, exakt übereinander, von denen nur der oberste erreichbar ist.

Und der Weg dorthin ist eine Sackgasse: Ein Tipp auf die „8" zoomt auf
`getClusterExpansionZoom` (gedeckelt auf 18) — genau in diesen Stapel hinein. **Identische Punkte
trennen sich bei keiner Zoomstufe.** Wer also mehr sehen will, tippt, zoomt, und hat danach
dieselbe Sackgasse in größer.

### Entscheidung (mit dem Nutzer geklärt): ein Marker, Vollbild mit Blättern

Fotos auf demselben Punkt werden **vor** dem Clustern zu einem Eintrag zusammengefasst. supercluster
sieht damit gar keine Dubletten mehr, und der Stapel ist auf jeder Zoomstufe **ein** Marker:

- **So dargestellt wie ein einzelnes Foto**, mit einer Anzahl in der Ecke („8"). Der Besucher sieht
  damit vor dem Tippen, dass mehr dahintersteckt — anders als beim heutigen anonymen Kreis.
- **Ein Tipp öffnet die Vollbildansicht** mit dem obersten Foto und zwei großen Knöpfen zum
  Blättern durch den Stapel („Vorheriges" / „Nächstes", dazu die Position: *3 von 8*).

Kein Kartentrick, kein Modus, keine Marker an falscher Stelle. Das Denkmodell bleibt
*ein Ort = ein Marker = die Fotos von dort*.

**Gruppiert wird auf fünf Nachkommastellen** (rund einen Meter). Das trifft den tatsächlichen Fall:
Fotos, die über die Ortssuche verortet wurden, tragen exakt dieselbe Koordinate der Straße. Wer
den Punkt von Hand gesetzt hat, liegt daneben und bleibt ein eigener Marker — richtig so, denn
dann *ist* es eine andere Stelle.

### Die Reihenfolge im Stapel

Oben liegt das zuletzt bearbeitete Foto. `app/api/photos.py`, `list_photos()` ordnet künftig nach
**`updated_at desc, imported_at desc, id desc`** statt nach `date_from, id`.

`Photo.updated_at` gibt es bereits mit `onupdate=func.now()` (`app/models.py:84`) — jeder
Besucherbeitrag und jede Bearbeitung im Verwaltungsbereich setzt es neu. Damit steht das eben
verortete oder datierte Foto von selbst obenauf, was mit Punkt 4 zusammenspielt: Die Karte fährt
hin, und das Foto liegt oben.

### Änderungen

- `app/api/photos.py` — die neue Sortierung. Sie bestimmt zugleich, welches Vorschaubild den Stapel
  vertritt.
- **Neu `frontend/src/kiosk/stapel.ts`** — `groupByLocation(photos)` als reine Funktion: gleiche
  gerundete Koordinate, Reihenfolge erhalten.
- `frontend/src/kiosk/PhotoLayer.tsx` — gruppiert vor `buildIndex()`; ein Stapel wird zu einem
  Marker mit Anzahl, der `openStack(ids)` auslöst. Die bestehende Cluster-Logik bleibt für
  Fotos, die tatsächlich nebeneinander liegen — dort ist Hineinzoomen weiterhin die richtige
  Antwort.
- `frontend/src/store/kiosk.ts` — `openPhotoId: number | null` wird zu
  `openStack: number[]` **plus** `openIndex: number`; `openPhoto(id)` bleibt als Kurzform für einen
  einzelnen. Blättern heißt dann nur, `openIndex` zu bewegen.
- `frontend/src/kiosk/PhotoOverlay.tsx` — zwei Knöpfe und die Positionsangabe; die Pfeiltasten
  blättern mit, wie heute schon Escape schließt. Bei einem Stapel von eins bleibt alles wie bisher.
- `frontend/src/texte/de.ts` — `overlay.prev`, `overlay.next`, `overlay.position(i, n)`,
  `map.stackLabel(count, title)` für die Beschriftung des Markers.
- `frontend/src/styles/global.css` — die Anzahl-Ecke am Marker, die beiden Blätterknöpfe
  (mindestens 48 px, am unteren Rand in Daumennähe).

### Prüfung

- Neu `frontend/src/kiosk/stapel.test.ts`: `test_gleiche_koordinate_wird_ein_marker`,
  `test_ein_meter_daneben_bleibt_ein_eigener_marker`,
  `test_reihenfolge_der_liste_bleibt_erhalten` (sonst läge nicht das zuletzt bearbeitete oben).
- `backend/tests/test_api_photos.py`: `test_zuletzt_bearbeitetes_foto_kommt_zuerst`.
- Am laufenden System: auf den Gasthof zoomen — **ein** Marker mit „8", nicht acht übereinander.
  Öffnen, durchblättern bis zum Ende, schließen. Danach ein Foto des Stapels im
  Verwaltungsbereich bearbeiten und prüfen, dass es anschließend oben liegt.

---

## Punkt 6 — Das Foto im „Hilf mit"-Bereich lässt sich groß ansehen

### Kontext

Das Vorschaubild im Beitragsbereich ist heute ein totes `<img>`. Dabei ist „genauer hinsehen"
genau das, was jemand tut, **bevor** er sagt, wo das war — auf einem 160 px breiten Bild ist ein
Hof kaum zu erkennen.

### Änderung

`kiosk/HelpPanel.tsx` — das `<img className="help-panel__image">` bekommt einen Knopf darum, wie
ihn die Marker auf der Karte schon haben, und öffnet dieselbe Vollbildansicht:

```tsx
<button type="button" className="help-panel__zoom" aria-label={t.help.enlarge}
        onClick={() => useKiosk.getState().openPhoto(photo.id)}>
  <img className="help-panel__image" … />
</button>
```

`openPhoto(id)` bleibt nach Punkt 5 die Kurzform für ein einzelnes Foto — der Weg ist damit
buchstäblich derselbe wie beim Tippen auf einen Marker, samt Schließen per Tipp daneben, Knopf
oder Escape.

- `texte/de.ts` — `help.enlarge: "Foto groß anzeigen"`.
- `styles/global.css` — `.help-panel__zoom` ohne eigene Optik (kein Rahmen, kein Grund), nur mit
  `:active`-Rückmeldung wie beim Wappen. Es soll ein Bild bleiben, kein Knopf werden.

> Die Vollbildansicht legt sich über die Karte, nicht über den Beitragsbereich. Ein gesetzter Pin
> bleibt dabei erhalten — er liegt im Store, nicht in der Ansicht. Nach dem Schließen steht die
> angefangene Verortung also unverändert da.

### Prüfung

Am laufenden System: bei laufender Ortsfrage einen Pin setzen, das Vorschaubild antippen, die
Vollbildansicht schließen — der Pin muss noch stehen und „Hier war das" weiterhin bereit sein.

---

## Abschluss

Nach den sechs Punkten in einem letzten Schritt:

- **CHANGELOG** unter „Behoben" (der Zeitschieber) und „Geändert" (der Rest).
- **`docs/kuratoren-anleitung.md`** — dort steht nichts über die Besucheransicht, aber die
  Datierungsfrage taucht im Abschnitt über die Besucherbeiträge auf. Nachlesen, ob ein Satz
  nachzuziehen ist.
- **`docs/adaption.md`** — der Absatz über `firstDecade`/`lastDecade` (siehe Punkt 3).
- **`docs/decisions.md`** — zwei Entscheidungen gehören dorthin, weil sie Grundsätzliches
  festlegen: die feste Zeitachse (Punkt 1) und der Stapel statt Auffächern (Punkt 5).
- Ein Durchgang über die ganze Ansicht auf einem Bildschirm in Museumsgröße, mit Screenshots.

---

## Offen, bewusst nicht eingeplant

- Die Kopfzeile des Zeitschiebers (siehe „Vorgemerkt" oben).
- Der Radius von 100 m aus Punkt 4 liegt über der Kachelauflösung (Zoom 15). Falls die
  Beschriftungen dabei unruhig wirken, ist der Radius die Stellschraube.
- „Hilf mit" verliert in Punkt 2 seine Akzentfarbe und wird eine stille graue Zeile. Sollte der
  Beitragsbereich seinen Zug auf das Auge behalten sollen, wäre das die Stelle.
