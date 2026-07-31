import { describe, expect, it } from "vitest";

import { MINIMUM_DECADES, offeredDecades } from "./jahrzehnte";

describe("Jahrzehnte zur Auswahl", () => {
  it("zeigt ohne datiertes Foto das Mindestfenster", () => {
    // Sonst haette ein frisch aufgesetztes Geraet ueberhaupt keinen Knopf.
    const jahrzehnte = offeredDecades(null);

    expect(jahrzehnte[0]).toBe(MINIMUM_DECADES.first);
    expect(jahrzehnte.at(-1)).toBe(MINIMUM_DECADES.last);
    expect(jahrzehnte).toHaveLength(10);
  });

  it("laesst einen Bestand innerhalb des Fensters unveraendert", () => {
    // Holm: 1920 bis 2019 -- genau das Fenster.
    expect(offeredDecades({ from: 1923, to: 2019 })).toEqual([
      1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010,
    ]);
  });

  it("engt bei schmalem Bestand nicht ein", () => {
    // Nur 1950er im Bestand -- ein Besucher muss trotzdem 1920 sagen koennen.
    expect(offeredDecades({ from: 1950, to: 1959 })).toHaveLength(10);
  });

  it("erweitert die Reihe nach vorn, sobald ein aelteres Foto datiert ist", () => {
    expect(offeredDecades({ from: 1893, to: 2019 })[0]).toBe(1890);
  });

  it("erweitert sie ebenso nach hinten", () => {
    expect(offeredDecades({ from: 1920, to: 2024 }).at(-1)).toBe(2020);
  });
});
