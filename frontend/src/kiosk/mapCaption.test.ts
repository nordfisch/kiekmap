import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { captionOf } from "./mapCaption";

function photo(fields: Partial<PhotoMarker>): PhotoMarker {
  return {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    title: null,
    place_name: null,
    date_label: "Jahr unbekannt",
    date_short: "",
    width: 100,
    height: 80,
    thumb_url: "/api/photos/1/thumb",
    ...fields,
  };
}

describe("what stands under a thumbnail", () => {
  it("takes the title before the address", () => {
    /**
     * The reversal of 12 August 2026. Until then the address stood there -- and rightly so,
     * because back then the titles *were* addresses. Since they were cleaned up, "Gasthof Timm"
     * says more than "Hauptstraße 11a".
     */
    const line = captionOf([photo({ title: "Gasthof Timm", place_name: "Hauptstraße 11a" })]);

    expect(line).toBe("Gasthof Timm");
  });

  it("falls back to the address without a title", () => {
    expect(captionOf([photo({ place_name: "Lehmweg 17b" })])).toBe("Lehmweg 17b");
  });

  it("writes a question mark when the house number is unknown", () => {
    /**
     * The gap is named, not kept quiet -- the same stance as not scattering the stacks
     * (decisions.md, point 33). That is exactly what the contribution panel asks about, and the
     * map shows where the question is still open.
     */
    expect(captionOf([photo({ place_name: "Hauptstraße" })])).toBe("Hauptstraße Nr. ?");
  });

  it("appends the year with an em dash", () => {
    expect(captionOf([photo({ title: "Funkmast", date_short: "2018" })])).toBe("Funkmast — 2018");
  });

  it("leaves the dash out where no year is known", () => {
    // Two thirds of the collection. An appended "Jahr unbekannt" would look the same seven
    // hundred times over and say nothing.
    expect(captionOf([photo({ title: "Funkmast" })])).toBe("Funkmast");
  });

  it("carries the line with the year alone if it has to", () => {
    // A photo located only through EXIF has neither a title nor an address.
    expect(captionOf([photo({ date_short: "2014" })])).toBe("2014");
  });

  it("stays empty when nothing is known", () => {
    // And not a dash or a notice of absence: the line falls away entirely.
    expect(captionOf([photo({})])).toBe("");
  });
});

describe("what stands over a stack", () => {
  it("names the title only when every photo shares it", () => {
    const line = captionOf([
      photo({ title: "Jagdhaus", place_name: "Lehmweg" }),
      photo({ title: "Jagdhaus", place_name: "Lehmweg" }),
    ]);

    expect(line).toBe("Jagdhaus");
  });

  it("falls back to the shared address when the titles differ", () => {
    /**
     * The silent error this rule prevents: photos land on one marker because they share a
     * coordinate -- so they usually share their address, rarely their titles. Taking the topmost
     * would mean writing "Gasthof Timm" over fifty images showing something else.
     */
    const line = captionOf([
      photo({ title: "Gasthof Timm", place_name: "Hauptstraße 11a" }),
      photo({ title: "Bäckerei Petersen", place_name: "Hauptstraße 11a" }),
    ]);

    expect(line).toBe("Hauptstraße 11a");
  });

  it("stays silent when the address is not shared either", () => {
    // Two photos located through EXIF can lie a metre apart without having anything to do with
    // each other.
    const line = captionOf([
      photo({ title: "Hof Sieveking", place_name: "Im Sande 3" }),
      photo({ title: "Hof Boysen", place_name: "Hauptstraße 29" }),
    ]);

    expect(line).toBe("");
  });

  it("gets no year", () => {
    // Fifty photos of Schulstrasse 2 were taken over decades. The year of the topmost would
    // stand over all of them.
    const line = captionOf([
      photo({ title: "Winter in Holm", date_short: "1985" }),
      photo({ title: "Winter in Holm", date_short: "1990" }),
    ]);

    expect(line).toBe("Winter in Holm");
  });
});
