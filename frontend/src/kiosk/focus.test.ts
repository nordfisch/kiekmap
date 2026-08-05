import { describe, expect, it } from "vitest";

import type { PhotoDetail } from "../api/client";
import { boundsAround, rangeForPhoto } from "./focus";

const BESTAND = { from: 1920, to: 2019 };

function foto(felder: Partial<PhotoDetail>): PhotoDetail {
  return {
    id: 1,
    title: "Testfoto",
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
    ...felder,
  } as PhotoDetail;
}

describe("Zeitraum, in dem das Foto zu sehen ist", () => {
  it("stellt bei einem Jahr auf dessen Jahrzehnt", () => {
    expect(rangeForPhoto(foto({ date_from: "1932-01-01" }), BESTAND)).toEqual({
      from: 1930,
      to: 1939,
    });
  });

  it("oeffnet ohne Jahr ganz", () => {
    // Undatierte Fotos stehen nur auf der Karte, solange kein Zeitfilter aktiv ist. Wer den
    // Schieber eingeengt hat und ein undatiertes Foto verortet, saehe sonst eine leere Stelle --
    // unter dem Satz, das Foto sei jetzt auf der Karte.
    expect(rangeForPhoto(foto({ date_from: null }), BESTAND)).toEqual(BESTAND);
  });

  it("laesst die Ansicht bei einem Foto ohne Ort in Ruhe", () => {
    // Es ist auf keiner Karte zu finden. Den Schieber trotzdem zu verstellen wuerde nur andere
    // Fotos ausblenden, ohne dass etwas sichtbar wird.
    expect(
      rangeForPhoto(foto({ lat: null, lon: null, date_from: "1932-01-01" }), BESTAND),
    ).toBeNull();
  });
});

describe("Kartenausschnitt um den Punkt", () => {
  it("misst rund hundert Meter in jede Richtung", () => {
    const [[west, sued], [ost, nord]] = boundsAround(53.62, 9.676);

    // 100 m Breite sind rund 0,0009 Grad.
    expect((nord - sued) / 2).toBeCloseTo(0.0009, 4);
    // In dieser Breite ist ein Grad Laenge nur etwa 66 km lang, der Abstand also groesser.
    expect((ost - west) / 2).toBeGreaterThan((nord - sued) / 2);
  });
});
