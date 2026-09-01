import { describe, expect, it } from "vitest";

import { MINIMUM_DECADES, offeredDecades } from "./decades";

describe("decades on offer", () => {
  it("shows the minimum window when no photo is dated", () => {
    // Otherwise a freshly set up device would have no button at all.
    const decades = offeredDecades(null);

    expect(decades[0]).toBe(MINIMUM_DECADES.first);
    expect(decades.at(-1)).toBe(MINIMUM_DECADES.last);
    expect(decades).toHaveLength(10);
  });

  it("leaves a collection inside the window unchanged", () => {
    // Holm: 1920 to 2019 -- exactly the window.
    expect(offeredDecades({ from: 1923, to: 2019 })).toEqual([
      1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010,
    ]);
  });

  it("does not narrow down for a thin collection", () => {
    // Only the 1950s in the collection -- a visitor still has to be able to say 1920.
    expect(offeredDecades({ from: 1950, to: 1959 })).toHaveLength(10);
  });

  it("extends the range backwards as soon as an older photo is dated", () => {
    expect(offeredDecades({ from: 1893, to: 2019 })[0]).toBe(1890);
  });

  it("extends it forwards just the same", () => {
    expect(offeredDecades({ from: 1920, to: 2024 }).at(-1)).toBe(2020);
  });
});
