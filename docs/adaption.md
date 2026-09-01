# Kiekmap for another place or another language

| What you want | What it costs |
|---|---|
| **Another German-speaking place** | configuration only — no fork, no change to the code |
| **Another language** | one line in the `.env` — see below |

That is no accident but a decision that runs through the whole project: **nothing place-specific
stands in the code.** The extent is fetched from `region.json` at run time, the map file is a build
artefact, the place index comes out of a build script. Whoever changes something here should keep
that property — it is the reason a second museum needs no second branch.

---

## Another place

### 1. Fixing the region

One file only: [`tiles/region.json`](../tiles/region.json).

```json
{
  "name": "Musterhausen",
  "bbox": [minLon, minLat, maxLon, maxLat],
  "center": [lon, lat],
  "defaultZoom": 14.8,
  "minZoom": 13,
  "maxZoom": 15,
  "streetChoice": 80
}
```

`streetChoice` is the number of streets the contribution panel offers as buttons — the ones nearest
to `center`. The place index may reach further; whatever lies beyond it is tapped on the map. **A
count and not a radius**, because that keeps the button budget independent of how densely a place
is built up: 80 streets fit into two questions with at most ten buttons each (see
[decisions.md](decisions.md), point 24). If the key is missing, 80 applies.

**The value is to be checked, not adopted** — how, is in [step 3](#3-checking-the-street-choice).

The file describes a **place** and nothing else. Which decades the contribution panel offers stood
here once — but that belongs to the collection and follows from it now: what is offered is what
the collection spans, but at least the 1920s to the 2010s. A museum that later dates a photo to
1890 gets the 1890s button by itself.

**On the length of `name`.** It stands as the heading in the header area, and there it adapts to
the column: the longer it is, the smaller it is set, so that it **stays on one line**. That does
not go on for ever — it does not get smaller than the line "Pictures from" above it, and below
that it wraps. Measured on 16 August 2026:

| Length of the name | On a 1024 screen | On a 1920 one |
|---|---|---|
| up to 12 characters | one line | one line |
| 13 to 16 characters | wraps | one line |
| more | wraps | wraps |

"Holm" has four, "Klein Nordende" has fourteen. **A wrap is not an error** but the deliberate
fallback — a truncated place name would be worse. Whoever wants to avoid it shortens the `name`
("Klein Nordende" instead of "Klein Nordende-Lieth"); the full name belongs in the welcome text
rather than in the heading anyway.

**Working out the bounding box.** From a centre and the radius you want:

```bash
python3 -c "
import math
lat, lon, r = 53.62053, 9.67601, 5.0   # centre, and radius in km
dlat = r / 111.320
dlon = r / (111.320 * math.cos(math.radians(lat)))
print([round(x, 5) for x in (lon-dlon, lat-dlat, lon+dlon, lat+dlat)])
"
```

Choose generously. The `bbox` also limits how far the map can be dragged; too tight shows up only
at the kiosk, when somebody zooms out. The tiles are built with a 10 % margin anyway.

**Determining the zoom levels.** Choose `defaultZoom` so that the centre of the place fills the
picture:

```bash
python3 -c "
import math
lat, map_width_px, wanted_km = 53.62, 1500, 3.0
mpp = 156543.03392 * math.cos(math.radians(lat))
for z in (13, 14, 14.5, 15, 15.5, 16):
    m = mpp / 2**z
    print(f'  z={z:<5} {map_width_px*m/1000:5.2f} km wide')
"
```

On a 1080p display the map area is about 1500 × 920 px. Choose `minZoom` so that the whole extent
is visible at once. `maxZoom` stays at 15 — that is the limit of the Protomaps daily build; beyond
it the map is over-zoomed and still stays sharp.

### 2. Building the map data and the place index

```bash
make tiles     # vector tiles, fonts and icons for the new region
make places    # place index from OpenStreetMap
```

Both need the internet and run on the development machine, not on the Pi. Order of magnitude for a
municipality with a 5 km radius: 4–5 MB of tiles, 14 MB of fonts and icons, some eight thousand
places (`places.json` about 1.5 MB).

**Addresses** make up the largest part — for Holm 7686 of 8513 entries. They make the placing
accurate to the house rather than to the street; without them every photo of a street 800 m long
would get the same point. Whoever wants to keep the place index small can comment the two `addr:`
lines out in `tiles/build-places.py`; the interface then skips the house-number step by itself.

`make tiles` also puts `region.json` under `data/` — the backend reads it there and uses it to
check whether a placing from the contribution panel lies in the region at all. **Without that file
the guard does not bite** (it then lets everything through instead of refusing for no reason).

### 3. Checking the street choice

The contribution panel asks where a photo was taken, and **the main way there is buttons**: first the
initial letter, then the street, then the house number. There is no search field — the visitor view
has no input field at all, because no keyboard stands at the kiosk (see
[decisions.md](decisions.md), point 24). Whether that way holds up is decided by the place index,
and that can be looked at before the first visitor.

**Where the streets come from.** From `make places`: the script asks the Overpass API once for
everything inside the `bbox` and writes it into the place index. Whoever skips this step gets no
error — the panel then says "Please tap the spot on the map" and arms the map by itself. That is a
working way out, but a way out: without the place index there is no house number either, and every
photo of a street 800 m long would get the same point.

**How to look instead of guessing.** One call returns exactly the list the tree gets:

```bash
curl -s localhost:8000/api/places/streets | python3 -c "
import json,sys
names = [p['name'] for p in json.load(sys.stdin)]
print(f'{len(names)} streets to choose from:')
print('  ' + ', '.join(names))
"
```

Whoever looks at it knows three things: whether the centre of the place is completely in, how many
streets from elsewhere come along, and whether `streetChoice` fits.

**How to choose `streetChoice`.** The value decides how many questions it takes to reach a street.
The groups are calculated, not written down: from at most ten buttons per level the tree follows by
itself. For Holm it looks like this:

| | |
|---|---|
| Streets to choose from (`streetChoice` 80) | 80 |
| Buttons on the first level | 10 — `A` `B–D` `E` `F–G` `H` `I` `K–L` `M–R` `S` `T–Z` |
| of those straight to the street list | 7 |
| with one step in between | 3 — `A` (15), `H` (11), `I` (11) |

Two questions as a rule, three in the exception. **That is the target.** A more densely built place
needs a smaller value, a spread-out one takes a larger — and it can be worked out with the same
query above: once more than about a hundred streets come together, the third level becomes the
rule and the way to the house number gets long.

**What can go wrong, both without an error message:**

- **The `bbox` is set too tight.** The place index reaches only as far as it does; edge streets are
  then missing entirely and stand neither in the search nor on a button.
- **The `bbox` is set too wide.** Neighbouring villages come along — and because `streetChoice`
  takes the *nearest*, their streets push the local ones out of the choice. In Holm 486 streets lie
  in the index and only 80 on the buttons; had the extent been twice as large, streets no photo of
  the collection ever shows would be among them.

Both can be seen in the list above, before anybody stands in front of it. If you expect a street
name and do not find it, the `bbox` is the first suspicion, not the code.

### 4. Putting the coat of arms in

**What ships is a placeholder, not a coat of arms** — a plain shield out of
[`tools/build_logo.py`](../tools/build_logo.py). Why not a real one is in
[decisions.md](decisions.md), point 21.

Replace [`frontend/public/logo.png`](../frontend/public/logo.png) with your own — same file name,
nothing else. The picture lies over the top left corner of the map and is at the same time the way
into the admin area. Nowhere in the code does it say what is on it; the label for screen readers is
put together from `name` in the `region.json`.

Portrait or landscape makes no difference, the picture is fitted into a square of 4.5 rem. About
400 px on a side is sensible; PNG with transparency looks best on the map.

> **Do not commit the replaced file.** It carries the same name as the placeholder, so it turns up
> as a changed file. On your own device that is right; in a repository somebody can clone, it
> passes the coat of arms on — see below.

#### On the law: two questions that often get merged into one

**Copyright.** A municipal coat of arms is an official work under § 5 (1) UrhG and therefore free
of copyright. There is nothing to settle from that side.

**The law on arms.** Independently of that, *using* a coat of arms is restricted: it is an official
emblem, the municipality governs its use, protected through the right to a name (§ 12 BGB) and the
rules on official emblems. Wikipedia points this out explicitly on its coat-of-arms pages too.

Two things follow:

- **On your own device** the coat of arms of your own place is as a rule unproblematic for a local
  history museum — if in doubt, ask the municipality.
- **In a public repository it is another matter.** Whoever publishes the repository passes every
  file in it to everybody who clones it. Permission for your own museum is not permission for
  third parties, and a note or an attribution changes nothing about that: this is not about credit
  but about permission.

That is why a placeholder lies in this repository, and the coat of arms stays a local file — like
the `.env` and the built map.

### 5. Checking what belongs to the collection

In the `.env`:

```bash
KIEKMAP_EXIF_DATE_MAX_YEAR=1990   # from when an EXIF date counts as the date of the scan
KIEKMAP_ADMIN_PIN_HASH=...        # PIN for the admin area

# Details that apply to every photo on import. All three are empty by default.
KIEKMAP_IMPORT_TAGS=["Gebäude"]                 # keywords for every imported photo
KIEKMAP_IMPORT_CREDIT=Sammlung Heimatmuseum Holm # credit where the file names nobody
KIEKMAP_IMPORT_PROVENANCE=Online-Archiv des Museums, Verzeichnis 01 Orte/
```

Raise `exif_date_max_year` if the collection also holds genuine digital photographs — otherwise
they lose the date they were taken. Lower it when nothing but scans is expected. Where the file
names its device, that decides anyway: a scanner never dates, a camera always does. The value
applies only to files with no device recorded.

The three `IMPORT_` values are the place for what makes a *collection*. `KIEKMAP_IMPORT_TAGS` is a
JSON list; in Holm the stock is buildings, elsewhere it is costumes or ships.
`KIEKMAP_IMPORT_PROVENANCE` is put verbatim in front of the file path in the import folder and
therefore carries its own separator at the end — so the provenance of a photo leads back to the
file in your own archive.

Whether the import reads the **folder names** need not be set anywhere: a path element counts as a
street when the place index knows it. An archive filed by street and house number is placed by
itself; one filed differently is simply left alone.

The PIN hash is produced by:

```bash
cd backend && .venv/bin/python -m app.cli pin
```

The PIN itself is stored nowhere. If `KIEKMAP_ADMIN_PIN_HASH` is empty, the admin area says so in
plain words instead of rejecting every entry.

### 6. Checking it all together

```bash
make dev
```

- Does the map show the right place in the right extent?
- Can the map not be dragged beyond the region?
- Do the buttons in the contribution panel lead to a real street in two or three steps (see
  [step 3](#3-checking-the-street-choice))?
- **Switch the wifi off and move the map** — the labels have to stay visible.

The last point is the most important. Checking it without looking:

```js
performance.getEntriesByType('resource')
  .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length
// has to be 0
```

### What *not* to do while doing it

No change to the code, no fork, no new branch. Whoever finds while adapting that they do have to
change code has found a bug — the value then belongs in `region.json` or in the `.env`, not in a
copy of the project.

Cosmetic residues are the exception: comments in the backend name Holm where an example makes the
case concrete. That is documentation, not logic.

---

## Another language

One setting, and it stands where every setting of the instance stands:

```bash
# .env
KIEKMAP_LANGUAGE=en
```

Then restart the service. **No new build is needed** — the frontend fetches the language at startup
through `GET /api/config`. `de` and `en` are allowed; any other value aborts the start instead of
falling back to German in silence.

What that switches is everything a person reads at the device: the visitor view, the admin area,
the error messages of the API, the import log, the messages of the backup, the date labels and the
number format.

**What it does not switch is the map underneath.** It labels its places in German whatever the
setting says, because the label language is a property of the place rather than of the reader — in
Holm the street is called Mühlenweg in every language. For a museum outside the German-speaking
area that is the wrong answer, and it is open work:
[issue #33](https://github.com/nordfisch/kiekmap/issues/33).

### Where the texts are

Two catalogues, built the same way:

| | Interface | Backend |
|---|---|---|
| Where | [`frontend/src/text/`](../frontend/src/text/) | [`backend/app/text/`](../backend/app/text/) |
| German | `de.ts` | `de.py` |
| English | `en.ts` | `en.py` |

**A missing entry breaks the build, not the museum.** In the frontend the type of the catalogues is
`typeof de`, so `tsc` refuses an incomplete translation. In the backend they are frozen dataclasses,
and a missing entry is a `TypeError` at startup.

### A third language

The same construction carries it without rebuilding: one file per catalogue, one more value in
`KIEKMAP_LANGUAGE`. At three languages a translation service starts to pay off — see
[decisions.md](decisions.md).

The language is a **setting of the instance, not a choice for visitors**. The device stands in a
museum and speaks that museum's language. A switch on the touchscreen would be one more thing to
operate for visitors who are often elderly, and no relief.

### What stays German in every language

| Where | What | Why |
|---|---|---|
| Kinds of place | `strasse`, `gebaeude`, `flur` … | keys from `tiles/build-places.py`; what is shown is what `t.location.kinds` makes of them |
| Street and place names | from OpenStreetMap | a proper name is not translated |
| Older entries in the import log | `ImportLog.message` | a record of what the device said at the time |
| `*.de.md` and `docs/archive/history.de.md` | docs for the museum and for operation | kept as a translation, see [development.md](development.md#language) |

The kinds of place are the one case that looks like a trap and is not: German keywords stand in the
database, and the translation is what gets shown. `en.ts` maps the same keys onto `"Street"`,
`"Building"` and so on.

The import log is the second. It reports what happened during an import, and the sentence was
written and stored at the time. New entries follow the language that is set; the old ones stay as
they read.

### What is fixed in English and does not travel

The folders `_done` and `_problem` in the inbox, the backup folder `kiekmap-backup/` with
everything in it, and the `status` of `/health`. The first two are names in the file system: were
they to follow the setting, changing it would have to rename folders — on the device and on every
stick already written. The third is a machine value that the kiosk service reads.

---

## When splitting things up starts to pay off

As long as it is **one place per installation**, the present cut is the right one: one
configuration file, two build scripts, done. More structure would only create work nobody needs.

It gets interesting as soon as one of these cases arrives:

- **Several places on one device** — a district museum with several municipalities, say. `region`
  would then need a database reference instead of a file, and photos would have to be assigned to
  a region.
- **One shared collection, several kiosks** — the backend would then be central and only the
  frontend configured per site.
- **Regular updates to several museums** — it would then pay off to take the configuration out of
  the repository entirely, so that a `git pull` never overwrites an adaptation.

Until then: a second museum gets a copy of the repository, changes `region.json` and the `.env`,
builds tiles and place index, and is done. It pulls updates with `git pull` — its own adaptations
lie in files that do not collide.
