// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The region of the museum's village.
 *
 * Fetched at runtime from `/tiles/region.json` rather than baked into the bundle -- for the same
 * reason as the map file itself: it belongs to the place, not to the software. That way the
 * viewport can be adjusted on the Pi without rebuilding the frontend.
 */

import { t } from "./text/de";

export type Region = {
  name: string;
  /** [minLon, minLat, maxLon, maxLat] in WGS84 */
  bbox: [number, number, number, number];
  center: [number, number];
  defaultZoom: number;
  minZoom: number;
  maxZoom: number;
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
