# Architecture

What the system is made of, and how the parts fit together. This file answers **what is there** —
not *why it is like this*, and not *how to work on it*:

| File | Question |
|---|---|
| **architecture.md** | *What* is there, and how does it fit together? |
| [decisions.md](decisions.md) | *Why* is it this way and not another? |
| [development.md](development.md) | *How* do you work on it? — setup, tests, conventions |
| [history.md](history.md) | *How* did it come about? |
| [operations.md](operations.md) | How does the device run in the museum? |

The full overview is in [index.md](index.md).

Where this file only names a decision, its reasoning is in `decisions.md`. The directory tree is
in `development.md`; the connections are here.

---

## The whole thing at a glance

```
   DEVELOPMENT MACHINE (online)                MUSEUM DEVICE (offline)
   ───────────────────────────────────         ──────────────────────────────────────────

   tiles/region.json                                    ┌──────────────┐
        │                                               │   Chromium   │  no container
        ├──► build-tiles.sh ──► map.pmtiles ────────┐   │  under cage  │
        │      (OpenStreetMap)   basemaps/          │   └──────┬───────┘
        │                                           │          │ port 80
        └──► build-places.py ──► places.json ───┐   │          ▼
               (Overpass)                       │   │   ┌──────────────┐
                                                │   └──►│    nginx     │  container 1
                                                │       │  + frontend  │
                                                │       └──┬────────┬──┘
                                                │          │        │ /api → proxy
                                                │   map,   │        ▼
                                                │   page   │  ┌──────────────┐
                                                └──────────┼─►│   FastAPI    │  container 2
                                                           │  │  + watcher   │
                                                           │  └──────┬───────┘
                                                           │         │
                                                           │         ▼
                                                           │   data/  (on the SD card)
                                                           │   ├── kiekmap.db   SQLite
                                                           │   ├── photos/      originals
                                                           │   ├── thumbs/      thumbnails
                                                           │   └── places.json ──┘ read in once
```

Three processes, two of them in containers. **Chromium is deliberately not one** — it runs as an
ordinary program on the Pi and only displays what the other two serve.

---

## The parts

### Backend — FastAPI and SQLite

The only way to the data. It holds the database, the image files and every rule; the frontend
knows no file and no table, only the API under `/api`.

Inside the backend one separation carries the testability: `app/api/` validates parameters, calls
a service and returns a schema — thin. `app/services/` holds the domain logic **without any HTTP
context**, and that is where the thinking belongs. Anything that can be tested without HTTP goes
there.

Two things happen at startup (`lifespan` in `app/main.py`): the place index is read in if the
table is empty, and the **incoming watcher** starts. It is a thread in the same process, not a
service of its own.

### Frontend — React, MapLibre and nginx

A single page with two views. There is **no router**: `App.tsx` decides from the state in the
`useAdmin` store whether to render the kiosk view (`src/kiosk/`), the PIN pad or the admin area
(`src/admin/`). On a device without an address bar a router would be ballast — and a URL somebody
leaves behind by accident would be a risk.

In production **nginx** serves the built page and proxies `/api` to the backend. Both therefore
come from the same origin; the CORS setting in the backend exists for the Vite development server
and never applies on the Pi.

nginx does more here than serve files: it answers **HTTP range requests** on the map file. That is
exactly why the project needs no tile server — MapLibre reads single tile ranges out of a static
file over `pmtiles://`. The configuration turns `gzip` off at that location; a compressing or
buffering step in between would destroy it.

### Tiles and place index — build artifacts

Both are produced on the development machine with internet access and are **not** in the
repository. From there they take separate paths, and that is where the two scripts differ:

| | produces | ends up in | path at runtime |
|---|---|---|---|
| `tiles/build-tiles.sh` | `map.pmtiles`, fonts, sprites | `frontend/public/` | goes into the frontend image, served by nginx |
| `tiles/build-places.py` | `places.json` | `data/` | read by the backend into the `places` table |

The map style points at a CDN by default. Fonts and sprites are therefore downloaded along with
the tiles and live under `frontend/public/basemaps/` — otherwise the map would have areas offline
but no labels.

### Kiosk layer on the Pi

Everything under `deploy/pi/`, and all of it **unverified** (see [backlog.md](backlog.md)):
`setup-pi.sh` sets up a fresh device, `kiekmap-kiosk.service` waits for `/api/health` and then
starts `cage` with Chromium in full screen, `update.sh` applies an update from a USB stick, and a
udev rule mounts USB sticks — Pi OS Lite has no automounter.

---

## What is produced when

The most important distinction in the whole architecture, because it settles what a second museum
has to do and what happens on its own:

**At build time** (development machine, internet required): map file, fonts, sprites and place
index, all from `tiles/region.json`. Plus the frontend bundle.

**At runtime** (device, offline): everything else. The map extent, the place name in the title and
the zoom levels are **not** baked into the bundle; they are fetched from `/tiles/region.json` at
startup. The same file therefore serves two purposes: it drives the build, and it configures the
running view.

From this follows the property that holds the project together: **nothing place-specific is in the
code.** A second museum needs no fork, only its own `region.json` and `.env`. The procedure is in
[adaption.md](adaption.md).

---

## Where the state lives

In three places, each with a job of its own:

**SQLite** (`data/kiekmap.db`) holds every piece of data — photos, datings, places, tags, the
change log, the import log and the place index. In WAL mode, so that a power cut costs at most the
last transaction. Schema changes go through Alembic and are applied when the container starts.

**The file system** (`data/photos/`, `data/thumbs/`) holds the images. The file name is the
**SHA-256 of the image content**, and three things hang on that: duplicate detection on import,
the cache headers when serving, and the incremental backup. The same name is the same image,
everywhere.

**The browser** holds only the admin token, in `sessionStorage`. It dies with the tab, so on the
Pi at the latest with the morning restart. Everything else in the frontend is transient state in
Zustand stores (`src/store/`), one per area.

Next to these sits **`seed/`**, and it is explicitly *not* part of the device state: a sample
collection for development, which `make seed` turns into `data/` and `make seed-save` writes back.
Image files plus a `seed.json`, so that a new column does not make it worthless; it never appears
on the Pi. See [decisions.md](decisions.md), point 18.

---

## The paths through the system

### A photo comes in

Four ways, one destination — they all run through `import_file()` in
`app/services/importer.py`, which always writes a row to the import log:

1. **Watched incoming folder** — the watcher takes a file once it is fully written, then moves it
   to `_erledigt/` or `_problem/`. Nothing is ever deleted. **One exception: it leaves ZIP files
   named like a backup alone** — those are not a photo but a whole collection, and they are only
   restored after a confirmation.
2. **Upload in the admin area** — the way for forty selected files.
3. **USB stick in the admin area** — the way for a folder of two hundred scans, subfolders
   included. **Nothing on the stick is moved and nothing is deleted**, unlike in the incoming
   folder.
4. **`python -m app.cli import`** — for the initial collection.

The import computes the hash, stores the original and two thumbnail sizes, and then reads what is
already there in **two layers** (reasoning in [decisions.md](decisions.md), point 20):

| Layer | Where | Applies to | What it reads |
|---|---|---|---|
| **Metadata** | `import_file()` | all four ways | date, GPS, title, description, credit, provenance, tags from EXIF/IPTC |
| **Path** | `foldermeta.py` | 1, 3, 4 | street and house number from the folder names |

The second layer is switched on through the `root` parameter of `import_file()` — the folder the
import was started on. That the decision sits there and not with the caller is not a matter of
taste: it hung on the caller for a while, and the incoming folder did not have it.

An upload has no path, so only the first layer applies there, and the shared values come from the
form as before. The second layer is a pure module with no HTTP context: it receives the path
segments and the place index and returns which street and which house number are in them. **The
place index recognises the street**, not a folder called „Straßen" — which is why nothing
place-specific is in the code despite this parsing.

Two precedence rules hold it together: a coordinate from the file beats the folder, and the path
layer fills **empty fields only**.

Whether an EXIF date dates the photo is decided first by the **device**: a scanner dates nothing,
a camera dates even after 1990, and where no device is named, `exif_date_max_year` still decides.
Without these rules a photo from 1932 would sit on the timeline at the date of the scanning run
and never come up for correction — and the genuine 2014 shots would arrive undated.

### A visitor contributes something

The „Hilf mit" panel fetches a photo that is missing a place or a year through
`/api/contribute/next`. The contribution goes straight into the collection — but **into empty
fields only**: what a curator entered is untouchable, and coordinates outside the region are
rejected. Every contribution also lands as a row in `changes` and can be taken back one by one,
as long as nobody has edited the field by hand in the meantime.

After a contribution the view settles on that one photo for the length of the thank-you — map and
time slider together, driven by a focus signal in the kiosk store.

### The map queries photos

`/api/photos` takes a map extent and optionally a time range. Two things about it are not obvious.

The time filter queries for **overlap** of the intervals, not for containment — a photo dated
„1920er" has to appear for the selection 1925–1930. And the answer is deliberately narrow:
description, tags and provenance fields come only when a photo is tapped.

In the frontend, photos at **the same spot** are merged into one marker before clustering;
supercluster never sees the duplicates. Without that, eight photos would lie exactly on top of
each other and only the topmost would be reachable.

### Backup, restore, stick import

These three share **one** job (`Job` in `app/services/backup/job.py`). They run in a thread,
report their progress, and only one can run at a time — two concurrent write runs against the same
SQLite file would be a source of errors for no gain. The frontend polls the status once a second.

---

## What to know at the edges

**The offline promise is testable, and it is tested.** The page must make **zero** requests to a
foreign origin. The one-liner for it is in [development.md](development.md).

**Foreign keys and migrations get along badly in SQLite.** Rebuilding a table drops the original,
and with the check switched on that clears out whatever hangs off it. `alembic/env.py` therefore
turns it off for the duration of a migration; in production it stays on. A test pins this down,
and the story is in
[history.md](history.md#fotos-löschen--und-ein-datenverlust-der-beinahe-unbemerkt-geblieben-wäre).

**The Pi has no browser controls.** No reload button, no address bar, no keyboard. That is why the
idle reset after five minutes reloads the page instead of only resetting the state, and why
leaving the admin area reloads as well.

**The place index knows only streets and house numbers.** Buildings, water and fields are not in
it — for those there is the pin on the map.
