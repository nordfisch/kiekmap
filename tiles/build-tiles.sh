#!/usr/bin/env bash
#
# Baut alles, was die Karte offline braucht:
#
#   frontend/public/tiles/map.pmtiles   Vektorkacheln der Region (eine Datei)
#   frontend/public/tiles/region.json   Kopie der Regionsdefinition, zur Laufzeit geholt
#   frontend/public/basemaps/fonts/     Beschriftungen
#   frontend/public/basemaps/sprites/   Symbole
#
# Die Schriften und Symbole sind der Punkt, an dem eine Offline-Karte sonst still zerbricht: der
# Protomaps-Stil verweist standardmaessig auf protomaps.github.io. Kacheln kaemen dann lokal,
# Beschriftungen aber gar nicht -- und das faellt erst auf, wenn das Geraet im Museum steht.
#
# Laeuft auf dem Entwicklungsrechner mit Internet, nicht auf dem Pi. Auf den Pi kommt nur das
# Ergebnis.

set -euo pipefail

WURZEL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGION="$WURZEL/tiles/region.json"
ZIEL="$WURZEL/frontend/public"

ASSETS_URL="https://github.com/protomaps/basemaps-assets/archive/refs/heads/main.zip"

rot()  { printf '\033[31m%s\033[0m\n' "$*" >&2; }
info() { printf '\033[36m%s\033[0m\n' "$*"; }

# --- Voraussetzungen --------------------------------------------------------

if ! command -v pmtiles >/dev/null 2>&1; then
  rot "Das Kommando 'pmtiles' fehlt."
  rot ""
  rot "  brew install pmtiles"
  rot ""
  rot "Alternativ von https://github.com/protomaps/go-pmtiles/releases herunterladen."
  exit 1
fi

for werkzeug in python3 curl unzip; do
  command -v "$werkzeug" >/dev/null 2>&1 || { rot "Das Kommando '$werkzeug' fehlt."; exit 1; }
done

# --- Region einlesen --------------------------------------------------------

eval "$(python3 - "$REGION" <<'PY'
import json, shlex, sys

region = json.load(open(sys.argv[1]))
min_lon, min_lat, max_lon, max_lat = region["bbox"]

# Etwas Rand um den Ausschnitt herum. Die bbox ist zugleich die Grenze, ueber die hinaus die Karte
# nicht geschoben werden kann -- ohne Rand liefe der Besucher am Anschlag gegen eine graue Flaeche.
RAND = 0.10
pad_lon = (max_lon - min_lon) * RAND
pad_lat = (max_lat - min_lat) * RAND
gepolstert = (min_lon - pad_lon, min_lat - pad_lat, max_lon + pad_lon, max_lat + pad_lat)

print(f"NAME={shlex.quote(region['name'])}")
print(f"BBOX={shlex.quote(','.join(f'{x:.5f}' for x in gepolstert))}")
print(f"MAXZOOM={shlex.quote(str(region['maxZoom']))}")
PY
)"

if [ "$NAME" = "PLATZHALTER" ]; then
  rot "tiles/region.json enthaelt noch den Platzhalter."
  rot "Bitte Name und bbox des Museumsorts eintragen, dann erneut ausfuehren."
  exit 1
fi

info "Region: $NAME"
info "Ausschnitt: $BBOX  (bis Zoom $MAXZOOM)"

mkdir -p "$ZIEL/tiles" "$ZIEL/basemaps"

# --- Kacheln ----------------------------------------------------------------
#
# Aus dem oeffentlichen Protomaps-Tagesbuild wird per Range-Request nur der Ausschnitt
# herausgeschnitten, der uns interessiert. Der Planet wird dabei nicht heruntergeladen.

DATUM="${PROTOMAPS_BUILD:-$(date -u -v-2d +%Y%m%d 2>/dev/null || date -u -d '2 days ago' +%Y%m%d)}"
QUELLE="https://build.protomaps.com/${DATUM}.pmtiles"

info "Kacheln aus dem Tagesbuild vom $DATUM schneiden ..."
pmtiles extract "$QUELLE" "$ZIEL/tiles/map.pmtiles" \
  --bbox="$BBOX" \
  --maxzoom="$MAXZOOM"

cp "$REGION" "$ZIEL/tiles/region.json"
# Auch ins Datenverzeichnis: dort kommt das Backend im Container heran und prueft damit, ob eine
# Verortung aus dem "Hilf mit"-Bereich ueberhaupt in der Region liegt.
mkdir -p "$WURZEL/data"
cp "$REGION" "$WURZEL/data/region.json"

# --- Schriften und Symbole --------------------------------------------------

if [ -d "$ZIEL/basemaps/fonts" ] && [ "${ERNEUERN:-}" != "1" ]; then
  info "Schriften und Symbole liegen bereits vor (ERNEUERN=1 erzwingt neues Laden)."
else
  info "Schriften und Symbole holen ..."
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  curl -fsSL "$ASSETS_URL" -o "$TMP/assets.zip"
  unzip -q "$TMP/assets.zip" -d "$TMP"
  rm -rf "$ZIEL/basemaps/fonts" "$ZIEL/basemaps/sprites"
  mv "$TMP/basemaps-assets-main/fonts" "$ZIEL/basemaps/fonts"
  mv "$TMP/basemaps-assets-main/sprites" "$ZIEL/basemaps/sprites"
fi

# --- Ergebnis ---------------------------------------------------------------

echo
info "Fertig."
du -sh "$ZIEL/tiles/map.pmtiles" "$ZIEL/basemaps" 2>/dev/null || true
echo
echo "Probe aufs Exempel: 'make dev' starten, dann im Browser das WLAN abschalten"
echo "und die Karte bewegen. Beschriftungen muessen sichtbar bleiben."
