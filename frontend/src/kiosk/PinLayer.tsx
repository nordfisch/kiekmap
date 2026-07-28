/**
 * Der Pin, mit dem ein Besucher ein Foto verortet.
 *
 * Liegt auf derselben Karte wie die Fotos -- das ist der Punkt der ganzen Uebung: man sieht die
 * Umgebung, erkennt die Straße wieder und setzt den Pin dorthin.
 *
 * Antippen der Karte setzt ihn, Ziehen verschiebt ihn. Beides muss gehen: manche tippen erst grob
 * und korrigieren dann, andere treffen sofort.
 */

import type maplibregl from "maplibre-gl";
import { Marker } from "maplibre-gl";
import { useEffect, useRef } from "react";

import { useHilfMit } from "../store/hilfmit";

export function PinLayer({ map }: { map: maplibregl.Map }) {
  const aktiv = useHilfMit((s) => s.bedarf === "location" && s.aufgabe?.photo != null && !s.dank);
  const pin = useHilfMit((s) => s.pin);
  const setzePin = useHilfMit((s) => s.setzePin);
  const marker = useRef<Marker | null>(null);

  // Tippen auf die Karte setzt den Pin.
  useEffect(() => {
    if (!aktiv) return;

    function beiKlick(ereignis: maplibregl.MapMouseEvent) {
      setzePin({ lat: ereignis.lngLat.lat, lon: ereignis.lngLat.lng });
    }

    map.on("click", beiKlick);
    map.getCanvas().style.cursor = "crosshair";
    return () => {
      map.off("click", beiKlick);
      map.getCanvas().style.cursor = "";
    };
  }, [map, aktiv, setzePin]);

  // Pin anlegen, verschieben, entfernen.
  useEffect(() => {
    if (!pin || !aktiv) {
      marker.current?.remove();
      marker.current = null;
      return;
    }

    if (!marker.current) {
      const element = document.createElement("div");
      element.className = "pin";
      element.setAttribute("aria-label", "Gesetzter Ort, verschiebbar");

      marker.current = new Marker({ element, anchor: "bottom", draggable: true })
        .setLngLat([pin.lon, pin.lat])
        .addTo(map);

      marker.current.on("dragend", () => {
        const ort = marker.current?.getLngLat();
        // Beim Verschieben faellt ein zuvor gewaehlter Ortsname weg: der Name gehoert zu der
        // Stelle, die die Suche geliefert hat, nicht zu der, wohin gezogen wurde.
        if (ort) setzePin({ lat: ort.lat, lon: ort.lng }, null);
      });
    } else {
      marker.current.setLngLat([pin.lon, pin.lat]);
    }
  }, [map, pin, aktiv, setzePin]);

  useEffect(
    () => () => {
      marker.current?.remove();
      marker.current = null;
    },
    [],
  );

  return null;
}
