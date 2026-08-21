// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Choosing a folder on a plugged-in USB stick.
 *
 * The choice only -- progress and result belong to `ImportView` since the rebuild, because there
 * they hold for both routes. What stays here is what concerns the stick alone: looking for the
 * folders while somebody stands in front of it, and reporting when the job inside the device is
 * through.
 *
 * **Nothing on the stick is changed.** Unlike the watched inbox, where what was taken in gets
 * moved aside -- somebody else's drive is only read.
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

/** Is one plugged in? Faster while reading, so the bar keeps moving. */
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
  /** Reports every job state -- ImportView decides what becomes of it. */
  onJob: (state: JobState) => void;
  /** True while a job runs: then only the progress is polled. */
  watching?: boolean;
}) {
  const [found, setFound] = useState<ImportFolders | null>(null);
  const [error, setError] = useState<string | null>(null);

  const poll = useCallback(async () => {
    try {
      const status = await fetchJob();
      if (status.kind === "import" && status.phase !== "idle") onJob(status);
      // While reading, the folder list does not change -- and finding it walks the stick.
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

  // Three states, not two: an empty folder list means either "no stick" or "stick without
  // pictures", and whoever just plugged one in must not read "Bitte einstecken".
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
