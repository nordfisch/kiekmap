import { describe, expect, it } from "vitest";

import type { PhotoMarker } from "../api/client";
import { t } from "../text/de";
import { buildIndex } from "./PhotoLayer";

let id = 0;
function foto(lat: number, lon: number): PhotoMarker {
  return {
    id: ++id,
    title: `Foto ${id}`,
    date_label: "1932",
    thumb_url: "/thumb",
    lat,
    lon,
    width: 100,
    height: 80,
  } as PhotoMarker;
}

describe("Was auf einem Kreis steht", () => {
  it("zaehlt die Fotos, nicht die Stellen", () => {
    // Ein Achterstapel und zwei Einzelbilder daneben: Der Kreis darueber muss 10 tragen, nicht 3.
    // Fuer supercluster ist ein Stapel naemlich ein einziger Punkt -- siehe stacks.ts.
    const stapel = Array.from({ length: 8 }, () => foto(53.619588, 9.6747118));
    const index = buildIndex([...stapel, foto(53.6192, 9.6684), foto(53.6193, 9.6685)]);

    const gruppen = index.getClusters([9.6, 53.57, 9.75, 53.67], 12);
    const kreis = gruppen.find((g) => "cluster" in g.properties && g.properties.cluster);

    expect(kreis, "die drei Stellen liegen bei Zoom 12 dicht genug beieinander").toBeDefined();
    expect((kreis!.properties as { photos: number }).photos).toBe(10);
  });

  it("laesst weit auseinander liegende Fotos einzeln", () => {
    const index = buildIndex([foto(53.58, 9.61), foto(53.66, 9.74)]);

    const gruppen = index.getClusters([9.5, 53.5, 9.9, 53.8], 14);

    expect(gruppen).toHaveLength(2);
    expect(gruppen.every((g) => !("cluster" in g.properties))).toBe(true);
  });
});

describe("Was unter einem Vorschaubild steht", () => {
  it("setzt Adresse und Jahr zusammen", () => {
    expect(t.map.markerCaption("Lehmweg 17b", "1953")).toBe("Lehmweg 17b — 1953");
  });

  it("laesst das Jahr weg, wo keines bekannt ist", () => {
    // Zwei Drittel des Bestands. Vorher stand hier siebenhundertmal „Jahr unbekannt" -- eine
    // Zeile, die ueber siebenhundert Bilder nichts sagt.
    expect(t.map.markerCaption("Im Sande 18", "")).toBe("Im Sande 18");
  });

  it("kommt auch ohne Adresse aus", () => {
    // Ein Foto, das nur ueber EXIF verortet ist, hat keine. Dann traegt das Jahr die Zeile allein.
    expect(t.map.markerCaption(null, "2014")).toBe("2014");
  });

  it("bleibt leer, wenn beides fehlt", () => {
    // Und nicht etwa ein Gedankenstrich oder eine Fehlanzeige: Die Zeile faellt dann ganz weg.
    expect(t.map.markerCaption(null, "")).toBe("");
  });
});
