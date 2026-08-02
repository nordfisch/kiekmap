/**
 * Der scrollende Bereich der Verwaltung, für die Ansichten darin erreichbar.
 *
 * Gescrollt wird nicht die einzelne Ansicht, sondern `.admin__body` um sie herum. Wechselt eine
 * Ansicht ihren Inhalt -- Fotoliste zu Editor, Importauswahl zu Ergebnis --, bleibt dieser
 * Container stehen und behält seinen `scrollTop`. Das neue Formular öffnet sich dann mittendrin,
 * und seine Überschrift steht oberhalb des Bildschirmrands.
 *
 * Weil der Container `AdminApp` gehört, der Wechsel aber in der Ansicht passiert, reicht ihn ein
 * Context durch. Das ist die Alternative dazu, jeder Ansicht ein weiteres Prop mitzugeben, das
 * mit ihrer eigentlichen Aufgabe nichts zu tun hat.
 */

import { type RefObject, createContext, useContext } from "react";

const ScrollAreaContext = createContext<RefObject<HTMLElement | null> | null>(null);

export const ScrollAreaProvider = ScrollAreaContext.Provider;

/**
 * Der scrollende Bereich, oder `null` ausserhalb der Verwaltung.
 *
 * Nur in Effekten benutzen: Das Ref sagt nicht Bescheid, wenn es sich füllt, und beim ersten
 * Rendern steht es noch leer.
 */
export function useScrollArea(): RefObject<HTMLElement | null> | null {
  return useContext(ScrollAreaContext);
}
