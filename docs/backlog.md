# Offene Punkte

Was noch aussteht, nach **Verwaltung · Besucher-Interface · Infrastruktur · Entwicklung**. Die
ersten drei betreffen das Programm, der letzte die Arbeit daran. Was schon gebaut ist, steht in
[history.md](history.md).

Jeder Eintrag trägt mit, was beim Aufgreifen sonst erst wieder herausgefunden werden müsste. Das
ist der Grund, warum er hier steht und nicht in einer Stichwortliste: Ein Punkt ohne seinen
Zusammenhang kostet beim zweiten Anlauf dieselbe Arbeit wie beim ersten.

## Wie diese Datei zu lesen ist

Jeder Punkt hat eine **Nummer**, eine **Art** und eine **Einordnung**. Alle drei stehen in der
Tabelle unten, und zwar nur dort — der Fließtext bleibt Text.

**Die Nummer ist die Kennung.** Sie wird einmal vergeben und **nie wieder**, auch nicht, wenn der
Punkt erledigt ist und in die [history.md](history.md) zieht; dort wird sie beim Umzug genannt.
Zitiert wird sie als „Punkt 7". Neue Punkte bekommen die nächste freie Nummer, nicht die nächste
Zeile — die Reihenfolge in dieser Datei darf sich also von der Zählung lösen, und genau das ist der
Sinn einer stabilen Kennung.

**Vier Arten**, weil vier verschiedene Dinge zu tun sind:

| Art | Was es heißt |
|---|---|
| **Fehler** | Etwas tut nicht, was es zusagt. |
| **Aufgabe** | Klar umrissen, es fehlt nur die Arbeit. |
| **Frage** | Vor der Arbeit ist zu entscheiden, *was* gebaut wird. |
| **Idee** | Noch nicht entschieden, ob überhaupt. |

**Zwei Achsen, und sie sind nicht dasselbe** — das ist der ganze Grund, sie zu trennen:

- **dringend** — es trifft heute jemanden (einen Besucher am Gerät oder das Museumsteam bei der
  Arbeit), oder es blockiert einen anderen Punkt.
- **wichtig** — ohne das ist das Projekt auf Dauer nicht das, was es sein soll.

Innerhalb jedes Bereichs steht oben, was beides ist, dann was wichtig ist, dann der Rest; bei
Gleichstand Fehler vor Aufgabe vor Frage vor Idee.

## Übersicht

| # | Punkt | Art | Einordnung |
|---|---|---|---|
| | **Verwaltung** | | |
| 31 | [Einstellungen in der Verwaltung pflegen statt in der `.env`](#31--einstellungen-in-der-verwaltung-pflegen-statt-in-der-env) | Frage | wichtig |
| 34 | [Eine Karte in der Nachbearbeitung des Imports](#34--eine-karte-in-der-nachbearbeitung-des-imports) | Idee | — |
| | **Besucher-Interface** | | |
| 30 | [Die Karte nach Schlagwörtern filtern](#30--die-karte-nach-schlagwörtern-filtern) | Idee | wichtig |
| 40 | [Ein Durchgang über die ganze Oberfläche](#40--ein-durchgang-über-die-ganze-oberfläche) | Aufgabe | wichtig |
| 43 | [Der Zeitschieber soll jahrgenau zählen, nicht jahrzehntgenau](#43--der-zeitschieber-soll-jahrgenau-zählen-nicht-jahrzehntgenau) | Aufgabe | — |
| 54 | [Das Layout der Detailansicht dem Bildformat folgen lassen](#54--das-layout-der-detailansicht-dem-bildformat-folgen-lassen) | Idee | — |
| 8 | [Historische Karte als umschaltbare Grundkarte](#8--historische-karte-als-umschaltbare-grundkarte) | Idee | wichtig |
| 9 | [Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode](#9--bilder-in-bewegung-diashow-ken-burns-effekt-attract-mode) | Idee | wichtig |
| | **Infrastruktur** | | |
| 14 | [Bedienbarkeitstest mit der echten Zielgruppe](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) | Aufgabe | wichtig · dringend |
| 15 | [Abnahme auf dem ersten Pi](#15--abnahme-auf-dem-ersten-pi) | Aufgabe | wichtig |
| 18 | [Wiederherstellung wirklich proben](#18--wiederherstellung-wirklich-proben) | Aufgabe | wichtig |
| 19 | [Displayauflösung und -orientierung des Museumsgeräts](#19--displayauflösung-und--orientierung-des-museumsgeräts) | Frage | wichtig |
| 20 | [Das Gerät muss einen Stromausfall überstehen](#20--das-gerät-muss-einen-stromausfall-überstehen) | Frage | wichtig |
| | **Entwicklung** | | |
| 21 | [Deployment auf einem Webserver evaluieren](#21--deployment-auf-einem-webserver-evaluieren) | Frage | wichtig · dringend |
| 22 | [Versionierung, Releaseprozess und Veröffentlichung des Codes](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes) | Frage | wichtig |

**Kein Fehler ist offen.** Was hier steht, ist Arbeit und Frage, nicht Reparatur. Die drei aus
dem Durchgang über den Code vom 19. August 2026
([Punkt 39](history.md#punkt-39-der-durchgang-von-aussen)) sind noch am selben Tag behoben
worden — 57, 58 und 59, und keiner von ihnen fiel beim Benutzen auf. Das ist die Eigenschaft,
die sie gefährlich machte, und der Grund, warum ein Durchgang von aussen sie fand.

**Achtundvierzig Nummern sind vergriffen** — 1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 16, 17, 23, 24,
25, 26, 27, 10, 28, 29, 32, 33, 35, 36, 37, 38, 39, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52,
53, 55, 56, 57, 58, 59, 60, 61, 62, 63. Sie sind erledigt, aufgelöst oder gestrichen; was aus jeder wurde, steht in
[history.md](history.md). Der nächste neue Punkt bekommt die **64**.

---

## Verwaltung

### 31 · Einstellungen in der Verwaltung pflegen statt in der `.env`

Was heute eingerichtet wird, wird in Dateien eingerichtet — und zwar in dreien, an drei Orten, mit
drei verschiedenen Wegen:

| Was | Wo heute | Wie geändert |
|---|---|---|
| PIN der Verwaltung | `.env` (`admin_pin_hash`) | `python -m app.cli pin`, Zeile eintragen, neu starten |
| Import-Schlagwörter, Bildnachweis, Herkunft | `.env` | Datei bearbeiten, neu starten |
| EXIF-Jahresgrenze | `.env` | dito |
| Anklickbare Schlagwörter ([Punkt 30](#30--die-karte-nach-schlagwörtern-filtern)) | wäre `.env` | dito |
| Ortsname, Ausschnitt, Zoomstufen, `streetChoice` | `tiles/region.json` → `data/region.json` | Datei bearbeiten, `make tiles` |
| Wappen | `frontend/public/logo.png` | Datei ersetzen, Frontend neu bauen |

Für ein Museumsteam, das ein- bis zweimal im Jahr an das Gerät geht, ist jeder dieser Wege
unerreichbar. **Die Idee ist deshalb richtig; zu klären ist der Zuschnitt.** Vier Fragen, und die
zweite ist die unangenehme:

**1. Was gehört überhaupt hinein?** `data_dir`, `media_dir` und `cors_origins` beschreiben den
Betrieb und gehören ins Deployment — die haben in einer Verwaltungsmaske nichts verloren. Alles
andere aus der Tabelle beschreibt die **Sammlung** oder den **Ort** und ist ein Kandidat.

**2. Nach einer Wiederherstellung sind die Einstellungen weg.** Die Sicherung nimmt neben der
Datenbank und den Bildern nur `region.json` und `places.json` mit (`LOOSE_FILES` in
`services/backup/common.py`) — **die `.env` nicht**. Wer ein Gerät ersetzt und die Sicherung einspielt,
hat den ganzen Bestand zurück, aber keine PIN, keine Import-Schlagwörter und keinen Bildnachweis.
Das ist heute schon so und fällt nur nicht auf, weil es noch kein zweites Gerät gab; **[Punkt
18](#18--wiederherstellung-wirklich-proben) wird es zutage fördern.** Einstellungen in der
Datenbank lösten es nebenbei mit.

**3. Die PIN ist ein Sonderfall in beide Richtungen.** Sie in der Verwaltung zu ändern liegt nahe —
man ist ja drin. Aber in der Datenbank reist sie mit der Sicherung: Wer eine ältere Sicherung
einspielt, bekommt die alte PIN zurück, ohne es zu merken. Und `python -m app.cli pin` wäre dann
eine zweite Quelle für dieselbe Sache. Beides ist lösbar, keines von selbst.

**4. Das Wappen ist keine Einstellung, sondern eine Datei im gebauten Frontend.** Über die
Verwaltung hochladen hieße, in ein Bauartefakt zu schreiben, das nginx statisch ausliefert. Es
müsste nach `data/` wandern und vom Backend kommen — dieselbe Bewegung, die `region.json` schon
gemacht hat, und aus demselben Grund: Was sich ändern darf, gehört unter das eingehängte
Verzeichnis.

**Und die Gegenrechnung, die nicht übersehen werden darf:** [adaption.md](adaption.md) sagt heute,
`region.json` und `.env` seien alles, was ein zweiter Ort anfassen muss — zwei Dateien, die man
weitergeben, vergleichen und in ein Repo legen kann. Wandern die Werte in die Datenbank, wird
daraus „starten und durch die Verwaltung gehen". Für Ehrenamtliche besser; für den, der ein
zweites Museum aufsetzt, ist die eine übergebbare Datei dann weg. Vielleicht ist die Antwort
beides: Datei als Startwert, Datenbank als Übersteuerung — genau das gehört durchdacht, bevor
etwas gebaut wird.

### 34 · Eine Karte in der Nachbearbeitung des Imports

Nach einem Upload steht eine Tabelle mit bis zu dreißig Zeilen (`REVIEW_LIMIT`), in der Titel,
Jahr und **Ort** je Foto nachgetragen werden. Der Ort wird dort über die Ortssuche eingegeben
(`admin/PlaceField.tsx`) — getippt, mit Tastatur, was im Verwaltungsbereich in Ordnung ist. Wer
die Stelle aber *sieht* und den Straßennamen nicht weiß, ist damit ausgesperrt; im Kiosk gibt es
für genau diesen Fall den Kartentipp.

**Zu klären, bevor daraus eine Aufgabe wird:**

- **Was die Karte dort kostet.** Sie ist eine MapLibre-Instanz mit WebGL-Kontext. Verwaltung und
  Kiosk laufen nie gleichzeitig — die Verwaltung ersetzt die Ansicht —, es bliebe also bei einer;
  ob das auf einem Pi neben dreißig Vorschaubildern trägt, ist zu messen.
- **Eine Karte für dreißig Zeilen oder eine je Zeile.** Dreißig Karten sind sicher zu viel;
  denkbar wäre eine, die sich beim Antippen einer Zeile öffnet und den Punkt für diese Zeile
  setzt.
- **Ob es sich überhaupt lohnt.** Der Stapel-Import setzt Ort und Jahr **einmal für alle**, und
  genau dafür ist er gebaut: vierzig Bilder desselben Hofes. Die Zeilennachbearbeitung ist der
  Ausnahmefall im Ausnahmefall.

Nicht wichtig, nicht dringend — erst zu prüfen und zu bewerten, dann zu spezifizieren.

---

## Besucher-Interface

### 30 · Die Karte nach Schlagwörtern filtern

Die Karte filtert heute nach **Zeit** (Schieber) und **Ort** (Ausschnitt). Ein drittes Sieb kommt
dazu: das Schlagwort. Unten in der Ecke der Karte stehen einige wenige zur Wahl, und **immer nur
eines ist aktiv** — ein zweiter Tipp auf dasselbe schaltet es ab, ein Tipp auf ein anderes löst das
bisherige ab. Kein Und, kein Oder, keine Liste zum Abhaken.

**Dazu ein Weg aus der Detailansicht.** Die Schlagwörter eines Fotos sind dort heute nur Text
(`overlay__tags`, drei Zeilen in `PhotoOverlay.tsx`). Ein Tipp darauf soll die Ansicht schließen
und die Karte danach filtern — **Zeit und Ort weit offen**, andere Schlagwörter abgewählt. So
kommt man an Schlagwörter heran, die unten in der Ecke gar nicht angeboten werden. Das so gewählte
erscheint dort dann **neben** den eingerichteten, als ausgewählt, bis es abgewählt wird; danach
verschwindet es wieder samt seiner Auswahlmöglichkeit. Die eingerichteten bleiben.

**Der Bestand ist dafür heute nicht bereit, und das ist der wichtigste Satz dieses Punktes.**
Nachgezählt an den 929 Fotos:

| Schlagwort | Fotos | |
|---|---|---|
| Gebäude | **929** | trägt *jedes* Foto — filtert nichts weg |
| Hauptstraße | 227 | Straßenname, den die Karte über den Ort schon abbildet |
| Förderkreis-Cloud | 142 | Archivkürzel |
| ArchivHolm | 114 | Archivkürzel |
| Winter | 53 | das erste, das etwas über das Bild sagt |

Von 308 Schlagwörtern saßen **260 auf weniger als zehn Fotos**, und „Erntefest" — das Beispiel aus
der Idee — gibt es nicht; es gibt „Fest" und „Feuerwehr". **Die Archivkürzel und die abgeschriebenen
Fotorückseiten sind inzwischen heraus** ([history.md](history.md), 12. August 2026); von 308
Schlagwörtern sind 253 geblieben, und die sind alle wirklich Stichwörter. Ob sie für einen Filter
taugen, ist damit erst jetzt zu beurteilen — und die Zahlen in diesem Punkt sind vom 9. August und
entsprechend zu erneuern.

**Warum die Auswahl eingerichtet wird und sich nicht aus dem Bestand ergibt:** Die naheliegende
Regel wäre „die häufigsten", wie sie die angebotenen Jahrzehnte aus der Sammlung ableitet
(`kiosk/decades.ts`). Hier ergäbe sie „Gebäude, Hauptstraße, Förderkreis-Cloud" — die Häufigkeit
misst hier nicht Bedeutung. Also eine kuratierte Liste, zunächst als Umgebungsvariable neben
`import_tags` in `config.py`. Sie beschreibt die **Sammlung**, nicht den Ort, und gehört deshalb
gerade **nicht** in `region.json`.

**Was technisch fehlt:** `/api/photos` kennt keinen Schlagwortfilter (`api/photos.py`), nur
`/photos/tags/alle` gibt es schon. Dazu ein Zustand im Kiosk-Store neben `timeRange` und `bbox`,
der bei jeder Abfrage mitgeht — und die Abstimmung mit dem Fokus nach einem Beitrag, der Ort und
Zeit heute schon verstellt und zurücknimmt.

### 40 · Ein Durchgang über die ganze Oberfläche

Die Ansicht ist über zehn Stufen gewachsen, und jede Stufe hat für sich gestimmt. Was fehlt, ist
der Blick auf das Ganze: Rückmeldungen einholen, auf Einheitlichkeit prüfen, sammeln, was auffällt,
und es dann in einem Zug umsetzen statt in zwölf Einzelentscheidungen.

**Drei Befunde standen schon als eigene Punkte** und waren damit die erste Ernte dieses
Durchgangs, nicht sein Ersatz: Punkt 10 (Maße der Detailansicht) — und Punkt 28 (die
Knopfsprache) sowie Punkt 29 (der Kopfbereich). Alle drei sind inzwischen erledigt. Dass ein
Befund einzeln lösbar war, spricht nicht gegen diesen Punkt: Die Knopfsprache stand als eigener
Punkt da, *weil* jemand sie am Stück angesehen hatte. Genau das soll hier für den Rest passieren.

**Was dieser Punkt darüber hinaus leistet:**

- **Rückmeldungen einholen**, und zwar von Menschen, die das Gerät nicht gebaut haben. Der
  ergiebigste Weg dafür steht schon als
  [Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) hier — zusehen, ohne zu helfen.
  Dieser Punkt ist das, was danach mit dem Gesehenen passiert.
- **Beide Bereiche vergleichen.** Besucheransicht und Verwaltung haben eigene Maße für Knöpfe,
  Eingabefelder und Mindesthöhen; die 48 px aus der Zielgruppen-Regel sind an jeder Stelle einzeln
  eingehalten statt an einer. Das ist erträglich, solange es jemand weiß — und ein Fallstrick,
  sobald es niemand mehr weiß.
- **Sammeln statt sofort ändern.** Eine Liste, die am Stück entschieden wird, ergibt eine
  Oberfläche; zwölf einzeln entschiedene Kleinigkeiten ergeben zwölf Sonderfälle.

**Der erste Eintrag dieser Liste liegt schon vor.** Er stand bis zum 9. August 2026 als eigener
Punkt 13 hier: Beim Angleichen von „Hilf mit:" an „Bilder aus" (`45ae42d`) wurde aus dem Akzentbraun
eine stille graue Zeile — die bewusste Folge einer bewussten Entscheidung, aber es war zugleich der
einzige Blickfang der linken Spalte. Als eigener Punkt war das zu klein, um je an die Reihe zu
kommen, und zu vereinzelt, um richtig entschieden zu werden: Ob der Beitragsbereich seinen Zug aufs
Auge zurückbekommt, ist eine Frage an die Farbverteilung des ganzen Schirms, nicht an eine Zeile.
Genau dafür ist dieser Punkt da.

### 8 · Historische Karte als umschaltbare Grundkarte

**Der größte Posten auf dieser Seite** — und die einzige Idee, die aus einer schönen Karte eine
Aussage macht.

**Warum.** Historische Fotos auf einer historischen Karte. Der Besucher sähe das Foto *und* den
Ort, wie er damals aussah — und der Zeitschieber, der bisher nur filtert, bekäme eine zweite
Bedeutung.

**Woher.** Preußische Landesaufnahme (um 1880) oder Urkataster. Schleswig-Holstein stellt
Geobasisdaten über sein Open-Data-Portal bereit; ob die historischen Blätter für Kreis Pinneberg
dabei und in brauchbarer Auflösung sind, ist **ungeprüft**. Das ist der erste Schritt, nicht der
Code.

**Wie es ins Projekt passt.** Rasterkacheln, einmal heruntergeladen und als zweite PMTiles-Datei
verpackt — dasselbe Muster wie die heutige Kartendatei, kein neuer Datenweg und kein Bruch mit dem
Offline-Betrieb. `make tiles` bekäme einen zweiten Schritt.

**Der Haken, der die Form bestimmt.** Auf einer Karte von 1880 fehlen die Straßen, die es heute
gibt. Ortssuche und Verortung durch Besucher hängen aber an heutigen Straßennamen. Also
**umschaltbar**: heutige Karte zum Verorten, historische zum Anschauen. Ein Knopf auf der Karte,
kein Ersatz.

**Vorher zu klären:**

- Gibt es die Blätter für Holm, und in welcher Auflösung?
- Lizenz — meist DL-DE/BY-2.0 oder CC-BY, also mit Namensnennung nutzbar. Nachlesen, nicht
  annehmen. Die Nennung gehört dann neben die OpenStreetMap-Zeile.
- Größe. Raster ist um ein Vielfaches schwerer als Vektor; für 5 km Umkreis und Zoom 13–16 sollte
  es im zweistelligen Megabyte-Bereich bleiben, das ist zu messen.

*Der billige Teil ist bereits gebaut: der Kartenstil „Papier" in den Farben der Oberfläche
(`2e648f6`).*

### 9 · Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode

Heute lädt der Leerlauf nach fünf Minuten die Seite neu (`IDLE_MS` in `kiosk/idle.ts`) — der
Bildschirm steht dann in der Standardansicht und wartet. Ein bewegtes Bild würde Besucher eher an
das Gerät holen.

**Zu evaluieren ist der Ken-Burns-Effekt** — das langsame Fahren und Zoomen über ein stehendes
Foto, das Bewegung erzeugt, ohne dass etwas geschnitten werden müsste. Wenn er nicht trägt,
wenigstens eine schlichte Diashow. **Zwei Stellen hätten etwas davon, und das ist das eigentliche
Argument:** Was hier gebaut wird, wird zweimal gebraucht.

1. **Der Attract-Mode** bei Leerlauf, statt der wartenden Standardansicht.
2. **Die Blätteransicht in der Detailansicht.** Liegen mehrere Fotos an derselben Stelle, öffnen
   sie sich als Stapel und werden durchgeblättert (`stepInStack`, „x von y" im Überlagerungsbild).
   Heute nur von Hand — als Galerie, die von selbst weiterläuft, wäre das dieselbe Mechanik.

**Was vorher zu messen ist, und zwar am Gerät:**

- **Bewegtbild neben der Karte.** MapLibre hält bereits einen WebGL-Kontext. Eine
  CSS-Transformation über ein bildschirmfüllendes Foto ist für sich billig, zusammen mit der Karte
  auf einem Pi aber nicht selbstverständlich. Das gehört zum Dauerlauf aus
  [Punkt 15](#15--abnahme-auf-dem-ersten-pi): Ein Effekt, der stundenlang läuft,
  ist genau die Sorte Sache, an der ein Kiosk langsam stirbt.
- **Die Auflösung reicht möglicherweise nicht.** Vorschaubilder liegen in 240 und 1200 px
  (`THUMBNAIL_SIZES`). Auf einem 1080p-Schirm ist ein 1200er Bild knapp — und ein Ken-Burns-Effekt
  *zoomt hinein*, vergrößert den Mangel also. Entweder wird dafür das Original geladen, was
  mehrere Megabyte je Bild bedeutet, oder es kommt eine dritte Vorschaugröße dazu.

**Was der Attract-Mode nicht darf:** die Arbeit von jemandem wegwerfen, der gerade etwas
beigetragen hat. Der Leerlauf lädt heute neu, gerade *weil* das der sichere Zustand ist — derselbe
Zielkonflikt ist beim Wappen schon einmal entschieden worden, das seit dem 9. August 2026 neu
lädt (Punkt 29, erledigt): Dort war die Antwort, dass der Verlust hinnehmbar ist, weil es sonst
gar keinen Weg zurück gibt. **Beim Attract-Mode gilt das nicht** — er startet von selbst, und was
er wegwirft, hat niemand weggeworfen.

### 54 · Das Layout der Detailansicht dem Bildformat folgen lassen

**Der Rest von Punkt 10**, der am 16. August 2026 bewusst liegen geblieben ist. Behoben sind dort
die drei pragmatischen Teile: Die Textspalte wächst mit statt fest zu stehen (auf 1024 px bekommt
das Bild 610 statt 466 px), die Blätterknöpfe stehen fest am unteren Rand, und der Schließen-Knopf
sitzt in der Ecke des Schirms. Siehe [history.md](history.md) und
[decisions.md](decisions.md), Punkt 44.

**Was offen bleibt, ist der Weg an die Ursache:** Ein Querformat braucht Breite und hat Höhe übrig
— der Text gehörte dann **darunter**. Ein Hochformat braucht Höhe und hat Breite übrig — dort ist
der Text **daneben** richtig, so wie heute. Die Ansicht weiß, was sie zeigt: Das Bild trägt sein
Seitenverhältnis als `aspect-ratio` (`PhotoOverlay.tsx`), und `.overlay__content` ist ein Raster
mit zwei Spalten, das sich auf eine umstellen ließe.

**Der Bestand sagt, dass es sich lohnt: 884 Querformate gegen 44 Hochformate.** Genau deshalb ist
es aber nichts, was man nebenbei macht — die Umstellung trifft fast jedes Foto der Sammlung, und
ob sie besser aussieht, entscheidet sich auf einem Gerät in einem Raum und nicht in einem
Browserfenster.

**Deshalb wartet dieser Punkt auf
[Punkt 19](#19--displayauflösung-und--orientierung-des-museumsgeräts)**, und zwar wirklich: Steht
das Gerät am Ende **hochkant**, dreht sich die Rechnung um und die Umstellung müsste in die andere
Richtung gehen. Solange die Auflösung nicht feststeht, wäre jede Zahl hier eine Annahme.

### 43 · Der Zeitschieber soll jahrgenau zählen, nicht jahrzehntgenau

Die Balken hinter dem Zeitschieber zeigen heute nicht immer Jahre. `bar_width()` in
`backend/app/services/dates.py` weitet die Balken auf **zehn Jahre**, sobald irgendwo im Bestand
auch nur ein einziges Foto als „1920er" statt als Jahr datiert ist — und das betrifft praktisch die
ganze Sammlung: 673 der 929 Fotos tragen gar kein Jahr, aber ein gutes Stück des Rests trägt nur ein
Jahrzehnt. Die Folge: Ein Jahrzehnt bekommt einen einzigen Balken, auch wenn darunter drei
jahrgenau datierte Fotos in 1932 liegen und keines in den übrigen neun Jahren — die Verteilung
*innerhalb* der Dekade verschwindet vollständig.

**Gewünscht:** Die Achse zählt immer in Jahren. Ein auf ein Jahrzehnt datiertes Foto trägt zu
**jedem** der zehn Jahre ein Zehntel bei, statt seine ganze Zählung auf ein einziges Jahr (oder,
wie heute, auf einen zehn Jahre breiten Balken) zu häufen — dieselbe Überlegung wie beim
Überlappungs-Filter (`services/dates.py`, siehe CLAUDE.md): eine grobe Angabe verschwindet nicht,
sie verteilt sich ehrlich.

**Was das an der Berechnung ändert:**

- `bar_width()` entfiele in der heutigen Form oder würde auf `1` festgenagelt — die Funktion
  existiert nur, um Balken zu verbreitern, wenn feine Angaben fehlen; genau das soll nicht mehr
  passieren.
- Die SQL-Abfrage in `histogram()` (`api/photos.py`) gruppiert heute nach `bar_start`
  (`date_from` gekappt auf die Balkenbreite) und zählt Fotos. Eine gewichtete Zählung über einen
  Jahresbereich ist damit nicht mehr eine `GROUP BY`-Abfrage über eine Spalte, sondern eine Summe
  über die Jahre zwischen `date_from` und `date_to` — SQLite kennt kein `generate_series`, das
  bräuchte entweder eine Hilfstabelle mit Jahreszahlen oder das Aufsummieren in Python.
- `Bar.count` (`schemas.py`, `frontend/src/api/client.ts`) ist heute ein `int`. Zehntelwerte machen
  daraus einen Bruch — zu klären, ob roh als Fließkommazahl ausgeliefert oder für die Anzeige
  gerundet wird. Die Balkenhöhe (`TimeSlider.tsx`, `barHeight()`) ist bereits relativ zum höchsten
  Balken und käme mit Fließkommazahlen ohne Änderung aus; die Beschriftung `title={...}: ${count}`
  müsste einen Nachkommawert vertretbar formatieren.
- **Was unverändert bleibt:** Der Zeit*filter* selbst fragt weiterhin auf Überlappung ab
  (`date_from <= bis AND date_to >= von`) und zeigt ein jahrzehntdatiertes Foto bei jeder Auswahl,
  die die Dekade berührt — das hier betrifft nur die **Visualisierung** hinter dem Schieber, nicht,
  welche Fotos eine Auswahl zurückgibt.

**Zu prüfen vor dem Bauen:** Ob `MAX_BARS` (heute 30, zur Verbreiterung großer Zeitspannen) in
einer Welt ohne Balkenverbreiterung noch dieselbe Rolle spielt — bei jahrgenauer Zählung über einen
Bestand von hundert Jahren stünden sonst hundert schmale Balken, wo heute zehn breite stehen.

---

## Infrastruktur

### 14 · Bedienbarkeitstest mit der echten Zielgruppe

Eine ehrenamtliche Person die Sicherung durchführen lassen, **ohne zu helfen**, und zusehen, wo sie
stockt. Der aussagekräftigste Test des ganzen Projekts — und die zweite Hälfte des
Abnahmekriteriums von Stufe 9, die bisher fehlt.

**Dringend ist er, weil er kein Gerät braucht.** Über
[Punkt 21](#21--deployment-auf-einem-webserver-evaluieren) steht das System dem Museumsteam zur
Verfügung, bevor Display und Pi beschafft sind — und damit ist dieser Test heute durchführbar statt
erst nach der Beschaffung. Was er zutage fördert, ändert womöglich Dinge, die danach teurer zu
ändern sind.

### 15 · Abnahme auf dem ersten Pi

**Der gewichtigste offene Punkt des Projekts** — dringend ist er nur nicht, weil das Gerät fehlt.
Alles unter `deploy/pi/` ist **ungeprüft**; beim Bauen gab es keins. Die Shell-Syntax stimmt,
gelaufen ist nichts. Betroffen sind `setup-pi.sh`, `kiekmap-kiosk`, `kiekmap-kiosk.service`,
`update.sh`, `99-kiekmap-usb.rules` und `kiekmap-usb-mount`.

**Die Container selbst sind es nicht mehr** (Punkt 17, erledigt am 14. August 2026): Beide Abbilder
bauen, nginx liefert die Karte kachelweise aus, die Seite fragt nichts Fremdes an, und der
Schemastand wird beim Start nachgezogen. Geprüft wurde auf einem Mac, und das lässt genau zwei
Dinge offen, die hierher gehören: **der USB-Weg** (siehe Punkt 18) und **das Verhalten nach einem
Neustart oder Stromausfall** — `restart: unless-stopped` ist eine Zusage, die nur ein Gerät
einlösen kann.

**Der erste Pi ist damit zugleich die Abnahme der Stufen 9 und 10.** Was zuerst hakt, gehört nach
[operations.md](operations.md).

Die erwarteten Stolpersteine, damit sie nicht erst gesucht werden müssen:

- **`:rshared` am `/media`-Mount.** Ein Docker-Bind-Mount zeigt später eingehängte Datenträger nur
  mit dieser Propagation. Ohne sie bleibt ein eingesteckter Stick **ohne Fehlermeldung**
  unsichtbar — der teuerste Fehlerfall, weil er wie „kein Stick" aussieht.
- **`uid=1000` bei FAT-Sticks**, sonst gehört der Einhängepunkt root und die Sicherung schreibt
  nicht.
- **Schwarzer Bildschirm mit der Meldung *„unable to open primary DRM device"*:** Dann fehlt eine
  der vier Sitzungszeilen `PAMName`, `TTYPath`, `StandardInput`, `UtmpIdentifier` in der
  systemd-Unit, oder der Benutzer ist nicht in den Gruppen `video`/`render`.

**Die sechs Prüfungen.** Sie standen bis zum 9. August 2026 als eigener Punkt 16 hier, dessen Text
mit „Der praktische Teil von Punkt 15" begann — zwei Nummern für eine Sache. Die letzten beiden
kamen aus Punkt 12 und 24 dazu:

- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Gezogener Netzstecker im Betrieb** — hier zeigt sich, ob
  `--disable-session-crashed-bubble` das tut, wofür es gedacht ist.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen. Kioske
  sterben an einem langsamen Leck im Frontend, nicht am Backend.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.
- **Der 100-m-Fokus nach einem Besucherbeitrag.** Die Karte fährt auf hundert Meter heran, die
  Vektorkacheln reichen aber nur bis Zoom 15. MapLibre skaliert sauber hoch, die Beschriftungen
  werden dabei groß. Wirkt das im Museum unruhig, ist **der Radius die Stellschraube, nicht die
  Bauform** — deshalb ist es eine Prüfung und keine Aufgabe.
- **Eine USB-Tastatur im laufenden Betrieb anstecken.** Wird sie erkannt, ohne dass jemand den Pi
  neu startet?

**Wozu die Tastatur gebraucht wird**, damit die Prüfung ihren Sinn behält: Die Besucheransicht
braucht seit dem 8. August 2026 keine mehr (siehe [history.md](history.md)) — der
Verwaltungsbereich dagegen hat **13 Eingabefelder in sieben Dateien**, und daran soll sich nichts
ändern: Wer Fotos pflegt, tippt. Die Antwort steht damit fest — eine **ausleihbare** Tastatur, die
nur zur Pflege angesteckt wird. Sie liegt dann nicht im Ausstellungsraum herum, verschmutzt nicht
und öffnet den Besuchern keine Tastenwege in Chromium, die der Kiosk gerade zumacht (F11, Strg-W,
Alt-Tab). Offen ist nur noch die Prüfung oben.

### 18 · Wiederherstellung wirklich proben

Auf ein zweites, leeres Gerät zurückspielen. **Ein ungetestetes Backup ist kein Backup.** Erprobt
ist bisher nur der Weg gegen ein `hdiutil`-Prüfvolumen auf dem Mac.

**Der USB-Weg im Container ist weiterhin ungeprüft**, und zwar als Einziges aus dem erledigten
Punkt 17: Die Prüfung des Containerbetriebs am 14. August 2026 lief auf einem Mac, wo es weder
`/media` noch die Mount-Propagierung `rshared` gibt (siehe
[`deploy/docker-compose.mac.yml`](../deploy/docker-compose.mac.yml)). Genau `rshared` soll aber den
Fall lösen, dass ein Stick **nach** dem Start des Containers eingesteckt wird — der Fall, der im
Museum der Normalfall ist. Er braucht Blech und gehört in denselben Durchgang wie diese Probe.

### 19 · Displayauflösung und -orientierung des Museumsgeräts

Steht noch nicht fest und beeinflusst die Layoutmaße. Die Ansicht ist bisher gegen 1280 × 800
nachgemessen; die Variable `--crest` hat für schmale Schirme bereits eine Media Query.

**Zwei Punkte warten auf diese Antwort**, und beide werden von ihr nicht nur abgestuft, sondern
umgestellt:

- [Punkt 54](#54--das-layout-der-detailansicht-dem-bildformat-folgen-lassen), das Layout der
  Detailansicht. Steht das Gerät **hochkant**, dreht sich die Rechnung um: Dann hat das
  querformatige Bild Breite im Überfluss und der Text darunter Platz.
- Der Kopfbereich hat sich davon inzwischen gelöst (Punkt 29, erledigt): Die drei Elemente
  richten sich an einer gemeinsamen Mittellinie aus statt an drei Rechnungen, und das gilt in
  jeder Breite. **Die Auflösung entscheidet dort nichts mehr** — ein Hinweis darauf, dass eine
  Abhängigkeit von dieser Frage auch eine schlecht gebaute Stelle sein kann.

**Die Frage ist also kleiner, als sie aussieht, und sollte früh gestellt werden**: Es ist eine
Frage an das Museum, keine an den Code, und sie kostet nichts als ein Telefonat.

### 20 · Das Gerät muss einen Stromausfall überstehen

Gegen SD-Karten-Korruption bei Stromausfall. Der Pi wird im Museum nicht heruntergefahren, sondern
ausgeschaltet — das ist auf Dauer der wahrscheinlichste Ausfallgrund.

**Das Ziel steht, der Weg nicht.** Zu verhindern ist, dass ein Verlust der Stromversorgung mit
hoher Wahrscheinlichkeit dazu führt, dass das Gerät **nicht mehr unterbrechungsfrei startet**. Ein
Read-Only-Overlay ist dafür ein Mittel, nicht die Aufgabe — der Punkt hieß bis zum 16. August 2026
nach dem Mittel und ist deshalb umbenannt.

**Erst abzuwägen ist das Risiko**, bevor irgendetwas gebaut wird: Wie wahrscheinlich sind
Datenverlust und ein beschädigtes Dateisystem beim Ziehen des Steckers überhaupt? SQLite läuft im
WAL-Modus mit `synchronous=NORMAL`, was für die Datenbank selbst schon einiges abdeckt; die Frage
gilt der SD-Karte und dem Betriebssystem darauf.

**Eine leichtere Möglichkeit steht im Raum:** in der Verwaltung statt „Anzeige neu laden"
(`t.admin.…reload`) einen **Herunterfahren-Knopf**. Dann gäbe es einen geordneten Weg, das Gerät
auszuschalten, und ein Read-Only-Overlay wäre womöglich gar nicht nötig. Zu klären wäre, wer diesen
Knopf drückt und was passiert, wenn es niemand tut — die Abwägung gehört vor die Entscheidung.

*Aufgenommen am 16. August 2026, ausdrücklich noch ohne Analyse.*

---

## Entwicklung

Nicht das Programm, sondern die Arbeit daran: wie das Projekt geordnet, veröffentlicht und
weitergegeben wird.

### 21 · Deployment auf einem Webserver evaluieren

Das System dem Museumsteam **zunächst online** anbieten — zur Erprobung und vor allem zum Aufbau
der Fotodatenbank, bevor ein Pi im Ausstellungsraum steht. Die Bilder könnten so über Monate von
zu Hause aus eingepflegt werden.

**Das macht diesen Punkt dringend**, obwohl er nach einer Evaluierung aussieht: Sein Wert ist
zeitgebunden. Solange kein Zugang steht, pflegt niemand Fotos ein, und jede Woche Verzögerung ist
eine verlorene Woche Datenbankaufbau. Ausserdem hängt
[Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) daran — der Bedienbarkeitstest wird
so möglich, bevor Hardware beschafft ist.

Technisch ist der Weg kurz, und seit dem 14. August 2026 ist das keine Annahme mehr, sondern
gemessen (Punkt 17): Es läuft in Containern (`make prod`), das Frontend ist statisch, nginx steht
davor, und die Datenbank ist eine Datei. Die Fragen liegen woanders:

- **Was aus dem Offline-Versprechen wird.** Die Regel „null Anfragen an eine fremde Herkunft" bleibt
  erfüllt, sie kostet online nur nichts mehr. Umgekehrt gilt: Kartendatei und Ortsindex sind auf
  einen Rechner im Ausstellungsraum zugeschnitten — 4,6 MB Kacheln und 1,5 MB Ortsindex über eine
  langsame Leitung sind spürbar, aber tragbar.
- **Wie die Daten zurück auf den Pi kommen.** Das ist der eigentliche Zweck, und dafür gibt es das
  Werkzeug bereits: Sicherung und Wiederherstellung. Zu prüfen ist, ob der Weg auch als
  Übertragungsweg taugt — dann wäre der Umzug vom Webserver ins Museum ein bekannter Vorgang und
  kein Sonderfall.

#### Der Entwurf steht — am 15. August 2026 entschieden

Die Frage nach dem Zugriffsschutz ist beantwortet, damit sie beim Aufgreifen nicht noch einmal
gestellt werden muss.

**Eine Tür vor der ganzen Anwendung, nichts in ihr.** Das löst die offene Beitragstür und die
fehlende Ratenbegrenzung in einem Zug — beides ist hinter einer Anmeldung kein Problem mehr. Der
umgekehrte Weg, den Schutz *in* die Anwendung zu bauen, verbögte die Besucheransicht dauerhaft für
einen Betrieb, der Wochen dauert.

```
Internet ──HTTPS──► Caddy ──HTTP──► nginx (frontend) ──► uvicorn (backend)
                      │                unveraendert        unveraendert
                 Let's Encrypt
                 basic_auth
```

**Traefik und Keycloak sind geprüft und verworfen.** Frontend und Backend liegen **schon** auf
einem Ursprung und einem Port — nginx liefert die Seite und leitet `/api/` weiter, das Backend ist
nach aussen gar nicht veröffentlicht. Traefik brächte Routing für Dienste, die es nicht gibt.
Keycloak wäre ein zweites System mit eigener Datenbank für zwei bis fünf Ehrenamtliche, und weil
das Programm kein OIDC spricht, säße es hinter einem Auth-Proxy, der die eigentliche Arbeit tut.
Caddy dagegen ist vier Zeilen: automatisches Let's Encrypt, `basic_auth` eingebaut.

**Entschieden:** ein kleiner VPS in Deutschland (arm64, dieselbe Architektur wie Pi und Mac), ein
gemeinsames Passwort für Team und einzelne Testleser, und `deploy/docker-compose.web.yml` als
dritte Überlagerung neben der des Pi und der des Macs — die Pi-Datei bleibt unangetastet.

**Vier Dinge, die beim Bauen sonst erst wieder auffallen:**

1. **`ports: !reset []` beim `frontend`** ist die sicherheitskritische Zeile: Ohne sie umginge
   `http://<ip>/` den Türsteher. Compose führt `ports` sonst zusammen, statt zu ersetzen.
2. **Auch die API muss ohne Passwort 401 sagen**, nicht nur die Seite. Das ist die Prüfung, für die
   der ganze Entwurf existiert.
3. **Auf einem VPS gibt es keine USB-Sticks.** `find_drives` liefert eine leere Liste, der
   Sicherungsknopf hat kein Ziel — die Sicherung der Online-Instanz ist der **ZIP-Download**, und
   jemand muss ihn regelmässig ziehen. Die Instanz wird für Wochen der massgebliche Bestand sein.
4. **Die Admin-PIN wird länger.** `app.cli pin` nimmt bis zu zwölf Ziffern; vier sind im offenen
   Netz zu wenig, falls das gemeinsame Passwort weitergereicht wird. Kein Codeeingriff.

**Was der Entwurf nicht löst:** Eine Anmeldemaske vor dem Kiosk verfälscht
[Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe). Für Testleser, denen man das
Passwort nennt, ist das hinnehmbar; ein echter Bedienbarkeitstest mit unvorbereiteten Besuchern
gehört vor Ort auf ein Gerät.

#### Zwei Zahlen zum Entwurf, nachgetragen am 19. August 2026

Beim Durchgang über den Code (Punkt 39) sind zwei Dinge gemessen worden, die den Entwurf oben nicht
umstossen, aber schärfen:

**Die Sperre gegen Rateversuche hält 33 Stunden, nicht ewig.** `services/auth.py`: fünf
Fehlversuche, dann 60 Sekunden Sperre — also 300 Versuche in der Stunde und der ganze vierstellige
Raum in rund 33 Stunden. Das ist die Zahl hinter dem Satz „vier sind im offenen Netz zu wenig",
und sie hat eine zweite Seite: Die Sperre gilt **geräteweit**, nicht je Aufrufer. Wer sie auslöst,
sperrt damit auch die Ehrenamtlichen aus. Beim Verlängern der PIN ist deshalb mitzuentscheiden, ob
die Sperre mitwächst (steigende Wartezeit statt fester 60 Sekunden).

**Auch der Pi veröffentlicht Port 80 auf allen Schnittstellen.** `deploy/docker-compose.yml` sagt
`ports: "80:80"`. Für den Entwurf oben ist das gelöst — `ports: !reset []` beim `frontend` ist die
sicherheitskritische Zeile —, für das Gerät im Museum nicht: Sobald der Pi in einem Netz hängt,
ist der Verwaltungsbereich mit der vierstelligen PIN von jedem Rechner darin erreichbar. Solange
das Gerät allein steht, trifft das niemanden; es gehört zu [Punkt 15](#15--abnahme-auf-dem-ersten-pi)
gefragt, wie das Museumsnetz aussieht. Die Gegenmassnahme wäre eine Zeile (`127.0.0.1:80:80`) und
kostet den Zugriff vom Nebenrechner, den das Team vielleicht will.

### 22 · Versionierung, Releaseprozess und Veröffentlichung des Codes

**Stand:** `development.md` kündigt SemVer-Tags und Conventional Commits an, beides zusammen
versioniert. Tatsächlich gibt es nach 99 Commits **keinen einzigen Tag**; `package.json` und
`pyproject.toml` stehen beide auf `0.1.0`, und `deploy/docker-compose.yml` baut Images mit
`${KIEKMAP_VERSION:-dev}`. Es fehlt also nicht die Entscheidung, sondern ihre Umsetzung: Was löst
eine Version aus, wer setzt den Tag, und wie kommt die Nummer in die beiden Dateien und in das
Image?

Daran hängt der Updateweg auf den Pi, der schon gebaut ist (`deploy/pi/update.sh` spielt ein
Update vom Stick ein) — er braucht etwas, das er einspielen kann.

**Die zweite, größere Frage: Wie öffentlich wird das Repo?** Zu recherchieren sind die üblichen
Vorgehensweisen und ihre Vor- und Nachteile. Die Bandbreite reicht von „alles öffentlich, von der
ersten Zeile an" bis „privates Arbeitsrepo, öffentlich nur die Release-Stände". Kurz gefasst:
Vollständige Offenheit ist die übliche und die ehrlichste Form, sie macht aber jede Zwischenstufe
und jeden Fehlversuch dauerhaft sichtbar; ein reines Release-Repo schützt davor, verliert aber die
Historie, die dieses Projekt gerade auszeichnet — die Commit-Nachrichten hier tragen die
Begründungen.

**Die beiden Blocker davor sind erledigt** (5. August 2026): das Wappen ist aus Repo und Historie
verschwunden, der Beispielbestand ist erfunden und mitgeliefert. Wie das ausging und was dabei
anders kam als geplant, steht in [history.md](history.md). **Offen bleibt der Releaseprozess
selbst.**

**Die Lizenzfrage ist seit dem 20. August 2026 beantwortet** (Punkt 23): Apache-2.0, Copyright
Kalle Erlhoff, `LICENSE` und `NOTICE` liegen an der Wurzel. Was daraus für ein Release folgt, steht
in [licensing.md](licensing.md) — und ein Satz daraus gehört hierher, weil er den Releaseprozess
festlegt: **Dockerfiles veröffentlichen, keine gebauten Abbilder.** Ein Abbild aus
`python:3.12-slim` oder `nginx:1.27-alpine` enthält GPL-lizenziertes Debian- bzw. Alpine-Userland;
wer es weitergibt, übernimmt dessen Pflichten. Wer nur die Dockerfiles veröffentlicht, lässt sie
dort, wo sie hingehören. Der Weg über `abbilder.tar` in `deploy/pi/update.sh` bleibt für das eigene
Gerät richtig.

Dazu die Frage, die ein Release erst auslöst: Was passiert mit `THIRD-PARTY.txt`? Sie wird erzeugt
und ist eingecheckt, also aktuell — aber nur, solange `make check` läuft. In einer CI
([Punkt 62](history.md)) wäre das automatisch.

**Dazu gehört das Festnageln der Abhängigkeiten**, nachgetragen am 19. August 2026. Das Frontend
hat eine `package-lock.json`; `backend/pyproject.toml` nennt nur untere Schranken (`fastapi>=0.115`,
`pillow>=11.0` …) und es gibt keine Lockdatei. Ein Neubau des Abbilds in einem Jahr zieht damit
andere Versionen als der heutige. Bei einem Dienst, der wöchentlich neu gebaut wird, fällt das
sofort auf; bei einem Gerät, das offline steht und einmal im Jahr angefasst wird, fällt es im
Museum auf. Eine Lockdatei (`pip-compile`, `uv lock`) macht aus einer Version eine Zusage — und
gehört zu dem, was ein Release überhaupt erst zu einem Release macht.

#### Namen und Adressen im Repo — vor der Veröffentlichung zu entscheiden

Die Frage kam am 21. August 2026 auf und lautete zuerst: *Sollen die Abschnitte zur Bereinigung des
Erstbestands aus der [history.md](history.md) heraus? Oder reicht es, personenbezogene und
konkrete Adressdaten zu entfernen und zusammenzufassen, was getan wurde?*

**Nachgezählt sieht die Frage anders aus, als sie gestellt war.** Echte Namen aus dem Holmer
Bestand — Familien, Hofnamen, Gaststätten, Geber, ein aktueller Eigentümer — stehen an

| | Zeilen |
|---|---|
| Dokumentation gesamt | 19 |
| davon `history.md` | 7 |
| davon `decisions.md` | 11 |
| Quelltext | 32 |
| davon in Testdateien | 22 |

**Die Historie ist also der kleinere Teil**, und sie herauszuschneiden löste das Problem nicht. Der
Schwerpunkt liegt in den Tests, und zwar aus einem guten Grund: CLAUDE.md verlangt dort ausdrücklich
echte Holmer Daten, *„weil sie den Fall konkret machen"*. Genau diese Regel kollidiert jetzt mit der
Veröffentlichung.

**Die Fälle sind unterschiedlich schwer, und das Zusammenwerfen macht die Entscheidung schwierig:**

1. **Eine lebende, identifizierbare Person an einem Grundstück** — eine Fundstelle, eine
   Archivnotiz der Form „heute (Jahr) <Name>". Der klarste Fall, weil hier Name, Ort und Gegenwart
   zusammenkommen.
2. **Namen von Gebern und Leihgebern** aus dem Herkunftsfeld, drei Fundstellen. Und darin die
   Ironie: [decisions.md](decisions.md), Punkt 36 erklärt die Herkunft zur *internen* Notiz, die den
   Kiosk nie erreichen darf — und zitiert in derselben Datei drei davon wörtlich.
3. **Lange Verstorbene** in historischen Bildunterschriften, etwa zu einem Hof nach einem
   Bombenangriff. Die DSGVO gilt für Verstorbene nicht; ein Persönlichkeitsrecht wirkt fort.
4. **Familien- und Firmennamen an einer Hausnummer** — die Masse der Fundstellen, im Ort öffentlich
   bekannt, einzeln harmlos. In Summe ergeben sie eine Liste, wer wo wohnt.
5. **Eine Bildunterschrift mit Verwandtschaftsangaben und Familienstand**, in einem Test und in
   einem Kommentar. Der schärfste Einzelfund, weil er weit über einen Namen hinausgeht.

**Und die teure Hälfte liegt im Git-Verlauf.** Eine Zeile heute zu ändern nimmt sie aus 177 Commits
nicht heraus; allein einer der Namen kommt in 16 Commits vor. Das ist derselbe Fall wie beim Wappen
am 5. August, und dort ist die Historie umgeschrieben worden. **Deshalb muss das vor der
Veröffentlichung entschieden sein** — danach ist es nicht mehr entscheidbar.

**Vorschlag, wenn es aufgegriffen wird:** nicht herausschneiden, sondern **ersetzen**. Der Wert
dieser Abschnitte liegt im Muster, nie im Wert — dass eine Jahreszahl neben einem Namen der Stand
des Archivs ist und kein Aufnahmedatum, zeigt ein erfundener Name genauso. Dasselbe gilt für das
Kodierungsbeispiel, das nur einen Umlaut braucht. Die Regel wäre die, nach der `seed/` schon lebt:
**Beispiele sind erfunden.** Für die Tests hiesse das, die Sprachregelung in CLAUDE.md um einen Satz
zu ergänzen — Holmer *Koordinaten* ja, Holmer *Namen* nein.

Zu entscheiden bleiben zwei Dinge, und nur das erste ist billig:

- **Reicht Ersetzen im aktuellen Stand?** Dann ist es ein Nachmittag Arbeit an 51 Zeilen.
- **Wird der Git-Verlauf mitgezogen?** Das kostet einen `filter-repo`-Lauf über 177 Commits und
  macht jede vorher gezogene Kopie unbrauchbar. Beim Wappen war die Antwort ja; dort ging es aber um
  eine Datei, nicht um Textstellen in achtundvierzig.

Ein Satz zum Umgang mit dieser Notiz selbst: **Sie nennt bewusst keinen der Namen.** Ein
Backlogeintrag, der die Fundstellen aufzählt, wäre eine Fundstelle mehr.
