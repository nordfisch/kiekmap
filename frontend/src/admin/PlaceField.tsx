/**
 * Pick a place from the gazetteer.
 *
 * Used by the photo editor and by the batch upload, which is the reason it is its own component.
 * Behind it is the OpenStreetMap index that `make places` builds -- it works without internet,
 * and it finds the "Mühlenweg" when someone types "muhlenweg".
 */

import { useEffect, useId, useState } from "react";

import { type Place, searchPlaces } from "../api/client";
import { t } from "../text/de";

const DEBOUNCE_MS = 250;
const MIN_QUERY = 2;

export type PickedPlace = { lat: number; lon: number; name: string };

export function PlaceField({
  value,
  onPick,
  onClear,
}: {
  value: PickedPlace | null;
  onPick: (place: PickedPlace) => void;
  onClear: () => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Place[]>([]);
  // The upload table shows one of these per row, so the id cannot be a constant.
  const fieldId = useId();

  useEffect(() => {
    if (query.trim().length < MIN_QUERY) {
      setResults([]);
      return;
    }
    const abort = new AbortController();
    const timer = setTimeout(() => {
      searchPlaces(query, abort.signal)
        .then(setResults)
        .catch(() => {
          /* A failed search leaves the list as it was -- the coordinate fields still work. */
        });
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [query]);

  function pick(place: Place) {
    onPick({ lat: place.lat, lon: place.lon, name: place.name });
    setQuery("");
    setResults([]);
  }

  return (
    <div className="place-field">
      {value && (
        <p className="place-field__current">
          <span>{value.name || `${value.lat.toFixed(5)}, ${value.lon.toFixed(5)}`}</span>
          <button type="button" className="link-button" onClick={onClear}>
            {t.admin.editor.clearLocation}
          </button>
        </p>
      )}

      <label className="field__label" htmlFor={fieldId}>
        {t.admin.editor.placeSearch}
      </label>
      <input
        id={fieldId}
        className="field__input"
        type="search"
        value={query}
        placeholder={t.location.searchPlaceholder}
        onChange={(event) => setQuery(event.target.value)}
      />

      {results.length > 0 && (
        <ul className="place-field__results">
          {results.map((place) => (
            <li key={place.id}>
              <button type="button" className="place-field__result" onClick={() => pick(place)}>
                <span>{place.name}</span>
                <span className="place-field__kind">
                  {t.location.kinds[place.kind] ?? place.kind}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
