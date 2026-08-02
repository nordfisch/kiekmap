# Offene Punkte

Was noch aussteht, nach **Verwaltung · Besucher-Interface · Infrastruktur**. Was schon gebaut ist,
steht in [history.md](history.md).

Jeder Eintrag trägt mit, was beim Aufgreifen sonst erst wieder herausgefunden werden müsste. Das
ist der Grund, warum er hier steht und nicht in einer Stichwortliste: Ein Punkt ohne seinen
Zusammenhang kostet beim zweiten Anlauf dieselbe Arbeit wie beim ersten.

Nichts hiervon ist terminiert. Innerhalb der Abschnitte stehen **Fehler zuerst**, danach der
Ausbau grob nach Gewicht. Ein Eintrag ist ein Fehler und kein Wunsch:
[Gleichnamige Straßen werden zu einer
verschmolzen](#fehler-gleichnamige-straßen-werden-zu-einer-verschmolzen) — er begegnet Besuchern
heute im Museum.

---

## Verwaltung

### Fotos löschen

Bisher gibt es nur „Verstecken". Das ist richtig für ein Foto, das man nicht zeigen will — aber
nicht für einen Fehlscan, eine doppelt eingelesene Datei oder ein Bild, das gar nicht ins Museum
gehört. Die bleiben auf ewig im Bestand und werden bei jeder Sicherung mitgeschleppt.

**Wo.** Auf jeden Fall in der Einzelbearbeitungsmaske. Für die Fotoliste wäre ein Mehrfachlöschen
naheliegend — das braucht dort aber erst eine Mehrfachauswahl, die es heute nicht gibt, und ist
deshalb der zweite Schritt, nicht der erste.

**Wie: Papierkorb, nicht endgültig.** Die Datenbankzeile verschwindet aus allen Listen, die
Bilddatei wandert nach `data/geloescht/<Datum>/`. Dasselbe Muster, mit dem das Zurückspielen einer
Sicherung den bisherigen Stand nach `data/vorher-<Datum>/` legt: Der Fehlgriff einer ehrenamtlichen
Person, die zweimal im Jahr hier ist, darf nicht unwiderruflich sein.

> **Das widerspricht einer festgehaltenen Zusage.** `backend/app/api/admin.py` beginnt heute mit
> *„Nothing is deleted. A photo can be hidden, a visitor contribution taken back — both are
> reversible, and neither loses the file."* Der Papierkorb hält den zweiten Halbsatz ein, den
> ersten nicht mehr. Der Docstring und der entsprechende Absatz in [decisions.md](decisions.md)
> sind beim Umsetzen mitzuziehen — nicht stillschweigend zu übergehen.

**Vorher zu klären:**

- **Kommt ein gelöschtes Foto beim nächsten Import zurück?** Der überwachte Eingangsordner und der
  Stick-Import erkennen Dubletten am SHA-256 des Inhalts. Ist die Zeile weg, ist es keine Dublette
  mehr — dieselbe Datei würde wieder aufgenommen. Es braucht also entweder eine Sperrliste
  gelöschter Hashes oder die bewusste Entscheidung, dass ein erneut angebotenes Bild erneut
  hereinkommt.
- **Was wird aus Änderungsprotokoll und Import-Protokoll?** Beide verweisen auf `photo_id`.
  Mitlöschen verliert die Spur, Stehenlassen erzeugt Einträge, die ins Leere zeigen.
- **Zählt der Papierkorb in die Sicherung?** Eher nicht — sonst wächst der Stick mit dem, was
  jemand gerade loswerden wollte.

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

### Fehler: gleichnamige Straßen werden zu einer verschmolzen

**Der einzige bekannte Fehler auf dieser Seite.** Wer bei der Verortung „Hauptstraße" eingibt und
den Vorschlag übernimmt, bekommt einen Punkt weit ausserhalb des erwarteten Bereichs.

**An den Daten nachgemessen** (`data/places.json`, Stand 29. Juli 2026):

| | |
|---|---|
| Adressen namens „Hauptstraße" im Index | **153** |
| davon räumlich getrennte Straßen | **17**, in verschiedenen Dörfern |
| Einträge der Art `strasse` dafür | **1** |
| dessen Punkt | 53,64050 / 9,66954 |
| Entfernung zur **nächstgelegenen** echten Hauptstraße | **490 m** — er liegt auf keiner |
| Entfernung zu Holms Ortsmitte | **2,26 km** |
| Holms eigene Hauptstraße läge bei | 53,6205 / 9,6727 — 200 m von der Mitte |

**Zwei Ursachen, beide in `tiles/build-places.py`:**

1. **Gleiche Namen werden zu einem Punkt verrechnet.** Die Segmente werden nach `(name, kind)`
   gruppiert, und aus ihren Mittelpunkten wird der **Durchschnitt** gebildet. Die Bounding Box der
   Region reicht über Holm hinaus — das war schon der Grund für die 7686 Adressen —, es liegen also
   siebzehn Hauptstraßen darin. Der Durchschnitt landet zwischen ihnen, auf keiner einzigen.
2. **`out center` liefert die Mitte des Rechtecks, nicht einen Punkt auf der Straße.** Overpass
   gibt zu jedem Weg den Mittelpunkt seiner Bounding Box zurück. Bei einer kurzen, geraden Straße
   fällt das kaum auf; bei einer gebogenen oder L-förmigen liegt der Punkt neben der Fahrbahn.

**Der zweite Schritt rettet es nicht — er erbt denselben Fehler.** `places.housenumbers()` sucht
die Nummern über `Place.street == street.name`, also über den **Namen**. Wer „Hauptstraße" antippt,
bekommt deshalb alle **153** Hausnummern aus siebzehn Dörfern angeboten, jede Nummer mehrfach. Die
Auswahl ist dann ein Münzwurf, und das neue Abschnittsraster („1–13", „15–24") sortiert Nummern
nebeneinander, die kilometerweit auseinanderliegen.

**Derselbe Mechanismus trifft ausgedehnte Naturobjekte.** Die „Elbe" liegt im Index bei
53,68963 / 9,50909 — ausserhalb der Bounding Box. Ein Beitrag dorthin würde vom Backend mit
„Dieser Ort liegt ausserhalb der Karte." abgewiesen (`app/api/contribute.py:142`).

**Gewünschtes Verhalten:** Bei mehreren gleichnamigen Straßen wird die des Museumsortes genommen.
Der vorgeschlagene Punkt liegt auf dem **Straßenverlauf selbst**, in der Mitte der Strecke — nicht
in der Mitte des umschließenden Vierecks. Und die Hausnummern gehören zu *dieser* Straße, nicht zu
allen gleichnamigen.

**Vorher zu klären:**

- **Woran wird „die aus Holm" erkannt?** Der Ortsname steht in `region.json`, es darf also nichts
  Ortsspezifisches in den Code. Drei Wege, in absteigender Verlässlichkeit: über die Grenzrelation
  des Ortes (`admin_level`), über `addr:city`/`is_in` an den Segmenten (nicht überall gepflegt),
  oder rein geometrisch über die Nähe zu `region.center`. Wahrscheinlich braucht es eine Kette aus
  zweien davon.
- **Oder werden gleichnamige Straßen gar nicht zusammengeworfen?** Die Alternative wäre, jede der
  siebzehn als eigenen Eintrag zu führen und in der Trefferliste zu unterscheiden. Für ein Museum,
  dessen Fotos aus einem Dorf stammen, ist das vermutlich zu viel Auswahl — aber es ist die
  ehrlichere Datenhaltung, und die Entscheidung gehört vor den Code.
- **Die Hausnummern brauchen eine Zuordnung zur Straße, die nicht der Name ist.** Heute gibt es
  keine, deshalb der Namensvergleich. Naheliegend: beim Bauen des Index jede Adresse dem
  nächstgelegenen gleichnamigen Segment zuordnen und die Beziehung mitschreiben.

**Was der Umbau kostet:** Für einen Punkt auf der Strecke reicht `out center` nicht, es braucht
`out geom` — die vollständige Geometrie aller Wege. Das vergrößert die Overpass-Antwort deutlich.
`places.json` muss dadurch nicht wachsen: Gespeichert wird weiterhin nur der ausgerechnete Punkt.

**Nach dem Umbau:** `make places` neu laufen lassen und den Index mit `python -m app.cli places`
einlesen — auf dem Pi über `update.sh`. **Fotos, die vorher auf einen falschen Punkt verortet
wurden, bleiben dort.** Sie sind an ihrem `place_name` erkennbar und über die Fotoliste zu
korrigieren; wie viele es sind, ist vor dem Umbau zu zählen.

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

### Lizenz des Projekts

Noch festzulegen. Alle verwendeten Komponenten sind Open Source.
