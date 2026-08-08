import { describe, expect, it } from "vitest";

import { axisBounds, barHeight, clampRange, fraction, shiftRange } from "./timeAxis";

describe("Achse", () => {
  it("rundet auf volle Jahrzehnte auf", () => {
    expect(axisBounds({ from: 1923, to: 2019 }, 10)).toEqual({ min: 1920, max: 2020 });
  });

  it("rundet bei Jahresbalken auf das Jahr", () => {
    // Kein leerer Schwanz bis 2030 mehr, in dem nie etwas liegen wird -- aber ein Jahr Platz fuer
    // den Balken 2024 selbst.
    expect(axisBounds({ from: 2010, to: 2024 }, 1)).toEqual({ min: 2010, max: 2025 });
  });

  it("gibt dem letzten Balken eigene Bahn", () => {
    /**
     * Sonst faengt er genau am rechten Rand an und laeuft darueber hinaus. Bei Jahrzehnten faellt
     * es selten auf -- naemlich nur, wenn die juengste Aufnahme im letzten Jahrzehnt der Achse
     * liegt. Genau das ist im Holmer Bestand der Fall.
     */
    expect(axisBounds({ from: 1920, to: 2020 }, 10)).toEqual({ min: 1920, max: 2030 });
  });

  it("gibt einer Sammlung aus einem einzigen Jahr trotzdem eine Laenge", () => {
    // Sonst waere max === min, und jede Rechnung darauf eine Division durch null.
    expect(axisBounds({ from: 1950, to: 1950 }, 10)).toEqual({ min: 1950, max: 1960 });
    expect(axisBounds({ from: 1950, to: 1950 }, 1)).toEqual({ min: 1950, max: 1951 });
  });

  it("bleibt leer, solange kein Foto datiert ist", () => {
    expect(axisBounds(null, 1)).toBeNull();
  });
});

describe("Balkenhoehe", () => {
  it("macht wenige Fotos neben vielen sichtbar", () => {
    /**
     * Der Fall aus dem Holmer Bestand: 11 Fotos in den 2020ern gegen 245 in den 2010ern. Linear
     * waeren das 4,5 % -- und damit derselbe Stummel, den ein leeres Jahrzehnt bekaeme.
     */
    const klein = barHeight(11, 245);

    expect(klein).toBeGreaterThan(15);
    expect(klein).toBeLessThan(barHeight(245, 245));
  });

  it("laesst den hoechsten Balken die volle Hoehe fuellen", () => {
    expect(barHeight(245, 245)).toBe(100);
  });

  it("haelt ein einziges Foto ueber dem Sockel", () => {
    expect(barHeight(1, 245)).toBeGreaterThanOrEqual(8);
  });

  it("laesst einen leeren Balken leer", () => {
    // Nichts ist nicht wenig. Ein Sockel, wo kein Foto liegt, wuerde den Besucher hinschicken.
    expect(barHeight(0, 245)).toBe(0);
  });
});

describe("Den ganzen Zeitraum verschieben", () => {
  const achse = { min: 1900, max: 2000 };

  it("verschiebt beide Enden gleich weit", () => {
    expect(shiftRange({ from: 1950, to: 1960 }, 5, achse)).toEqual({ from: 1955, to: 1965 });
  });

  it("behaelt die Spanne am Anfang der Achse", () => {
    /**
     * Der Fehler, um den es geht: Klammert man jedes Ende fuer sich, schrumpft der Zeitraum beim
     * Anstossen an den Rand -- der Besucher schiebt zur Seite und sieht seinen Zeitraum enger
     * werden, ohne etwas dafuer zu koennen.
     */
    const verschoben = shiftRange({ from: 1905, to: 1925 }, -50, achse);

    expect(verschoben).toEqual({ from: 1900, to: 1920 });
    expect(verschoben.to - verschoben.from).toBe(20);
  });

  it("behaelt die Spanne am Ende der Achse", () => {
    const verschoben = shiftRange({ from: 1975, to: 1995 }, 50, achse);

    expect(verschoben).toEqual({ from: 1980, to: 2000 });
    expect(verschoben.to - verschoben.from).toBe(20);
  });

  it("laesst eine Verschiebung um null in Ruhe", () => {
    expect(shiftRange({ from: 1950, to: 1960 }, 0, achse)).toEqual({ from: 1950, to: 1960 });
  });
});

describe("Auswahl ausserhalb der Achse bleibt im Bild", () => {
  const achse = { min: 1950, max: 1960 };

  it("klammert den Anteil auf null bis eins", () => {
    // Genau der Fall, der den Auswahlbalken mit left: -300% quer ueber den Titel laufen liess.
    expect(fraction(1920, achse)).toBe(0);
    expect(fraction(2019, achse)).toBe(1);
  });

  it("rechnet dazwischen genau", () => {
    expect(fraction(1955, achse)).toBe(0.5);
  });

  it("zieht auch den Zustand in die Achse", () => {
    expect(clampRange({ from: 1920, to: 2019 }, achse)).toEqual({ from: 1950, to: 1960 });
  });

  it("laesst eine gueltige Auswahl in Ruhe", () => {
    expect(clampRange({ from: 1952, to: 1958 }, achse)).toEqual({ from: 1952, to: 1958 });
  });

  it("dreht eine verkehrt herum liegende Auswahl nicht um", () => {
    expect(clampRange({ from: 1958, to: 1952 }, achse)).toEqual({ from: 1952, to: 1958 });
  });
});
