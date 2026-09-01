/**
 * Taking photos in -- from the computer or from a USB stick.
 *
 * Three steps, and their order is the statement: **first where from, then what holds for all of
 * them, then one button.** The form for year and place used to sit at the very top, before
 * anybody had said where the pictures come from, and the stick hung below a rule as an
 * afterthought.
 *
 * Year and place are asked **once** and hold for both routes. With forty pictures of the same
 * village fair that is the whole difference -- but they only fill what the import left empty;
 * what the file itself knows wins.
 *
 * After that the same rule for both routes: up to REVIEW_LIMIT pictures the review table, beyond
 * it only the summary. Whoever takes in two hundred pictures does not want a table with two
 * hundred rows -- for them the "Ohne Ort" list is the work surface.
 */

import { useEffect, useLayoutEffect, useState } from "react";

import {
  type BatchDefaults,
  type ImportFolder,
  type JobState,
  type UploadItem,
  acknowledgeJob,
  patchPhoto,
  startStickImport,
  uploadPhoto,
} from "../api/admin";
import type { PhotoDetail } from "../api/client";
import { t } from "../text";
import { titleFromFilename } from "./filename";
import { type YearInput, fromPhoto, toDate } from "./yearInput";
import { FileDropZone } from "./DropZone";
import { PlaceField, type PickedPlace } from "./PlaceField";
import { YearField } from "./YearField";
import { StickFolders } from "./StickImport";
import { useScrollArea } from "./scrollArea";

/** Has to match REVIEW_LIMIT in backend/app/api/backup.py. */
const REVIEW_LIMIT = 30;

type Source = "computer" | "stick";
type Phase = "choose" | "working" | "review";

type Row = {
  key: string;
  filename: string;
  /** imported | duplicate | rejected -- only the first can be edited. */
  result: string;
  message: string;
  photo: PhotoDetail | null;
  title: string;
  /** Year and precision together -- the same shape as in the photo editor. */
  date: YearInput;
  place: PickedPlace | null;
  busy: boolean;
  error: string | null;
};

function toRow(item: UploadItem, defaults: { year: YearInput; place: PickedPlace | null }): Row {
  const photo = item.photo;
  return {
    key: `${item.filename}-${photo?.id ?? Math.random()}`,
    filename: item.filename,
    result: item.result,
    message: item.message,
    photo,
    // What the file brought along beats the file name -- though a scan rarely brings anything.
    title: photo?.title ?? titleFromFilename(item.filename),
    // The precision comes from the photo, not from the year: a 1920 already stored as a decade
    // must not quietly become the year 1920 while somebody edits the row.
    date: photo?.date_from ? fromPhoto(photo.date_from, photo.date_precision) : defaults.year,
    place:
      photo?.lat != null && photo.lon != null
        ? { lat: photo.lat, lon: photo.lon, name: photo.place_name ?? "" }
        : defaults.place,
    busy: false,
    error: null,
  };
}

export function ImportView({ onReview }: { onReview: () => void }) {
  const [source, setSource] = useState<Source>("computer");
  const [files, setFiles] = useState<File[]>([]);
  const [folder, setFolder] = useState<ImportFolder | null>(null);

  const [year, setYear] = useState<YearInput>({ year: "", precision: "year" });
  const [place, setPlace] = useState<PickedPlace | null>(null);
  const [credit, setCredit] = useState("");
  const [provenance, setProvenance] = useState("");
  const [tags, setTags] = useState("");

  const [phase, setPhase] = useState<Phase>("choose");
  const [done, setDone] = useState(0);
  const [job, setJob] = useState<JobState | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Same cause as in the photo editor: changing phase swaps the content, not the scrolling area
  // around it. Whoever taps "Importieren" at the bottom would otherwise land in the middle of the
  // result table instead of at its heading.
  const scrollArea = useScrollArea();
  useLayoutEffect(() => {
    scrollArea?.current?.scrollTo({ top: 0 });
  }, [phase, scrollArea]);

  const ready = source === "computer" ? files.length > 0 : folder !== null;

  function batchDefaults(): BatchDefaults {
    const date = toDate(year);
    return {
      ...(date ? { year: date.year, precision: date.precision } : {}),
      ...(place ? { lat: place.lat, lon: place.lon, placeName: place.name } : {}),
      // A box of scans almost always comes from one person -- so both hold for all of them.
      ...(credit.trim() ? { credit: credit.trim() } : {}),
      ...(provenance.trim() ? { provenance: provenance.trim() } : {}),
      // Not "what is empty stays empty" like the rest: keywords are a set, so this one joins
      // whatever the files themselves carry -- see importer.apply_batch_defaults.
      ...(tags.trim() ? { tags: tags.trim() } : {}),
    };
  }

  function finish(items: UploadItem[] | null, text: string) {
    setSummary(text);
    // No table when there are too many -- and none when the backend did not send one at all.
    setRows(
      items && items.length <= REVIEW_LIMIT
        ? items
            .filter((item) => item.result === "imported")
            .map((item) => toRow(item, { year, place }))
        : [],
    );
    setPhase("review");
  }

  async function startFromComputer() {
    setPhase("working");
    setDone(0);
    setError(null);

    const defaults = batchDefaults();
    const collected: UploadItem[] = [];
    const tally = { imported: 0, duplicates: 0, rejected: 0 };

    for (const [index, file] of files.entries()) {
      try {
        const result = await uploadPhoto(file, defaults);
        tally.imported += result.imported;
        tally.duplicates += result.duplicates;
        tally.rejected += result.rejected;
        collected.push(...result.items);
      } catch (e) {
        // One broken file must not hold up the other thirty-nine.
        collected.push({
          filename: file.name,
          result: "rejected",
          message: e instanceof Error ? e.message : String(e),
          photo: null,
        });
        tally.rejected += 1;
      }
      setDone(index + 1);
    }

    finish(collected, t.admin.upload.summary(tally.imported, tally.duplicates, tally.rejected));
  }

  async function startFromStick() {
    if (!folder) return;
    setError(null);
    try {
      setJob(await startStickImport(folder.path, batchDefaults()));
      setPhase("working");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  /** The stick job runs inside the device; StickFolders reports when it is through. */
  function stickFinished(state: JobState) {
    setJob(state);
    if (state.phase === "done") {
      void acknowledgeJob();
      finish(state.items, state.message);
    } else if (state.phase === "error") {
      setError(state.error);
      setPhase("choose");
      void acknowledgeJob();
    }
  }

  function update(key: string, patch: Partial<Row>) {
    setRows((current) => current.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  async function apply(row: Row) {
    if (!row.photo) return;
    update(row.key, { busy: true, error: null });

    try {
      await patchPhoto(row.photo.id, {
        title: row.title.trim() || null,
        // null means "clear the date" -- an empty year field is exactly that, as in the editor.
        date: toDate(row.date),
        location: row.place
          ? { lat: row.place.lat, lon: row.place.lon, place_name: row.place.name || null }
          : null,
      });
      setRows((current) => current.filter((other) => other.key !== row.key));
    } catch (e) {
      update(row.key, { busy: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  async function applyAll() {
    // One after another: forty concurrent writes to one SQLite file on a Pi is a way to produce
    // lock errors, and nobody is waiting on the millisecond.
    for (const row of rows.filter((candidate) => candidate.photo)) {
      await apply(row);
    }
  }

  function again() {
    setPhase("choose");
    setFiles([]);
    setFolder(null);
    setRows([]);
    setDone(0);
    setJob(null);
  }

  // --- Step 3: what became of it ------------------------------------------

  if (phase === "review") {
    return (
      <div className="upload">
        <p className="admin__heading">{summary}</p>

        {rows.length === 0 ? (
          <>
            <p className="admin__note">{t.admin.upload.tooManyForTable}</p>
            <div className="upload__actions">
              <button type="button" className="button button--primary" onClick={onReview}>
                {t.admin.upload.toReview}
              </button>
              <button type="button" className="button" onClick={again}>
                {t.admin.upload.more}
              </button>
            </div>
          </>
        ) : (
          <>
            <p className="admin__note">{t.admin.upload.tableHint}</p>
            <ReviewTable rows={rows} onChange={update} onApply={apply} />
            <div className="upload__actions">
              <button
                type="button"
                className="button button--primary"
                onClick={() => void applyAll()}
              >
                {t.admin.upload.applyAll}
              </button>
              <button type="button" className="button" onClick={again}>
                {t.admin.upload.more}
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  // --- While it runs -------------------------------------------------------

  if (phase === "working") {
    const isStick = source === "stick";
    const text = isStick
      ? (job?.message ?? t.admin.loading)
      : t.admin.upload.progress(done, files.length);
    const share = isStick
      ? job && job.total > 0
        ? job.done / job.total
        : 0
      : done / Math.max(1, files.length);

    return (
      <div className="upload">
        <p className="backup__progress-text">{text}</p>
        <div className="progress" role="progressbar" aria-valuenow={Math.round(share * 100)}>
          <span className="progress__bar" style={{ width: `${share * 100}%` }} />
        </div>
        {isStick && (
          <>
            <p className="admin__note">{t.admin.stick.running}</p>
            <StickFolders selected={folder} onSelect={setFolder} onJob={stickFinished} watching />
          </>
        )}
      </div>
    );
  }

  // --- Steps 1 and 2 -------------------------------------------------------

  return (
    <div className="upload">
      <h3 className="admin__heading">{t.admin.upload.whereFrom}</h3>

      <div className="sources">
        <button
          type="button"
          className={source === "computer" ? "source source--active" : "source"}
          onClick={() => setSource("computer")}
        >
          <span className="source__title">{t.admin.upload.fromComputer}</span>
          <span className="source__hint">
            {files.length > 0 ? t.admin.upload.chosen(files.length) : t.admin.upload.chooseHint}
          </span>
        </button>

        <button
          type="button"
          className={source === "stick" ? "source source--active" : "source"}
          onClick={() => setSource("stick")}
        >
          <span className="source__title">{t.admin.upload.fromStick}</span>
          <span className="source__hint">
            {folder
              ? t.admin.stick.folder(folder.name, folder.drive)
              : t.admin.upload.fromStickHint}
          </span>
        </button>
      </div>

      {source === "computer" ? (
        <FileDropZone files={files} onFiles={setFiles} />
      ) : (
        <StickFolders selected={folder} onSelect={setFolder} onJob={stickFinished} />
      )}

      <h3 className="admin__heading">{t.admin.upload.step1}</h3>
      <p className="admin__note">{t.admin.upload.step1Hint}</p>

      <div className="batch-fields">
        <fieldset className="field__group">
          <legend className="field__label">{t.admin.editor.time}</legend>
          <YearField value={year} onChange={setYear} />
        </fieldset>

        <fieldset className="field__group">
          <legend className="field__label">{t.admin.editor.place}</legend>
          <PlaceField value={place} onPick={setPlace} onClear={() => setPlace(null)} />
        </fieldset>

        <fieldset className="field__group">
          <legend className="field__label">{t.admin.editor.tags}</legend>
          <input
            className="field__input"
            aria-label={t.admin.editor.tags}
            value={tags}
            onChange={(event) => setTags(event.target.value)}
          />
          <p className="admin__note">{t.admin.upload.tagsHint}</p>
        </fieldset>

        <fieldset className="field__group">
          <legend className="field__label">{t.admin.editor.credit}</legend>
          <input
            className="field__input"
            aria-label={t.admin.editor.credit}
            value={credit}
            onChange={(event) => setCredit(event.target.value)}
          />
          <label className="field__label" htmlFor="upload-provenance">
            {t.admin.editor.provenance}
          </label>
          <input
            id="upload-provenance"
            className="field__input"
            value={provenance}
            onChange={(event) => setProvenance(event.target.value)}
          />
        </fieldset>
      </div>

      {error && <p className="admin__error">{error}</p>}

      <button
        type="button"
        className="button button--primary upload__start"
        disabled={!ready}
        onClick={() => void (source === "computer" ? startFromComputer() : startFromStick())}
      >
        {t.admin.upload.start}
      </button>
    </div>
  );
}

function ReviewTable({
  rows,
  onChange,
  onApply,
}: {
  rows: Row[];
  onChange: (key: string, patch: Partial<Row>) => void;
  onApply: (row: Row) => Promise<void>;
}) {
  /** Which photo is currently shown large. */
  const [zoomed, setZoomed] = useState<PhotoDetail | null>(null);

  return (
    <>
      <ul className="upload-rows">
        {rows.map((row) => (
          <li key={row.key} className="upload-row">
            {/* The thumbnail is so small that a village fair and a fire brigade party cannot be
                told apart on it -- which is exactly what checking title and year needs. One click
                shows it large. */}
            {row.photo && (
              <button
                type="button"
                className="upload-row__zoom"
                onClick={() => setZoomed(row.photo)}
                aria-label={t.admin.upload.enlarge(row.filename)}
              >
                <img
                  className="upload-row__thumb"
                  src={`/api/photos/${row.photo.id}/thumb?size=240`}
                  alt=""
                />
              </button>
            )}

            <div className="upload-row__fields">
              <span className="upload-row__filename">{row.filename}</span>
              <input
                className="field__input"
                aria-label={t.admin.editor.title}
                value={row.title}
                onChange={(event) => onChange(row.key, { title: event.target.value })}
              />
              <div className="field__row">
                {/* The same component as in the photo editor: without the precision beside it no
                    decade could be entered here, and "1920er" is the normal case. */}
                <YearField value={row.date} onChange={(date) => onChange(row.key, { date })} />
                <PlaceField
                  value={row.place}
                  onPick={(picked) => onChange(row.key, { place: picked })}
                  onClear={() => onChange(row.key, { place: null })}
                />
              </div>
              {row.error && <span className="admin__error">{row.error}</span>}
            </div>

            <button
              type="button"
              className="button"
              onClick={() => void onApply(row)}
              disabled={row.busy}
            >
              {t.admin.upload.apply}
            </button>
          </li>
        ))}
      </ul>

      {zoomed && <ZoomView photo={zoomed} onClose={() => setZoomed(null)} />}
    </>
  );
}

/**
 * One photo large, above the list.
 *
 * Deliberately not a link into a new tab: the admin area runs in the same Chromium as the kiosk,
 * and that one has no tab bar -- whoever opens a second tab there never gets back. What is shown
 * is the 1200 px thumbnail, the same as in the photo editor; the original can be an 80 MB scan.
 */
function ZoomView({ photo, onClose }: { photo: PhotoDetail; onClose: () => void }) {
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="zoom"
      role="dialog"
      aria-modal="true"
      aria-label={t.admin.upload.enlarged}
      onClick={onClose}
    >
      <div className="zoom__box" onClick={(event) => event.stopPropagation()}>
        <button type="button" className="button zoom__close" onClick={onClose}>
          {t.overlay.close}
        </button>
        <img className="zoom__image" src={photo.thumb_url} alt={photo.title ?? ""} />
      </div>
    </div>
  );
}
