/**
 * Batch upload.
 *
 * Three steps: state place and year for the whole batch, upload, then correct row by row.
 *
 * The one decision worth knowing: the photos are in the database **after the upload**, not after
 * "Übernehmen". A browser that gets closed must not cost uploads. What is left lying here shows
 * up in the "Hilf mit" panel later -- the table is a list of things to tidy up, not a queue.
 *
 * Files go up one request at a time, although the endpoint would take a list. That is what makes
 * "Bild 7 von 40" possible; a single request over a gigabyte would show nothing for minutes.
 */

import { useState } from "react";

import { type BatchDefaults, patchPhoto, uploadPhoto } from "../api/admin";
import type { PhotoDetail } from "../api/client";
import { t } from "../texte/de";
import { titleFromFilename } from "./filename";
import { PlaceField, type PickedPlace } from "./PlaceField";
import { StickImport } from "./StickImport";

type Phase = "choose" | "uploading" | "review";

type Row = {
  key: string;
  filename: string;
  /** imported | duplicate | rejected -- only the first is editable. */
  result: string;
  message: string;
  photo: PhotoDetail | null;
  title: string;
  year: string;
  place: PickedPlace | null;
  busy: boolean;
  error: string | null;
};

function toRow(
  filename: string,
  result: string,
  message: string,
  photo: PhotoDetail | null,
  defaults: { year: string; place: PickedPlace | null },
): Row {
  return {
    key: `${filename}-${photo?.id ?? Math.random()}`,
    filename,
    result,
    message,
    photo,
    // What the file itself brought wins over the file name -- but a scan almost never brings one.
    title: photo?.title ?? titleFromFilename(filename),
    year: photo?.date_from ? photo.date_from.slice(0, 4) : defaults.year,
    place:
      photo?.lat != null && photo.lon != null
        ? { lat: photo.lat, lon: photo.lon, name: photo.place_name ?? "" }
        : defaults.place,
    busy: false,
    error: null,
  };
}

export function BatchUpload({ onShowIncomplete }: { onShowIncomplete: () => void }) {
  const [phase, setPhase] = useState<Phase>("choose");
  const [files, setFiles] = useState<File[]>([]);
  const [year, setYear] = useState("");
  const [place, setPlace] = useState<PickedPlace | null>(null);
  const [done, setDone] = useState(0);
  const [rows, setRows] = useState<Row[]>([]);
  const [counts, setCounts] = useState({ imported: 0, duplicates: 0, rejected: 0 });
  const [error, setError] = useState<string | null>(null);

  function batchDefaults(): BatchDefaults {
    const parsed = Number.parseInt(year, 10);
    return {
      ...(Number.isFinite(parsed) ? { year: parsed, precision: "year" as const } : {}),
      ...(place ? { lat: place.lat, lon: place.lon, placeName: place.name } : {}),
    };
  }

  async function start() {
    setPhase("uploading");
    setDone(0);
    setError(null);

    const defaults = batchDefaults();
    const collected: Row[] = [];
    const tally = { imported: 0, duplicates: 0, rejected: 0 };

    for (const [index, file] of files.entries()) {
      try {
        const result = await uploadPhoto(file, defaults);
        tally.imported += result.imported;
        tally.duplicates += result.duplicates;
        tally.rejected += result.rejected;
        for (const item of result.items) {
          collected.push(
            toRow(item.filename, item.result, item.message, item.photo, { year, place }),
          );
        }
      } catch (e) {
        // One broken file must not stop the other thirty-nine.
        collected.push(
          toRow(file.name, "rejected", e instanceof Error ? e.message : String(e), null, {
            year,
            place,
          }),
        );
        tally.rejected += 1;
      }
      setDone(index + 1);
    }

    setRows(collected);
    setCounts(tally);
    setPhase("review");
  }

  function update(key: string, patch: Partial<Row>) {
    setRows((current) => current.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  async function apply(row: Row): Promise<boolean> {
    if (!row.photo) return false;
    update(row.key, { busy: true, error: null });

    const parsed = Number.parseInt(row.year, 10);
    try {
      await patchPhoto(row.photo.id, {
        title: row.title.trim() || null,
        date: Number.isFinite(parsed) ? { year: parsed, precision: "year" } : null,
        location: row.place
          ? { lat: row.place.lat, lon: row.place.lon, place_name: row.place.name || null }
          : null,
      });
      setRows((current) => current.filter((other) => other.key !== row.key));
      return true;
    } catch (e) {
      update(row.key, { busy: false, error: e instanceof Error ? e.message : String(e) });
      return false;
    }
  }

  async function applyAll() {
    // Sequentially, not in parallel: forty simultaneous writes to one SQLite file on a Pi is a
    // way to produce lock errors, and nobody is waiting for the millisecond.
    for (const row of rows.filter((candidate) => candidate.photo)) {
      await apply(row);
    }
  }

  function again() {
    setPhase("choose");
    setFiles([]);
    setRows([]);
    setDone(0);
  }

  if (phase === "choose") {
    return (
      <div className="upload">
        <h3 className="admin__heading">{t.admin.upload.step1}</h3>
        <p className="admin__note">{t.admin.upload.step1Hint}</p>

        <label className="field__label" htmlFor="batch-year">
          {t.admin.editor.year}
        </label>
        <input
          id="batch-year"
          className="field__input field__input--year"
          type="number"
          min={1800}
          max={2100}
          value={year}
          onChange={(event) => setYear(event.target.value)}
        />

        <fieldset className="field__group">
          <legend className="field__label">{t.admin.editor.place}</legend>
          <PlaceField value={place} onPick={setPlace} onClear={() => setPlace(null)} />
        </fieldset>

        <label className="field__label" htmlFor="batch-files">
          {t.admin.upload.choose}
        </label>
        <input
          id="batch-files"
          className="field__input"
          type="file"
          multiple
          accept="image/jpeg,image/png,image/tiff,image/webp"
          onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
        />

        {files.length > 0 && <p className="admin__note">{t.admin.upload.chosen(files.length)}</p>}
        {error && <p className="admin__error">{error}</p>}

        <button
          type="button"
          className="button button--primary"
          onClick={() => void start()}
          disabled={files.length === 0}
        >
          {t.admin.upload.start}
        </button>

        {/* Derselbe Stapel, anderer Weg herein. Ort und Jahr von oben gelten für beide -- wer sie
            eingetragen hat, muss das für den Stick nicht wiederholen. */}
        <StickImport defaults={batchDefaults()} onFinished={onShowIncomplete} />
      </div>
    );
  }

  if (phase === "uploading") {
    return (
      <div className="upload">
        <p className="admin__heading">{t.admin.upload.progress(done, files.length)}</p>
        <div
          className="progress"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={files.length}
          aria-valuenow={done}
        >
          <span
            className="progress__bar"
            style={{ width: `${(done / Math.max(1, files.length)) * 100}%` }}
          />
        </div>
      </div>
    );
  }

  const editable = rows.filter((row) => row.photo && row.result === "imported");

  return (
    <div className="upload">
      <p className="admin__heading">
        {t.admin.upload.summary(counts.imported, counts.duplicates, counts.rejected)}
      </p>
      <p className="admin__note">{t.admin.upload.tableHint}</p>

      {rows.length === 0 ? (
        <p className="admin__note">{t.admin.upload.allApplied}</p>
      ) : (
        <ul className="upload-rows">
          {rows.map((row) => (
            <li key={row.key} className="upload-row">
              {row.photo ? (
                // Not photo.thumb_url: that one is the 1200 px version for the overlay, and forty
                // of those on a Pi is a lot of picture for a 6 rem box.
                <img
                  className="upload-row__thumb"
                  src={`/api/photos/${row.photo.id}/thumb?size=240`}
                  alt=""
                />
              ) : (
                <span className="upload-row__thumb upload-row__thumb--empty" aria-hidden="true" />
              )}

              <div className="upload-row__fields">
                <span className="upload-row__filename">{row.filename}</span>

                {row.result === "imported" ? (
                  <>
                    <input
                      className="field__input"
                      aria-label={t.admin.editor.title}
                      value={row.title}
                      onChange={(event) => update(row.key, { title: event.target.value })}
                    />
                    <div className="field__row">
                      <input
                        className="field__input field__input--year"
                        type="number"
                        min={1800}
                        max={2100}
                        aria-label={t.admin.editor.year}
                        value={row.year}
                        onChange={(event) => update(row.key, { year: event.target.value })}
                      />
                      <PlaceField
                        value={row.place}
                        onPick={(picked) => update(row.key, { place: picked })}
                        onClear={() => update(row.key, { place: null })}
                      />
                    </div>
                  </>
                ) : (
                  <span className="upload-row__message">{row.message}</span>
                )}

                {row.error && <span className="admin__error">{row.error}</span>}
              </div>

              {row.result === "imported" ? (
                <button
                  type="button"
                  className="button"
                  onClick={() => void apply(row)}
                  disabled={row.busy}
                >
                  {t.admin.upload.apply}
                </button>
              ) : (
                <button
                  type="button"
                  className="button button--quiet"
                  onClick={() => setRows((current) => current.filter((o) => o.key !== row.key))}
                >
                  {t.admin.upload.done}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}

      <div className="upload__actions">
        {editable.length > 0 && (
          <button type="button" className="button button--primary" onClick={() => void applyAll()}>
            {t.admin.upload.applyAll}
          </button>
        )}
        <button type="button" className="button" onClick={again}>
          {t.admin.upload.more}
        </button>
      </div>
    </div>
  );
}
