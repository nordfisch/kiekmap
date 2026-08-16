# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    KIEKMAP_DATA_DIR=/data

WORKDIR /srv

# Abhaengigkeiten zuerst, damit Codeaenderungen die Installationsschicht nicht ungueltig machen.
# Auf dem Pi ist das der Unterschied zwischen Sekunden und Minuten pro Neubau.
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install .

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
