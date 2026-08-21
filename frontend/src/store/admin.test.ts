// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/admin", () => ({
  checkSession: vi.fn(),
  onAdminActivity: vi.fn(),
  onAdminSignedOut: vi.fn(),
  setAdminToken: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

import { useAdmin } from "./admin";

/**
 * Das Ziel, mit dem jemand die Verwaltung betritt.
 *
 * Der Stift neben dem Titel in der Detailansicht setzt es; die Verwaltung liest es beim Aufbau
 * einmal und legt es sofort weg. Faellt es an einer Stelle nicht zurueck, oeffnet sich beim
 * naechsten Betreten wieder dasselbe Foto — bei jemandem, der nur die Uebersicht wollte.
 */
describe("Der Weg vom Foto in seine Bearbeitung", () => {
  beforeEach(() => {
    useAdmin.setState({ view: "kiosk", editPhotoId: null, error: null, expiresAt: null });
  });

  it("merkt sich das Foto und fragt die PIN", () => {
    useAdmin.getState().askPin(412);

    expect(useAdmin.getState().view).toBe("pin");
    expect(useAdmin.getState().editPhotoId).toBe(412);
  });

  it("bleibt ohne Ziel, wenn das Wappen die Tuer war", () => {
    // Der andere Weg hinein. Ohne diese Unterscheidung landete jeder in einem Foto.
    useAdmin.getState().askPin();

    expect(useAdmin.getState().view).toBe("pin");
    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("vergisst es bei „Zurueck zur Karte“", () => {
    useAdmin.getState().askPin(412);
    useAdmin.getState().cancelPin();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("vergisst es, wenn die Sitzung endet", () => {
    // Sonst stuende das Ziel noch, wenn spaeter jemand anders ueber das Wappen hereinkommt.
    useAdmin.getState().askPin(412);
    useAdmin.getState().dropSession();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("vergisst es, sobald die Verwaltung es aufgegriffen hat", () => {
    /**
     * Der Fall, der sonst zur Falle wird: Die Verwaltung liest das Ziel beim Aufbau und oeffnet
     * das Foto. Bliebe es stehen, legte das Schliessen des Bearbeiten-Bildschirms es sofort
     * wieder vor — und an der Fotoliste kaeme niemand mehr vorbei.
     */
    useAdmin.getState().askPin(412);
    useAdmin.getState().clearTarget();

    expect(useAdmin.getState().editPhotoId).toBeNull();
  });

  it("laesst ein zweites Ziel das erste ersetzen", () => {
    useAdmin.getState().askPin(412);
    useAdmin.getState().askPin(7);

    expect(useAdmin.getState().editPhotoId).toBe(7);
  });
});
