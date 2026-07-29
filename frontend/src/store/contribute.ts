/**
 * State of the "Hilf mit" panel.
 *
 * Kept apart from the map state because both run independently: the visitor can explore the map
 * while a question stands on the right, and the other way round.
 *
 * One exception -- locating a photo. There the pin is dropped on the very same map that shows the
 * photos. The pin therefore lives here and the map layer reads it.
 */

import { create } from "zustand";

import {
  type Need,
  type PhotoDetail,
  type Precision,
  type Task,
  fetchTask,
  postDate,
  postLocation,
} from "../api/client";
import { t } from "../texte/de";
import { useKiosk } from "./kiosk";

/** How long the thank-you note stays before the next question arrives. */
const THANKS_MS = 2200;

/**
 * Session key.
 *
 * Distinguishes visitors at the same device without identifying them: a random value per page
 * load, stored nowhere. The curator can tell whether ten statements came from one person or from
 * ten -- and should not be able to do more than that.
 */
const SESSION_ID = Math.random().toString(36).slice(2, 12);

/**
 * Remember only the last few skipped photos, otherwise nothing would be left to show.
 *
 * One list for both questions, not one each: a photo somebody has just waved away should not come
 * straight back with the other question on it. That would read as "you were not listening".
 */
const SKIP_MEMORY = 20;

type ContributeState = {
  need: Need;
  task: Task | null;
  loading: boolean;
  error: string | null;
  /** Right after a contribution: thank-you note instead of the next question. */
  thanks: string | null;

  /** Photos the visitor has just dismissed. This session only. */
  skipped: number[];

  /** Pin dropped on the map while the location question is running. */
  pin: { lat: number; lon: number } | null;
  /** Name from the place search, when set that way. */
  pinLabel: string | null;
  /**
   * How precise the pin is, in metres -- a house number is worth more than a street.
   *
   * Null for a pin someone tapped onto the map: how well they aimed is not for us to claim.
   * Dragging the pin clears it again, for the same reason.
   */
  pinAccuracy: number | null;

  load: (need?: Need) => Promise<void>;
  skip: () => void;
  setPin: (
    pin: { lat: number; lon: number } | null,
    details?: { label?: string | null; accuracyM?: number | null },
  ) => void;
  submitLocation: () => Promise<void>;
  submitDate: (year: number, precision: Precision) => Promise<void>;
  reset: () => void;
};

let abort: AbortController | null = null;
let thanksTimer: ReturnType<typeof setTimeout> | null = null;

/** The two questions take turns -- after a contribution and after "Weiß ich nicht" alike. */
export function otherNeed(current: Need): Need {
  return current === "location" ? "date" : "location";
}

export const useContribute = create<ContributeState>((set, get) => {
  /**
   * Fetch the next task, and fall back to the other question when this one has run dry.
   *
   * The fallback is what makes taking turns safe. Both kinds empty out at different rates -- in a
   * collection where every photo is placed but half of them are undated, always asking "where is
   * this?" would report "everything is complete" while hundreds of photos still wait for a year.
   */
  async function load(need: Need) {
    abort?.abort();
    abort = new AbortController();
    const signal = abort.signal;

    set({ loading: true, error: null, pin: null, pinLabel: null, pinAccuracy: null });
    try {
      const task = await fetchTask(need, get().skipped, signal);

      if (!task.photo) {
        const fallback = await fetchTask(otherNeed(need), get().skipped, signal);
        if (fallback.photo) {
          set({ task: fallback, need: otherNeed(need), loading: false });
          return;
        }
      }

      set({ task, need, loading: false });
    } catch (e) {
      if (signal.aborted) return;
      set({ loading: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  function showThanks(text: string, next: Need) {
    if (thanksTimer) clearTimeout(thanksTimer);
    set({ thanks: text });
    thanksTimer = setTimeout(() => {
      thanksTimer = null;
      set({ thanks: null });
      void load(next);
    }, THANKS_MS);
  }

  async function contribute(
    action: (photo: PhotoDetail) => Promise<PhotoDetail>,
    thanksText: string,
  ) {
    const { task, need } = get();
    if (!task?.photo) return;

    set({ loading: true, error: null });
    try {
      await action(task.photo);
      set({ loading: false, pin: null, pinLabel: null, pinAccuracy: null });

      // Map and timeline have to show it now. The thank-you note promises exactly that -- and
      // before this line it only came true once somebody happened to pan the map.
      useKiosk.getState().refresh();

      showThanks(thanksText, otherNeed(need));
    } catch (e) {
      // Most common case: somebody else was quicker (HTTP 409). The backend already phrases that
      // message kindly.
      set({ loading: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  return {
    need: "location",
    task: null,
    loading: false,
    error: null,
    thanks: null,
    skipped: [],
    pin: null,
    pinLabel: null,
    pinAccuracy: null,

    load: (need) => load(need ?? get().need),

    /**
     * "Weiß ich nicht -- nächstes Foto" changes the question, not just the picture.
     *
     * Whoever cannot place a photo may well know the decade, and the other way round. Asking the
     * same kind of question again is what makes a visitor give up after three pictures.
     */
    skip() {
      const { task, need, skipped } = get();
      const id = task?.photo?.id;
      set({
        skipped: id ? [...skipped, id].slice(-SKIP_MEMORY) : skipped,
        pin: null,
        pinLabel: null,
        pinAccuracy: null,
      });
      void load(otherNeed(need));
    },

    setPin(pin, details) {
      set({
        pin,
        pinLabel: details?.label ?? null,
        pinAccuracy: details?.accuracyM ?? null,
      });
    },

    async submitLocation() {
      const { pin, pinLabel, pinAccuracy } = get();
      if (!pin) return;
      await contribute(
        (photo) =>
          postLocation(photo.id, {
            lat: pin.lat,
            lon: pin.lon,
            ...(pinLabel ? { place_name: pinLabel } : {}),
            ...(pinAccuracy !== null ? { accuracy_m: pinAccuracy } : {}),
            session_id: SESSION_ID,
          }),
        t.help.thanksLocation,
      );
    },

    async submitDate(year, precision) {
      await contribute(
        (photo) => postDate(photo.id, { year, precision, session_id: SESSION_ID }),
        t.help.thanksDate,
      );
    },

    /** For the idle reset: forget everything and start over. */
    reset() {
      if (thanksTimer) clearTimeout(thanksTimer);
      thanksTimer = null;
      set({ skipped: [], pin: null, pinLabel: null, pinAccuracy: null, thanks: null, error: null });
      void load("location");
    },
  };
});
