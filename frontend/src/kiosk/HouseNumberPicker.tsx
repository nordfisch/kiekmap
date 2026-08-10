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

import { type ReactNode, useMemo, useState } from "react";

import type { Place } from "../api/client";
import { t } from "../text/de";
import { type NumberBlock, blocksOf, groupByBase } from "./houseNumbers";
import { BackIcon } from "./icons";

export function HouseNumberPicker({
  street,
  numbers,
  disabled,
  onPick,
  children,
}: {
  street: string;
  numbers: Place[];
  disabled: boolean;
  onPick: (place: Place) => void;
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
