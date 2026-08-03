/**
 * Backup onto a USB stick or into one file, and restoring from a stick.
 *
 * The screen this stage exists for. A shell script would be less work and would never be run --
 * the people who do this are volunteers, once or twice a year. So: plug the stick in, one button,
 * a progress bar, and at the end a sentence that says the job is done and the stick may come out.
 *
 * Two tiles, the same shape the import screen uses, and below them one surface that keeps its
 * place and only changes what is in it. **The stick is on the left because it is the better
 * backup**: it writes only what is new and stays usable when it breaks off halfway. The file is
 * the addition -- see docs/decisions.md, point 11.
 *
 * Two loops run here. While nothing is happening, the drive list is polled -- plugging a stick in
 * is then enough, with no reload and no "search" button. While a job runs, its progress is polled
 * instead, faster, because that is what the bar moves on. The download is in neither loop: the
 * browser carries it, and there is nothing for us to watch.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import {
  type DriveItem,
  type DriveList,
  type JobState,
  type WaitingBackup,
  acknowledgeJob,
  downloadBackupZip,
  fetchDrives,
  fetchJob,
  restoreFromIncoming,
  startBackup,
  startRestore,
} from "../api/admin";
import { t } from "../texte/de";
import { formatBytes, formatCount, formatDate } from "./format";

/** While idle: has a stick appeared? While running: how far along is it? */
const IDLE_POLL_MS = 4000;
const BUSY_POLL_MS = 800;

type Target = "stick" | "zip";

export function Backup() {
  const [target, setTarget] = useState<Target>("stick");
  const [drives, setDrives] = useState<DriveList | null>(null);
  const [job, setJob] = useState<JobState | null>(null);
  const [error, setError] = useState<string | null>(null);
  /** Path of the drive whose restore is waiting for a yes. */
  const [confirming, setConfirming] = useState<string | null>(null);
  /** True once the download has been handed to the browser. */
  const [downloading, setDownloading] = useState(false);

  const running = job?.phase === "running";
  const waiting = drives?.incoming ?? null;

  /* Liegt eine Sicherung im Eingangsordner, ist sie das Wichtigste auf diesem Bildschirm --
     also wird die Kachel vorgewählt. Einmalig, nicht bei jedem Abruf: Wer danach bewusst auf
     „Auf USB-Stick" wechselt, soll nicht vier Sekunden später zurückgeschoben werden. */
  const announced = useRef<string | null>(null);
  useEffect(() => {
    if (waiting && announced.current !== waiting.file) {
      announced.current = waiting.file;
      setTarget("zip");
    }
    if (!waiting) announced.current = null;
  }, [waiting]);

  const poll = useCallback(async () => {
    try {
      const status = await fetchJob();
      setJob(status);
      // No point re-reading the drives mid-job: nothing may be plugged in or out anyway, and the
      // list walks the whole collection to work out how much room it needs.
      if (status.phase !== "running") setDrives(await fetchDrives());
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

  async function begin(action: () => Promise<JobState>) {
    setConfirming(null);
    setError(null);
    try {
      setJob(await action());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function finish() {
    setJob(await acknowledgeJob());
    void poll();
  }

  if (job && (job.phase === "running" || job.phase === "done" || job.phase === "error")) {
    return <JobView job={job} onFinish={() => void finish()} />;
  }

  async function download() {
    setError(null);
    try {
      await downloadBackupZip();
      setDownloading(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const drive = drives?.drives[0] ?? null;

  return (
    <div className="backup">
      <h3 className="admin__heading">{t.admin.backup.title}</h3>
      <p className="admin__note">{t.admin.backup.intro}</p>

      {error && <p className="admin__error">{error}</p>}
      <Reminder list={drives} />

      <h3 className="admin__heading">{t.admin.backup.whereTo}</h3>
      <div className="sources">
        <button
          type="button"
          className={target === "stick" ? "source source--active" : "source"}
          onClick={() => setTarget("stick")}
        >
          <span className="source__title">{t.admin.backup.toStick}</span>
          <span className="source__hint">{t.admin.backup.toStickHint}</span>
        </button>

        <button
          type="button"
          className={target === "zip" ? "source source--active" : "source"}
          onClick={() => setTarget("zip")}
        >
          <span className="source__title">{t.admin.backup.toZip}</span>
          <span className="source__hint">{t.admin.backup.toZipHint}</span>
        </button>
      </div>

      {target === "zip" ? (
        waiting ? (
          <IncomingCard
            waiting={waiting}
            onRestore={() => void begin(() => restoreFromIncoming(waiting.file))}
            onDownload={() => void download()}
            downloading={downloading}
          />
        ) : (
          <ZipCard downloading={downloading} onStart={() => void download()} />
        )
      ) : !drives ? (
        <p className="admin__note">{t.admin.backup.searching}</p>
      ) : !drive ? (
        <div className="backup__empty">
          <p className="backup__wait">{t.admin.backup.noDrive}</p>
          <p className="admin__note">{t.admin.backup.noDriveHint}</p>
        </div>
      ) : (
        <>
          <DriveCard
            drive={drive}
            list={drives}
            onStart={() => void begin(() => startBackup(drive.path))}
          />

          <section className="backup__restore">
            <h3 className="admin__heading">{t.admin.backup.restoreTitle}</h3>
            <p className="admin__note">{t.admin.backup.restoreIntro}</p>

            {!drive.backup ? (
              <p className="admin__note">{t.admin.backup.restoreNone}</p>
            ) : confirming === drive.path ? (
              <div className="backup__confirm">
                <p className="backup__confirm-title">{t.admin.backup.restoreConfirmTitle}</p>
                <p>
                  {t.admin.backup.restoreConfirm(
                    formatDate(drive.backup.created_at),
                    formatCount(drive.backup.photos),
                  )}
                </p>
                <div className="backup__actions">
                  <button
                    type="button"
                    className="button button--primary"
                    onClick={() => void begin(() => startRestore(drive.path))}
                  >
                    {t.admin.backup.restoreYes}
                  </button>
                  <button type="button" className="button" onClick={() => setConfirming(null)}>
                    {t.admin.backup.restoreNo}
                  </button>
                </div>
              </div>
            ) : (
              <button type="button" className="button" onClick={() => setConfirming(drive.path)}>
                {t.admin.backup.restore}
              </button>
            )}
          </section>
        </>
      )}
    </div>
  );
}

/**
 * Die Fläche, wenn im Eingangsordner eine Sicherung liegt.
 *
 * Sie wird **vorgelegt, nicht eingespielt**. Der Eingangsordner nimmt sonst Fotos auf — das ist
 * hinzufügend und folgenlos —, während dies den ganzen Bestand ersetzt. Deshalb dieselbe
 * Rückfrage mit Datum und Anzahl, die der Stick-Weg schon stellt.
 */
function IncomingCard({
  waiting,
  onRestore,
  onDownload,
  downloading,
}: {
  waiting: WaitingBackup;
  onRestore: () => void;
  onDownload: () => void;
  downloading: boolean;
}) {
  return (
    <div className="backup__drive">
      <p className="backup__drive-name">{t.admin.backup.incomingTitle}</p>
      <p className="backup__confirm-title">
        {t.admin.backup.incomingFound(formatDate(waiting.created_at), formatCount(waiting.photos))}
      </p>

      <button type="button" className="button button--primary backup__start" onClick={onRestore}>
        {t.admin.backup.incomingStart}
      </button>

      <p className="admin__note">{t.admin.backup.incomingWhat}</p>

      {/* Sonst wäre der einzige Moment, in dem man den jetzigen Bestand nicht mehr sichern kann,
          ausgerechnet der unmittelbar vor dem Überschreiben. */}
      <p className="admin__note">{t.admin.backup.incomingDownloadFirst}</p>
      <button type="button" className="button" onClick={onDownload}>
        {t.admin.backup.zipStart}
      </button>
      {downloading && <p className="backup__wait">{t.admin.backup.zipRunning}</p>}
    </div>
  );
}

/**
 * Die Fläche für den Download — an derselben Stelle wie die Laufwerkskachel daneben.
 *
 * Kein Fortschrittsbalken: Der Browser führt die Übertragung und zeigt sie selbst an. Was hier
 * steht, ist die Einordnung — dass jedes Mal alles neu gepackt wird und wie eine solche Datei
 * wieder ins Gerät kommt.
 */
function ZipCard({ downloading, onStart }: { downloading: boolean; onStart: () => void }) {
  return (
    <div className="backup__drive">
      <p className="backup__drive-name">{t.admin.backup.zipTitle}</p>
      <p className="admin__note">{t.admin.backup.zipIntro}</p>

      <button type="button" className="button button--primary backup__start" onClick={onStart}>
        {t.admin.backup.zipStart}
      </button>

      {downloading && <p className="backup__wait">{t.admin.backup.zipRunning}</p>}
      <p className="admin__note">{t.admin.backup.zipRestoreHint}</p>
    </div>
  );
}

function Reminder({ list }: { list: DriveList | null }) {
  if (!list) return null;
  const { reminder } = list;

  if (!reminder.last_backup_at) {
    return <p className="backup__reminder backup__reminder--overdue">{t.admin.backup.lastNever}</p>;
  }
  return (
    <p
      className={
        reminder.overdue ? "backup__reminder backup__reminder--overdue" : "backup__reminder"
      }
    >
      {t.admin.backup.lastOn(formatDate(reminder.last_backup_at), reminder.days_since ?? 0)}
    </p>
  );
}

function DriveCard({
  drive,
  list,
  onStart,
}: {
  drive: DriveItem;
  list: DriveList;
  onStart: () => void;
}) {
  return (
    <div className="backup__drive">
      <p className="backup__drive-name">{drive.name}</p>
      <p className="backup__drive-space">
        {t.admin.backup.free(formatBytes(drive.free_bytes))} —{" "}
        {drive.enough_space
          ? t.admin.backup.enough(formatCount(list.photos))
          : t.admin.backup.notEnough(formatBytes(list.needed_bytes))}
      </p>

      {drive.backup && (
        <p className="admin__note">
          {t.admin.backup.existing(
            formatDate(drive.backup.created_at),
            formatCount(drive.backup.photos),
          )}
        </p>
      )}

      {/* No button that leads nowhere: a stick that is too small cannot be written to. */}
      <button
        type="button"
        className="button button--primary backup__start"
        onClick={onStart}
        disabled={!drive.enough_space}
      >
        {drive.backup ? t.admin.backup.startAgain : t.admin.backup.start}
      </button>
    </div>
  );
}

function JobView({ job, onFinish }: { job: JobState; onFinish: () => void }) {
  const share = job.total > 0 ? job.done / job.total : 0;

  return (
    <div className="backup">
      <h3 className="admin__heading">{t.admin.backup.title}</h3>

      {job.phase === "running" && (
        <>
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
          <p className="admin__note">{t.admin.backup.cancelHint}</p>
        </>
      )}

      {job.phase === "done" && (
        <div className="backup__done">
          <span className="backup__check" aria-hidden="true">
            ✓
          </span>
          <p>{job.message}</p>
          <button type="button" className="button button--primary" onClick={onFinish}>
            {t.admin.backup.done}
          </button>
        </div>
      )}

      {job.phase === "error" && (
        <>
          <p className="admin__error">{job.error}</p>
          <button type="button" className="button" onClick={onFinish}>
            {t.admin.backup.done}
          </button>
        </>
      )}
    </div>
  );
}
