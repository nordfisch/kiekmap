/**
 * The "Hilf mit" panel along the right edge.
 *
 * For historical scans, place and year are nowhere in the file -- whoever knows the village often
 * knows them at a glance. This panel is therefore not a side feature but the main way the system
 * acquires data.
 */

import { useEffect } from "react";

import type { Region } from "../region";
import { useContribute } from "../store/contribute";
import { t } from "../texte/de";
import { DateTask } from "./DateTask";
import { LocationTask } from "./LocationTask";

export function HelpPanel({ region }: { region: Region }) {
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

  return (
    <aside className="help-panel">
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
          <p className="help-panel__question">
            {need === "location" ? t.help.askLocation : t.help.askDate}
          </p>

          <img
            className="help-panel__image"
            src={photo.thumb_url}
            alt={photo.title ?? t.help.photoAlt}
            style={{ aspectRatio: `${photo.width} / ${photo.height}` }}
          />

          <div className="help-panel__known">
            {photo.title && <span className="help-panel__photo-title">{photo.title}</span>}
            {/* What is already known helps with recognition -- a year narrows the possibilities
                considerably. */}
            {need === "location" && !photo.needs_date && <span>{photo.date_label}</span>}
            {need === "date" && photo.place_name && <span>{photo.place_name}</span>}
          </div>

          {error && <p className="help-panel__error">{error}</p>}

          {need === "location" ? <LocationTask /> : <DateTask region={region} />}

          <button type="button" className="button button--quiet help-panel__next" onClick={skip}>
            {t.help.next}
          </button>

          {task && task.open_count > 1 && (
            <p className="help-panel__open">{t.help.stillOpen(task.open_count, need)}</p>
          )}
        </>
      )}
    </aside>
  );
}
