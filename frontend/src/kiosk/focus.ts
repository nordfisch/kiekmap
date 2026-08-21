// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * How the view settles on a photo just completed.
 *
 * The thank-you promises "Das Foto ist jetzt auf der Karte". For that to be true, the map travels
 * to the photo for the duration of the thank-you, and the time range sets itself so that it is
 * really visible. Afterwards both come back -- nothing the visitor set themselves is lost.
 *
 * Decided from the photo as it now stands, not from which of the two routes triggered the
 * contribution.
 *
 * A photo without a place is the one case where nothing here can move. The thank-you does not
 * claim otherwise: it asks where the photo was and hands it straight on to that question -- see
 * ``contribute()`` in `store/contribute.ts`.
 */

import type { PhotoDetail, TimeRange } from "../api/client";

/** How close the map goes. A radius, not a zoom level: that depends on the window size. */
export const FOCUS_RADIUS_M = 100;

/** Degrees of latitude per metre. For longitude the cosine of the latitude comes on top. */
const M_PER_DEGREE = 111_320;

export function decadeOf(year: number): number {
  return Math.floor(year / 10) * 10;
}

/**
 * The time range in which this photo is visible.
 *
 * - With a year: its decade. Whoever just tapped "1932" sees the handles jump to the 1930s and
 *   their photo appear inside them.
 * - Without a year: wide open. **Undated photos are on the map only while no time filter is
 *   active** (see `_viewport_filters` in the backend). Whoever narrowed the slider and then
 *   locates an undated photo would otherwise be shown an empty spot -- under a sentence saying
 *   the photo is now on the map.
 */
export function rangeForPhoto(photo: PhotoDetail, fullRange: TimeRange | null): TimeRange | null {
  if (photo.lat === null || photo.lon === null) return null;

  if (photo.date_from) {
    const decade = decadeOf(Number.parseInt(photo.date_from.slice(0, 4), 10));
    return { from: decade, to: decade + 9 };
  }
  return fullRange;
}

/** The square around a point that the map fits: [[west, south], [east, north]]. */
export function boundsAround(
  lat: number,
  lon: number,
  radiusM = FOCUS_RADIUS_M,
): [[number, number], [number, number]] {
  const dLat = radiusM / M_PER_DEGREE;
  const dLon = radiusM / (M_PER_DEGREE * Math.cos((lat * Math.PI) / 180));
  return [
    [lon - dLon, lat - dLat],
    [lon + dLon, lat + dLat],
  ];
}

/**
 * The rectangle that holds all of these points -- for the house numbers currently on offer.
 *
 * **Never smaller than `boundsAround`**, and that is the whole reason this is not two lines. The
 * numbers of one block sit along one side of one street: their own rectangle is a few metres wide
 * and, for a single number, has no width at all. `fitBounds` on that puts the map at a zoom level
 * where nothing is recognisable -- or divides by zero. Every point therefore gets the same
 * breathing space a single one would.
 *
 * Empty list: nothing to fit, and the caller decides what to do instead.
 */
export function boundsOf(
  points: { lat: number; lon: number }[],
  radiusM = FOCUS_RADIUS_M,
): [[number, number], [number, number]] | null {
  if (points.length === 0) return null;

  const corners = points.map((point) => boundsAround(point.lat, point.lon, radiusM));
  return [
    [Math.min(...corners.map((c) => c[0][0])), Math.min(...corners.map((c) => c[0][1]))],
    [Math.max(...corners.map((c) => c[1][0])), Math.max(...corners.map((c) => c[1][1]))],
  ];
}
