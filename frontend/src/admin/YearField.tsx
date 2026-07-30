/**
 * Jahreszahl und Genauigkeit, nebeneinander und gleich breit.
 *
 * Ein Bauteil für beide Stellen, an denen datiert wird: den Stapel beim Importieren und das
 * einzelne Foto im Editor. Vorher war es zweierlei — dort ein Ankreuzfeld unter der Zahl, hier
 * ein Auswahlfeld daneben, und die Regel für „Jahrzehnt" galt nur an einer der beiden Stellen.
 *
 * Die Genauigkeit ist gesperrt, solange kein Jahr dasteht: ohne Jahr gibt es nichts, dessen
 * Genauigkeit sich angeben ließe.
 */

import { useId } from "react";

import { t } from "../texte/de";
import { type Precision, type YearInput, decadeAllowed, withYear } from "./jahr";

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
          {/* Sichtbar, aber nicht wählbar: sonst würde aus einer 1934 still das Jahrzehnt 1930. */}
          <option value="decade" disabled={!decadeAllowed(value.year)}>
            {t.admin.editor.precisionDecade}
          </option>
        </select>
      </div>
    </div>
  );
}
