# Offene Punkte

Was noch aussteht, nach **Verwaltung · Besucher-Interface · Infrastruktur · Entwicklung**. Die
ersten drei betreffen das Programm, der letzte die Arbeit daran. Was schon gebaut ist, steht in
[history.md](history.md).

Jeder Eintrag trägt mit, was beim Aufgreifen sonst erst wieder herausgefunden werden müsste. Das
ist der Grund, warum er hier steht und nicht in einer Stichwortliste: Ein Punkt ohne seinen
Zusammenhang kostet beim zweiten Anlauf dieselbe Arbeit wie beim ersten.

Nichts hiervon ist terminiert. Innerhalb der Abschnitte stehen **Fehler zuerst**, danach der
Ausbau grob nach Gewicht. Zurzeit ist kein Fehler offen — alles hier ist Ausbau.

---

## Verwaltung

### Fotos löschen — über den bisherigen „Versteckt"-Status

Es fehlt ein Weg, einen Fehlscan, eine doppelt eingelesene Datei oder ein Bild loszuwerden, das
gar nicht ins Museum gehört. Es gibt nur die Ankreuzbox „Verstecken" im Editor, und niemand aus
dem Museumsteam sucht unter diesem Wort nach dem Löschen.

**Gelöscht wird deshalb nichts — der vorhandene Status wird umbenannt und anders bedient.** Die
Bilddatei bleibt liegen, die Datenbankzeile bleibt stehen, und beides ist über „Wiederherstellen"
zurückzuholen.

**Was sich ändert**

- Im Editor **entfällt die Ankreuzbox** „Verstecken" samt ihrem Hinweis. An ihre Stelle tritt eine
  Schaltfläche neben „Speichern" und „Abbrechen": **„Löschen"** — bei einem bereits gelöschten Foto
  heißt sie **„Wiederherstellen"**.
- **„Löschen" fragt zurück.** „Wiederherstellen" nicht: Es macht nichts kaputt.
- Ein Druck darauf ändert den Status, **speichert und kehrt zur Liste zurück** — genau so, wie es
  „Speichern" tut.
- In der Fotoliste heißt der Filter **„Gelöscht"** statt „Versteckt", ebenso die Marke an der Zeile
  und die Kachel in der Übersicht.
- **Kein Mehrfachlöschen.** Dafür bräuchte die Liste erst eine Mehrfachauswahl; das ist ein eigener
  Schritt und ausdrücklich nicht Teil dieses Punktes.

**Warum diese Variante die bessere ist**

Die zuvor hier eingeplante Fassung — Zeile weg, Datei in einen Papierkorb — hatte drei offene
Fragen. **Alle drei entfallen**, weil nichts verschwindet:

| bisher offen | jetzt |
|---|---|
| Kommt ein gelöschtes Foto beim nächsten Import zurück? | Nein. Die Zeile bleibt, der SHA-256 ist bekannt, der Import erkennt die Dublette. |
| Was wird aus Änderungs- und Import-Protokoll? | Nichts. Beide zeigen weiter auf ein Foto, das es gibt. |
| Zählt der Papierkorb in die Sicherung? | Keine Sonderregel — die Datei wird gesichert wie jede andere. |

Und die Zusage in `backend/app/api/admin.py` — *„Nothing is deleted"* — **bleibt wahr**. Sie muss
beim Umsetzen nur präziser werden: Gelöscht heißt hier *aus der Ausstellung genommen*, nicht *von
der Platte entfernt*. Das gehört so auch nach [decisions.md](decisions.md), denn es ist die
eigentliche Entscheidung.

**Umzubenennen**

| | heute | neu |
|---|---|---|
| `app/models.py:52` | `PhotoStatus.HIDDEN = "hidden"` | `DELETED = "deleted"` |
| `app/api/admin.py:170` | `Selection = Literal[…, "hidden"]` | `…, "deleted"` |
| `app/api/admin.py:148,188` | Zählung und Filter | mitziehen |
| `app/schemas.py:409` | `Overview.hidden` | `deleted` |
| `api/admin.ts:28,151,154` | Typen im Frontend | mitziehen |
| `texte/de.ts` | fünf Stellen „Versteckt" / „Verstecken" | „Gelöscht" / „Löschen" |
| `admin/PhotoEditor.tsx`, `Overview.tsx`, `PhotoCare.tsx` | Ankreuzbox, Kachel, Filter, Marke | siehe oben |

**Der teuerste Teil ist die Migration.** Die initiale Migration schreibt den Wert in einem
Check-Constraint fest (`status IN ('published', 'hidden')`,
`alembic/versions/85f5993e7f4f_initial_schema.py:60`). SQLite kann Constraints nicht ändern —
Alembic baut die Tabelle dazu neu (`render_as_batch`), und dabei gehen Details verloren, wenn man
nicht hinsieht (siehe [development.md](development.md), Abschnitt „Datenbank"). Dazu ein `UPDATE`
auf die vorhandenen Zeilen.

*Die billigere Alternative wäre, nur die Oberfläche umzubenennen und den Datenbankwert `hidden` zu
lassen.* Das spart die Migration, hinterlässt aber genau die Sorte Diskrepanz, über die später
jemand stolpert: In der API steht `hidden`, auf dem Schirm „Gelöscht". Empfehlung ist deshalb die
durchgängige Umbenennung — sie ist einmal Arbeit und danach nie wieder ein Thema.

**Was beim Umsetzen auffallen wird**

- **Die Arbeitslisten zeigen gelöschte Fotos mit.** `list_photos()` filtert nur „Ohne Ort" und
  „Ohne Jahr" auf ihr jeweiliges Feld, nicht auf den Status (`app/api/admin.py:183–189`). Heute ist
  das bei „Versteckt" halbwegs vertretbar; sobald es „Gelöscht" heißt, bekommt jemand, der die
  Liste „Ohne Ort" abarbeitet, **gelöschte Fotos zur Bearbeitung vorgelegt**. Zu entscheiden:
  Schließen die Arbeitslisten Gelöschte künftig aus? Und was heißt dann „Alle" — mit oder ohne?
- **„Fotos insgesamt" zählt Gelöschte mit** (`app/api/admin.py:148`). „28 Fotos insgesamt, davon 7
  gelöscht" liest sich anders als „28 Fotos, davon 7 versteckt": Gelöschtes gehört im Kopf nicht
  mehr zum Bestand. Die Zahl gehört vermutlich um die Gelöschten bereinigt — dann muss aber die
  Summe der Kacheln weiterhin aufgehen.
- **„Speichern und zurück" heißt: die übrigen Änderungen im Formular auch.** Wer den Titel ändert
  und dann „Löschen" drückt, speichert beides. Das ist vermutlich richtig, sollte aber eine
  Entscheidung sein und keine Nebenwirkung.
- **Wird eine gelöschte Datei erneut eingelesen, meldet der Import „war schon da"** und ändert
  nichts — das Foto bleibt gelöscht. Für jemanden, der es bewusst noch einmal einliest, um es
  zurückzuholen, ist diese Meldung irreführend. Sie sollte den Fall benennen.

> **Was dabei verlorengeht, und das ist zu wollen:** Es gibt danach keinen Weg mehr, ein Foto nur
> *vorübergehend* auszublenden, ohne es „gelöscht" zu nennen — etwa, solange die Rechtelage geklärt
> wird. Ein Status trägt dann zwei Bedeutungen. Das ist vertretbar, weil „Verstecken" bisher
> praktisch nur zum Aussortieren benutzt wurde; wer es anders sieht, braucht einen dritten Status
> statt einer Umbenennung.

### Sicherung und Wiederherstellung auch als ZIP

Heute geht beides nur über einen USB-Stick. Ein zweiter Weg über den Browser hilft dort, wo kein
Stick zur Hand ist — und beim Entwickeln ohnehin. Der Pi veröffentlicht Port 80, ein Notebook am
Netzwerkkabel kommt also an die Verwaltung heran.

**Die Maske übernimmt die Form, die das Importieren schon hat:** zwei gleichrangige Kacheln für
das Ziel beziehungsweise die Quelle — links Browser/ZIP-Datei, rechts USB-Stick —, darunter **eine
Fläche an fester Stelle**, die den Fortschritt und das Ergebnis des gewählten Weges zeigt. Damit
sieht der Sicherungsbereich aus wie der Importbereich, und wer den einen bedient hat, erkennt den
anderen wieder.

**Umfang: alles, wie auf den Stick** — Fotos, Vorschaubilder und Datenbank in einem Archiv. Eine
halbe Sicherung wäre gefährlicher als keine, weil sie sich wie eine ganze anfühlt.

**Was dabei verlorengeht, und das ist zu benennen:** Das Archiv ist **nicht inkrementell**. Der
Stick schreibt beim zweiten Mal nur, was dazugekommen ist, und ist in Sekunden fertig; das ZIP
packt jedes Mal den ganzen Bestand — bei zweitausend Fotos mehrere Gigabyte. Und ein Abbruch macht
das Archiv wertlos, während eine abgebrochene Ordner-Sicherung teilweise brauchbar bleibt. Genau
diese beiden Eigenschaften waren die Begründung für „Ordner statt ZIP" auf dem Stick
([decisions.md](decisions.md), Punkt 11). Der Browser-Weg ist deshalb die **Ergänzung**, nicht der
Ersatz, und die Oberfläche sollte das sagen.

**Vorher zu klären:** Wird das Archiv im Speicher gebaut (auf einem Pi mit 2 GB keine gute Idee),
auf die SD-Karte geschrieben (die dafür Platz braucht) oder im Strom erzeugt? Letzteres geht mit
ZIP ohne Kompression und ist für JPEGs ohnehin das Richtige — komprimieren bringt bei ihnen
nichts.

### Rechte- und Herkunftsangaben pro Foto

Im Museumskontext oft relevant, bisher **nicht spezifiziert** — weder das Datenfeld noch, wer es
sieht. Vor dem Code zu klären: Gehört die Angabe zum Foto oder zur Sammlung? Steht sie im
Foto-Overlay für Besucher oder nur im Verwaltungsbereich? Und braucht der Stapel-Import ein
gemeinsames Feld dafür, wie er es für Jahr und Ort hat?

### Jahreszahl aus dem Dateinamen raten

`Kirchweih_1932_Muehle.jpg` trägt seine Datierung im Namen, und beim Erstimport von einigen
hundert Scans ist das viel wert.

**Vorsicht:** `IMG_1932.jpg` ist ein Kamerazähler, keine Jahreszahl. Das Ergebnis darf deshalb nur
als **Vorschlag** markiert werden, nie als Tatsache — sonst entsteht genau der Fehler, den die
EXIF-Regel aus Stufe 3 vermeidet: ein falsch datiertes Foto, das nie zur Korrektur vorgelegt wird,
weil es als datiert gilt.

### Perceptual Hash gegen zugeschnittene Dubletten

Der SHA-256 erkennt nur bitgleiche Dateien. Zwei Scans desselben Fotos mit unterschiedlichem
Zuschnitt oder Kontrast sind für ihn zwei verschiedene Bilder — im Museumsbestand ein realistischer
Fall, wenn dasselbe Original zweimal durch den Scanner ging.

### Volltextsuche über SQLite FTS5

Über Titel, Beschreibung und Schlagwörter. Heute sucht die Fotoliste im Verwaltungsbereich nur über
den Titel.

---

## Besucher-Interface

### Tastatur: was ist ohne sie erreichbar, und wollen wir eine?

**Die ganze Besucheransicht hat genau ein Eingabefeld** — die Ortssuche in
`kiosk/LocationTask.tsx:159`. Alles andere ist Knopf: Zeitschieber, Jahrzehnte, Jahre,
Hausnummern, Marker, Blättern, Schließen. Diese eine Stelle entscheidet also die ganze Frage.

**Ohne Tastatur bleibt der Beitragsbereich vollständig bedienbar** — aber auf dem zweiten Weg:
Pin auf die Karte tippen statt Straßennamen suchen. Datieren geht ohnehin nur über Knöpfe. Es
fehlt also keine *Funktion*, es fehlt der bequemere von zwei Wegen zum selben Ziel. Zu prüfen ist,
ob das in der Praxis stimmt: Wer den Hof auf dem Foto kennt, aber nicht weiß, wo er auf einer
Karte liegt, kommt über den Pin **nicht** ans Ziel. Für den ist die Suche der einzige Weg.

**Zu klären, in dieser Reihenfolge:**

1. **Ist der Zustand konsistent?** Ein Suchfeld, das ohne Tastatur nichts annimmt, sieht aus wie
   ein defektes Bedienelement — schlimmer als gar keins. Wenn keine Tastatur kommt, gehört es
   entweder weg oder muss sagen, dass hier getippt werden kann.
2. **Echte Tastatur oder Bildschirmtastatur?** Eine echte Tastatur im Ausstellungsraum ist ein
   Gegenstand, der wegkommt, verschmutzt und nach Büro aussieht; sie öffnet ausserdem Tastenwege
   in Chromium, die der Kiosk gerade zumacht (F11, Strg-W, Alt-Tab). Eine Bildschirmtastatur
   kostet Fläche, muss aber nur dort erscheinen, wo sie gebraucht wird — und ist bei
   Touchbedienung das Erwartete.
3. **Chromium unter `cage` blendet keine Bildschirmtastatur ein.** Es gibt keine vom System; sie
   müsste im Frontend gebaut werden — ein Tastenraster wie das PIN-Feld, aber mit Buchstaben und
   Umlauten. Der Aufwand ist überschaubar, die Fläche ist das Problem.

> **Der Zusammenhang, der die Entscheidung mitbestimmt:** Der Verwaltungsbereich hat **13**
> Eingabefelder in sieben Dateien — Titel, Beschreibung, Schlagwörter, Suche, Jahr, Ortssuche. Die
> sind ohne Tastatur nicht zu bedienen. Wer Fotos am Gerät pflegen will, braucht also ohnehin
> eine; die PIN auf dem Zahlenfeld ändert daran nichts. Denkbar ist deshalb: **keine Tastatur für
> Besucher, eine ausleihbare für die Pflege** — dann muss die Besucheransicht ohne auskommen, und
> Punkt 1 ist zu beantworten.

### Braucht der Kiosk einen eigenen Reload-Knopf?

Auf dem Besucherschirm gibt es heute keinen Weg, die Anzeige zurückzusetzen. Es gibt drei
Umwege: fünf Minuten warten (der Leerlauf lädt neu), die PIN eingeben und die Verwaltung wieder
verlassen (lädt seit `a3a5be7` ebenfalls neu), oder den Netzstecker.

Für einen Besucher, der sich verhakt hat, sind alle drei keine Antwort. Für eine ehrenamtliche
Person, die danebensteht, reicht der Weg über die Verwaltung — aber nur, wenn sie die PIN weiß.

**Was dagegen spricht**, und deshalb ist es eine Frage und keine Aufgabe: Ein Knopf im
Besucherbild, den fast niemand braucht, wird trotzdem gedrückt — von Kindern zuerst. Er nimmt
Fläche, und er wirft die Arbeit weg, die gerade jemand angefangen hat. Die Ansicht kann sich
ausserdem kaum noch verhaken: Der Leerlauf lädt neu statt zurückzusetzen, seit `c32748d`.

**Der naheliegende Mittelweg wäre eine unauffällige Geste** — ein langer Druck auf das Wappen etwa.
Genau diese Bauform wurde in Stufe 8 für den Verwaltungszugang **verworfen**, weil eine unsichtbare
Geste etwas ist, das Ehrenamtliche sich merken müssten (siehe [history.md](history.md), Stufe 8).
Wer sie hier wieder aufgreift, sollte das wissen und begründen.

### Abbruch in der Hausnummern-Auswahl

Sobald eine Straße gewählt ist, zeigt der Beitragsbereich nur noch das Knopfraster der
Hausnummern. Zurück führt von dort einzig „Reicht so" — und das ist **keine** Abbruchtaste,
sondern eine Antwort: Es behält den Pin auf der Straße.

Wer die Straße versehentlich getroffen hat oder es sich anders überlegt, braucht einen Weg zurück
zur **Startansicht von „Hilf mit"** — Suchfeld und Karte, ohne gesetzten Pin. Der Knopf gehört
neben „Reicht so" und muss sich davon deutlich unterscheiden; die beiden bedeuten das Gegenteil
voneinander.

**Dazu, und das ist der subtilere Teil:** Setzt der Besucher währenddessen einen Pin auf der Karte,
soll dieser die begonnene Hausnummern-Auswahl **übersteuern**. Heute läuft beides nebeneinander
her — der Pin wandert, das Knopfraster bleibt stehen, und der nächste Tipp auf eine Hausnummer
wirft den eben gesetzten Punkt wieder weg. Ein Tipp auf die Karte ist die bestimmtere Aussage: Dort
hat jemand gerade gezielt.

### Die Dankmeldung: brauchen wir sie, und stimmt sie immer?

**Zuerst die Tatsache, weil die Vermutung eine andere war:** Den Dank gibt es bei **beiden**
Beiträgen. `submitLocation()` und `submitDate()` gehen durch dieselbe Funktion `contribute()`
(`store/contribute.ts:136`), die ihn mit dem jeweiligen Text auslöst — „Danke! Das Foto ist jetzt
auf der Karte." beziehungsweise „… auf der Zeitleiste.". Es ist also **nichts zu vereinheitlichen**;
die Wege sind schon einer.

Warum der Eindruck entstanden ist, ist trotzdem die interessante Spur — und dahinter steckt ein
handfester Fall:

**Beim Datieren eines Fotos ohne Ort ist der Dank eine falsche Zusage.** `rangeForPhoto()` in
`kiosk/fokus.ts:36` gibt für ein Foto ohne Koordinaten `null` zurück, die Ansicht stellt sich also
bewusst *nicht* ein — richtig so, denn ein Foto ohne Ort steht auf keiner Karte. Auf dem Schirm
steht dann aber „Das Foto ist jetzt auf der Zeitleiste", und sichtbar wird nichts. Beim Verorten
fährt die Karte sichtbar heran; beim Datieren springt bestenfalls der Schieber, und in diesem Fall
passiert gar nichts. Das ist dieselbe Sorte Fehler, die beim Verorten schon einmal behoben wurde
(siehe [history.md](history.md), Teil IV, Punkt 4) — nur an der anderen Frage.

Im Museumsbestand ist das **nicht** der Randfall: Ein frisch importierter Scan hat typischerweise
weder Ort noch Jahr, und welche der beiden Fragen zuerst kommt, entscheidet der Zufall.

**Zu klären:**

- **Braucht es die Meldung überhaupt?** Sie steht 2,2 Sekunden und blendet den Beitragsbereich so
  lange aus. Die eigentliche Rückmeldung ist die Ansicht selbst — die Karte fährt hin, das Foto
  taucht auf. Wo das eintritt, ist der Satz vielleicht überflüssig; wo es *nicht* eintritt, ist er
  irreführend. Beides spricht gegen ihn, aus entgegengesetzten Richtungen.
- **Falls sie bleibt: was sagt sie im Fall ohne Ort?** Ehrlich wäre etwa „Danke! Sobald jemand
  weiß, wo das war, erscheint es auf der Karte." — das benennt zugleich, was noch fehlt, und
  könnte den nächsten Beitrag anstoßen.
- **Die 2,2 Sekunden sind zugleich die Fokusdauer.** Zoom und Schieberstellung leben genau so
  lange wie der Dank, ohne zweiten Zeitgeber (`showThanks` in `store/contribute.ts:123`). Wer die
  Meldung streicht, muss diesen Zeitgeber ersetzen, sonst kehrt die Karte nie zurück.

### Historische Karte als umschaltbare Grundkarte

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
(`09de5a5`).*

### Kopfzeile des Zeitschiebers aufräumen

Zurückgestellt, aber gewollt: Die Kopfzeile über dem Schieber soll weg — sowohl „1920 bis 2019"
als auch „x Fotos ohne Jahr".

**Vorher zu klären, zwei Dinge:**

1. Mit der Kopfzeile verschwindet die einzige Stelle, an der der gewählte Zeitraum als **Zahl**
   steht. Bleibt es bei der Skala unter dem Schieber (den beiden Enden der Achse), oder tragen die
   Griffe ihre Jahreszahl mit sich?
2. Ohne Kopfzeile braucht die obere Zeile weniger als die heutigen 9 rem. Schrumpft sie auf etwa
   6,5 rem, gewinnt die Karte die Differenz.

Dazu ein Erbe aus dem Umbau der Zeitachse: Der Satz „Für diesen Ausschnitt gibt es keine datierten
Fotos." steht in dieser Kopfzeile. Fällt sie, muss er woanders hin — oder ganz weg, denn die Karte
sagt mit „Hier gibt es noch keine Fotos im gewählten Zeitraum." ohnehin dasselbe.

### Detailansicht: der Schließen-Knopf soll doch nach oben rechts

Der Umbau vom 2. August (`b20ff5c`) hat den Schließen-Knopf aus der Ecke in die Kopfzeile der
Textspalte geholt. Das steht in der Flucht, aber es liest sich nicht wie ein Schließen-Knopf — die
gewohnte Stelle ist oben rechts, und dort soll er wieder hin.

**Die Ansicht bekommt dafür drei gedachte Zeilen:**

```
┌───────────────────────────────────────────────────────────┐
│                                          [× Schließen]    │  ← Kopfzeile
├───────────────────────────────┬───────────────────────────┤
│                               │  Titel                    │
│         Bild, so groß         │  1943                     │
│         wie es geht           │  Friedhofsweg 30          │  ← Mittelzeile
│                               │  Beschreibung … (scrollt) │
│                               │                           │
├───────────────────────────────┴───────────────────────────┤
│           [Vorheriges]  3 von 8  [Nächstes]               │  ← Fußzeile
└───────────────────────────────────────────────────────────┘
```

- **Kopfzeile:** rechtsbündig der Schließen-Knopf, sonst nichts.
- **Mittelzeile:** links etwa zwei Drittel das Bild, so groß, dass es **oben/unten oder
  rechts/links anstößt** — je nachdem, was zuerst greift. Rechts daneben der Textbereich, oben
  bündig mit der Oberkante des Bildes, weiterhin scrollend.
- **Fußzeile:** die Blätterknöpfe mittig **unter dem Bild** — das bleibt, wie es seit `b20ff5c`
  ist, und gilt weiterhin: nicht mittig im Schirm.

**Vorher zu klären:** Kopf- und Fußzeile brauchen ihre Höhe auch dann, wenn nichts darin steht —
sonst springt das Bild in der Größe, je nachdem ob ein Stapel offen ist oder ein einzelnes Foto.
Feste Höhen sind der einfache Weg; sie kosten das Bild oben und unten je gut drei Zentimeter.

### „Hilf mit:" hat seine Akzentfarbe verloren

Beim Angleichen an „Bilder aus" (`cc5a437`) wurde aus dem Akzentbraun eine stille graue Zeile. Das
war die bewusste Folge einer bewussten Entscheidung — aber es war zugleich der einzige Blickfang
der linken Spalte. Falls der Beitragsbereich seinen Zug aufs Auge zurückbekommen soll, ist das die
Stelle.

### Der 100-m-Fokus liegt über der Kachelauflösung

Nach einem Besucherbeitrag fährt die Karte auf hundert Meter heran; die Vektorkacheln reichen bis
Zoom 15. MapLibre skaliert sauber hoch, die Beschriftungen werden dabei aber groß. Falls das im
Museum unruhig wirkt, ist **der Radius die Stellschraube, nicht die Bauform**.

### Attract-Mode

Diashow bei Leerlauf statt Standardansicht. Heute lädt der Leerlauf nach fünf Minuten die Seite
neu — ein bewegtes Bild würde Besucher eher an das Gerät holen.

---

## Infrastruktur

### Abnahme auf dem ersten Pi

**Der wichtigste offene Punkt des Projekts.** Alles unter `deploy/pi/` ist **ungeprüft** — beim
Bauen gab es kein Gerät. Die Shell-Syntax stimmt, gelaufen ist nichts. Betroffen sind
`setup-pi.sh`, `photomap-kiosk`, `photomap-kiosk.service`, `update.sh`, `99-photomap-usb.rules`
und `photomap-usb-mount`.

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

### Die vier Prüfungen, die das Gerät brauchen

- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Gezogener Netzstecker im Betrieb** — hier zeigt sich, ob
  `--disable-session-crashed-bubble` das tut, wofür es gedacht ist.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen. Kioske
  sterben an einem langsamen Leck im Frontend, nicht am Backend.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.

### Wiederherstellung wirklich proben

Auf ein zweites, leeres Gerät zurückspielen. **Ein ungetestetes Backup ist kein Backup.** Erprobt
ist bisher nur der Weg gegen ein `hdiutil`-Prüfvolumen auf dem Mac.

### Bedienbarkeitstest mit der echten Zielgruppe

Eine ehrenamtliche Person die Sicherung durchführen lassen, **ohne zu helfen**, und zusehen, wo sie
stockt. Der aussagekräftigste Test des ganzen Projekts — und die zweite Hälfte des
Abnahmekriteriums von Stufe 9, die bisher fehlt.

### Containerbetrieb prüfen

`make prod` ist ungeprüft, weil beim Bauen kein Docker lief. Auf dem Pi ist das der einzige
Betriebsmodus.

### Displayauflösung und -orientierung des Museumsgeräts

Steht noch nicht fest und beeinflusst die Layoutmaße. Die Ansicht ist bisher gegen 1280 × 800
nachgemessen; die Variable `--crest` hat für schmale Schirme bereits eine Media Query.

### Read-Only-Overlay-Dateisystem

Gegen SD-Karten-Korruption bei Stromausfall. Der Pi wird im Museum nicht heruntergefahren, sondern
ausgeschaltet — das ist auf Dauer der wahrscheinlichste Ausfallgrund.

---

## Entwicklung

Nicht das Programm, sondern die Arbeit daran: wie das Projekt geordnet, veröffentlicht und
weitergegeben wird.

### Gute Beispieldaten für Entwicklung und Test

Heute gibt es sechs Testbilder in `backend/tests/fixtures/`, und die decken genau die schwierigen
Fälle der Import-Pipeline ab: Scan ohne EXIF, Scan mit Scandatum von 2019, hochkant über
EXIF-Orientierung, CMYK-TIFF, Graustufen, Datei ohne Bild. Sie sind mit
`tests/fixtures/erzeuge_testbilder.py` **synthetisch erzeugt** — für die Pipeline richtig, für
alles andere nutzlos: Man sieht auf ihnen nichts, was auf einer Karte an einer Stelle Sinn ergäbe.

Was fehlt, ist ein **Bestand zum Ansehen**: genug Fotos, an verschiedenen Orten, mit und ohne
Datierung, mit und ohne Ort, damit Karte, Zeitschieber, Cluster, Stapel und der „Hilf mit"-Bereich
in einem realistischen Zustand geprüft werden können. Bisher stammt jeder solche Test aus einer von
Hand befüllten `data/`, die niemand sonst hat.

> **Das README verspricht das schon.** In seiner Kommandotabelle steht `make seed` —
> „Beispielfotos importieren". **Dieses Ziel gibt es im Makefile nicht.** Entweder es entsteht mit
> diesem Punkt, oder die Zeile muss weg.

**Vorher zu klären — und das ist der Knoten:** Welche Fotos? Echte historische Aufnahmen aus Holm
gehören dem Museum und sind nicht ohne Weiteres in einem Repo zu veröffentlichen. Drei Wege:

1. **Weiter synthetisch**, aber ansehnlich: erzeugte Bilder mit erkennbarem Motiv und Beschriftung
   („Beispiel 3 — Mühlenweg, 1930er"). Rechtlich unbedenklich, im Repo tragbar, sieht aber nie aus
   wie ein Museum.
2. **Gemeinfreie historische Fotos** aus Wikimedia Commons oder einem Landesarchiv, auf Holmer
   Koordinaten gelegt. Realistisch, braucht aber je Bild eine Lizenzprüfung und die Namensnennung
   im Repo.
3. **Ein kleiner echter Satz mit Erlaubnis des Museums**, klar als solcher gekennzeichnet und mit
   schriftlicher Freigabe.

Dazu gehört: die vorhandenen Tests auf den neuen Satz ziehen und ihn **committen** — ein
Beispielbestand, den man erst herstellen muss, wird nicht benutzt.

### Versionierung, Releaseprozess und Veröffentlichung des Codes

**Stand:** `development.md` kündigt SemVer-Tags und Conventional Commits an, beides zusammen
versioniert. Tatsächlich gibt es nach 62 Commits **keinen einzigen Tag**; `package.json` und
`pyproject.toml` stehen beide auf `0.1.0`, und `deploy/docker-compose.yml` baut Images mit
`${PHOTOMAP_VERSION:-dev}`. Es fehlt also nicht die Entscheidung, sondern ihre Umsetzung: Was löst
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

**Zwei Dinge sind vor jeder Veröffentlichung zu klären, und eines davon ist ein echter Blocker:**

- **`frontend/public/logo.png` ist das Wappen der Gemeinde Holm.** Ein Gemeindewappen ist kein
  freies Werk, sondern ein hoheitliches Zeichen; seine Verwendung braucht die Erlaubnis der
  Gemeinde, und in einem öffentlichen Repo liegt es für jeden zum Mitnehmen. Der Code ist darauf
  vorbereitet — im Code steht nirgends, was auf dem Bild zu sehen ist —, die Datei müsste also nur
  durch einen Platzhalter ersetzt werden. **Vor der Veröffentlichung zu entscheiden, nicht danach:
  aus der Git-Historie bekommt man sie nur mit einem Rewrite wieder heraus.**
- **Die Historie ist sonst sauber.** Keine `.env`, keine Laufzeitdaten, keine Kartendateien, keine
  echten Fotos — nur `deploy/.env.example` und die sechs synthetischen Testbilder. Das ist vor dem
  Veröffentlichen noch einmal zu prüfen, aber der Ausgangspunkt ist gut.

### Lizenz des Projekts und der verwendeten Komponenten

Noch festzulegen. Zwei getrennte Fragen, die oft verwechselt werden:

- **Unter welcher Lizenz steht Photomap selbst?** Für ein Projekt, das ausdrücklich für ein zweites
  Museum nachnutzbar sein soll, ist das keine Formalie — ohne Lizenz ist Nachnutzung rechtlich
  nicht erlaubt, auch wenn der Code offen daliegt.
- **Was verlangen die verwendeten Komponenten?** Bisher steht im README nur der Satz „Alle
  verwendeten Komponenten sind Open Source" — das ist geglaubt, nicht geprüft. Nachzusehen sind
  mindestens MapLibre GL (BSD-3), PMTiles, `@protomaps/basemaps` samt der mitgelieferten
  **Schriften und Symbole** unter `frontend/public/basemaps/`, die OpenStreetMap-Daten in Kacheln
  und Ortsindex (ODbL — verlangt Namensnennung, die auf der Karte steht) und die
  Python-Abhängigkeiten. Die Kombination entscheidet, welche Lizenz für Photomap überhaupt möglich
  ist.

Gehört anschließend in eine `LICENSE`-Datei und in den Lizenzabschnitt des README.

### Deployment auf einem Webserver evaluieren

Das System dem Museumsteam **zunächst online** anbieten — zur Erprobung und vor allem zum Aufbau
der Fotodatenbank, bevor ein Pi im Ausstellungsraum steht. Die Bilder könnten so über Monate von
zu Hause aus eingepflegt werden.

Technisch ist der Weg kurz: Es läuft schon in Containern (`make prod`), das Frontend ist statisch,
nginx steht davor, und die Datenbank ist eine Datei. Die Fragen liegen woanders:

- **Zugriffsschutz.** Die PIN ist für einen Touchscreen in einem Museumsraum gebaut — vier Ziffern,
  gesichert durch eine Sperre nach fünf Fehlversuchen. Im offenen Netz ist das zu wenig, und vor
  allem schützt sie nur die Verwaltung: Der „Hilf mit"-Bereich nimmt **Beiträge ohne jede
  Anmeldung** an. Online wäre das eine offene Tür. Naheliegend ist ein Schutz **vor** der ganzen
  Anwendung (HTTP-Basisauthentifizierung im nginx oder ein Zugang über VPN), nicht ein zweiter
  Schutz in der Anwendung.
- **Was aus dem Offline-Versprechen wird.** Die Regel „null Anfragen an eine fremde Herkunft" bleibt
  erfüllt, sie kostet online nur nichts mehr. Umgekehrt gilt: Kartendatei und Ortsindex sind auf
  einen Rechner im Ausstellungsraum zugeschnitten — 4,6 MB Kacheln und 1,5 MB Ortsindex über eine
  langsame Leitung sind spürbar, aber tragbar.
- **Wie die Daten zurück auf den Pi kommen.** Das ist der eigentliche Zweck, und dafür gibt es das
  Werkzeug bereits: Sicherung und Wiederherstellung. Zu prüfen ist, ob der Weg auch als
  Übertragungsweg taugt — dann wäre der Umzug vom Webserver ins Museum ein bekannter Vorgang und
  kein Sonderfall.

### `architecture.md` anlegen

Es gibt keine Stelle, an der jemand nachlesen kann, **aus welchen Teilen das System besteht und wie
sie zusammenspielen**. Wer heute einsteigt, muss sich das aus vier Dateien zusammensuchen.

Beschreiben: die Bausteine (Backend, Frontend, Kacheln und Ortsindex, Container, Kiosk-Schicht auf
dem Pi), ihre jeweilige Aufgabe, und die Wege dazwischen — welche Daten wann wohin fließen, was
zur Bauzeit entsteht und was zur Laufzeit, was auf dem Entwicklungsrechner läuft und was auf dem
Gerät.

**Die Abgrenzung ist der eigentliche Teil der Arbeit**, sonst entsteht eine vierte Datei, die
dasselbe noch einmal sagt:

| Datei | beantwortet |
|---|---|
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? |
| [development.md](development.md) | *Wie* arbeitet man daran? (Einrichtung, Tests, Konventionen) |
| **architecture.md** | *Was* gibt es, und wie greift es ineinander? |
| [history.md](history.md) | *Wie* ist es dazu gekommen? |

Konkret heißt das: Der Abschnitt „Aufbau" in `development.md` ist eine Ordnerliste und bleibt eine;
`architecture.md` erklärt stattdessen die Zusammenhänge und verweist für Begründungen nach
`decisions.md`, statt sie zu wiederholen.

### Backlog ordnen und klassifizieren

Diese Datei wächst. Sie mischt inzwischen Fehler, konkrete Aufgaben, Entscheidungsfragen und Ideen
in einer Gliederung, die nur nach Bereich sortiert. Was fehlt:

- **Trennung nach Art:** Fehler, Aufgabe, offene Frage, Idee. Fehler stehen heute nur durch eine
  Namenskonvention („Fehler: …") vorn.
- **Einordnung nach Dringlichkeit und Wichtigkeit** — die beiden sind nicht dasselbe, und gerade
  hier fällt es auf: Der Straßenfehler ist wichtig *und* dringend (er trifft Besucher heute), die
  historische Karte ist wichtig und gar nicht dringend, die Akzentfarbe von „Hilf mit:" ist beides
  nicht.
- **Stabile Kennungen**, damit ein Punkt referenzierbar wird — in einem Commit, in einer
  Besprechung, in einem Auftrag an einen Coding-Agent. Heute geht das nur über die Überschrift, und
  die ändert sich.

**Das ist ausdrücklich die Vorstufe zu einem Ticketsystem**, nicht sein Ersatz. Solange alles in
einer Datei steht, liest es sich am Stück und überlebt einen Kontextverlust — genau der Grund,
warum die Pläne früher so geführt wurden. Der Umzug lohnt, sobald mehr als eine Person daran
arbeitet oder die Reihenfolge häufiger wechselt als die Inhalte.

### Sprach- und Namenskonsistenz prüfen

Die Sprachregelung in [CLAUDE.md](../CLAUDE.md) ist klar, die Umsetzung ist es nicht. **Der
deutlichste Fall sind die Dateinamen**, für die Englisch vorgeschrieben ist — tatsächlich stehen
sie fast genau halbe-halbe:

| | |
|---|---|
| deutsch | `fokus.ts`, `hausnummern.ts`, `jahrzehnte.ts`, `stapel.ts`, `zeitachse.ts`, `jahr.ts` (samt Tests), `tests/fixtures/erzeuge_testbilder.py` |
| englisch | `idle.ts`, `mapStyle.ts`, `filename.ts`, `format.ts`, `paging.ts`, `scrollArea.tsx`, `useLoaded.ts` |

Beide Gruppen sind Module derselben Art — kleine reine Fachlogik neben den Komponenten. Es gibt
also keine Regel dahinter, nur die Reihenfolge ihrer Entstehung. Zu entscheiden ist, ob die Regel
gilt (dann sechs Umbenennungen) oder ob Fachlogik-Module die Ausnahme sind wie die Testnamen (dann
gehört das in die Regel geschrieben).

**Dasselbe für Kommentare.** Sie sollen englisch sein; in den jüngeren Dateien sind viele deutsch,
und teils stehen beide Sprachen in einer Datei nebeneinander. Auch hier: entweder nachziehen oder
die Regel ändern — aber nicht offenlassen, denn genau daran orientiert sich, wer als Nächstes etwas
hinzufügt.

**Dazu die Sinnfrage.** Nicht nur die Sprache eines Dateinamens ist zu prüfen, sondern ob er sagt,
was drinsteht: `jahr.ts` enthält die Jahrzehnt-Regel des Verwaltungsbereichs, `format.ts` formatiert
Tagesangaben, `paging.ts` heißt so, weil `pager.ts` auf macOS mit `Pager.tsx` kollidierte. Solche
Namen kosten jedes Mal einen Blick in die Datei.

**Commit-Nachrichten** sind deutsch und ohne Umlaute — das ist bisher durchgehalten; ein Durchgang
über `git log` sollte es bestätigen statt es anzunehmen.
