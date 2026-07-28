/**
 * Photos at their capture location on the map.
 *
 * Real thumbnails as markers are the goal -- an image at its place is immediately understandable,
 * a dot is not. At high density that turns into hundreds of image elements, which the Pi can no
 * longer pan smoothly. supercluster therefore merges nearby photos into a circle with a count;
 * zooming in dissolves them again. That is also the most natural gesture on a touchscreen.
 */

import type maplibregl from "maplibre-gl";
import { Marker } from "maplibre-gl";
import { useEffect, useMemo, useRef } from "react";
import Supercluster from "supercluster";

import type { PhotoMarker } from "../api/client";
import { useKiosk } from "../store/kiosk";
import { t } from "../texte/de";

/** Radius in pixels within which photos are merged. About a thumb's width. */
const CLUSTER_RADIUS = 70;

/** Beyond this zoom nothing is merged -- closer together than that is rarely meaningful. */
const CLUSTER_MAXZOOM = 17;

type PhotoProps = { photo: PhotoMarker };

/** getClusters returns merged groups and single photos mixed together. */
type Group = Supercluster.PointFeature<PhotoProps | Supercluster.ClusterProperties>;

function isCluster(
  group: Group,
): group is Supercluster.PointFeature<Supercluster.ClusterProperties> {
  return "cluster" in group.properties && group.properties.cluster;
}

function buildIndex(photos: PhotoMarker[]): Supercluster<PhotoProps> {
  const index = new Supercluster<PhotoProps>({
    radius: CLUSTER_RADIUS,
    maxZoom: CLUSTER_MAXZOOM,
  });
  index.load(
    photos.map((photo) => ({
      type: "Feature" as const,
      properties: { photo },
      geometry: { type: "Point" as const, coordinates: [photo.lon, photo.lat] },
    })),
  );
  return index;
}

function photoElement(photo: PhotoMarker, onSelect: () => void): HTMLElement {
  const root = document.createElement("button");
  root.type = "button";
  root.className = "marker";
  root.setAttribute("aria-label", t.map.markerLabel(photo.title ?? "Foto", photo.date_label));

  const image = document.createElement("img");
  image.className = "marker__image";
  image.src = photo.thumb_url;
  image.alt = "";
  image.loading = "lazy";
  image.decoding = "async";
  // Portrait and landscape should look equally large, hence a fixed height rather than width.
  image.style.aspectRatio = `${photo.width} / ${photo.height}`;
  root.appendChild(image);

  const year = document.createElement("span");
  year.className = "marker__year";
  year.textContent = photo.date_label;
  root.appendChild(year);

  root.addEventListener("click", (event) => {
    event.stopPropagation();
    onSelect();
  });
  return root;
}

function clusterElement(count: number, onSelect: () => void): HTMLElement {
  const root = document.createElement("button");
  root.type = "button";
  root.className = "cluster";
  root.setAttribute("aria-label", t.map.clusterLabel(count));
  root.textContent = String(count);
  // Slightly larger for many photos, so the distribution reads at a glance.
  const size = Math.min(88, 48 + Math.log10(count) * 26);
  root.style.width = root.style.height = `${Math.round(size)}px`;

  root.addEventListener("click", (event) => {
    event.stopPropagation();
    onSelect();
  });
  return root;
}

export function PhotoLayer({ map }: { map: maplibregl.Map }) {
  const photos = useKiosk((s) => s.photos);
  const openPhoto = useKiosk((s) => s.openPhoto);
  const markers = useRef<Marker[]>([]);

  const index = useMemo(() => buildIndex(photos), [photos]);

  useEffect(() => {
    function draw() {
      // Markers are rebuilt wholesale rather than diffed. With at most a few dozen visible
      // elements that is cheaper than reconciling -- and far less code for a state bug to hide in.
      for (const old of markers.current) old.remove();
      markers.current = [];

      const bounds = map.getBounds();
      const zoom = Math.round(map.getZoom());
      const groups = index.getClusters(
        [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()],
        zoom,
      );

      for (const group of groups) {
        const [lon, lat] = group.geometry.coordinates as [number, number];

        if (isCluster(group)) {
          const { cluster_id: clusterId, point_count: count } = group.properties;
          const element = clusterElement(count, () => {
            // Zoom in far enough for this group to dissolve.
            map.easeTo({
              center: [lon, lat],
              zoom: Math.min(index.getClusterExpansionZoom(clusterId), CLUSTER_MAXZOOM + 1),
              duration: 500,
            });
          });
          markers.current.push(new Marker({ element }).setLngLat([lon, lat]).addTo(map));
        } else {
          const photo = group.properties.photo;
          const element = photoElement(photo, () => openPhoto(photo.id));
          markers.current.push(
            // The marker sits with its lower edge on the location, like a pin.
            new Marker({ element, anchor: "bottom" }).setLngLat([lon, lat]).addTo(map),
          );
        }
      }
    }

    draw();
    map.on("move", draw);
    map.on("zoom", draw);
    return () => {
      map.off("move", draw);
      map.off("zoom", draw);
      for (const old of markers.current) old.remove();
      markers.current = [];
    };
  }, [map, index, openPhoto]);

  return null;
}
