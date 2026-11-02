# Operations manual

Everything somebody needs to know who keeps the device running in the museum. How to use it is in
the [guide for the museum team](usermanual.md); the technology is here.

> **Tried on a Raspberry Pi 4 with Raspberry Pi OS on Debian 13, on 1 and 2 November 2026:**
> setting up from the bundle, the kiosk after a restart, touch, restoring a backup from a USB
> stick, and updating with the collection on the device. **Not yet tried:** a power cut, and a
> backup onto a stick from the device.

---

## What the development machine needs

Once, before the first Pi. Everything the device gets is put together on the development machine;
after setting up, the Pi needs neither git nor the internet.

**The map and the place index**, from `make tiles` and `make places`. Both need the internet and
processing time, which is why they run here and not on the Pi.

**The folder `local/`.** It holds what belongs to this museum and must not go into the
repository. Git ignores it.

| File | Content |
|---|---|
| `local/logo.png` | the coat of arms of the place |
| `local/pi.env` | the `.env` of the Pi |

The coat of arms:

```bash
mkdir -p local
cp ~/Developer/Museum/Wappen/holm-wappen.png local/logo.png
```

It goes into the frontend image when the image is built. `frontend/public/logo.png` stays the
placeholder, and nothing is to be changed there. Source and rights are in
[adaption.md](adaption.md), section "Putting the coat of arms in". A museum without a coat of arms
copies the placeholder to `local/logo.png`.

**`local/pi.env`** is created by the first `make deploy` from the template, which then stops. Two
things go into it:

- **The PIN line.** `make pin` asks for the PIN twice and prints the line
  `KIEKMAP_ADMIN_PIN_HASH='…'`. **Keep the single quotes.** The hash contains `$` signs, and
  without the quotes Compose cuts it at the first one: the PIN then never matches.
- **The settings of the collection**, from
  [step 5 of the adaption](adaption.md#5-checking-what-belongs-to-the-collection).

`KIEKMAP_VERSION` stays as it is; the scripts on the Pi write it.

**A name for the Pi in SSH.** In `~/.ssh/config`:

```
Host kiekmap-pi
    HostName kiekmap.local
    User admin
```

`kiekmap.local` is the host name set in the Imager, `admin` the user created there. Then the key,
once:

```bash
ssh-copy-id kiekmap-pi
```

Afterwards `ssh kiekmap-pi` has to open a shell without asking for a password. `make deploy` uses
the name `kiekmap-pi`; another one is passed as `host=`.

---

## Setting up a new Pi

A **Raspberry Pi 4 or 5**. The map needs WebGL 2, and a Pi 3 does not offer it: the map would stay
grey there.

**1. The operating system.** With the Raspberry Pi Imager: Raspberry Pi OS **Lite** (64 bit), no
desktop. In the Imager's settings: the host name `kiekmap`, a user with a password, SSH switched on,
and the Wi-Fi if no cable is plugged in. The Pi needs the internet while it is set up, because it
installs Chromium and Docker. **A network cable is better than Wi-Fi:** Chromium alone is 120 MB,
and on the first Pi the Wi-Fi took a quarter of an hour for it.

**2. The bundle, on the development machine:**

```bash
make deploy
```

`make deploy` builds both images with the coat of arms. It puts them together with the map, the
place index, the scripts and `local/pi.env` into `release/kiekmap/` and copies the folder to
`~/kiekmap` on the Pi. It refuses a working tree that is not clean, and it names whatever is
missing: map, place index, coat of arms or PIN.

The bundle carries the version of the commit it was built from: `v0.9.6` on the release tag,
`v0.9.6-g0942491` on any other commit.

**3. On the Pi**, after `ssh kiekmap-pi`:

```bash
sudo sh ~/kiekmap/deploy/pi/setup-pi.sh
```

`sudo` asks for the password of the user set in the Imager. Run directly from the development
machine, the `-t` is needed for that prompt: `ssh -t kiekmap-pi 'sudo sh ~/kiekmap/deploy/pi/setup-pi.sh'`.

The script installs cage, Chromium and Docker and creates the user `kiekmap`, who runs the kiosk.
It copies the software to `/opt/kiekmap`, sets up the kiosk service, the USB rule and the off
button, and switches the screen blanking off. Then it loads the images, starts them, and waits
until the API answers. **It refuses a device that already holds a collection**; for that one there
is the update.

**4. Restart:** `sudo reboot`. The Pi lands in the map without a keyboard.

**5. The collection.** It is empty after setting up. Plug in the stick with the backup, open the
admin area through the coat of arms, and restore the backup there.

`~/kiekmap` is no longer needed afterwards: `rm -r ~/kiekmap`.

**What lies where on the Pi:**

| Path | Content | Belongs to |
|---|---|---|
| `/opt/kiekmap/data/` | the collection: database, photos, place index | UID 1000, the backend in the container |
| `/opt/kiekmap/.env` | the settings, PIN hash included | root, readable for the group `docker` |
| `/opt/kiekmap/deploy/` | compose file and scripts | root |
| `/opt/kiekmap/frontend/public/tiles/` | the map | root |
| `/opt/kiekmap/pre-update/` | the database before the last two updates | root |

Every `docker compose` command on the Pi therefore runs with `sudo`.

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
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env ps
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

**`data/shutdown-watcher` is what makes the button work.** `setup-pi.sh` writes it, and `update.sh`
writes it again. Without it the backend refuses, because the same program also runs on a
development machine and online, where nothing would act on the request.

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

## Updating

**1. A backup**, in the admin area, onto a stick. The update keeps the collection, but a backup is
the one copy that does not lie on the device.

**2. The bundle, on the development machine**, from the release being installed:

```bash
git switch --detach v0.9.6
make deploy
```

**3. On the Pi**, after `ssh kiekmap-pi`:

```bash
sudo sh ~/kiekmap/deploy/pi/update.sh
```

The script, in this order:

1. loads the new images while the old version keeps running;
2. stops the containers and copies the database to `pre-update/<old version>/`. The last two
   copies are kept;
3. replaces `deploy/` and the map. Each is copied beside the old one first and then renamed, so
   that a copy broken off halfway leaves no half map file;
4. writes the new version into `KIEKMAP_VERSION`;
5. takes the place index only when it differs from the one on the device, and then reads it in;
6. starts the containers, waits for the API and checks that the backend runs the new image;
7. restarts the kiosk and removes the images older than the previous version.

**What stays:** everything in `data/` — photos, database, the state of the backup — and the
`.env`, except for `KIEKMAP_VERSION`. A change to `local/pi.env` therefore does not reach a device
that is already set up. A changed setting is entered on the Pi as well:

```bash
sudo nano /opt/kiekmap/.env
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env up -d
```

**The script refuses a device that is not set up**; for that one there is `setup-pi.sh`.

**A connection that drops does not stop it.** Both scripts start themselves again as a systemd unit,
`kiekmap-update` and `kiekmap-setup-pi`, and the terminal only shows its output. After a new
`ssh kiekmap-pi`, `journalctl -u kiekmap-update` shows how far it got.

**Going back.** The script prints the commands for it at its end. The image of the previous
version stays on the device, and the database before the update lies in `pre-update/`. Whatever
was entered after the update is lost that way.

### Updating by stick

The Pi in the museum hangs on no network. The same bundle then goes onto a stick, on the
development machine:

```bash
make deploy to=/Volumes/STICK/kiekmap
```

`to=` names a folder of its own on the stick, not the stick itself: an earlier bundle in it is
replaced, anything else is refused. On the Pi, with the stick plugged in:

```bash
ls /media
sudo sh /media/<name of the stick>/kiekmap/deploy/pi/update.sh
```

The script finds the bundle beside itself and does the same as above.

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
| The button says the device cannot switch itself off | `data/shutdown-watcher` is missing — run `update.sh` once more |
| The login rejects every PIN | `KIEKMAP_ADMIN_PIN_HASH` is empty; the area says so in plain words |
| Imported photos without a keyword or a credit | A setting does not reach the container — [see below](#settings-in-container-operation) |

---

## Setting up the PIN for the admin area

```bash
cd backend && .venv/bin/python -m app.cli pin
```

`make pin` does the same. That is the development machine. **On the device there is no virtual
environment** — the Pi carries the software as an image, not as a Python installation, so there the
same command runs in the container:

```bash
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env \
    run --rm backend python -m app.cli pin
```

The command asks for the PIN twice and prints the line that belongs in the `.env`, in single
quotes. The quotes stay: without them Compose cuts the hash at its first `$`. The PIN itself is
stored nowhere; forgetting it means setting a new one.

On a device the line goes into `/opt/kiekmap/.env` (`sudo nano`), followed by the `up -d` from
[Updating](#updating). It also goes into `local/pi.env`, so that the next device set up gets it.

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
[Updating](#updating).

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
why. The PIN hash comes from `make pin` on the development machine, in single quotes, which
protect it the same way; see [Setting up the PIN](#setting-up-the-pin-for-the-admin-area).

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

**2. The images, on the development machine**, built from the release:

```bash
git switch --detach v0.9.6
make release to=$HOME/kiekmap-update
```

`make release` writes `images.tar` and a `version` file. The coat of arms comes from
`local/logo.png`, as for the Pi; see [What the development machine needs](#what-the-development-machine-needs).
Without that file the image carries the placeholder.

**3. Onto the server**, into the home directory of the server's user — `/opt` belongs to root, and
only `/opt/kiekmap` was handed over:

```bash
rsync -a --progress $HOME/kiekmap-update/ kiekmap-web:kiekmap-update/
```

**4. On the server**, after `ssh kiekmap-web`:

```bash
cd /opt/kiekmap
git fetch --tags && git switch --detach v0.9.6
docker load -i ~/kiekmap-update/images.tar
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
rm -r ~/kiekmap-update
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
