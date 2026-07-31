import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef, useState } from "react";

import type { Bbox } from "../api/client";
import type { Region } from "../region";
import { useKiosk } from "../store/kiosk";
import { PhotoLayer } from "./PhotoLayer";
import { PinLayer } from "./PinLayer";
import { IDLE_MS, watchForIdle } from "./idle";
import { buildStyle } from "./mapStyle";

// Once per page load: teaches MapLibre to read `pmtiles://` sources via HTTP range requests.
// That is exactly what makes a tile server unnecessary -- nginx just serves a static file.
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

export function MapView({ region }: { region: Region }) {
  const container = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<maplibregl.Map | null>(null);
  const setViewport = useKiosk((s) => s.setViewport);
  const focus = useKiosk((s) => s.focus);

  useEffect(() => {
    if (!container.current) return;

    const instance = new maplibregl.Map({
      container: container.current,
      style: buildStyle(region),
      center: region.center,
      zoom: region.defaultZoom,
      minZoom: region.minZoom,
      // Beyond the region there are no tiles. Without this bound a visitor could wander into a
      // grey plane and would not find the way back on their own.
      maxBounds: [
        [region.bbox[0], region.bbox[1]],
        [region.bbox[2], region.bbox[3]],
      ],
      // Rotating and tilting are only ways to misalign the map on a museum touchscreen.
      dragRotate: false,
      pitchWithRotate: false,
      touchPitch: false,
      attributionControl: { compact: true },
    });
    instance.touchZoomRotate.disableRotation();
    instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    function reportViewport() {
      const bounds = instance.getBounds();
      setViewport([
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth(),
      ] satisfies Bbox);
    }

    // Guard against a cleanup that has already run.
    //
    // "load" fires asynchronously. If the effect is torn down before then -- React's StrictMode
    // does exactly that on every mount, and a re-render of the region would too -- the callback
    // would hand a removed map to the layers below. They then add their markers to a dead
    // instance: the thumbnails are even fetched, but nothing ever appears on screen.
    let disposed = false;

    instance.on("load", () => {
      if (disposed) return;
      reportViewport();
      setMap(instance);
    });
    // "moveend" rather than "move": loading is debounced anyway, and reporting new viewports
    // continuously while swiping achieves nothing.
    instance.on("moveend", reportViewport);

    return () => {
      disposed = true;
      instance.remove();
      setMap(null);
    };
  }, [region, setViewport]);

  /**
   * Back to the state the device should be in each morning.
   *
   * Nach fünf Minuten ohne Berührung wird die Seite **neu geladen**, nicht nur zurückgesetzt. Im
   * Kiosk gibt es keine Browser-Bedienung — kein Reload-Knopf, keine Adressleiste, keine Tastatur
   * (`--kiosk` unter cage, siehe deploy/pi/photomap-kiosk). Ein verhakter Zustand bliebe sonst bis
   * zum nächsten Netzstecker stehen. So heilt sich das Gerät selbst, und niemand muss davon wissen.
   *
   * Es kostet nichts: Die Kacheln liegen im Cache, und ohne Besucher stört das Nachladen keinen.
   */
  useEffect(() => {
    if (!map) return;
    return watchForIdle(window, IDLE_MS, () => window.location.reload());
  }, [map]);

  /**
   * Die Kamera merken, solange ein Fokus läuft — und am Ende dorthin zurückfahren.
   *
   * Bewusst an `focused` gebunden und nicht an den Fokus selbst: Während einer Verortung wechselt
   * er zweimal (erst der gesetzte Punkt, dann das bestätigte Foto). Hinge die Rückfahrt am Objekt,
   * würde die Karte beim Bestätigen kurz heraus- und sofort wieder hineinfahren.
   */
  const focused = focus !== null;
  const cameraBefore = useRef<{ center: maplibregl.LngLat; zoom: number } | null>(null);

  useEffect(() => {
    if (!map || !focused) return;

    cameraBefore.current = { center: map.getCenter(), zoom: map.getZoom() };
    return () => {
      const before = cameraBefore.current;
      cameraBefore.current = null;
      // Eine bereits entfernte Karte darf nicht mehr bewegt werden -- beim Wechsel in den
      // Verwaltungsbereich verschwindet sie mitsamt ihrem Container aus dem Dokument.
      if (before && map.getContainer().isConnected) {
        map.easeTo({ ...before, duration: 800 });
      }
    };
  }, [map, focused]);

  // Hinfahren, wann immer der Fokus auf eine neue Stelle zeigt.
  useEffect(() => {
    if (!map || !focus) return;
    map.fitBounds(focus.bounds, { padding: 40, duration: 800 });
  }, [map, focus]);

  return (
    <div className="map">
      <div ref={container} className="map__canvas" />
      {map && <PhotoLayer map={map} />}
      {map && <PinLayer map={map} />}
    </div>
  );
}
