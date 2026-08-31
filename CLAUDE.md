# Notes for coding agents

Kiekmap is a touchscreen kiosk for a local history museum in **Holm**, in the district of
Pinneberg: historic photos of the place on a map, filtered by a time-range slider, plus a
contribution panel — labelled „Hilf mit" on screen — where visitors fill in what is missing. The
device runs **offline** on a Raspberry Pi.

Read [docs/decisions.md](docs/decisions.md) first — it says *why* things are the way they are —
and [docs/architecture.md](docs/architecture.md), which says *what* the system is made of and how
the parts fit together. This file says *how* to work here. Which file answers which other question is
in [docs/index.md](docs/index.md).

## The three things you can get wrong here

Miss these three and you build something that only shows up in the museum:

1. **Historic photos are scans.** Their EXIF carries the date of the scan, not of the shot. An
   EXIF date from `exif_date_max_year` (1990) on must therefore **not** date a photo — it would sit
   on the timeline at 2019, count as dated, and never be offered for correction. See
   `backend/app/services/exif.py`.

   **That does not make an EXIF coordinate wrong, and it does not make it measured.** 413 photos
   of the initial collection carried one, and 278 of those shared it with another photo: values
   typed in, not measured. Before weighing a coordinate from a file against another source, count
   how often it repeats. See `docs/decisions.md`, point 34.

2. **Datings are intervals, not points in time.** „1920er" is the normal case. The time filter
   queries for **overlap** (`date_from <= to AND date_to >= from`), not for containment. With the
   obvious query most of the collection disappears from the view without a sound. See
   `backend/app/services/dates.py` and `tests/test_dates.py`.

3. **Offline means offline.** No CDN, no web font, no external API at runtime. The Protomaps map
   style points at `protomaps.github.io` by default, which is why the fonts and sprites live under
   `frontend/public/basemaps/`. The test: the page must make **zero** requests to a foreign origin.

## Language

**Every text exists exactly once, in the language of its readers.** The axis is the audience, not
the language.

| What | Language |
|---|---|
| Identifiers (variables, functions, classes, CSS classes, file names) | **English** |
| Code comments and docstrings | **English** |
| **Everything in a test file** — names, docstrings, comments | **German** |
| Interface texts | German, in `frontend/src/text/de.ts` |
| Messages that can appear in the visitor view or the admin view | German, straight in the code |
| Messages that only surface when working against the API | English |
| API paths, query parameters, JSON fields, OpenAPI descriptions | English |
| Output of the CLI (`python -m app.cli …`) | German |
| Docs for museum and operation: `usermanual`, `operations`, `adaption`, README, CHANGELOG | German |
| Docs for developers: `architecture`, `development`, `decisions`, `CONTRIBUTING`, this file | English |
| `docs/history.md` up to v0.8.0 | German, frozen |
| Title and body of a pull request | English |
| GitHub issues | German |
| Labels on issues and pull requests | English |
| Commit messages from 30 August 2026 on | **English** |
| Values in the database that come from OSM (`kind`: `strasse`, `flur` …) | German, as delivered |

The developer docs are being translated. A file still standing in German is a leftover of that
switch, not a counter-example.

**Rule of thumb for messages:** *Can it appear in the visitor view or the admin view? Then German,
otherwise English.* That settles every borderline case. The CLI is the exception — the museum team
runs it too when filling the device for the first time.

**Test files are German throughout**, name and docstring and comment. A test name is not an
identifier but a sentence of specification: `test_scandatum_datiert_das_foto_nicht` says at once
which promise the test protects. Class names likewise (`class TestUeberlappung`).

**Umlauts:** written out in texts for people (Mühlenweg); transcribed (`ue`, `oe`, `ae`, `ss`) in
German prose **inside source code** and in shell scripts. A writing habit for German messages in
code follows from that: **phrase them so they need no umlaut**.
Not „Sie koennen den Stick abziehen" but „Der Stick kann abgezogen werden".
For commit messages the rule is moot since the switch to English.

**Quotations and data values keep their umlauts** — `"Mühlenweg"` as an example in an English
comment, `["Gebäude"]` as a setting value, `"März"` in `services/dates.py`. That is not prose but
the subject the text talks about; without the umlaut it would simply be wrong. `ß` may become
`ss`, the three umlauts may not.

**`tiles/` counts**, and so does `tools/`. Both run on the development machine only, but they are
ordinary source code of this repository.

Why the rule reads this way and where its borderline cases lie is spelled out in
[docs/development.md](docs/development.md). Whether a file obeys it is answered by
`python3 tools/language_check.py` — it checks both sides.

## Writing rules

For all documentation, German and English alike. These are style rules, not language rules.

**As simple as possible, as complex as necessary. Plain and factual, no promotional or narrative
tone.**

1. One thought per sentence. No nesting beyond a single subordinate clause.
2. Active over passive, wherever it shortens the sentence or makes it clearer.
3. No teasers, no rhetorical questions, no opening filler.
4. No filler words and no hedging ("actually", "basically", "in a sense") without a reason of
   substance.
5. No redundancy: do not restate the same content in other words.
6. Order by relevance and logical sequence, not by the order it was written in.
7. The deletion test: every sentence must serve a factual purpose. If it can go without losing
   information, it goes.
8. No metaphors, no imagery, no exaggeration.

**Two exceptions:** [docs/history.md](docs/history.md) is closed and keeps its tone. Test names
stay long where precision demands it.

No tool checks these rules. They work while writing and in review.

## Layout

The directory tree is in [docs/architecture.md](docs/architecture.md); only what you cannot see
from it is here:

- **`backend/app/services/` is the place for domain logic without HTTP context** — that is where
  the thinking belongs. `app/api/` validates parameters, calls a service, returns a schema, and
  stays thin.
- **`frontend/src/api/` mirrors `app/schemas.py`.** Change a field there and you change it here.
- **`tiles/` runs on the development machine, never on the Pi.** Map and place index are build
  artifacts and are not in the repository.
- **`data/` is runtime data** and is never versioned; `seed/` is the invented sample collection for
  development and tests.

## Commands

```bash
make dev          # backend (8000) and frontend (5173) with hot reload
make check        # everything before a commit: style, checks, tests
make test         # tests only -- pytest and vitest
make lint         # ruff check and format --check
make docs-check   # only the checks, without the tests
make tiles        # offline map, fonts, sprites for the region
make places       # build and read in the place index
make seed         # build the sample collection from seed/ (deletes the current one!)
make seed-save    # save the running collection to seed/
make empty        # delete the whole collection (asks first; before an initial import)
make prod         # everything in containers, as on the Pi
```

`make` without a target lists them all. Backend tests on their own:
`cd backend && .venv/bin/pytest -q`.

## How to work here

**Tests.** Every domain decision gets a test that describes the *failure* case, not only the happy
path. The most valuable tests here are called `test_jahrzehnt_erscheint_bei_auswahl_mittendrin` and
`test_scandatum_datiert_das_foto_nicht` — both cover mistakes that would happen silently. **Run
`make check` before every commit.**

**These checks run beside the tests**, because they read files no test ever sees:
`tools/language_check.py` (the language rule), `tools/check_anchors.py` (links inside `docs/`),
`tools/check_settings.py` (does every setting reach the container?), `tools/check_numbers.py` (does
the backlog's bookkeeping about its own numbers add up?), `tools/build_register.py --check` (is the
register of the history complete?) and `tools/set_version.py --check` (do all five places name the
same version?). All of them run with `python3` and no venv; `make check` and the hook under
`.githooks/` execute them. More in [docs/development.md](docs/development.md).

**Work happens on `develop`**, never on `main` — that branch holds the state running in the museum
and takes merges only. A topic of its own gets a `feature/` or `fix/` branch. **Never squash:** the
documentation cites individual commits by hash. More in
[docs/development.md](docs/development.md).

**Comments** explain the *why*, not the *what*. A comment that only repeats what the code says gets
deleted. A comment that names a pitfall is gold, and there are a few here (the `rshared` mount, the
sprite URL that has to be absolute, `+` meaning addition in SQLite).

**A finished item is recorded in two places, not nine:** what the program can do now goes into the
[changelog](CHANGELOG.md), and the issue gets closed. If a decision came out of it, that becomes a
new point in [docs/decisions.md](docs/decisions.md), with a short reason. How the work went is in
the commit and the closed issue, and nowhere else — `docs/history.md` is closed and takes nothing
more.

**Keep the audience in mind.** Visitors stand at a touchscreen, often elderly. Controls at least
48 px. The admin view is used once or twice a year by volunteers — plain wording matters more than
compactness there.

## Nothing place-specific belongs in the code

The map extent comes from `tiles/region.json` at runtime; the map file and the place index are
build artifacts. That is why a second museum needs **no fork**, only its own `region.json` and
`.env`.

This property is easy to destroy and hard to win back. If you find yourself writing a coordinate, a
place name or a number that depends on the collection into the code, it belongs in `region.json` or
in the settings instead. Test data is exempt — coordinates from Holm are wanted there, because they
make the case concrete.

**Names from the collection are the exception to that exception: examples are invented.**
Coordinates, streets and house numbers yes — family, farm and company names no, not in a test, not
in a comment, not in the documentation. The sample collection provides a cast for that, and it is
enough: **Gasthof Petersen**, **Hof Sieveking**, **Familie Wendt**, **Familie Boysen**,
**A. Brahms**, plus **Timm**, **Möller**, **Harms** and **Ohlsen**. An invented name shows whatever
the example is meant to show — that a year beside a name is the archive's date and not the date of
the shot does not depend on the name. The collection lives in `data/` and never goes into the
repository; neither do its people.

How to adapt the project is in [docs/adaption.md](docs/adaption.md), including what a second
language would cost and when splitting things up starts to pay off.

## What not to touch

- **`data/`** — runtime data. Never in the repository, never accessed from a test (tests get a
  temporary directory through the `settings` fixture).
- **The file names of the photos** are the SHA-256 of their content. Duplicate detection, cache
  headers and the incremental backup all hang on that.
- **`frontend/public/tiles/`** and **`frontend/public/basemaps/`** — produced by `make tiles`.
- **The quality setting in `tools/to_jpeg.py`** — it is measured against the initial collection,
  not chosen. Two runs over the same file must produce the same SHA-256; adjust it and every
  existing image comes in a second time with the next archive delivery.
- **The gaps in the sample collection** (`seed/`) — photos without a year, without a place, two
  accurate only to the street, one withdrawn visitor contribution. They are deliberate: without
  them the contribution panel has nothing to offer and a third of the program is never exercised.
  `tools/build_seed.py` counts them after every run and **aborts if one is missing** — whoever
  builds a new question gives it its supply there.

## State of things

What is built is in the [changelog](CHANGELOG.md); how it came about and what turned out differently
from the plan is in [docs/history.md](docs/history.md); what is open is in
the [issues](https://github.com/nordfisch/kiekmap/issues). Only what you would **assume wrongly**
while working is here.

**Stages 0 to 10 are built** — backend, map, time slider, contribution panel, admin view, backup,
kiosk operation. The initial collection is imported, cleaned and reviewed. **All of that has run
locally only**, as a development server and in containers on a Mac; nothing stands in the museum
yet.

**But everything under `deploy/pi/` is unverified.** It was built without a device; the syntax is
right, nothing has run. The first Pi is also the acceptance test. Unverified for the same reason
are the **USB path of the backup** and the behaviour after **restart and power cut** — neither can
be checked on a Mac. The containers, by contrast, are verified, if only there.

**To develop on a Mac**, set `KIEKMAP_MEDIA_DIR=/Volumes` and create a test volume with `hdiutil` —
see [docs/operations.md](docs/operations.md). Container operation runs there with `make prod-mac`.

**The admin view needs a PIN:** `cd backend && .venv/bin/python -m app.cli pin` produces the line
for the `.env`. Without it the login says so in plain words instead of rejecting every attempt.

**Open work lives in the [issues](https://github.com/nordfisch/kiekmap/issues), not in a file.** The documentation cites older items as
„Punkt N" — a numbering that ran to 66 and was never reissued. Those numbers are not issue numbers
and cannot become them, because GitHub shares one counter with the pull requests. The number
register in [docs/history.md](docs/history.md#nummernregister) resolves them, and
[docs/decisions.md](docs/decisions.md) point 69 says why.

**What is no longer a backlog item but curation:** photos without a description, without a title,
without a place. Those are written by whoever looks at the picture and knows the place — no program
does it.
