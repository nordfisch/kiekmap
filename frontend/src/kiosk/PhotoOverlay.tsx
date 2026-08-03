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
  /**
   * Welches Foto fertig geladen ist — und nur das wird gezeichnet.
   *
   * Das Seitenverhältnis steht als `aspect-ratio` am Bild, die Box hat ihre volle Größe also
   * schon, während die Datei noch unterwegs ist. Ohne diese Bremse stünde in dieser Zeit ein
   * leeres Rechteck mit Schlagschatten im Bild — beim Öffnen und bei jedem Schritt durch einen
   * Stapel. Der Platz bleibt trotzdem reserviert, sonst springt die Ansicht.
   */
  const [loadedId, setLoadedId] = useState<number | null>(null);

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
      {/* Clicks inside must not close -- otherwise you cannot look at the photo without losing it.
          Beside it they do: whoever is stuck taps somewhere, and that has to lead back. */}
      <div className="overlay__content" onClick={(e) => e.stopPropagation()}>
        {/* Eigene Kopfzeile über beiden Spalten, damit der Knopf dort sitzt, wo ihn jeder sucht:
            oben rechts. Er stand eine Zeit lang in der Kopfzeile der Textspalte — das fluchtete
            zwar, las sich aber nicht wie ein Schließen-Knopf. */}
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
              // Aus dem Cache ist das Bild unter Umständen schon fertig, bevor React ``onLoad``
              // hängen kann -- dann bliebe es unsichtbar. Derselbe Wert noch einmal gesetzt ist
              // für React ein Nichtstun, das schleift also nicht.
              ref={(node) => {
                if (node?.complete && node.naturalWidth > 0) setLoadedId(detail.id);
              }}
            />
          )}

          {/* Blättern durch die Fotos, die an derselben Stelle liegen -- mittig unter dem Bild,
              damit die Knöpfe zu dem gehören, was sie wechseln. */}
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

        {/* Oben bündig mit der Oberkante des Bildes, und scrollt für sich, wenn der Text lang
            wird — statt unter den Bildschirmrand zu laufen. */}
        <div className="overlay__text">
          {error && <p className="overlay__notice">{error}</p>}
          {detail && (
            <>
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
              {/* Zuletzt und leise: Der Nachweis gehört zum Bild, aber niemand kommt an den
                  Touchscreen, um ihn zu lesen. */}
              {detail.credit && <p className="overlay__credit">{detail.credit}</p>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
