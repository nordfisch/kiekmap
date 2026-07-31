/**
 * Die Rechnung hinter dem Zeitschieber.
 *
 * Als reine Funktionen, weil hier ein Fehler steckte, den man nicht am Code sieht, sondern erst
 * auf dem Bildschirm: Die Achse kam aus dem Histogramm des sichtbaren Ausschnitts und änderte sich
 * bei jedem Zoom, die Auswahl blieb stehen. Nach dem Hineinzoomen auf zwei Fotos aus den 1950ern
 * stand die Achse auf 1950–1960, die Auswahl aber weiterhin auf 1920–2019 — und der Auswahlbalken
 * lief mit `left: -300%` quer über Wappen und Titel.
 *
 * Zwei Riegel dagegen, beide hier:
 *
 *   1. Die Achse spannt über den ganzen Bestand und steht still (`collection_from`/`collection_to`
 *      aus dem Histogramm). Der Schieber bedeutet damit immer dasselbe.
 *   2. `fraction()` ist auf 0…1 geklammert. Selbst wenn Achse und Auswahl je wieder auseinander-
 *      laufen, kann kein Element mehr aus seiner Zelle laufen.
 */

import type { TimeRange } from "../api/client";

export type Bounds = { min: number; max: number };

/** Auf- und abrunden auf volle Jahrzehnte -- das liest sich schlicht besser als 1923 bis 2019. */
function roundToDecade(year: number, direction: "down" | "up"): number {
  return direction === "down" ? Math.floor(year / 10) * 10 : Math.ceil(year / 10) * 10;
}

/**
 * Die Enden der Achse.
 *
 * Null, solange der Bestand kein einziges datiertes Foto hat — dann gibt es nichts zu schieben.
 */
export function axisBounds(fullRange: TimeRange | null): Bounds | null {
  if (!fullRange) return null;
  const min = roundToDecade(fullRange.from, "down");
  const max = roundToDecade(fullRange.to, "up");
  // Ein einzelnes Jahr ergäbe sonst eine Achse ohne Länge und jede Rechnung darauf eine Division
  // durch null.
  return { min, max: max > min ? max : min + 10 };
}

/** Wo auf der Achse ein Jahr liegt: 0 am linken Ende, 1 am rechten. Nie daneben. */
export function fraction(year: number, bounds: Bounds): number {
  const raw = (year - bounds.min) / (bounds.max - bounds.min);
  return Math.min(1, Math.max(0, raw));
}

/** Eine Auswahl in die Achse ziehen, damit der Zustand gar nicht erst ungültig wird. */
export function clampRange(range: TimeRange, bounds: Bounds): TimeRange {
  const from = Math.min(Math.max(range.from, bounds.min), bounds.max);
  const to = Math.min(Math.max(range.to, bounds.min), bounds.max);
  return { from: Math.min(from, to), to: Math.max(from, to) };
}
