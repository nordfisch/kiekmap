/**
 * The region of the museum's village.
 *
 * Fetched at runtime from `/tiles/region.json` rather than baked into the bundle -- for the same
 * reason as the map file itself: it belongs to the place, not to the software. That way the
 * viewport can be adjusted on the Pi without rebuilding the frontend.
 */

import { t } from "./texte/de";

export type Region = {
  name: string;
  /** [minLon, minLat, maxLon, maxLat] in WGS84 */
  bbox: [number, number, number, number];
  center: [number, number];
  defaultZoom: number;
  minZoom: number;
  maxZoom: number;
  /**
   * Range of decades offered in the "Hilf mit" date question.
   *
   * Belongs to the collection, not to the software: a museum whose oldest print is from 1890 gains
   * nothing from a 1860s button. Optional -- ``DEFAULT_DECADES`` applies when absent.
   */
  firstDecade?: number;
  lastDecade?: number;
};

/** Fallback when region.json says nothing about it. */
export const DEFAULT_DECADES = { first: 1860, last: 1990 };

export async function loadRegion(signal?: AbortSignal): Promise<Region> {
  const response = await fetch("/tiles/region.json", { signal });
  if (!response.ok) {
    throw new Error(t.errors.regionMissing(response.status));
  }
  return (await response.json()) as Region;
}
