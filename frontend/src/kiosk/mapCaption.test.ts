import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { captionOf } from "./mapCaption";

function foto(felder: Partial<PhotoMarker>): PhotoMarker {
  return {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    title: null,
    place_name: null,
    date_label: "Jahr unbekannt",
    date_short: "",
    width: 100,
    height: 80,
    thumb_url: "/api/photos/1/thumb",
    ...felder,
  };
}

describe("Was unter einem Vorschaubild steht", () => {
  it("nimmt den Titel vor der Adresse", () => {
    /**
     * Die Umkehrung vom 12. August 2026. Bis dahin stand dort die Adresse — und zwar zu Recht,
     * weil die Titel damals Adressen *waren*. Seit sie aufgeräumt sind, sagt „Gasthof Timm"
     * mehr als „Hauptstraße 11a".
     */
    const zeile = captionOf([foto({ title: "Gasthof Timm", place_name: "Hauptstraße 11a" })]);

    expect(zeile).toBe("Gasthof Timm");
  });

  it("faellt ohne Titel auf die Adresse zurueck", () => {
    expect(captionOf([foto({ place_name: "Lehmweg 17b" })])).toBe("Lehmweg 17b");
  });

  it("schreibt bei unbekannter Hausnummer ein Fragezeichen", () => {
    /**
     * Die Luecke wird benannt, nicht verschwiegen — dieselbe Haltung wie beim Nichtstreuen der
     * Stapel (decisions.md, Punkt 33). Genau danach fragt der Beitragsbereich unter „Welche
     * Hausnummer?", und auf der Karte steht, wo die Frage noch offen ist.
     */
    expect(captionOf([foto({ place_name: "Hauptstraße" })])).toBe("Hauptstraße Nr. ?");
  });

  it("haengt das Jahr mit einem Gedankenstrich an", () => {
    expect(captionOf([foto({ title: "Funkmast", date_short: "2018" })])).toBe("Funkmast — 2018");
  });

  it("laesst den Gedankenstrich weg, wo kein Jahr bekannt ist", () => {
    // Zwei Drittel des Bestands. Ein angehaengtes „Jahr unbekannt" saehe siebenhundertmal gleich
    // aus und sagte nichts.
    expect(captionOf([foto({ title: "Funkmast" })])).toBe("Funkmast");
  });

  it("traegt die Zeile notfalls mit dem Jahr allein", () => {
    // Ein nur ueber EXIF verortetes Foto hat weder Titel noch Adresse.
    expect(captionOf([foto({ date_short: "2014" })])).toBe("2014");
  });

  it("bleibt leer, wenn nichts bekannt ist", () => {
    // Und nicht etwa ein Gedankenstrich oder eine Fehlanzeige: Die Zeile faellt ganz weg.
    expect(captionOf([foto({})])).toBe("");
  });
});

describe("Was ueber einem Stapel steht", () => {
  it("nennt den Titel nur, wenn alle Fotos ihn teilen", () => {
    const zeile = captionOf([
      foto({ title: "Jagdhaus", place_name: "Lehmweg" }),
      foto({ title: "Jagdhaus", place_name: "Lehmweg" }),
    ]);

    expect(zeile).toBe("Jagdhaus");
  });

  it("faellt bei verschiedenen Titeln auf die gemeinsame Adresse zurueck", () => {
    /**
     * Der stille Fehler, den diese Regel verhindert: Fotos landen auf einem Marker, weil sie eine
     * Koordinate teilen — ihre Adresse teilen sie damit meist, ihre Titel selten. Den obersten zu
     * nehmen hiesse, „Gasthof Timm" ueber fuenfzig Bilder zu schreiben, die etwas anderes
     * zeigen.
     */
    const zeile = captionOf([
      foto({ title: "Gasthof Timm", place_name: "Hauptstraße 11a" }),
      foto({ title: "Bäckerei Petersen", place_name: "Hauptstraße 11a" }),
    ]);

    expect(zeile).toBe("Hauptstraße 11a");
  });

  it("schweigt, wenn auch die Adresse nicht geteilt wird", () => {
    // Zwei ueber EXIF verortete Fotos koennen einen Meter auseinander liegen, ohne miteinander zu
    // tun zu haben.
    const zeile = captionOf([
      foto({ title: "Hof Sieveking", place_name: "Im Sande 3" }),
      foto({ title: "Hof Boysen", place_name: "Hauptstraße 29" }),
    ]);

    expect(zeile).toBe("");
  });

  it("bekommt kein Jahr", () => {
    // Fuenfzig Fotos der Schulstrasse 2 sind ueber Jahrzehnte entstanden. Das Jahr des obersten
    // stuende ueber allen.
    const zeile = captionOf([
      foto({ title: "Winter in Holm", date_short: "1985" }),
      foto({ title: "Winter in Holm", date_short: "1990" }),
    ]);

    expect(zeile).toBe("Winter in Holm");
  });
});
