/**
 * Time range slider, built like the trim control of a video editor.
 *
 * A continuous bar for the chosen period, a handle at each end to widen or narrow it, and the bar
 * itself to move the whole period through time. That last movement is the one visitors actually
 * want -- walking a fixed span through the decades -- and it used to cost two drags with a wrong
 * span in between.
 *
 * The bar carried a drawn grip in its middle for a while, for the case where the period is
 * squeezed onto a single bar and has no surface left to grab. It does not need one any more: the
 * period cannot be narrowed below a decade (``minSpan`` in timeAxis.ts), so there is always
 * something to take hold of. A mark on screen for a state nobody can reach is a mark too many.
 *
 * Hand-built rather than a library, for three reasons, any one of which would suffice:
 *
 *   - The handles have to be large for fingers. A range input with a 16 px knob is unusable on a
 *     touchscreen; the grab zone here is the size of a fingertip.
 *   - The histogram sits behind the track, the way the filmstrip sits behind the trimmer. It shows
 *     the visitor where anything is to be found at all -- without it you are pushing blind.
 *   - Three grips on one axis driven by pointer events are manageable; bending a foreign component
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
import { t } from "../text";
import {
  axisBounds,
  barHeight,
  fraction,
  resizeRange,
  shiftRange,
  yearAtFraction,
} from "./timeAxis";

type Grip = "start" | "end" | "range";

/** What one bar covers, in words: "2014", "1920er", "1920–1924". */
function barLabel(year: number, step: number): string {
  if (step === 1) return String(year);
  if (step === 10) return `${year}er`;
  return `${year}–${year + step - 1}`;
}

export function TimeSlider() {
  const histogram = useKiosk((s) => s.histogram);
  const fullRange = useKiosk((s) => s.fullRange);
  const timeRange = useKiosk((s) => s.timeRange);
  const setTimeRange = useKiosk((s) => s.setTimeRange);
  const showUndated = useKiosk((s) => s.showUndated);
  const setShowUndated = useKiosk((s) => s.setShowUndated);

  const track = useRef<HTMLDivElement>(null);

  // The grip being dragged lives in a ref, not only in state.
  //
  // Pointer events arrive faster than React re-renders: on a brisk swipe the first pointermove
  // events land before the state change is visible. A handler reading the old value discards the
  // movement -- the handle appears stuck. The ref is set synchronously; the state only drives
  // appearance.
  const draggingRef = useRef<Grip | null>(null);
  const [dragging, setDragging] = useState<Grip | null>(null);
  // Where the finger went down, in years. Moving the whole period works on the difference to this
  // -- otherwise the period would jump its middle under the finger on first touch.
  const grabbedAt = useRef(0);

  const step = histogram?.step ?? 10;
  const bounds = useMemo(() => axisBounds(fullRange, step), [fullRange, step]);

  const yearToFraction = useCallback(
    (year: number) => (bounds ? fraction(year, bounds) : 0),
    [bounds],
  );

  const positionToYear = useCallback(
    (clientX: number): number => {
      if (!track.current || !bounds) return 0;
      // Where the finger is, is the DOM's business; what that means is timeAxis's.
      const box = track.current.getBoundingClientRect();
      return yearAtFraction((clientX - box.left) / box.width, bounds);
    },
    [bounds],
  );

  const moveGrip = useCallback(
    (grip: Grip, clientX: number) => {
      if (!timeRange || !bounds) return;
      const year = positionToYear(clientX);

      if (grip === "range") {
        const moved = shiftRange(timeRange, year - grabbedAt.current, bounds);
        // Carry the grab point along: without it the period would creep away from the finger as
        // soon as the shift hits a limit.
        grabbedAt.current += moved.from - timeRange.from;
        setTimeRange(moved);
      } else {
        setTimeRange(resizeRange(timeRange, grip, year, step));
      }
    },
    [timeRange, bounds, step, positionToYear, setTimeRange],
  );

  function onGripDown(grip: Grip) {
    return (event: ReactPointerEvent<HTMLElement>) => {
      event.preventDefault();
      // Without this the press also reaches the track below, where it would send the nearer end
      // to the finger -- and the period would jump before it moved.
      event.stopPropagation();
      // Capture the pointer: the finger may leave the grip while dragging without the movement
      // breaking off. Without it you slip out constantly on a touchscreen.
      event.currentTarget.setPointerCapture(event.pointerId);
      grabbedAt.current = positionToYear(event.clientX);
      draggingRef.current = grip;
      setDragging(grip);
    };
  }

  function onPointerMove(event: ReactPointerEvent<HTMLElement>) {
    if (!draggingRef.current) return;
    moveGrip(draggingRef.current, event.clientX);
  }

  function onPointerUp() {
    draggingRef.current = null;
    setDragging(null);
  }

  /** Tapping the track outside the period moves the nearer end there. */
  function onTrackDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (!timeRange || draggingRef.current) return;
    const year = positionToYear(event.clientX);
    const grip: Grip =
      Math.abs(year - timeRange.from) <= Math.abs(year - timeRange.to) ? "start" : "end";
    moveGrip(grip, event.clientX);
  }

  /** Arrow keys, for the two ends and for the whole period alike. */
  function onGripKey(grip: Grip) {
    return (event: React.KeyboardEvent<HTMLElement>) => {
      if (!timeRange || !bounds) return;
      const direction = event.key === "ArrowLeft" ? -1 : event.key === "ArrowRight" ? 1 : 0;
      if (!direction) return;
      event.preventDefault();

      if (grip === "range") {
        setTimeRange(shiftRange(timeRange, direction, bounds));
      } else {
        // Same floor as dragging -- the arrow keys must not reach a period the finger cannot.
        const end = grip === "start" ? timeRange.from : timeRange.to;
        setTimeRange(resizeRange(timeRange, grip, end + direction, step));
      }
    };
  }

  // Only when the whole collection holds no dated photo is there nothing to slide. A viewport
  // without dated photos leaves the axis standing and simply shows no bars -- the view then does
  // not jump back and forth between two layouts.
  if (!bounds || !timeRange || !histogram) {
    return (
      <div className="timeline timeline--empty">
        {histogram ? t.timeline.empty : t.timeline.loading}
      </div>
    );
  }

  const tallest = Math.max(1, ...histogram.bars.map((bar) => bar.count));
  const startFraction = yearToFraction(timeRange.from);
  const endFraction = yearToFraction(timeRange.to);

  return (
    <div className="timeline">
      <div className="timeline__header">
        <span className="timeline__selection">
          {timeRange.from} <span className="timeline__to">{t.timeline.to}</span> {timeRange.to}
        </span>
        {histogram.undated > 0 ? (
          /* The count was standing here anyway; it is now the label of the switch that decides
             what happens to it. Photos without a date overlap no period, so a time range drops
             every one of them -- and until this switch existed, that was something the visitor
             found out only by watching the map empty out. */
          <button
            type="button"
            className="timeline__undated"
            onClick={() => setShowUndated(!showUndated)}
            aria-pressed={showUndated}
          >
            <span
              className={`timeline__box${showUndated ? " timeline__box--on" : ""}`}
              aria-hidden="true"
            >
              ✓
            </span>
            {t.timeline.undated(histogram.undated)}
          </button>
        ) : (
          // No bars and nothing undated either: there is simply nothing here. That needs saying,
          // or the empty axis looks like a fault.
          histogram.bars.length === 0 && (
            <span className="timeline__undated">{t.timeline.empty}</span>
          )
        )}
      </div>

      {/* Movement is followed **only** here, not on the grips as well.
       *
       * The grips capture the pointer, so its events are retargeted to them -- and bubble up to
       * here anyway. A second handler on the grip therefore ran on the same move: harmless for
       * the two ends, where moving to the same place twice changes nothing, but it undid every
       * shift of the whole period. The second call still saw the old range and put it back. */}
      <div
        ref={track}
        className="timeline__track"
        onPointerDown={onTrackDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        {/* The filmstrip: where is anything at all? */}
        <div className="timeline__histogram" aria-hidden="true">
          {histogram.bars.map((bar) => {
            const inRange = bar.year + step - 1 >= timeRange.from && bar.year <= timeRange.to;
            return (
              <div
                key={bar.year}
                className={`timeline__bar${inRange ? " timeline__bar--active" : ""}`}
                style={{
                  left: `${yearToFraction(bar.year) * 100}%`,
                  width: `${(step / (bounds.max - bounds.min)) * 100}%`,
                  height: `${barHeight(bar.count, tallest)}%`,
                }}
                title={`${barLabel(bar.year, step)}: ${bar.count}`}
              />
            );
          })}
        </div>

        <div className="timeline__rail" />

        {/* The whole period takes a grab, the way a clip does in a video editor. */}
        <div
          className={`timeline__selected${dragging === "range" ? " timeline__selected--active" : ""}`}
          style={{ left: `${startFraction * 100}%`, right: `${(1 - endFraction) * 100}%` }}
          onPointerDown={onGripDown("range")}
          role="slider"
          tabIndex={0}
          aria-label={t.timeline.rangeHandle}
          aria-valuemin={bounds.min}
          aria-valuemax={bounds.max}
          aria-valuenow={timeRange.from}
          aria-valuetext={`${timeRange.from} ${t.timeline.to} ${timeRange.to}`}
          onKeyDown={onGripKey("range")}
        />

        {(["start", "end"] as const).map((grip) => (
          <div
            key={grip}
            className={`timeline__handle${dragging === grip ? " timeline__handle--active" : ""}`}
            style={{ left: `${(grip === "start" ? startFraction : endFraction) * 100}%` }}
            onPointerDown={onGripDown(grip)}
            role="slider"
            tabIndex={0}
            aria-label={grip === "start" ? t.timeline.startHandle : t.timeline.endHandle}
            aria-valuemin={bounds.min}
            aria-valuemax={bounds.max}
            aria-valuenow={grip === "start" ? timeRange.from : timeRange.to}
            onKeyDown={onGripKey(grip)}
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
