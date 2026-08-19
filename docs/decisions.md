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

Solange „Wo ist das?" steht, war **die ganze Karte scharf**: Jeder Tipp auf eine freie Flaeche
setzte einen Punkt. Seit dem 9. August 2026 muss der Besucher das erst verlangen — ueber den Knopf
**„Auf der Karte zeigen"**. Vorher passiert bei einem Tipp auf die Karte nichts.

**Der Grund ist die Datenqualitaet, nicht die Sauberkeit.** Wer waehrend der Frage nur schauen will
— die Karte verschieben, sich orientieren, ein Foto in der Naehe suchen —, beantwortete sie dabei
versehentlich. Und sobald ein Punkt stand, bot der Bereich **„Hier war das"** an: ein Tipp daneben,
ein bestaetigender Tipp danach, und im Bestand stand eine Verortung, die niemand gemeint hat.

**Es ist immer nur ein Weg auf dem Schirm.** Wer die Karte scharf schaltet, dem verschwindet die
Strassenwahl; wer zurueckgeht, bekommt sie wieder. Nebeneinander standen sie sich im Weg: Das
Knopfraster wirft bei der naechsten Beruehrung weg, was der Kartentipp gerade gesetzt hat. Der
Knopf steht deshalb **ueber** der jeweiligen Auswahl, nicht darunter — er ist die Alternative *zu*
ihr, und darunter laese er sich als letzter Ausweg nach dem Scrollen.

**Angeboten wird er in jedem Schritt, auch bei der Hausnummer**, und dort verdient er am meisten:
Wer die Strasse kennt, die Nummer aber nicht, zeigt auf das Haus statt „Reicht so" zu druecken.
Danach ist die Nummernfrage hinfaellig — ein Punkt auf der Karte sagt mehr als eine Zahl aus einer
Liste.

**Zwei Dinge bleiben unabhaengig davon scharf.** Der gesetzte Punkt wird immer gezeichnet und laesst
sich immer ziehen, gleich wer ihn gesetzt hat — sonst gaelte die Zusage „Der Punkt laesst sich auf
der Karte noch verschieben" fuer den Punkt aus der Strassenwahl nicht mehr. Im Code sind das
deshalb zwei Bedingungen und nicht eine (`armed` und `active` in `kiosk/PinLayer.tsx`).

**Ohne Ortsverzeichnis gibt es keine zweite Wahl** — dann ist die Karte von Anfang an scharf, denn
sonst waere der Bereich unbedienbar. Das trifft eine Einrichtung, die `make places` nie gelaufen
hat. [Punkt 24](#24-die-straße-wird-gewählt-nicht-getippt) sagt, was weiter drauszen liegt, werde
„auf der Karte angetippt"; das gilt weiter, kostet jetzt aber einen Knopfdruck vorher.

**Der Schalter liegt im Store, nicht in der Komponente.** `LocationTask` wird bei fast jedem
Fotowechsel abgebaut, ein `useState` faellt dort also von selbst zurueck — nur nicht auf dem einen
Weg, auf dem `load()` zur urspruenglichen Frage zurueckfaellt, weil die andere leergelaufen ist.
Genau dieser Fall tritt ein, wenn eine Art von Luecke abgearbeitet ist, und er hinterliesze eine
scharfe Karte ueber einem Foto, das der Besucher noch nicht angesehen hat.

---

## 28. Fotos ohne Jahr sind ein Schalter, keine Nebenwirkung

Ein Foto ohne Datum ueberlappt keinen Zeitraum. Es fiel damit aus **jeder** Auswahl heraus, sobald
der Besucher den Schieber auch nur ein Stueck zusammenzog — bei diesem Bestand zwei Drittel der
Sammlung, ohne dass irgendwo gestanden haette, dass das passieren wuerde. Seit dem 9. August 2026
steht neben dem Schieber ein Schalter: **„507 Fotos ohne Jahr anzeigen"**, mit Haken.

**Die Zahl stand ohnehin dort.** Sie war bisher eine Meldung; jetzt ist sie die Beschriftung einer
Handlung. Das ist der ganze Trick an der Stelle — es kommt kein Bedienelement hinzu, ein
vorhandenes bekommt einen Zweck.

**Eingeschaltet heiszt „kein Datum ODER Ueberlappung".** Der Zeitraum gilt dann nicht mehr fuer
alles, was auf dem Schirm steht. Das ist eine echte Einbusze an Genauigkeit, und sie ist
vertretbar, weil der Besucher sie sieht und sie selbst eingestellt hat. Die Gegenrichtung — der
Schalter wirkt nur, wenn ohnehin kein Zeitfilter geht — waere eine Anzeige gewesen und kein
Schalter: Beim ersten Anfassen des Schiebers waeren die Fotos trotzdem verschwunden.

**Er steht anfangs an und geht genau einmal von selbst aus** — beim ersten Zusammenziehen des
Zeitraums. Das ist der Moment, in dem die Auswahl anfaengt, etwas zu bedeuten: Bis dahin hat der
Besucher nichts eingestellt, ab da schon. Der Anfangszustand zeigt also alles, was das Museum hat,
und niemand verliert etwas, ohne es getan zu haben.

**Danach gehoert der Schalter dem Besucher.** Wer ihn von Hand wieder einschaltet, bei dem bleibt
er an, auch beim naechsten Zug am Schieber. Ginge er jedes Mal wieder aus, waere genau die
Nebenwirkung zurueck, gegen die dieser Punkt gebaut ist — nur eine Ebene hoeher und aergerlicher,
weil sie eine Entscheidung ueberschriebe, die jemand gerade getroffen hat. Im Store steht dafuer
ein zweiter Wert (`undatedByHand`), der nie zurueckfaellt.

**Wonach die Automatik greift, ist `queryTimeFilter`** — dieselbe Funktion, die entscheidet, ob
ueberhaupt ein Zeitfilter zum Backend geht. Damit geht der Schalter exakt dort aus, wo sonst Fotos
anfingen zu verschwinden. Eine zweite, eigene Regel dafuer waere eine zweite Wahrheit gewesen.

**Das Histogramm zaehlt die undatierten Fotos immer mit**, gleich wie der Schalter steht. Sonst
stuende dort nach dem Abschalten eine Null, das Etikett verschwaende — und mit ihm der einzige Weg
zurueck.

Der Schalter ist ein Knopf mit gezeichnetem Kaestchen, kein `input[type=checkbox]`: Der ist rund
13 px grosz, die Zielgruppe braucht 48. Die Kopfzeile des Schiebers ist dadurch hoeher geworden;
was das fuer die drei Elemente der oberen Zeile bedeutet, gehoert zu Punkt 29 im
[backlog.md](backlog.md).

---

## 29. Unter dem Vorschaubild steht die Adresse, nicht das Datum

Unter jedem Vorschaubild auf der Karte stand die fertige Datumsangabe. Seit dem 9. August 2026
steht dort **Adresse und Jahr**: „Lehmweg 17b — 1953", und wo kein Jahr bekannt ist, „Im Sande 18"
allein.

**Die alte Zeile war an dieser Stelle zweimal falsch.** Unter den 256 Kameraaufnahmen stand
„22. März 2014" — der Tag ist auf einer Uebersichtskarte nie der Punkt. Und unter den rund 670
Fotos ohne Datierung stand „Jahr unbekannt", siebenhundertmal dieselbe Zeile: eine Fehlanzeige, die
ueber siebenhundert Bilder nichts sagt.

> **Nachtrag vom 12. August 2026 — dieser Punkt ist abgeloest.** Die Beschriftung nimmt jetzt
> **den Titel** und faellt auf die Adresse zurueck; siehe Punkt 39 unten. Die Begruendung darunter
> ist nicht falsch geworden, sondern gegenstandslos: Sie stand auf einem Bestand, in dem 815 Titel
> die Adresse daneben wiederholten und achtzehn „Intel(R) JPEG Library" hiessen. Das ist
> aufgeraeumt. Was hier ueber **Stapel** und ueber die **wegfallende Zeile** steht, gilt
> unveraendert weiter.

**Warum die Adresse und nicht der Titel**, obwohl der naheliegender klingt: Der Bestand hat es
entschieden. Alle 922 vorhandenen `place_name` bleiben unter dreissig Zeichen — die laengste ist
„Uetersener Straße 12". 105 Titel sind laenger als vierzig Zeichen, und achtzehn lauten
„Intel(R) JPEG Library, version […]". Die Adresse passt also immer unter ein Vorschaubild, der
Titel oft nicht. Dass die Position auf der Karte die Adresse schon ungefaehr verraet, spricht nicht
dagegen: Auf einer Dorfkarte sieht man die Strasse, nicht die Hausnummer.

**Ein Stapel bekommt die Adresse, aber kein Jahr.** Fotos landen auf einem Marker, weil sie eine
Koordinate teilen — und das heisst hier: dieselbe Adresse. Einundfuenfzig Bilder von Schulstraße 2
sind alle von Schulstraße 2. Ihre Jahre sind nicht geteilt; das oberste zu nehmen setzte ein Datum
unter fuenfzig Fotos, die es nicht tragen. Die Adresse wird nur behauptet, wo **alle** Fotos des
Stapels sie teilen: Zwei ueber EXIF verortete Aufnahmen koennen auf einen Meter zusammenfallen,
ohne miteinander zu tun zu haben.

**Fehlt beides, faellt die Zeile weg** — kein Gedankenstrich, keine Fehlanzeige. Eine leere Stelle
unter einem Bild verlangt nichts vom Besucher.

**Die kurze Datumsform gehoert ins Backend**, neben `format_label` (`services/dates.py`), nicht als
Zeichenkettenschnipselei ins Frontend. Sie kuerzt Tag und Monat auf das Jahr, laesst ein Jahrzehnt
ein Jahrzehnt („1930er" wird nicht „1930" — das erfaende eine Genauigkeit) und gibt fuer
Undatiertes eine leere Zeichenkette.

**`PhotoMarker` traegt dafuer den `place_name`, und das ist die eine bewusste Ausnahme** von seiner
Regel, moeglichst wenig zu tragen. Der Preis wurde gemessen statt geschaetzt: Bei fuenfhundert
Markern sind das rund 13 kB, auf einem Geraet, das seine Karte aus dem Nebenzimmer bekommt. Fuer
alles andere gilt die Regel weiter.

**Die Beschriftung fuer Vorlesewerkzeuge behaelt das volle Datum.** Dort stoert die Genauigkeit
nicht, und wer sich die Karte vorlesen laesst, hat den Marker nicht im Blick. Deshalb liefert der
Marker beide Formen.

**Der Erstbestand ist inzwischen aufgeraeumt** (11. und 12. August 2026, siehe
[history.md](history.md)), und damit ist die Voraussetzung dieser Entscheidung entfallen: Die Titel
sind keine Adressen mehr. **Am 12. August ist sie deshalb neu getroffen worden** — die Beschriftung
nimmt jetzt den Titel und faellt auf die Adresse zurueck; siehe Punkt 39 unten.

---

## 30. Vier Rollen, und jede sieht wie ein Knopf aus

Der „Hilf mit"-Bereich ist ueber mehrere Stufen gewachsen, und man sah es: zwanzig Knoepfe in fuenf
Formen, ohne dass die Form gesagt haette, was der Knopf tut. Seit dem 9. August 2026 gibt es **vier
Rollen**, und mehr sollen es nicht werden:

| Rolle | Form | Symbol | Beispiele |
|---|---|---|---|
| **auswaehlen** | weiss mit Rand | — | Buchstabe, Strasse, Jahrzehnt, Jahr, Hausnummer, Abschnitt, „Auf der Karte zeigen" |
| **uebernehmen** | gefuellt, Akzentbraun | Haken | „Hier war das", „Ganze 1920er Jahre", „Reicht so — die Strasse genuegt" |
| **zurueck** | weiss mit Rand, graue Schrift | Pfeil links | „Anderer Buchstabe", „Anderes Jahrzehnt", „Doch nicht — von vorn", „Punkt entfernen" |
| **ueberspringen** | wie zurueck, durch eine Linie abgesetzt | Pfeil rechts | „Weiss ich nicht — naechstes Foto" |

**Die randlose Form ist weg.** Sie war grau, ohne Rand und las sich als Text — fuer eine
Zielgruppe, die einmal im Jahr vor diesem Geraet steht, genau das Falsche. Leiser wird ein Knopf
jetzt ueber die Schriftfarbe, nicht ueber die Form; Rand und Hoehe sind bei allen gleich, und die
gemessene Mindesthoehe liegt bei 54 px.

**Die wichtigste Grenze verlief an der falschen Stelle.** Dieselbe leise Form trug *zurueckgehen*
und *ueberspringen* — das eine bleibt beim Foto, das andere legt es weg. „Weiss ich nicht —
naechstes Foto" sieht deshalb aus wie „Anderer Buchstabe" und ist durch eine Linie davon getrennt:
Was ueber der Linie steht, gehoert zur Frage, was darunter steht zum Foto. Der Abstand liegt
ueberwiegend ausserhalb des Knopfes, damit kein mittippbarer Streifen ueber der Beschriftung
entsteht.

**„Reicht so — die Strasse genuegt" ist eine Antwort und sieht seitdem danach aus.** Es war ein
schlichter weisser Knopf, waehrend „Hier war das" gefuellt war — obwohl beide dasselbe tun:
abschliessen. Nicht jedes Haus steht in OpenStreetMap, und wer die Nummer nicht kennt, soll das
ohne Zoegern sagen koennen. Konkurrenz entsteht dabei nicht: In diesem Schritt steht kein zweiter
gefuellter Knopf auf dem Schirm.

**Symbole neben der Beschriftung, nie an ihrer Stelle.** Ein Piktogramm allein verlangt Vorwissen,
das aeltere Besucher nicht mitbringen muessen; neben den Worten muss es nur bestaetigen, was
gelesen wurde. Deshalb ist der Satz klein — Haken, Pfeil links, Pfeil rechts, Fadenkreuz —, und
alles andere traegt keins. Ein Symbol auf jedem Knopf waere Zierde, und Zierde erklaert nichts.

**Gezeichnet, nicht geladen** (`kiosk/icons.tsx`): kein Symbolzeichensatz, kein CDN, kein Sprite
aus dem Netz. Das Geraet ist offline, und ein Symbol, das nicht laedt, hinterlaesst einen Knopf,
der nichts sagt.

**Der Verwaltungsbereich bleibt ausdruecklich draussen.** Er hat eigene Masze, wird ein- bis
zweimal im Jahr benutzt und folgt einer anderen Regel: Dort zaehlt Klartext mehr als Kompaktheit.
Die alte leise Form steht deshalb noch — fuer „Zurueck zur Karte" am Zahlenfeld, das aus der
Verwaltungstuer herausfuehrt und zu keiner Besucherfrage gehoert.

Was daran haengt: [backlog.md](backlog.md), Punkt 10. Der Schliessen-Knopf der Detailansicht war
an die Blaetterknoepfe gebunden, damit die Ansicht *eine* Knopfform kennt. Jetzt gibt es vier
benannte Rollen, und keine heisst „schliessen" — welche er bekommt, ist dort zu entscheiden.

---

## 31. Der Kopfbereich steht auf einer Mittellinie, der Zeitraum auf einem Boden

Zwei Aenderungen an derselben Zeile, beide am 9. August 2026, und beide ersetzen eine Rechnung
durch eine Regel, die sich selbst traegt.

**Wappen, Titel und Zeitschieber richten sich senkrecht mittig aus.** Sie standen oben buendig und
endeten fast fuenfzig Pixel auseinander. Das CSS behauptete an der Stelle das Gegenteil: Ein
Kommentar rechnete vor, dass beide Titelzeilen zusammen genau `--crest` ergeben und „damit genau so
hoch wie der Schieber nebenan" stehen. Das galt einmal — fuer eine Schirmbreite, und bis der
Schieber wuchs. `--crest` schrumpft auf schmalen Schirmen per Media Query, der Schieber nicht.

Drei Rechnungen, die auseinanderlaufen koennen, sind durch eine gemeinsame Mittellinie ersetzt:
`align-items: center` im Titelfeld, `justify-content: center` im Schieberfeld. Beide Zellen der
Gitterzeile sind ohnehin gleich hoch, also steht die ganze Zeile mittig, ohne dass eine Seite die
Hoehe der anderen kennen muesste. Nachgemessen liegen alle drei Mittellinien auf demselben Pixel.

**Und das hat einen Punkt nebenbei aufgeloest:** Die Layoutmasze der Kopfzeile haengen seitdem
nicht mehr an der Displayaufloesung des Museumsgeraets. Wo eine Abhaengigkeit von einer offenen
Frage verschwindet, sobald man die Stelle richtig baut, war die Abhaengigkeit vielleicht nie
die Frage.

**Der Zeitraum laesst sich nicht unter ein Jahrzehnt zusammenschieben.** Der ausgewaehlte Bereich
ist zugleich die Flaeche, an der man ihn ueber die Achse zieht; auf einen Balken zusammengeschoben
bliebe nichts zum Anfassen. Dafuer trug er bisher einen gezeichneten Griff in der Mitte — eine
Marke auf dem Schirm fuer einen Zustand, in den niemand geraten will. Der Griff ist weg, der Boden
ist da: `minSpan()` in `kiosk/timeAxis.ts`, ein Jahrzehnt, aber nie schmaler als ein Balken (bei
25-Jahres-Buendeln waere ein Jahrzehnt schmaler als ein einziger). Gemessen bleiben so 65 px
Greifflaeche statt eines Stummels.

**Das bewegte Ende stoppt, das andere wird nie mitgeschoben.** Mitzuschieben klingt geschmeidiger
und ist die Falle: Ein Zug am linken Ende truege das rechte ueber das Achsenende, wo es geklemmt
wuerde — und der Zeitraum kaeme schmaler zurueck, als er hineinging. Genau das Schrumpfen, das
`shiftRange` an anderer Stelle schon einmal verhindern musste.

**Kein Auge, kein Ersatzsymbol.** Der Griff war die Antwort auf ein Problem, das es nicht mehr
gibt; ein anderes Zeichen an derselben Stelle waere die Antwort auf gar keins.

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
und dieselben Fotos sind im Bestand nachgezogen worden; siehe [history.md](history.md) und Punkt 34
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

*Entschieden und umgesetzt am 12. August 2026* — Punkt 46, und damit die Ruecknahme dessen, was am
10. August gebaut wurde.

Damals bekam die Detailansicht ihre eigenen Auswahlraster: Wer ein undatiertes Foto gross ansah,
sollte es dort datieren koennen, ohne zu schliessen und zu hoffen, dass der Bereich dasselbe Foto
vorlegt. Das war richtig, **weil der Bereich es damals nicht vorlegen konnte** — das Nachschaerfen
stand dort hinter 74 unverorteten Fotos und erschien nie.

Zwei Dinge haben sich seither geaendert, und beide sprechen dagegen:

**Die Textspalte lief voll.** Ein Foto ohne Jahr und ohne Hausnummer trug bis zu 37 Schaltflaechen
unter der Beschreibung. Allein die Jahrzehnte sind fuenfzehn, seit die Zeitleiste von 1880 bis 2030
reicht statt von 2010 bis 2025 — die Datierung des Erstbestands hat das Problem selbst vergroessert.

**Die Ortsfrage war dort nie zu stellen.** Sie braucht die Karte, und die Karte liegt unter dem
Overlay. Von den drei Fragen konnte die Detailansicht also nur zwei, und ausgerechnet die
wertvollste nicht.

**Jetzt stehen dort bis zu drei Knoepfe** — je an der Zeile, die sie aendern —, und ein Tipp
schliesst die Ansicht und stellt dieses Foto im Bereich zu dieser Frage. Der Kiosk hat damit
**einen Antwortweg statt zwei**.

**Das Schliessen ist nicht Nebenwirkung, sondern die halbe Absicht.** Bei „Wo ist das?" muss die
Karte frei werden. Es je Frage anders zu machen waere eine Regel, die niemand sehen kann.

**Und danach passiert nichts Besonderes**, was die eigentliche Entscheidung ist: Dank, dann die
naechste offene Frage zu diesem Foto, dann ein neues — der gewoehnliche Ablauf. Ein Rueckweg in die
Detailansicht waere naeher am Ausgangspunkt, braeuchte aber eine Sonderregel im Store und liesse
die Kette wegfallen. Wer aus einem Foto heraus antwortet, ist im Beitragsbereich gelandet, und dort
gehoert die naechste Frage hin.

**Was das kostet:** Das Datieren ist zwei Tipps laenger geworden, und die Ansicht schliesst sich
dabei. Der Gewinn ist strukturell und beim ersten Antippen nicht zu sehen. Wenn sich das am Geraet
schlechter anfuehlt, ist die Rueckfallebene, den `DatePicker` eingebettet zu lassen und nur Ort und
Hausnummer zu verzweigen — dann waeren es aber wieder zwei Wege.

**Der Wunsch ist eine Bitte, keine Anweisung.** `GET /contribute/next?photo_id=…` prueft das Foto
gegen dieselbe Bedingung wie jedes andere und faellt auf die Zufallswahl zurueck, wo sie nicht mehr
gilt. Sonst stuende eine Frage auf dem Schirm, die zwischen Tippen und Laden schon von jemand
anderem beantwortet wurde — und der Schreibweg wiese die Antwort mit 409 ab, was klingt, als sei
der Besucher zu langsam gewesen.

## 39. Eine Beschriftung fuer das Auge und fuer das Vorlesewerkzeug

*Entschieden und umgesetzt am 12. August 2026* — Punkt 44, und die Abloesung von Punkt 29.

Unter dem Vorschaubild stand die **Adresse**, im `aria-label` desselben Knopfes der **Titel**. Zwei
Formulierungen derselben Sache, an zwei Stellen im Code. **Monatelang fiel es niemandem auf, weil
beide dasselbe sagten** — 815 Titel wiederholten die Adresse daneben. Als der Erstbestand
aufgeraeumt war, las das Auge „Hauenweg 7" und das Ohr „Hermann Berg".

**Der Fehler war nicht die falsche Zeile, sondern dass es zwei gab.** Beide zu berichtigen haette
ihn vertagt: Zwei Formulierungen laufen wieder auseinander, sobald jemand eine davon anfasst. Es
gibt jetzt eine (`kiosk/mapCaption.ts`), und beide Sinne lesen sie.

**Die Kette ist Titel, dann Adresse, dann nichts**, mit dem Jahr wo bekannt. Dass der Titel
vorangeht, ist die Umkehrung von Punkt 29 — und die Voraussetzung jener Entscheidung ist entfallen:
Titel waren damals Adressen und oft vierzig Zeichen lang. Heute sind es Titel.

**„Hauptstraße Nr. ?" statt nur „Hauptstraße"**, wo die Hausnummer fehlt. Das ist kein Notbehelf,
sondern dieselbe Haltung wie beim Nichtstreuen der Stapel (Punkt 33): Die Ungenauigkeit soll
**sichtbar** bleiben, damit jemand sie behebt, statt hinter einem hübscheren Bild zu verschwinden.
Es ist genau die Luecke, nach der der Beitragsbereich unter „Welche Hausnummer?" fragt — auf 82
Markern steht sie jetzt.

**Fuer Stapel gilt die Regel aus Punkt 29 unveraendert, jetzt auch fuer den Titel:** Gezeigt wird
nur, worin **alle** Fotos uebereinstimmen. Und sie greift beim Titel oefter, denn eine Adresse
teilen Fotos leicht, einen Titel selten — ein Stapel faellt damit meist auf die Adresse zurueck.
Den obersten Titel zu nehmen hiesse „Gasthof Timm" ueber fuenfzig Bilder zu schreiben, die
etwas anderes zeigen.

**Dazu haben 75 Fotos einen Titel aus ihrer Beschreibung bekommen** — zusammengefasst, nicht
abgeschnitten: „Errichtung des Funkmastes" wurde „Funkmast", „Otto Petersen, Inhaber der Baeckerei"
wurde „Baeckerei Petersen". 14 weitere Beschreibungen taugten nicht, weil sie ueber Besitzer,
Rueckseiten oder Ortsvermutungen sprechen statt ueber das Motiv.

**Was ausdruecklich *nicht* geschrieben wurde:** ein Titel fuer die 152 Fotos, deren Titel nur ihre
Adresse waere. Der stuende dann zum zweiten Mal in derselben Zeile — genau das, was einen Tag
zuvor fuer 815 Fotos entfernt worden ist —, er veraltete beim ersten Nachschaerfen, und er naehme
[Punkt 1](backlog.md) die Arbeitsgrundlage: Danach haetten alle 929 Fotos einen Titel, und welche
einen **echten** brauchen, waere nicht mehr zu erkennen. Abgeleitet steht auf der Karte dasselbe.

## 40. Ein Symlink ist nie ein Datentraeger

Die Suche nach Sicherungszielen (`services/backup/drives.py`, `find_drives`) **ueberspringt Symlinks**,
auf beiden Ebenen, die sie durchsucht.

Der Grund ist eine Eigenheit von `os.path.ismount`: Es antwortet fuer einen Symlink
**grundsaetzlich `False`** — „ein Symlink kann nie ein Einhaengepunkt sein". Damit sieht ein
Symlink unter `/media` wie ein gewoehnlicher Ordner aus, und die Suche steigt eine Ebene hinab.
Dieser Abstieg ist gewollt, denn Raspberry Pi OS haengt unter `/media/<benutzer>/<bezeichnung>`
ein — nur folgt `iterdir()` dabei dem Symlink, und was dahinter liegt, wird als Sicherungsziel
angeboten.

**Gemessen am 14. August 2026**, bei der Pruefung des Containerbetriebs: Der Verwaltungsbereich bot
zwei „Laufwerke" namens `data` und `media` an — das erste war das Datenverzeichnis selbst. Die
Sicherung lief durch, vollstaendig, mit Handzettel: **931 Fotos, 1,45 GB, abgelegt in dem Ordner,
den sie sichert.**

Genau davor soll die Einhaengepruefung schuetzen, und ihr Docstring sagte das auch schon: „sonst
landete die Sicherung auf derselben SD-Karte, gegen deren Ausfall sie schuetzen soll — und niemand
saehe es". Der Symlink war das Loch darin. `find_drive` fing es nicht auf, denn es prueft den
Pfad aus dem Browser nur gegen das, was `find_drives` gefunden hat.

**Auf jedem Mac war das der Normalfall, nicht ein Zufall.** macOS legt in `/Volumes` stets einen
Symlink auf `/` an, benannt nach dem internen Volume. Wer also der `operations.md` folgt und zum
Entwickeln `KIEKMAP_MEDIA_DIR=/Volumes` setzt, bekam diesen Fehler zuverlaessig — er war nur
nie jemandem aufgefallen, weil niemand den Sicherungsknopf auf einem Mac gedrueckt hatte.

Auf einem Pi ist der Fall dagegen unwahrscheinlich: In `/media` legt einen Symlink nur root an.
Die Folge waere aber die schlimmste im System — eine Sicherung, die aussieht wie eine, und die mit
dem Datentraeger stirbt, vor dem sie schuetzen sollte. Zwei Zeilen sind dafuer ein guenstiger
Preis, und fuer die Entwicklung sind sie keine Vorsorge, sondern eine Behebung.

**Fuer den Test war dieselbe Falle noch einmal aufgestellt.** Die eingesetzte `_is_mounted`
vergleicht Pfade, und woertlich verglichen ist `media/Danger/data` nicht `anderswo/data` — der
Test war deshalb im ersten Anlauf auch ohne die Absicherung gruen. Er vergleicht jetzt
aufgeloest. **Eine Gegenprobe, die nicht ausschlaegt, ist ein Ergebnis und keine Formalie.**

## 41. Der Name nennt die Sache, nicht den Ort

Das Projekt heisst **Kiekmap** — plattdeutsch *kieken*, gucken. Nach aussen mit grossem K, im
Quelltext, in Pfaden und Verzeichnisnamen klein, als Praefix der Einstellungen `KIEKMAP_`.

Der bisherige Arbeitsname beschrieb, was das Programm tut. **Ein Name fuer den ersten Ort waere
der schlechtere gewesen**, und zwar aus demselben Grund, aus dem `CLAUDE.md` verlangt, dass nichts
Ortsspezifisches in den Code gehoert: Das zweite Museum soll eine eigene `region.json` und eine
eigene `.env` brauchen, keinen Fork. Ein „holm" im Paketnamen haette dieser Zusage widersprochen,
lange bevor jemand sie technisch verletzt haette.

**Umbenannt wurde am 15. August 2026**, an 213 Stellen in 38 versionierten Dateien. Fuer Besucher
war der Name nie sichtbar — die Seite heisst „Bilder aus unserem Ort".

Der Zeitpunkt war der letzte guenstige: kein Pi im Feld, kein Git-Remote, der einzige Bestand auf
dem Entwicklungsrechner. Danach haetten Geraete, Sicherungen auf Sticks und fremde Arbeitskopien
mitgezogen werden muessen.

**Was dabei bricht, und zwar bewusst:** Sicherungen aus der Zeit davor werden nicht mehr erkannt.
`is_restorable` und `looks_like_archive` suchen den Namen im Ordner bzw. im Dateinamen des Archivs
— eine Vertraeglichkeitsregel dafuer waere Ballast fuer einen Fall, der genau einmal eintritt und
sich mit einem Klick loesen laesst: neu sichern.

## 42. Die Wiederherstellung bringt das Schema selbst auf Stand

Eine zurueckgespielte Sicherung wird migriert, und zwar von der Wiederherstellung selbst
(`services/schema.py`, aufgerufen in `backup.restore._swap_in`). Ein Neustart ist dafuer nicht mehr noetig.

**Der Anlass ist ein Fehler, der zwei Tage lang unbemerkt lief.** Eine Sicherung bringt ihr Schema
mit; getauscht wird die Datei im Ganzen, und das laufende Programm haengt sich nur neu an sie.
Migrationen liefen dabei nicht — sie laufen beim *Start*, und eine Wiederherstellung ist kein
Start. Das Geraet sah danach voellig normal aus und **nahm nichts mehr an**: Jeder Besucherbeitrag,
jede Bearbeitung, jeder Upload endete mit HTTP 500.

Die Abhilfe stand seit dem 12. August 2026 in beiden Handbuechern: einmal neu starten. **Eine
Anweisung an Menschen ist aber die schwaechste Stelle, die eine Zusage haben kann** — sie muss
gelesen, erinnert und befolgt werden, und zwar von jemandem, der ein- bis zweimal im Jahr an dieses
Geraet geht. Wer sie vergisst, merkt nichts, denn der Fehler zeigt sich erst beim naechsten
Besucher, der etwas beitragen will.

**Die Reihenfolge ist der ganze Punkt**, und sie hat zwei Haelften auf beiden Seiten des Tauschs:

1. **Abgelehnt wird vorher.** Traegt die Sicherung eine Revision, die dieses Programm nicht kennt,
   bricht die Wiederherstellung ab, **bevor** irgendetwas ersetzt ist. Der Bestand auf dem Geraet
   bleibt unangetastet. Migrieren waere hier keine Option: Die zugehoerigen Migrationen gibt es in
   diesem Programm gar nicht.
2. **Migriert wird nachher.** Erst nach dem Tausch ist die zurueckgespielte Datei die am
   konfigurierten Pfad.

**Formuliert als „kennen wir diese Revision?", nicht als „ist sie neuer?".** Eine Revision, die
sich nicht einordnen laesst, ist eine, die man nicht anfassen darf — gleich ob sie aus einem
neueren Programm stammt, aus einem anderen Zweig oder aus einer Datei, die gar nicht unsere ist.

**Ein Sonderfall bleibt bewusst offen:** Eine Datenbank ohne `alembic_version` wird nicht migriert,
sondern in Ruhe gelassen. Ohne Stempel ist nicht zu sagen, was die Datei ist, und Alembic finge bei
der ersten Migration gegen Tabellen an, die es schon gibt. Im Museum kann das nicht vorkommen —
dort entsteht jede Datenbank durch Migrationen. Es kommt in der Testumgebung vor, wo das Schema
direkt aus den Modellen entsteht, und genau dort waere Migrieren falsch.

**Dazu zwei Dinge, die den Fehler haetten finden koennen und es nicht taten**, jetzt nachgeholt:
`test_migrationen_und_modelle_beschreiben_dasselbe_schema` baut das Schema einmal ueber Alembic und
einmal ueber `create_all` und vergleicht Tabellen und Spaltennamen — die uebrigen Tests bauen es
aus den Modellen und koennen eine fehlende Migration deshalb grundsaetzlich nicht bemerken. Und
`make dev` zieht den Schemastand jetzt vorweg nach, denn im Container tut das der Entrypoint, auf
dem Entwicklungsrechner aber niemand.

## 43. Der Kopfbereich misst sich an seiner Spalte, nicht am Ansichtsfenster

Wappen und Titel bekommen ihre Groesse aus der Breite der Zelle, in der sie stehen
(`container-type: inline-size` und `cqi` in `styles/global.css`), nicht aus einer Medienabfrage.
Der Ortsname bekommt zusaetzlich seine **Laenge** mitgeteilt, weil CSS Text nicht messen kann.

**Der Anlass war ein Fehler mit zwei Ursachen, und die zweite war die schwerere.**

Die erste ist ein Fallstrick, den man einmal kennen muss: **In einer Medienabfrage ist `rem` immer
16 px.** Es ist die Schriftgroesse des Wurzelelements, *bevor* eine eigene Regel sie aendert —
`:root { font-size: 18px }` gilt darin nicht. `@media (max-width: 85rem)` meinte also 1360 px, wo
1530 px gedacht waren, und dazwischen stand ein zu grosses Wappen neben einer zu schmalen Spalte.

Die zweite: **Der Entwurf hatte 0,3 px Luft.** Auch oberhalb der Schwelle passte „Bilder aus" nur
knapp; bei 1470 x 956 brach Safari um und Chromium nicht. Die Grenze zu berichtigen haette den
Fehler also nur verschoben. **Eine Zeile, die erst beim Nachmessen passt, passt nicht.**

**Daraus die Regel:** Wer im Kopfbereich eine Groesse setzt, bezieht sie auf den Platz, der da ist,
und laesst Luft. Eine Schwelle im Ansichtsfenster ist immer eine Stelle, an der zwei Rechnungen
auseinanderlaufen koennen — dasselbe Muster, das am 9. August 2026 schon die drei Hoehenrechnungen
von Wappen, Titel und Schieber durch eine gemeinsame Ausrichtung ersetzt hat.

**Und die Zusage ist begrenzt, mit Absicht.** Der Ortsname wird kleiner gesetzt, je laenger er ist,
aber **nie kleiner als die Zeile „Bilder aus" darueber** — sonst stuende die Rangfolge auf dem
Kopf. Wo dieser Boden greift, bricht der Name um; das ist die bessere der beiden schlechten
Antworten und war auch vorher schon die gewaehlte. Bis zwoelf Zeichen geht es auf jedem Schirm gut,
bis sechzehn auf einem breiten — nachgemessen und in `docs/adaption.md` aufgeschrieben, weil es
die naechste Gemeinde betrifft und nicht diese.

## 44. Die Blaetterknoepfe stehen fest, das Bild bewegt sich

In der Detailansicht sind die Blaetterknoepfe **senkrecht am unteren Rand verankert** und stehen
**waagerecht mittig unter dem Bild**. Das Bild sitzt darueber und aendert seine Hoehe, die Knoepfe
nicht.

**Vorher klebten sie am Bild und wanderten mit ihm.** Zwischen einem 3:2-Querformat und einem
2:3-Hochformat lagen **103 px** -- gemessen am 16. August 2026 auf einem 1024er Schirm. Wer durch
einen Stapel blaettert, dessen Fotos nicht alle dasselbe Format haben, jagt damit den Knopf ueber
den Schirm; im schlimmsten Fall liegt beim naechsten Tippen das Bild dort, wo eben noch
„Naechstes" stand. Auf einem Touchscreen ist das kein Schoenheitsfehler, sondern ein Fehlgriff.

**Waagerecht bleiben sie beim Bild**, und das ist die Gegenrichtung derselben Frage: Sie gehoeren
zu dem, was sie aendern. Mittig im Schirm stuenden sie bei einem Hochformat weit neben dem Bild,
und der Bezug ginge verloren. Die linke Spalte ist deshalb weiterhin genau so breit wie das Bild.

**Die Regel dahinter:** Was der Besucher *trifft*, steht still; was er *ansieht*, darf sich
bewegen. Ein Bedienelement, dessen Ort vom Inhalt abhaengt, ist auf einem Beruehrungsschirm eine
Falle -- besonders fuer die Zielgruppe, die hier vor dem Geraet steht.

**Der Schliessen-Knopf folgt derselben Regel** und steht seit demselben Tag in der Ecke des
Schirms statt am rechten Rand des Inhalts. Er bekommt dabei **keine** der vier Rollen aus Punkt 30:
Die sind die Sprache des Beitragsbereichs -- auswaehlen, uebernehmen, zurueck, ueberspringen --,
und Schliessen ist keine davon. Die Detailansicht fuehrt auf ihrem dunklen Grund ohnehin eine
eigene Knopffamilie; sie behaelt ihn als Sonderfall.

## 45. Woher eine Koordinate kommt, sagt nichts darueber, wie genau sie ist

Ob ein Foto zum Nachschaerfen vorgelegt wird, entscheidet, **was ueber das Haus bekannt ist** --
nicht, aus welcher Quelle seine Koordinate stammt (`services/needs.py`, `_needs_housenumber`).

**Bis zum 16. August 2026 stand dort das Gegenteil.** Die Bedingung verlangte ausdruecklich
`location_accuracy_m == ACCURACY_STREET_M`, liess also nur zu, was ein Kurator auf eine Strasse
gesetzt hatte. Begruendet war das mit einem Satz, der plausibel klingt: „Das Geraet weiss, wo der
Fotograf stand, nicht was er fotografiert hat."

**Der Satz war vier Tage vorher widerlegt worden.** Am 12. August ergab das Nachzaehlen, dass von
413 EXIF-Koordinaten des Erstbestands **278 sich zwei Fotos teilten** -- eingetragene Werte, keine
Messungen (Punkt 34, und es steht seitdem in `CLAUDE.md` unter den drei Dingen, die man hier falsch
machen kann). Niemand ist danach zu `needs.py` zurueckgegangen. 53 Fotos mit einem Strassennamen
aus dem Archivordner und einer eingetragenen Koordinate blieben aus der Frage draussen, obwohl sie
genau ihr Fall sind.

**Aufgefallen ist es als etwas anderes**, und das ist der Teil, der das Aufschreiben lohnt: Gemeldet
wurde, in der Detailansicht fehle der Knopf, *sobald das Jahr bekannt ist*. Die Beobachtung stimmte,
die Erklaerung nicht. Unter den Fotos mit blossem Strassennamen sind die mit Jahr ueberwiegend
gerade die aus dem EXIF -- 35 von 53, gegen 13 von 71 bei den strassengenauen. Wer sich durchklickt,
sieht eine saubere Korrelation und schliesst auf die falsche Ursache. **Eine gemeldete Beobachtung
ist ein Befund, ihre Erklaerung eine Vermutung**, und die beiden gehoeren getrennt geprueft.

**Die Bedingung nennt jetzt, was sie meint:** auf der Karte, nicht schon hausgenau, ein
Strassenname ohne Ziffer, und der Ortsindex kennt Adressen dazu. Die Frage waechst damit von 70 auf
116 Fotos; keines faellt weg.

**Was daraus fuer aehnliche Regeln folgt:** Eine Bedingung, die ueber die *Herkunft* eines Wertes
statt ueber seinen *Inhalt* entscheidet, traegt eine Annahme mit sich, die veralten kann, ohne dass
die Regel es merkt. Wo es geht, wird gefragt, was bekannt ist -- nicht, wer es eingetragen hat.

## 46. Der Bestand ist JPEG, und das Rezept dafuer steht fest

*Entschieden am 16. August 2026, beim Nachziehen des neueren Archivstands (Punkt 52).*

Ein Museumsarchiv ist gemischt: Scans kommen als TIFF, Bildschirmaufnahmen als PNG, ein Bild von
einer Webseite als WEBP. Der Bestand fuehrt nur JPEG, und der Grund ist nicht Ordnungsliebe --
**ein Browser zeigt kein TIFF an.** Der Kiosk brauchte ein Vorschaubild und reichte eine
Originaldatei heraus, die sich nirgends oeffnen laesst; die Detailansicht bietet genau diese Datei
an.

**Die Einstellung ist gemessen, nicht gewaehlt.** Der Erstbestand war schon umgewandelt
angekommen, von einem Werkzeug, das niemand aufgeschrieben hatte. Seine Quantisierungstabellen
sagen: Pillow, Qualitaet 92, Subsampling 4:4:4, `optimize`. Gegen die 19 Dateien, fuer die beide
Fassungen vorliegen, kommen damit **vier bitgleich** und **achtzehn pixelgleich** heraus; mit
Qualitaet 90 keine einzige.

**Das ist mehr als Sauberkeit, es ist die Voraussetzung fuer die Dublettenerkennung.** Der Import
erkennt eine Dublette am SHA-256 der Datei. Zweimal dasselbe Rezept ueber dieselbe Datei gibt
denselben Hash -- eine andere Qualitaet gibt einen anderen, und beim naechsten Archivstand kaeme
jedes schon vorhandene Bild ein zweites Mal herein, ohne dass jemand etwas merkt. Deshalb steht
die Einstellung in `tools/to_jpeg.py` als Konstante und hat einen eigenen Test, der sie festhaelt.

Die neunzehnte ist `Weidenstieg/Straszenauffahrt`, deren altes JPEG andere Tabellen traegt: Die
hat jemand von Hand umgewandelt, bevor es ein Rezept gab.

## 47. Ein Diff ueber Bytes ist kein Diff ueber Bilder

*Gelernt am 16. August 2026, an 619 Dateien.*

Vom Museum kam ein neuerer Archivstand, bereits als Differenz geliefert: alles, was im aktuellen
Bestand des Museums liegt, minus dem, was in unseren Erstimport ging. 619 Dateien. Und im Backlog
stand die Zusage, der Abgleich erledige sich zum grossen Teil von selbst -- der SHA-256 entscheide
ueber Dublette oder nicht.

**223 der 619 zeigten ein Bild, das schon im Bestand stand.** Ein Import ueber den ganzen Ordner
haette 223 zweite Fassungen angelegt.

Der Grund: Das Museum hat seinen Bestand durch **ExifTool** laufen lassen und dabei die
Metadatenbloecke neu geschrieben -- Ortsangaben korrigiert, Stichwoerter vereinheitlicht, den
eingebetteten Vorschau-Anhang verkleinert. `P4139301.JPG` liegt alt mit 1 848 144 Bytes vor, neu
mit 1 843 343: **dieselben Bildpunkte, andere Bytes.** Wer so einen Stand byteweise vergleicht,
bekommt keinen Diff der Bilder, sondern einen Diff der Bearbeitungslaeufe.

**Die Regel daraus:** Ein Datenstand, der ueber Bytes verglichen wurde, sagt nichts darueber, was
neu *ist* -- nur darueber, was neu *geschrieben* wurde. Vor jedem Import eines gelieferten Diffs
wird deshalb ueber den Bildinhalt nachgezaehlt, in zwei Durchgaengen: erst pixelgenau bei gleichen
Kantenlaengen (das siebt fast alles), dann grob ueber 32x32-Graustufen fuer das, was beim
Neuausspielen auch die Groesse geaendert hat. Der zweite Durchgang fand sechs weitere, darunter
eine Sporthalle in dreifacher Aufloesung.

**Der Abstand zwischen Treffer und Nicht-Treffer war dabei kein Ermessen**, und das ist der Grund,
warum eine Schwelle hier ueberhaupt vertretbar ist: 212 der Treffer lagen bei einer mittleren
Abweichung von exakt 0,00, der hoechste bei 3,01 -- und der naechste Nicht-Treffer bei 56.

## 48. Was im Titelfeld steht, ist nicht automatisch ein Titel

*Entschieden am 16. August 2026, nachdem der neue Archivstand denselben Fehler dreifach
zurueckgebracht hatte.*

In der Detailansicht steht der Titel **ueber** der Adresse, nicht an ihrer Stelle. Ein Foto, das
„Hauptstrasse 14, Museum" heisst und darunter noch einmal „Hauptstrasse 14" fuehrt, sagt eine Zeile
umsonst -- und die Zeile darueber ist die auffaelligste der ganzen Ansicht.

Punkt 41 hat im August 2026 **815 solcher Titel von Hand auseinandergenommen**. Die Regel, die sie
erzeugt, blieb dabei stehen: `apply_folder_meta` setzte den Titel weiter auf „Strasse Hausnummer,
Zusatz". Der naechste Archivstand schrieb **323 von 395** neuen Fotos genau so wieder an. Daher
drei Regeln statt einer Aufraeumaktion:

**Der Ordnertitel ist der Zusatz.** „14 Gasthof Petersen" ergibt den Titel „Gasthof Petersen", die
Adresse steht in `place_name`. Nennt der Ordner nur eine Nummer, bleibt der Titel **leer** -- eine
Zeile, die nur die naechste wiederholt, ist keine.

**Die Laengengrenze ist gemessen, nicht gewaehlt.** `TITLE_MAX` stand bei 120 und liess acht
Bildunterschriften als Titel durch, die laengste mit 108 Zeichen. Von den 781 Titeln, die das
Museum von Hand gesetzt hat, ueberschreitet **kein einziger 58 Zeichen**; der Mittelwert liegt bei
13. Die Grenze steht jetzt bei 60, und was darueber liegt, wandert in die Beschreibung statt
weggeworfen zu werden.

**Der Name der Scannersoftware gehoert in kein Feld.** „Intel(R) JPEG Library, version
[1.51.12.44]" kam als Titel von 35 Fotos. Anders als eine zu lange Bildunterschrift darf er
**nicht** in die Beschreibung ausweichen: Das schoebe denselben Unsinn nur eine Zeile tiefer, wo er
im Kiosk unter dem Bild stuende. Punkt 41 hatte achtzehn davon von Hand entfernt.

**Die Lehre steckt nicht in den drei Regeln, sondern darin, warum es sie zweimal brauchte.** Eine
Bereinigung von Hand raeumt den Bestand auf und laesst die Ursache stehen. Solange die Ursache im
Import sitzt, ist die naechste Lieferung die naechste Bereinigung. Was von Hand aufgeraeumt wird,
gehoert danach als Regel dorthin, wo es entstanden ist -- sonst zaehlt man dieselbe Arbeit in
Monaten.

## 49. Ein Datumswort sagt, dass es ein Datum ist -- nicht, wovon

*Ergaenzung zu Punkt 37, am 16. August 2026 im Trockenlauf aufgefallen.*

Punkt 37 hatte die Regel umgedreht: nicht „eine Jahreszahl ohne Warnwort", sondern „eine
Jahreszahl, der *um*, *ca.*, *im Jahre*, *Herbst* oder *Dezember* vorausgeht". Begruendet damit,
dass eine Warnwortliste nie fertig wird, ein positives Muster aber schon.

**Das Muster allein reicht nicht.** Im Bestand steht:

    ca. 1970 wurde dieses Haus abgerissen und durch ein Mehrfamilienhaus ersetzt

Das Datumswort steht davor, sauber. Nur datiert die Jahreszahl den **Abriss** -- und die Aufnahme
liegt zwingend davor, sonst gaebe es das Haus auf dem Bild nicht. Zwei Fotos waeren so auf das Jahr
ihres eigenen Verschwindens datiert worden, und weil sie damit als datiert gelten, haette sie
niemand mehr gefragt.

**Beide Listen werden gebraucht, und sie tun Verschiedenes.** Das Datumswort davor sagt, *dass*
eine Zahl ein Datum ist. Ein Ereigniswort dahinter -- *abgerissen*, *erbaut*, *abgebrannt*,
*ausgesiedelt*, *verkauft* -- sagt, *wovon*. Der Einwand aus Punkt 37 gilt weiter, trifft aber nur
die eine Richtung: **Eine Liste, die ausschliesslich ablehnt, darf unvollstaendig sein.** Sie laesst
dann einen Fall durch, den ein Mensch danach noch sieht; eine Liste, die etwas *annimmt*, macht aus
einer Luecke eine falsche Angabe.

## 50. Wer es geliehen hat und wo es lag, sind zwei Antworten

*Nachgebessert am 16. August 2026, gemeldet vom Museum.*

Die Herkunft trug bei 265 Fotos den Archivpfad nicht -- genau bei denen, deren Datei selbst schon
etwas sagte („Familie Boysen", „Sammlung Jan Wendt", „August Möller"). `apply_folder_meta`
fuellte das Feld nur, wenn es leer war, und stand damit vor jeder Angabe, die jemand schon
gemacht hatte.

**Das ist genau umgekehrt, als es sein muesste.** Wer ein Foto geliehen hat, steht in der Datei
und ist damit gesichert. **Wo es im Archiv lag, steht nur im Pfad** -- und der Pfad geht mit dem
Import verloren, denn im Bestand heisst die Datei nach ihrem SHA-256. Es ist die einzige Angabe
der beiden, die sich aus dem Bild nie wiederherstellen laesst, und sie fehlte ausgerechnet dort,
wo ohnehin schon jemand mitgedacht hatte.

Beides steht jetzt nebeneinander, durch Komma getrennt:

    Familie Boysen, Online-Archiv des Museums, Verzeichnis 01 Orte/Straßen/Im Sande/…/15.jpg

Das Feld bleibt, was es war: **nicht oeffentlich**. Es steht nicht in `PhotoDetail`, also auch
nicht auf dem Schirm im Ausstellungsraum -- siehe Punkt 36.

## 51. Ein Feld, das an seiner Grenze endet, ist abgeschnitten

*Gemeldet am 16. August 2026.*

Bei 19 Fotos lautete der Bildnachweis „Förderkreis für Kultur und Brauc". Das sieht nach einem
Tippfehler aus und ist keiner: **Die Zeichenkette ist genau 32 Zeichen lang**, und 32 ist die
Laengengrenze des IPTC-Feldes 2:80 (By-line). Nicht wir haben gekuerzt -- das Programm, das die
Datei beschriftet hat, hat an seiner Feldgrenze aufgehoert, und wir haben es unbesehen uebernommen.

**Eine Angabe, deren Laenge auf eine runde Zahl faellt, ist verdaechtig**, und der Fall kostet
nichts nachzuzaehlen: Ein Blick auf die Byte- und Zeichenlaenge der haeufigsten Werte eines
Textfeldes zeigt ihn sofort. Hier war es der einzige; „August" bei neun Fotos ist mit sechs
Zeichen keine Feldgrenze, sondern eine unvollstaendige Eingabe und gehoert damit zu Punkt 1.

## 52. Eine Vorgabe ist kein Befund

*Gelernt am 16. August 2026, an fuenf falsch zugeschriebenen Fotos.*

Die Umwandlung nach JPEG reichte lange nur Farbprofil und Aufloesung durch. Zwoelf Fotos des
neueren Archivstands verloren dabei, was ihre Datei ueber sie sagte -- und **fuenf davon trugen
danach den Bildnachweis "Sammlung Heimatmuseum Holm", wo "Hubert Wulf" haette stehen muessen.**

Der Weg dorthin ist eine einzige Zeile im Import:

    credit=info.credit or settings.import_credit or None

Die Vorgabe aus der ``.env`` springt ein, wenn die Datei nichts sagt -- und das ist richtig so.
Falsch wurde es, weil die Datei etwas sagte und wir es unterwegs verloren hatten. **Der Ausfall
war damit nicht sichtbar**: Das Feld war gefuellt, es sah nach einer Auskunft aus, und eine falsche
Zuschreibung ist schlimmer als eine fehlende. Bei einem Museum ist sie die unangenehmste Sorte
Fehler ueberhaupt.

**Zwei Regeln folgen daraus.**

Erstens, fuer die Reparatur: Wo ein Feld genau den Vorgabewert traegt und die Datei etwas anderes
sagt, gewinnt die Datei. Eine Vorgabe ist eine Rueckfallebene, keine Aussage, und darf deshalb
weichen -- anders als eine Angabe, die ein Mensch gesetzt hat.

Zweitens, fuer alles, was Daten von A nach B traegt: **Was auf dem Weg verloren geht, faellt nur
dort auf, wo hinterher eine Luecke steht.** Wo eine Vorgabe die Luecke fuellt, wird aus dem Verlust
eine Behauptung. Die Probe darauf ist billig und heisst nicht "sind die Bytes mitgekommen", sondern
"liest unser eigener Leser aus der Kopie dasselbe wie aus der Quelle" -- so steht sie jetzt als
Test in ``test_to_jpeg.py``.

## 53. Das XMP des Archivs wird nicht gelesen -- nachgemessen, nicht vermutet

*Entschieden am 16. August 2026, nachdem der Gesamtbestand vorlag.*

`services/exif.py` liest EXIF und IPTC, kein XMP. Das stand als Punkt 55 im Backlog, mit einer
verlockenden Zahl: **251 der neuen Dateien tragen eine Ortsangabe in `Iptc4xmpCore:Location`**, und
40 der zurueckgestellten wichen von unserem Ortsnamen ab, oft um eine Hausnummer, die uns fehlt.

**Vor dem Bauen wurde gemessen**, ueber alle 1322 Archivdateien unter `Straßen`. 1189 tragen XMP.
Das Ergebnis kehrt die Erwartung um:

| Feld | was wirklich drinsteht |
|---|---|
| `dc:creator` | „unbekannt", „Winter" -- kein Fotograf. Fuer „unbekannt" gibt es die Regel schon |
| `dc:description` | „Gebäude", „Abriss & Neubau", „Winterspaziergang" -- **Kategorien, keine Beschreibungen** |
| `Iptc4xmpCore:Location` | 515-mal genau das, was der Ordner schon sagt |
| `photoshop:Location` | 96-mal im Widerspruch zum ersten, meist ein stehengebliebener Stapelwert |

**Der Ertrag beim Ort, dem staerksten Feld, sind 26 Fotos** -- und davon tragen **neun denselben
Wert „Am Felde 5"**, der auch als veraltete `photoshop:Location` auf Fotos unter den Nummern 9,
10, 16 und 31 klebt. Zwei widersprechen dem Ordner, einer nennt statt einer Nummer den Gebaeudenamen
(„Am Sportzentrum Geräteraum"). **Es bleiben eine Handvoll brauchbarer Angaben, jede einzeln zu
pruefen.**

Der Umbau des Lesers, eine Entscheidung ueber zwei widerspruechliche Ortsfelder und ein
Vorlage-Weg fuer 259 Konflikte -- fuer eine Handvoll Hausnummern, die ein Mensch ohnehin ansehen
muesste. **Das lohnt nicht.**

**Was der Durchgang stattdessen gebracht hat**, ist der Grund, warum er richtig war: Er hat einen
Ordner gefunden, der seine Strasse wiederholt (`Hörnstraße/Hörnstraße 14`) und damit denselben
Adressabklatsch erzeugte, den Punkt 48 gerade abgeschafft hatte. **Erst messen, dann bauen** heisst
eben auch, dass die Messung etwas anderes findet als das Gesuchte.

## 54. Dubletten findet die Maschine, entscheiden muss ein Mensch

*Entschieden am 16. August 2026 -- Punkt 42, und die offene Frage darin war der Grad der
Selbsttaetigkeit.*

Der SHA-256 erkennt eine Kopie der *Datei*. Er erkennt nicht denselben Papierabzug, zweimal
gescannt, und nicht denselben Scan, einmal gross und einmal klein gespeichert. Gefunden wird das
mit einem **Differenzhash ueber 256 Bit** auf den vorhandenen Vorschaubildern -- 876 000 Paare,
ein XOR je Paar, wenige Sekunden. Er ertraegt Helligkeit, Farbstich und Verkleinerung.

**Die Schwelle ist angesehen, nicht gewaehlt.** Sechzig Paare durchgeblaettert: bis Abstand 12
zweifelsfrei dasselbe Bild, bis 30 fast immer, bei 37 bis 40 immer noch die Mehrheit. Das Signal
reisst nicht ab, es wird unscharf -- also ist die Vorgabe grosszuegig (40) und ein Mensch
entscheidet.

**Vollautomatisch waere falsch, und der Beweis stand in den Gruppen:**

* Zwei Fotos derselben Grundsteinlegung standen an **verschiedenen Adressen und in verschiedenen
  Jahren** -- Schulstrasse 9/1971 gegen Lehmweg 8/1968. Eines war falsch abgelegt. Eine Maschine,
  die das groessere behaelt, haette die Frage nie gestellt.
* Bei einem Paar traegt die **kleinere** Fassung den eingebrannten Bildtext „Dörpshus vor dem
  Brand". Aufloesung ist dort das falsche Kriterium.
* Auf einem von drei sonst gleichen Strassenbildern steht ein Lastwagen. Zwei Momente, keine
  Dublette.

**Der Umfang macht die Entscheidung leicht.** Es waren 44 Gruppen ueber 95 Fotos, nicht Hunderte.
Eine Vorlage-Liste mit 44 Zeilen ist in einer Viertelstunde durchgesehen; eine Automatik, die
gelegentlich das bessere Bild verliert, waere nie wieder zu pruefen. Deshalb findet
``services/similar.py`` und schreibt nichts.

**Zusammengefuehrt wird vor dem Herausnehmen**, nicht danach: Titel, Beschreibung, Datierung, Ort,
Bildnachweis, Schlagwoerter und der Archivpfad wandern auf das behaltene Foto, soweit ihm etwas
fehlt. Und „herausnehmen" heisst ``status = deleted`` -- aus der Ausstellung, nicht von der Platte
(Punkt 16). Wer sich vertut, holt es zurueck.

**Zwei Schlagwoerter blieben dabei absichtlich liegen.** „Bauernhaus von Paul Stein, im Jahre 1987.
Abriss 18.1.1988" ist kein Stichwort, sondern ein Satz aus der Kommazerlegung von Punkt 41. Ihn
auf das behaltene Foto zu tragen hiesse, den Fehler zu vermehren; am herausgenommenen bleibt er
stehen, verloren geht also nichts.

## 55. Ein Schlagwort ist kein Feld, sondern eine Menge

*Entschieden am 16. August 2026 -- Punkt 50, das Stapelschlagwort beim Import.*

Alle Stapelangaben des Importformulars folgen einer Regel: **sie fuellen nur, was leer ist.** Jahr,
Koordinate, Ortsname, Bildnachweis, Herkunft -- wo die Datei es besser weiss, gewinnt die Datei.
Das ist richtig, weil jedes dieser Felder genau einen Wert haelt: Fuellen hiesse entscheiden.

**Fuer Schlagwoerter gilt sie nicht, und die Regel umzubiegen waere der Fehler gewesen.** Eine
Schlagwortliste haelt keinen Wert, sondern eine Menge. Wer hundert Fotos aus einem Ordner
„Feuerwehr" hochlaedt, will nicht *entweder* das Stapelwort *oder* das der Datei -- er will beides.
Das Stapelschlagwort tritt also **neben** das, was die Datei mitbringt, statt ihm zu weichen.

**Damit gibt es drei Quellen, und ihre Reihenfolge steht im Code**, bevor sie jemand sich
zusammenreimt:

1. ``KIEKMAP_IMPORT_TAGS`` -- gilt fuer jeden Import dieses Geraets, in Holm ``["Gebäude"]``
2. die Stichwoerter aus der Datei selbst
3. das Stapelwort aus dem Formular

``add_tags`` ueberspringt, was das Foto schon traegt, und legt einen Namen nur einmal an. Die
Reihenfolge kostet deshalb nichts und entscheidet nur, wer einen Namen zuerst anlegt.

**Kommas trennen.** Das ist dieselbe Zerlegung, die bei Punkt 41 aus Bildunterschriften
Schlagwoerter gemacht hat -- aber nicht derselbe Fall: Dort zerschnitt eine Maschine eine
Beschreibung, hier tippt ein Mensch in ein Feld, das „Schlagwörter" heisst.

## 56. Ein Jahrzehnt ist eine Datierung -- „vor 1978" ist keine

*Entschieden am 18. August 2026 -- Punkt 1.3, die Datierungen im Text.*

Die Bereinigungsrunde vom 11./12. August suchte im Text nach **vierstelligen Jahreszahlen**. Sie
fand 83 und uebernahm 52. Was sie nicht suchte, war alles andere, womit Menschen datieren: „80er
Jahre", „in den 1930gern", „Winter 63", „Foto aus der Nachkriegszeit".

**Das war die groessere Haelfte.** Nachgezaehlt am 18. August trugen 94 Fotos ohne Jahr eine
Datierung im Text; 44 liessen sich uebernehmen, und die ergiebigste einzelne Fundstelle war eine
Ordnernotiz auf **achtzehn** Fotos: „Gebäude und Umgebung im Holm der 80er Jahre". Ein Jahrzehnt
ist kein unscharfes Jahr, sondern eine eigene Aussage -- ``date_precision`` kennt ``decade`` genau
dafuer (Punkt 2 dieser Liste).

**„Vor 1978" dagegen wird nicht uebernommen, und der Grund liegt im Zeitfilter.** Er fragt auf
Ueberlappung ab. Ein Foto mit dem Intervall 1880--1978 ueberlappt mit *jeder* Stellung des
Schiebers und stuende deshalb ueberall -- schlechter als undatiert, denn undatiert legt der
Beitragsbereich es wenigstens als Frage vor. Eine Datierung braucht beide Enden; wo eines erfunden
werden muesste, ist keine da.

**Zwei Muster sind dabei als eigene Faelle herausgekommen**, beide Verwandte von Punkt 49:

- **Die Jahreszahl des Archivstands.** „heute (2018) Marc Sieveking", „bis 2018 Besitzer", „2026
  Reitanlage Holm". Im Holmer Bestand ist „2018" fast nie ein Aufnahmejahr, sondern der Tag, an dem
  jemand das Archiv gepflegt hat. Fuenfzehn Fotos.
- **Das nicht ausgeschriebene Jahr.** „Notiz: Schule 78" ist dieselbe Archivnotiz wie „Notiz:
  1978", nur zwei Zeichen kuerzer -- und fiel durch, weil die Suche das zweistellige Jahr nur
  hinter einem Jahreszeitwort kannte („Winter 63"), nicht hinter einem Hausnamen. Dasselbe beim
  Monat: „März 73", „Notiz: 5.80". **Bei einer Suche nach Mustern bestimmt die Form des Musters
  den Befund**, nicht der Bestand -- und wer nur eine Schreibweise sucht, misst seine eigene
  Annahme. Die Gegenprobe dagegen ist billig: nachsehen, ob dieselbe Aussage anderswo in einer
  anderen Schreibweise steht, die man akzeptiert hat.
- **Das Scandatum in Prosa.** „Im Januar 2020 eingescannt von einem SW-Abzug von Olaf Sieveking."
  Dieselbe Falle wie das EXIF-Datum eines Scans, nur in einem Textfeld statt in einem Tag -- und
  ohne die Jahresgrenze aus ``services/exif.py``, die sie dort abfaengt.

## 57. Der Kiosk heilt sich selbst — aber nur einmal

*Entschieden am 19. August 2026 — Backlogpunkt 59, gefunden beim Durchgang über den Code.*

Ein Fehler beim Rendern reisst in React den ganzen Baum ab, und übrig bleibt eine weisse Seite. Am
Schreibtisch ist das eine Unannehmlichkeit — man drückt Neu laden. Im Museum gibt es nichts zu
drücken: Chromium läuft unter `cage` ohne Tastatur, ohne Adressleiste, ohne Knöpfe. Und der
Leerlauf-Neustart, der sonst jeden verfahrenen Zustand heilt, sitzt in `MapView` und geht mit
unter. Die Vitrine steht dann weiss, bis jemand den Stecker zieht.

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
fängt so etwas**, weil beide Werte gültige Zeitstempel sind. Deshalb heisst die Uhr jetzt
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
ist entweder offen oder vergriffen — keine Lücke, kein Überhang, keine zweimal. Genau das heisst
„Nummern werden nie neu vergeben". `tools/check_numbers.py` rechnet das nach, dazu die Übereinstimmung
von Tabelle und Fliesstext, den Anker jeder Zeile auf ihren *eigenen* Punkt, und das
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

**Wo die Grenze verläuft**, zeigt der Gegenfall aus derselben Messung: Die Grösse eines Kreises auf
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
durch, die der Rest des Programms benutzt. `from app.services import backup` heisst weiterhin, was
es hiess; keine Importzeile in `api/`, in `watcher.py` oder in den Tests hat sich bewegt. Am Ende
sind **sechs Zeilen** in den Tests anders, und keine davon ist eine Zusage: Es sind die Stellen,
an denen `monkeypatch` einen privaten Namen umsetzt, jetzt `backup.drives._is_mounted` statt
`backup._is_mounted`. Ein Test, der in einen privaten Namen greift, greift damit sichtbar in ein
bestimmtes Modul — das ist ehrlicher als vorher, nicht weniger ehrlich.

**Was die Aufteilung ans Licht brachte**, hätte man vorher nicht gesehen: Die Wiederherstellung
setzte den Grössen-Zwischenspeicher mit `global _size_cache` zurück. Das funktioniert nur, solange
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
