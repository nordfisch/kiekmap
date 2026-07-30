import { describe, expect, it } from "vitest";

import { formatBytes, formatCount, formatDaysSince } from "./format";

describe("Groessenangaben", () => {
  it("rechnet in Tausenderschritten, wie es auf der Packung steht", () => {
    // Ein als "32 GB" verkaufter Stick soll auch als 32 GB dastehen, nicht als 29,8.
    expect(formatBytes(32_000_000_000)).toBe("32 GB");
    expect(formatBytes(1_500_000)).toBe("1,5 MB");
    expect(formatBytes(2_400)).toBe("2,4 kB");
  });

  it("schreibt Kleines ohne Einheitenakrobatik aus", () => {
    expect(formatBytes(0)).toBe("0 Bytes");
    expect(formatBytes(999)).toBe("999 Bytes");
  });

  it("setzt im Deutschen Komma und Punkt richtig", () => {
    expect(formatCount(2150)).toBe("2.150");
    expect(formatBytes(28_400_000_000)).toBe("28,4 GB");
  });
});

describe("Tage seit dem letzten Mal", () => {
  it("schreibt Heute statt null Tagen", () => {
    // "0 Tage seit der letzten Sicherung" ist eine Denksportaufgabe, "Heute gesichert" nicht.
    expect(formatDaysSince(0)).toBe("Heute");
  });

  it("schreibt Noch nie, wenn es das Ereignis nie gab", () => {
    expect(formatDaysSince(null)).toBe("Noch nie");
  });

  it("zaehlt sonst die Tage", () => {
    expect(formatDaysSince(1)).toBe("1");
    expect(formatDaysSince(34)).toBe("34");
  });
});
