/**
 * The contribution panel along the right edge.
 *
 * For historical scans, place and year are nowhere in the file -- whoever knows the village often
 * knows them at a glance. This panel is therefore not a side feature but the main way the system
 * acquires data.
 */

import { useEffect, useRef } from "react";

import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { t } from "../text";
import { DateTask } from "./DateTask";
import { HouseNumberTask } from "./HouseNumberTask";
import { LocationTask } from "./LocationTask";
import { SkipIcon } from "./icons";

export function HelpPanel() {
  const need = useContribute((s) => s.need);
  const task = useContribute((s) => s.task);
  const loading = useContribute((s) => s.loading);
  const error = useContribute((s) => s.error);
  const thanks = useContribute((s) => s.thanks);
  const load = useContribute((s) => s.load);
  const skip = useContribute((s) => s.skip);

  useEffect(() => {
    void load();
  }, [load]);

  const photo = task?.photo ?? null;

  // Back to the top on every change: new photo, other question, thank-you. Otherwise the panel
  // would stay where the last finger pushed it -- and the new question would stand off-screen.
  // The intermediate steps of one task ("Andere Strasse") leave it alone: there the eye stays in
  // the same place anyway.
  const panel = useRef<HTMLElement>(null);
  useEffect(() => {
    panel.current?.scrollTo({ top: 0 });
  }, [photo?.id, need, thanks]);

  return (
    <aside className="help-panel" ref={panel}>
      <h2 className="help-panel__title">{t.help.title}</h2>

      {thanks ? (
        <div className="help-panel__thanks">
          <span className="help-panel__check" aria-hidden="true">
            ✓
          </span>
          <p>{thanks}</p>
        </div>
      ) : !photo ? (
        <p className="help-panel__empty">
          {loading ? t.timeline.loading : error ? error : t.help.allComplete}
        </p>
      ) : (
        <>
          <p className="help-panel__question">{t.help.ask[need]}</p>

          {/* Looking closer is what somebody does before saying where it was -- on a
              160 px wide picture a farmstead is barely recognisable. The same route as tapping a
              marker, including closing by tapping beside it, by button or by Escape. */}
          <button
            type="button"
            className="help-panel__zoom"
            aria-label={t.help.enlarge}
            onClick={() => useKiosk.getState().openPhoto(photo.id)}
          >
            <img
              className="help-panel__image"
              src={photo.thumb_url}
              alt={photo.title ?? t.help.photoAlt}
              style={{ aspectRatio: `${photo.width} / ${photo.height}` }}
            />
          </button>

          <div className="help-panel__known">
            {photo.title && <span className="help-panel__photo-title">{photo.title}</span>}
            {/* What is already known helps with recognition -- a year narrows the possibilities
                considerably. */}
            {need === "location" && !photo.needs_date && <span>{photo.date_label}</span>}
            {need === "date" && photo.place_name && <span>{photo.place_name}</span>}
            {/* The street belongs above the numbers, not here: `HouseNumberPicker` puts it into
                the question itself ("Am Kamp — welche Hausnummer?"). Twice would be twice. */}
            {need === "housenumber" && !photo.needs_date && <span>{photo.date_label}</span>}
          </div>

          {error && <p className="help-panel__error">{error}</p>}

          {need === "location" && <LocationTask />}
          {need === "date" && <DateTask />}
          {need === "housenumber" && <HouseNumberTask />}

          {/* Set apart from everything above it, by a rule and by its arrow: this is the one
              button here that puts the photo away instead of staying with it. It used to look
              exactly like "Anderer Buchstabe", which stays.

              If this is the last open task, "Weiss ich nicht" leads nowhere -- the same photo
              would come back. Then the button is better not there at all. */}
          {task && (task.open_count > 1 || task.open_other > 0) && (
            <button type="button" className="button button--skip help-panel__next" onClick={skip}>
              <SkipIcon />
              {t.help.next}
            </button>
          )}

          {task && task.open_count > 1 && (
            <p className="help-panel__open">{t.help.stillOpen(task.open_count, need)}</p>
          )}
        </>
      )}
    </aside>
  );
}
