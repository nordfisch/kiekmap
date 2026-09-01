import { describe, expect, it } from "vitest";

import {
  formatBytes,
  formatCount,
  formatDate,
  formatDaysSince,
  formatLogTime,
  formatWhen,
} from "./format";

describe("size figures", () => {
  it("calculates in steps of a thousand, the way the packaging does", () => {
    // A stick sold as "32 GB" should stand there as 32 GB too, not as 29.8.
    expect(formatBytes(32_000_000_000)).toBe("32 GB");
    expect(formatBytes(1_500_000)).toBe("1,5 MB");
    expect(formatBytes(2_400)).toBe("2,4 kB");
  });

  it("writes small figures out without unit acrobatics", () => {
    expect(formatBytes(0)).toBe("0 Bytes");
    expect(formatBytes(999)).toBe("999 Bytes");
  });

  it("places the German comma and full stop correctly", () => {
    expect(formatCount(2150)).toBe("2.150");
    expect(formatBytes(28_400_000_000)).toBe("28,4 GB");
  });
});

describe("days since the last time", () => {
  it("writes today instead of zero days", () => {
    // "0 Tage seit der letzten Sicherung" is a puzzle, "Heute gesichert" is not.
    expect(formatDaysSince(0)).toBe("Heute");
  });

  it("writes never when the event never happened", () => {
    expect(formatDaysSince(null)).toBe("Noch nie");
  });

  it("counts the days otherwise", () => {
    expect(formatDaysSince(1)).toBe("1");
    expect(formatDaysSince(34)).toBe("34");
  });
});

describe("the three date forms", () => {
  // A moment in August: whatever zone the test runs in, the year does not tip over. That is
  // exactly the point here -- what is checked is what each form **leaves out**, not how it looks
  // in Berlin. Since point 58 the backend names the zone.
  const august_day = "2026-08-05T12:00:00Z";

  it("leaves the time of day out of the backup tile", () => {
    // A backup is a day, not a minute.
    expect(formatDate(august_day)).not.toContain(":");
    expect(formatDate(august_day)).toContain("2026");
  });

  it("leaves the year out of the visitor contributions", () => {
    // The list shows what came in this season -- the year would be noise.
    expect(formatWhen(august_day)).not.toContain("2026");
    expect(formatWhen(august_day)).toContain(":");
  });

  it("writes the month as a number in the import log", () => {
    // The column is narrow and set in tabular-nums so that the rows line up. A written-out
    // month destroys exactly that.
    const written = formatLogTime(august_day);

    expect(written).toMatch(/^\d+\.\d+\.\d{4}/);
    expect(written).toContain("2026");
    expect(written).toContain(":");
  });

  it("writes the month out where there is room for it", () => {
    expect(formatDate(august_day)).toMatch(/^\d+\. \p{L}+/u);
    expect(formatWhen(august_day)).toMatch(/^\d+\. \p{L}+/u);
  });
});
