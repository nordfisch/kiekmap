// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * How the map looks.
 *
 * Its own module because the look is a decision, not a detail: the map is the backdrop for the
 * photographs, and everything here serves that. Three things happen:
 *
 *   1. A colour flavour of our own, in the tones of the rest of the kiosk.
 *   2. Layers a museum has no use for are left out.
 *   3. Roads are drawn a little thinner than a navigation map would draw them.
 *
 * See docs/decisions.md, point 12.
 */

import { type Flavor, layers, namedFlavor } from "@protomaps/basemaps";
import type maplibregl from "maplibre-gl";

import type { Region } from "../region";

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

/**
 * "Papier" -- the map in the colours of the room around it.
 *
 * The ready-made flavours are built for navigation: turquoise water, saturated green, cool grey.
 * Beside a panel in paper white (--paper) and sepia brown (--accent) they look like a different
 * program. These tones come from the same family, so the scans sit on something that looks like
 * the paper they were printed on.
 *
 * The rule while picking them: nothing on the map may be as saturated as a photograph. Whatever
 * colour is on screen should be a photograph's.
 */
const PAPER: Partial<Flavor> = {
  //: Warmer than --paper (#faf8f4), so the panel still reads as the lighter surface.
  earth: "#f3ede2",
  //: Green desaturated to sage. Real green would compete with the pictures.
  park_a: "#e6e6d5",
  park_b: "#cdd4bb",
  wood_a: "#e6e6d5",
  wood_b: "#cdd4bb",
  scrub_a: "#e6e6d5",
  scrub_b: "#cdd4bb",
  //: Matt grey-blue instead of turquoise -- the Elbe marshes are not the Caribbean.
  water: "#c6d2d4",
  //: Areas that mean nothing to a visitor melt into the ground.
  pedestrian: "#f3ede2",
  hospital: "#f3ede2",
  school: "#f3ede2",
  industrial: "#f3ede2",
  sand: "#f3ede2",
  beach: "#f3ede2",
  //: Buildings a touch darker than the ground, so a village core is readable as one.
  buildings: "#e5dbc9",

  other: "#f7f2e8",
  minor_service: "#f7f2e8",
  minor_a: "#f7f2e8",
  minor_b: "#fffdf8",
  link: "#fffdf8",
  major: "#fffdf8",
  highway: "#fffdf8",
  bridges_other: "#f7f2e8",
  bridges_minor: "#fffdf8",
  bridges_link: "#fffdf8",
  bridges_major: "#fffdf8",
  bridges_highway: "#fffdf8",

  //: Sand rather than grey, otherwise every road carries a cool outline.
  minor_service_casing: "#e0d5c0",
  minor_casing: "#e0d5c0",
  link_casing: "#e0d5c0",
  major_casing_early: "#e0d5c0",
  major_casing_late: "#e0d5c0",
  highway_casing_early: "#e0d5c0",
  highway_casing_late: "#e0d5c0",
  bridges_other_casing: "#e0d5c0",
  bridges_minor_casing: "#e0d5c0",
  bridges_link_casing: "#e0d5c0",
  bridges_major_casing: "#e0d5c0",
  bridges_highway_casing: "#e0d5c0",
  railway: "#e0d5c0",
  boundaries: "#e0d5c0",

  //: --muted, the same colour the panel uses for secondary text.
  roads_label_minor: "#6f6862",
  roads_label_major: "#6f6862",
  subplace_label: "#6f6862",
  city_label: "#6f6862",
  address_label: "#6f6862",
  //: Halo in the ground colour, not white -- a white outline would glare on beige.
  roads_label_minor_halo: "#f3ede2",
  roads_label_major_halo: "#f3ede2",
  subplace_label_halo: "#f3ede2",
  city_label_halo: "#f3ede2",
  address_label_halo: "#f3ede2",
};

/**
 * Layers a museum kiosk has no use for.
 *
 * Deliberately short. Street names stay -- including the small ones: the panel says "tap the spot
 * on the map, or search for the street name", and in a village most streets are minor ones. What
 * goes is what nobody came here for: shops and their icons, house numbers printed on the map, and
 * motorway shields.
 */
const OMITTED = new Set(["pois", "address_label", "roads_shields"]);

/** Roads are the backdrop here, not the subject. */
const ROAD_WIDTH = 0.8;

/**
 * Take a line width down a notch.
 *
 * The obvious way does not work. Wrapping the whole thing as ``["*", width, 0.8]`` is rejected by
 * MapLibre with *«"zoom" expression may only be used as input to a top-level "step" or
 * "interpolate" expression»* -- the zoom interpolation has to stay the outermost thing there is.
 *
 * So the *stop values* are scaled and the shape of the curve is left alone. That also keeps this
 * from becoming a hand-maintained copy of somebody else's cartography: when the flavour changes
 * its widths, ours follow.
 */
function scaleWidth(width: unknown): unknown {
  const thinner = (value: number) => Math.round(value * ROAD_WIDTH * 100) / 100;

  if (typeof width === "number") return thinner(width);
  if (!Array.isArray(width)) return width;

  // ["interpolate", interpolation, input, stop, value, stop, value, …] -- values sit on the even
  // positions from 4 on. ["step", input, value, stop, value, …] -- from 2 on.
  const firstValue = width[0] === "interpolate" ? 4 : width[0] === "step" ? 2 : -1;
  if (firstValue < 0) return width;

  return width.map((part, index) =>
    index >= firstValue && index % 2 === 0 && typeof part === "number" ? thinner(part) : part,
  );
}

function calmRoads(layer: maplibregl.LayerSpecification): maplibregl.LayerSpecification {
  if (layer.type !== "line" || !layer.id.startsWith("roads_")) return layer;

  const width = layer.paint?.["line-width"];
  if (width === undefined) return layer;

  return {
    ...layer,
    paint: { ...layer.paint, "line-width": scaleWidth(width) },
  } as maplibregl.LayerSpecification;
}

export function buildStyle(region: Region): maplibregl.StyleSpecification {
  const flavor = { ...namedFlavor("light"), ...PAPER } as Flavor;

  return {
    version: 8,
    glyphs: GLYPHS,
    sprite: SPRITE,
    sources: {
      protomaps: {
        type: "vector",
        url: "pmtiles:///tiles/map.pmtiles",
        // The licence belongs beside the name, not only the name: vector tiles are a derivative
        // database in the sense of the ODbL, which asks that they be recognisable as one.
        // See docs/licensing.md.
        attribution:
          '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende, ODbL',
      },
    },
    layers: layers("protomaps", flavor, { lang: "de" })
      .filter((layer) => !OMITTED.has(layer.id))
      .map(calmRoads),
    ...{ maxzoom: region.maxZoom },
  } as maplibregl.StyleSpecification;
}
