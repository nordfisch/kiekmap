import { describe, expect, it } from "vitest";

import { PAGE_SIZE, clampOffset, pageCount, pageNumber } from "./paging";

describe("Seitenzahl", () => {
  it("gibt auch einer leeren Liste eine Seite", () => {
    // "Seite 1 von 0" waere eine Auskunft ueber nichts.
    expect(pageCount(0)).toBe(1);
  });

  it("rechnet angefangene Seiten mit", () => {
    expect(pageCount(PAGE_SIZE)).toBe(1);
    expect(pageCount(PAGE_SIZE + 1)).toBe(2);
    expect(pageCount(214, 30)).toBe(8);
  });
});

describe("Versatz", () => {
  it("landet auf der letzten Seite, wenn er hinter dem Ende steht", () => {
    // Der Normalfall dieser Listen: wer den letzten Eintrag von "Ohne Ort" verortet, steht danach
    // hinter dem Ende. Ohne diese Klammer bliebe eine leere Seite stehen.
    expect(clampOffset(90, 45, 30)).toBe(30);
  });

  it("laesst eine gueltige Seite in Ruhe", () => {
    expect(clampOffset(30, 214, 30)).toBe(30);
  });

  it("faellt nie unter null", () => {
    expect(clampOffset(-10, 214, 30)).toBe(0);
    expect(clampOffset(0, 0, 30)).toBe(0);
  });

  it("zaehlt die Seiten von eins an, wie ein Mensch", () => {
    expect(pageNumber(0, 30)).toBe(1);
    expect(pageNumber(30, 30)).toBe(2);
  });
});
