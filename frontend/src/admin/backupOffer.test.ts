import { describe, expect, it } from "vitest";

import type { DriveItem } from "../api/admin";
import { t } from "../text";
import { driveOffer, jobTitle } from "./backupOffer";

function stick(photosOnStick: number | null): DriveItem {
  return {
    path: "/media/SANDISK",
    name: "SANDISK",
    total_bytes: 128_000_000_000,
    free_bytes: 120_000_000_000,
    enough_space: true,
    backup:
      photosOnStick === null
        ? null
        : { created_at: "2026-10-01T10:00:00Z", photos: photosOnStick, bytes: 1, place: "Holm" },
  };
}

describe("what the stick card offers", () => {
  it("offers no backup on an empty device, so the backup on the stick survives", () => {
    // A fresh device: set up, plug in the stick, restore. A backup first would empty the stick.
    expect(driveOffer(stick(2150), 0)).toBe("nothing");
  });

  it("offers no backup on an empty device even when the stick is blank", () => {
    expect(driveOffer(stick(null), 0)).toBe("nothing");
  });

  it("asks before a smaller collection replaces a bigger backup", () => {
    expect(driveOffer(stick(2150), 12)).toBe("ask");
  });

  it("does not ask when the collection has grown or stayed the same", () => {
    expect(driveOffer(stick(2150), 2150)).toBe("backup");
    expect(driveOffer(stick(2150), 2200)).toBe("backup");
    expect(driveOffer(stick(null), 3)).toBe("backup");
  });
});

describe("the title of the progress view", () => {
  it("does not call a restore a backup", () => {
    expect(jobTitle("restore")).toBe(t.admin.backup.restoreRunningTitle);
    expect(jobTitle("restore")).not.toBe(t.admin.backup.title);
  });

  it("keeps the backup title for a backup", () => {
    expect(jobTitle("backup")).toBe(t.admin.backup.title);
  });
});
