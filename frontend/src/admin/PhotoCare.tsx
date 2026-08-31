/**
 * The photo list with its editor.
 *
 * Newest import at the top, because that is what someone is looking for right after an upload.
 *
 * "Ohne Ort" and "Ohne Jahr" are the actual working views -- the lists a volunteer goes through
 * on a winter afternoon. Kept apart because locating and dating are two different jobs: whoever
 * is matching street names is in a different frame of mind from somebody estimating decades.
 */

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

import {
  type PhotoAdminDetail,
  type Selection,
  fetchAdminPhoto,
  fetchAdminPhotos,
  patchPhoto,
} from "../api/admin";
import { t } from "../text/de";
import { Pager } from "./Pager";
import { PhotoEditor } from "./PhotoEditor";
import { clampOffset } from "./pagination";
import { useScrollArea } from "./scrollArea";
import { useLoaded } from "./useLoaded";

// Place and year kept apart: locating and dating are two jobs, and whoever is doing one does not
// want the other in between.
const FILTERS: { value: Selection; label: string }[] = [
  { value: "all", label: t.admin.photos.filterAll },
  { value: "without_location", label: t.admin.photos.filterWithoutLocation },
  { value: "without_date", label: t.admin.photos.filterWithoutDate },
  { value: "deleted", label: t.admin.photos.filterDeleted },
];

export function PhotoCare({
  initialFilter = "all",
  openPhotoId = null,
}: {
  initialFilter?: Selection;
  /** One photo to open straight away -- the way in from the pencil in the visitor's detail view. */
  openPhotoId?: number | null;
}) {
  const [show, setShow] = useState<Selection>(initialFilter);
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [offset, setOffset] = useState(0);
  const [editing, setEditing] = useState<PhotoAdminDetail | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(query), 250);
    return () => clearTimeout(timer);
  }, [query]);

  // Changing filter or search starts over at page one. Whoever is on page 5 of "Alle" and
  // switches to "Ohne Ort" would otherwise see an empty list and think the filter was broken.
  useEffect(() => setOffset(0), [show, debounced]);

  const { data, error, loading, reload } = useLoaded(
    useCallback(() => fetchAdminPhotos(show, debounced, offset), [show, debounced, offset]),
  );

  // Working through it makes the list shorter -- whoever locates the last entry of the last page
  // would otherwise stand past the end.
  useEffect(() => {
    if (data) setOffset((current) => clampOffset(current, data.total));
  }, [data]);

  // The editor starts at the top, the list returns to where it was. What scrolls is the area
  // around both (see scrollArea.tsx); without that the form inherited the list's position and
  // opened halfway down.
  const scrollArea = useScrollArea();
  const listScroll = useRef(0);

  // Counts up as soon as a row was deleted: the effect below has to run again even though
  // `editing` did not change.
  const [restoreScroll, setRestoreScroll] = useState(0);

  useLayoutEffect(() => {
    const area = scrollArea?.current;
    if (area) area.scrollTop = editing ? 0 : listScroll.current;
  }, [editing, scrollArea, restoreScroll, data]);

  async function open(id: number) {
    listScroll.current = scrollArea?.current?.scrollTop ?? 0;
    setEditing(await fetchAdminPhoto(id));
  }

  /**
   * Opened by way of the pencil: this photo goes up before the list has even arrived.
   *
   * Runs exactly once. ``AdminApp`` holds the id for the lifetime of the area, so a second run
   * would put the photo back up the moment somebody closed it -- and there would be no way past
   * it into the list.
   */
  const [entered, setEntered] = useState(false);
  useEffect(() => {
    if (openPhotoId === null || entered) return;
    setEntered(true);
    void open(openPhotoId).catch(() => {
      /* Deleted in the meantime, or a broken link: then the plain list is the right answer. */
    });
    // ``open`` is deliberately not a dependency -- it is re-created on every render, and the
    // guard above is what limits this effect, not the list of deps.
  }, [openPhotoId, entered]);

  /* Delete and restore straight from the list, without the detour through the editor -- sorting
     out after an import goes row by row. The row then disappears from view (every filter shows
     either the deleted ones or the others), but the list stays where it stood: the next reach
     should land in the same place.

     Only deleting asks back. Restoring breaks nothing. */
  async function setDeleted(id: number, title: string | null, deleted: boolean) {
    if (
      deleted &&
      !window.confirm(t.admin.editor.deleteConfirm(title || t.admin.photos.untitled))
    ) {
      return;
    }
    const stand = scrollArea?.current?.scrollTop ?? 0;
    await patchPhoto(id, { status: deleted ? "deleted" : "published" });
    reload();
    listScroll.current = stand;
    setRestoreScroll((n) => n + 1);
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
      <h3 className="admin__heading">{t.admin.photos.title}</h3>

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
                      {photo.status === "deleted" && (
                        <span className="flag flag--muted">{t.admin.photos.deleted}</span>
                      )}
                    </span>
                  </div>
                  <div className="photo-row__actions">
                    <button type="button" className="button" onClick={() => void open(photo.id)}>
                      {t.admin.photos.edit}
                    </button>
                    {photo.status === "deleted" ? (
                      <button
                        type="button"
                        className="button button--restore"
                        onClick={() => void setDeleted(photo.id, photo.title, false)}
                      >
                        {t.admin.photos.restore}
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="button button--danger"
                        onClick={() => void setDeleted(photo.id, photo.title, true)}
                      >
                        {t.admin.photos.delete}
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <Pager total={data.total} offset={offset} onOffset={setOffset} />
        </>
      )}
    </div>
  );
}
