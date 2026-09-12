# syntax=docker/dockerfile:1

FROM node:22-alpine AS build
WORKDIR /src

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
# public/ holds the fonts and sprites of the map (part of the software, goes into the image).
# public/tiles/map.pmtiles is excluded by .dockerignore: the map file belongs to the place, not to
# the software, is large, and is mounted at runtime.
COPY public ./public

# Fail early and plainly instead of having a map without labels in the museum later.
RUN test -d public/basemaps/fonts || { \
      echo "ERROR: public/basemaps/fonts is missing. Run 'make tiles' first."; \
      exit 1; \
    }

RUN npm run build

# The map's web worker is a file of its own since MapLibre 6, and a build that misses it runs
# without an error and shows a grey map. See the comment at `setWorkerUrl` in src/kiosk/MapView.tsx.
RUN ls dist/assets/maplibre-gl-worker-*.js >/dev/null 2>&1 || { \
      echo "ERROR: the MapLibre worker is missing from dist/assets. The map would stay grey."; \
      exit 1; \
    }


FROM nginx:1.27-alpine AS runtime
COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
