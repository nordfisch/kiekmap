# Kiekmap

[![check](https://github.com/nordfisch/kiekmap/actions/workflows/check.yml/badge.svg?branch=develop)](https://github.com/nordfisch/kiekmap/actions/workflows/check.yml)
[![Licence: Apache 2.0](https://img.shields.io/badge/Licence-Apache%202.0-blue.svg)](LICENSE)

> **Deutsch:** [README.de.md](README.de.md) · [Benutzung](docs/usermanual.md) ·
> [Betrieb](docs/operations.md) · [Übernahme](docs/adaption.md)

Discover historic pictures of a village on a map, decade by decade. A touchscreen kiosk for a local
history museum: it runs offline on a Raspberry Pi, adapts to any place, and the visitors fill in
what is missing. A spare-time project by Kalle Erlhoff for the Heimatmuseum Holm, built together
with Anthropic Claude Code.

> **Careful: work in progress.** What lies here is the state that came out of **building the
> initial collection** — 929 historic photos, taken in, cleaned up and looked through. So far it
> has run **locally only**: as a development server and in containers, both on a Mac.
>
> **It has not yet been installed on a Raspberry Pi or on a web server.** Everything under
> `deploy/pi/` was written without a device — the syntax is right, nothing has been run. Kiosk
> operation, the USB path of the backup and the behaviour after a restart or a power cut are
> therefore unverified. The first real setup is at the same time the acceptance test:
> [issue #18](https://github.com/nordfisch/kiekmap/issues/18) and
> [issue #22](https://github.com/nordfisch/kiekmap/issues/22).
>
> What can be checked without a device is checked: the containers build and run, the page requests
> nothing from a foreign origin, and the test suite is green.

The device is meant to stand in the museum, run **entirely offline** in kiosk mode, and be backed
up by plugging in a USB stick and pressing one button.

## What a visitor sees

![The visitor view: the „Hilf mit" panel on the left, the time slider and the map on the
right](docs/images/kiosk-map.png)

*The device in Holm, in German. `KIEKMAP_LANGUAGE=en` switches the same screen to English.*

Zooming the map and moving the time slider filters the photos. The slider sits above the map it
filters — not above the contribution panel. On the left, the „Hilf mit" panel asks for what is
missing — *"Where is this?"*, *"When was this?"* — because with historic scans none of that stands
in the file. Whoever knows the place fills the database in passing. Once nothing is open any more,
the panel falls away and the map takes the full width.

A tap opens a photo at full size, with everything known about it: the dating, the address, the
keywords, the credit — and the identifier, so that it can be found again in the archive.

![The detail view: the photo at full size, its statements beside it](docs/images/kiosk-detail.png)

The coat of arms heads the left column and is at the same time the way into the admin area.

Behind it lies the admin view, used once or twice a year by volunteers: what the collection holds,
what is still missing, and how long ago the last backup was.

![The admin view: nine tiles with the state of the collection](docs/images/admin-overview.png)

## Layout

| Folder | Content |
|---|---|
| `backend/` | FastAPI + SQLite: photos, metadata, import, API |
| `frontend/` | React + MapLibre: the visitor view (`src/kiosk/`) and the admin view (`src/admin/`) |
| `tiles/` | Scripts that build the offline map and the local place search |
| `deploy/` | Docker Compose and the setup of the Raspberry Pi |
| `docs/` | All the documentation — signpost: [docs/index.md](docs/index.md) |
| `data/` | Runtime data (not in the repository): database, photos, thumbnails |

## Development

Prerequisites: Python 3.12+, Node 18+, Docker optional.

```bash
make dev
```

Starts the backend (port 8000, API docs under `/api/docs`) and the frontend (port 5173) with hot
reload. Vite passes `/api` on to the backend, so development and production share the same paths.

`make` without a target lists every command.

| Command | Purpose |
|---|---|
| `make dev` | backend and frontend with hot reload |
| `make seed` | build the sample collection from `seed/` — [everything in it is invented](seed/README.md) |
| `make empty` | delete the whole photo collection. It asks first, and there is no way back |
| `make test` | pytest and vitest |
| `make tiles` | build the offline map and the place index for the configured region |
| `make prod` | everything in containers, the way it runs on the Pi |

Setup in detail, the language rule, the testing strategy and the traps that cost time:
[docs/development.md](docs/development.md). For coding agents: [CLAUDE.md](CLAUDE.md).

**For a different place:** adjusting `tiles/region.json` and running `make tiles && make places` is
enough — no fork, no change to the code. Step by step in [docs/adaption.md](docs/adaption.md).

**For a different language:** one line in the `.env`. `KIEKMAP_LANGUAGE=en` switches the visitor
view, the admin area, the messages and the date labels, without a new build.

## Operation

The Pi boots straight into the map — no login, no desktop, nothing to operate. Setup, backup,
restore and troubleshooting are in [docs/operations.md](docs/operations.md). The short guide to
print out for the volunteers is [docs/usermanual.md](docs/usermanual.md), in German.

What the system is made of and how the parts fit together is in
[docs/architecture.md](docs/architecture.md); why the technology was chosen this way, in
[docs/decisions.md](docs/decisions.md); how it came about, in
[docs/history.de.md](docs/history.de.md), in German. What is still open is in the
[issues](https://github.com/nordfisch/kiekmap/issues). Which file answers which question is in
[docs/index.md](docs/index.md).

## Contributing

How to get started, what rules apply here and what you may expect — one maintainer, on the side, no
promised response time — is in [CONTRIBUTING.md](CONTRIBUTING.md). On the tone:
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). A security vulnerability does **not** belong in a public
issue; the way is described in [SECURITY.md](SECURITY.md).

**What helps most is a second museum that sets it up and reports back.** The guide for that was
written without a device; every stumbling block from it is worth more than any new feature.

## Licence

Copyright 2026 Kalle Erlhoff, licensed under the **Apache License 2.0**
(`SPDX-License-Identifier: Apache-2.0`). The licence text is in [LICENSE](LICENSE), the attribution
in [NOTICE](NOTICE); both travel with every copy.

**Every third-party component in use is permissively licensed** — counted against the installed
packages, not against the manifest files: MIT, ISC, BSD-2, BSD-3, Apache-2.0, HPND and PSF. No
copyleft, nothing that stands in the way of using it.

**The map data is a question of its own.** It comes from OpenStreetMap and is under the
**ODbL 1.0**; the fonts under the OFL 1.1, the map sprites under MIT. What that means for passing
it on — and what the museum's photo collection has to do with it, namely nothing — is in
[docs/licensing.md](docs/licensing.md).

Without warranty and without liability, as described in sections 7 and 8 of the licence.
