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

### Geändert

- Bezeichner und Code-Kommentare durchgängig auf Englisch; Deutsch bleibt für Oberfläche,
  Fehlermeldungen, Dokumentation und Commit-Nachrichten
- Die beiden Migrationen zu einer initialen zusammengefasst, mit englischen Index- und
  Constraint-Namen — möglich, solange nichts ausgeliefert ist
- `CLAUDE.md` (für Coding-Agents) und `docs/entwicklung.md` (für Entwickler) ergänzt
