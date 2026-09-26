import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/admin", () => ({
  checkSession: vi.fn(),
  onAdminActivity: vi.fn(),
  onAdminSignedOut: vi.fn(),
  requestShutdown: vi.fn(),
  setAdminToken: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

import { requestShutdown, setAdminToken } from "../api/admin";
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

/**
 * Switching the device off.
 *
 * The screen that says the power may be switched off is a promise, and the device is the only one
 * who can keep it: the backend refuses where nothing on the host acts on the request, and while a
 * backup or an import is running. So only a successful answer may change the view.
 */
describe("switching the device off", () => {
  beforeEach(() => {
    vi.mocked(requestShutdown).mockReset();
    vi.mocked(setAdminToken).mockReset();
    useAdmin.setState({ view: "admin", busy: false, error: null, expiresAt: Date.now() + 1000 });
  });

  it("shows the last screen once the device has taken the request", async () => {
    vi.mocked(requestShutdown).mockResolvedValue(undefined);

    await useAdmin.getState().switchOff();

    expect(useAdmin.getState().view).toBe("off");
    expect(useAdmin.getState().busy).toBe(false);
    expect(useAdmin.getState().expiresAt).toBeNull();
    expect(vi.mocked(setAdminToken)).toHaveBeenCalledWith(null);
  });

  it("stays in the admin area when the device refuses to switch off", async () => {
    // A development machine, the online instance, or a running backup. Announcing that the power
    // may go while the device runs on would be the one unrecoverable mistake here.
    vi.mocked(requestShutdown).mockRejectedValue(new Error("Dieses System kann sich nicht ..."));

    await useAdmin.getState().switchOff();

    expect(useAdmin.getState().view).toBe("admin");
    expect(useAdmin.getState().error).toBe("Dieses System kann sich nicht ...");
    expect(useAdmin.getState().busy).toBe(false);
    expect(vi.mocked(setAdminToken)).not.toHaveBeenCalledWith(null);
  });

  it("does not drop the token before the device has answered", async () => {
    // Dropped first, a request still in flight answers 401, and the view would go back to the
    // kiosk instead of to the last screen.
    let answer: () => void = () => {};
    vi.mocked(requestShutdown).mockReturnValue(
      new Promise<void>((resolve) => {
        answer = resolve;
      }),
    );

    const pending = useAdmin.getState().switchOff();
    expect(vi.mocked(setAdminToken)).not.toHaveBeenCalledWith(null);
    expect(useAdmin.getState().busy).toBe(true);

    answer();
    await pending;

    expect(vi.mocked(setAdminToken)).toHaveBeenCalledWith(null);
  });
});
