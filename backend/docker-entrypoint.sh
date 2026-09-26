#!/bin/sh
# Bring the schema forward before the application starts.
#
# This belongs here and not in a maintenance script: the Pi is updated from a USB stick, and nobody
# on site should have to remember to run a migration by hand afterwards.
set -eu

echo "Kiekmap: checking the schema ..."
alembic upgrade head

exec "$@"
