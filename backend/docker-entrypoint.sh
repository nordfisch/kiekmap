#!/bin/sh
# Schemastand nachziehen, bevor die Anwendung startet.
#
# Das gehoert hierhin und nicht in ein Wartungsskript: auf dem Pi wird per USB-Stick aktualisiert,
# und niemand vor Ort soll daran denken muessen, danach noch eine Migration von Hand anzustossen.
set -eu

echo "Photomap: Schemastand pruefen ..."
alembic upgrade head

exec "$@"
