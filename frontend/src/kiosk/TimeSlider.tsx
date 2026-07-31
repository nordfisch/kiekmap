/**
 * Time range slider with two handles.
 *
 * Hand-built rather than a library, for three reasons, any one of which would suffice:
 *
 *   - The handles have to be large for fingers. A range input with a 16 px knob is unusable on a
 *     touchscreen; the grab zone here is the size of a fingertip.
 *   - The histogram sits behind the track. It shows the visitor where anything is to be found at
 *     all -- without it you are pushing blind.
 *   - Two handles on one axis driven by pointer events are manageable; bending a foreign component
 *     to all of the above would be more work than this.
 */

import {
  type PointerEvent as ReactPointerEvent,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";

import { useKiosk } from "../store/kiosk";
import { t } from "../texte/de";
import { axisBounds, fraction } from "./zeitachse";

type Handle = "start" | "end";

export function TimeSlider() {
  const histogram = useKiosk((s) => s.histogram);
  const fullRange = useKiosk((s) => s.fullRange);
  const timeRange = useKiosk((s) => s.timeRange);
  const setTimeRange = useKiosk((s) => s.setTimeRange);

  const track = useRef<HTMLDivElement>(null);

  // The handle being dragged lives in a ref, not only in state.
  //
  // Pointer events arrive faster than React re-renders: on a brisk swipe the first pointermove
  // events land before the state change is visible. A handler reading the old value discards the
  // movement -- the handle appears stuck. The ref is set synchronously; the state only drives
  // appearance.
  const draggingRef = useRef<Handle | null>(null);
  const [dragging, setDragging] = useState<Handle | null>(null);

  const bounds = useMemo(() => axisBounds(fullRange), [fullRange]);

  const yearToFraction = useCallback(
    (year: number) => (bounds ? fraction(year, bounds) : 0),
    [bounds],
  );

  const positionToYear = useCallback(
    (clientX: number): number => {
      if (!track.current || !bounds) return 0;
      const box = track.current.getBoundingClientRect();
      const fraction = Math.min(1, Math.max(0, (clientX - box.left) / box.width));
      return Math.round(bounds.min + fraction * (bounds.max - bounds.min));
    },
    [bounds],
  );

  const moveHandle = useCallback(
    (handle: Handle, clientX: number) => {
      if (!timeRange || !bounds) return;
      const year = positionToYear(clientX);
      if (handle === "start") {
        setTimeRange({ from: Math.min(year, timeRange.to), to: timeRange.to });
      } else {
        setTimeRange({ from: timeRange.from, to: Math.max(year, timeRange.from) });
      }
    },
    [timeRange, bounds, positionToYear, setTimeRange],
  );

  function onHandleDown(handle: Handle) {
    return (event: ReactPointerEvent<HTMLElement>) => {
      event.preventDefault();
      event.stopPropagation();
      // Capture the pointer: the finger may leave the handle while dragging without the movement
      // breaking off. Without it you slip out constantly on a touchscreen.
      event.currentTarget.setPointerCapture(event.pointerId);
      draggingRef.current = handle;
      setDragging(handle);
    };
  }

  function onPointerMove(event: ReactPointerEvent<HTMLElement>) {
    if (!draggingRef.current) return;
    moveHandle(draggingRef.current, event.clientX);
  }

  function onPointerUp() {
    draggingRef.current = null;
    setDragging(null);
  }

  /** Tapping the track moves the nearer handle there. */
  function onTrackDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (!timeRange || draggingRef.current) return;
    const year = positionToYear(event.clientX);
    const handle: Handle =
      Math.abs(year - timeRange.from) <= Math.abs(year - timeRange.to) ? "start" : "end";
    moveHandle(handle, event.clientX);
  }

  // Nur wenn der ganze Bestand kein datiertes Foto hat, gibt es nichts zu schieben. Ein Ausschnitt
  // ohne datierte Fotos lässt die Achse dagegen stehen und zeigt einfach keine Balken -- die
  // Ansicht springt dann nicht zwischen zwei Bauformen hin und her.
  if (!bounds || !timeRange || !histogram) {
    return (
      <div className="timeline timeline--empty">
        {histogram ? t.timeline.empty : t.timeline.loading}
      </div>
    );
  }

  const tallest = Math.max(1, ...histogram.decades.map((d) => d.count));
  const startFraction = yearToFraction(timeRange.from);
  const endFraction = yearToFraction(timeRange.to);

  return (
    <div className="timeline">
      <div className="timeline__header">
        <span className="timeline__selection">
          {timeRange.from} <span className="timeline__to">{t.timeline.to}</span> {timeRange.to}
        </span>
        {histogram.undated > 0 ? (
          <span className="timeline__undated">{t.timeline.undated(histogram.undated)}</span>
        ) : (
          // Keine Balken und auch nichts Undatiertes: hier ist schlicht nichts. Das gehört gesagt,
          // sonst wirkt die leere Achse wie ein Fehler.
          histogram.decades.length === 0 && (
            <span className="timeline__undated">{t.timeline.empty}</span>
          )
        )}
      </div>

      <div
        ref={track}
        className="timeline__track"
        onPointerDown={onTrackDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        {/* Histogram: where is anything at all? */}
        <div className="timeline__histogram" aria-hidden="true">
          {histogram.decades.map((bar) => {
            const fraction = yearToFraction(bar.decade);
            const width = 10 / (bounds.max - bounds.min);
            const inRange = bar.decade + 9 >= timeRange.from && bar.decade <= timeRange.to;
            return (
              <div
                key={bar.decade}
                className={`timeline__bar${inRange ? " timeline__bar--active" : ""}`}
                style={{
                  left: `${fraction * 100}%`,
                  width: `${width * 100}%`,
                  height: `${Math.max(6, (bar.count / tallest) * 100)}%`,
                }}
                title={`${bar.decade}er: ${bar.count}`}
              />
            );
          })}
        </div>

        <div className="timeline__rail" />
        <div
          className="timeline__selected"
          style={{ left: `${startFraction * 100}%`, right: `${(1 - endFraction) * 100}%` }}
        />

        {(["start", "end"] as const).map((handle) => (
          <div
            key={handle}
            className={`timeline__handle${dragging === handle ? " timeline__handle--active" : ""}`}
            style={{
              left: `${(handle === "start" ? startFraction : endFraction) * 100}%`,
            }}
            onPointerDown={onHandleDown(handle)}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerUp}
            role="slider"
            tabIndex={0}
            aria-label={handle === "start" ? t.timeline.startHandle : t.timeline.endHandle}
            aria-valuemin={bounds.min}
            aria-valuemax={bounds.max}
            aria-valuenow={handle === "start" ? timeRange.from : timeRange.to}
            onKeyDown={(e) => {
              const step = e.key === "ArrowLeft" ? -1 : e.key === "ArrowRight" ? 1 : 0;
              if (!step) return;
              e.preventDefault();
              const next = (handle === "start" ? timeRange.from : timeRange.to) + step;
              setTimeRange(
                handle === "start"
                  ? {
                      from: Math.max(bounds.min, Math.min(next, timeRange.to)),
                      to: timeRange.to,
                    }
                  : {
                      from: timeRange.from,
                      to: Math.min(bounds.max, Math.max(next, timeRange.from)),
                    },
              );
            }}
          />
        ))}
      </div>

      <div className="timeline__scale" aria-hidden="true">
        <span>{bounds.min}</span>
        <span>{bounds.max}</span>
      </div>
    </div>
  );
}
