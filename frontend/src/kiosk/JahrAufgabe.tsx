/**
 * "Von wann ist dieses Bild?" -- Datierung durch den Besucher.
 *
 * Erst das Jahrzehnt, dann das Jahr. Nicht aus Bequemlichkeit, sondern weil es der ehrlichen
 * Antwort entspricht: Wer ein altes Foto sieht, weiß meist "die Zwanziger" und nicht "1924".
 * Eine Zahlentastatur würde eine Genauigkeit verlangen, die niemand hat -- und am Touchscreen
 * ist sie für ältere Finger ohnehin mühsam.
 *
 * Deshalb ist "Ganze 1920er Jahre" ein vollwertiges Ergebnis und kein Ausweichen: es wird als
 * Intervall gespeichert und der Zeitfilter fragt auf Überlappung ab.
 */

import { useState } from "react";

import { useHilfMit } from "../store/hilfmit";

const ERSTES_JAHRZEHNT = 1860;
const LETZTES_JAHRZEHNT = 1990;

const JAHRZEHNTE = Array.from(
  { length: (LETZTES_JAHRZEHNT - ERSTES_JAHRZEHNT) / 10 + 1 },
  (_, i) => ERSTES_JAHRZEHNT + i * 10,
);

export function JahrAufgabe() {
  const bestaetigeJahr = useHilfMit((s) => s.bestaetigeJahr);
  const laedt = useHilfMit((s) => s.laedt);
  const [jahrzehnt, setJahrzehnt] = useState<number | null>(null);

  if (jahrzehnt === null) {
    return (
      <div className="aufgabe">
        <p className="aufgabe__anleitung">Aus welchem Jahrzehnt stammt das Foto?</p>
        <div className="jahrzehnte">
          {JAHRZEHNTE.map((jahr) => (
            <button
              key={jahr}
              type="button"
              className="knopf knopf--jahr"
              onClick={() => setJahrzehnt(jahr)}
            >
              {jahr}er
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="aufgabe">
      <p className="aufgabe__anleitung">
        Wissen Sie es genauer? Sonst genügt das Jahrzehnt.
      </p>

      <button
        type="button"
        className="knopf knopf--haupt"
        onClick={() => void bestaetigeJahr(jahrzehnt, "decade")}
        disabled={laedt}
      >
        Ganze {jahrzehnt}er Jahre
      </button>

      <div className="jahre">
        {Array.from({ length: 10 }, (_, i) => jahrzehnt + i).map((jahr) => (
          <button
            key={jahr}
            type="button"
            className="knopf knopf--jahr"
            onClick={() => void bestaetigeJahr(jahr, "year")}
            disabled={laedt}
          >
            {jahr}
          </button>
        ))}
      </div>

      <button type="button" className="knopf knopf--leise" onClick={() => setJahrzehnt(null)}>
        Anderes Jahrzehnt
      </button>
    </div>
  );
}
