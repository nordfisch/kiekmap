import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import { fetchHistogram, fetchPhotos } from "../api/client";
import { queryTimeFilter, sameViewport, useKiosk } from "./kiosk";

describe("queryTimeFilter", () => {
  const fullRange = { from: 1900, to: 1980 };

  it("schickt keinen Filter, wenn die ganze Spanne gewählt ist", () => {
    // Sonst fielen Fotos heraus, deren Datierung über die bekannte Spanne hinausreicht --
    // ausgerechnet bei dem Besucher, der gar nichts eingestellt hat.
    expect(queryTimeFilter({ from: 1900, to: 1980 }, fullRange)).toBeNull();
  });

  it("schickt einen Filter, sobald eingeschränkt wurde", () => {
    expect(queryTimeFilter({ from: 1920, to: 1930 }, fullRange)).toEqual({ from: 1920, to: 1930 });
    expect(queryTimeFilter({ from: 1900, to: 1930 }, fullRange)).toEqual({ from: 1900, to: 1930 });
    expect(queryTimeFilter({ from: 1920, to: 1980 }, fullRange)).toEqual({ from: 1920, to: 1980 });
  });

  it("kommt ohne bekannte Spanne aus", () => {
    expect(queryTimeFilter({ from: 1920, to: 1930 }, null)).toBeNull();
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

describe("Leerlauf-Reset", () => {
  beforeEach(() => {
    vi.mocked(fetchPhotos).mockResolvedValue({ photos: [], total: 0, truncated: false });
    vi.mocked(fetchHistogram).mockResolvedValue({
      decades: [],
      undated: 0,
      collection_from: null,
      collection_to: null,
    });
    useKiosk.setState({
      bbox: [9.6, 53.57, 9.75, 53.67],
      fullRange: { from: 1860, to: 1990 },
      timeRange: { from: 1930, to: 1939 },
      openPhotoId: 42,
    });
  });

  it("schliesst das offene Foto", () => {
    // Sonst steht morgens das Bild des letzten Besuchers vom Vorabend ueber der Karte.
    useKiosk.getState().reset();

    expect(useKiosk.getState().openPhotoId).toBeNull();
  });

  it("gibt den ganzen Zeitraum wieder frei", () => {
    useKiosk.getState().reset();

    expect(useKiosk.getState().timeRange).toEqual({ from: 1860, to: 1990 });
  });

  it("kommt ohne bekannte Spanne zurecht", () => {
    // Vor der ersten Histogramm-Antwort gibt es keine. Ein Absturz waere hier besonders bitter:
    // niemand sieht ihn, das Geraet bleibt einfach stehen.
    useKiosk.setState({ fullRange: null });

    expect(() => useKiosk.getState().reset()).not.toThrow();
    expect(useKiosk.getState().timeRange).toBeNull();
  });
});
