/**
 * The pin a visitor uses to locate a photo.
 *
 * It lives on the same map as the photos -- that is the whole point of the exercise: you see the
 * surroundings, recognise the street and drop the pin there.
 *
 * Tapping the map drops it, dragging moves it. Both have to work: some tap roughly first and
 * correct afterwards, others hit it straight away.
 */

import type maplibregl from "maplibre-gl";
import { Marker } from "maplibre-gl";
import { useEffect, useRef } from "react";

import { useContribute } from "../store/contribute";
import { t } from "../texte/de";

export function PinLayer({ map }: { map: maplibregl.Map }) {
  const active = useContribute(
    (s) => s.need === "location" && s.task?.photo != null && !s.thanks,
  );
  const pin = useContribute((s) => s.pin);
  const setPin = useContribute((s) => s.setPin);
  const marker = useRef<Marker | null>(null);

  // Tapping the map drops the pin.
  useEffect(() => {
    if (!active) return;

    function onClick(event: maplibregl.MapMouseEvent) {
      setPin({ lat: event.lngLat.lat, lon: event.lngLat.lng });
    }

    map.on("click", onClick);
    map.getCanvas().style.cursor = "crosshair";
    return () => {
      map.off("click", onClick);
      map.getCanvas().style.cursor = "";
    };
  }, [map, active, setPin]);

  // Create, move, remove the pin.
  useEffect(() => {
    if (!pin || !active) {
      marker.current?.remove();
      marker.current = null;
      return;
    }

    if (!marker.current) {
      const element = document.createElement("div");
      element.className = "pin";
      element.setAttribute("aria-label", t.map.pinLabel);

      marker.current = new Marker({ element, anchor: "bottom", draggable: true })
        .setLngLat([pin.lon, pin.lat])
        .addTo(map);

      marker.current.on("dragend", () => {
        const position = marker.current?.getLngLat();
        // Dragging drops the chosen place name -- and with it the claimed accuracy. Both belong
        // to the spot the search returned, not to wherever the pin was dragged.
        if (position) setPin({ lat: position.lat, lon: position.lng });
      });
    } else {
      marker.current.setLngLat([pin.lon, pin.lat]);
    }
  }, [map, pin, active, setPin]);

  useEffect(
    () => () => {
      marker.current?.remove();
      marker.current = null;
    },
    [],
  );

  return null;
}
