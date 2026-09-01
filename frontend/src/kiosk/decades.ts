/**
 * Which decades the contribution panel offers.
 *
 * They follow from the **collection**, not from a setting: what a collection spans is something
 * the collection itself knows best. This used to sit in `region.json` -- a file where every other
 * key describes geography and which the map build reads. Changing two years therefore dragged an
 * internet connection and a complete map build along behind it.
 *
 * Plus a guaranteed minimum window: a device without a single dated photo would otherwise have no
 * button at all, and a collection that happens to span only the 1950s would not let a visitor say
 * what they know. If the collection grows past it, the row grows along -- without anybody having
 * to go looking for a setting.
 */

import type { TimeRange } from "../api/client";

/**
 * The decades that are always on offer.
 *
 * Not a collection-dependent value but the floor for every kiosk: the century a local museum's
 * photographs usually come from.
 */
export const MINIMUM_DECADES = { first: 1920, last: 2010 };

function decadeOf(year: number): number {
  return Math.floor(year / 10) * 10;
}

/** From oldest to youngest, ascending -- the order they stand in on screen. */
export function offeredDecades(collection: TimeRange | null): number[] {
  const first = Math.min(
    MINIMUM_DECADES.first,
    collection ? decadeOf(collection.from) : MINIMUM_DECADES.first,
  );
  const last = Math.max(
    MINIMUM_DECADES.last,
    collection ? decadeOf(collection.to) : MINIMUM_DECADES.last,
  );

  return Array.from({ length: (last - first) / 10 + 1 }, (_, i) => first + i * 10);
}
