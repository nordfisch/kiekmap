# syntax=docker/dockerfile:1

FROM node:22-alpine AS build
WORKDIR /src

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
# public/ enthaelt die Schriften und Symbole der Karte (Teil der Software, kommt ins Image).
# public/tiles/map.pmtiles ist per .dockerignore ausgeschlossen: die Kartendatei gehoert zum Ort,
# nicht zur Software, ist gross und wird zur Laufzeit eingehaengt.
COPY public ./public

# Frueh und deutlich scheitern statt spaeter im Museum eine Karte ohne Beschriftungen zu haben.
RUN test -d public/basemaps/fonts || { \
      echo "FEHLER: public/basemaps/fonts fehlt. Bitte zuerst 'make tiles' ausfuehren."; \
      exit 1; \
    }

RUN npm run build


FROM nginx:1.27-alpine AS runtime
COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
