import { layers, namedFlavor } from "@protomaps/basemaps";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef } from "react";

import type { Region } from "../region";

// Einmal pro Seitenaufruf: lehrt MapLibre, `pmtiles://`-Quellen per HTTP-Range-Request zu lesen.
// Genau das macht den Tileserver ueberfluessig -- nginx liefert einfach eine statische Datei aus.
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

/**
 * Schriften und Symbole liegen lokal unter /basemaps/.
 *
 * Das ist der Punkt, an dem eine Offline-Karte sonst still zerbricht: Kacheln und Stil kaemen aus
 * der PMTiles-Datei, aber Beschriftungen und Symbole wuerden weiterhin von protomaps.github.io
 * geholt. Ohne Netz bliebe eine Karte ohne jede Schrift uebrig.
 */
const GLYPHS = "/basemaps/fonts/{fontstack}/{range}.pbf";
// Sprites verlangt MapLibre absolut -- relative Pfade lehnt es ab. Die Herkunft kommt aus dem
// Browser statt aus der Konfiguration, damit derselbe Bau unter localhost, im Museums-WLAN und
// hinter dem nginx des Pi funktioniert.
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
    // Ueber die gebaute Zoomstufe hinaus wird ueberzoomt statt unscharf zu werden -- der Vorteil
    // von Vektorkacheln, den wir am Touchscreen brauchen.
    ...{ maxzoom: region.maxZoom },
  } as maplibregl.StyleSpecification;
}

export function MapView({ region }: { region: Region }) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!container.current || map.current) return;

    const instance = new maplibregl.Map({
      container: container.current,
      style: buildStyle(region),
      center: region.center,
      zoom: region.defaultZoom,
      minZoom: region.minZoom,
      // Ueber die Region hinaus gibt es keine Kacheln. Ohne diese Grenze koennte der Besucher in
      // eine graue Flaeche hinauswandern und faende allein nicht zurueck.
      maxBounds: [
        [region.bbox[0], region.bbox[1]],
        [region.bbox[2], region.bbox[3]],
      ],
      // Drehen und Neigen sind am Museums-Touchscreen nur Wege, die Karte zu verstellen.
      dragRotate: false,
      pitchWithRotate: false,
      touchPitch: false,
      attributionControl: { compact: true },
    });
    instance.touchZoomRotate.disableRotation();
    instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.current = instance;
    return () => {
      instance.remove();
      map.current = null;
    };
  }, [region]);

  return <div ref={container} className="map" />;
}
