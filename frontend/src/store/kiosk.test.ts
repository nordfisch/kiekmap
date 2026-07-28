import { describe, expect, it } from "vitest";

import { queryTimeFilter, sameViewport } from "./kiosk";

describe("queryTimeFilter", () => {
  const fullRange = { von: 1900, bis: 1980 };

  it("schickt keinen Filter, wenn die ganze Spanne gewählt ist", () => {
    // Sonst fielen Fotos heraus, deren Datierung über die bekannte Spanne hinausreicht --
    // ausgerechnet bei dem Besucher, der gar nichts eingestellt hat.
    expect(queryTimeFilter({ von: 1900, bis: 1980 }, fullRange)).toBeNull();
  });

  it("schickt einen Filter, sobald eingeschränkt wurde", () => {
    expect(queryTimeFilter({ von: 1920, bis: 1930 }, fullRange)).toEqual({ von: 1920, bis: 1930 });
    expect(queryTimeFilter({ von: 1900, bis: 1930 }, fullRange)).toEqual({ von: 1900, bis: 1930 });
    expect(queryTimeFilter({ von: 1920, bis: 1980 }, fullRange)).toEqual({ von: 1920, bis: 1980 });
  });

  it("kommt ohne bekannte Spanne aus", () => {
    expect(queryTimeFilter({ von: 1920, bis: 1930 }, null)).toBeNull();
    expect(queryTimeFilter(null, fullRange)).toBeNull();
  });
});

describe("sameViewport", () => {
  const bbox = [9.6, 53.57, 9.75, 53.67] as const;

  it("erkennt winzige Unterschiede als gleich", () => {
    // Beim Antippen der Karte wackelt der Ausschnitt um Bruchteile eines Meters. Ohne diese
    // Toleranz liefe bei jedem Fingertipp eine neue Abfrage los.
    expect(sameViewport([...bbox], [9.600001, 53.570001, 9.750001, 53.670001])).toBe(true);
  });

  it("erkennt eine echte Verschiebung", () => {
    expect(sameViewport([...bbox], [9.61, 53.57, 9.76, 53.67])).toBe(false);
  });

  it("kommt mit fehlendem Ausschnitt zurecht", () => {
    expect(sameViewport(null, [...bbox])).toBe(false);
    expect(sameViewport(null, null)).toBe(true);
  });
});
