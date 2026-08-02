/**
 * "Where is this?" -- locating a photo by a visitor.
 *
 * Two routes, because people who know the village differ: whoever recognises the spot on the map
 * taps it directly. Whoever knows the street name but cannot find the spot types it. Both lead to
 * the same pin, which can still be dragged afterwards.
 *
 * Picking a street opens a second step: which house number? The same shape as the dating, where
 * the decade comes before the year -- and for the same reason. A street of 800 m has one point,
 * so without the number every photo on it would land in the same spot. "Reicht so" is a full
 * answer, not an evasion: not every house is in OpenStreetMap, and nobody knows the number for
 * every photograph.
 */

import { useEffect, useMemo, useState } from "react";

import { type Place, fetchHouseNumbers, searchPlaces } from "../api/client";
import { useContribute } from "../store/contribute";
import { t } from "../texte/de";
import { type NumberBlock, blocksOf, groupByBase } from "./hausnummern";

/** How long the input has to rest before searching. */
const DEBOUNCE_MS = 200;

export function LocationTask() {
  const pin = useContribute((s) => s.pin);
  const pinLabel = useContribute((s) => s.pinLabel);
  const setPin = useContribute((s) => s.setPin);
  const submitLocation = useContribute((s) => s.submitLocation);
  const loading = useContribute((s) => s.loading);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Place[]>([]);
  /** The street whose house numbers are on offer, or null while none is. */
  const [street, setStreet] = useState<Place | null>(null);
  const [numbers, setNumbers] = useState<Place[]>([]);
  /** Der gewählte Bereich einer langen Straße, oder null, solange die Bereiche dastehen. */
  const [block, setBlock] = useState<NumberBlock | null>(null);

  // Zusammenfassen und Aufteilen in einem Zug -- beides haengt nur an der geholten Liste.
  const blocks = useMemo(() => blocksOf(groupByBase(numbers)), [numbers]);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    const abort = new AbortController();
    const timer = setTimeout(() => {
      searchPlaces(query.trim(), abort.signal)
        .then(setResults)
        .catch(() => {
          /* If the visitor keeps typing, another answer is on its way. */
        });
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [query]);

  function choosePlace(place: Place) {
    // The pin sits on the street straight away -- the second step only moves it. Whoever stops
    // here has still answered.
    setPin({ lat: place.lat, lon: place.lon }, { label: place.name, accuracyM: place.accuracy_m });
    setQuery("");
    setResults([]);
    setStreet(null);
    setNumbers([]);
    setBlock(null);

    if (place.kind !== "strasse") return;

    fetchHouseNumbers(place.id)
      .then((found) => {
        // An empty answer is ordinary: not every street has addresses in OpenStreetMap. The step
        // is then skipped rather than shown empty.
        if (found.length === 0) return;
        setStreet(place);
        setNumbers(found);
        setBlock(null);
      })
      .catch(() => {
        /* Without the numbers the street stands as the answer -- that was always allowed. */
      });
  }

  function chooseNumber(place: Place) {
    setPin({ lat: place.lat, lon: place.lon }, { label: place.name, accuracyM: place.accuracy_m });
    setStreet(null);
    setNumbers([]);
    setBlock(null);
  }

  /** Den zweiten Schritt schliessen. Was mit dem Pin geschieht, entscheidet der Aufrufer. */
  function closeNumbers() {
    setStreet(null);
    setNumbers([]);
    setBlock(null);
  }

  /** „Doch nicht": zurueck auf Anfang, ohne gesetzten Punkt. Das Gegenteil von „Reicht so". */
  function cancelStreet() {
    closeNumbers();
    setPin(null);
  }

  /**
   * Ein Tipp auf die Karte beendet die Hausnummern-Auswahl.
   *
   * Sonst liefe beides nebeneinander her: Der Pin waere versetzt, das Knopfraster stuende noch da,
   * und der naechste Tipp auf eine Hausnummer wuerfe den eben gesetzten Punkt wieder weg. Ein Tipp
   * auf die Karte ist die bestimmtere Aussage -- dort hat jemand gerade gezielt.
   *
   * Erkennbar am fehlenden Etikett: Nur die Ortssuche setzt eines (siehe store/contribute.ts).
   */
  useEffect(() => {
    if (street && pinLabel === null) closeNumbers();
  }, [street, pinLabel]);

  // Second step: the street is set, now the number. The search steps aside meanwhile, so that
  // nothing but the numbers is on offer.
  if (street) {
    // Bei einer langen Straße kommt ein Bereich davor -- wie das Jahrzehnt vor dem Jahr. Passt
    // alles auf eine Seite, gibt `blocksOf` einen einzigen zurück und der Schritt entfällt.
    const shown = block ? [block] : blocks;
    const asking = !block && blocks.length > 1;

    return (
      <div className="task">
        <p className="task__hint">
          {asking ? t.location.askArea(street.name) : t.location.askHouseNumber(street.name)}
        </p>

        <div className="housenumbers">
          {asking
            ? blocks.map((entry) => (
                <button
                  key={entry.label}
                  type="button"
                  className="button button--year"
                  onClick={() => setBlock(entry)}
                >
                  {entry.label}
                </button>
              ))
            : shown[0]?.numbers.map((place) => (
                <button
                  key={place.id}
                  type="button"
                  className="button button--year"
                  onClick={() => chooseNumber(place)}
                >
                  {place.housenumber}
                </button>
              ))}
        </div>

        {block && (
          <button type="button" className="button button--quiet" onClick={() => setBlock(null)}>
            {t.location.otherArea}
          </button>
        )}

        <button type="button" className="button" onClick={closeNumbers}>
          {t.location.noHouseNumber}
        </button>

        {/* Leiser als „Reicht so", weil es keine Antwort ist, sondern ein Rueckweg -- dieselbe
            Form wie „Anderer Abschnitt" darueber. */}
        <button type="button" className="button button--quiet" onClick={cancelStreet}>
          {t.location.cancelStreet}
        </button>
      </div>
    );
  }

  return (
    <div className="task">
      <p className="task__hint">{pin ? t.location.hintSet : t.location.hintEmpty}</p>

      <label className="search">
        <span className="search__label">{t.location.searchLabel}</span>
        <input
          className="search__field"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t.location.searchPlaceholder}
          autoComplete="off"
          spellCheck={false}
          enterKeyHint="search"
        />
      </label>

      {results.length > 0 && (
        <ul className="search__results">
          {results.map((place) => (
            <li key={place.id}>
              <button type="button" className="search__result" onClick={() => choosePlace(place)}>
                <span className="search__name">{place.name}</span>
                <span className="search__kind">{t.location.kinds[place.kind] ?? place.kind}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {pin && (
        <div className="task__confirm">
          {pinLabel && <p className="task__chosen">{pinLabel}</p>}
          <button
            type="button"
            className="button button--primary"
            onClick={() => void submitLocation()}
            disabled={loading}
          >
            {t.location.confirm}
          </button>
          <button type="button" className="button button--quiet" onClick={() => setPin(null)}>
            {t.location.clear}
          </button>
        </div>
      )}
    </div>
  );
}
