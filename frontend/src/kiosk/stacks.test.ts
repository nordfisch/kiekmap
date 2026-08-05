import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { groupByLocation } from "./stacks";

function marker(id: number, lat: number, lon: number): PhotoMarker {
  return {
    id,
    title: `Foto ${id}`,
    date_label: "1932",
    thumb_url: `/api/photos/${id}/thumb`,
    lat,
    lon,
    width: 100,
    height: 80,
  } as PhotoMarker;
}

describe("Fotos am selben Ort", () => {
  it("macht aus gleichen Koordinaten einen Marker", () => {
    // Der Fall vom Gasthof: acht Fotos, exakt derselbe Punkt. Ohne das Zusammenfassen liegen sie
    // uebereinander, und nur das oberste laesst sich antippen.
    const stapel = groupByLocation([
      marker(1, 53.619588, 9.6747118),
      marker(2, 53.619588, 9.6747118),
      marker(3, 53.619588, 9.6747118),
    ]);

    expect(stapel).toHaveLength(1);
    expect(stapel[0]!.photos.map((p) => p.id)).toEqual([1, 2, 3]);
  });

  it("laesst einen Meter daneben einen eigenen Marker", () => {
    // Von Hand gesetzte Punkte liegen nie exakt aufeinander -- dann ist es auch eine andere Stelle.
    const stapel = groupByLocation([
      marker(1, 53.619588, 9.6747118),
      marker(2, 53.61962, 9.6747118),
    ]);

    expect(stapel).toHaveLength(2);
  });

  it("behaelt die Reihenfolge der Liste", () => {
    // Sonst laege nicht das zuletzt bearbeitete Foto oben -- die Abfrage sortiert danach.
    const stapel = groupByLocation([
      marker(7, 53.62, 9.68),
      marker(3, 53.62, 9.68),
      marker(9, 53.63, 9.68),
    ]);

    expect(stapel[0]!.photos.map((p) => p.id)).toEqual([7, 3]);
    expect(stapel[1]!.photos.map((p) => p.id)).toEqual([9]);
  });

  it("kommt mit einer leeren Liste zurecht", () => {
    expect(groupByLocation([])).toEqual([]);
  });
});
