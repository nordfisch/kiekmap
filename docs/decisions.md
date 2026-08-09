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
zusammengelegt. Der Grund ist schlicht: Es hatte nie ein Gerät Photomap ausgeführt. Es gab also
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

*Entschieden am 9. August 2026, gebaut noch nicht* — die Umsetzung steht als Punkt 25 und 29 im
[backlog.md](backlog.md). Diese Entscheidung schreibt [Punkt 7](#7-admin-aufs-wappen-tippen-dann-pin)
fort, der genau **eine** Tür festgelegt hatte.

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
