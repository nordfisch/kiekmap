// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";

import type { Place } from "../api/client";
import { baseNumber, blocksOf, groupByBase } from "./houseNumbers";

let id = 0;
function adresse(housenumber: string): Place {
  return {
    id: ++id,
    name: `Mühlenweg ${housenumber}`,
    kind: "adresse",
    lat: 53.62,
    lon: 9.676,
    street: "Mühlenweg",
    housenumber,
    accuracy_m: 15,
  } as Place;
}

describe("Grundzahl", () => {
  it("liest die fuehrende Zahl", () => {
    expect(baseNumber("3")).toBe(3);
    expect(baseNumber("3c")).toBe(3);
    expect(baseNumber("10-18")).toBe(10);
  });

  it("faellt auf Unsinn nicht herein", () => {
    expect(baseNumber("")).toBeNull();
    expect(baseNumber("ohne Nummer")).toBeNull();
  });
});

describe("Buchstabenzusaetze zusammenfassen", () => {
  it("macht aus einer Reihenhauszeile einen Knopf", () => {
    // 3a bis 3z am Muehlenweg: raeumlich ist das ein Punkt, in der Liste waren es 27.
    const liste = groupByBase([
      adresse("3"),
      adresse("3a"),
      adresse("3b"),
      adresse("3c"),
      adresse("5"),
    ]);

    expect(liste.map((p) => p.housenumber)).toEqual(["3", "5"]);
  });

  it("nimmt den ersten Eintrag, wenn es die nackte Zahl nicht gibt", () => {
    // Sonst stuende auf dem Knopf eine Adresse, die es gar nicht gibt.
    const liste = groupByBase([adresse("3a"), adresse("3b")]);

    expect(liste.map((p) => p.housenumber)).toEqual(["3a"]);
  });

  it("sortiert nach der Zahl, nicht alphabetisch", () => {
    const liste = groupByBase([adresse("10"), adresse("9"), adresse("1")]);

    expect(liste.map((p) => p.housenumber)).toEqual(["1", "9", "10"]);
  });
});

describe("Bereiche", () => {
  const viele = Array.from({ length: 39 }, (_, i) => adresse(String(i * 2 + 1)));

  it("laesst kurze Strassen in einem Schritt", () => {
    // Holms mittlere Strasse hat fuenfzehn Adressen -- dort soll kein zweiter Schritt entstehen.
    const bloecke = blocksOf(viele.slice(0, 12));

    expect(bloecke).toHaveLength(1);
    expect(bloecke[0]!.numbers).toHaveLength(12);
  });

  it("teilt lange Strassen in etwa gleich grosse Bereiche", () => {
    const bloecke = blocksOf(viele);

    expect(bloecke.length).toBeLessThanOrEqual(12);
    for (const block of bloecke) expect(block.numbers.length).toBeLessThanOrEqual(12);
    // Keine Nummer geht verloren und keine kommt doppelt vor.
    expect(bloecke.flatMap((b) => b.numbers)).toHaveLength(viele.length);
  });

  it("beschriftet die Bereiche mit den Nummern, die wirklich darin liegen", () => {
    // Nach der Luecke am Muehlenweg heisst der letzte Bereich eben "47-183" -- das ist ehrlicher
    // als ein glattes "40-49", in dem nichts steht.
    const bloecke = blocksOf([...viele.slice(0, 20), adresse("169"), adresse("183")]);

    expect(bloecke[0]!.label).toMatch(/^1–/);
    expect(bloecke.at(-1)!.label).toMatch(/–183$/);
  });
});
