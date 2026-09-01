/**
 * Editing one photo.
 *
 * The form works with the same distinction the backend makes: an empty year field means "unknown"
 * and clears the dating, it does not mean "leave as it was". That is what lets a curator take a
 * wrong year back out instead of only replacing it with another wrong one.
 *
 * What the file itself claims is shown but never silently adopted -- for a scan the EXIF date is
 * the date of the scanning run. See backend/app/services/exif.py.
 */

import { useEffect, useState } from "react";

import { type PhotoAdminDetail, type PhotoPatch, patchPhoto } from "../api/admin";
import { t } from "../text";
import { type YearInput, toDate } from "./yearInput";
import { PlaceField, type PickedPlace } from "./PlaceField";
import { YearField } from "./YearField";

type Draft = {
  title: string;
  description: string;
  credit: string;
  provenance: string;
  date: YearInput;
  place: PickedPlace | null;
  tags: string;
  deleted: boolean;
};

function toDraft(photo: PhotoAdminDetail): Draft {
  return {
    title: photo.title ?? "",
    description: photo.description ?? "",
    credit: photo.credit ?? "",
    provenance: photo.provenance ?? "",
    date: {
      year: photo.date_from ? photo.date_from.slice(0, 4) : "",
      precision: photo.date_precision === "decade" ? "decade" : "year",
    },
    place:
      photo.lat !== null && photo.lon !== null
        ? { lat: photo.lat, lon: photo.lon, name: photo.place_name ?? "" }
        : null,
    tags: photo.tags.join(", "),
    deleted: photo.status === "deleted",
  };
}

function toPatch(draft: Draft, deleted = draft.deleted): PhotoPatch {
  return {
    title: draft.title.trim() || null,
    description: draft.description.trim() || null,
    credit: draft.credit.trim() || null,
    provenance: draft.provenance.trim() || null,
    // null means "clear the date" -- an empty year field is exactly that, see below.
    date: toDate(draft.date),
    location: draft.place
      ? { lat: draft.place.lat, lon: draft.place.lon, place_name: draft.place.name || null }
      : null,
    tags: draft.tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    status: deleted ? "deleted" : "published",
  };
}

export function PhotoEditor({
  photo,
  onSaved,
  onClose,
}: {
  photo: PhotoAdminDetail;
  onSaved: (photo: PhotoAdminDetail) => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<Draft>(() => toDraft(photo));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setDraft(toDraft(photo)), [photo]);

  function change<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function save(deleted = draft.deleted) {
    setBusy(true);
    setError(null);
    try {
      onSaved(await patchPhoto(photo.id, toPatch(draft, deleted)));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  /* Deleting saves and returns like "Speichern" -- only with the other status. The remaining
     changes in the form go along; throwing them away would be the bigger surprise. Restoring does
     not ask back: it breaks nothing. */
  function remove() {
    if (window.confirm(t.admin.editor.deleteConfirm(photo.title || t.admin.photos.untitled))) {
      void save(true);
    }
  }

  return (
    <div className="editor">
      <img className="editor__image" src={photo.thumb_url} alt={photo.title ?? ""} />
      <p className="admin__note">
        {t.admin.editor.fileInfo(photo.original_filename, photo.width, photo.height)}
      </p>
      {photo.exif_datetime && (
        <p className="admin__note">
          {t.admin.editor.scanDate(new Date(photo.exif_datetime).toLocaleDateString("de-DE"))}
        </p>
      )}

      <label className="field__label" htmlFor="editor-title">
        {t.admin.editor.title}
      </label>
      <input
        id="editor-title"
        className="field__input"
        value={draft.title}
        onChange={(event) => change("title", event.target.value)}
      />

      <label className="field__label" htmlFor="editor-description">
        {t.admin.editor.description}
      </label>
      <textarea
        id="editor-description"
        className="field__input field__input--area"
        rows={3}
        value={draft.description}
        onChange={(event) => change("description", event.target.value)}
      />

      <YearField value={draft.date} onChange={(date) => change("date", date)} />
      <p className="admin__note">{t.admin.editor.yearHint}</p>

      <fieldset className="field__group">
        <legend className="field__label">{t.admin.editor.place}</legend>
        <PlaceField
          value={draft.place}
          onPick={(place) => change("place", place)}
          onClear={() => change("place", null)}
        />
        {/* For places the gazetteer does not know -- a field in the marsh has no street name. */}
        <label className="field__label" htmlFor="editor-lat">
          {t.admin.editor.coordinates}
        </label>
        <div className="field__row">
          <input
            id="editor-lat"
            className="field__input"
            type="number"
            step="0.00001"
            value={draft.place?.lat ?? ""}
            onChange={(event) =>
              change("place", {
                lat: Number(event.target.value),
                lon: draft.place?.lon ?? 0,
                name: draft.place?.name ?? "",
              })
            }
          />
          <input
            className="field__input"
            type="number"
            step="0.00001"
            aria-label={t.admin.editor.coordinates}
            value={draft.place?.lon ?? ""}
            onChange={(event) =>
              change("place", {
                lat: draft.place?.lat ?? 0,
                lon: Number(event.target.value),
                name: draft.place?.name ?? "",
              })
            }
          />
        </div>
      </fieldset>

      <label className="field__label" htmlFor="editor-tags">
        {t.admin.editor.tags}
      </label>
      <input
        id="editor-tags"
        className="field__input"
        value={draft.tags}
        onChange={(event) => change("tags", event.target.value)}
      />
      <p className="admin__note">{t.admin.editor.tagsHint}</p>

      <label className="field__label" htmlFor="editor-credit">
        {t.admin.editor.credit}
      </label>
      <input
        id="editor-credit"
        className="field__input"
        value={draft.credit}
        onChange={(event) => change("credit", event.target.value)}
      />
      <p className="admin__note">{t.admin.editor.creditHint}</p>

      <label className="field__label" htmlFor="editor-provenance">
        {t.admin.editor.provenance}
      </label>
      <textarea
        id="editor-provenance"
        className="field__input field__input--area"
        rows={2}
        value={draft.provenance}
        onChange={(event) => change("provenance", event.target.value)}
      />
      <p className="admin__note">{t.admin.editor.provenanceHint}</p>

      {error && <p className="admin__error">{error}</p>}

      <div className="editor__actions">
        <button
          type="button"
          className="button button--primary"
          onClick={() => void save()}
          disabled={busy}
        >
          {t.admin.editor.save}
        </button>
        <button type="button" className="button" onClick={onClose} disabled={busy}>
          {t.admin.editor.cancel}
        </button>
        {draft.deleted ? (
          <button
            type="button"
            className="button button--restore editor__status"
            onClick={() => void save(false)}
            disabled={busy}
          >
            {t.admin.editor.restore}
          </button>
        ) : (
          <button
            type="button"
            className="button button--danger editor__status"
            onClick={remove}
            disabled={busy}
          >
            {t.admin.editor.delete}
          </button>
        )}
      </div>
    </div>
  );
}
