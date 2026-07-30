/**
 * Die Ordnerauswahl auf einem eingesteckten USB-Stick.
 *
 * Nur die Auswahl — Fortschritt und Ergebnis gehören seit dem Umbau nach `ImportView`, weil sie
 * dort für beide Wege gelten. Was hier bleibt, ist das, was nur den Stick betrifft: die Ordner
 * suchen, während jemand davorsteht, und melden, wenn der Auftrag im Gerät durch ist.
 *
 * **Auf dem Stick wird nichts verändert.** Anders als im überwachten Eingangsordner, wo
 * Aufgenommenes beiseitegeräumt wird — ein fremder Datenträger wird nur gelesen.
 */

import { useCallback, useEffect, useState } from "react";

import { type ImportFolder, type JobState, fetchImportFolders, fetchJob } from "../api/admin";
import { t } from "../texte/de";

/** Steckt einer? Während gelesen wird schneller, damit der Balken läuft. */
const IDLE_POLL_MS = 4000;
const BUSY_POLL_MS = 800;

export function StickFolders({
  selected,
  onSelect,
  onJob,
  watching = false,
}: {
  selected: ImportFolder | null;
  onSelect: (folder: ImportFolder) => void;
  /** Meldet jeden Auftragsstand -- ImportView entscheidet, was daraus wird. */
  onJob: (state: JobState) => void;
  /** True, solange ein Auftrag läuft: dann wird nur noch der Fortschritt abgefragt. */
  watching?: boolean;
}) {
  const [folders, setFolders] = useState<ImportFolder[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const poll = useCallback(async () => {
    try {
      const status = await fetchJob();
      if (status.kind === "import" && status.phase !== "idle") onJob(status);
      // Während gelesen wird ändert sich die Ordnerliste nicht -- und sie durchsucht den Stick.
      if (status.phase !== "running") setFolders(await fetchImportFolders());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [onJob]);

  useEffect(() => {
    void poll();
    const timer = setInterval(() => void poll(), watching ? BUSY_POLL_MS : IDLE_POLL_MS);
    return () => clearInterval(timer);
  }, [poll, watching]);

  if (watching) return null;

  return (
    <div className="stick">
      {error && <p className="admin__error">{error}</p>}

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
                <span className="photo-row__meta">{t.admin.stick.images(folder.images)}</span>
              </div>
              <button
                type="button"
                className={selected?.path === folder.path ? "button button--primary" : "button"}
                onClick={() => onSelect(folder)}
              >
                {selected?.path === folder.path ? t.admin.stick.chosen : t.admin.stick.choose}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
