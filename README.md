# Photomap

Interaktive Bilddatenbank für ein Heimatmuseum: historische Ortsfotos, räumlich und zeitlich
erkundbar an einem Touchscreen — und ein Weg, das Wissen der Besucher einzusammeln.

Das Gerät steht im Museum, läuft **vollständig offline** im Kiosk-Modus und wird gesichert, indem
man einen USB-Stick einsteckt und einen Knopf drückt.

## Was der Besucher sieht

```
┌────────────────────────────────────────┬──────────────┐
│                                        │  HILF MIT    │
│         Karte des Ortes                │              │
│         Fotos an ihrem Aufnahmeort     │  [Foto]      │
│         Tippen öffnet sie groß         │  "Wo ist     │
│                                        │   das?"      │
├────────────────────────────────────────┤              │
│  1880 ├──●━━━━━━━━━━━━━━━●──┤ 1990     │  [Karte][×]  │
└────────────────────────────────────────┴──────────────┘
```

Karte zoomen und den Zeitraum-Schieber bewegen filtert die Fotos. Rechts fragt der
„Hilf mit"-Bereich nach fehlenden Angaben — *„Wo ist das?"*, *„Von wann ist dieses Bild?"* —, denn
bei historischen Scans steht das nirgends in der Datei. Wer den Ort kennt, ergänzt die Datenbank im
Vorbeigehen.

## Aufbau

| Ordner | Inhalt |
|---|---|
| `backend/` | FastAPI + SQLite: Fotos, Metadaten, Import, API |
| `frontend/` | React + MapLibre: Besucheransicht (`src/kiosk/`) und Admin (`src/admin/`) |
| `tiles/` | Skripte, die die Offline-Karte und die lokale Ortssuche bauen |
| `deploy/` | Docker Compose und die Einrichtung des Raspberry Pi |
| `docs/` | Entscheidungen, Betriebshandbuch, Anleitung für Ehrenamtliche |
| `data/` | Laufzeitdaten (nicht im Repo): Datenbank, Fotos, Thumbnails |

## Entwicklung

Voraussetzungen: Python 3.12+, Node 18+, optional Docker.

```bash
make dev
```

Startet Backend (Port 8000, API-Doku unter `/api/docs`) und Frontend (Port 5173) mit Hot Reload.
Vite leitet `/api` an das Backend weiter, sodass in Entwicklung und Betrieb dieselben Pfade gelten.

`make` ohne Ziel zeigt alle Kommandos.

| Kommando | Zweck |
|---|---|
| `make dev` | Backend und Frontend mit Hot Reload |
| `make seed` | Beispielfotos importieren |
| `make test` | pytest und vitest |
| `make tiles` | Offline-Karte und Ortsindex für die konfigurierte Region bauen |
| `make prod` | Alles in Containern, so wie es auf dem Pi läuft |

## Betrieb

Der Pi bootet direkt in die Karte — kein Login, kein Desktop, keine Bedienung nötig.
Einrichtung, Sicherung, Wiederherstellung und Fehlersuche stehen in [docs/betrieb.md](docs/betrieb.md).
Die Kurzanleitung zum Ausdrucken für die Ehrenamtlichen ist
[docs/kuratoren-anleitung.md](docs/kuratoren-anleitung.md).

Warum die Technik so gewählt ist, steht in [docs/decisions.md](docs/decisions.md).

## Lizenz

Noch festzulegen. Alle verwendeten Komponenten sind Open Source.
