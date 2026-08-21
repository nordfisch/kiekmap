// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Year and precision, side by side and equally wide.
 *
 * One component for both places where dating happens: the batch during import and the single
 * photo in the editor. It used to be two -- a checkbox under the number there, a select beside it
 * here, and the rule for "Jahrzehnt" held in only one of the two places.
 *
 * The precision is disabled while no year stands there: without a year there is nothing whose
 * precision could be stated.
 */

import { useId } from "react";

import { t } from "../text/de";
import { type Precision, type YearInput, decadeAllowed, withYear } from "./yearInput";

export function YearField({
  value,
  onChange,
}: {
  value: YearInput;
  onChange: (next: YearInput) => void;
}) {
  const id = useId();
  const hasYear = value.year.trim() !== "";

  return (
    <div className="year-field">
      <div>
        <label className="field__label" htmlFor={`${id}-year`}>
          {t.admin.editor.year}
        </label>
        <input
          id={`${id}-year`}
          className="field__input"
          type="number"
          min={1800}
          max={2100}
          value={value.year}
          onChange={(event) => onChange(withYear(value, event.target.value))}
        />
      </div>

      <div>
        <label className="field__label" htmlFor={`${id}-precision`}>
          {t.admin.editor.precision}
        </label>
        <select
          id={`${id}-precision`}
          className="field__input"
          value={value.precision}
          disabled={!hasYear}
          onChange={(event) => onChange({ ...value, precision: event.target.value as Precision })}
        >
          <option value="year">{t.admin.editor.precisionYear}</option>
          {/* Visible but not selectable: otherwise a 1934 would quietly become the decade 1930. */}
          <option value="decade" disabled={!decadeAllowed(value.year)}>
            {t.admin.editor.precisionDecade}
          </option>
        </select>
      </div>
    </div>
  );
}
