/**
 * The house numbers of one street, on the map, for as long as they are being asked about.
 *
 * As a permanent layer this would be noise, not orientation: even the tightest usable viewport
 * holds 152 addresses, and the map is about the photographs. In the one moment somebody is looking
 * for a house number, the same numbers become the answer to the question on screen -- a median of
 * thirteen per street.
 *
 * **The limit is no new number.** What stands on the map is what stands on the buttons, and the
 * picker already caps that at `MAX_BUTTONS`; for the six long streets its block step does the rest.
 * Nothing is shown while the blocks are on screen -- "1–19" written onto a single house would
 * claim something about that house.
 *
 * **Labels, not buttons.** They would otherwise compete with the photo markers for the same
 * finger, and they would be a second way of answering -- one that reaches past the server's list.
 */

import type maplibregl from "maplibre-gl";
import { Marker } from "maplibre-gl";
import { useEffect, useRef } from "react";

import { useContribute } from "../store/contribute";

export function HouseNumberLayer({ map }: { map: maplibregl.Map }) {
  const numbers = useContribute((s) => s.offeredNumbers);
  const hidden = useContribute((s) => s.thanks !== null);
  const markers = useRef<Marker[]>([]);

  useEffect(() => {
    for (const marker of markers.current) marker.remove();
    markers.current = [];

    if (hidden) return;

    for (const place of numbers) {
      const element = document.createElement("div");
      element.className = "housenumber-label";
      element.textContent = place.housenumber ?? "";
      // Nothing here answers anything: the taps belong to the photos underneath.
      element.setAttribute("aria-hidden", "true");

      markers.current.push(new Marker({ element }).setLngLat([place.lon, place.lat]).addTo(map));
    }

    return () => {
      for (const marker of markers.current) marker.remove();
      markers.current = [];
    };
  }, [map, numbers, hidden]);

  return null;
}
