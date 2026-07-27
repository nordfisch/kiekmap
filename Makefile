.DEFAULT_GOAL := help
.PHONY: help venv dev dev-backend test test-backend migrate revision lint prod prod-down clean

PYTHON  ?= python3.12
VENV    := backend/.venv
PY      := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
COMPOSE := docker compose -f deploy/docker-compose.yml --env-file .env

help:  ## Diese Uebersicht
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# --- Entwicklung ------------------------------------------------------------

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -e "backend[dev]"

venv: $(VENV)  ## Python-Umgebung anlegen

dev: dev-backend  ## Backend und Frontend mit Hot Reload (Frontend folgt in Stufe 2)

dev-backend: $(VENV)  ## Nur das Backend, Port 8000, Doku unter /api/docs
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

# --- Datenbank --------------------------------------------------------------

migrate: $(VENV)  ## Schemastand auf den neuesten Stand bringen
	cd backend && .venv/bin/alembic upgrade head

revision: $(VENV)  ## Neue Migration erzeugen: make revision m="Beschreibung"
	@test -n "$(m)" || { echo 'Bitte m="Beschreibung" angeben'; exit 1; }
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(m)"

# --- Pruefen ----------------------------------------------------------------

test: test-backend  ## Alle Tests

test-backend: $(VENV)
	cd backend && .venv/bin/pytest -q

lint: $(VENV)  ## Code-Stil pruefen
	$(VENV)/bin/ruff check backend
	$(VENV)/bin/ruff format --check backend

# --- Betrieb ----------------------------------------------------------------

.env:
	cp deploy/.env.example .env
	@echo "  .env aus der Vorlage angelegt -- bitte durchsehen."

prod: .env  ## Alles in Containern, so wie es auf dem Pi laeuft
	$(COMPOSE) up --build

prod-down: .env
	$(COMPOSE) down

clean:  ## Virtuelle Umgebung und Caches entfernen (Daten bleiben unberuehrt)
	rm -rf $(VENV) backend/.pytest_cache backend/.ruff_cache
	find backend -name __pycache__ -type d -prune -exec rm -rf {} +
