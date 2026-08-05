/**
 * Ein Jahr aussuchen: erst das Jahrzehnt, dann das Jahr.
 *
 * Nicht aus Bequemlichkeit so, sondern weil es der ehrlichen Antwort entspricht: Wer ein altes
 * Foto sieht, weiß meist „die Zwanziger", nicht „1924". Ein Zahlenfeld verlangte eine Genauigkeit,
 * die niemand hat -- und auf einem Touchscreen ist es für ältere Finger ohnehin mühsam.
 *
 * „Ganze 1920er Jahre" ist deshalb eine vollwertige Antwort und kein Ausweichen: Sie wird als
 * Intervall gespeichert, und der Zeitfilter fragt auf Überlappung ab.
 *
 * **Nur die Anzeige, kein Zustand von aussen.** Dasselbe Bauteil bedient zwei Stellen -- den
 * Beitragsbereich und die Detailansicht --, und beide legen etwas anderes darüber: Der eine
 * schickt den Beitrag zum Foto seiner Frage, die andere zu dem, das gerade groß zu sehen ist.
 */

import { useState } from "react";

import type { Precision } from "../api/client";
import { t } from "../text/de";

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

      <button type="button" className="button button--quiet" onClick={() => setDecade(null)}>
        {t.date.otherDecade}
      </button>
    </div>
  );
}
