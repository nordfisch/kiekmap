// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Photos that lie on the same point.
 *
 * At the Gasthof Petersen eight photos sit on identical coordinates. Below `CLUSTER_MAXZOOM`
 * supercluster merges them into one circle, above it not at all -- then there are eight markers
 * exactly on top of each other, of which only the topmost can be reached. And the way there was a
 * dead end: tapping the circle zoomed straight into that stack, because **identical points never
 * separate at any zoom level.**
 *
 * So the grouping happens here, **before** clustering. supercluster never sees a duplicate, and a
 * stack is one marker at every zoom level.
 */

import type { PhotoMarker } from "../api/client";

/**
 * Five decimal places, so about one metre.
 *
 * Hits the actual case: photos located through the place search carry exactly the same coordinate
 * of the street. Whoever set the point by hand lands beside it and stays a marker of their own --
 * rightly so, because then it *is* a different spot.
 */
const PLACES = 5;

export type Stack = {
  lat: number;
  lon: number;
  /** In the order of the list; the most recently edited photo first. */
  photos: PhotoMarker[];
};

function key(photo: PhotoMarker): string {
  return `${photo.lat.toFixed(PLACES)},${photo.lon.toFixed(PLACES)}`;
}

export function groupByLocation(photos: PhotoMarker[]): Stack[] {
  const stacks = new Map<string, Stack>();

  for (const photo of photos) {
    const id = key(photo);
    const stack = stacks.get(id);
    if (stack) stack.photos.push(photo);
    // The stack's place is the first photo's -- the others lie within a metre of it anyway.
    else stacks.set(id, { lat: photo.lat, lon: photo.lon, photos: [photo] });
  }

  return [...stacks.values()];
}
