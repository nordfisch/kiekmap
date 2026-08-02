# Offene Punkte

Was noch aussteht, nach **Verwaltung · Besucher-Interface · Infrastruktur**. Was schon gebaut ist,
steht in [history.md](history.md).

Jeder Eintrag trägt mit, was beim Aufgreifen sonst erst wieder herausgefunden werden müsste. Das
ist der Grund, warum er hier steht und nicht in einer Stichwortliste: Ein Punkt ohne seinen
Zusammenhang kostet beim zweiten Anlauf dieselbe Arbeit wie beim ersten.

Nichts hiervon ist terminiert. Die Reihenfolge innerhalb der Abschnitte ist grob nach Gewicht.

---

## Verwaltung

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
