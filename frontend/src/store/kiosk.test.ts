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

describe("Der Zeitraum beim ersten Laden", () => {
  /** Der Bestand von Holm: juengste Aufnahme 2024, alles taggenau, also Jahresbalken. */
  function histogramm(felder: Record<string, unknown> = {}) {
    vi.mocked(fetchHistogram).mockResolvedValue({
      bars: [{ year: 2014, count: 118 }],
      step: 1,
      undated: 673,
      collection_from: 2010,
      collection_to: 2024,
      ...felder,
    } as never);
  }

  beforeEach(() => {
    vi.mocked(fetchPhotos).mockResolvedValue({ photos: [], total: 0, truncated: false });
    histogramm();
    useKiosk.setState({ bbox: null, fullRange: null, timeRange: null, histogram: null });
  });

  it("greift ueber die ganze Achse, nicht nur bis zum juengsten Foto", async () => {
    /**
     * Die Achse reicht einen Balken ueber das juengste Foto hinaus, damit dieser Balken eigene
     * Bahn hat. Startete die Auswahl auf der Spanne des Bestands, bliebe rechts ein Stueck offen
     * -- und das sieht aus, als waere schon etwas weggefiltert.
     */
    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().timeRange).not.toBeNull());

    expect(useKiosk.getState().timeRange).toEqual({ from: 2010, to: 2025 });
  });

  it("schickt trotzdem keinen Zeitfilter", async () => {
    /**
     * Der Grund, warum die weitere Auswahl nichts kostet: ``queryTimeFilter`` fragt, ob die
     * Auswahl die Spanne *ueberdeckt*, nicht ob sie ihr gleicht. Ginge ein Filter hinaus, fielen
     * die 673 undatierten Fotos von der Karte -- die gibt es nur ohne Filter.
     */
    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().timeRange).not.toBeNull());

    const { timeRange, fullRange } = useKiosk.getState();
    expect(queryTimeFilter(timeRange, fullRange)).toBeNull();
  });

  it("laesst eine schon getroffene Auswahl in Ruhe", async () => {
    useKiosk.setState({ timeRange: { from: 2014, to: 2016 } });

    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().histogram).not.toBeNull());

    expect(useKiosk.getState().timeRange).toEqual({ from: 2014, to: 2016 });
  });
});

describe("Der Schalter für die Fotos ohne Jahr", () => {
  /**
   * Ein Foto ohne Datum überlappt keinen Zeitraum, fällt also aus jeder Auswahl heraus — beim
   * Erstbestand zwei Drittel der Sammlung. Bisher war das eine Nebenwirkung der Schieberstellung,
   * die niemandem angesagt wurde; jetzt ist es ein Schalter, den der Schieber genau einmal für
   * den Besucher umlegt.
   */
  beforeEach(() => {
    vi.mocked(fetchPhotos).mockResolvedValue({ photos: [], total: 0, truncated: false });
    useKiosk.setState({
      bbox: [9.6, 53.57, 9.75, 53.67],
      fullRange: { from: 2010, to: 2024 },
      histogram: null,
      timeRange: { from: 2010, to: 2030 },
      showUndated: true,
      undatedByHand: false,
    });
  });

  it("steht anfangs an", () => {
    // Der erste Blick zeigt, was das Museum hat. Niemand verliert etwas, ohne es getan zu haben.
    expect(useKiosk.getInitialState().showUndated).toBe(true);
  });

  it("geht aus, sobald der Zeitraum eingeengt wird", () => {
    useKiosk.getState().setTimeRange({ from: 2014, to: 2016 });

    expect(useKiosk.getState().showUndated).toBe(false);
  });

  it("bleibt an, solange die Auswahl die ganze Spanne überdeckt", () => {
    /**
     * Die Achse reicht bis 2030, das jüngste Foto liegt bei 2024: Der Endgriff kann ein Stück
     * wandern, ohne dass irgendetwas herausfiele. ``queryTimeFilter`` schickt dann keinen Filter,
     * und wo nichts gefiltert wird, ist auch nichts abzuschalten — sonst nähme der Schieber die
     * undatierten Fotos schon beim ersten Antippen weg, ganz ohne Wirkung auf den Rest.
     */
    useKiosk.getState().setTimeRange({ from: 2010, to: 2026 });

    expect(useKiosk.getState().timeRange).toEqual({ from: 2010, to: 2026 });
    expect(useKiosk.getState().showUndated).toBe(true);
  });

  it("greift nicht mehr, wenn der Besucher ihn selbst angefasst hat", () => {
    /**
     * Der Fall, der die Automatik sonst zur Plage macht: Wer die undatierten Fotos von Hand
     * wieder einschaltet und danach den Schieber anfasst, verlöre sie sofort wieder — genau die
     * Nebenwirkung, gegen die dieser Schalter gebaut ist, nur eine Ebene höher.
     */
    useKiosk.getState().setTimeRange({ from: 2014, to: 2016 });
    useKiosk.getState().setShowUndated(true);

    useKiosk.getState().setTimeRange({ from: 2018, to: 2020 });

    expect(useKiosk.getState().showUndated).toBe(true);
  });

  it("geht auch von Hand wieder aus", () => {
    useKiosk.getState().setShowUndated(false);

    expect(useKiosk.getState().showUndated).toBe(false);
    expect(useKiosk.getState().undatedByHand).toBe(true);
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
