/** Numbers and dates as they are read out loud in German. */

const NUMBER = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 1 });
const COUNT = new Intl.NumberFormat("de-DE");

/**
 * File sizes in the units printed on the packaging.
 *
 * Powers of a thousand, not of 1024: a stick sold as "32 GB" should show up as roughly 32 GB, not
 * as 29,8. Nobody at the museum is comparing this against `df`.
 */
export function formatBytes(bytes: number): string {
  for (const [unit, factor] of [
    ["GB", 1000 ** 3],
    ["MB", 1000 ** 2],
    ["kB", 1000],
  ] as const) {
    if (bytes >= factor) return `${NUMBER.format(bytes / factor)} ${unit}`;
  }
  return `${COUNT.format(bytes)} Bytes`;
}

export function formatCount(value: number): string {
  return COUNT.format(value);
}

/**
 * How long ago something was, as the heading of a tile.
 *
 * The edges get a word instead of a number: "0 Tage seit der letzten Sicherung" is a puzzle for
 * somebody who walks up to this device twice a year. Capitalised, because the value starts the
 * line.
 */
export function formatDaysSince(days: number | null): string {
  if (days === null) return "Noch nie";
  if (days <= 0) return "Heute";
  return COUNT.format(days);
}

/**
 * Three shapes for three lists, and the differences are deliberate.
 *
 * They lived in three places until 19 August 2026 -- one of them exported and used by nobody,
 * the other two written out by hand inside the components that show them. Gathered here because
 * this module is where formatting belongs; kept apart because each of them leaves out something
 * on purpose:
 *
 *   | where | shape | what it leaves out, and why |
 *   |---|---|---|
 *   | backup tile | `formatDate` | the time -- a backup is a day, not a minute |
 *   | contributions | `formatWhen` | the year -- the list holds this season's entries |
 *   | import log | `formatLogTime` | nothing, but writes the month as a number, because the
 *     column is narrow, right-aligned and set in `tabular-nums` so the rows line up |
 *
 * Folding them into one would cost either the alignment in the log or the readability in the
 * other two. **The time zone is not part of this decision** -- the backend names it, so every
 * one of the three is right by itself; see `docs/decisions.md`, point 58.
 */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("de-DE", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function formatWhen(iso: string): string {
  return new Date(iso).toLocaleString("de-DE", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatLogTime(iso: string): string {
  return new Date(iso).toLocaleString("de-DE", {
    day: "numeric",
    month: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
