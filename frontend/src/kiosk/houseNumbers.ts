/**
 * Turning a list of house numbers into a choice that fits on one screen.
 *
 * The Pinneberger Straße has 163 addresses, the Lehmweg 139, even the Mühlenweg 78. As a grid of
 * buttons that is no longer a choice but a search task. Two cuts, in this order:
 *
 *   1. **Letter suffixes fall away.** Every fifth address in Holm is one (3a-3z on the Mühlenweg
 *      is a terrace); spatially they add nothing -- 3a and 3c lie a few metres apart, and the
 *      accuracy is stated as 15 m anyway. On the Mühlenweg this halves the list.
 *   2. **If too many remain, a block step comes first** -- "1-19", "20-39" -- exactly like the
 *      decade before the year. Cut by count, not by numeric value: streets are numbered with
 *      gaps, and ten equally sized blocks beat twenty-one differently full ones.
 */

import type { Place } from "../api/client";

/** As many buttons as one step can carry. Beyond that it is split. */
export const MAX_BUTTONS = 12;

/** The leading number: "3c" becomes 3, "10-18" becomes 10. */
export function baseNumber(housenumber: string): number | null {
  const match = /^\d+/.exec(housenumber.trim());
  return match ? Number.parseInt(match[0], 10) : null;
}

/**
 * One entry per base number.
 *
 * The representative is the bare number where it exists -- otherwise the first entry of the
 * group. The label therefore always stays an address that really exists: "3" where 3 exists, "3a"
 * where the terrace starts at 3a. (Across the whole village that affects 284 of 6174 groups.)
 */
export function groupByBase(numbers: Place[]): Place[] {
  const groups = new Map<number, Place[]>();

  for (const place of numbers) {
    const base = baseNumber(place.housenumber ?? "");
    if (base === null) continue;
    const group = groups.get(base);
    if (group) group.push(place);
    else groups.set(base, [place]);
  }

  return [...groups.entries()]
    .sort(([a], [b]) => a - b)
    .map(([base, group]) => group.find((p) => p.housenumber === String(base)) ?? group[0]!);
}

export type NumberBlock = { label: string; numbers: Place[] };

/**
 * The blocks of the first step -- or a single one when everything fits on one page.
 *
 * The caller skips the step as soon as only one block comes out. For Holm's average street (15
 * addresses, usually a dozen after merging) that is the normal case: there it stays at one step
 * as before.
 */
export function blocksOf(numbers: Place[], max = MAX_BUTTONS): NumberBlock[] {
  if (numbers.length <= max) return [{ label: "", numbers }];

  const count = Math.ceil(numbers.length / max);
  const size = Math.ceil(numbers.length / count);

  return Array.from({ length: count }, (_, i) => {
    const part = numbers.slice(i * size, (i + 1) * size);
    const first = part[0]?.housenumber ?? "";
    const last = part.at(-1)?.housenumber ?? "";
    return { label: first === last ? first : `${first}–${last}`, numbers: part };
  }).filter((block) => block.numbers.length > 0);
}
