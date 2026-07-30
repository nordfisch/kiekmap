/**
 * Die Rechnung hinter dem Blättern.
 *
 * Als reine Funktionen, weil beide Fälle, die hier schiefgehen können, still schiefgehen: eine
 * Liste, die auf einer leeren Seite steht, sieht aus wie eine kaputte Abfrage.
 */

/** Zeilen je Seite. Rund drei Bildschirmseiten -- so weit trägt ein Wisch mit dem Finger. */
export const PAGE_SIZE = 30;

export function pageCount(total: number, size = PAGE_SIZE): number {
  // Auch eine leere Liste hat eine Seite: "Seite 1 von 0" wäre eine Auskunft über nichts.
  return Math.max(1, Math.ceil(total / size));
}

/**
 * Den Versatz auf eine Seite ziehen, die es noch gibt.
 *
 * Der Normalfall dieser Ansichten, nicht die Ausnahme: Wer den letzten Eintrag der letzten Seite
 * von „Ohne Ort" verortet, steht danach hinter dem Ende — die Liste wird beim Abarbeiten ja
 * kürzer. Ohne diese Klammer bliebe eine leere Seite stehen.
 */
export function clampOffset(offset: number, total: number, size = PAGE_SIZE): number {
  if (offset <= 0) return 0;
  return Math.min(offset, (pageCount(total, size) - 1) * size);
}

/** Die Seitenzahl, die auf dem Schirm steht — von 1 an gezählt, wie ein Mensch zählt. */
export function pageNumber(offset: number, size = PAGE_SIZE): number {
  return Math.floor(Math.max(0, offset) / size) + 1;
}
