/**
 * Fotos hereinholen — vom Rechner oder vom USB-Stick.
 *
 * Drei Schritte, und die Reihenfolge ist die Aussage: **erst woher, dann was für alle gilt, dann
 * ein Knopf.** Vorher stand das Formular für Jahr und Ort ganz oben, bevor überhaupt gesagt war,
 * woher die Bilder kommen, und der Stick hing als Nachtrag unter einer Trennlinie darunter.
 *
 * Jahr und Ort werden **einmal** gefragt und gelten für beide Wege. Bei vierzig Bildern derselben
 * Kirchweih ist das der ganze Unterschied — sie füllen aber nur, was der Import leer gelassen
 * hat; was die Datei selbst weiß, gewinnt.
 *
 * Danach dieselbe Regel für beide Wege: bis REVIEW_LIMIT Bilder die Nacharbeits-Tabelle, darüber
 * nur die Zusammenfassung. Wer zweihundert Bilder einliest, will keine Tabelle mit zweihundert
 * Zeilen — für den ist die „Ohne Ort"-Liste die Arbeitsfläche.
 */

import { useLayoutEffect, useState } from "react";

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
import { t } from "../texte/de";
import { titleFromFilename } from "./filename";
import { type YearInput, toDate } from "./jahr";
import { FileDropZone } from "./DropZone";
import { PlaceField, type PickedPlace } from "./PlaceField";
import { YearField } from "./YearField";
import { StickFolders } from "./StickImport";
import { useScrollArea } from "./scrollArea";

/** Muss zu REVIEW_LIMIT in backend/app/api/backup.py passen. */
const REVIEW_LIMIT = 30;

type Source = "computer" | "stick";
type Phase = "choose" | "working" | "review";

type Row = {
  key: string;
  filename: string;
  /** imported | duplicate | rejected -- nur das erste ist bearbeitbar. */
  result: string;
  message: string;
  photo: PhotoDetail | null;
  title: string;
  year: string;
  place: PickedPlace | null;
  busy: boolean;
  error: string | null;
};

function toRow(item: UploadItem, defaults: { year: string; place: PickedPlace | null }): Row {
  const photo = item.photo;
  return {
    key: `${item.filename}-${photo?.id ?? Math.random()}`,
    filename: item.filename,
    result: item.result,
    message: item.message,
    photo,
    // Was die Datei selbst mitbrachte, schlaegt den Dateinamen -- ein Scan bringt aber selten
    // etwas mit.
    title: photo?.title ?? titleFromFilename(item.filename),
    year: photo?.date_from ? photo.date_from.slice(0, 4) : defaults.year,
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

  const [phase, setPhase] = useState<Phase>("choose");
  const [done, setDone] = useState(0);
  const [job, setJob] = useState<JobState | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Dieselbe Ursache wie beim Fotoeditor: Der Phasenwechsel tauscht den Inhalt, nicht den
  // scrollenden Bereich darum. Wer unten auf „Importieren" tippt, stünde sonst mitten in der
  // Ergebnistabelle, statt bei ihrer Überschrift.
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
    };
  }

  function finish(items: UploadItem[] | null, text: string) {
    setSummary(text);
    // Keine Tabelle bei zu vielen -- und keine, wenn das Backend sie gar nicht erst geschickt hat.
    setRows(
      items && items.length <= REVIEW_LIMIT
        ? items
            .filter((item) => item.result === "imported")
            .map((item) => toRow(item, { year: year.year, place }))
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
        // Eine kaputte Datei darf die anderen neununddreissig nicht aufhalten.
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

  /** Der Stick-Auftrag läuft im Gerät; StickFolders meldet, wenn er durch ist. */
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
    } catch (e) {
      update(row.key, { busy: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  async function applyAll() {
    // Nacheinander: vierzig gleichzeitige Schreibzugriffe auf eine SQLite-Datei auf einem Pi sind
    // ein Weg, Sperrfehler zu erzeugen, und auf die Millisekunde wartet niemand.
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

  // --- Schritt 3: was daraus geworden ist ---------------------------------

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

  // --- Während es läuft ---------------------------------------------------

  if (phase === "working") {
    const isStick = source === "stick";
    const text = isStick
      ? (job?.message ?? t.admin.loading)
      : t.admin.upload.progress(done, files.length);
    const share = isStick
      ? (job && job.total > 0 ? job.done / job.total : 0)
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

  // --- Schritt 1 und 2 ----------------------------------------------------

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
            {folder ? t.admin.stick.folder(folder.name, folder.drive) : t.admin.upload.fromStickHint}
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
  return (
    <ul className="upload-rows">
      {rows.map((row) => (
        <li key={row.key} className="upload-row">
          {row.photo && (
            <img
              className="upload-row__thumb"
              src={`/api/photos/${row.photo.id}/thumb?size=240`}
              alt=""
            />
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
              <input
                className="field__input field__input--year"
                type="number"
                min={1800}
                max={2100}
                aria-label={t.admin.editor.year}
                value={row.year}
                onChange={(event) => onChange(row.key, { year: event.target.value })}
              />
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
  );
}
