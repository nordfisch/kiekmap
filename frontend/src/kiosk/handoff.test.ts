import { describe, expect, it } from "vitest";

import { leaveHandoff, readHandoff } from "./handoff";

function memory() {
  const items = new Map<string, string>();
  return {
    getItem: (key: string) => items.get(key) ?? null,
    setItem: (key: string, value: string) => void items.set(key, value),
    removeItem: (key: string) => void items.delete(key),
  };
}

describe("the handoff across the reload", () => {
  it("carries the tapped photo", () => {
    const storage = memory();
    leaveHandoff({ id: 7, lat: 53.62, lon: 9.676 }, storage);

    expect(readHandoff(storage)).toEqual({ id: 7, lat: 53.62, lon: 9.676 });
  });

  it("is read once, so a second reload lands on the start view", () => {
    const storage = memory();
    leaveHandoff({ id: 7, lat: 53.62, lon: 9.676 }, storage);
    readHandoff(storage);

    expect(readHandoff(storage)).toBeNull();
  });

  it("ignores a note that is not complete", () => {
    const storage = memory();
    storage.setItem("kiekmap.showcase.open", JSON.stringify({ id: 7, lat: null }));

    expect(readHandoff(storage)).toBeNull();
  });

  it("works without storage", () => {
    expect(() => leaveHandoff({ id: 7, lat: 1, lon: 2 }, null)).not.toThrow();
    expect(readHandoff(null)).toBeNull();
  });
});
