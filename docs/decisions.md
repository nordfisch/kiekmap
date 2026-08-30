# Entscheidungen

Warum die Dinge so sind, wie sie sind. Jeder Punkt nennt die **Entscheidung**, ihren **Grund** und
ihre **Folge**. Wie es dazu kam, steht in [history.md](history.md); was das Programm kann, im
[CHANGELOG](../CHANGELOG.md).

Neue Einträge unten anhängen, alte nicht löschen. Überholte bekommen den Vermerk
*Überholt durch …*; zusammengelegte behalten ihre Nummer als Verweis, damit ein Zitat aus einer
alten Notiz weiter auflöst.

---

## 1. Historische Fotos sind Scans — das prägt das ganze Datenmodell

Die Fotos eines Heimatmuseums sind eingescannte Papierabzüge. Ihr EXIF trägt das Datum des Scans,
nicht der Aufnahme, und praktisch nie GPS. Der EXIF-Import ist der Bonusfall, nicht der Normalfall;
die eigentlichen Daten entstehen durch Kuratoren und Besucher.

Drei Folgen tragen das ganze Datenmodell:

1. **Jedes Feld trägt seine Herkunft** (`exif` / `curator` / `visitor`). Ein aus EXIF geratenes
   Datum darf eine kuratierte Angabe nie überschreiben.
2. **Datumsangaben sind Intervalle.** „um 1930", „1920er", „vor dem Krieg" sind die Realität. Jedes
   Foto speichert `date_from`/`date_to` plus eine Genauigkeit (`day|month|year|decade|unknown`),
   und der Zeitfilter fragt auf **Überlappung** ab. Bei der naheliegenden Abfrage verschwinden genau
   die unscharf datierten Fotos, und zwar ohne Fehlermeldung. Dafür gibt es einen eigenen Test.
3. **Der Beitragsbereich ist der Hauptweg**, auf dem das System an Orte und Daten kommt, und keine
   Nebensache.

---

## 2. Bilder im Dateisystem, Metadaten in SQLite

Originale und Vorschaubilder liegen als Dateien unter `data/`, alles andere in einer SQLite-Datei
daneben.

**Warum nicht Bilder in die Datenbank:** Vorschaubilder sollen billig ausgeliefert werden, die
Datenbankdatei soll klein und schnell zu sichern bleiben, und im Notfall muss ein Kurator mit einem
gewöhnlichen Dateimanager an die Originale kommen. Eine Datenbank voller Bilddaten erfüllt keinen
dieser Punkte.

**Warum SQLite und nicht Postgres:** ein Gerät, ein Prozess, einige tausend Datensätze, und Sichern
soll „eine Datei kopieren" heißen.

---

## 3. Dateinamen sind der SHA-256 des Bildinhalts

```
data/photos/a3/f2/a3f29c…e81b.jpg
data/thumbs/240/a3/f2/a3f29c…e81b.webp
```

Vier Eigenschaften folgen daraus:

1. **Keine Namenskollisionen.** Zwei `Kirche.jpg` aus verschiedenen Quellen stören sich nicht.
2. **Dublettenerkennung.** Der Hash ist `UNIQUE`; ein zweiter Import wird abgewiesen und
   protokolliert.
3. **Beliebig cachebar.** Gleicher Name heißt garantiert gleicher Inhalt, also `immutable`-Header.
4. **Inkrementelle Sicherung.** Liegt der Name schon auf dem Stick, ist es dasselbe Bild. Die zweite
   Sicherung dauert damit Sekunden statt Minuten, und eine Sicherung, die schnell geht, wird auch
   gemacht.

Der ursprüngliche Dateiname bleibt als `original_filename`; er ist oft die einzige inhaltliche
Information, die mitkommt (`Kirchweih_1932_Muehle.jpg`). Die zweistufige Verzeichnisaufteilung
(`a3/f2/`) hält die Ordner klein.

**Was der SHA-256 nicht kann:** inhaltlich gleiche, aber anders zugeschnittene Scans erkennen. Dafür
gibt es den Differenzhash aus
[Punkt 54](#54-dubletten-findet-die-maschine-entscheiden-muss-ein-mensch).

---

## 4. Offline-Karte: PMTiles und MapLibre GL

Eine einzige `map.pmtiles` mit Vektorkacheln der Region, gebaut aus dem Protomaps-Tagesbuild,
angezeigt von MapLibre GL JS.

**Kein Tileserver nötig:** PMTiles ist ein Format, aus dem der Browser einzelne Kacheln per
HTTP-Range-Request liest. Das kann nginx für eine statische Datei von Haus aus. Damit entfällt eine
ganze Komponente aus dem Betrieb.

**Vektor statt Raster:** scharf über die gebaute Zoomstufe hinaus, deutlich kleiner, Farben und
Beschriftungen im Stil anpassbar statt eingebrannt. Preis ist WebGL — auf Pi 4/5 unproblematisch,
auf einem Pi 3 wäre Raster die bessere Wahl.

**Schriften und Symbole liegen lokal.** Der Protomaps-Stil verweist dafür auf `protomaps.github.io`.
Ohne den Eingriff kämen die Kacheln offline und die Beschriftung gar nicht, und das fällt erst auf,
wenn das Gerät ohne Netz im Museum steht. `make tiles` lädt beides nach
`frontend/public/basemaps/`. Geprüft wird gezählt, nicht durch Hinsehen: Die Seite darf **null**
Anfragen an eine fremde Herkunft absetzen.

**Ortssuche ohne Internet:** Aus demselben Extrakt entsteht eine `places.json`, die beim Start in
die `places`-Tabelle geht. Das ersetzt Nominatim für den einen Zweck, den wir haben.

Die `.pmtiles`-Datei gehört nicht ins Repo. Versioniert werden das Bauskript und die Bounding Box in
`tiles/region.json`.

---

## 5. Besucherbeiträge werden direkt übernommen — mit vollständigem Protokoll

Was ein Besucher angibt, steht sofort in den Metadaten und erscheint sofort auf der Karte. Jede
Änderung wird in `changes` protokolliert und ist einzeln zurücknehmbar.

**Warum keine Moderationsqueue:** Der Reiz für den Besucher ist der unmittelbare Effekt. Eine
Warteschlange nimmt ihn weg und erzeugt Arbeit für Ehrenamtliche, die ohnehin knapp ist.

**„Sofort auf der Karte" heißt auch: sofort zu sehen.** Ein Beitrag stößt ein Nachladen an, Marker
und Histogramm zusammen; die Zeitraumauswahl des Besuchers bleibt unangetastet. Ohne das wäre der
Beitrag erst nach dem Verschieben der Karte sichtbar, und ältere Besucher verschieben sie nicht.

Drei Regeln fangen den Missbrauchsfall auf, ohne den Normalfall auszubremsen:

1. **Nur leere Felder dürfen gefüllt werden**, sonst HTTP 409. Was ein Kurator gesetzt hat, ist
   unantastbar, und der zweite Besucher kann den ersten nicht überschreiben.
2. **Koordinaten müssen in der Region liegen.** Der Pin lässt sich nur auf der Karte setzen, aber
   die API ist erreichbar; ein Foto im Pazifik wäre aus der Ansicht verschwunden, ohne dass jemand
   merkt, warum.
3. **Jede Änderung steht in `changes`** mit einer Sitzungskennung — einer Zufallszahl pro
   Seitenaufruf, nirgends gespeichert. Der Kurator sieht damit, ob mehrere Angaben von einer Person
   stammen; mehr soll er nicht können.

**Jahrzehnt vor Jahr.** Die Datumseingabe fragt erst das Jahrzehnt, dann optional das Jahr. Wer ein
altes Foto sieht, weiß meist „die Zwanziger", nicht „1924". „Ganze 1920er" ist deshalb ein
vollwertiges Ergebnis und kein Ausweichen.

---

## 6. Betrieb: Pi OS Lite, cage, Chromium — Anwendung in Docker

Raspberry Pi OS **Lite** ohne Desktop, dazu `cage`: ein Wayland-Compositor, dessen einzige Aufgabe
es ist, ein Programm im Vollbild anzuzeigen.

**Warum kein Desktop:** Dort sind Bildschirmschoner, Energiesparen, Update-Hinweise und
Autostart-Eigenheiten einzeln zu zähmen, und beim Booten wird der Hintergrund sichtbar. Unter cage
kann nichts in den Vordergrund kommen. Das Gerät bootet in rund 20 Sekunden direkt in die Karte.

**Warum die Anwendung trotzdem in Docker:** Reproduzierbarkeit und ein Update-Weg, der offline
funktioniert — `docker save`-Tarball auf einen Stick, `update.sh`, fertig. Versionen sind über
Image-Tags nachvollziehbar statt über den Zustand eines gewachsenen Systems.

**Der Kiosk-Dienst wartet auf `/api/health`**, bevor Chromium startet. Sonst zeigt das Gerät morgens
für ein paar Sekunden eine Fehlerseite.

---

## 7. Der Zugang zur Verwaltung ist sichtbar, die PIN schützt ihn

Ein Zahlenfeld mit großen Tasten, danach die Verwaltung mit ablaufender Sitzung. **Wo der Zugang
sitzt, sagt [Punkt 26](#26-zwei-wege-in-die-verwaltung-und-keiner-davon-ist-mehr-das-wappen);**
alles hier gilt unverändert für jeden davon.

**Warum sichtbar statt versteckt.** Eine unsichtbare Geste vergessen genau die Ehrenamtlichen, die
zweimal im Jahr hineinmüssen. Und sie schützt nichts: Das Schutzmittel ist die PIN. Wer aus Neugier
tippt, sieht ein Zahlenfeld und geht zurück.

**Warum PIN statt Passwort.** Die Eingabe erfolgt mit dem Finger auf einem Touchscreen, oft von
älteren Menschen. Ein Zahlenfeld mit großen Tasten ist dafür besser als eine Bildschirmtastatur.

**Was eine vierstellige PIN trägt, ist die Sperre, nicht die Länge.** Zehntausend Möglichkeiten
probiert ein Skript in Sekunden durch. Nach fünf Fehlversuchen sperrt das Gerät eine Minute; das
streckt denselben Angriff auf gut zwei Jahre. Der Hash ist PBKDF2 mit 200 000 Runden.

**Sitzungen liegen im Arbeitsspeicher, nicht in der Datenbank.** Ein Neustart beendet damit jede
Sitzung — auf einem Gerät, das jeden Morgen bootet, die billigste Garantie, dass keine Anmeldung die
Nacht übersteht. Gezählt wird in verbleibenden Sekunden statt in Zeitpunkten: Der Pi hat keine
Echtzeituhr und kein Netz, seine Wanduhr kann nach einem Stromausfall um Jahre danebenliegen.

---

## 9. Bearbeiten: fehlendes Feld heißt „lassen", leeres Feld heißt „löschen"

Der Metadateneditor unterscheidet ein Feld, das gar nicht mitgeschickt wird, von einem, das
ausdrücklich leer ist. Ersteres bleibt unverändert, letzteres wird gelöscht. Im Backend trägt das
`model_fields_set` von Pydantic.

**Warum.** Ohne diesen Unterschied ließe sich eine falsche Datierung nur ersetzen, nie
herausnehmen. Genau das ist aber der häufige Fall: Jemand merkt, dass eine Jahreszahl nicht stimmen
kann, weiß aber nicht, was stimmt. Kann er die Angabe herausnehmen, gilt das Foto wieder als
undatiert und landet im Beitragsbereich. Das ist der Unterschied zwischen einer Datenbank, die sich
selbst korrigiert, und einer, in der sich Fehler festsetzen.

**Zurücknehmen eines Besucherbeitrags** löscht das Feld, statt einen alten Wert wiederherzustellen —
ein Besucher darf ohnehin nur füllen, was leer war
([Punkt 5](#5-besucherbeiträge-werden-direkt-übernommen--mit-vollständigem-protokoll)). Hat
inzwischen jemand aus dem Team das Feld bearbeitet, wird das Zurücknehmen verweigert: Es würde diese
Arbeit mit wegwerfen.

---

## 10. Hochgeladene Fotos sind sofort in der Datenbank

Der Stapel-Upload speichert jedes Bild beim Hochladen. Die Tabelle danach ist eine Nacharbeitsliste,
keine Warteschlange; „Übernehmen" ergänzt nur noch Titel, Jahr und Ort.

**Warum.** Sonst kostet ein geschlossener Browser den ganzen Stapel — und der Moment, in dem jemand
zum ersten Mal vierzig Bilder hochlädt, ist der, in dem etwas dazwischenkommt. Was liegen bleibt,
ist nicht verloren, sondern unvollständig, und taucht damit von selbst im Beitragsbereich auf.

Die Stapelangaben füllen nur, was leer ist; bringt eine Datei ein brauchbares Datum oder GPS mit,
gewinnt die Datei. Hochgeladen wird **eine Datei je Anfrage**, obwohl der Endpunkt eine Liste nimmt:
Nur so lässt sich ein Fortschritt anzeigen.

---

## 11. Sicherung ist eine Funktion, kein Skript

Sichern und Wiederherstellen sind Bildschirme in der Verwaltung mit Fortschrittsbalken und Klartext,
nicht `backup.sh`.

**Warum.** Die Zielgruppe sind ältere Ehrenamtliche, die das ein- bis zweimal im Jahr tun. Ein
Shell-Skript bedeutet in der Praxis: es wird nie ausgeführt.

- **Ordner statt ZIP** auf dem Stick. Eine abgebrochene Sicherung ist dann teilweise brauchbar statt
  wertlos, und sie lässt sich an jedem Rechner öffnen.
- **`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Betrieb anzuhalten.
- **Wiederherstellen** packt daneben aus und schaltet erst am Ende um; der bisherige Stand wird
  beiseitegelegt. Eine abgebrochene Wiederherstellung darf den laufenden Bestand nie zerstören.
- **Erinnerung statt Automatik**, ab 30 Tagen rot. Es passiert nichts ungefragt, aber es wird auch
  nicht über Jahre vergessen.

**Ein ZIP-Download ist der zweite Weg, nicht der Ersatz.** Er hilft dort, wo kein Stick liegt. Die
Gründe gegen ZIP gelten unverändert, und deshalb nennt die Oberfläche sie: Das Archiv ist nicht
inkrementell, und ein abgebrochener Download ist wertlos.

**Was den zweiten Weg trägt, ist eine Eigenschaft, die ihn an den ersten bindet:** Das Archiv ist
genau der Ordner, den auch der Stick bekommt, nur gezippt. Zurückspielen heißt deshalb: auf einen
Stick entpacken und die vorhandene Wiederherstellung benutzen. Es gibt keinen zweiten
Wiederherstellungsweg mit eigenen Fehlern, und `test_entpacktes_archiv_laesst_sich_wiederherstellen`
hält die Eigenschaft fest.

Zwei Bedingungen hängen daran:

- **Das Archiv entsteht im Strom, unkomprimiert.** Auf einem Pi mit 2 GB RAM darf es nirgends
  vollständig liegen, und die SD-Karte ist genau das, wovor die Sicherung schützt. `ZIP_STORED` ist
  dabei nicht Sparsamkeit: JPEG und WebP sind komprimiert, ein zweiter Durchgang kostet nur
  Rechenzeit.
- **`proxy_buffering off` im nginx.** Mit der Voreinstellung sammelt nginx die ganze Antwort erst
  auf der Platte — bei mehreren Gigabyte auf ebenjener SD-Karte.

**Der Rückweg läuft über den Eingangsordner, aber er fragt nach.** Eine dort abgelegte ZIP-Sicherung
spielt sich nicht von selbst ein; sie wird erkannt und im Sicherungsbereich vorgelegt. Der Grund ist
eine Eigenschaft des Ordners: Er tut sonst nur etwas **Hinzufügendes und Folgenloses**. Eine
Wiederherstellung **ersetzt den ganzen Bestand**. Beides ohne Rückfrage zu mischen hieße: Eine
versehentlich dorthin kopierte Datei tauscht die Sammlung aus, und auf einem Kiosk fällt das
wochenlang niemandem auf.

Der Download authentisiert sich über ein **Einmal-Ticket**, weil ein Browser-Download keinen
`X-Admin-Token` mitschicken kann. Den Sitzungstoken in die Adresse zu hängen wäre falsch: Adressen
landen im Verlauf, in Lesezeichen und in Proxy-Protokollen, und dieser Token öffnet den ganzen
Verwaltungsbereich.

---

## 12. Die Karte ist Hintergrund, nicht Hauptsache

Ein eigener Farbstil „Papier" in den Tönen der Oberfläche statt eines der mitgelieferten, dazu drei
Ebenen weniger und Straßen auf 80 % ihrer Breite
([`kiosk/mapStyle.ts`](../frontend/src/kiosk/mapStyle.ts)).

**Warum.** Die fertigen Stile sind für Navigation gebaut: türkises Wasser, kräftiges Grün, kühles
Grau. Die Regel beim Aussuchen war: **nichts auf der Karte darf so gesättigt sein wie ein Foto.**

**Was weggelassen wird**, und was ausdrücklich nicht: `pois`, `address_label` und `roads_shields`
fallen weg. Die Straßennamen bleiben — **auch die kleinen**: Der Beitragsbereich verweist auf sie,
und in einem Dorf sind die meisten Straßen klein.

**Skaliert werden die Stützstellen, nicht die Kurve.** Die Breiten sind Zoom-Interpolationen; sie in
`["*", breite, 0.8]` einzupacken lehnt MapLibre ab. So wandern spätere Änderungen des Stils weiter
mit, statt in einer handgepflegten Kopie fremder Kartografie zu enden.

---

## 13. Verortung in Schritten: Straße, dann Abschnitt, dann Hausnummer

*Fasst [Punkt 24](#24-die-straße-wird-gewählt-nicht-getippt) mit auf.*

Die Ortsauswahl liefert Straßen, dann Hausnummern als Knopfraster, darunter „Reicht so — die Straße
genügt". In der freien Suche der Verwaltung tauchen Adressen nur auf, wenn die Eingabe eine
**Ziffer** enthält.

**Warum keine flache Liste.** Eine Trefferliste wäre nach den Hausnummern einer einzigen Straße voll
und hätte jede andere Straße verdrängt.

**Warum Schritte gut sind, nicht nur erträglich.** Es ist dieselbe Form wie bei der Datierung
(Jahrzehnt, dann Jahr), und aus demselben Grund: Der zweite Schritt ist **überspringbar**. Nicht
jedes Haus steht in OpenStreetMap, und niemand weiß bei jedem Foto die Hausnummer. Der Pin sitzt
schon nach dem ersten Schritt auf der Straße; wer dort aufhört, hat geantwortet.

**Lange Straßen bekommen einen dritten Schritt.** Zwei Kürzungen, in dieser Reihenfolge:

- *Die Grundzahl vertritt ihre Buchstabenzusätze.* Räumlich fügen sie nichts hinzu — 3a und 3c
  liegen wenige Meter auseinander, die Genauigkeit steht ohnehin bei 15 m. Auf dem Knopf steht immer
  eine Adresse, die es wirklich gibt.
- *Bleiben es zu viele, kommt ein Abschnitt davor* — „1–13", „15–24". Geschnitten wird **nach
  Anzahl, nicht nach Zahlenwert**: Straßen sind löchrig nummeriert, und gleich große Abschnitte sind
  besser als verschieden volle. Der Preis ist eine gelegentlich ungewohnte Beschriftung wie
  „37–183"; sie benennt die Lücke, statt sie zu verschweigen.

Bei einer durchschnittlichen Dorfstraße bleibt es bei dem einen Schritt.

**Auch die Straße wird gewählt, nicht getippt** — erst der Anfangsbuchstabe, dann die Straße. Damit
hat die Besucheransicht **kein einziges Eingabefeld mehr** und braucht keine Tastatur. Eine echte
Tastatur im Ausstellungsraum kommt weg und öffnet Tastenwege in Chromium, die der Kiosk gerade
zumacht; eine Bildschirmtastatur hätte gebaut werden müssen. Beides wäre Aufwand für ein
Bedienelement, das ohne Tastatur wie defekt aussieht. Die Verwaltung behält ihr Suchfeld — dort wird
gepflegt, nicht besucht.

**Die Buchstabengruppen werden gerechnet, nicht aufgeschrieben.** Ein Buchstabe mit wenigen Straßen
wird mit dem Nachbarn verschmolzen, bis höchstens zehn Knöpfe bleiben; eine Gruppe mit mehr als zehn
Straßen teilt sich eine Ebene tiefer, und der Schnitt folgt den Namen statt einer festen Tiefe. Ein
zweites Museum bekommt damit seinen eigenen Baum. Gruppiert wird über den **entschärften** Namen —
sonst bekäme ein „Ölmühlenweg" einen einsamen Ö-Knopf hinter dem Z.

**Zur Wahl stehen nicht alle Straßen, sondern die `streetChoice` ortsnächsten.** Der Ortsindex
reicht über die Nachbardörfer hinaus; sie alle in Knöpfe zu fassen kostete eine vierte Frage. Die
Fotos eines Heimatmuseums zeigen seinen eigenen Ort, und was weiter draussen liegt, wird auf der
Karte angetippt. Eine **Anzahl** statt eines Radius, weil sie das Knopfbudget unabhängig davon hält,
wie dicht ein Ort bebaut ist. Fehlt der Schlüssel in `tiles/region.json`, gilt 80.

**Die Genauigkeit wird dabei benutzt.** Eine Straße bekommt 150 m, eine Hausnummer 15 m. Ein von
Hand auf die Karte getippter Punkt bekommt **keine** Angabe — wie gut jemand gezielt hat, ist nicht
unsere Behauptung. Wer den Pin verschiebt, verliert Name und Genauigkeit wieder, aus demselben
Grund.

**Hausnummern werden natürlich sortiert**, nach (führender Zahl, Rest): 1, 1a, 2, 9, 10 statt 1, 10,
12, 1a, 2, 9.

---

## 14. Die Zeitachse gehört dem Bestand, nicht dem Kartenausschnitt

Der Zeitschieber spannt immer über die Spanne der **ganzen Sammlung** und steht still. Die Balken
darunter zeigen, was im sichtbaren Ausschnitt liegt.

**Warum nicht mitskalieren.** Eine Achse, die sich beim Zoomen neu skaliert, ändert unter der Hand,
was dieselbe Stelle des Schiebers bedeutet. Für jemanden, der einmal davorsteht, ist ein
Bedienelement, das seine Bedeutung wechselt, nicht zu durchschauen. Dazu liefen Achse und Auswahl
auseinander, sobald der Ausschnitt weniger Jahrzehnte enthielt als der Gesamtbestand, und der
Auswahlbalken zeichnete sich ausserhalb seines Feldes.

**Was die feste Achse zusätzlich kann:** Eine leere Achse mit einem einzelnen Balken sagt etwas, das
die mitskalierende Achse verschwieg — *hier gibt es nur Fotos aus diesem einen Jahrzehnt.*

**Die Absicherung:** `fraction()` in `kiosk/timeAxis.ts` klammert auf 0…1, `setTimeRange()` zieht die
Auswahl in die Achse. Selbst wenn beide je wieder auseinanderlaufen, bleibt jedes Element in seiner
Zelle.

---

## 15. Fotos am selben Ort: ein Stapel zum Blättern, kein Fächer

Fotos auf demselben Punkt (auf rund einen Meter genau) werden **vor** dem Clustern zu einem Eintrag
zusammengefasst. Auf der Karte stehen sie als ein Vorschaubild mit der Anzahl in der Ecke; ein Tipp
öffnet die Vollbildansicht, dort wird geblättert.

**Warum nötig.** Fotos auf identischen Koordinaten wurden oberhalb der Clusterschwelle zu ebenso
vielen Markern exakt übereinander, von denen nur der oberste erreichbar war. **Identische Punkte
trennen sich bei keiner Zoomstufe.**

**Warum nicht auffächern.** Ein Fächer zeigt die Fotos dort, wo sie nicht sind, und ist bei einem
größeren Stapel dauerhaft unruhig; am Kartenrand hat er keinen Platz. Ein Fächer *auf Tipp* führt
zudem einen Zustand ein, den man wieder verlassen muss, ohne dass etwas den Ausweg zeigt.
Zwei-Schritt-Gesten sind das, woran ältere Besucher hängenbleiben.

**Warum vor dem Clustern.** Danach zu gruppieren hilft nur unterhalb von `CLUSTER_MAXZOOM`. So sieht
supercluster gar keine Dubletten, und ein Stapel ist auf **jeder** Zoomstufe ein Marker.

**Die Schwelle ist fünf Nachkommastellen**, also rund ein Meter. Sie trifft den tatsächlichen Fall:
Fotos aus der Ortsauswahl tragen exakt dieselbe Koordinate der Straße. Wer den Punkt von Hand
gesetzt hat, liegt daneben und bleibt ein eigener Marker — richtig so, denn dann *ist* es eine
andere Stelle.

**Oben liegt das zuletzt bearbeitete Foto**, weil die Kartenabfrage nach `updated_at` sortiert.
Damit liegt das eben verortete Foto dort obenauf, wohin die Karte nach einem Beitrag fährt.

---

## 16. Löschen heißt: aus der Ausstellung genommen, nicht von der Platte entfernt

Der Status heißt `deleted` statt `hidden`, die Bilddatei bleibt liegen, die Datenbankzeile steht,
und „Wiederherstellen" holt beides zurück. Das spart drei Probleme:

- Der SHA-256 bleibt bekannt; ein erneuter Import erkennt die Dublette und bringt das Foto nicht
  ungefragt zurück.
- Änderungs- und Import-Protokoll zeigen weiter auf ein Foto, das es gibt.
- Die Sicherung braucht keine Sonderregel für einen Papierkorb.

**Was daraus folgt, ist der eigentliche Teil der Entscheidung:** Gelöschte Fotos zählen in keiner
Kachel der Übersicht mit und stehen in keiner Liste ausser „Gelöscht" — auch nicht in „Alle". Sonst
wäre das Löschen dort wirkungslos, wo jemand hinsieht, und die Arbeitslisten legten immer wieder das
Foto vor, das eben jemand aussortiert hat. Jede Zahl sagt dasselbe wie die Liste, in die sie führt.

**Der Preis:** Es gibt keinen Weg, ein Foto nur *vorübergehend* auszublenden, ohne es „gelöscht" zu
nennen — etwa, solange die Rechtelage geklärt wird. Wer das braucht, braucht einen dritten Status,
keine zweite Bedeutung für diesen.

---

## 17. Der Migrationsverlauf wurde einmal zusammengefasst — und das war die letzte Gelegenheit

Die vorhandenen Alembic-Revisionen wurden zu einem Anfangsschema zusammengelegt, solange kein Gerät
Kiekmap ausgeführt hatte. Es gab also keine Datenbank, von der ein Migrationsweg irgendwohin hätte
führen können.

**Ab dem ersten Pi ist das nicht mehr erlaubt.** Sobald ein Museum eine gefüllte Datenbank hat, ist
die Kette der Migrationen der einzige Weg, auf dem seine Daten eine Schemaänderung überleben. Das
Zusammenfassen wäre dann kein Aufräumen, sondern ein Datenverlust mit Ansage.

**Das `PRAGMA foreign_keys=OFF` in `alembic/env.py` bleibt.** Es ist die Lehre aus einem
Datenverlust, und der Test, der es bewacht, hängt an keiner Revisionsnummer — ein Test, der mit dem
Fehler stirbt, den er bewacht, ist keiner.

---

## 18. Der Beispielbestand liegt als Bilder plus JSON, nicht als Datenbankabzug

`seed/` enthält die Bilddateien unter ihren ursprünglichen Namen und eine `seed.json` mit allem
Übrigen.

**Ein Datenbankabzug wäre der kürzere Weg und ist trotzdem der falsche:** Er ist wertlos, sobald
eine Spalte dazukommt, und genau das passiert hier regelmäßig. So kostet eine neue Spalte eine Zeile
je Foto, und der Bestand muss nicht neu kuratiert werden.

Zwei Eigenschaften fallen dabei ab:

- **Das Einlesen geht durch die echte Import-Pipeline**, erzeugt die Vorschaubilder, füllt das
  Import-Protokoll und prüft den Import bei jedem Lauf gleich mit.
- **Die Datei ist im Diff lesbar.** Wer eine Datierung ändert, sieht das als eine Zeile.

SHA-256, Dateigröße, Abmessungen und MIME-Typ stehen mit Absicht **nicht** darin: Sie werden beim
Einlesen aus dem Bild gelesen, eine Kopie könnte nur veralten. Der SHA-256 ist die Ausnahme und
warnt allein davor, dass sich eine Datei seit dem Sichern geändert hat.

**Die Lücken im Bestand sind Teil des Bestands.** Fotos ohne Jahr, ohne Ort, eines ohne beides, ein
zurückgenommener Besucherbeitrag: Ohne sie prüft der Bestand die Hälfte des Programms nicht.
`test_luecken_bleiben_luecken` hält fest, dass auch das Einlesen sie nicht zuschüttet.

---

## 19. Bildnachweis und Herkunft sind zwei Felder, weil sie zwei Leser haben

- **`credit`** — der Bildnachweis, eine Zeile, steht im Besucher-Overlay unter der Beschreibung.
- **`provenance`** — von wem das Bild kam, ob es eine Leihgabe ist, ob eine Freigabe vorliegt. Eine
  interne Notiz, die die Verwaltung nie verlässt.

**Durchgesetzt wird das durch den Typ, nicht durch eine Verabredung.** Der Kiosk-Endpunkt liefert
`PhotoDetail`, und diese Klasse hat kein Feld für die Herkunft — sie kann sie also auch
versehentlich nicht mitschicken. Die Verwaltung bekommt `PhotoAdminDetail`, das davon erbt. Eine
Regel, die nur im Kopf steht, hält der nächste Endpunkt nicht ein.

Beide sind auch gemeinsame Angabe des Stapel-Imports: Eine Kiste Scans kommt fast immer von einer
Person, und keines der beiden Felder kann aus der Datei stammen — ein Scanner weiß nicht, wer das
Bild verliehen hat.

---

## 20. Der Import wertet aus, was die Dateien und ihre Ordner schon sagen

Museumsarchive sind nach Straße und Hausnummer abgelegt:

```
Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
```

Wer diese Ordnernamen verwirft, fragt Besucher nach dem Ort eines Fotos, dessen Adresse
danebensteht — und lässt Ehrenamtliche Adressen abtippen, die schon da sind.

**Die Regeln zerfallen in zwei Schichten, und die Trennung ist der eigentliche Entwurf:**

| Schicht | Gilt für | Was sie tut |
|---|---|---|
| **Metadaten** (`import_file`) | *alle vier* Importwege | Datum, Ort, Titel, Beschreibung, Nachweis, Herkunft, Schlagwörter aus EXIF/IPTC |
| **Pfad** (`foldermeta.py`) | Eingangsordner, CLI, USB-Stick | Straße und Hausnummer aus den Ordnernamen |

**Angeschaltet wird die zweite Schicht über den `root`-Parameter von `import_file()`** — den Ordner,
auf dem der Import gestartet wurde. Damit ist es **eine Frage, die man beantworten muss, statt sie
übersehen zu können**: Wer einen fünften Importweg baut, entscheidet über einen Parameter, was die
Wurzel dieser Datei ist. Der Browser-Upload antwortet mit `None`, weil ein Browser keinen Pfad
schickt.

### Erst das Gerät, dann die Jahresgrenze

`exif_date_max_year` ([Punkt 1](#1-historische-fotos-sind-scans--das-prägt-das-ganze-datenmodell))
bleibt, ist aber der **Ersatz für eine fehlende Geräteangabe**, nicht die erste Instanz:

- **Scanner** (`HP Scanjet 3670`) → **kein Datum**, ganz gleich welches Jahr dort steht. Unbesehen
  datiert lägen historische Ortsbilder am Tag des Scans auf der Zeitleiste und kämen, weil sie als
  datiert gelten, nie zur Korrektur.
- **Kamera** (`OLYMPUS E-500`) → **Datum zählt, auch nach 1990.** Diese Aufnahmen sind wirklich neu;
  ohne die Umkehrung käme ein großer Teil des Bestands undatiert an.
- **Keine Geräteangabe** → die Jahresgrenze entscheidet allein.

Die Umkehrung ist am Bestand nachgemessen: Die Kamerafotos sind fast durchweg farbige Aufnahmen der
Häuser, wie sie heute stehen, und keine Reprofotos alter Abzüge.

### Die Straße erkennt der Ortsindex, nicht ein Ordner namens „Straßen"

Ein Pfadteil gilt als Straße, wenn `places` sie kennt. Deshalb steht trotz dieser Auswertung
**nichts Ortsspezifisches im Code**. Was das Archiv kürzt, wird ebenfalls erkannt — Ordner
„Wiesengrund", Straße „Im Wiesengrund" —, aber nur unter zwei Bedingungen:

1. **Genau ein Treffer.** „Deelenweg" steckt in „Deelenweg I" *und* „Deelenweg II"; geraten lägen
   die Fotos am anderen Ende des Dorfes.
2. **Jedes Wort enthält einen Buchstaben.** Der Hausnummernordner „2" traf sonst die Straße „Kolonie
   Autal 2" — eindeutig und vollkommen falsch. Eine Zahl ist eine Hausnummer; nur ein Name ist eine
   Straße.

### Ein Ordner ohne Hausnummer verortet auf der Straße

Zuerst blieb ein solches Foto unverortet, damit es nicht mit einem mehrere hundert Meter falschen
Punkt als beantwortet gilt und aus „Wo ist das?" fällt. Seit es die Nachschärf-Frage gibt
([Punkt 32](#32-nachschärfen-läuft-über-einen-eigenen-endpunkt-nicht-über-eine-gelockerte-prüfung)),
fällt es nicht heraus, sondern in die genauere Frage hinein. Der Straßenname wird zusätzlich
Schlagwort und Ortsbezeichnung.

### Vorrang, wo zwei Quellen sprechen

Eine Koordinate aus den Metadaten schlägt den Ordner, solange der Ordner keine Hausnummer nennt —
die Abwägung steht in
[Punkt 34](#34-der-archivordner-schlägt-die-exif-koordinate--sobald-er-eine-hausnummer-nennt).
Umgekehrt setzt die Pfad-Schicht **nur leere Felder**.

### Die Kehrseite

Der Import ist damit **nicht mehr zurückhaltend**, und ein Foto, das er betitelt, gilt als betitelt
und wird nicht mehr vorgelegt. Deshalb bleibt die Prüfung auf Nichtwerte streng
([Punkt 52](#52-eine-vorgabe-ist-kein-befund)), deshalb setzt die Pfad-Schicht nur leere Felder, und
deshalb wandert ein zu langer Titel in die Beschreibung
([Punkt 48](#48-was-im-titelfeld-steht-ist-nicht-automatisch-ein-titel)).

---

## 21. Kein Gemeindewappen im Repo

`frontend/public/logo.png` ist ein Platzhalter aus `tools/build_logo.py`; das Wappen wird auf dem
Gerät eingesetzt, wie die Kartendaten.

Der Grund ist keine Lizenzfrage, und genau darin liegt die Falle. Ein Gemeindewappen ist nach
**§ 5 Abs. 1 UrhG ein amtliches Werk und gemeinfrei**. Daneben steht aber das **Wappenrecht**: Ein
Wappen ist ein Hoheitszeichen, seine Führung regelt die Gemeinde, geschützt über das Namensrecht
(§ 12 BGB) und die Vorschriften über Hoheitszeichen.

**Ein Hinweis heilt das nicht.** Bei einer Lizenz hilft Namensnennung — man nennt den Urheber und
darf. Hier geht es um *Erlaubnis*, und die ist nicht durch eine Fußnote zu ersetzen. Dazu sind die
beiden Fälle verschieden:

| | |
|---|---|
| Das Museum zeigt das Wappen seines Ortes auf seinem Kiosk | in aller Regel unproblematisch |
| Ein öffentliches Repo enthält die Datei | gibt sie an jeden weiter, der klont |

**Ein Repo liefert seine Historie mit**, ein späteres Löschen genügt also nicht — die Datei muss aus
dem ganzen Verlauf verschwinden, und das geht nur, solange es keinen Remote gibt.

**Der Tausch kostete eine Datei und keine Zeile Logik**, weil nirgends im Code steht, was auf dem
Bild zu sehen ist. Dieselbe Eigenschaft, die ein zweites Museum ohne Fork auskommen lässt, hat hier
ein Rechtsproblem auf einen Dateitausch reduziert.

---

## 22. Der Backlog wird klassifiziert und bleibt trotzdem eine Datei

[backlog.md](backlog.md) hat eine **Art** je Punkt, eine **Einordnung** nach Wichtigkeit und
Dringlichkeit, und eine **Nummer**.

**Vier Arten, weil vier verschiedene Dinge zu tun sind.** *Fehler* (etwas tut nicht, was es zusagt),
*Aufgabe* (klar umrissen, es fehlt nur die Arbeit), *Frage* (vor der Arbeit ist zu entscheiden, was
gebaut wird), *Idee* (noch nicht entschieden, ob überhaupt). Der Schnitt sitzt dort, wo er die
Arbeit ändert: Eine Aufgabe kann man an einem Nachmittag aufgreifen, eine Frage nicht.

**Wichtigkeit und Dringlichkeit sind zwei Achsen, weil sie hier auseinanderfallen.** Die Abnahme auf
dem ersten Pi ist der gewichtigste offene Punkt und trotzdem nicht dringend, weil das Gerät fehlt.
Eine einzige Prioritätsspalte hätte ihn entweder überhöht oder kleingeredet. Jede Achse hat deshalb
eine Definition in der Datei: **dringend** heißt, es trifft heute jemanden oder es blockiert einen
anderen Punkt; **wichtig** heißt, ohne das ist das Projekt auf Dauer nicht das, was es sein soll.

**Die Nummer wird nie neu vergeben**, auch nicht nach dem Erledigen. Sie soll in einem Commit, einer
Besprechung oder einem Auftrag an einen Coding-Agent auf genau eine Sache zeigen, auch noch, wenn
die Überschrift sich geändert hat. Eine wiederverwendete Nummer zeigt später auf etwas anderes; das
ist schlimmer als keine Nummer. Der Preis: Die Reihenfolge in der Datei löst sich mit der Zeit von
der Zählung. Sortiert wird nach Einordnung, nicht nach Nummer.

Diese Datei hier hält es genauso: **Punkt 8 fehlt**, weil er in
[Punkt 11](#11-sicherung-ist-eine-funktion-kein-skript) aufgegangen ist.

**Die Einordnung steht nur in der Übersichtstabelle**, nicht zusätzlich unter jeder Überschrift.
Zwei Stellen für dieselbe Angabe laufen auseinander, und welche dann stimmt, weiß niemand.

**Und es bleibt eine Datei.** Solange der Backlog eine Datei ist, liest er sich am Stück, steht in
derselben Historie wie der Code, den er beschreibt, und überlebt einen Kontextverlust eines
Coding-Agents. **Der Umzug lohnt, sobald mehr als eine Person daran arbeitet oder die Reihenfolge
häufiger wechselt als die Inhalte.**

---

## 23. Nach einem Beitrag zählt dasselbe Foto, nicht das nächste

Wer eine Frage beantwortet, bekommt anschließend **dasselbe Foto mit der anderen Frage**, solange
dieser Frage etwas fehlt. Erst wenn nichts mehr fehlt, kommt ein neues Foto.

**Der Grund ist eine Zusage, die sonst bricht.** Der Dank sagte nach jedem Beitrag „Das Foto ist
jetzt auf der Zeitleiste" — auch bei einem Foto ohne Ort, das auf keiner Karte erscheint. Eine
Meldung darf nur behaupten, was die Ansicht im selben Moment zeigt.

**Ein ehrlicherer Satz hätte nicht gereicht.** Der Besucher bekäme weiter nichts zu tun,
unmittelbar nachdem er gezeigt hat, dass er dieses Foto kennt. Stattdessen fragt der Dank nach dem,
was fehlt, und die nächste Frage gilt demselben Foto — das ist zugleich der ergiebigste Moment, den
der Bereich bekommt.

**Was bewusst übergangen wird:** die Liste der weggetippten Fotos. Wer eines weggewischt hat und
jetzt doch etwas beiträgt, bekommt es mit der anderen Frage wieder vorgelegt. „Weiß ich nicht"
bleibt der Ausweg, und die Kette endet von selbst.

---

## 24. Die Straße wird gewählt, nicht getippt

**Aufgegangen in [Punkt 13](#13-verortung-in-schritten-straße-dann-abschnitt-dann-hausnummer)**, wo
die Verortung in einem Stück steht. Die Nummer bleibt für ältere Zitate stehen.

---

## 25. Die Balken bündeln, was der Bestand hergibt

Wie viele Jahre ein Balken hinter dem Zeitschieber umfasst, rechnet `bar_width()` in
[services/dates.py](../backend/app/services/dates.py) aus, nach zwei Regeln.

**Erstens: nie feiner als die gröbste Datierung im Bestand.** Ein auf „1920er" datiertes Foto trägt
`date_from = 1920-01-01`. In Jahresbalken sammeln sich seine zehn Jahrgänge auf dem einen Balken
1920, wo in Wahrheit ein Jahrzehnt liegt. Derselbe Fehler, dessentwegen das Datenmodell mit
Intervallen arbeitet ([Punkt 1](#1-historische-fotos-sind-scans--das-prägt-das-ganze-datenmodell)),
nur in der Anzeige: Er sieht nicht nach Fehler aus, sondern nach Befund.

**Zweitens: so breit, dass die Spanne in dreißig Balken passt.** Gewählt wird aus 1, 5, 10, 25, 50
Jahren, damit die Beschriftung lesbar bleibt.

**Die Höhe wird mit der Wurzel skaliert, nicht linear.** Linear verschwindet ein kleiner Jahrgang
neben einem großen fast vollständig, und eine Untergrenze klemmte ihn dann auf denselben Sockel, den
auch ein Jahrzehnt mit einem einzigen Foto bekam. Mit der Wurzel bleibt er klar kleiner und klar
vorhanden. Ein **leerer** Balken bleibt bei null: Ein Sockel dort schickte den Besucher an eine
Stelle, wo nichts liegt.

**Die Breite gehört der Sammlung, nicht dem Ausschnitt**, genau wie die Achse. Sonst wechselte die
Bedeutung eines Balkens beim Verschieben der Karte.

**Die Achse reicht über das letzte Jahr hinaus.** Der Balken für das jüngste Jahr braucht sein
eigenes Stück Bahn; sonst begänne er am rechten Rand und liefe darüber hinaus.

---

## 26. Zwei Wege in die Verwaltung, und keiner davon ist mehr das Wappen

*Schreibt [Punkt 7](#7-der-zugang-zur-verwaltung-ist-sichtbar-die-pin-schützt-ihn) fort, der genau
einen Weg festgelegt hatte.*

| Wo | Wohin |
|---|---|
| Der Titel im Kopfbereich | in die Verwaltung |
| Ein Stift neben dem Titel der Detailansicht | direkt in die Bearbeitung **dieses** Fotos |

**Das Wappen verliert diese Aufgabe** und bekommt eine andere: Ein Tipp darauf lädt neu und setzt
die Filter zurück.

**Punkt 7 wird dadurch nicht aufgeweicht.** Dort wurde nicht „genau ein Weg" entschieden, sondern
**„sichtbar statt versteckt"**. Beide neuen Wege sind sichtbar und durch dieselbe PIN gesichert.

**Warum der zweite Weg.** Wer am Gerät ein falsch beschriftetes Foto sieht, musste bisher in der
Verwaltung danach suchen — und wonach er sucht, ist ausgerechnet der Titel, der falsch ist.

**Warum das Wappen das Zurücksetzen bekommt und nicht ein eigener Knopf.** Der Besucherschirm hatte
keinen Weg zurück in den Anfangszustand; es gab nur Umwege — fünf Minuten warten, die PIN eingeben
und wieder hinaus, oder den Netzstecker. Ein *zusätzlicher* Knopf wäre einer, den fast niemand
braucht und den trotzdem jemand drückt, und er wirft die Arbeit weg, die gerade jemand angefangen
hat. Das Wappen kostet keine zusätzliche Fläche und ist bereits als tippbar bekannt.

**Die Kennung unter dem Bildnachweis.** In der Detailansicht stehen unten, klein und grau, die
**ersten acht Zeichen des SHA-256**. Sie sind die Identität des Fotos unabhängig von jeder
Datenbank: Ein neu aufgebauter Bestand vergibt neue laufende Nummern, derselbe Scan behält seinen
Hash. Acht Hexzeichen sind kurz genug zum Abschreiben und eindeutig genug für einen Museumsbestand —
dieselbe Länge, die git aus demselben Grund nimmt. **Die Verwaltungssuche findet sie**, und das ist
die Bedingung, unter der sie dort stehen darf.

**Der Preis:** Wer das Wappen antippt, weil er in die Verwaltung will, setzt stattdessen die Ansicht
zurück. Für ein bis zwei Ehrenamtliche im Jahr ist das verkraftbar.

---

## 27. Der Kartentipp ist erst nach Ansage scharf

Solange „Wo ist das?" steht, war die ganze Karte scharf: Jeder Tipp auf eine freie Fläche setzte
einen Punkt. Jetzt muss der Besucher das über den Knopf **„Auf der Karte zeigen"** verlangen.

**Der Grund ist die Datenqualität.** Wer während der Frage nur schauen will, beantwortete sie dabei
versehentlich — ein Tipp daneben, ein bestätigender danach, und im Bestand stand eine Verortung, die
niemand gemeint hat.

**Es ist immer nur ein Weg auf dem Schirm.** Wer die Karte scharf schaltet, dem verschwindet die
Straßenwahl. Nebeneinander standen sie sich im Weg: Das Knopfraster wirft bei der nächsten Berührung
weg, was der Kartentipp gerade gesetzt hat. Der Knopf steht deshalb **über** der jeweiligen Auswahl
— er ist die Alternative *zu* ihr, und darunter läse er sich als letzter Ausweg.

**Angeboten wird er in jedem Schritt, auch bei der Hausnummer**, und dort verdient er am meisten:
Wer die Straße kennt, die Nummer aber nicht, zeigt auf das Haus statt „Reicht so" zu drücken.

**Zwei Dinge bleiben unabhängig davon scharf.** Der gesetzte Punkt wird immer gezeichnet und lässt
sich immer ziehen, gleich wer ihn gesetzt hat. Im Code sind das deshalb zwei Bedingungen und nicht
eine (`armed` und `active`).

**Ohne Ortsverzeichnis gibt es keine zweite Wahl** — dann ist die Karte von Anfang an scharf, sonst
wäre der Bereich unbedienbar. Das trifft eine Einrichtung, die `make places` nie gelaufen hat.

**Der Schalter liegt im Store, nicht in der Komponente.** `LocationTask` wird bei fast jedem
Fotowechsel abgebaut, ein `useState` fiele dort von selbst zurück — nur nicht auf dem einen Weg, auf
dem die Frage zur ursprünglichen zurückfällt, weil die andere leergelaufen ist. Der hinterliesze
eine scharfe Karte über einem Foto, das der Besucher noch nicht angesehen hat.

---

## 28. Fotos ohne Jahr sind ein Schalter, keine Nebenwirkung

Ein Foto ohne Datum überlappt keinen Zeitraum. Es fiel damit aus **jeder** Auswahl heraus, sobald
der Besucher den Schieber auch nur ein Stück zusammenzog — bei diesem Bestand zwei Drittel der
Sammlung, ohne dass irgendwo gestanden hätte, dass das passiert. Jetzt steht daneben ein Schalter:
**„… Fotos ohne Jahr anzeigen"**, mit Haken und der Zahl darin.

**Die Zahl stand ohnehin dort.** Sie war eine Meldung; jetzt ist sie die Beschriftung einer
Handlung. Es kommt kein Bedienelement hinzu, ein vorhandenes bekommt einen Zweck.

**Eingeschaltet heiszt „kein Datum ODER Überlappung".** Der Zeitraum gilt dann nicht mehr für alles
auf dem Schirm. Das ist eine echte Einbusze an Genauigkeit, und sie ist vertretbar, weil der
Besucher sie sieht und selbst eingestellt hat.

**Er steht anfangs an und geht genau einmal von selbst aus** — beim ersten Zusammenziehen des
Zeitraums, also in dem Moment, in dem die Auswahl anfängt, etwas zu bedeuten. Der Anfangszustand
zeigt alles, was das Museum hat, und niemand verliert etwas, ohne es getan zu haben.

**Danach gehört der Schalter dem Besucher.** Wer ihn von Hand wieder einschaltet, bei dem bleibt er
an. Ginge er jedes Mal wieder aus, überschriebe die Automatik eine Entscheidung, die jemand gerade
getroffen hat.

**Wonach die Automatik greift, ist `queryTimeFilter`** — dieselbe Funktion, die entscheidet, ob
überhaupt ein Zeitfilter zum Backend geht. Damit geht der Schalter exakt dort aus, wo sonst Fotos
anfingen zu verschwinden. Eine zweite Regel dafür wäre eine zweite Wahrheit gewesen.

**Das Histogramm zählt die undatierten Fotos immer mit.** Sonst stünde dort nach dem Abschalten eine
Null, das Etikett verschwände — und mit ihm der einzige Weg zurück.

Der Schalter ist ein Knopf mit gezeichnetem Kästchen, kein `input[type=checkbox]`: Der ist zu klein
für die Mindestgröße von 48 px, die für diese Zielgruppe gilt.

---

## 29. Unter dem Vorschaubild steht die Adresse, nicht das Datum

**Überholt durch [Punkt 39](#39-eine-beschriftung-für-das-auge-und-für-das-vorlesewerkzeug)**, der
die Beschriftung auf den Titel umgestellt und die Regeln übernommen hat, die weiter gelten. Die
Nummer bleibt für ältere Zitate stehen.

---

## 30. Vier Rollen, und jede sieht wie ein Knopf aus

| Rolle | Form | Symbol | Beispiele |
|---|---|---|---|
| **auswählen** | weiß mit Rand | — | Buchstabe, Straße, Jahrzehnt, Jahr, Hausnummer, „Auf der Karte zeigen" |
| **übernehmen** | gefüllt, Akzentbraun | Haken | „Hier war das", „Ganze 1920er Jahre", „Reicht so — die Straße genügt" |
| **zurück** | weiß mit Rand, graue Schrift | Pfeil links | „Anderer Buchstabe", „Doch nicht — von vorn" |
| **überspringen** | wie zurück, durch eine Linie abgesetzt | Pfeil rechts | „Weiß ich nicht — nächstes Foto" |

**Die randlose Form ist weg.** Sie war grau, ohne Rand und las sich als Text — für eine Zielgruppe,
die einmal im Jahr vor diesem Gerät steht, genau das Falsche. Leiser wird ein Knopf über die
Schriftfarbe, nicht über die Form; Rand und Höhe sind bei allen gleich und halten die Mindestgröße
für den Finger ein.

**Die wichtigste Grenze verlief an der falschen Stelle.** Dieselbe leise Form trug *zurückgehen* und
*überspringen* — das eine bleibt beim Foto, das andere legt es weg. Was über der Linie steht, gehört
zur Frage, was darunter steht zum Foto.

**„Reicht so — die Straße genügt" ist eine Antwort und sieht seitdem danach aus.** Nicht jedes Haus
steht in OpenStreetMap, und wer die Nummer nicht kennt, soll das ohne Zögern sagen können.
Konkurrenz entsteht nicht: In diesem Schritt steht kein zweiter gefüllter Knopf auf dem Schirm.

**Symbole neben der Beschriftung, nie an ihrer Stelle.** Ein Piktogramm allein verlangt Vorwissen,
das ältere Besucher nicht mitbringen müssen. Der Satz ist deshalb klein — Haken, Pfeil links, Pfeil
rechts, Fadenkreuz —, und alles andere trägt keins. **Gezeichnet, nicht geladen**
(`kiosk/icons.tsx`): Das Gerät ist offline, und ein Symbol, das nicht lädt, hinterlässt einen Knopf,
der nichts sagt.

**Die Verwaltung bleibt ausdrücklich draussen.** Sie hat eigene Masze, wird ein- bis zweimal im Jahr
benutzt und folgt einer anderen Regel: Dort zählt Klartext mehr als Kompaktheit.

---

## 31. Der Kopfbereich steht auf einer Mittellinie, der Zeitraum auf einem Boden

Wappen, Titel und Zeitschieber richten sich senkrecht mittig aus. Sie standen oben bündig und
endeten sichtbar auseinander, während ein Kommentar im CSS vorrechnete, sie seien gleich hoch. Das
galt für eine Schirmbreite, und bis der Schieber wuchs.

**Drei Rechnungen, die auseinanderlaufen können, sind durch eine gemeinsame Mittellinie ersetzt:**
`align-items: center` im Titelfeld, `justify-content: center` im Schieberfeld. Beide Zellen der
Gitterzeile sind ohnehin gleich hoch, also steht die Zeile mittig, ohne dass eine Seite die Höhe der
anderen kennen müsste.

**Der Zeitraum lässt sich nicht unter ein Jahrzehnt zusammenschieben.** Der ausgewählte Bereich ist
zugleich die Fläche, an der man ihn über die Achse zieht; auf einen Balken zusammengeschoben bliebe
nichts zum Anfassen. Dafür trug er einen gezeichneten Griff in der Mitte — eine Marke für einen
Zustand, in den niemand geraten will. Der Griff ist weg, der Boden ist da: `minSpan()` in
`kiosk/timeAxis.ts`, ein Jahrzehnt, aber nie schmaler als ein Balken.

**Das bewegte Ende stoppt, das andere wird nie mitgeschoben.** Mitzuschieben klingt geschmeidiger
und ist die Falle: Ein Zug am linken Ende trüge das rechte über das Achsenende, wo es geklemmt
würde — und der Zeitraum käme schmaler zurück, als er hineinging.

---

## 32. Nachschärfen läuft über einen eigenen Endpunkt, nicht über eine gelockerte Prüfung

Die erste Ausnahme zu
[Punkt 5](#5-besucherbeiträge-werden-direkt-übernommen--mit-vollständigem-protokoll), und sie ist so
gebaut, dass sie den Satz dort **nicht anfasst**.

**Der Fall.** Ein Foto, das nur seine Straße kennt, liegt auf deren Mitte — bei einer langen Straße
mehrere hundert Meter vom Haus entfernt. Es gilt als verortet und wird deshalb nie wieder vorgelegt.
Nachschärfen heißt aber, eine vorhandene Angabe zu ersetzen, und genau das verbietet Punkt 5.

**Entscheidung: nicht `_require_empty` lockern, sondern ein eigener Endpunkt, der keine Koordinate
annimmt.**

```
POST /api/contribute/{photo_id}/housenumber   { place_id, session_id }
```

Der Server schlägt `place_id` im Ortsverzeichnis nach, prüft `kind == "adresse"` und dass die
Adresse zur Straße des Fotos gehört, und schreibt Koordinate, `place_name` und Genauigkeit **aus der
Ortsindex-Zeile**. Der Besucher wählt aus einer Menge, die der Server aufgestellt hat.

**Warum daran alles hängt.** `POST /location` nimmt `accuracy_m` vom Client entgegen. Heute ist das
eine harmlose Behauptung, *weil* das Feld ohnehin leer sein muss. Würde die Genauigkeit darüber
entscheiden, ob überschrieben werden darf, wäre sie ein Schlüssel — und den hielte der Client: Ein
Aufruf mit `accuracy_m: 1` dürfte jede Angabe im Bestand ersetzen. Die Regel „genauer darf ungenauer
ersetzen, nie umgekehrt" ist richtig; sie ist nur nichts, was man dem zu bewerten geben darf, der
davon profitiert.

**Wer gefragt wird**, entscheidet `services/needs.py`: ein Foto auf der Karte, noch nicht hausgenau,
mit einem `place_name` **ohne Ziffer** — steht die Nummer schon im Namen, fehlt nur die Koordinate,
und das ist maschinelle Arbeit —, und der Ortsindex muss für diese Straße überhaupt Adressen haben.
Knapp ein Drittel der Straßen im Index hat keine; ohne diese Bedingung stünde die Frage ohne einen
einzigen Knopf darunter auf dem Schirm. **Woher die Koordinate stammt, zählt ausdrücklich nicht**;
warum das zuerst anders war, steht in
[Punkt 45](#45-woher-eine-koordinate-kommt-sagt-nichts-darüber-wie-genau-sie-ist).

**Kuratorenangaben sind ausdrücklich einbezogen**, Besucherarbeit überschreibt hier also
Kuratorenarbeit. Getragen wird das von der Rücknahme: `Change` hat eine Spalte `old_source`, und
„zurücknehmen" heißt hier **zurücksetzen auf die Straßenmitte** samt der alten Quelle, nicht löschen.
Ohne diese Spalte machte eine Rücknahme aus Kuratorenwissen einen Besucherbeitrag. **Ältere
Ortsangaben lassen sich erst zurücknehmen, wenn die neueren zurückgenommen sind** — sonst liesze
eine Rücknahme einen längst ersetzten Ort wieder auferstehen.

**Was diese Begründung aushöhlen würde**, ohne dass eine einzelne Änderung falsch aussähe:
Koordinaten vom Client anzunehmen; weitere Genauigkeitsstufen einzuführen und die Regel darauf zu
verallgemeinern; die Prüfung `place.street == photo.place_name` zu lockern. Jedes für sich wäre eine
Bequemlichkeit, zusammen wären sie das Ende von Punkt 5.

---

## 33. Stapel werden nicht gestreut, Stufenwechsel werden animiert

**Die Marker blenden ein, wenn die Gruppierung kippt.** `draw()` fragt supercluster auf der
**gerundeten** Zoomstufe ab; beim Wischen läuft der Zoom stetig, die Gruppierung wechselt aber erst,
wenn die Rundung umspringt — und dann alle Marker auf einmal. Animiert wird deshalb der Wechsel,
nicht feiner abgefragt: Feiner abzufragen hieße häufiger zeichnen, und das kostet auf dem Pi mehr,
als es auf dem Mac aussieht.

**Gezeichnet wird auf `moveend`**, und nur, wenn sich die Menge der Gruppen tatsächlich geändert hat.
Vorher hing `draw()` an `move` *und* `zoom`; beide feuern zusammen und dutzendfach je Zoomstufe.
Nötig war nichts davon, denn MapLibre hält die Marker selbst auf ihren Koordinaten.

**Und Stapel werden nicht gestreut.** Sie auseinanderzuziehen wäre die naheliegende Abhilfe und ist
die falsche: **Eine gestreute Position täuscht eine Genauigkeit vor, die es nicht gibt.** Ein Stapel
liegt auf einem Punkt, weil alle seine Fotos nur die Adresse kennen; auseinandergezogen sähen sie
aus wie ebenso viele verschiedene Stellen.

Streuen und Nachschärfen sind zwei Antworten auf dieselbe Frage, und nur eine erzeugt Daten. Das
Nachschärfen
([Punkt 32](#32-nachschärfen-läuft-über-einen-eigenen-endpunkt-nicht-über-eine-gelockerte-prüfung))
hält die Ungenauigkeit **sichtbar**, damit jemand sie behebt.

---

## 34. Der Archivordner schlägt die EXIF-Koordinate — sobald er eine Hausnummer nennt

Bis dahin galt: eine Koordinate aus der Datei schlägt den Ordner immer. Die Begründung las sich als
*Messung gegen Meinung* — die Kamera stand tatsächlich dort, der Ordner ist die Ablage von jemandem.

**Am Bestand nachgemessen ist sie keine.** **Zwei Drittel der EXIF-verorteten Fotos teilen ihre
Koordinate mit einem anderen Foto**, und an einzelnen Punkten hängen Aufnahmen aus mehreren Jahren.
Kein Empfänger liefert an vier Tagen sechs gleiche Nachkommastellen — diese Werte sind eingetragen
worden. Es steht also eine Ablage gegen eine andere, und nur eine davon macht sich am Ortsindex
fest.

**Deshalb gewinnt die Ordneradresse — aber nur die Adresse.** Die Straßenmitte gewinnt nicht: Sie
ist mit 150 m gröber als der Punkt, den sie ersetzen würde. Ein Foto, dessen Ordner keine Hausnummer
nennt, behält seinen EXIF-Punkt. Diese Grenze ist die eigentliche Regel, und sie hat ihren eigenen
Test.

**Was diese Entscheidung aushöhlen würde:** eine spätere Quelle, die Koordinaten liefert, ohne dass
nachgesehen wird, ob sie gemessen oder eingetragen sind. Die Begründung hängt an einer Messung,
nicht an einer Rangordnung der Quellen — wer sie zitiert, ohne nachzuzählen, zitiert sie falsch.

---

## 35. Die Hausnummer wird vor dem Jahr gefragt, und das ist Arithmetik

Die Reihenfolge in `NEEDS` (`services/needs.py`) ist der Rang, und eine Frage wird erst erreicht,
wenn die vor ihr **leer** ist. Sie lautete `location, date, housenumber` — aus dem Gefühl heraus
richtig, denn ein Jahr ist mehr wert als eine Hausnummer.

**Am Bestand ist das Gefühl falsch.** Fast alle Fotos sind verortet, zwei Drittel sind undatiert,
und zum Nachschärfen stehen einige Dutzend an. Die Jahresfrage läuft nie leer, die dritte Frage wäre
also nie erreicht worden. Das Nachschärfen dagegen läuft nach wenigen Dutzend Antworten trocken, und
danach hat die Jahresfrage den Bereich für sich.

**Die Nachrangigkeit einer Frage bemisst sich nicht an ihrem Wert, sondern daran, ob die vor ihr je
zu Ende geht.**

**Eine Ausnahme von der Rangfolge:** Wer „Reicht so — die Straße genügt" gedrückt hat, wird nicht im
selben Atemzug nach der Hausnummer gefragt. Die Frage wäre schon beantwortet.

---

## 36. Archivinterna gehören in die Herkunft, Fotorückseiten in die Beschreibung

Archive liefern abgeschriebene Rückseiten von Abzügen und Archivkarten als Schlagwörter mit. Sie
zerfallen in zwei Arten, und die eine gehört vor Besucheraugen, die andere nicht.

**Inhalt geht in die Beschreibung.** „Notiz: Grundsteinlegung der Turnhalle ca. 1968" ist eine
Aussage über das Bild. Als Schlagwort taugt sie nichts — sie hängt an genau einem Foto. **Der Präfix
„Notiz:" bleibt stehen**: Er ist die Quellenangabe. Der Satz stammt von der Rückseite, nicht von
einem Kurator, der das Bild betrachtet hat.

**Regalnummern gehen an die Herkunft.** „Notiz: P 11" ist eine Signatur des Archivs. Sie soll
erhalten bleiben — wer ein Foto im Regal wiederfinden will, braucht sie — aber sie gehört **nicht in
die Beschreibung**, denn die steht im Kiosk unter dem Bild. `provenance` ist das Feld dafür, und
`PhotoDetail` hat keines
([Punkt 19](#19-bildnachweis-und-herkunft-sind-zwei-felder-weil-sie-zwei-leser-haben)).

**Die Regel, die daraus folgt:** Eine Angabe, die dem Museum beim *Verwalten* hilft, gehört in die
Herkunft. Eine Angabe, die etwas über das *Bild* sagt, gehört in die Beschreibung.

---

## 37. Ein Jahr im Text datiert nicht das Foto, sondern manchmal nur das Haus

Undatierte Fotos tragen oft eine Jahreszahl in Titel, Beschreibung oder Schlagwort. Sie auszuwerten
ist naheliegend und wäre falsch:

| im Text steht | eine Regel liest | es ist aber |
|---|---|---|
| `Notiz: P 37` | 1937 | eine Regalnummer |
| `Friedhofsweg 30` | 1930 | eine Hausnummer |
| „erbaut 1972, verkauft 2000" | 1972 | keins von beidem |
| „**vor** 1978" | 1978 | eine Obergrenze |
| „in den 70er Jahren **abgerissen**" | 1970er | das Foto ist **davor** |

Daraus zwei Festlegungen:

**Zweistellige Kurzformen werden nicht ausgewertet.** „78" für 1978 ist im Bestand üblich und nicht
von Regalnummern und Hausnummern zu unterscheiden. Die Fotos, die daran hängen, bleiben undatiert.

**Gesucht wird das positive Muster, nicht das negative.** Nicht „ein Jahr ohne Warnwort", sondern
„ein Jahr, dem *um*, *ca.*, *im Jahre*, *Herbst*, *Dezember* oder *aus den* vorausgeht". Eine
Warnwortliste ist nie fertig.

**Übernommen wird einzeln durchgesehen und als Liste festgehalten, nicht als Regel.** Der Grund ist
eine Asymmetrie: Ein verworfener Vorschlag kostet nichts — das Foto bleibt undatiert und wird weiter
gefragt. Ein angenommener falscher Vorschlag macht das Foto **datiert**: Es fällt aus der Frage
heraus, liegt an der falschen Stelle der Zeitleiste, und niemand sieht es je wieder an. Dieselbe
Asymmetrie trägt schon die EXIF-Regel.

---

## 38. Die Detailansicht fragt nicht selbst, sie verzweigt in den Beitragsbereich

In der Detailansicht stehen bis zu drei Knöpfe, je an der Zeile, die sie ändern; ein Tipp schließt
die Ansicht und stellt dieses Foto im Beitragsbereich zu dieser Frage. Der Kiosk hat damit **einen
Antwortweg statt zwei**.

Zwei Gründe sprachen gegen die eingebetteten Auswahlraster, die es vorher gab:

**Die Textspalte lief voll.** Ein Foto ohne Jahr und ohne Hausnummer trug Dutzende Schaltflächen
unter der Beschreibung — allein die Jahrzehnte sind so viele, wie die Zeitleiste Jahrzehnte hat.

**Die Ortsfrage war dort nie zu stellen.** Sie braucht die Karte, und die Karte liegt unter dem
Overlay. Von den drei Fragen konnte die Detailansicht nur zwei, und ausgerechnet die wertvollste
nicht.

**Das Schließen ist nicht Nebenwirkung, sondern die halbe Absicht:** Bei „Wo ist das?" muss die
Karte frei werden, und es je Frage anders zu machen wäre eine Regel, die niemand sehen kann.

**Danach passiert nichts Besonderes**, und das ist die eigentliche Entscheidung: Dank, dann die
nächste offene Frage zu diesem Foto, dann ein neues. Ein Rückweg in die Detailansicht bräuchte eine
Sonderregel im Store und liesze die Kette wegfallen.

**Der Wunsch ist eine Bitte, keine Anweisung.** `GET /contribute/next?photo_id=…` prüft das Foto
gegen dieselbe Bedingung wie jedes andere und fällt auf die Zufallswahl zurück, wo sie nicht mehr
gilt. Sonst stünde eine Frage auf dem Schirm, die zwischen Tippen und Laden schon beantwortet wurde
— und der Schreibweg wiese die Antwort mit 409 ab.

---

## 39. Eine Beschriftung für das Auge und für das Vorlesewerkzeug

*Löst [Punkt 29](#29-unter-dem-vorschaubild-steht-die-adresse-nicht-das-datum) ab.*

Unter dem Vorschaubild stand die **Adresse**, im `aria-label` desselben Knopfes der **Titel**. Zwei
Formulierungen derselben Sache, an zwei Stellen im Code, die dasselbe sagten, solange die Titel
Adressen waren. **Der Fehler war nicht die falsche Zeile, sondern dass es zwei gab.** Beide zu
berichtigen hätte ihn vertagt: Zwei Formulierungen laufen wieder auseinander, sobald jemand eine
anfasst. Es gibt jetzt eine (`kiosk/mapCaption.ts`), und beide Sinne lesen sie.

**Die Kette ist Titel, dann Adresse, dann nichts**, mit dem Jahr wo bekannt.

**„Hauptstraße Nr. ?" statt nur „Hauptstraße"**, wo die Hausnummer fehlt. Das ist kein Notbehelf,
sondern dieselbe Haltung wie beim Nichtstreuen der Stapel
([Punkt 33](#33-stapel-werden-nicht-gestreut-stufenwechsel-werden-animiert)): Die Ungenauigkeit soll
**sichtbar** bleiben, damit jemand sie behebt. Es ist genau die Lücke, nach der der Beitragsbereich
unter „Welche Hausnummer?" fragt.

**Ein Stapel zeigt nur, worin alle seine Fotos übereinstimmen.** Fotos landen auf einem Marker, weil
sie eine Koordinate teilen, und das heißt: dieselbe Adresse. Ihre Jahre und ihre Titel sind nicht
geteilt; den obersten zu nehmen schriebe einen Titel über Dutzende Bilder, die etwas anderes zeigen.
Ein Stapel fällt damit meist auf die Adresse zurück.

**Fehlt beides, fällt die Zeile weg** — kein Gedankenstrich, keine Fehlanzeige. Eine leere Stelle
unter einem Bild verlangt nichts vom Besucher.

**Die kurze Datumsform gehört ins Backend**, neben `format_label`: Sie kürzt Tag und Monat auf das
Jahr und lässt ein Jahrzehnt ein Jahrzehnt („1930er" wird nicht „1930", das erfände eine
Genauigkeit). `PhotoMarker` trägt dafür den `place_name` — die eine bewusste Ausnahme von seiner
Regel, möglichst wenig zu tragen.

**Was ausdrücklich *nicht* geschrieben wird:** ein Titel für die Fotos, deren Titel nur ihre Adresse
wäre. Der stünde zum zweiten Mal in derselben Zeile, veraltete beim ersten Nachschärfen, und er
nähme dem Kuratieren die Arbeitsgrundlage: Danach hätten alle Fotos einen Titel, und welche einen
**echten** brauchen, wäre nicht mehr zu erkennen.

---

## 40. Ein Symlink ist nie ein Datenträger

Die Suche nach Sicherungszielen (`services/backup/drives.py`) **überspringt Symlinks**, auf beiden
Ebenen, die sie durchsucht.

Der Grund ist eine Eigenheit von `os.path.ismount`: Es antwortet für einen Symlink **grundsätzlich
`False`**. Damit sieht ein Symlink unter `/media` wie ein gewöhnlicher Ordner aus, und die Suche
steigt eine Ebene hinab. Dieser Abstieg ist gewollt, denn Raspberry Pi OS hängt unter
`/media/<benutzer>/<bezeichnung>` ein — nur folgt `iterdir()` dabei dem Symlink, und was dahinter
liegt, wird als Sicherungsziel angeboten.

**Die Folge ist die schlimmste im System:** eine Sicherung, die vollständig durchläuft und im
Datenverzeichnis landet, das sie sichert. Genau davor soll die Einhängeprüfung schützen, und der Symlink
umgeht sie. Auf einem Mac tritt der Fall zuverlässig ein, weil macOS in `/Volumes` stets
einen Symlink auf `/` anlegt; auf einem Pi ist er unwahrscheinlich, aber möglich.

**Für den Test war dieselbe Falle noch einmal aufgestellt.** `_is_mounted` vergleicht Pfade, und
wörtlich verglichen ist ein Pfad hinter dem Symlink ein anderer — der Test war deshalb auch ohne die
Absicherung grün. Er vergleicht jetzt aufgelöst. **Eine Gegenprobe, die nicht ausschlägt, ist ein
Ergebnis und keine Formalie.**

---

## 41. Der Name nennt die Sache, nicht den Ort

Das Projekt heißt **Kiekmap** — plattdeutsch *kieken*, gucken. Nach aussen mit großem K, im Quelltext
und in Pfaden klein, als Präfix der Einstellungen `KIEKMAP_`.

**Ein Name für den ersten Ort wäre der schlechtere gewesen**, aus demselben Grund, aus dem nichts
Ortsspezifisches in den Code gehört: Das zweite Museum soll eine eigene `region.json` und `.env`
brauchen, keinen Fork. Ein Ortsname im Paketnamen hätte dieser Zusage widersprochen, lange bevor
jemand sie technisch verletzt hätte.

Umbenannt wurde, solange kein Pi im Feld stand und es keinen Git-Remote gab. Danach hätten Geräte,
Sicherungen auf Sticks und fremde Arbeitskopien mitgezogen werden müssen.

---

## 42. Die Wiederherstellung bringt das Schema selbst auf Stand

Eine zurückgespielte Sicherung wird migriert, und zwar von der Wiederherstellung selbst
(`services/schema.py`). Ein Neustart ist dafür nicht nötig.

**Der Grund.** Eine Sicherung bringt ihr Schema mit; getauscht wird die Datei im Ganzen, und das
laufende Programm hängt sich neu an sie. Migrationen laufen beim *Start*, und eine
Wiederherstellung ist kein Start. Ohne den Nachzug sieht das Gerät danach völlig normal aus und
**nimmt nichts mehr an**: Jeder Besucherbeitrag, jede Bearbeitung, jeder Upload endet mit HTTP 500.
Die Abhilfe stand in beiden Handbüchern — einmal neu starten —, und **eine Anweisung an Menschen ist
die schwächste Stelle, die eine Zusage haben kann.**

**Die Reihenfolge ist der ganze Punkt**, und sie hat zwei Hälften auf beiden Seiten des Tauschs:

1. **Abgelehnt wird vorher.** Trägt die Sicherung eine Revision, die dieses Programm nicht kennt,
   bricht die Wiederherstellung ab, **bevor** irgendetwas ersetzt ist. Migrieren wäre hier keine
   Option: Die zugehörigen Migrationen gibt es in diesem Programm gar nicht.
2. **Migriert wird nachher.** Erst nach dem Tausch ist die zurückgespielte Datei die am
   konfigurierten Pfad.

**Formuliert als „kennen wir diese Revision?", nicht als „ist sie neuer?".** Eine Revision, die sich
nicht einordnen lässt, ist eine, die man nicht anfassen darf — gleich ob sie aus einem neueren
Programm stammt, aus einem anderen Zweig oder aus einer Datei, die gar nicht unsere ist.

**Ein Sonderfall bleibt bewusst offen:** Eine Datenbank ohne `alembic_version` wird nicht migriert,
sondern in Ruhe gelassen. Ohne Stempel ist nicht zu sagen, was die Datei ist, und Alembic finge bei
der ersten Migration gegen Tabellen an, die es schon gibt. Im Museum kann das nicht vorkommen; in
der Testumgebung schon, und genau dort wäre Migrieren falsch.

**`test_migrationen_und_modelle_beschreiben_dasselbe_schema`** baut das Schema einmal über Alembic
und einmal über `create_all` und vergleicht sie. Die übrigen Tests bauen es aus den Modellen und
können eine fehlende Migration deshalb grundsätzlich nicht bemerken.

---

## 43. Der Kopfbereich misst sich an seiner Spalte, nicht am Ansichtsfenster

Wappen und Titel bekommen ihre Größe aus der Breite der Zelle, in der sie stehen
(`container-type: inline-size` und `cqi`), nicht aus einer Medienabfrage. Der Ortsname bekommt
zusätzlich seine **Länge** mitgeteilt, weil CSS Text nicht messen kann.

**Zwei Ursachen, und die zweite war die schwerere.** Die erste ist ein Fallstrick, den man einmal
kennen muss: **In einer Medienabfrage ist `rem` immer 16 px** — die Schriftgröße des Wurzelelements,
*bevor* eine eigene Regel sie ändert. Die Schwelle lag damit anders, als sie gedacht war. Die
zweite: **Der Entwurf hatte fast keine Luft.** Auch oberhalb der Schwelle passte die Zeile nur
knapp, und bei einer bestimmten Fenstergröße brach Safari um und Chromium nicht. Die Grenze zu
berichtigen hätte den Fehler nur verschoben. **Eine Zeile, die erst beim Nachmessen passt, passt
nicht.**

**Daraus die Regel:** Wer im Kopfbereich eine Größe setzt, bezieht sie auf den Platz, der da ist,
und lässt Luft. Eine Schwelle im Ansichtsfenster ist immer eine Stelle, an der zwei Rechnungen
auseinanderlaufen können.

**Die Zusage ist begrenzt, mit Absicht.** Der Ortsname wird kleiner gesetzt, je länger er ist, aber
**nie kleiner als die Zeile darüber** — sonst stünde die Rangfolge auf dem Kopf. Wo dieser Boden
greift, bricht der Name um. Ab welcher Namenslänge das passiert, steht in
[adaption.md](adaption.md), weil es die nächste Gemeinde betrifft und nicht diese.

---

## 44. Die Blätterknöpfe stehen fest, das Bild bewegt sich

In der Detailansicht sind die Blätterknöpfe **senkrecht am unteren Rand verankert** und stehen
**waagerecht mittig unter dem Bild**. Das Bild sitzt darüber und ändert seine Höhe, die Knöpfe
nicht.

**Vorher klebten sie am Bild und wanderten mit ihm.** Zwischen einem Querformat und einem Hochformat
verschob sich der Knopf um mehr als seine eigene Höhe. Wer durch einen Stapel mit gemischten
Formaten blättert, muss ihn bei jedem Bild neu suchen; im schlimmsten Fall liegt beim nächsten
Tippen das Bild dort, wo eben noch „Nächstes" stand.

**Waagerecht bleiben sie beim Bild**, und das ist die Gegenrichtung derselben Frage: Sie gehören zu
dem, was sie ändern. Mittig im Schirm stünden sie bei einem Hochformat weit neben dem Bild.

**Die Regel dahinter:** Was der Besucher *trifft*, steht still; was er *ansieht*, darf sich bewegen.

**Der Schließen-Knopf folgt derselben Regel** und steht in der Ecke des Schirms statt am rechten
Rand des Inhalts. Er bekommt **keine** der vier Rollen aus
[Punkt 30](#30-vier-rollen-und-jede-sieht-wie-ein-knopf-aus): Die sind die Sprache des
Beitragsbereichs, und Schließen ist keine davon.

---

## 45. Woher eine Koordinate kommt, sagt nichts darüber, wie genau sie ist

Ob ein Foto zum Nachschärfen vorgelegt wird, entscheidet, **was über das Haus bekannt ist** — nicht,
aus welcher Quelle seine Koordinate stammt.

**Vorher stand dort das Gegenteil.** Die Bedingung verlangte `location_accuracy_m ==
ACCURACY_STREET_M`, liess also nur zu, was ein Kurator auf eine Straße gesetzt hatte. Begründet war
das mit einem Satz, der plausibel klingt: „Das Gerät weiß, wo der Fotograf stand, nicht was er
fotografiert hat." **Der Satz war widerlegt**
([Punkt 34](#34-der-archivordner-schlägt-die-exif-koordinate--sobald-er-eine-hausnummer-nennt)):
Die meisten EXIF-Koordinaten sind eingetragene Werte. Damit blieb eine ganze Gruppe von Fotos aus
der Frage draussen, obwohl sie genau ihr Fall ist.

**Gemeldet wurde etwas anderes**, und das lohnt das Aufschreiben: Es fehle der Knopf, *sobald das
Jahr bekannt ist*. Die Beobachtung stimmte, die Erklärung nicht — unter den Fotos mit bloßem
Straßennamen sind die mit Jahr überwiegend gerade die aus dem EXIF, und genau die schloss die
Bedingung aus. **Eine gemeldete Beobachtung ist ein Befund, ihre Erklärung eine Vermutung.**

**Was daraus für ähnliche Regeln folgt:** Eine Bedingung, die über die *Herkunft* eines Wertes statt
über seinen *Inhalt* entscheidet, trägt eine Annahme mit sich, die veralten kann, ohne dass die
Regel es merkt. Wo es geht, wird gefragt, was bekannt ist — nicht, wer es eingetragen hat.

---

## 46. Der Bestand ist JPEG, und das Rezept dafür steht fest

Ein Museumsarchiv ist gemischt: Scans als TIFF, Bildschirmaufnahmen als PNG, ein Bild von einer
Webseite als WEBP. Der Bestand führt nur JPEG, weil **ein Browser kein TIFF anzeigt** und die
Detailansicht die Originaldatei herausreicht.

**Die Einstellung ist gemessen, nicht gewählt:** **Pillow, Qualität 92, Subsampling 4:4:4,
`optimize`** — die Quantisierungstabellen des schon umgewandelt gelieferten Erstbestands. Eine Stufe
daneben stimmt keine Datei mehr überein.

**Das ist die Voraussetzung für die Dublettenerkennung.** Der Import erkennt eine Dublette am
SHA-256. Zweimal dasselbe Rezept über dieselbe Datei gibt denselben Hash; eine andere Qualität gibt
einen anderen, und beim nächsten Archivstand käme jedes vorhandene Bild ein zweites Mal herein.
Deshalb steht die Einstellung in `tools/to_jpeg.py` als Konstante und hat einen eigenen Test.

---

## 47. Ein Diff über Bytes ist kein Diff über Bilder

Ein als Differenz gelieferter Archivstand enthielt zu über einem Drittel Bilder, die schon im
Bestand standen. Der Grund: Das Museum hatte seinen Bestand durch **ExifTool** laufen lassen und
dabei die Metadatenblöcke neu geschrieben. **Dieselben Bildpunkte, andere Bytes.**

**Die Regel daraus:** Ein Datenstand, der über Bytes verglichen wurde, sagt nichts darüber, was neu
*ist* — nur darüber, was neu *geschrieben* wurde. Vor jedem Import eines gelieferten Diffs wird
deshalb über den Bildinhalt nachgezählt, in zwei Durchgängen: erst pixelgenau bei gleichen
Kantenlängen, dann grob über verkleinerte Graustufenbilder für das, was beim Neuausspielen auch die
Größe geändert hat.

**Der Abstand zwischen Treffer und Nicht-Treffer war kein Ermessen**, und deshalb ist eine Schwelle
hier vertretbar: Fast alle Treffer lagen bei einer Abweichung von exakt null, der höchste knapp
darüber — und der nächste Nicht-Treffer um mehr als eine Größenordnung entfernt.

---

## 48. Was im Titelfeld steht, ist nicht automatisch ein Titel

In der Detailansicht steht der Titel **über** der Adresse, nicht an ihrer Stelle. Ein Foto, das
„Hauptstraße 14, Museum" heißt und darunter noch einmal „Hauptstraße 14" führt, sagt eine Zeile
umsonst — und die Zeile darüber ist die auffälligste der ganzen Ansicht.

Drei Regeln im Import statt einer Bereinigung von Hand:

**Der Ordnertitel ist der Zusatz.** „14 Gasthof Petersen" ergibt den Titel „Gasthof Petersen", die
Adresse steht in `place_name`. Nennt der Ordner nur eine Nummer, bleibt der Titel **leer**.

**Die Längengrenze ist gemessen, nicht gewählt.** Von den Titeln, die das Museum von Hand gesetzt
hat, überschreitet **kein einziger 58 Zeichen**. `TITLE_MAX` steht deshalb bei **60**, und was
darüber liegt, wandert in die Beschreibung statt weggeworfen zu werden.

**Der Name der Scannersoftware gehört in kein Feld.** Anders als eine zu lange Bildunterschrift darf
er **nicht** in die Beschreibung ausweichen: Das schöbe denselben Unsinn eine Zeile tiefer, wo er im
Kiosk unter dem Bild stünde.

**Die Lehre steckt darin, warum es die Regeln brauchte.** Eine Bereinigung von Hand räumt den
Bestand auf und lässt die Ursache stehen. Solange die Ursache im Import sitzt, ist die nächste
Lieferung die nächste Bereinigung.

---

## 49. Ein Datumswort sagt, dass es ein Datum ist — nicht, wovon

*Ergänzt [Punkt 37](#37-ein-jahr-im-text-datiert-nicht-das-foto-sondern-manchmal-nur-das-haus).*

Punkt 37 verlangt ein Datumswort vor der Jahreszahl. **Das Muster allein reicht nicht:**

    ca. 1970 wurde dieses Haus abgerissen und durch ein Mehrfamilienhaus ersetzt

Das Datumswort steht davor, sauber. Nur datiert die Jahreszahl den **Abriss** — und die Aufnahme
liegt zwingend davor.

**Beide Listen werden gebraucht, und sie tun Verschiedenes.** Das Datumswort davor sagt, *dass* eine
Zahl ein Datum ist. Ein Ereigniswort dahinter — *abgerissen*, *erbaut*, *abgebrannt*, *verkauft* —
sagt, *wovon*. Der Einwand aus Punkt 37 gilt weiter, trifft aber nur die eine Richtung: **Eine
Liste, die ausschließlich ablehnt, darf unvollständig sein.** Sie lässt dann einen Fall durch, den
ein Mensch danach noch sieht; eine Liste, die etwas *annimmt*, macht aus einer Lücke eine falsche
Angabe.

---

## 50. Wer es geliehen hat und wo es lag, sind zwei Antworten

Die Herkunft nennt beides nebeneinander, durch Komma getrennt. Vorher füllte `apply_folder_meta` das
Feld nur, wenn es leer war — der Archivpfad fehlte also überall dort, wo die Datei selbst schon
etwas sagte.

**Das ist genau umgekehrt, als es sein müsste.** Wer ein Foto geliehen hat, steht in der Datei und
ist damit gesichert. **Wo es im Archiv lag, steht nur im Pfad** — und der geht mit dem Import
verloren, denn im Bestand heißt die Datei nach ihrem SHA-256. Es ist die einzige der beiden Angaben,
die sich aus dem Bild nie wiederherstellen lässt.

Das Feld bleibt, was es war: **nicht öffentlich**.

---

## 51. Ein Feld, das an seiner Grenze endet, ist abgeschnitten

Ein Bildnachweis lautete „Förderkreis für Kultur und Brauc". Das sieht nach einem Tippfehler aus und
ist keiner: **Die Zeichenkette ist genau 32 Zeichen lang**, und 32 ist die Längengrenze des
IPTC-Feldes 2:80. Das Programm, das die Datei beschriftet hat, hat an seiner Feldgrenze aufgehört,
und wir haben es unbesehen übernommen.

**Eine Angabe, deren Länge auf eine runde Zahl fällt, ist verdächtig**, und der Fall kostet nichts
nachzuzählen: Ein Blick auf die Zeichenlänge der häufigsten Werte eines Textfeldes zeigt ihn sofort.

---

## 52. Eine Vorgabe ist kein Befund

Die Umwandlung nach JPEG reichte lange nur Farbprofil und Auflösung durch. Fotos verloren dabei, was
ihre Datei über sie sagte — und trugen danach den Vorgabe-Bildnachweis der Sammlung, wo der Name
eines Fotografen hätte stehen müssen.

Der Weg dorthin ist eine Zeile im Import:

    credit=info.credit or settings.import_credit or None

Die Vorgabe aus der `.env` springt ein, wenn die Datei nichts sagt, und das ist richtig so. Falsch
wurde es, weil die Datei etwas sagte und wir es unterwegs verloren hatten. **Der Ausfall war damit
nicht sichtbar**: Das Feld war gefüllt, es sah nach einer Auskunft aus, und eine falsche
Zuschreibung ist schlimmer als eine fehlende.

**Zwei Regeln folgen daraus.** Wo ein Feld genau den Vorgabewert trägt und die Datei etwas anderes
sagt, gewinnt die Datei: Eine Vorgabe ist eine Rückfallebene, keine Aussage.

Und für alles, was Daten von A nach B trägt: **Was auf dem Weg verloren geht, fällt nur dort auf, wo
hinterher eine Lücke steht.** Wo eine Vorgabe die Lücke füllt, wird aus dem Verlust eine Behauptung.
Die Probe darauf heißt nicht „sind die Bytes mitgekommen", sondern „liest unser eigener Leser aus
der Kopie dasselbe wie aus der Quelle".

---

## 53. Das XMP des Archivs wird nicht gelesen — nachgemessen, nicht vermutet

`services/exif.py` liest EXIF und IPTC, kein XMP. Das stand als Backlogpunkt mit einer verlockenden
Aussicht: Ein großer Teil der Archivdateien trägt eine Ortsangabe in `Iptc4xmpCore:Location`.

**Vor dem Bauen wurde gemessen**, über den ganzen Archivbestand. Das Ergebnis kehrt die Erwartung
um:

| Feld | was wirklich drinsteht |
|---|---|
| `dc:creator` | „unbekannt", „Winter" — kein Fotograf |
| `dc:description` | „Gebäude", „Abriss & Neubau" — **Kategorien, keine Beschreibungen** |
| `Iptc4xmpCore:Location` | fast immer genau das, was der Ordner schon sagt |
| `photoshop:Location` | oft im Widerspruch zum ersten, meist ein stehengebliebener Stapelwert |

Der Ertrag beim stärksten Feld sind ein paar Dutzend Fotos, und ein Drittel davon trägt denselben
Wert. Der Umbau des Lesers, eine Entscheidung über zwei widersprüchliche Ortsfelder und ein
Vorlage-Weg für Hunderte Konflikte — für eine Handvoll Hausnummern, die ein Mensch ohnehin ansehen
müsste. **Das lohnt nicht.**

**Erst messen, dann bauen** heißt dabei auch, dass die Messung etwas anderes findet als das
Gesuchte: Sie fand einen Ordner, der seine Straße wiederholt (`Hörnstraße/Hörnstraße 14`) und damit
denselben Adressabklatsch erzeugte, den Punkt 48 gerade abgeschafft hatte.

---

## 54. Dubletten findet die Maschine, entscheiden muss ein Mensch

Der SHA-256 erkennt eine Kopie der *Datei*. Er erkennt nicht denselben Papierabzug, zweimal
gescannt. Gefunden wird das mit einem **Differenzhash über 256 Bit** auf den vorhandenen
Vorschaubildern; er erträgt Helligkeit, Farbstich und Verkleinerung.

**Die Schwelle ist angesehen, nicht gewählt.** Bis zu einem kleinen Abstand ist zweifelsfrei dasselbe
Bild zu sehen, bei größerem noch überwiegend. Das Signal reißt nicht ab, es wird unscharf — also ist
die Vorgabe großzügig (**40**) und ein Mensch entscheidet.

**Vollautomatisch wäre falsch, und der Beweis stand in den Gruppen:**

- Zwei Fotos derselben Grundsteinlegung standen an **verschiedenen Adressen und in verschiedenen
  Jahren**. Eines war falsch abgelegt; eine Maschine, die das größere behält, hätte die Frage nie
  gestellt.
- Bei einem Paar trägt die **kleinere** Fassung den eingebrannten Bildtext. Auflösung ist dort das
  falsche Kriterium.
- Auf einem von drei sonst gleichen Straßenbildern steht ein Lastwagen. Zwei Momente, keine
  Dublette.

**Der Umfang macht die Entscheidung leicht.** Es waren einige Dutzend Gruppen, nicht Hunderte. Eine
Vorlage-Liste dieser Länge ist in einer Viertelstunde durchgesehen; eine Automatik, die gelegentlich
das bessere Bild verliert, wäre nie wieder zu prüfen. Deshalb findet `services/similar.py` und
schreibt nichts.

**Zusammengeführt wird vor dem Herausnehmen**, nicht danach: Titel, Beschreibung, Datierung, Ort,
Bildnachweis, Schlagwörter und der Archivpfad wandern auf das behaltene Foto, soweit ihm etwas
fehlt. „Herausnehmen" heißt `status = deleted`
([Punkt 16](#16-löschen-heißt-aus-der-ausstellung-genommen-nicht-von-der-platte-entfernt)).

---

## 55. Ein Schlagwort ist kein Feld, sondern eine Menge

Alle Stapelangaben des Importformulars folgen einer Regel: **sie füllen nur, was leer ist.** Das ist
richtig, weil jedes dieser Felder genau einen Wert hält — füllen hiesse entscheiden.

**Für Schlagwörter gilt sie nicht, und die Regel umzubiegen wäre der Fehler gewesen.** Eine
Schlagwortliste hält keinen Wert, sondern eine Menge. Wer Fotos aus einem Ordner „Feuerwehr"
hochlädt, will nicht *entweder* das Stapelwort *oder* das der Datei — er will beides.

**Damit gibt es drei Quellen, und ihre Reihenfolge steht im Code:**

1. `KIEKMAP_IMPORT_TAGS` — gilt für jeden Import dieses Geräts
2. die Stichwörter aus der Datei selbst
3. das Stapelwort aus dem Formular

`add_tags` überspringt, was das Foto schon trägt, und legt einen Namen nur einmal an. Die
Reihenfolge kostet deshalb nichts.

---

## 56. Ein Jahrzehnt ist eine Datierung — „vor 1978" ist keine

Menschen datieren nicht nur mit vierstelligen Jahreszahlen: „80er Jahre", „in den 1930gern",
„Winter 63", „Foto aus der Nachkriegszeit". Ein Jahrzehnt ist kein unscharfes Jahr, sondern eine
eigene Aussage; `date_precision` kennt `decade` genau dafür.

**„Vor 1978" wird nicht übernommen, und der Grund liegt im Zeitfilter.** Er fragt auf Überlappung
ab. Ein Foto, dessen Intervall am Anfang der Zeitleiste beginnt, überlappt mit *jeder* Stellung des
Schiebers und stünde überall — schlechter als undatiert, denn undatiert legt der Beitragsbereich es
wenigstens als Frage vor. **Eine Datierung braucht beide Enden; wo eines erfunden werden müsste, ist
keine da.**

Drei Muster sind als eigene Fälle herausgekommen, alle Verwandte von
[Punkt 49](#49-ein-datumswort-sagt-dass-es-ein-datum-ist--nicht-wovon):

- **Die Jahreszahl des Archivstands.** „heute (2018) Marc Sieveking", „bis 2018 Besitzer". Eine
  solche Jahreszahl ist fast nie ein Aufnahmejahr, sondern der Tag, an dem jemand das Archiv
  gepflegt hat.
- **Das nicht ausgeschriebene Jahr.** „Notiz: Schule 78" ist dieselbe Archivnotiz wie „Notiz: 1978"
  und fiel durch, weil die Suche das zweistellige Jahr nur hinter einem Jahreszeitwort kannte. **Bei
  einer Suche nach Mustern bestimmt die Form des Musters den Befund**, nicht der Bestand — wer nur
  eine Schreibweise sucht, misst seine eigene Annahme.
- **Das Scandatum in Prosa.** „Im Januar 2020 eingescannt von einem SW-Abzug." Dieselbe Falle wie
  das EXIF-Datum eines Scans, nur in einem Textfeld statt in einem Tag — und ohne die Jahresgrenze,
  die sie dort abfängt.

---

## 57. Der Kiosk heilt sich selbst — aber nur einmal

Ein Fehler beim Rendern reißt in React den ganzen Baum ab, und übrig bleibt eine weiße Seite. Am
Schreibtisch drückt man Neu laden; im Museum gibt es nichts zu drücken. Der Leerlauf-Neustart, der
sonst jeden verfahrenen Zustand heilt, sitzt in `MapView` und geht mit unter.

Also lädt die Seite sich selbst neu. Die einzige Frage war: **wie oft.**

**Genau einmal, dann redet das Gerät.** Ein Absturz, der beim Laden wiederkommt, liesse den
Bildschirm sonst endlos flackern — schlechter als eine Meldung, die jemand lesen kann. Der Vermerk
über den letzten Versuch liegt im `sessionStorage`: Er übersteht das Neuladen und stirbt mit dem
Tab, auf dem Pi also spätestens beim morgendlichen Neustart.

**Eine rückwärts gesprungene Uhr gilt als „lange her".** Der Pi hat keine Echtzeituhr; nach einem
Stromausfall kann seine Uhr um Jahre danebenliegen. Rechnete man stur vorwärts, wäre die
Selbstheilung dauerhaft abgeschaltet — genau der Zustand, den sie verhindern soll.

**Und der Zeitgeber wird nicht aufgeräumt.** Die ordentliche Fassung hatte ein
`componentWillUnmount`, das ihn löscht, und damit tat das Ganze nichts: Nach dem Fangen baut React
den Baum von Grund auf neu und nimmt die Fehlergrenze mit. **Der Aufräumreflex ist richtig für einen
Zeitgeber, der zu einer Ansicht gehört; er ist falsch für einen, der zum Gerät gehört.**

---

## 58. Gespeichert wird UTC, hinausgeschrieben mit Marker, gelesen als Wanduhr

Alles, was dieses Programm speichert, ist UTC. Die Regel endete bisher an der Datenbank.

**Ohne Zonenmarker ist ein Zeitstempel keine Angabe, sondern eine Falle.**
`new Date("2026-08-18T19:25:21")` liest eine markerlose ISO-Zeit laut Norm als **Ortszeit**. Die
Verwaltung zeigte damit jeden Besucherbeitrag und jede Protokollzeile um den Zonenversatz zu früh,
und die Sicherungskachel konnte den Tag verschieben.

**Der Marker gehört an das Ende, das die Zone kennt.** Drei Anzeigestellen im Browser umrechnen zu
lassen hiesse, dieselbe Regel dreimal hinzuschreiben — und die vierte, die jemand später dazubaut,
vergisst sie. Ein `UtcDatetime` in `schemas.py` sagt es einmal.

**Das `exif_datetime` bekommt ihn ausdrücklich nicht**, und darin liegt die eigentliche
Unterscheidung. Es kommt aus einer Kamera oder einem Scanner; die schreiben die Wanduhr ihres
Standorts und wissen von keiner Zone. Wer ihm UTC aufstempelt, verschiebt einen Scan um zwei Stunden
und erfindet damit eine Tatsache. **Ein Zeitstempel trägt nicht nur einen Wert, sondern eine
Herkunft.**

**Dateinamen sind die Ausnahme und tragen Ortszeit.** Der Ordner `vorher-…` und der Name des
heruntergeladenen Archivs werden von Menschen im Dateimanager gelesen, nicht von einem Programm
verglichen. Wer um halb eins nachts eine Sicherung zieht, sucht das heutige Datum.

---

## 59. Eine Zahl in der Prosa ist ein Zitat oder ein Protokoll — geprüft wird die Buchführung

Die Prüfungen neben den Tests liefen nur, wenn jemand daran dachte. In [index.md](index.md) standen
zwei ausgezählte Angaben wochenlang falsch, ohne Folgen und von niemandem bemerkt.

Der naheliegende Schluss war, eine Prüfung nachzählen zu lassen. **Nachgemessen war das falsch.**
Das Muster „N Punkte" trifft in dieser Dokumentation eine Handvoll Stellen, und **keine einzige
davon darf berichtigt werden**: Mehrfach steht die alte, falsche Zahl absichtlich da, als Zitat;
mehrfach sind Punkte auf einer Karte gemeint; einmal steht in der Historie ein Satz, der an seinem
Datum stimmte.

**Eine Zahl in laufendem Text ist fast nie eine Behauptung über den Jetztzustand.** Sie ist ein
Zitat oder ein Protokolleintrag, und beide werden durch eine Berichtigung falsch. Die zwei Stellen,
die wirklich aktuell sein sollten, haben ihre Zahlen deshalb **verloren** statt eine Prüfung
bekommen.

**Was sich prüfen lässt, ist die Buchführung des Backlogs über sich selbst.** Sie ist nicht Prosa,
sondern Struktur, und sie hat eine Zusage, die entweder gilt oder nicht: Jede je vergebene Nummer
ist entweder offen oder vergriffen — keine Lücke, kein Überhang, keine zweimal.
`tools/check_numbers.py` rechnet das nach.

**Und ein Ort, an dem sie laufen.** `make check` bündelt Stil, die Prüfungen und die Tests — die
schnellen zuerst. Der Hook unter `.githooks/pre-commit` führt **nur** die Prüfungen aus und keine
Testreihe: Die Tests laufen ohnehin, vergessen werden die Prüfungen, und zusammen brauchen sie unter
einer Sekunde. Ein Hook, den man merkt, wird abgeschaltet. Er ist je Klon einzuschalten —
versioniert, aber nicht aufgedrängt.

`.github/workflows/check.yml` führt denselben Lauf bei jedem Pull Request aus. Er findet, was auf
dem Entwicklungsrechner unsichtbar bleibt: eine andere Node-Fassung, ein fehlendes venv, eine
Umgebung ohne die lokale `.env`.

---

## 60. Getestet wird, was still falsch sein kann — gerendert wird, was man sieht

Das Frontend hat **keinen einzigen Komponententest**: kein jsdom, keine Testing Library, kein
Rendern im Test. Aufgeschrieben ist das, weil ein Durchgang von aussen sonst berechtigt fragt, was
da fehlt.

**Die Regel ist nicht „Komponenten werden nicht getestet".** Sie lautet: *Jede Entscheidung wandert
in eine reine Funktion und bekommt dort ihren Test — das Rendern bekommt keinen.* Wo die Funktion
wohnt, ist gleichgültig; `PhotoLayer.test.ts` prüft `buildIndex` aus einer `.tsx`-Datei, ohne etwas
zu rendern.

**Der Grund ist derselbe wie überall hier: Geprüft wird, was *still* schiefgeht.** Eine falsch
gezeichnete Schaltfläche sieht falsch aus — dafür braucht es einen Blick, keinen Test. Ein falsch
gerundetes Jahr sieht nach nichts aus; die Karte zeigt einfach etwas anderes.

**Wo die Grenze verläuft**, zeigt der Gegenfall: Die Größe eines Kreises auf der Karte wird ebenfalls
gerechnet und bleibt trotzdem in `PhotoLayer.tsx`. Ein falscher Wert ergibt dort einen Kreis, der
falsch *aussieht*.

**Warum kein jsdom.** Es wäre ein nachgebauter Browser, und geprüft würde der Nachbau. Was am
Rendern dieses Programms wirklich schiefgehen kann, prüft jsdom ohnehin nicht: ob die Seite offline
null fremde Herkünfte anfragt, ob ein Kreis unter einem Vorschaubild mit dem Finger zu treffen ist,
ob eine Beschriftung auf dem Gerät lesbar bleibt. Das erste ist ein Einzeiler in den
Entwicklerwerkzeugen, das letzte braucht einen Menschen vor dem Bildschirm.

---

## 61. Ein Paket mit einem Einstiegspunkt — und die Tests bleiben, wie sie waren

`services/backup.py` war auf fast tausend Zeilen gewachsen und tat sechs Dinge. Jedes Stück war
begründet, die Grenzen standen sogar schon da — als Kommentarbalken.

**Die Bedingung, unter der der Umbau lohnte, war: Die Tests dürfen sich nicht ändern.** Daneben
liegt fast ebenso viel Testcode, und er ist der einzige Beweis, dass eine Umschichtung nichts
kaputtmacht. Wer ihn mit umschreibt, hat den Beweis weggeworfen und muss dem Ergebnis glauben.

Deshalb ein **Paket mit einem Einstiegspunkt**: `app/services/backup/__init__.py` reicht genau die
Namen durch,
die der Rest des Programms benutzt. Keine Importzeile in `api/`, in `watcher.py` oder in den Tests
hat sich bewegt; geändert sind nur die Stellen, an denen `monkeypatch` einen privaten Namen umsetzt.

**Was die Aufteilung ans Licht brachte:** Die Wiederherstellung setzte einen Zwischenspeicher mit
`global` zurück. Das funktioniert nur, solange beide in derselben Datei stehen — die Trennung machte
daraus eine benannte Funktion und damit aus einem stillen Zugriff eine sichtbare Handlung.

**Wer zwischen Modulen gebraucht wird, verliert den Unterstrich.** Der fehlende Unterstrich ist die
Auskunft „das benutzt jemand anderes", und der vorhandene bleibt dort, wo er stimmt.

**Die Warnung dazu:** Der Umbau gewinnt nichts, was ein Besucher merkt. Wer in dieser Lage steht,
prüft zuerst, ob die Tests einen Umbau *tragen*; tun sie es nicht, ist das Aufteilen der zweite
Schritt und nicht der erste.

---

## 62. Apache-2.0 — weil das Projekt zum Übernehmen gebaut ist

Die Wahl war frei: Von den Fremdpaketen ist **kein einziges Copyleft**, gemessen an den
installierten Paketen statt an den Manifestdateien. Zur Wahl standen MIT, BSD-3-Clause, Apache-2.0,
MPL-2.0, EUPL-1.2 und die GPL-Familie.

Drei Ziele gaben den Ausschlag — andere sollen es nutzen können, Mitwirkung soll möglich sein, der
Name soll mitgehen —, und ein Vorbehalt: Sorge vor rechtlichen Auseinandersetzungen.

**Ausschlaggebend war §4.2.** Dieses Projekt ist ausdrücklich dafür gebaut, dass ein zweites Museum
es übernimmt. Apache verlangt, dass **geänderte Dateien als geändert gekennzeichnet** werden. Eine
Übernahme, die schiefgeht, bleibt damit sichtbar eine Übernahme und nicht „Kiekmap". MIT gibt das
nicht her.

**§5 erledigt die Beitragsfrage, bevor sie entsteht.** Beiträge stehen ohne weitere Vereinbarung
unter derselben Lizenz. Bleiben sie aus, hat es nichts gekostet.

**§4.1 und §4.4** verlangen Copyright-Vermerk *und* NOTICE-Datei bei jeder Weitergabe. Mehr
Namensnennung gibt eine permissive Lizenz nicht her.

**Was nicht den Ausschlag gab, obwohl es so aussieht:** die ausführlichere Freizeichnung in §§7–8.
Sie liest sich beruhigender als MITs zwei Sätze, bewirkt in Deutschland aber kaum mehr — § 276
Abs. 3 BGB und das AGB-Recht begrenzen beide gleich. Was das Risiko klein hält, ist die
Unentgeltlichkeit, nicht die Klausel. Der Patentgrant in §3 ist hier gegenstandslos; sein Wert liegt
darin, die Frage gar nicht erst zu haben.

**Verworfen:** **MIT** fehlen genau die drei Paragrafen oben. **BSD-3-Clause** schützt den Namen nur
gegen Werbung, nicht gegen Verwechslung. **MPL-2.0** und **EUPL-1.2** wären vertretbar; die EUPL ist
international so unbekannt, dass sie eher abschreckt, als Beiträge einbringt, und das Ziel war
Verbreitung, nicht Rückfluss. **GPL/AGPL** erschweren einer Einrichtung genau das, was hier erwünscht
ist.

**Eine Lizenz für alles**, Code wie Dokumentation. Getrennt wäre genauer — Code-Lizenzen reden von
„the Software" und von Patenten, was auf Prosa schief liegt —, verschafft aber niemandem mehr
Rechte: Eine permissive Lizenz über dem ganzen Repo erlaubt das Kopieren und Anpassen der Doku
bereits.

**Was die Entscheidung ausdrücklich nicht berührt: den Fotobestand.** Eine Softwarelizenz
lizenziert das Programm, nicht die Daten. Das steht samt der ODbL-Frage in
[licensing.md](licensing.md).

---

## 63. Die Historie wird nicht aufgeteilt, sondern erschlossen — über ihr Datum

*Ergänzt durch [Punkt 68](#68-die-sprachgrenze-verläuft-nach-publikum-nicht-nach-dateityp): Die
Datei ist seit dem 30. August 2026 abgeschlossen. Aufgeteilt wurde sie weiterhin nicht; sie wächst
nur nicht mehr.*

Die Frage war, ob `history.md` aufzuteilen ist — nach Jahr, nach Thema — oder ob eine Datei, die
niemand von vorn liest, lang sein darf.

**Nachgemessen war die Länge nicht das Problem.** Rund neunzig Abschnitte mittlerer Länge, alle in
einer Reihenfolge, die nie umsortiert wird. Eine Aufteilung nach Thema würde das Einzige zerstören,
was diese Datei voraushat: **die Reihenfolge.** Und sie brächte bei jedem Anhängen eine Frage mit,
die es heute nicht gibt — *in welche Datei?* —, deren falsche Antwort niemandem auffällt.

**Das Problem war ein anderes, und es war messbar:** Von den Verweisen aus anderen Dateien auf
`history.md` zeigte **fast keiner auf einen Anker**, jeder also auf die ganze Datei. Ein Verweis,
der nichts eingrenzt, ist kaum ein Verweis.

**Also erschlossen statt zerteilt:** ein Register am Anfang, eine Zeile je Abschnitt mit Datum und
Sprungmarke. **Das Datum ist der Eingang, nicht der Titel** — gesucht wird ein Tag, selten eine
Überschrift; für ein Stichwort ist `grep` das bessere Werkzeug.

**Damit steht eine Zusage, und sie hat eine Prüfung:** *Jeder Abschnitt nennt sein Datum in den
ersten Zeilen darunter.* `tools/build_register.py` erzeugt das Register und **bricht ab**, wenn ein
Abschnitt kein Datum nennt: Ein Register, das einen Abschnitt still auslässt, ist schlimmer als
keins.

**Eine Regel über Datumsangaben, ohne Ausnahme:** Ein Abschnitt erbt das Datum seines Teils, und ein
Teil, der keins nennt, gibt keins weiter.

**Verworfen: das Datum aus Git zu ziehen.** Es wäre eine Messung statt einer Behauptung, misst aber
das Falsche. Git datiert das Aufschreiben, nicht die Arbeit, und ein umgeschriebener Verlauf
verschiebt alle Datumsangaben auf einmal.

---

## 64. Die Umlautregel gilt für die Dokumentation — und wird jetzt geprüft

Die Sprachregelung sagt: Umlaute werden in Texten für Menschen normal geschrieben und nur im
Quelltext umschrieben. Die Dokumentation hielt sich nicht daran, und die Frage war, ob die Regel der
Praxis folgen soll.

**Nein — gemessen war es nicht die Praxis, sondern zwei Dateien.** Fast alle Dokumente halten die
Regel makellos ein; die Drift saß in `decisions.md` und `history.md`, dort nicht einmal gleichmäßig,
sondern in einer Strecke Arbeit, in der die Regel für Quelltext auf die Dokumentation übergriff.
**Eine Regel, die elf Dateien trägt, wird nicht wegen zweier aufgegeben.** Dasselbe gilt für `ß`:
Die Regel erlaubt `ss` ausdrücklich, aber nicht *im selben Absatz wie das Gegenteil*.

**Der eigentliche Fund: `tools/language_check.py` prüfte das nie**, obwohl
[development.md](development.md) direkt unter dem Umlaut-Absatz sagte, es tue das. Das Werkzeug las
nur `.py`, `.ts` und `.tsx`. **Eine Zusage, die niemand nachrechnet, ist keine Regel, sondern eine
Absicht.**

**Drei Dinge sind ausgenommen:** umzäunte Blöcke und Codespannen, weil dort Bezeichner und
Kommandos stehen; und Zitiertes, weil CLAUDE.md eine umschriebene Meldung als eigenes Beispiel der
Regel führt. Die Liste der gesuchten Formen ist mit Absicht kurz — sie läuft im Commit-Hook, und
eine einzige Fehlmeldung genügt, damit jemand die Prüfung abschaltet.

---

## 65. Die fünf Dateien einer Veröffentlichung, und was in ihnen nicht steht

`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS` und Meldungsvorlagen unter
`.github/`. Zwei Entscheidungen darin sind keine technischen.

**Keine Adresse im Klartext.** Eine E-Mail in `SECURITY.md` wird abgegriffen und steht danach in
jedem Fork und jedem Archiv, auch wenn sie hier längst gelöscht ist. Sicherheitsmeldungen laufen
deshalb über die private Meldung bei GitHub — der Weg ist nicht öffentlich, geht nur an den
Betreuer, und er taugt zugleich als der eine vertrauliche Kanal, den auch der Verhaltenskodex
braucht. **Den Schalter dafür gibt es nur auf öffentlichen Repos**; solange das Repo privat war,
zeigte der Meldeweg ins Leere.

**Kein Contributor Covenant, sondern fünfzehn Zeilen in der Stimme des Projekts.** Der Covenant ist
der erkannte Standard, und der Wechsel steht als nächster Schritt im Kodex — aber heute gibt es hier
keine Gemeinschaft und keinen zweiten Betreuer. Ein Kodex, der Verfahren beschreibt, die niemand
durchführt, ist eine Zusage ohne Deckung.

**Das Leitmotiv aller fünf: eine Veröffentlichung darf keine stille Zusage werden.** Deshalb steht
in `CONTRIBUTING.md`, dass es einen Betreuer nebenher gibt und eine Meldung Wochen liegen bleiben
kann, und in `SECURITY.md` eine Liste dessen, was **kein** Fund ist, sondern Entwurf: die
Besucheransicht ohne Anmeldung, der Beitragsweg ohne Ratenbegrenzung, der unverschlüsselte Bestand.

---

## 66. Zwei Branches — `main` sagt, was im Museum läuft

Zur Wahl stand **GitHub Flow**: genau ein langlebiger Branch, `main` jederzeit auslieferbar.
**Gewählt wurde ein zweiter langlebiger Branch**, `develop` für den Alltag und `main` für den
ausgelieferten Stand.

**Der Grund liegt im Gerät, nicht im Geschmack.** GitHub Flow ist für Dienste gebaut, die mehrmals
täglich ausliefern. Dieses Gerät steht offline und wird ein- bis zweimal im Jahr vom USB-Stick
aktualisiert; zwischen zwei Aktualisierungen liegen Monate Arbeit. Ein eigener `main` beantwortet
eine Frage, die im Museum wirklich gestellt wird — *was läuft eigentlich auf dem Gerät?* —, und zwar
als Branch, gegen den sich diffen lässt, statt als Tag, den man erst kennen muss.

**Kein `release/*`, kein `hotfix/*`.** Bei einem Betreuer ist das Aufwand ohne Gegenwert.

**Squash-Merge ist abgeschaltet, und das ist die eigentliche Entscheidung.** `history.md` zitiert
**Commits einzeln, mit Hash**, an Dutzenden Stellen — ein Squash vernichtet genau die, und er
liefert **keine** Zuordnungstabelle, mit der sich die Zitate nachziehen liessen.

**Gemerged wird mit einem Merge-Commit, nicht per Rebase.** Das Argument oben spricht gegen Squash,
nicht für Rebase. Ein Rebase erzeugt die Commits neu; GitHub baut sie auf dem Server, wo kein
Schlüssel liegt, und sie kommen **unsigniert** heraus. Ein Merge lässt seine Eltern unangetastet:
**Signaturen bleiben, Hashes bleiben, jeder Commit bleibt einzeln sichtbar.** Der Preis sind
Verzweigungen im Graphen; `git log --first-parent` blendet sie aus.

**Vorgabe-Branch ist `develop`**, damit Pull Requests von selbst dorthin zielen. Dass `main` dadurch
monatelang hinterherhinkt, ist kein Mangel, sondern die Aussage.

---

## 67. Eine Identität in allen Commits, und alle signiert

**Der Befund war ein Versehen, das sich wiederholte.** `user.name` und `user.email` waren nirgends
gesetzt. Git baute die Adresse deshalb aus dem Konto- und dem Rechnernamen des Macs, und ein
Rechnerwechsel erzeugte von selbst eine dritte Identität. Zwei davon sind keine Postfächer, sondern
verraten den Kontonamen und je einen Rechnernamen.

**Gewählt wurde eine eigene Projektadresse**, nicht die persönliche und nicht die
`noreply`-Adresse von GitHub. Die persönliche stünde dauerhaft in jedem Klon und jedem Archiv; die
`noreply`-Adresse enthält eine Konto-Kennung, die es vor dem Konto nicht gibt, und hätte den
unumkehrbaren Schritt an das Anlegen des Kontos gebunden.

**Signiert wird alles, auch rückwirkend** — das ist unüblich, und die Abwägung gehört deshalb
aufgeschrieben. Der naheliegendste Einwand trägt nicht: Eine SSH-Signatur hat **keinen eigenen
Zeitstempel**. Rückwirkend zu signieren behauptet also nichts nachweisbar Falsches.

**Ein Preis bleibt und ist zu kennen:** `allowed_signers` kennt `valid-after=`, und Git prüft eine
Signatur gegen das Commit-Datum. Wer diesem Schlüssel je eine Gültigkeitsspanne ab dem
25. August 2026 gibt, bekommt alles davor als ungültig gemeldet. Wer den Schlüssel wechselt, trägt
den alten also **ohne** `valid-after` weiter ein.

**Der Zeitpunkt war die eigentliche Entscheidung.** Beides kostete einen Rewrite, und ein Rewrite
ist gratis, solange es keinen Remote gibt. Am Tag danach tragen Klone, Forks und Archive die alte
Fassung weiter.

**Was es kostete, war nicht der Rewrite, sondern sein Nachlauf:** alle zitierten Kurz-Hashes in der
Dokumentation nachziehen. Beim ersten Mal lieferte `git filter-repo` eine Zuordnungstabelle; ein
`git rebase --root --exec` liefert keine. **Das ist die Rechnung, die auch gegen Squash-Merge
spricht** ([Punkt 66](#66-zwei-branches--main-sagt-was-im-museum-läuft)).

---

## 68. Die Sprachgrenze verläuft nach Publikum, nicht nach Dateityp

Deutsche Dokumentation stand neben englischen Bezeichnern, deutschen Tests, deutschen Commits und
einer englischen Repo-Beschreibung. Der Mix war kein Konzept, sondern ein Rückstand: Jede Datei
bekam ihre Sprache, als sie entstand.

**Die Regel lautet jetzt: Jeder Text existiert genau einmal, in der Sprache seiner Leser.** Nicht
übersetzen, sondern trennen. Die Sprachkarte steht in
[development.md](development.md#language).

**Warum nicht zweisprachig.** Doppelter Inhalt in zwei Sprachen ist die teure Fehlerart: Die
zweite Fassung veraltet, und niemand merkt es. Bei einem Betreuer nebenher ist das keine Prognose,
sondern eine Gewissheit. Genau daran scheitern mehrsprachige Wikis, und das war der Anlass der
Frage.

**Warum die Museumsdoku deutsch bleibt.** Das Produkt ist deutsch — Oberfläche, CLI, Verwaltung.
Ein nicht deutschsprachiges Museum kann Kiekmap heute nicht betreiben; `usermanual`, `operations`
und `adaption` haben also kein englisches Publikum. Englisch im Entwicklerteil macht das Projekt
nicht international. Es macht es lesbar für die, die den Code lesen.

**Warum die Tests deutsch bleiben.** Ein Testname ist hier ein Spezifikationssatz, kein
Bezeichner: `test_scandatum_datiert_das_foto_nicht` sagt in einer Zeile, welche Zusage der Test
schützt. Dazu haben die Fachbegriffe — Flurname, Hausnummer, Ortsteil — kein gutes englisches
Äquivalent.

**Warum Issues deutsch werden.** Die Fachlichkeit ist deutsch, und wer hier meldet, meldet aus
einem deutschen Museum. Das steht so in [CONTRIBUTING](../CONTRIBUTING.md), zusammen mit dem Satz,
dass Code, Commits und Entwicklerdoku englisch sind. Ungewöhnlich, aber kohärent.

**Kein Simplified Technical English.** Geprüft und verworfen: Sein kontrolliertes Vokabular ist
für Wartungsanleitungen gebaut und schneidet genau die Nuance ab, die
[decisions.md](decisions.md) und [development.md](development.md) tragen. Stattdessen gelten
Schreibregeln für beide Sprachen — ein Gedanke pro Satz, Aktiv, kein Hedging, keine Bildsprache.
Sie stehen in [CLAUDE.md](../CLAUDE.md#writing-rules).

**Was die Regel prüfbar macht:** `tools/language_check.py` hat statt einer Prosaliste zwei,
`GERMAN_PROSE` und `ENGLISH_PROSE`. Die deutsche Hälfte wird auf umschriebene Umlaute geprüft, die
englische auf deutsche Absätze. Eine Datei in Umstellung steht in keiner der Listen — sie ist halb
das eine und halb das andere, und beide Prüfungen hätten recht. Eine Liste mit einem Schalter
täte es nicht: Eine englische Datei besteht die Umlautprüfung aus dem falschen Grund, weil sie
nichts Deutsches hat, das umschrieben sein könnte.

**Commit-Nachrichten sind seit dem 30. August 2026 englisch.** Alle davor bleiben deutsch. Sie umzuschreiben
hieße, jeden Hash zu verschieben, den die Dokumentation zitiert — dieselbe Rechnung wie bei
Punkt 66, und diesmal ohne Gewinn.

**Was folgt, und was ausdrücklich nicht:** `history.md` wird eingefroren statt übersetzt; ein
schlanker englischer Nachfolger tritt daneben. `decisions.md` wird erst gekürzt, dann übersetzt.
Kein GitHub-Wiki: `make check` reicht nicht in ein zweites Repository hinein, und `operations.md`
beschreibt `deploy/pi/update.sh` Zeile für Zeile — heute ist eine Änderung an beidem ein Commit
und ein Review.
