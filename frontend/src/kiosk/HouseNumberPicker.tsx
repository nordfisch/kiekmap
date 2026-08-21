// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Picking a house number: the block first where the street is long, then the number.
 *
 * The same shape as `DatePicker`, and for the same reason -- the grid appears in more than one
 * place. In the contribution panel it is the second step of "Wo ist das?"; in the detail view it
 * sharpens a photo that only knows its street.
 *
 * **Display only, no state from outside.** What a picked number means is the caller's business:
 * one moves a pin that has not been sent yet, the other writes to a photo straight away.
 *
 * What stays outside on purpose: "Reicht so -- die Straße genügt" and "Doch nicht -- von vorn".
 * Both are answers to the *location* question, not to this one. Where a photo is already located
 * and only being sharpened, there is nothing to decline and nothing to take back -- the way out is
 * to leave it as it is.
 */

import { type ReactNode, useEffect, useMemo, useState } from "react";

import type { Place } from "../api/client";
import { t } from "../text/de";
import { type NumberBlock, blocksOf, groupByBase } from "./houseNumbers";
import { BackIcon } from "./icons";

/** One shared empty list, so that "nothing on offer" keeps the same identity between renders. */
const NONE: Place[] = [];

export function HouseNumberPicker({
  street,
  numbers,
  disabled,
  onPick,
  onOffer,
  children,
}: {
  street: string;
  numbers: Place[];
  disabled: boolean;
  onPick: (place: Place) => void;
  /**
   * What is on the buttons right now -- for whoever wants to show it elsewhere, empty while the
   * blocks are on screen. The map layer reads it; see `HouseNumberLayer`.
   *
   * Has to be stable across renders (a store setter is), otherwise the effect below runs on every
   * one of them.
   */
  onOffer?: (numbers: Place[]) => void;
  /** Stands between the question and the buttons -- see the note in `LocationTask`. */
  children?: ReactNode;
}) {
  /** The chosen block of a long street, or null while the blocks are still on screen. */
  const [block, setBlock] = useState<NumberBlock | null>(null);

  // Grouping and splitting in one go -- both depend on the given list alone.
  const blocks = useMemo(() => blocksOf(groupByBase(numbers)), [numbers]);

  // A long street gets a block step in front -- like the decade before the year. If everything
  // fits on one page, `blocksOf` returns a single one and the step falls away.
  const shown = block ? [block] : blocks;
  const asking = !block && blocks.length > 1;

  /**
   * Nothing is offered during the block step, and that is deliberate: "1–19" written onto a
   * single house would claim something about that house.
   *
   * Cleared on the way out, so that nothing survives the step that put it there.
   */
  const offered = asking ? NONE : (shown[0]?.numbers ?? NONE);
  useEffect(() => {
    onOffer?.(offered);
    return () => onOffer?.(NONE);
  }, [onOffer, offered]);

  return (
    <>
      <p className="task__hint">
        {asking ? t.location.askArea(street) : t.location.askHouseNumber(street)}
      </p>

      {children}

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
                onClick={() => onPick(place)}
                disabled={disabled}
              >
                {place.housenumber}
              </button>
            ))}
      </div>

      {block && (
        <button type="button" className="button button--back" onClick={() => setBlock(null)}>
          <BackIcon />
          {t.location.otherArea}
        </button>
      )}
    </>
  );
}
