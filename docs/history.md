# Entstehung

Was gebaut wurde, in der Reihenfolge, in der es gebaut wurde — und vor allem: **was dabei anders
kam als geplant.** Das ist der Zweck dieser Datei. Sie ist aus den drei Plandokumenten
zusammengeführt, die inzwischen unter [archiv/](archiv/) liegen.

Drei Dateien beschreiben dasselbe Projekt und beantworten drei verschiedene Fragen:

| Datei | Frage |
|---|---|
| [../CHANGELOG.md](../CHANGELOG.md) | *Was kann das Programm?* — sortiert nach Keep a Changelog |
| [decisions.md](decisions.md) | *Warum ist es technisch so gebaut?* — die Grundsatzentscheidungen |
| **history.md** | *Wie ist es dazu gekommen?* — die Reihenfolge und die Überraschungen |
| [backlog.md](backlog.md) | *Was fehlt noch?* |

Die Überraschungen sind das, was sonst niemand aufschreibt. Sie stehen hier als
*„Was der Plan nicht wusste"* und sind der eigentliche Grund für diese Datei.

## Die Arbeitsblöcke

| | Block | Zeitraum | Commits |
|---|---|---|---|
| I | Die Stufen 0 bis 10 | 28.–30. Juli 2026 | `0e0dc23` … `9c89c9f` |
| II | Umbau des Verwaltungsmenüs | 30. Juli 2026 | `63828e2` |
| III | Nachbesserungen an der Verwaltung | 30.–31. Juli 2026 | `850db95` … `b4a9f6f` |
| IV | Besucheransicht: Fehler und Verbesserungen | 31. Juli 2026 | `cc5a437` … `006f9ee` |
| V | Nachbesserungen an der Besucheransicht | 31. Juli – 2. August 2026 | `2f773f1` … `b20ff5c` |
| VI | Einzelne Punkte aus dem Backlog | ab 2. August 2026 | `a3a5be7` … `b064e62` |

---

# Teil I — Die Stufen 0 bis 10

Der ursprüngliche Bauplan sah elf Stufen vor, jede in einem lauffähigen, committeten Zustand
endend, jede mit einem Abnahmekriterium in der Form *„Fertig, wenn …"*. Zehn davon sind gebaut.

## Stufe 0 — Gerüst und Entscheidungen

`0e0dc23` · Ordnerstruktur, Git-Repo, README, `docs/decisions.md`, `tiles/region.json` als
Platzhalter für den Museumsort.

Die Entscheidungsdatei stand **vor** dem ersten Backend-Commit. Das war kein Formalismus: Aus ihr
folgt, dass nichts Ortsspezifisches in den Code kommt — die Eigenschaft, die ein zweites Museum
ohne Fork möglich macht und die sich später nicht mehr nachrüsten ließe.

## Stufe 1 — FastAPI, SQLite, Alembic, Docker

`a91e99e` · Backend mit `/api/health`, SQLite im WAL-Modus, Migrationen, Dockerfile.

Migrationen laufen beim Containerstart automatisch (`backend/docker-entrypoint.sh`) — auf dem Pi
soll niemand daran denken müssen.

## Stufe 2 — Frontend-Gerüst und Offline-Karte

`022b921`, `29b1d62` · React mit MapLibre, Vektorkacheln aus einer PMTiles-Datei, nginx mit
Range-Requests, `tiles/build-tiles.sh`, Region Holm festgelegt.

**Was der Plan nicht wusste:** Der Protomaps-Kartenstil verweist standardmäßig auf
`protomaps.github.io`. Schriften und Symbole mussten mit heruntergeladen und unter
`frontend/public/basemaps/` abgelegt werden — sonst hätte die Karte offline zwar Flächen, aber
keine Beschriftung. Seither gilt die Prüfung: **null Anfragen an eine fremde Herkunft.**

## Stufe 3 — Import-Pipeline

`8e82447` · Datenmodell und Import: SHA-256 als Dateiname und Dublettenschutz, EXIF und IPTC,
Vorschaubilder in zwei Größen, EXIF-Ausrichtung, CMYK-Umwandlung, überwachter Eingangsordner,
`python -m app.cli import|scan|stats`.

Hier entstand die Regel, die das ganze Datenmodell prägt: **ein EXIF-Datum ab 1990 ist das Datum
des Scans und datiert das Foto nicht.** Ohne sie läge ein Foto von 1932 auf der Zeitleiste bei
2019 — und gälte damit als datiert, würde also nie zur Korrektur vorgelegt. Der Fehler wäre still.

Der Eingangsordner räumt Aufgenommenes nach `_erledigt/` bzw. `_problem/`. **Gelöscht wird nie.**

## Stufe 4 — Abfrage-API

`bb4faad` · `/api/photos` mit Kartenausschnitt und Zeitraum, `/histogram`, Auslieferung von
Vorschaubild und Original mit dauerhaftem Cache.

Die zweite stille Falle des Projekts: Datierungen sind **Intervalle**, keine Zeitpunkte. Der
Zeitfilter fragt deshalb auf **Überlappung** ab (`date_from <= bis AND date_to >= von`), nicht auf
Enthaltensein. Bei der naiven Abfrage verschwände der Großteil des Bestands lautlos aus der
Ansicht — ein auf „1920er" datiertes Foto erschiene bei der Auswahl 1925–1930 nicht.

## Stufen 5 und 6 — Karte mit Markern, Zeitschieber

`0a6b074` · Fotos als Vorschaubilder an ihrem Aufnahmeort, supercluster bei hoher Dichte,
Foto-Overlay in voller Größe, Zeitschieber mit zwei Griffen und Jahrzehnt-Histogramm.

Kartenbewegung und Zeitraum lösen entprellt genau eine Abfrage aus; überholte werden verworfen.

**Was der Plan nicht wusste:** Zeigerereignisse kommen schneller, als React rendert. Der gezogene
Slider-Griff steht deshalb in einem Ref, nicht nur im State — sonst bleibt er bei einer zügigen
Wischbewegung kleben.

## Stufe 7 — „Hilf mit"

`2f6b3d6` · Zufällige Fotos ohne Ort oder Jahr, Verortung per Pin auf der Karte oder über die
Ortssuche, Datierung über Jahrzehnt und optional Jahr, Ortsindex aus OpenStreetMap
(`tiles/build-places.py`).

Besucherbeiträge werden **direkt übernommen**, aber nur in leere Felder: Kuratierte Angaben sind
unantastbar, Koordinaten außerhalb der Region werden abgewiesen. Die Suche findet „Mühlenweg" auch
bei Eingabe ohne Umlaut und läuft ohne Internet.

## Stufe 7.5 — Sprachregelung

`09f1f62`, `2622975`, `29a276e`, `b8ee5a6`, `dcd1f93` · Bezeichner und Code-Kommentare
durchgängig englisch, Oberflächentexte in `frontend/src/texte/de.ts`, `CLAUDE.md`,
`docs/development.md`, `docs/adaption.md`, der Stufenplan.

Der Grund ist nicht Konvention um ihrer selbst willen: `def zeitraum(...) -> DatePrecision` erzeugt
an jeder Grenze zum Bibliothekscode einen Bruch. **Testnamen bleiben die Ausnahme und deutsch** —
sie sind Spezifikationssätze, keine Bezeichner, und `test_scandatum_datiert_das_foto_nicht` ist die
wertvollste Dokumentation im Repo.

## Stufe 7.6 — Deutsche Texte im Backend nach Konvention ordnen

`ba3e978` · Bestandsaufnahme nach der Umstellung.

Query-Parameter `?von=…&bis=…` heißen seither `?from_year=…&to_year=…` (nicht `from`, das ist in
Python reserviert). Dabei entstand die **Faustregel**, die alle Grenzfälle ohne Einzelabwägung
entscheidet:

> *Kann diese Meldung im Kiosk oder im Admin-Bereich erscheinen? Dann Deutsch, sonst Englisch.*

Ein 404 auf ein gelöschtes Foto landet im Overlay des Besuchers — deutsch. Eine kaputte `bbox`
sieht nur, wer die API selbst aufruft — englisch. Die CLI ist die Ausnahme in der Ausnahme: Den
Erstimport führt auch das Museumsteam aus, ihre Ausgaben bleiben deutsch.

**Nebenbei ein Fehler, der schwer zu fassen war:** Marker verschwanden gelegentlich von der Karte.
Der `load`-Rückruf konnte eine bereits entfernte Karteninstanz an die Ebenen weiterreichen — die
Vorschaubilder wurden dann sogar geladen, waren aber nie zu sehen. Seither hat der Rückruf einen
`disposed`-Riegel, der später beim Fokus-Effekt (Teil IV, Punkt 4) noch einmal gebraucht wurde.

## Stufe 8 — Admin-Bereich mit Stapel-Upload

`2d237ff` · Klick auf das Ortswappen, PIN auf einem Zahlenfeld mit großen Tasten, Sitzung mit
Ablauf. Fotoliste mit Filter und Suche, Metadateneditor, Besucherbeiträge sichten und einzeln
zurücknehmen, Import-Protokoll, Statusübersicht. Stapel-Upload mit Ort und Jahr für den ganzen
Stapel und einer Nacharbeitstabelle.

**Anders als ursprünglich geplant:** Vorgesehen war ein drei Sekunden langer Druck auf die untere
linke Bildschirmecke — für Besucher unsichtbar. Das sichtbare Wappen hat gewonnen: Das Schloss ist
die PIN, nicht das Versteck, und eine unsichtbare Geste ist etwas, das Ehrenamtliche sich merken
müssten. Wer aus Neugier tippt, sieht ein Zahlenfeld und tippt „Zurück zur Karte".

Eine vierstellige PIN sind zehntausend Möglichkeiten, die ein Skript in Sekunden durchprobiert
hätte. **Das Gegengewicht ist die Sperre nach fünf Fehlversuchen** — sie macht aus Sekunden Jahre
und ist der eigentliche Schutz, nicht die Länge der PIN.

**Was der Plan nicht wusste:** Beim Bearbeiten muss ein **fehlendes** Feld „unverändert lassen"
heißen und ein **leeres** Feld „löschen". Ohne diesen Unterschied ließe sich eine falsche
Datierung nur durch eine andere ersetzen, nie durch „weiß man nicht" — und das Foto käme nie
wieder in den „Hilf mit"-Bereich. Pydantic hält die beiden über `model_fields_set` auseinander,
der Endpunkt liest `exclude_unset`.

Dazu: Das Zurücknehmen eines Besucherbeitrags wird verweigert, sobald das Feld inzwischen von Hand
bearbeitet wurde — sonst würde die Arbeit des Kurators mit weggeworfen.

*Fertig, wenn: du am Touchscreen ohne Tastatur hinein- und wieder hinauskommst, einen Stapel
hochladen und dabei Ort und Jahr für alle setzen kannst, und ein Foto vollständig über die
Oberfläche pflegen kannst.* ✅

## Das Raster der Kioskansicht

`45e56c0` · Zwei Spalten, zwei Zeilen: links Titelbereich über „Hilf mit", rechts Zeitschieber
über der Karte.

Der Schieber steht damit genau über der Karte, die er filtert — nicht über dem Beitragsbereich.
Das Wappen führt die linke Spalte an, statt die Karte zu verdecken, und ist zugleich der Weg in
die Verwaltung.

## Stufe 9 — Sicherung und Wiederherstellung auf USB

`bcbb873` · Stick einstecken, ein Knopf, Fortschrittsbalken, am Ende „Der Stick kann jetzt
abgezogen werden".

Bewusst eine **gestaltete Funktion, kein Shell-Skript**: Die Zielgruppe sind ältere Ehrenamtliche,
die das ein- bis zweimal im Jahr tun. Ein Skript bedeutet in der Praxis, dass es nie ausgeführt
wird. Ohne Stick steht dort nur „Bitte USB-Stick einstecken" — kein Knopf, der ins Leere führt.

Drei Bauentscheidungen und ihr Grund:

- **Ordner statt Archiv** auf dem Stick: Eine abgebrochene Sicherung ist dann teilweise brauchbar
  statt komplett wertlos, und man kann sie an jedem Rechner öffnen.
- **Inkrementell über die Hash-Dateinamen:** Liegt der Name schon dort, ist es dasselbe Bild — die
  zweite Sicherung dauert Sekunden.
- **`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Kiosk anzuhalten.

Wiederherstellen kopiert erst daneben und schaltet zuletzt um; der bisherige Stand wandert nach
`data/vorher-<Datum>/` und wird nie gelöscht. Eine abgebrochene Wiederherstellung darf den
laufenden Bestand nicht zerstören. Statt einer Automatik gibt es eine Erinnerung: „Letzte
Sicherung vor 34 Tagen", ab 30 Tagen rot.

**Was der Plan nicht wusste:** Ein Laufwerk muss ein echter Einhängepunkt **und** beschreibbar
sein. Ohne das Erste liefe die Sicherung auf dieselbe SD-Karte, gegen deren Ausfall sie schützt;
ohne das Zweite fiele ein schreibgeschützter Stick erst auf, nachdem jemand den Knopf gedrückt hat.

*Fertig, wenn: jemand aus der Zielgruppe die Sicherung ohne Hilfe und ohne Anleitung schafft — und
die Wiederherstellung auf einem zweiten, leeren Gerät nachweislich funktioniert.* — Die Funktion
ist gegen einen echten eingehängten Datenträger erprobt (sichern, inkrementell erneuern,
zurückspielen, Beiseitelegen). **Beide Hälften des Kriteriums brauchen aber das Gerät und die
Zielgruppe und stehen deshalb im [backlog](backlog.md).**

## Vormerkung erledigt: „Weiß ich nicht" wechselt die Frage

`af395f7` · Wer einen Ort nicht erkennt, weiß vielleicht trotzdem das Jahrzehnt. Dieselbe Frage
noch einmal ist der Grund, warum jemand nach drei Bildern aufhört.

**Was der Plan nicht wusste** — beziehungsweise: was er als Verdacht notierte und was sich
bestätigte: Läuft eine der beiden Fragen leer, muss das Laden auf die andere zurückfallen. Sonst
stünde „Zurzeit ist alles vollständig" auf dem Schirm, während Hunderte Fotos auf eine Jahreszahl
warten. Der Rückfall greift jetzt bei **jedem** Laden, nicht nur beim Wechseln — und behebt
denselben Fehler damit auch nach einem abgegebenen Beitrag.

## Der Dank lief ins Leere

`c9271f8` · **Karte und Zeitleiste blieben nach einem Besucherbeitrag stehen.** Der Dank versprach
„Das Foto ist jetzt auf der Karte", zu sehen war es aber erst, wenn jemand die Karte verschob und
damit eine neue Abfrage auslöste — also gerade bei den älteren Besuchern, für die der Bereich
gebaut ist, gar nicht. Der unmittelbare Effekt, der überhaupt der Grund für den „Hilf mit"-Bereich
ist, lief damit ins Leere.

`refresh()` lädt seither Marker **und** Histogramm nach: Ein verortetes Foto wandert aus „ohne
Ort" heraus, ein datiertes aus „ohne Jahr" in einen Jahrzehnt-Balken. Nicht entprellt, anders als
beim Kartenverschieben — ein Beitrag ist eine einzelne bewusste Handlung, und genau die soll sofort
sichtbar werden. Bei einem abgelehnten Beitrag (HTTP 409, jemand war schneller) wird nicht
nachgeladen; es hat sich nichts geändert.

## Kartenstil „Papier"

`09de5a5` · Erde in Papierton, Grün zu Salbei entsättigt, Wasser in mattem Graublau statt Türkis.

Die Regel beim Aussuchen: **Nichts auf der Karte darf so gesättigt sein wie ein Foto.** Dazu ohne
Geschäfte, Hausnummern und Autobahnschilder, und mit Straßen auf 80 % ihrer Breite — die kleinen
Straßennamen bleiben, an ihnen hängt die Verortung.

## Vormerkung erledigt: Hausnummern im Ortsindex

`7396564` · Verortung in zwei Schritten: Straße antippen, dann die Hausnummer aus einem
Knopfraster — oder „Reicht so", denn nicht jedes Haus steht in OpenStreetMap. Ohne sie bekam jedes
Foto einer 800 m langen Straße denselben Punkt.

**Was der Plan nicht wusste:** Es sind **7686 Adressen**, nicht „einige hundert bis zweitausend" —
die Bounding Box reicht über Holm hinaus. Der Ortsindex wuchs von 827 auf 8513 Einträge,
`places.json` von 130 kB auf 1,5 MB. Die Suche blieb trotzdem unter 6 ms. Der Lehmweg allein hat
139 Hausnummern — deshalb erscheinen Adressen in der freien Suche erst ab einer Ziffer in der
Eingabe, sonst wären die zwölf Plätze der Trefferliste von einer einzigen Straße belegt.

Dabei fand `location_accuracy_m` endlich seine Verwendung: 150 m für eine Straße, 15 m für eine
Hausnummer, nichts für einen von Hand getippten Punkt. Und Hausnummern werden natürlich sortiert —
1, 1a, 2, 9, 10, nicht 1, 10, 1a, 2, 9.

## Stufe 10 — Kiosk-Deployment auf dem Pi

`c159dbe` · Raspberry Pi OS **Lite** plus **cage**, ein winziger Wayland-Compositor, der genau ein
Programm im Vollbild anzeigt. Robuster als der volle Desktop: nichts kann sich in den Vordergrund
drängen, kein Hintergrundbild blitzt beim Booten auf, keine Update-Hinweise, kein
Bildschirmschoner.

Ablauf nach dem Einschalten (~20 s): Docker startet, die Container laufen von selbst hoch;
`photomap-kiosk.service` wartet auf `/api/health` — sonst begrüßt das Museum seine Besucher für
ein paar Sekunden mit einer Fehlerseite; dann `cage -- chromium --kiosk`. Stürzt Chromium ab,
startet systemd ihn neu.

**Was der Plan nicht wusste — dreierlei:**

1. Der Leerlauf-Reset brachte ans Licht, dass `useKiosk.reset()` und `useContribute.reset()` seit
   den Stufen 6 und 7 existierten und **nie jemand sie aufgerufen hatte**. Sie sind seither
   getestet.
2. Was als Anwesenheit zählt, muss eng gefasst sein: Tippen, Tasten, Scrollen — *keine*
   Mausbewegung. Ein vom Ärmel angestoßener Zeiger hielte den Kiosk sonst die ganze Nacht wach.
3. Beim Schreiben der Chromium-Aufrufzeile fielen zwei Flaggen an, die man erst nach dem ersten
   Museumstag vermisst hätte: `--disable-session-crashed-bubble` (nach einem gezogenen Netzstecker
   fragt Chromium sonst „Seiten wiederherstellen?" — mitten in der Ausstellung) und
   `--overscroll-history-navigation=0` (ein Wisch nach rechts löste sonst „Zurück" aus, auf einer
   Karte, die man wischt).

*Fertig, wenn: der Pi nach einem Kaltstart ohne Tastatur von selbst in der Karte landet — und nach
einem gezogenen Netzstecker genauso wieder hochkommt.* — **Gebaut und dokumentiert, aber auf
keinem Pi gelaufen**; es gab beim Bauen kein Gerät. Geprüft sind der Leerlauf-Reset und die
Shell-Syntax aller Skripte. Alles andere steht im [backlog](backlog.md).

## Vormerkung erledigt: Import vom USB-Stick

`9c89c9f` · Unter dem Upload über den Rechner. Ordner mit Bildern erscheinen von allein, sobald
ein Stick steckt; Ort und Jahr aus demselben Formular gelten für beide Wege.

**Bewusst anders als geplant:** Nach dem Lesen kommt *keine* Nacharbeitstabelle. Wer einen Ordner
mit zweihundert Bildern einliest, will keine Tabelle mit zweihundert Zeilen; die
„Unvollständig"-Liste aus Stufe 8 ist genau dafür gebaut. Der Weg endet deshalb mit einem Knopf
dorthin. Beim Upload über den Rechner bleibt die Tabelle — dort hat jemand vierzig Dateien
ausgesucht und will sie beschriften.

Die Warnung aus der Vormerkung erwies sich als die wichtigste Zusage und bekam einen eigenen Test:
**Auf dem Stick wird nichts verschoben und nichts gelöscht.** Der überwachte Eingangsordner räumt
Aufgenommenes nach `_erledigt/` — dort ist das richtig, es ist unser Ordner. Auf einem fremden
Datenträger wäre es ein Übergriff.

**Was der Plan nicht nannte:** Der Pfad wird gegen die erkannten Laufwerke geprüft (`..` bringt
niemanden heraus), und der Import teilt sich den einen Auftrag mit der Sicherung — zwei
gleichzeitige Schreibläufe auf dieselbe SQLite-Datei wären eine Fehlerquelle ohne Not.

---

# Teil II — Umbau des Verwaltungsmenüs

`63828e2` · 30. Juli 2026. Plan: [archiv/umbau-verwaltung.md](archiv/umbau-verwaltung.md).

Der Admin-Bereich war über die Stufen 8 bis 10 gewachsen, und man sah es ihm an. Drei Dinge
störten konkret: Der Filter kannte nur „Unvollständig" und warf zwei verschiedene Arbeiten
zusammen; die Übersicht nannte sechs Zahlen, von denen nur eine irgendwohin führte; und die
Menünamen überschnitten sich („Hochladen" und „Import" klingen beide nach dem Hereinholen von
Bildern, dabei war das zweite ein Protokoll).

Ziel: eine Verwaltung, in der jemand, der zweimal im Jahr hier ist, **von jeder Zahl aus dorthin
kommt, wo die Arbeit stattfindet.**

1. **Menü** — Übersicht · Fotos · Moderation · Importieren · Protokoll · Sicherung. Erst die
   Pflege des Bestands, dann das Hinzufügen, dann das Technische.
2. **Fotofilter aufgeteilt** in „Ohne Ort" und „Ohne Jahr". Verorten und Datieren sind zwei
   Arbeiten; wer die eine macht, will die andere nicht dazwischen.
3. **Zahlen werden Wege.** Die Kacheln der Übersicht sind Knöpfe und führen in die passend
   gefilterte Liste. Nur „auf der Karte zu sehen" blieb zunächst eine reine Anzeige — es ist das
   Ergebnis, keine Aufgabe.
4. **Importieren fragt erst die Quelle**, dann was für alle gilt: zwei gleichrangige Kacheln statt
   eines Nachtrags unter einer Trennlinie. Jahr und Ort werden **einmal** gefragt und gelten für
   beide Wege.
5. **Nach dem Import eine Regel für beide Wege:** bis 30 Bilder die Nacharbeitstabelle, darüber
   die Zusammenfassung mit einem Sprung in die Liste „Ohne Ort". Die Grenze (`REVIEW_LIMIT`) hat
   einen zweiten Grund: Ohne sie wanderte die Nutzlast von zweihundert Fotos durch einen Status,
   der im Sekundentakt abgefragt wird.

**Der wichtigste Einzelfund war eine stille Falle.** `date_range()` rundet ein Jahrzehnt ab: Wer
1934 eintrug und „Jahrzehnt" wählte, bekam kommentarlos 1930–1939 gespeichert — die 4 verschwand,
ohne dass jemand es merkte. Seither ist „Ganzes Jahrzehnt" nur bei durch zehn teilbaren
Jahreszahlen wählbar, und ein gesetztes Häkchen **nimmt sich selbst zurück**, wenn die Zahl
danach geändert wird. Nur auszugrauen hätte nicht gereicht: Ein gesetztes, aber ausgegrautes Feld
schickte beim Absenden weiterhin `decade`.

**Was der Plan nicht wusste:**

- Die Sicherungs-Erinnerung auf der Startseite verlinkte durch den Umbau versehentlich in die
  Fotoliste. Sie führt jetzt in den Abschnitt „Sicherung".
- Die Dateiauswahl brauchte eine sichtbare Beschriftung — ein `input type="file"` zeigt von sich
  aus kaum etwas an, und in der Maske stand sonst nur ein fast leerer Kasten.
- Die Kuratoren-Anleitung war weiter veraltet als gedacht: Sie beschrieb noch den alten Ablauf und
  trug zwei Platzhalter aus den Stufen 9 und 10, die längst gebaut waren.
- `ImportOutcome` brauchte ein Feld `source` — für die Nacharbeitstabelle wird der Name der
  Quelldatei gebraucht, und `path` war schon mit dem Ablageort belegt.

---

# Teil III — Nachbesserungen an der Verwaltung

`850db95` … `b4a9f6f` · 30.–31. Juli 2026. **Ohne Plandokument** — die Punkte kamen einzeln
aus dem Durchsehen der fertigen Oberfläche.

## Statuskacheln in der Übersicht

`850db95` · Unter den sechs Zahlen eine Trennlinie, darunter in denselben drei Spalten der
Betrieb: Tage seit der letzten Sicherung, seit dem neuesten Import, seit dem jüngsten
Besucherbeitrag. Die Sicherungskachel ersetzt den bisherigen Erinnerungsknopf und wird rot, sobald
sie fällig ist. An den Rändern steht ein Wort statt einer Zahl — „Heute gesichert", „Noch nie
importiert". Dazu: „Auf der Karte zu sehen" führt jetzt zurück zur Karte, denselben Weg wie
„Verwaltung beenden" — damit führt **jede** Zahl der Übersicht irgendwohin.

**Was dabei auffiel:** „Wie lange ist das her?" kann der Browser nicht beantworten. Ein
gespeicherter Zeitstempel trägt keine Zeitzone, und JavaScript liest ihn als Ortszeit. Die Antwort
hängt außerdem davon ab, wo die Tagesgrenze liegt. `services/dates.days_since()` zählt deshalb
**Kalendertage** im Backend, entlang der deutschen Tagesgrenze: Eine Sicherung von gestern Abend
ist „1 Tag", nicht „Heute". Bei der Gelegenheit wurden auch die Zeitstempel der Sicherungsdatei
und der Kopfdaten auf dem Stick auf UTC umgestellt — sie schrieben bisher Ortszeit.

## Seitenweises Blättern

`4e3784a` · Fotoliste, Moderation und Protokoll, dreißig Zeilen je Seite.

Vorher hörten alle drei **still** auf. Die Fotoliste schrieb „60 von 214 Fotos" — an die übrigen
154 kam niemand heran. Der Filterwechsel fängt wieder auf Seite eins an, und wer den letzten
Eintrag der letzten Seite abarbeitet, rutscht auf die letzte noch vorhandene.

## Gemeinsames Jahresfeld, Überschriften

`ffd4112` · Jahreszahl und Genauigkeit sind seither **ein Bauteil** für beide Stellen, an denen
datiert wird: den Stapel beim Importieren und das einzelne Foto im Editor. Vorher war es dort ein
Ankreuzfeld unter der Zahl, hier ein breites Auswahlfeld daneben — und die Jahrzehnt-Regel aus
Teil II galt nur an einer der beiden Stellen. Im selben Bereich galt zweierlei Recht.

Dazu klarere Überschriften: „Liste aller Fotos", „Protokoll der Foto-Importe", „Auswahl der zu
importierenden Bilder", „Angaben für alle neu hinzugefügten Bilder (optional)". Der Fotobereich
hatte als einziger gar keine.

## Ablagefeld für beide Importwege

`774594c`, `774d1f9`, `b4a9f6f` · Unter den beiden Quellenkacheln liegt jetzt **eine Fläche an
fester Stelle**, die nur ihren Inhalt wechselt — gestrichelt, solange gewartet wird, mit vollem
Rand, sobald etwas da ist, wie im Sicherungsbereich. Bei „Vom Rechner" ist sie zugleich
Ablagefläche für Dateien; der Knopf „Auswählen" bleibt der verlässliche Weg, denn auf dem Kiosk
gibt es kein Ziehen und Ablegen.

Beim Stick unterscheidet sie **drei** Lagen: kein Stick, Stick ohne Bilder, Ordner gefunden.
Vorher hätte sie jemandem, der gerade eingesteckt hat, „Bitte USB-Stick einstecken"
entgegengehalten — die Art Sackgasse, in der eine ehrenamtliche Person aufgibt.

---

# Teil IV — Besucheransicht: Fehler und Verbesserungen

`cc5a437` … `006f9ee` · 31. Juli 2026. Plan:
[archiv/besucheransicht.md](archiv/besucheransicht.md).

Sechs Punkte aus dem Durchsehen der Kioskansicht: ein handfester Fehler, zwei Sackgassen in der
Bedienung, drei Verbesserungen. Abgearbeitet wurden sie in der Reihenfolge 2 – 1 – 3 – 4 – 5 – 6:
zuerst die kleinste isolierte Änderung, damit alles Weitere schon richtig aussieht; dann das
Fundament, auf dem zwei andere Punkte aufbauen.

## 1. Ruhigeres Bild

`cc5a437` · Alle vier Trennlinien zwischen Titel, Zeitschieber, Beitragsbereich und Karte fallen —
die Bereiche unterscheiden sich danach nur noch durch den Papierton gegen die Karte, und das ist
die einzige Kante mit einer Aufgabe. Neben dem Wappen steht „Bilder aus" statt „Bilder aus
unserem", beide Zeilen größer, zusammen so hoch wie das Wappen.

## 2. Der Zeitschieber lief aus seinem Feld

`267cdc5` · **Der handfeste Fehler.** Nach dem Hineinzoomen auf zwei Fotos am Friedhofsweg (beide
„1950er") stand auf der Skala 1950–1960, in der Auswahl aber weiterhin 1920 bis 2019. Die Elemente
rechnen ihre Position in Prozent der Achse aus:

```
.timeline__selected   left: -300%  right: -590%   →  x = -2373 … 6557 px
.timeline__handle     left: -300%                 →  x = -2400 px  (ausserhalb des Bildschirms)
```

Der Auswahlbalken war **8930 px breit** und lief quer über Wappen und Titel. Geklammert wurde
nirgends — weder im Code noch per CSS.

Die Ursache lag tiefer als die Darstellung: Die Achse kam aus dem Histogramm des **sichtbaren
Ausschnitts** und änderte sich bei jedem Zoom, während die Auswahl bewusst stehenblieb. Das ist
kein Randfall — es passiert bei jedem Hineinzoomen in einen Bereich mit weniger Jahrzehnten als
der Gesamtbestand, im Museum also ständig.

**Die Achse spannt seither über den ganzen Bestand und steht still**; nur die Balken darunter
zeigen den Ausschnitt. Damit verschwindet auch die Ursache dahinter: Vorher bedeutete dieselbe
Stelle des Schiebers nach jedem Zoom ein anderes Jahr. Zusätzlich ist die Positionsrechnung auf
0…1 geklammert — der bauliche Riegel, falls Achse und Auswahl je wieder auseinanderlaufen. Steht
in [decisions.md](decisions.md), Punkt 14.

## 3. Jahrzehnte kommen aus dem Bestand

`f2f948f` · Die Datierungsfrage heißt seither „Wann war das?", passend zu „Wo ist das?".

**Der eigentliche Fund war eine Fehlablage.** `firstDecade`/`lastDecade` standen in
`tiles/region.json` — einer Datei, in der jeder andere Schlüssel Geografie beschreibt und die vom
Kartenbau gelesen wird. Was die Sammlung umspannt, hat damit nichts zu tun. Genau diese Fehlablage
zog beim Ändern zweier Jahreszahlen den Kartenbau und einen Netzzugang hinter sich her.

Die Angabe verschwand **ersatzlos**. Welche Jahrzehnte zur Auswahl stehen, ergibt sich seither aus
dem Bestand, vereinigt mit einem Mindestfenster von 1920er bis 2010er. Findet sich später ein Foto
von 1890, wächst die Reihe nach vorn, sobald das Team es datiert hat — von selbst, ohne dass
jemand eine Einstellung sucht.

*(Ein zuvor geplanter Umbau — `make region`, ein Verteilskript, eine Baumarke — wurde gestrichen.
Er hätte den falschen Ort bequemer erreichbar gemacht, statt ihn zu räumen.)*

## 4. Der eigene Beitrag wird sofort sichtbar

`458a4b2` · Nach einem Beitrag stellt sich die Ansicht für die Dauer des Dankes (2,2 s) auf dieses
Foto ein: Die Karte fährt auf hundert Meter heran, der Zeitraum auf das Jahrzehnt der Angabe —
oder ganz auf, wenn das Foto undatiert ist. Danach kehren **beide zusammen** zurück. Außerdem
springt der „Hilf mit"-Bereich bei jedem Wechsel nach oben.

Die Angaben kommen aus erster Hand: `postLocation()` und `postDate()` geben das aktualisierte Foto
zurück, das vorher weggeworfen wurde. Entschieden wird allein nach dem Foto, wie es jetzt dasteht
— welcher Weg den Beitrag ausgelöst hat, spielt keine Rolle.

**Der Fall „Ort, kein Jahr" deckt eine falsche Zusage ab:** Undatierte Fotos stehen auf der Karte
nur, solange kein Zeitfilter aktiv ist. Wer den Schieber eingeengt hat und dann ein undatiertes
Foto verortet, bekäme sonst eine leere Stelle zu sehen — unter dem Satz „Das Foto ist jetzt auf
der Karte".

**Die Falle, die der Plan vorwegnahm und die tatsächlich zuschlug:** Bei zwei Beiträgen
hintereinander darf `showPhoto` den vorherigen Zeitraum **nur merken, wenn noch keiner gemerkt
ist**. Sonst merkt sich der zweite Aufruf den Zeitraum des ersten Fokus, und der Besucher bekommt
am Ende ein Jahrzehnt zurück, das er nie eingestellt hat.

## 5. Fotos am selben Ort

`1db5ad1` · **Die zweite Sackgasse.** Am Gasthof Petersen lagen acht Fotos auf identischen
Koordinaten. Ab Zoom 18 fasste supercluster nichts mehr zusammen — aus den acht wurden acht Marker
exakt übereinander, von denen nur der oberste erreichbar war. Und der Weg dorthin führte ins
Leere: Ein Tipp auf die „8" zoomte genau in diesen Stapel hinein. **Identische Punkte trennen sich
bei keiner Zoomstufe.**

Fotos auf demselben Punkt werden seither **vor** dem Clustern zu einem Eintrag zusammengefasst.
supercluster sieht gar keine Dubletten mehr; der Stapel ist auf jeder Zoomstufe ein Marker, so
dargestellt wie ein einzelnes Foto, mit einer Anzahl in der Ecke. Ein Tipp öffnet die
Vollbildansicht mit zwei großen Blätterknöpfen. Das Denkmodell bleibt *ein Ort = ein Marker = die
Fotos von dort*. Steht in [decisions.md](decisions.md), Punkt 15.

Gruppiert wird auf fünf Nachkommastellen, rund einen Meter — das trifft den tatsächlichen Fall:
Über die Ortssuche verortete Fotos tragen exakt dieselbe Koordinate der Straße. Wer den Punkt von
Hand gesetzt hat, bleibt ein eigener Marker; dann *ist* es eine andere Stelle. Oben im Stapel
liegt das zuletzt bearbeitete Foto — die Kartenabfrage sortiert dafür nach `updated_at`, was mit
Punkt 4 zusammenspielt: Die Karte fährt hin, und das eben ergänzte Foto liegt obenauf.

## 6. Das Foto im Beitragsbereich groß ansehen

`b5b148c` · Das Vorschaubild im „Hilf mit"-Bereich war ein totes `<img>`. Dabei ist „genauer
hinsehen" genau das, was jemand tut, **bevor** er sagt, wo das war — auf 160 px ist ein Hof kaum
zu erkennen. Es öffnet jetzt dieselbe Vollbildansicht wie ein Marker auf der Karte. Ein gesetzter
Pin bleibt dabei erhalten: Er liegt im Store, nicht in der Ansicht.

---

# Teil V — Nachbesserungen an der Besucheransicht

`2f773f1` … `b20ff5c` · 31. Juli – 2. August 2026. **Ohne Plandokument**, wie Teil III.

- **Die Karte fährt schon beim Setzen des Punktes heran** (`2f773f1`) — sobald über die Ortssuche
  eine Straße oder Hausnummer gewählt ist, nicht erst nach dem Bestätigen. Der Besucher sieht, wo
  sein Punkt gelandet ist, bevor er ihn abgibt. Ein selbst auf die Karte getippter oder
  verschobener Pin lässt sie stehen: Dort hat er gerade gezielt.
- **Hausnummern in zwei Schritten** (`f908467`) — bei langen Straßen kommt ein **Abschnitt** vor
  die Nummer („1–13", „15–24"), genau wie das Jahrzehnt vor dem Jahr. Dazu vertritt die Grundzahl
  ihre Buchstabenzusätze. Aus 78 Knöpfen im Mühlenweg werden vier plus zehn. Kurze Straßen
  behalten den einen Schritt.
- **„Hilf mit:" führt in die Frage** (`5164603`) — mit Doppelpunkt, und der Abstand zur Frage
  darunter ist derselbe wie zwischen „Bilder aus" und dem Ortsnamen.
- **Zwei Oberkanten in einer Flucht** (`d9be7fc`) — die des Wappens mit der des gewählten
  Zeitraums, die von „Hilf mit:" mit der der Karte.
- **Kreise zählen Fotos, nicht Stellen** (`f055d21`) — eine Folge der Stapel-Gruppierung aus
  Teil IV: Über einem Achterstapel und zwei Einzelbildern stand 3 statt 10. Gelöst über die
  `map`/`reduce`-Aggregation von supercluster.
- **Titel auf Schieberhöhe, Leerlauf lädt neu** (`c32748d`) — Wappen und Titel stehen zusammen so
  hoch wie der Zeitschieber daneben, von seiner ersten Zeile bis zur Jahresskala. Und der Leerlauf
  nach fünf Minuten **lädt die Seite neu**, statt nur den Zustand zurückzusetzen: Im Kiosk gibt es
  keine Browser-Bedienung — kein Reload-Knopf, keine Adressleiste, keine Tastatur —, ein verhakter
  Zustand bliebe sonst bis zum Netzstecker stehen. Dazu ein Knopf „Anzeige neu laden" in der
  Verwaltung, für den Fall, dass jemand danebensteht.
- **Weniger Beiwerk, wenn nichts mehr fehlt** (`ce37d22`) — „Weiß ich nicht — nächstes Foto"
  verschwindet, wenn es die letzte offene Aufgabe ist; es gäbe kein nächstes, dasselbe Foto käme
  zurück. Ist gar nichts mehr zu ergänzen, fällt der Beitragsbereich ganz weg und die **Karte
  nimmt die volle Breite**. Eine Erfolgsmeldung, die monatelang dasteht, ist kein Inhalt — die
  Fotos sind es.
- **Ein Abstand für waagerecht und senkrecht** (`e98392b`) — eine Variable `--gap` statt zweier
  Zahlen, die auseinanderlaufen.
- **Die Detailansicht auf Fluchtlinien gebaut** (`b20ff5c`) — Bild, Textspalte und
  Schließen-Knopf beginnen auf derselben Höhe; die Blätterknöpfe stehen mittig **unter dem Bild**
  statt mittig im Schirm. Viel Text scrollt in seiner Spalte, statt oben den Schließen-Knopf zu
  überlagern und unten aus dem Bild zu laufen. Der Schließen-Knopf verließ dafür die Ecke über dem
  Foto und führt jetzt die Textspalte an — in der Form der Blätterknöpfe, damit die Ansicht genau
  eine Knopfform kennt. *Dabei gefunden:* Die Bildbreite war auf `62vw` gedeckelt, was die
  Textspalte nicht einrechnete; bei einem querformatigen Foto lief der Inhalt über seine eigenen
  Ränder hinaus.

---

# Teil VI — Einzelne Punkte aus dem Backlog

Ab hier keine Blöcke mehr, sondern einzeln aufgegriffene Einträge aus [backlog.md](backlog.md).

## Verwaltung verlassen lädt die Besucheransicht neu

`a3a5be7` · 2. August 2026.

„Verwaltung beenden" führte zurück zur Karte, ohne dass die Ansicht ihre Daten neu holte. Wer
gerade dreißig Fotos importiert oder eine Datierung korrigiert hatte, stand vor dem Bestand von
vorher — und die naheliegende Erklärung, es habe nicht geklappt, war die falsche.

**Das Neuladen sitzt in `leave()`, nicht in `dropSession()`, und das ist keine Feinheit.** Ein
abgelaufenes Token aus der `sessionStorage` lässt `restore()` beim Start über `onAdminSignedOut`
genau in `dropSession()` landen — ein Neuladen dort lüde die Seite endlos neu. Der Docstring hält
das jetzt fest, damit es niemand „aufräumt".

Damit gehen alle drei Auswege denselben Weg: der Knopf oben rechts, die Kachel „Auf der Karte zu
sehen" und „Anzeige neu laden". Der letzte tut technisch dasselbe wie der erste und bleibt
trotzdem stehen — wer eine verhakte Anzeige reparieren will, sucht nach „neu laden" und nicht nach
„beenden". Er ist der Name für den Weg, nicht ein zweiter Weg.

## Der Bearbeitungsdialog fängt oben an

`b064e62` · 2. August 2026.

Wer in der Fotoliste nach unten gescrollt hatte und dann ein Foto öffnete, bekam das Formular an
derselben Stelle — mittendrin, mit Vorschaubild und Titel oberhalb des Bildschirmrands.

**Gescrollt wird nicht die Ansicht, sondern `.admin__body` um sie herum.** `PhotoCare` tauscht nur
seinen eigenen Inhalt gegen den Editor; der Container bleibt und behält seinen `scrollTop`. Der
Inhalt darunter ist dann ein völlig anderer.

**Was der Bericht nicht wusste:** Filter, Suche und Seite waren nie das Problem. `PhotoCare` bleibt
beim Öffnen des Editors gemountet — nur `editing` wechselt —, also lebt sein State weiter. Die als
wichtigste genannte Zusage war schon erfüllt; offen war allein die Scrollposition, und die ist
billig zu haben, wenn man sie beim Öffnen merkt.

Weil der Container `AdminApp` gehört, der Wechsel aber in der Ansicht passiert, reicht ihn ein
Context durch (`admin/scrollArea.tsx`). Die Alternative wäre ein weiteres Prop an jeder Ansicht
gewesen, das mit ihrer Aufgabe nichts zu tun hat.

**Damit waren es drei Stellen, nicht eine** — die Ursache ist allgemein, und wer nur die gemeldete
Stelle geflickt hätte, hätte die anderen beiden stehen lassen:

| | vorher |
|---|---|
| Fotoliste → Editor | Formular öffnet mittendrin; Rückkehr an zufälliger Stelle |
| Abschnittswechsel | nach langer Fotoliste steht man im „Protokoll" mitten im Nichts |
| Importieren, Phasenwechsel | wer unten auf „Importieren" tippt, steht mitten in der Ergebnistabelle |

*Nachgemessen, auch mit Paginierung (`PAGE_SIZE` zum Prüfen vorübergehend auf 5): Seite 4 von 6,
auf 196,5 gescrollt, Foto geöffnet → 0. Nach „Speichern" wie nach „Abbrechen" wieder 196,5,
Seite 4 von 6, Filter „Alle". Der Phasenwechsel beim Importieren ist ungeprüft — dazu bräuchte es
einen echten Import.*

> **Eine Grenze, die bleibt und die keine ist:** Fällt das bearbeitete Foto durch die Änderung aus
> dem aktiven Filter — Ort ergänzt in der Liste „Ohne Ort" —, wird die Liste kürzer, und
> `clampOffset` zieht den Versatz auf eine Seite, die es noch gibt. „Gleiche Seite" gilt also nur,
> solange die Trefferzahl das hergibt. Das ist gewollt: Die Alternative wäre eine leere Seite
> hinter dem Ende.
