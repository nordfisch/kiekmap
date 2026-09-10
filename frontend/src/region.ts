/**
 * The region of the museum's village.
 *
 * Fetched at runtime from `/tiles/region.json` rather than baked into the bundle -- for the same
 * reason as the map file itself: it belongs to the place, not to the software. That way the
 * viewport can be adjusted on the Pi without rebuilding the frontend.
 */

import { t } from "./text";

export type Region = {
  name: string;
  /** [minLon, minLat, maxLon, maxLat] in WGS84 */
  bbox: [number, number, number, number];
  center: [number, number];
  defaultZoom: number;
  minZoom: number;
  maxZoom: number;
  /**
   * What the ground is called -- "de", "en", "fr". Not what the device says to its visitors.
   *
   * The two agree in Holm and part company elsewhere: a museum in France speaks French to its
   * visitors *and* wants French labels, but a German-speaking museum near the border may want the
   * ground named in the local language whatever the interface says. So the label language belongs
   * to the place, and the place is described here.
   *
   * Optional, because a device set up before this field existed carries a `region.json` without
   * it. Missing, it falls back to the language of the interface -- which is what the map did
   * before, so an update cannot take the labels away from a running device.
   */
  labelLanguage?: string;
};

// Which decades the date question offers used to stand here too -- but that describes the
// collection, not the place. It now follows from the collection, see kiosk/decades.ts.

export async function loadRegion(signal?: AbortSignal): Promise<Region> {
  const response = await fetch("/tiles/region.json", { signal });
  if (!response.ok) {
    throw new Error(t.errors.regionMissing(response.status));
  }
  return (await response.json()) as Region;
}
