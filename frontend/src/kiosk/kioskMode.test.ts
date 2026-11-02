import { describe, expect, it } from "vitest";

import { isKiosk } from "./kioskMode";

describe("isKiosk", () => {
  it("is set by the marker the kiosk service opens the page with", () => {
    expect(isKiosk("?kiosk")).toBe(true);
  });

  it("holds beside other parameters", () => {
    expect(isKiosk("?lang=de&kiosk")).toBe(true);
  });

  it("is not set on a development machine or online, where the page opens without a query", () => {
    expect(isKiosk("")).toBe(false);
  });

  it("does not take a parameter that only begins with the word", () => {
    expect(isKiosk("?kioskmode=1")).toBe(false);
  });
});
