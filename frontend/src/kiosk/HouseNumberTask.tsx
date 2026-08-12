/**
 * "Welche Hausnummer?" -- sharpening a photo that so far only knows its street.
 *
 * Only the wiring; the visible flow lives in `HouseNumberPicker`, because the detail view shows it
 * too. What stays here is the binding that makes this place what it is -- the contribution goes to
 * the photo of the running question, with a thank-you and the chain to whatever it still lacks.
 *
 * **No way out of its own.** "Reicht so" and "Doch nicht" belong to the location question, where
 * they answer something; here the photo already has a place, and whoever cannot name the house
 * uses "Weiß ich nicht — nächstes Foto" like everywhere else.
 */

import { useEffect, useState } from "react";

import { type Place, fetchPhotoHouseNumbers } from "../api/client";
import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { HouseNumberPicker } from "./HouseNumberPicker";
import { boundsOf } from "./focus";

export function HouseNumberTask() {
  const submitHouseNumber = useContribute((s) => s.submitHouseNumber);
  const setOfferedNumbers = useContribute((s) => s.setOfferedNumbers);
  const loading = useContribute((s) => s.loading);
  const photo = useContribute((s) => s.task?.photo ?? null);
  /**
   * What the buttons currently show -- the same list the map layer draws.
   *
   * Read out of the store rather than kept here: ``HouseNumberPicker`` reports it upwards through
   * ``onOffer``, and the map layer is a different corner of the tree.
   */
  const offered = useContribute((s) => s.offeredNumbers);

  const [numbers, setNumbers] = useState<Place[]>([]);

  useEffect(() => {
    setNumbers([]);
    if (!photo) return;

    const abort = new AbortController();
    fetchPhotoHouseNumbers(photo.id, abort.signal)
      .then(setNumbers)
      .catch(() => {
        /* Then nothing is on offer -- "Weiß ich nicht" is still there. */
      });
    return () => abort.abort();
  }, [photo?.id]);

  /**
   * Take the map to what is on the buttons -- and only here.
   *
   * The other two questions leave the map alone: for "Wo ist das?" it is the answer surface, and
   * for "Wann war das?" it has nothing to do with the question. Here the answer lies on the map,
   * usually outside the viewport the visitor had. ``releaseFocus`` in ``load`` brings the old view
   * back afterwards.
   *
   * **Bound to the numbers, not to the photo**, and that is the whole fix. Going to the street
   * point looks right and is wrong on a long street: the Lehmweg has 132 addresses, its point sits
   * in the middle, and the block on the buttons lies at one end -- measured, exactly one of eleven
   * labels was in view. Following the numbers also carries the map along when somebody taps
   * "Anderer Abschnitt", where it used to stand still.
   *
   * While the block step is running, ``offered`` is empty on purpose (see ``HouseNumberPicker``):
   * nothing is written on the map then, and the street point is the honest answer.
   */
  useEffect(() => {
    const area = boundsOf(offered);
    if (area) {
      useKiosk.getState().showArea(area);
    } else if (photo?.lat != null && photo.lon != null) {
      useKiosk.getState().showLocation(photo.lat, photo.lon);
    }
  }, [offered, photo?.id, photo?.lat, photo?.lon]);

  // The street is the photo's own place name -- the backend picked this photo *because* the
  // gazetteer holds addresses under exactly that name.
  if (!photo?.place_name || numbers.length === 0) return null;

  return (
    <div className="task">
      <HouseNumberPicker
        street={photo.place_name}
        numbers={numbers}
        disabled={loading}
        onPick={(place) => void submitHouseNumber(place.id)}
        onOffer={setOfferedNumbers}
      />
    </div>
  );
}
