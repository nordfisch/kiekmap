# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    KIEKMAP_DATA_DIR=/data

WORKDIR /srv

# Dependencies first, so that a change to the code does not invalidate the install layer. On the
# Pi that is the difference between seconds and minutes per rebuild.
#
# From the lock file, not from pyproject.toml: that names lower bounds only, and a rebuild in a
# year would pull different versions than today's. On a device that stands offline and is touched
# once a year, something like that shows up only in the museum. Built with `make lock`.
#
# `pip install .` stood here before and did less than it looks like: `app/` is copied further down,
# so the package search found nothing and installed a distribution without content. What was ever
# pulled were the dependencies -- which is what this line does now, only traceably.
COPY requirements.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.lock

# The licence notices belong in the image, not only in the repository: they have to travel with
# every copy. Built by tools/build_notices.py and checked in, so that this build context is
# complete in itself -- the LICENSE at the project root lies outside it.
COPY THIRD-PARTY.txt ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Do not run as root. The UID has to match the file permissions of ./data on the host -- on
# Raspberry Pi OS the first user is 1000, hence exactly this number.
RUN useradd --uid 1000 --create-home kiekmap
USER kiekmap

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
