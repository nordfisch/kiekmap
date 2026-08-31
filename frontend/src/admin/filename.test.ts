import { describe, expect, it } from "vitest";

import { titleFromFilename } from "./filename";

describe("a suggested title from the file name", () => {
  it("takes the suffix off", () => {
    expect(titleFromFilename("Kirchweih.jpg")).toBe("Kirchweih");
    expect(titleFromFilename("Kirchweih.TIFF")).toBe("Kirchweih");
  });

  it("turns underscores into spaces", () => {
    expect(titleFromFilename("Kirchweih_1932_Muehle.jpg")).toBe("Kirchweih 1932 Muehle");
  });

  it("leaves a hyphen inside a word alone", () => {
    // "Sued-West" is one word, "Umzug - 1932" is two entries.
    expect(titleFromFilename("Sued-West_1932.jpg")).toBe("Sued-West 1932");
    expect(titleFromFilename("Umzug - 1932.jpg")).toBe("Umzug 1932");
  });

  it("throws the copy counter away", () => {
    expect(titleFromFilename("bild (2).jpg")).toBe("bild");
  });

  it("leaves a full stop in the middle of the name alone", () => {
    // Cutting at the last full stop would name the photo "St".
    expect(titleFromFilename("St. Martin 1955.jpg")).toBe("St. Martin 1955");
  });

  it("invents nothing for a name that says nothing", () => {
    expect(titleFromFilename("IMG_4711.jpg")).toBe("IMG 4711");
    expect(titleFromFilename(".jpg")).toBe("");
  });
});
