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

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("de-DE", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("de-DE", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
