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
  NEEDS,
  type Need,
  type PhotoDetail,
  type Place,
  type Precision,
  type Task,
  fetchTask,
  postDate,
  postHouseNumber,
  postLocation,
} from "../api/client";
import { t } from "../text/de";
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

  /**
   * Is a tap on the map allowed to drop the pin?
   *
   * Off by default: while "Wo ist das?" stands, somebody who only wants to look around -- pan the
   * map, get their bearings, find a photo nearby -- would otherwise answer the question by
   * accident, and one confirming tap later a place nobody meant is in the collection.
   *
   * **Lives here rather than in ``LocationTask``** so that it falls back on *every* route to the
   * next photo. The component is normally torn down on the way (``HelpPanel`` swaps it for
   * ``DateTask``), which would clear a ``useState`` by itself -- but not when ``load`` falls back
   * to the question it started from because the other one has run dry. That case arrives exactly
   * when one kind of gap has been worked off, and it would leave the map armed over a photo the
   * visitor has not looked at yet.
   */
  pickingOnMap: boolean;

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

  /**
   * The house numbers currently on the buttons -- the map draws them beside the photos.
   *
   * Lives here rather than in the component for the same reason the pin does: the map is a
   * different corner of the tree, and it has to read what the panel is offering.
   */
  offeredNumbers: Place[];
  setOfferedNumbers: (numbers: Place[]) => void;

  load: (need?: Need) => Promise<void>;
  skip: () => void;
  setPickingOnMap: (on: boolean) => void;
  setPin: (
    pin: { lat: number; lon: number } | null,
    details?: { label?: string | null; accuracyM?: number | null },
  ) => void;
  submitLocation: () => Promise<void>;
  submitDate: (year: number, precision: Precision) => Promise<void>;
  submitHouseNumber: (placeId: number) => Promise<void>;
  submitDateFor: (photoId: number, year: number, precision: Precision) => Promise<PhotoDetail>;
  submitHouseNumberFor: (photoId: number, placeId: number) => Promise<PhotoDetail>;
};

let abort: AbortController | null = null;
let thanksTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * "housenumber" sharpens "location" -- and therefore never follows it.
 *
 * The one real exception to the plain ranking, and it is worth a line of its own: somebody who
 * has just pressed "Reicht so — die Straße genügt" must not be asked "Genauer: welche
 * Hausnummer?" in the same breath. That reads as though nobody had been listening.
 */
const refines: Partial<Record<Need, Need>> = { housenumber: "location" };

/**
 * Where to go from here: every other question, in rank order.
 *
 * The ranking *is* the array -- "sharpening comes last" needs no case distinction. Callers walk
 * the list and take the first that leads anywhere.
 */
export function nextNeeds(current: Need): Need[] {
  return NEEDS.filter((need) => need !== current);
}

/**
 * Where to go after somebody has **answered** ``current`` -- the same list, minus the question
 * their answer already settled.
 *
 * The distinction matters and is easy to lose: running dry and being answered are not the same
 * thing. ``nextNeeds`` covers a question that had nothing left, where every other one is fair
 * game. Only an answer can make a further question redundant.
 */
export function nextAfterAnswer(current: Need): Need[] {
  return nextNeeds(current).filter((need) => refines[need] !== current);
}

/**
 * Does this photo still owe an answer to that question?
 *
 * **Not for "housenumber", and that is not an oversight.** Whether a photo can be sharpened
 * depends on the gazetteer -- whether its street holds addresses at all -- and a photo object has
 * never seen it (see `services/needs.py`). The chain, which hands the same photo on to the next
 * question, therefore never leads into the sharpening question; the panel reaches it through a
 * fresh task instead.
 */
export function stillNeeds(photo: PhotoDetail, need: Need): boolean {
  if (need === "location") return photo.needs_location;
  if (need === "date") return photo.needs_date;
  return false;
}

/**
 * The thank-you for an answered question.
 *
 * Only where the photo is complete may it name what became visible. Where the same photo carries
 * on, the sentence asks the question that really follows -- a promise nobody can see kept is
 * worse than no sentence at all.
 */
export function thanksFor(answered: Need, chained: Need | null): string {
  return chained ? t.help.thanksAsk[chained] : t.help.thanks[answered];
}

export const useContribute = create<ContributeState>((set, get) => {
  /**
   * Put up the next task, trying the questions in the order given.
   *
   * **``order`` rather than a single question**, because falling back is what makes taking turns
   * safe: the kinds empty out at different rates, and in a collection where every photo is placed
   * but half of them are undated, always asking "where is this?" would report "everything is
   * complete" while hundreds of photos still wait for a year.
   *
   * That the caller hands over the whole order is the point. Only the caller knows *why* it is
   * loading -- and a question that was just answered has to stay out of the fallback too, not only
   * out of the first attempt (see ``nextAfterAnswer``). With a single question plus a fallback
   * computed here, "Reicht so — die Straße genügt" was answered with "Welche Hausnummer?" two
   * seconds later.
   *
   * ``prefer`` carries a photo that has just been contributed to. If it still owes an answer to
   * the first question, it is put up instead of the random one -- see the chain in
   * ``contribute()``.
   */
  async function load(order: Need[], prefer?: PhotoDetail | null) {
    abort?.abort();
    abort = new AbortController();
    const signal = abort.signal;

    // Changing photo or question puts the map back where the visitor had it. Covers "Weiss ich
    // nicht" as well; after a contribution the thank-you timer has already done it, and doing it
    // twice does no harm.
    useKiosk.getState().releaseFocus();

    set({
      loading: true,
      error: null,
      pin: null,
      pinLabel: null,
      pinAccuracy: null,
      pickingOnMap: false,
      offeredNumbers: [],
    });
    try {
      const need = order[0]!;
      const task = await fetchTask(need, get().skipped, signal);

      // The counts come from the fetch, only the photo is swapped -- so the panel keeps saying
      // truthfully how much is still open. Deliberately ignores ``skipped``: whoever waved a
      // photo away earlier and has now told us something about it after all gets it back with
      // the other question, and "Weiß ich nicht" remains the way out.
      if (prefer && stillNeeds(prefer, need)) {
        set({ task: { ...task, photo: prefer }, need, loading: false });
        return;
      }

      if (!task.photo) {
        for (const other of order.slice(1)) {
          const fallback = await fetchTask(other, get().skipped, signal);
          if (fallback.photo) {
            set({ task: fallback, need: other, loading: false });
            return;
          }
        }
      }

      set({ task, need, loading: false });
    } catch (e) {
      if (signal.aborted) return;
      set({ loading: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  function showThanks(text: string, order: Need[], prefer: PhotoDetail | null) {
    if (thanksTimer) clearTimeout(thanksTimer);
    set({ thanks: text });
    thanksTimer = setTimeout(() => {
      thanksTimer = null;
      set({ thanks: null });
      // Map and time range come back as the thank-you goes -- both live exactly as long as it
      // does, without a second timer.
      useKiosk.getState().releaseFocus();
      void load(order, prefer);
    }, THANKS_MS);
  }

  /**
   * Apply a contribution, then thank -- and hand the same photo on where something is still open.
   *
   * **The chain is what keeps the thank-you honest.** "Das Foto ist jetzt auf der Zeitleiste" is a
   * promise the view cannot keep for a photo without a place: ``showPhoto()`` leaves map and
   * slider alone, so the visitor reads a sentence and sees nothing. Where something is missing,
   * the thank-you therefore asks about it instead of claiming anything -- and the next question is
   * about *this* photo rather than a random one. Somebody who has just shown they know this
   * picture, and is looking straight at it, is the best moment the panel ever gets.
   *
   * It ends by itself: once nothing is missing, ``stillNeeds`` is false and the next photo comes.
   */
  async function contribute(action: (photo: PhotoDetail) => Promise<PhotoDetail>) {
    const { task, need } = get();
    if (!task?.photo) return;

    set({ loading: true, error: null });
    try {
      // The backend hands back the updated photo -- place and date therefore come first hand
      // instead of being guessed at again here.
      const updated = await action(task.photo);
      set({ loading: false, pin: null, pinLabel: null, pinAccuracy: null, pickingOnMap: false });

      // Map and timeline have to show it now. The thank-you note promises exactly that -- and
      // before this line it only came true once somebody happened to pan the map.
      useKiosk.getState().refresh();
      // And the view settles on this one photo for as long as the thank-you stands.
      useKiosk.getState().showPhoto(updated);

      // The first of the remaining questions this very photo can still answer comes first; the
      // rest follow as the fallback, with the answered question last of all. What is *not* in the
      // list is the question this answer settled -- see ``nextAfterAnswer``.
      const others = nextAfterAnswer(need);
      const chained = others.find((other) => stillNeeds(updated, other)) ?? null;
      const order = chained ? [chained, ...others.filter((o) => o !== chained)] : others;
      showThanks(thanksFor(need, chained), [...order, need], chained ? updated : null);
    } catch (e) {
      // Most common case: somebody else was quicker (HTTP 409). The backend already phrases that
      // message kindly.
      set({ loading: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  return {
    // The highest-ranked question, not a name written out again -- the ranking is the array.
    need: NEEDS[0],
    task: null,
    loading: false,
    error: null,
    thanks: null,
    skipped: [],
    pickingOnMap: false,
    pin: null,
    pinLabel: null,
    pinAccuracy: null,
    offeredNumbers: [],

    setOfferedNumbers(numbers) {
      set({ offeredNumbers: numbers });
    },

    load(need) {
      const first = need ?? get().need;
      return load([first, ...nextNeeds(first)]);
    },

    /**
     * "Weiß ich nicht -- nächstes Foto" changes the question, not just the picture.
     *
     * Whoever cannot place a photo may well know the decade, and the other way round. Asking the
     * same kind of question again is what makes a visitor give up after three pictures. Where the
     * next question has nothing left, ``load`` carries on down the ranking.
     */
    skip() {
      const { task, need, skipped } = get();
      const id = task?.photo?.id;
      set({
        skipped: id ? [...skipped, id].slice(-SKIP_MEMORY) : skipped,
        pin: null,
        pinLabel: null,
        pinAccuracy: null,
        pickingOnMap: false,
      });
      // The skipped question last: it stays reachable with a different photo, but only once
      // everything else has run dry.
      void load([...nextNeeds(need), need]);
    },

    setPickingOnMap(on) {
      set({ pickingOnMap: on });
    },

    setPin(pin, details) {
      set({
        pin,
        pinLabel: details?.label ?? null,
        pinAccuracy: details?.accuracyM ?? null,
      });

      // Out of the place search -- the only thing that sets a label -- the map takes the visitor
      // along: they did not place the pin themselves and want to see where it landed. A pin
      // tapped onto the map or dragged leaves it alone: that is where they just aimed, and a map
      // that jumps out from under a finger feels like slipping.
      if (pin && details?.label) useKiosk.getState().showLocation(pin.lat, pin.lon);
      // "Punkt entfernen" takes the zoom back too.
      if (!pin) useKiosk.getState().releaseFocus();
    },

    async submitLocation() {
      const { pin, pinLabel, pinAccuracy } = get();
      if (!pin) return;
      await contribute((photo) =>
        postLocation(photo.id, {
          lat: pin.lat,
          lon: pin.lon,
          ...(pinLabel ? { place_name: pinLabel } : {}),
          ...(pinAccuracy !== null ? { accuracy_m: pinAccuracy } : {}),
          session_id: SESSION_ID,
        }),
      );
    },

    async submitDate(year, precision) {
      await contribute((photo) => postDate(photo.id, { year, precision, session_id: SESSION_ID }));
    },

    async submitHouseNumber(placeId) {
      await contribute((photo) =>
        postHouseNumber(photo.id, { place_id: placeId, session_id: SESSION_ID }),
      );
    },

    /**
     * A year for a photo that is **not** the one the running question is about.
     *
     * The case is the detail view: whoever looks at an undated photo full screen and knows when
     * it was should be able to say so right there. Which is why this route deliberately does
     * **not** go through ``contribute()``:
     *
     *   * **No thank-you.** The feedback is the view itself -- "Jahr unbekannt" becomes "1932"
     *     and the buttons disappear, exactly where the visitor is looking. A sentence saying so
     *     again, and hiding the contribution panel for 2.2 seconds while it does, would only be
     *     in the way here.
     *   * **No map focus.** The map lies underneath the detail view; moving it anywhere would be
     *     seen by nobody.
     *
     * Errors stay with the caller: the detail view shows them where its messages always stand.
     */
    async submitDateFor(photoId, year, precision) {
      const updated = await postDate(photoId, { year, precision, session_id: SESSION_ID });

      // Map and timeline have to show it: the photo moves out of "ohne Jahr" into a decade bar,
      // and with a narrowed time range possibly out of view altogether.
      useKiosk.getState().refresh();

      // Was the contribution panel asking about *this* photo's year, it has to move on. Otherwise
      // it puts it up again, the visitor answers a second time -- and gets "Dieses Foto hat
      // inzwischen schon eine Angabe bekommen", a message that sounds as though somebody else had
      // been quicker. About the *place* it may keep asking for the same photo: that one is still
      // needed.
      // The place is usually already known here -- a photo reaches the detail view by way of its
      // marker. Where it is not, ``prefer`` carries the chain into this route as well.
      const { task, need } = get();
      if (need === "date" && task?.photo?.id === photoId) {
        void load([...nextAfterAnswer(need), need], updated);
      }

      return updated;
    },

    /**
     * A house number for a photo that so far only knows its street.
     *
     * Same route as ``submitDateFor`` and for the same reasons -- no thank-you, no map focus, the
     * error stays with the caller. What the visitor gets to see is the line above the picker: "Am
     * Kamp" becomes "Am Kamp 12" and the buttons are gone.
     *
     * Only the id of the address travels. Coordinate and accuracy come from the gazetteer, on the
     * server -- see ``api/contribute.py``; the client determines nothing here.
     *
     * Errors stay with the caller: the detail view shows them where its messages always stand.
     */
    async submitHouseNumberFor(photoId, placeId) {
      const updated = await postHouseNumber(photoId, { place_id: placeId, session_id: SESSION_ID });

      // The marker moves from the middle of the street to the house. Without this it stays where
      // it was until somebody happens to pan the map.
      useKiosk.getState().refresh();

      // Only where the panel was asking *this* photo for its number. About its place it never
      // asks -- a photo that can be sharpened is located -- and its year is untouched here.
      const { task, need } = get();
      if (need === "housenumber" && task?.photo?.id === photoId) {
        void load([...nextAfterAnswer(need), need]);
      }

      return updated;
    },
  };
});
