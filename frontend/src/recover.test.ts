import { describe, expect, it } from "vitest";

import { RELOAD_COOLDOWN_MS, lastRecovery, mayReload, noteRecovery } from "./recover";

/** Ein sessionStorage aus zwei Zeilen -- der Test braucht keinen Browser. */
function speicher(inhalt: Record<string, string> = {}) {
  return {
    getItem: (schluessel: string) => inhalt[schluessel] ?? null,
    setItem: (schluessel: string, wert: string) => {
      inhalt[schluessel] = wert;
    },
  };
}

describe("Darf sich die Seite selbst neu laden?", () => {
  it("beim ersten Absturz auf jeden Fall", () => {
    expect(mayReload(null, 1_000_000)).toBe(true);
  });

  it("nicht gleich noch einmal", () => {
    // Der Fall, um dessentwillen es diese Frage gibt: Ein Absturz, der beim Laden wiederkommt,
    // liesse den Bildschirm sonst endlos flackern. Eine lesbare Meldung ist besser als das.
    expect(mayReload(1_000_000, 1_000_000 + 5_000)).toBe(false);
  });

  it("spaeter wieder", () => {
    expect(mayReload(1_000_000, 1_000_000 + RELOAD_COOLDOWN_MS + 1)).toBe(true);
  });

  it("auch wenn die Uhr rueckwaerts gesprungen ist", () => {
    // Der Pi hat keine Echtzeituhr: Nach einem Stromausfall kann seine Uhr um Jahre danebenliegen.
    // Rechnete man stur vorwaerts, waere die Selbstheilung damit dauerhaft abgeschaltet -- genau
    // der Zustand, den sie verhindern soll.
    expect(mayReload(1_000_000, 1_000_000 - 60_000)).toBe(true);
  });
});

describe("Der Vermerk ueber den letzten Neustart", () => {
  it("wird geschrieben und wiedergefunden", () => {
    const store = speicher();
    noteRecovery(store, 42_000);

    expect(lastRecovery(store)).toBe(42_000);
  });

  it("ist ohne Vermerk leer", () => {
    expect(lastRecovery(speicher())).toBeNull();
  });

  it("uebersteht einen unbrauchbaren Wert", () => {
    // Irgendwer hat im Speicher herumgeschrieben. Dann lieber einen Versuch zu viel als eine
    // Ausnahme im Fehlerfall -- das waere ein Absturz waehrend der Behandlung eines Absturzes.
    expect(lastRecovery(speicher({ "kiekmap-neustart": "gestern" }))).toBeNull();
  });

  it("uebersteht einen Speicher, der sich verweigert", () => {
    const verweigert = {
      getItem: () => {
        throw new Error("nicht verfuegbar");
      },
      setItem: () => {
        throw new Error("nicht verfuegbar");
      },
    };

    expect(lastRecovery(verweigert)).toBeNull();
    expect(() => noteRecovery(verweigert, 1)).not.toThrow();
  });
});
