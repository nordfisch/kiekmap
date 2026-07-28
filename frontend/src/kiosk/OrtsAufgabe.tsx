/**
 * "Wo ist das?" -- Verortung durch den Besucher.
 *
 * Zwei Wege, weil sich Ortskundige unterscheiden: Wer die Stelle auf der Karte wiedererkennt,
 * tippt sie direkt an. Wer den Straßennamen weiß, aber nicht die Stelle findet, tippt ihn.
 * Beides führt auf denselben Pin, der sich danach noch verschieben lässt.
 */

import { useEffect, useState } from "react";

import { type Ort, sucheOrte } from "../api/client";
import { useHilfMit } from "../store/hilfmit";

/** So lange muss die Eingabe ruhen, bevor gesucht wird. */
const RUHE_MS = 200;

const ART_BESCHRIFTUNG: Record<string, string> = {
  strasse: "Straße",
  ortsteil: "Ortsteil",
  gebaeude: "Gebäude",
  natur: "Natur",
  flur: "Flur",
};

export function OrtsAufgabe() {
  const pin = useHilfMit((s) => s.pin);
  const pinName = useHilfMit((s) => s.pinName);
  const setzePin = useHilfMit((s) => s.setzePin);
  const bestaetigeOrt = useHilfMit((s) => s.bestaetigeOrt);
  const laedt = useHilfMit((s) => s.laedt);

  const [eingabe, setEingabe] = useState("");
  const [treffer, setTreffer] = useState<Ort[]>([]);

  useEffect(() => {
    if (eingabe.trim().length < 2) {
      setTreffer([]);
      return;
    }
    const abbruch = new AbortController();
    const timer = setTimeout(() => {
      sucheOrte(eingabe.trim(), abbruch.signal)
        .then(setTreffer)
        .catch(() => {
          /* Sucht der Besucher weiter, kommt gleich eine neue Antwort. */
        });
    }, RUHE_MS);

    return () => {
      clearTimeout(timer);
      abbruch.abort();
    };
  }, [eingabe]);

  function waehleOrt(ort: Ort) {
    setzePin({ lat: ort.lat, lon: ort.lon }, ort.name);
    setEingabe("");
    setTreffer([]);
  }

  return (
    <div className="aufgabe">
      <p className="aufgabe__anleitung">
        {pin
          ? "Stimmt die Stelle? Der Punkt lässt sich auf der Karte noch verschieben."
          : "Tippen Sie auf der Karte auf die Stelle — oder suchen Sie den Straßennamen."}
      </p>

      <label className="suche">
        <span className="suche__beschriftung">Straße oder Ort suchen</span>
        <input
          className="suche__feld"
          type="search"
          value={eingabe}
          onChange={(e) => setEingabe(e.target.value)}
          placeholder="z. B. Mühlenweg"
          autoComplete="off"
          spellCheck={false}
          enterKeyHint="search"
        />
      </label>

      {treffer.length > 0 && (
        <ul className="suche__treffer">
          {treffer.map((ort) => (
            <li key={ort.id}>
              <button type="button" className="suche__treffer-knopf" onClick={() => waehleOrt(ort)}>
                <span className="suche__name">{ort.name}</span>
                <span className="suche__art">{ART_BESCHRIFTUNG[ort.kind] ?? ort.kind}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {pin && (
        <div className="aufgabe__bestaetigen">
          {pinName && <p className="aufgabe__gewaehlt">{pinName}</p>}
          <button
            type="button"
            className="knopf knopf--haupt"
            onClick={() => void bestaetigeOrt()}
            disabled={laedt}
          >
            Hier war das
          </button>
          <button type="button" className="knopf knopf--leise" onClick={() => setzePin(null)}>
            Punkt entfernen
          </button>
        </div>
      )}
    </div>
  );
}
