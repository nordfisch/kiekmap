/**
 * Wie sich die Ansicht auf ein eben ergänztes Foto einstellt.
 *
 * Der Dank verspricht „Das Foto ist jetzt auf der Karte". Damit das stimmt, fährt die Karte für
 * die Dauer des Dankes zu dem Foto, und der Zeitraum stellt sich so, dass es auch wirklich zu
 * sehen ist. Danach kehrt beides zurück — nichts, was der Besucher selbst eingestellt hat, geht
 * verloren.
 *
 * Entschieden wird allein nach dem Foto, wie es jetzt dasteht, nicht danach, welcher der beiden
 * Wege den Beitrag ausgelöst hat.
 */

import type { PhotoDetail, TimeRange } from "../api/client";

/** Wie nah die Karte herangeht. Ein Radius, keine Zoomstufe: die hängt von der Fenstergröße ab. */
export const FOCUS_RADIUS_M = 100;

/** Grad Breite je Meter. Für die Länge kommt der Kosinus der Breite dazu. */
const M_PER_DEGREE = 111_320;

export function decadeOf(year: number): number {
  return Math.floor(year / 10) * 10;
}

/**
 * Der Zeitraum, in dem dieses Foto zu sehen ist.
 *
 * - Mit Jahr: sein Jahrzehnt. Wer eben „1932" getippt hat, sieht die Griffe auf die 1930er
 *   springen und sein Foto darin auftauchen.
 * - Ohne Jahr: ganz auf. **Undatierte Fotos stehen nur dann auf der Karte, wenn kein Zeitfilter
 *   aktiv ist** (siehe `_viewport_filters` im Backend). Wer den Schieber eingeengt hat und dann
 *   ein undatiertes Foto verortet, bekäme sonst eine leere Stelle zu sehen — unter dem Satz, das
 *   Foto sei jetzt auf der Karte.
 */
export function rangeForPhoto(photo: PhotoDetail, fullRange: TimeRange | null): TimeRange | null {
  if (photo.lat === null || photo.lon === null) return null;

  if (photo.date_from) {
    const decade = decadeOf(Number.parseInt(photo.date_from.slice(0, 4), 10));
    return { from: decade, to: decade + 9 };
  }
  return fullRange;
}

/** Das Quadrat um einen Punkt, das die Karte einpasst: [[West, Süd], [Ost, Nord]]. */
export function boundsAround(
  lat: number,
  lon: number,
  radiusM = FOCUS_RADIUS_M,
): [[number, number], [number, number]] {
  const dLat = radiusM / M_PER_DEGREE;
  const dLon = radiusM / (M_PER_DEGREE * Math.cos((lat * Math.PI) / 180));
  return [
    [lon - dLon, lat - dLat],
    [lon + dLon, lat + dLat],
  ];
}
