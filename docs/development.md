# Development

For people who work on Kiekmap. Why things are the way they are is in
[decisions.md](decisions.md); what the system is made of is in
[architecture.md](architecture.md); how it came about is in [history.de.md](history.de.md); what is
still open is in the [issues](https://github.com/nordfisch/kiekmap/issues); how to work on it is here.

## Setup

Requirements: Python 3.12+, Node 18+ (22 recommended), Git. Optionally Docker for the reality
check, and `pmtiles` (via Homebrew) for building the map.

```bash
git clone <repo> && cd kiekmap
make dev
```

On its first run `make dev` creates the Python environment, installs the Node packages and starts
both. Backend on **8000** (docs under `/api/docs`), frontend on **5173**. Vite proxies `/api`, so
the same relative paths apply in development and in production.

**The map is still missing.** Without it the frontend shows „Die Region konnte nicht geladen
werden":

```bash
make tiles     # tiles, fonts and sprites for the region from tiles/region.json
make places    # place index for the place search (queries Overpass once)
```

`make tiles` downloads about 19 MB and takes a minute. Both need the internet and run on the
development machine — only the result goes to the Pi.

Test data:

```bash
cd backend && .venv/bin/python -m app.cli import tests/fixtures
```

## Development environment

**PyCharm Professional** covers everything in one window. The alternative is **PyCharm Community**
for the backend plus **WebStorm** for the frontend — WebStorm is free for non-commercial use, and
there is no "Community" edition of it. What the Community variant lacks, and how to replace it:

| missing | replacement |
|---|---|
| database tool | DB Browser for SQLite, or `sqlite3 data/kiekmap.db` |
| HTTP client | `/api/docs` — interactive and always current, because it is generated from the code |
| Docker | `make prod` |

Settings: interpreter on `backend/.venv/bin/python`, mark `backend` as sources root.

## Language

**The repository speaks English. German is a translation, and it is marked as one.**

The boundary used to run through the repository, file by file, by audience. It now runs between
the repository and what is published from it. Everything a contributor touches is English;
everything a museum needs to run the device exists in German as well, under a `.de.md` name and
watched for drift.

| What | Language |
|---|---|
| Identifiers, code comments, docstrings | English |
| Test files — name, docstring, comment | English |
| [architecture.md](architecture.md), this file, [decisions.md](decisions.md), [CONTRIBUTING](../CONTRIBUTING.md), [CLAUDE.md](../CLAUDE.md) | English |
| [README](../README.md), [CHANGELOG](../CHANGELOG.md), `SECURITY`, `CODE_OF_CONDUCT`, `AUTHORS`, `NOTICE` | English |
| GitHub issues, issue and pull request templates | English |
| `Makefile`, `deploy/`, GitHub workflows — comments | English |
| CLI — commands, switches and output | English |
| Commit messages from 30 August 2026 on | English |
| Title and body of a pull request | English |
| Interface, messages in the visitor view and the admin view | **both**, by `KIEKMAP_LANGUAGE` |
| `*.de.md` | German, kept as a translation |
| [history.de.md](history.de.md) up to v0.8.0 | German, frozen |
| Values from OSM (`kind`: `strasse`, `flur` …) | German, as delivered |

**The file name carries the rule.** `operations.de.md` is German, `operations.md` is English.
Until 31 August 2026 this was two hand-kept lists in `language_check.py`, and a new file belonged
to whichever one somebody remembered to add it to. A suffix cannot be forgotten.

**Why the code is English:** `def zeitraum(...) -> DatePrecision` creates a break at every boundary
between our own code and a library. Coding agents and later contributors stumble over mixed code
measurably more often.

**Why German survives anyway:** the museum team, the operator and a second museum read German, and
their documents are the ones that matter in practice — the handbook printed beside the device, the
Pi setup, the guide to adopting the project elsewhere. Those exist in both languages and are
delivered bilingually; see [point 71](decisions.md).

**German examples inside English texts are wanted** wherever they explain the case. They are the
subject the text talks about, not the prose.

**Messages that reach a screen come from a catalogue**, not from the code around them:
`frontend/src/text/` in the frontend, `backend/app/text/` in the backend, both selected by
`KIEKMAP_LANGUAGE`. Messages that only ever surface when calling the API directly stay English in
place — `bbox is inverted: min must be smaller than max` has no other reader.

Umlauts are transcribed (`ue`, `oe`, `ae`, `ss`) in German prose inside source code and in shell
scripts, and written out in texts for people. **Quotations and data values keep them**:
`"Mühlenweg"` as an example in a comment, `["Gebäude"]` as a setting value, `"März"` in the month
list — without the umlaut they would simply be wrong. For commit messages the rule is moot since
the switch to English.

`python3 tools/language_check.py` checks both sides: transcribed umlauts in German documentation,
German paragraphs in English documentation. Its `IN_TRANSITION` tuple lists what has not made the
switch yet — a file that is half of each is checked in neither language, and that list has to
reach empty. It is the progress bar of [issue #31](https://github.com/nordfisch/kiekmap/issues/31).

**The table above is the target, and one row of it is not true yet.** The test files are still
German, and the checker still requires that of them; both flip in the same commit that translates
them. Until then a German test name is correct, not a leftover.

## Glossary

The subject is a German village museum, and the words for it were German first. **One German term
gets exactly one English word here**, so that the same thing is not called three things in three
files. Where the translation is not obvious, the reason is beside it.

| German | English | Note |
|---|---|---|
| Bestand | **collection** | the whole set of photos, not one folder of it |
| Eingangsordner | **inbox** | the directory is `data/incoming/` |
| Dublette | **duplicate** | same SHA-256, therefore the same image |
| Scandatum | **scan date** | the date the paper was scanned, not the date of the shot |
| Datierung | **dating** | what a photo says about when it was taken |
| Spanne, Zeitraum | **range** | `date_from`/`date_to`; a dating is a range, never a point |
| Überlappung | **overlap** | the filter asks for overlap, not for containment |
| Genauigkeit | **precision** | `DatePrecision`: day, month, year, decade |
| Jahrzehnt | **decade** | |
| Zeitschieber | **time slider** | |
| Stapel | **stack** | photos sharing one spot on the map |
| Beitrag | **contribution** | what a visitor adds; the panel is the *contribution panel* |
| Sicherung | **backup** | |
| Wappen | **coat of arms** | the way into the admin view |
| Vorlegen | **to offer** | the panel offers a photo that is missing something |
| Abweisen | **to reject** | `ImportResult.REJECTED` |

**Place kinds keep their German keys**, because that is how `tiles/build-places.py` writes them into
the database and how OSM delivers them. Only the display is translated:

| Key | English |
|---|---|
| `strasse` | Street |
| `ortsteil` | District |
| `gebaeude` | Building |
| `natur` | Nature |
| `flur` | Field name |
| `adresse` | Address |

`Flur` is the one with no ready equivalent: a named stretch of open land, older than the streets
around it. **Field name** carries it; *locality* would be vaguer and *parcel* would be a land
registry term this project does not mean.

## Writing rules

How a text is written here — German and English alike — is in
[CLAUDE.md](../CLAUDE.md#writing-rules). Eight rules in one place, because they apply while
writing and not while looking things up.

## Examples are invented

**Coordinates, streets and house numbers** from Holm belong in test data and comments — they make
the case concrete. **Names** from Holm do not: no families, no farms, no companies, not in a test,
not in a comment, not in the documentation.

The sample collection provides the cast, and it is enough for everything: **Gasthof Petersen**,
**Hof Sieveking**, **Ladengeschäft Rohlf**, **Familie Wendt**, **Familie Boysen**, **A. Brahms**,
plus **Timm**, **Möller**, **Harms** and **Ohlsen**. Whoever needs another one invents it and adds
it here.

**The reason is not caution but that it costs nothing.** An invented name shows whatever the
example is meant to show: that a year beside a name is the archive's date and not the date of the
shot does not depend on who the person was. On 21 August 2026, 87 occurrences in 15 files were
replaced this way, and not one example lost its edge. The occasion is in
[history.de.md](history.de.md#punkt-64-abschnitt-1-die-namen-aus-dem-repo), point 64, section 1.

**Some slipped through** and were caught up afterwards: a surname as an example of a misread
archive entry, a house name in a comment, a photo title that is a person's name, and — found on
31 August 2026 while translating the tests — a photographer's name in a docstring and in three test
values. Each stood in an example that an invented name carries just as well. **What loses them:**
a search for names the database knows as names. They stand in prose and in literals, not in a name
field. The counter-check before a release therefore matches the patterns names take in the
collection — *Familie X*, *Hof X*, *A. Surname*, north German endings — across prose and test
values, not only the fields. **No number is given here on purpose:** it was wrong within a week,
and a count that has to be maintained is a promise that quietly expires.

**They are still in the git history**, and that is decided, not overlooked: a further
rewrite would have moved every hash again, demanded another pass over the cited
identifiers and cost the `v0.8.0` tag — for names in example sentences of old commits that nobody
sees who reads today's files. **The promise is therefore exactly this:** the current state names
nobody from the collection; the git history and `history.de.md` still do.

## Testing

```bash
make check         # everything: style, checks, tests -- the target before a commit
make test          # tests only
make test-backend  # pytest
make test-frontend # typecheck and vitest
make lint          # ruff
make docs-check    # only the checks below
```

**These checks run beside the tests, because they read files no test ever sees:**

```bash
python3 tools/language_check.py   # does the source obey the language rule?
python3 tools/check_anchors.py    # do the links in docs/ still point somewhere?
                                  #   (across files too, since 15 August 2026)
python3 tools/check_settings.py   # does every setting reach the container?
python3 tools/check_numbers.py    # does the backlog's bookkeeping about its numbers add up?
python3 tools/build_register.py --check   # is the register of the history still complete?
python3 tools/set_version.py --check      # do all five places name the same version?
```

They need neither `venv` nor `node_modules` — pure readers, the system `python3` is enough.
**`tools/build_notices.py` is explicitly not one of them:** it reads the metadata of the installed
packages and evaluates their environment markers with `packaging`, so it runs with the venv's
Python. `make notices` and `make check` know that.

**And they hang in the git hook**, because "by hand" meant "not at all" in practice.
`.githooks/pre-commit` runs exactly these, **not** the test suite: that one runs anyway, these
were the ones being forgotten, and together they take under a second. Enable it once per clone;
`--no-verify` bypasses it:

```bash
git config core.hooksPath .githooks
```

**`check_settings.py` exists since 14 August 2026, and it has an occasion.** The compose file
passed only four of eight settings through; the rest silently fell back to their defaults in the
container. An import lost the tag, the credit and the provenance that way — **with no error
message, and 393 green tests beside it**, because no test ever touches a compose file. It also
checks the other direction: a name in `docker-compose.yml` or `deploy/.env.example` that does not
exist in `config.py` has no effect and would otherwise never be noticed.

**`check_numbers.py` joined on 19 August 2026** and has one too. An item moving into the history
demands four edits in three places — remove the table row, remove the section, add the number to
the retired list, raise the count in front of it. That happened four times in one day. It verifies
the one promise the numbering still makes: the points of `decisions.md` ascend and no number
occurs twice. **What it deliberately does not do is count numbers in running text**; why that would
be wrong is in [decisions.md](decisions.md), point 59.

**`build_register.py` joined on 21 August 2026**, together with the register at the top of
[history.de.md](history.de.md). It is really a generator — `make register` writes the table, `--check`
only says that it no longer matches. Both need the same promise: **every section of the history
states its date in the first lines below its heading.** Whoever forgets learns about it at commit
time, not half a year later at a table with holes.

**What gets tested.** Not coverage for the number's sake, but the places where a mistake happens
*silently*. The most important test classes in the project:

- `test_dates.py::TestUeberlappung` — a photo dated „1920er" has to appear for the selection
  1925–1930. A naive date query drops it without a sound.
- `test_importer.py::TestDatumAusExif` — the EXIF date of a scan must not date the photo.
- `test_foldermeta.py` — what the folder name says, and where it must not be guessed. „10 H
  Brahms" must not become house number 10h, the folder „2" must not become the street „Kolonie
  Autal 2", and a street without a house number must not be placed at its midpoint.
- `test_watcher.py` — a half-copied file must not be imported.

All of them describe mistakes that would have shown up in the museum, not in development — and
three of them actually happened during the real initial import, before they became tests.

**In the frontend it follows that no component has a test** — and that is not a backlog item but
the rule: *every decision moves into a pure function and gets its test there; rendering gets none.*
Where the function lives does not matter; `PhotoLayer.test.ts` checks `buildIndex` from a `.tsx`
file without rendering anything.

The reason is the same as above. A wrongly drawn button looks wrong, and that takes a glance, not
a test. A wrongly rounded year looks like nothing — the map simply shows something else. While
building, that means: as soon as a component calculates, sorts or decides, that part belongs in a
module next to it. No jsdom, no Testing Library; why, is in [decisions.md](decisions.md),
point 60.

**The offline test is the most important check in the project** and cannot be automated:
disconnect the network, move the map, open photos, submit a contribution — and then look in the
DevTools to confirm that no request went to a foreign origin.

```js
performance.getEntriesByType('resource')
  .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length  // 0
```

**Fixtures.** `make_photo` creates database rows without files (fast, for query tests),
`sample_image` copies a real test image (for the import pipeline). The test images in
`backend/tests/fixtures/` deliberately cover the hard cases: a scan without EXIF, a scan with a
2019 scan date, a portrait image via EXIF orientation, a CMYK TIFF, a file without an image.
Rebuild them with `python tests/fixtures/build_test_images.py`.

Every test gets its own temporary data directory through the `settings` fixture. Never touch
`data/` from a test.

## Database

SQLite with a WAL journal. Schema changes go through Alembic:

```bash
make revision m="description"   # generate a migration from the models
make migrate                    # apply it
```

Migrations run automatically when the container starts (`backend/docker-entrypoint.sh`) — nobody
on the Pi should have to think about it. Always read the generated migration: SQLite cannot alter
columns, so Alembic rebuilds the table (`render_as_batch`), and details get lost in the process if
you do not look.

> **The history starts at an initial schema, and it stays that way.** On 3 August 2026 the three
> existing revisions were squashed into one, because no device was in the field yet. **From the
> first Pi on this is no longer allowed** — the chain of migrations is then the only way a museum's
> data survives a schema change. See [decisions.md](decisions.md), point 17.

What can go wrong when a table is rebuilt has gone wrong once and cost every visitor contribution:
`app/db.py` turns `PRAGMA foreign_keys=ON` on for *every* engine in the process, including
Alembic's, and the rebuild drops the original. `alembic/env.py` therefore turns the check off for
the duration of a migration. `tests/test_migrations.py` guards this — anyone changing something
there should run the counter-check: with `foreign_keys=ON` the test has to be red.

## Sample collection

```bash
make seed        # build the collection from seed/ -- deletes the current one!
make seed-save   # save the running collection to seed/
make empty       # delete everything with no replacement -- the step before an initial import
```

Sixteen photos, deliberately full of gaps: photos without a year, without a place, staggered text
lengths, deleted photos, visitor contributions including a withdrawn one. Without those gaps the
collection exercises half the program — the contribution panel would have nothing to offer.

**Everything in this collection is invented** — drawn images, made-up people, produced by
[../tools/build_seed.py](../tools/build_seed.py). Only street names and coordinates are real, and
they have to be: without them the map shows nothing and the place search finds nothing. The real
photographs belong to the museum and are not in the repository. The rest is in
[../seed/README.md](../seed/README.md).

## Taking in an archive delivery

When the museum sends a new delivery, two steps come before the import — and both have been
skipped once, with consequences.

**First: everything becomes JPEG.**

```bash
python3 tools/to_jpeg.py "~/Museum/Neuer Stand" "~/Museum/Neuer Stand zwecks Import/Straßen"
```

The tree is copied and the source is left untouched. TIFF, PNG and WEBP are converted, JPEG is
passed through. **The setting inside is measured and is not readjusted** — why, is in
[decisions.md](decisions.md), point 46. The target folder is called `Straßen` so that the
provenance takes the same shape as for the initial collection (`KIEKMAP_IMPORT_PROVENANCE` puts
the prefix in front of it).

**Second: count what is really new.** Even a delivery described as a delta contains images that
are long since in the collection — the comparison ran over bytes, and those change as soon as
somebody rewrites the metadata. On 16 August 2026 that was **223 of 619 files**.
[decisions.md](decisions.md), point 47, describes the way: exact pixel comparison first where the
edge lengths match, then a coarse pass over downscaled greyscale images.

Only then `python -m app.cli import <folder>`. Take a copy of `data/` first, **including the
`-wal` and `-shm` files** — without them the copy is at the state of the last checkpoint.

## Layout

```
backend/app/
  api/        endpoints. Thin: validate parameters, call a service, return a schema.
  services/   domain logic without HTTP context. The thinking belongs here, and it tests easily.
  models.py   SQLAlchemy tables
  schemas.py  Pydantic shapes of the API
  config.py   every path hangs off data_dir
frontend/src/
  kiosk/      visitor view
  admin/      admin view
  store/      Zustand stores, one per area
  api/        backend access; the types mirror backend/app/schemas.py
  text/       interface texts
seed/         sample collection: image files and seed.json
```

**Rule of thumb:** if something can be tested without HTTP, it belongs in `services/`.

That is the directory list. How the parts play together — which data flows where and when, what is
produced at build time and what at runtime — is in [architecture.md](architecture.md).

## Checking against the running system

Experience from the last rebuilds, so that it does not have to be gathered twice:

- **The admin PIN is 4711 locally**, and a click on the coat of arms (`.admin-gate`) leads into
  the admin view. `python -m app.cli pin` produces a PIN of your own.
- **A click on the map sets a pin while the place question is running.** Use the controls or the
  scroll wheel to zoom — otherwise you create a visitor contribution by accident while testing,
  and somebody has to take it back in the moderation view later.
- For import testing, create a test stick instead of hunting for a real one:
  ```bash
  hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK teststick.dmg && hdiutil attach teststick.dmg
  ```
  Together with `KIEKMAP_MEDIA_DIR=/Volumes` in `backend/.env` — it is already there.

For anyone driving the view through a browser (coding agents do):

- Start the services through the preview tools (`backend`, `frontend` from `.claude/launch.json`),
  not through the shell.
- The screenshot compositor often paints at a reduced size after a navigation. Setting the window
  size forces a clean rebuild.
- State is lost between two calls to the JavaScript console. Play a sequence through **in one**
  call — log in, click, measure.

## What goes wrong easily

Pitfalls that have cost time and are commented in the code:

- **The sprite URL has to be absolute** — MapLibre rejects relative paths, but not for glyphs.
- **SQLite: `+` is addition, not concatenation.** `substr(x,1,3) + '0'` gives 193, not „1930".
- **SQLAlchemy: `/` is true division.** `1932/10` is 193.2; without a cast it becomes 1932 again.
- **Pointer events arrive faster than React renders.** The dragged slider handle therefore lives
  in a ref, not only in state — otherwise it sticks during a brisk swipe.
- **Docker bind mounts do not show volumes mounted later** without `rshared` propagation. This
  affects the USB backup in stage 9.
- **Overpass rejects the default user agent of `urllib`** (HTTP 406).

## For another place

Nothing place-specific is in the code — the map extent comes from `tiles/region.json` at runtime,
and the map file and place index are build artifacts. A second museum therefore needs no fork,
only its own `region.json` and `.env`.

This property is easy to destroy: if you want to write a coordinate, a place name or a number that
depends on the collection into the code, it belongs in the configuration instead. Test data is
exempt.

The full procedure — compute the bounding box, choose the zoom levels, build tiles and place
index, verify — is in [adaption.md](adaption.md). That file also covers what a second language
would cost and when splitting things up starts to pay off.

## The dependencies are pinned

`backend/pyproject.toml` names lower bounds only (`fastapi>=0.115`); the image installs from
`backend/requirements.lock` instead. Without it a rebuild in a year would pull different versions
than today's — and on a device that stands offline and is touched once a year, that only shows up
in the museum.

```bash
make lock        # resolve the lock file again (after a change to pyproject.toml)
make deps-lock   # bring your own venv to that state
```

**The two belong together, and `make check` enforces it.** `tools/build_notices.py` reads the
names and versions from the lock file — it *is* the list of what goes into the image — but the
licence texts from the venv, because only an installed package has its `LICENSE` on disk. If the
two diverge, the run aborts. A notice file naming a version that is not in the image is worse than
none.

**`make deps-lock` strips the environment markers while doing so.** `greenlet` comes into the
image through SQLAlchemy but never onto a Mac — without the locally installed licence file the
notice could not be written. The other way round, `colorama` is installed but appears in no notice
file: its marker applies to Windows only, and the image is Linux.

## The checks run without you too

`.github/workflows/check.yml` runs `make check` on every pull request and on every push to `main`
or `develop`. On feature branches the pull request covers it; nothing has to run twice.

**Why, given that the commit hook exists:** the hook takes the fast checks off your hands — but
only for whoever switched it on (`git config core.hooksPath .githooks`, once per clone). And a
green `make check` on your own machine only says it was green *there*. On the pull request it says
so for everyone.

The order of steps in the workflow has a reason: `make venv` installs from `pyproject.toml`, so
without fixed versions; `make deps-lock` then pulls the lock file's versions over it. Without the
second step `tools/build_notices.py` aborts — **and that is exactly right**, because the licence
notices would then not be those of the image.

## Building a release

```bash
make version v=0.9.0                 # set the number
git commit -am "chore: version 0.9.0"
git tag -s v0.9.0 -m v0.9.0          # signed, tag.gpgsign is set
make release to=/Volumes/STICK/kiekmap-update
```

`tools/build_release.py` builds both images, saves them as `images.tar`, writes the `version`
file next to them and on request (`map=1`) takes the map file and place index along — exactly
the folder `deploy/pi/update.sh` expects.

**It aborts on a dirty working tree or a missing tag**, and there is no `--force` against that: a
stick that belongs to no commit cannot be identified a year later — and a year is exactly the
interval at which such a device is touched.

**The `version` file is the line that gets forgotten by hand.** Without it `KIEKMAP_VERSION` stays
as it is in the Pi's `.env`, the next start pulls the old image back up, and the device runs the
old software without saying so anywhere.

## Branches and merges

Two long-lived branches, and `main` means something specific:

| Branch | Meaning | Who writes into it |
|---|---|---|
| `main` | **What runs in the museum.** Every commit on it carries a tag. | merges from `develop` only |
| `develop` | Everyday work. The default branch. | merges from `feature/*` and `fix/*` |
| `feature/<short>`, `fix/<short>` | short-lived, one topic | by pull request into `develop`, deleted afterwards |

**This is not GitHub Flow**, even though it looks like it. GitHub Flow has exactly one long-lived
branch and is built for services that ship several times a day. This device stands offline and is
updated once or twice a year from a stick; there, a `main` of its own answers a question that
really gets asked in the museum: *what is actually running on the device?* The reasoning is in
[decisions.md](decisions.md).

**No `release/*`, no `hotfix/*`.** With one maintainer that is ballast. An urgent bug becomes a
`fix/` branch, goes into `develop` and from there straight into `main` — the same road, driven
faster.

### Squash merge is disabled here, and there is a reason

`history.de.md` cites **individual commits by hash** — over eighty occurrences. A squash merge
collapses the commits of a branch and destroys exactly the ones the documentation points at. That
is not a matter of style but data loss in a file whose value hangs on those references.

**Merging happens in both directions with a merge commit**, not by rebase. A rebase creates the
commits anew — GitHub builds them on the server, where no key is kept, and they come out
**unsigned**. The first pull request demonstrated it. A merge leaves its parents untouched:
signatures stay, hashes stay, every commit stays visible on its own.

The forks in the graph are the price; `git log --first-parent` hides them.

### Commit messages are English

Since 30 August 2026. The 211 commits before that are German and stay that way: a rewrite would
move every hash the documentation cites, and this project did that twice in August — both times
the follow-up work was half the job.

The Conventional Commits prefixes apply unchanged (`feat:`, `fix:`, `docs:` …). Transcribing
umlauts no longer applies to new messages.

## Releasing

SemVer tags, Conventional Commits, one repository for frontend and backend. Frontend and backend
are versioned together — for a single-device system separate versioning is only ballast, and API
compatibility is guaranteed by it.

### One number, five places

```bash
make version            # show it
make version v=0.8.0    # set it everywhere
```

`tools/set_version.py` writes it to `frontend/package.json`, twice to
`frontend/package-lock.json` (the root package), to `backend/pyproject.toml` and to
`backend/app/__init__.py`. `make check` reports when one of them steps out of line.

**The fourth is the most important and would have been the one left behind:** `__version__` is what
`/api/health` answers and what stands in the OpenAPI description — the version the device in the
museum claims about itself. If it stood still while the image tag counted on, the API would give
the wrong answer to the one question it exists for.

**The tag is not the source, the files are.** A check against `git describe` would be red exactly
in the window where the version is already raised but the tag is not yet set — and that is where
the commit hook runs. The tag has to match instead.

**All commits are signed** (SSH, not GPG), and so are the tags — including the 185 from before the
key existed, done retroactively on 25 August 2026. That is unusual, so the trade-off belongs in
writing.

**The obvious objection does not hold:** an SSH signature has **no timestamp of its own**; the
commit carries only the key, the namespace `git`, the hash algorithm and the signature. Signing
retroactively therefore asserts nothing demonstrably false.

**One price remains, and it has to be known:** `allowed_signers` supports `valid-after=`, and Git
verifies a signature against the moment of *its creation* — that is, against the commit date.
Whoever ever gives this key a validity window starting 25 August 2026 gets every commit before
that reported as invalid. Whoever changes the key therefore keeps the old one listed **without**
`valid-after`.

**It was done with** `git rebase --root --exec` — `filter-repo` does not sign. The run reset the
committer date from the author date, otherwise all 188 commits would have got 25 August as their
committer date. One commit previously had ten seconds between the two dates; those were lost.

The museum device is offline. The update path to it (an image tarball on a USB stick) is in
[operations.md](operations.md).
