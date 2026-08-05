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

import {
  type ImportFolder,
  type ImportFolders,
  type JobState,
  fetchImportFolders,
  fetchJob,
} from "../api/admin";
import { t } from "../text/de";
import { DropZone } from "./DropZone";

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
  const [found, setFound] = useState<ImportFolders | null>(null);
  const [error, setError] = useState<string | null>(null);

  const poll = useCallback(async () => {
    try {
      const status = await fetchJob();
      if (status.kind === "import" && status.phase !== "idle") onJob(status);
      // Während gelesen wird ändert sich die Ordnerliste nicht -- und sie durchsucht den Stick.
      if (status.phase !== "running") setFound(await fetchImportFolders());
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

  if (error) return <p className="admin__error">{error}</p>;

  // Drei Zustaende, nicht zwei: eine leere Ordnerliste heisst entweder "kein Stick" oder "Stick
  // ohne Bilder", und wer gerade eingesteckt hat, darf nicht "Bitte einstecken" lesen.
  if (!found) return <DropZone title={t.admin.stick.searching} />;

  if (found.drives.length === 0) {
    return <DropZone title={t.admin.stick.waitTitle} hint={t.admin.stick.waitHint} />;
  }

  if (found.folders.length === 0) {
    return (
      <DropZone
        title={t.admin.stick.noImages(found.drives.join(", "))}
        hint={t.admin.stick.noImagesHint}
      />
    );
  }

  return (
    <DropZone filled>
      <ul className="photo-rows">
        {found.folders.map((folder) => (
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
    </DropZone>
  );
}
