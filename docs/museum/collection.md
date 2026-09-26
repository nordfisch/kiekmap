# Building the first collection

A museum that adopts Kiekmap starts with an archive: a few hundred or a few thousand scans, on
a hard disk, sorted into folders. This page brings them into the device.

It is the one-off job. Adding individual photos later is the
[guide for the museum team](usermanual.md) — the watched folder or the upload in the admin area.
Neither is built for three thousand files, and the initial fill therefore runs on the command line.

Adapting the device to the place comes first: the map, the place index and the settings are in
[Setting it up for another place](adaption.md). This page starts where that one ends.

---

## Before anything: a copy

Two commands on this page delete the collection, and nothing brings it back but a copy. Make one
before you start:

```bash
cp -a data/ ~/kiekmap-data-backup/
```

**Including the `-wal` and `-shm` files beside `data/kiekmap.db`.** SQLite writes into them and
moves the content over later; a copy without them stands at the state of the last checkpoint, and
the difference is invisible until somebody reads it back.

On a device that is already running, the backup in the admin area is the better route — it is
described in the [guide for the museum team](usermanual.md#backup-onto-a-usb-stick).

---

## Where a command runs

**On the development machine**, where the map was built, in the backend's virtual environment:

```bash
cd backend && .venv/bin/python -m app.cli stats
```

**On the device there is no virtual environment.** The Pi carries the software as an image, not as
a Python installation, so the same command runs in the container:

```bash
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env \
    run --rm backend python -m app.cli stats
```

From `/opt/kiekmap` and with `--env-file`, never from `deploy/` — the reason is in the
[operations manual](operations.md#settings-in-container-operation), and it applies to every
`docker compose` command on the device.

**Both fill a different `data/`**, and that decides where the work happens. Building the collection
on the development machine and moving the result over is the easier way: the archive lies there,
the conversion needs processing time, and a mistake costs nothing on a machine nobody is waiting
for. The finished collection then reaches the device the way every backup does — write it onto a
USB stick and read it back in there, see
[Reading a backup back in](usermanual.md#reading-a-backup-back-in).

Importing directly on the Pi works. It takes hours for a few thousand scans, and the museum cannot
use the device meanwhile.

---

## The order of the steps

### 1. Map, place index, settings

```bash
make tiles     # map, fonts and sprites for the region
make places    # build the place index and read it in
```

Both need the internet and are described in
[Setting it up for another place](adaption.md#2-building-the-map-data-and-the-place-index). The
place index matters for the import as well, not only for the map: **a folder name places a photo
only where the place index knows the street.**

The import settings belong in the `.env` before the first photo comes in, not after:
`KIEKMAP_EXIF_DATE_MAX_YEAR`, `KIEKMAP_IMPORT_TAGS`, `KIEKMAP_IMPORT_CREDIT`,
`KIEKMAP_IMPORT_PROVENANCE`. What each of them does is in
[step 5 of the adaption](adaption.md#5-checking-what-belongs-to-the-collection). They apply at the
moment of the import, and changing them afterwards changes nothing about the photos already in.

### 2. Removing the sample collection

A fresh installation carries the invented sample collection, so that the device shows something
before it holds anything. It goes before the real archive comes in:

```bash
make empty
```

The command names what it is about to destroy and **asks for the number of photos to be typed
back**. A question answered with "y" is answered without reading; a number cannot be.

### 3. Everything becomes JPEG

Museum archives are mixed: scans as TIFF, a screenshot as PNG, a picture from a website as WEBP.
The collection is JPEG throughout, and not for tidiness — **a browser cannot display a TIFF.** The
kiosk would show a thumbnail and hand out an original that nothing opens.

```bash
python3 tools/to_jpeg.py ~/Archive ~/Archive-for-import/Streets
```

The tree is copied and the source is left as the museum sent it. The run reports:

```text
2431 files looked at:
  copied     1840
  converted  588
  skipped    3
```

`skipped` is everything that is not a picture — a text file, a spreadsheet. `failed` appears only
when a file could not be read, and names each one.

**The target folder name is part of the provenance.** `KIEKMAP_IMPORT_PROVENANCE` is put in front
of the path inside it, so a photo's provenance leads back to the file in the museum's own archive.
Pick the name accordingly.

### 4. The import

```bash
cd backend && .venv/bin/python -m app.cli import ~/Archive-for-import/Streets
```

The originals stay where they are; the import copies what it takes in. It reports:

```text
588 files looked at:
  taken in    571
  duplicates  14
  rejected    3
    ! No readable image: cannot identify image file '/home/museum/Archive-for-import/Streets/Mühlenweg/12/scan-0043.jpg'
```

- **taken in** — in the collection, with a thumbnail, visible in the admin area.
- **duplicates** — this file was already there, recognised by its content. Nothing was changed.
- **rejected** — not taken in, with a reason per file. Usually a broken file or a format the
  collection does not hold. The reasons appear in the language the device is set to; the labels
  around them are English.

A rejected photo is in the import log of the admin area as well, so nothing is lost by scrolling
past it.

### 5. Checking

```bash
cd backend && .venv/bin/python -m app.cli stats
```

```text
Photos in total       1284
  on the map          1102
  without a place     182
  without a year      766

85 % have a place and are therefore on the map.
```

**Without a year is the normal case** and no fault of the import — most historic photographs carry
no date. That is what the contribution panel is for: visitors fill the gaps in, and the museum
confirms them. A photo **without a place** is not on the map, and that is the number worth working
on.

Then the pictures that came in twice without being the same file:

```bash
cd backend && .venv/bin/python -m app.cli duplicates
```

```text
5 groups, 11 photos, distance up to 40

--- group 1 (2 photos) ---
  photo   502  3543x3543  ----  Mühlenweg 3                Gasthof Petersen
  photo  1235  3366x3366  1928  Mühlenweg 3                Gasthof Petersen
```

The import recognises a duplicate **by the content of the file only**. The same picture scanned a
second time, re-encoded, or saved with different metadata is a different file and comes in again.
This command finds those pairs afterwards by comparing the pictures themselves. `--distance` says
how different two pictures may be and still be shown as a pair; 40 of 256 bits is the default,
a smaller number finds fewer and surer pairs.

What to keep is a decision for a person. The largest image is the usual candidate and not always
the right one — a caption may sit on the smaller version. Deleting happens in the admin area.

### 6. Curating

The rest is not a program's work. Photos without a description, without a title, without a place
are written by whoever looks at the picture and knows the place. The admin area leads into it: its
overview names the gaps and each one opens the list behind it.

---

## What the import reads, and what it does not

**An EXIF date on a scan is the date of the scan.** A photograph from 1928 scanned in 2019 carries
2019 in the file. Taken as the date of the shot it would sit at the right-hand end of the time
slider, count as dated, and never be offered to a visitor for correction.
`KIEKMAP_EXIF_DATE_MAX_YEAR` draws the line: a date from that year on does not date a photo. Where
the file names its device the question does not arise — a scanner never dates, a camera always
does.

**A folder name places a photo** when the place index knows the street. `Mühlenweg/12/` places
every picture below it at Mühlenweg 12. An archive sorted by street and house number places itself;
one sorted differently is simply left alone, and no error is reported for it.

**A coordinate in the file is read, and a house number from the folder beats it.** An EXIF
coordinate looks like a measurement and often is not: in the first collection 278 of 413 such
photos shared their coordinate with another one — values typed in, not measured. A folder that
names a street and a house number is the better statement, and the import treats it as one.

**A duplicate is recognised by the content of the file.** Two files with the same content are the
same photo, whatever they are called. Two files with the same picture and different metadata are
two photos, and the `duplicates` command is the answer to that — see above.

---

## Every command

The commands of `python -m app.cli`. On the development machine with `.venv/bin/python` in front
of it, on the device inside the container — see [above](#where-a-command-runs).

<!-- cli-table -->

| Command | Arguments | What it does | Changes the collection |
|---|---|---|---|
| `import` | `<path>` | Takes a directory in. The originals stay where they are. | yes |
| `scan` | | Sweeps the watched folder once, the same way the service does by itself. | yes |
| `stats` | | How much is in the collection and what is missing from it. | no |
| `duplicates` | `--distance N` | The same picture more than once, found by comparing pictures. | no |
| `places` | | Reads the place index in again, after `make places` or a new `places.json`. | yes |
| `pin` | | Asks for a PIN twice and prints the line for the `.env`. | no |
| `seed-export` | | Writes the collection out to `seed/`. **Development only.** | no |
| `seed-load` | | Deletes the collection and rebuilds it from `seed/`. **Development only.** | yes |
| `empty` | `--yes` | Deletes the whole collection. Asks first. | yes |

`seed-export` and `seed-load` serve development: they carry the invented sample collection this
project is tested with. A museum needs neither, and `seed-load` would throw its archive away.

Every command answers `--help`, and so does each of their names: `python -m app.cli import --help`.

---

## What cannot be undone, and what refuses

**`empty` deletes the collection and leaves nothing in its place.** Rows, originals and thumbnails,
all of them. Map, place index and settings stay. The command shows the numbers first and asks for
the number of photos to be typed back. `--yes` skips the question and exists for scripts; on a
keyboard it is the wrong answer.

**`seed-load` also empties the collection**, and puts the invented sample collection in its place.
On a museum's machine that is the same loss.

**A command that writes refuses while a restore is running.** Reading a backup back in swaps the
database underneath a running import, and the rows written meanwhile would be in no collection at
all. The command notices and ends without doing anything:

```text
A restore is running. Nothing was changed.
```

Run it again when the restore has finished. The commands that write are marked in the table above.
