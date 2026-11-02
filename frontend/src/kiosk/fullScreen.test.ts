import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import { useKiosk } from "../store/kiosk";

describe("the full-screen photo", () => {
  beforeEach(() => useKiosk.setState({ openStack: [], openIndex: 0, fullScreen: false }));

  it("leads back to the detail view of the same photo, not to the map", () => {
    useKiosk.getState().openStackAt([11, 12, 13], 1);
    useKiosk.getState().setFullScreen(true);

    useKiosk.getState().setFullScreen(false);

    expect(useKiosk.getState().fullScreen).toBe(false);
    expect(useKiosk.getState().openStack).toEqual([11, 12, 13]);
    expect(useKiosk.getState().openIndex).toBe(1);
  });

  it("does not let the stack page on underneath it", () => {
    // The photo would change while the visitor looks at it, with no pager in sight.
    useKiosk.getState().openStackAt([11, 12, 13], 0);
    useKiosk.getState().setFullScreen(true);

    useKiosk.getState().advanceStack();

    expect(useKiosk.getState().openIndex).toBe(0);
  });

  it("lets the stack page on again once it is closed", () => {
    useKiosk.getState().openStackAt([11, 12, 13], 0);
    useKiosk.getState().setFullScreen(true);
    useKiosk.getState().setFullScreen(false);

    useKiosk.getState().advanceStack();

    expect(useKiosk.getState().openIndex).toBe(1);
  });

  it("does not open the next photo full screen after the detail view was closed", () => {
    useKiosk.getState().openPhoto(7);
    useKiosk.getState().setFullScreen(true);
    useKiosk.getState().openPhoto(null);

    useKiosk.getState().openPhoto(8);

    expect(useKiosk.getState().fullScreen).toBe(false);
  });

  it("does not carry over into a stack opened from the map", () => {
    useKiosk.getState().openPhoto(7);
    useKiosk.getState().setFullScreen(true);

    useKiosk.getState().openStackAt([11, 12]);

    expect(useKiosk.getState().fullScreen).toBe(false);
  });

  it("does not wait for a photo while none is open", () => {
    // A flag set with nothing open would wait and open the next photo straight into full screen.
    useKiosk.getState().setFullScreen(true);

    expect(useKiosk.getState().fullScreen).toBe(false);
  });
});
