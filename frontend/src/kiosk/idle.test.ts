import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { watchForIdle } from "./idle";

describe("idle detection", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  function setUp() {
    const target = new EventTarget();
    const happened = vi.fn();
    const stop = watchForIdle(target, 1000, happened);
    return { target, happened, stop };
  }

  it("speaks up when nobody is there any more", () => {
    const { happened } = setUp();

    vi.advanceTimersByTime(1000);

    expect(happened).toHaveBeenCalledTimes(1);
  });

  it("stays silent while somebody is tapping", () => {
    const { target, happened } = setUp();

    for (let i = 0; i < 5; i++) {
      vi.advanceTimersByTime(900);
      target.dispatchEvent(new Event("pointerdown"));
    }
    vi.advanceTimersByTime(900);

    expect(happened).not.toHaveBeenCalled();
  });

  it("speaks up only once per quiet spell", () => {
    // Otherwise an untouched device would reset itself every five minutes all night -- each
    // time with a round of requests to a Pi that has nothing to do.
    const { happened } = setUp();

    vi.advanceTimersByTime(10_000);

    expect(happened).toHaveBeenCalledTimes(1);
  });

  it("starts again after the next touch", () => {
    const { target, happened } = setUp();
    vi.advanceTimersByTime(1000);

    target.dispatchEvent(new Event("touchstart"));
    vi.advanceTimersByTime(1000);

    expect(happened).toHaveBeenCalledTimes(2);
  });

  it("does not accept a mouse movement as presence", () => {
    // A touchscreen knows no hovering, and a pointer nudged by a sleeve would otherwise keep
    // the kiosk awake all night.
    const { target, happened } = setUp();

    vi.advanceTimersByTime(900);
    target.dispatchEvent(new Event("pointermove"));
    vi.advanceTimersByTime(200);

    expect(happened).toHaveBeenCalledTimes(1);
  });

  it("stops when it is stopped", () => {
    const { happened, stop } = setUp();

    stop();
    vi.advanceTimersByTime(10_000);

    expect(happened).not.toHaveBeenCalled();
  });
});
