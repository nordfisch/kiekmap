import { describe, expect, it } from "vitest";

import { RELOAD_COOLDOWN_MS, lastRecovery, mayReload, noteRecovery } from "./recover";

/** A sessionStorage in two lines -- the test needs no browser. */
function storage(content: Record<string, string> = {}) {
  return {
    getItem: (key: string) => content[key] ?? null,
    setItem: (key: string, value: string) => {
      content[key] = value;
    },
  };
}

describe("may the page reload itself?", () => {
  it("on the first crash, certainly", () => {
    expect(mayReload(null, 1_000_000)).toBe(true);
  });

  it("not straight away a second time", () => {
    // The case this question exists for: a crash that returns while loading would otherwise
    // make the screen flicker endlessly. A readable message is better than that.
    expect(mayReload(1_000_000, 1_000_000 + 5_000)).toBe(false);
  });

  it("later on, again", () => {
    expect(mayReload(1_000_000, 1_000_000 + RELOAD_COOLDOWN_MS + 1)).toBe(true);
  });

  it("even when the clock has jumped backwards", () => {
    // The Pi has no real-time clock: after a power cut its clock can be years out. Calculating
    // strictly forwards would switch the self-healing off for good -- exactly the state it is
    // there to prevent.
    expect(mayReload(1_000_000, 1_000_000 - 60_000)).toBe(true);
  });
});

describe("the note about the last restart", () => {
  it("is written and found again", () => {
    const store = storage();
    noteRecovery(store, 42_000);

    expect(lastRecovery(store)).toBe(42_000);
  });

  it("is empty without a note", () => {
    expect(lastRecovery(storage())).toBeNull();
  });

  it("survives an unusable value", () => {
    // Somebody has written into the storage. Then rather one attempt too many than an exception
    // in the error path -- that would be a crash while handling a crash.
    expect(lastRecovery(storage({ "kiekmap-neustart": "gestern" }))).toBeNull();
  });

  it("survives a storage that refuses", () => {
    const refuses = {
      getItem: () => {
        throw new Error("not available");
      },
      setItem: () => {
        throw new Error("not available");
      },
    };

    expect(lastRecovery(refuses)).toBeNull();
    expect(() => noteRecovery(refuses, 1)).not.toThrow();
  });
});
