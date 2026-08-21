// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Recovering from a crash of the interface.
 *
 * A render error tears the whole tree down, and what stays is a white screen. On a device with no
 * keyboard, no address bar and no reload button that is the end of the exhibit until somebody
 * pulls the plug -- and the idle reload that heals every other stuck state cannot help, because it
 * lives inside the map and goes down with it.
 *
 * So the page reloads itself. The only question this module answers is **whether it may**: a crash
 * that comes back the moment the page is up again would otherwise leave the screen flashing, which
 * is worse than a message somebody can read. After one automatic attempt the device therefore says
 * what happened and waits for a finger.
 */

/** Where the last automatic reload is noted. */
const STORAGE_KEY = "kiekmap-neustart";

/** How long the message stands before the page reloads itself. Long enough to be read. */
export const RELOAD_DELAY_MS = 8000;

/**
 * Within this span a second crash counts as the same one -- and is not reloaded away again.
 *
 * Generous on purpose: a crash that only shows up after a minute of use is a different one than
 * the crash that greets the page on load.
 */
export const RELOAD_COOLDOWN_MS = 120_000;

/**
 * May the page heal itself, or has it just tried?
 *
 * **A difference below zero counts as "yes"**, and that is not a formality here: the Pi has no
 * real-time clock and no network, so after a power cut its wall clock can jump backwards by years
 * (the same reason the admin sessions count down instead of holding a point in time -- see
 * ``services/auth.py``). Read the other way round, a clock jump would switch the self-healing off
 * for good, which is exactly the state this whole module exists to prevent.
 */
export function mayReload(
  lastAt: number | null,
  now: number,
  cooldownMs: number = RELOAD_COOLDOWN_MS,
): boolean {
  if (lastAt === null) return true;
  const elapsed = now - lastAt;
  return elapsed < 0 || elapsed > cooldownMs;
}

/**
 * When the page last reloaded itself, or null.
 *
 * ``sessionStorage`` and not ``localStorage``: it survives a reload of this tab and dies with the
 * tab -- so on the Pi the count starts fresh every morning, the same reasoning as for the admin
 * token. A storage that cannot be read is not an error worth reporting to anybody standing in
 * front of the screen; it only means the device gets its one attempt again.
 */
export function lastRecovery(store: Pick<Storage, "getItem">): number | null {
  try {
    const raw = store.getItem(STORAGE_KEY);
    if (raw === null) return null;
    const stamp = Number(raw);
    return Number.isFinite(stamp) ? stamp : null;
  } catch {
    return null;
  }
}

export function noteRecovery(store: Pick<Storage, "setItem">, now: number): void {
  try {
    store.setItem(STORAGE_KEY, String(now));
  } catch {
    /* see lastRecovery */
  }
}
