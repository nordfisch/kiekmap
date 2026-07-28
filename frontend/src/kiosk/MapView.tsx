import { layers, namedFlavor } from "@protomaps/basemaps";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef, useState } from "react";

import type { Bbox } from "../api/client";
import type { Region } from "../region";
import { useKiosk } from "../store/kiosk";
import { PhotoLayer } from "./PhotoLayer";
import { PinLayer } from "./PinLayer";

// Once per page load: teaches MapLibre to read `pmtiles://` sources via HTTP range requests.
// That is exactly what makes a tile server unnecessary -- nginx just serves a static file.
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

/**
 * Fonts and icons live locally under /basemaps/.
 *
 * This is where an offline map otherwise breaks silently: tiles and style would come from the
 * PMTiles file, but labels and icons would still be fetched from protomaps.github.io. Without a
 * network what remains is a map without a single word on it.
 */
const GLYPHS = "/basemaps/fonts/{fontstack}/{range}.pbf";
// MapLibre demands an absolute sprite URL -- it rejects relative paths. The origin comes from the
// browser rather than from configuration, so the same build works on localhost, in the museum's
// wifi and behind the Pi's nginx.
const SPRITE = `${window.location.origin}/basemaps/sprites/v4/light`;

function buildStyle(region: Region): maplibregl.StyleSpecification {
  return {
    version: 8,
    glyphs: GLYPHS,
    sprite: SPRITE,
    sources: {
      protomaps: {
        type: "vector",
        url: "pmtiles:///tiles/map.pmtiles",
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>-Mitwirkende',
      },
    },
    layers: layers("protomaps", namedFlavor("light"), { lang: "de" }),
    ...{ maxzoom: region.maxZoom },
  } as maplibregl.StyleSpecification;
}

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

    instance.on("load", () => {
      reportViewport();
      setMap(instance);
    });
    // "moveend" rather than "move": loading is debounced anyway, and reporting new viewports
    // continuously while swiping achieves nothing.
    instance.on("moveend", reportViewport);

    return () => {
      instance.remove();
      setMap(null);
    };
  }, [region, setViewport]);

  return (
    <div className="map">
      <div ref={container} className="map__canvas" />
      {map && <PhotoLayer map={map} />}
      {map && <PinLayer map={map} />}
    </div>
  );
}
