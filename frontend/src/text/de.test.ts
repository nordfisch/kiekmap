// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Tests der Oberflaechentexte.
 *
 * Geprueft wird nicht der Wortlaut -- der darf sich aendern -- sondern eine Zusage, die beim
 * Umformulieren still bricht: Kein Text setzt einen Artikel vor einen Strassennamen.
 */

import { describe, expect, it } from "vitest";

import { t } from "./de";

describe("Fragen mit einem Strassennamen darin", () => {
  /** Alle drei Geschlechter, wie sie in Holm nebeneinander vorkommen. */
  const strassen = ["Mühlenweg", "Hauptstraße", "Achter de Möhl"];

  it("stellt den Strassennamen voran, statt ihn in den Satz zu setzen", () => {
    /**
     * Der Fehler, um den es geht: "In welchem Abschnitt vom Hauptstraße?" stand so im Kiosk. Ein
     * deutscher Strassenname kann maennlich, weiblich oder saechlich sein, ein fester Artikel
     * davor ist also bei zwei Dritteln falsch. Eine Geschlechterliste waere genau das Ortswissen,
     * das nicht in den Code gehoert -- deshalb weicht der Satz dem Fall aus, indem der Name
     * vornansteht. Steht er vorn, kann nichts vor ihm falsch gebeugt sein.
     */
    for (const strasse of strassen) {
      for (const frage of [t.location.askHouseNumber(strasse), t.location.askArea(strasse)]) {
        expect(frage.startsWith(strasse)).toBe(true);
      }
    }
  });

  it("nennt die Strasse und fragt danach", () => {
    expect(t.location.askHouseNumber("Hauptstraße")).toBe("Hauptstraße — welche Hausnummer?");
    expect(t.location.askArea("Hauptstraße")).toBe("Hauptstraße — welcher Abschnitt?");
  });
});
