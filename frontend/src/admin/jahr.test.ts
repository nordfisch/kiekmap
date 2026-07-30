import { describe, expect, it } from "vitest";

import { decadeAllowed, toBatchDate, withYear } from "./jahr";

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
});

describe("Geaendertes Jahr nimmt das Haekchen zurueck", () => {
  it("loescht die Auswahl, sobald die Zahl nicht mehr passt", () => {
    // Nur auszugrauen genuegt nicht: ein gesetztes, aber ausgegrautes Feld schickte weiterhin
    // "Jahrzehnt" mit -- und aus 1923 wuerden still die 1920er.
    const vorher = { year: "1920", decade: true };

    expect(withYear(vorher, "1923")).toEqual({ year: "1923", decade: false });
  });

  it("laesst die Auswahl stehen, wenn sie weiterhin passt", () => {
    expect(withYear({ year: "1920", decade: true }, "1930")).toEqual({
      year: "1930",
      decade: true,
    });
  });

  it("setzt nichts von allein", () => {
    expect(withYear({ year: "1923", decade: false }, "1920")).toEqual({
      year: "1920",
      decade: false,
    });
  });
});

describe("Was an die API geht", () => {
  it("schickt ohne Jahreszahl nichts", () => {
    expect(toBatchDate({ year: "", decade: false })).toBeNull();
  });

  it("schickt ein genaues Jahr", () => {
    expect(toBatchDate({ year: "1932", decade: false })).toEqual({
      year: 1932,
      precision: "year",
    });
  });

  it("schickt ein Jahrzehnt nur, wenn es eines sein darf", () => {
    expect(toBatchDate({ year: "1920", decade: true })).toEqual({
      year: 1920,
      precision: "decade",
    });
    // Der Gurt fuer den Fall, dass die Oberflaeche doch einmal beides zulaesst.
    expect(toBatchDate({ year: "1923", decade: true })).toEqual({
      year: 1923,
      precision: "year",
    });
  });
});
