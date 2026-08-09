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
 * **An undated photo can be dated right here.** Whoever looks at it large and knows when it was
 * should not first have to close it and hope the contribution panel puts the same photo up. It is
 * the same two-step choice as there -- decade, then year, all through buttons. A number field
 * would be a control that accepts nothing without a keyboard.
 */

import { useEffect, useMemo, useState } from "react";

import { type PhotoDetail, type Precision, fetchPhoto } from "../api/client";
import { useAdmin } from "../store/admin";
import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { t } from "../text/de";
import { DatePicker } from "./DatePicker";
import { PencilIcon } from "./icons";
import { offeredDecades } from "./decades";

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
  const [dating, setDating] = useState(false);

  const collection = useKiosk((s) => s.fullRange);
  const askPin = useAdmin((s) => s.askPin);
  const submitDateFor = useContribute((s) => s.submitDateFor);
  const decades = useMemo(() => offeredDecades(collection), [collection]);

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
   * A year for the photo currently on screen.
   *
   * The backend's answer replaces the local state -- so the year stands where "Jahr unbekannt"
   * stood a moment ago, and the buttons are gone because `needs_date` no longer holds. No more
   * feedback is needed: the change happens at exactly the spot being looked at.
   */
  async function pickDate(year: number, precision: Precision) {
    if (!detail) return;
    setDating(true);
    setError(null);
    try {
      setDetail(await submitDateFor(detail.id, year, precision));
    } catch (e) {
      // Most common case: somebody else was quicker (409). The backend phrases that kindly.
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setDating(false);
    }
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
              <p className="overlay__year">{detail.date_label}</p>
              {/* Only when nothing stands there: a visitor must not overwrite a curated or
                  already contributed date -- the backend refuses it anyway. */}
              {detail.needs_date && (
                <div className="overlay__date">
                  <DatePicker
                    decades={decades}
                    disabled={dating}
                    onPick={(y, p) => void pickDate(y, p)}
                  />
                </div>
              )}
              {detail.place_name && <p className="overlay__place">{detail.place_name}</p>}
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
