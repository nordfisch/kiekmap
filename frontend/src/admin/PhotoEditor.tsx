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

import { type PhotoPatch, patchPhoto } from "../api/admin";
import type { PhotoDetail } from "../api/client";
import { t } from "../texte/de";
import { PlaceField, type PickedPlace } from "./PlaceField";

type Draft = {
  title: string;
  description: string;
  year: string;
  precision: "year" | "decade";
  place: PickedPlace | null;
  tags: string;
  hidden: boolean;
};

function toDraft(photo: PhotoDetail): Draft {
  return {
    title: photo.title ?? "",
    description: photo.description ?? "",
    year: photo.date_from ? photo.date_from.slice(0, 4) : "",
    precision: photo.date_precision === "decade" ? "decade" : "year",
    place:
      photo.lat !== null && photo.lon !== null
        ? { lat: photo.lat, lon: photo.lon, name: photo.place_name ?? "" }
        : null,
    tags: photo.tags.join(", "),
    hidden: photo.status === "hidden",
  };
}

function toPatch(draft: Draft): PhotoPatch {
  const year = Number.parseInt(draft.year, 10);

  return {
    title: draft.title.trim() || null,
    description: draft.description.trim() || null,
    date: Number.isFinite(year) ? { year, precision: draft.precision } : null,
    location: draft.place
      ? { lat: draft.place.lat, lon: draft.place.lon, place_name: draft.place.name || null }
      : null,
    tags: draft.tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    status: draft.hidden ? "hidden" : "published",
  };
}

export function PhotoEditor({
  photo,
  onSaved,
  onClose,
}: {
  photo: PhotoDetail;
  onSaved: (photo: PhotoDetail) => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<Draft>(() => toDraft(photo));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setDraft(toDraft(photo)), [photo]);

  function change<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function save() {
    setBusy(true);
    setError(null);
    try {
      onSaved(await patchPhoto(photo.id, toPatch(draft)));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
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

      <label className="field__label" htmlFor="editor-year">
        {t.admin.editor.year}
      </label>
      <div className="field__row">
        <input
          id="editor-year"
          className="field__input field__input--year"
          type="number"
          min={1800}
          max={2100}
          value={draft.year}
          onChange={(event) => change("year", event.target.value)}
        />
        <select
          className="field__input"
          aria-label={t.admin.editor.year}
          value={draft.precision}
          onChange={(event) => change("precision", event.target.value as "year" | "decade")}
        >
          <option value="year">{t.admin.editor.precisionYear}</option>
          <option value="decade">{t.admin.editor.precisionDecade}</option>
        </select>
      </div>
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

      <label className="field__check">
        <input
          type="checkbox"
          checked={draft.hidden}
          onChange={(event) => change("hidden", event.target.checked)}
        />
        {t.admin.editor.hidden}
      </label>
      <p className="admin__note">{t.admin.editor.hiddenHint}</p>

      {error && <p className="admin__error">{error}</p>}

      <div className="editor__actions">
        <button type="button" className="button button--primary" onClick={save} disabled={busy}>
          {t.admin.editor.save}
        </button>
        <button type="button" className="button" onClick={onClose} disabled={busy}>
          {t.admin.editor.cancel}
        </button>
      </div>
    </div>
  );
}
