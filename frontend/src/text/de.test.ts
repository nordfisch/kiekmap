/**
 * Tests of the interface texts.
 *
 * What is checked is not the wording -- that may change -- but a promise that breaks silently
 * while rephrasing: no text puts an article in front of a street name.
 */

import { describe, expect, it } from "vitest";

import { t } from "./de";

describe("questions with a street name in them", () => {
  /** All three genders, as they occur side by side in Holm. */
  const streets = ["Mühlenweg", "Hauptstraße", "Achter de Möhl"];

  it("puts the street name first instead of into the sentence", () => {
    /**
     * The error at issue: "In welchem Abschnitt vom Hauptstraße?" stood like that in the kiosk. A
     * German street name can be masculine, feminine or neuter, so a fixed article in front of it
     * is wrong two thirds of the time. A list of genders would be exactly the local knowledge that
     * does not belong in the code -- so the sentence sidesteps the case by putting the name first.
     * Standing first, nothing before it can be inflected wrongly.
     */
    for (const street of streets) {
      for (const question of [t.location.askHouseNumber(street), t.location.askArea(street)]) {
        expect(question.startsWith(street)).toBe(true);
      }
    }
  });

  it("names the street and asks afterwards", () => {
    expect(t.location.askHouseNumber("Hauptstraße")).toBe("Hauptstraße — welche Hausnummer?");
    expect(t.location.askArea("Hauptstraße")).toBe("Hauptstraße — welcher Abschnitt?");
  });
});
