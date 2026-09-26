import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ADMIN_IDLE_MS, JOB_POLL_MS, watchAdminIdle } from "./leaveWhenIdle";

describe("leaving the admin area when idle", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("leaves after two quiet minutes", async () => {
    const onIdle = vi.fn();
    watchAdminIdle(new EventTarget(), async () => false, onIdle, Date.now);

    await vi.advanceTimersByTimeAsync(ADMIN_IDLE_MS + JOB_POLL_MS);

    expect(onIdle).toHaveBeenCalledOnce();
  });

  it("does not leave while a backup runs, however long it takes", async () => {
    // Leaving reloads the page in the middle of the job.
    const onIdle = vi.fn();
    watchAdminIdle(new EventTarget(), async () => true, onIdle, Date.now);

    await vi.advanceTimersByTimeAsync(10 * ADMIN_IDLE_MS);

    expect(onIdle).not.toHaveBeenCalled();
  });

  it("counts the two minutes from the end of the job, not from the last touch", async () => {
    // Otherwise a backup of ten minutes would end in an immediate reload, and the result on the
    // screen would be gone before anybody read it.
    let busy = true;
    const onIdle = vi.fn();
    watchAdminIdle(new EventTarget(), async () => busy, onIdle, Date.now);

    await vi.advanceTimersByTimeAsync(10 * ADMIN_IDLE_MS);
    busy = false;
    await vi.advanceTimersByTimeAsync(ADMIN_IDLE_MS - 2 * JOB_POLL_MS);
    expect(onIdle).not.toHaveBeenCalled();

    await vi.advanceTimersByTimeAsync(3 * JOB_POLL_MS);
    expect(onIdle).toHaveBeenCalledOnce();
  });

  it("starts again with every touch", async () => {
    const target = new EventTarget();
    const onIdle = vi.fn();
    watchAdminIdle(target, async () => false, onIdle, Date.now);

    await vi.advanceTimersByTimeAsync(ADMIN_IDLE_MS - JOB_POLL_MS);
    target.dispatchEvent(new Event("pointerdown"));
    await vi.advanceTimersByTimeAsync(ADMIN_IDLE_MS - JOB_POLL_MS);

    expect(onIdle).not.toHaveBeenCalled();
  });

  it("does not hold on to a failed question", async () => {
    // A backend that cannot answer is no running job. Staying open for that reason would keep the
    // admin area on the screen for as long as the backend is down.
    const onIdle = vi.fn();
    watchAdminIdle(
      new EventTarget(),
      async () => {
        throw new Error("down");
      },
      onIdle,
      Date.now,
    );

    await vi.advanceTimersByTimeAsync(ADMIN_IDLE_MS + JOB_POLL_MS);

    expect(onIdle).toHaveBeenCalledOnce();
  });
});
