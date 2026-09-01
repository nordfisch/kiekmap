/**
 * Tests of choosing a street without a keyboard.
 *
 * The most expensive error would be a silent one: a street that falls through the grid has not
 * vanished for the visitor, it was never there -- and nobody misses it, because nobody knows the
 * list. That is why the completeness test stands at the end.
 */

import { describe, expect, it } from "vitest";

import type { Place } from "../api/client";
import { MAX_BUTTONS, groupStreets } from "./streetGroups";

/** Only the name counts for the grouping -- the rest comes from the backend unchanged. */
function streetsNamed(...names: string[]): Place[] {
  return names.map(
    (name, i) => ({ id: i + 1, name, lat: 53.62, lon: 9.676, kind: "strasse" }) as Place,
  );
}

/** The way the backend delivers them: alphabetically, without regard for umlauts. */
function sorted(list: Place[]): Place[] {
  return [...list].sort((a, b) => a.name.localeCompare(b.name, "de"));
}

describe("grouping streets for the choice", () => {
  it("leaves a short list undivided", () => {
    // A village with eight streets needs no letter step. Just as with the house numbers the
    // question falls away instead of standing there with a single button.
    const few = streetsNamed("Aweg", "Bweg", "Cweg", "Dweg", "Eweg", "Fweg", "Gweg", "Hweg");

    const groups = groupStreets(few);

    expect(groups).toHaveLength(1);
    expect(groups[0]!.label).toBe("");
    expect(groups[0]!.streets).toHaveLength(8);
  });

  it("only divides once it no longer fits on one page", () => {
    const ten = streetsNamed(...Array.from({ length: MAX_BUTTONS }, (_, i) => `Strasse ${i}`));
    const eleven = streetsNamed(
      ...Array.from({ length: MAX_BUTTONS + 1 }, (_, i) => `Weg ${i}`),
    );

    expect(groupStreets(ten)).toHaveLength(1);
    expect(groupStreets(eleven).length).toBeGreaterThan(1);
  });

  it("merges thin letters with their neighbour", () => {
    /**
     * A village has four streets under M and none under Q. One button per letter would give the
     * space away to empty ones -- so they are merged until at most ten buttons remain.
     */
    const collection = sorted(
      streetsNamed(
        ...Array.from({ length: 14 }, (_, i) => `Am Feld ${i}`),
        "Birkenweg",
        "Deelenweg",
        "Eichengrund",
        "Fasanenweg",
        "Kreuzweg",
        "Lehmweg",
        "Mittelweg",
        "Niederstrasse",
        "Papentwiete",
        "Rehnaer Strasse",
        "Schulstrasse",
        "Twiete",
        "Wedeler Strasse",
      ),
    );

    const labels = groupStreets(collection).map((group) => group.label);

    expect(labels.length).toBeLessThanOrEqual(MAX_BUTTONS);
    // A alone carries 14 streets and therefore stays on its own.
    expect(labels).toContain("A");
    // Somewhere the thin letters must have been merged.
    expect(labels.some((label) => label.includes("–"))).toBe(true);
  });

  it("gives an umlaut at the start no button of its own", () => {
    /**
     * The case Holm does not have and the second museum silently gets: without defusing it, the
     * Ölmühlenweg would stand under a lonely "Ö" -- and behind the Z at that.
     */
    const collection = sorted(
      streetsNamed(
        "Ölmühlenweg",
        "Ostweg",
        "Osterende",
        ...Array.from({ length: 20 }, (_, i) => `Bahnweg ${i}`),
      ),
    );

    const groups = groupStreets(collection);
    const withUmlaut = groups.find((group) =>
      group.streets.some((street) => street.name === "Ölmühlenweg"),
    )!;

    expect(withUmlaut.label.startsWith("O")).toBe(true);
    expect(withUmlaut.streets.map((street) => street.name)).toContain("Ostweg");
    expect(groups.map((group) => group.label)).not.toContain("Ö");
  });

  it("divides a large group further at the second word", () => {
    /**
     * 29 streets all beginning with "Am " -- in Holm that is the normal case behind the A. A fixed
     * cut after one character achieved nothing here; the cut follows the names.
     */
    const amStreets = sorted(
      streetsNamed(
        ...["Bullensee", "Burggraben", "Felde", "Freibad", "Hang", "Kamp", "Knick", "Lohhof"].map(
          (rest) => `Am ${rest}`,
        ),
        ...["Marienhof", "Meierhof", "Melkplatz", "Nienkamp", "Ohlenhof", "Park", "Redder"].map(
          (rest) => `Am ${rest}`,
        ),
      ),
    );

    const groups = groupStreets(amStreets);

    expect(groups.length).toBeGreaterThan(1);
    // Every label begins with "Am " -- the cut sits behind the shared word.
    for (const group of groups) expect(group.label.startsWith("Am ")).toBe(true);
  });

  it("drops no street", () => {
    /**
     * The test that counts. Across two levels, exactly the streets that went in have to stand at
     * the end -- none twice, none missing.
     */
    const collection = sorted(
      streetsNamed(
        ...Array.from({ length: 80 }, (_, i) => {
          const letter = "ABCDEFGHIKLMNOPRSTWZ"[i % 20];
          return `${letter}${"m".repeat((i % 3) + 1)}strasse ${i}`;
        }),
      ),
    );

    const leaves: string[] = [];
    for (const upper of groupStreets(collection)) {
      expect(upper.streets.length).toBeGreaterThan(0);
      for (const lower of groupStreets(upper.streets)) {
        expect(lower.streets.length).toBeLessThanOrEqual(MAX_BUTTONS);
        leaves.push(...lower.streets.map((street) => street.name));
      }
    }

    expect(leaves.sort()).toEqual(collection.map((street) => street.name).sort());
  });
});
