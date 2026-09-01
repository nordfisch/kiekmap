import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { buildIndex } from "./PhotoLayer";

let id = 0;
function photo(lat: number, lon: number): PhotoMarker {
  return {
    id: ++id,
    title: `Photo ${id}`,
    date_label: "1932",
    thumb_url: "/thumb",
    lat,
    lon,
    width: 100,
    height: 80,
  } as PhotoMarker;
}

describe("what stands on a circle", () => {
  it("counts the photos, not the spots", () => {
    // A stack of eight and two single images beside it: the circle above has to carry 10, not 3.
    // To supercluster a stack is a single point -- see stacks.ts.
    const stack = Array.from({ length: 8 }, () => photo(53.619588, 9.6747118));
    const index = buildIndex([...stack, photo(53.6192, 9.6684), photo(53.6193, 9.6685)]);

    const groups = index.getClusters([9.6, 53.57, 9.75, 53.67], 12);
    const circle = groups.find((g) => "cluster" in g.properties && g.properties.cluster);

    expect(circle, "at zoom 12 the three spots lie close enough together").toBeDefined();
    expect((circle!.properties as { photos: number }).photos).toBe(10);
  });

  it("leaves photos far apart as single ones", () => {
    const index = buildIndex([photo(53.58, 9.61), photo(53.66, 9.74)]);

    const groups = index.getClusters([9.5, 53.5, 9.9, 53.8], 14);

    expect(groups).toHaveLength(2);
    expect(groups.every((g) => !("cluster" in g.properties))).toBe(true);
  });
});
