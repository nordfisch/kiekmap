// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Turning the streets of a village into a choice that fits on one screen.
 *
 * The panel has no text field any more -- a search box that takes nothing without a keyboard is
 * worse than no box at all. So the street is asked the way the year is asked: the rough group
 * first, then the exact one. Holm offers 80 streets; they fall into ten letter groups of which
 * seven lead straight to the list. Only the crowded A, H and I need a step in between.
 *
 * The groups are computed, never written down. A second museum gets its own tree without anybody
 * counting letters -- which is the whole point of keeping the village out of the code.
 */

import type { Place } from "../api/client";

/** As many buttons as one step can carry. Beyond that it is split again. */
export const MAX_BUTTONS = 10;

export type StreetGroup = { label: string; streets: Place[] };

/**
 * The key a street is filed under: lower case, without diacritics.
 *
 * Without this the "Ölmühlenweg" gets a lonely Ö button and stands behind the Z. Holm has no such
 * street -- the next village might, and then it would go wrong quietly.
 *
 * Matches `normalize()` in `app/services/places.py`, which sorts the list that arrives here.
 */
function key(name: string): string {
  return name.replace(/ß/g, "ss").normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
}

/** "am" becomes "Am", "sch" becomes "Sch" -- a label out of the key, not out of one name. */
function label(prefix: string): string {
  const trimmed = prefix.trimEnd();
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

/** Streets by the first `length` characters of their key, in the order they came in. */
function pots(streets: Place[], length: number): Map<string, Place[]> {
  const found = new Map<string, Place[]>();
  for (const street of streets) {
    const prefix = key(street.name).slice(0, length);
    const pot = found.get(prefix);
    if (pot) pot.push(street);
    else found.set(prefix, [street]);
  }
  return found;
}

/**
 * The groups of one step -- or a single one when everything fits on one page.
 *
 * The caller skips the step as soon as only one group comes out, exactly like `blocksOf` for the
 * house numbers. Two rules, in this order:
 *
 *   1. **Cut by the shortest prefix that gives enough groups.** One letter for a whole village,
 *      two inside a letter ("Am", "An"), four inside "Am " -- the split follows the names rather
 *      than a fixed depth.
 *   2. **Merge the thinnest neighbours back together** until at most `max` buttons remain. A
 *      village has four streets on M and none on Q; a button per letter would waste the screen
 *      on empty ones.
 *
 * Expects the list sorted the way the backend sorts it. Feeding a group back in gives the next
 * level down -- the function carries every step.
 */
export function groupStreets(streets: Place[], max = MAX_BUTTONS): StreetGroup[] {
  if (streets.length <= max) return [{ label: "", streets }];

  const longest = Math.max(...streets.map((street) => key(street.name).length));
  let length = 1;
  let split = pots(streets, length);
  // The first letter is the coarsest cut and therefore the one easiest to read -- the prefix only
  // grows while it separates nothing at all. That is the "Am ..." case: fourteen streets on one
  // letter, then on "Am", then on "Am " -- it takes four characters before they come apart.
  while (split.size === 1 && length < longest) {
    length += 1;
    split = pots(streets, length);
  }

  const groups = [...split.entries()].map(([prefix, part]) => ({
    from: prefix,
    to: prefix,
    streets: part,
  }));

  while (groups.length > max) {
    let smallest = 0;
    for (let i = 1; i < groups.length - 1; i++) {
      const here = groups[i]!.streets.length + groups[i + 1]!.streets.length;
      const best = groups[smallest]!.streets.length + groups[smallest + 1]!.streets.length;
      if (here < best) smallest = i;
    }
    const merged = groups[smallest]!;
    const next = groups[smallest + 1]!;
    groups.splice(smallest, 2, {
      from: merged.from,
      to: next.to,
      streets: [...merged.streets, ...next.streets],
    });
  }

  return groups.map((group) => ({
    label: group.from === group.to ? label(group.from) : `${label(group.from)}–${label(group.to)}`,
    streets: group.streets,
  }));
}
