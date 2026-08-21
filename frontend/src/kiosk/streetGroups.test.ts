// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Tests der Strassenwahl ohne Tastatur.
 *
 * Der teuerste Fehler waere still: Eine Strasse, die durch das Raster faellt, ist fuer den
 * Besucher nicht verschwunden, sondern gar nicht erst da -- und niemand vermisst sie, weil
 * niemand die Liste kennt. Deshalb steht der Vollstaendigkeitstest am Ende.
 */

import { describe, expect, it } from "vitest";

import type { Place } from "../api/client";
import { MAX_BUTTONS, groupStreets } from "./streetGroups";

/** Nur der Name zaehlt fuer die Gruppierung -- der Rest kommt vom Backend unveraendert mit. */
function strassen(...namen: string[]): Place[] {
  return namen.map(
    (name, i) => ({ id: i + 1, name, lat: 53.62, lon: 9.676, kind: "strasse" }) as Place,
  );
}

/** Wie das Backend sie liefert: alphabetisch ohne Ruecksicht auf Umlaute. */
function sortiert(liste: Place[]): Place[] {
  return [...liste].sort((a, b) => a.name.localeCompare(b.name, "de"));
}

describe("Strassen zur Auswahl gruppieren", () => {
  it("laesst eine kurze Liste ungeteilt", () => {
    // Ein Dorf mit acht Strassen braucht keinen Buchstabenschritt. Genau wie bei den Hausnummern
    // faellt die Frage weg, statt mit einem einzigen Knopf dazustehen.
    const wenige = strassen("Aweg", "Bweg", "Cweg", "Dweg", "Eweg", "Fweg", "Gweg", "Hweg");

    const gruppen = groupStreets(wenige);

    expect(gruppen).toHaveLength(1);
    expect(gruppen[0]!.label).toBe("");
    expect(gruppen[0]!.streets).toHaveLength(8);
  });

  it("teilt erst, wenn es nicht mehr auf eine Seite passt", () => {
    const zehn = strassen(...Array.from({ length: MAX_BUTTONS }, (_, i) => `Strasse ${i}`));
    const elf = strassen(...Array.from({ length: MAX_BUTTONS + 1 }, (_, i) => `Weg ${i}`));

    expect(groupStreets(zehn)).toHaveLength(1);
    expect(groupStreets(elf).length).toBeGreaterThan(1);
  });

  it("verschmilzt duenne Buchstaben mit dem Nachbarn", () => {
    /**
     * Ein Dorf hat vier Strassen auf M und keine auf Q. Ein Knopf je Buchstabe verschenkte die
     * Flaeche an leere -- deshalb wird zusammengelegt, bis hoechstens zehn Knoepfe bleiben.
     */
    const bestand = sortiert(
      strassen(
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

    const etiketten = groupStreets(bestand).map((gruppe) => gruppe.label);

    expect(etiketten.length).toBeLessThanOrEqual(MAX_BUTTONS);
    // Das A traegt allein 14 Strassen und bleibt deshalb fuer sich.
    expect(etiketten).toContain("A");
    // Irgendwo muessen die duennen Buchstaben zusammengefasst worden sein.
    expect(etiketten.some((etikett) => etikett.includes("–"))).toBe(true);
  });

  it("gibt einem Umlaut am Anfang keinen eigenen Knopf", () => {
    /**
     * Der Fall, den Holm nicht hat und das zweite Museum still bekommt: Ohne Entschaerfung
     * stuende der Oelmuehlenweg unter einem einsamen "Ö" -- und zwar hinter dem Z.
     */
    const bestand = sortiert(
      strassen(
        "Ölmühlenweg",
        "Ostweg",
        "Osterende",
        ...Array.from({ length: 20 }, (_, i) => `Bahnweg ${i}`),
      ),
    );

    const gruppen = groupStreets(bestand);
    const mitOel = gruppen.find((gruppe) =>
      gruppe.streets.some((strasse) => strasse.name === "Ölmühlenweg"),
    )!;

    expect(mitOel.label.startsWith("O")).toBe(true);
    expect(mitOel.streets.map((strasse) => strasse.name)).toContain("Ostweg");
    expect(gruppen.map((gruppe) => gruppe.label)).not.toContain("Ö");
  });

  it("teilt eine grosse Gruppe am zweiten Wort weiter", () => {
    /**
     * 29 Strassen, die alle mit "Am " anfangen -- in Holm ist das der Regelfall hinter dem A.
     * Ein fester Schnitt nach einem Zeichen brachte hier gar nichts; der Schnitt folgt den Namen.
     */
    const amStrassen = sortiert(
      strassen(
        ...["Bullensee", "Burggraben", "Felde", "Freibad", "Hang", "Kamp", "Knick", "Lohhof"].map(
          (rest) => `Am ${rest}`,
        ),
        ...["Marienhof", "Meierhof", "Melkplatz", "Nienkamp", "Ohlenhof", "Park", "Redder"].map(
          (rest) => `Am ${rest}`,
        ),
      ),
    );

    const gruppen = groupStreets(amStrassen);

    expect(gruppen.length).toBeGreaterThan(1);
    // Alle Etiketten fangen mit "Am " an -- der Schnitt sitzt hinter dem gemeinsamen Wort.
    for (const gruppe of gruppen) expect(gruppe.label.startsWith("Am ")).toBe(true);
  });

  it("laesst keine Strasse fallen", () => {
    /**
     * Der Test, der zaehlt. Ueber zwei Ebenen hinweg muessen am Ende genau die Strassen stehen,
     * die hineingegangen sind -- keine doppelt, keine fehlend.
     */
    const bestand = sortiert(
      strassen(
        ...Array.from({ length: 80 }, (_, i) => {
          const buchstabe = "ABCDEFGHIKLMNOPRSTWZ"[i % 20];
          return `${buchstabe}${"m".repeat((i % 3) + 1)}strasse ${i}`;
        }),
      ),
    );

    const blaetter: string[] = [];
    for (const oben of groupStreets(bestand)) {
      expect(oben.streets.length).toBeGreaterThan(0);
      for (const unten of groupStreets(oben.streets)) {
        expect(unten.streets.length).toBeLessThanOrEqual(MAX_BUTTONS);
        blaetter.push(...unten.streets.map((strasse) => strasse.name));
      }
    }

    expect(blaetter.sort()).toEqual(bestand.map((strasse) => strasse.name).sort());
  });
});
