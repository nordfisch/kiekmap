/**
 * Zustand der Besucheransicht.
 *
 * Zwei Schleifen laufen hier mit unterschiedlicher Geschwindigkeit:
 *
 *   langsam  Kartenausschnitt oder Zeitraum aendern sich -> nach kurzer Ruhe eine Abfrage
 *   schnell  die Karte wird geschoben -> die vorhandenen Fotos werden neu geclustert
 *
 * Ohne diese Trennung liefe bei jedem Ruckeln am Touchscreen eine Anfrage los.
 */

import { create } from "zustand";

import {
  type Bbox,
  type Histogramm,
  type PhotoMarker,
  type Zeitraum,
  ladeHistogramm,
  ladePhotos,
} from "../api/client";

/** So lange muss die Karte ruhig stehen, bevor geladen wird. */
export const RUHE_MS = 250;

/** Mehr Marker ergeben auf einer Karte keinen Sinn -- und der Pi soll flott bleiben. */
export const HOECHSTZAHL = 500;

type KioskState = {
  bbox: Bbox | null;
  zeitraum: Zeitraum | null;
  /** Die volle Spanne aus dem Histogramm. Der Schieber kann nicht darueber hinaus. */
  spanne: Zeitraum | null;

  photos: PhotoMarker[];
  total: number;
  truncated: boolean;
  histogramm: Histogramm | null;

  laedt: boolean;
  fehler: string | null;

  /** Nummer des gross angezeigten Fotos, oder null. */
  offenesFoto: number | null;

  setzeAusschnitt: (bbox: Bbox) => void;
  setzeZeitraum: (zeitraum: Zeitraum) => void;
  oeffneFoto: (id: number | null) => void;
  zuruecksetzen: () => void;
};

let photoAbbruch: AbortController | null = null;
let histogrammAbbruch: AbortController | null = null;
let ruheTimer: ReturnType<typeof setTimeout> | null = null;

export function gleicherAusschnitt(a: Bbox | null, b: Bbox | null): boolean {
  if (!a || !b) return a === b;
  return a.every((wert, index) => Math.abs(wert - b[index]!) < 1e-5);
}

/**
 * Welcher Zeitfilter an das Backend geht.
 *
 * Deckt die Auswahl die ganze bekannte Spanne ab, ist der Filter wirkungslos -- dann lieber keinen
 * schicken. Das ist kein Geschwindigkeitstrick: mit Filter fallen Fotos heraus, deren Datierung am
 * Rand liegt oder deren Intervall ueber die Spanne hinausreicht. Der Besucher, der nichts
 * eingestellt hat, soll aber alles sehen.
 */
export function filterFuerAbfrage(
  zeitraum: Zeitraum | null,
  spanne: Zeitraum | null,
): Zeitraum | null {
  if (!zeitraum || !spanne) return null;
  const deckungsgleich = zeitraum.von <= spanne.von && zeitraum.bis >= spanne.bis;
  return deckungsgleich ? null : zeitraum;
}

export const useKiosk = create<KioskState>((set, get) => {
  async function lade() {
    const { bbox, zeitraum, spanne } = get();
    if (!bbox) return;

    // Ueberholte Anfragen verwerfen: am Touchscreen wird schnell hintereinander gewischt, und die
    // Antwort auf einen laengst verlassenen Ausschnitt darf die aktuelle nicht ueberschreiben.
    photoAbbruch?.abort();
    photoAbbruch = new AbortController();
    const signal = photoAbbruch.signal;

    set({ laedt: true, fehler: null });
    try {
      const liste = await ladePhotos(bbox, filterFuerAbfrage(zeitraum, spanne), HOECHSTZAHL, signal);
      set({
        photos: liste.photos,
        total: liste.total,
        truncated: liste.truncated,
        laedt: false,
      });
    } catch (e) {
      if (signal.aborted) return;
      set({ laedt: false, fehler: e instanceof Error ? e.message : String(e) });
    }
  }

  async function ladeHistogrammFuer(bbox: Bbox) {
    histogrammAbbruch?.abort();
    histogrammAbbruch = new AbortController();
    const signal = histogrammAbbruch.signal;

    try {
      const histogramm = await ladeHistogramm(bbox, signal);
      if (signal.aborted) return;

      const { zeitraum } = get();
      const neueSpanne =
        histogramm.earliest !== null && histogramm.latest !== null
          ? { von: histogramm.earliest, bis: histogramm.latest }
          : null;

      set({
        histogramm,
        spanne: neueSpanne,
        // Beim ersten Mal die ganze Spanne auswaehlen: der Besucher soll zuerst alles sehen und
        // dann einschraenken, nicht umgekehrt. Eine getroffene Auswahl bleibt unangetastet, auch
        // wenn sich die Spanne beim Verschieben der Karte aendert.
        zeitraum: zeitraum ?? neueSpanne,
      });
    } catch {
      /* Ohne Histogramm bleibt der Schieber leer -- die Karte funktioniert weiter. */
    }
  }

  function angestossen() {
    if (ruheTimer) clearTimeout(ruheTimer);
    ruheTimer = setTimeout(() => {
      ruheTimer = null;
      void lade();
    }, RUHE_MS);
  }

  return {
    bbox: null,
    zeitraum: null,
    spanne: null,
    photos: [],
    total: 0,
    truncated: false,
    histogramm: null,
    laedt: false,
    fehler: null,
    offenesFoto: null,

    setzeAusschnitt(bbox) {
      if (gleicherAusschnitt(get().bbox, bbox)) return;
      set({ bbox });
      angestossen();
      void ladeHistogrammFuer(bbox);
    },

    setzeZeitraum(zeitraum) {
      const jetzt = get().zeitraum;
      if (jetzt && jetzt.von === zeitraum.von && jetzt.bis === zeitraum.bis) return;
      set({ zeitraum });
      angestossen();
    },

    oeffneFoto(id) {
      set({ offenesFoto: id });
    },

    /** Fuer den Leerlauf-Reset: zurueck in den Zustand, in dem das Geraet morgens stehen soll. */
    zuruecksetzen() {
      const { spanne } = get();
      set({ offenesFoto: null, zeitraum: spanne });
      angestossen();
    },
  };
});
