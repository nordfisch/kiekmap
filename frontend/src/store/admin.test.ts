import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/admin", () => ({
  checkSession: vi.fn(),
  onAdminActivity: vi.fn(),
  onAdminSignedOut: vi.fn(),
  setAdminToken: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

import { useAdmin } from "./admin";

/**
 * The target somebody enters the admin view with.
 *
 * The pencil beside the title in the detail view sets it; the admin view reads it once while
 * building and puts it away at once. If it fails to reset anywhere, the same photo opens on the
 * next entry -- for somebody who only wanted the overview.
 */
describe("the way from a photo into editing it", () => {
  beforeEach(() => {
    useAdmin.setState({ view: "kiosk", editPhotoId: null, error: null, expiresAt: null });
  });

  it("remembers the photo and asks for the PIN", () => {
    useAdmin.getState().askPin(412);

    expect(useAdmin.getState().view).toBe("pin");
    expect(useAdmin.getState().editPhotoId).toBe(412);
  });

  it("stays without a target when the coat of arms was the door", () => {
    // The other way in. Without this distinction everybody would land inside a photo.
    useAdmin.getState().askPin();

    expect(useAdmin.getState().view).toBe("pin");
    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("forgets it on going back to the map", () => {
    useAdmin.getState().askPin(412);
    useAdmin.getState().cancelPin();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("forgets it when the session ends", () => {
    // Otherwise the target would still stand when somebody else comes in via the coat of arms.
    useAdmin.getState().askPin(412);
    useAdmin.getState().dropSession();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("forgets it as soon as the admin view has picked it up", () => {
    /**
     * The case that otherwise becomes a trap: the admin view reads the target while building and
     * opens the photo. If it stayed, closing the edit screen would offer it again at once -- and
     * nobody would get past it to the photo list.
     */
    useAdmin.getState().askPin(412);
    useAdmin.getState().clearTarget();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("lets a second target replace the first", () => {
    useAdmin.getState().askPin(412);
    useAdmin.getState().askPin(7);

    expect(useAdmin.getState().editPhotoId).toBe(7);
  });
});
