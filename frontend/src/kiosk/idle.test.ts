import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { watchForIdle } from "./idle";

describe("Leerlauf-Erkennung", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  function aufbau() {
    const ziel = new EventTarget();
    const geschehen = vi.fn();
    const aufhoeren = watchForIdle(ziel, 1000, geschehen);
    return { ziel, geschehen, aufhoeren };
  }

  it("meldet sich, wenn niemand mehr da ist", () => {
    const { geschehen } = aufbau();

    vi.advanceTimersByTime(1000);

    expect(geschehen).toHaveBeenCalledTimes(1);
  });

  it("schweigt, solange jemand tippt", () => {
    const { ziel, geschehen } = aufbau();

    for (let i = 0; i < 5; i++) {
      vi.advanceTimersByTime(900);
      ziel.dispatchEvent(new Event("pointerdown"));
    }
    vi.advanceTimersByTime(900);

    expect(geschehen).not.toHaveBeenCalled();
  });

  it("meldet sich nur einmal je Ruhephase", () => {
    // Sonst setzte sich ein unberuehrtes Geraet die ganze Nacht alle fuenf Minuten zurueck --
    // jedes Mal mit einer Runde Anfragen an einen Pi, der nichts zu tun hat.
    const { geschehen } = aufbau();

    vi.advanceTimersByTime(10_000);

    expect(geschehen).toHaveBeenCalledTimes(1);
  });

  it("faengt nach der naechsten Beruehrung wieder an", () => {
    const { ziel, geschehen } = aufbau();
    vi.advanceTimersByTime(1000);

    ziel.dispatchEvent(new Event("touchstart"));
    vi.advanceTimersByTime(1000);

    expect(geschehen).toHaveBeenCalledTimes(2);
  });

  it("laesst sich eine Mausbewegung nicht als Anwesenheit verkaufen", () => {
    // Ein Touchscreen kennt kein Schweben, und ein vom Ärmel angestossener Zeiger haelt den
    // Kiosk sonst die ganze Nacht wach.
    const { ziel, geschehen } = aufbau();

    vi.advanceTimersByTime(900);
    ziel.dispatchEvent(new Event("pointermove"));
    vi.advanceTimersByTime(200);

    expect(geschehen).toHaveBeenCalledTimes(1);
  });

  it("hoert auf, wenn man sie beendet", () => {
    const { geschehen, aufhoeren } = aufbau();

    aufhoeren();
    vi.advanceTimersByTime(10_000);

    expect(geschehen).not.toHaveBeenCalled();
  });
});
