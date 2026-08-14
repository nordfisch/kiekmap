.DEFAULT_GOAL := help
.PHONY: help venv node-check deps dev dev-backend dev-frontend test test-backend test-frontend \
        migrate revision seed seed-save empty lint tiles places build prod prod-mac prod-down clean

PYTHON  ?= python3.12
VENV    := backend/.venv
PIP     := $(VENV)/bin/pip
COMPOSE := docker compose -f deploy/docker-compose.yml --env-file .env

help:  ## Diese Uebersicht
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# --- Voraussetzungen --------------------------------------------------------

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -e "backend[dev]"

venv: $(VENV)  ## Python-Umgebung anlegen

# Vite 6 laeuft ab Node 18. Node 18 wird allerdings nicht mehr gepflegt, daher der Hinweis --
# ohne die Pruefung scheitert ein zu altes Node mit einer Syntaxmeldung, der man nicht ansieht,
# dass nur die Version das Problem ist.
node-check:
	@node -e 'const v=+process.versions.node.split(".")[0]; \
		if (v < 18) { \
			console.error("\033[31mNode " + process.versions.node + " ist zu alt, gebraucht wird 18 oder neuer.\033[0m"); \
			console.error("  nvm install 22 && nvm alias default 22"); \
			process.exit(1); \
		} else if (v < 20) { \
			console.error("\033[33mHinweis: Node " + process.versions.node + " wird nicht mehr gepflegt. Empfohlen: nvm install 22\033[0m"); \
		}'

frontend/node_modules: frontend/package.json | node-check
	cd frontend && npm install --no-audit --no-fund
	@touch frontend/node_modules

deps: $(VENV) frontend/node_modules  ## Alle Abhaengigkeiten installieren

# --- Entwicklung ------------------------------------------------------------

dev: deps  ## Backend und Frontend mit Hot Reload
	@trap 'kill 0' EXIT INT TERM; \
	( cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000 ) & \
	( cd frontend && npm run dev ) & \
	wait

dev-backend: $(VENV)  ## Nur das Backend, Port 8000, Doku unter /api/docs
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend: frontend/node_modules  ## Nur das Frontend, Port 5173
	cd frontend && npm run dev

# --- Karte ------------------------------------------------------------------

tiles:  ## Offline-Karte, Schriften und Symbole fuer die Region in tiles/region.json bauen
	./tiles/build-tiles.sh

places: $(VENV)  ## Ortsverzeichnis fuer die Ortssuche bauen und einlesen
	python3 ./tiles/build-places.py
	cd backend && .venv/bin/python -m app.cli places

# --- Datenbank --------------------------------------------------------------

migrate: $(VENV)  ## Schemastand auf den neuesten Stand bringen
	cd backend && .venv/bin/alembic upgrade head

revision: $(VENV)  ## Neue Migration erzeugen: make revision m="Beschreibung"
	@test -n "$(m)" || { echo 'Bitte m="Beschreibung" angeben'; exit 1; }
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(m)"

# --- Beispielbestand --------------------------------------------------------
#
# Ein Entwicklungsstand, den man nicht zurueckholen kann, ist keiner. `make seed` wirft den
# Bestand weg und baut ihn aus seed/ neu auf -- das ist der Punkt, nicht ein Versehen.

seed: migrate  ## Beispielbestand aus seed/ herstellen (loescht den vorhandenen!)
	cd backend && .venv/bin/python -m app.cli seed-load

seed-save: $(VENV)  ## Den laufenden Bestand nach seed/ sichern
	cd backend && .venv/bin/python -m app.cli seed-export

# --- Bestand leeren ---------------------------------------------------------
#
# Der Schritt vor einem Erstimport -- und der einzige hier, aus dem kein Weg zurueckfuehrt.
# `make seed` wirft den Bestand auch weg, setzt aber etwas an seine Stelle; dieses Ziel laesst
# nichts. Deshalb fragt es nach und will die Anzahl der Fotos getippt haben.
#
# Absichtlich nicht `clear` genannt: `make clean` steht eine Zeile weiter unten, ist harmlos, und
# zwei Ziele, die sich um einen Buchstaben unterscheiden, waeren eine Falle.

empty: migrate  ## Den ganzen Fotobestand loeschen (nicht rueckholbar!)
	cd backend && .venv/bin/python -m app.cli empty

# --- Pruefen ----------------------------------------------------------------

test: test-backend test-tiles test-frontend  ## Alle Tests

test-backend: $(VENV)
	cd backend && .venv/bin/pytest -q

# Der Kartenbau laeuft nie auf dem Pi, seine Rechnung geht aber genauso still schief wie die des
# Backends -- ein Ortsindex mit falschen Punkten faellt erst im Museum auf.
test-tiles: $(VENV)
	$(VENV)/bin/pytest -q tiles

test-frontend: frontend/node_modules
	cd frontend && npm run typecheck && npm test

lint: $(VENV)  ## Code-Stil pruefen
	$(VENV)/bin/ruff check backend tiles tools
	$(VENV)/bin/ruff format --check backend tiles tools

build: frontend/node_modules  ## Frontend-Bundle bauen (Ergebnis in frontend/dist)
	cd frontend && npm run build

# --- Betrieb ----------------------------------------------------------------

.env:
	cp deploy/.env.example .env
	@echo "  .env aus der Vorlage angelegt -- bitte durchsehen."

prod: .env  ## Alles in Containern, so wie es auf dem Pi laeuft
	$(COMPOSE) up --build

# Auf dem Mac fehlen /media und die Mount-Propagierung rshared. Warum, steht in der Datei.
# PHOTOMAP_PROD_DATA zeigt wahlweise auf eine Kopie des Bestands -- empfohlen, weil der
# Entrypoint bei jedem Start den Schemastand nachzieht.
prod-mac: .env  ## Wie prod, aber mit den Pfaden des Entwicklungsmacs
	$(COMPOSE) -f deploy/docker-compose.mac.yml up --build

prod-down: .env
	$(COMPOSE) down

clean:  ## Umgebungen und Caches entfernen (Daten und Karte bleiben unberuehrt)
	rm -rf $(VENV) backend/.pytest_cache backend/.ruff_cache frontend/node_modules frontend/dist
	find backend -name __pycache__ -type d -prune -exec rm -rf {} +
