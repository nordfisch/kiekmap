import { describe, expect, it } from "vitest";

import { decadeAllowed, toDate, withYear } from "./jahr";

describe("Jahrzehnt nur bei vollen Jahrzehnten", () => {
  it("laesst 1920 und 1930 zu", () => {
    expect(decadeAllowed("1920")).toBe(true);
    expect(decadeAllowed("1930")).toBe(true);
  });

  it("verweigert alles dazwischen", () => {
    // Das Backend wuerde 1934 kommentarlos zu den 1930ern runden -- die 4 waere weg.
    expect(decadeAllowed("1934")).toBe(false);
    expect(decadeAllowed("1923")).toBe(false);
  });

  it("faellt auf Unsinn nicht herein", () => {
    expect(decadeAllowed("")).toBe(false);
    expect(decadeAllowed("Kirchweih")).toBe(false);
    expect(decadeAllowed("1920er")).toBe(false);
  });

  it("laesst ohne Jahr auch kein Jahrzehnt zu", () => {
    // Die Oberflaeche sperrt die Auswahl dann ohnehin -- hier steht der Gurt darunter.
    expect(decadeAllowed("")).toBe(false);
    expect(toDate({ year: "", precision: "decade" })).toBeNull();
  });
});

describe("Geaendertes Jahr nimmt die Genauigkeit zurueck", () => {
  it("faellt auf das Jahr zurueck, sobald die Zahl nicht mehr passt", () => {
    // Nur zu sperren genuegt nicht: ein gesetztes, aber gesperrtes Feld schickte weiterhin
    // "Jahrzehnt" mit -- und aus 1923 wuerden still die 1920er.
    const vorher = { year: "1920", precision: "decade" } as const;

    expect(withYear(vorher, "1923")).toEqual({ year: "1923", precision: "year" });
  });

  it("laesst die Auswahl stehen, wenn sie weiterhin passt", () => {
    expect(withYear({ year: "1920", precision: "decade" }, "1930")).toEqual({
      year: "1930",
      precision: "decade",
    });
  });

  it("setzt nichts von allein", () => {
    expect(withYear({ year: "1923", precision: "year" }, "1920")).toEqual({
      year: "1920",
      precision: "year",
    });
  });
});

describe("Was an die API geht", () => {
  it("schickt ohne Jahreszahl nichts", () => {
    expect(toDate({ year: "", precision: "year" })).toBeNull();
  });

  it("schickt ein genaues Jahr", () => {
    expect(toDate({ year: "1932", precision: "year" })).toEqual({
      year: 1932,
      precision: "year",
    });
  });

  it("schickt ein Jahrzehnt nur, wenn es eines sein darf", () => {
    expect(toDate({ year: "1920", precision: "decade" })).toEqual({
      year: 1920,
      precision: "decade",
    });
    // Der Gurt fuer den Fall, dass die Oberflaeche doch einmal beides zulaesst.
    expect(toDate({ year: "1923", precision: "decade" })).toEqual({
      year: 1923,
      precision: "year",
    });
  });
});
