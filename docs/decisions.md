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

## 7. Admin: Ecke lang drücken, dann PIN

**Entscheidung.** 3 Sekunden Druck auf die untere linke Bildschirmecke öffnet ein Zahlenfeld mit
großen Tasten. Danach der Admin-Bereich, mit ablaufendem Token.

**Warum versteckt statt sichtbarem Knopf?** Ein sichtbares Zahnrad wird von Besuchern garantiert
angetippt; die Anmeldemaske gehört nicht in eine Museumsausstellung. Für Eingeweihte dauert der
Weg zwei Sekunden.

**Warum PIN statt Passwort?** Die Eingabe erfolgt mit dem Finger auf einem Touchscreen, oft von
älteren Menschen. Ein Zahlenfeld mit großen Tasten ist dafür ungleich besser als eine
Bildschirmtastatur. Für ein Gerät, das ohnehin im verschlossenen Museum steht, ist eine PIN mit
Verzögerung nach Fehlversuchen angemessen.

**Warum überhaupt am Gerät und nicht nur vom Laptop?** Weil der USB-Stick für die Sicherung im Pi
steckt. Alles andere wäre umständlich.

---

## 8. Sicherung ist eine Funktion, kein Skript

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
