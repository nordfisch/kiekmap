/**
 * "When is this from?" -- dating a photo by a visitor.
 *
 * Decade first, then the year. Not out of convenience but because it matches the honest answer:
 * whoever sees an old photo mostly knows "the twenties", not "1924". A numeric keypad would demand
 * a precision nobody has -- and on a touchscreen it is awkward for older fingers anyway.
 *
 * "The whole 1920s" is therefore a full answer, not an evasion: it is stored as an interval and
 * the time filter queries for overlap.
 */

import { useState } from "react";

import { useContribute } from "../store/contribute";
import { t } from "../texte/de";

const FIRST_DECADE = 1860;
const LAST_DECADE = 1990;

const DECADES = Array.from(
  { length: (LAST_DECADE - FIRST_DECADE) / 10 + 1 },
  (_, i) => FIRST_DECADE + i * 10,
);

export function DateTask() {
  const submitDate = useContribute((s) => s.submitDate);
  const loading = useContribute((s) => s.loading);
  const [decade, setDecade] = useState<number | null>(null);

  if (decade === null) {
    return (
      <div className="task">
        <p className="task__hint">{t.date.askDecade}</p>
        <div className="decades">
          {DECADES.map((year) => (
            <button
              key={year}
              type="button"
              className="button button--year"
              onClick={() => setDecade(year)}
            >
              {year}er
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="task">
      <p className="task__hint">{t.date.askYear}</p>

      <button
        type="button"
        className="button button--primary"
        onClick={() => void submitDate(decade, "decade")}
        disabled={loading}
      >
        {t.date.wholeDecade(decade)}
      </button>

      <div className="years">
        {Array.from({ length: 10 }, (_, i) => decade + i).map((year) => (
          <button
            key={year}
            type="button"
            className="button button--year"
            onClick={() => void submitDate(year, "year")}
            disabled={loading}
          >
            {year}
          </button>
        ))}
      </div>

      <button type="button" className="button button--quiet" onClick={() => setDecade(null)}>
        {t.date.otherDecade}
      </button>
    </div>
  );
}
