/**
 * The arithmetic behind the time slider.
 *
 * Pure functions, because a fault sat here that is invisible in the code and only shows on
 * screen: the axis came from the histogram of the visible viewport and changed with every zoom
 * while the selection stayed put. After zooming in on two photos from the 1950s the axis read
 * 1950-1960 but the selection still 1920-2019 -- and the selection bar ran across the coat of
 * arms and the title at `left: -300%`.
 *
 * Two bolts against that, both here:
 *
 *   1. The axis spans the whole collection and stands still (`collection_from`/`collection_to`
 *      out of the histogram). The slider therefore always means the same thing.
 *   2. `fraction()` is clamped to 0…1. Even if axis and selection ever drift apart again, no
 *      element can leave its cell.
 */

import type { TimeRange } from "../api/client";

export type Bounds = { min: number; max: number };

/** Rounded out to whole decades -- that simply reads better than 1923 to 2019. */
function roundToDecade(year: number, direction: "down" | "up"): number {
  return direction === "down" ? Math.floor(year / 10) * 10 : Math.ceil(year / 10) * 10;
}

/**
 * The ends of the axis.
 *
 * Null as long as the collection holds not one dated photo -- then there is nothing to slide.
 */
export function axisBounds(fullRange: TimeRange | null): Bounds | null {
  if (!fullRange) return null;
  const min = roundToDecade(fullRange.from, "down");
  const max = roundToDecade(fullRange.to, "up");
  // A single year would otherwise give an axis without length, and every calculation on it a
  // division by zero.
  return { min, max: max > min ? max : min + 10 };
}

/** Where a year sits on the axis: 0 at the left end, 1 at the right. Never outside. */
export function fraction(year: number, bounds: Bounds): number {
  const raw = (year - bounds.min) / (bounds.max - bounds.min);
  return Math.min(1, Math.max(0, raw));
}

/** Pull a selection into the axis, so the state cannot become invalid in the first place. */
export function clampRange(range: TimeRange, bounds: Bounds): TimeRange {
  const from = Math.min(Math.max(range.from, bounds.min), bounds.max);
  const to = Math.min(Math.max(range.to, bounds.min), bounds.max);
  return { from: Math.min(from, to), to: Math.max(from, to) };
}
