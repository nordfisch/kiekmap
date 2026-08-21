// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";

import { titleFromFilename } from "./filename";

describe("Titelvorschlag aus dem Dateinamen", () => {
  it("nimmt die Endung weg", () => {
    expect(titleFromFilename("Kirchweih.jpg")).toBe("Kirchweih");
    expect(titleFromFilename("Kirchweih.TIFF")).toBe("Kirchweih");
  });

  it("macht aus Unterstrichen Leerzeichen", () => {
    expect(titleFromFilename("Kirchweih_1932_Muehle.jpg")).toBe("Kirchweih 1932 Muehle");
  });

  it("laesst einen Bindestrich im Wort stehen", () => {
    // "Sued-West" ist ein Wort, "Umzug - 1932" sind zwei Angaben.
    expect(titleFromFilename("Sued-West_1932.jpg")).toBe("Sued-West 1932");
    expect(titleFromFilename("Umzug - 1932.jpg")).toBe("Umzug 1932");
  });

  it("wirft den Kopierzaehler weg", () => {
    expect(titleFromFilename("bild (2).jpg")).toBe("bild");
  });

  it("laesst einen Punkt mitten im Namen in Ruhe", () => {
    // Bei einem Schnitt am letzten Punkt hiesse das Foto "St".
    expect(titleFromFilename("St. Martin 1955.jpg")).toBe("St. Martin 1955");
  });

  it("liefert bei einem nichtssagenden Namen nichts Erfundenes", () => {
    expect(titleFromFilename("IMG_4711.jpg")).toBe("IMG 4711");
    expect(titleFromFilename(".jpg")).toBe("");
  });
});
