/**
 * What the stick card offers, and what the progress view is called.
 *
 * Kept out of `Backup.tsx` so that the decisions can be tested without rendering the screen.
 */

import type { DriveItem, JobState } from "../api/admin";
import { t } from "../text";

/**
 * - `nothing`: the device holds no photos. A backup would replace the records on the stick with
 *   an empty database -- on a fresh device, whose next step is to restore from that very stick.
 * - `ask`: the stick holds more photos than the device. Replacing that is sometimes right, more
 *   often the wrong stick or the wrong device, so it is asked first.
 * - `backup`: the ordinary case.
 *
 * The backend refuses the first two as well; see `check_backup` in services/backup/write.py.
 */
export type DriveOffer = "nothing" | "ask" | "backup";

export function driveOffer(drive: DriveItem, photos: number): DriveOffer {
  if (photos === 0) return "nothing";
  if (drive.backup && drive.backup.photos > photos) return "ask";
  return "backup";
}

/** One progress view serves every job, and a restore is not a backup. */
export function jobTitle(kind: JobState["kind"]): string {
  return kind === "restore" ? t.admin.backup.restoreRunningTitle : t.admin.backup.title;
}
