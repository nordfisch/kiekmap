#!/usr/bin/env bash
#
# Builds everything the map needs offline:
#
#   frontend/public/tiles/map.pmtiles   vector tiles of the region (one file)
#   frontend/public/tiles/region.json   copy of the region definition, fetched at runtime
#   frontend/public/basemaps/fonts/     labels
#   frontend/public/basemaps/sprites/   sprites
#
# The fonts and sprites are where an offline map otherwise breaks silently: the Protomaps style
# points at protomaps.github.io by default. Tiles would then come locally, labels not at all --
# and that shows only once the device stands in the museum.
#
# Runs on the development machine with internet, not on the Pi. Only the result goes to the Pi.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGION="$ROOT/tiles/region.json"
TARGET="$ROOT/frontend/public"

ASSETS_URL="https://github.com/protomaps/basemaps-assets/archive/refs/heads/main.zip"

red()  { printf '\033[31m%s\033[0m\n' "$*" >&2; }
info() { printf '\033[36m%s\033[0m\n' "$*"; }

# --- prerequisites ----------------------------------------------------------

if ! command -v pmtiles >/dev/null 2>&1; then
  red "The command 'pmtiles' is missing."
  red ""
  red "  brew install pmtiles"
  red ""
  red "Or download it from https://github.com/protomaps/go-pmtiles/releases."
  exit 1
fi

for tool in python3 curl unzip; do
  command -v "$tool" >/dev/null 2>&1 || { red "The command '$tool' is missing."; exit 1; }
done

# --- reading the region -----------------------------------------------------

eval "$(python3 - "$REGION" <<'PY'
import json, shlex, sys

region = json.load(open(sys.argv[1]))
min_lon, min_lat, max_lon, max_lat = region["bbox"]

# A little margin around the extent. The bbox is at the same time the boundary beyond which the
# map cannot be pushed -- without a margin the visitor would run against a grey surface at the end.
MARGIN = 0.10
pad_lon = (max_lon - min_lon) * MARGIN
pad_lat = (max_lat - min_lat) * MARGIN
padded = (min_lon - pad_lon, min_lat - pad_lat, max_lon + pad_lon, max_lat + pad_lat)

print(f"NAME={shlex.quote(region['name'])}")
print(f"BBOX={shlex.quote(','.join(f'{x:.5f}' for x in padded))}")
print(f"MAXZOOM={shlex.quote(str(region['maxZoom']))}")
PY
)"

if [ "$NAME" = "PLACEHOLDER" ]; then
  red "tiles/region.json still holds the placeholder."
  red "Please enter the name and bbox of the museum's place, then run it again."
  exit 1
fi

info "Region: $NAME"
info "Extent: $BBOX  (up to zoom $MAXZOOM)"

mkdir -p "$TARGET/tiles" "$TARGET/basemaps"

# --- tiles ------------------------------------------------------------------
#
# Only the extent we care about is cut out of the public Protomaps daily build, by range request.
# The planet is not downloaded on the way.

DAY="${PROTOMAPS_BUILD:-$(date -u -v-2d +%Y%m%d 2>/dev/null || date -u -d '2 days ago' +%Y%m%d)}"
SOURCE="https://build.protomaps.com/${DAY}.pmtiles"

info "Cutting tiles out of the daily build of $DAY ..."
pmtiles extract "$SOURCE" "$TARGET/tiles/map.pmtiles" \
  --bbox="$BBOX" \
  --maxzoom="$MAXZOOM"

cp "$REGION" "$TARGET/tiles/region.json"
# Into the data directory as well: that is where the backend reaches it inside the container, and
# checks with it whether a location from the "Hilf mit" panel lies in the region at all.
mkdir -p "$ROOT/data"
cp "$REGION" "$ROOT/data/region.json"

# --- fonts and sprites ------------------------------------------------------

if [ -d "$TARGET/basemaps/fonts" ] && [ "${REFRESH:-}" != "1" ]; then
  info "Fonts and sprites are already there (REFRESH=1 forces a new download)."
else
  info "Fetching fonts and sprites ..."
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  curl -fsSL "$ASSETS_URL" -o "$TMP/assets.zip"
  unzip -q "$TMP/assets.zip" -d "$TMP"
  rm -rf "$TARGET/basemaps/fonts" "$TARGET/basemaps/sprites"
  mv "$TMP/basemaps-assets-main/fonts" "$TARGET/basemaps/fonts"
  mv "$TMP/basemaps-assets-main/sprites" "$TARGET/basemaps/sprites"
  # Take the licence of the archive along. That the fonts were covered was luck so far: their
  # OFL.txt lies *inside* fonts/. The sprites (MIT, derived from tangrams/icons) carried no text
  # at all, because only the two folders were pulled out here and the rest vanished with the
  # temporary directory. See docs/licensing.md.
  for LICENCE in "$TMP/basemaps-assets-main"/LICENSE*; do
    [ -f "$LICENCE" ] && cp "$LICENCE" "$TARGET/basemaps/"
  done
fi

# --- result -----------------------------------------------------------------

echo
info "Done."
du -sh "$TARGET/tiles/map.pmtiles" "$TARGET/basemaps" 2>/dev/null || true
echo
echo "The test: start 'make dev', then switch the wifi off in the browser and move the map."
echo "The labels have to stay visible."
