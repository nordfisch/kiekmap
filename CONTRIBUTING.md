# Contributing

Kiekmap is a touchscreen kiosk for the local history museum in Holm: historic photos of the place
on a map, offline on a Raspberry Pi. It is built explicitly so that a **second museum can take it
over** — no fork, only its own `region.json` and `.env`.

## What to expect here, and what not

Said plainly up front, so that publishing does not become a silent promise:

**One maintainer, on the side.** There is no promised response time, no warranty, no support. A
report can sit for weeks. A contribution can be turned down because it does not fit the purpose of
the device — that is not a criticism of the work.

**What helps most**, in this order:

1. **A second museum that sets it up and reports back.** [adaption.md](docs/adaption.md) was
   written without a device; every stumbling block from a real setup is worth more than any
   feature.
2. **Bug reports from real operation** — from the Pi, from the touchscreen, from the museum.
   Everything under `deploy/pi/` is unverified to this day.
3. **Clearer documentation.** Whoever reads it for the first time sees the gaps the author no
   longer sees.
4. Code.

## Setup

```bash
make dev          # backend on 8000, frontend on 5173, both with hot reload
make seed         # build the invented sample collection
```

In full in [development.md](docs/development.md). The admin view needs a PIN:
`cd backend && .venv/bin/python -m app.cli pin` produces the line for the `.env`.

## The rules of this repository

They are complete in [CLAUDE.md](CLAUDE.md) and in [development.md](docs/development.md). The
important ones:

- **`make check` before every commit.** Style, checks, tests. The hook under `.githooks/` takes
  the fast ones off your hands: `git config core.hooksPath .githooks`.
- **Language by audience.** Every text exists once, in the language of its readers. German: the
  interface, the CLI, the documentation for museum and operation, issues, test files. English:
  identifiers, comments, developer documentation and commit messages. Umlauts are written out in
  German texts for people and transcribed in source code.
- **Every domain decision gets a test that describes the failure case.** The most valuable tests
  here cover mistakes that would happen *silently*.
- **Nothing place-specific in the code.** No coordinate, no place name, no number that depends on
  the collection — those go into `region.json` or into the settings. Test data is exempt.
- **No names from the real collection**, not even in a comment. The sample collection provides an
  invented cast; it is listed in [development.md](docs/development.md).
- **A finished item is recorded in three places**, not nine: the changelog, `history.md`,
  `backlog.md` — plus `decisions.md` if a decision came out of it.

## An idea or a bug

First check [backlog.md](docs/backlog.md) for an existing item, and [history.md](docs/history.md)
for whether the thing has been tried before. Then open an issue; the templates ask for what is
needed. **Issues are written in German** — the subject matter is a German museum.

**Backlog items carry fixed numbers** they are cited by ("Punkt 15"). Numbers are never reissued,
not even after an item is done. `tools/check_numbers.py` verifies that.

## The path of a contribution

1. **Fork**, then one branch per topic: `feature/short-name` or `fix/short-name`.
2. Work, get `make check` green. Conventional Commits (`feat:`, `fix:`, `docs:` …) — over 99
   percent of the commits here follow them. **New commit messages are English**; everything
   before 30 August 2026 is German and stays that way.
3. **Pull request against `develop`**, not against `main`. `main` is the state running in the
   museum and takes merges from `develop` only. More in [development.md](docs/development.md).
4. Merging uses a **merge commit**. Squash and rebase are disabled for this repository: the
   documentation cites individual commits by hash, a squash destroys them, and a rebase rewrites
   them and throws the signatures away.

## Licence of contributions

The project is under the [Apache License 2.0](LICENSE). Under its **§5** every contribution
submitted here is automatically under the same licence — there is no separate agreement (CLA), and
none is needed. Whoever changes a file marks it as changed (**§4.2**); the two SPDX lines at the
top of each source file carry that. More in [licensing.md](docs/licensing.md).

Add yourself to [AUTHORS](AUTHORS) if you like.
