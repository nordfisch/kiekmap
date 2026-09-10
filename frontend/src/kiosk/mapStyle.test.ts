import { beforeAll, describe, expect, it } from "vitest";

import type { Region } from "../region";
import { setLanguage } from "../text";
import { buildStyle } from "./mapStyle";

// The module asks the browser for the origin of the sprite URL. The tests run in node.
beforeAll(() => {
  (globalThis as unknown as { window: { location: { origin: string } } }).window = {
    location: { origin: "http://localhost" },
  };
});

const HOLM: Region = {
  name: "Testdorf",
  bbox: [9.6, 53.57, 9.75, 53.66],
  center: [9.67, 53.62],
  defaultZoom: 14.8,
  minZoom: 13,
  maxZoom: 15,
};

function labelled(region: Region) {
  return buildStyle(region).layers.filter(
    (layer) => "layout" in layer && layer.layout && "text-field" in layer.layout,
  );
}

describe("the language of the map labels", () => {
  it("asks for the language the region names", () => {
    setLanguage("en");

    expect(JSON.stringify(labelled({ ...HOLM, labelLanguage: "fr" }))).toContain("name:fr");
  });

  it("falls back to the language of the interface when the region names none", () => {
    // Asserted through the *absence* of "name:de", not the presence of "name:en". Protomaps
    // coalesces the asked-for language with English, so "name:en" is in the expression whatever
    // was asked for -- an assertion on it passes against a hard-wired "de" as well and proves
    // nothing. Measured: "de" yields name:de and name:en, "en" only name:en, "fr" name:fr and
    // name:en.
    setLanguage("en");
    expect(JSON.stringify(labelled(HOLM))).not.toContain("name:de");

    setLanguage("de");
    expect(JSON.stringify(labelled(HOLM))).toContain("name:de");
  });

  it("never leaves the language out, because that is a map without a single word on it", () => {
    // The failure this test exists for: `layers()` without `lang` returns 57 layers instead of 71,
    // and not one of them carries a text field. Nothing raises, nothing logs -- the map simply
    // comes up unlabelled, which on a kiosk nobody would trace back to a missing setting.
    setLanguage("de");

    expect(labelled(HOLM).length).toBeGreaterThan(0);
    expect(labelled({ ...HOLM, labelLanguage: "fr" }).length).toBeGreaterThan(0);
  });
});
