# The sample collection

A small photo collection for developing and trying things out. It replaces what everybody used to
click together by hand in `data/` — and what nobody else had.

```bash
make seed        # build the collection from this folder (deletes the current one!)
make seed-save   # save the running collection here
```

## Everything here is invented

> **The pictures are drawn, the people made up.** Familie Wendt, Gasthof Petersen, Ladengeschäft
> Rohlf, "Foto: A. Brahms" — none of them existed. The same goes for the credits, the provenance
> notes and the visitor contributions.

**Only the street names and the coordinates are real**, and they have to be: the points have to lie
inside the `bbox` from `tiles/region.json`, or the map shows nothing, and `place_name` has to match
the place index that was built, or the place search in the contribution panel finds nothing — and
that search is the heart of the demonstration. Streets and coordinates are public geography from
OpenStreetMap anyway, which `make places` puts on every device.

**A link to a real person would only arise from tying names to addresses — and that tie is
invented.**

The reason for the effort: the real pictures belong to the local history museum. Shipping them in a
repository anybody can clone is a different thing from showing them in the museum. The same holds
for the village coat of arms — see [decisions.md](../docs/developer/decisions.md), point 21.

## What lies here

| | |
|---|---|
| `photos/` | the image files |
| `seed.json` | everything else: title, dating, place, keywords, credit, provenance, status — and the visitor contributions belonging to each photo |

Both are produced by [`tools/build_seed.py`](../tools/build_seed.py) from a table inside the script.
Whoever wants to change the collection changes the table and runs the script — not the files here:

```bash
python3 tools/build_seed.py
```

The run is **deterministic**: the same call produces the same collection, byte for byte.

**Pictures and JSON rather than a database dump**, and that is the real decision: a dump is
worthless as soon as a column is added. Here a new column costs one line per photo, and the
collection does not have to be curated again. On top of that `make seed` goes through the real
import pipeline — so it builds the thumbnails, fills the import log and checks the import along the
way.

What is **not** in `seed.json` is left out on purpose: file size, dimensions and MIME type are read
from the image while it is taken in. A copy of them could only go stale. The SHA-256 is the one
exception — it serves only to warn when a file has changed since it was built.

## The collection has gaps on purpose

A collection in which everything is complete leaves half the program unchecked. So it holds photos
without a year, photos without a place and one without either — otherwise the contribution panel
would have nothing to offer:

| | |
|---|---|
| without a year | 3 |
| without a place | 2 — one of them **without either** |
| street-accurate only | 2 — for the refinement question |
| deleted | 2, for the list that exists for them |
| visitor contributions | 8, **2 of them taken back** |
| without a credit | 1 |

**Why there are two street-accurate ones and not one:** the number picker has two routes, and a
single photo would only ever exercise one of them. "Gasthof Petersen mit Kastanie" stands on
Hauptstraße (76 addresses, 39 buttons after grouping) — there the section step comes first.
"Schulstraße, heutiger Zustand" stands on Schulstraße (26 addresses, 11 buttons) — there it falls
away and the numbers appear at once.

The two also differ in their **source**: one comes from a visitor who pressed "Reicht so — die
Straße genügt", the other from the curator. That a curator's statement may be refined as well is
the softening from [decisions.md](../docs/developer/decisions.md), point 32 — it belongs in the collection
where it can be seen.

Beside that: descriptions of different lengths, portrait and landscape formats, and a few untidy
file names. `build_seed.py` counts these gaps after every run and **aborts when one is missing.**
They are not an oversight.

## Developing against real photos

Whoever has a real collection saves it here with `make seed-save` — **but does not commit it.** The
invented collection is part of the repository; replacing it with real pictures is exactly the way
museum photos would end up published after all. `make seed-save` says so on every run.
