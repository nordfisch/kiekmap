import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef, useState } from "react";

import type { Bbox } from "../api/client";
import type { Region } from "../region";
import { useContribute } from "../store/contribute";
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

  // Back to the state the device should be in each morning. The map is part of it, and only this
  // component can move it -- so the idle watch lives here rather than in a store.
  useEffect(() => {
    if (!map) return;

    return watchForIdle(window, IDLE_MS, () => {
      useKiosk.getState().reset();
      useContribute.getState().reset();
      map.easeTo({ center: region.center, zoom: region.defaultZoom, duration: 1500 });
    });
  }, [map, region]);

  return (
    <div className="map">
      <div ref={container} className="map__canvas" />
      {map && <PhotoLayer map={map} />}
      {map && <PinLayer map={map} />}
    </div>
  );
}
