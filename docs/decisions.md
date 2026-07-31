# Entscheidungen

Warum die Dinge so sind, wie sie sind. In zwei Jahren ist das die nützlichste Datei im Repo.
Neue Einträge unten anhängen, alte nicht löschen — überholte Entscheidungen bekommen den
Vermerk *Überholt durch …*.

---

## 1. Historische Fotos sind Scans — das prägt das ganze Datenmodell

**Beobachtung.** Die Fotos in einem Heimatmuseum sind eingescannte Papierabzüge. Ihr EXIF enthält
das Datum des Scans, nicht das der Aufnahme, und praktisch nie GPS-Koordinaten. Der EXIF-Import ist
also der Bonusfall, nicht der Normalfall. Die eigentlichen Daten entstehen durch Kuratoren und
Besucher.

**Folge 1: Jedes Feld trägt seine Herkunft** (`exif` / `curator` / `visitor`). Ein aus EXIF
geratenes Datum darf eine kuratierte Angabe niemals überschreiben.

**Folge 2: Datumsangaben sind unscharf.** „um 1930", „1920er", „vor dem Krieg" sind die Realität.
Statt eines Datums speichert jedes Foto ein Intervall `date_from`/`date_to` plus eine Genauigkeit
(`day|month|year|decade|unknown`). Der Zeitraum-Filter fragt auf **Intervall-Überlappung** ab.

> Der Fallstrick dabei: Bei naiver Datumsabfrage („Datum liegt zwischen von und bis") verschwinden
> genau die unscharf datierten Fotos aus der Ansicht — also die interessanten. Das passiert still,
> ohne Fehlermeldung. Deshalb gibt es dafür einen eigenen Test.

**Folge 3:** Der „Hilf mit"-Bereich ist keine Spielerei am Rand, sondern der Hauptweg, auf dem das
System an Orte und Daten kommt.

---

## 2. Bilder im Dateisystem, Metadaten in SQLite

**Entscheidung.** Originale und Thumbnails liegen als Dateien unter `data/`, alles andere in einer
SQLite-Datei daneben.

**Warum nicht Bilder in die Datenbank?** Thumbnails sollen billig und direkt ausgeliefert werden,
die Datenbankdatei soll klein und schnell zu sichern bleiben, und im Notfall muss ein Kurator mit
einem gewöhnlichen Dateimanager an die Originale kommen. Eine 20-GB-BLOB-Datenbank erfüllt keinen
dieser Punkte.

**Warum SQLite und nicht Postgres?** Ein Gerät, ein Prozess, einige tausend Datensätze, und Sichern
soll „eine Datei kopieren" heißen. Postgres wäre hier reiner Betriebsaufwand.

---

## 3. Dateinamen sind der SHA-256 des Bildinhalts

```
data/photos/a3/f2/a3f29c…e81b.jpg
data/thumbs/240/a3/f2/a3f29c…e81b.webp
```

Eine Entscheidung, die vier Probleme auf einmal löst:

1. **Keine Namenskollisionen.** Zwei Dateien `Kirche.jpg` aus verschiedenen Quellen stören sich nicht.
2. **Duplikaterkennung gratis.** Der Hash ist `UNIQUE`; ein zweiter Import derselben Datei wird
   abgewiesen und im Import-Log vermerkt, statt eine Dublette anzulegen.
3. **Beliebig cachebar.** Gleicher Name heißt garantiert gleicher Inhalt, also `immutable`-Header.
4. **Inkrementelle Sicherung gratis.** Liegt der Name schon auf dem USB-Stick, ist es dasselbe Bild
   und wird übersprungen. Die zweite Sicherung dauert Sekunden statt Minuten — bei ehrenamtlichen
   Helfern der Unterschied zwischen „mache ich" und „mache ich später mal".

Der ursprüngliche Dateiname bleibt als `original_filename` erhalten. Er ist oft die einzige
inhaltliche Information, die mitkommt (`Kirchweih_1932_Muehle.jpg`).

Die zweistufige Verzeichnisaufteilung (`a3/f2/`) hält die Ordner klein. Bei einigen tausend Dateien
noch egal, bei Wachstum spürbar.

*Offen für später:* Perceptual Hash gegen inhaltlich gleiche, aber unterschiedlich zugeschnittene
Scans. Der SHA-256 erkennt die nicht.

---

## 4. Offline-Karte: PMTiles + MapLibre GL

**Entscheidung.** Eine einzige `map.pmtiles`-Datei mit Vektorkacheln der Region, gebaut aus dem
öffentlichen Protomaps-Tagesbuild, angezeigt von MapLibre GL JS.

**Warum das den Tileserver überflüssig macht:** PMTiles ist ein Format, aus dem der Browser einzelne
Kacheln per HTTP-Range-Request liest. nginx kann das für eine statische Datei von Haus aus. Damit
entfällt eine ganze Komponente aus dem Betrieb.

**Warum Vektor statt Raster:** scharf bei jedem Zoom auch über die gebaute Zoomstufe hinaus,
deutlich kleiner, und Beschriftungen und Farben sind im Stil anpassbar statt eingebrannt.
Preis dafür ist WebGL — auf Pi 4/5 unproblematisch, auf einem Pi 3 wäre Raster die bessere Wahl.

**Der Fallstrick, der Offline-Karten still zerbricht:** Der Protomaps-Stil verweist für
Beschriftungen (Glyphen) und Symbole (Sprites) standardmäßig auf `protomaps.github.io`. Kacheln
kämen dann lokal, Schrift und Symbole aber gar nicht — und das fällt erst auf, wenn das Gerät ohne
Netz im Museum steht. `make tiles` lädt beides deshalb mit herunter (~14 MB) nach
`frontend/public/basemaps/`, und der Stil zeigt auf diese lokalen Pfade.

Zwei Details, die dabei Zeit kosten, wenn man sie nicht kennt:

- Die **Sprite-URL muss absolut sein**, MapLibre lehnt relative Pfade ab. Sie wird deshalb aus
  `window.location.origin` gebaut, damit derselbe Bau unter localhost und auf dem Pi funktioniert.
- Die Glyphen-URL darf relativ bleiben.

Geprüft wird das nicht durch Hinsehen, sondern mit einer Zählung: die Seite darf **null** Anfragen
an eine fremde Herkunft absetzen (`performance.getEntriesByType('resource')`).

**Ortssuche ohne Internet:** Aus demselben Extrakt entsteht per Skript eine `places.json`
(Straßennamen, benannte Gebäude, Fluren, Gewässer), die beim Start in die `places`-Tabelle geht.
Das ersetzt Nominatim für den einen Zweck, den wir haben.

Die `.pmtiles`-Datei gehört nicht ins Repo. Versioniert wird das Bauskript und die Bounding Box in
`tiles/region.json`; die Datei selbst ist ein Release-Artefakt.

---

## 5. Besucherbeiträge werden direkt übernommen — mit vollständigem Protokoll

**Entscheidung.** Was ein Besucher im „Hilf mit"-Bereich angibt, steht sofort in den Metadaten und
erscheint sofort auf der Karte. Zusätzlich wird jede Änderung in der Tabelle `changes` protokolliert
und ist im Admin einzeln zurücknehmbar.

**Warum nicht Moderationsqueue?** Der Reiz für den Besucher ist der unmittelbare Effekt — „mein
Wissen ist jetzt Teil der Karte". Eine Warteschlange nimmt genau das weg und erzeugt zusätzlich
Arbeit für Ehrenamtliche, die ohnehin knapp ist.

*„Sofort auf der Karte" heißt auch: sofort zu sehen.* Das war eine Weile nur die halbe Wahrheit —
der Beitrag stand in der Datenbank, aber die Karte lud erst nach, wenn jemand sie verschob.
Ausgerechnet die älteren Besucher, für die der Bereich gebaut ist, tun das nicht. Ein Beitrag
stößt deshalb im Kiosk-Store ein Nachladen an (`useKiosk.refresh()`), Marker und Histogramm
zusammen. Die Zeitraumauswahl des Besuchers bleibt dabei unangetastet.

Drei Dinge fangen den Missbrauchsfall auf, ohne den Normalfall auszubremsen:

1. **Nur leere Felder dürfen gefüllt werden** (sonst HTTP 409 mit freundlichem Text). Was ein
   Kurator gesetzt hat, ist unantastbar — und der zweite Besucher kann den ersten nicht
   überschreiben.
2. **Koordinaten müssen in der Region liegen.** Der Pin lässt sich zwar nur auf der Karte setzen,
   aber die API ist erreichbar; ein Foto im Pazifik wäre aus der Ansicht verschwunden, ohne dass
   jemand merkt, warum. Geprüft wird gegen `data/region.json`, das `make tiles` mit ablegt.
3. **Jede Änderung steht in `changes`** mit Sitzungskennung und ist einzeln zurücknehmbar.

Die Sitzungskennung ist eine Zufallszahl pro Seitenaufruf, nirgends gespeichert. Der Kurator kann
damit sehen, ob zehn Angaben von einer Person stammen oder von zehn — mehr soll er nicht können.

**Jahrzehnt vor Jahr.** Die Datumseingabe fragt erst das Jahrzehnt, dann optional das Jahr. Das ist
nicht Bequemlichkeit, sondern entspricht der ehrlichen Antwort: Wer ein altes Foto sieht, weiß
meist „die Zwanziger", nicht „1924". Eine Zahlentastatur würde eine Genauigkeit verlangen, die
niemand hat. „Ganze 1920er Jahre" ist deshalb ein vollwertiges Ergebnis und kein Ausweichen —
gespeichert als Intervall, gefunden über die Überlappungsabfrage.

---

## 6. Betrieb: Pi OS Lite + cage + Chromium, Anwendung in Docker

**Kiosk-Unterbau.** Raspberry Pi OS **Lite**, also ohne Desktop, dazu `cage` — ein winziger
Wayland-Compositor, dessen einzige Aufgabe es ist, genau ein Programm im Vollbild anzuzeigen.

**Warum kein Desktop?** Auf einem Desktop muss man Bildschirmschoner, Energiesparen, Update-Hinweise
und Autostart-Eigenheiten einzeln zähmen, und beim Booten blitzt der Hintergrund auf. Mit cage gibt
es nichts, was in den Vordergrund kommen könnte. Boot in ~20 s direkt in die Karte.

**Warum die Anwendung trotzdem in Docker?** Reproduzierbarkeit und ein Update-Weg, der auch offline
funktioniert: `docker save`-Tarball auf einen Stick, `update.sh`, fertig. Versionen sind über
Image-Tags nachvollziehbar statt über den Zustand eines gewachsenen Systems.

**Startreihenfolge.** Der Kiosk-Dienst wartet auf `/api/health`, bevor Chromium startet — sonst
begrüßt das Museum seine Besucher morgens für ein paar Sekunden mit einer Fehlerseite.

---

## 7. Admin: aufs Wappen tippen, dann PIN

**Entscheidung.** Ein Klick auf das Ortswappen über der linken oberen Ecke der Karte öffnet ein
Zahlenfeld mit großen Tasten. Danach der Admin-Bereich, mit ablaufender Sitzung.

**Warum sichtbar statt versteckt?** *Geändert in Stufe 8.* Ursprünglich war ein drei Sekunden
langer Druck auf die untere linke Bildschirmecke vorgesehen — unsichtbar für Besucher. Dagegen
sprach beim Bauen zweierlei: Das Schloss ist die PIN, nicht das Versteck; und eine unsichtbare
Geste ist genau das, was Ehrenamtliche vergessen, die zweimal im Jahr hier hineinmüssen. Wer aus
Neugier auf das Wappen tippt, sieht ein Zahlenfeld und tippt „Zurück zur Karte" — das ist der ganze
Schaden. Das Wappen gehört ohnehin an einen Museumskiosk.

**Warum PIN statt Passwort?** Die Eingabe erfolgt mit dem Finger auf einem Touchscreen, oft von
älteren Menschen. Ein Zahlenfeld mit großen Tasten ist dafür ungleich besser als eine
Bildschirmtastatur. Für ein Gerät, das ohnehin im verschlossenen Museum steht, ist eine PIN mit
Verzögerung nach Fehlversuchen angemessen.

**Warum überhaupt am Gerät und nicht nur vom Laptop?** Weil der USB-Stick für die Sicherung im Pi
steckt. Alles andere wäre umständlich.

**Was eine vierstellige PIN trägt, ist die Sperre, nicht die Länge.** Zehntausend Möglichkeiten
hätte ein Skript in Sekunden durchprobiert. Nach fünf Fehlversuchen sperrt das Gerät eine Minute —
das streckt denselben Angriff auf gut zwei Jahre. Der Hash ist PBKDF2 mit 200 000 Runden, damit
auch ein gestohlener `.env`-Eintrag nicht in Minuten zurückgerechnet ist.

**Sitzungen liegen im Arbeitsspeicher, nicht in der Datenbank.** Ein Neustart des Dienstes beendet
damit jede Sitzung — auf einem Gerät, das jeden Morgen in den Kiosk bootet, ist das die billigste
Garantie, dass keine Anmeldung die Nacht übersteht. Gezählt wird in verbleibenden Sekunden statt in
Zeitpunkten: Der Pi hat keine Echtzeituhr und kein Netz, seine Wanduhr kann nach einem Stromausfall
um Jahre danebenliegen.

---

## 9. Bearbeiten: fehlendes Feld heißt „lassen", leeres Feld heißt „löschen"

**Entscheidung.** Der Metadateneditor unterscheidet zwischen einem Feld, das gar nicht mitgeschickt
wird, und einem, das ausdrücklich leer ist. Ersteres bleibt unverändert, letzteres wird gelöscht.
Im Backend trägt das `model_fields_set` von Pydantic, in der Oberfläche das leere Jahresfeld.

**Warum.** Ohne diesen Unterschied könnte eine falsche Datierung nur durch eine andere ersetzt
werden, nie durch „weiß man nicht". Genau das ist aber der häufige Fall: Jemand merkt, dass 1932
nicht stimmen kann, weiß aber nicht, was stimmt. Kann er die Angabe herausnehmen, gilt das Foto
wieder als undatiert — und landet im „Hilf mit"-Bereich, wo es der nächste Besucher beantwortet.
Das ist der Unterschied zwischen einer Datenbank, die sich selbst korrigiert, und einer, in der
sich Fehler festsetzen.

**Zurücknehmen eines Besucherbeitrags** löscht das Feld, statt einen alten Wert wiederherzustellen
— ein Besucher darf ohnehin nur füllen, was leer war (siehe Entscheidung 5), es gibt also nichts
wiederherzustellen. Hat inzwischen jemand aus dem Team das Feld bearbeitet, wird das Zurücknehmen
verweigert: Es würde diese Arbeit mit wegwerfen.

---

## 10. Hochgeladene Fotos sind sofort in der Datenbank

**Entscheidung.** Der Stapel-Upload speichert jedes Bild beim Hochladen. Die Tabelle danach ist
eine Nacharbeitsliste, keine Warteschlange; „Übernehmen" ergänzt nur noch Titel, Jahr und Ort.

**Warum.** Andernfalls wäre ein geschlossener Browser gleichbedeutend mit vierzig verlorenen Scans
— und ausgerechnet der Moment, in dem jemand zum ersten Mal vierzig Bilder hochlädt, ist der, in
dem etwas dazwischenkommt. Was in der Liste liegen bleibt, ist nicht verloren, sondern unvollständig
und taucht damit von selbst im „Hilf mit"-Bereich auf.

Die Stapelangaben (Ort und Jahr für alle) füllen nur, was leer ist. Bringt eine Datei ein
brauchbares Datum oder GPS mit, gewinnt die Datei — die Zeile lässt sich hinterher trotzdem
einzeln korrigieren.

Hochgeladen wird **eine Datei je Anfrage**, obwohl der Endpunkt eine Liste nimmt. Nur so lässt sich
„Bild 7 von 40" anzeigen; eine einzelne Anfrage über ein Gigabyte zeigt minutenlang gar nichts.

---

## 11. Sicherung ist eine Funktion, kein Skript

**Entscheidung.** Sichern und Wiederherstellen sind Bildschirme im Admin-Bereich mit
Fortschrittsbalken und Klartext, nicht `backup.sh`.

**Warum.** Die Zielgruppe sind ältere Ehrenamtliche, die das ein- bis zweimal im Jahr tun. Ein
Shell-Skript bedeutet in der Praxis: es wird nie ausgeführt. Ein Knopf, der sagt
*„2.150 Fotos gesichert, Sie können den Stick jetzt abziehen"*, wird benutzt.

Details:

- **Ordner statt ZIP** auf dem Stick. Eine abgebrochene Sicherung ist dann teilweise brauchbar statt
  komplett wertlos, und man kann sie an jedem Rechner öffnen und die Bilder wiederfinden.
- **`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Betrieb anzuhalten.
- **Wiederherstellen** packt daneben aus und schaltet erst am Ende um; der bisherige Stand wird
  vorher beiseitegelegt. Eine abgebrochene Wiederherstellung darf den laufenden Bestand nie
  zerstören.
- **Erinnerung** statt Automatik: „Letzte Sicherung vor 34 Tagen", ab 30 Tagen rot. Es passiert
  nichts ungefragt, aber es wird auch nicht über Jahre vergessen.

*Bekannter Fallstrick:* Auf Pi OS Lite mountet nichts von selbst (udev-Regel nötig), und ein
Docker-Bind-Mount zeigt neu eingehängte Datenträger nur mit `rshared`-Propagation. Ohne das bleibt
der Stick im Container unsichtbar.

---

## 12. Die Karte ist Hintergrund, nicht Hauptsache

**Entscheidung.** Ein eigener Farb-Flavor („Papier") in den Tönen der Oberfläche, statt eines der
fünf mitgelieferten. Dazu drei Ebenen weniger und Straßen auf 80 % ihrer Breite. Alles in
[`frontend/src/kiosk/mapStyle.ts`](../frontend/src/kiosk/mapStyle.ts).

**Warum.** Die fertigen Flavors sind für Navigation gebaut: türkises Wasser, kräftiges Grün, kühles
Grau. Neben einem Bereich in Papierweiß und Sepiabraun sahen sie aus wie ein zweites Programm. Die
Regel beim Aussuchen der Farben war: **nichts auf der Karte darf so gesättigt sein wie ein Foto.**
Was auf dem Schirm Farbe hat, soll ein Foto sein.

**Was weggelassen wird**, und was ausdrücklich nicht: `pois` (Geschäfte samt Symbolen),
`address_label` (Hausnummern im Kartenbild) und `roads_shields` (Autobahnschilder). Die
Straßennamen bleiben — **auch die kleinen**: Der „Hilf mit"-Bereich sagt „Tippen Sie auf der Karte
auf die Stelle — oder suchen Sie den Straßennamen", und in einem Dorf sind die meisten Straßen
kleine. Sie zu entfernen hätte die Karte beruhigt und die Verortung erschwert.

*Fallstrick bei der Strichstärke:* Die Breiten sind Zoom-Interpolationen. Sie in `["*", breite,
0.8]` einzupacken wirkt naheliegend und wird von MapLibre abgelehnt — *„zoom expression may only be
used as input to a top-level step or interpolate expression"*. Skaliert werden deshalb die
**Stützstellen**, die Kurve bleibt, wie sie ist. Damit wandern spätere Änderungen des Flavors
weiterhin mit, statt in einer handgepflegten Kopie fremder Kartografie zu enden.

---

## 13. Verortung in zwei Schritten: Straße, dann Hausnummer

**Entscheidung.** Die Ortssuche liefert Straßen. Wer eine antippt, bekommt deren Hausnummern als
Knopfraster und darunter „Reicht so — die Straße genügt". Adressen tauchen in der freien Suche
nur auf, wenn die Eingabe eine **Ziffer** enthält.

**Warum nicht eine flache Liste?** Weil zwölf Plätze nach den Hausnummern einer Straße voll wären.
Der Lehmweg in Holm hat 139. Eine Trefferliste aus „Lehmweg 1" bis „Lehmweg 12" hätte jede andere
Straße verdrängt — und der Mühlenteich, den jemand vielleicht meinte, wäre nicht mehr darin
gewesen.

**Warum zwei Schritte gut sind, nicht nur erträglich.** Es ist dieselbe Form wie bei der
Datierung (Jahrzehnt, dann Jahr), und aus demselben Grund: Der zweite Schritt ist **überspringbar**.
Nicht jedes Haus steht in OpenStreetMap, und niemand weiß bei jedem Foto die Hausnummer. Der Pin
sitzt schon nach dem ersten Schritt auf der Straße; wer dort aufhört, hat geantwortet.

**Nebenprodukt: die Genauigkeit wird endlich benutzt.** `location_accuracy_m` gibt es seit Stufe 3
ungenutzt. Eine Straße bekommt 150 m, eine Hausnummer 15 m. Der Kurator sieht damit, worauf Verlass
ist, ohne dass jemand es dazuschreiben musste. Ein von Hand auf die Karte getippter Punkt bekommt
**keine** Angabe — wie gut jemand gezielt hat, ist nicht unsere Behauptung. Wer den Pin verschiebt,
verliert Name und Genauigkeit wieder, aus demselben Grund.

*Zwei stille Fallstricke, beide mit Test:*

- **Die Sammelschleife im Bauskript** übersprang jedes Element ohne `name`-Tag — und genau das
  haben Adressknoten. Der Adresszweig muss davor stehen, sonst läuft die Overpass-Abfrage grün
  durch und liefert null Adressen.
- **Hausnummern alphabetisch sortiert** ergibt 1, 10, 12, 1a, 2, 9. Sortiert wird nach
  (führender Zahl, Rest) — beim Lehmweg kommt „10-18" so hinter der 9 heraus, wo sie hingehört.

**Nachtrag: zwei Schritte werden bei langen Straßen drei.** Die Pinneberger Straße hat 163
Adressen, der Lehmweg 139, der Mühlenweg 78 — als Knopfraster ist das keine Auswahl mehr, sondern
eine Suchaufgabe. Zwei Kürzungen, in dieser Reihenfolge:

*Die Grundzahl vertritt ihre Buchstabenzusätze.* Jede fünfte Adresse in Holm ist eine (3a–3z am
Mühlenweg ist eine Reihenhauszeile). Räumlich fügen sie nichts hinzu: 3a und 3c liegen wenige Meter
auseinander, und die Genauigkeit steht ohnehin bei 15 m. Auf dem Knopf steht dabei immer eine
Adresse, die es wirklich gibt — die nackte Zahl, wo es sie gibt, sonst der erste Eintrag der Gruppe
(im ganzen Ort betrifft das 284 von 6174 Gruppen).

*Bleiben es zu viele, kommt ein Abschnitt davor* — „1–13", „15–24" —, dieselbe Form wie Jahrzehnt
vor Jahr. Geschnitten wird **nach Anzahl, nicht nach Zahlenwert**: Straßen sind löchrig nummeriert,
und zehn gleich große Abschnitte sind besser als einundzwanzig verschieden volle. Der Preis ist
eine gelegentlich ungewohnte Beschriftung wie „37–183" — sie benennt die Lücke, statt sie zu
verschweigen.

Bei Holms mittlerer Straße (15 Adressen, nach dem Zusammenfassen meist ein Dutzend) ändert sich
nichts: Dort bleibt es bei dem einen Schritt.

---

## 14. Die Zeitachse gehört dem Bestand, nicht dem Kartenausschnitt

**Entscheidung.** Der Zeitschieber spannt immer über die Spanne der **ganzen Sammlung** und steht
still. Die Balken darunter zeigen weiterhin, was im sichtbaren Ausschnitt liegt.

**Warum nicht mitskalieren?** Es war so gebaut, und es hatte eine Logik: Der Schieber zeigte den
Bereich, den man gerade sieht. Zwei Dinge sprechen dagegen, und das zweite ist ein Fehler.

*Erstens die Bedeutung.* Eine Achse, die sich beim Zoomen neu skaliert, ändert unter der Hand, was
dieselbe Stelle des Schiebers bedeutet. Für jemanden, der einmal im Leben davorsteht, ist ein
Bedienelement, das seine Bedeutung wechselt, nicht zu durchschauen.

*Zweitens.* Die Achse kam aus dem Ausschnitt, die Auswahl blieb bewusst stehen — nach dem
Hineinzoomen auf zwei Fotos aus den 1950ern stand die Achse auf 1950–1960 und die Auswahl auf
1920–2019. Der Auswahlbalken zeichnete sich mit `left: -300%` quer über Wappen und Titel, beide
Griffe lagen außerhalb des Bildschirms. Das passierte bei **jedem** Hineinzoomen in einen Bereich
mit weniger Jahrzehnten als der Gesamtbestand, im Museum also ständig.

**Was die feste Achse zusätzlich kann.** Eine leere Achse mit einem einzelnen Balken bei 1950 sagt
etwas, das die mitskalierende Achse verschwieg: *hier gibt es nur Fotos aus den 1950ern.*

**Der Riegel darunter.** `fraction()` in `kiosk/zeitachse.ts` klammert auf 0…1, `setTimeRange()`
zieht die Auswahl in die Achse. Selbst wenn beide je wieder auseinanderlaufen, kann kein Element
mehr aus seiner Zelle laufen. Die Regel steht als reine Funktion mit Test da, weil sie sich nicht
am Code ablesen ließ, sondern erst auf dem Bildschirm.

---

## 15. Fotos am selben Ort: ein Stapel zum Blättern, kein Fächer

**Entscheidung.** Fotos auf demselben Punkt (auf rund einen Meter genau) werden **vor** dem
Clustern zu einem Eintrag zusammengefasst. Auf der Karte stehen sie als ein Vorschaubild mit der
Anzahl in der Ecke; ein Tipp öffnet die Vollbildansicht, dort wird geblättert.

**Warum das nötig wurde.** Am Gasthof Petersen liegen acht Fotos auf identischen Koordinaten. Ab
Zoom 18 fasst supercluster nichts mehr zusammen — es wurden acht Marker exakt übereinander, von
denen nur der oberste erreichbar war. Der Weg dorthin war eine Sackgasse: Ein Tipp auf den Kreis
zoomte genau in diesen Stapel hinein. **Identische Punkte trennen sich bei keiner Zoomstufe.**

**Warum nicht auffächern?** Ein Fächer zeigte die Fotos dort, wo sie nicht sind, und bei acht
Bildern ist er dauerhaft viel Unruhe — am Kartenrand hat er zudem keinen Platz. Ein Fächer *auf
Tipp* führt außerdem einen Zustand ein, den man auch wieder verlassen muss, ohne dass etwas den
Ausweg zeigt. Zwei-Schritt-Gesten sind das, woran ältere Besucher hängenbleiben.

**Warum vor dem Clustern.** Danach zu gruppieren hätte nur unterhalb von `CLUSTER_MAXZOOM`
geholfen. So sieht supercluster gar keine Dubletten, und ein Stapel ist auf **jeder** Zoomstufe
ein Marker.

**Die Schwelle ist fünf Nachkommastellen**, also rund ein Meter. Sie trifft den tatsächlichen
Fall: Fotos aus der Ortssuche tragen exakt dieselbe Koordinate der Straße. Wer den Punkt von Hand
gesetzt hat, liegt daneben und bleibt ein eigener Marker — richtig so, denn dann *ist* es eine
andere Stelle.

**Oben liegt das zuletzt bearbeitete Foto.** Die Kartenabfrage sortiert nach `updated_at`; damit
liegt das eben verortete oder datierte Foto genau dort obenauf, wohin die Karte nach einem Beitrag
fährt.
