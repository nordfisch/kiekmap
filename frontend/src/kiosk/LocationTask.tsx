// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * "Where is this?" -- locating a photo by a visitor.
 *
 * Two routes, because people who know the village differ: whoever knows the street picks it from
 * buttons -- the initial first, then the street. Whoever recognises the spot but not its name
 * says so and then taps the map. Both lead to the same pin, which can still be dragged
 * afterwards.
 *
 * **Only ever one of the two is on screen.** The street route is the default; the map route has
 * to be asked for, and asking for it takes the buttons away. Side by side they got in each
 * other's way -- a stray tap on the map answered a question the visitor was still thinking about,
 * and the buttons standing behind it would throw that answer away at the next tap.
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
import { HouseNumberPicker } from "./HouseNumberPicker";
import { BackIcon, CheckIcon, CrosshairIcon } from "./icons";
import { type StreetGroup, groupStreets } from "./streetGroups";

export function LocationTask() {
  const pin = useContribute((s) => s.pin);
  const pinLabel = useContribute((s) => s.pinLabel);
  const setPin = useContribute((s) => s.setPin);
  const submitLocation = useContribute((s) => s.submitLocation);
  const loading = useContribute((s) => s.loading);
  const picking = useContribute((s) => s.pickingOnMap);
  const setPicking = useContribute((s) => s.setPickingOnMap);
  const setOfferedNumbers = useContribute((s) => s.setOfferedNumbers);
  const photoId = useContribute((s) => s.task?.photo?.id ?? null);

  /** All streets on offer. Fetched once -- a village fits in a few kilobytes. */
  const [streets, setStreets] = useState<Place[]>([]);
  /** Has that fetch finished? Until it has, an empty list means "not yet", not "none". */
  const [ready, setReady] = useState(false);
  /**
   * The groups tapped so far. Empty means the top level; every tap appends one, "Anderer
   * Buchstabe" takes the last one back.
   */
  const [trail, setTrail] = useState<StreetGroup[]>([]);
  /** The street whose house numbers are on offer, or null while none is. */
  const [street, setStreet] = useState<Place | null>(null);
  const [numbers, setNumbers] = useState<Place[]>([]);

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
        /* Without the gazetteer the map stays -- see the arming below. */
      })
      .finally(() => {
        if (!abort.signal.aborted) setReady(true);
      });
    return () => abort.abort();
  }, []);

  /**
   * No gazetteer, no second route: then the map is live from the start.
   *
   * Runs again for every photo on purpose. The store disarms the map on each new one, and without
   * the photo in the dependencies an install that never ran ``make places`` would be usable for
   * the first photo and dead for all the rest -- with a panel that says "tippen Sie die Stelle
   * bitte auf der Karte an" while nothing happens.
   */
  useEffect(() => {
    if (ready && streets.length === 0) setPicking(true);
  }, [ready, streets.length, photoId, setPicking]);

  function choosePlace(place: Place) {
    // The pin sits on the street straight away -- the further step only moves it. Whoever stops
    // here has still answered.
    setPin({ lat: place.lat, lon: place.lon }, { label: place.name, accuracyM: place.accuracy_m });
    setTrail([]);
    closeNumbers();

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
    closeNumbers();
  }

  /**
   * Close the second step. What happens to the pin is the caller's decision.
   *
   * Which block of a long street was open needs no clearing: it lives in the picker, and the
   * picker goes with the step.
   */
  function closeNumbers() {
    setStreet(null);
    setNumbers([]);
  }

  /** "Doch nicht": back to the start, with no point set. The opposite of "Reicht so". */
  function cancelStreet() {
    closeNumbers();
    setPin(null);
  }

  /**
   * Moving the pin by hand ends the house-number choice.
   *
   * Otherwise both would run side by side: the pin moved, the grid of buttons still standing, and
   * the next tap on a house number throwing the point just set away again. Dragging is the more
   * definite statement -- that is where somebody just aimed.
   *
   * Told apart by the missing label: only the place search sets one (see store/contribute.ts).
   *
   * **Two ways in, since the map has to be armed.** Dragging the pin, which stays live throughout
   * so that the promise in ``t.location.hintSet`` holds for a pin the street buttons placed. And
   * a tap after "Auf der Karte zeigen" was pressed *in this step* -- somebody who does not know
   * the number but recognises the house. Either way the number question is void afterwards: a
   * point on the map says more than a number from a list.
   */
  useEffect(() => {
    if (street && pinLabel === null) closeNumbers();
  }, [street, pinLabel]);

  // Belongs to every step: once a point stands it can be confirmed or taken back, no matter which
  // route put it there.
  const confirm = pin && (
    <div className="task__confirm">
      {pinLabel && <p className="task__chosen">{pinLabel}</p>}
      <button
        type="button"
        className="button button--primary"
        onClick={() => void submitLocation()}
        disabled={loading}
      >
        <CheckIcon />
        {t.location.confirm}
      </button>
      <button type="button" className="button button--back" onClick={() => setPin(null)}>
        <BackIcon />
        {t.location.clear}
      </button>
    </div>
  );

  /**
   * The way to the other route, above whatever is on offer -- and offered in every step.
   *
   * Above, because it is the alternative *to* the list below it; underneath it would read as the
   * last resort after scrolling past everything. And in the house-number step too, because that
   * is where it earns the most: whoever does not know the number can still point at the house.
   *
   * A plain button, not a back one: it leads towards an answer rather than away from the
   * question. In the language of the buttons here it is a choice -- which of the two routes.
   */
  const mapButton = (
    <button type="button" className="button" onClick={() => setPicking(true)}>
      <CrosshairIcon />
      {t.location.pickOnMap}
    </button>
  );

  // The map route. Nothing else is on offer while it runs -- that is the whole point of asking
  // for it; see the module docstring.
  if (picking) {
    return (
      <div className="task">
        <p className="task__hint">
          {pin
            ? t.location.hintSet
            : streets.length
              ? t.location.hintPicking
              : t.location.noStreets}
        </p>

        {confirm}

        {/* Without streets there is nowhere to go back to, and the map is the only route. Where
            there is, the wording names the step that is still standing behind this one -- the
            house numbers, unless a tap on the map has already made them beside the point. */}
        {streets.length > 0 && (
          <button type="button" className="button button--back" onClick={() => setPicking(false)}>
            <BackIcon />
            {street ? t.location.backToNumbers : t.location.backToStreets}
          </button>
        )}
      </div>
    );
  }

  // Second step: the street is set, now the number. The search steps aside meanwhile, so that
  // nothing but the numbers is on offer.
  if (street) {
    return (
      <div className="task">
        {/* The map route stands between the question and the buttons -- above the list because it
            is the alternative *to* it, and inside the picker because underneath it would read as
            the last resort after scrolling past everything. */}
        <HouseNumberPicker
          street={street.name}
          numbers={numbers}
          disabled={loading}
          onPick={chooseNumber}
          onOffer={setOfferedNumbers}
        >
          {mapButton}
        </HouseNumberPicker>

        {/* A full answer, not an evasion: not every house is in OpenStreetMap, and whoever does
            not know the number should be able to say so without hesitating. Hence the same shape
            as "Hier war das" -- and no competition, because in this step there is no other filled
            button on screen. */}
        <button type="button" className="button button--primary" onClick={closeNumbers}>
          <CheckIcon />
          {t.location.noHouseNumber}
        </button>

        {/* A way back, not an answer: it keeps nothing. The same shape as "Anderer Abschnitt"
            above it, because both stay with this photo. */}
        <button type="button" className="button button--back" onClick={cancelStreet}>
          <BackIcon />
          {t.location.cancelStreet}
        </button>
      </div>
    );
  }

  return (
    <div className="task">
      <p className="task__hint">{pin ? t.location.hintSet : t.location.hintEmpty}</p>

      {mapButton}

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
              className="button button--back"
              onClick={() => setTrail(trail.slice(0, -1))}
            >
              <BackIcon />
              {t.location.otherInitial}
            </button>
          )}
        </>
      )}

      {confirm}
    </div>
  );
}
