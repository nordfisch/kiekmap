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

import { useEffect, useState } from "react";

import { type Place, fetchHouseNumbers, searchPlaces } from "../api/client";
import { useContribute } from "../store/contribute";
import { t } from "../texte/de";

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

    if (place.kind !== "strasse") return;

    fetchHouseNumbers(place.id)
      .then((found) => {
        // An empty answer is ordinary: not every street has addresses in OpenStreetMap. The step
        // is then skipped rather than shown empty.
        if (found.length === 0) return;
        setStreet(place);
        setNumbers(found);
      })
      .catch(() => {
        /* Without the numbers the street stands as the answer -- that was always allowed. */
      });
  }

  function chooseNumber(place: Place) {
    setPin({ lat: place.lat, lon: place.lon }, { label: place.name, accuracyM: place.accuracy_m });
    setStreet(null);
    setNumbers([]);
  }

  function keepStreet() {
    setStreet(null);
    setNumbers([]);
  }

  // Second step: the street is set, now the number. The search steps aside meanwhile, so that
  // nothing but the numbers is on offer.
  if (street) {
    return (
      <div className="task">
        <p className="task__hint">{t.location.askHouseNumber(street.name)}</p>

        <div className="housenumbers">
          {numbers.map((place) => (
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

        <button type="button" className="button" onClick={keepStreet}>
          {t.location.noHouseNumber}
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
