/**
 * The admin session.
 *
 * Three states, and the device is in the first of them almost always:
 *
 *   kiosk  the visitor view -- the corner press is the only way out of it
 *   pin    the number pad is up
 *   admin  signed in
 *
 * The token is kept in sessionStorage as well, so an accidental reload does not demand the PIN
 * again. sessionStorage and not localStorage: it dies with the browser tab, and on the Pi that
 * means it dies at the latest when the kiosk restarts in the morning.
 */

import { create } from "zustand";

import {
  checkSession,
  onAdminActivity,
  onAdminSignedOut,
  setAdminToken,
  signIn as postPin,
  signOut as postSignOut,
} from "../api/admin";

const STORAGE_KEY = "kiekmap.admin.token";

type View = "kiosk" | "pin" | "admin";

type AdminState = {
  view: View;
  busy: boolean;
  error: string | null;
  /** Point in time when the session runs out. Recomputed on every accepted request. */
  expiresAt: number | null;
  /** How long a session lasts, as the backend reported it. Not a number of our own. */
  lifetimeMs: number;

  /**
   * A photo to open in the editor as soon as the PIN goes through, or null for the usual way in.
   *
   * The pencil beside the title in the detail view sets it. Without it the admin area could only
   * be entered at its front door, and finding one particular photo again meant searching for it
   * -- by the very title that is the thing being corrected.
   *
   * Cleared by whoever acts on it (see ``AdminApp``), so that closing the editor does not put the
   * same photo up again, and by every route out of the PIN pad.
   */
  editPhotoId: number | null;

  /** The number pad. With a photo id: after signing in, that photo opens for editing. */
  askPin: (editPhotoId?: number) => void;
  cancelPin: () => void;
  /** Called once the target has been acted on -- otherwise it would fire again on every render. */
  clearTarget: () => void;
  signIn: (pin: string) => Promise<void>;
  /** Deliberately leaving the admin area. Signs out **and reloads** -- see the action. */
  leave: () => Promise<void>;
  /** Session ended by the backend or by the countdown -- no request left to make. */
  dropSession: () => void;
  restore: () => Promise<void>;
};

function remember(token: string | null): void {
  try {
    if (token) sessionStorage.setItem(STORAGE_KEY, token);
    else sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* A browser without storage is no reason not to work -- it just forgets on reload. */
  }
}

function stored(): string | null {
  try {
    return sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export const useAdmin = create<AdminState>((set, get) => ({
  view: "kiosk",
  busy: false,
  error: null,
  expiresAt: null,
  lifetimeMs: 30 * 60 * 1000,
  editPhotoId: null,

  askPin(editPhotoId) {
    set({ view: "pin", error: null, editPhotoId: editPhotoId ?? null });
  },

  cancelPin() {
    set({ view: "kiosk", error: null, editPhotoId: null });
  },

  clearTarget() {
    set({ editPhotoId: null });
  },

  async signIn(pin) {
    set({ busy: true, error: null });
    try {
      const session = await postPin(pin);
      setAdminToken(session.token);
      remember(session.token);
      set({
        view: "admin",
        busy: false,
        error: null,
        expiresAt: Date.now() + session.expires_in_s * 1000,
        lifetimeMs: session.expires_in_s * 1000,
      });
    } catch (e) {
      set({ busy: false, error: e instanceof Error ? e.message : String(e) });
    }
  },

  async leave() {
    try {
      await postSignOut();
    } catch {
      /* Whatever the answer: from here on this browser is out. */
    }
    get().dropSession();

    // Whoever leaves the admin area has usually changed something: imported, dated, located,
    // hidden. The visitor view saw none of it -- it held on to its markers and its histogram the
    // whole time. Without the reload the old collection would be standing there, and the obvious
    // explanation ("it did not work") would be the wrong one.
    window.location.reload();
  },

  /**
   * The session ended without anybody ending it -- time ran out, or the backend refused a token.
   *
   * **Nothing may be reloaded here**, unlike in ``leave``. An expired token out of sessionStorage
   * makes ``restore`` land exactly here at startup via ``onAdminSignedOut`` -- a reload at this
   * point would load the page over and over.
   */
  dropSession() {
    setAdminToken(null);
    remember(null);
    set({ view: "kiosk", expiresAt: null, error: null, editPhotoId: null });
  },

  /** Called once at startup. A token from before only counts if the backend still knows it. */
  async restore() {
    const token = stored();
    if (!token) return;

    setAdminToken(token);
    try {
      const session = await checkSession();
      set({
        view: "admin",
        expiresAt: Date.now() + session.expires_in_s * 1000,
        lifetimeMs: session.expires_in_s * 1000,
      });
    } catch {
      /* Expired or the service restarted. dropSession has already run via onAdminSignedOut. */
    }
  },
}));

// The backend refused the token: back to the kiosk rather than an error message in some list.
onAdminSignedOut(() => useAdmin.getState().dropSession());

// Every accepted request pushed the session back on the server -- follow suit here, otherwise the
// countdown would throw out someone who is working the whole time.
onAdminActivity(() => {
  const { expiresAt, lifetimeMs } = useAdmin.getState();
  if (expiresAt === null) return;
  useAdmin.setState({ expiresAt: Date.now() + lifetimeMs });
});
