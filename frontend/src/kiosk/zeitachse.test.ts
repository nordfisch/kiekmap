import { describe, expect, it } from "vitest";

import { axisBounds, clampRange, fraction } from "./zeitachse";

describe("Achse", () => {
  it("rundet auf volle Jahrzehnte auf", () => {
    expect(axisBounds({ from: 1923, to: 2019 })).toEqual({ min: 1920, max: 2020 });
  });

  it("gibt einer Sammlung aus einem einzigen Jahr trotzdem eine Laenge", () => {
    // Sonst waere max === min, und jede Rechnung darauf eine Division durch null.
    expect(axisBounds({ from: 1950, to: 1950 })).toEqual({ min: 1950, max: 1960 });
  });

  it("bleibt leer, solange kein Foto datiert ist", () => {
    expect(axisBounds(null)).toBeNull();
  });
});

describe("Auswahl ausserhalb der Achse bleibt im Bild", () => {
  const achse = { min: 1950, max: 1960 };

  it("klammert den Anteil auf null bis eins", () => {
    // Genau der Fall, der den Auswahlbalken mit left: -300% quer ueber den Titel laufen liess.
    expect(fraction(1920, achse)).toBe(0);
    expect(fraction(2019, achse)).toBe(1);
  });

  it("rechnet dazwischen genau", () => {
    expect(fraction(1955, achse)).toBe(0.5);
  });

  it("zieht auch den Zustand in die Achse", () => {
    expect(clampRange({ from: 1920, to: 2019 }, achse)).toEqual({ from: 1950, to: 1960 });
  });

  it("laesst eine gueltige Auswahl in Ruhe", () => {
    expect(clampRange({ from: 1952, to: 1958 }, achse)).toEqual({ from: 1952, to: 1958 });
  });

  it("dreht eine verkehrt herum liegende Auswahl nicht um", () => {
    expect(clampRange({ from: 1958, to: 1952 }, achse)).toEqual({ from: 1952, to: 1958 });
  });
});
