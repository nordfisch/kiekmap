/**
 * When the grouping of the map markers actually changes.
 *
 * The zoom runs continuously while a finger drags, but supercluster is asked at a **whole** level
 * (`Math.round`). So the markers stand still through most of a gesture and then all jump at once,
 * on the one frame where the rounded level tips over. That jump is what gets animated -- and it
 * has to be told apart from the dozens of redraws in between, where an animation would make the
 * map twitch continuously. On a Pi that is not only ugly but expensive.
 *
 * Its own module without a DOM, so the decision can be checked without a map.
 */

/** The level supercluster is asked at -- see `draw()` in `PhotoLayer.tsx`. */
export function clusterZoom(zoom: number): number {
  return Math.round(zoom);
}

/**
 * Did the grouping tip over between these two draws?
 *
 * ``previous`` is null before the first draw. **That is not a change**: the first markers are the
 * map appearing, not a regrouping, and fading them in would delay the first thing anybody sees.
 */
export function isStepChange(previous: number | null, next: number): boolean {
  return previous !== null && previous !== next;
}

/** How long a regrouping takes to fade in. **Must match `marker-enter` in `global.css`.** */
export const ENTER_MS = 180;

/**
 * Is a marker built right now still part of the entrance that began at ``since``?
 *
 * One regrouping is not one draw. The photos of the new viewport are fetched right after the
 * camera stops, and when they arrive every marker is rebuilt -- measured on 10 August 2026, that
 * second draw followed the first within a few dozen milliseconds and took the fade with it,
 * because it was no step change of its own. Whoever is built while the entrance is still running
 * therefore joins it.
 */
export function stillEntering(since: number | null, now: number): boolean {
  return since !== null && now - since < ENTER_MS;
}
