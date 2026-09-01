/**
 * Both catalogues, and the promise that neither has a hole in it.
 *
 * `tsc` already refuses a missing key -- `Texts` is `typeof de`. What it cannot see is an empty
 * string somebody left as a placeholder, or a function where the other language has plain text.
 * On a museum screen an empty label looks like a fault in the program.
 */

import { beforeEach, describe, expect, it } from "vitest";

import { de } from "./de";
import { en } from "./en";
import { setLanguage, t } from "./index";

type Leaf = string | ((...args: never[]) => string);

/** Every leaf of a catalogue, as `path -> value`. */
function leaves(node: Record<string, unknown>, prefix = ""): [string, Leaf][] {
  return Object.entries(node).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "object" && value !== null) {
      return leaves(value as Record<string, unknown>, path);
    }
    return [[path, value as Leaf]];
  });
}

describe.each([
  ["de", de],
  ["en", en],
])("the %s catalogue", (language, catalogue) => {
  const entries = leaves(catalogue as unknown as Record<string, unknown>);

  it("has no empty text", () => {
    for (const [path, value] of entries) {
      if (typeof value === "string") expect(value.trim(), path).not.toBe("");
    }
  });

  it("has a function everywhere the other one has one", () => {
    const other = language === "de" ? en : de;
    for (const [path, value] of entries) {
      const counterpart = path
        .split(".")
        .reduce<unknown>((node, key) => (node as Record<string, unknown>)[key], other);
      expect(typeof counterpart, path).toBe(typeof value);
    }
  });
});

describe("the switch", () => {
  beforeEach(() => setLanguage("de"));

  it("changes what the interface says", () => {
    expect(t.map.untitled).toBe("Ohne Titel");

    setLanguage("en");

    expect(t.map.untitled).toBe("Untitled");
  });

  it("changes the locale the numbers are formatted with", () => {
    expect(t.locale).toBe("de-DE");

    setLanguage("en");

    expect(t.locale).toBe("en-GB");
  });

  it("reaches a module that imported t before the switch", () => {
    /**
     * The construction, in one assertion. `t` is an exported `let`; ES modules bind by reference,
     * so the thirty importers see the reassignment instead of holding a stale copy. A plain
     * `export const t = de` would compile and then show German on an English device.
     */
    setLanguage("en");

    expect(t.admin.format.never).toBe("Never");
  });
});
