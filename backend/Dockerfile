# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    KIEKMAP_DATA_DIR=/data

WORKDIR /srv

# Abhaengigkeiten zuerst, damit Codeaenderungen die Installationsschicht nicht ungueltig machen.
# Auf dem Pi ist das der Unterschied zwischen Sekunden und Minuten pro Neubau.
#
# Aus der Lockdatei, nicht aus pyproject.toml: Dort stehen nur untere Schranken, und ein Neubau in
# einem Jahr zoege andere Versionen als der heutige. Bei einem Geraet, das offline steht und einmal
# im Jahr angefasst wird, faellt so etwas erst im Museum auf. Erzeugt mit `make lock`.
#
# `pip install .` stand hier vorher und tat weniger, als es aussieht: `app/` wird erst weiter unten
# kopiert, die Paketsuche fand also nichts und installierte eine Distribution ohne Inhalt. Gezogen
# wurden immer nur die Abhaengigkeiten -- genau das tut die Zeile jetzt, nur nachvollziehbar.
COPY requirements.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.lock

# Die Lizenzhinweise gehoeren ins Abbild, nicht nur ins Repo: Sie muessen mit jeder Kopie
# mitgehen. Erzeugt von tools/build_notices.py, eingecheckt, damit dieser Kontext fuer sich
# vollstaendig ist -- die LICENSE der Projektwurzel liegt ausserhalb davon.
COPY THIRD-PARTY.txt ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Nicht als root laufen. Die UID muss zu den Dateirechten von ./data auf dem Host passen --
# auf Raspberry Pi OS ist der erste Benutzer 1000, deshalb genau diese Nummer.
RUN useradd --uid 1000 --create-home kiekmap
USER kiekmap

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
