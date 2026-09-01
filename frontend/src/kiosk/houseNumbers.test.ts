import { describe, expect, it } from "vitest";

import type { Place } from "../api/client";
import { baseNumber, blocksOf, groupByBase } from "./houseNumbers";

let id = 0;
function address(housenumber: string): Place {
  return {
    id: ++id,
    name: `Mühlenweg ${housenumber}`,
    kind: "adresse",
    lat: 53.62,
    lon: 9.676,
    street: "Mühlenweg",
    housenumber,
    accuracy_m: 15,
  } as Place;
}

describe("the base number", () => {
  it("reads the leading number", () => {
    expect(baseNumber("3")).toBe(3);
    expect(baseNumber("3c")).toBe(3);
    expect(baseNumber("10-18")).toBe(10);
  });

  it("is not taken in by nonsense", () => {
    expect(baseNumber("")).toBeNull();
    expect(baseNumber("ohne Nummer")).toBeNull();
  });
});

describe("grouping letter suffixes", () => {
  it("turns a terrace of houses into one button", () => {
    // 3a to 3z on the Muehlenweg: spatially that is one point, in the list it was 27.
    const list = groupByBase([
      address("3"),
      address("3a"),
      address("3b"),
      address("3c"),
      address("5"),
    ]);

    expect(list.map((p) => p.housenumber)).toEqual(["3", "5"]);
  });

  it("takes the first entry when the bare number does not exist", () => {
    // Otherwise an address that does not exist would stand on the button.
    const list = groupByBase([address("3a"), address("3b")]);

    expect(list.map((p) => p.housenumber)).toEqual(["3a"]);
  });

  it("sorts by the number, not alphabetically", () => {
    const list = groupByBase([address("10"), address("9"), address("1")]);

    expect(list.map((p) => p.housenumber)).toEqual(["1", "9", "10"]);
  });
});

describe("blocks", () => {
  const many = Array.from({ length: 39 }, (_, i) => address(String(i * 2 + 1)));

  it("leaves short streets in one step", () => {
    // Holm's average street has fifteen addresses -- no second step should arise there.
    const blocks = blocksOf(many.slice(0, 12));

    expect(blocks).toHaveLength(1);
    expect(blocks[0]!.numbers).toHaveLength(12);
  });

  it("splits long streets into roughly equal blocks", () => {
    const blocks = blocksOf(many);

    expect(blocks.length).toBeLessThanOrEqual(12);
    for (const block of blocks) expect(block.numbers.length).toBeLessThanOrEqual(12);
    // No number is lost and none appears twice.
    expect(blocks.flatMap((b) => b.numbers)).toHaveLength(many.length);
  });

  it("labels the blocks with the numbers that really lie in them", () => {
    // After the gap on the Muehlenweg the last block is simply called "47-183" -- that is more
    // honest than a round "40-49" with nothing in it.
    const blocks = blocksOf([...many.slice(0, 20), address("169"), address("183")]);

    expect(blocks[0]!.label).toMatch(/^1–/);
    expect(blocks.at(-1)!.label).toMatch(/–183$/);
  });
});
