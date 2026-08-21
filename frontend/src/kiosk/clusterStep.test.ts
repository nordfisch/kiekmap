// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";

import { ENTER_MS, clusterZoom, isStepChange, stillEntering } from "./clusterStep";

describe("Die Gruppierungsstufe", () => {
  it("ist die gerundete Zoomstufe", () => {
    // Genau die Zahl, mit der `draw()` supercluster befragt -- steht sie hier anders, animiert
    // die Karte an einer anderen Stelle, als sie neu gruppiert.
    expect(clusterZoom(13.4)).toBe(13);
    expect(clusterZoom(13.5)).toBe(14);
  });
});

describe("Wann die Marker einblenden", () => {
  it("wechselt erst, wenn die gerundete Stufe kippt", () => {
    expect(isStepChange(13, 14)).toBe(true);
  });

  it("bleibt beim Verschieben ruhig", () => {
    /**
     * Der teure Fehler. Beim Wischen zeichnet `draw()` dutzende Male auf derselben Stufe; würde
     * dabei jedes Mal eingeblendet, flackerte die Karte durchgehend — auf dem Pi spürbar mehr als
     * auf dem Entwicklungsrechner.
     */
    expect(isStepChange(13, 13)).toBe(false);
  });

  it("zaehlt den ersten Aufbau nicht als Wechsel", () => {
    // Die ersten Marker sind die Karte, die erscheint, keine Umgruppierung. Sie einzublenden
    // verzögerte das Erste, was jemand ueberhaupt zu sehen bekommt.
    expect(isStepChange(null, 13)).toBe(false);
  });
});

describe("Wie lange ein Einblenden dauert", () => {
  it("nimmt einen zweiten Aufbau kurz danach mit", () => {
    /**
     * Der Fall, an dem die Animation zuerst gescheitert ist. Eine Umgruppierung ist nicht *ein*
     * Zeichnen: Direkt nach dem Zoom werden die Fotos des neuen Ausschnitts geholt, und wenn sie
     * ankommen, entstehen alle Marker neu. Gemessen lagen zwischen beiden wenige Dutzend
     * Millisekunden — der zweite Aufbau nahm die Einblendung wieder weg, weil er selbst kein
     * Stufenwechsel war.
     */
    expect(stillEntering(1000, 1000 + ENTER_MS - 1)).toBe(true);
  });

  it("ist danach vorbei", () => {
    expect(stillEntering(1000, 1000 + ENTER_MS)).toBe(false);
  });

  it("laeuft nicht, solange nichts eingeblendet wurde", () => {
    expect(stillEntering(null, 5000)).toBe(false);
  });
});
