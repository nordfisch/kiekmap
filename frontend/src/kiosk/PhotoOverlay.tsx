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
  const openPhotoId = useKiosk((s) => s.openPhotoId);
  const openPhoto = useKiosk((s) => s.openPhoto);
  const [detail, setDetail] = useState<PhotoDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

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
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openPhotoId, openPhoto]);

  if (openPhotoId === null) return null;

  const close = () => openPhoto(null);

  return (
    <div
      className="overlay"
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
