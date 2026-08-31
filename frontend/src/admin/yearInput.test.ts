import { describe, expect, it } from "vitest";

import { decadeAllowed, fromPhoto, toDate, withYear } from "./yearInput";

describe("a decade only for whole decades", () => {
  it("allows 1920 and 1930", () => {
    expect(decadeAllowed("1920")).toBe(true);
    expect(decadeAllowed("1930")).toBe(true);
  });

  it("refuses everything in between", () => {
    // The backend would round 1934 down to the 1930s without a word -- the 4 would be gone.
    expect(decadeAllowed("1934")).toBe(false);
    expect(decadeAllowed("1923")).toBe(false);
  });

  it("is not taken in by nonsense", () => {
    expect(decadeAllowed("")).toBe(false);
    expect(decadeAllowed("Kirchweih")).toBe(false);
    expect(decadeAllowed("1920er")).toBe(false);
  });

  it("allows no decade either when there is no year", () => {
    // The interface disables the choice anyway -- this is the belt underneath it.
    expect(decadeAllowed("")).toBe(false);
    expect(toDate({ year: "", precision: "decade" })).toBeNull();
  });
});

describe("a changed year takes the precision back", () => {
  it("falls back to the year as soon as the number no longer fits", () => {
    // Disabling alone is not enough: a set but disabled field still sent "decade" along -- and
    // 1923 would silently become the 1920s.
    const before = { year: "1920", precision: "decade" } as const;

    expect(withYear(before, "1923")).toEqual({ year: "1923", precision: "year" });
  });

  it("leaves the choice standing when it still fits", () => {
    expect(withYear({ year: "1920", precision: "decade" }, "1930")).toEqual({
      year: "1930",
      precision: "decade",
    });
  });

  it("sets nothing of its own accord", () => {
    expect(withYear({ year: "1923", precision: "year" }, "1920")).toEqual({
      year: "1920",
      precision: "year",
    });
  });
});

describe("what goes to the API", () => {
  it("sends nothing without a year", () => {
    expect(toDate({ year: "", precision: "year" })).toBeNull();
  });

  it("sends an exact year", () => {
    expect(toDate({ year: "1932", precision: "year" })).toEqual({
      year: 1932,
      precision: "year",
    });
  });

  it("sends a decade only when it is allowed to be one", () => {
    expect(toDate({ year: "1920", precision: "decade" })).toEqual({
      year: 1920,
      precision: "decade",
    });
    // The belt for the case where the interface does allow both after all.
    expect(toDate({ year: "1923", precision: "decade" })).toEqual({
      year: 1923,
      precision: "year",
    });
  });
});

describe("the precision of a stored photo", () => {
  it("keeps the decade instead of turning it into a year", () => {
    expect(fromPhoto("1920-01-01", "decade")).toEqual({ year: "1920", precision: "decade" });
  });

  it("does not turn a year into a decade", () => {
    expect(fromPhoto("1932-01-01", "year")).toEqual({ year: "1932", precision: "year" });
  });

  it("leaves a whole decade stored as a year a year", () => {
    // 1920 is an allowed decade -- the entry still must not change.
    expect(fromPhoto("1920-01-01", "year")).toEqual({ year: "1920", precision: "year" });
  });

  it("gives an empty field when there is no dating", () => {
    expect(fromPhoto(null, "unknown")).toEqual({ year: "", precision: "year" });
  });
});
