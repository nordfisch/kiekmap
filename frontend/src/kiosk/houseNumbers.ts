/**
 * Aus einer Hausnummernliste eine Auswahl machen, die auf einen Bildschirm passt.
 *
 * Die Pinneberger Straße hat 163 Adressen, der Lehmweg 139, selbst der Mühlenweg 78. Als
 * Knopfraster ist das keine Auswahl mehr, sondern eine Suchaufgabe. Zwei Kürzungen, in dieser
 * Reihenfolge:
 *
 *   1. **Buchstabenzusätze fallen weg.** Jede fünfte Adresse in Holm ist eine (3a–3z am
 *      Mühlenweg ist eine Reihenhauszeile); räumlich fügen sie nichts hinzu — 3a und 3c liegen
 *      wenige Meter auseinander, und die Genauigkeitsangabe steht ohnehin bei 15 m. Beim
 *      Mühlenweg halbiert das die Liste.
 *   2. **Bleiben es zu viele, kommt ein Bereich davor** — „1–19", „20–39" —, genau wie das
 *      Jahrzehnt vor dem Jahr. Geschnitten wird nach Anzahl, nicht nach Zahlenwert: Straßen sind
 *      löchrig nummeriert, und zehn gleich große Blöcke sind besser als einundzwanzig verschieden
 *      volle.
 */

import type { Place } from "../api/client";

/** So viele Knöpfe verträgt eine Stufe. Darüber wird geteilt. */
export const MAX_BUTTONS = 12;

/** Die führende Zahl: aus „3c" wird 3, aus „10-18" wird 10. */
export function baseNumber(housenumber: string): number | null {
  const match = /^\d+/.exec(housenumber.trim());
  return match ? Number.parseInt(match[0], 10) : null;
}

/**
 * Je Grundzahl ein Eintrag.
 *
 * Vertreter ist die nackte Zahl, wenn es sie gibt — sonst der erste Eintrag der Gruppe. Die
 * Beschriftung bleibt damit immer eine Adresse, die es wirklich gibt: „3" wo 3 existiert, „3a" wo
 * die Zeile bei 3a anfängt. (Im ganzen Ort betrifft das 284 von 6174 Gruppen.)
 */
export function groupByBase(numbers: Place[]): Place[] {
  const groups = new Map<number, Place[]>();

  for (const place of numbers) {
    const base = baseNumber(place.housenumber ?? "");
    if (base === null) continue;
    const group = groups.get(base);
    if (group) group.push(place);
    else groups.set(base, [place]);
  }

  return [...groups.entries()]
    .sort(([a], [b]) => a - b)
    .map(([base, group]) => group.find((p) => p.housenumber === String(base)) ?? group[0]!);
}

export type NumberBlock = { label: string; numbers: Place[] };

/**
 * Die Bereiche der ersten Stufe — oder ein einziger, wenn alles auf eine Seite passt.
 *
 * Der Aufrufer überspringt die Stufe, sobald nur ein Block herauskommt. Bei Holms mittlerer Straße
 * (15 Adressen, nach dem Zusammenfassen meist ein Dutzend) ist das der Normalfall: Dort bleibt es
 * bei einem Schritt wie bisher.
 */
export function blocksOf(numbers: Place[], max = MAX_BUTTONS): NumberBlock[] {
  if (numbers.length <= max) return [{ label: "", numbers }];

  const count = Math.ceil(numbers.length / max);
  const size = Math.ceil(numbers.length / count);

  return Array.from({ length: count }, (_, i) => {
    const part = numbers.slice(i * size, (i + 1) * size);
    const first = part[0]?.housenumber ?? "";
    const last = part.at(-1)?.housenumber ?? "";
    return { label: first === last ? first : `${first}–${last}`, numbers: part };
  }).filter((block) => block.numbers.length > 0);
}
