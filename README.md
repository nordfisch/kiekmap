# Photomap

Interaktive Bilddatenbank für ein Heimatmuseum: historische Ortsfotos, räumlich und zeitlich
erkundbar an einem Touchscreen — und ein Weg, das Wissen der Besucher einzusammeln.

Das Gerät steht im Museum, läuft **vollständig offline** im Kiosk-Modus und wird gesichert, indem
man einen USB-Stick einsteckt und einen Knopf drückt.

## Was der Besucher sieht

```
┌──────────────┬────────────────────────────────────────┐
│ [Wappen]     │  1920 ├──●━━━━━━━━━━━━━━━●──┤ 2019     │
│ Bilder aus   │                                        │
│ HOLM         │                                        │
├──────────────┼────────────────────────────────────────┤
│  HILF MIT:   │                                        │
│              │         Karte des Ortes                │
│  [Foto]      │         Fotos an ihrem Aufnahmeort     │
│  "Wo ist     │         Tippen öffnet sie groß         │
│   das?"      │                                        │
│              │                                        │
│  [Karte][×]  │                                        │
└──────────────┴────────────────────────────────────────┘
```

Karte zoomen und den Zeitraum-Schieber bewegen filtert die Fotos. Der Schieber steht über der
Karte, die er filtert — nicht über dem Beitragsbereich. Links fragt der „Hilf mit"-Bereich nach
fehlenden Angaben — *„Wo ist das?"*, *„Wann war das?"* —, denn bei historischen Scans steht das
nirgends in der Datei. Wer den Ort kennt, ergänzt die Datenbank im Vorbeigehen. Ist nichts mehr
offen, fällt der Bereich weg und die Karte nimmt die volle Breite.

Das Wappen führt die linke Spalte an und ist zugleich der Weg in die Verwaltung.

## Aufbau

| Ordner | Inhalt |
|---|---|
| `backend/` | FastAPI + SQLite: Fotos, Metadaten, Import, API |
| `frontend/` | React + MapLibre: Besucheransicht (`src/kiosk/`) und Admin (`src/admin/`) |
| `tiles/` | Skripte, die die Offline-Karte und die lokale Ortssuche bauen |
| `deploy/` | Docker Compose und die Einrichtung des Raspberry Pi |
| `docs/` | Die ganze Dokumentation — Wegweiser: [docs/index.md](docs/index.md) |
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
| `make seed` | Beispielbestand aus `seed/` herstellen — [noch nicht mitgeliefert](seed/README.md) |
| `make empty` | Den ganzen Fotobestand löschen. Fragt nach und ist nicht rückholbar |
| `make test` | pytest und vitest |
| `make tiles` | Offline-Karte und Ortsindex für die konfigurierte Region bauen |
| `make prod` | Alles in Containern, so wie es auf dem Pi läuft |

Einrichtung im Detail, Sprachregelung, Teststrategie und die Fallstricke, die Zeit gekostet haben:
[docs/development.md](docs/development.md). Für Coding-Agents: [CLAUDE.md](CLAUDE.md).

**Für einen anderen Ort:** Es genügt, `tiles/region.json` anzupassen und `make tiles && make places`
auszuführen — kein Fork, kein Codeeingriff. Schritt für Schritt in
[docs/adaption.md](docs/adaption.md).

## Betrieb

Der Pi bootet direkt in die Karte — kein Login, kein Desktop, keine Bedienung nötig.
Einrichtung, Sicherung, Wiederherstellung und Fehlersuche stehen in
[docs/operations.md](docs/operations.md). Die Kurzanleitung zum Ausdrucken für die Ehrenamtlichen
ist [docs/usermanual.md](docs/usermanual.md).

Woraus das System besteht und wie die Teile zusammenspielen, steht in
[docs/architecture.md](docs/architecture.md); warum die Technik so gewählt ist, in
[docs/decisions.md](docs/decisions.md); wie es dazu gekommen ist, in
[docs/history.md](docs/history.md). Was noch offen ist, im [docs/backlog.md](docs/backlog.md).
Welche Datei welche Frage beantwortet, sagt [docs/index.md](docs/index.md).

## Lizenz

Noch festzulegen. Alle verwendeten Komponenten sind Open Source.
