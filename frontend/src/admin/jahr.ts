/**
 * Die Regel für „ganzes Jahrzehnt".
 *
 * `date_range()` im Backend **rundet ein Jahrzehnt ab**: Aus 1934 mit Genauigkeit „Jahrzehnt"
 * werden kommentarlos die 1930er. Die 4 verschwindet, ohne dass jemand es merkt — genau die Art
 * Fehler, die in einem Museumsbestand jahrelang unentdeckt bleibt.
 *
 * Deshalb ist die Auswahl nur bei vollen Jahrzehnten zu haben. Wer 1934 meint, meint 1934.
 */

export type YearInput = { year: string; decade: boolean };

/** Volle Jahrzehnte, und nur die: 1920 ja, 1923 nein, „Kirchweih" nein. */
export function decadeAllowed(year: string): boolean {
  const parsed = Number.parseInt(year, 10);
  return Number.isFinite(parsed) && String(parsed) === year.trim() && parsed % 10 === 0;
}

/**
 * Eine neue Jahreszahl übernehmen — und das Häkchen mitnehmen, wenn es nicht mehr zulässig ist.
 *
 * Nur auszugrauen genügt nicht: Ein gesetztes, aber ausgegrautes Ankreuzfeld schickt beim
 * Absenden weiterhin „Jahrzehnt" mit und macht aus der 1923 stillschweigend die 1920er — also
 * genau der Fehler, den die Regel verhindern soll.
 */
export function withYear(current: YearInput, year: string): YearInput {
  return { year, decade: current.decade && decadeAllowed(year) };
}

/** Was daraus für die API wird: nichts, ein Jahr, oder ein Jahrzehnt. */
export function toBatchDate(input: YearInput): { year: number; precision: "year" | "decade" } | null {
  const parsed = Number.parseInt(input.year, 10);
  if (!Number.isFinite(parsed)) return null;
  return { year: parsed, precision: input.decade && decadeAllowed(input.year) ? "decade" : "year" };
}
