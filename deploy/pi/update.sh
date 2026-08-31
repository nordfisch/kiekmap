#!/bin/sh
# Update without the internet -- from a USB stick.
#
#     sudo sh /opt/kiekmap/deploy/pi/update.sh /media/STICK/kiekmap-update
#
# The Pi in the museum hangs on no network. An update therefore arrives as a folder on a stick:
# the images as a tar file, plus the new map data if the region has changed.
#
# Such a folder is built on the development machine with:
#
#     make release to=/Volumes/STICK/kiekmap-update
#
# The collection is not touched. Whoever wants photos back takes the backup in the admin area --
# this only swaps the software.

set -eu

SOURCE="${1:-}"
ROOT="${KIEKMAP_ROOT:-/opt/kiekmap}"

[ "$(id -u)" -eq 0 ] || { echo "Please start with sudo." >&2; exit 1; }
[ -n "$SOURCE" ] && [ -d "$SOURCE" ] || {
    echo "Usage: $0 /media/STICK/kiekmap-update" >&2
    exit 1
}

IMAGES="$SOURCE/images.tar"
[ -f "$IMAGES" ] || { echo "$IMAGES is missing." >&2; exit 1; }

echo "== loading the images"
docker load -i "$IMAGES"

# Take the version from the stick, if it came along. Otherwise the old one stays in the .env --
# and a "docker compose up" would pull the old image back up.
if [ -f "$SOURCE/version" ]; then
    VERSION="$(cat "$SOURCE/version")"
    echo "== writing version $VERSION"
    if grep -q '^KIEKMAP_VERSION=' "$ROOT/.env" 2>/dev/null; then
        sed -i "s/^KIEKMAP_VERSION=.*/KIEKMAP_VERSION=$VERSION/" "$ROOT/.env"
    else
        echo "KIEKMAP_VERSION=$VERSION" >>"$ROOT/.env"
    fi
fi

if [ -d "$SOURCE/tiles" ]; then
    echo "== taking over the map data"
    # Beside it first, then rename: an aborted copy must not leave half a map file behind for the
    # device to start with.
    rm -rf "$ROOT/frontend/public/tiles.new"
    cp -r "$SOURCE/tiles" "$ROOT/frontend/public/tiles.new"
    rm -rf "$ROOT/frontend/public/tiles.old"
    [ -d "$ROOT/frontend/public/tiles" ] &&
        mv "$ROOT/frontend/public/tiles" "$ROOT/frontend/public/tiles.old"
    mv "$ROOT/frontend/public/tiles.new" "$ROOT/frontend/public/tiles"
fi

if [ -f "$SOURCE/places.json" ]; then
    echo "== taking over the place index"
    cp "$SOURCE/places.json" "$ROOT/data/places.json"
fi

echo "== restarting"
cd "$ROOT/deploy"
docker compose up -d

echo "== waiting for the API to answer"
ATTEMPT=0
until curl -sf --max-time 3 http://localhost/api/health >/dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    [ "$ATTEMPT" -gt 60 ] && { echo "The API does not come up -- see: docker compose logs" >&2; exit 1; }
    sleep 2
done

# The place index is loaded at startup only when the table is empty. After an update with a new
# places.json it has to be pulled in explicitly.
if [ -f "$SOURCE/places.json" ]; then
    echo "== reading the place index in again"
    docker compose exec -T backend python -m app.cli places
fi

echo "== restarting the kiosk"
systemctl restart kiekmap-kiosk

echo
echo "Done. The stick can be removed."
