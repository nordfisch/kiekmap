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

import { useMemo, useState } from "react";

import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { t } from "../texte/de";
import { offeredDecades } from "./jahrzehnte";

export function DateTask() {
  const submitDate = useContribute((s) => s.submitDate);
  const loading = useContribute((s) => s.loading);
  const collection = useKiosk((s) => s.fullRange);
  const [decade, setDecade] = useState<number | null>(null);

  // Was zur Wahl steht, ergibt sich aus dem Bestand -- siehe kiosk/jahrzehnte.ts.
  const decades = useMemo(() => offeredDecades(collection), [collection]);

  if (decade === null) {
    return (
      <div className="task">
        <p className="task__hint">{t.date.askDecade}</p>
        <div className="decades">
          {decades.map((year) => (
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
