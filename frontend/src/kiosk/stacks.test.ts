import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { groupByLocation } from "./stacks";

function marker(id: number, lat: number, lon: number): PhotoMarker {
  return {
    id,
    title: `Photo ${id}`,
    date_label: "1932",
    thumb_url: `/api/photos/${id}/thumb`,
    lat,
    lon,
    width: 100,
    height: 80,
  } as PhotoMarker;
}

describe("photos at the same spot", () => {
  it("turns identical coordinates into one marker", () => {
    // The case of the inn: eight photos, exactly the same point. Without grouping they lie on
    // top of one another, and only the topmost can be tapped.
    const stacks = groupByLocation([
      marker(1, 53.619588, 9.6747118),
      marker(2, 53.619588, 9.6747118),
      marker(3, 53.619588, 9.6747118),
    ]);

    expect(stacks).toHaveLength(1);
    expect(stacks[0]!.photos.map((p) => p.id)).toEqual([1, 2, 3]);
  });

  it("leaves a metre away as a marker of its own", () => {
    // Points set by hand never lie exactly on top of each other -- then it is a different spot.
    const stacks = groupByLocation([
      marker(1, 53.619588, 9.6747118),
      marker(2, 53.61962, 9.6747118),
    ]);

    expect(stacks).toHaveLength(2);
  });

  it("keeps the order of the list", () => {
    // Otherwise the most recently edited photo would not be on top -- the query sorts by that.
    const stacks = groupByLocation([
      marker(7, 53.62, 9.68),
      marker(3, 53.62, 9.68),
      marker(9, 53.63, 9.68),
    ]);

    expect(stacks[0]!.photos.map((p) => p.id)).toEqual([7, 3]);
    expect(stacks[1]!.photos.map((p) => p.id)).toEqual([9]);
  });

  it("copes with an empty list", () => {
    expect(groupByLocation([])).toEqual([]);
  });
});
