import { describe, expect, it } from "vitest";

import type { PhotoDetail } from "../api/client";
import { boundsAround, boundsOf, rangeForPhoto } from "./focus";

const COLLECTION = { from: 1920, to: 2019 };

function photo(fields: Partial<PhotoDetail>): PhotoDetail {
  return {
    id: 1,
    title: "Test photo",
    description: null,
    date_from: null,
    date_to: null,
    date_label: "Jahr unbekannt",
    date_precision: "year",
    lat: 53.62,
    lon: 9.676,
    place_name: null,
    location_accuracy_m: null,
    title_source: null,
    date_source: null,
    location_source: null,
    exif_datetime: null,
    original_filename: "test.jpg",
    imported_at: "2026-01-01T00:00:00",
    width: 100,
    height: 80,
    tags: [],
    needs_location: false,
    ...fields,
  } as PhotoDetail;
}

describe("the range in which the photo is visible", () => {
  it("sets a year to its decade", () => {
    expect(rangeForPhoto(photo({ date_from: "1932-01-01" }), COLLECTION)).toEqual({
      from: 1930,
      to: 1939,
    });
  });

  it("opens up fully when there is no year", () => {
    // Undated photos stand on the map only while no time filter is active. Whoever has narrowed
    // the slider and then locates an undated photo would otherwise see an empty spot -- under the
    // sentence saying the photo is now on the map.
    expect(rangeForPhoto(photo({ date_from: null }), COLLECTION)).toEqual(COLLECTION);
  });

  it("leaves the view alone for a photo without a place", () => {
    // It is on no map. Moving the slider anyway would only hide other photos without anything
    // becoming visible.
    expect(
      rangeForPhoto(photo({ lat: null, lon: null, date_from: "1932-01-01" }), COLLECTION),
    ).toBeNull();
  });
});

describe("the map viewport around the point", () => {
  it("measures about a hundred metres in each direction", () => {
    const [[west, south], [east, north]] = boundsAround(53.62, 9.676);

    // 100 m of latitude are about 0.0009 degrees.
    expect((north - south) / 2).toBeCloseTo(0.0009, 4);
    // At this latitude a degree of longitude is only about 66 km, so the span is larger.
    expect((east - west) / 2).toBeGreaterThan((north - south) / 2);
  });
});

describe("the map viewport around the house numbers on offer", () => {
  it("encloses every number on offer", () => {
    const numbers = [
      { lat: 53.62, lon: 9.67 },
      { lat: 53.625, lon: 9.68 },
      { lat: 53.622, lon: 9.674 },
    ];

    const [[west, south], [east, north]] = boundsOf(numbers)!;

    // Only the enclosing, without margin: the minimum span has its own tests below.
    for (const number of numbers) {
      expect(number.lat).toBeGreaterThanOrEqual(south);
      expect(number.lat).toBeLessThanOrEqual(north);
      expect(number.lon).toBeGreaterThanOrEqual(west);
      expect(number.lon).toBeLessThanOrEqual(east);
    }
  });

  it("gives a single number some surroundings all the same", () => {
    /**
     * The silent error: a single point has no rectangle. `fitBounds` on it sets the map to a zoom
     * level where nothing is recognisable -- and the label at issue then stands alone in an empty
     * surface.
     */
    expect(boundsOf([{ lat: 53.62, lon: 9.676 }])).toEqual(boundsAround(53.62, 9.676));
  });

  it("does not turn two numbers side by side into a strip", () => {
    // Two houses on the same side of the street lie a few metres apart. Without the minimum
    // span the viewport would be a band a few metres high.
    const [[west, south], [east, north]] = boundsOf([
      { lat: 53.62, lon: 9.676 },
      { lat: 53.62, lon: 9.6765 },
    ])!;

    expect(north - south).toBeGreaterThan(0.0017);
    expect(east - west).toBeGreaterThan(north - south);
  });

  it("returns nothing without numbers", () => {
    // While choosing a block nothing stands on the map -- then the caller decides.
    expect(boundsOf([])).toBeNull();
  });
});
