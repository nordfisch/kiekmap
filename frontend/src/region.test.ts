import { afterEach, describe, expect, it, vi } from "vitest";

import { loadRegion } from "./region";

afterEach(() => {
  vi.unstubAllGlobals();
});

function respond(status: number, body?: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: status >= 200 && status < 300,
      status,
      json: async () => body,
    })),
  );
}

describe("loadRegion", () => {
  it("reads the region definition", async () => {
    const region = {
      name: "Musterhausen",
      bbox: [9.9, 51.4, 10.3, 51.7],
      center: [10.1, 51.55],
      defaultZoom: 13,
      minZoom: 10,
      maxZoom: 15,
    };
    respond(200, region);

    await expect(loadRegion()).resolves.toEqual(region);
  });

  it("names the reason and the way out when the file is missing", async () => {
    // The most frequent case with a fresh clone: 'make tiles' has not been run yet. A bare
    // error message would help nobody here.
    respond(404);

    await expect(loadRegion()).rejects.toThrow(/make tiles/);
  });
});
