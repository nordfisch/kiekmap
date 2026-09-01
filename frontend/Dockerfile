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
      echo "FEHLER: public/basemaps/fonts fehlt. Bitte zuerst 'make tiles' ausfuehren."; \
      exit 1; \
    }

RUN npm run build


FROM nginx:1.27-alpine AS runtime
COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
