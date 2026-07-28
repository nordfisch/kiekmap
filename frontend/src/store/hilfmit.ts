/**
 * Zustand des "Hilf mit"-Bereichs.
 *
 * Getrennt vom Kartenzustand, weil beides unabhaengig voneinander laeuft: der Besucher kann die
 * Karte erkunden, waehrend rechts eine Frage steht, und umgekehrt.
 *
 * Eine Ausnahme gibt es -- die Verortung. Dort wird der Pin auf derselben Karte gesetzt, die auch
 * die Fotos zeigt. Deshalb liegt der Pin hier und die Kartenebene liest ihn.
 */

import { create } from "zustand";

import {
  type Aufgabe,
  type Bedarf,
  type Genauigkeit,
  type PhotoDetail,
  ladeAufgabe,
  sendeDatum,
  sendeOrt,
} from "../api/client";

/** Wie lange die Dankesmeldung stehen bleibt, bevor die naechste Frage kommt. */
const DANK_MS = 2200;

/**
 * Kennung der Sitzung.
 *
 * Unterscheidet Besucher am selben Geraet, ohne sie zu identifizieren: eine Zufallszahl pro
 * Seitenaufruf, nirgends gespeichert. Der Kurator kann damit sehen, ob zehn Angaben von einer
 * Person stammen oder von zehn -- mehr soll sie nicht koennen.
 */
const SITZUNG = Math.random().toString(36).slice(2, 12);

type HilfMitState = {
  bedarf: Bedarf;
  aufgabe: Aufgabe | null;
  laedt: boolean;
  fehler: string | null;
  /** Kurz nach einem Beitrag: Dankesmeldung statt naechster Frage. */
  dank: string | null;

  /** Fotos, die der Besucher gerade weggetippt hat. Nur fuer diese Sitzung. */
  uebersprungen: number[];

  /** Gesetzter Pin auf der Karte, solange die Ortsfrage laeuft. */
  pin: { lat: number; lon: number } | null;
  /** Name aus der Ortssuche, falls darueber gesetzt. */
  pinName: string | null;

  hole: (bedarf?: Bedarf) => Promise<void>;
  ueberspringen: () => void;
  setzePin: (pin: { lat: number; lon: number } | null, name?: string | null) => void;
  bestaetigeOrt: () => Promise<void>;
  bestaetigeJahr: (jahr: number, genauigkeit: Genauigkeit) => Promise<void>;
  zuruecksetzen: () => void;
};

let abbruch: AbortController | null = null;
let dankTimer: ReturnType<typeof setTimeout> | null = null;

/** Nach einem Beitrag: welche Frage als naechstes? Die mit mehr offenen Fotos. */
function naechsterBedarf(aufgabe: Aufgabe | null, jetzt: Bedarf): Bedarf {
  if (!aufgabe) return jetzt;
  // Nach einem beantworteten Ort ist ein Jahr die willkommene Abwechslung -- und umgekehrt.
  return jetzt === "location" ? "date" : "location";
}

export const useHilfMit = create<HilfMitState>((set, get) => {
  async function laden(bedarf: Bedarf) {
    abbruch?.abort();
    abbruch = new AbortController();
    const signal = abbruch.signal;

    set({ laedt: true, fehler: null, pin: null, pinName: null });
    try {
      const aufgabe = await ladeAufgabe(bedarf, get().uebersprungen, signal);
      set({ aufgabe, bedarf, laedt: false });
    } catch (e) {
      if (signal.aborted) return;
      set({ laedt: false, fehler: e instanceof Error ? e.message : String(e) });
    }
  }

  function danke(text: string, weiter: Bedarf) {
    if (dankTimer) clearTimeout(dankTimer);
    set({ dank: text });
    dankTimer = setTimeout(() => {
      dankTimer = null;
      set({ dank: null });
      void laden(weiter);
    }, DANK_MS);
  }

  async function nachBeitrag(
    aktion: (foto: PhotoDetail) => Promise<PhotoDetail>,
    dankText: string,
  ) {
    const { aufgabe, bedarf } = get();
    if (!aufgabe?.photo) return;

    set({ laedt: true, fehler: null });
    try {
      await aktion(aufgabe.photo);
      set({ laedt: false, pin: null, pinName: null });
      danke(dankText, naechsterBedarf(aufgabe, bedarf));
    } catch (e) {
      // Haeufigster Fall: jemand anderes war schneller (HTTP 409). Die Meldung des Backends ist
      // dafuer schon freundlich formuliert.
      set({ laedt: false, fehler: e instanceof Error ? e.message : String(e) });
    }
  }

  return {
    bedarf: "location",
    aufgabe: null,
    laedt: false,
    fehler: null,
    dank: null,
    uebersprungen: [],
    pin: null,
    pinName: null,

    hole: (bedarf) => laden(bedarf ?? get().bedarf),

    ueberspringen() {
      const { aufgabe, bedarf, uebersprungen } = get();
      const id = aufgabe?.photo?.id;
      set({
        // Nur die letzten paar merken: sonst waere nach einer Weile nichts mehr uebrig, was
        // gezeigt werden darf, und der Bereich bliebe leer.
        uebersprungen: id ? [...uebersprungen, id].slice(-20) : uebersprungen,
        pin: null,
        pinName: null,
      });
      void laden(bedarf);
    },

    setzePin(pin, name = null) {
      set({ pin, pinName: name });
    },

    async bestaetigeOrt() {
      const { pin, pinName } = get();
      if (!pin) return;
      await nachBeitrag(
        (foto) =>
          sendeOrt(foto.id, {
            lat: pin.lat,
            lon: pin.lon,
            ...(pinName ? { place_name: pinName } : {}),
            session_id: SITZUNG,
          }),
        "Danke! Das Foto ist jetzt auf der Karte.",
      );
    },

    async bestaetigeJahr(jahr, genauigkeit) {
      await nachBeitrag(
        (foto) => sendeDatum(foto.id, { year: jahr, precision: genauigkeit, session_id: SITZUNG }),
        "Danke! Das Foto ist jetzt auf der Zeitleiste.",
      );
    },

    /** Fuer den Leerlauf-Reset: alles vergessen und von vorn anfangen. */
    zuruecksetzen() {
      if (dankTimer) clearTimeout(dankTimer);
      dankTimer = null;
      set({ uebersprungen: [], pin: null, pinName: null, dank: null, fehler: null });
      void laden("location");
    },
  };
});
