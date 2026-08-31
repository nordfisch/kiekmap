import { afterEach, describe, expect, it, vi } from "vitest";

import { loadRegion } from "./region";

afterEach(() => {
  vi.unstubAllGlobals();
});

function antworte(status: number, koerper?: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: status >= 200 && status < 300,
      status,
      json: async () => koerper,
    })),
  );
}

describe("loadRegion", () => {
  it("liest die Regionsdefinition", async () => {
    const region = {
      name: "Musterhausen",
      bbox: [9.9, 51.4, 10.3, 51.7],
      center: [10.1, 51.55],
      defaultZoom: 13,
      minZoom: 10,
      maxZoom: 15,
    };
    antworte(200, region);

    await expect(loadRegion()).resolves.toEqual(region);
  });

  it("nennt bei fehlender Datei den Grund und den Ausweg", async () => {
    // Der haeufigste Fall bei einem frischen Clone: 'make tiles' wurde noch nicht ausgefuehrt.
    // Eine nackte Fehlermeldung wuerde hier niemandem weiterhelfen.
    antworte(404);

    await expect(loadRegion()).rejects.toThrow(/make tiles/);
  });
});
