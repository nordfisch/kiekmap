import { describe, expect, it } from "vitest";

import { readError } from "./client";

function response(status: number, body: unknown): Response {
  return { status, json: async () => body } as unknown as Response;
}

describe("readError", () => {
  it("passes the backend's sentence on", async () => {
    expect(await readError(response(409, { detail: "Schon angegeben" }))).toBe("Schon angegeben");
  });

  it("does not put a refusal from the schema on screen as [object Object]", async () => {
    const detail = [
      {
        type: "string_too_long",
        loc: ["body", "description"],
        msg: "String should have at most 4000 characters",
        ctx: { max_length: 4000 },
      },
    ];

    const message = await readError(response(422, { detail }));

    expect(message).toContain("4000");
    expect(message).not.toContain("object");
    expect(message).not.toContain("String should");
  });

  it("names no limit where the schema refused something else", async () => {
    const detail = [{ type: "less_than_equal", loc: ["body", "lat"], ctx: { le: 90 } }];

    const message = await readError(response(422, { detail }));

    expect(message).not.toContain("object");
    expect(message).not.toContain("Zeichen");
  });

  it("falls back to the status without JSON", async () => {
    const broken = {
      status: 502,
      json: async () => {
        throw new SyntaxError("not JSON");
      },
    } as unknown as Response;

    expect(await readError(broken)).toBe("HTTP 502");
  });
});
