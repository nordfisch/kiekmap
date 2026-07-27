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
