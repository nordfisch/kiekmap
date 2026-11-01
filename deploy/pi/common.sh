# What setup-pi.sh and update.sh share. Sourced, not run.
#
# Both scripts run from a bundle that `make deploy` built on the development machine and copied
# over (or put onto a stick). The bundle holds the images, the map, the place index, deploy/ and
# the Pi's .env as `env`. The software is copied out of it into $ROOT; the bundle itself is not
# needed afterwards.
#
# Nothing here touches the collection. data/ is created, handed to UID 1000 and given the place
# index; the photos and the database are the backend's business.

ROOT="${KIEKMAP_ROOT:-/opt/kiekmap}"
USER_NAME="${KIEKMAP_USER:-kiekmap}"

# The backend in the container writes as UID 1000 (backend/Dockerfile). By number, not by the user
# name: when the first user of the Pi already carries 1000, `kiekmap` gets 1001, and a chown to
# the name leaves the backend in front of a folder it cannot write.
SERVICE_UID=1000

# The bundle is the folder two levels above this file: <bundle>/deploy/pi/common.sh.
BUNDLE="$(cd "$(dirname "$0")/../.." && pwd)"

# From the project root and with --env-file, not from deploy/: Compose reads the .env from the
# directory it is started in, and the .env lies one above the compose file. Started from deploy/
# the KIEKMAP_VERSION just written would go unread, ${KIEKMAP_VERSION:-dev} would fall back to
# `dev` -- and since the compose file carries a `build:`, a missing image would make the Pi build
# the frontend itself, npm and all. Measured on 8 September 2026.
COMPOSE="docker compose -f $ROOT/deploy/docker-compose.yml --env-file $ROOT/.env"

say() { printf '== %s\n' "$*"; }
fail() { printf '%s\n' "$*" >&2; exit 1; }

require_root() {
    [ "$(id -u)" -eq 0 ] || fail "Please start with sudo."
}

# Run the script again as a transient systemd unit, and follow its output from here.
#
# Started over SSH, a script dies with the connection. On the first Pi the Wi-Fi dropped during an
# update, and the shell went with it. Cut off between `compose stop` and `compose up`, a script
# leaves the containers stopped, and a stopped container stays down at the next boot. As a unit it
# runs to the end whatever happens to the connection; this terminal only reads the journal.
#
# Called after the checks that refuse at once, so that a refusal is printed straight away.
detach() {
    [ -n "${KIEKMAP_DETACHED:-}" ] && return 0
    UNIT="kiekmap-$(basename "$0" .sh)"
    SCRIPT="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
    systemctl is-active -q "$UNIT" &&
        fail "$UNIT is running already. Its output: journalctl -fu $UNIT"
    systemctl stop "$UNIT" 2>/dev/null || true
    systemctl reset-failed "$UNIT" 2>/dev/null || true

    SINCE="$(date +%s)"
    # RemainAfterExit keeps the unit, and with it the exit status, after the script has ended.
    systemd-run --quiet --unit="$UNIT" --property=RemainAfterExit=yes \
        --setenv=KIEKMAP_DETACHED=1 --setenv=KIEKMAP_ROOT="$ROOT" \
        --setenv=KIEKMAP_USER="$USER_NAME" --setenv=DEBIAN_FRONTEND=noninteractive \
        /bin/sh "$SCRIPT"
    echo "Runs as $UNIT and carries on if this connection drops."
    echo "Its output, later or from another shell:  journalctl -u $UNIT"
    echo
    journalctl -f -o cat -u "$UNIT" --since "@$SINCE" &
    FOLLOWER=$!
    while [ "$(systemctl show -p MainPID --value "$UNIT")" != 0 ]; do sleep 1; done
    # The last lines need a moment to reach the journal.
    sleep 2
    kill "$FOLLOWER" 2>/dev/null || true

    STATUS="$(systemctl show -p ExecMainStatus --value "$UNIT")"
    # Stopping removes the transient unit. Only a failed one needs its state cleared as well;
    # asking about it once it is gone makes systemd log "Failed to open /run/systemd/transient".
    if systemctl is-failed -q "$UNIT"; then
        systemctl reset-failed "$UNIT"
    else
        systemctl stop "$UNIT"
    fi
    exit "${STATUS:-1}"
}

check_bundle() {
    for f in version images.tar env places.json tiles deploy/docker-compose.yml; do
        [ -e "$BUNDLE/$f" ] || fail "$BUNDLE/$f is missing -- this is not a complete bundle.
Build it on the development machine with: make deploy"
    done
    VERSION="$(cat "$BUNDLE/version")"
}

# The installed version, read from the .env. Empty on a device without one.
installed_version() {
    sed -n 's/^KIEKMAP_VERSION=//p' "$ROOT/.env" 2>/dev/null | tail -n 1
}

# deploy/ and the map out of the bundle. Each goes beside the old one first and is then renamed:
# an aborted copy must not leave half a map file behind for the device to start with.
install_software() {
    mkdir -p "$ROOT/frontend/public"
    swap "$BUNDLE/deploy" "$ROOT/deploy"
    swap "$BUNDLE/tiles" "$ROOT/frontend/public/tiles"
}

swap() {
    rm -rf "$2.new" "$2.old"
    cp -r "$1" "$2.new"
    [ -e "$2" ] && mv "$2" "$2.old"
    mv "$2.new" "$2"
    rm -rf "$2.old"
}

# Readable for the docker group and nobody else: it holds the PIN hash. Compose runs as root or as
# a member of that group, and either may read it; the backend gets its values from Compose.
protect_env() {
    chown root:docker "$ROOT/.env"
    chmod 640 "$ROOT/.env"
}

set_version() {
    if grep -q '^KIEKMAP_VERSION=' "$ROOT/.env"; then
        sed -i "s/^KIEKMAP_VERSION=.*/KIEKMAP_VERSION=$VERSION/" "$ROOT/.env"
    else
        printf 'KIEKMAP_VERSION=%s\n' "$VERSION" >>"$ROOT/.env"
    fi
}

# The units, the udev rule and the watcher of the off button. Run on every update as well, so
# that a changed unit reaches a device that is already installed.
install_system() {
    say "kiosk service"
    install -m 755 "$ROOT/deploy/pi/kiekmap-kiosk" /usr/local/bin/
    install -m 644 "$ROOT/deploy/pi/kiekmap-kiosk.service" /etc/systemd/system/

    say "USB sticks (for the backup)"
    install -m 755 "$ROOT/deploy/pi/kiekmap-usb-mount" /usr/local/sbin/
    install -m 644 "$ROOT/deploy/pi/99-kiekmap-usb.rules" /etc/udev/rules.d/
    udevadm control --reload

    say "switching off from the admin area"
    install -m 755 "$ROOT/deploy/pi/kiekmap-shutdown" /usr/local/sbin/
    install -m 644 "$ROOT/deploy/pi/kiekmap-shutdown.path" /etc/systemd/system/
    install -m 644 "$ROOT/deploy/pi/kiekmap-shutdown.service" /etc/systemd/system/
    # The two units carry the default path; a unit file cannot read KIEKMAP_ROOT.
    if [ "$ROOT" != /opt/kiekmap ]; then
        sed -i "s#/opt/kiekmap#$ROOT#g" /etc/systemd/system/kiekmap-shutdown.path \
            /etc/systemd/system/kiekmap-shutdown.service
    fi

    # What the backend asks about before it offers to switch anything off. The same program runs
    # on a development machine and online behind Caddy, and there nothing would act on the request.
    mkdir -p "$ROOT/data"
    printf 'kiekmap-shutdown.path is installed on this host.\n' >"$ROOT/data/shutdown-watcher"
    chown -R "$SERVICE_UID:$SERVICE_UID" "$ROOT/data"

    systemctl daemon-reload
    systemctl enable kiekmap-kiosk
    # --now, so that the button in the admin area works without a restart.
    systemctl enable --now kiekmap-shutdown.path
}

load_images() {
    say "loading the images ($VERSION)"
    docker load -i "$BUNDLE/images.tar"
}

# Start, wait for the API, and check that the containers run the images of this bundle. The last
# check is the one that matters: a version left behind in the .env starts the old images, and the
# API would answer all the same.
start() {
    say "starting"
    cd "$ROOT"
    $COMPOSE up -d

    say "waiting for the API to answer"
    ATTEMPT=0
    until curl -sf --max-time 3 http://localhost/api/health >/dev/null 2>&1; do
        ATTEMPT=$((ATTEMPT + 1))
        [ "$ATTEMPT" -gt 60 ] && fail "The API does not come up -- see: $COMPOSE logs backend"
        sleep 2
    done

    RUNNING="$(docker inspect --format '{{.Config.Image}}' "$($COMPOSE ps -q backend)")"
    [ "$RUNNING" = "kiekmap-backend:$VERSION" ] ||
        fail "The backend runs $RUNNING, not kiekmap-backend:$VERSION. Check KIEKMAP_VERSION in $ROOT/.env."
}

restart_kiosk() {
    say "restarting the kiosk"
    systemctl restart kiekmap-kiosk
}
