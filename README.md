# Kiekmap

[![check](https://github.com/nordfisch/kiekmap/actions/workflows/check.yml/badge.svg?branch=develop)](https://github.com/nordfisch/kiekmap/actions/workflows/check.yml)
[![Lizenz: Apache 2.0](https://img.shields.io/badge/Lizenz-Apache%202.0-blue.svg)](LICENSE)

Historische Ortsfotos auf einer Karte entdecken, Jahrzehnt für Jahrzehnt. Ein Touchscreen-Kiosk
fürs Heimatmuseum: Läuft offline auf einem Raspberry Pi, lässt sich an jeden Ort anpassen, und die
Besucher ergänzen, was fehlt. Ein Freizeitprojekt von Kalle Erlhoff für das Heimatmuseum Holm,
erstellt in Zusammenarbeit mit Anthropic Claude Code.

> **Achtung: Arbeitsstand.** Was hier liegt, ist der Stand, der beim **Aufbau des Erstbestands**
> entstanden ist — 929 historische Fotos, eingelesen, bereinigt und durchgesehen. Gelaufen ist das
> bisher **ausschließlich lokal**: als Entwicklungsserver und in Containern, beides auf einem Mac.
>
> **Auf einem Raspberry Pi oder einem Webserver wurde es bisher noch nicht installiert.** Alles
> unter `deploy/pi/` ist ohne Gerät geschrieben — die Syntax stimmt, ausgeführt wurde nichts.
> Ungeprüft sind damit der Kiosk-Betrieb, der USB-Weg der Sicherung und das Verhalten nach
> Neustart und Stromausfall. Der erste echte Aufbau ist zugleich die Abnahme:
> [Punkt 15](https://github.com/nordfisch/kiekmap/issues/18) und [Punkt 21](https://github.com/nordfisch/kiekmap/issues/22).
>
> Geprüft ist, was sich ohne Gerät prüfen lässt: Die Container bauen und laufen, die Seite fragt
> nichts Fremdes an, und 647 Tests laufen durch.

Das Gerät soll im Museum stehen, **vollständig offline** im Kiosk-Modus laufen und gesichert
werden, indem man einen USB-Stick einsteckt und einen Knopf drückt.

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
| `make seed` | Beispielbestand aus `seed/` herstellen — [alles darin ist erfunden](seed/README.md) |
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
[docs/history.md](docs/history.md). Was noch offen ist, in den [Issues](https://github.com/nordfisch/kiekmap/issues).
Welche Datei welche Frage beantwortet, sagt [docs/index.md](docs/index.md).

## Mitwirken

Wie man einsteigt, welche Regeln hier gelten und was man erwarten darf — ein Betreuer, nebenher,
ohne zugesagte Antwortzeit —, steht in [CONTRIBUTING.md](CONTRIBUTING.md). Zum Umgangston:
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Eine Sicherheitslücke gehört **nicht** in eine
öffentliche Meldung; der Weg steht in [SECURITY.md](SECURITY.md).

**Am meisten hilft ein zweites Museum, das es aufsetzt und berichtet.** Die Anleitung dafür ist
ohne Gerät geschrieben worden; jeder Stolperstein daraus ist wertvoller als jede neue Funktion.

## Lizenz

Copyright 2026 Kalle Erlhoff, lizenziert unter der **Apache-Lizenz 2.0** (`SPDX-License-Identifier:
Apache-2.0`). Der Lizenztext steht in [LICENSE](LICENSE), die Namensnennung in [NOTICE](NOTICE);
beide reisen mit jeder Weitergabe mit.

**Alle 169 verwendeten Fremdkomponenten sind permissiv lizenziert** — nachgezählt an den
installierten Paketen, nicht an den Manifestdateien: MIT, ISC, BSD-2, BSD-3, Apache-2.0, HPND und
PSF. Kein Copyleft, nichts, was einer Nutzung im Weg steht.

**Die Kartendaten sind eine eigene Frage.** Sie stammen aus OpenStreetMap und stehen unter der
**ODbL 1.0**; die Schriften unter der OFL 1.1, die Kartensymbole unter MIT. Was das für eine
Weitergabe bedeutet — und was der Fotobestand des Museums damit zu tun hat, nämlich nichts —,
steht in [docs/licensing.md](docs/licensing.md).

Ohne Gewähr, ohne Haftung, wie in Abschnitt 7 und 8 der Lizenz beschrieben.
