# Passing it on

What may be passed on, and under which conditions. This file is read by whoever **publishes** the
project, whoever **takes it over** for another place, or whoever is asked what law the museum's
collection stands under.

> A technical stocktaking, not legal advice. Where German law comes up below, it is orientation;
> for a binding answer, ask somebody admitted to practise.

## Kiekmap itself

**Apache Licence 2.0**, Copyright 2026 Kalle Erlhoff. The text is in [../LICENSE](../../LICENSE), the
attribution in [../NOTICE](../../NOTICE). Both cover the code, the documentation and the invented
sample pictures under `seed/` — one licence for everything, with no questions of demarcation. Why
this one and not MIT: [decisions.md](../developer/decisions.md), point 62.

The licence text is **verbatim the one from apache.org** and is not touched. The placeholder
`Copyright [yyyy] [name of copyright owner]` in its appendix is the template for file headers, not
a field to fill in — the usual detection tools no longer recognise an altered text as Apache-2.0.

## The ways something goes out

The obligations do not hang on the project but on **what somebody gets into their hands**:

| Way | What is in it | What has to go with it |
|---|---|---|
| **The repository** | own code, docs, sample pictures | `LICENSE`, `NOTICE` — they lie at the root |
| **The container images** | plus 37 npm and 26 Python packages, fonts, icons | `THIRD-PARTY.txt` per image, the licence files under `basemaps/` |
| **The update stick** | plus the map file and the place index | the ODbL notice as well |
| **The screen in the museum** | the running map | "© OpenStreetMap contributors, ODbL" — at the bottom right |
| **The documentation site** | the files under `docs/`, and MkDocs Material with them | the footer names both licences; nothing else travels |

## The dependencies, all permissive

Measured on 20 August 2026 against the **installed** packages, not against the manifest files.

| | Packages | Licences |
|---|---|---|
| Python, whole venv | 39 | MIT, BSD-2, BSD-3, Apache-2.0, MIT-CMU (HPND), PSF-2.0 |
| Python, of those in the backend image | 26 | the same |
| npm, whole tree | 128 | 99 × MIT, 16 × ISC, 6 × BSD-3, 3 × Apache-2.0, 2 × BSD-2, 1 × "MIT OR Apache-2.0", 1 × CC-BY-4.0 |
| npm, of those in the frontend bundle | 37 | MIT, ISC, BSD-2/3, "MIT OR Apache-2.0" |

**No copyleft.** The only non-software licence is `caniuse-lite` (CC-BY-4.0) — a build-time
database from browserslist that lands in no artefact. Nothing restricts the choice of our own
licence, and nothing stands in the way of publishing.

**The names and their licence texts are in `THIRD-PARTY.txt`**, produced by
[../tools/build_notices.py](../../tools/build_notices.py) and checked in like a lock file. Why
produced and not maintained: a hand-written list is wrong within three months, and wrong in the
direction nobody checks. `make notices` writes it, `make check` notices when it has gone stale.

**For the backend the list has come from `backend/requirements.lock` since 25 August 2026**,
because the image installs from exactly that. Before, the tool walked the dependencies of
`pyproject.toml` itself, with a hand-written addition for what `uvicorn[standard]` pulls in — a
rebuilt resolver that would go stale in silence. **One package was missing already:** `greenlet`,
which SQLAlchemy brings along on Linux, stood in no notice file, because it does not get installed
on the development Mac at all. The environment markers of the lock file are now evaluated against
**both target platforms**, aarch64 and x86_64.

Three npm packages name their licence only in `package.json` and enclose no text
(`@protomaps/basemaps`, `pmtiles`, `murmurhash-js`). They get the standard text of their
identifier, **with a note that the text does not come from the package**. A package with no
statement at all aborts the run.

## The map: this is where the real obligations sit

| Part | Origin | Licence |
|---|---|---|
| `map.pmtiles` | `build.protomaps.com`, from OpenStreetMap | **ODbL 1.0** |
| `places.json` and the table `places` | Overpass API, from OpenStreetMap | **ODbL 1.0** |
| Fonts | Noto through `protomaps/basemaps-assets` | OFL 1.1 |
| Icons | tangrams/icons through the same archive | MIT |
| Map style | `@protomaps/basemaps` | BSD-3-Clause |

`tiles/build-tiles.sh` puts the licence texts beside the files they apply to — under
`frontend/public/basemaps/`.

**The table `places` is the place that gets overlooked.** It sits in `kiekmap.db` and therefore in
every backup. Without consequence for museum operation; whoever passes the database to a third
party passes ODbL material along and has to make it recognisable. The same sentence is in
[usermanual.md](usermanual.md).

## What the licence does **not** cover

**The photo collection.** A software licence licenses the program, not the data it processes: a
photo in the database does not become a derivative work of the program. That holds for the Apache
licence as for any other — the GPL would not draw data in either. The photos lie under `data/` and
are not in the repository.

The rights to them lie with the museum and with those who gave them, **per photo**, and the system
is built for that: `credit` is the picture credit that stands beside the picture, `provenance` the
internal note on origin and release. A collection of mixed rights is the normal case, not the
exception.

Whether the museum one day puts its own photos under a licence is a decision independent of this
one.

**The municipal coat of arms.** Free of copyright (§ 5 (1) UrhG), but restricted in its *use* as an
official emblem. That is why a drawn placeholder lies in the repository and not the coat of arms.
At length in [decisions.md](../developer/decisions.md), point 21, and in [adaption.md](adaption.md).

## Base images and the route of distribution

`python:3.12-slim` and `nginx:1.27-alpine` bring a Debian and an Alpine userland with them, and
**GPL-licensed binaries** in them. That does not touch the licence of our own code — it runs on
top, it is not linked with them. It does create obligations for whoever passes on a **finished
image**.

**Therefore: publish Dockerfiles, not built images.** Every operator then builds their own, and
the obligations stay where they belong. The route through `images.tar` in `deploy/pi/update.sh`
stays right for one's own device; it just does not belong in a release.

## How the project came about

One person built Kiekmap together with a language model; the commits carry it as `Co-Authored-By`.
It is recorded here because keeping quiet would be the worse way to handle it.

Little follows from that for the legal position, and nothing surprising: what is produced purely
by machine is no personal intellectual creation (§ 2 (2) UrhG) and is therefore not protected;
what is protected is the work of selecting, arranging and editing. That work lies open in this
repository — [decisions.md](../developer/decisions.md) holds the decisions with their reasons,
[archive/history.de.md](../developer/archive/history.de.md) the cases where the first proposal was thrown out.

In practice this means one thing: **do not overstate the claim.** The copyright line is right; a
sentence saying every line is our own work would not be. Where individual lines do not reach the
threshold of originality — which holds for standard code anyway, with or without a model — no
licence hangs on them. They are then freer than the rest, not invalid.

## Liability

Sections 7 and 8 of the licence exclude warranty and liability as far as that goes. No licence
goes further than the law allows: § 276 (3) BGB does not permit liability for intent to be waived,
and § 309 no. 7 BGB limits exclusions.

What keeps the risk small is therefore not the clause but the fact that it is **given away for
free** — whoever makes a gift is liable in essence only for intent and gross negligence. One rule
of conduct follows from that: **make no assurances.** Do not promise that the collection is safe,
that the backup works, that the device keeps running. What the program can do is in the changelog;
what is unverified is in the [issues](https://github.com/nordfisch/kiekmap/issues) and in
[index.md](index.md).
