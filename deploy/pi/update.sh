#!/bin/sh
# Update ohne Internet -- vom USB-Stick.
#
#     sudo sh /opt/photomap/deploy/pi/update.sh /media/STICK/photomap-update
#
# Der Pi im Museum haengt an keinem Netz. Ein Update kommt deshalb als Ordner auf einem Stick:
# die Abbilder als Tar-Datei, dazu die neuen Kartendaten, falls sich die Region geaendert hat.
#
# Erzeugt wird so ein Ordner auf dem Entwicklungsrechner mit:
#
#     docker save photomap-backend:v1.2 photomap-frontend:v1.2 -o abbilder.tar
#     cp -r frontend/public/tiles data/places.json <Stick>/photomap-update/
#
# Der Bestand wird dabei nicht angefasst. Wer Fotos zurueckholen will, nimmt die Sicherung im
# Admin-Bereich -- das hier tauscht nur die Software.

set -eu

QUELLE="${1:-}"
WURZEL="${PHOTOMAP_ROOT:-/opt/photomap}"

[ "$(id -u)" -eq 0 ] || { echo "Bitte mit sudo starten." >&2; exit 1; }
[ -n "$QUELLE" ] && [ -d "$QUELLE" ] || {
    echo "Aufruf: $0 /media/STICK/photomap-update" >&2
    exit 1
}

ABBILDER="$QUELLE/abbilder.tar"
[ -f "$ABBILDER" ] || { echo "$ABBILDER fehlt." >&2; exit 1; }

echo "== Abbilder einlesen"
docker load -i "$ABBILDER"

# Version aus dem Stick uebernehmen, falls dabei. Sonst bleibt die alte in der .env stehen --
# und ein "docker compose up" zoege wieder das alte Abbild hoch.
if [ -f "$QUELLE/version" ]; then
    VERSION="$(cat "$QUELLE/version")"
    echo "== Version $VERSION eintragen"
    if grep -q '^PHOTOMAP_VERSION=' "$WURZEL/.env" 2>/dev/null; then
        sed -i "s/^PHOTOMAP_VERSION=.*/PHOTOMAP_VERSION=$VERSION/" "$WURZEL/.env"
    else
        echo "PHOTOMAP_VERSION=$VERSION" >>"$WURZEL/.env"
    fi
fi

if [ -d "$QUELLE/tiles" ]; then
    echo "== Kartendaten uebernehmen"
    # Erst daneben, dann umbenennen: ein abgebrochenes Kopieren darf keine halbe Kartendatei
    # hinterlassen, mit der das Geraet dann startet.
    rm -rf "$WURZEL/frontend/public/tiles.neu"
    cp -r "$QUELLE/tiles" "$WURZEL/frontend/public/tiles.neu"
    rm -rf "$WURZEL/frontend/public/tiles.alt"
    [ -d "$WURZEL/frontend/public/tiles" ] &&
        mv "$WURZEL/frontend/public/tiles" "$WURZEL/frontend/public/tiles.alt"
    mv "$WURZEL/frontend/public/tiles.neu" "$WURZEL/frontend/public/tiles"
fi

if [ -f "$QUELLE/places.json" ]; then
    echo "== Ortsindex uebernehmen"
    cp "$QUELLE/places.json" "$WURZEL/data/places.json"
fi

echo "== Neu starten"
cd "$WURZEL/deploy"
docker compose up -d

echo "== Warten, bis die API antwortet"
VERSUCH=0
until curl -sf --max-time 3 http://localhost/api/health >/dev/null 2>&1; do
    VERSUCH=$((VERSUCH + 1))
    [ "$VERSUCH" -gt 60 ] && { echo "API kommt nicht hoch -- siehe: docker compose logs" >&2; exit 1; }
    sleep 2
done

# Der Ortsindex wird beim Start nur geladen, wenn die Tabelle leer ist. Nach einem Update mit
# neuer places.json muss er ausdruecklich nachgezogen werden.
if [ -f "$QUELLE/places.json" ]; then
    echo "== Ortsindex neu einlesen"
    docker compose exec -T backend python -m app.cli places
fi

echo "== Kiosk neu starten"
systemctl restart photomap-kiosk

echo
echo "Fertig. Der Stick kann abgezogen werden."
