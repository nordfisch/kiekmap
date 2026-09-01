import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import { fetchHistogram, fetchPhotos } from "../api/client";
import { queryTimeFilter, sameViewport, useKiosk } from "./kiosk";

describe("queryTimeFilter", () => {
  const fullRange = { from: 1900, to: 1980 };

  it("sends no filter when the whole span is selected", () => {
    // Otherwise photos whose dating reaches beyond the known span would drop out -- for the very
    // visitor who set nothing at all.
    expect(queryTimeFilter({ from: 1900, to: 1980 }, fullRange)).toBeNull();
  });

  it("sends a filter as soon as the range was narrowed", () => {
    expect(queryTimeFilter({ from: 1920, to: 1930 }, fullRange)).toEqual({ from: 1920, to: 1930 });
    expect(queryTimeFilter({ from: 1900, to: 1930 }, fullRange)).toEqual({ from: 1900, to: 1930 });
    expect(queryTimeFilter({ from: 1920, to: 1980 }, fullRange)).toEqual({ from: 1920, to: 1980 });
  });

  it("manages without a known span", () => {
    expect(queryTimeFilter({ from: 1920, to: 1930 }, null)).toBeNull();
    expect(queryTimeFilter(null, fullRange)).toBeNull();
  });
});

describe("sameViewport", () => {
  const bbox = [9.6, 53.57, 9.75, 53.67] as const;

  it("treats tiny differences as equal", () => {
    // Tapping the map wobbles the viewport by fractions of a metre. Without this tolerance a
    // new query would fire on every tap.
    expect(sameViewport([...bbox], [9.600001, 53.570001, 9.750001, 53.670001])).toBe(true);
  });

  it("recognises a real shift", () => {
    expect(sameViewport([...bbox], [9.61, 53.57, 9.76, 53.67])).toBe(false);
  });

  it("copes with a missing viewport", () => {
    expect(sameViewport(null, [...bbox])).toBe(false);
    expect(sameViewport(null, null)).toBe(true);
  });
});

describe("the range on first load", () => {
  /** The Holm collection: most recent photo 2024, all day-precise, so year bars. */
  function histogram(fields: Record<string, unknown> = {}) {
    vi.mocked(fetchHistogram).mockResolvedValue({
      bars: [{ year: 2014, count: 118 }],
      step: 1,
      undated: 673,
      collection_from: 2010,
      collection_to: 2024,
      ...fields,
    } as never);
  }

  beforeEach(() => {
    vi.mocked(fetchPhotos).mockResolvedValue({ photos: [], total: 0, truncated: false });
    histogram();
    useKiosk.setState({ bbox: null, fullRange: null, timeRange: null, histogram: null });
  });

  it("reaches across the whole axis, not only to the most recent photo", async () => {
    /**
     * The axis reaches one bar beyond the most recent photo so that this bar has a lane of its
     * own. If the selection started at the span of the collection, a piece would stay open on the
     * right -- and that looks as though something had already been filtered away.
     */
    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().timeRange).not.toBeNull());

    expect(useKiosk.getState().timeRange).toEqual({ from: 2010, to: 2025 });
  });

  it("still sends no time filter", async () => {
    /**
     * The reason the wider selection costs nothing: ``queryTimeFilter`` asks whether the selection
     * *covers* the span, not whether it equals it. If a filter went out, the 673 undated photos
     * would fall off the map -- they exist only without a filter.
     */
    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().timeRange).not.toBeNull());

    const { timeRange, fullRange } = useKiosk.getState();
    expect(queryTimeFilter(timeRange, fullRange)).toBeNull();
  });

  it("leaves a selection already made alone", async () => {
    useKiosk.setState({ timeRange: { from: 2014, to: 2016 } });

    useKiosk.getState().setViewport([9.6, 53.57, 9.75, 53.67]);
    await vi.waitFor(() => expect(useKiosk.getState().histogram).not.toBeNull());

    expect(useKiosk.getState().timeRange).toEqual({ from: 2014, to: 2016 });
  });
});

describe("the switch for the photos without a year", () => {
  /**
   * A photo without a date overlaps no range, so it drops out of every selection -- two thirds of
   * the initial collection. That used to be a side effect of where the slider stood, announced to
   * nobody; now it is a switch the slider throws for the visitor exactly once.
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

  it("is on to begin with", () => {
    // The first look shows what the museum has. Nobody loses anything without having done it.
    expect(useKiosk.getInitialState().showUndated).toBe(true);
  });

  it("goes off as soon as the range is narrowed", () => {
    useKiosk.getState().setTimeRange({ from: 2014, to: 2016 });

    expect(useKiosk.getState().showUndated).toBe(false);
  });

  it("stays on while the selection covers the whole span", () => {
    /**
     * The axis reaches to 2030, the most recent photo lies at 2024: the end handle can travel a
     * little without anything dropping out. ``queryTimeFilter`` then sends no filter, and where
     * nothing is filtered there is nothing to switch off -- otherwise the slider would take the
     * undated photos away at the first tap, with no effect on the rest at all.
     */
    useKiosk.getState().setTimeRange({ from: 2010, to: 2026 });

    expect(useKiosk.getState().timeRange).toEqual({ from: 2010, to: 2026 });
    expect(useKiosk.getState().showUndated).toBe(true);
  });

  it("no longer takes hold once the visitor has touched it themselves", () => {
    /**
     * The case that otherwise makes the automation a nuisance: whoever switches the undated photos
     * back on by hand and then touches the slider would lose them again at once -- exactly the
     * side effect this switch is built against, one level higher.
     */
    useKiosk.getState().setTimeRange({ from: 2014, to: 2016 });
    useKiosk.getState().setShowUndated(true);

    useKiosk.getState().setTimeRange({ from: 2018, to: 2020 });

    expect(useKiosk.getState().showUndated).toBe(true);
  });

  it("goes off again by hand too", () => {
    useKiosk.getState().setShowUndated(false);

    expect(useKiosk.getState().showUndated).toBe(false);
    expect(useKiosk.getState().undatedByHand).toBe(true);
  });
});

describe("focus after a contribution", () => {
  function makePhoto(fields: Record<string, unknown>) {
    return {
      id: 1,
      lat: 53.62,
      lon: 9.676,
      date_from: null,
      // showPhoto does not care about the rest.
      ...fields,
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

  it("sets the range to the decade of the photo", () => {
    useKiosk.getState().showPhoto(makePhoto({ date_from: "1932-01-01" }));

    expect(useKiosk.getState().timeRange).toEqual({ from: 1930, to: 1939 });
    expect(useKiosk.getState().focus).not.toBeNull();
  });

  it("gives the map and the range back together", () => {
    useKiosk.getState().showPhoto(makePhoto({ date_from: "1932-01-01" }));
    useKiosk.getState().releaseFocus();

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
    expect(useKiosk.getState().focus).toBeNull();
  });

  it("gives the original range back after two contributions", () => {
    // The thank-you timer is reset on the second contribution. If the second call remembered the
    // range of the first focus, the visitor would get a decade back at the end that they never
    // set.
    useKiosk.getState().showPhoto(makePhoto({ date_from: "1932-01-01" }));
    useKiosk.getState().showPhoto(makePhoto({ id: 2, date_from: "1975-01-01" }));
    useKiosk.getState().releaseFocus();

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
  });

  it("does not let a photo without a place move the view", () => {
    useKiosk.getState().showPhoto(makePhoto({ lat: null, lon: null, date_from: "1932-01-01" }));

    expect(useKiosk.getState().focus).toBeNull();
    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
  });
});
