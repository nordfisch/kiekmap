import { describe, expect, it } from "vitest";

import { PAGE_SIZE, clampOffset, pageCount, pageNumber } from "./pagination";

describe("page count", () => {
  it("gives even an empty list one page", () => {
    // "Page 1 of 0" would be information about nothing.
    expect(pageCount(0)).toBe(1);
  });

  it("counts a partly filled page too", () => {
    expect(pageCount(PAGE_SIZE)).toBe(1);
    expect(pageCount(PAGE_SIZE + 1)).toBe(2);
    expect(pageCount(214, 30)).toBe(8);
  });
});

describe("offset", () => {
  it("lands on the last page when it stands beyond the end", () => {
    // The normal case for these lists: whoever locates the last entry of "without a place" ends up
    // beyond the end. Without this clamp an empty page would be left standing.
    expect(clampOffset(90, 45, 30)).toBe(30);
  });

  it("leaves a valid page alone", () => {
    expect(clampOffset(30, 214, 30)).toBe(30);
  });

  it("never falls below zero", () => {
    expect(clampOffset(-10, 214, 30)).toBe(0);
    expect(clampOffset(0, 0, 30)).toBe(0);
  });

  it("counts the pages from one, the way a person does", () => {
    expect(pageNumber(0, 30)).toBe(1);
    expect(pageNumber(30, 30)).toBe(2);
  });
});
