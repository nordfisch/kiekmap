/**
 * The photo list with its editor.
 *
 * Newest import at the top, because that is what someone is looking for right after an upload.
 *
 * „Ohne Ort" und „Ohne Jahr" sind die eigentlichen Arbeitsansichten -- die Listen, die ein
 * Ehrenamtlicher an einem Winternachmittag durchgeht. Getrennt, weil Verorten und Datieren zwei
 * verschiedene Arbeiten sind: Wer Straßennamen zuordnet, ist in einem anderen Kopf als jemand,
 * der Jahrzehnte schätzt.
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

// Ort und Jahr getrennt: Verorten und Datieren sind zwei Arbeiten, und wer die eine macht, will
// die andere nicht dazwischen haben.
const FILTERS: { value: Selection; label: string }[] = [
  { value: "all", label: t.admin.photos.filterAll },
  { value: "without_location", label: t.admin.photos.filterWithoutLocation },
  { value: "without_date", label: t.admin.photos.filterWithoutDate },
  { value: "deleted", label: t.admin.photos.filterDeleted },
];

export function PhotoCare({ initialFilter = "all" }: { initialFilter?: Selection }) {
  const [show, setShow] = useState<Selection>(initialFilter);
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [offset, setOffset] = useState(0);
  const [editing, setEditing] = useState<PhotoAdminDetail | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(query), 250);
    return () => clearTimeout(timer);
  }, [query]);

  // Filter- oder Suchwechsel fängt wieder auf Seite eins an. Wer auf Seite 5 von „Alle" steht und
  // auf „Ohne Ort" umschaltet, sähe sonst eine leere Liste und hielte den Filter für kaputt.
  useEffect(() => setOffset(0), [show, debounced]);

  const { data, error, loading, reload } = useLoaded(
    useCallback(() => fetchAdminPhotos(show, debounced, offset), [show, debounced, offset]),
  );

  // Beim Abarbeiten wird die Liste kürzer -- wer den letzten Eintrag der letzten Seite verortet,
  // stünde sonst hinter dem Ende.
  useEffect(() => {
    if (data) setOffset((current) => clampOffset(current, data.total));
  }, [data]);

  // Der Editor fängt oben an, die Liste kommt an ihre Stelle zurück. Gescrollt wird der Bereich um
  // beide herum (siehe scrollArea.tsx); ohne das erbte das Formular die Position der Liste und
  // öffnete sich mittendrin.
  const scrollArea = useScrollArea();
  const listScroll = useRef(0);

  // Zählt hoch, sobald eine Zeile gelöscht wurde: Der Effekt darunter muss dann noch einmal
  // laufen, obwohl sich `editing` nicht geändert hat.
  const [restoreScroll, setRestoreScroll] = useState(0);

  useLayoutEffect(() => {
    const area = scrollArea?.current;
    if (area) area.scrollTop = editing ? 0 : listScroll.current;
  }, [editing, scrollArea, restoreScroll, data]);

  async function open(id: number) {
    listScroll.current = scrollArea?.current?.scrollTop ?? 0;
    setEditing(await fetchAdminPhoto(id));
  }

  /* Löschen und Wiederherstellen direkt aus der Liste, ohne den Umweg über den Editor -- beim
     Aussortieren nach einem Import geht es reihenweise. Die Zeile verschwindet danach aus der
     Ansicht (jeder Filter zeigt entweder Gelöschte oder die anderen), die Liste bleibt aber
     stehen, wo sie stand: Der nächste Griff soll dieselbe Stelle treffen.

     Nur das Löschen fragt zurück. Wiederherstellen macht nichts kaputt. */
  async function setDeleted(id: number, title: string | null, deleted: boolean) {
    if (deleted && !window.confirm(t.admin.editor.deleteConfirm(title || t.admin.photos.untitled))) {
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
