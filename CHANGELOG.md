# Changelog

Format after [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning after SemVer.

## [Unreleased]

### Added

- **The device speaks German or English**, decided by `KIEKMAP_LANGUAGE` in the `.env`. It switches
  the visitor view, the admin area, the messages, the import log, the date labels and the number
  format. **No new build** — the frontend fetches the language at startup. An unknown value aborts
  the start instead of falling back in silence. A museum that does not speak German no longer needs
  a fork. See [point 73](docs/decisions.md)
- **A documentation site**, [nordfisch.github.io/kiekmap](https://nordfisch.github.io/kiekmap/),
  in both languages and built from the newest tag: the museum reads the documentation for the
  version it runs. MkDocs Material, deployed by Actions. See [point 72](docs/decisions.md)
- **`tools/check_translations.py`** — every German file carries the hash of the English text it was
  made from, and the check reports what has drifted apart. It is the condition under which the
  project keeps a text twice at all
- **The repository is public** — `github.com/nordfisch/kiekmap`, Apache-2.0, with GitHub's private
  security reporting, branch protection for `main` and `develop`, secret scanning, and a badge in
  the README

### Changed

- **The repository speaks English; German is a translation and is marked as one.** The boundary
  used to run through the repository by audience; it now runs between the repository and what is
  published from it. `operations.de.md` is German, `operations.md` is English — the file name
  carries the rule, so there is no list to keep. Issues, labels, commit messages from 30 August
  2026, and every test name are English. See [point 71](docs/decisions.md)
- **`docs/archive/history.de.md` is closed, and nothing succeeds it.** It ends on 25 August 2026 with
  v0.8.0 and stays German. What the work teaches becomes a point in `decisions.md`; how it went
  stays in the commits and the closed issues
- **The open items are GitHub issues**, `docs/backlog.md` is gone. The **number register** now sits
  in `history.de.md` and resolves every "Punkt N" — the open ones to their issue, the rest to the
  section under their date. They could not become issue numbers, because GitHub shares one counter
  with the pull requests; "Punkt 15" became issue #18. See [point 69](docs/decisions.md)
- **The developer documentation is English** — `architecture`, `development`, `decisions`,
  `CONTRIBUTING` and `CLAUDE.md`, about 24,000 words. `decisions.md` was consolidated first: all 67
  points stay, the text is a third shorter
- **The `0.8.0` block below was condensed**, grouped by area rather than by working step. The
  detail is in `history.de.md` and in the commits
- **`tools/language_check.py` checks both sides** and every format, not only `.py`, `.ts` and
  `.tsx`: German documentation for transcribed umlauts, English documentation for German
  paragraphs, and the comments of CSS, Dockerfiles, shell scripts and configuration files
- **The museum documentation is bilingual.** `usermanual`, `operations`, `adaption`, `licensing`,
  `index`, the README and the CHANGELOG exist as an English original and a German translation.
  Checking the German sources against the writing rules first turned up four errors, among them a
  package count contradicting its own table and an instruction for a setting that no longer exists
- **The CLI, the tools, the `Makefile`, `deploy/` and the workflows are English**, output included:
  `dubletten` is `duplicates`, `--abstand` is `--distance`. The folders in the inbox are `_done`
  and `_problem` in both languages — they are names in the file system, and a changed setting must
  not have to rename folders
- **`tools/check_anchors.py` reads `CLAUDE.md` and `CONTRIBUTING.md` as well**
- **A count in front of a list is gone** wherever the list stands right below it. Four files said
  "five" and listed six; a number in prose goes stale in silence. See
  [point 59](docs/decisions.md)
- **Vitest from 2 to 3.** Not for a feature: Vitest 2 brought its own old copies of `vite` and
  `esbuild`, and five of six Dependabot reports hung on those

### Fixed

- **The map credit was German in the English instance.** It stood hard-wired in the map style
  instead of the text catalogue
- **Twenty interface texts stayed German in the English instance**, because they were read at
  module level before the language was resolved. A test now walks the sources with the TypeScript
  parser and fails on any read outside a function

### Removed

- **The SPDX headers are gone from every source file.** Two lines of licence bookkeeping above each
  docstring; the licence does not demand them and no check enforced them. `LICENSE` and `NOTICE`
  cover every distribution of the repository. A single file copied out on its own now carries no
  notice — the price is in [point 70](docs/decisions.md)

## [0.8.0] — 2026-08-25

The first numbered version. **Not a milestone of function** but the point at which the project can
hold on to itself: one version number in one place, pinned dependencies, a release process, and a
verified origin for every commit.

**Why 0.8 and not 1.0:** under SemVer `1.0.0` promises a stable public interface. Everything under
`deploy/pi/` is still unverified and the acceptance on the first device is outstanding. The `1.0.0`
comes after that — see [issue #18](https://github.com/nordfisch/kiekmap/issues/18).

**This block is ordered by area, not by Added, Changed and Fixed.** Before 0.8.0 there was no
version to change anything against; everything here is new. The steps it grew from are in
[docs/archive/history.de.md](docs/archive/history.de.md) and in the commits. From 0.9.0 the three headings apply
again.

### Map and timeline

- Historic photos as thumbnails at the place they were taken, on a **vector map read offline**.
  Crowded ones become one circle with a count; photos at the same spot form a stack to page through
- A map style of its own, **"paper"**: nothing on the map is as saturated as a photograph
- **A time slider with three handles** — the two ends and the whole range. The axis always shows
  the entire collection, so the same position always means the same year
- **The time filter queries for overlap.** A photo dated "1920er" appears for the selection
  1925–1930 as well; with the obvious query most of the collection would disappear
- **A switch for the photos without a year**, on to begin with. An undated photo overlaps no range
  and would otherwise drop out of every selection — two thirds of this collection
- **A detail view at full size** with title, description, address, credit, the short SHA-256, and a
  pencil that leads into editing after the PIN

### The contribution panel

- **Three questions for the visitor:** "Wo ist das?", "Wann war das?" and, after those, "Welche
  Hausnummer?"
- **Not one input field, no keyboard.** Street by initial and buttons, dating by decade and then
  year, house number by section and a grid
- **Contributions land in the collection at once, but only in empty fields.** Curated statements
  are untouchable, coordinates outside the region are refused
- **After a contribution the same photo comes back with the other question**, as long as it is
  missing something
- **A tap on the map only counts once it is asked for** — before that, a searching visitor set a
  point by accident
- **When a question runs dry the panel falls back to the other.** With nothing left to add it
  disappears and the map takes the full width

### Admin area

- **Entry through the coat of arms and a PIN**, in a session that expires. The lock after five
  wrong attempts is what makes four digits defensible
- **An overview in which every number is a way in**, and below it the operation: days since backup,
  import and last contribution
- **A photo list with the filters "Ohne Ort" and "Ohne Jahr"**, search and paging. Locating and
  dating are two jobs
- **A metadata editor.** A **missing** field means "leave unchanged", an **empty** one means
  "delete" — otherwise a wrong dating could only be replaced, never removed
- **Moderation:** take back visitor contributions one at a time, unless the field has since been
  edited by hand
- **Deleting means taking out of the exhibition.** File and row stay and can be restored
- **A batch import with a table for the follow-up work.** The photos are saved as soon as they are
  uploaded — a closed browser must not cost uploads

### Import

- **Four ways, one pipeline:** the watched inbox folder, the CLI, an upload in the browser and a
  USB stick. SHA-256 as the file name and as duplicate protection, EXIF, IPTC and XMP, two
  thumbnail sizes, orientation, CMYK conversion, JPEG, TIFF and MPO
- **Whether an EXIF date dates the photo is decided by the device.** Where the file names none,
  `exif_date_max_year` applies: a date from 1990 on is the scan, not the shot
- **The path is read.** `Hauptstraße/14 Gasthof Petersen/` becomes place, title, place name and
  keywords, and the street is recognised by the place index rather than by a folder name
- **The archive folder beats the EXIF coordinate** as soon as it names a house number. Measured:
  278 of 413 EXIF-located photos shared their coordinate with another — such values are typed in,
  not measured
- **What looks like a statement and is none gets discarded:** "OLYMPUS DIGITAL CAMERA" as a title,
  "unbekannt" as the photographer, the name of the scanning software
- **A place index from OpenStreetMap**, streets and house numbers only. Same-named streets are
  separated spatially, numbers sort naturally, and the search finds "Mühlenweg" without the umlaut
- **Tools for the initial import:** `empty`, `dubletten` and `tools/to_jpeg.py`
- **The collection stands at 1324 photos** from two archive deliveries; 45 duplicates are out of
  the exhibition, 1275 are on the map

### Backup

- **Onto a USB stick: plug it in, one button, a progress bar.** A folder rather than an archive, so
  an aborted backup is partly usable; the second run writes only what is new
- **Only real, writable mount points count as a target** — otherwise the backup lands on the same
  SD card it protects against
- **Restoring copies beside first and switches over last.** The previous state moves aside and is
  never deleted; a backup from a newer version is refused before anything is replaced
- **Also as one ZIP file** for the case without a stick, read back through the inbox folder
- **A reminder on the overview**, red from 30 days on

### Kiosk operation on the Pi

- **`setup-pi.sh` sets up a fresh Raspberry Pi**, `kiekmap-kiosk.service` starts Chromium full
  screen under cage once `/api/health` answers, with a fresh profile and a restart after a crash
- **`update.sh` reads an update in from a USB stick**, without touching the collection
- **An idle reset after five minutes.** The kiosk has no reload button, no address bar and no
  keyboard — a stuck state would otherwise stand until the power is pulled
- **The map redraws only when the camera comes to rest.** On the Pi that is the difference between
  stuttering and not
- **`99-kiekmap-usb.rules` and `kiekmap-usb-mount`** mount sticks on Pi OS Lite, which has no
  automounter. `make prod-mac` runs the same container setup on a Mac

### Nothing place-specific in the code

- **Map extent, decades and street choice come from `tiles/region.json`**; map and place index are
  build artefacts. A second museum needs no fork — see [docs/adaption.md](docs/adaption.md)
- **The coat of arms is an exchangeable file**; the repository holds a placeholder, because an
  emblem of a municipality may not be passed to everybody who clones a repository
- **Three import settings**, all empty by default
- **The sample collection is invented.** 18 drawn pictures with made-up people; only street names
  and coordinates are real, and its gaps are deliberate

### Tooling and checks

- **`make check` before every commit:** style, the checks beside the tests, all tests. Plus a git
  hook for the fast ones and the same run on every pull request
- **The checks read files no test ever sees:** the language rule, the links inside `docs/`, the way
  of every setting into the container, the bookkeeping over the backlog numbers, the register of
  the history, and the version number in its five places
- **One version number in one place.** `make version v=0.8.0` writes it to all five
- **The backend dependencies are pinned** in `backend/requirements.lock`; the image installs from it
- **`make release` builds the update stick** and aborts on a dirty working tree or a missing tag

### Origin, licence, publication

- **Every commit and every tag is signed** (SSH), including those from before the key existed.
  Trees, subject lines and author dates stayed unchanged
- **Two branches:** `develop` for everyday work, `main` for the state running in the museum. Squash
  and rebase are off — the documentation cites commits by hash
- **Apache License 2.0**, Copyright 2026 Kalle Erlhoff. The museum's photo collection is explicitly
  not covered
- **The licence notices of the bundled packages travel along**, as a `THIRD-PARTY.txt` beside every
  artefact. The map names the ODbL alongside OpenStreetMap
- **Examples name nobody from the Holm collection**, but the invented cast from `seed/`
- **`CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`, `AUTHORS`** and report templates. Security
  reports go through GitHub's private reporting, so no address stands in the repository

### Documentation

- **Eight files, each with exactly one question**, opened up by [docs/index.md](docs/index.md)
- **Backlog items carry fixed numbers** under which they are cited; a number is never handed out
  twice
- **The history has a register** with one line per section and date, generated and checked
