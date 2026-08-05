# Entstehung

Was gebaut wurde, in der Reihenfolge, in der es gebaut wurde — und vor allem: **was dabei anders
kam als geplant.** Das ist der Zweck dieser Datei. Sie ist aus drei Plandokumenten zusammengeführt
— dem Stufenplan, dem Umbau des Verwaltungsmenüs und der Besucheransicht —, die danach entfielen;
in der Git-Historie sind sie weiter zu lesen.

Drei Dateien beschreiben dasselbe Projekt und beantworten drei verschiedene Fragen:

| Datei | Frage |
|---|---|
| [../CHANGELOG.md](../CHANGELOG.md) | *Was kann das Programm?* — sortiert nach Keep a Changelog |
| [decisions.md](decisions.md) | *Warum ist es technisch so gebaut?* — die Grundsatzentscheidungen |
| [architecture.md](architecture.md) | *Woraus besteht es, und wie greift es ineinander?* |
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
| VI | Einzelne Punkte aus dem Backlog | ab 2. August 2026 | `a3a5be7` … `0c6bd75` |

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
durchgängig englisch, Oberflächentexte in `frontend/src/text/de.ts`, `CLAUDE.md`,
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

`63828e2` · 30. Juli 2026. Der Plan dazu stand in `docs/archiv/umbau-verwaltung.md`, bis das
Verzeichnis am 5. August 2026 entfiel.

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

`cc5a437` … `006f9ee` · 31. Juli 2026. Der Plan dazu stand in
`docs/archiv/besucheransicht.md`, bis das Verzeichnis am 5. August 2026 entfiel.

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

## Gleichnamige Straßen werden nicht mehr verschmolzen

`42fe5d8` · 2. August 2026.

Wer bei der Verortung „Hauptstraße" eingab, bekam einen Punkt **2,26 km von Holms Ortsmitte** — auf
keiner Straße, mitten im Feld. Und der zweite Schritt bot **153 Hausnummern aus siebzehn Dörfern**
an, jede mehrfach.

**Zwei Ursachen, beide im Bauskript.** Gleichnamige Wegstücke wurden nach `(Name, Art)` gruppiert
und ihre Mittelpunkte gemittelt; der Ausschnitt reicht über Holm hinaus, also lagen darin siebzehn
Hauptstraßen, und der Durchschnitt landete zwischen ihnen. Dazu liefert Overpass mit `out center`
die Mitte des umschließenden Rechtecks — bei einer gebogenen Straße also einen Punkt neben der
Fahrbahn.

**Die Lösung kam aus einem Vorschlag im Gespräch und ist besser als die geplante.** Der Plan sah
vor, die ortsnächste Straßengruppe geometrisch zu bestimmen. Stattdessen entscheidet jetzt die
**niedrigste Hausnummer**: Sie liegt in einem gewachsenen Dorf am Ortskern und bleibt dort, auch
wenn die Straße weit hinausführt — die Mitte einer langen Straße wandert dagegen mit ihr aus dem
Ort heraus. Und der Vertreterpunkt ist die **mittlere Hausnummer**, liegt also an einem Haus statt
auf der Fahrbahn; für „Wo war das?" ist das die brauchbarere Antwort.

**Was der Vorschlag nicht wusste:** Ein erster Einfall war, die Postleitzahl in die Konfiguration
aufzunehmen — dann gäbe es je Name nur noch eine Straße. Die Messung sprach dagegen: **29 % der
Straßen (141 von 486) haben gar keine Hausnummer** und damit auch keine PLZ, und an den
Straßen-Wegen selbst steht sie ohnehin nie. Ein Stichprobenlauf gegen Overpass zeigte zudem, dass
sie an 17 % der Adressknoten fehlt. Ein geometrischer Rückfall war also in jedem Fall nötig — er
ist geblieben und deckt genau diese 141 Straßen ab, mit einem Punkt auf ihrem Verlauf
(`out geom` statt `out center`).

**Der Index führt seither nur noch Straßen und Adressen.** Gebäude, Gewässer, Fluren und Ortsteile
sind entfallen — für sie gibt es den Pin auf der Karte. Damit erledigte sich der zweite Fall
desselben Fehlers: Die „Elbe" hatte sich aus ihren Teilstücken zu einem Punkt **ausserhalb der
Region** gemittelt, den das Backend bei einem Beitrag abgewiesen hätte. Dazu werden Wege jetzt auf
den Ausschnitt zugeschnitten, denn Overpass liefert jeden Weg vollständig, sobald er die Bounding
Box nur berührt.

**Die Rechnung steht als `tiles/geometry.py` mit 19 Tests daneben**, und `make test` hat dafür ein
drittes Ziel bekommen. Der Grund ist derselbe wie überall in diesem Projekt: Beide Fehler passieren
**still**. Das Skript lief grün durch, der Index wurde gebaut, und erst im Museum hätte jemand auf
„Hauptstraße" getippt.

*Nachgemessen:*

| | vorher | nachher |
|---|---|---|
| Punkt der Hauptstraße, Abstand zur Ortsmitte | 2,26 km | **0,18 km** |
| Hausnummern der Hauptstraße | 153, alphabetisch sortiert | **76**, in Gehreihenfolge |
| Straßen, deren Punkt auf einer eigenen Hausnummer liegt | — | **345 von 345** |
| Einträge ausserhalb der Region | 54 | **0** |

> **Was bleibt:** Fotos, die vorher auf einen falschen Punkt verortet wurden, stehen weiter dort.
> Der Ortsindex wird ersetzt, die Fotos werden nicht neu verortet — sie sind an ihrem `place_name`
> erkennbar und über die Fotoliste zu korrigieren.

## Fotos löschen — und ein Datenverlust, der beinahe unbemerkt geblieben wäre

`f9b6506` · 2. August 2026.

Aus „Verstecken" wurde „Löschen": derselbe Status unter dem Wort, unter dem das Museumsteam ihn
sucht. Bedient wird es im Editor und in jeder Zeile der Fotoliste, beide mit Rückfrage; gelöschte
Fotos zählen in keiner Kachel mehr mit und stehen in keiner Liste ausser „Gelöscht". Die
Begründung steht als Punkt 16 in [decisions.md](decisions.md).

**Der eigentliche Fund war die Migration.** Sie benennt den Wert `hidden` in `deleted` um, und
weil SQLite einen Check-Constraint nicht ändern kann, baut Alembic die Tabelle `photos` dazu neu:
Kopie anlegen, **Original löschen**, umbenennen. Beim ersten Lauf gegen die Entwicklungsdatenbank
nahm dieses `DROP` mit, was daran hing:

| | vorher | nachher |
|---|---|---|
| Besucherbeiträge (`changes`, ON DELETE CASCADE) | 21 | **0** |
| Schlagwort-Zuordnungen (`photo_tags`) | vorhanden | **0** |
| Verknüpfte Einträge im Import-Protokoll (ON DELETE SET NULL) | 38 | **0** |

**Nichts davon warf einen Fehler.** Die Migration lief grün durch, die Fotos waren alle noch da,
und aufgefallen ist es nur, weil die Übersicht danach „0 Beiträge von Besuchern" zeigte, wo vorher
21 standen. Auf dem Museums-Pi wäre der Verlust Wochen später aufgefallen — und dann unwiederbringlich.

Die Ursache ist eine Kette, die einzeln überall richtig aussieht: `app/db.py` schaltet
`PRAGMA foreign_keys=ON` über einen Listener auf der **Engine-Klasse** ein, gilt also für jede
Engine des Prozesses. `alembic/env.py` importiert die Modelle und damit `app.db` — die
Migrationsverbindung erbt die Einstellung. Und mit eingeschalteten Fremdschlüsseln räumt der
Tabellenneubau ab, was auf die Tabelle zeigt.

`env.py` schaltet die Prüfung jetzt für die Dauer der Migration ausdrücklich ab. Das gilt für
**jede künftige Batch-Migration**, nicht nur für diese eine — dieselbe Falle stünde sonst beim
nächsten Constraint wieder auf.

Dazu ein Test, der die Migration wirklich fährt (`tests/test_migrations.py`): Foto, Beitrag,
Schlagwort und Protokolleintrag anlegen, migrieren, nachzählen. Ohne die Reparatur ist er rot.

> **Verloren sind die Testdaten dieser Entwicklungsdatenbank** — 21 Besucherbeiträge, die
> Schlagwörter und die Verknüpfungen des Import-Protokolls. Die Fotos selbst sind vollständig.

*Nebenbei repariert:* `test_alte_sicherung_ist_ueberfaellig` schrieb seinen Zeitstempel in
Ortszeit, gelesen wird er als UTC. Zwischen 22 und 24 Uhr MESZ rutschte der umgerechnete Stempel
auf den nächsten Kalendertag und der Test war rot — zwei Stunden am Tag, seit die Kalendertage
eingeführt wurden.

## Abbruch in der Hausnummern-Auswahl

`853d6b8` · 2. August 2026.

Sobald eine Straße gewählt war, zeigte der Beitragsbereich nur noch das Knopfraster der
Hausnummern. Zurück führte einzig „Reicht so" — und das ist **keine Abbruchtaste, sondern eine
Antwort**: Es behält den Pin auf der Straße. Wer die Straße versehentlich getroffen hatte, kam
nicht mehr heraus, ohne etwas zu behaupten.

Daneben steht jetzt **„Doch nicht — von vorn"**: zurück zur Startansicht, ohne gesetzten Punkt.
Leiser gestaltet als „Reicht so", weil es keine Antwort ist, sondern ein Rückweg — dieselbe Form
wie „Anderer Abschnitt" darüber.

**Der subtilere Teil war der zweite:** Ein Tipp auf die Karte beendet die Auswahl jetzt. Vorher
lief beides nebeneinander her — der Pin wanderte, das Knopfraster blieb stehen, und der nächste
Tipp auf eine Hausnummer warf den eben gesetzten Punkt wieder weg. Ein Tipp auf die Karte ist die
bestimmtere Aussage: Dort hat jemand gerade gezielt.

**Woran das erkannt wird, war der eigentliche Fund:** Der Store setzt ein Etikett am Pin **nur**,
wenn er aus der Ortssuche kommt — eine Eigenschaft, die seit dem Heranfahren der Karte
(Teil V) besteht und dort aus einem anderen Grund gebraucht wird. Ein Pin ohne Etikett ist also
per Definition einer von der Karte. Damit ist die ganze Regel eine Zeile, ohne zusätzlichen
Zustand und ohne Vergleich von Koordinaten.

Diese Zusage trägt jetzt die Bedienung an zwei Stellen und hat deshalb einen eigenen Test bekommen.
Bräche sie, bliebe das Knopfraster nach einem Kartentipp still stehen — der Fehler, der eben
behoben wurde, wäre wieder da, ohne dass irgendetwas rot würde.

## `architecture.md` — was es gibt und wie es ineinandergreift

`0c6bd75` · 2. August 2026.

Es gab keine Stelle, an der jemand nachlesen konnte, **aus welchen Teilen das System besteht**. Wer
einstieg, musste sich das aus vier Dateien und dem Code zusammensuchen: `development.md` listete
die Ordner, `decisions.md` begründete Einzelentscheidungen, `operations.md` beschrieb den Betrieb
auf dem Pi — die Verbindung dazwischen stand nirgends.

**Die Abgrenzung war der eigentliche Teil der Arbeit**, sonst wäre eine vierte Datei entstanden,
die dasselbe noch einmal sagt. Die Regel, nach der geschnitten wurde: `architecture.md` beschreibt
*Zusammenhänge* und verweist für Begründungen weiter, statt sie zu wiederholen. Der Abschnitt
„Aufbau" in `development.md` bleibt eine Ordnerliste und verweist jetzt hierher.

Was nur hier steht, weil es zwischen den Teilen liegt und deshalb bisher nirgends hingehörte:

- **Drei Prozesse, zwei davon in Containern.** Chromium ist bewusst keiner.
- **nginx ist der Grund, warum es keinen Tileserver braucht** — es beantwortet Range-Requests auf
  die Kartendatei, und deshalb steht in seiner Konfiguration `gzip off` an genau dieser Stelle.
- **Bauzeit gegen Laufzeit.** Kartendatei und Ortsindex entstehen auf dem Entwicklungsrechner und
  gehen danach *getrennte Wege* — die eine ins Frontend-Image, der andere in die Datenbank.
  `region.json` dient dabei zwei Zwecken: Sie steuert den Bau und konfiguriert die laufende
  Ansicht.
- **Der Zustand liegt an drei Stellen** — SQLite, Dateisystem, `sessionStorage` — mit je einer
  eigenen Aufgabe.
- **Vier Importwege, eine Funktion.** Alle laufen durch `import_file()`, und die schreibt immer
  einen Protokolleintrag.
- **Sicherung, Wiederherstellung und Stick-Import teilen sich einen Auftrag**, damit nie zwei
  Schreibläufe auf dieselbe SQLite-Datei treffen.

Dazu ein Diagramm, das die drei Prozesse, die zwei gebauten Artefakte und ihre Wege in einem Bild
zeigt — die Frage „was läuft wo?" beantwortet es schneller als jeder Absatz.

## Ein Beispielbestand — und drei Funde auf dem Weg dahin

3. August 2026.

Jeder Test der Karte, des Zeitschiebers und des „Hilf mit"-Bereichs lief bis hierhin gegen eine von
Hand befüllte `data/`, die niemand sonst hatte und die zwischen zwei Versuchen nicht
zurückzusetzen war. Das README versprach in seiner Kommandotabelle längst ein `make seed` — das
Ziel gab es nicht.

Die Reihenfolge stand fest, sobald der erste Blick in die Daten fiel: **Die zwanzig echten Holmer
Fotos existierten nur als SHA-benannte Dateien**, ihre Originalnamen und alle Metadaten
ausschließlich in der Datenbank, die geleert werden sollte. Der Export musste also vor allem
anderen kommen — und wurde vor dem Löschen Datei für Datei per SHA-256 gegen seinen Eintrag
nachgerechnet.

### Die Form: Bilder und JSON, kein Datenbankabzug

Ein Abzug ist wertlos, sobald eine Spalte dazukommt — und genau das war zwei Tage vorher passiert.
Hier kostet eine neue Spalte eine Zeile je Foto. Dazu kommt, dass `make seed` durch die **echte**
Import-Pipeline geht statt Zeilen zu schreiben: Es erzeugt die Vorschaubilder, füllt das
Import-Protokoll und prüft den Import gleich mit.

Der Rundlauf ist als Test festgehalten (`test_ausgangszustand_uebersteht_das_hin_und_zurueck`),
und einer seiner Geschwister beschreibt den Fall, der sonst still kaputtginge:
`test_luecken_bleiben_luecken` — beim Zurückholen läuft jedes Foto durch den Import, und wenn der
dabei ein Datum oder einen Ort einträgt, verschwindet das Foto aus dem Beitragsbereich. **Die
Lücke muss die stärkere Angabe sein.**

### Was der Plan nicht wusste, erstens: die Schlagwörter waren Zeichensalat

Im Bestand standen die Schlagwörter `牁档癩潈浬`, `楗瑮牥` und `浉匠湡敤`. Das sind „ArchivHolm",
„Winter" und „Im Sande", als UTF-16 gelesen.

`_text()` in `services/exif.py` probierte `utf-16-le` **zuerst** — richtig für die
Windows-Felder `XPTitle` und `XPKeywords`, die wirklich UCS2-LE sind, falsch für IPTC. Die Tücke:
**Jede** Bytefolge gerader Länge ist gültiges UTF-16, es fliegt also nie ein `UnicodeDecodeError`
und der Rückfall auf UTF-8 kommt nie zum Zug. Der Beweis stand in den Daten selbst — kaputt waren
genau die Wörter mit gerader Byte-Länge, heil die mit ungerader („Gebäude", „Hauptstraße"). Das
sah nach Zufall aus und war eine Regel.

Die Funktion ist jetzt zweigeteilt: `_xp_text()` für die XP-Felder, `_text()` für alles übrige.

### Was der Plan nicht wusste, zweitens: der Import hielt „OLYMPUS DIGITAL CAMERA" für einen Titel

Zwei Fotos trugen genau diesen Satz als Titel *und* als Beschreibung. Er steht wirklich in den
Dateien — Olympus-Kameras schreiben ihren eigenen Namen in beide Felder.

**Das ist dieselbe Falle wie das Scandatum, ein Feld weiter.** Der Wert ist da, das Foto gilt
damit als betitelt und wird nie wieder jemandem vorgelegt, der einen echten Titel wüsste. Also
dieselbe Behandlung: `_statement()` verwirft eine kleine Liste bekannter Kamera-Textbausteine, und
kein Titel ist ehrlicher als dieser.

### Was der Plan nicht wusste, drittens: der Testschutz hing an den Revisionsnummern

Die drei Migrationen wurden zu einem Anfangsschema zusammengefasst — es gibt kein Gerät im Feld,
also gab es keine Datenbank, von der ein Migrationsweg irgendwohin geführt hätte. Mit den Dateien
verschwand auch die Migration, die den Datenverlust angerichtet hatte.

Beinahe verschwunden wäre damit aber der Test, der ihn seither verhindert: Er zog namentlich auf
die Revision `b7c41d0a92e3` hoch. Ein Test, der mit dem Fehler stirbt, den er bewacht, ist keiner.

Er läuft jetzt gegen eine **Probe-Migration** unter `tests/fixtures/sample_migration/` — eine
einzige Revision, die `photos` mit `recreate="always"` neu baut und sonst nichts. Ihre `env.py`
tut nur eines: sie führt die **echte** aus. Eine eigene Kopie der Fremdschlüssel-Regel würde nur
sich selbst bestätigen. Die Gegenprobe steht: Wird das `PRAGMA foreign_keys=OFF` in
`alembic/env.py` auf `ON` gedreht, ist der Test rot.

### Bildnachweis und Herkunft

Als einziger schema-wirksamer Backlog-Punkt vorgezogen, weil die Angaben beim Kuratieren ohnehin
mit eingegeben werden. Der Backlog ließ offen, ob es ein Feld oder zwei sind und wer sie sieht —
es sind zwei, und **die Trennung ist der Punkt**:

- `credit` — Bildnachweis, eine Zeile, im Besucher-Overlay unter der Beschreibung
- `provenance` — Herkunft, Leihgeber, Freigabe, nur in der Verwaltung

Durchgesetzt wird das nicht durch eine Verabredung, sondern durch den Typ: Der Kiosk-Endpunkt
liefert `PhotoDetail`, und diese Klasse hat kein Feld für die Herkunft. Die Verwaltung bekommt
`PhotoAdminDetail`, das davon erbt und eines hinzufügt. Der Test dazu heißt
`test_herkunft_erscheint_nicht_in_der_besucheransicht` und prüft den Fehlerfall, nicht den
Erfolgsfall.

Beide sind auch **gemeinsame Angabe** beim Stapel-Import, neben Jahr und Ort — eine Kiste Scans
kommt fast immer von einer Person.

### Der Bestand selbst

Aus 28 Zeilen wurden 16: neun synthetische Testbilder heraus (die gehören nach
`backend/tests/fixtures/`, auf ihnen ist nichts zu sehen, was auf einer Karte Sinn ergäbe), drei
von vier 4K-Videostandbildern desselben Motivs heraus — sie belegten 40 der 51 MB —, und ein Foto
auf Wunsch.

Was beim Durchsehen sonst noch auffiel und korrigiert wurde:

- **Drei Fotos lagen 1,6 km neben ihrer eigenen Adresse.** Sie trugen „Hauptstraße 14" als Namen
  und Koordinaten im freien Feld bei „An den Wischen". Der Ortsindex sagte eindeutig, welche der
  beiden Angaben stimmt.
- **Zwei Titel waren Dateinamen** („pic 158-1"). Geleert — aus demselben Grund, aus dem der
  Kamera-Filter entstand.
- **Die Beitragsliste enthielt nur Statuswechsel aus dem Ausprobieren**, während mehrere Fotos
  `*_source = visitor` trugen, **ohne** dass es dazu einen Protokolleintrag gab. Das Zurücknehmen
  in der Verwaltung hängt aber genau daran. Jetzt gibt es zu jeder Besucherangabe einen Eintrag,
  und einer davon ist zurückgenommen — sonst ließe sich der Fall nie ansehen.

**Die Lücken im Bestand sind Absicht.** Ein Bestand, in dem alles vollständig ist, prüft die
Hälfte des Programms nicht: Ohne undatierte und unverortete Fotos hat der „Hilf mit"-Bereich
nichts vorzulegen. Sie entstehen aus nachgelieferten Scans, nicht aus dem Löschen echter Angaben —
ein frisch importierter Scan hat von sich aus weder Ort noch Jahr, und das ist zugleich der
realistische Fall.

## Der Schließen-Knopf steht wieder oben rechts

3. August 2026.

Der Umbau vom 2. August (`b20ff5c`) hatte ihn aus der Ecke in die Kopfzeile der Textspalte geholt.
Das fluchtete mit der Oberkante des Bildes — aber es las sich nicht wie ein Schließen-Knopf. Die
gewohnte Stelle ist oben rechts.

Die Ansicht hat dafür eine eigene Kopfzeile bekommen, die **über beide Spalten geht**. Das ist der
ganze Trick: Stünde der Knopf weiter in der Textspalte, säße er am rechten Rand *dieser Spalte*;
über beide Spalten gespannt sitzt er am rechten Rand der ganzen Ansicht. Drei Zeilen also — Kopf,
darunter Bild und Text nebeneinander, darunter die Blätterknöpfe.

**Die Frage, die der Backlog offengelassen hatte:** Sollen Kopf- und Fußzeile ihre Höhe auch dann
reservieren, wenn nichts darin steht? Die Kopfzeile ist nie leer. Die Fußzeile gibt es nur bei
einem Stapel — und sie reserviert **nicht**. Ein einzelnes Foto ist der häufigere Fall und bekommt
die 4,5 rem als Bildhöhe, auf 1280 × 800 rund 8 % mehr Bild. Der Preis ist, dass die Unterkante
des Bildes bei Stapel und Einzelfoto verschieden hoch sitzt; zwei Öffnungen sieht aber niemand
nebeneinander, und der Schließen-Knopf steht in beiden Fällen an derselben Stelle. Das ist der
Punkt, an dem die Ansicht ruhig wirkt.

Nachgemessen auf 1280 × 800, in beiden Zuständen und für Hoch- wie Querformat: Der Knopf schließt
auf **0 px** mit dem rechten Rand des Inhalts ab, Bild und Text fangen auf **0 px** genau in
derselben Zeile an, und die Blätterknöpfe stehen auf **0 px** mittig unter dem Bild — nicht mittig
im Schirm, was der eigentliche Grund dafür ist, dass die linke Spalte `auto` breit ist und nicht
`1fr`. Auf 1024 × 768 passt der Inhalt ebenfalls vollständig in den Schirm.

## Der schwarze Blitz hinter dem Bild

3. August 2026.

In der Detailansicht war gelegentlich eine schwarze Fläche hinter dem Foto zu sehen. Die Suche nach
der Ursache ging über drei Verdachtsmomente, und die ersten zwei waren falsch:

- **Kein Alphakanal.** Kein einziges Vorschaubild trägt Transparenz — die WebP-Erzeugung wandelt
  vorher um.
- **Kein Seitenverhältnis-Fehler.** Über alle achtzehn Fotos des Beispielbestands nachgemessen
  stimmt das Verhältnis der Bildbox mit dem des Vorschaubilds auf **0 %** überein. `object-fit:
  contain` lässt also nirgends einen Rand frei.

Damit blieb nur eine Erklärung übrig, und sie war die richtige: **`background: #000` auf
`.overlay__image`.** Die Zeile stammte aus der Zeit, bevor das Element sein Seitenverhältnis als
`aspect-ratio` mitbekam — damals konnte die Box breiter oder höher sein als das Bild darin, und der
Rand brauchte eine Farbe. Seitdem entspricht die Box dem Bild genau, und der Hintergrund ist nur
noch in einem einzigen Moment zu sehen: **bevor das Bild gezeichnet ist.** Die Box steht wegen
`aspect-ratio` schon in voller Größe da, das Bild ist noch unterwegs.

Deshalb „gelegentlich": Es traf beim Öffnen und bei jedem Schritt durch einen Stapel, und wie lange,
hing an der Dateigröße. Auf dem Entwicklungsrechner über localhost kaum zu sehen, auf dem Pi mit
einem großen Scan lang genug.

Die Zeile ist ersatzlos entfallen — und damit trat der Fehler ein zweites Mal auf, nur anders
herum. Ohne Hintergrund blieb im Ladezustand der **Schlagschatten um eine leere Fläche** stehen,
und das sieht schlechter aus als das Schwarz vorher: Es wirkt wie ein Bild, das fehlt.

Also die Ursache eine Stufe tiefer angefasst. Das Bild wird jetzt erst gezeichnet, wenn es geladen
ist — `visibility: hidden`, solange nicht. Das nimmt den Schatten mit, während `display: none` den
Platz genommen hätte und die Ansicht beim Blättern gesprungen wäre. Die Bedingung hängt an der
Foto-Kennung, nicht an einem Umschalter: `loadedId === detail.id`. Damit gilt sie beim ersten
Öffnen und bei jedem Schritt durch einen Stapel gleichermaßen, ohne dass irgendwo etwas
zurückgesetzt werden muss.

**Der eine Fallstrick dabei** steht als Kommentar daneben: Liegt das Bild schon im Cache, ist es
unter Umständen fertig, bevor React `onLoad` hängen kann — dann bliebe es für immer unsichtbar.
Deshalb prüft zusätzlich die `ref`-Funktion `node.complete`. Denselben Wert noch einmal zu setzen
ist für React ein Nichtstun, es schleift also nicht.

Nachgemessen über sieben Blätterschritte: kein Foto blieb verborgen, und die Ladeklasse zeichnet
nachweislich nichts, auch keinen Schatten.

*Nachtrag zur Fehlersuche selbst:* Die Meldung lautete „jetzt ist da eine Fläche mit Schatten zu
sehen", mit der Vermutung, die Fläche sei größer als das Bild. Das war sie nicht — nachgemessen
0,03 px Rand auf 366 px Breite. Die Fläche war nicht zu groß, sie war leer. Der Unterschied klingt
klein und ist der ganze Unterschied zwischen der falschen und der richtigen Reparatur.

## Die Sicherung gibt es jetzt auch als eine Datei

3. August 2026.

Sichern ging nur über einen USB-Stick. Für das Museum ist das richtig und bleibt der Hauptweg —
aber es gibt zwei Fälle, in denen es nicht trägt: Es liegt kein Stick bereit, oder man sitzt beim
Entwickeln vor dem Rechner und will den Bestand einfach herunterladen.

**Der Entwurf steht und fällt mit einer Eigenschaft:** Das Archiv ist genau der Ordner, den auch
der Stick bekommt, nur gezippt. Daraus folgt alles Weitere — vor allem, dass die fehlende
Upload-Wiederherstellung keine Lücke ist, sondern eine Unbequemlichkeit: auf einen Stick
entpacken, vorhandene Wiederherstellung benutzen. Es gibt damit **keinen zweiten
Wiederherstellungsweg**, der eigene Fehler haben könnte.

Weil diese Eigenschaft leicht zu zerstören und schwer zu bemerken wäre, hält
`test_entpacktes_archiv_laesst_sich_wiederherstellen` sie fest: Archiv bauen, in ein
Prüf-Laufwerk entpacken, `run_restore` laufen lassen, nachzählen. Bricht der Test, ist der Rückweg
weg — und zwar lautlos.

### Im Strom, nicht im Speicher

Die Frage, die der Backlog offengelassen hatte: Wird das Archiv im Speicher gebaut, auf die
SD-Karte geschrieben oder im Strom erzeugt? Auf einem Pi mit 2 GB RAM scheidet das Erste aus, und
die SD-Karte ist genau das, wovor die Sicherung schützt. Also im Strom.

Das braucht eine Senke für `zipfile`, die nichts aufhebt — `_ArchiveStream`, drei Methoden. Zwei
davon sind offensichtlich (`write` sammelt, `tell` zählt mit, weil `zipfile` daraus seine Offsets
rechnet). Die dritte ist der eigentliche Schalter: **`seekable()` sagt nein**, und daraufhin
arbeitet `zipfile` mit Data Descriptors, statt später in Kopfdaten zurückzuspringen, die längst
ausgeliefert sind. Ein `seek` gibt es deshalb bewusst nicht — mit einem würde die Klasse still
anfangen zu lügen.

`ZIP_STORED` ist dabei keine Sparsamkeit: JPEG und WebP sind komprimiert, ein zweiter Durchgang
kostet den Pi nur Zeit. ZIP64 ist Pflicht, zweitausend Scans gehen ohne Weiteres über vier
Gigabyte.

### Zwei Fallstricke, die erst beim ersten großen Bestand aufgefallen wären

**`proxy_buffering`** steht im nginx auf der Voreinstellung — es hätte den ganzen Strom erst auf
die SD-Karte gesammelt, bevor der Browser ein Byte sieht. Genau der Fallstrick, den bei den Kacheln
schon das `gzip off` daneben abfängt, und genau der, der auf einem Bestand von achtzehn Fotos
nichts tut.

**Ein Browser-Download kann keinen `X-Admin-Token` mitschicken.** Der kurze Weg wäre, den
Sitzungstoken in die Adresse zu hängen; er ist falsch, weil Adressen im Verlauf, in Lesezeichen
und in Proxy-Protokollen landen und dieser Token den ganzen Verwaltungsbereich öffnet. Stattdessen
ein `TicketStore` nach dem Vorbild des `SessionStore`: ein Ticket kauft genau einen Download, wird
beim Einlösen vergessen und ist nach einer Minute wertlos.

### Was die Oberfläche sagen muss

Die Maske hat die Form des Importbereichs übernommen — zwei gleichrangige Kacheln, darunter eine
Fläche an fester Stelle. Der Stick steht links, weil er die bessere Sicherung ist.

Zwei Sätze stehen dabei bewusst auf dem Bildschirm und nicht nur in der Dokumentation. Der erste
ordnet den Weg ein: Das Archiv ist nicht inkrementell, und ein abgebrochener Download ist
wertlos — beides Eigenschaften, die genau die Begründung für „Ordner statt ZIP" waren
([decisions.md](decisions.md), Punkt 11). Der zweite sagt, wie eine solche Datei wieder ins Gerät
kommt; ohne ihn sähe die fehlende Rückrichtung wie ein Fehler aus.

Am echten Bestand nachgemessen: 31 MB in 132 Stücken, entpackt 18 Fotos, 36 Vorschaubilder, eine
lesbare Datenbank ohne WAL daneben — und `is_restorable` sagt ja.

## Der Rückweg führt durch den Eingangsordner

3. August 2026.

Die Sicherung als Datei gab es seit dem Vormittag, der Rückweg nicht — man musste sie auf einen
Stick entpacken. Der Backlog hatte dafür drei Hindernisse notiert, und alle drei hingen am Upload
durch den Browser: `client_max_body_size`, eine zweiphasige Fortschrittsanzeige und der dreifache
Platzbedarf beim Auspacken.

**Der Eingangsordner räumt alle drei ab.** Die Datei liegt schon auf der Platte — kein Upload,
keine nginx-Grenze, keine zweite Anzeige. Und weil direkt in den Arbeitsordner entpackt wird statt
erst daneben, bleibt es beim Dreifachen statt beim Vierfachen; mehr geht nicht, solange das Archiv
seine eigene Quelle ist.

### Die Entscheidung, die den Entwurf prägt

Der Ordner tut bisher etwas **Hinzufügendes und Folgenloses**: Ein Foto zu viel darin ist ein Foto
zu viel. Eine Wiederherstellung **ersetzt den ganzen Bestand**. Beides ohne Rückfrage in denselben
Ordner zu legen, hieße: Eine versehentlich dorthin kopierte Datei tauscht die Sammlung aus, und auf
einem Kiosk fällt das wochenlang niemandem auf.

Deshalb spielt sich nichts von selbst ein. Die Datei wird **erkannt** und im Sicherungsbereich
vorgelegt — dieselbe Rückfrage mit Datum und Anzahl, die der Stick-Weg schon stellt. Die Kachel
„Als eine Datei" bekommt dafür einen zweiten Zustand und wird vorgewählt, sobald etwas wartet.
Darunter steht weiterhin der Download: Sonst wäre der einzige Moment, in dem sich der *jetzige*
Bestand nicht mehr sichern lässt, ausgerechnet der unmittelbar vor dem Überschreiben.

### Was der Plan nicht wusste

**Ohne eine Zeile im Watcher tut nichts davon etwas.** Das Archiv wäre in `import_file` gelaufen,
dort als „Kein lesbares Bild" abgewiesen worden und in `_problem/` gelandet — bevor es überhaupt
jemand hätte bestätigen können. `_candidates()` übergeht es jetzt. Die Gegenprobe steht: Ohne die
Zeile ist `test_zip_im_eingang_landet_nicht_im_problemordner` rot.

**Ein Name kollidierte.** `importer._move_aside` sollte öffentlich werden, damit die Sicherung das
eingespielte Archiv nach `_erledigt/` räumen kann. Aber `import_file` hat einen **Parameter**
namens `move_aside` — die Funktion wäre in seinem Geltungsbereich verdeckt gewesen, und die Aufrufe
darin hätten den Wahrheitswert aufzurufen versucht. Stattdessen heißt die öffentliche Variante
`move_to_done` und ist zugleich enger: Sie kennt nur ein Ziel.

**Halb kopierte Dateien brauchen keine Sonderbehandlung.** Der Watcher wartet sonst darauf, dass
eine Dateigröße sich nicht mehr ändert. Für ein Archiv genügt der Versuch, es zu öffnen: Ohne sein
Zentralverzeichnis am Ende ist ein ZIP für `zipfile` schlicht kein ZIP.

Am echten Bestand geprüft: 18 Fotos gesichert, fünf Dateien gelöscht, eingespielt — 18 wieder da,
das Archiv in `_erledigt/`, der alte Stand in `vorher-2026-08-03-2341/`, und die Abschlussmeldung
nennt beide.

## Datieren in der Detailansicht

4. August 2026.

Wer ein undatiertes Foto groß ansah, las dort „Jahr unbekannt" und hatte keine Möglichkeit, es zu
sagen — er hätte schließen und hoffen müssen, dass der Beitragsbereich ihm zufällig dasselbe Foto
vorlegt. Jetzt steht die Auswahl in der Ansicht selbst.

**Mit Knöpfen, nicht mit einem Zahlenfeld.** Die ganze Besucheransicht hat genau ein Eingabefeld,
und ob das Gerät je eine Tastatur bekommt, ist im Backlog offen — ein Zahlenfeld wäre dort ein
Bedienelement, das nichts annimmt. Es ist dasselbe zweistufige Verfahren wie im Beitragsbereich,
und deshalb ist es jetzt ein Bauteil: `DatePicker` zeigt Jahrzehnt und Jahr, `DateTask` hängt den
Beitrag der laufenden Frage daran, die Detailansicht den zum Foto, das gerade zu sehen ist.

### Was der Weg absichtlich nicht tut

`submitDateFor` geht **nicht** durch `contribute()`, und das sind zwei bewusste Auslassungen:

- **Kein Dank.** Die Rückmeldung ist die Ansicht selbst — aus „Jahr unbekannt" wird „1963", und die
  Knöpfe verschwinden, an genau der Stelle, auf die geschaut wird. Das ist der Fall, den der
  Backlog unter *„Die Dankmeldung: brauchen wir sie, und stimmt sie immer?"* als den beschreibt, in
  dem der Satz überflüssig ist: Wo die Ansicht sich sichtbar ändert, sagt sie es schon.
- **Kein Kartenfokus.** Die Karte liegt unter der Detailansicht. Sie irgendwohin zu fahren, sähe
  niemand.

### Die Regel, die still gebrochen wäre

**Der Beitragsbereich zieht nur weiter, wenn er dasselbe Foto nach dem Jahr fragte.** Ohne das legt
er es gleich noch einmal vor, der Besucher antwortet ein zweites Mal — und bekommt „Dieses Foto hat
inzwischen schon eine Angabe bekommen". Eine Meldung, die klingt, als sei jemand anders schneller
gewesen, obwohl er selbst es war.

Fragte er nach dem **Ort**, bleibt er stehen: Den braucht das Foto unverändert. Beide Fälle sind
im Store getestet und am laufenden Gerät nachgestellt — bei der Ortsfrage blieb dasselbe Foto
stehen, bei der Jahresfrage wechselte die Ansicht auf „Wo ist das?".

### Reichweite

Größer als erwartet: Undatierte Fotos stehen sehr wohl auf der Karte, weil die Kartenabfrage den
Zeitfilter weglässt, solange der Schieber den ganzen Bestand umspannt. Erst wer den Zeitraum
einengt, blendet sie aus — richtig so. Die Auswahl ist damit über den Marker *und* über „Foto groß
anzeigen" erreichbar.

## Der Erstbestand: 929 Fotos aus einem sortierten Archiv

Der Anlass war ein Ordner mit 929 Bildern, den das Museum vorbereitet hatte — und die Frage, ob
daraus ein Programm entsteht, das einmal läuft, oder ob der Import selbst es lernt. Es wurde das
Zweite. Was das kostete und was dabei anders kam als gedacht, steht hier.

### Was der Ordner schon wusste

```
Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
```

Straße, Hausnummer, Hausname — dreimal Auskunft, in einem Pfad. 801 der 929 Fotos lagen so, 124
nur unter einer Straße, 4 ganz oben. Diese Namen zu verwerfen hätte geheißen: Ehrenamtliche tippen
929 Adressen ab, die schon da sind, und Besucher werden nach dem Ort von Fotos gefragt, deren
Adresse danebensteht.

### Zwei Funde vor der ersten Zeile Code

Bevor irgendetwas gebaut wurde, wurde der Ordner vermessen. Zwei Ergebnisse haben den Entwurf
danach getragen:

**116 Fotos tragen ein Scandatum, 91 davon aus einem einzigen Lauf von 2015.** Sie unbesehen zu
datieren hätte 91 historische Ortsbilder auf der Zeitleiste bei 2015 abgelegt — und weil sie damit
als datiert gelten, wären sie nie mehr jemandem vorgelegt worden. Genau der Fehler, gegen den
`exif_date_max_year` gebaut wurde. Der Fund war aber zugleich die Widerlegung dieser Regel in
ihrer bisherigen Form: 256 Fotos sind **echte Kameraaufnahmen von 2010 bis 2024**, und die
Jahresgrenze hätte sie alle mit verworfen. Die Regel musste also nicht schärfer werden, sondern
zweistufig: erst das Gerät, das die Datei nennt, und die Jahresgrenze nur dort, wo keines
dasteht. Geprüft wurde das an den Bildern selbst — von 256 Kamerafotos sind 234 farbige Aufnahmen
der Häuser, wie sie heute stehen, und die 22 fast graustufigen zeigen trübes Wetter, Schnee und
eine dunkle Scheune. Keine Reprofotos alter Abzüge, also trägt die Umkehrung.

**In 82 Dateien steht als Fotograf wörtlich „unbekannt".** Ein Nichtwert, der ein Feld füllt. Das
ist dieselbe Falle wie „OLYMPUS DIGITAL CAMERA" ein Feld weiter, und die Antwort dieselbe: Was
nichts sagt, gilt als leer.

### Drei Fehler, die erst der echte Lauf zeigte

Der Probelauf auf eine Straße und danach der volle Lauf haben drei Dinge zutage gefördert, die
kein Testentwurf vorweggenommen hätte:

1. **`UNIQUE constraint failed: tags.name`** — mitten im Import. Die Sitzung läuft mit
   `autoflush=False`; ein Schlagwort, das die Pfad-Schicht für ein Foto anlegte, war für die
   Abfrage des nächsten noch unsichtbar. Zwei Fotos an derselben Adresse legten es also zweimal
   an. Seitdem schreibt `add_tags` ein neues Schlagwort sofort heraus — und zwar **nach** dem
   Flush des Fotos, denn davor ist es noch nicht in der Sitzung und die Verknüpfung ginge
   verloren.
2. **Der Ordner „2" wurde zur Straße „Kolonie Autal 2".** Damit das Archiv auch kürzen darf
   („Wiesengrund" für „Im Wiesengrund"), sucht die Straßenerkennung notfalls wortweise — und die
   Hausnummer 2 unter „Achter de Möhl" fand eindeutig eine Straße, die den Namen zufällig auf
   eine Zahl enden lässt. Zwei Fotos lagen danach am anderen Ende des Dorfes. Seitdem gilt: Jedes
   Wort muss einen Buchstaben enthalten. Aufgefallen ist es nur, weil die Zahlen zweier Läufe
   verglichen wurden — 381 hausgenaue Fotos beim ersten, 379 beim zweiten.
3. **Der Titel war manchmal ein ganzer Absatz.** Bis zu 223 Zeichen, mit Zeilenumbrüchen: Wer das
   Archiv pflegte, schrieb die Bildunterschrift dorthin, wo der Cursor stand. Als Überschrift ist
   das eine Textwand. Weggeworfen gehört sie trotzdem nicht — sie wandert in die Beschreibung, und
   den Titel liefert der Ordner.

Dazu kamen zwei Kleinigkeiten mit demselben Muster: `x-default`, ein Sprachmarker aus XMP, stand
als Titel; und „August MÃ¶ller" ist „August Möller", zweimal durch die falsche Kodierung gedreht.
Beides passiert in fremden Programmen, lange bevor eine Datei hier ankommt — der Import ist die
letzte Stelle, an der es noch auffallen kann.

### Was herauskam

929 aufgenommen, keine einzige Dublette, zwei `Thumbs.db` abgewiesen. 852 Fotos verortet, davon
381 hausgenau; 256 datiert; 922 mit Titel, alle mit Bildnachweis, 926 mit Herkunftsangabe. 77
Fotos ohne Ort und 673 ohne Jahr — das ist kein Rest, sondern der Vorrat des „Hilf mit"-Bereichs.

Der Bestand liegt als ZIP-Sicherung außerhalb des Repos (1,4 GB, 2791 Einträge, geprüft), und die
Entwicklung läuft danach wieder auf den 18 Fotos des Beispielbestands weiter.

### Was die Entscheidung eigentlich war

Nicht die Regeln, sondern ihre **Trennung in zwei Schichten**: Metadaten für alle vier
Importwege, Pfad nur für die drei, die einen haben. Damit bekam das Hochladen im Browser die
Metadaten-Regeln geschenkt, ohne die Pfad-Regeln zu erben — und der USB-Stick verhält sich seither
wie der Eingangsordner, weil er dieselbe Schicht durchläuft. Wäre es ein einmaliges Skript
geworden, hätte das nächste Archiv wieder eines gebraucht.

## Sprach- und Namenskonsistenz

`e29c161` … `692ebfc` · 5. August 2026.

Die Sprachregelung stand seit Stufe 7.5 in CLAUDE.md und galt als geklärt. Der Backlog-Punkt dazu
forderte etwas anderes: **nachsehen statt annehmen.** Die Messung über alle 108 Quelldateien war
die eigentliche Arbeit — was danach zu tun war, ergab sich fast von selbst.

### Vier Regeln waren lückenlos eingehalten, ohne dass es jemand geprüft hatte

Kein deutscher Oberflächentext stand fest im TSX, kein deutscher Name in einem API-Pfad, einem
Query-Parameter oder einem JSON-Feld, die CLI-Ausgaben waren durchweg deutsch — und **90 von 90
Commit-Nachrichten trugen keinen einzigen Umlaut**. Genau das hatte der Backlog-Punkt verlangt:
„ein Durchgang über `git log` sollte es bestätigen statt es anzunehmen."

Zwei Regeln waren es nicht: **338 deutsche Kommentare in 52 Produktivcode-Dateien** neben 687
englischen, teils in derselben Datei, und neun deutsche Dateinamen. Nachgezogen statt aufgeweicht
— bei den Kommentaren war das zugleich der billigere Weg, andersherum wären 687 zu übersetzen
gewesen.

### Die Regel widersprach sich selbst

Sie verbot Umlaute im Python-Quelltext und gab zwei Absätze weiter ``so that "muhlenweg" finds the
"Mühlenweg"`` als *erwünschtes* Beispiel — mit Umlaut. Alle fünfzehn gefundenen Stellen waren von
dieser Art: zitierte Beispiele oder Datenwerte. `"März"` in der Monatsliste von `services/dates.py`
hat ohnehin keinen Ersatz; ohne Umlaut zeigte der Kiosk „Maerz".

Daraus wurde die Präzisierung: **In deutscher Prosa im Quelltext werden Umlaute umschrieben, in
Zitaten und Datenwerten bleiben sie.** Das ist keine Ausnahme von der Regel, sondern ihre
Ausformulierung — Prosa ist etwas anderes als der Gegenstand, über den sie spricht.

### Die Tests waren längst eine eigene, stimmige Welt

326 deutsche gegen 10 englische Kommentare. Die Regel nannte als Ausnahme nur die *Testnamen* und
beschrieb damit die Hälfte der Wirklichkeit — dabei ist ein Test-Docstring die Fortsetzung des
Testnamens und trägt dasselbe Warum („Das EXIF sagt 2019, das Foto ist historisch"). Seitdem steht
in der Regel, was ohnehin galt: **Testdateien sind ganz deutsch.** Die zehn englischen Ausreißer
in `conftest.py` zogen nach.

### Zwei Umbenennungen lösten die Sinnfrage mit

Der Backlog-Punkt hatte nicht nur nach der Sprache gefragt, sondern danach, ob ein Dateiname sagt,
was drinsteht. `admin/jahr.ts` enthielt die Jahrzehnt-Regel und heißt jetzt `yearInput.ts`, wie das
`YearField`, dem es dient. `admin/paging.ts` hieß nur so, weil `pager.ts` auf macOS mit `Pager.tsx`
kollidiert wäre; als `pagination.ts` kollidiert nichts mehr.

### Das Prüfskript meldete einen Verstoß, der keiner war

`tools/language_check.py` zählt deutsche und englische Kommentare je Datei. Es fand `config.py`
schuldig — wegen ``PHOTOMAP_IMPORT_PROVENANCE="Online-Archiv des Museums, Verzeichnis 01 Orte/"``,
einem Einstellungswert. Zu „beheben" wäre das nur durch Fälschen des Beispiels gewesen. Das Skript
streicht Zitiertes deshalb, bevor es zählt; die Regel oben ist dieselbe Einsicht in Worten.

**Bewusst kein Test.** Die Spracherkennung ist eine Wortlisten-Heuristik, und ein Test, der bei
einem Fachbegriff falsch anschlägt, wird binnen eines Monats ausgeschaltet — danach ist gar nichts
mehr bewacht.

### Und die erste Gegenprobe griff nicht

Um zu prüfen, ob das Skript überhaupt etwas findet, wurde ein deutscher Satz eingeschmuggelt — und
das Skript schwieg. Nicht weil es blind war: Der Satz hing vorn in einem langen englischen
Docstring, dessen übrige Wörter ihn überstimmten. Die Probe war falsch gebaut, nicht das Werkzeug.
Als eigenständiger Kommentar gesetzt, fand es ihn sofort — und in der Gegenrichtung auch einen
englischen Kommentar in einer Testdatei, beide mit Exitcode 1.

Das ist die Lehre, die über diesen Tag hinausreicht: **Eine Gegenprobe, die nicht anschlägt,
beweist erst einmal nichts über den Code — sie stellt eine Frage an die Probe.**
