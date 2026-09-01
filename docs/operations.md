# Operations manual

Everything somebody needs to know who keeps the device running in the museum. How to use it is in
the [guide for the museum team](usermanual.md); the technology is here.

> **Not yet tried on a real Pi.** The files under `deploy/pi/` are written carefully and checked
> for syntax, but have never run — there was no device while they were built. Whatever sticks
> first belongs in this file, as soon as the Pi stands there.

---

## Setting up a new Pi

Raspberry Pi OS **Lite** (64 bit), no desktop. Then:

```bash
sudo git clone <repo> /opt/kiekmap
sudo sh /opt/kiekmap/deploy/pi/setup-pi.sh
```

The script installs cage, Chromium and Docker, creates the user `kiekmap`, sets up the kiosk
service and the USB rule, and switches the screen blanking off. It then names the four steps it
cannot do itself: create the `.env`, set the PIN, copy the map data, start the containers.

**The map data comes from the development machine**, not from the Pi. `make tiles` and
`make places` need the internet and processing time; only the results belong on the Pi:

```bash
rsync -a frontend/public/tiles/ pi:/opt/kiekmap/frontend/public/tiles/
rsync -a data/places.json       pi:/opt/kiekmap/data/places.json
```

**The coat of arms comes the same way.** Only a placeholder lies in the repository — a municipal
coat of arms must not lie there, see [decisions.md](decisions.md), point 21. The real one belongs
on the device:

```bash
rsync -a wappen.png pi:/opt/kiekmap/frontend/public/logo.png
```

Then build the frontend again (`make prod` rebuilds the images anyway) — the file is taken into
the image at build time, not read at run time. The coat of arms of Holm lies under
`~/Developer/Museum/Wappen/holm-wappen.png` on the development machine; its source and the rights
to it are in [adaption.md](adaption.md), section "Putting the coat of arms in".

---

## What happens when it is switched on

About 20 seconds, in this order:

1. **Docker starts.** The containers come up by themselves with `restart: unless-stopped`. On the
   first start after an update the Alembic migrations run, which is why it can take longer.
2. **`kiekmap-kiosk.service` waits for `/api/health`.** Without that wait the first visitors would
   see an error page for a few seconds — and it would stay, because Chromium does not reload by
   itself. After five minutes the service starts regardless: an error page that somebody sees and
   reports is better than a black screen.
3. **`cage -- chromium --kiosk`** takes over the screen. A fresh browser profile on every start,
   so that nothing from yesterday is left after a power cut.
4. **If Chromium crashes, systemd starts it again** (`Restart=always`, 5 s pause).

How to tell that something is stuck:

```bash
systemctl status kiekmap-kiosk       # is the kiosk running?
journalctl -u kiekmap-kiosk -n 50    # why not?
cd /opt/kiekmap/deploy && docker compose ps
curl -sf http://localhost/api/health && echo " the API answers"
```

---

## The way out for maintenance

The kiosk knows no key combination for quitting — that is deliberate, so that a visitor does not
leave the exhibition by accident. The way out goes through SSH:

```bash
sudo systemctl stop kiekmap-kiosk     # the screen goes black, the services keep running
sudo systemctl start kiekmap-kiosk    # back into the map
```

For work on the device itself the admin area through the coat of arms is usually enough — tending
photos, uploading, backing up. SSH is needed for updates and for troubleshooting.

---

## Updating without the internet

Build a folder for the stick on the development machine:

```bash
make release to=/Volumes/STICK/kiekmap-update
make release to=/Volumes/STICK/kiekmap-update map=1   # if the region has changed
```

The target builds both images, saves them as `images.tar` and writes the `version` file beside
them. **It aborts when the working tree is not clean or the matching tag is missing** — a stick
that belongs to no commit cannot be placed a year later.

So beforehand: `make version v=0.9.0`, commit, `git tag -s v0.9.0 -m v0.9.0`.

By hand these were four commands. The one that gets forgotten writes the `version` file: the
images load, `KIEKMAP_VERSION` stays as it was in the `.env`, and the next start pulls the **old**
image up again. The device then runs the old software and says so nowhere.

On the Pi:

```bash
sudo sh /opt/kiekmap/deploy/pi/update.sh /media/STICK/kiekmap-update
```

The script reads the images in, enters the version in the `.env`, swaps the map data and the place
index, restarts the containers and waits until the API answers. **The collection is not touched** —
photos and records stay where they are.

Two details sit in there: the map data is first put beside the old file and then renamed, so that
a copy broken off halfway leaves no half map file. And the place index is read in explicitly — at
startup the backend loads it only when the table is empty.

---

## Cloning the SD card

The complete backup of the device, operating system included. Once after setting it up and after
every larger update:

```bash
# shut the Pi down, card into the development machine:
sudo dd if=/dev/rdiskN bs=4m | gzip > holm-pi-2026-07-29.img.gz
```

This does **not** replace the backup in the admin area — that one runs while the device is in
service and saves the collection. The clone saves the set-up device.

---

## The screen stays black

In this order:

1. `systemctl status kiekmap-kiosk` — is the service running?
2. `journalctl -u kiekmap-kiosk -n 50` — does cage report anything? *"unable to open primary DRM
   device"* means: the session has no output device. Then one of the four lines `PAMName`,
   `TTYPath`, `StandardInput`, `UtmpIdentifier` is missing from the unit, or the user is not in
   the groups `video` and `render`.
3. `docker compose ps` — are the containers running? If not: `docker compose logs backend`.
4. Black after ten minutes although everything ran before: `consoleblank=0` is missing from
   `cmdline.txt` (`setup-pi.sh` sets it, and it takes effect only after a restart).

---

## Troubleshooting in brief

| What you see | First suspicion |
|---|---|
| Map without labels | `frontend/public/basemaps/` is missing — `make tiles` did not run |
| Map grey, no tiles | `frontend/public/tiles/map.pmtiles` is missing or half copied |
| The place search finds nothing | `data/places.json` is missing, or `python -m app.cli places` did not run |
| The contribution panel fails silently | The region check without `data/region.json` — `make tiles` puts it there too |
| **Display normal, but nothing can be saved** | **The schema is out of date. Since August 2026 the restore brings it forward itself — [see below](#the-schema-of-a-restored-backup)** |
| The USB stick does not appear | The udev rule or `:rshared` — see below |
| The login rejects every PIN | `KIEKMAP_ADMIN_PIN_HASH` is empty; the area says so in plain words |
| Imported photos without a keyword or a credit | A setting does not reach the container — [see below](#settings-in-container-operation) |

---

## Setting up the PIN for the admin area

```bash
cd backend && .venv/bin/python -m app.cli pin
```

The command asks for the PIN twice and prints the line that belongs in the `.env`. The PIN itself
is stored nowhere; forgetting it means setting a new one. Restart the service afterwards.

If no PIN is set up, the number pad says exactly that — it does not silently reject every entry.
After five wrong attempts it locks for a minute. The session ends after 30 minutes without use;
every action pushes that out, and a restart of the service ends every session.

---

## Settings in container operation

The `.env` in the project directory is where the settings stand in operation as well. It
deliberately does **not** lie in the image — the image is the software, the `.env` is the place —
and is read by [`deploy/docker-compose.yml`](../deploy/docker-compose.yml) as `env_file`. Whoever
changes something there restarts the containers afterwards:

```bash
cd /opt/kiekmap && docker compose up -d
```

**The language of the device** stands here too:

```bash
KIEKMAP_LANGUAGE=de     # or en
```

It switches the visitor view, the admin area, the messages and the date labels. **No new build is
needed** — the new value applies once the containers have restarted. A value other than `de` or
`en` aborts the start instead of falling back to German in silence; a line from Pydantic then
stands in the log. More in [adaption.md](adaption.md#another-language).

**Four values the compose file sets itself**, and those win over the `.env`:
`KIEKMAP_DATA_DIR`, `KIEKMAP_MEDIA_DIR`, `KIEKMAP_CORS_ORIGINS` and the location of the PIN hash.
They describe the container, not the place — inside, the directories are always called `/data` and
`/media`, wherever they lie outside. A `KIEKMAP_MEDIA_DIR=/Volumes` in the `.env` of the
development Mac therefore does not disturb operation.

**Why this stands here:** until 14 August 2026 the compose file passed only individual values
through. The rest fell back to their defaults inside the container in silence, and that hit the
import of all things: photos arrived, but without a keyword, without a credit and without a note
on their provenance. Nothing failed, nothing stood in the log. Whoever introduces a new setting
today need do nothing further — it comes through by itself; that is verified both through the
inbox folder and through the batch upload of the admin area.

---

## Making USB sticks visible

Raspberry Pi OS **Lite** has no desktop and therefore no automounter: a stick that is plugged in
turns up nowhere by itself. The admin area would never see one and would report "Please plug in a
USB stick" for ever.

```bash
sudo install -m 755 deploy/pi/kiekmap-usb-mount /usr/local/sbin/
sudo install -m 644 deploy/pi/99-kiekmap-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload
```

To check: plug a stick in, then

```bash
ls /media && findmnt /media/*
```

Two traps sit in there, both silent:

**The container does not see the stick.** A Docker bind mount shows only what was already mounted
when the container started. A stick plugged in later stays invisible — with no error message, the
folder is simply empty. `:rshared` on the line `/media:/media` in
[`deploy/docker-compose.yml`](../deploy/docker-compose.yml) is what stands against that. Without
it, not even restarting the container at the right moment helps.

**The stick is there but write-protected.** FAT and exFAT sticks know no owners; without `uid=1000`
at mount time they belong to root, and the service (UID 1000, see `backend/Dockerfile`) is not
allowed to write. The script sets the option — the admin area hides such drives anyway, rather
than offering a button that fails later.

**On the Mac for development:** `KIEKMAP_MEDIA_DIR=/Volumes` into the `.env`. A test volume comes
into being with

```bash
hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK teststick.dmg && hdiutil attach teststick.dmg
```

> **There is always a symlink to `/` in `/Volumes`**, named after the internal volume — macOS
> creates it itself. Until 14 August 2026 it counted as a drive, and the backup landed behind it,
> in the running data directory. Symlinks have been skipped since ([decisions.md](decisions.md),
> point 40); on a Mac with no drive attached the list is now empty, and that is exactly right.

---

## The schema of a restored backup

**The restore has handled this itself since 15 August 2026** — this section describes *how*, and
what to do if something sticks after all. The short way for the team is in the
[guide](usermanual.md#when-the-backup-is-older-than-the-program).

**Why it is a question at all.** A backup holds `kiekmap.db` exactly as the file looked at the
time — schema version in the table `alembic_version` included. On restoring, the file is swapped
**as a whole** (`_swap_in` in `services/backup/restore.py`); the running program then only attaches
itself to it again (`_reopen_database`). Migrations do not run by themselves in the process: they
run at *startup* (`backend/docker-entrypoint.sh`), and a restore is not a startup.

**What happens now**, and the order is the whole point (`services/schema.py`):

| The backup is … | … and then |
|---|---|
| **older** than the program | `alembic upgrade head` runs after the swap. The bar reads "The schema is being brought forward" |
| **at the same level** | nothing happens, the call has no effect |
| **newer** than the program | **it aborts before anything is swapped** — the collection on the device stays untouched |

The refusal comes **before** the swap, and that is no detail: a backup this program cannot read
must not leave the device half replaced. After the refusal the archive still lies in the inbox
folder, and the working directory is tidied up.

**With a backup that is too new: update the program first, then read it in.** See
[Updating without the internet](#updating-without-the-internet).

### Looking up where things stand

```bash
docker compose exec backend python -c "import sqlite3; print(sqlite3.connect('/data/kiekmap.db').execute('select * from alembic_version').fetchone())"
docker compose exec backend alembic heads
```

If the two values do not agree, the schema is not up to date. That is the first thing to look at
when writing fails in operation, and the state cannot be seen from outside: the exhibition shows
photos, map and timeline as always, only **every write** fails with HTTP 500. The same on the
development machine, without containers:

```bash
sqlite3 data/kiekmap.db "select * from alembic_version;"
cd backend && .venv/bin/alembic heads
```

And the repair by hand:

```bash
make migrate
```

## Where the backup lies

On the stick, in the folder `kiekmap-backup/`:

```
kiekmap-backup/
  backup.json        date, count, name of the place
  kiekmap.db         the records, written out consistently with VACUUM INTO
  photos/            the originals, filed under their hash
  thumbs/            the thumbnails
  region.json        the map extent
  places.json        the place index
```

A folder rather than an archive: a backup broken off halfway is then partly usable instead of
worthless, and the pictures can be looked at on any computer.

After a **restore** the previous state lies under `data/before-<date>/` — database and
write-ahead log included. It is never deleted automatically. Once it is certain that everything is
right:

```bash
rm -rf data/before-2026-07-29-1115
```

That is the only place where the SD card can fill up unnoticed.

Setting the device up for another place: [adaption.md](adaption.md).
