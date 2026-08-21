// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

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

/** Rounded out to whole bars -- that simply reads better, and the bars then fill the axis. */
function roundToStep(year: number, step: number, direction: "down" | "up"): number {
  const scaled = year / step;
  return (direction === "down" ? Math.floor(scaled) : Math.ceil(scaled)) * step;
}

/**
 * The ends of the axis.
 *
 * Rounded to the width of a bar rather than always to decades: with yearly bars, 2010 to 2024
 * would otherwise become 2010 to 2030 -- six years of empty track in which nothing will ever lie.
 *
 * Null as long as the collection holds not one dated photo -- then there is nothing to slide.
 */
export function axisBounds(fullRange: TimeRange | null, step = 10): Bounds | null {
  if (!fullRange) return null;
  const min = roundToStep(fullRange.from, step, "down");
  // Past the last year, not up to it: the bar for 2024 has to have its own year of track to
  // stand on. Rounding to 2024 exactly would put it at the very end and let it run off the rail
  // -- the same thing happened to a decade bar starting in the last decade of the axis.
  const max = roundToStep(fullRange.to + 1, step, "up");
  // A collection from a single year would otherwise give an axis without length, and every
  // calculation on it a division by zero.
  return { min, max: max > min ? max : min + step };
}

/**
 * How tall a bar stands, in percent.
 *
 * **Square root, not linear.** In the Holm collection the 2020s hold 11 photos against the 2010s'
 * 245 -- linearly 4.5 %, which the floor below flattens to the same stub an empty decade would
 * get. The root makes it 21 %: clearly smaller, clearly there. The floor keeps a single photo
 * visible; zero stays zero, because nothing is not a little.
 */
export function barHeight(count: number, tallest: number): number {
  if (count <= 0) return 0;
  return Math.max(8, (Math.sqrt(count) / Math.sqrt(Math.max(1, tallest))) * 100);
}

/**
 * Move the whole selection along the axis, keeping its span.
 *
 * The quiet mistake sits at the ends: clamping each end for itself lets the range **shrink** when
 * it is pushed past the start of the axis -- the visitor drags sideways and watches their period
 * narrow. So the shift is what gets limited, never the ends.
 */
export function shiftRange(range: TimeRange, delta: number, bounds: Bounds): TimeRange {
  const possible = Math.min(Math.max(delta, bounds.min - range.from), bounds.max - range.to);
  return { from: range.from + possible, to: range.to + possible };
}

/**
 * The narrowest period the visitor can set, in years.
 *
 * A decade -- and the reason is physical, not statistical. The selected range **is** the surface
 * one grabs to walk the period along the axis; squeezed onto a single bar it has no surface left.
 * A drawn grip in the middle used to answer that case, which meant carrying a mark on screen for
 * a state nobody wants to be in. A floor under the width answers it without one.
 */
export const MIN_SPAN_YEARS = 10;

/** The floor on this axis: a decade, but never narrower than a single bar. */
export function minSpan(step: number): number {
  return Math.max(MIN_SPAN_YEARS, step);
}

/**
 * Move one end of the period, keeping it at least ``minSpan`` wide.
 *
 * The moving end stops; the other one is never pushed. Being pushed would let a drag at the left
 * carry the right end past the end of the axis, where it would then be clamped -- and the period
 * would come back narrower than it went. Stopping is also what a floor should feel like.
 *
 * Both ends are inclusive, so a decade is ``to - from === 9``.
 */
export function resizeRange(
  range: TimeRange,
  grip: "start" | "end",
  year: number,
  step: number,
): TimeRange {
  const span = minSpan(step);
  if (grip === "start") return { from: Math.min(year, range.to - span + 1), to: range.to };
  return { from: range.from, to: Math.max(year, range.from + span - 1) };
}

/** Where a year sits on the axis: 0 at the left end, 1 at the right. Never outside. */
export function fraction(year: number, bounds: Bounds): number {
  const raw = (year - bounds.min) / (bounds.max - bounds.min);
  return Math.min(1, Math.max(0, raw));
}

/**
 * The other way round: which year lies at that point of the track.
 *
 * The inverse of ``fraction``, and it belongs beside it rather than in the slider, because its
 * mistakes are the quiet kind. A rounding that goes the wrong way selects 1931 while the visitor
 * aimed at 1932, and nothing on screen looks wrong -- the map simply shows a slightly different
 * set. The test therefore checks the round trip: every year has to come back out of its own
 * fraction.
 *
 * Takes the raw share rather than a pointer position: where the finger is belongs to the DOM and
 * stays in the component, what that means belongs here. Clamped like ``fraction``, so a finger
 * dragged past the end of the track holds at the end instead of walking off the axis.
 */
export function yearAtFraction(share: number, bounds: Bounds): number {
  const clamped = Math.min(1, Math.max(0, share));
  return Math.round(bounds.min + clamped * (bounds.max - bounds.min));
}

/** Pull a selection into the axis, so the state cannot become invalid in the first place. */
export function clampRange(range: TimeRange, bounds: Bounds): TimeRange {
  const from = Math.min(Math.max(range.from, bounds.min), bounds.max);
  const to = Math.min(Math.max(range.to, bounds.min), bounds.max);
  return { from: Math.min(from, to), to: Math.max(from, to) };
}
