import { describe, expect, it } from "vitest";

import {
  formatBytes,
  formatCount,
  formatDate,
  formatDaysSince,
  formatLogTime,
  formatWhen,
} from "./format";

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

describe("Die drei Datumsformen", () => {
  // Ein Zeitpunkt im August: In welcher Zone der Test auch laeuft, das Jahr kippt nicht. Genau
  // darum geht es hier -- geprueft wird, was jede Form **weglaesst**, nicht wie sie in Berlin
  // aussieht. Die Zone benennt seit Punkt 58 das Backend.
  const augusttag = "2026-08-05T12:00:00Z";

  it("laesst in der Sicherungskachel die Uhrzeit weg", () => {
    // Eine Sicherung ist ein Tag, keine Minute.
    expect(formatDate(augusttag)).not.toContain(":");
    expect(formatDate(augusttag)).toContain("2026");
  });

  it("laesst bei den Besucherbeitraegen das Jahr weg", () => {
    // Die Liste zeigt, was in dieser Saison hereingekommen ist -- das Jahr waere Rauschen.
    expect(formatWhen(augusttag)).not.toContain("2026");
    expect(formatWhen(augusttag)).toContain(":");
  });

  it("schreibt im Import-Protokoll den Monat als Zahl", () => {
    // Die Spalte ist schmal und in tabular-nums gesetzt, damit die Zeilen untereinander stehen.
    // Ein ausgeschriebener Monat zerstoert genau das.
    const gesetzt = formatLogTime(augusttag);

    expect(gesetzt).toMatch(/^\d+\.\d+\.\d{4}/);
    expect(gesetzt).toContain("2026");
    expect(gesetzt).toContain(":");
  });

  it("schreibt den Monat aus, wo Platz dafuer ist", () => {
    expect(formatDate(augusttag)).toMatch(/^\d+\. \p{L}+/u);
    expect(formatWhen(augusttag)).toMatch(/^\d+\. \p{L}+/u);
  });
});
