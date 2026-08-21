// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The idle reset.
 *
 * Without it the device stands there each morning in the state the last visitor of the previous
 * evening left it: a photo open over the map, the time slider narrowed to 1932, the "Hilf mit"
 * panel showing a picture somebody had already waved away. The next person has to undo all of
 * that before they can start -- and mostly will not.
 *
 * What counts as "somebody is here" is deliberately narrow: touching, typing, scrolling. Not
 * mouse movement -- a touchscreen has no hover, and a mouse nudged by a passing sleeve would keep
 * the kiosk awake all night.
 */

/** How long the device has to be left alone. Long enough that nobody is interrupted mid-thought. */
export const IDLE_MS = 5 * 60 * 1000;

const ACTIVITY = ["pointerdown", "keydown", "wheel", "touchstart"] as const;

/**
 * Call ``onIdle`` once the target has been quiet for ``idleMs``.
 *
 * Fires **once** per quiet period: after a reset the timer stays down until somebody touches the
 * device again. Otherwise an untouched kiosk would reset itself every five minutes all night,
 * each time with a round of requests to a Pi that has nothing to do.
 *
 * The event target is passed in rather than reaching for ``window`` -- that is what lets this be
 * tested without a browser.
 */
export function watchForIdle(target: EventTarget, idleMs: number, onIdle: () => void): () => void {
  let timer: ReturnType<typeof setTimeout> | null = null;

  function stop() {
    if (timer !== null) clearTimeout(timer);
    timer = null;
  }

  function restart() {
    stop();
    timer = setTimeout(() => {
      timer = null;
      onIdle();
    }, idleMs);
  }

  for (const event of ACTIVITY) {
    target.addEventListener(event, restart, { passive: true });
  }
  restart();

  return () => {
    stop();
    for (const event of ACTIVITY) {
      target.removeEventListener(event, restart);
    }
  };
}
