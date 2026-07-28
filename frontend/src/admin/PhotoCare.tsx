/**
 * The photo list with its editor.
 *
 * Newest import at the top, because that is what someone is looking for right after an upload.
 * The "Unvollständig" filter is the actual working view: it is the list a volunteer works
 * through on a winter afternoon.
 */

import { useCallback, useEffect, useState } from "react";

import { type Selection, fetchAdminPhoto, fetchAdminPhotos } from "../api/admin";
import type { PhotoDetail } from "../api/client";
import { t } from "../texte/de";
import { PhotoEditor } from "./PhotoEditor";
import { useLoaded } from "./useLoaded";

const FILTERS: { value: Selection; label: string }[] = [
  { value: "all", label: t.admin.photos.filterAll },
  { value: "incomplete", label: t.admin.photos.filterIncomplete },
  { value: "hidden", label: t.admin.photos.filterHidden },
];

export function PhotoCare({ initialFilter = "all" }: { initialFilter?: Selection }) {
  const [show, setShow] = useState<Selection>(initialFilter);
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [editing, setEditing] = useState<PhotoDetail | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(query), 250);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, error, loading, reload } = useLoaded(
    useCallback(() => fetchAdminPhotos(show, debounced), [show, debounced]),
  );

  async function open(id: number) {
    setEditing(await fetchAdminPhoto(id));
  }

  if (editing) {
    return (
      <PhotoEditor
        photo={editing}
        onSaved={() => {
          setEditing(null);
          reload();
        }}
        onClose={() => setEditing(null)}
      />
    );
  }

  return (
    <div className="photo-care">
      <label className="field__label" htmlFor="photo-search">
        {t.admin.photos.searchLabel}
      </label>
      <input
        id="photo-search"
        className="field__input"
        type="search"
        value={query}
        placeholder={t.admin.photos.searchPlaceholder}
        onChange={(event) => setQuery(event.target.value)}
      />

      <div className="tabs tabs--filters">
        {FILTERS.map((filter) => (
          <button
            key={filter.value}
            type="button"
            className={show === filter.value ? "tab tab--active" : "tab"}
            onClick={() => setShow(filter.value)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {error && <p className="admin__error">{error}</p>}
      {loading && !data && <p className="admin__note">{t.admin.loading}</p>}

      {data && (
        <>
          <p className="admin__note">{t.admin.photos.found(data.photos.length, data.total)}</p>
          {data.photos.length === 0 ? (
            <p className="admin__note">{t.admin.photos.none}</p>
          ) : (
            <ul className="photo-rows">
              {data.photos.map((photo) => (
                <li key={photo.id} className="photo-row">
                  <img className="photo-row__thumb" src={photo.thumb_url} alt="" />
                  <div className="photo-row__text">
                    <span className="photo-row__title">
                      {photo.title || t.admin.photos.untitled}
                    </span>
                    <span className="photo-row__meta">
                      {photo.date_label}
                      {photo.place_name ? ` · ${photo.place_name}` : ""}
                    </span>
                    <span className="photo-row__flags">
                      {photo.needs_location && (
                        <span className="flag">{t.admin.photos.missingLocation}</span>
                      )}
                      {photo.needs_date && (
                        <span className="flag">{t.admin.photos.missingDate}</span>
                      )}
                      {photo.status === "hidden" && (
                        <span className="flag flag--muted">{t.admin.photos.hidden}</span>
                      )}
                    </span>
                  </div>
                  <button type="button" className="button" onClick={() => void open(photo.id)}>
                    {t.admin.photos.edit}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
