import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import { fetchPhotos } from "../api/client";
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

describe("Fokus nach einem Beitrag", () => {
  function machFoto(felder: Record<string, unknown>) {
    return {
      id: 1,
      lat: 53.62,
      lon: 9.676,
      date_from: null,
      // Der Rest interessiert showPhoto nicht.
      ...felder,
    } as never;
  }

  beforeEach(() => {
    vi.mocked(fetchPhotos).mockResolvedValue({ photos: [], total: 0, truncated: false });
    useKiosk.setState({
      bbox: [9.6, 53.57, 9.75, 53.67],
      fullRange: { from: 1920, to: 2019 },
      timeRange: { from: 1950, to: 1959 },
      focus: null,
      rangeBefore: null,
    });
  });

  it("stellt den Zeitraum auf das Jahrzehnt des Fotos", () => {
    useKiosk.getState().showPhoto(machFoto({ date_from: "1932-01-01" }));

    expect(useKiosk.getState().timeRange).toEqual({ from: 1930, to: 1939 });
    expect(useKiosk.getState().focus).not.toBeNull();
  });

  it("gibt Karte und Zeitraum zusammen zurueck", () => {
    useKiosk.getState().showPhoto(machFoto({ date_from: "1932-01-01" }));
    useKiosk.getState().releaseFocus();

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
    expect(useKiosk.getState().focus).toBeNull();
  });

  it("gibt nach zwei Beitraegen den urspruenglichen Zeitraum zurueck", () => {
    // Der Dank-Zeitgeber wird beim zweiten Beitrag neu gesetzt. Merkte sich der zweite Aufruf den
    // Zeitraum des ersten Fokus, bekaeme der Besucher am Ende ein Jahrzehnt zurueck, das er nie
    // eingestellt hat.
    useKiosk.getState().showPhoto(machFoto({ date_from: "1932-01-01" }));
    useKiosk.getState().showPhoto(machFoto({ id: 2, date_from: "1975-01-01" }));
    useKiosk.getState().releaseFocus();

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
  });

  it("laesst ein Foto ohne Ort die Ansicht nicht verstellen", () => {
    useKiosk.getState().showPhoto(machFoto({ lat: null, lon: null, date_from: "1932-01-01" }));

    expect(useKiosk.getState().focus).toBeNull();
    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
  });
});
