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

> **Fortgeschrieben durch [Punkt 26](#26-zwei-türen-in-die-verwaltung-und-keine-davon-ist-mehr-das-wappen)**
> (9. August 2026): Die Tür ist künftig der Titel, dazu ein Stift in der Detailansicht; das Wappen
> lädt neu. Alles Weitere hier — PIN statt Passwort, die Sperre, die Sitzungen im Arbeitsspeicher —
> gilt unverändert und für beide Türen.

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

**Nachtrag vom 3. August 2026: es gibt jetzt doch ein ZIP — als zweiten Weg, nicht als Ersatz.**
Ein Download über den Browser hilft dort, wo kein Stick liegt. Die beiden Gründe gegen ZIP gelten
unverändert, und deshalb sagt die Oberfläche sie: Das Archiv ist nicht inkrementell, und ein
abgebrochener Download ist wertlos.

Was den zweiten Weg trägt, ist eine Eigenschaft, die ihn an den ersten bindet: **Das Archiv ist
genau der Ordner, den auch der Stick bekommt, nur gezippt.** Wer eine ZIP-Sicherung zurückspielen
will, entpackt sie auf einen Stick und benutzt die vorhandene Wiederherstellung. Es gibt also
keinen zweiten Wiederherstellungsweg, der eigene Fehler haben könnte — und weil die Eigenschaft
leicht zu zerstören und schwer zu bemerken wäre, hält
`test_entpacktes_archiv_laesst_sich_wiederherstellen` sie fest.

Zwei Dinge waren dafür nötig und sind es beim Nachbauen wieder:

- **Das Archiv entsteht im Strom, unkomprimiert.** Auf einem Pi mit 2 GB RAM darf es nirgends
  vollständig liegen, und die SD-Karte ist genau das, wovor die Sicherung schützt. `ZIP_STORED`
  ist dabei nicht Sparsamkeit: JPEG und WebP sind komprimiert, ein zweiter Durchgang kostet nur
  Rechenzeit.
- **`proxy_buffering off` im nginx.** Mit der Voreinstellung sammelt nginx die ganze Antwort erst
  auf der Platte, bevor es das erste Byte ausliefert — bei mehreren Gigabyte auf ebenjener
  SD-Karte. Derselbe Fallstrick wie das `gzip off` bei den Kacheln.

**Der Rückweg läuft über den Eingangsordner — aber er fragt nach.** Eine ZIP-Sicherung, die dort
abgelegt wird, spielt sich **nicht** von selbst ein. Sie wird erkannt und im Sicherungsbereich
vorgelegt, mit Datum und Anzahl, wie eine Sicherung auf dem Stick.

Der Grund ist eine Eigenschaft des Ordners, die man leicht übersieht: Er tut bisher etwas
**Hinzufügendes und Folgenloses** — ein Foto zu viel darin ist ein Foto zu viel. Eine
Wiederherstellung **ersetzt den ganzen Bestand**. Beides im selben Ordner ohne Rückfrage zu
mischen, hieße: Eine versehentlich dorthin kopierte Datei tauscht die Sammlung aus, und auf einem
Kiosk fällt das wochenlang niemandem auf.

Damit fallen zugleich die drei Hindernisse weg, an denen ein Upload durch den Browser gescheitert
wäre: keine `client_max_body_size`, keine zweite Fortschrittsanzeige (der vorhandene Auftrag
reicht) und kein vierfacher Platzbedarf — das Archiv wird direkt in den Arbeitsordner entpackt,
nicht erst daneben.

Der Download authentisiert sich über ein **Einmal-Ticket**, weil ein Browser-Download keinen
`X-Admin-Token` mitschicken kann. Den Sitzungstoken in die Adresse zu hängen wäre der kurze und
der falsche Weg: Adressen landen im Verlauf, in Lesezeichen und in Proxy-Protokollen, und dieser
Token öffnet den ganzen Verwaltungsbereich.

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

**Der Riegel darunter.** `fraction()` in `kiosk/timeAxis.ts` klammert auf 0…1, `setTimeRange()`
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

## 16. Löschen heißt: aus der Ausstellung genommen, nicht von der Platte entfernt

Es fehlte ein Weg, einen Fehlscan oder ein versehentlich doppelt eingelesenes Bild loszuwerden.
Es gab nur ein Ankreuzfeld „Verstecken" im Editor — und niemand im Museumsteam sucht unter diesem
Wort nach dem Löschen.

**Gelöscht wird trotzdem nichts.** Der vorhandene Status heißt jetzt `deleted` statt `hidden`, die
Bilddatei bleibt liegen, die Datenbankzeile steht, und „Wiederherstellen" holt beides zurück. Das
ist keine Halbherzigkeit, sondern spart drei Probleme, die echtes Löschen mitbrächte:

- Der SHA-256 bleibt bekannt, ein erneuter Import erkennt die Dublette und bringt das Foto nicht
  ungefragt zurück.
- Änderungsprotokoll und Import-Protokoll zeigen weiter auf ein Foto, das es gibt.
- Die Sicherung braucht keine Sonderregel für einen Papierkorb.

Für eine ehrenamtliche Person, die zweimal im Jahr hier ist, ist der Fehlgriff damit folgenlos.

**Was daraus folgt, und das ist der eigentliche Teil der Entscheidung:** Gelöschte Fotos zählen in
keiner Kachel der Übersicht mit und stehen in keiner Liste ausser „Gelöscht" — auch nicht in
„Alle". Sonst wäre das Löschen genau dort wirkungslos, wo überhaupt jemand hinsieht, und die
beiden Arbeitslisten legten immer wieder das Foto vor, das eben jemand aussortiert hat. Jede Zahl
sagt dasselbe wie die Liste, in die sie führt.

Der Preis: Es gibt keinen Weg mehr, ein Foto nur *vorübergehend* auszublenden, ohne es „gelöscht"
zu nennen — etwa, solange die Rechtelage geklärt wird. Wer das braucht, braucht einen dritten
Status, keine zweite Bedeutung für diesen.

## 17. Der Migrationsverlauf wurde einmal zusammengefasst — und das war die letzte Gelegenheit

Am 3. August 2026 wurden die drei vorhandenen Alembic-Revisionen zu einem Anfangsschema
zusammengelegt. Der Grund ist schlicht: Es hatte nie ein Gerät Kiekmap ausgeführt. Es gab also
keine Datenbank, von der ein Migrationsweg irgendwohin hätte führen können — ein Verlauf, den
nichts nachspielen kann, ist kein Verlauf, sondern Ballast. Mit ihm verschwand nebenbei die
Migration, die einen Datenverlust verursacht hatte.

**Ab dem ersten Pi ist das nicht mehr erlaubt.** Sobald ein Museum eine gefüllte Datenbank hat,
ist die Kette der Migrationen der einzige Weg, auf dem seine Daten eine Schemaänderung überleben.
Das Zusammenfassen wäre dann kein Aufräumen mehr, sondern ein Datenverlust mit Ansage.

**Was bleiben musste, blieb:** Das `PRAGMA foreign_keys=OFF` in `alembic/env.py` ist die Lehre aus
dem Verlust und steht unverändert. Der Test, der es bewacht, hing allerdings namentlich an einer
der gelöschten Revisionen — ein Test, der mit dem Fehler stirbt, den er bewacht, ist keiner. Er
läuft jetzt gegen eine Probe-Migration unter `tests/fixtures/sample_migration/`, die an keiner
Revisionsnummer hängt und deren `env.py` die echte ausführt.

## 18. Der Beispielbestand liegt als Bilder plus JSON, nicht als Datenbankabzug

`make seed` stellt einen kleinen Fotobestand zum Entwickeln her, `make seed-save` sichert ihn.
Dazwischen liegt `seed/` — die Bilddateien unter ihren ursprünglichen Namen und eine `seed.json`
mit allem Übrigen.

Ein Datenbankabzug wäre der kürzere Weg gewesen und ist trotzdem der falsche: **Er ist wertlos,
sobald eine Spalte dazukommt**, und genau das passiert in diesem Projekt regelmäßig. Hier kostet
eine neue Spalte eine Zeile je Foto, und der Bestand muss nicht neu kuratiert werden.

Zwei Eigenschaften fallen dabei ab, die den Aufwand rechtfertigen:

- **Das Einlesen geht durch die echte Import-Pipeline.** Es erzeugt damit die Vorschaubilder,
  füllt das Import-Protokoll und prüft den Import bei jedem Lauf gleich mit.
- **Die Datei ist im Diff lesbar.** Wer eine Datierung ändert, sieht das als eine Zeile.

Was *nicht* in der JSON steht, steht mit Absicht nicht darin: SHA-256, Dateigröße, Abmessungen und
MIME-Typ werden beim Einlesen aus dem Bild gelesen. Eine Kopie davon könnte nur veralten. Der
SHA-256 ist die einzige Ausnahme und dient allein der Warnung, falls sich eine Datei seit dem
Sichern geändert hat.

**Die Lücken im Bestand sind Teil des Bestands.** Fotos ohne Jahr, Fotos ohne Ort, eines ohne
beides, ein zurückgenommener Besucherbeitrag: Ohne sie prüft der Bestand die Hälfte des Programms
nicht — der „Hilf mit"-Bereich hätte nichts vorzulegen. Wer den Bestand pflegt, muss sie erhalten;
`test_luecken_bleiben_luecken` hält fest, dass auch das Einlesen sie nicht zuschüttet.

## 19. Bildnachweis und Herkunft sind zwei Felder, weil sie zwei Leser haben

Museumsfotos brauchen eine Rechte- und Herkunftsangabe. Naheliegend wäre ein Freitextfeld gewesen;
es sind zwei geworden, und die Trennung ist der eigentliche Inhalt der Entscheidung:

- **`credit`** — der Bildnachweis, eine Zeile, steht im Besucher-Overlay unter der Beschreibung.
  „Sammlung Heimatmuseum Holm", „Foto: H. Meyer".
- **`provenance`** — von wem das Bild kam, ob es eine Leihgabe ist, ob eine Freigabe vorliegt.
  Eine interne Notiz, die den Verwaltungsbereich nie verlässt.

**Durchgesetzt wird das durch den Typ, nicht durch eine Verabredung.** Der Kiosk-Endpunkt liefert
`PhotoDetail`, und diese Klasse hat kein Feld für die Herkunft — sie kann sie also auch
versehentlich nicht mitschicken. Die Verwaltung bekommt `PhotoAdminDetail`, das davon erbt und
eines hinzufügt. Eine Regel, die nur im Kopf steht, hält der nächste Endpunkt nicht ein.

Beide sind auch gemeinsame Angabe des Stapel-Imports, neben Jahr und Ort: Eine Kiste Scans kommt
fast immer von einer Person, und keines der beiden Felder kann aus der Datei stammen — ein Scanner
weiß nicht, wer das Bild verliehen hat.

## 20. Der Import wertet aus, was die Dateien und ihre Ordner schon sagen

Bis Stufe 10 war der Import zurückhaltend: EXIF-Datum, GPS, Titel, Schlagwörter — alles andere
kam später von Hand. Beim Erstbestand für Holm ging das nicht mehr auf. 929 Fotos lagen in einer
Struktur, die selbst schon Auskunft gibt:

```
Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
Straßen/Hörnstraße/10 H Brahms/023.jpg
Straßen/Rehnaer Straße/119.jpg
```

Wer diese Ordnernamen verwirft, fragt Besucher nach dem Ort eines Fotos, dessen Adresse
danebensteht — und lässt Ehrenamtliche 929 Adressen abtippen, die schon da sind.

**Die Regeln zerfallen in zwei Schichten, und die Trennung ist der eigentliche Entwurf:**

| Schicht | Gilt für | Was sie tut |
|---|---|---|
| **Metadaten** (`import_file`) | *alle vier* Importwege | Datum, Ort, Titel, Beschreibung, Nachweis, Herkunft, Schlagwörter aus EXIF/IPTC |
| **Pfad** (`foldermeta.py`) | Eingangsordner, CLI, USB-Stick | Straße und Hausnummer aus den Ordnernamen |

Beim Hochladen im Browser gibt es keinen Pfad — dort greift nur die erste Schicht, und die
gemeinsamen Angaben der Maske kommen wie bisher darüber.

**Angeschaltet wird die zweite Schicht über den `root`-Parameter von `import_file()`** — den
Ordner, auf dem der Import gestartet wurde. Das war zuerst anders und ist die Lehre aus einem
Fehler, der 929 Fotos gekostet hat: Die Pfad-Schicht stand als eigener Aufruf bei den Aufrufern,
und der Eingangsordner — laut CLAUDE.md „der übliche Weg für das Museumsteam" — hatte sie nicht.
Straße und Hausnummer standen im Pfad und danach nirgends in der Datenbank. Aufgefallen ist es
erst an der fertigen Karte, weil die Metadaten-Schicht sauber lief: Der Bestand sah nicht kaputt
aus, nur leer.

Die Lehre ist nicht „besser aufpassen", sondern **eine Frage, die man beantworten muss statt sie
übersehen zu können**. Wer einen fünften Importweg baut, entscheidet jetzt über einen Parameter,
was die Wurzel dieser Datei ist; der Browser-Upload antwortet mit `None`, weil ein Browser keinen
Pfad schickt.

### Erst das Gerät, dann die Jahresgrenze

`exif_date_max_year` (Punkt 1 und die Kopfzeile von `exif.py`) bleibt — aber es ist ab jetzt der
**Ersatz für eine fehlende Geräteangabe**, nicht die erste Instanz. Wo eine Datei sagt, womit sie
entstanden ist, entscheidet das:

- **Scanner** (`HP Scanjet 3670`, `DIGITAL CAMERA Film Scanner`) → **kein Datum**, ganz gleich
  welches Jahr dort steht. 116 Dateien des Erstbestands, 91 davon aus einem einzigen Scanlauf
  von 2015. Unbesehen datiert lägen 91 historische Ortsbilder auf der Zeitleiste bei 2015 und
  kämen, weil sie als datiert gelten, nie zur Korrektur.
- **Kamera** (`OLYMPUS E-500`, `Panasonic DMC-GX8`) → **Datum zählt, auch nach 1990.** Die
  Grenze wäre hier eine Fehlannahme: Diese Aufnahmen *sind* von 2014 und 2018. Ohne diese
  Umkehrung käme der halbe Bestand undatiert an.
- **Keine Geräteangabe** → die Jahresgrenze entscheidet allein, wie bisher.

Geprüft wurde das, bevor es Regel wurde: Von 256 Kamerafotos sind 234 farbige Aufnahmen der
Häuser, wie sie heute stehen; die 22 fast graustufigen sind Aufnahmen bei trübem Wetter, im
Schnee und in einer dunklen Scheune — keine Reprofotos alter Abzüge. Die Umkehrung ist damit
tragfähig.

### Ein Wert, der nichts sagt, gilt als leer

`_NON_VALUES` in `exif.py` deckt jetzt zwei Quellen ab: was eine Kamera von sich aus schreibt
(`OLYMPUS DIGITAL CAMERA`), und was jemand tippt, weil ein Formular eine Antwort verlangt.
**In 82 Dateien steht als Fotograf wörtlich „unbekannt".** Übernommen stünde unter 82 Fotos im
Kiosk die Zeile „unbekannt" — schlechter als gar keine, weil sie aussieht wie eine Auskunft.

Dazu kam beim echten Lauf: `x-default` (ein Sprachmarker aus XMP), und die Reparatur doppelt
kodierter Umlaute — „August MÃ¶ller" ist „August Möller", zweimal durch die falsche Kodierung
gedreht. Beides passiert vor uns, in fremden Programmen; hier ist die letzte Stelle, an der es
noch auffallen kann.

### Die Straße erkennt der Ortsindex, nicht ein Ordner namens „Straßen"

Ein Pfadteil gilt als Straße, wenn `places` sie kennt. Das ist der Grund, warum trotz dieser
Erweiterung **nichts Ortsspezifisches im Code steht**: kein „Straßen"-Schalter, keine Liste
Holmer Straßennamen. Auf einem USB-Stick mit anderer Ablage funktioniert es genauso.

Was das Archiv kürzt, wird trotzdem erkannt — Ordner „Wiesengrund", Straße „Im Wiesengrund" —,
aber nur unter zwei Bedingungen, und beide haben im echten Lauf einen Fehler abgefangen:

1. **Genau ein Treffer.** „Deelenweg" steckt in „Deelenweg I" *und* „Deelenweg II". Geraten
   lägen fünf Fotos am anderen Ende des Dorfes, und niemand sähe es je.
2. **Jedes Wort enthält einen Buchstaben.** Der Hausnummernordner „2" unter „Achter de Möhl"
   traf die Straße „Kolonie Autal 2" — eindeutig und vollkommen falsch. Eine Zahl ist eine
   Hausnummer; nur ein Name ist eine Straße.

### Ohne Hausnummer bleibt das Foto unverortet

Die Straße ist bekannt, der Punkt trotzdem nicht gesetzt. Der Straßenpunkt sähe aus wie eine
Antwort, ist bis zu 400 m daneben — und das Foto gälte danach als verortet, käme also nie mehr
jemandem vor die Augen, der das Haus kennt. Der Straßenname wird stattdessen **Schlagwort und
Ortsbezeichnung**: Das ist dieselbe Aussage, ehrlich beschriftet, und im „Hilf mit"-Bereich steht
sie als Hilfestellung unter der Frage „Wo ist das?".

### Vorrang, wo zwei Quellen sprechen

Eine Koordinate aus den Metadaten schlägt den Ordner: Die Kamera stand dort, der Ordner ist die
Ablage von jemandem. 413 Fotos des Erstbestands tragen GPS, alle innerhalb der Region — auch
Scans, die jemand von Hand verortet hat. Umgekehrt setzt die Pfad-Schicht **nur leere Felder**.

### Was sich am Verhalten geändert hat

Der Import ist danach **nicht mehr zurückhaltend**. Das hat eine Kehrseite: Ein Foto, das der
Import betitelt, gilt als betitelt und wird nicht mehr vorgelegt. Deshalb bleibt die Prüfung auf
Nichtwerte streng, deshalb setzt die Pfad-Schicht nur leere Felder — und deshalb wandert ein
Titel von mehr als 120 Zeichen in die Beschreibung, statt als Überschrift eine Textwand zu
bilden (`TITLE_MAX`; im Archiv steht die ganze Bildunterschrift im Titelfeld, bis zu 223 Zeichen).

## 21. Kein Gemeindewappen im Repo

Über der linken oberen Ecke der Karte liegt ein Wappen — es führt die Kopfzeile an und ist
zugleich der Weg in den Verwaltungsbereich (Punkt 7). Bis zum 5. August 2026 war das
`frontend/public/logo.png` mit dem Wappen der Gemeinde Holm darin. Seitdem liegt dort ein
**Platzhalter**, gezeichnet von `tools/build_logo.py`.

Der Grund ist keine Lizenzfrage, und genau darin liegt die Falle. Ein Gemeindewappen ist nach
**§ 5 Abs. 1 UrhG ein amtliches Werk und gemeinfrei** — urheberrechtlich ist es also frei
verwendbar, und die Wikipedia-Seite zum Holmer Wappen sagt das auch so. Zwei Zeilen weiter steht
dort aber der zweite Baustein:

> „Wappen sind allgemein unabhängig von ihrem urheberrechtlichen Status in ihrer Nutzung
> gesetzlich beschränkt."

Das ist **Wappenrecht**: Ein Wappen ist ein Hoheitszeichen, seine Führung regelt die Gemeinde,
geschützt über das Namensrecht (§ 12 BGB) und die Vorschriften über Hoheitszeichen.

**Der entscheidende Satz: Ein Hinweis heilt das nicht.** Bei einer Lizenz hilft Namensnennung —
man nennt den Urheber und darf. Hier geht es um *Erlaubnis*, und die ist nicht durch eine Fußnote
zu ersetzen. Dazu kommt, dass die beiden Fälle verschieden sind:

| | |
|---|---|
| Das Museum zeigt das Wappen seines Ortes auf seinem Kiosk | in aller Regel unproblematisch |
| Ein öffentliches Repo enthält die Datei | gibt sie an jeden weiter, der klont |

Eine Erlaubnis für den einen Fall ist keine für den anderen. Und weil ein Repo seine Historie
mitliefert, hätte auch ein späteres Löschen nichts geholfen: Die Datei lag seit `e14802b` in jedem
Commit-Baum. Sie ist deshalb am 5. August 2026 aus der gesamten Historie entfernt worden — solange
das Repo noch keinen Remote hatte und der Schnitt nur die eigene Arbeitskopie kostete.

**Der Code war darauf vorbereitet**, und das ist der Grund, warum der Tausch eine Datei kostete
und keine Zeile Logik: Nirgends steht, was auf dem Bild zu sehen ist; die Beschriftung für
Vorlesewerkzeuge baut sich aus `name` in der `region.json` (`t.admin.logoLabel`). Dieselbe
Eigenschaft, die ein zweites Museum ohne Fork auskommen lässt, hat hier ein Rechtsproblem auf
einen Dateitausch reduziert.

Vorgehen für den eigenen Ort: [adaption.md](adaption.md), Abschnitt „Wappen einsetzen".

---

## 22. Der Backlog wird klassifiziert und bleibt trotzdem eine Datei

Am 8. August 2026 hat [backlog.md](backlog.md) drei Dinge bekommen, die er vorher nicht hatte:
eine **Art** je Punkt, eine **Einordnung** nach Wichtigkeit und Dringlichkeit, und eine **Nummer**.
Die Begründung für jedes der drei ist eine eigene.

**Vier Arten, weil vier verschiedene Dinge zu tun sind.** *Fehler* (etwas tut nicht, was es
zusagt), *Aufgabe* (klar umrissen, es fehlt nur die Arbeit), *Frage* (vor der Arbeit ist zu
entscheiden, was gebaut wird), *Idee* (noch nicht entschieden, ob überhaupt). Der Schnitt sitzt
dort, wo er die Arbeit ändert: Eine Aufgabe kann man an einem Nachmittag aufgreifen, eine Frage
nicht — wer sie wie eine Aufgabe behandelt, baut etwas, das anschließend zur Diskussion steht. Eine
fünfte Art („Recherche", „Wartung") wäre schon nicht mehr trennscharf gewesen.

**Wichtigkeit und Dringlichkeit sind zwei Achsen, weil sie hier auseinanderfallen.** Und zwar
sichtbar: „Abnahme auf dem ersten Pi" ist der gewichtigste offene Punkt des Projekts und trotzdem
nicht dringend, weil das Gerät fehlt. Eine einzige Prioritätsspalte hätte diesen Punkt entweder
nach oben gelogen oder seine Bedeutung kleingeredet. Damit die Einordnung nicht Geschmackssache
wird, hat jede Achse eine Definition, die in der Datei steht: **dringend** heißt, es trifft heute
jemanden oder es blockiert einen anderen Punkt; **wichtig** heißt, ohne das ist das Projekt auf
Dauer nicht das, was es sein soll.

Der Nutzen zeigte sich sofort: Die Achse hat die Reihenfolge des Projekts umgestellt. Dringend sind
nur noch die Wege, die ohne Hardware auskommen — und die Klassifizierung hat nebenbei zwei Punkte
als **Fehler** ausgewiesen, die als Ausbau geführt waren, in einer Datei, die von sich behauptete,
es sei keiner offen.

**Die Nummer wird nie neu vergeben.** Auch nicht, wenn ein Punkt erledigt ist — dann zieht sie mit
ihm in die [history.md](history.md). Der Grund ist der Zweck der Kennung: Sie soll in einem Commit,
einer Besprechung oder einem Auftrag an einen Coding-Agent auf genau eine Sache zeigen, und zwar
auch noch, wenn die Überschrift sich geändert hat. Eine wiederverwendete Nummer zeigt später auf
etwas anderes; das ist schlimmer als keine Nummer. Der Preis: Die Reihenfolge in der Datei löst
sich mit der Zeit von der Zählung. Das ist hinnehmbar — sortiert wird nach Einordnung, nicht nach
Nummer.

Diese Datei hier hält es unausgesprochen längst so: **Punkt 8 fehlt.** Er hieß „Sicherung ist eine
Funktion, kein Skript" und ging später in einer größeren Entscheidung auf; nachgerückt ist niemand.
Die Lücke stört beim Lesen nicht — eine falsche Zuordnung hätte gestört.

**Die Einordnung steht nur in der Übersichtstabelle**, nicht zusätzlich unter jeder Überschrift.
Zwei Stellen für dieselbe Angabe laufen auseinander, und welche dann stimmt, weiß niemand.

**Und es bleibt eine Datei.** Das ist die eigentliche Entscheidung, denn alles oben ist ein
Ticketsystem in Zeitlupe. Solange der Backlog eine Datei ist, liest er sich am Stück, steht in
derselben Historie wie der Code, den er beschreibt, und überlebt einen Kontextverlust eines
Coding-Agents — genau der Grund, warum auch die Pläne früher so geführt wurden. **Der Umzug lohnt,
sobald mehr als eine Person daran arbeitet oder die Reihenfolge häufiger wechselt als die
Inhalte.** Bis dahin ist die Klassifizierung die Vorstufe, nicht der Ersatz.

---

## 23. Nach einem Beitrag zählt dasselbe Foto, nicht das nächste

Wer im „Hilf mit"-Bereich eine Frage beantwortet, bekommt anschließend **dasselbe Foto mit der
anderen Frage** vorgelegt, solange dieser Frage noch etwas fehlt. Erst wenn nichts mehr fehlt,
kommt ein neues Foto.

**Der Anlass war ein Fehler, nicht eine Idee.** Der Dank sagte nach jedem Beitrag „Das Foto ist
jetzt auf der Zeitleiste" — auch dann, wenn das Foto keinen Ort hat. Dann fährt die Karte nirgends
hin (`showPhoto()` steigt ohne Koordinaten sofort aus), der Zeitschieber springt nicht, und der
Besucher liest einen Satz und sieht nichts. Bei 673 Fotos ohne Jahr und 77 ohne Ort ist das kein
Randfall.

**Die naheliegende Reparatur wäre ein vierter Satz gewesen** — „Sobald jemand weiß, wo das war,
erscheint es auf der Karte." Damit wäre die Meldung ehrlich, aber der Besucher stünde immer noch
vor einer Sackgasse, unmittelbar nachdem er bewiesen hat, dass er dieses Foto kennt. Stattdessen
wird die Lage aufgelöst: Wo etwas fehlt, fragt der Dank danach („Und wissen Sie auch, wo das
war?"), und die nächste Frage gilt demselben Foto.

**Das ist die vorhandene Regel zu Ende gedacht, keine neue.** „Weiß ich nicht" wechselt schon immer
*die Frage* und nicht nur das Bild, weil jemand, der einen Ort nicht kennt, das Jahrzehnt sehr wohl
kennen kann. Nach einem geglückten Beitrag wechselte die Frage bisher auch — nur sprang das Foto
dabei unnötig weg, ausgerechnet im ergiebigsten Moment, den der Bereich je bekommt: Der Besucher
hat gerade gezeigt, dass er dieses Bild kennt, und schaut es an.

**Es kostete keine API-Änderung.** Der Beitrag gibt das aktualisierte Foto zurück, und `PhotoDetail`
trägt `needs_location` und `needs_date` mit — der Store weiß also bereits, was noch fehlt. Die
Zähler kommen weiter aus dem regulären Abruf, nur das Foto wird ersetzt; die Zeile „Noch n Fotos
ohne Ort" bleibt damit richtig.

**Was dabei bewusst übergangen wird:** die Liste der weggetippten Fotos. Wer eins vorhin weggewischt
hat und jetzt doch etwas dazu beiträgt, bekommt es mit der anderen Frage wieder vorgelegt. „Weiß
ich nicht" bleibt der Ausweg, und die Kette endet von selbst, sobald dem Foto nichts mehr fehlt.

**Die beiden alten Sätze stehen seitdem nur noch da, wo sie stimmen.** Das ist die eigentliche
Regel hinter dem Ganzen: Eine Meldung darf nur behaupten, was die Ansicht im selben Moment zeigt.

---

## 24. Die Straße wird gewählt, nicht getippt

Der „Hilf mit"-Bereich hatte ein Suchfeld für den Straßennamen. Seit dem 8. August 2026 steht dort
eine Folge von Knöpfen: erst der Anfangsbuchstabe, dann die Straße, dann die Hausnummer. **Die
Besucheransicht hat damit kein einziges Eingabefeld mehr**, und das soll so bleiben.

**Der Anlass war die Tastaturfrage, die Antwort war, sie überflüssig zu machen.** Ein Kiosk hat
keine Tastatur; eine echte im Ausstellungsraum ist ein Gegenstand, der wegkommt und Tastenwege in
Chromium öffnet, die der Kiosk gerade zumacht. Eine Bildschirmtastatur hätte gebaut werden müssen,
denn Chromium unter `cage` blendet keine ein. Beides wäre Aufwand gewesen, um ein Bedienelement zu
retten, das es an genau **einer** Stelle gab — und das ohne Tastatur wie defekt aussieht.

Die Form war schon da: Der Zeitpunkt wird als Jahrzehnt und dann Jahr erfragt, die Hausnummer bei
langen Straßen als Abschnitt und dann Nummer. Die Straße ist dieselbe Bauform, eine Ebene weiter
vorn.

**Die Gruppen werden gerechnet, nicht aufgeschrieben.** Ein Buchstabe mit wenigen Straßen wird mit
dem Nachbarn verschmolzen, bis höchstens zehn Knöpfe bleiben; eine Gruppe mit mehr als zehn
Straßen teilt sich eine Ebene tiefer, und der Schnitt folgt dabei den Namen statt einer festen
Tiefe — die vierzehn Holmer „Am …"-Straßen kommen erst nach vier Zeichen auseinander. Für Holm
ergibt das zehn Knöpfe, von denen sieben direkt zur Straßenliste führen; A, H und I bekommen einen
Zwischenschritt. Ein zweites Museum bekommt seinen eigenen Baum, ohne dass jemand Buchstaben
abzählt.

Gruppiert wird über den **entschärften** Namen. Sonst bekäme ein „Ölmühlenweg" einen einsamen
Ö-Knopf und stünde hinter dem Z. In Holm gibt es keine solche Straße — anderswo schon, und dann
fiele es niemandem auf.

**Nicht alle Straßen stehen zur Wahl, sondern die `streetChoice` ortsnächsten.** Der Ortsindex
reicht sieben Kilometer weit und umfasst die Nachbardörfer; alle 486 Straßen in Knöpfe zu fassen
kostete eine vierte Frage, allein „Am …" hat dort 29 Einträge. Die Fotos eines Heimatmuseums zeigen
seinen eigenen Ort, und was weiter draußen liegt, wird auf der Karte angetippt — den Weg gab es
immer. (Seit [Punkt 27](#27-der-kartentipp-ist-erst-nach-ansage-scharf) kostet er einen Knopfdruck
vorher.) Eine **Anzahl** statt eines Radius, weil sie das Knopfbudget unabhängig davon hält, wie
dicht ein Ort bebaut ist.

**Der Verwaltungsbereich behält sein Suchfeld.** Dort wird gepflegt, nicht besucht, und eine
Tastatur ist zur Hand. Der Suchendpunkt bleibt deshalb, was er war.

---

## 25. Die Balken bündeln, was der Bestand hergibt

Hinter dem Zeitschieber liegen Balken, die zeigen, wo überhaupt Fotos liegen. Wie viele Jahre ein
Balken umfasst, stand bis zum 9. August 2026 fest auf zehn. Seitdem rechnet
`bar_width()` in [services/dates.py](../backend/app/services/dates.py) es aus, nach zwei Regeln.

**Erstens: nie feiner als die gröbste Datierung im Bestand.** Ein auf „1920er" datiertes Foto
trägt `date_from = 1920-01-01`. In Jahresbalken türmten sich seine zehn Jahrgänge auf dem einen
Balken 1920 — ein Turm, wo in Wahrheit ein Jahrzehnt liegt. Das ist derselbe Fehler, dessentwegen
das ganze Datenmodell mit Intervallen arbeitet (Punkt 1), nur in der Anzeige: Er sieht nicht nach
Fehler aus, sondern nach Befund. Solange jede Angabe in ein Jahr passt — tag-, monats- oder
jahresgenau — sind Jahresbalken dagegen exakt.

**Zweitens: so breit, dass die Spanne in dreißig Balken passt.** Über 130 Jahre wären Jahresbalken
eine Hecke. Gewählt wird aus 1, 5, 10, 25, 50 Jahren, damit die Beschriftung lesbar bleibt.

**Warum das nötig wurde.** Der eingelesene Erstbestand hat es gezeigt: 929 Fotos, davon 673 ohne
Jahr, und die 256 datierten stammen ausnahmslos aus Kamera-EXIF — Spanne 2010 bis 2024, also
**zwei** Jahrzehnte. Der Schieber zeigte zwei Balken, einen vollen und einen Stummel. In Jahren
zerlegt zeigt derselbe Bestand einen Ausreißer 2014 und leere Jahrgänge 2012 und 2015. Dieselben
Daten, ein anderes Bild.

**Die Höhe wird mit der Wurzel skaliert, nicht linear.** 11 Fotos gegen 245 sind linear 4,5 % —
und darunter klemmte die Untergrenze alles auf denselben Sockel, den auch ein Jahrzehnt mit einem
einzigen Foto bekam. Mit der Wurzel sind es 21 %: klar kleiner, klar vorhanden. Ein **leerer**
Balken bleibt bei null, denn nichts ist nicht wenig — ein Sockel dort schickte den Besucher an eine
Stelle, wo nichts liegt.

**Die Breite gehört der Sammlung, nicht dem Ausschnitt** — genau wie die Achse. Sonst wechselte
die Bedeutung eines Balkens beim Verschieben der Karte, und der Besucher verglich Bilder, die nicht
vergleichbar sind.

**Die Achse reicht über das letzte Jahr hinaus.** Der Balken für 2024 braucht sein eigenes Stück
Bahn; endete die Achse auf 2024, begänne er am rechten Rand und liefe darüber hinaus. Bei
Jahrzehnten fiel das selten auf — nämlich nur, wenn die jüngste Aufnahme im letzten Jahrzehnt der
Achse liegt.

---

## 26. Zwei Türen in die Verwaltung, und keine davon ist mehr das Wappen

*Entschieden und gebaut am 9. August 2026* — der Stift als Punkt 25, der Titel und das neu
ladende Wappen als Punkt 29. Diese Entscheidung schreibt
[Punkt 7](#7-admin-aufs-wappen-tippen-dann-pin) fort, der genau **eine** Tür festgelegt hatte.

**Entscheidung.** Es gibt künftig zwei Wege in den Verwaltungsbereich, beide sichtbar, beide durch
dieselbe PIN gesichert:

| Wo | Wohin |
|---|---|
| Der Titel „Bilder aus Holm" im Kopfbereich, ohne Unterstreichung | in die Verwaltung, wie bisher über das Wappen |
| Ein Stift neben dem Titel der Detailansicht | direkt in die Bearbeitung **dieses** Fotos |

**Das Wappen verliert diese Aufgabe** und bekommt eine andere: Ein Tipp darauf lädt neu und setzt
die Filter zurück.

**Warum das keine Aufweichung von Punkt 7 ist.** Was dort entschieden wurde, war nicht „genau eine
Tür", sondern **„sichtbar statt versteckt"** — gegen die unsichtbare Drei-Sekunden-Geste in der
Bildschirmecke, und mit der Begründung, das Schloss sei die PIN und nicht das Versteck. Beide neuen
Türen sind sichtbar und tragen dasselbe Schloss. Die Zahl der Türen war eine Folge dieser
Entscheidung, keine eigene: Es gab damals nur eine sichtbare Fläche, die sich dafür anbot.

**Warum die zweite Tür überhaupt.** Wer am Gerät ein falsch beschriftetes Foto sieht, hat heute
keinen kurzen Weg dorthin — er muss in der Verwaltung nach dem Foto suchen, und wonach er sucht,
ist ausgerechnet der Titel, der falsch ist. Der Stift führt ohne Umweg zu diesem einen Foto. Das
ist auch der Grund, warum es **keine sichtbare Kennung** braucht, die sich jemand notiert.

**Warum das Wappen das Zurücksetzen bekommt und nicht ein eigener Knopf.** Der Besucherschirm hat
bisher keinen Weg zurück in den Anfangszustand; es gibt drei Umwege — fünf Minuten warten, die PIN
eingeben und die Verwaltung wieder verlassen, oder den Netzstecker. Für einen Besucher, der sich
verhakt hat, ist keiner davon eine Antwort. Ein *zusätzlicher* Knopf dafür wäre allerdings ein
Knopf, den fast niemand braucht und den trotzdem jemand drückt — Kinder zuerst —, und er wirft die
Arbeit weg, die gerade jemand angefangen hat. Das Wappen kostet keine zusätzliche Fläche und ist
bereits als tippbar bekannt.

**Zur Kennung unter dem Bildnachweis.** In der Detailansicht stehen ganz unten, klein und grau,
die **ersten acht Zeichen des SHA-256**. Sie sind die Identität des Fotos unabhängig von jeder
Datenbank: Ein neu aufgebauter Bestand vergibt neue laufende Nummern, derselbe Scan behält seinen
Hash. Acht Hexzeichen sind vier Milliarden Möglichkeiten — kurz genug zum Abschreiben, eindeutig
genug für einen Museumsbestand, dieselbe Länge, die git aus demselben Grund nimmt. **Die
Verwaltungssuche findet sie**, und das ist die Bedingung, unter der sie dort stehen darf: Eine
Kennung, die sich nirgends nachschlagen lässt, wäre Zierrat.

Sie ersetzt den Stift nicht, sondern deckt den Fall ab, den er nicht kann — jemanden, der sich ein
Foto notiert und später an einem anderen Gerät danach sucht.

**Der Preis, und er ist zu nennen:** Wer das Wappen antippt, weil er in die Verwaltung will, setzt
stattdessen die Ansicht zurück. Für ein bis zwei Ehrenamtliche im Jahr ist das verkraftbar; es ist
trotzdem die eine Stelle, an der diese Entscheidung jemandem wehtut, und sie steht deshalb hier und
nicht nur im Backlog.

**Was das über die Regel „genau eine Tür" sagt.** Sie war nie das Ziel, sondern eine Zahl, die sich
ergeben hat — und sie stand danach zweimal beiläufig im Backlog als „ist fortzuschreiben", ohne
dass jemand sie fortgeschrieben hätte. Eine Entscheidung, die an zwei Stellen halb widerrufen wird,
ist an keiner Stelle mehr auffindbar. Sie gehört an eine.

---

## 27. Der Kartentipp ist erst nach Ansage scharf

Solange „Wo ist das?" steht, war **die ganze Karte scharf**: Jeder Tipp auf eine freie Fläche
setzte einen Punkt. Seit dem 9. August 2026 muss der Besucher das erst verlangen — über den Knopf
**„Auf der Karte zeigen"**. Vorher passiert bei einem Tipp auf die Karte nichts.

**Der Grund ist die Datenqualität, nicht die Sauberkeit.** Wer während der Frage nur schauen will
— die Karte verschieben, sich orientieren, ein Foto in der Nähe suchen —, beantwortete sie dabei
versehentlich. Und sobald ein Punkt stand, bot der Bereich **„Hier war das"** an: ein Tipp daneben,
ein bestätigender Tipp danach, und im Bestand stand eine Verortung, die niemand gemeint hat.

**Es ist immer nur ein Weg auf dem Schirm.** Wer die Karte scharf schaltet, dem verschwindet die
Straßenwahl; wer zurückgeht, bekommt sie wieder. Nebeneinander standen sie sich im Weg: Das
Knopfraster wirft bei der nächsten Berührung weg, was der Kartentipp gerade gesetzt hat. Der
Knopf steht deshalb **über** der jeweiligen Auswahl, nicht darunter — er ist die Alternative *zu*
ihr, und darunter läse er sich als letzter Ausweg nach dem Scrollen.

**Angeboten wird er in jedem Schritt, auch bei der Hausnummer**, und dort verdient er am meisten:
Wer die Straße kennt, die Nummer aber nicht, zeigt auf das Haus statt „Reicht so" zu drücken.
Danach ist die Nummernfrage hinfällig — ein Punkt auf der Karte sagt mehr als eine Zahl aus einer
Liste.

**Zwei Dinge bleiben unabhängig davon scharf.** Der gesetzte Punkt wird immer gezeichnet und lässt
sich immer ziehen, gleich wer ihn gesetzt hat — sonst gälte die Zusage „Der Punkt lässt sich auf
der Karte noch verschieben" für den Punkt aus der Straßenwahl nicht mehr. Im Code sind das
deshalb zwei Bedingungen und nicht eine (`armed` und `active` in `kiosk/PinLayer.tsx`).

**Ohne Ortsverzeichnis gibt es keine zweite Wahl** — dann ist die Karte von Anfang an scharf, denn
sonst wäre der Bereich unbedienbar. Das trifft eine Einrichtung, die `make places` nie gelaufen
hat. [Punkt 24](#24-die-straße-wird-gewählt-nicht-getippt) sagt, was weiter drauszen liegt, werde
„auf der Karte angetippt"; das gilt weiter, kostet jetzt aber einen Knopfdruck vorher.

**Der Schalter liegt im Store, nicht in der Komponente.** `LocationTask` wird bei fast jedem
Fotowechsel abgebaut, ein `useState` fällt dort also von selbst zurück — nur nicht auf dem einen
Weg, auf dem `load()` zur ursprünglichen Frage zurückfällt, weil die andere leergelaufen ist.
Genau dieser Fall tritt ein, wenn eine Art von Lücke abgearbeitet ist, und er hinterliesze eine
scharfe Karte über einem Foto, das der Besucher noch nicht angesehen hat.

---

## 28. Fotos ohne Jahr sind ein Schalter, keine Nebenwirkung

Ein Foto ohne Datum überlappt keinen Zeitraum. Es fiel damit aus **jeder** Auswahl heraus, sobald
der Besucher den Schieber auch nur ein Stück zusammenzog — bei diesem Bestand zwei Drittel der
Sammlung, ohne dass irgendwo gestanden hätte, dass das passieren würde. Seit dem 9. August 2026
steht neben dem Schieber ein Schalter: **„507 Fotos ohne Jahr anzeigen"**, mit Haken.

**Die Zahl stand ohnehin dort.** Sie war bisher eine Meldung; jetzt ist sie die Beschriftung einer
Handlung. Das ist der ganze Trick an der Stelle — es kommt kein Bedienelement hinzu, ein
vorhandenes bekommt einen Zweck.

**Eingeschaltet heiszt „kein Datum ODER Überlappung".** Der Zeitraum gilt dann nicht mehr für
alles, was auf dem Schirm steht. Das ist eine echte Einbusze an Genauigkeit, und sie ist
vertretbar, weil der Besucher sie sieht und sie selbst eingestellt hat. Die Gegenrichtung — der
Schalter wirkt nur, wenn ohnehin kein Zeitfilter geht — wäre eine Anzeige gewesen und kein
Schalter: Beim ersten Anfassen des Schiebers wären die Fotos trotzdem verschwunden.

**Er steht anfangs an und geht genau einmal von selbst aus** — beim ersten Zusammenziehen des
Zeitraums. Das ist der Moment, in dem die Auswahl anfängt, etwas zu bedeuten: Bis dahin hat der
Besucher nichts eingestellt, ab da schon. Der Anfangszustand zeigt also alles, was das Museum hat,
und niemand verliert etwas, ohne es getan zu haben.

**Danach gehört der Schalter dem Besucher.** Wer ihn von Hand wieder einschaltet, bei dem bleibt
er an, auch beim nächsten Zug am Schieber. Ginge er jedes Mal wieder aus, wäre genau die
Nebenwirkung zurück, gegen die dieser Punkt gebaut ist — nur eine Ebene höher und ärgerlicher,
weil sie eine Entscheidung überschriebe, die jemand gerade getroffen hat. Im Store steht dafür
ein zweiter Wert (`undatedByHand`), der nie zurückfällt.

**Wonach die Automatik greift, ist `queryTimeFilter`** — dieselbe Funktion, die entscheidet, ob
überhaupt ein Zeitfilter zum Backend geht. Damit geht der Schalter exakt dort aus, wo sonst Fotos
anfingen zu verschwinden. Eine zweite, eigene Regel dafür wäre eine zweite Wahrheit gewesen.

**Das Histogramm zählt die undatierten Fotos immer mit**, gleich wie der Schalter steht. Sonst
stünde dort nach dem Abschalten eine Null, das Etikett verschwände — und mit ihm der einzige Weg
zurück.

Der Schalter ist ein Knopf mit gezeichnetem Kästchen, kein `input[type=checkbox]`: Der ist rund
13 px grosz, die Zielgruppe braucht 48. Die Kopfzeile des Schiebers ist dadurch höher geworden;
was das für die drei Elemente der oberen Zeile bedeutet, gehört zu Punkt 29 im
[backlog.md](backlog.md).

---

## 29. Unter dem Vorschaubild steht die Adresse, nicht das Datum

Unter jedem Vorschaubild auf der Karte stand die fertige Datumsangabe. Seit dem 9. August 2026
steht dort **Adresse und Jahr**: „Lehmweg 17b — 1953", und wo kein Jahr bekannt ist, „Im Sande 18"
allein.

**Die alte Zeile war an dieser Stelle zweimal falsch.** Unter den 256 Kameraaufnahmen stand
„22. März 2014" — der Tag ist auf einer Übersichtskarte nie der Punkt. Und unter den rund 670
Fotos ohne Datierung stand „Jahr unbekannt", siebenhundertmal dieselbe Zeile: eine Fehlanzeige, die
über siebenhundert Bilder nichts sagt.

> **Nachtrag vom 12. August 2026 — dieser Punkt ist abgelöst.** Die Beschriftung nimmt jetzt
> **den Titel** und fällt auf die Adresse zurück; siehe Punkt 39 unten. Die Begründung darunter
> ist nicht falsch geworden, sondern gegenstandslos: Sie stand auf einem Bestand, in dem 815 Titel
> die Adresse daneben wiederholten und achtzehn „Intel(R) JPEG Library" hiessen. Das ist
> aufgeräumt. Was hier über **Stapel** und über die **wegfallende Zeile** steht, gilt
> unverändert weiter.

**Warum die Adresse und nicht der Titel**, obwohl der naheliegender klingt: Der Bestand hat es
entschieden. Alle 922 vorhandenen `place_name` bleiben unter dreißig Zeichen — die längste ist
„Uetersener Straße 12". 105 Titel sind länger als vierzig Zeichen, und achtzehn lauten
„Intel(R) JPEG Library, version […]". Die Adresse passt also immer unter ein Vorschaubild, der
Titel oft nicht. Dass die Position auf der Karte die Adresse schon ungefähr verrät, spricht nicht
dagegen: Auf einer Dorfkarte sieht man die Straße, nicht die Hausnummer.

**Ein Stapel bekommt die Adresse, aber kein Jahr.** Fotos landen auf einem Marker, weil sie eine
Koordinate teilen — und das heißt hier: dieselbe Adresse. Einundfünfzig Bilder von Schulstraße 2
sind alle von Schulstraße 2. Ihre Jahre sind nicht geteilt; das oberste zu nehmen setzte ein Datum
unter fünfzig Fotos, die es nicht tragen. Die Adresse wird nur behauptet, wo **alle** Fotos des
Stapels sie teilen: Zwei über EXIF verortete Aufnahmen können auf einen Meter zusammenfallen,
ohne miteinander zu tun zu haben.

**Fehlt beides, fällt die Zeile weg** — kein Gedankenstrich, keine Fehlanzeige. Eine leere Stelle
unter einem Bild verlangt nichts vom Besucher.

**Die kurze Datumsform gehört ins Backend**, neben `format_label` (`services/dates.py`), nicht als
Zeichenkettenschnipselei ins Frontend. Sie kürzt Tag und Monat auf das Jahr, lässt ein Jahrzehnt
ein Jahrzehnt („1930er" wird nicht „1930" — das erfände eine Genauigkeit) und gibt für
Undatiertes eine leere Zeichenkette.

**`PhotoMarker` trägt dafür den `place_name`, und das ist die eine bewusste Ausnahme** von seiner
Regel, möglichst wenig zu tragen. Der Preis wurde gemessen statt geschätzt: Bei fünfhundert
Markern sind das rund 13 kB, auf einem Gerät, das seine Karte aus dem Nebenzimmer bekommt. Für
alles andere gilt die Regel weiter.

**Die Beschriftung für Vorlesewerkzeuge behält das volle Datum.** Dort stört die Genauigkeit
nicht, und wer sich die Karte vorlesen lässt, hat den Marker nicht im Blick. Deshalb liefert der
Marker beide Formen.

**Der Erstbestand ist inzwischen aufgeräumt** (11. und 12. August 2026, siehe
[history.md](history.md#der-erstbestand-wird-bereinigt--und-zwei-regeln-drehen-sich-um)), und damit ist die Voraussetzung dieser Entscheidung entfallen: Die Titel
sind keine Adressen mehr. **Am 12. August ist sie deshalb neu getroffen worden** — die Beschriftung
nimmt jetzt den Titel und fällt auf die Adresse zurück; siehe Punkt 39 unten.

---

## 30. Vier Rollen, und jede sieht wie ein Knopf aus

Der „Hilf mit"-Bereich ist über mehrere Stufen gewachsen, und man sah es: zwanzig Knöpfe in fünf
Formen, ohne dass die Form gesagt hätte, was der Knopf tut. Seit dem 9. August 2026 gibt es **vier
Rollen**, und mehr sollen es nicht werden:

| Rolle | Form | Symbol | Beispiele |
|---|---|---|---|
| **auswählen** | weiß mit Rand | — | Buchstabe, Straße, Jahrzehnt, Jahr, Hausnummer, Abschnitt, „Auf der Karte zeigen" |
| **übernehmen** | gefüllt, Akzentbraun | Haken | „Hier war das", „Ganze 1920er Jahre", „Reicht so — die Straße genügt" |
| **zurück** | weiß mit Rand, graue Schrift | Pfeil links | „Anderer Buchstabe", „Anderes Jahrzehnt", „Doch nicht — von vorn", „Punkt entfernen" |
| **überspringen** | wie zurück, durch eine Linie abgesetzt | Pfeil rechts | „Weiß ich nicht — nächstes Foto" |

**Die randlose Form ist weg.** Sie war grau, ohne Rand und las sich als Text — für eine
Zielgruppe, die einmal im Jahr vor diesem Gerät steht, genau das Falsche. Leiser wird ein Knopf
jetzt über die Schriftfarbe, nicht über die Form; Rand und Höhe sind bei allen gleich, und die
gemessene Mindesthöhe liegt bei 54 px.

**Die wichtigste Grenze verlief an der falschen Stelle.** Dieselbe leise Form trug *zurückgehen*
und *überspringen* — das eine bleibt beim Foto, das andere legt es weg. „Weiß ich nicht —
nächstes Foto" sieht deshalb aus wie „Anderer Buchstabe" und ist durch eine Linie davon getrennt:
Was über der Linie steht, gehört zur Frage, was darunter steht zum Foto. Der Abstand liegt
überwiegend ausserhalb des Knopfes, damit kein mittippbarer Streifen über der Beschriftung
entsteht.

**„Reicht so — die Straße genügt" ist eine Antwort und sieht seitdem danach aus.** Es war ein
schlichter weißer Knopf, während „Hier war das" gefüllt war — obwohl beide dasselbe tun:
abschließen. Nicht jedes Haus steht in OpenStreetMap, und wer die Nummer nicht kennt, soll das
ohne Zögern sagen können. Konkurrenz entsteht dabei nicht: In diesem Schritt steht kein zweiter
gefüllter Knopf auf dem Schirm.

**Symbole neben der Beschriftung, nie an ihrer Stelle.** Ein Piktogramm allein verlangt Vorwissen,
das ältere Besucher nicht mitbringen müssen; neben den Worten muss es nur bestätigen, was
gelesen wurde. Deshalb ist der Satz klein — Haken, Pfeil links, Pfeil rechts, Fadenkreuz —, und
alles andere trägt keins. Ein Symbol auf jedem Knopf wäre Zierde, und Zierde erklärt nichts.

**Gezeichnet, nicht geladen** (`kiosk/icons.tsx`): kein Symbolzeichensatz, kein CDN, kein Sprite
aus dem Netz. Das Gerät ist offline, und ein Symbol, das nicht lädt, hinterlässt einen Knopf,
der nichts sagt.

**Der Verwaltungsbereich bleibt ausdrücklich draussen.** Er hat eigene Masze, wird ein- bis
zweimal im Jahr benutzt und folgt einer anderen Regel: Dort zählt Klartext mehr als Kompaktheit.
Die alte leise Form steht deshalb noch — für „Zurück zur Karte" am Zahlenfeld, das aus der
Verwaltungstür herausführt und zu keiner Besucherfrage gehört.

Was daran hängt: [backlog.md](backlog.md), Punkt 10. Der Schließen-Knopf der Detailansicht war
an die Blätterknöpfe gebunden, damit die Ansicht *eine* Knopfform kennt. Jetzt gibt es vier
benannte Rollen, und keine heißt „schließen" — welche er bekommt, ist dort zu entscheiden.

---

## 31. Der Kopfbereich steht auf einer Mittellinie, der Zeitraum auf einem Boden

Zwei Änderungen an derselben Zeile, beide am 9. August 2026, und beide ersetzen eine Rechnung
durch eine Regel, die sich selbst trägt.

**Wappen, Titel und Zeitschieber richten sich senkrecht mittig aus.** Sie standen oben bündig und
endeten fast fünfzig Pixel auseinander. Das CSS behauptete an der Stelle das Gegenteil: Ein
Kommentar rechnete vor, dass beide Titelzeilen zusammen genau `--crest` ergeben und „damit genau so
hoch wie der Schieber nebenan" stehen. Das galt einmal — für eine Schirmbreite, und bis der
Schieber wuchs. `--crest` schrumpft auf schmalen Schirmen per Media Query, der Schieber nicht.

Drei Rechnungen, die auseinanderlaufen können, sind durch eine gemeinsame Mittellinie ersetzt:
`align-items: center` im Titelfeld, `justify-content: center` im Schieberfeld. Beide Zellen der
Gitterzeile sind ohnehin gleich hoch, also steht die ganze Zeile mittig, ohne dass eine Seite die
Höhe der anderen kennen müsste. Nachgemessen liegen alle drei Mittellinien auf demselben Pixel.

**Und das hat einen Punkt nebenbei aufgelöst:** Die Layoutmasze der Kopfzeile hängen seitdem
nicht mehr an der Displayauflösung des Museumsgeräts. Wo eine Abhängigkeit von einer offenen
Frage verschwindet, sobald man die Stelle richtig baut, war die Abhängigkeit vielleicht nie
die Frage.

**Der Zeitraum lässt sich nicht unter ein Jahrzehnt zusammenschieben.** Der ausgewählte Bereich
ist zugleich die Fläche, an der man ihn über die Achse zieht; auf einen Balken zusammengeschoben
bliebe nichts zum Anfassen. Dafür trug er bisher einen gezeichneten Griff in der Mitte — eine
Marke auf dem Schirm für einen Zustand, in den niemand geraten will. Der Griff ist weg, der Boden
ist da: `minSpan()` in `kiosk/timeAxis.ts`, ein Jahrzehnt, aber nie schmaler als ein Balken (bei
25-Jahres-Bündeln wäre ein Jahrzehnt schmaler als ein einziger). Gemessen bleiben so 65 px
Greiffläche statt eines Stummels.

**Das bewegte Ende stoppt, das andere wird nie mitgeschoben.** Mitzuschieben klingt geschmeidiger
und ist die Falle: Ein Zug am linken Ende trüge das rechte über das Achsenende, wo es geklemmt
würde — und der Zeitraum käme schmaler zurück, als er hineinging. Genau das Schrumpfen, das
`shiftRange` an anderer Stelle schon einmal verhindern musste.

**Kein Auge, kein Ersatzsymbol.** Der Griff war die Antwort auf ein Problem, das es nicht mehr
gibt; ein anderes Zeichen an derselben Stelle wäre die Antwort auf gar keins.

## 32. Nachschärfen geht durch eine eigene Tür, nicht durch eine gelockerte Prüfung

*Entschieden und gebaut am 10. August 2026* — Punkt 36, erste Lieferung. Diese Entscheidung ist die
erste Ausnahme zu [Punkt 5](#5-besucherbeiträge-werden-direkt-übernommen--mit-vollständigem-protokoll),
und sie ist so gebaut, dass sie den Satz dort **nicht anfasst**.

**Der Fall.** Ein Foto, das nur seine Straße kennt, liegt auf deren Mitte — bei einer 800-m-Straße
bis zu 400 Meter vom Haus entfernt. Es gilt als verortet und wurde deshalb nie wieder vorgelegt.
Wer das Haus erkennt, erkennt es am Bild; nachschärfen heißt aber, eine vorhandene Angabe zu
ersetzen, und genau das verbietet Punkt 5.

**Entscheidung.** Nicht `_require_empty` lockern, sondern ein eigener Endpunkt, der **keine
Koordinate annimmt**:

```
POST /api/contribute/{photo_id}/housenumber   { place_id, session_id }
```

Der Server schlägt `place_id` im Ortsverzeichnis nach, prüft `kind == "adresse"` und dass die
Adresse zur Straße des Fotos gehört, und schreibt Koordinate, `place_name` und Genauigkeit **aus
der Ortsindex-Zeile**. Der Besucher wählt aus einer Menge, die der Server aufgestellt hat.

**Warum das der Punkt ist, an dem alles hängt.** `POST /location` nimmt `accuracy_m` vom Client
entgegen. Heute ist das eine harmlose Behauptung, *weil* das Feld ohnehin leer sein muss. Würde die
Genauigkeit darüber entscheiden, ob überschrieben werden darf, wäre sie ein Schlüssel — und den
hielte der Client: Ein Aufruf mit `accuracy_m: 1` dürfte dann jede Angabe im Bestand ersetzen. Die
Regel „genauer darf ungenauer ersetzen, nie umgekehrt" ist richtig; sie ist nur nichts, was man
demjenigen zu bewerten geben darf, der davon profitiert.

**Wer gefragt wird**, entscheidet `services/needs.py` aus vier Bedingungen: straßengenau (150 m),
ein `place_name` **ohne Ziffer** — steht die Nummer schon im Namen, fehlt nur die Koordinate, und
das ist maschinelle Arbeit (am 11. August 2026 erledigt, siehe Punkt 34) —, und der Ortsindex muss
für diese Straße überhaupt Adressen
haben. 141 der 486 Straßen haben keine; ohne diese Bedingung stünde die Frage ohne einen einzigen
Knopf darunter auf dem Schirm.

**Kuratorenangaben sind ausdrücklich einbezogen.** Damit überschreibt Besucherarbeit
Kuratorenarbeit — das, was Punkt 5 sonst ausschließt. Getragen wird das von der Rücknahme: `Change`
hat seit heute eine Spalte `old_source`, und „zurücknehmen" heißt hier **zurücksetzen auf die
Straßenmitte** samt der alten Quelle, nicht löschen. Ohne diese Spalte machte eine Rücknahme aus
Kuratorenwissen stillschweigend einen Besucherbeitrag.

**Was diese Begründung aushöhlen würde**, ohne dass eine einzelne Änderung falsch aussähe:
Koordinaten vom Client anzunehmen; weitere Genauigkeitsstufen einzuführen und die Regel darauf zu
verallgemeinern; die Prüfung `place.street == photo.place_name` zu lockern. Jedes für sich wäre eine
Bequemlichkeit, zusammen wären sie das Ende von Punkt 5.

**Ein Widerruf gehört dazu.** `_locate` in `services/foldermeta.py` lässt Fotos aus Ordnern mit
einem Straßennamen ohne Hausnummer **bewusst unverortet**, mit der Begründung: Die Straßenmitte
„sähe aus wie eine Antwort", und das Foto fiele aus „Wo ist das?" heraus. Das war richtig, solange
es zwei Fragen gab. Mit der dritten fallen diese Fotos nicht heraus, sondern **in die genauere
Frage hinein** — die Begründung ist damit hinfällig, und die Regel gehört umgekehrt. Betroffen sind
64 der 72 Fotos ohne Ort. **Ausgeführt am 11. August 2026** — die Regel in `_locate` ist umgekehrt,
und dieselben Fotos sind im Bestand nachgezogen worden; siehe [history.md](history.md#der-erstbestand-wird-bereinigt--und-zwei-regeln-drehen-sich-um) und Punkt 34
weiter unten.

## 33. Stapel werden nicht gestreut, Stufenwechsel werden animiert

*Entschieden und gebaut am 10. August 2026* — Punkt 38, beide Teile. Zwei Fragen an dieselbe
Ansicht, und die eine beantwortet sich aus der anderen.

**Die Marker blenden ein, wenn die Gruppierung kippt.** `draw()` fragt supercluster auf der
**gerundeten** Zoomstufe ab; beim Wischen läuft der Zoom stetig, die Gruppierung wechselt aber erst,
wenn die Rundung umspringt — und dann alle Marker auf einmal. Das las sich wie ein Fehler, nicht wie
ein Maßstabswechsel. Animiert wird deshalb der Wechsel, nicht feiner abgefragt: Feiner abzufragen
hieße häufiger zeichnen, und das kostet auf dem Pi mehr, als es auf dem Mac aussieht.

**Was daran der eigentliche Fund war:** `draw()` hing an `move` *und* `zoom`. Beide feuern
zusammen — gemessen 31 zu 30 bei einem einzigen Tipp auf „+" —, es wurde also rund sechzigmal je
Zoomstufe alles neu gebaut. Nötig war nichts davon: MapLibre hält die Marker selbst auf ihren
Koordinaten. Gezeichnet wird jetzt auf `moveend`, und nur, wenn sich die Menge der Gruppen
tatsächlich geändert hat. Ohne das ist die Animation gar nicht möglich — ein als einblendend
markierter Marker wurde einen Frame später weggeworfen.

**Und Stapel werden nicht gestreut.** 854 verortete Fotos liegen auf 294 Punkten, der größte Stapel
trägt 51 Fotos auf einer Koordinate. Sie leicht auseinanderzuziehen, sobald weit genug
hineingezoomt ist, wäre die naheliegende Abhilfe — und sie ist die falsche: **Eine gestreute
Position täuscht eine Genauigkeit vor, die es nicht gibt.** Fünfzig Fotos der Schulstraße 2 liegen
auf einem Punkt, weil sie alle nur die Adresse kennen; auseinandergezogen sähen sie aus wie fünfzig
verschiedene Stellen.

Streuen und Nachschärfen sind zwei Antworten auf dieselbe Frage — und nur eine erzeugt Daten. Das
Nachschärfen (Punkt 32) will die Ungenauigkeit **sichtbar halten**, damit jemand sie behebt; das
Streuen versteckt sie hinter einem hübscheren Bild. Wenn ein Stapel von 51 unhandlich ist, ist das
ein Argument für eine bessere Stapelansicht, nicht für erfundene Koordinaten.

## 34. Der Archivordner schlägt die EXIF-Koordinate — sobald er eine Hausnummer nennt

*Entschieden und umgesetzt am 11. August 2026* — beim Bereinigen des Erstbestands (Punkt 41).

Bis dahin galt: **eine Koordinate aus der Datei schlägt den Ordner immer.** Die Begründung stand im
Modulkopf von `services/foldermeta.py` und klang zwingend — die Kamera stand tatsächlich dort, der
Ordner ist die Ablage von jemandem. Sie las sich als *Messung gegen Meinung*.

**Am Bestand nachgemessen ist sie keine.** Von 413 EXIF-verorteten Fotos teilen sich 278 ihre
Koordinate mit einem anderen; die Fotos verteilen sich auf 196 Punkte. An einem davon hängen 20
Fotos, die an **vier verschiedenen Tagen** aufgenommen wurden. Kein Empfänger liefert an vier Tagen
sechs gleiche Nachkommastellen — diese Werte sind eingetragen worden, von Hand oder von einem
Verwaltungsprogramm. Es steht also eine Ablage gegen eine andere, und nur eine davon macht sich am
Ortsindex fest.

**Deshalb gewinnt die Ordneradresse — aber nur die Adresse.** Die Straßenmitte gewinnt nicht: Sie
ist mit 150 m gröber als der Punkt, den sie ersetzen würde. Ein Foto, dessen Ordner keine
Hausnummer nennt, behält seinen EXIF-Punkt; im Erstbestand waren das 64. Diese Grenze ist die
eigentliche Regel, und sie hat ihren eigenen Test.

Wie weit die Fotos gewandert sind: 171 unter 15 m, 99 bis 50 m, 52 bis 150 m, 27 darüber, eines um
689 m. **Bei den Ausreißern liegt der EXIF-Punkt fast immer präzise auf einem anderen Haus** —
„Hauptstraße 11" lag 2 m neben Hauenweg 1. Welche Seite dort irrt, ist nicht zu entscheiden; die
Entscheidung fällt zugunsten der Angabe, die das Museum selbst über das Bild gemacht hat.

**Was diese Entscheidung aushöhlen würde:** eine spätere Quelle, die Koordinaten liefert, ohne dass
nachgesehen wird, ob sie gemessen oder eingetragen sind. Die Begründung hier hängt an einer
Messung, nicht an einer Rangordnung der Quellen — wer sie zitiert, ohne nachzuzählen, zitiert sie
falsch.

## 35. Die Hausnummer wird vor dem Jahr gefragt, und das ist Arithmetik

*Entschieden und umgesetzt am 11. August 2026* — nach dem Bereinigen, am laufenden Kiosk gesehen.

Die Reihenfolge in `NEEDS` (`services/needs.py`) ist der Rang, und eine Frage wird erst erreicht,
wenn die vor ihr **leer** ist. Sie lautete `location, date, housenumber` — aus dem Gefühl heraus
richtig, denn ein Jahr ist mehr wert als eine Hausnummer.

**Am Bestand ist das Gefühl falsch.** Nach der Bereinigung stehen 5 Fotos ohne Ort, **673 ohne
Jahr** und 71 zum Nachschärfen. Die Jahresfrage läuft nie leer — die dritte Frage wäre also nie
erreicht worden. Der Bereich trüge eine Frage, die niemandem je gestellt wird, und der ganze Aufwand
von Punkt 36 läge brach.

Umgekehrt läuft das Nachschärfen nach 71 Antworten trocken, und danach hat die Jahresfrage den
Bereich für sich, so lange es dauert. **Die Nachrangigkeit einer Frage bemisst sich nicht an ihrem
Wert, sondern daran, ob die vor ihr je zu Ende geht.**

Aufgefallen ist es erst am laufenden Kiosk: Überspringen der Jahresfrage führte zurück zu „Wo ist
das?", und die dritte Frage kam nie. Kein Test im Backend fiel, als die Reihenfolge vertauscht
wurde — gemerkt hat es allein einer im Frontend, wo dieselbe Liste ein zweites Mal steht. Diese
Lücke ist mit `TestRangfolge` geschlossen.

## 36. Archivinterna gehören in die Herkunft, Fotorückseiten in die Beschreibung

*Entschieden und umgesetzt am 12. August 2026* — beim Aufräumen der Textfelder (Punkt 41).

Der Erstbestand brachte 52 Schlagwörter mit, die mit „Notiz" beginnen: abgeschriebene Rückseiten
von Abzügen und Archivkarten. Sie zerfallen in zwei Arten, und die eine gehört vor Besucheraugen,
die andere nicht.

**Inhalt geht in die Beschreibung.** „Notiz: Grundsteinlegung der Turnhalle ca. 1968" ist eine
Aussage über das Bild. Als Schlagwort taugt sie nichts — sie hängt an genau einem Foto und stünde
in einer Schlagwortliste ([Punkt 30](backlog.md)) nur im Weg. **Der Präfix „Notiz:" bleibt stehen**:
Er ist keine Verzierung, sondern die Quellenangabe. Der Satz stammt von der Rückseite, nicht von
einem Kurator, der das Bild betrachtet hat.

**Regalnummern gehen an die Herkunft.** „Notiz: P 11", „Notiz: O 40", „Notiz: 3" sind Signaturen
des Archivs. Sie sollen erhalten bleiben — wer ein Foto im Regal wiederfinden will, braucht sie —
aber sie gehören **nicht in die Beschreibung**, denn die steht im Kiosk unter dem Bild
(`overlay__description`). Unter einem Hof des 19. Jahrhunderts stünde dann „P 35".

`provenance` ist das Feld dafür, und zwar nicht aus Bequemlichkeit: `PhotoDetail` in `schemas.py`
hat kein Feld dafür, und der Docstring nennt das den Zweck der Klasse — „der sicherste Weg, sie von
diesem Schirm fernzuhalten, ist ein öffentliches Schema, das kein Feld dafür hat". Die Signatur
schließt an den Archivpfad an, der dort ohnehin steht.

**Die Regel, die daraus folgt und die beim nächsten Bestand wieder gebraucht wird:** Eine Angabe,
die dem Museum beim *Verwalten* hilft, gehört in die Herkunft. Eine Angabe, die etwas über das
*Bild* sagt, gehört in die Beschreibung. Wer sie zusammenwirft, spart einen Gedanken und nimmt
dafür in Kauf, dass Archivinterna in der Ausstellung erscheinen.

## 37. Ein Jahr im Text datiert nicht das Foto, sondern manchmal nur das Haus

*Entschieden und umgesetzt am 12. August 2026* — Punkt 41, letzter Teil.

83 undatierte Fotos trugen eine Jahreszahl in Titel, Beschreibung oder Schlagwort, bei 673
undatierten. Die naheliegende Auswertung wäre eine Regel gewesen. **Sie wäre falsch gewesen, und
das Nachmessen zeigt genau, woran:**

| im Text steht | eine Regel liest | es ist aber |
|---|---|---|
| `Notiz: P 37` | 1937 | eine Regalnummer |
| `Friedhofsweg 30` | 1930 | eine Hausnummer |
| „erbaut 1972, verkauft 2000" | 1972 | keins von beidem |
| „**vor** 1978" | 1978 | eine Obergrenze |
| „in den 70er Jahren **abgerissen**" | 1970er | das Foto ist **davor** |

Daraus zwei Festlegungen:

**Zweistellige Kurzformen werden nicht ausgewertet.** „78" für 1978 ist im Bestand üblich — und
nicht von Regalnummern und Hausnummern zu unterscheiden. 62 Fotos hingen an solchen
Zweideutigkeiten und bleiben undatiert.

**Gesucht wird das positive Muster, nicht das negative.** Nicht „ein Jahr ohne Warnwort", sondern
„ein Jahr, dem *um*, *ca.*, *im Jahre*, *Herbst*, *Dezember* oder *aus den* vorausgeht". Eine
Warnwortliste ist nie fertig — beim ersten Versuch fehlten *bebaut*, *abgebrannt* und *Baujahr*,
und jedes davon hätte ein Foto falsch datiert.

Am Ende sind es 52 Fotos geworden, **einzeln durchgesehen und als Liste im Skript festgehalten,
nicht als Regel.** 17 Vorschläge wurden verworfen.

**Und warum das Verwerfen die teurere Hälfte der Entscheidung ist:** Ein verworfener Vorschlag
kostet nichts — das Foto bleibt undatiert, der Text bleibt lesbar, und im „Hilf mit"-Bereich wird
weiter „Wann war das?" dazu gefragt, wo jemand aus Holm es richtig beantworten kann. Ein
angenommener falscher Vorschlag dagegen macht das Foto **datiert**: Es fällt aus der Frage heraus,
liegt auf der Zeitleiste an der falschen Stelle, und niemand sieht es je wieder an. Das ist
dieselbe Asymmetrie, die schon die EXIF-Regel aus Stufe 3 trägt.

## 38. Die Detailansicht fragt nicht selbst, sie verzweigt in den Beitragsbereich

*Entschieden und umgesetzt am 12. August 2026* — Punkt 46, und damit die Rücknahme dessen, was am
10. August gebaut wurde.

Damals bekam die Detailansicht ihre eigenen Auswahlraster: Wer ein undatiertes Foto groß ansah,
sollte es dort datieren können, ohne zu schließen und zu hoffen, dass der Bereich dasselbe Foto
vorlegt. Das war richtig, **weil der Bereich es damals nicht vorlegen konnte** — das Nachschärfen
stand dort hinter 74 unverorteten Fotos und erschien nie.

Zwei Dinge haben sich seither geändert, und beide sprechen dagegen:

**Die Textspalte lief voll.** Ein Foto ohne Jahr und ohne Hausnummer trug bis zu 37 Schaltflächen
unter der Beschreibung. Allein die Jahrzehnte sind fünfzehn, seit die Zeitleiste von 1880 bis 2030
reicht statt von 2010 bis 2025 — die Datierung des Erstbestands hat das Problem selbst vergrößert.

**Die Ortsfrage war dort nie zu stellen.** Sie braucht die Karte, und die Karte liegt unter dem
Overlay. Von den drei Fragen konnte die Detailansicht also nur zwei, und ausgerechnet die
wertvollste nicht.

**Jetzt stehen dort bis zu drei Knöpfe** — je an der Zeile, die sie ändern —, und ein Tipp
schließt die Ansicht und stellt dieses Foto im Bereich zu dieser Frage. Der Kiosk hat damit
**einen Antwortweg statt zwei**.

**Das Schließen ist nicht Nebenwirkung, sondern die halbe Absicht.** Bei „Wo ist das?" muss die
Karte frei werden. Es je Frage anders zu machen wäre eine Regel, die niemand sehen kann.

**Und danach passiert nichts Besonderes**, was die eigentliche Entscheidung ist: Dank, dann die
nächste offene Frage zu diesem Foto, dann ein neues — der gewöhnliche Ablauf. Ein Rückweg in die
Detailansicht wäre näher am Ausgangspunkt, bräuchte aber eine Sonderregel im Store und liesse
die Kette wegfallen. Wer aus einem Foto heraus antwortet, ist im Beitragsbereich gelandet, und dort
gehört die nächste Frage hin.

**Was das kostet:** Das Datieren ist zwei Tipps länger geworden, und die Ansicht schließt sich
dabei. Der Gewinn ist strukturell und beim ersten Antippen nicht zu sehen. Wenn sich das am Gerät
schlechter anfühlt, ist die Rückfallebene, den `DatePicker` eingebettet zu lassen und nur Ort und
Hausnummer zu verzweigen — dann wären es aber wieder zwei Wege.

**Der Wunsch ist eine Bitte, keine Anweisung.** `GET /contribute/next?photo_id=…` prüft das Foto
gegen dieselbe Bedingung wie jedes andere und fällt auf die Zufallswahl zurück, wo sie nicht mehr
gilt. Sonst stünde eine Frage auf dem Schirm, die zwischen Tippen und Laden schon von jemand
anderem beantwortet wurde — und der Schreibweg wiese die Antwort mit 409 ab, was klingt, als sei
der Besucher zu langsam gewesen.

## 39. Eine Beschriftung für das Auge und für das Vorlesewerkzeug

*Entschieden und umgesetzt am 12. August 2026* — Punkt 44, und die Ablösung von Punkt 29.

Unter dem Vorschaubild stand die **Adresse**, im `aria-label` desselben Knopfes der **Titel**. Zwei
Formulierungen derselben Sache, an zwei Stellen im Code. **Monatelang fiel es niemandem auf, weil
beide dasselbe sagten** — 815 Titel wiederholten die Adresse daneben. Als der Erstbestand
aufgeräumt war, las das Auge „Hauenweg 7" und das Ohr „Hermann Berg".

**Der Fehler war nicht die falsche Zeile, sondern dass es zwei gab.** Beide zu berichtigen hätte
ihn vertagt: Zwei Formulierungen laufen wieder auseinander, sobald jemand eine davon anfasst. Es
gibt jetzt eine (`kiosk/mapCaption.ts`), und beide Sinne lesen sie.

**Die Kette ist Titel, dann Adresse, dann nichts**, mit dem Jahr wo bekannt. Dass der Titel
vorangeht, ist die Umkehrung von Punkt 29 — und die Voraussetzung jener Entscheidung ist entfallen:
Titel waren damals Adressen und oft vierzig Zeichen lang. Heute sind es Titel.

**„Hauptstraße Nr. ?" statt nur „Hauptstraße"**, wo die Hausnummer fehlt. Das ist kein Notbehelf,
sondern dieselbe Haltung wie beim Nichtstreuen der Stapel (Punkt 33): Die Ungenauigkeit soll
**sichtbar** bleiben, damit jemand sie behebt, statt hinter einem hübscheren Bild zu verschwinden.
Es ist genau die Lücke, nach der der Beitragsbereich unter „Welche Hausnummer?" fragt — auf 82
Markern steht sie jetzt.

**Für Stapel gilt die Regel aus Punkt 29 unverändert, jetzt auch für den Titel:** Gezeigt wird
nur, worin **alle** Fotos übereinstimmen. Und sie greift beim Titel öfter, denn eine Adresse
teilen Fotos leicht, einen Titel selten — ein Stapel fällt damit meist auf die Adresse zurück.
Den obersten Titel zu nehmen hiesse „Gasthof Timm" über fünfzig Bilder zu schreiben, die
etwas anderes zeigen.

**Dazu haben 75 Fotos einen Titel aus ihrer Beschreibung bekommen** — zusammengefasst, nicht
abgeschnitten: „Errichtung des Funkmastes" wurde „Funkmast", „Otto Petersen, Inhaber der Bäckerei"
wurde „Bäckerei Petersen". 14 weitere Beschreibungen taugten nicht, weil sie über Besitzer,
Rückseiten oder Ortsvermutungen sprechen statt über das Motiv.

**Was ausdrücklich *nicht* geschrieben wurde:** ein Titel für die 152 Fotos, deren Titel nur ihre
Adresse wäre. Der stünde dann zum zweiten Mal in derselben Zeile — genau das, was einen Tag
zuvor für 815 Fotos entfernt worden ist —, er veraltete beim ersten Nachschärfen, und er nähme
[Punkt 1](backlog.md) die Arbeitsgrundlage: Danach hätten alle 929 Fotos einen Titel, und welche
einen **echten** brauchen, wäre nicht mehr zu erkennen. Abgeleitet steht auf der Karte dasselbe.

## 40. Ein Symlink ist nie ein Datenträger

Die Suche nach Sicherungszielen (`services/backup/drives.py`, `find_drives`) **überspringt Symlinks**,
auf beiden Ebenen, die sie durchsucht.

Der Grund ist eine Eigenheit von `os.path.ismount`: Es antwortet für einen Symlink
**grundsätzlich `False`** — „ein Symlink kann nie ein Einhängepunkt sein". Damit sieht ein
Symlink unter `/media` wie ein gewöhnlicher Ordner aus, und die Suche steigt eine Ebene hinab.
Dieser Abstieg ist gewollt, denn Raspberry Pi OS hängt unter `/media/<benutzer>/<bezeichnung>`
ein — nur folgt `iterdir()` dabei dem Symlink, und was dahinter liegt, wird als Sicherungsziel
angeboten.

**Gemessen am 14. August 2026**, bei der Prüfung des Containerbetriebs: Der Verwaltungsbereich bot
zwei „Laufwerke" namens `data` und `media` an — das erste war das Datenverzeichnis selbst. Die
Sicherung lief durch, vollständig, mit Handzettel: **931 Fotos, 1,45 GB, abgelegt in dem Ordner,
den sie sichert.**

Genau davor soll die Einhängeprüfung schützen, und ihr Docstring sagte das auch schon: „sonst
landete die Sicherung auf derselben SD-Karte, gegen deren Ausfall sie schützen soll — und niemand
sähe es". Der Symlink war das Loch darin. `find_drive` fing es nicht auf, denn es prüft den
Pfad aus dem Browser nur gegen das, was `find_drives` gefunden hat.

**Auf jedem Mac war das der Normalfall, nicht ein Zufall.** macOS legt in `/Volumes` stets einen
Symlink auf `/` an, benannt nach dem internen Volume. Wer also der `operations.md` folgt und zum
Entwickeln `KIEKMAP_MEDIA_DIR=/Volumes` setzt, bekam diesen Fehler zuverlässig — er war nur
nie jemandem aufgefallen, weil niemand den Sicherungsknopf auf einem Mac gedrückt hatte.

Auf einem Pi ist der Fall dagegen unwahrscheinlich: In `/media` legt einen Symlink nur root an.
Die Folge wäre aber die schlimmste im System — eine Sicherung, die aussieht wie eine, und die mit
dem Datenträger stirbt, vor dem sie schützen sollte. Zwei Zeilen sind dafür ein günstiger
Preis, und für die Entwicklung sind sie keine Vorsorge, sondern eine Behebung.

**Für den Test war dieselbe Falle noch einmal aufgestellt.** Die eingesetzte `_is_mounted`
vergleicht Pfade, und wörtlich verglichen ist `media/Danger/data` nicht `anderswo/data` — der
Test war deshalb im ersten Anlauf auch ohne die Absicherung grün. Er vergleicht jetzt
aufgelöst. **Eine Gegenprobe, die nicht ausschlägt, ist ein Ergebnis und keine Formalie.**

## 41. Der Name nennt die Sache, nicht den Ort

Das Projekt heißt **Kiekmap** — plattdeutsch *kieken*, gucken. Nach aussen mit großem K, im
Quelltext, in Pfaden und Verzeichnisnamen klein, als Präfix der Einstellungen `KIEKMAP_`.

Der bisherige Arbeitsname beschrieb, was das Programm tut. **Ein Name für den ersten Ort wäre
der schlechtere gewesen**, und zwar aus demselben Grund, aus dem `CLAUDE.md` verlangt, dass nichts
Ortsspezifisches in den Code gehört: Das zweite Museum soll eine eigene `region.json` und eine
eigene `.env` brauchen, keinen Fork. Ein „holm" im Paketnamen hätte dieser Zusage widersprochen,
lange bevor jemand sie technisch verletzt hätte.

**Umbenannt wurde am 15. August 2026**, an 213 Stellen in 38 versionierten Dateien. Für Besucher
war der Name nie sichtbar — die Seite heißt „Bilder aus unserem Ort".

Der Zeitpunkt war der letzte günstige: kein Pi im Feld, kein Git-Remote, der einzige Bestand auf
dem Entwicklungsrechner. Danach hätten Geräte, Sicherungen auf Sticks und fremde Arbeitskopien
mitgezogen werden müssen.

**Was dabei bricht, und zwar bewusst:** Sicherungen aus der Zeit davor werden nicht mehr erkannt.
`is_restorable` und `looks_like_archive` suchen den Namen im Ordner bzw. im Dateinamen des Archivs
— eine Verträglichkeitsregel dafür wäre Ballast für einen Fall, der genau einmal eintritt und
sich mit einem Klick lösen lässt: neu sichern.

## 42. Die Wiederherstellung bringt das Schema selbst auf Stand

Eine zurückgespielte Sicherung wird migriert, und zwar von der Wiederherstellung selbst
(`services/schema.py`, aufgerufen in `backup.restore._swap_in`). Ein Neustart ist dafür nicht mehr nötig.

**Der Anlass ist ein Fehler, der zwei Tage lang unbemerkt lief.** Eine Sicherung bringt ihr Schema
mit; getauscht wird die Datei im Ganzen, und das laufende Programm hängt sich nur neu an sie.
Migrationen liefen dabei nicht — sie laufen beim *Start*, und eine Wiederherstellung ist kein
Start. Das Gerät sah danach völlig normal aus und **nahm nichts mehr an**: Jeder Besucherbeitrag,
jede Bearbeitung, jeder Upload endete mit HTTP 500.

Die Abhilfe stand seit dem 12. August 2026 in beiden Handbüchern: einmal neu starten. **Eine
Anweisung an Menschen ist aber die schwächste Stelle, die eine Zusage haben kann** — sie muss
gelesen, erinnert und befolgt werden, und zwar von jemandem, der ein- bis zweimal im Jahr an dieses
Gerät geht. Wer sie vergisst, merkt nichts, denn der Fehler zeigt sich erst beim nächsten
Besucher, der etwas beitragen will.

**Die Reihenfolge ist der ganze Punkt**, und sie hat zwei Hälften auf beiden Seiten des Tauschs:

1. **Abgelehnt wird vorher.** Trägt die Sicherung eine Revision, die dieses Programm nicht kennt,
   bricht die Wiederherstellung ab, **bevor** irgendetwas ersetzt ist. Der Bestand auf dem Gerät
   bleibt unangetastet. Migrieren wäre hier keine Option: Die zugehörigen Migrationen gibt es in
   diesem Programm gar nicht.
2. **Migriert wird nachher.** Erst nach dem Tausch ist die zurückgespielte Datei die am
   konfigurierten Pfad.

**Formuliert als „kennen wir diese Revision?", nicht als „ist sie neuer?".** Eine Revision, die
sich nicht einordnen lässt, ist eine, die man nicht anfassen darf — gleich ob sie aus einem
neueren Programm stammt, aus einem anderen Zweig oder aus einer Datei, die gar nicht unsere ist.

**Ein Sonderfall bleibt bewusst offen:** Eine Datenbank ohne `alembic_version` wird nicht migriert,
sondern in Ruhe gelassen. Ohne Stempel ist nicht zu sagen, was die Datei ist, und Alembic finge bei
der ersten Migration gegen Tabellen an, die es schon gibt. Im Museum kann das nicht vorkommen —
dort entsteht jede Datenbank durch Migrationen. Es kommt in der Testumgebung vor, wo das Schema
direkt aus den Modellen entsteht, und genau dort wäre Migrieren falsch.

**Dazu zwei Dinge, die den Fehler hätten finden können und es nicht taten**, jetzt nachgeholt:
`test_migrationen_und_modelle_beschreiben_dasselbe_schema` baut das Schema einmal über Alembic und
einmal über `create_all` und vergleicht Tabellen und Spaltennamen — die übrigen Tests bauen es
aus den Modellen und können eine fehlende Migration deshalb grundsätzlich nicht bemerken. Und
`make dev` zieht den Schemastand jetzt vorweg nach, denn im Container tut das der Entrypoint, auf
dem Entwicklungsrechner aber niemand.

## 43. Der Kopfbereich misst sich an seiner Spalte, nicht am Ansichtsfenster

Wappen und Titel bekommen ihre Größe aus der Breite der Zelle, in der sie stehen
(`container-type: inline-size` und `cqi` in `styles/global.css`), nicht aus einer Medienabfrage.
Der Ortsname bekommt zusätzlich seine **Länge** mitgeteilt, weil CSS Text nicht messen kann.

**Der Anlass war ein Fehler mit zwei Ursachen, und die zweite war die schwerere.**

Die erste ist ein Fallstrick, den man einmal kennen muss: **In einer Medienabfrage ist `rem` immer
16 px.** Es ist die Schriftgröße des Wurzelelements, *bevor* eine eigene Regel sie ändert —
`:root { font-size: 18px }` gilt darin nicht. `@media (max-width: 85rem)` meinte also 1360 px, wo
1530 px gedacht waren, und dazwischen stand ein zu großes Wappen neben einer zu schmalen Spalte.

Die zweite: **Der Entwurf hatte 0,3 px Luft.** Auch oberhalb der Schwelle passte „Bilder aus" nur
knapp; bei 1470 x 956 brach Safari um und Chromium nicht. Die Grenze zu berichtigen hätte den
Fehler also nur verschoben. **Eine Zeile, die erst beim Nachmessen passt, passt nicht.**

**Daraus die Regel:** Wer im Kopfbereich eine Größe setzt, bezieht sie auf den Platz, der da ist,
und lässt Luft. Eine Schwelle im Ansichtsfenster ist immer eine Stelle, an der zwei Rechnungen
auseinanderlaufen können — dasselbe Muster, das am 9. August 2026 schon die drei Höhenrechnungen
von Wappen, Titel und Schieber durch eine gemeinsame Ausrichtung ersetzt hat.

**Und die Zusage ist begrenzt, mit Absicht.** Der Ortsname wird kleiner gesetzt, je länger er ist,
aber **nie kleiner als die Zeile „Bilder aus" darüber** — sonst stünde die Rangfolge auf dem
Kopf. Wo dieser Boden greift, bricht der Name um; das ist die bessere der beiden schlechten
Antworten und war auch vorher schon die gewählte. Bis zwölf Zeichen geht es auf jedem Schirm gut,
bis sechzehn auf einem breiten — nachgemessen und in `docs/adaption.md` aufgeschrieben, weil es
die nächste Gemeinde betrifft und nicht diese.

## 44. Die Blätterknöpfe stehen fest, das Bild bewegt sich

In der Detailansicht sind die Blätterknöpfe **senkrecht am unteren Rand verankert** und stehen
**waagerecht mittig unter dem Bild**. Das Bild sitzt darüber und ändert seine Höhe, die Knöpfe
nicht.

**Vorher klebten sie am Bild und wanderten mit ihm.** Zwischen einem 3:2-Querformat und einem
2:3-Hochformat lagen **103 px** -- gemessen am 16. August 2026 auf einem 1024er Schirm. Wer durch
einen Stapel blättert, dessen Fotos nicht alle dasselbe Format haben, jagt damit den Knopf über
den Schirm; im schlimmsten Fall liegt beim nächsten Tippen das Bild dort, wo eben noch
„Nächstes" stand. Auf einem Touchscreen ist das kein Schönheitsfehler, sondern ein Fehlgriff.

**Waagerecht bleiben sie beim Bild**, und das ist die Gegenrichtung derselben Frage: Sie gehören
zu dem, was sie ändern. Mittig im Schirm stünden sie bei einem Hochformat weit neben dem Bild,
und der Bezug ginge verloren. Die linke Spalte ist deshalb weiterhin genau so breit wie das Bild.

**Die Regel dahinter:** Was der Besucher *trifft*, steht still; was er *ansieht*, darf sich
bewegen. Ein Bedienelement, dessen Ort vom Inhalt abhängt, ist auf einem Berührungsschirm eine
Falle -- besonders für die Zielgruppe, die hier vor dem Gerät steht.

**Der Schließen-Knopf folgt derselben Regel** und steht seit demselben Tag in der Ecke des
Schirms statt am rechten Rand des Inhalts. Er bekommt dabei **keine** der vier Rollen aus Punkt 30:
Die sind die Sprache des Beitragsbereichs -- auswählen, übernehmen, zurück, überspringen --,
und Schließen ist keine davon. Die Detailansicht führt auf ihrem dunklen Grund ohnehin eine
eigene Knopffamilie; sie behält ihn als Sonderfall.

## 45. Woher eine Koordinate kommt, sagt nichts darüber, wie genau sie ist

Ob ein Foto zum Nachschärfen vorgelegt wird, entscheidet, **was über das Haus bekannt ist** --
nicht, aus welcher Quelle seine Koordinate stammt (`services/needs.py`, `_needs_housenumber`).

**Bis zum 16. August 2026 stand dort das Gegenteil.** Die Bedingung verlangte ausdrücklich
`location_accuracy_m == ACCURACY_STREET_M`, liess also nur zu, was ein Kurator auf eine Straße
gesetzt hatte. Begründet war das mit einem Satz, der plausibel klingt: „Das Gerät weiß, wo der
Fotograf stand, nicht was er fotografiert hat."

**Der Satz war vier Tage vorher widerlegt worden.** Am 12. August ergab das Nachzählen, dass von
413 EXIF-Koordinaten des Erstbestands **278 sich zwei Fotos teilten** -- eingetragene Werte, keine
Messungen (Punkt 34, und es steht seitdem in `CLAUDE.md` unter den drei Dingen, die man hier falsch
machen kann). Niemand ist danach zu `needs.py` zurückgegangen. 53 Fotos mit einem Straßennamen
aus dem Archivordner und einer eingetragenen Koordinate blieben aus der Frage draussen, obwohl sie
genau ihr Fall sind.

**Aufgefallen ist es als etwas anderes**, und das ist der Teil, der das Aufschreiben lohnt: Gemeldet
wurde, in der Detailansicht fehle der Knopf, *sobald das Jahr bekannt ist*. Die Beobachtung stimmte,
die Erklärung nicht. Unter den Fotos mit bloßem Straßennamen sind die mit Jahr überwiegend
gerade die aus dem EXIF -- 35 von 53, gegen 13 von 71 bei den straßengenauen. Wer sich durchklickt,
sieht eine saubere Korrelation und schließt auf die falsche Ursache. **Eine gemeldete Beobachtung
ist ein Befund, ihre Erklärung eine Vermutung**, und die beiden gehören getrennt geprüft.

**Die Bedingung nennt jetzt, was sie meint:** auf der Karte, nicht schon hausgenau, ein
Straßenname ohne Ziffer, und der Ortsindex kennt Adressen dazu. Die Frage wächst damit von 70 auf
116 Fotos; keines fällt weg.

**Was daraus für ähnliche Regeln folgt:** Eine Bedingung, die über die *Herkunft* eines Wertes
statt über seinen *Inhalt* entscheidet, trägt eine Annahme mit sich, die veralten kann, ohne dass
die Regel es merkt. Wo es geht, wird gefragt, was bekannt ist -- nicht, wer es eingetragen hat.

## 46. Der Bestand ist JPEG, und das Rezept dafür steht fest

*Entschieden am 16. August 2026, beim Nachziehen des neueren Archivstands (Punkt 52).*

Ein Museumsarchiv ist gemischt: Scans kommen als TIFF, Bildschirmaufnahmen als PNG, ein Bild von
einer Webseite als WEBP. Der Bestand führt nur JPEG, und der Grund ist nicht Ordnungsliebe --
**ein Browser zeigt kein TIFF an.** Der Kiosk brauchte ein Vorschaubild und reichte eine
Originaldatei heraus, die sich nirgends öffnen lässt; die Detailansicht bietet genau diese Datei
an.

**Die Einstellung ist gemessen, nicht gewählt.** Der Erstbestand war schon umgewandelt
angekommen, von einem Werkzeug, das niemand aufgeschrieben hatte. Seine Quantisierungstabellen
sagen: Pillow, Qualität 92, Subsampling 4:4:4, `optimize`. Gegen die 19 Dateien, für die beide
Fassungen vorliegen, kommen damit **vier bitgleich** und **achtzehn pixelgleich** heraus; mit
Qualität 90 keine einzige.

**Das ist mehr als Sauberkeit, es ist die Voraussetzung für die Dublettenerkennung.** Der Import
erkennt eine Dublette am SHA-256 der Datei. Zweimal dasselbe Rezept über dieselbe Datei gibt
denselben Hash -- eine andere Qualität gibt einen anderen, und beim nächsten Archivstand käme
jedes schon vorhandene Bild ein zweites Mal herein, ohne dass jemand etwas merkt. Deshalb steht
die Einstellung in `tools/to_jpeg.py` als Konstante und hat einen eigenen Test, der sie festhält.

Die neunzehnte ist `Weidenstieg/Straszenauffahrt`, deren altes JPEG andere Tabellen trägt: Die
hat jemand von Hand umgewandelt, bevor es ein Rezept gab.

## 47. Ein Diff über Bytes ist kein Diff über Bilder

*Gelernt am 16. August 2026, an 619 Dateien.*

Vom Museum kam ein neuerer Archivstand, bereits als Differenz geliefert: alles, was im aktuellen
Bestand des Museums liegt, minus dem, was in unseren Erstimport ging. 619 Dateien. Und im Backlog
stand die Zusage, der Abgleich erledige sich zum großen Teil von selbst -- der SHA-256 entscheide
über Dublette oder nicht.

**223 der 619 zeigten ein Bild, das schon im Bestand stand.** Ein Import über den ganzen Ordner
hätte 223 zweite Fassungen angelegt.

Der Grund: Das Museum hat seinen Bestand durch **ExifTool** laufen lassen und dabei die
Metadatenblöcke neu geschrieben -- Ortsangaben korrigiert, Stichwörter vereinheitlicht, den
eingebetteten Vorschau-Anhang verkleinert. `P4139301.JPG` liegt alt mit 1 848 144 Bytes vor, neu
mit 1 843 343: **dieselben Bildpunkte, andere Bytes.** Wer so einen Stand byteweise vergleicht,
bekommt keinen Diff der Bilder, sondern einen Diff der Bearbeitungsläufe.

**Die Regel daraus:** Ein Datenstand, der über Bytes verglichen wurde, sagt nichts darüber, was
neu *ist* -- nur darüber, was neu *geschrieben* wurde. Vor jedem Import eines gelieferten Diffs
wird deshalb über den Bildinhalt nachgezählt, in zwei Durchgängen: erst pixelgenau bei gleichen
Kantenlängen (das siebt fast alles), dann grob über 32x32-Graustufen für das, was beim
Neuausspielen auch die Größe geändert hat. Der zweite Durchgang fand sechs weitere, darunter
eine Sporthalle in dreifacher Auflösung.

**Der Abstand zwischen Treffer und Nicht-Treffer war dabei kein Ermessen**, und das ist der Grund,
warum eine Schwelle hier überhaupt vertretbar ist: 212 der Treffer lagen bei einer mittleren
Abweichung von exakt 0,00, der höchste bei 3,01 -- und der nächste Nicht-Treffer bei 56.

## 48. Was im Titelfeld steht, ist nicht automatisch ein Titel

*Entschieden am 16. August 2026, nachdem der neue Archivstand denselben Fehler dreifach
zurückgebracht hatte.*

In der Detailansicht steht der Titel **über** der Adresse, nicht an ihrer Stelle. Ein Foto, das
„Hauptstraße 14, Museum" heißt und darunter noch einmal „Hauptstraße 14" führt, sagt eine Zeile
umsonst -- und die Zeile darüber ist die auffälligste der ganzen Ansicht.

Punkt 41 hat im August 2026 **815 solcher Titel von Hand auseinandergenommen**. Die Regel, die sie
erzeugt, blieb dabei stehen: `apply_folder_meta` setzte den Titel weiter auf „Straße Hausnummer,
Zusatz". Der nächste Archivstand schrieb **323 von 395** neuen Fotos genau so wieder an. Daher
drei Regeln statt einer Aufräumaktion:

**Der Ordnertitel ist der Zusatz.** „14 Gasthof Petersen" ergibt den Titel „Gasthof Petersen", die
Adresse steht in `place_name`. Nennt der Ordner nur eine Nummer, bleibt der Titel **leer** -- eine
Zeile, die nur die nächste wiederholt, ist keine.

**Die Längengrenze ist gemessen, nicht gewählt.** `TITLE_MAX` stand bei 120 und liess acht
Bildunterschriften als Titel durch, die längste mit 108 Zeichen. Von den 781 Titeln, die das
Museum von Hand gesetzt hat, überschreitet **kein einziger 58 Zeichen**; der Mittelwert liegt bei
13. Die Grenze steht jetzt bei 60, und was darüber liegt, wandert in die Beschreibung statt
weggeworfen zu werden.

**Der Name der Scannersoftware gehört in kein Feld.** „Intel(R) JPEG Library, version
[1.51.12.44]" kam als Titel von 35 Fotos. Anders als eine zu lange Bildunterschrift darf er
**nicht** in die Beschreibung ausweichen: Das schöbe denselben Unsinn nur eine Zeile tiefer, wo er
im Kiosk unter dem Bild stünde. Punkt 41 hatte achtzehn davon von Hand entfernt.

**Die Lehre steckt nicht in den drei Regeln, sondern darin, warum es sie zweimal brauchte.** Eine
Bereinigung von Hand räumt den Bestand auf und lässt die Ursache stehen. Solange die Ursache im
Import sitzt, ist die nächste Lieferung die nächste Bereinigung. Was von Hand aufgeräumt wird,
gehört danach als Regel dorthin, wo es entstanden ist -- sonst zählt man dieselbe Arbeit in
Monaten.

## 49. Ein Datumswort sagt, dass es ein Datum ist -- nicht, wovon

*Ergänzung zu Punkt 37, am 16. August 2026 im Trockenlauf aufgefallen.*

Punkt 37 hatte die Regel umgedreht: nicht „eine Jahreszahl ohne Warnwort", sondern „eine
Jahreszahl, der *um*, *ca.*, *im Jahre*, *Herbst* oder *Dezember* vorausgeht". Begründet damit,
dass eine Warnwortliste nie fertig wird, ein positives Muster aber schon.

**Das Muster allein reicht nicht.** Im Bestand steht:

    ca. 1970 wurde dieses Haus abgerissen und durch ein Mehrfamilienhaus ersetzt

Das Datumswort steht davor, sauber. Nur datiert die Jahreszahl den **Abriss** -- und die Aufnahme
liegt zwingend davor, sonst gäbe es das Haus auf dem Bild nicht. Zwei Fotos wären so auf das Jahr
ihres eigenen Verschwindens datiert worden, und weil sie damit als datiert gelten, hätte sie
niemand mehr gefragt.

**Beide Listen werden gebraucht, und sie tun Verschiedenes.** Das Datumswort davor sagt, *dass*
eine Zahl ein Datum ist. Ein Ereigniswort dahinter -- *abgerissen*, *erbaut*, *abgebrannt*,
*ausgesiedelt*, *verkauft* -- sagt, *wovon*. Der Einwand aus Punkt 37 gilt weiter, trifft aber nur
die eine Richtung: **Eine Liste, die ausschließlich ablehnt, darf unvollständig sein.** Sie lässt
dann einen Fall durch, den ein Mensch danach noch sieht; eine Liste, die etwas *annimmt*, macht aus
einer Lücke eine falsche Angabe.

## 50. Wer es geliehen hat und wo es lag, sind zwei Antworten

*Nachgebessert am 16. August 2026, gemeldet vom Museum.*

Die Herkunft trug bei 265 Fotos den Archivpfad nicht -- genau bei denen, deren Datei selbst schon
etwas sagte („Familie Boysen", „Sammlung Jan Wendt", „August Möller"). `apply_folder_meta`
füllte das Feld nur, wenn es leer war, und stand damit vor jeder Angabe, die jemand schon
gemacht hatte.

**Das ist genau umgekehrt, als es sein müsste.** Wer ein Foto geliehen hat, steht in der Datei
und ist damit gesichert. **Wo es im Archiv lag, steht nur im Pfad** -- und der Pfad geht mit dem
Import verloren, denn im Bestand heißt die Datei nach ihrem SHA-256. Es ist die einzige Angabe
der beiden, die sich aus dem Bild nie wiederherstellen lässt, und sie fehlte ausgerechnet dort,
wo ohnehin schon jemand mitgedacht hatte.

Beides steht jetzt nebeneinander, durch Komma getrennt:

    Familie Boysen, Online-Archiv des Museums, Verzeichnis 01 Orte/Straßen/Im Sande/…/15.jpg

Das Feld bleibt, was es war: **nicht öffentlich**. Es steht nicht in `PhotoDetail`, also auch
nicht auf dem Schirm im Ausstellungsraum -- siehe Punkt 36.

## 51. Ein Feld, das an seiner Grenze endet, ist abgeschnitten

*Gemeldet am 16. August 2026.*

Bei 19 Fotos lautete der Bildnachweis „Förderkreis für Kultur und Brauc". Das sieht nach einem
Tippfehler aus und ist keiner: **Die Zeichenkette ist genau 32 Zeichen lang**, und 32 ist die
Längengrenze des IPTC-Feldes 2:80 (By-line). Nicht wir haben gekürzt -- das Programm, das die
Datei beschriftet hat, hat an seiner Feldgrenze aufgehört, und wir haben es unbesehen übernommen.

**Eine Angabe, deren Länge auf eine runde Zahl fällt, ist verdächtig**, und der Fall kostet
nichts nachzuzählen: Ein Blick auf die Byte- und Zeichenlänge der häufigsten Werte eines
Textfeldes zeigt ihn sofort. Hier war es der einzige; „August" bei neun Fotos ist mit sechs
Zeichen keine Feldgrenze, sondern eine unvollständige Eingabe und gehört damit zu Punkt 1.

## 52. Eine Vorgabe ist kein Befund

*Gelernt am 16. August 2026, an fünf falsch zugeschriebenen Fotos.*

Die Umwandlung nach JPEG reichte lange nur Farbprofil und Auflösung durch. Zwölf Fotos des
neueren Archivstands verloren dabei, was ihre Datei über sie sagte -- und **fünf davon trugen
danach den Bildnachweis "Sammlung Heimatmuseum Holm", wo "Hubert Wulf" hätte stehen müssen.**

Der Weg dorthin ist eine einzige Zeile im Import:

    credit=info.credit or settings.import_credit or None

Die Vorgabe aus der ``.env`` springt ein, wenn die Datei nichts sagt -- und das ist richtig so.
Falsch wurde es, weil die Datei etwas sagte und wir es unterwegs verloren hatten. **Der Ausfall
war damit nicht sichtbar**: Das Feld war gefüllt, es sah nach einer Auskunft aus, und eine falsche
Zuschreibung ist schlimmer als eine fehlende. Bei einem Museum ist sie die unangenehmste Sorte
Fehler überhaupt.

**Zwei Regeln folgen daraus.**

Erstens, für die Reparatur: Wo ein Feld genau den Vorgabewert trägt und die Datei etwas anderes
sagt, gewinnt die Datei. Eine Vorgabe ist eine Rückfallebene, keine Aussage, und darf deshalb
weichen -- anders als eine Angabe, die ein Mensch gesetzt hat.

Zweitens, für alles, was Daten von A nach B trägt: **Was auf dem Weg verloren geht, fällt nur
dort auf, wo hinterher eine Lücke steht.** Wo eine Vorgabe die Lücke füllt, wird aus dem Verlust
eine Behauptung. Die Probe darauf ist billig und heißt nicht "sind die Bytes mitgekommen", sondern
"liest unser eigener Leser aus der Kopie dasselbe wie aus der Quelle" -- so steht sie jetzt als
Test in ``test_to_jpeg.py``.

## 53. Das XMP des Archivs wird nicht gelesen -- nachgemessen, nicht vermutet

*Entschieden am 16. August 2026, nachdem der Gesamtbestand vorlag.*

`services/exif.py` liest EXIF und IPTC, kein XMP. Das stand als Punkt 55 im Backlog, mit einer
verlockenden Zahl: **251 der neuen Dateien tragen eine Ortsangabe in `Iptc4xmpCore:Location`**, und
40 der zurückgestellten wichen von unserem Ortsnamen ab, oft um eine Hausnummer, die uns fehlt.

**Vor dem Bauen wurde gemessen**, über alle 1322 Archivdateien unter `Straßen`. 1189 tragen XMP.
Das Ergebnis kehrt die Erwartung um:

| Feld | was wirklich drinsteht |
|---|---|
| `dc:creator` | „unbekannt", „Winter" -- kein Fotograf. Für „unbekannt" gibt es die Regel schon |
| `dc:description` | „Gebäude", „Abriss & Neubau", „Winterspaziergang" -- **Kategorien, keine Beschreibungen** |
| `Iptc4xmpCore:Location` | 515-mal genau das, was der Ordner schon sagt |
| `photoshop:Location` | 96-mal im Widerspruch zum ersten, meist ein stehengebliebener Stapelwert |

**Der Ertrag beim Ort, dem stärksten Feld, sind 26 Fotos** -- und davon tragen **neun denselben
Wert „Am Felde 5"**, der auch als veraltete `photoshop:Location` auf Fotos unter den Nummern 9,
10, 16 und 31 klebt. Zwei widersprechen dem Ordner, einer nennt statt einer Nummer den Gebäudenamen
(„Am Sportzentrum Geräteraum"). **Es bleiben eine Handvoll brauchbarer Angaben, jede einzeln zu
prüfen.**

Der Umbau des Lesers, eine Entscheidung über zwei widersprüchliche Ortsfelder und ein
Vorlage-Weg für 259 Konflikte -- für eine Handvoll Hausnummern, die ein Mensch ohnehin ansehen
müsste. **Das lohnt nicht.**

**Was der Durchgang stattdessen gebracht hat**, ist der Grund, warum er richtig war: Er hat einen
Ordner gefunden, der seine Straße wiederholt (`Hörnstraße/Hörnstraße 14`) und damit denselben
Adressabklatsch erzeugte, den Punkt 48 gerade abgeschafft hatte. **Erst messen, dann bauen** heißt
eben auch, dass die Messung etwas anderes findet als das Gesuchte.

## 54. Dubletten findet die Maschine, entscheiden muss ein Mensch

*Entschieden am 16. August 2026 -- Punkt 42, und die offene Frage darin war der Grad der
Selbsttätigkeit.*

Der SHA-256 erkennt eine Kopie der *Datei*. Er erkennt nicht denselben Papierabzug, zweimal
gescannt, und nicht denselben Scan, einmal groß und einmal klein gespeichert. Gefunden wird das
mit einem **Differenzhash über 256 Bit** auf den vorhandenen Vorschaubildern -- 876 000 Paare,
ein XOR je Paar, wenige Sekunden. Er erträgt Helligkeit, Farbstich und Verkleinerung.

**Die Schwelle ist angesehen, nicht gewählt.** Sechzig Paare durchgeblättert: bis Abstand 12
zweifelsfrei dasselbe Bild, bis 30 fast immer, bei 37 bis 40 immer noch die Mehrheit. Das Signal
reißt nicht ab, es wird unscharf -- also ist die Vorgabe großzügig (40) und ein Mensch
entscheidet.

**Vollautomatisch wäre falsch, und der Beweis stand in den Gruppen:**

* Zwei Fotos derselben Grundsteinlegung standen an **verschiedenen Adressen und in verschiedenen
  Jahren** -- Schulstraße 9/1971 gegen Lehmweg 8/1968. Eines war falsch abgelegt. Eine Maschine,
  die das größere behält, hätte die Frage nie gestellt.
* Bei einem Paar trägt die **kleinere** Fassung den eingebrannten Bildtext „Dörpshus vor dem
  Brand". Auflösung ist dort das falsche Kriterium.
* Auf einem von drei sonst gleichen Straßenbildern steht ein Lastwagen. Zwei Momente, keine
  Dublette.

**Der Umfang macht die Entscheidung leicht.** Es waren 44 Gruppen über 95 Fotos, nicht Hunderte.
Eine Vorlage-Liste mit 44 Zeilen ist in einer Viertelstunde durchgesehen; eine Automatik, die
gelegentlich das bessere Bild verliert, wäre nie wieder zu prüfen. Deshalb findet
``services/similar.py`` und schreibt nichts.

**Zusammengeführt wird vor dem Herausnehmen**, nicht danach: Titel, Beschreibung, Datierung, Ort,
Bildnachweis, Schlagwörter und der Archivpfad wandern auf das behaltene Foto, soweit ihm etwas
fehlt. Und „herausnehmen" heißt ``status = deleted`` -- aus der Ausstellung, nicht von der Platte
(Punkt 16). Wer sich vertut, holt es zurück.

**Zwei Schlagwörter blieben dabei absichtlich liegen.** „Bauernhaus von Paul Stein, im Jahre 1987.
Abriss 18.1.1988" ist kein Stichwort, sondern ein Satz aus der Kommazerlegung von Punkt 41. Ihn
auf das behaltene Foto zu tragen hiesse, den Fehler zu vermehren; am herausgenommenen bleibt er
stehen, verloren geht also nichts.

## 55. Ein Schlagwort ist kein Feld, sondern eine Menge

*Entschieden am 16. August 2026 -- Punkt 50, das Stapelschlagwort beim Import.*

Alle Stapelangaben des Importformulars folgen einer Regel: **sie füllen nur, was leer ist.** Jahr,
Koordinate, Ortsname, Bildnachweis, Herkunft -- wo die Datei es besser weiß, gewinnt die Datei.
Das ist richtig, weil jedes dieser Felder genau einen Wert hält: Füllen hiesse entscheiden.

**Für Schlagwörter gilt sie nicht, und die Regel umzubiegen wäre der Fehler gewesen.** Eine
Schlagwortliste hält keinen Wert, sondern eine Menge. Wer hundert Fotos aus einem Ordner
„Feuerwehr" hochlädt, will nicht *entweder* das Stapelwort *oder* das der Datei -- er will beides.
Das Stapelschlagwort tritt also **neben** das, was die Datei mitbringt, statt ihm zu weichen.

**Damit gibt es drei Quellen, und ihre Reihenfolge steht im Code**, bevor sie jemand sich
zusammenreimt:

1. ``KIEKMAP_IMPORT_TAGS`` -- gilt für jeden Import dieses Geräts, in Holm ``["Gebäude"]``
2. die Stichwörter aus der Datei selbst
3. das Stapelwort aus dem Formular

``add_tags`` überspringt, was das Foto schon trägt, und legt einen Namen nur einmal an. Die
Reihenfolge kostet deshalb nichts und entscheidet nur, wer einen Namen zuerst anlegt.

**Kommas trennen.** Das ist dieselbe Zerlegung, die bei Punkt 41 aus Bildunterschriften
Schlagwörter gemacht hat -- aber nicht derselbe Fall: Dort zerschnitt eine Maschine eine
Beschreibung, hier tippt ein Mensch in ein Feld, das „Schlagwörter" heißt.

## 56. Ein Jahrzehnt ist eine Datierung -- „vor 1978" ist keine

*Entschieden am 18. August 2026 -- Punkt 1.3, die Datierungen im Text.*

Die Bereinigungsrunde vom 11./12. August suchte im Text nach **vierstelligen Jahreszahlen**. Sie
fand 83 und übernahm 52. Was sie nicht suchte, war alles andere, womit Menschen datieren: „80er
Jahre", „in den 1930gern", „Winter 63", „Foto aus der Nachkriegszeit".

**Das war die größere Hälfte.** Nachgezählt am 18. August trugen 94 Fotos ohne Jahr eine
Datierung im Text; 44 liessen sich übernehmen, und die ergiebigste einzelne Fundstelle war eine
Ordnernotiz auf **achtzehn** Fotos: „Gebäude und Umgebung im Holm der 80er Jahre". Ein Jahrzehnt
ist kein unscharfes Jahr, sondern eine eigene Aussage -- ``date_precision`` kennt ``decade`` genau
dafür (Punkt 2 dieser Liste).

**„Vor 1978" dagegen wird nicht übernommen, und der Grund liegt im Zeitfilter.** Er fragt auf
Überlappung ab. Ein Foto mit dem Intervall 1880--1978 überlappt mit *jeder* Stellung des
Schiebers und stünde deshalb überall -- schlechter als undatiert, denn undatiert legt der
Beitragsbereich es wenigstens als Frage vor. Eine Datierung braucht beide Enden; wo eines erfunden
werden müsste, ist keine da.

**Zwei Muster sind dabei als eigene Fälle herausgekommen**, beide Verwandte von Punkt 49:

- **Die Jahreszahl des Archivstands.** „heute (2018) Marc Sieveking", „bis 2018 Besitzer", „2026
  Reitanlage Holm". Im Holmer Bestand ist „2018" fast nie ein Aufnahmejahr, sondern der Tag, an dem
  jemand das Archiv gepflegt hat. Fünfzehn Fotos.
- **Das nicht ausgeschriebene Jahr.** „Notiz: Schule 78" ist dieselbe Archivnotiz wie „Notiz:
  1978", nur zwei Zeichen kürzer -- und fiel durch, weil die Suche das zweistellige Jahr nur
  hinter einem Jahreszeitwort kannte („Winter 63"), nicht hinter einem Hausnamen. Dasselbe beim
  Monat: „März 73", „Notiz: 5.80". **Bei einer Suche nach Mustern bestimmt die Form des Musters
  den Befund**, nicht der Bestand -- und wer nur eine Schreibweise sucht, misst seine eigene
  Annahme. Die Gegenprobe dagegen ist billig: nachsehen, ob dieselbe Aussage anderswo in einer
  anderen Schreibweise steht, die man akzeptiert hat.
- **Das Scandatum in Prosa.** „Im Januar 2020 eingescannt von einem SW-Abzug von Olaf Sieveking."
  Dieselbe Falle wie das EXIF-Datum eines Scans, nur in einem Textfeld statt in einem Tag -- und
  ohne die Jahresgrenze aus ``services/exif.py``, die sie dort abfängt.

## 57. Der Kiosk heilt sich selbst — aber nur einmal

*Entschieden am 19. August 2026 — Backlogpunkt 59, gefunden beim Durchgang über den Code.*

Ein Fehler beim Rendern reißt in React den ganzen Baum ab, und übrig bleibt eine weiße Seite. Am
Schreibtisch ist das eine Unannehmlichkeit — man drückt Neu laden. Im Museum gibt es nichts zu
drücken: Chromium läuft unter `cage` ohne Tastatur, ohne Adressleiste, ohne Knöpfe. Und der
Leerlauf-Neustart, der sonst jeden verfahrenen Zustand heilt, sitzt in `MapView` und geht mit
unter. Die Vitrine steht dann weiß, bis jemand den Stecker zieht.

Also lädt die Seite sich selbst neu. Die einzige Frage, die dabei zu entscheiden war: **wie oft.**

**Genau einmal, dann redet das Gerät.** Ein Absturz, der beim Laden wiederkommt, liesse den
Bildschirm sonst endlos flackern — schlechter als eine Meldung, die jemand lesen kann. Nach dem
ersten selbsttätigen Versuch steht deshalb ein Satz da und ein Knopf darunter. Der Vermerk über den
letzten Versuch liegt im `sessionStorage`: Er übersteht das Neuladen und stirbt mit dem Tab, auf
dem Pi also spätestens beim morgendlichen Neustart — dieselbe Überlegung wie beim Admin-Token.

**Eine rückwärts gesprungene Uhr gilt als „lange her".** Der Pi hat keine Echtzeituhr; nach einem
Stromausfall kann seine Uhr um Jahre danebenliegen. Rechnete man stur vorwärts, wäre die
Selbstheilung damit dauerhaft abgeschaltet — genau der Zustand, den sie verhindern soll. Deshalb
zählt eine negative Differenz als abgelaufen. (Dieselbe Gerätewahrheit steht hinter dem Countdown
in `services/auth.py`.)

**Und der Zeitgeber wird nicht aufgeräumt — das ist der Fallstrick, nicht die Schlamperei.** Die
ordentliche Fassung hatte ein `componentWillUnmount`, das ihn löscht, und damit tat das Ganze
nichts: Nach dem Fangen baut React den Baum von Grund auf neu und nimmt die Fehlergrenze mit.
Gemessen an der Spur im Protokoll — „Timer gesetzt", „unmount" — und die Seite stand unverändert
da. Der Aufräumreflex ist richtig für einen Zeitgeber, der zu einer Ansicht gehört; er ist falsch
für einen, der zum Gerät gehört.

Was das kostet: Ein Absturz, den der Neuaufbau zufällig behebt, lädt acht Sekunden später trotzdem
neu. Für einen Kiosk ist das ohnehin die ehrliche Antwort — nach einem Absturz eine saubere Seite.

## 58. Gespeichert wird UTC, hinausgeschrieben mit Marker, gelesen als Wanduhr

*Entschieden am 19. August 2026 — Backlogpunkt 58, gefunden beim Durchgang über den Code.*

Alles, was dieses Programm speichert, ist UTC: `func.now()` in SQLite, die JSON-Zustandsdateien,
seit heute `dates.utc_now()`. Das war schon am 30. Juli entschieden, als die zweite Uhr
verschwand. Nur endete die Regel bisher an der Datenbank.

**Ohne Zonenmarker ist ein Zeitstempel keine Angabe, sondern eine Falle.**
`new Date("2026-08-18T19:25:21")` liest eine markerlose ISO-Zeit laut Norm als **Ortszeit**. Der
Verwaltungsbereich zeigte damit jeden Besucherbeitrag und jede Protokollzeile zwei Stunden zu
früh, und die Sicherungskachel konnte den Tag verschieben: Eine Sicherung um halb eins nachts ist
22:30 UTC vom Vortag.

**Der Marker gehört an das Ende, das die Zone kennt.** Drei Anzeigestellen im Browser umrechnen zu
lassen hiesse, dieselbe Regel dreimal hinzuschreiben — und die vierte, die jemand später
dazubaut, vergisst sie. Ein `UtcDatetime` in `schemas.py` sagt es einmal, und die Anzeige durfte
bleiben, wie sie war.

**Das `exif_datetime` bekommt ihn ausdrücklich nicht**, und darin liegt die eigentliche
Unterscheidung. Es kommt aus einer Kamera oder einem Scanner. Die schreiben die Wanduhr ihres
Standorts und wissen von keiner Zone; als Ortszeit gelesen ist der Wert genau richtig. Wer ihm UTC
aufstempelt, verschiebt einen Scan von 14:00 auf 16:00 und erfindet damit eine Tatsache. **Ein
Zeitstempel trägt nicht nur einen Wert, sondern eine Herkunft** — dieselbe Einsicht wie bei den
Feldern der Fotos, eine Ebene tiefer.

Daneben stand die zweite Uhr, die 30. Juli übersehen hatte: `reverted_at` kam aus `datetime.now()`
und war Ortszeit, während `created_at` aus SQLite kam und UTC war. Ein sofort zurückgenommener
Beitrag stand damit in der Datenbank zwei Stunden nach sich selbst — und **keine Prüfung im Schema
fängt so etwas**, weil beide Werte gültige Zeitstempel sind. Deshalb heißt die Uhr jetzt
`dates.utc_now()` und hat einen Namen, statt an drei Stellen einzeln hingeschrieben zu werden.

**Dateinamen sind die Ausnahme und tragen Ortszeit.** Der Ordner `vorher-2026-08-19-2230` und der
Name des heruntergeladenen Archivs werden von Menschen im Dateimanager gelesen, nicht von einem
Programm verglichen. Wer um halb eins nachts eine Sicherung zieht, sucht das heutige Datum. Die
beiden waren sich darin uneins; jetzt nicht mehr.

## 59. Eine Zahl in der Prosa ist ein Zitat oder ein Protokoll — geprüft wird die Buchführung

*Entschieden am 19. August 2026 — Backlogpunkt 62.*

Drei Prüfungen laufen neben den Tests, weil sie Dateien lesen, die kein Test je sieht. Sie liefen
bisher nur, wenn jemand daran dachte. Das Symptom stand in [index.md](index.md): „33
Entscheidungen" bei 56 und „21 Punkte" bei 17 — beides seit Wochen falsch, beides ohne Folgen,
beides von niemandem bemerkt.

Der naheliegende Schluss war, eine vierte Prüfung nachzählen zu lassen. **Nachgemessen war das
falsch.** Das Muster „N Punkte" trifft in dieser Dokumentation vier Stellen, und **keine einzige
davon darf berichtigt werden**:

- zweimal steht die alte, falsche Zahl absichtlich da — als Zitat, im Backlogpunkt selbst;
- zweimal sind Punkte auf einer Karte gemeint, keine Backlogpunkte;
- einmal steht in der Historie ein Satz, der an seinem Datum stimmte und stehenbleiben muss.

**Eine Zahl in laufendem Text ist fast nie eine Behauptung über den Jetztzustand.** Sie ist ein
Zitat oder ein Protokolleintrag, und beide werden durch eine Berichtigung falsch. Die zwei
Stellen, die wirklich aktuell sein sollten, haben ihre Zahlen deshalb verloren statt eine Prüfung
bekommen.

**Was sich prüfen lässt, ist die Buchführung des Backlogs über sich selbst.** Sie ist nicht Prosa,
sondern Struktur, und sie hat eine Zusage, die entweder gilt oder nicht: Jede je vergebene Nummer
ist entweder offen oder vergriffen — keine Lücke, kein Überhang, keine zweimal. Genau das heißt
„Nummern werden nie neu vergeben". `tools/check_numbers.py` rechnet das nach, dazu die Übereinstimmung
von Tabelle und Fließtext, den Anker jeder Zeile auf ihren *eigenen* Punkt, und das
ausgeschriebene Zahlwort vor der Liste.

Der Anlass ist Erfahrung, keine Vorsorge: Ein Punkt, der in die Historie zieht, verlangt vier
Bearbeitungen an drei Stellen. An einem Tag ist das viermal passiert.

**Und ein Ort, an dem sie laufen.** `make check` bündelt Stil, die vier Prüfungen und die Tests —
die schnellen zuerst. Daneben liegt der Hook unter `.githooks/pre-commit`, der **nur** die vier
Prüfungen ausführt und keine Testreihe: Die Tests laufen ohnehin, vergessen werden die vier, und
zusammen brauchen sie unter einer Sekunde. Ein Hook, den man merkt, wird abgeschaltet. Er ist je
Klon einzuschalten (`git config core.hooksPath .githooks`) — versioniert, aber nicht aufgedrängt.

Eine CI wäre der nächste Schritt und ist bewusst keiner: Sie setzt voraus, dass
[Punkt 22](backlog.md) entschieden ist. Ohne ein öffentliches Repo gibt es keinen Ort dafür.

## 60. Getestet wird, was still falsch sein kann — gerendert wird, was man sieht

*Entschieden am 19. August 2026 — Backlogpunkt 63, aufgelöst statt erledigt.*

Das Frontend hat rund fünfundzwanzig Komponenten und **keinen einzigen Komponententest**: kein
jsdom, keine Testing Library, kein Rendern im Test. Das war nie entschieden, sondern nur immer so
gemacht. Aufgeschrieben ist es jetzt, weil ein Durchgang von aussen sonst berechtigt fragt, was da
fehlt — und weil sonst der Nächste zwei Testrahmen dazulegt, ohne dass jemand widerspricht.

**Die Regel ist nicht „Komponenten werden nicht getestet".** Sie lautet: *Jede Entscheidung wandert
in eine reine Funktion und bekommt dort ihren Test — das Rendern bekommt keinen.*

Wo die Funktion wohnt, ist dabei gleichgültig. `PhotoLayer.test.ts` prüft `buildIndex` aus einer
`.tsx`-Datei, ohne irgendetwas zu rendern; die Datei ist kein Kriterium, die Frage ist, ob ein Wert
berechnet oder ein Knopf gezeichnet wird.

**Der Grund ist derselbe wie überall in diesem Projekt: Es wird geprüft, was *still* schiefgeht.**
Eine falsch gezeichnete Schaltfläche sieht falsch aus — dafür braucht es keinen Test, sondern einen
Blick. Ein falsch gerundetes Jahr sieht nach gar nichts aus; die Karte zeigt einfach etwas anderes,
und niemand erfährt je davon. Genau diese Sorte gehört in ein Modul.

**Gemessen, nicht behauptet:** Am 19. August 2026 ruft **jedes `useMemo` in einer Komponente eine
importierte reine Funktion auf** — `offeredDecades`, `buildIndex`, `groupStreets`, `axisBounds`,
`blocksOf(groupByBase(…))`. Sechzehn reine Module tragen die Entscheidungen, die Komponenten die
Darstellung. Die Praxis hielt also, bevor sie hier stand.

**Eine Lücke fand sich beim Aufschreiben doch**, und sie war genau die beschriebene Sorte: Der
Zeitschieber rechnete die Fingerposition selbst in ein Jahr um — Klammern und Runden, inmitten der
Komponente. Ein Rundungsfehler dort wählt 1931, wo der Besucher auf 1932 gezielt hat, und auf dem
Bildschirm sieht nichts falsch aus. Das ist jetzt `yearAtFraction` in `timeAxis.ts`, die Umkehrung
von `fraction`, und der Test prüft genau das: Jedes Jahr der Achse muss aus seinem eigenen Anteil
wieder herauskommen.

**Wo die Grenze verläuft**, zeigt der Gegenfall aus derselben Messung: Die Größe eines Kreises auf
der Karte (`48 + log10(Anzahl) × 26`) bleibt in `PhotoLayer.tsx`. Sie ist auch eine Rechnung — aber
ein falscher Wert ergibt einen Kreis, der falsch *aussieht*. Sichtbar falsch braucht keinen Test.

**Warum kein jsdom.** Es wäre ein nachgebauter Browser, und geprüft würde der Nachbau. Was am
Rendern dieses Programms wirklich schiefgehen kann, prüft jsdom ohnehin nicht: ob die Seite offline
null fremde Herkünfte anfragt, ob ein Kreis unter einem Vorschaubild noch mit dem Finger zu treffen
ist, ob eine Beschriftung auf dem Gerät im Ausstellungsraum lesbar bleibt. Das erste ist ein
Einzeiler in den Entwicklerwerkzeugen, das zweite wurde am Inline-`transform` nachgemessen, das
dritte ist [Punkt 14](backlog.md) und braucht einen Menschen vor dem Bildschirm.

Ein zweiter Testrahmen für das, was ein Blick beantwortet, kostet Abhängigkeiten, Laufzeit und
Pflege — und liesse ausgerechnet die Prüfungen ungetan, auf die es hier ankommt.

## 61. Ein Paket mit einer Tür — und die Tests bleiben, wie sie waren

*Entschieden am 19. August 2026 — Backlogpunkt 60.*

`services/backup.py` hatte 938 Zeilen und tat sechs Dinge: Laufwerke finden, auf den Stick
sichern, das Archiv im Strom bauen, wiederherstellen, die Zustandsdatei führen, den einen Auftrag
verwalten. Jedes Stück war begründet, die Grenzen standen sogar schon da — als Kommentarbalken.
Es war die einzige Datei im Backend, die ihren Namen überwachsen hatte.

**Die Bedingung, unter der der Umbau überhaupt lohnte, war: Die Tests dürfen sich nicht ändern.**
Daneben liegen 908 Zeilen Testcode, und sie sind der einzige Beweis, dass eine Umschichtung nichts
kaputtmacht. Wer sie mit umschreibt, hat den Beweis weggeworfen und muss dem Ergebnis glauben.

Deshalb ein **Paket mit einer Tür**: `app/services/backup/__init__.py` reicht genau die Namen
durch, die der Rest des Programms benutzt. `from app.services import backup` heißt weiterhin, was
es hiess; keine Importzeile in `api/`, in `watcher.py` oder in den Tests hat sich bewegt. Am Ende
sind **sechs Zeilen** in den Tests anders, und keine davon ist eine Zusage: Es sind die Stellen,
an denen `monkeypatch` einen privaten Namen umsetzt, jetzt `backup.drives._is_mounted` statt
`backup._is_mounted`. Ein Test, der in einen privaten Namen greift, greift damit sichtbar in ein
bestimmtes Modul — das ist ehrlicher als vorher, nicht weniger ehrlich.

**Was die Aufteilung ans Licht brachte**, hätte man vorher nicht gesehen: Die Wiederherstellung
setzte den Größen-Zwischenspeicher mit `global _size_cache` zurück. Das funktioniert nur, solange
beide in derselben Datei stehen — die Trennung machte daraus `collection.forget_size()`, und
damit aus einem stillen Zugriff eine benannte Handlung.

**Wer zwischen Modulen gebraucht wird, verliert den Unterstrich.** `copy_if_new`, `vacuum_into`,
`human_size`, `manifest_bytes`: Der fehlende Unterstrich ist die Auskunft „das benutzt jemand
anderes", und der vorhandene bleibt dort, wo er stimmt — `_swap_in`, `_set_aside`, `_ArchiveStream`
sind weiterhin die Sache ihres einen Moduls.

**Und die Warnung von gestern gilt weiter**, sie hat sich nur erledigt: Der Umbau gewinnt nichts,
was ein Besucher merkt. Er war fällig, weil die Datei ihren Namen überwachsen hatte — nicht, weil
etwas falsch war. Wer in dieser Lage steht, sollte zuerst prüfen, ob die Tests einen Umbau
*tragen*; tun sie es nicht, ist das Aufteilen der zweite Schritt und nicht der erste.

## 62. Apache-2.0 — weil das Projekt zum Übernehmen gebaut ist

*Entschieden am 20. August 2026 — Backlogpunkt 23.*

Die Wahl war frei: Von 169 Fremdpaketen ist **kein einziges Copyleft**, gemessen an den
installierten Paketen statt an den Manifestdateien. Keine Abhängigkeit schreibt etwas vor, keine
verhindert eine Veröffentlichung. Zur Wahl standen MIT, BSD-3-Clause, Apache-2.0, MPL-2.0,
EUPL-1.2 und die GPL-Familie.

Drei Ziele gaben den Ausschlag — andere sollen es nutzen können, Rückmeldungen und Mitwirkung
sollen möglich sein, der Name soll mitgehen —, und ein Vorbehalt: Sorge vor rechtlichen
Auseinandersetzungen.

**Ausschlaggebend war §4.2, und der Grund steht in [adaption.md](adaption.md).** Dieses Projekt ist
ausdrücklich dafür gebaut, dass ein zweites Museum es übernimmt; eine ganze Datei erklärt Schritt
für Schritt, wie. Apache verlangt, dass **geänderte Dateien als geändert gekennzeichnet** werden.
Eine Übernahme, die schiefgeht, bleibt damit sichtbar eine Übernahme und nicht „Kiekmap". Genau das
schützt den Namen, an dem die Sichtbarkeit hängt. MIT gibt das nicht her.

**§5 erledigt die Beitragsfrage, bevor sie entsteht.** Beiträge stehen ohne weitere Vereinbarung
unter derselben Lizenz. Bleiben sie aus — wahrscheinlicher als erhofft, so sind Nischenprojekte —,
hat es nichts gekostet.

**§4.1 und §4.4** verlangen Copyright-Vermerk *und* NOTICE-Datei bei jeder Weitergabe. Mehr
Namensnennung gibt eine permissive Lizenz nicht her.

**Was nicht den Ausschlag gab, obwohl es so aussieht:** die ausführlichere Freizeichnung in §§7–8.
Sie liest sich beruhigender als MITs zwei Sätze, bewirkt in Deutschland aber kaum mehr — § 276
Abs. 3 BGB und das AGB-Recht begrenzen beide gleich. Was das Risiko klein hält, ist die
Unentgeltlichkeit, nicht die Klausel. Und der Patentgrant in §3 ist hier gegenstandslos: An einer
Fotoverwaltung mit Karte ist nichts patentiert. Sein Wert liegt darin, die Frage gar nicht erst zu
haben.

**Verworfen:**

- **MIT** wäre die naheliegendste Wahl für ein Projekt dieser Größe und ist es fast geworden. Es
  fehlen ihr genau die drei Paragrafen oben. Der Unterschied in der Praxis ist klein, der
  Unterschied bei einer missratenen Übernahme nicht.
- **BSD-3-Clause** schützt den Namen nur gegen Werbung, nicht gegen Verwechslung.
- **MPL-2.0** und **EUPL-1.2** — schwaches Copyleft, beide vertretbar. Die EUPL hat einen
  verbindlichen deutschen Text und passt kulturell; sie ist international aber so unbekannt, dass
  sie eher abschreckt, als Beiträge einbringt. Das Ziel war Verbreitung, nicht Rückfluss.
- **GPL-3.0/AGPL-3.0** — starkes Copyleft. Für einen Offline-Kiosk greift die AGPL ohnehin nicht,
  und die GPL erschwert einer Einrichtung genau das, was hier erwünscht ist.

**Eine Lizenz für alles**, Code wie Dokumentation. Getrennt wäre genauer — Code-Lizenzen reden von
„the Software" und von Patenten, was auf 9.400 Zeilen Prosa schief liegt —, und der nächste
Verwandte macht es so (CollectionBuilder: MIT plus CC-BY-SA für die Doku). Es verschafft aber
niemandem mehr Rechte: Eine permissive Lizenz über dem ganzen Repo erlaubt das Kopieren und
Anpassen der Doku bereits. Zwei Dateien und eine Abgrenzungsregel wären Verwaltung ohne Gewinn.

**Was die Entscheidung ausdrücklich nicht berührt: den Fotobestand.** Eine Softwarelizenz
lizenziert das Programm, nicht die Daten. Das steht samt der ODbL-Frage beim Ortsverzeichnis in
[licensing.md](licensing.md) — der Datei, die es seit dieser Entscheidung gibt.

---

## 63. Die Historie wird nicht aufgeteilt, sondern erschlossen — über ihr Datum

*Entschieden am 21. August 2026 — Backlogpunkt 64, Abschnitt 3.*

`history.md` ist mit 3.858 Zeilen die größte Datei im Repo und wächst mit jedem Arbeitsschritt.
Die Frage war, ob sie aufzuteilen ist — nach Jahr, nach Thema — oder ob eine Datei, die niemand von
vorn liest, lang sein darf.

**Nachgemessen war die Länge nicht das Problem.** 90 Abschnitte, der mittlere 55 Zeilen lang, alle
in einer Reihenfolge, die nie umsortiert wird. Eine Aufteilung nach Jahr wäre gegenstandslos — das
Projekt ist vier Monate alt. Eine nach Thema würde das Einzige zerstören, was diese Datei
gegenüber [CHANGELOG](../CHANGELOG.md) und den Entscheidungen voraushat: **die Reihenfolge.** Und
sie brächte bei jedem Anhängen eine Frage mit, die es heute nicht gibt — *in welche Datei?* —,
deren falsche Antwort niemandem auffällt.

**Das Problem war ein anderes, und es war messbar:** 31 Verweise aus anderen Dateien zeigten auf
`history.md`, **30 davon ohne Anker** — also auf 3.858 Zeilen. Ein Verweis, der nichts eingrenzt,
ist kaum ein Verweis. Dazu kam, dass die Datei keinen Eingang hatte: Wer sie öffnete, stand vor
einer Wand.

**Also erschlossen statt zerteilt**, in drei Schritten:

1. **Ein Register am Anfang**, eine Zeile je Abschnitt, mit Datum und Sprungmarke. Es ersetzt die
   Tabelle der Arbeitsblöcke, die eine Commit-Spanne nannte und seit fünfzig Abschnitten falsch war.
2. **Das Datum ist der Eingang, nicht der Titel.** Gesucht wird ein Tag — *„was war um den
   Neunten?"* —, selten eine Überschrift; die Titel hier sind Merkhilfen. Für ein Stichwort ist
   `grep` das bessere Werkzeug, und die Datei ist ausführlich genug dafür.
3. **Die acht Verweise, die eine bestimmte Stelle meinten, zeigen jetzt dorthin.** Die übrigen
   meinen wirklich die ganze Datei und bleiben, wie sie sind.

**Damit steht eine Zusage, und sie hat eine Prüfung:** *Jeder Abschnitt nennt sein Datum in den
ersten Zeilen darunter.* Neun Abschnitte taten das nicht — die neuesten, in denen die Gewohnheit
eingeschlafen war. `tools/build_register.py` erzeugt das Register und **bricht ab**, wenn ein
Abschnitt kein Datum nennt, nach dem Vorbild von `build_seed.py` und `build_notices.py`: Neunzig
Zeilen von Hand sind in einem Monat falsch, und ein Register, das einen Abschnitt still auslässt,
ist schlimmer als keins.

**Eine Regel über Datumsangaben, ohne Ausnahme:** Ein Abschnitt erbt das Datum seines Teils, und
ein Teil, der keins nennt, gibt keins weiter. Die Teile I bis V sind abgeschlossene Blöcke —
niemand hat notiert, an welchem Tag Stufe 4 gebaut wurde, nur dass der Block vom 28. bis zum
30. Juli lief; also sagt der Block es einmal, und seine achtzehn Abschnitte erben es. Teil VI ist
ein Tagebuch und nennt kein eigenes Datum; seine Abschnitte müssen ihres deshalb selbst nennen,
und die Sperre fängt den, der es vergisst. Die Spanne von Teil VI rechnet das Register aus seinen
Abschnitten aus — so kann sie nicht wieder veralten.

**Verworfen: das Datum aus Git zu ziehen.** Es wäre eine Messung statt einer Behauptung, aber es
misst das Falsche. Git datiert das Aufschreiben, nicht die Arbeit: Für alle 28 Abschnitte der
Teile I bis V meldet es den 2. August, den Tag, an dem sie aus drei Plandokumenten
zusammengeführt wurden. Dazu kommt, dass ein umgeschriebener Verlauf alle Datumsangaben auf einmal
verschiebt — am Tag zuvor war genau das passiert.

---

## 64. Die Umlautregel gilt für die Dokumentation — und wird jetzt geprüft

*Entschieden am 22. August 2026 — Backlogpunkt 64, Abschnitt 4.*

Die Sprachregelung sagt: Umlaute werden in Texten für Menschen normal geschrieben und nur im
Quelltext, in Shell-Skripten und in Commit-Nachrichten umschrieben. Die Dokumentation hielt sich
nicht daran, und die Frage war, ob die Regel der Praxis folgen soll.

**Nein — gemessen war es nicht die Praxis, sondern zwei Dateien.** Elf von dreizehn halten die
Regel makellos ein (zusammen acht umschriebene Wörter); `decisions.md` und `history.md` standen
bei 338 und 568. In `history.md` liegt die Drift ausserdem nicht gleichmäßig, sondern in einer
Strecke Arbeit, in der die Regel für Quelltext auf die Dokumentation übergriff. Eine Regel, die
elf Dateien trägt, wird nicht wegen zweier aufgegeben.

**Dasselbe gilt für `ß`.** 177 Stellen schrieben `ss`, wo ein `ß` hingehört, in denselben zwei
Dateien, die daneben 268 Mal ein richtiges `ß` tragen. Die Regel erlaubt `ss` ausdrücklich, aber
sie erlaubt es nicht *im selben Absatz wie das Gegenteil*. Beides ist in einem Durchgang
nachgezogen worden, rund 900 Ersetzungen, gegen eine Ausnahmeliste echter `ue`-Wörter — `neue`,
`Quelle`, `Feuerwehr`, `dauert` und rund dreißig weitere, die eine naive Ersetzung zerstört hätte.

**Und der eigentliche Fund: `tools/language_check.py` prüfte das nie**, obwohl
[development.md](development.md) direkt unter dem Umlaut-Absatz sagt, es tue das. Das Werkzeug
las nur `.py`, `.ts` und `.tsx` und beantwortete eine andere Frage — in welcher Sprache ein
Kommentar geschrieben ist. Es prüft jetzt beides. **Eine Zusage, die niemand nachrechnet, ist
keine Regel, sondern eine Absicht** — das ist derselbe Satz, der schon
`tools/check_numbers.py` und `tools/build_register.py` begründet hat.

**Drei Dinge sind ausgenommen, und jedes hat seinen Grund:** umzäunte Blöcke und Codespannen, weil
dort Bezeichner und Kommandos stehen und die Umschreibung dort richtig ist; und Zitiertes, weil
CLAUDE.md eine umschriebene Meldung als eigenes Beispiel der Regel führt. Die Liste der gesuchten
Formen ist mit Absicht kurz gehalten — sie läuft im Commit-Hook, und eine einzige Fehlmeldung
genügt, damit jemand die Prüfung abschaltet.

---

## 65. Die fünf Dateien einer Veröffentlichung, und was in ihnen nicht steht

*Entschieden am 22. August 2026 — Backlogpunkt 64, Abschnitt 4.*

`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS` und Meldungsvorlagen unter
`.github/`. Zwei Entscheidungen darin sind keine technischen.

**Keine Adresse im Klartext.** Eine E-Mail in `SECURITY.md` wird abgegriffen und steht danach in
jedem Fork und jedem Archiv, auch wenn sie hier längst gelöscht ist. Sicherheitsmeldungen laufen
deshalb über die private Meldung bei GitHub. Das kostet nichts — der Weg ist nicht öffentlich,
geht nur an den Betreuer, und er taugt zugleich als der eine vertrauliche Kanal, den auch der
Verhaltenskodex braucht. Er setzt voraus, dass das Repo bei GitHub liegt, was
[Punkt 22](backlog.md) ohnehin plant.

**Kein Contributor Covenant, sondern fünfzehn Zeilen in der Stimme des Projekts.** Der Covenant
ist der erkannte Standard, und der Wechsel steht als nächster Schritt im Kodex — aber heute gibt
es hier keine Gemeinschaft und keinen zweiten Betreuer. Ein Kodex, der Verfahren beschreibt, die
niemand durchführt, ist eine Zusage ohne Deckung; das im Text auszuschreiben ist ehrlicher als
130 importierte Zeilen. Nebenbei entfällt damit die Frage nach der CC-BY-4.0-Attribution, unter
der der Covenant steht.

**Das Leitmotiv aller fünf: eine Veröffentlichung darf keine stille Zusage werden.** Deshalb steht
in `CONTRIBUTING.md`, dass es einen Betreuer nebenher gibt und eine Meldung Wochen liegen bleiben
kann, und in `SECURITY.md` eine Liste dessen, was **kein** Fund ist, sondern Entwurf: die
Besucheransicht ohne Anmeldung, der Beitragsweg ohne Ratenbegrenzung, der unverschlüsselte
Bestand. Wer das liest, weiß, worauf er sich einlässt — und das ist mehr wert als der Eindruck
eines gepflegten Projekts.
