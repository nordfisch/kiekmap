/**
 * Das gross angezeigte Foto.
 *
 * Gezeigt wird die 1200-px-Vorschau, nicht das Original: ein Scan kann 80 MB haben, und auf einem
 * Display mit 1080 oder 2160 Pixeln Hoehe sieht man davon nichts. Der Unterschied ist der zwischen
 * sofort und mehreren Sekunden -- und im Museum bricht ein Besucher nach zwei Sekunden ab.
 *
 * Geschlossen wird ueberall: Tippen daneben, der Knopf, Escape. Wer nicht weiterweiss, tippt
 * irgendwohin, und das muss zurueckfuehren.
 */

import { useEffect, useState } from "react";

import { type PhotoDetail, ladeDetail } from "../api/client";
import { useKiosk } from "../store/kiosk";

export function PhotoOverlay() {
  const offenesFoto = useKiosk((s) => s.offenesFoto);
  const oeffneFoto = useKiosk((s) => s.oeffneFoto);
  const [detail, setDetail] = useState<PhotoDetail | null>(null);
  const [fehler, setFehler] = useState<string | null>(null);

  useEffect(() => {
    if (offenesFoto === null) {
      setDetail(null);
      setFehler(null);
      return;
    }

    const abbruch = new AbortController();
    ladeDetail(offenesFoto, abbruch.signal)
      .then(setDetail)
      .catch((e: unknown) => {
        if (abbruch.signal.aborted) return;
        setFehler(e instanceof Error ? e.message : String(e));
      });
    return () => abbruch.abort();
  }, [offenesFoto]);

  useEffect(() => {
    if (offenesFoto === null) return;
    function beiTaste(ereignis: KeyboardEvent) {
      if (ereignis.key === "Escape") oeffneFoto(null);
    }
    window.addEventListener("keydown", beiTaste);
    return () => window.removeEventListener("keydown", beiTaste);
  }, [offenesFoto, oeffneFoto]);

  if (offenesFoto === null) return null;

  const schliessen = () => oeffneFoto(null);

  return (
    <div
      className="overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Foto in voller Größe"
      onClick={schliessen}
    >
      <button type="button" className="overlay__schliessen" onClick={schliessen}>
        <span aria-hidden="true">×</span>
        <span className="overlay__schliessen-text">Schließen</span>
      </button>

      {fehler && <p className="overlay__hinweis">{fehler}</p>}

      {detail && (
        // Klicks auf das Bild selbst sollen nicht schliessen -- sonst kann man es nicht ansehen,
        // ohne es zu verlieren.
        <figure className="overlay__inhalt" onClick={(e) => e.stopPropagation()}>
          <img
            className="overlay__bild"
            src={detail.thumb_url}
            alt={detail.title ?? "Historisches Foto"}
            style={{ aspectRatio: `${detail.width} / ${detail.height}` }}
          />
          <figcaption className="overlay__text">
            <h2 className="overlay__titel">{detail.title ?? "Ohne Titel"}</h2>
            <p className="overlay__jahr">{detail.date_label}</p>
            {detail.place_name && <p className="overlay__ort">{detail.place_name}</p>}
            {detail.description && <p className="overlay__beschreibung">{detail.description}</p>}
            {detail.tags.length > 0 && (
              <ul className="overlay__schlagwoerter">
                {detail.tags.map((wort) => (
                  <li key={wort}>{wort}</li>
                ))}
              </ul>
            )}
          </figcaption>
        </figure>
      )}
    </div>
  );
}
