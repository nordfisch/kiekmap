# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [Unveröffentlicht]

### Hinzugefügt

- Projektgerüst: Ordnerstruktur, Git-Repo, README
- `docs/decisions.md` mit den Technologieentscheidungen und ihren Begründungen
- `tiles/region.json` als Platzhalter für die Region des Museumsorts
- FastAPI-Backend mit `/api/health`, SQLite im WAL-Modus, Alembic, Dockerfile
- Migrationen laufen beim Containerstart automatisch — auf dem Pi soll niemand daran denken müssen
- `Makefile` mit `dev`, `test`, `lint`, `migrate`, `tiles`, `prod`
- `deploy/docker-compose.yml` für den Betrieb auf dem Pi
- React-Frontend mit MapLibre und offline gelesenen PMTiles-Vektorkacheln
- `tiles/build-tiles.sh` baut Kacheln, Schriften und Symbole für die Region — Schriften und
  Symbole werden mit heruntergeladen, sonst bliebe die Karte offline ohne Beschriftung
- Grundlayout: Karte mit Zeitschieber darunter, „Hilf mit"-Bereich rechts über die volle Höhe
- nginx-Konfiguration mit Range-Requests für die Kartendatei und `/api`-Proxy
- Datenmodell: Fotos mit Zeitintervall statt Zeitpunkt, Herkunft pro Feld, Schlagwörter,
  Änderungsprotokoll, Ortsverzeichnis, Import-Protokoll
- Import-Pipeline: SHA-256 als Dateiname und Dublettenschutz, EXIF und IPTC, Vorschaubilder in
  zwei Größen, Beachtung der EXIF-Ausrichtung, CMYK-Umwandlung
- **EXIF-Datumsangaben ab 1990 gelten als Scandatum und datieren das Foto nicht** — sonst läge
  ein Foto von 1932 auf der Zeitleiste bei 2019 und würde nie zur Korrektur vorgelegt
- Überwachter Eingangsordner: importiert erst, wenn eine Datei fertig geschrieben ist, und räumt
  sie danach nach `_erledigt/` bzw. `_problem/` — gelöscht wird nie
- `python -m app.cli import|scan|stats` für Massenimport und Bestandsübersicht
- Abfrage-API: `/api/photos` mit Kartenausschnitt und Zeitraum, `/histogram` für den Zeitschieber,
  Auslieferung von Vorschaubild und Original mit dauerhaftem Cache
- Der Zeitfilter fragt auf **Überlappung** der Intervalle ab — ein auf „1920er" datiertes Foto
  erscheint damit auch bei der Auswahl 1925–1930
- Fotos erscheinen als Vorschaubilder an ihrem Aufnahmeort; bei hoher Dichte fasst supercluster
  sie zu einem Kreis mit Anzahl zusammen, der beim Antippen aufgeht
- Foto-Overlay in voller Größe, schließbar per Tippen daneben, Knopf oder Escape
- Zeitschieber mit zwei Griffen und Jahrzehnt-Histogramm im Hintergrund, fingergerecht bemessen
- Kartenbewegung und Zeitraum lösen entprellt genau eine Abfrage aus; überholte werden verworfen
- „Hilf mit"-Bereich: zufällige Fotos ohne Ort oder Jahr, Verortung per Pin auf der Karte oder
  über die Ortssuche, Datierung über Jahrzehnt und optional Jahr
- Besucherbeiträge werden direkt übernommen, aber nur in leere Felder — kuratierte Angaben sind
  unantastbar, und Koordinaten außerhalb der Region werden abgewiesen
- `tiles/build-places.py` baut einen Ortsindex aus OpenStreetMap; die Suche findet „Mühlenweg"
  auch bei Eingabe ohne Umlaut und läuft ohne Internet
- `make places` baut und lädt den Ortsindex, `python -m app.cli places` lädt ihn neu
- Admin-Bereich: Klick auf das Ortswappen über der Karte, PIN auf einem Zahlenfeld mit großen
  Tasten, Sitzung mit Ablauf. Die Sperre nach fünf Fehlversuchen ist der eigentliche Schutz einer
  vierstelligen PIN — sie macht aus Sekunden Jahre
- `python -m app.cli pin` erzeugt den PIN-Hash für die `.env`; die PIN selbst wird nie gespeichert
- Statusübersicht, Fotoliste mit Filter „unvollständig" und Suche, Metadateneditor mit Ortssuche,
  Besucherbeiträge sichten und einzeln zurücknehmen, Import-Protokoll
- Beim Bearbeiten heißt ein **fehlendes** Feld „unverändert lassen", ein **leeres** Feld „löschen" —
  sonst ließe sich eine falsche Datierung nur ersetzen, nie herausnehmen
- Ein Besucherbeitrag lässt sich nicht mehr zurücknehmen, wenn das Feld inzwischen von Hand
  bearbeitet wurde; das würde die Arbeit des Kurators mit wegwerfen
- Stapel-Upload: Ort und Jahr optional für den ganzen Stapel, danach eine Tabelle mit Vorschau,
  Titel aus dem Dateinamen, Jahr und Ort je Bild änderbar, „Übernehmen" und „Alle übernehmen".
  Die Fotos sind schon **nach dem Hochladen** in der Datenbank — ein geschlossener Browser darf
  keine Uploads kosten. Dubletten werden benannt („3 waren schon da")
- Das Ortswappen liegt als austauschbare Datei unter `frontend/public/logo.png`; im Code steht
  nirgends, was darauf zu sehen ist
- Sicherung auf USB-Stick: Stick einstecken, ein Knopf, Fortschrittsbalken, am Ende „Der Stick
  kann jetzt abgezogen werden". Ein Ordner statt eines Archivs — eine abgebrochene Sicherung ist
  so teilweise brauchbar statt komplett wertlos
- Die zweite Sicherung schreibt nur, was dazugekommen ist: der Dateiname ist der Hash des Inhalts,
  ein gleicher Name ist dasselbe Bild
- `VACUUM INTO` schreibt die Datenbank konsistent heraus, ohne den Kiosk anzuhalten
- Als Sicherungsziel gelten nur echte Einhängepunkte, die auch beschreibbar sind — sonst liefe die
  Sicherung auf dieselbe SD-Karte, gegen deren Ausfall sie schützt
- Wiederherstellen kopiert erst daneben und schaltet zuletzt um; der bisherige Stand wird nach
  `data/vorher-<Datum>/` beiseitegelegt, mitsamt Write-Ahead-Log, und nie gelöscht
- Erinnerung „Letzte Sicherung vor 34 Tagen" auf der Startseite der Verwaltung, ab 30 Tagen rot
- `deploy/pi/99-photomap-usb.rules` und `photomap-usb-mount` hängen Sticks auf Pi OS Lite ein —
  dort gibt es keinen Automounter
- „Weiß ich nicht — nächstes Foto" wechselt jetzt die Frage zwischen Ort und Jahr. Wer einen Ort
  nicht erkennt, weiß vielleicht trotzdem das Jahrzehnt; dieselbe Frage noch einmal ist der Grund,
  warum jemand nach drei Bildern aufhört
- Läuft eine der beiden Fragen leer, fällt der „Hilf mit"-Bereich auf die andere zurück, statt
  „alles vollständig" zu melden, während Hunderte Fotos auf eine Jahreszahl warten

### Geändert

- Bezeichner und Code-Kommentare durchgängig auf Englisch; Deutsch bleibt für Oberfläche,
  Fehlermeldungen, Dokumentation und Commit-Nachrichten
- Die beiden Migrationen zu einer initialen zusammengefasst, mit englischen Index- und
  Constraint-Namen — möglich, solange nichts ausgeliefert ist
- `CLAUDE.md` (für Coding-Agents) und `docs/entwicklung.md` (für Entwickler) ergänzt
- `docs/adaption.md` und `docs/stufenplan.md` ergänzt
- Query-Parameter `von`/`bis` heißen jetzt `from_year`/`to_year` — die Konvention verlangt
  Englisch für die API
- Faustregel für Meldungen eingeführt: erscheint sie im Kiosk oder Admin-Bereich, ist sie deutsch,
  sonst englisch. OpenAPI-Beschreibungen sind damit englisch, CLI-Ausgaben bleiben deutsch
- Jahrzehnte der Datumsfrage kommen aus `region.json` statt aus dem Code
- Hausnummern im Ortsindex: Wer eine Straße antippt, wählt danach die Hausnummer aus einem
  Knopfraster — oder tippt „Reicht so", denn nicht jedes Haus steht in OpenStreetMap. Ohne sie
  bekam jedes Foto einer 800 m langen Straße denselben Punkt
- In der freien Suche erscheinen Adressen erst ab einer Ziffer in der Eingabe. Sonst wären die
  zwölf Plätze der Trefferliste nach den Hausnummern einer Straße voll — der Lehmweg hat 139
- Hausnummern werden natürlich sortiert: 1, 1a, 2, 9, 10 — nicht 1, 10, 1a, 2, 9
- `location_accuracy_m` wird endlich benutzt: 150 m für eine Straße, 15 m für eine Hausnummer,
  nichts für einen von Hand getippten Punkt
- Eigener Kartenstil „Papier" in den Farben der Oberfläche: Erde in Papierton, Grün zu Salbei
  entsättigt, Wasser in mattem Graublau statt Türkis. Regel beim Aussuchen: nichts auf der Karte
  darf so gesättigt sein wie ein Foto. Dazu ohne Geschäfte, Hausnummern und Autobahnschilder, und
  mit Straßen auf 80 % ihrer Breite — die kleinen Straßennamen bleiben, an ihnen hängt die
  Verortung
- Kiosk-Aufteilung auf ein Raster aus zwei Spalten und zwei Zeilen: links Titelbereich über
  „Hilf mit", rechts Zeitschieber über der Karte. Der Schieber steht damit weiterhin genau über
  der Karte, die er filtert, und das Wappen führt den Bereich an, statt die Karte zu verdecken.
  Der Ortsname im Titel kommt aus `region.json`

### Behoben

- Marker verschwanden gelegentlich von der Karte: der `load`-Rückruf konnte eine bereits entfernte
  Karteninstanz an die Ebenen weiterreichen. Die Vorschaubilder wurden dann sogar geladen, waren
  aber nie zu sehen
- Karte und Zeitleiste blieben nach einem Besucherbeitrag stehen. Der Dank versprach „Das Foto ist
  jetzt auf der Karte", zu sehen war es aber erst, wenn jemand die Karte verschob — also gerade bei
  den älteren Besuchern, für die der Bereich gebaut ist, gar nicht. Ein Beitrag stößt jetzt ein
  Nachladen von Markern und Histogramm an
