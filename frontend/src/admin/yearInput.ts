/**
 * Die Regel für „Jahrzehnt".
 *
 * `date_range()` im Backend **rundet ein Jahrzehnt ab**: Aus 1934 mit Genauigkeit „Jahrzehnt"
 * werden kommentarlos die 1930er. Die 4 verschwindet, ohne dass jemand es merkt — genau die Art
 * Fehler, die in einem Museumsbestand jahrelang unentdeckt bleibt.
 *
 * Deshalb ist die Auswahl nur bei vollen Jahrzehnten zu haben. Wer 1934 meint, meint 1934.
 */

export type Precision = "year" | "decade";

export type YearInput = { year: string; precision: Precision };

/** Volle Jahrzehnte, und nur die: 1920 ja, 1923 nein, „Kirchweih" nein. */
export function decadeAllowed(year: string): boolean {
  const parsed = Number.parseInt(year, 10);
  return Number.isFinite(parsed) && String(parsed) === year.trim() && parsed % 10 === 0;
}

/**
 * Eine neue Jahreszahl übernehmen — und die Genauigkeit mitnehmen, wenn sie nicht mehr zulässig
 * ist.
 *
 * Das Auswahlfeld nur zu sperren genügt nicht: Ein gesetztes, aber gesperrtes Feld schickt beim
 * Absenden weiterhin „Jahrzehnt" mit und macht aus der 1923 stillschweigend die 1920er — also
 * genau der Fehler, den die Regel verhindern soll.
 */
export function withYear(current: YearInput, year: string): YearInput {
  return { year, precision: decadeAllowed(year) ? current.precision : "year" };
}

/** Was daraus für die API wird: nichts, ein Jahr, oder ein Jahrzehnt. */
export function toDate(input: YearInput): { year: number; precision: Precision } | null {
  const parsed = Number.parseInt(input.year, 10);
  if (!Number.isFinite(parsed)) return null;
  return {
    year: parsed,
    precision: input.precision === "decade" && decadeAllowed(input.year) ? "decade" : "year",
  };
}

/**
 * Was ein gespeichertes Foto für die Eingabefelder bedeutet.
 *
 * Die Genauigkeit kommt aus dem Foto, **nicht** aus der Jahreszahl. Sonst würde aus einem als
 * Jahrzehnt gespeicherten 1920 beim Nachbearbeiten stillschweigend das Jahr 1920 — und die
 * Zeitleiste zeigte danach einen Punkt statt einer Spanne, ohne dass jemand etwas eingegeben
 * hätte.
 */
export function fromPhoto(dateFrom: string | null, precision: string): YearInput {
  if (!dateFrom) return { year: "", precision: "year" };
  return { year: dateFrom.slice(0, 4), precision: precision === "decade" ? "decade" : "year" };
}
