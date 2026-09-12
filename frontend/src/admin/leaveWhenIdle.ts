/**
 * Leave the admin area when nobody has touched it for two minutes.
 *
 * The admin area stands on the same screen visitors walk up to. Left open after a volunteer walks
 * away, it offers the next visitor the photo editor and the backup, with no PIN in between.
 *
 * **A running job does not count as idle.** A backup, a restore or an import from a stick takes
 * minutes with nobody touching the screen, and leaving means reloading in the middle of it. The two
 * minutes therefore start when the job ends, not at the last touch. The same holds for an upload
 * the browser is still sending.
 */

import { ACTIVITY } from "../kiosk/idle";

export const ADMIN_IDLE_MS = 2 * 60 * 1000;

/** How often the watcher asks whether a job is running. */
export const JOB_POLL_MS = 5_000;

/** Whether the quiet time is up. Busy time never counts. */
export function shouldLeave(now: number, lastActivity: number, busy: boolean): boolean {
  return !busy && now - lastActivity >= ADMIN_IDLE_MS;
}

/**
 * Call `onIdle` once the admin area has been quiet for two minutes outside of any job.
 *
 * `isBusy` is asked on every poll; while it says yes, the quiet time starts again. `now` and the
 * event target are passed in so that the watcher can be tested with fake timers and no browser.
 */
export function watchAdminIdle(
  target: EventTarget,
  isBusy: () => Promise<boolean>,
  onIdle: () => void,
  now: () => number = Date.now,
): () => void {
  let lastActivity = now();
  let stopped = false;

  const touch = () => {
    lastActivity = now();
  };
  for (const event of ACTIVITY) target.addEventListener(event, touch, { passive: true });

  const timer = setInterval(() => {
    void isBusy()
      .catch(() => false)
      .then((busy) => {
        if (stopped) return;
        if (busy) lastActivity = now();
        if (!shouldLeave(now(), lastActivity, busy)) return;
        stop();
        onIdle();
      });
  }, JOB_POLL_MS);

  function stop() {
    stopped = true;
    clearInterval(timer);
    for (const event of ACTIVITY) target.removeEventListener(event, touch);
  }

  return stop;
}
