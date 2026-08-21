// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

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
import { clusterZoom, isStepChange, stillEntering } from "./clusterStep";
import { captionOf } from "./mapCaption";
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

/**
 * What identifies a group between two draws.
 *
 * A cluster by its id and its count -- the id alone would let a circle that has grown from 8 to 9
 * photos keep its old number. A stack by its first photo, which is what its marker shows.
 */
function groupKey(group: Group): string {
  if (isCluster(group)) return `c${group.properties.cluster_id}:${group.properties.photos}`;
  const { stack } = group.properties as PhotoProps;
  return `p${stack.photos[0]!.id}:${stack.photos.length}`;
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

/**
 * The element MapLibre positions, wrapped around the one that moves.
 *
 * MapLibre writes the marker position as ``transform: translate(...)`` into the inline style of
 * the element it is given. Anything that also sets ``transform`` there does not compose with it,
 * it competes with it -- and the cascade decides in opposite directions: an **animation** outranks
 * an inline style, so ``marker-enter`` used to win, lose the translate and drop the marker at the
 * container's top left corner for its whole duration. A plain **rule** loses to it, so
 * ``.marker:hover`` did nothing at all, silently, for as long as there have been markers.
 *
 * One element cannot serve both. The shell separates the two layers: outside the map's translate,
 * inside everything the stylesheet wants.
 */
function markerShell(content: HTMLElement): HTMLElement {
  const shell = document.createElement("div");
  shell.className = "marker-shell";
  // A circle must stay tappable, so it is stacked above the thumbnails -- see `global.css`.
  // The class goes here rather than at the two call sites because the stacking follows from
  // what the marker *is*, and the shell is the only element that can carry it.
  if (content.classList.contains("cluster")) shell.classList.add("marker-shell--cluster");
  shell.appendChild(content);
  return shell;
}

function photoElement(stack: Stack, onSelect: () => void): HTMLElement {
  const photo = stack.photos[0]!;
  const count = stack.photos.length;

  // The caption is built once and serves both senses -- see kiosk/mapCaption.ts. Where it comes
  // out empty the marker keeps its picture and says nothing, which is the honest state for a photo
  // that carries neither a title nor a place.
  const caption = captionOf(stack.photos);

  const root = document.createElement("button");
  root.type = "button";
  root.className = "marker";
  root.setAttribute(
    "aria-label",
    count > 1 ? t.map.stackLabel(count) : t.map.markerLabel(caption || t.map.photoAlt),
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
  /**
   * The grouping level of the last draw -- null until the first one.
   *
   * A ref rather than state: it must not trigger a render, and it has to survive the effect being
   * set up again when new photos arrive. Surviving is the point -- a fresh set of photos at an
   * unchanged zoom is not a regrouping and must not flash.
   */
  const drawnStep = useRef<number | null>(null);
  /**
   * What was last drawn -- the level and the groups on it.
   *
   * The markers themselves need no redrawing while the map moves: MapLibre keeps them on their
   * coordinates. Only a changed *set* does. Comparing this is what makes the entry animation
   * possible at all: ``draw`` used to run on every one of the roughly thirty ``move`` events of a
   * single zoom, so a marker marked as entering was thrown away one frame later and the animation
   * never got to play. Beside that it saves the Pi the same work thirty times over.
   */
  const drawn = useRef<string | null>(null);
  /** When the running entrance began -- null while none is. See ``stillEntering``. */
  const enteredAt = useRef<number | null>(null);
  /**
   * The circle a finger last tapped -- null when the regrouping came from somewhere else.
   *
   * A regrouping also happens on a pinch, on ``+``/``-`` and while panning, and none of those has
   * a point the visitor pointed at. Only a tap does, and only then do the new markers grow out of
   * it; otherwise they pop where they belong, which is what the animation always meant to do.
   */
  const tappedAt = useRef<[number, number] | null>(null);

  useEffect(() => {
    function draw() {
      // Consumed at the top, before any early return: a tap that did not change the grouping must
      // not leave its origin lying around for the next one, which would fan from a stale circle.
      const from = tappedAt.current;
      tappedAt.current = null;

      const bounds = map.getBounds();
      const zoom = clusterZoom(map.getZoom());
      const groups = index.getClusters(
        [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()],
        zoom,
      );

      const key = `${zoom}|${groups.map(groupKey).join(",")}`;
      if (key === drawn.current) return;
      drawn.current = key;

      // Only where the grouping actually tips over. Panning changes the set just as often, and
      // animating there would leave the map twitching under the finger.
      if (isStepChange(drawnStep.current, zoom)) enteredAt.current = performance.now();
      drawnStep.current = zoom;
      const entering = stillEntering(enteredAt.current, performance.now());

      // Markers are rebuilt wholesale rather than diffed. With at most a few dozen visible
      // elements that is cheaper than reconciling -- and far less code for a state bug to hide in.
      for (const old of markers.current) old.remove();
      markers.current = [];

      for (const group of groups) {
        const [lon, lat] = group.geometry.coordinates as [number, number];
        // Only fading in, never out: fading out would mean keeping removed elements alive on a
        // timer -- exactly the kind of state the wholesale rebuild above avoids.
        const enter = (content: HTMLElement) => {
          // The animation goes on the content, the shell goes to MapLibre. The other way round
          // reproduces the very bug the shell exists to prevent -- measured on 18 August 2026:
          // with the animation on the shell the markers still started at the container origin,
          // merely displaced by the offset, so they fanned out of four different points.
          if (!entering) return markerShell(content);
          content.classList.add("marker--enter");
          if (from) {
            // Where the tapped circle now sits, minus where this marker sits: the vector the
            // marker travels along, in screen pixels, so it reads the same at every zoom. The
            // circle has been eased to the centre by then, which is exactly where the visitor
            // last saw it.
            const origin = map.project(from);
            const here = map.project([lon, lat]);
            content.classList.add("marker--fan");
            content.style.setProperty("--enter-x", `${origin.x - here.x}px`);
            content.style.setProperty("--enter-y", `${origin.y - here.y}px`);
            // Smaller than the pop in place: it should look like it came out of the circle, not
            // like it was already there and merely slid over.
            content.style.setProperty("--enter-scale", "0.4");
          }
          return markerShell(content);
        };

        if (isCluster(group)) {
          const { cluster_id: clusterId, photos: count } = group.properties;
          const element = clusterElement(count, () => {
            // Remembered for the draw that follows this movement -- see ``tappedAt``.
            tappedAt.current = [lon, lat];
            // Zoom in far enough for this group to dissolve.
            map.easeTo({
              center: [lon, lat],
              zoom: Math.min(index.getClusterExpansionZoom(clusterId), CLUSTER_MAXZOOM + 1),
              duration: 500,
            });
          });
          markers.current.push(
            new Marker({ element: enter(element) }).setLngLat([lon, lat]).addTo(map),
          );
        } else {
          const stack = group.properties.stack;
          const element = photoElement(stack, () =>
            openStackAt(stack.photos.map((photo) => photo.id)),
          );
          markers.current.push(
            // The marker sits with its lower edge on the location, like a pin.
            new Marker({ element: enter(element), anchor: "bottom" })
              .setLngLat([lon, lat])
              .addTo(map),
          );
        }
      }
    }

    draw();
    /**
     * Once the camera has come to rest -- not on every frame while it moves.
     *
     * It hung on ``move`` *and* ``zoom``, and both fire together: measured on 10 August 2026, one
     * tap on "+" produced 31 ``move`` and 30 ``zoom`` events, so everything was drawn some sixty
     * times for a single zoom step. Nothing is gained by any of it. MapLibre keeps the markers on
     * their coordinates by itself, so they follow the movement without being rebuilt; only a
     * changed *set* needs drawing, and that is settled when the camera stops.
     *
     * The photos of a newly revealed area arrive on ``moveend`` anyway -- the store fetches then.
     * And it is what makes the entry animation possible: rebuilt on every frame, a marker marked
     * as entering was thrown away one frame later, and the animation never got to play.
     */
    map.on("moveend", draw);
    return () => {
      map.off("moveend", draw);
      for (const old of markers.current) old.remove();
      markers.current = [];
      // Whatever was drawn is off the map now, so the next ``draw`` must not recognise its own key
      // and skip the work. Without this line an unchanged collection would leave an empty map.
      drawn.current = null;
    };
  }, [map, index, openStackAt]);

  return null;
}
