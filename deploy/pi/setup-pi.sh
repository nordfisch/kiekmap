#!/bin/sh
# Sets up a fresh Raspberry Pi as the museum kiosk.
#
#     sudo sh deploy/pi/setup-pi.sh
#
# Expects Raspberry Pi OS **Lite** (64 bit) and the project already checked out under
# /opt/kiekmap. Runs once; a second call does no harm.
#
# What is different afterwards: the Pi boots into the map without a keyboard, mounts USB sticks
# under /media, and the screen stays on.

set -eu

ROOT="${KIEKMAP_ROOT:-/opt/kiekmap}"
USER_NAME="${KIEKMAP_USER:-kiekmap}"

[ "$(id -u)" -eq 0 ] || { echo "Please start with sudo." >&2; exit 1; }
[ -d "$ROOT" ] || { echo "$ROOT does not exist -- clone the project there first." >&2; exit 1; }

echo "== packages"
apt-get update
# cage instead of a desktop, chromium as the display, curl for the health query.
apt-get install -y --no-install-recommends cage chromium-browser curl ca-certificates

echo "== Docker"
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "== user $USER_NAME"
# UID 1000 has to match the one in backend/Dockerfile, otherwise the service may not write into
# ./data. On a fresh Pi OS the first user already carries that number.
if ! id "$USER_NAME" >/dev/null 2>&1; then
    useradd --uid 1000 --create-home --shell /bin/bash "$USER_NAME" 2>/dev/null \
        || useradd --create-home --shell /bin/bash "$USER_NAME"
fi
usermod -aG docker,video,input,render,tty "$USER_NAME"
chown -R "$USER_NAME":"$USER_NAME" "$ROOT/data" 2>/dev/null || true

echo "== kiosk service"
install -m 755 "$ROOT/deploy/pi/kiekmap-kiosk" /usr/local/bin/
install -m 644 "$ROOT/deploy/pi/kiekmap-kiosk.service" /etc/systemd/system/

echo "== USB sticks (for the backup)"
install -m 755 "$ROOT/deploy/pi/kiekmap-usb-mount" /usr/local/sbin/
install -m 644 "$ROOT/deploy/pi/99-kiekmap-usb.rules" /etc/udev/rules.d/
udevadm control --reload

echo "== the screen stays on"
# Two different blankings, and both have to go: the one of the text console (consoleblank) and the
# one the kernel does while booting. Without this the screen is black after ten minutes, and
# nobody in the museum can tell whether the device is still running.
CMDLINE=/boot/firmware/cmdline.txt
[ -f "$CMDLINE" ] || CMDLINE=/boot/cmdline.txt
if [ -f "$CMDLINE" ] && ! grep -q consoleblank=0 "$CMDLINE"; then
    sed -i 's/$/ consoleblank=0/' "$CMDLINE"
    echo "  consoleblank=0 added -- takes effect after the next restart."
fi

echo "== switching the services on"
systemctl daemon-reload
systemctl enable kiekmap-kiosk

cat <<'END'

Done. What is still missing:

  1. Create the .env (PIN, version):
       cd /opt/kiekmap && cp deploy/.env.example .env
       cd backend && python3 -m app.cli pin      # put the line into the .env
  2. Copy the map data and the place index over from the development machine:
       frontend/public/tiles/  and  data/places.json
  3. Start the containers:
       cd /opt/kiekmap/deploy && docker compose up -d
  4. Restart and watch:
       sudo reboot

After the restart the Pi should land in the map without a keyboard.
END
