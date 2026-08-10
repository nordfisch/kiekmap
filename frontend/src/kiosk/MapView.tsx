import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef, useState } from "react";

import type { Bbox } from "../api/client";
import type { Region } from "../region";
import { useKiosk } from "../store/kiosk";
import { HouseNumberLayer } from "./HouseNumberLayer";
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
   * After five minutes without a touch the page is **reloaded**, not merely reset. The kiosk has
   * no browser controls -- no reload button, no address bar, no keyboard (`--kiosk` under cage,
   * see deploy/pi/photomap-kiosk). A stuck state would otherwise stand there until somebody
   * pulled the plug. This way the device heals itself and nobody has to know about it.
   *
   * It costs nothing: the tiles are cached, and with no visitor around the reload disturbs
   * nobody.
   */
  useEffect(() => {
    if (!map) return;
    return watchForIdle(window, IDLE_MS, () => window.location.reload());
  }, [map]);

  /**
   * Remember the camera while a focus runs -- and travel back there at the end.
   *
   * Deliberately tied to `focused` and not to the focus itself: during one locating it changes
   * twice (first the pin set, then the confirmed photo). If the return trip hung on the object,
   * the map would briefly fly out and straight back in on confirmation.
   */
  const focused = focus !== null;
  const cameraBefore = useRef<{ center: maplibregl.LngLat; zoom: number } | null>(null);

  useEffect(() => {
    if (!map || !focused) return;

    cameraBefore.current = { center: map.getCenter(), zoom: map.getZoom() };
    return () => {
      const before = cameraBefore.current;
      cameraBefore.current = null;
      // A map already removed must not be moved any more -- switching into the admin area takes
      // it out of the document together with its container.
      if (before && map.getContainer().isConnected) {
        map.easeTo({ ...before, duration: 800 });
      }
    };
  }, [map, focused]);

  // Travel there whenever the focus points at a new spot.
  useEffect(() => {
    if (!map || !focus) return;
    map.fitBounds(focus.bounds, { padding: 40, duration: 800 });
  }, [map, focus]);

  return (
    <div className="map">
      <div ref={container} className="map__canvas" />
      {map && <PhotoLayer map={map} />}
      {map && <PinLayer map={map} />}
      {map && <HouseNumberLayer map={map} />}
    </div>
  );
}
