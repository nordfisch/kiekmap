/**
 * The photo shown full screen.
 *
 * What is shown is the 1200 px thumbnail, not the original: a scan can be 80 MB, and on a display
 * 1080 or 2160 pixels tall none of that is visible. The difference is between instant and several
 * seconds -- and in a museum a visitor gives up after two.
 *
 * It closes everywhere: tapping beside it, the button, Escape. Whoever is stuck taps somewhere,
 * and that has to lead back.
 *
 * **What is missing is answered next door, not here.** Up to three buttons stand beside the lines
 * they would change -- "Wo ist das?", "Welche Hausnummer?", "Wann war das?". A tap closes this
 * view and puts *this* photo up in the "Hilf mit" panel for *that* question.
 *
 * Until August 2026 the pickers sat here, embedded. Two reasons ended that, and the second is the
 * heavier one: the text column carried up to 37 buttons under the description -- fifteen decades
 * alone, since the timeline reaches from 1880 to 2030 -- and **the place question could not be
 * asked here at all**, because it needs the map and the map lies underneath. See decisions.md.
 */

import { useEffect, useState } from "react";

import {
  type Need,
  type PhotoDetail,
  type Place,
  fetchPhoto,
  fetchPhotoHouseNumbers,
} from "../api/client";
import { useAdmin } from "../store/admin";
import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { t } from "../text";
import { PencilIcon } from "./icons";

/**
 * How much of the hash is shown.
 *
 * Eight hex characters are four billion possibilities -- for a collection of a few thousand
 * photos that is a collision every few million, and short enough to read off a screen and type
 * into the search field. The same length git uses for the same reason.
 */
const HASH_CHARS = 8;

export function PhotoOverlay() {
  const openStack = useKiosk((s) => s.openStack);
  const openIndex = useKiosk((s) => s.openIndex);
  const openPhoto = useKiosk((s) => s.openPhoto);
  const stepInStack = useKiosk((s) => s.stepInStack);
  const [detail, setDetail] = useState<PhotoDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  /**
   * Which photo has finished loading -- and only that one gets drawn.
   *
   * The aspect ratio sits on the image as `aspect-ratio`, so the box already has its full size
   * while the file is still on its way. Without this brake an empty rectangle with a drop shadow
   * would stand there for that time -- on opening and on every step through a stack. The space
   * stays reserved regardless, otherwise the view jumps.
   */
  const [loadedId, setLoadedId] = useState<number | null>(null);
  /**
   * The house numbers this photo may be sharpened to.
   *
   * Only their **count** is used here, and only to decide whether the button appears: empty means
   * "do not offer it", and that rule lives in the backend alone. The picker itself is in the panel.
   */
  const [numbers, setNumbers] = useState<Place[]>([]);

  const askPin = useAdmin((s) => s.askPin);
  const askAbout = useContribute((s) => s.askAbout);

  const openPhotoId = openStack[openIndex] ?? null;

  useEffect(() => {
    if (openPhotoId === null) {
      setDetail(null);
      setError(null);
      return;
    }

    const abort = new AbortController();
    fetchPhoto(openPhotoId, abort.signal)
      .then(setDetail)
      .catch((e: unknown) => {
        if (abort.signal.aborted) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    return () => abort.abort();
  }, [openPhotoId]);

  /**
   * Its own request, and one for every photo opened.
   *
   * Separate from the detail above so that a slow answer here never holds up the picture -- and
   * unconditional because the condition is exactly what is being asked. Testing anything on
   * `detail` first ("only when it is street-precise") would be the backend's rule written a second
   * time, in a place that cannot see the gazetteer. Most answers are empty; on a local database
   * that costs nothing worth saving.
   */
  useEffect(() => {
    setNumbers([]);
    if (openPhotoId === null) return;

    const abort = new AbortController();
    fetchPhotoHouseNumbers(openPhotoId, abort.signal)
      .then(setNumbers)
      .catch(() => {
        /* Without the numbers the photo stands as it is -- there is nothing to report here. */
      });
    return () => abort.abort();
  }, [openPhotoId]);

  useEffect(() => {
    if (openPhotoId === null) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") openPhoto(null);
      if (event.key === "ArrowLeft") stepInStack(-1);
      if (event.key === "ArrowRight") stepInStack(1);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openPhotoId, openPhoto, stepInStack]);

  if (openPhotoId === null) return null;

  const close = () => openPhoto(null);

  /**
   * Hand this photo and this question over to the panel, and get out of the way.
   *
   * Closing is not a side effect but half the point: "Wo ist das?" is answered on the map, and the
   * map lies under this view. The other two would work without closing -- doing it differently per
   * question would be a rule nobody can see.
   */
  function branch(need: Need) {
    if (!detail) return;
    void askAbout(detail.id, need);
    close();
  }

  /** A question this photo still owes, as a button. */
  function question(need: Need) {
    return (
      <button type="button" className="button overlay__ask" onClick={() => branch(need)}>
        {t.help.ask[need]}
      </button>
    );
  }

  return (
    <div
      className={openStack.length > 1 ? "overlay overlay--stack" : "overlay"}
      role="dialog"
      aria-modal="true"
      aria-label={t.overlay.dialogLabel}
      onClick={close}
    >
      {/* Clicks inside must not close -- otherwise you cannot look at the photo without losing it.
          Beside it they do: whoever is stuck taps somewhere, and that has to lead back. */}
      <div className="overlay__content" onClick={(e) => e.stopPropagation()}>
        {/* Its own header across both columns, so the button sits where everybody looks for it:
            top right. It stood in the text column's header for a while -- that lined up, but it
            did not read like a close button. */}
        <div className="overlay__head">
          <button type="button" className="overlay__close" onClick={close}>
            <span aria-hidden="true">×</span>
            <span className="overlay__close-text">{t.overlay.close}</span>
          </button>
        </div>

        <div className="overlay__figure">
          {detail && (
            <img
              className={
                loadedId === detail.id ? "overlay__image" : "overlay__image overlay__image--loading"
              }
              src={detail.thumb_url}
              alt={detail.title ?? t.map.photoAlt}
              style={{ aspectRatio: `${detail.width} / ${detail.height}` }}
              onLoad={() => setLoadedId(detail.id)}
              // Out of the cache the image may be complete before React can attach ``onLoad`` --
              // then it would stay invisible. Setting the same value again is a no-op for React,
              // so this does not loop.
              ref={(node) => {
                if (node?.complete && node.naturalWidth > 0) setLoadedId(detail.id);
              }}
            />
          )}

          {/* Paging through the photos that lie at the same spot -- centred below the picture,
              so the buttons belong to what they change. */}
          {openStack.length > 1 && (
            <div className="overlay__pager">
              <button
                type="button"
                className="button"
                disabled={openIndex === 0}
                onClick={() => stepInStack(-1)}
              >
                {t.overlay.prev}
              </button>
              <span className="overlay__position">
                {t.overlay.position(openIndex + 1, openStack.length)}
              </span>
              <button
                type="button"
                className="button"
                disabled={openIndex === openStack.length - 1}
                onClick={() => stepInStack(1)}
              >
                {t.overlay.next}
              </button>
            </div>
          )}
        </div>

        {/* Flush with the top edge of the picture, and scrolls on its own when the text gets
            long -- rather than running off the bottom of the screen. */}
        <div className="overlay__text">
          {error && <p className="overlay__notice">{error}</p>}
          {detail && (
            <>
              {/* The title and, beside it, the way into its correction.

                  Whoever stands at the device and sees a wrong caption has no short way there
                  otherwise: open the admin area, PIN, photo list, search -- and what one would
                  search by is the very title that is wrong. See decisions.md, point 26. */}
              <div className="overlay__title-row">
                <h2 className="overlay__title">{detail.title ?? t.map.untitled}</h2>
                <button
                  type="button"
                  className="overlay__edit"
                  aria-label={t.overlay.edit}
                  title={t.overlay.edit}
                  onClick={() => askPin(detail.id)}
                >
                  <PencilIcon className="overlay__edit-icon" />
                </button>
              </div>
              {/* Each button beside the line it would change -- that is what makes it readable
                  without a caption. Only where something is actually missing: a visitor must not
                  overwrite a curated or already contributed statement, and the backend refuses it
                  anyway. */}
              <p className="overlay__year">{detail.date_label}</p>
              {detail.needs_date && question("date")}

              {detail.place_name && <p className="overlay__place">{detail.place_name}</p>}
              {detail.needs_location && question("location")}
              {/* Whether sharpening may be offered the backend decides -- an empty list means the
                  photo is house-precise already, or its street has no addresses to offer. */}
              {numbers.length > 0 && question("housenumber")}
              {detail.description && <p className="overlay__description">{detail.description}</p>}
              {detail.tags.length > 0 && (
                <ul className="overlay__tags">
                  {detail.tags.map((tag) => (
                    <li key={tag}>{tag}</li>
                  ))}
                </ul>
              )}
              {/* Last and quiet: the credit belongs to the picture, but nobody walks up to the
                  touchscreen to read it. */}
              {detail.credit && <p className="overlay__credit">{detail.credit}</p>}

              {/* Below even that, smaller still: the photo's identity independent of any
                  database. A rebuilt collection hands out new running numbers, but the same scan
                  keeps its hash -- so this names a photo without anybody having to open it. Eight
                  characters are enough to find it again, and the admin search knows them. */}
              <p className="overlay__hash">{detail.sha256.slice(0, HASH_CHARS)}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
