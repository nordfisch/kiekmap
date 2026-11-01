#!/bin/sh
# Sets up a fresh Raspberry Pi as the museum kiosk, from a bundle.
#
#     sudo sh ~/kiekmap/deploy/pi/setup-pi.sh
#
# The bundle comes from the development machine: `make deploy` builds it and copies it into the
# home directory of the SSH user. Expects Raspberry Pi OS **Lite** (64 bit) and no installation in
# /opt/kiekmap yet. For a device that already runs, update.sh is the script.
#
# What is different afterwards: the software lies in /opt/kiekmap, the containers run, the Pi
# boots into the map without a keyboard, mounts USB sticks under /media, and the screen stays on.
# The collection is empty. It is filled by restoring a backup in the admin area.

set -eu

. "$(dirname "$0")/common.sh"

require_root
check_bundle

# A database means a device in service. Setting it up again would leave the collection alone, but
# it would also replace the .env with the one from the bundle -- and whoever runs the wrong script
# should learn that here, not after the PIN changed.
if [ -e "$ROOT/data/kiekmap.db" ]; then
    fail "$ROOT already holds a collection. For an update:
  sudo sh $BUNDLE/deploy/pi/update.sh"
fi

say "packages"
apt-get update
# cage instead of a desktop, chromium as the display, curl for the health query.
#
# Raspberry Pi OS Bookworm carries the Debian package and calls it `chromium`; up to Bullseye it
# was `chromium-browser`. The name is picked before the install, because with `set -e` an unknown
# package would abort the whole script at its first task.
BROWSER_PACKAGE=chromium
apt-cache show chromium >/dev/null 2>&1 || BROWSER_PACKAGE=chromium-browser
apt-get install -y --no-install-recommends cage "$BROWSER_PACKAGE" curl ca-certificates

say "Docker"
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

say "user $USER_NAME"
# Runs the kiosk. It need not carry UID 1000: data/ is handed to the number, see common.sh.
if ! id "$USER_NAME" >/dev/null 2>&1; then
    useradd --create-home --shell /bin/bash "$USER_NAME"
fi
usermod -aG docker,video,input,render,tty "$USER_NAME"

say "software to $ROOT"
mkdir -p "$ROOT"
install_software
cp "$BUNDLE/env" "$ROOT/.env"
set_version
protect_env

say "the place index"
# The backend reads it in at startup while its table is empty -- which on a new device it is.
mkdir -p "$ROOT/data"
cp "$BUNDLE/places.json" "$ROOT/data/places.json"

install_system

say "the screen stays on"
# Two different blankings, and both have to go: the one of the text console (consoleblank) and the
# one the kernel does while booting. Without this the screen is black after ten minutes, and
# nobody in the museum can tell whether the device is still running.
CMDLINE=/boot/firmware/cmdline.txt
[ -f "$CMDLINE" ] || CMDLINE=/boot/cmdline.txt
if [ -f "$CMDLINE" ] && ! grep -q consoleblank=0 "$CMDLINE"; then
    sed -i 's/$/ consoleblank=0/' "$CMDLINE"
    echo "  consoleblank=0 added -- takes effect after the next restart."
fi

load_images
start

cat <<END

Done. $VERSION runs, with an empty collection.

  1. Restart:  sudo reboot
     The Pi should land in the map without a keyboard.
  2. Fill the collection: plug in the stick with the backup, open the admin area through the
     coat of arms, and restore the backup there.

The folder $BUNDLE is no longer needed and can be deleted.
END
