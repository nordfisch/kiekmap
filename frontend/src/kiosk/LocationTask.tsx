/**
 * "Where is this?" -- locating a photo by a visitor.
 *
 * Two routes, because people who know the village differ: whoever recognises the spot on the map
 * taps it directly. Whoever knows the street but cannot find the spot picks it from buttons --
 * the initial first, then the street. Both lead to the same pin, which can still be dragged
 * afterwards.
 *
 * **Nothing here is typed.** A search box that takes nothing without a keyboard looks like a
 * broken control, and this was the only text field on the visitor's side; see decisions.md. The
 * admin area keeps its search -- there a keyboard is at hand.
 *
 * Picking a street opens a further step: which house number? The same shape as the dating, where
 * the decade comes before the year -- and for the same reason. A street of 800 m has one point,
 * so without the number every photo on it would land in the same spot. "Reicht so" is a full
 * answer, not an evasion: not every house is in OpenStreetMap, and nobody knows the number for
 * every photograph.
 */

import { useEffect, useMemo, useState } from "react";

import { type Place, fetchHouseNumbers, fetchStreets } from "../api/client";
import { useContribute } from "../store/contribute";
import { t } from "../text/de";
import { type NumberBlock, blocksOf, groupByBase } from "./houseNumbers";
import { type StreetGroup, groupStreets } from "./streetGroups";

export function LocationTask() {
  const pin = useContribute((s) => s.pin);
  const pinLabel = useContribute((s) => s.pinLabel);
  const setPin = useContribute((s) => s.setPin);
  const submitLocation = useContribute((s) => s.submitLocation);
  const loading = useContribute((s) => s.loading);

  /** All streets on offer. Fetched once -- a village fits in a few kilobytes. */
  const [streets, setStreets] = useState<Place[]>([]);
  /**
   * The groups tapped so far. Empty means the top level; every tap appends one, "Anderer
   * Buchstabe" takes the last one back.
   */
  const [trail, setTrail] = useState<StreetGroup[]>([]);
  /** The street whose house numbers are on offer, or null while none is. */
  const [street, setStreet] = useState<Place | null>(null);
  const [numbers, setNumbers] = useState<Place[]>([]);
  /** The chosen block of a long street, or null while the blocks are still on screen. */
  const [block, setBlock] = useState<NumberBlock | null>(null);

  // Grouping and splitting in one go -- both depend on the fetched list alone.
  const blocks = useMemo(() => blocksOf(groupByBase(numbers)), [numbers]);

  const atHand = trail.at(-1)?.streets ?? streets;
  // A single group means everything fits on one page -- then the step falls away, exactly as it
  // does for the house numbers.
  const groups = useMemo(() => groupStreets(atHand), [atHand]);
  const leaves = groups.length === 1;
  // Street names need a column of their own -- "Heinrich-Eschenburg-Weg" does not fit next to a
  // second one. Initials do not, so a step made purely of them stays a grid.
  const wide = leaves || groups.some((group) => group.streets.length === 1);

  useEffect(() => {
    const abort = new AbortController();
    fetchStreets(abort.signal)
      .then(setStreets)
      .catch(() => {
        /* Without the gazetteer the map stays -- the panel says so below. */
      });
    return () => abort.abort();
  }, []);

  function choosePlace(place: Place) {
    // The pin sits on the street straight away -- the further step only moves it. Whoever stops
    // here has still answered.
    setPin({ lat: place.lat, lon: place.lon }, { label: place.name, accuracyM: place.accuracy_m });
    setTrail([]);
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

  /** Close the second step. What happens to the pin is the caller's decision. */
  function closeNumbers() {
    setStreet(null);
    setNumbers([]);
    setBlock(null);
  }

  /** "Doch nicht": back to the start, with no point set. The opposite of "Reicht so". */
  function cancelStreet() {
    closeNumbers();
    setPin(null);
  }

  /**
   * A tap on the map ends the house-number choice.
   *
   * Otherwise both would run side by side: the pin moved, the grid of buttons still standing, and
   * the next tap on a house number throwing the point just set away again. A tap on the map is
   * the more definite statement -- that is where somebody just aimed.
   *
   * Told apart by the missing label: only the place search sets one (see store/contribute.ts).
   */
  useEffect(() => {
    if (street && pinLabel === null) closeNumbers();
  }, [street, pinLabel]);

  // Second step: the street is set, now the number. The search steps aside meanwhile, so that
  // nothing but the numbers is on offer.
  if (street) {
    // A long street gets a block step in front -- like the decade before the year. If everything
    // fits on one page, `blocksOf` returns a single one and the step falls away.
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

        {/* Quieter than "Reicht so", because it is not an answer but a way back -- the same
            shape as "Anderer Abschnitt" above it. */}
        <button type="button" className="button button--quiet" onClick={cancelStreet}>
          {t.location.cancelStreet}
        </button>
      </div>
    );
  }

  return (
    <div className="task">
      <p className="task__hint">
        {pin ? t.location.hintSet : streets.length ? t.location.hintEmpty : t.location.noStreets}
      </p>

      {streets.length > 0 && (
        <>
          <p className="task__hint">{leaves ? t.location.askStreet : t.location.askInitial}</p>

          <div className={wide ? "streets streets--names" : "streets"}>
            {leaves
              ? atHand.map((place) => (
                  <button
                    key={place.id}
                    type="button"
                    className="button button--street"
                    onClick={() => choosePlace(place)}
                  >
                    {place.name}
                  </button>
                ))
              : groups.map((group) =>
                  // A group holding a single street shows that street: a button reading "Ac" that
                  // leads to one name would be a step for nothing.
                  group.streets.length === 1 ? (
                    <button
                      key={group.streets[0]!.id}
                      type="button"
                      className="button button--street"
                      onClick={() => choosePlace(group.streets[0]!)}
                    >
                      {group.streets[0]!.name}
                    </button>
                  ) : (
                    <button
                      key={group.label}
                      type="button"
                      className="button button--year"
                      onClick={() => setTrail([...trail, group])}
                    >
                      {group.label}
                    </button>
                  ),
                )}
          </div>

          {trail.length > 0 && (
            <button
              type="button"
              className="button button--quiet"
              onClick={() => setTrail(trail.slice(0, -1))}
            >
              {t.location.otherInitial}
            </button>
          )}
        </>
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
