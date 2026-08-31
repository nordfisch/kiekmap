/**
 * Picking a year: the decade first, then the year.
 *
 * Not out of convenience but because it matches the honest answer: whoever sees an old photo
 * usually knows "the twenties", not "1924". A number field would demand a precision nobody has --
 * and on a touchscreen it is awkward for older fingers anyway.
 *
 * "Ganze 1920er Jahre" is therefore a full answer and not a dodge: it is stored as an interval,
 * and the time filter queries on overlap.
 *
 * **Display only, no state from outside.** The same component serves two places -- the
 * contribution panel and the detail view -- and each puts something different on top: one sends
 * the contribution to the photo of its question, the other to the one currently shown large.
 */

import { useState } from "react";

import type { Precision } from "../api/client";
import { t } from "../text/de";
import { BackIcon, CheckIcon } from "./icons";

export function DatePicker({
  decades,
  disabled,
  onPick,
}: {
  decades: number[];
  disabled: boolean;
  onPick: (year: number, precision: Precision) => void;
}) {
  const [decade, setDecade] = useState<number | null>(null);

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
        onClick={() => onPick(decade, "decade")}
        disabled={disabled}
      >
        <CheckIcon />
        {t.date.wholeDecade(decade)}
      </button>

      <div className="years">
        {Array.from({ length: 10 }, (_, i) => decade + i).map((year) => (
          <button
            key={year}
            type="button"
            className="button button--year"
            onClick={() => onPick(year, "year")}
            disabled={disabled}
          >
            {year}
          </button>
        ))}
      </div>

      <button type="button" className="button button--back" onClick={() => setDecade(null)}>
        <BackIcon />
        {t.date.otherDecade}
      </button>
    </div>
  );
}
