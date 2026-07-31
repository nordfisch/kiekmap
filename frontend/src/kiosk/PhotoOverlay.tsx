/**
 * The photo shown full screen.
 *
 * What is shown is the 1200 px thumbnail, not the original: a scan can be 80 MB, and on a display
 * 1080 or 2160 pixels tall none of that is visible. The difference is between instant and several
 * seconds -- and in a museum a visitor gives up after two.
 *
 * It closes everywhere: tapping beside it, the button, Escape. Whoever is stuck taps somewhere,
 * and that has to lead back.
 */

import { useEffect, useState } from "react";

import { type PhotoDetail, fetchPhoto } from "../api/client";
import { useKiosk } from "../store/kiosk";
import { t } from "../texte/de";

export function PhotoOverlay() {
  const openStack = useKiosk((s) => s.openStack);
  const openIndex = useKiosk((s) => s.openIndex);
  const openPhoto = useKiosk((s) => s.openPhoto);
  const stepInStack = useKiosk((s) => s.stepInStack);
  const [detail, setDetail] = useState<PhotoDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div
      className={openStack.length > 1 ? "overlay overlay--stack" : "overlay"}
      role="dialog"
      aria-modal="true"
      aria-label={t.overlay.dialogLabel}
      onClick={close}
    >
      <button type="button" className="overlay__close" onClick={close}>
        <span aria-hidden="true">×</span>
        <span className="overlay__close-text">{t.overlay.close}</span>
      </button>

      {error && <p className="overlay__notice">{error}</p>}

      {/* Blättern durch die Fotos, die an derselben Stelle liegen. Zwei große Knöpfe am unteren
          Rand, in Daumennähe -- das Fingerfreundlichste, was das Gerät hergibt. */}
      {openStack.length > 1 && (
        <div className="overlay__pager" onClick={(e) => e.stopPropagation()}>
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

      {detail && (
        // Clicks on the image itself must not close -- otherwise you cannot look at it without
        // losing it.
        <figure className="overlay__content" onClick={(e) => e.stopPropagation()}>
          <img
            className="overlay__image"
            src={detail.thumb_url}
            alt={detail.title ?? t.map.photoAlt}
            style={{ aspectRatio: `${detail.width} / ${detail.height}` }}
          />
          <figcaption className="overlay__text">
            <h2 className="overlay__title">{detail.title ?? t.map.untitled}</h2>
            <p className="overlay__year">{detail.date_label}</p>
            {detail.place_name && <p className="overlay__place">{detail.place_name}</p>}
            {detail.description && <p className="overlay__description">{detail.description}</p>}
            {detail.tags.length > 0 && (
              <ul className="overlay__tags">
                {detail.tags.map((tag) => (
                  <li key={tag}>{tag}</li>
                ))}
              </ul>
            )}
          </figcaption>
        </figure>
      )}
    </div>
  );
}
