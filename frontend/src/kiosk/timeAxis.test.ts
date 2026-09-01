import { describe, expect, it } from "vitest";

import {
  axisBounds,
  barHeight,
  clampRange,
  fraction,
  minSpan,
  resizeRange,
  shiftRange,
  yearAtFraction,
} from "./timeAxis";

describe("the axis", () => {
  it("rounds up to whole decades", () => {
    expect(axisBounds({ from: 1923, to: 2019 }, 10)).toEqual({ min: 1920, max: 2020 });
  });

  it("rounds to the year with year bars", () => {
    // No empty tail up to 2030 any more, in which nothing will ever lie -- but a year of room
    // for the 2024 bar itself.
    expect(axisBounds({ from: 2010, to: 2024 }, 1)).toEqual({ min: 2010, max: 2025 });
  });

  it("gives the last bar a lane of its own", () => {
    /**
     * Otherwise it starts exactly at the right edge and runs beyond it. With decades that is
     * rarely noticed -- only when the most recent photo lies in the last decade of the axis. That
     * is exactly the case in the Holm collection.
     */
    expect(axisBounds({ from: 1920, to: 2020 }, 10)).toEqual({ min: 1920, max: 2030 });
  });

  it("gives a collection from a single year a length all the same", () => {
    // Otherwise max === min, and every calculation on it a division by zero.
    expect(axisBounds({ from: 1950, to: 1950 }, 10)).toEqual({ min: 1950, max: 1960 });
    expect(axisBounds({ from: 1950, to: 1950 }, 1)).toEqual({ min: 1950, max: 1951 });
  });

  it("stays empty while no photo is dated", () => {
    expect(axisBounds(null, 1)).toBeNull();
  });
});

describe("bar height", () => {
  it("makes a few photos visible beside many", () => {
    /**
     * The case from the Holm collection: 11 photos in the 2020s against 245 in the 2010s. Linear
     * that would be 4.5 % -- and thereby the same stub an empty decade would get.
     */
    const small = barHeight(11, 245);

    expect(small).toBeGreaterThan(15);
    expect(small).toBeLessThan(barHeight(245, 245));
  });

  it("lets the tallest bar fill the full height", () => {
    expect(barHeight(245, 245)).toBe(100);
  });

  it("keeps a single photo above the base", () => {
    expect(barHeight(1, 245)).toBeGreaterThanOrEqual(8);
  });

  it("leaves an empty bar empty", () => {
    // Nothing is not few. A base where no photo lies would send the visitor there.
    expect(barHeight(0, 245)).toBe(0);
  });
});

describe("shifting the whole range", () => {
  const axis = { min: 1900, max: 2000 };

  it("shifts both ends equally far", () => {
    expect(shiftRange({ from: 1950, to: 1960 }, 5, axis)).toEqual({ from: 1955, to: 1965 });
  });

  it("keeps the span at the start of the axis", () => {
    /**
     * The error at issue: clamping each end separately shrinks the range when it hits the edge --
     * the visitor pushes sideways and watches their range narrow through no fault of their own.
     */
    const shifted = shiftRange({ from: 1905, to: 1925 }, -50, axis);

    expect(shifted).toEqual({ from: 1900, to: 1920 });
    expect(shifted.to - shifted.from).toBe(20);
  });

  it("keeps the span at the end of the axis", () => {
    const shifted = shiftRange({ from: 1975, to: 1995 }, 50, axis);

    expect(shifted).toEqual({ from: 1980, to: 2000 });
    expect(shifted.to - shifted.from).toBe(20);
  });

  it("leaves a shift of zero alone", () => {
    expect(shiftRange({ from: 1950, to: 1960 }, 0, axis)).toEqual({ from: 1950, to: 1960 });
  });
});

describe("a selection outside the axis stays in view", () => {
  const axis = { min: 1950, max: 1960 };

  it("clamps the fraction to zero and one", () => {
    // Exactly the case that ran the selection bar across the title with left: -300%.
    expect(fraction(1920, axis)).toBe(0);
    expect(fraction(2019, axis)).toBe(1);
  });

  it("calculates precisely in between", () => {
    expect(fraction(1955, axis)).toBe(0.5);
  });

  it("pulls the state into the axis too", () => {
    expect(clampRange({ from: 1920, to: 2019 }, axis)).toEqual({ from: 1950, to: 1960 });
  });

  it("leaves a valid selection alone", () => {
    expect(clampRange({ from: 1952, to: 1958 }, axis)).toEqual({ from: 1952, to: 1958 });
  });

  it("turns a selection lying the wrong way round the right way", () => {
    expect(clampRange({ from: 1958, to: 1952 }, axis)).toEqual({ from: 1952, to: 1958 });
  });
});

describe("the minimum width of the range", () => {
  /**
   * The selected range is at the same time the surface by which it is dragged across the axis.
   * Squeezed onto one bar, nothing would be left to grab -- there used to be a drawn handle in the
   * middle for that. A floor under the width answers the same case without a mark on the screen.
   */

  it("keeps the start no closer than a decade to the end", () => {
    // Dragged to 1955, 1946 remains: ten years including both ends.
    expect(resizeRange({ from: 1920, to: 1955 }, "start", 1990, 1)).toEqual({
      from: 1946,
      to: 1955,
    });
  });

  it("keeps the end no closer to the start", () => {
    expect(resizeRange({ from: 1920, to: 1990 }, "end", 1922, 1)).toEqual({
      from: 1920,
      to: 1929,
    });
  });

  it("leaves the range alone otherwise", () => {
    expect(resizeRange({ from: 1920, to: 1990 }, "start", 1950, 1)).toEqual({
      from: 1950,
      to: 1990,
    });
  });

  it("never pushes the other end along", () => {
    /**
     * The silent error if it were otherwise: dragging the start to the right and pushing the end
     * past the end of the axis would wedge it there -- and the range would come back narrower than
     * it went in. Exactly the kind of shrinking ``shiftRange`` already had to prevent.
     */
    const narrow = resizeRange({ from: 1920, to: 1929 }, "start", 1990, 1);

    expect(narrow.to).toBe(1929);
  });

  it("gives way to a bar wider than a decade", () => {
    // With 25-year bundles a floor of ten years would be narrower than a single bar.
    expect(minSpan(25)).toBe(25);
    expect(minSpan(1)).toBe(10);
    expect(minSpan(10)).toBe(10);
  });
});

describe("which year lies under the finger", () => {
  const axis = { min: 1880, max: 2030 };

  it("hits the ends exactly", () => {
    expect(yearAtFraction(0, axis)).toBe(1880);
    expect(yearAtFraction(1, axis)).toBe(2030);
  });

  it("holds at the end when the finger leaves the track", () => {
    // On a touchscreen one constantly slides past the edge. Without the clamp the selection
    // would run out of the axis -- and the track would show a range that does not exist.
    expect(yearAtFraction(-0.4, axis)).toBe(1880);
    expect(yearAtFraction(2.5, axis)).toBe(2030);
  });

  it("is the inverse of fraction -- for every year of the axis", () => {
    // The counter-check the arithmetic was pulled out of the slider for in the first place: a
    // rounding error picks 1931 where the visitor aimed at 1932, and nothing on the screen looks
    // wrong. Only the map shows something else.
    for (let year = axis.min; year <= axis.max; year++) {
      expect(yearAtFraction(fraction(year, axis), axis), `year ${year}`).toBe(year);
    }
  });

  it("copes with an axis of a single step", () => {
    const narrow = { min: 1930, max: 1940 };

    expect(yearAtFraction(0.5, narrow)).toBe(1935);
  });
});
