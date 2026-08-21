// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The arithmetic behind paging.
 *
 * Pure functions, because both ways this can go wrong go wrong silently: a list standing on an
 * empty page looks like a broken query.
 */

/** Rows per page. About three screenfuls -- as far as one swipe of a finger carries. */
export const PAGE_SIZE = 30;

export function pageCount(total: number, size = PAGE_SIZE): number {
  // An empty list has a page too: "Seite 1 von 0" would be a statement about nothing.
  return Math.max(1, Math.ceil(total / size));
}

/**
 * Pull the offset onto a page that still exists.
 *
 * The normal case in these views, not the exception: whoever locates the last entry of the last
 * page of "Ohne Ort" then stands past the end -- working through it makes the list shorter, after
 * all. Without this clamp an empty page would be left standing.
 */
export function clampOffset(offset: number, total: number, size = PAGE_SIZE): number {
  if (offset <= 0) return 0;
  return Math.min(offset, (pageCount(total, size) - 1) * size);
}

/** The page number shown on screen -- counted from 1, the way a person counts. */
export function pageNumber(offset: number, size = PAGE_SIZE): number {
  return Math.floor(Math.max(0, offset) / size) + 1;
}
