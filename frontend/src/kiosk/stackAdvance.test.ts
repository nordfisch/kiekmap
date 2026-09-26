import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import { useKiosk } from "../store/kiosk";
import { nextInStack } from "./stackAdvance";

describe("the next photo of a stack", () => {
  it("starts again after the last instead of stopping on it", () => {
    // Whoever walks up in the middle of a stack would otherwise never see its beginning.
    expect(nextInStack(4, 5)).toBe(0);
  });

  it("goes on one at a time before that", () => {
    expect(nextInStack(0, 5)).toBe(1);
    expect(nextInStack(3, 5)).toBe(4);
  });

  it("does not move a single photo", () => {
    expect(nextInStack(0, 1)).toBe(0);
    expect(nextInStack(0, 0)).toBe(0);
  });
});

describe("a stack paging by itself", () => {
  beforeEach(() => useKiosk.setState({ openStack: [], openIndex: 0 }));

  it("starts again after the last photo", () => {
    useKiosk.getState().openStackAt([11, 12, 13], 2);

    useKiosk.getState().advanceStack();

    expect(useKiosk.getState().openIndex).toBe(0);
  });

  it("does not take the stop at either end away from the buttons", () => {
    // The buttons disable themselves at the ends because stepInStack stops there. A wrap in
    // stepInStack would leave "Weiter" active on the last photo and jump to the first.
    useKiosk.getState().openStackAt([11, 12, 13], 2);

    useKiosk.getState().stepInStack(1);
    expect(useKiosk.getState().openIndex).toBe(2);

    useKiosk.getState().stepInStack(-3);
    expect(useKiosk.getState().openIndex).toBe(2);
  });

  it("leaves a single photo alone", () => {
    useKiosk.getState().openPhoto(7);

    useKiosk.getState().advanceStack();

    expect(useKiosk.getState().openStack).toEqual([7]);
    expect(useKiosk.getState().openIndex).toBe(0);
  });
});
