// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The rule behind "Jahrzehnt".
 *
 * `date_range()` in the backend **rounds a decade down**: 1934 with precision "decade" quietly
 * becomes the 1930s. The 4 disappears without anybody noticing -- exactly the kind of mistake
 * that stays undetected in a museum collection for years.
 *
 * Which is why the choice is only on offer for whole decades. Whoever means 1934 means 1934.
 */

export type Precision = "year" | "decade";

export type YearInput = { year: string; precision: Precision };

/** Whole decades and only those: 1920 yes, 1923 no, "Kirchweih" no. */
export function decadeAllowed(year: string): boolean {
  const parsed = Number.parseInt(year, 10);
  return Number.isFinite(parsed) && String(parsed) === year.trim() && parsed % 10 === 0;
}

/**
 * Take a new year -- and take the precision along with it when it is no longer allowed.
 *
 * Merely disabling the select is not enough: a set but disabled field still submits "decade" and
 * quietly turns 1923 into the 1920s -- exactly the mistake the rule is there to prevent.
 */
export function withYear(current: YearInput, year: string): YearInput {
  return { year, precision: decadeAllowed(year) ? current.precision : "year" };
}

/** What becomes of it for the API: nothing, a year, or a decade. */
export function toDate(input: YearInput): { year: number; precision: Precision } | null {
  const parsed = Number.parseInt(input.year, 10);
  if (!Number.isFinite(parsed)) return null;
  return {
    year: parsed,
    precision: input.precision === "decade" && decadeAllowed(input.year) ? "decade" : "year",
  };
}

/**
 * What a stored photo means for the input fields.
 *
 * The precision comes from the photo, **not** from the year. Otherwise a 1920 stored as a decade
 * would quietly become the year 1920 while somebody edits it -- and the timeline would show a
 * point instead of a span, without anybody having typed a thing.
 */
export function fromPhoto(dateFrom: string | null, precision: string): YearInput {
  if (!dateFrom) return { year: "", precision: "year" };
  return { year: dateFrom.slice(0, 4), precision: precision === "decade" ? "decade" : "year" };
}
