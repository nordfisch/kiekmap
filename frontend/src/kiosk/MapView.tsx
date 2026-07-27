import { layers, namedFlavor } from "@protomaps/basemaps";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef, useState } from "react";

import type { Bbox } from "../api/client";
import type { Region } from "../region";
import { useKiosk } from "../store/kiosk";
import { PhotoLayer } from "./PhotoLayer";

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
    ...{ maxzoom: region.maxZoom },
  } as maplibregl.StyleSpecification;
}

export function MapView({ region }: { region: Region }) {
  const container = useRef<HTMLDivElement>(null);
  const [karte, setKarte] = useState<maplibregl.Map | null>(null);
  const setzeAusschnitt = useKiosk((s) => s.setzeAusschnitt);

  useEffect(() => {
    if (!container.current) return;

    const instanz = new maplibregl.Map({
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
    instanz.touchZoomRotate.disableRotation();
    instanz.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    function meldeAusschnitt() {
      const grenzen = instanz.getBounds();
      setzeAusschnitt([
        grenzen.getWest(),
        grenzen.getSouth(),
        grenzen.getEast(),
        grenzen.getNorth(),
      ] satisfies Bbox);
    }

    instanz.on("load", () => {
      meldeAusschnitt();
      setKarte(instanz);
    });
    // "moveend" statt "move": das Nachladen wird ohnehin entprellt, und waehrend des Wischens
    // staendig neue Ausschnitte zu melden bringt nichts.
    instanz.on("moveend", meldeAusschnitt);

    return () => {
      instanz.remove();
      setKarte(null);
    };
  }, [region, setzeAusschnitt]);

  return (
    <div className="karte">
      <div ref={container} className="karte__flaeche" />
      {karte && <PhotoLayer map={karte} />}
    </div>
  );
}
