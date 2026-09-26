import { describe, expect, it } from "vitest";

import { cornerTags } from "./keywords";

describe("cornerTags", () => {
  const offered = ["Gasthof", "Hof", "Laden"];

  it("adds a keyword chosen from the detail view behind the configured ones", () => {
    // Otherwise the map would be filtered by a keyword that no button names or switches off.
    expect(cornerTags(offered, "Winter")).toEqual(["Gasthof", "Hof", "Laden", "Winter"]);
  });

  it("does not add a configured keyword a second time", () => {
    expect(cornerTags(offered, "Hof")).toEqual(offered);
  });

  it("drops the added keyword once nothing is chosen", () => {
    expect(cornerTags(offered, null)).toEqual(offered);
  });

  it("shows a chosen keyword even when nothing is configured", () => {
    // The way in from the detail view works without a configured list.
    expect(cornerTags([], "Winter")).toEqual(["Winter"]);
    expect(cornerTags([], null)).toEqual([]);
  });
});
