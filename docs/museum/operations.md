# Operations manual

Everything somebody needs to know who keeps the device running in the museum. How to use it is in
the [guide for the museum team](usermanual.md); the technology is here.

> **Not yet tried on a real Pi.** The files under `deploy/pi/` are written carefully and checked
> for syntax, but have never run — there was no device while they were built. Whatever sticks
> first belongs in this file, as soon as the Pi stands there.

---

## Setting up a new Pi

A **Raspberry Pi 4 or 5**. The map needs WebGL 2, and a Pi 3 does not offer it: the map would stay
grey there.

Raspberry Pi OS **Lite** (64 bit), no desktop. Then:

```bash
sudo git clone <repo> /opt/kiekmap
sudo sh /opt/kiekmap/deploy/pi/setup-pi.sh
```

The script installs cage, Chromium and Docker, creates the user `kiekmap`, sets up the kiosk
service and the USB rule, and switches the screen blanking off. It then names the steps it
cannot do itself: create the `.env`, bring images and map data over from the development machine,
set the PIN, restart.

**The map data comes from the development machine**, not from the Pi. `make tiles` and
`make places` need the internet and processing time; only the results belong on the Pi:

```bash
rsync -a frontend/public/tiles/ pi:/opt/kiekmap/frontend/public/tiles/
rsync -a data/places.json       pi:/opt/kiekmap/data/places.json
```

**The coat of arms does not come that way — it goes into the image.** Only a placeholder lies in
the repository; a municipal coat of arms must not lie there, see
[decisions.md](../developer/decisions.md), point 21. The real one is taken into the frontend image
when it is built and is not read at run time, so it belongs on the **development machine** before
the images are built:

```bash
cp ~/Developer/Museum/Wappen/holm-wappen.png frontend/public/logo.png
```

The next `make release` then carries it to the device inside the image. **Copying it onto the Pi
does nothing**: the compose file mounts `tiles/` back into the container and nothing else, so a
`logo.png` lying beside it is read by nobody. Its source and the rights to it are in
[adaption.md](adaption.md), section "Putting the coat of arms in".

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
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env ps
curl -sf http://localhost/api/health && echo " the API answers"
```

---

## Switching off from the admin area

The button at the foot of the admin area's start page, and the three pieces behind it:

1. The backend writes `data/shutdown-requested`, with the time in it. It runs unprivileged in a
   container and can do no more than that.
2. `kiekmap-shutdown.path` sees the file and starts `kiekmap-shutdown.service`.
3. `/usr/local/sbin/kiekmap-shutdown` deletes the request, checks that it is from this boot, and
   calls `systemctl --no-block poweroff`.

```bash
systemctl status kiekmap-shutdown.path      # is the watcher running?
journalctl -u kiekmap-shutdown -n 20        # what happened on the last request
```

**`data/shutdown-watcher` is what makes the button work.** `setup-pi.sh` writes it; without it the
backend refuses, because the same program also runs on a development machine and online, where
nothing would act on the request. A device that was only updated from a stick therefore needs
`sudo sh /opt/kiekmap/deploy/pi/setup-pi.sh` once — it may run as often as you like.

**The containers are deliberately not stopped.** `docker compose stop` marks them as stopped by
hand, and `restart: unless-stopped` would then leave them down at the next boot. systemd stops
Docker itself, and the database survives that: WAL with `synchronous=NORMAL` costs at most the last
transaction.

**Pulling the plug stays survivable**, and that is the point of [issue #21](https://github.com/nordfisch/kiekmap/issues/21):
the button is the orderly way, not a repair. What it does not cover is the moment nobody presses it.

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
git switch --detach v0.9.6                            # the release to be shipped
make release to=/Volumes/STICK/kiekmap-update
make release to=/Volumes/STICK/kiekmap-update map=1   # if the region has changed
```

The target builds both images, saves them as `images.tar` and writes the `version` file beside
them. **It aborts when the working tree is not clean or the matching tag is missing** — a stick
that belongs to no commit cannot be placed a year later.

**A stick is built from a release, on its tag.** How a release is made is in
[development.md](../developer/development.md#making-a-release).

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
3. `docker compose ... ps` — are the containers running? If not: `... logs backend`. The full
   command is in [Settings in container operation](#settings-in-container-operation).
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
| The button says the device cannot switch itself off | `data/shutdown-watcher` is missing — run `setup-pi.sh` once more |
| The login rejects every PIN | `KIEKMAP_ADMIN_PIN_HASH` is empty; the area says so in plain words |
| Imported photos without a keyword or a credit | A setting does not reach the container — [see below](#settings-in-container-operation) |

---

## Setting up the PIN for the admin area

```bash
cd backend && .venv/bin/python -m app.cli pin
```

That is the development machine. **On the device there is no virtual environment** — the Pi
carries the software as an image, not as a Python installation, so there the same command runs in
the container:

```bash
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env \
    run --rm backend python -m app.cli pin
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
and is read by [`deploy/docker-compose.yml`](../../deploy/docker-compose.yml) as `env_file`. Whoever
changes something there restarts the containers afterwards:

```bash
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env up -d
```

**From `/opt/kiekmap` and with `--env-file`, not from `deploy/`.** Compose reads the `.env` from
the directory it is started in, and the `.env` lies one above the compose file. Started from
`deploy/` it would not find it: `KIEKMAP_VERSION` would fall back to `dev`, and since the compose
file carries a `build:`, a missing image would make the Pi build the frontend itself. Every
`docker compose` command on the device takes this form.

**The language of the device** stands here too:

```bash
KIEKMAP_LANGUAGE=de     # or en
```

It switches the visitor view, the admin area, the messages and the date labels. **No new build is
needed** — the new value applies once the containers have restarted. A value other than `de` or
`en` aborts the start instead of falling back to German in silence; a line from Pydantic then
stands in the log. More in [adaption.md](adaption.md#another-language).

**Three values the compose file sets itself**, and those win over the `.env`:
`KIEKMAP_DATA_DIR`, `KIEKMAP_MEDIA_DIR` and the location of the PIN hash.
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
[`deploy/docker-compose.yml`](../../deploy/docker-compose.yml) is what stands against that. Without
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
> in the running data directory. Symlinks have been skipped since ([decisions.md](../developer/decisions.md),
> point 40); on a Mac with no drive attached the list is now empty, and that is exactly right.

---

## The schema of a restored backup

**The restore has handled this itself since 15 August 2026** — this section describes *how*, and
what to do if something sticks after all. The short way for the team is in the
[guide](usermanual.md#when-the-backup-is-older-than-the-program).

**Why it is a question at all.** A backup holds `kiekmap.db` exactly as the file looked at the
time — schema version in the table `alembic_version` included. On restoring, the file is swapped
**as a whole** (`_swap_in` in `services/backup/restore.py`). For those seconds the program closes
the database, and then attaches itself to the new file (`closed_for_swap` in `app/db.py`). Migrations do not run by themselves in the process: they
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
docker compose -f deploy/docker-compose.yml --env-file .env exec backend python -c "import sqlite3; print(sqlite3.connect('/data/kiekmap.db').execute('select * from alembic_version').fetchone())"
docker compose -f deploy/docker-compose.yml --env-file .env exec backend alembic heads
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

## The online instance

Beside the Pi there is a second way to run this: on a web server, reachable from anywhere, behind
one password. It exists for the months in which the museum team fills the database from home,
before a device stands in the exhibition room.

The same two containers run there as on the Pi — the same images, the same nginx configuration.
Only Caddy stands in front of them and takes care of HTTPS and the password:

```
Internet --HTTPS--> Caddy --HTTP--> nginx (frontend) --> uvicorn (backend)
```

**The password protects everything**, the map included and `/api/` as well. Whoever does not have
it gets a 401 and sees nothing. That is the purpose of this instance: the collection is not public
while it is being built.

**The backup is the ZIP download.** A server has no USB ports, so the backup button of the admin
area finds no target there. Instead somebody downloads the archive from the admin area, regularly,
and keeps it somewhere else. The stick is for the device in the museum.

**Give the PIN more digits.** Four are enough on the Pi — whoever stands in front of it is standing
in the museum. Online, four are not; the PIN allows up to twelve.

**Two commands never run on the server.** `deploy/pi/update.sh` starts the containers without
Caddy: nginx then answers on port 80, and nobody is asked for a password. `make prod-web` builds
the images on the server itself and stays in the foreground. The images come from the development
machine, as for the Pi.

### What the server needs

- **A Linux machine with a public address and SSH access.** The commands below are written for
  Oracle Linux 9 on an Oracle Cloud Ampere instance. Another distribution differs in how Docker is
  installed and in how the firewall is opened.
- **A domain name whose A record points at that address.** Caddy asks Let's Encrypt for a
  certificate for this name.
- **The processor of the development machine, or a flag.** The images are built there and only
  run on the same architecture. A Mac with Apple silicon and an Ampere instance are both `arm64`
  and fit together. For an `x86_64` server, put `DOCKER_DEFAULT_PLATFORM=linux/amd64` in front of
  `make release`. `uname -m` on the server says which it is.

**One name for the server, on the development machine.** Every command below reaches the server
through an SSH alias, so its address stands in one place. In `~/.ssh/config`:

```
Host kiekmap-web
    HostName <address of the server>
    User opc
```

`opc` is the user Oracle creates. Other providers name it differently. Afterwards `ssh kiekmap-web`
has to open a shell on the server.

### Setting up the server

Once. The first four steps on the server, after `ssh kiekmap-web`.

**1. Open the ports.** 80 for the certificate, 443 for the site. In the provider's console — for
Oracle Cloud an ingress rule for TCP 80 and 443 in the security list of the instance's subnet —
and in the firewall of the machine:

```bash
sudo firewall-cmd --permanent --add-service=http --add-service=https && sudo firewall-cmd --reload
```

**2. Docker and git:**

```bash
sudo dnf -y install dnf-plugins-core git
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in, so that the group applies. `docker run --rm hello-world` then has to work
without `sudo`.

**3. The repository and the `.env`:**

```bash
sudo mkdir -p /opt/kiekmap && sudo chown $USER:$USER /opt/kiekmap
git clone https://github.com/nordfisch/kiekmap.git /opt/kiekmap
mkdir -p /opt/kiekmap/data
cp /opt/kiekmap/deploy/.env.example /opt/kiekmap/.env
```

**4. What the `.env` needs.** The three lines of the online instance, the PIN, and the settings of
the collection from [step 5 of the adaption](adaption.md#5-checking-what-belongs-to-the-collection):

```bash
KIEKMAP_WEB_DOMAIN=fotos.example.org
KIEKMAP_WEB_USER=museum
KIEKMAP_WEB_PASSWORD_HASH=$$2a$$14$$...
KIEKMAP_ADMIN_PIN_HASH=...
```

The password hash, on the development machine:

```bash
docker run --rm caddy:2.11.4-alpine caddy hash-password --plaintext '<password>'
```

**Every `$` in it has to be written twice** in the `.env`. Compose reads a single one as the start
of a variable name and drops what follows it — the password then never matches, and nothing says
why. The PIN hash comes from `cd backend && .venv/bin/python -m app.cli pin` on the development
machine; see [Setting up the PIN](#setting-up-the-pin-for-the-admin-area).

**5. The map data**, on the development machine, from `make tiles` and `make places`:

```bash
rsync -a frontend/public/tiles/ kiekmap-web:/opt/kiekmap/frontend/public/tiles/
rsync -a data/places.json       kiekmap-web:/opt/kiekmap/data/places.json
```

**6. The software:** the steps of [Updating the server](#updating-the-server). On a fresh server
they are the first start. The collection is empty afterwards; it is filled through the admin area,
or by reading in a backup there.

### Updating the server

Every release. The version in the commands is an example; take the one being installed.

**1. A backup.** Download the ZIP from the admin area of the online instance.

**2. The images, on the development machine.** Built from the release, with the museum's coat of
arms, which only reaches the frontend image this way:

```bash
git switch --detach v0.9.6
cp ~/Developer/Museum/Wappen/holm-wappen.png frontend/public/logo.png
make release to=$HOME/kiekmap-update
git restore frontend/public/logo.png
```

`make release` accepts the coat of arms as the one changed file. It writes `images.tar` and a
`version` file. The last line puts the placeholder back, so that the real coat of arms never gets
into a commit.

**3. Onto the server:**

```bash
rsync -a --progress $HOME/kiekmap-update/ kiekmap-web:/opt/kiekmap-update/
```

**4. On the server**, after `ssh kiekmap-web`:

```bash
cd /opt/kiekmap
git fetch --tags && git switch --detach v0.9.6
docker load -i /opt/kiekmap-update/images.tar
sed -i 's/^KIEKMAP_VERSION=.*/KIEKMAP_VERSION=v0.9.6/' .env
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.web.yml --env-file .env up -d
```

- The clone follows the release, because the compose files and the `Caddyfile` come from it.
- `KIEKMAP_VERSION` names the images Compose starts. Without the new value it starts the old ones
  again, and nothing says so.
- `up -d` replaces the containers whose image changed and returns. On its first start the backend
  brings the database schema forward by itself.
- A coat of arms lying in the server's tree does no harm and does nothing: the image carries its
  own.

**5. The check**, still on the server:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.web.yml --env-file .env ps
```

Three containers, all `Up`, the backend `healthy`, and the two Kiekmap images tagged with the new
version. The version the backend itself reports, from anywhere:

```bash
curl -u museum https://fotos.example.org/api/health
```

curl asks for the password and has to answer with the new version.

**6. Tidying up**, once the new version runs:

```bash
rm -r /opt/kiekmap-update
docker image ls 'kiekmap-*'
docker image rm kiekmap-backend:<old version> kiekmap-frontend:<old version>
```

### Trying it out beforehand

With `KIEKMAP_WEB_DOMAIN=localhost` Caddy issues its own certificate and needs neither a domain nor
a public address. The browser warns about that certificate once. This checks the password and the
routing; it does not check the certificate from Let's Encrypt. On a Mac the overlay of the
development machine has to come along, because `/media` does not exist there:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.mac.yml \
    -f deploy/docker-compose.web.yml --env-file .env up --build
```

---

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

**A restore and a command that writes exclude each other.** `import`, `scan`, `places`,
`seed-load` and `empty` hold a lock on `data/kiekmap.lock` while they run. A restore started
meanwhile stops at once, changes nothing and says so in the admin area. A command started during a
restore writes nothing and ends with `A restore is running`. `stats`, `duplicates`, `pin` and
`seed-export` only read and run at any time. The lock reaches commands run with
`docker compose exec` or `run --rm`, because every container sees the same `data/`. The kernel
releases it when a process ends, a crash or a power cut included; the file itself stays and must
not be deleted. **Not on the Mac with `make prod-mac`:** Docker Desktop's file sharing ignores the
lock, even inside one container.

Setting the device up for another place: [adaption.md](adaption.md).
