/**
 * Welche Jahrzehnte im „Hilf mit"-Bereich zur Auswahl stehen.
 *
 * Sie ergeben sich aus dem **Bestand**, nicht aus einer Einstellung: Was eine Sammlung umspannt,
 * weiß die Sammlung selbst am besten. Bisher stand das in `region.json` — einer Datei, in der
 * jeder andere Schlüssel Geografie beschreibt und die vom Kartenbau gelesen wird. Zwei
 * Jahreszahlen zu ändern zog damit einen Netzzugang und einen kompletten Kartenbau hinter sich
 * her.
 *
 * Dazu ein garantiertes Mindestfenster: Ein Gerät ohne ein einziges datiertes Foto hätte sonst
 * überhaupt keinen Knopf, und ein Bestand, der zufällig nur die 1950er umfasst, ließe einen
 * Besucher nicht sagen, was er weiß. Wächst die Sammlung darüber hinaus, wächst die Reihe mit —
 * ohne dass jemand eine Einstellung suchen muss.
 */

import type { TimeRange } from "../api/client";

/**
 * Die Jahrzehnte, die immer zur Wahl stehen.
 *
 * Kein sammlungsabhängiger Wert, sondern die Untergrenze für jeden Kiosk: das Jahrhundert, aus dem
 * die Fotos eines Heimatmuseums üblicherweise stammen.
 */
export const MINIMUM_DECADES = { first: 1920, last: 2010 };

function decadeOf(year: number): number {
  return Math.floor(year / 10) * 10;
}

/** Von der ältesten bis zur jüngsten, aufsteigend — so stehen sie auch auf dem Schirm. */
export function offeredDecades(collection: TimeRange | null): number[] {
  const first = Math.min(
    MINIMUM_DECADES.first,
    collection ? decadeOf(collection.from) : MINIMUM_DECADES.first,
  );
  const last = Math.max(
    MINIMUM_DECADES.last,
    collection ? decadeOf(collection.to) : MINIMUM_DECADES.last,
  );

  return Array.from({ length: (last - first) / 10 + 1 }, (_, i) => first + i * 10);
}
