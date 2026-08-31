.DEFAULT_GOAL := help
.PHONY: help venv node-check deps dev dev-backend dev-frontend test test-backend test-frontend \
        migrate revision seed seed-save empty lint docs-check notices notices-check check \
        tiles places build prod \
        prod-mac prod-down clean

PYTHON  ?= python3.12
VENV    := backend/.venv
PIP     := $(VENV)/bin/pip
COMPOSE := docker compose -f deploy/docker-compose.yml --env-file .env

help:  ## This overview
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# --- prerequisites -----------------------------------------------------------

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -e "backend[dev]"

venv: $(VENV)  ## create the Python environment

# Vite 6 runs from Node 18 on. Node 18 is no longer maintained, hence the notice -- without the
# check a Node that is too old fails with a syntax message that does not show that only the
# version is the problem.
# The continuation lines stand outside the quotes, and that is not style but necessary: inside
# single quotes the shell does not remove a backslash line ending, so node gets a real backslash.
# Node 18 forgave that; Node 22 evaluates -e through a TypeScript-capable parser and aborts --
# with the very version this check itself recommends. Found by the first CI run on 25 August 2026.
node-check:
	@v=$$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null) || \
		{ echo "Node is missing -- 18 or newer is needed."; exit 1; }; \
	if [ "$$v" -lt 18 ]; then \
		printf '\033[31mNode %s is too old, 18 or newer is needed.\033[0m\n' "$$(node -v)"; \
		echo "  nvm install 22 && nvm alias default 22"; \
		exit 1; \
	elif [ "$$v" -lt 20 ]; then \
		printf '\033[33mNote: Node %s is no longer maintained. Recommended: nvm install 22\033[0m\n' "$$(node -v)"; \
	fi

frontend/node_modules: frontend/package.json | node-check
	cd frontend && npm install --no-audit --no-fund
	@touch frontend/node_modules

deps: $(VENV) frontend/node_modules  ## install all dependencies

# --- development -------------------------------------------------------------

# The schema state first: inside the container the entrypoint pulls it forward, on the
# development machine nobody does. On 12 August 2026 a database therefore ran for two days that
# nothing could write to any more -- see docs/decisions.md, point 42.
dev: deps migrate  ## backend and frontend with hot reload
	@trap 'kill 0' EXIT INT TERM; \
	( cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000 ) & \
	( cd frontend && npm run dev ) & \
	wait

dev-backend: migrate  ## the backend only, port 8000, docs under /api/docs
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend: frontend/node_modules  ## the frontend only, port 5173
	cd frontend && npm run dev

# --- map ---------------------------------------------------------------------

tiles:  ## build the offline map, fonts and sprites for the region in tiles/region.json
	./tiles/build-tiles.sh

places: $(VENV)  ## build the gazetteer for the place search and read it in
	python3 ./tiles/build-places.py
	cd backend && .venv/bin/python -m app.cli places

# --- database ----------------------------------------------------------------

migrate: $(VENV)  ## bring the schema up to date
	cd backend && .venv/bin/alembic upgrade head

revision: $(VENV)  ## create a migration: make revision m="description"
	@test -n "$(m)" || { echo 'Please give m="description"'; exit 1; }
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(m)"

# --- sample collection -------------------------------------------------------
#
# A development state that cannot be brought back is none. `make seed` throws the collection away
# and builds it anew from seed/ -- that is the point, not an accident.

seed: migrate  ## build the sample collection from seed/ (deletes the current one!)
	cd backend && .venv/bin/python -m app.cli seed-load

seed-save: $(VENV)  ## save the running collection to seed/
	cd backend && .venv/bin/python -m app.cli seed-export

# --- emptying the collection -------------------------------------------------
#
# The step before an initial import -- and the only one here from which no way leads back.
# `make seed` throws the collection away too, but puts something in its place; this target leaves
# nothing. So it asks, and wants the number of photos typed back.
#
# Deliberately not called `clear`: `make clean` stands a line below, is harmless, and two targets
# that differ by one letter would be a trap.

empty: migrate  ## delete the whole photo collection (no way back!)
	cd backend && .venv/bin/python -m app.cli empty

# --- checking ----------------------------------------------------------------

test: test-backend test-tiles test-frontend  ## all tests

test-backend: $(VENV)
	cd backend && .venv/bin/pytest -q

# The map build never runs on the Pi, but its arithmetic goes wrong just as silently as the
# backend's -- a place index with wrong points shows up only in the museum.
test-tiles: $(VENV)
	$(VENV)/bin/pytest -q tiles

test-frontend: frontend/node_modules
	cd frontend && npm run typecheck && npm test

lint: $(VENV)  ## check the code style
	$(VENV)/bin/ruff check backend tiles tools
	$(VENV)/bin/ruff format --check backend tiles tools

# The checks that read files no test ever sees: the language rule, the links inside docs/, the
# way of every setting into the container, and the bookkeeping of the decisions over their own
# numbers.
#
# Pure readers, therefore without venv and without node_modules -- python3 from the system is
# enough. Together they need under a second, and that is exactly why they also hang in the git
# hook under .githooks/. Why they are needed at all: docs/decisions.md, point 59.
docs-check:  ## language rule, links, settings, numbers, register, version
	@python3 tools/language_check.py
	@python3 tools/check_anchors.py
	@python3 tools/check_settings.py
	@python3 tools/check_numbers.py
	@python3 tools/build_register.py --check
	@python3 tools/set_version.py --check

# The register at the start of docs/history.de.md. Generated instead of maintained, for the same
# reason as the licence notices: ninety lines by hand are wrong within a month. See
# docs/decisions.md.
register:  ## rewrite the register in docs/history.de.md
	@python3 tools/build_register.py

# One number, two files. The tag is not the source but has to match it -- a check against
# `git describe` would be red in the window in which the version is already raised but the tag is
# not yet set. And that is exactly where the commit hook runs.
version:  ## show the version, or set it: make version v=0.8.0
	@if [ -n "$(v)" ]; then python3 tools/set_version.py "$(v)"; else python3 tools/set_version.py; fi

# The licence notices that have to travel with every artefact -- MIT and BSD demand the copyright
# notice in *every* copy, and a bundled index-*.js is a copy.
#
# Generated instead of maintained, but checked in: every Docker context stays complete in itself,
# and a new dependency shows up in the diff where somebody sees it. See docs/licensing.md.
# With the Python of the venv, not that of the system -- the only one of the tools. The six checks
# are pure readers and manage with the standard library; this one reads the metadata of the
# installed packages and evaluates their environment markers with `packaging`. So it needs the
# venv anyway. On a machine whose system Python happens to bring `packaging` along that does not
# show -- in a fresh CI it does.
notices: deps  ## build the licence notices of the bundled packages
	@$(VENV)/bin/python tools/build_notices.py

# Pinned backend dependencies for the image. pyproject.toml names lower bounds only; without this
# file a rebuild in a year would pull different versions. --universal, because it is produced on a
# Mac here and installed on Linux in the image.
# Bring the venv to the state of the lock file. The markers are removed on the way: greenlet
# occurs in the image but never on a Mac -- and without the installed licence file
# tools/build_notices.py cannot write its notice.
deps-lock: $(VENV)  ## bring the venv to the versions of the lock file
	@command -v uv >/dev/null || { echo "uv is missing: brew install uv"; exit 1; }
	@sed 's/ ;.*//' backend/requirements.lock > /tmp/kiekmap-lock-without-markers.txt
	VIRTUAL_ENV=backend/.venv uv pip install -q -r /tmp/kiekmap-lock-without-markers.txt
	@rm -f /tmp/kiekmap-lock-without-markers.txt
	@echo "  venv at the state of the lock file."

lock:  ## resolve backend/requirements.lock anew (needs uv)
	@command -v uv >/dev/null || { echo "uv is missing: brew install uv"; exit 1; }
	uv pip compile --universal --python-version 3.12 --no-header \
	    -o backend/requirements.lock backend/pyproject.toml

notices-check: deps
	@$(VENV)/bin/python tools/build_notices.py --check

# The target before a commit. The fast ones first: whoever broke the style should learn that
# after two seconds and not after ten.
check: lint docs-check notices-check test  ## check everything that should run before a commit

# The folder deploy/pi/update.sh expects. Aborts on a dirty working tree or a missing tag: a stick
# that belongs to no commit cannot be traced back later.
release:  ## build the update stick: make release [to=/Volumes/STICK/kiekmap-update] [map=1]
	@python3 tools/build_release.py $(if $(to),--to "$(to)") $(if $(map),--with-map)

build: frontend/node_modules notices  ## build the frontend bundle (result in frontend/dist)
	cd frontend && npm run build

# --- operation ---------------------------------------------------------------

.env:
	cp deploy/.env.example .env
	@echo "  .env created from the template -- please look it over."

prod: .env  ## everything in containers, the way it runs on the Pi
	$(COMPOSE) up --build

# On the Mac /media and the mount propagation rshared are missing. Why, stands in the file.
# KIEKMAP_PROD_DATA optionally points at a copy of the collection -- recommended, because the
# entrypoint pulls the schema forward on every start.
prod-mac: .env  ## like prod, but with the paths of the development Mac
	$(COMPOSE) -f deploy/docker-compose.mac.yml up --build

prod-down: .env
	$(COMPOSE) down

clean:  ## remove environments and caches (data and map stay untouched)
	rm -rf $(VENV) backend/.pytest_cache backend/.ruff_cache frontend/node_modules frontend/dist
	find backend -name __pycache__ -type d -prune -exec rm -rf {} +
