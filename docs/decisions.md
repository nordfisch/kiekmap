# Decisions

Why things are the way they are. Every point names the **decision**, its **reason** and its
**consequence**. What the program can do is in the [changelog](../CHANGELOG.md); how the work went
is in the commits and the closed issues, and up to v0.8.0 in [history.de.md](history.de.md).

**A lesson is kept as the decision it led to, not as a lesson.** Whatever the work teaches ends up
here in one point with a short reason, or it stays where it happened — in a commit message, in an
issue. There is no third place for it.

Append new entries at the bottom, do not delete old ones. Superseded ones get the note
*Superseded by …*; merged ones keep their number as a pointer, so that a citation in an old note
still resolves.

---

## 1. Historic photos are scans — that shapes the whole data model

The photos in a local history museum are scanned paper prints. Their EXIF carries the date of the
scan, not of the shot, and almost never GPS. The EXIF import is the bonus case, not the normal one;
the actual data comes from curators and visitors.

Three consequences carry the whole data model:

1. **Every field carries its origin** (`exif` / `curator` / `visitor`). A date guessed from EXIF
   must never overwrite a curated one.
2. **Dates are intervals.** „um 1930", „1920er", „vor dem Krieg" are the reality. Every photo stores
   `date_from`/`date_to` plus a precision (`day|month|year|decade|unknown`), and the time filter
   queries for **overlap**. With the obvious query it is exactly the loosely dated photos that
   disappear, and without an error. There is a test for that.
3. **The contribution panel is the main path** by which the system gets places and dates, not a side
   feature.

---

## 2. Images in the file system, metadata in SQLite

Originals and thumbnails are files under `data/`, everything else is in a SQLite file beside them.

**Why not images in the database:** thumbnails should be served cheaply, the database file should
stay small and quick to back up, and in an emergency a curator has to reach the originals with an
ordinary file manager. A database full of image data meets none of these.

**Why SQLite and not Postgres:** one device, one process, a few thousand records, and backing up
should mean „copy one file".

---

## 3. File names are the SHA-256 of the image content

```
data/photos/a3/f2/a3f29c…e81b.jpg
data/thumbs/240/a3/f2/a3f29c…e81b.webp
```

Four properties follow from that:

1. **No name collisions.** Two `Kirche.jpg` from different sources do not clash.
2. **Duplicate detection.** The hash is `UNIQUE`; a second import is rejected and logged.
3. **Cacheable without limit.** The same name guarantees the same content, so `immutable` headers
   apply.
4. **Incremental backup.** If the name is already on the stick, it is the same image. The second
   backup therefore takes seconds instead of minutes, and a backup that is quick actually gets done.

The original file name is kept as `original_filename`; it is often the only content that comes along
(`Kirchweih_1932_Muehle.jpg`). The two-level directory split (`a3/f2/`) keeps the folders small.

**What the SHA-256 cannot do:** recognise scans that show the same thing but are cropped
differently. The difference hash from
[point 54](#54-the-machine-finds-duplicates-a-human-has-to-decide) covers that.

---

## 4. Offline map: PMTiles and MapLibre GL

A single `map.pmtiles` with vector tiles of the region, built from the Protomaps daily build,
displayed by MapLibre GL JS.

**No tile server needed:** PMTiles is a format the browser reads single tiles out of by HTTP range
request. nginx does that for a static file out of the box, which removes a whole component from
operation.

**Vector instead of raster:** sharp beyond the zoom level it was built for, considerably smaller,
colours and labels adjustable in the style instead of baked in. The price is WebGL — no problem on a
Pi 4/5, and on a Pi 3 raster would be the better choice.

**Fonts and sprites are local.** The Protomaps style points at `protomaps.github.io` for them.
Without the change the tiles would come offline and the labels not at all, and that only shows up
once the device stands in the museum without a network. `make tiles` downloads both into
`frontend/public/basemaps/`. The check is a count, not a look: the page must make **zero** requests
to a foreign origin.

**Place search without the internet:** the same extract produces a `places.json`, which is read into
the `places` table at startup. That replaces Nominatim for the one purpose we have.

The `.pmtiles` file does not belong in the repository. What is versioned is the build script and the
bounding box in `tiles/region.json`.

---

## 5. Visitor contributions go in directly — with a complete log

What a visitor enters is in the metadata at once and appears on the map at once. Every change is
logged in `changes` and can be taken back one by one.

**Why no moderation queue:** the appeal for the visitor is the immediate effect. A queue removes it
and creates work for volunteers, who are scarce anyway.

**„At once on the map" also means: visible at once.** A contribution triggers a reload, markers and
histogram together; the visitor's time range stays untouched. Without that the contribution would
only become visible after panning the map, and older visitors do not pan.

Three rules catch the abuse case without slowing the normal one:

1. **Only empty fields may be filled**, otherwise HTTP 409. What a curator set is untouchable, and
   the second visitor cannot overwrite the first.
2. **Coordinates have to lie inside the region.** The pin can only be set on the map, but the API is
   reachable; a photo in the Pacific would vanish from the view without anyone noticing why.
3. **Every change is in `changes`** with a session id — a random number per page load, stored
   nowhere. It lets a curator see whether several entries came from one person; more it should not
   allow.

**Decade before year.** The date input asks for the decade first, then optionally the year. Somebody
looking at an old photo usually knows „die Zwanziger", not „1924". „Ganze 1920er" is therefore a
full answer and not an evasion.

---

## 6. Operation: Pi OS Lite, cage, Chromium — the application in Docker

Raspberry Pi OS **Lite** without a desktop, plus `cage`: a Wayland compositor whose only job is to
show one program full screen.

**Why no desktop:** there you have to tame screensaver, power saving, update notices and autostart
quirks one by one, and the background becomes visible while booting. Under cage nothing can come to
the front. The device boots into the map in about 20 seconds.

**Why the application is in Docker anyway:** reproducibility, and an update path that works offline
— a `docker save` tarball on a stick, `update.sh`, done. Versions are traceable through image tags
instead of through the state of a system that grew.

**The kiosk service waits for `/api/health`** before Chromium starts. Otherwise the device shows an
error page for a few seconds every morning.

---

## 7. The way into the admin view is visible, the PIN protects it

A keypad with large keys, then the admin view with an expiring session. **Where the way in sits is
in [point 26](#26-two-ways-into-the-admin-view-and-neither-is-the-coat-of-arms-any-more);**
everything here applies unchanged to each of them.

**Why visible instead of hidden.** An invisible gesture is exactly what the volunteers forget who
have to get in twice a year. And it protects nothing: the protection is the PIN. Somebody who taps
out of curiosity sees a keypad and goes back.

**Why a PIN and not a password.** Input happens with a finger on a touchscreen, often by older
people. A keypad with large keys beats an on-screen keyboard for that.

**What carries a four-digit PIN is the lockout, not the length.** A script tries ten thousand
possibilities in seconds. After five failed attempts the device locks for a minute, which stretches
the same attack to a good two years. The hash is PBKDF2 with 200,000 rounds.

**Sessions live in memory, not in the database.** A restart therefore ends every session — on a
device that boots every morning, the cheapest guarantee that no login survives the night. Time is
counted in remaining seconds rather than in points in time: the Pi has no real-time clock and no
network, and its wall clock can be years off after a power cut.

---

## 9. Editing: a missing field means „leave", an empty field means „delete"

The metadata editor distinguishes a field that is not sent at all from one that is explicitly
empty. The first stays unchanged, the second is cleared. In the backend `model_fields_set` from
Pydantic carries this.

**Why.** Without the distinction a wrong dating could only be replaced, never removed. And removing
it is the common case: somebody notices that a year cannot be right but does not know what is. If
the entry can be taken out, the photo counts as undated again and lands in the contribution panel.
That is the difference between a database that corrects itself and one where mistakes settle in.

**Taking back a visitor contribution** clears the field instead of restoring an old value — a
visitor may only fill what was empty
([point 5](#5-visitor-contributions-go-in-directly--with-a-complete-log)). If somebody from the team
has edited the field in the meantime, taking it back is refused: it would throw that work away with
it.

---

## 10. Uploaded photos are in the database at once

The batch upload stores every image as it arrives. The table afterwards is a follow-up list, not a
queue; „Übernehmen" only adds title, year and place.

**Why.** Otherwise a closed browser costs the whole batch — and the moment somebody uploads forty
images for the first time is the moment something interrupts. What is left lying is not lost but
incomplete, and it turns up in the contribution panel on its own.

The batch values fill only what is empty; if a file brings a usable date or GPS, the file wins.
Upload sends **one file per request**, although the endpoint takes a list: only that way can
progress be shown.

---

## 11. Backup is a feature, not a script

Backing up and restoring are screens in the admin view with a progress bar and plain wording, not
`backup.sh`.

**Why.** The audience is older volunteers who do this once or twice a year. A shell script means, in
practice, that it never runs.

- **A folder instead of a ZIP** on the stick. An aborted backup is then partly usable instead of
  worthless, and it opens on any computer.
- **`VACUUM INTO`** writes the database out consistently without stopping operation.
- **Restoring** unpacks alongside and switches over only at the end; the previous state is set
  aside. An aborted restore must never destroy the running collection.
- **A reminder instead of automation**, red after 30 days. Nothing happens unasked, but nothing is
  forgotten for years either.

**A ZIP download is the second path, not the replacement.** It helps where no stick is at hand. The
arguments against ZIP still hold, and the interface says them: the archive is not incremental, and
an aborted download is worthless.

**What carries the second path is a property that binds it to the first:** the archive is exactly
the folder the stick gets, only zipped. Restoring therefore means unpacking it onto a stick and
using the existing restore. There is no second restore path with its own bugs, and
`test_entpacktes_archiv_laesst_sich_wiederherstellen` pins the property down.

Two conditions hang on it:

- **The archive is built as a stream, uncompressed.** On a Pi with 2 GB of RAM it must not exist
  anywhere in full, and the SD card is precisely what the backup protects against. `ZIP_STORED` is
  not thrift here: JPEG and WebP are already compressed, and a second pass only costs time.
- **`proxy_buffering off` in nginx.** With the default, nginx collects the whole response on disk
  before sending the first byte — several gigabytes onto that same SD card.

**The way back runs through the incoming folder, but it asks first.** A ZIP backup dropped there
does not restore itself; it is recognised and offered in the backup screen. The reason is a property
of that folder: everything else it does is **additive and inconsequential**. A restore **replaces
the whole collection**. Mixing both without a confirmation would mean that a file copied there by
accident swaps out the collection, and on a kiosk nobody notices for weeks.

The download authenticates with a **one-time ticket**, because a browser download cannot send an
`X-Admin-Token`. Putting the session token in the address would be wrong: addresses end up in
history, in bookmarks and in proxy logs, and that token opens the whole admin view.

---

## 12. The map is background, not the main thing

A colour style of its own, „Papier", in the tones of the interface instead of one of the supplied
ones, plus three layers fewer and streets at 80 % of their width
([`kiosk/mapStyle.ts`](../frontend/src/kiosk/mapStyle.ts)).

**Why.** The ready-made styles are built for navigation: turquoise water, strong green, cool grey.
The rule while picking colours was: **nothing on the map may be as saturated as a photo.**

**What is left out**, and what explicitly is not: `pois`, `address_label` and `roads_shields` go. The
street names stay — **the small ones too**: the contribution panel refers to them, and in a village
most streets are small.

**The interpolation stops are scaled, not the curve.** The widths are zoom interpolations; wrapping
them in `["*", width, 0.8]` is rejected by MapLibre. This way later changes to the style still come
along, instead of ending in a hand-maintained copy of somebody else's cartography.

---

## 13. Locating in steps: street, then block, then house number

*Absorbs [point 24](#24-the-street-is-chosen-not-typed).*

The place picker offers streets, then house numbers as a grid of buttons, and below them „Reicht so
— die Straße genügt". In the free search of the admin view, addresses only appear once the input
contains a **digit**.

**Why not a flat list.** A result list would be full of the house numbers of a single street and
would have crowded out every other street.

**Why steps are good, not merely bearable.** It is the same shape as the dating (decade, then year),
and for the same reason: the second step is **skippable**. Not every house is in OpenStreetMap, and
nobody knows the house number for every photo. The pin sits on the street after the first step;
whoever stops there has answered.

**Long streets get a third step.** Two reductions, in this order:

- *The base number stands in for its letter suffixes.* Spatially they add nothing — 3a and 3c are a
  few metres apart, and the accuracy is 15 m anyway. The button always shows an address that really
  exists.
- *If there are still too many, a block comes first* — „1–13", „15–24". The cut goes **by count, not
  by numeric value**: streets are numbered with gaps, and equally large blocks beat differently
  filled ones. The price is an occasionally odd label like „37–183"; it names the gap instead of
  hiding it.

For an average village street it stays at the one step.

**The street is chosen as well, not typed** — first the initial letter, then the street. The visitor
view therefore has **no input field at all** and needs no keyboard. A real keyboard in an exhibition
room goes missing and opens key paths in Chromium that the kiosk just closed; an on-screen keyboard
would have had to be built. Both would be effort for a control that looks broken without a keyboard.
The admin view keeps its search field — that is where curating happens, not visiting.

**The letter groups are computed, not written down.** A letter with few streets is merged with its
neighbour until at most ten buttons remain; a group with more than ten streets splits one level
deeper, and the cut follows the names instead of a fixed depth. A second museum gets its own tree
that way. Grouping uses the **folded** name — otherwise an „Ölmühlenweg" would get a lone Ö button
behind the Z.

**Not all streets are on offer, but the `streetChoice` nearest to the centre.** The place index
reaches beyond the neighbouring villages; putting them all into buttons would cost a fourth
question. The photos of a local history museum show its own place, and what lies further out is
tapped on the map. A **count** instead of a radius, because it keeps the button budget independent
of how densely a place is built. If the key is missing from `tiles/region.json`, 80 applies.

**The accuracy is used for this.** A street gets 150 m, a house number 15 m. A point tapped on the
map by hand gets **no** value — how well somebody aimed is not our claim. Moving the pin loses name
and accuracy again, for the same reason.

**House numbers are sorted naturally**, by (leading number, rest): 1, 1a, 2, 9, 10 instead of 1, 10,
12, 1a, 2, 9.

---

## 14. The timeline belongs to the collection, not to the map extent

The time slider always spans the range of the **whole collection** and stands still. The bars below
it show what lies in the visible extent.

**Why not scale along.** An axis that rescales while zooming changes, unnoticed, what the same
position on the slider means. For somebody standing in front of it once, a control that changes its
meaning cannot be understood. On top of that, axis and selection drifted apart as soon as the extent
held fewer decades than the whole collection, and the selection bar drew itself outside its field.

**What the fixed axis can do as well:** an empty axis with a single bar says something the rescaling
axis concealed — *there are only photos from this one decade here.*

**The safeguard:** `fraction()` in `kiosk/timeAxis.ts` clamps to 0…1, `setTimeRange()` pulls the
selection into the axis. Even if the two ever drift apart again, every element stays in its cell.

---

## 15. Photos at the same place: a stack to page through, not a fan

Photos on the same point (to about a metre) are merged into one entry **before** clustering. On the
map they appear as one thumbnail with the count in the corner; a tap opens the full-screen view, and
paging happens there.

**Why it is needed.** Photos on identical coordinates became just as many markers exactly on top of
each other above the cluster threshold, and only the topmost was reachable. **Identical points do
not separate at any zoom level.**

**Why not fan them out.** A fan shows the photos where they are not, and with a larger stack it is
permanently restless; at the edge of the map it has no room. A fan *on tap* also introduces a state
that has to be left again, without anything showing the way out. Two-step gestures are what older
visitors get stuck on.

**Why before clustering.** Grouping afterwards only helps below `CLUSTER_MAXZOOM`. This way
supercluster never sees the duplicates, and a stack is one marker at **every** zoom level.

**The threshold is five decimal places**, about a metre. It matches the actual case: photos from the
place picker carry exactly the same coordinate of the street. Somebody who set the point by hand
lands beside it and stays a marker of their own — correctly, because then it *is* a different place.

**On top lies the most recently edited photo**, because the map query sorts by `updated_at`. The
photo just located therefore lies on top exactly where the map moves to after a contribution.

---

## 16. Deleting means taken out of the exhibition, not removed from disk

The status is called `deleted` instead of `hidden`, the image file stays, the database row stays,
and „Wiederherstellen" brings both back. That saves three problems:

- The SHA-256 stays known; a repeated import recognises the duplicate and does not bring the photo
  back unasked.
- Change log and import log still point at a photo that exists.
- The backup needs no special rule for a recycle bin.

**What follows is the real part of the decision:** deleted photos count in no tile of the overview
and appear in no list except „Gelöscht" — not in „Alle" either. Otherwise deleting would have no
effect where anybody looks, and the work lists would keep offering the photo somebody just sorted
out. Every number says the same as the list it leads into.

**The price:** there is no way to hide a photo *temporarily* without calling it deleted — while the
rights are being clarified, for instance. Whoever needs that needs a third status, not a second
meaning for this one.

---

## 17. The migration history was squashed once — and that was the last chance

The existing Alembic revisions were merged into one initial schema while no device had ever run
Kiekmap. There was therefore no database from which a migration path could have led anywhere.

**From the first Pi on this is no longer allowed.** Once a museum has a filled database, the chain
of migrations is the only way its data survives a schema change. Squashing would then not be tidying
up but announced data loss.

**The `PRAGMA foreign_keys=OFF` in `alembic/env.py` stays.** It is the lesson from a data loss, and
the test that guards it hangs on no revision number — a test that dies with the bug it guards is not
a test.

---

## 18. The sample collection is images plus JSON, not a database dump

`seed/` holds the image files under their original names and a `seed.json` with everything else.

**A database dump would be the shorter path and is still the wrong one:** it is worthless as soon as
a column is added, and that happens here regularly. This way a new column costs one line per photo,
and the collection does not have to be curated again.

Two properties come with it:

- **Reading it in goes through the real import pipeline**, produces the thumbnails, fills the import
  log and exercises the import on every run.
- **The file is readable in a diff.** Changing a dating shows up as one line.

SHA-256, file size, dimensions and MIME type are deliberately **not** in it: they are read from the
image on import, and a copy could only go stale. The SHA-256 is the exception and warns only that a
file has changed since it was saved.

**The gaps in the collection are part of the collection.** Photos without a year, without a place,
one without either, a withdrawn visitor contribution: without them the collection exercises half the
program. `test_luecken_bleiben_luecken` pins down that reading it in does not fill them either.

---

## 19. Credit and provenance are two fields because they have two readers

- **`credit`** — one line, shown in the visitor overlay below the description.
- **`provenance`** — who the image came from, whether it is a loan, whether there is a release. An
  internal note that never leaves the admin view.

**The type enforces it, not an agreement.** The kiosk endpoint returns `PhotoDetail`, and that class
has no field for the provenance — so it cannot send it by accident either. The admin view gets
`PhotoAdminDetail`, which inherits from it. A rule that exists only in somebody's head is not kept
by the next endpoint.

Both are also batch values of the import: a box of scans almost always comes from one person, and
neither field can come out of the file — a scanner does not know who lent the picture.

---

## 20. The import reads what the files and their folders already say

Museum archives are filed by street and house number:

```
Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
```

Discarding these folder names means asking visitors for the place of a photo whose address is
written right beside it — and making volunteers type in addresses that are already there.

**The rules fall into two layers, and that separation is the actual design:**

| Layer | Applies to | What it reads |
|---|---|---|
| **Metadata** (`import_file`) | *all four* import paths | date, place, title, description, credit, provenance, tags from EXIF/IPTC |
| **Path** (`foldermeta.py`) | incoming folder, CLI, USB stick | street and house number from the folder names |

**The second layer is switched on through the `root` parameter of `import_file()`** — the folder the
import was started on. That makes it **a question you have to answer instead of one you can
overlook**: whoever builds a fifth import path decides through a parameter what the root of this
file is. The browser upload answers `None`, because a browser sends no path.

### The device first, then the year limit

`exif_date_max_year` ([point 1](#1-historic-photos-are-scans--that-shapes-the-whole-data-model))
stays, but as the **substitute for a missing device entry**, not as the first authority:

- **Scanner** (`HP Scanjet 3670`) → **no date**, whatever year is written there. Taken at face value,
  historic photos of the village would sit on the timeline at the day of the scan and, counting as
  dated, never come up for correction.
- **Camera** (`OLYMPUS E-500`) → **the date counts, even after 1990.** These shots really are recent;
  without the reversal a large part of the collection would arrive undated.
- **No device entry** → the year limit decides alone.

The reversal is measured against the collection: the camera photos are almost all colour shots of
the houses as they stand today, and not reproductions of old prints.

### The place index recognises the street, not a folder called „Straßen"

A path segment counts as a street when `places` knows it. That is why nothing place-specific is in
the code despite this parsing. What the archive shortens is recognised too — folder „Wiesengrund",
street „Im Wiesengrund" — but only under two conditions:

1. **Exactly one match.** „Deelenweg" is contained in „Deelenweg I" *and* „Deelenweg II"; guessed,
   the photos would lie at the other end of the village.
2. **Every word contains a letter.** The house-number folder „2" otherwise matched the street
   „Kolonie Autal 2" — unambiguous and completely wrong. A number is a house number; only a name is
   a street.

### A folder without a house number locates on the street

At first such a photo stayed unlocated, so that it would not count as answered with a point several
hundred metres off and drop out of „Wo ist das?". Since the refining question exists
([point 32](#32-refining-goes-through-its-own-endpoint-not-through-a-loosened-check)), it does not
drop out but falls into the more precise question. The street name additionally becomes a tag and a
place name.

### Precedence where two sources speak

A coordinate from the metadata beats the folder as long as the folder names no house number — the
trade-off is in
[point 34](#34-the-archive-folder-beats-the-exif-coordinate--as-soon-as-it-names-a-house-number).
The other way round, the path layer fills **empty fields only**.

### The downside

The import is **no longer reticent**, and a photo it titles counts as titled and is not offered
again. That is why the check for non-values stays strict
([point 52](#52-a-default-is-not-a-finding)), why the path layer fills only empty fields, and why an
overlong title moves into the description
([point 48](#48-what-stands-in-the-title-field-is-not-automatically-a-title)).

---

## 21. No municipal coat of arms in the repository

`frontend/public/logo.png` is a placeholder from `tools/build_logo.py`; the coat of arms is put in
on the device, like the map data.

The reason is not a licence question, and that is exactly where the trap is. A German municipal coat
of arms is an official work under **§ 5 Abs. 1 UrhG and in the public domain**. Beside that stands
**Wappenrecht**, the law on armorial bearings: a coat of arms is a sovereign emblem, its use is
governed by the municipality and protected through the right to a name (§ 12 BGB) and the rules on
sovereign emblems.

**A notice does not cure that.** With a licence, attribution helps — you name the author and you
may. Here it is about *permission*, and permission cannot be replaced by a footnote. The two cases
also differ:

| | |
|---|---|
| The museum shows the arms of its own place on its own kiosk | as a rule unproblematic |
| A public repository contains the file | hands it to everybody who clones |

**A repository carries its history with it**, so deleting the file later is not enough — it has to
disappear from the whole history, and that only works while there is no remote.

**Swapping it cost one file and no line of logic**, because nowhere in the code does it say what the
image shows. The same property that lets a second museum do without a fork reduced a legal problem
to a file swap here.

---

## 22. The backlog gets classified, and its numbering outlives it

The backlog gave every item a **kind**, a **ranking** by importance and urgency, and a **number**.

**Four kinds, because there are four different things to do.** *Fehler* (something does not do what
it promises), *Aufgabe* (clearly bounded, only the work is missing), *Frage* (before the work,
somebody has to decide what gets built), *Idee* (not yet decided whether at all). The cut sits where
it changes the work: a task can be picked up in an afternoon, a question cannot.

**Importance and urgency are two axes because they come apart here.** Acceptance on the first Pi is
the weightiest open item and still not urgent, because the device is missing. A single priority
column would have either inflated it or played it down. Each axis therefore has a definition in the
file: **urgent** means it affects somebody today or blocks another item; **important** means that
without it the project will not be what it should be.

**The number is never reissued**, not even after an item is done. It has to point at exactly one
thing in a commit, a conversation or an instruction to a coding agent, even after the heading has
changed. A reused number later points at something else, which is worse than no number. The price:
the order in the file comes loose from the counting over time. Sorting goes by ranking, not by
number.

This file does the same: **point 8 is missing**, because it was absorbed into
[point 11](#11-backup-is-a-feature-not-a-script).

**Two sequences share one word.** This file numbers its points as well, independently of the
backlog, and both were cited as „Punkt N". A citation therefore always names its target, as a link —
an anchor for a decision, the issue for open work. And whoever writes a new point reads the last
heading of the file it goes into first: what the other sequence has reached says nothing about this
one.

**The ranking stands only in the overview table**, not additionally under each heading. Two places
for the same value drift apart, and then nobody knows which one is right.

**And it stayed one file for as long as that held.** As a file the backlog reads in one go, lives in
the same history as the code it describes, and survives a coding agent losing its context. What
ended it is in [point 69](#69-the-backlog-moves-into-issues-and-the-old-numbering-stays-where-it-is).

---

## 23. After a contribution the same photo counts, not the next one

Whoever answers a question then gets **the same photo with the other question**, as long as that
question is still missing something. Only when nothing is missing does a new photo come.

**The reason is a promise that would otherwise break.** After every contribution the thank-you said
„Das Foto ist jetzt auf der Zeitleiste" — even for a photo without a place, which appears on no map.
A message may only claim what the view shows at that same moment.

**A more honest sentence would not have been enough.** The visitor would still get nothing to do,
right after showing that they know this photo. Instead the thank-you asks for what is missing, and
the next question applies to the same photo — which is also the most productive moment the panel
gets.

**What is deliberately ignored:** the list of photos tapped away. Whoever skipped one and then does
contribute something gets it back with the other question. „Weiß ich nicht" stays the way out, and
the chain ends by itself.

---

## 24. The street is chosen, not typed

**Absorbed into [point 13](#13-locating-in-steps-street-then-block-then-house-number)**, where
locating is described in one piece. The number stays for older citations.

---

## 25. The bars group what the collection allows

How many years one bar behind the time slider covers is computed by `bar_width()` in
[services/dates.py](../backend/app/services/dates.py), by two rules.

**First: never finer than the coarsest dating in the collection.** A photo dated „1920er" carries
`date_from = 1920-01-01`. In yearly bars its ten years pile up on the single bar for 1920, where in
truth a decade lies. The same mistake the interval data model exists for
([point 1](#1-historic-photos-are-scans--that-shapes-the-whole-data-model)), only in the display: it
does not look like a mistake, it looks like a finding.

**Second: wide enough that the span fits into thirty bars.** The choice is 1, 5, 10, 25 or 50 years,
so the labels stay readable.

**Height scales with the square root, not linearly.** Linearly a small year all but disappears next
to a large one, and a floor then clamped it to the same stub a decade with a single photo got. With
the square root it stays clearly smaller and clearly present. An **empty** bar stays at zero: a stub
there would send the visitor to a place where nothing is.

**The width belongs to the collection, not to the extent**, exactly like the axis. Otherwise the
meaning of a bar would change when the map is panned.

**The axis reaches past the last year.** The bar for the most recent year needs its own stretch of
track; otherwise it would start at the right edge and run beyond it.

---

## 26. Two ways into the admin view, and neither is the coat of arms any more

*Continues [point 7](#7-the-way-into-the-admin-view-is-visible-the-pin-protects-it), which had
settled on exactly one way.*

| Where | To what |
|---|---|
| The title in the header | into the admin view |
| A pencil beside the title in the detail view | straight into editing **this** photo |

**The coat of arms loses that job** and gets another: a tap on it reloads and resets the filters.

**Point 7 is not weakened by this.** What was decided there was not „exactly one way" but **„visible
instead of hidden"**. Both new ways are visible and protected by the same PIN.

**Why the second way.** Somebody who sees a wrongly captioned photo at the device had to search for
it in the admin view — and what they search by is precisely the title that is wrong.

**Why the coat of arms gets the reset and not a button of its own.** The visitor screen had no way
back to the initial state; there were only detours — wait five minutes, enter the PIN and leave
again, or pull the plug. An *additional* button would be one almost nobody needs and somebody
presses anyway, and it throws away work somebody just started. The coat of arms costs no extra
space and is already known to be tappable.

**The identifier below the credit.** At the bottom of the detail view, small and grey, stand the
**first eight characters of the SHA-256**. They are the identity of the photo independent of any
database: a rebuilt collection issues new running numbers, the same scan keeps its hash. Eight hex
characters are short enough to copy down and unique enough for a museum collection — the same length
git uses for the same reason. **The admin search finds them**, and that is the condition under which
they may stand there.

**The price:** somebody who taps the coat of arms wanting the admin view resets the display instead.
For one or two volunteers a year that is bearable.

---

## 27. The map tap is armed only on request

While „Wo ist das?" was on screen the whole map was armed: every tap on open space set a point. Now
the visitor has to ask for it through the button **„Auf der Karte zeigen"**.

**The reason is data quality.** Somebody who only wants to look during the question answered it by
accident — a tap beside the spot, a confirming tap after it, and the collection held a location
nobody meant.

**There is only ever one way on screen.** Arming the map removes the street picker. Side by side
they got in each other's way: the button grid discards on the next touch what the map tap just set.
The button therefore stands **above** the picker — it is the alternative *to* it, and below it would
read as a last resort.

**It is offered at every step, including the house number**, and there it earns the most: whoever
knows the street but not the number points at the house instead of pressing „Reicht so".

**Two things stay armed regardless.** The point that has been set is always drawn and can always be
dragged, no matter who set it. In the code these are therefore two conditions and not one (`armed`
and `active`).

**Without a place index there is no second option** — then the map is armed from the start, or the
panel would be unusable. That affects an installation that never ran `make places`.

**The switch lives in the store, not in the component.** `LocationTask` is torn down on almost every
photo change, so a `useState` would reset by itself — except on the one path where the question
falls back to the original one because the other has run dry. That would leave an armed map over a
photo the visitor has not yet looked at.

---

## 28. Photos without a year are a switch, not a side effect

A photo without a date overlaps no time range. It therefore dropped out of **every** selection as
soon as the visitor narrowed the slider even slightly — with this collection two thirds of it,
without anything saying that this would happen. Now a switch stands beside the slider: **„… Fotos
ohne Jahr anzeigen"**, ticked, with the count in it.

**The number was there anyway.** It was a message; now it is the label of an action. No control is
added, an existing one gains a purpose.

**Switched on it means „no date OR overlap".** The time range then no longer applies to everything
on screen. That is a real loss of precision, and it is acceptable because the visitor sees it and
set it themselves.

**It starts on and goes off by itself exactly once** — at the first narrowing of the time range,
which is the moment the selection starts to mean something. The initial state shows everything the
museum has, and nobody loses anything without having done it.

**After that the switch belongs to the visitor.** Whoever turns it back on by hand keeps it on. If
it went off every time, the automation would overwrite a decision somebody just made.

**What the automation keys on is `queryTimeFilter`** — the same function that decides whether a time
filter goes to the backend at all. The switch therefore goes off exactly where photos would
otherwise start disappearing. A second rule for it would have been a second truth.

**The histogram always counts the undated photos.** Otherwise a zero would stand there after
switching off, the label would disappear — and with it the only way back.

The switch is a button with a drawn box, not an `input[type=checkbox]`: that is too small for the
48 px minimum that applies to this audience.

---

## 29. The address stands under the thumbnail, not the date

**Superseded by [point 39](#39-one-caption-for-the-eye-and-for-the-screen-reader)**, which moved the
caption to the title and took over the rules that still hold. The number stays for older citations.

The reason for the reversal has fallen away, not been refuted: this point rested on a collection in
which most titles repeated the address beside them and a good number carried the name of the scanner
software. That has been cleaned up.

---

## 30. Four roles, and each one looks like a button

| Role | Shape | Symbol | Examples |
|---|---|---|---|
| **choose** | white with a border | — | letter, street, decade, year, house number, „Auf der Karte zeigen" |
| **commit** | filled, accent brown | check | „Hier war das", „Ganze 1920er Jahre", „Reicht so — die Straße genügt" |
| **back** | white with a border, grey text | left arrow | „Anderer Buchstabe", „Doch nicht — von vorn" |
| **skip** | like back, separated by a line | right arrow | „Weiß ich nicht — nächstes Foto" |

**The borderless shape is gone.** It was grey, without a border, and read as text — for an audience
that stands in front of this device once a year, exactly wrong. A button is quieter through its text
colour now, not through its shape; border and height are the same for all and keep the minimum size
for a finger.

**The most important boundary ran in the wrong place.** The same quiet shape carried *going back*
and *skipping* — one stays with the photo, the other puts it away. What stands above the line
belongs to the question, what stands below it to the photo.

**„Reicht so — die Straße genügt" is an answer and has looked like one since.** Not every house is
in OpenStreetMap, and somebody who does not know the number should be able to say so without
hesitating. No competition arises: in this step there is no second filled button on screen.

**Symbols beside the label, never in its place.** A pictogram alone demands knowledge that older
visitors need not bring. The set is therefore small — check, left arrow, right arrow, crosshair —
and everything else carries none. **Drawn, not loaded** (`kiosk/icons.tsx`): the device is offline,
and a symbol that fails to load leaves a button that says nothing.

**The admin view stays explicitly outside this.** It has its own measurements, is used once or twice
a year and follows a different rule: there, plain wording matters more than compactness.

---

## 31. The header sits on a centre line, the time range on a floor

Coat of arms, title and time slider are centred vertically. They used to be aligned at the top and
ended visibly apart, while a comment in the CSS calculated that they were the same height. That held
for one screen width, and until the slider grew.

**Three calculations that can drift apart are replaced by one shared centre line:**
`align-items: center` in the title cell, `justify-content: center` in the slider cell. Both cells of
the grid row are the same height anyway, so the row sits centred without either side having to know
the other's height.

**The time range cannot be squeezed below one decade.** The selected range is also the surface you
drag it along the axis by; squeezed onto one bar there would be nothing to grab. It used to carry a
drawn grip in the middle for that — a mark for a state nobody wants to reach. The grip is gone, the
floor is there: `minSpan()` in `kiosk/timeAxis.ts`, one decade, but never narrower than one bar.

**The moving end stops, the other is never pushed along.** Pushing it along sounds smoother and is
the trap: a pull on the left end would carry the right one past the end of the axis, where it would
be clamped — and the range would come back narrower than it went in.

---

## 32. Refining goes through its own endpoint, not through a loosened check

The first exception to [point 5](#5-visitor-contributions-go-in-directly--with-a-complete-log), and
it is built so that it **does not touch** the sentence there.

**The case.** A photo that only knows its street lies at the street's midpoint — on a long street
several hundred metres from the house. It counts as located and is therefore never offered again.
But refining means replacing an entry that exists, and that is exactly what point 5 forbids.

**The decision: do not loosen `_require_empty`, but add an endpoint that accepts no coordinate.**

```
POST /api/contribute/{photo_id}/housenumber   { place_id, session_id }
```

The server looks `place_id` up in the place index, checks `kind == "adresse"` and that the address
belongs to the photo's street, and writes coordinate, `place_name` and accuracy **from the place
index row**. The visitor picks from a set the server put together.

**Why everything hangs on that.** `POST /location` accepts `accuracy_m` from the client. Today that
is a harmless claim, *because* the field has to be empty anyway. If accuracy decided whether
overwriting is allowed, it would become a key — and the client would hold it: a call with
`accuracy_m: 1` could replace any entry in the collection. The rule „more precise may replace less
precise, never the other way round" is right; it is only nothing to let the party who benefits
assess.

**Who gets asked** is decided by `services/needs.py`: a photo on the map, not yet house-precise,
with a `place_name` **without a digit** — if the number is already in the name, only the coordinate
is missing, and that is machine work — and the place index has to hold addresses for that street at
all. Nearly a third of the streets in the index have none; without this condition the question would
stand on screen with not a single button under it. **Where the coordinate came from explicitly does
not count**; why that was different at first is in
[point 45](#45-where-a-coordinate-comes-from-says-nothing-about-how-precise-it-is).

**Curator entries are explicitly included**, so visitor work overwrites curator work here. What
carries that is the reversal: `Change` has a column `old_source`, and „taking back" here means
**resetting to the street midpoint** together with the old source, not deleting. Without that column
a reversal would turn curator knowledge into a visitor contribution. **Older place entries can only
be taken back once the newer ones have been**, otherwise a reversal would resurrect a place that was
long since replaced.

**What would hollow this reasoning out**, without any single change looking wrong: accepting
coordinates from the client; introducing further accuracy levels and generalising the rule onto
them; loosening the check `place.street == photo.place_name`. Each on its own would be a
convenience; together they would be the end of point 5.

---

## 33. Stacks are not scattered, zoom-level changes are animated

**The markers fade in when the grouping flips.** `draw()` queries supercluster at the **rounded**
zoom level; while swiping the zoom runs continuously, but the grouping only changes when the
rounding flips — and then all markers at once. What is animated is therefore the change, not a finer
query: querying finer means drawing more often, and that costs more on the Pi than it looks like on
a Mac.

**Drawing happens on `moveend`**, and only when the set of groups has actually changed. Before,
`draw()` hung on `move` *and* `zoom`; both fire together and dozens of times per zoom level. None of
it was necessary, because MapLibre keeps the markers on their coordinates itself.

**And stacks are not scattered.** Pulling them apart is the obvious remedy and the wrong one: **a
scattered position pretends to a precision that does not exist.** A stack lies on one point because
all its photos know only the address; pulled apart they would look like just as many different
places.

Scattering and refining are two answers to the same question, and only one produces data. Refining
([point 32](#32-refining-goes-through-its-own-endpoint-not-through-a-loosened-check)) keeps the
imprecision **visible**, so that somebody fixes it.

---

## 34. The archive folder beats the EXIF coordinate — as soon as it names a house number

Until then the rule was: a coordinate from the file always beats the folder. The reasoning read as
*measurement against opinion* — the camera really did stand there, the folder is somebody's filing.

**Measured against the collection it is no measurement.** **Two thirds of the EXIF-located photos
share their coordinate with another photo**, and single points carry shots from several different
years. No receiver delivers six identical decimal places on four different days — these values were
typed in. So it is one filing against another, and only one of them is anchored to the place index.

**That is why the folder address wins — but only the address.** The street midpoint does not win: at
150 m it is coarser than the point it would replace. A photo whose folder names no house number
keeps its EXIF point. That boundary is the actual rule, and it has a test of its own.

**What would hollow this decision out:** a later source that delivers coordinates without anybody
checking whether they were measured or typed in. The reasoning rests on a measurement, not on a
ranking of sources — whoever cites it without counting cites it wrongly.

---

## 35. The house number is asked before the year, and that is arithmetic

The order in `NEEDS` (`services/needs.py`) is the ranking, and a question is only reached when the
one before it is **empty**. It used to read `location, date, housenumber` — right by instinct, since
a year is worth more than a house number.

**Measured against the collection the instinct is wrong.** Almost all photos are located, two thirds
are undated, and a few dozen are waiting to be refined. The year question never runs dry, so the
third question would never have been reached. Refining, by contrast, runs dry after a few dozen
answers, and after that the year question has the panel to itself.

**How subordinate a question is does not follow from its value, but from whether the one before it
ever ends.**

**One exception to the ranking:** whoever pressed „Reicht so — die Straße genügt" is not asked for
the house number in the same breath. The question would already have been answered.

---

## 36. Archive internals belong in the provenance, photo backs in the description

Archives deliver transcribed backs of prints and index cards as tags. They fall into two kinds, and
one belongs in front of visitors, the other does not.

**Content goes into the description.** „Notiz: Grundsteinlegung der Turnhalle ca. 1968" is a
statement about the image. As a tag it is useless — it hangs on exactly one photo. **The prefix
„Notiz:" stays**: it is the source attribution. The sentence comes from the back of the print, not
from a curator who looked at the image.

**Shelf marks go to the provenance.** „Notiz: P 11" is an archive signature. It should be kept —
whoever wants to find a photo on the shelf needs it — but it does **not** belong in the description,
because that appears under the image in the kiosk. `provenance` is the field for it, and
`PhotoDetail` has none
([point 19](#19-credit-and-provenance-are-two-fields-because-they-have-two-readers)).

**The rule that follows:** an entry that helps the museum *administer* belongs in the provenance. An
entry that says something about the *image* belongs in the description.

---

## 37. A year in the text does not date the photo, sometimes only the house

Undated photos often carry a year in the title, description or a tag. Evaluating it is the obvious
move and would be wrong:

| the text says | a rule reads | but it is |
|---|---|---|
| `Notiz: P 37` | 1937 | a shelf mark |
| `Friedhofsweg 30` | 1930 | a house number |
| „erbaut 1972, verkauft 2000" | 1972 | neither |
| „**vor** 1978" | 1978 | an upper bound |
| „in den 70er Jahren **abgerissen**" | 1970s | the photo is **older** |

Two rules follow:

**Two-digit short forms are not evaluated.** „78" for 1978 is common in the collection and cannot be
told apart from shelf marks and house numbers. The photos that hang on those stay undated.

**What is searched for is the positive pattern, not the negative one.** Not „a year without a
warning word", but „a year preceded by *um*, *ca.*, *im Jahre*, *Herbst*, *Dezember* or *aus den*".
A list of warning words is never finished.

**What is taken over is reviewed one by one and kept as a list, not as a rule.** The reason is an
asymmetry: a rejected suggestion costs nothing — the photo stays undated and keeps being asked
about. An accepted wrong suggestion makes the photo **dated**: it drops out of the question, sits at
the wrong place on the timeline, and nobody ever looks at it again. The same asymmetry already
carries the EXIF rule.

---

## 38. The detail view does not ask itself, it branches into the contribution panel

The detail view holds up to three buttons, each at the line it changes; a tap closes the view and
puts this photo into the panel at that question. The kiosk therefore has **one answering path
instead of two**.

Two reasons spoke against the embedded pickers it had before:

**The text column filled up.** A photo without a year and without a house number carried dozens of
buttons under the description — the decades alone are as many as the timeline has decades.

**The place question could never be asked there.** It needs the map, and the map lies under the
overlay. Of the three questions the detail view could only do two, and not the most valuable one.

**Closing is not a side effect but half the intent:** for „Wo ist das?" the map has to become free,
and doing it differently per question would be a rule nobody can see.

**Nothing special happens afterwards**, and that is the actual decision: thank-you, then the next
open question for this photo, then a new one. A way back into the detail view would need a special
case in the store and would drop the chain.

**The wish is a request, not an instruction.** `GET /contribute/next?photo_id=…` checks the photo
against the same condition as any other and falls back to the random pick where it no longer holds.
Otherwise a question would stand on screen that was already answered between the tap and the load —
and the write path would reject the answer with 409.

---

## 39. One caption for the eye and for the screen reader

*Supersedes [point 29](#29-the-address-stands-under-the-thumbnail-not-the-date).*

Under the thumbnail stood the **address**, in the `aria-label` of the same button the **title**. Two
wordings of the same thing, in two places in the code, which said the same as long as the titles
were addresses. **The mistake was not the wrong line but that there were two.** Correcting both
would have postponed it: two wordings drift apart again as soon as somebody touches one. There is
one now (`kiosk/mapCaption.ts`), and both senses read it.

**The chain is title, then address, then nothing**, with the year where it is known.

**„Hauptstraße Nr. ?" instead of just „Hauptstraße"** where the house number is missing. That is not
a stopgap but the same stance as not scattering the stacks
([point 33](#33-stacks-are-not-scattered-zoom-level-changes-are-animated)): the imprecision should
stay **visible**, so that somebody fixes it. It is exactly the gap the contribution panel asks about
under „Welche Hausnummer?".

**A stack shows only what all its photos agree on.** Photos land on one marker because they share a
coordinate, and that means the same address. Their years and their titles are not shared; taking the
topmost would write one title over dozens of images that show something else. A stack therefore
usually falls back to the address.

**If both are missing, the line disappears** — no dash, no „unknown". An empty spot under an image
demands nothing of the visitor.

**The short date form belongs in the backend**, beside `format_label`: it shortens day and month to
the year and leaves a decade a decade („1930er" does not become „1930", which would invent
precision). `PhotoMarker` carries the `place_name` for this — the one deliberate exception to its
rule of carrying as little as possible.

**What is explicitly *not* written:** a title for the photos whose title would only be their
address. It would stand a second time in the same line, go stale at the first refinement, and it
would take the basis away from curating: afterwards every photo would have a title, and which ones
need a **real** one could no longer be told.

---

## 40. A symlink is never a drive

The search for backup targets (`services/backup/drives.py`) **skips symlinks**, on both levels it
searches.

The reason is a quirk of `os.path.ismount`: for a symlink it answers **`False` on principle**. A
symlink under `/media` therefore looks like an ordinary folder, and the search descends one level.
That descent is wanted, because Raspberry Pi OS mounts under `/media/<user>/<label>` — but
`iterdir()` follows the symlink while doing so, and whatever lies behind it is offered as a backup
target.

**The consequence is the worst one in the system:** a backup that runs through completely and lands
in the data directory it is backing up. That is exactly what the mount check protects against, and
the symlink gets around it. On a Mac the case occurs reliably, because macOS always puts a symlink
to `/` into `/Volumes`; on a Pi it is unlikely but possible.

**The same trap was set once more for the test.** `_is_mounted` compares paths, and compared
literally a path behind the symlink is a different one — so the test was green even without the
safeguard. It compares resolved paths now. **A counter-check that does not trigger is a result, not
a formality.**

---

## 41. The name says the thing, not the place

The project is called **Kiekmap** — Low German *kieken*, to look. Capital K outside, lower case in
source and paths, `KIEKMAP_` as the prefix of the settings.

**A name for the first place would have been the worse one**, for the same reason nothing
place-specific belongs in the code: the second museum should need its own `region.json` and `.env`,
not a fork. A place name in the package name would have contradicted that promise long before
anybody broke it technically.

The rename happened while no Pi was in the field and there was no git remote. After that, devices,
backups on sticks and other people's working copies would have had to follow.

---

## 42. The restore brings the schema up to date itself

A restored backup is migrated, by the restore itself (`services/schema.py`). A restart is not
needed for it.

**The reason.** A backup brings its schema with it; the file is swapped as a whole, and the running
program just attaches to it again. Migrations run at *startup*, and a restore is not a startup.
Without the catch-up the device looks completely normal afterwards and **accepts nothing any more**:
every visitor contribution, every edit, every upload ends in HTTP 500. The remedy stood in both
manuals — restart once — and **an instruction to people is the weakest place a promise can have.**

**The order is the whole point**, and it has two halves on either side of the swap:

1. **Rejection happens before.** If the backup carries a revision this program does not know, the
   restore aborts **before** anything is replaced. Migrating would be no option here: the
   corresponding migrations do not exist in this program at all.
2. **Migration happens after.** Only after the swap is the restored file the one at the configured
   path.

**Phrased as „do we know this revision?", not as „is it newer?".** A revision that cannot be placed
is one you must not touch — whether it comes from a newer program, from another branch, or from a
file that is not ours at all.

**One special case stays open deliberately:** a database without `alembic_version` is not migrated
but left alone. Without the stamp there is no telling what the file is, and Alembic would start its
first migration against tables that already exist. In the museum that cannot happen; in the test
environment it can, and there migrating would be wrong.

**`test_migrationen_und_modelle_beschreiben_dasselbe_schema`** builds the schema once through
Alembic and once through `create_all` and compares them. The other tests build it from the models
and therefore cannot notice a missing migration at all.

---

## 43. The header measures itself against its column, not the viewport

Coat of arms and title take their size from the width of the cell they stand in
(`container-type: inline-size` and `cqi`), not from a media query. The place name is additionally
told its **length**, because CSS cannot measure text.

**Two causes, and the second was the harder one.** The first is a pitfall you have to know once:
**in a media query `rem` is always 16 px** — the root element's font size *before* a rule of your
own changes it. The threshold therefore sat somewhere other than intended. The second: **the design
had almost no slack.** Even above the threshold the line only just fitted, and at one particular
window size Safari wrapped and Chromium did not. Correcting the threshold would only have moved the
bug. **A line that fits only after measuring does not fit.**

**The rule from that:** whoever sets a size in the header relates it to the space that is there, and
leaves slack. A threshold in the viewport is always a place where two calculations can drift apart.

**The promise is deliberately bounded.** The place name is set smaller the longer it is, but **never
smaller than the line above it** — otherwise the hierarchy would stand on its head. Where that floor
takes effect, the name wraps. From what name length that happens is in [adaption.md](adaption.md),
because it concerns the next municipality and not this one.

---

## 44. The paging buttons stand still, the image moves

In the detail view the paging buttons are **anchored vertically at the bottom edge** and sit
**horizontally centred under the image**. The image sits above and changes its height, the buttons
do not.

**Before, they stuck to the image and travelled with it.** Between a landscape and a portrait format
the button moved by more than its own height. Whoever pages through a stack with mixed formats has
to look for it again at every image; in the worst case the next tap lands on the image where
„Nächstes" just was.

**Horizontally they stay with the image**, and that is the other direction of the same question:
they belong to what they change. Centred in the screen they would sit far beside a portrait image.

**The rule behind it:** what the visitor *hits* stands still; what they *look at* may move.

**The close button follows the same rule** and sits in the corner of the screen instead of at the
right edge of the content. It gets **none** of the four roles from
[point 30](#30-four-roles-and-each-one-looks-like-a-button): those are the language of the
contribution panel, and closing is not one of them.

---

## 45. Where a coordinate comes from says nothing about how precise it is

Whether a photo is offered for refining is decided by **what is known about the house** — not by
which source its coordinate came from.

**Before, the opposite stood there.** The condition demanded `location_accuracy_m ==
ACCURACY_STREET_M`, admitting only what a curator had put on a street. The reasoning sounds
plausible: „the device knows where the photographer stood, not what they photographed." **The
sentence had been refuted**
([point 34](#34-the-archive-folder-beats-the-exif-coordinate--as-soon-as-it-names-a-house-number)):
most EXIF coordinates are typed-in values. A whole group of photos stayed out of the question,
although they are exactly its case.

**What was reported was something else**, and that is worth writing down: the button was missing
*as soon as the year was known*. The observation was right, the explanation was not — among the
photos with a bare street name, those with a year are predominantly the EXIF ones, and those were
what the condition excluded. **A reported observation is a finding, its explanation is a
conjecture.**

**What follows for similar rules:** a condition that decides on the *origin* of a value instead of
its *content* carries an assumption that can go stale without the rule noticing. Where possible, ask
what is known — not who entered it.

---

## 46. The collection is JPEG, and the recipe for it is fixed

A museum archive is mixed: scans as TIFF, screenshots as PNG, an image from a web page as WEBP. The
collection holds only JPEG, because **a browser does not display TIFF** and the detail view hands
out the original file.

**The setting is measured, not chosen:** **Pillow, quality 92, subsampling 4:4:4, `optimize`** — the
quantisation tables of the initial collection, which arrived already converted. One step beside
that and not a single file matches any more.

**This is the precondition for duplicate detection.** The import recognises a duplicate by the
SHA-256. The same recipe twice over the same file gives the same hash; a different quality gives a
different one, and with the next archive delivery every existing image would come in a second time.
That is why the setting is a constant in `tools/to_jpeg.py` and has a test of its own.

---

## 47. A diff over bytes is not a diff over images

An archive delivery described as a delta contained, to more than a third, images that were already
in the collection. The reason: the museum had run its collection through **ExifTool** and rewritten
the metadata blocks. **The same pixels, different bytes.**

**The rule from that:** a data set compared over bytes says nothing about what *is* new — only about
what was newly *written*. Before importing a delivered delta, the image content is therefore counted
again, in two passes: exact pixel comparison first where the edge lengths match, then a coarse pass
over downscaled greyscale images for whatever also changed size on re-export.

**The gap between match and non-match was not a judgement call**, and that is why a threshold is
defensible here: almost all matches sat at a deviation of exactly zero, the highest just above it —
and the nearest non-match more than an order of magnitude away.

---

## 48. What stands in the title field is not automatically a title

In the detail view the title stands **above** the address, not in its place. A photo called
„Hauptstraße 14, Museum" that carries „Hauptstraße 14" below it again spends a line for nothing —
and the line above is the most prominent one in the whole view.

Three rules in the import instead of another cleanup by hand:

**The folder title is the suffix.** „14 Gasthof Petersen" gives the title „Gasthof Petersen", the
address goes into `place_name`. If the folder names only a number, the title stays **empty**.

**The length limit is measured, not chosen.** Of the titles the museum set by hand, **not one
exceeds 58 characters**. `TITLE_MAX` therefore stands at **60**, and what is longer moves into the
description instead of being thrown away.

**The name of the scanner software belongs in no field.** Unlike an overlong caption it must **not**
fall back to the description: that would push the same nonsense one line lower, where it would stand
under the image in the kiosk.

**The lesson is why the rules were needed at all.** A cleanup by hand tidies the collection and
leaves the cause in place. As long as the cause sits in the import, the next delivery is the next
cleanup.

---

## 49. A date word says that it is a date — not what of

*Extends [point 37](#37-a-year-in-the-text-does-not-date-the-photo-sometimes-only-the-house).*

Point 37 requires a date word before the year. **The pattern alone is not enough:**

```
ca. 1970 wurde dieses Haus abgerissen und durch ein Mehrfamilienhaus ersetzt
```

The date word stands before it, cleanly. Only the year dates the **demolition** — and the photo
necessarily predates it.

**Both lists are needed, and they do different things.** The date word before says *that* a number is
a date. An event word after — *abgerissen*, *erbaut*, *abgebrannt*, *verkauft* — says *what of*. The
objection from point 37 still holds but applies to one direction only: **a list that only rejects
may be incomplete.** It then lets a case through that a human still sees afterwards; a list that
*accepts* something turns a gap into a wrong entry.

---

## 50. Who lent it and where it lay are two answers

The provenance names both side by side, separated by a comma. Before, `apply_folder_meta` filled the
field only when it was empty — so the archive path was missing everywhere the file itself already
said something.

**That is exactly the wrong way round.** Who lent a photo is in the file and thereby safe. **Where
it lay in the archive is only in the path** — and the path is lost on import, because in the
collection the file is named after its SHA-256. It is the only one of the two entries that can never
be recovered from the image.

The field stays what it was: **not public**.

---

## 51. A field that ends at its limit is truncated

One credit read „Förderkreis für Kultur und Brauc". That looks like a typo and is not one: **the
string is exactly 32 characters long**, and 32 is the length limit of IPTC field 2:80. The program
that captioned the file stopped at its field boundary, and we took it over unexamined.

**An entry whose length falls on a round number is suspicious**, and the case costs nothing to
check: a glance at the character length of the most frequent values of a text field shows it at once.

---

## 52. A default is not a finding

The conversion to JPEG passed through only the colour profile and the resolution for a long time.
Photos lost what their file said about them in the process — and afterwards carried the collection's
default credit where a photographer's name should have stood.

The path there is one line in the import:

```python
credit=info.credit or settings.import_credit or None
```

The default from the `.env` steps in when the file says nothing, and that is right. It went wrong
because the file did say something and we had lost it on the way. **The loss was therefore not
visible**: the field was filled, it looked like information, and a wrong attribution is worse than a
missing one.

**Two rules follow.** Where a field carries exactly the default value and the file says something
else, the file wins: a default is a fallback, not a statement.

And for everything that carries data from A to B: **what is lost on the way only shows up where a
gap is left behind.** Where a default fills the gap, the loss becomes a claim. The test for it is
not „did the bytes come along" but „does our own reader read the same from the copy as from the
source".

---

## 53. The archive's XMP is not read — measured, not assumed

`services/exif.py` reads EXIF and IPTC, no XMP. That stood as a backlog item with a tempting
prospect: a large part of the archive files carries a place entry in `Iptc4xmpCore:Location`.

**Measurement came before building**, across the whole archive. The result inverts the expectation:

| Field | what is really in it |
|---|---|
| `dc:creator` | „unbekannt", „Winter" — no photographer |
| `dc:description` | „Gebäude", „Abriss & Neubau" — **categories, not descriptions** |
| `Iptc4xmpCore:Location` | almost always exactly what the folder already says |
| `photoshop:Location` | often contradicting the first, usually a batch value left standing |

The yield from the strongest field is a few dozen photos, and a third of those carry the same value.
Rebuilding the reader, deciding between two contradictory place fields and a review path for
hundreds of conflicts — for a handful of house numbers a human would have to look at anyway. **That
does not pay off.**

**Measure first, then build** also means that the measurement finds something other than what was
sought: it found a folder that repeats its street (`Hörnstraße/Hörnstraße 14`) and thereby produced
the same duplicated address that point 48 had just abolished.

---

## 54. The machine finds duplicates, a human has to decide

The SHA-256 recognises a copy of the *file*. It does not recognise the same paper print scanned
twice. That is found with a **difference hash over 256 bits** on the existing thumbnails; it
tolerates brightness, colour cast and downscaling.

**The threshold was looked at, not chosen.** Up to a small distance it is unmistakably the same
image, at a larger distance still predominantly. The signal does not break off, it goes fuzzy — so
the default is generous (**40**) and a human decides.

**Fully automatic would be wrong, and the proof stood in the groups:**

- Two photos of the same foundation-stone ceremony sat at **different addresses and in different
  years**. One was filed wrongly; a machine that keeps the larger one would never have raised the
  question.
- In one pair the **smaller** version carries the burnt-in caption. Resolution is the wrong
  criterion there.
- On one of three otherwise identical street pictures there is a lorry. Two moments, not a
  duplicate.

**The scale makes the decision easy.** There were a few dozen groups, not hundreds. A review list of
that length is worked through in a quarter of an hour; an automation that occasionally loses the
better image would never be checked again. That is why `services/similar.py` finds and writes
nothing.

**Merging happens before taking out**, not after: title, description, dating, place, credit, tags
and the archive path move onto the photo that is kept, wherever it is missing something. „Taking
out" means `status = deleted`
([point 16](#16-deleting-means-taken-out-of-the-exhibition-not-removed-from-disk)).

---

## 55. A tag is not a field but a set

All batch values of the import form follow one rule: **they fill only what is empty.** That is right
because each of those fields holds exactly one value — filling would mean deciding.

**For tags it does not hold, and bending the rule would have been the mistake.** A tag list holds no
value but a set. Whoever uploads photos from a folder „Feuerwehr" does not want *either* the batch
tag *or* the file's — they want both.

**There are therefore three sources, and their order is in the code:**

1. `KIEKMAP_IMPORT_TAGS` — applies to every import on this device
2. the keywords from the file itself
3. the batch tag from the form

`add_tags` skips what the photo already carries and creates a name only once. The order therefore
costs nothing.

---

## 56. A decade is a dating — „vor 1978" is not

People do not date only with four-digit years: „80er Jahre", „in den 1930gern", „Winter 63", „Foto
aus der Nachkriegszeit". A decade is not a fuzzy year but a statement of its own; `date_precision`
has `decade` for exactly that.

**„Vor 1978" is not taken over, and the reason lies in the time filter.** It queries for overlap. A
photo whose interval starts at the beginning of the timeline overlaps with *every* position of the
slider and would stand everywhere — worse than undated, because undated at least gets it offered as
a question. **A dating needs both ends; where one would have to be invented, there is none.**

Three patterns came out as cases of their own, all relatives of
[point 49](#49-a-date-word-says-that-it-is-a-date--not-what-of):

- **The year of the archive revision.** „heute (2018) Marc Sieveking", „bis 2018 Besitzer". Such a
  year is almost never the year of the shot but the day somebody tended the archive.
- **The year not written out.** „Notiz: Schule 78" is the same archive note as „Notiz: 1978" and
  slipped through because the search knew the two-digit year only after a season word. **In a search
  for patterns the shape of the pattern determines the finding**, not the collection — whoever
  searches for one spelling measures their own assumption.
- **The scan date in prose.** „Im Januar 2020 eingescannt von einem SW-Abzug." The same trap as the
  EXIF date of a scan, only in a text field instead of a tag — and without the year limit that
  catches it there.

---

## 57. The kiosk heals itself — but only once

An error while rendering tears down the whole tree in React, and a white page is left. At a desk you
press reload; in the museum there is nothing to press. The idle restart, which otherwise heals every
stuck state, sits in `MapView` and goes down with it.

So the page reloads itself. The only question was: **how often.**

**Exactly once, then the device speaks.** A crash that returns on load would otherwise make the
screen flicker endlessly — worse than a message somebody can read. The note about the last attempt
lives in `sessionStorage`: it survives the reload and dies with the tab, so on the Pi at the latest
with the morning restart.

**A clock that jumped backwards counts as „long ago".** The Pi has no real-time clock; after a power
cut its clock can be years off. Counting strictly forward would switch the self-healing off
permanently — exactly the state it is supposed to prevent.

**And the timer is not cleaned up.** The tidy version had a `componentWillUnmount` that clears it,
and with that the whole thing did nothing: after catching, React rebuilds the tree from scratch and
takes the error boundary with it. **The cleanup reflex is right for a timer that belongs to a view;
it is wrong for one that belongs to the device.**

---

## 58. Stored as UTC, written out with a marker, read as wall-clock time

Everything this program stores is UTC. Until now the rule ended at the database.

**Without a zone marker a timestamp is not information but a trap.**
`new Date("2026-08-18T19:25:21")` reads a marker-less ISO time as **local time**, by the standard.
The admin view therefore showed every visitor contribution and every log line off by the zone
offset, and the backup tile could shift the day.

**The marker belongs at the end that knows the zone.** Letting three display sites in the browser
convert would mean writing the same rule three times — and the fourth, which somebody adds later,
forgets it. A `UtcDatetime` in `schemas.py` says it once.

**The `exif_datetime` explicitly does not get one**, and that is where the real distinction lies. It
comes from a camera or a scanner; those write the wall clock of their location and know no zone.
Stamping UTC onto it shifts a scan by two hours and thereby invents a fact. **A timestamp carries
not only a value but an origin.**

**File names are the exception and carry local time.** The folder `before-…` and the name of the
downloaded archive are read by people in a file manager, not compared by a program. Somebody pulling
a backup at half past midnight is looking for today's date.

---

## 59. A number in prose is a quotation or a record — what gets checked is the bookkeeping

The checks beside the tests only ran when somebody thought of them. Two counted figures in
[index.md](index.md) were wrong for weeks, without consequence and unnoticed by anyone.

The obvious conclusion was to have a check count them. **Measured, that was wrong.** The pattern „N
Punkte" occurs in a handful of places in this documentation, and **not one of them may be
corrected**: several times the old, wrong number stands there deliberately, as a quotation; several
times points on a map are meant; once a sentence in the history is right for its date.

**A number in running text is almost never a claim about the current state.** It is a quotation or a
log entry, and a correction makes both wrong. The two places that really were meant to be current
therefore **lost** their numbers instead of getting a check.

**A number that something else already states does not get written at all.** Four files said this
repository has „five checks" and then listed six of them; the count in front of the list said
nothing a reader could not see, and it went stale the moment a sixth check arrived. Where the list
is right there, the list counts itself.

**What can be checked is the backlog's bookkeeping about itself.** That is not prose but structure,
and it makes a promise that either holds or does not: every number ever issued is either open or
retired — no gap, no surplus, none twice. `tools/check_numbers.py` verifies it.

**And a place where the checks run.** `make check` bundles style, the checks and the tests, fastest
first. The hook under `.githooks/pre-commit` runs **only** the checks and no test suite: the tests
run anyway, the checks are what gets forgotten, and together they take under a second. A hook you
notice gets switched off. It is enabled once per clone — versioned, but not forced on anybody.

`.github/workflows/check.yml` runs the same thing on every pull request. It catches what stays
invisible on the development machine: a different Node version, a missing venv, an environment
without the local `.env`.

---

## 60. What can be silently wrong gets tested — what you can see gets rendered

The frontend has **not a single component test**: no jsdom, no Testing Library, no rendering in a
test. It is written down because a review from outside would otherwise rightly ask what is missing.

**The rule is not „components are not tested".** It is: *every decision moves into a pure function
and gets its test there — rendering gets none.* Where the function lives does not matter;
`PhotoLayer.test.ts` checks `buildIndex` from a `.tsx` file without rendering anything.

**The reason is the same as everywhere here: what gets tested is what goes wrong *silently*.** A
wrongly drawn button looks wrong — that takes a glance, not a test. A wrongly rounded year looks
like nothing; the map simply shows something else.

**Where the boundary runs** is shown by the counter-case: the size of a circle on the map is also
computed and still stays in `PhotoLayer.tsx`. A wrong value gives a circle that *looks* wrong there.

**Why no jsdom.** It would be a rebuilt browser, and what got tested would be the rebuild. What can
really go wrong in this program's rendering, jsdom does not check anyway: whether the page requests
zero foreign origins offline, whether a circle under a thumbnail can be hit with a finger, whether a
label stays readable on the device. The first is a one-liner in the developer tools, the last needs
a human in front of the screen.

---

## 61. A package with one entry point — and the tests stay as they were

`services/backup.py` had grown to almost a thousand lines and did six things. Every piece was
justified, and the boundaries were even there already — as comment banners.

**The condition under which the rebuild was worth it: the tests must not change.** Beside it lies
almost as much test code, and it is the only proof that a rearrangement breaks nothing. Whoever
rewrites it along with the code has thrown the proof away and has to take the result on faith.

Hence a **package with one entry point**: `app/services/backup/__init__.py` re-exports exactly the
names the rest of the program uses. Not one import line in `api/`, in `watcher.py` or in the tests
moved; the only changes are the places where `monkeypatch` replaces a private name.

**What the split brought to light:** the restore reset a cache with `global`. That works only as
long as both sit in the same file — the separation turned it into a named function, and thereby a
silent access into a visible action.

**Whoever is needed between modules loses the underscore.** The missing underscore is the
information „somebody else uses this", and the present one stays where it is true.

**The caveat:** the rebuild gains nothing a visitor notices. Whoever is in this position first
checks whether the tests *carry* a rebuild; if they do not, splitting is the second step and not the
first.

---

## 62. Apache-2.0 — because the project is built to be taken over

The choice was free: of the third-party packages **not one is copyleft**, measured against the
installed packages rather than the manifest files. On the table were MIT, BSD-3-Clause, Apache-2.0,
MPL-2.0, EUPL-1.2 and the GPL family.

Three goals decided it — others should be able to use it, contribution should be possible, the name
should travel with it — and one reservation: concern about legal disputes.

**§4.2 was decisive.** This project is built explicitly so that a second museum can take it over.
Apache requires that **changed files are marked as changed**. A takeover that goes wrong therefore
stays visibly a takeover and not „Kiekmap". MIT does not give that.

**§5 settles the contribution question before it arises.** Contributions are under the same licence
without a further agreement. If they do not come, it cost nothing.

**§4.1 and §4.4** require a copyright notice *and* a NOTICE file with every distribution. A
permissive licence gives no more attribution than that.

**What did not decide it, although it looks as if it did:** the more detailed disclaimer in §§7–8.
It reads more reassuringly than MIT's two sentences but achieves little more in Germany — § 276
Abs. 3 BGB and the law on standard terms limit both alike. What keeps the risk small is that it is
free of charge, not the clause. The patent grant in §3 is moot here; its value is in not having the
question at all.

**Rejected:** **MIT** lacks exactly the three sections above. **BSD-3-Clause** protects the name only
against advertising, not against confusion. **MPL-2.0** and **EUPL-1.2** would be defensible; the
EUPL is so unknown internationally that it deters more than it attracts, and the goal was
distribution, not reciprocity. **GPL/AGPL** make exactly what is wanted here harder for an
institution.

**One licence for everything**, code and documentation alike. Separating them would be more precise
— code licences talk about „the Software" and about patents, which sits badly on prose — but it
grants nobody more rights: a permissive licence over the whole repository already allows copying and
adapting the documentation.

**What the decision explicitly does not touch: the photo collection.** A software licence licenses
the program, not the data. That, together with the ODbL question, is in
[licensing.md](licensing.md).

---

## 63. The history is not split but indexed — by its date

*Extended by [point 68](#68-the-language-boundary-follows-the-audience-not-the-file-type): the file
has been closed since 30 August 2026. It still was not split; it just no longer grows.*

The question was whether `history.de.md` should be split — by year, by topic — or whether a file nobody
reads from the front may be long.

**Measured, the length was not the problem.** Around ninety sections of medium length, all in an
order that is never rearranged. Splitting by topic would destroy the one thing this file has over
the others: **the order.** And it would bring a question along with every append that does not exist
today — *into which file?* — whose wrong answer nobody notices.

**The problem was a different one, and it was measurable:** of the references from other files to
`history.de.md`, **almost none pointed at an anchor**, so each pointed at the whole file. A reference
that narrows nothing is hardly a reference.

**So indexed instead of split:** a register at the top, one row per section with date and anchor.
**The date is the way in, not the title** — people look for a day, rarely for a heading; for a
keyword `grep` is the better tool.

**That makes a promise, and the promise has a check:** *every section states its date in the first
lines below its heading.* `tools/build_register.py` generates the register and **aborts** when a
section names no date: a register that silently omits a section is worse than none.

**One rule about dates, without exception:** a section inherits the date of its part, and a part that
names none passes none on.

**Rejected: taking the date from git.** It would be a measurement instead of a claim, but it
measures the wrong thing. Git dates the writing, not the work, and a rewritten history shifts every
date at once.

---

## 64. The umlaut rule applies to the documentation — and is now checked

The language rule says: umlauts are written out in texts for people and transcribed only in source
code. The documentation did not follow it, and the question was whether the rule should follow the
practice.

**No — measured, it was not the practice but two files.** Almost all documents keep the rule
flawlessly; the drift sat in `decisions.md` and `history.de.md`, and in the history not even evenly but
in one stretch of work where the rule for source code spilled over onto the documentation. **A rule
that eleven files carry is not given up because of two.** The same holds for `ß`: the rule allows
`ss` explicitly, but not *in the same paragraph as its opposite*.

**The real finding: `tools/language_check.py` never checked it**, although
[development.md](development.md) said right under the umlaut paragraph that it did. The tool read
only `.py`, `.ts` and `.tsx`. **A promise nobody verifies is not a rule but an intention.**

**Three things are exempt:** fenced blocks and code spans, because identifiers and commands live
there; and quoted material, because CLAUDE.md carries a transcribed message as its own example of
the rule. The list of forms searched for is deliberately short — it runs in the commit hook, and a
single false alarm is enough for somebody to switch the check off.

---

## 65. The five files of a release, and what is not in them

`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS` and issue templates under
`.github/`. Two decisions in them are not technical ones.

**No address in plain text.** An email address in `SECURITY.md` gets harvested and then stands in
every fork and every archive, even after it is long deleted here. Security reports therefore go
through GitHub's private reporting — the path is not public, goes only to the maintainer, and it
doubles as the one confidential channel the code of conduct needs as well. **The switch for it
exists only on public repositories**; while the repository was private, the reporting path pointed
nowhere.

**No Contributor Covenant, but fifteen lines in the project's own voice.** The Covenant is the
recognised standard, and switching to it is named as the next step in the code of conduct — but
today there is no community here and no second maintainer. A code that describes procedures nobody
carries out is a promise without backing.

**The theme of all five: a release must not become a silent promise.** That is why `CONTRIBUTING.md`
says there is one maintainer on the side and a report can sit for weeks, and `SECURITY.md` carries a
list of what is **not** a finding but a design choice: the visitor view without a login, the
contribution path without rate limiting, the unencrypted collection.

---

## 66. Two branches — `main` says what runs in the museum

On the table was **GitHub Flow**: exactly one long-lived branch, `main` deployable at any time.
**What was chosen is a second long-lived branch**, `develop` for everyday work and `main` for the
state that has shipped.

**The reason is the device, not taste.** GitHub Flow is built for services that ship several times a
day. This device stands offline and is updated once or twice a year from a USB stick; between two
updates lie months of work. A `main` of its own answers a question that really gets asked in the
museum — *what is actually running on the device?* — and it answers it as a branch you can diff
against, instead of as a tag you have to know first.

**No `release/*`, no `hotfix/*`.** With one maintainer that is effort without a return.

**Squash merge is disabled, and that is the actual decision.** `history.de.md` cites **individual
commits by hash**, in dozens of places — a squash destroys exactly those, and it delivers **no**
mapping table with which the citations could be caught up.

**Merging uses a merge commit, not a rebase.** The argument above speaks against squash, not for
rebase. A rebase creates the commits anew; GitHub builds them on the server, where no key is kept,
and they come out **unsigned**. A merge leaves its parents untouched: **signatures stay, hashes
stay, every commit stays visible on its own.** The price is forks in the graph;
`git log --first-parent` hides them.

**The default branch is `develop`**, so that pull requests aim there by themselves. That `main` lags
behind for months is not a flaw but the statement.

---

## 67. One identity in all commits, and all signed

**The finding was an oversight that repeated itself.** `user.name` and `user.email` were set
nowhere. Git therefore built the address from the account and host name of the Mac, and a change of
machine produced a third identity by itself. Two of them are not mailboxes but reveal the account
name and a host name each.

**What was chosen is a project address of its own**, not the personal one and not GitHub's `noreply`
address. The personal one would stand permanently in every clone and every archive; the `noreply`
address contains an account id that does not exist before the account, and it would have tied the
irreversible step to creating one.

**Everything is signed, retroactively as well** — that is unusual, so the trade-off belongs in
writing. The most obvious objection does not hold: an SSH signature has **no timestamp of its own**.
Signing retroactively therefore asserts nothing demonstrably false.

**One price remains and has to be known:** `allowed_signers` supports `valid-after=`, and Git
verifies a signature against the commit date. Whoever ever gives this key a validity window starting
25 August 2026 gets everything before that reported as invalid. Whoever changes the key therefore
keeps the old one listed **without** `valid-after`.

**The timing was the actual decision.** Both cost a rewrite, and a rewrite is free as long as there
is no remote. The day after, clones, forks and archives carry the old version onward.

**What it cost was not the rewrite but the follow-up:** catching up every short hash cited in the
documentation. The first time `git filter-repo` supplied a mapping table; a `git rebase --root
--exec` supplies none. **That is the same arithmetic that speaks against squash merge**
([point 66](#66-two-branches--main-says-what-runs-in-the-museum)).

---

## 68. The language boundary follows the audience, not the file type

German documentation stood next to English identifiers, German tests, German commits and an English
repository description. The mix was not a concept but a leftover: every file got its language when
it was written.

**The rule now reads: every text exists exactly once, in the language of its readers.** Do not
translate, separate. The language map is in [development.md](development.md#language).

**Why not bilingual.** Duplicate content in two languages is the expensive kind of mistake: the
second copy goes stale and nobody notices. With one maintainer on the side that is not a forecast
but a certainty. It is exactly what multilingual wikis fail at, and that was the occasion for the
question.

**Why the museum documentation stays German.** The product is German — interface, CLI, admin view. A
museum that does not speak German cannot run Kiekmap today; `usermanual`, `operations` and
`adaption` therefore have no English audience. English in the developer half does not make the
project international. It makes it readable for the people who read the code.

**Why the tests stay German.** A test name here is a sentence of specification, not an identifier:
`test_scandatum_datiert_das_foto_nicht` says in one line which promise the test protects. On top of
that the domain terms — Flurname, Hausnummer, Ortsteil — have no good English equivalent.

**Why issues are German.** The subject matter is German, and whoever reports here reports from a
German museum. That is written in [CONTRIBUTING](../CONTRIBUTING.md), together with the sentence
that code, commits and developer documentation are English. Unusual, but coherent: the subject is a
German museum, the tool is software.

**No Simplified Technical English.** Checked and rejected: its controlled vocabulary is built for
maintenance instructions and cuts away exactly the nuance these texts carry. Instead, writing rules
apply to both languages — one thought per sentence, active voice, no hedging, no imagery. They are
in [CLAUDE.md](../CLAUDE.md#writing-rules).

**What makes the rule checkable:** `tools/language_check.py` has two prose lists instead of one,
`GERMAN_PROSE` and `ENGLISH_PROSE`. The German half is checked for transcribed umlauts, the English
half for German paragraphs. A file being converted is in neither list — it is half of each, and both
checks would be right to complain. One list with a flag would not do: an English file passes the
umlaut check for the wrong reason, because it has nothing German that could be transcribed.

**Commit messages are English since 30 August 2026.** All earlier ones stay German. Rewriting them
would move every hash the documentation cites — the same arithmetic as in point 66, and this time
without a gain.

**What follows, and what explicitly does not:** `history.de.md` is closed rather than translated, and
nothing takes its place — what the work teaches becomes a decision here, and how it went stays in
the commits and the issues. `decisions.md` is consolidated first and then translated.
No GitHub wiki: `make check` does not reach into a second repository, and `operations.md` describes
`deploy/pi/update.sh` line by line — today a change to both is one commit and one review.

---

## 69. The backlog moves into issues, and the old numbering stays where it is

*Supersedes the last paragraph of [point 22](#22-the-backlog-gets-classified-and-its-numbering-outlives-it).*

Point 22 named the condition for moving: more than one person working on the backlog, or the order
changing more often than the contents. **Neither happened; the reason is a different one.** The
repository is public. Somebody who finds a bug does not send a pull request against a markdown file,
they open an issue — and a backlog that lives in a file puts an outside report beside the work
instead of in it.

**The numbers do not travel with the points.** GitHub shares one counter between issues and pull
requests, and the low numbers were used up by the first pull requests: „Punkt 15" could never become
issue #15. The documentation cites points at over three hundred places, and one of the citing files
is frozen. So the old numbering stays where it is, and
[history.de.md](history.de.md#nummernregister) resolves it: the fourteen open points became issues #15 to
#28, and every other number is described in that file under its date.

**The register stands in the history, not in a file of its own.** That is where the numbers are
cited — 186 of the three hundred citations are in `history.de.md` — and a register in a second file
would be one more thing to keep in step. It sits above the change register, under the note that the
file is closed. New work is named by its issue number alone.

**The kinds and the ranking become labels**, so the list can be filtered the way the file was
ordered. The four areas of the backlog come along as labels as well.

**The labels are English, although the issues are German**, and that is a deliberate exception to
the language map. Three of them are GitHub's own — `bug`, `enhancement` and `question` carry Fehler,
Aufgabe and Frage. Somebody filing an issue from outside reaches for `bug`, and a second German
label beside it would be two truths about the same thing. The rest follow suit rather than mixing
two languages in one list: `idea`, `important`, `urgent`, and `admin`, `visitor`, `infrastructure`
and `development` for the areas.

**The fit is exact only for `bug`.** `enhancement` is narrower than Aufgabe, and `question` means a
request for information where this project means a decision to be taken before the work starts. The
label descriptions therefore carry this project's definitions, not GitHub's.

**The old number is not in the issue title**, it is in its footer. A title should say what the thing
is about; the number only matters to somebody following a citation, and for them the footer names
it.

## 70. No licence header in the source files

*The section „The head of every source file" in [development.md](development.md) is gone with
this point.*

Every source file carried two lines above its docstring:

```python
# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0
```

**They are gone from all 153 files.** The Apache licence never required them. [LICENSE](../LICENSE)
and [NOTICE](../NOTICE) cover every distribution of the repository, which is what §4.1 and §4.4 ask
for, and no check enforced the headers anyway.

**The reason to remove them is what a reader sees first.** Two lines of licence bookkeeping stood
above the docstring in every file, and the docstring is the line that says what the file does.

**The price, named:** the original argument was that those two lines are the only thing a **single
copied file** carries with it. That was true and stays true. Pull `services/dates.py` into another
project now and it arrives without a licence notice. The gap covers exactly that case; anyone who
takes the repository, a release archive or a clone gets both files with it.

## 71. The repository speaks English, German is a translation

*Amends [point 68](#68-the-language-boundary-follows-the-audience-not-the-file-type) in four
paragraphs: the museum documentation, the tests, the issues, and „why not bilingual".*

Point 68 drew the boundary **by audience** and ran it through the repository, file by file. That was
right for a project that had just been made public and had to stop mixing its languages at random.
It stopped being enough for the same reason: the repository is public, and most of what a stranger
sees first was German — `README`, `SECURITY`, `CHANGELOG`, the issue templates, and every one of the
520 backend test names.

**The boundary now runs between the repository and what is published from it.** Everything a
contributor touches is English. Everything a museum needs in order to run the device exists in
German as well, delivered through a bilingual documentation site.

**The file name carries the rule.** `operations.de.md` is German, `operations.md` is English. Point
68 left this to two hand-kept lists in `language_check.py`, and a new file belonged to whichever
list somebody remembered to add it to. A suffix cannot be forgotten.

**The price is the one point 68 named**, and it is paid deliberately: *„duplicate content in two
languages is the expensive kind of mistake — the second copy goes stale and nobody notices."* That
is still true. It is answered rather than ignored: every translated file carries the hash of the
English source it was made from, and `tools/check_translations.py` reports what has drifted apart.
The doubling is allowed because it is now watched, not because the risk went away.

**Not everything is doubled.** `usermanual` exists in German only — it is a handout printed and left
beside the device in Holm, and an English version would have no reader and would be exactly the copy
that goes stale. `history.de.md` stays German and frozen: 40,768 words whose value is in the nuance,
in a file that takes no further entries.

**Why the tests turn.** Point 68 argued that a test name is a sentence of specification and that
Flurname, Hausnummer and Ortsteil have no good English equivalent. The first half still holds — the
names stay long and stay sentences. The second half was the weaker argument: a glossary settles the
domain terms once, and 8,809 lines of German inside an otherwise English code base cost every
contributor more than the translation costs once.

**Why the issues turn.** A public repository takes reports from people who did not grow up with the
subject. The labels were already English for that reason, and a German issue beside an English label
was half a decision. Whoever prefers to write German still may; nothing is sent back for its
language.

**What point 68 keeps:** no Simplified Technical English, the writing rules for both languages,
English commit messages from 30 August 2026, and `history` closed rather than translated.
