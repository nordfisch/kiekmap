/**
 * "Where is this?" -- locating a photo by a visitor.
 *
 * Two routes, because people who know the village differ: whoever recognises the spot on the map
 * taps it directly. Whoever knows the street name but cannot find the spot types it. Both lead to
 * the same pin, which can still be dragged afterwards.
 */

import { useEffect, useState } from "react";

import { type Place, searchPlaces } from "../api/client";
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
    setPin({ lat: place.lat, lon: place.lon }, place.name);
    setQuery("");
    setResults([]);
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
