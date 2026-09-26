import { describe, expect, it } from "vitest";

import { BAND_MARGIN, MAX_ZOOM, bandTravel, kenBurnsPath, nextTile, zoomLimit } from "./attract";

describe("nextTile", () => {
  it("turns every tile once per round", () => {
    const round = [0, 1, 2, 3].map(nextTile);
    expect([...round].sort()).toEqual([0, 1, 2, 3]);
    expect([4, 5, 6, 7].map(nextTile)).toEqual(round);
  });

  it("never turns the same tile twice in a row, not even across rounds", () => {
    // A tile turning twice would cut a photo off five seconds after it appeared.
    for (let step = 0; step < 12; step++) {
      expect(nextTile(step + 1)).not.toBe(nextTile(step));
    }
  });

  it("does not run in reading order", () => {
    // Reading order is a sweep across the wall, and a sweep is a pattern people watch instead of
    // the photos.
    expect([0, 1, 2, 3].map(nextTile)).not.toEqual([0, 1, 2, 3]);
  });
});

describe("zoomLimit", () => {
  const tile = { width: 960, height: 540 };

  it("gives a large photo the full zoom", () => {
    expect(zoomLimit({ width: 4000, height: 2667 }, tile)).toBe(MAX_ZOOM);
  });

  it("never zooms a photo beyond its own pixels", () => {
    // 1024 px across a 960 px tile leaves room for 1.07, not for 1.25. More would turn it soft.
    const zoom = zoomLimit({ width: 1024, height: 683 }, tile);
    expect(zoom).toBeCloseTo(1024 / 960, 5);
  });

  it("does not zoom a photo that barely covers the tile", () => {
    expect(zoomLimit({ width: 800, height: 533 }, tile)).toBe(1);
  });

  it("counts the thumbnail, not the original", () => {
    // The show loads the 1200 px thumbnail. A 6000 px scan does not help a tile twice as wide.
    expect(zoomLimit({ width: 6000, height: 4000 }, { width: 1920, height: 1080 })).toBe(1);
  });
});

describe("kenBurnsPath", () => {
  function sequence(...values: number[]) {
    let index = 0;
    return () => values[index++ % values.length]!;
  }

  const room = ((1.25 - 1) / (2 * 1.25)) * 100;
  const kinds = { in: 0, out: 0.4, across: 0.9 };

  it("never drifts beyond the room the zoom frees", () => {
    // Even at the extreme draw the edge of the image stays outside the tile.
    for (const kind of Object.values(kinds)) {
      for (const side of [0, 0.999]) {
        for (const frame of kenBurnsPath(1.25, sequence(kind, side, side))) {
          const limit = ((frame.scale - 1) / (2 * frame.scale)) * 100;
          expect(Math.abs(frame.x)).toBeLessThanOrEqual(limit + 1e-9);
          expect(Math.abs(frame.y)).toBeLessThanOrEqual(limit + 1e-9);
        }
      }
    }
  });

  it("always reaches the edge of the room", () => {
    // A path to a point near the middle is the motion nobody sees. Every kind goes to the edge.
    for (const kind of Object.values(kinds)) {
      const frames = kenBurnsPath(1.25, sequence(kind, 0.1, 0.9));
      expect(Math.max(...frames.map((frame) => Math.abs(frame.x)))).toBeCloseTo(room, 9);
    }
  });

  it("goes into a corner, out of one, or across", () => {
    const [inFrom, inTo] = kenBurnsPath(1.25, sequence(kinds.in, 0.1, 0.1));
    expect([inFrom.scale, inTo.scale]).toEqual([1, 1.25]);

    const [outFrom, outTo] = kenBurnsPath(1.25, sequence(kinds.out, 0.1, 0.1));
    expect([outFrom.scale, outTo.scale]).toEqual([1.25, 1]);

    const [acrossFrom, acrossTo] = kenBurnsPath(1.25, sequence(kinds.across, 0.1, 0.1));
    expect([acrossFrom.scale, acrossTo.scale]).toEqual([1.25, 1.25]);
    expect(acrossFrom.x).toBeCloseTo(-acrossTo.x, 9);
  });

  it("stands still without a zoom", () => {
    for (const kind of Object.values(kinds)) {
      for (const frame of kenBurnsPath(1, sequence(kind, 0.9, 0.1))) {
        expect(frame).toEqual({ scale: 1, x: 0, y: 0 });
      }
    }
  });
});

describe("bandTravel", () => {
  it("keeps the band whole on the screen at the far end of its path", () => {
    const stage = { width: 1920, height: 1080 };
    const band = { width: 520, height: 52 };
    const travel = bandTravel(stage, band);

    expect(BAND_MARGIN + travel.x + band.width).toBe(stage.width - BAND_MARGIN);
    expect(BAND_MARGIN + travel.y + band.height).toBe(stage.height - BAND_MARGIN);
  });

  it("does not move a band wider than the screen out of it", () => {
    expect(bandTravel({ width: 400, height: 300 }, { width: 520, height: 52 }).x).toBe(0);
  });
});
