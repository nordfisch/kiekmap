/**
 * A photo tapped in the slide show, carried across the reload that follows.
 *
 * The show ends with a reload, the way the idle timer and the coat of arms always brought the
 * device back to a clean state. What the visitor tapped has to survive it, and sessionStorage is
 * what survives a reload and nothing more: it dies with the tab, so a note left behind cannot
 * open a photo the next morning.
 */

const KEY = "kiekmap.showcase.open";

/**
 * How far around the photo the map opens, in metres.
 *
 * A few streets: close enough that the place is recognisable, far enough that the photos around
 * it are on the map as well. The focus after a contribution uses 100 m, which is right for a pin
 * that was just set and too close for somebody who has not looked at the map yet.
 */
export const HANDOFF_RADIUS_M = 300;

export type Handoff = { id: number; lat: number; lon: number };

type Storage = Pick<globalThis.Storage, "getItem" | "setItem" | "removeItem">;

function session(): Storage | null {
  try {
    return globalThis.sessionStorage ?? null;
  } catch {
    return null;
  }
}

/** Leave a note for the page that comes after the reload. */
export function leaveHandoff(photo: Handoff, storage: Storage | null = session()): void {
  try {
    storage?.setItem(KEY, JSON.stringify({ id: photo.id, lat: photo.lat, lon: photo.lon }));
  } catch {
    /* Without storage the reload lands on the start view -- a smaller loss than no reload. */
  }
}

/**
 * Read the note and remove it, so a second reload does not open the same photo again.
 *
 * Anything that is not a complete note counts as none: this reads what an earlier version of the
 * page may have written.
 */
export function readHandoff(storage: Storage | null = session()): Handoff | null {
  try {
    const raw = storage?.getItem(KEY);
    storage?.removeItem(KEY);
    if (!raw) return null;
    const note = JSON.parse(raw) as Partial<Handoff>;
    const complete = [note.id, note.lat, note.lon].every(
      (value) => typeof value === "number" && Number.isFinite(value),
    );
    return complete ? (note as Handoff) : null;
  } catch {
    return null;
  }
}

let taken: Handoff | null | undefined;

/**
 * The note of this page load, read once.
 *
 * Cached because React's StrictMode runs initialisers twice in development: the second call would
 * find the note already removed, and the photo would open in one of the two renders only.
 */
export function takeHandoff(): Handoff | null {
  if (taken === undefined) taken = readHandoff();
  return taken;
}
