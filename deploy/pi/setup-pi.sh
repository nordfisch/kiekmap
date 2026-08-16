#!/bin/sh
# Richtet einen frischen Raspberry Pi als Museums-Kiosk ein.
#
#     sudo sh deploy/pi/setup-pi.sh
#
# Erwartet Raspberry Pi OS **Lite** (64 Bit) und ein bereits ausgechecktes Projekt unter
# /opt/kiekmap. Laeuft einmal; ein zweiter Aufruf schadet nicht.
#
# Was danach anders ist: Der Pi bootet ohne Tastatur in die Karte, haengt USB-Sticks unter /media
# ein, und der Bildschirm bleibt an.

set -eu

WURZEL="${KIEKMAP_ROOT:-/opt/kiekmap}"
BENUTZER="${KIEKMAP_USER:-kiekmap}"

[ "$(id -u)" -eq 0 ] || { echo "Bitte mit sudo starten." >&2; exit 1; }
[ -d "$WURZEL" ] || { echo "$WURZEL gibt es nicht -- Projekt zuerst dorthin klonen." >&2; exit 1; }

echo "== Pakete"
apt-get update
# cage statt eines Desktops, chromium als Anzeige, curl fuer die Gesundheitsabfrage.
apt-get install -y --no-install-recommends cage chromium-browser curl ca-certificates

echo "== Docker"
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "== Benutzer $BENUTZER"
# UID 1000 muss zu der im backend/Dockerfile passen, sonst darf der Dienst nicht in ./data
# schreiben. Auf einem frischen Pi OS hat der erste Benutzer diese Nummer bereits.
if ! id "$BENUTZER" >/dev/null 2>&1; then
    useradd --uid 1000 --create-home --shell /bin/bash "$BENUTZER" 2>/dev/null \
        || useradd --create-home --shell /bin/bash "$BENUTZER"
fi
usermod -aG docker,video,input,render,tty "$BENUTZER"
chown -R "$BENUTZER":"$BENUTZER" "$WURZEL/data" 2>/dev/null || true

echo "== Kiosk-Dienst"
install -m 755 "$WURZEL/deploy/pi/kiekmap-kiosk" /usr/local/bin/
install -m 644 "$WURZEL/deploy/pi/kiekmap-kiosk.service" /etc/systemd/system/

echo "== USB-Sticks (fuer die Sicherung)"
install -m 755 "$WURZEL/deploy/pi/kiekmap-usb-mount" /usr/local/sbin/
install -m 644 "$WURZEL/deploy/pi/99-kiekmap-usb.rules" /etc/udev/rules.d/
udevadm control --reload

echo "== Bildschirm bleibt an"
# Zwei verschiedene Abschaltungen, beide muessen weg: die der Textkonsole (consoleblank) und die
# des Kernels beim Booten. Ohne sie ist der Bildschirm nach zehn Minuten schwarz, und niemand im
# Museum weiss, ob das Geraet noch laeuft.
CMDLINE=/boot/firmware/cmdline.txt
[ -f "$CMDLINE" ] || CMDLINE=/boot/cmdline.txt
if [ -f "$CMDLINE" ] && ! grep -q consoleblank=0 "$CMDLINE"; then
    sed -i 's/$/ consoleblank=0/' "$CMDLINE"
    echo "  consoleblank=0 ergaenzt -- wirkt nach dem naechsten Neustart."
fi

echo "== Dienste einschalten"
systemctl daemon-reload
systemctl enable kiekmap-kiosk

cat <<'ENDE'

Fertig. Was jetzt noch fehlt:

  1. .env anlegen (PIN, Version):
       cd /opt/kiekmap && cp deploy/.env.example .env
       cd backend && python3 -m app.cli pin      # Zeile in die .env eintragen
  2. Kartendaten und Ortsindex vom Entwicklungsrechner herueberkopieren:
       frontend/public/tiles/  und  data/places.json
  3. Container starten:
       cd /opt/kiekmap/deploy && docker compose up -d
  4. Neu starten und zusehen:
       sudo reboot

Nach dem Neustart sollte der Pi ohne Tastatur in der Karte landen.
ENDE
