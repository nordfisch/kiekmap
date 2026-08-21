// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The one line under a thumbnail on the map -- and the same line for a screen reader.
 *
 * **That it is one line for both is the point.** Until August 2026 the caption was built from
 * `place_name` and the read-aloud label from `title`, in two places. Nobody noticed, because until
 * the first stock was cleaned up the two said the same thing: 815 titles repeated the address
 * beside them. Once the titles became titles, the eye read "Hauenweg 7" while the ear heard
 * "Hermann Berg". Two formulations of the same thing drift apart; one cannot.
 *
 * The chain is **title, then address, then nothing** -- and the year where it is known. The address
 * stood there first (see decisions.md, Punkt 29), and for a good reason that has since expired.
 */

import type { PhotoMarker } from "../api/client";
import { t } from "../text/de";

/**
 * Does this place name carry a house number?
 *
 * A digit decides, which is the same yardstick the panel uses to find photos worth sharpening
 * (`open_filter("housenumber")` in `services/needs.py`). It errs towards "number known" -- a
 * "Straße des 17. Juni" would count as complete -- and that is the harmless direction: it stays
 * silent rather than claiming a gap that is not there.
 */
function hasHouseNumber(place: string): boolean {
  return /\d/.test(place);
}

/** What a single photo is called: its title, else its address -- or nothing. */
function nameOf(photo: PhotoMarker): string | null {
  if (photo.title) return photo.title;
  if (!photo.place_name) return null;
  return hasHouseNumber(photo.place_name)
    ? photo.place_name
    : t.map.addressWithoutNumber(photo.place_name);
}

/**
 * The caption for what sits on one marker -- one photo or a whole stack.
 *
 * **A stack only says what every photo in it agrees on.** They land on one marker because they
 * share a coordinate, which usually means they share an address; their titles they do not share.
 * Taking the topmost one would put "Gasthof Timm" over fifty pictures that are not of it. The
 * same rule already governed the address, and for the same reason -- EXIF-located photos can land
 * within a metre of each other without having anything to do with one another.
 *
 * **And a stack carries no year.** Fifty photos of Schulstraße 2 were taken across decades.
 */
export function captionOf(photos: PhotoMarker[]): string {
  const first = photos[0];
  if (!first) return "";

  if (photos.length > 1) {
    const shared = photos.every((other) => other.title === first.title);
    // Without a shared title the address may still hold -- it is the coarser statement.
    const name = shared
      ? nameOf(first)
      : photos.every((other) => other.place_name === first.place_name)
        ? nameOf({ ...first, title: null })
        : null;
    return name ?? "";
  }

  const name = nameOf(first);
  if (!name) return first.date_short;
  return first.date_short ? t.map.withDate(name, first.date_short) : name;
}
