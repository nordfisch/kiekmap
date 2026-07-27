# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [Unveröffentlicht]

### Hinzugefügt

- Projektgerüst: Ordnerstruktur, Git-Repo, README
- `docs/decisions.md` mit den Technologieentscheidungen und ihren Begründungen
- `tiles/region.json` als Platzhalter für die Region des Museumsorts
- FastAPI-Backend mit `/api/health`, SQLite im WAL-Modus, Alembic, Dockerfile
- Migrationen laufen beim Containerstart automatisch — auf dem Pi soll niemand daran denken müssen
- `Makefile` mit `dev`, `test`, `lint`, `migrate`, `prod`
- `deploy/docker-compose.yml` für den Betrieb auf dem Pi
