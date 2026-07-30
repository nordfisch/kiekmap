/**
 * Bilder von einem USB-Stick aufnehmen.
 *
 * Der zweite Weg neben dem Upload über den Rechner, und für jemanden, der mit einem Stick voller
 * Scans vor dem Gerät steht, der einzige. Ort und Jahr gelten wie beim Stapel-Upload für alles.
 *
 * **Auf dem Stick wird nichts verändert.** Anders als im überwachten Eingangsordner, wo
 * Aufgenommenes beiseitegeräumt wird -- ein fremder Datenträger wird nur gelesen.
 *
 * Nach dem Lesen kommt hier *keine* Nacharbeitstabelle wie beim Upload. Wer einen Ordner mit
 * zweihundert Bildern einliest, will keine Tabelle mit zweihundert Zeilen; die
 * „Unvollständig"-Liste ist dafür gebaut. Der Weg endet deshalb mit einem Sprung dorthin.
 */

import { useCallback, useEffect, useState } from "react";

import {
  type BatchDefaults,
  type ImportFolder,
  type JobState,
  acknowledgeJob,
  fetchImportFolders,
  fetchJob,
  startStickImport,
} from "../api/admin";
import { t } from "../texte/de";
import { formatCount } from "./format";

const IDLE_POLL_MS = 4000;
const BUSY_POLL_MS = 800;

export function StickImport({
  defaults,
  onFinished,
}: {
  /** Ort und Jahr aus dem Formular darüber -- dieselben wie beim Upload. */
  defaults: BatchDefaults;
  onFinished: () => void;
}) {
  const [folders, setFolders] = useState<ImportFolder[] | null>(null);
  const [job, setJob] = useState<JobState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const running = job?.phase === "running";

  const poll = useCallback(async () => {
    try {
      const status = await fetchJob();
      setJob(status);
      // Während gelesen wird, ändert sich die Ordnerliste nicht -- und sie durchsucht den Stick.
      if (status.phase !== "running") setFolders(await fetchImportFolders());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void poll();
    const timer = setInterval(() => void poll(), running ? BUSY_POLL_MS : IDLE_POLL_MS);
    return () => clearInterval(timer);
  }, [poll, running]);

  async function begin(folder: ImportFolder) {
    setError(null);
    try {
      setJob(await startStickImport(folder.path, defaults));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function finish() {
    setJob(await acknowledgeJob());
    void poll();
  }

  // Ein Auftrag für das Gerät: läuft gerade eine Sicherung, gehört dieser Bereich ihr.
  const mine = job && job.kind === "import";

  if (mine && job.phase === "running") {
    const share = job.total > 0 ? job.done / job.total : 0;
    return (
      <section className="stick">
        <h3 className="admin__heading">{t.admin.stick.title}</h3>
        <p className="backup__progress-text">{job.message}</p>
        <div
          className="progress"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={job.total}
          aria-valuenow={job.done}
        >
          <span className="progress__bar" style={{ width: `${share * 100}%` }} />
        </div>
        <p className="admin__note">{t.admin.stick.running}</p>
      </section>
    );
  }

  if (mine && job.phase === "done") {
    return (
      <section className="stick">
        <div className="backup__done">
          <span className="backup__check" aria-hidden="true">
            ✓
          </span>
          <p>{job.message}</p>
          <div className="upload__actions">
            <button
              type="button"
              className="button button--primary"
              onClick={() => {
                void finish();
                onFinished();
              }}
            >
              {t.admin.stick.toIncomplete}
            </button>
            <button type="button" className="button" onClick={() => void finish()}>
              {t.admin.stick.done}
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="stick">
      <h3 className="admin__heading">{t.admin.stick.title}</h3>
      <p className="admin__note">{t.admin.stick.intro}</p>

      {(error || (mine && job.phase === "error")) && (
        <p className="admin__error">{error ?? job?.error}</p>
      )}

      {!folders ? (
        <p className="admin__note">{t.admin.stick.searching}</p>
      ) : folders.length === 0 ? (
        <p className="admin__note">{t.admin.stick.none}</p>
      ) : (
        <ul className="photo-rows">
          {folders.map((folder) => (
            <li key={folder.path} className="photo-row">
              <div className="photo-row__text">
                <span className="photo-row__title">
                  {t.admin.stick.folder(folder.name, folder.drive)}
                </span>
                <span className="photo-row__meta">
                  {t.admin.stick.images(folder.images)}
                </span>
              </div>
              <button type="button" className="button" onClick={() => void begin(folder)}>
                {t.admin.stick.start}
              </button>
            </li>
          ))}
        </ul>
      )}

      {folders && folders.length > 0 && (
        <p className="admin__note">{formatCount(folders.length)} Ordner gefunden.</p>
      )}
    </section>
  );
}
