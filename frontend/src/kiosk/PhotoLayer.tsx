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
import { t } from "../text/de";
import { type Stack, groupByLocation } from "./stacks";

/** Radius in pixels within which photos are merged. About a thumb's width. */
const CLUSTER_RADIUS = 70;

/** Beyond this zoom nothing is merged -- closer together than that is rarely meaningful. */
const CLUSTER_MAXZOOM = 17;

type PhotoProps = { stack: Stack };

/**
 * What a circle stands for.
 *
 * Not the number of points but the number of **photos**: a stack is one single point to
 * supercluster (see stacks.ts), and a circle over a stack of eight plus two singles would
 * otherwise have carried a 3 instead of a 10.
 */
type ClusterProps = Supercluster.ClusterProperties & { photos: number };

/** getClusters returns merged groups and single photos mixed together. */
type Group = Supercluster.PointFeature<PhotoProps | ClusterProps>;

function isCluster(group: Group): group is Supercluster.PointFeature<ClusterProps> {
  return "cluster" in group.properties && group.properties.cluster;
}

export function buildIndex(photos: PhotoMarker[]): Supercluster<PhotoProps, ClusterProps> {
  const index = new Supercluster<PhotoProps, ClusterProps>({
    radius: CLUSTER_RADIUS,
    maxZoom: CLUSTER_MAXZOOM,
    // When merging, count the photos, not the points.
    map: (props) => ({ photos: props.stack.photos.length }) as ClusterProps,
    reduce: (summe, props) => {
      summe.photos += props.photos;
    },
  });
  // Grouped before clustering: supercluster never sees duplicates, and a stack stays one marker
  // at every zoom level. See stacks.ts.
  index.load(
    groupByLocation(photos).map((stack) => ({
      type: "Feature" as const,
      properties: { stack },
      geometry: { type: "Point" as const, coordinates: [stack.lon, stack.lat] },
    })),
  );
  return index;
}

function photoElement(stack: Stack, onSelect: () => void): HTMLElement {
  const photo = stack.photos[0]!;
  const count = stack.photos.length;

  const root = document.createElement("button");
  root.type = "button";
  root.className = "marker";
  root.setAttribute(
    "aria-label",
    count > 1
      ? t.map.stackLabel(count)
      : t.map.markerLabel(photo.title ?? "Foto", photo.date_label),
  );

  const image = document.createElement("img");
  image.className = "marker__image";
  image.src = photo.thumb_url;
  image.alt = "";
  image.loading = "lazy";
  image.decoding = "async";
  // Portrait and landscape should look equally large, hence a fixed height rather than width.
  image.style.aspectRatio = `${photo.width} / ${photo.height}`;
  root.appendChild(image);

  // Address and year, and nothing where neither is known -- see t.map.markerCaption.
  //
  // A stack shows the address but no year. Photos land on one marker because they share a
  // coordinate, which here means they share an address -- fifty-one pictures of Schulstraße 2 are
  // all of Schulstraße 2. Their years are not shared, and taking the topmost one would put a
  // date under fifty photos that do not carry it. The address is only claimed where every photo
  // in the stack agrees: EXIF-located photos can land within a metre of each other without
  // having anything to do with one another.
  const shared = stack.photos.every((other) => other.place_name === photo.place_name);
  const caption = t.map.markerCaption(
    shared ? photo.place_name : null,
    count > 1 ? "" : photo.date_short,
  );
  if (caption) {
    const line = document.createElement("span");
    line.className = "marker__caption";
    line.textContent = caption;
    root.appendChild(line);
  }

  // The count in the corner: the visitor should know there is more behind it before tapping.
  if (count > 1) {
    const badge = document.createElement("span");
    badge.className = "marker__count";
    badge.textContent = String(count);
    root.appendChild(badge);
  }

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
  const openStackAt = useKiosk((s) => s.openStackAt);
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
          const { cluster_id: clusterId, photos: count } = group.properties;
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
          const stack = group.properties.stack;
          const element = photoElement(stack, () =>
            openStackAt(stack.photos.map((photo) => photo.id)),
          );
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
  }, [map, index, openStackAt]);

  return null;
}
