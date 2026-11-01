#!/bin/sh
# Updates a device that is already set up, from a bundle.
#
#     sudo sh ~/kiekmap/deploy/pi/update.sh                     copied over by `make deploy`
#     sudo sh /media/STICK/kiekmap/deploy/pi/update.sh          from a stick
#
# The bundle is built on the development machine with `make deploy` (or `make deploy
# to=/Volumes/STICK/kiekmap` for a stick). This script finds it beside itself.
#
# **The collection stays.** data/ is not touched beyond the place index, and the .env not beyond
# KIEKMAP_VERSION. Before anything changes, the database is copied to pre-update/<old version>/.

set -eu

. "$(dirname "$0")/common.sh"

require_root
check_bundle

[ -f "$ROOT/.env" ] && [ -d "$ROOT/data" ] ||
    fail "$ROOT is not set up yet. For a first installation:
  sudo sh $BUNDLE/deploy/pi/setup-pi.sh"

OLD="$(installed_version)"
echo "Updating from ${OLD:-unknown} to $VERSION."

say "stopping the containers"
cd "$ROOT"
$COMPOSE stop

# A copy of the database before the new version migrates it. The migrations run forward only, and
# the previous image cannot read a schema it does not know. Photos are not copied: no update
# changes them, and they would fill the card. Two snapshots are kept.
say "a snapshot of the database"
SNAPSHOT="$ROOT/pre-update/${OLD:-unknown}"
mkdir -p "$SNAPSHOT"
for f in kiekmap.db kiekmap.db-wal kiekmap.db-shm; do
    if [ -f "$ROOT/data/$f" ]; then cp -p "$ROOT/data/$f" "$SNAPSHOT/"; fi
done
# shellcheck disable=SC2012 -- the names are version numbers, no spaces in them
ls -1t "$ROOT/pre-update" | tail -n +3 | while read -r stale; do
    rm -rf "$ROOT/pre-update/$stale"
done

install_software
set_version
protect_env

PLACES_CHANGED=
if ! cmp -s "$BUNDLE/places.json" "$ROOT/data/places.json"; then
    say "a new place index"
    cp "$BUNDLE/places.json" "$ROOT/data/places.json"
    PLACES_CHANGED=1
fi

install_system
load_images
start

# The place index is loaded at startup only when the table is empty. A new one has to be pulled in.
if [ -n "$PLACES_CHANGED" ]; then
    say "reading the place index in again"
    $COMPOSE exec -T backend python -m app.cli places
fi

restart_kiosk

say "removing old images"
# The new version and the one before it stay, so that going back needs no bundle.
for name in kiekmap-backend kiekmap-frontend; do
    docker image ls "$name" --format '{{.Tag}}' | while read -r tag; do
        [ "$tag" = "$VERSION" ] || [ "$tag" = "$OLD" ] || docker image rm "$name:$tag" >/dev/null
    done
done

cat <<END

Done. $VERSION runs, the collection is unchanged.

Going back to ${OLD:-the previous version}, should it be needed -- its image is still here:
  cd $ROOT && sudo $COMPOSE stop
  sudo rm -f data/kiekmap.db-wal data/kiekmap.db-shm
  sudo cp -p $SNAPSHOT/kiekmap.db* data/
  sudo sed -i 's/^KIEKMAP_VERSION=.*/KIEKMAP_VERSION=$OLD/' .env
  sudo $COMPOSE up -d
Whatever was entered after the update is lost that way. The rm matters: a newer -wal file beside
the older database would damage it.

The folder $BUNDLE is no longer needed and can be deleted.
END
