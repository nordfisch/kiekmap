import { describe, expect, it } from "vitest";

import { ENTER_MS, clusterZoom, isStepChange, stillEntering } from "./clusterStep";

describe("the clustering step", () => {
  it("is the rounded zoom level", () => {
    // Exactly the number `draw()` asks supercluster with -- if it differs here, the map
    // animates at a different point from where it regroups.
    expect(clusterZoom(13.4)).toBe(13);
    expect(clusterZoom(13.5)).toBe(14);
  });
});

describe("when the markers fade in", () => {
  it("only changes once the rounded step tips over", () => {
    expect(isStepChange(13, 14)).toBe(true);
  });

  it("stays quiet while panning", () => {
    /**
     * The expensive error. While swiping, `draw()` runs dozens of times at the same step; fading
     * in on each of them would make the map flicker throughout -- noticeably more on the Pi than
     * on the development machine.
     */
    expect(isStepChange(13, 13)).toBe(false);
  });

  it("does not count the first build as a change", () => {
    // The first markers are the map appearing, not a regrouping. Fading them in would delay
    // the very first thing anybody gets to see.
    expect(isStepChange(null, 13)).toBe(false);
  });
});

describe("how long a fade-in lasts", () => {
  it("takes a second build shortly afterwards along with it", () => {
    /**
     * The case the animation first failed on. A regrouping is not *one* draw: right after the
     * zoom the photos of the new viewport are fetched, and when they arrive every marker is built
     * again. Measured, a few dozen milliseconds lay between the two -- and the second build took
     * the fade-in away again, because it was not itself a step change.
     */
    expect(stillEntering(1000, 1000 + ENTER_MS - 1)).toBe(true);
  });

  it("is over after that", () => {
    expect(stillEntering(1000, 1000 + ENTER_MS)).toBe(false);
  });

  it("does not run while nothing has been faded in", () => {
    expect(stillEntering(null, 5000)).toBe(false);
  });
});
