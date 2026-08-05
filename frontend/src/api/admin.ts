/**
 * Backend access for the admin area. The types mirror backend/app/schemas.py.
 *
 * Everything except signing in goes through `adminFetch`, for one reason: a session that has
 * expired must not surface as an error message somewhere in a list. It has to put the PIN pad
 * back on screen -- which is what `onAdminSignedOut` is for.
 */

import { PAGE_SIZE } from "../admin/pagination";
import { t } from "../text/de";
import { type PhotoDetail, readError } from "./client";

export type AdminSession = { token: string; expires_in_s: number };

export type BackupReminder = {
  last_backup_at: string | null;
  last_drive: string;
  days_since: number | null;
  /** True when it is time -- and also when there has never been a backup at all. */
  overdue: boolean;
};

export type Overview = {
  total: number;
  on_map: number;
  without_location: number;
  without_date: number;
  deleted: number;
  visitor_changes: number;
  /** Days already worked out: see services/dates.days_since in the backend. */
  days_since_import: number | null;
  days_since_change: number | null;
  backup: BackupReminder;
};

export type BackupOnDrive = {
  created_at: string;
  photos: number;
  bytes: number;
  place: string;
};

export type DriveItem = {
  path: string;
  name: string;
  total_bytes: number;
  free_bytes: number;
  /** Room for the whole collection, not just for what is still missing. */
  enough_space: boolean;
  backup: BackupOnDrive | null;
};

/** A backup waiting in the inbox as a ZIP file for somebody to confirm it. */
export type WaitingBackup = BackupOnDrive & { file: string };

export type DriveList = {
  drives: DriveItem[];
  photos: number;
  needed_bytes: number;
  reminder: BackupReminder;
  incoming: WaitingBackup | null;
};

/** How far along backup or restore is. `phase` is idle | running | done | error. */
export type JobState = {
  kind: string;
  phase: string;
  done: number;
  total: number;
  message: string;
  error: string | null;
  /** Rows for the review table, when there were few enough. See REVIEW_LIMIT in the backend. */
  items: UploadItem[] | null;
};

export type PhotoAdminItem = {
  id: number;
  title: string | null;
  date_label: string;
  place_name: string | null;
  thumb_url: string;
  needs_location: boolean;
  needs_date: boolean;
  status: string;
  original_filename: string;
  imported_at: string;
};

export type PhotoAdminList = { photos: PhotoAdminItem[]; total: number };

export type ChangeItem = {
  id: number;
  photo_id: number;
  photo_title: string | null;
  thumb_url: string;
  field: string;
  old_value: string | null;
  new_value: string | null;
  source: string;
  created_at: string;
  reverted_at: string | null;
  revertable: boolean;
};

/** The total is for the filter, not for the page -- the page count comes out of it. */
export type ChangeList = {
  changes: ChangeItem[];
  total: number;
};

export type ImportLogItem = {
  id: number;
  filename: string;
  result: string;
  message: string | null;
  photo_id: number | null;
  created_at: string;
};

export type ImportLogList = {
  entries: ImportLogItem[];
  total: number;
};

export type UploadItem = {
  filename: string;
  result: string;
  message: string;
  photo: PhotoDetail | null;
};

export type UploadResult = {
  items: UploadItem[];
  imported: number;
  duplicates: number;
  rejected: number;
};

/** Batch statements that apply to every file of one upload. */
export type BatchDefaults = {
  year?: number;
  precision?: "year" | "decade";
  lat?: number;
  lon?: number;
  placeName?: string;
  credit?: string;
  provenance?: string;
};

/**
 * A photo as the admin area sees it.
 *
 * `provenance` is the reason for the separate type: where the picture came from and whether there
 * is a release is none of the visitor screen's business -- the kiosk endpoints return
 * `PhotoDetail`, which has no such field in the first place.
 */
export type PhotoAdminDetail = PhotoDetail & { provenance: string | null };

export type PhotoPatch = {
  title?: string | null;
  description?: string | null;
  credit?: string | null;
  provenance?: string | null;
  /** null clears the dating; leaving the key out keeps it. See backend PhotoUpdate. */
  date?: {
    year: number;
    month?: number;
    day?: number;
    precision: string;
  } | null;
  location?: { lat: number; lon: number; place_name?: string | null } | null;
  tags?: string[];
  status?: "published" | "deleted";
};

export type Selection = "all" | "without_location" | "without_date" | "deleted";

let token: string | null = null;
let signedOutHandler: (() => void) | null = null;
let activityHandler: (() => void) | null = null;

export function setAdminToken(next: string | null): void {
  token = next;
}

/** Called when the backend refuses the token -- the UI has to ask for the PIN again. */
export function onAdminSignedOut(handler: () => void): void {
  signedOutHandler = handler;
}

/** Called after every accepted request: the backend has just pushed the expiry back too. */
export function onAdminActivity(handler: () => void): void {
  activityHandler = handler;
}

async function adminFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api/admin${path}`, {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      ...(token ? { "X-Admin-Token": token } : {}),
    },
  });

  if (response.status === 401) {
    setAdminToken(null);
    signedOutHandler?.();
    throw new Error(t.admin.expired);
  }
  if (!response.ok) throw new Error(await readError(response));

  activityHandler?.();
  // 204: logout has no body.
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

/** Not via adminFetch: there is no token yet, and a 401 here means "wrong PIN", not "expired". */
export async function signIn(pin: string): Promise<AdminSession> {
  const response = await fetch("/api/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin }),
  });
  if (!response.ok) throw new Error(await readError(response));
  return (await response.json()) as AdminSession;
}

export function signOut(): Promise<void> {
  return adminFetch<void>("/logout", { method: "POST" });
}

/** After a page reload: is the stored token still good? */
export function checkSession(): Promise<AdminSession> {
  return adminFetch<AdminSession>("/session");
}

export function fetchOverview(): Promise<Overview> {
  return adminFetch<Overview>("/overview");
}

export function fetchAdminPhotos(
  show: Selection,
  query: string,
  offset = 0,
  limit = PAGE_SIZE,
): Promise<PhotoAdminList> {
  const params = new URLSearchParams({
    show,
    limit: String(limit),
    offset: String(offset),
  });
  if (query.trim()) params.set("q", query.trim());
  return adminFetch<PhotoAdminList>(`/photos?${params}`);
}

export function fetchAdminPhoto(id: number): Promise<PhotoAdminDetail> {
  return adminFetch<PhotoAdminDetail>(`/photos/${id}`);
}

export function patchPhoto(id: number, patch: PhotoPatch): Promise<PhotoAdminDetail> {
  return adminFetch<PhotoAdminDetail>(`/photos/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export function fetchChanges(includeReverted = false, offset = 0): Promise<ChangeList> {
  const params = new URLSearchParams({
    include_reverted: String(includeReverted),
    limit: String(PAGE_SIZE),
    offset: String(offset),
  });
  return adminFetch<ChangeList>(`/changes?${params}`);
}

export function revertChange(id: number): Promise<PhotoAdminDetail> {
  return adminFetch<PhotoAdminDetail>(`/changes/${id}/revert`, {
    method: "POST",
  });
}

export function fetchImportLog(result?: string, offset = 0): Promise<ImportLogList> {
  const params = new URLSearchParams({
    limit: String(PAGE_SIZE),
    offset: String(offset),
  });
  if (result) params.set("result", result);
  return adminFetch<ImportLogList>(`/imports?${params}`);
}

// --- backup onto a USB stick ------------------------------------------------
//
// Backup and restore run in a thread on the device and take minutes. The screen therefore starts
// them and then asks how far along they are -- one request could not carry that, and it would run
// into a proxy timeout on the way.

export function fetchDrives(): Promise<DriveList> {
  return adminFetch<DriveList>("/backup/drives");
}

export function startBackup(path: string): Promise<JobState> {
  return adminFetch<JobState>("/backup/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
}

export function startRestore(path: string): Promise<JobState> {
  return adminFetch<JobState>("/backup/restore", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
}

export type ImportFolder = {
  path: string;
  /** Relative to the drive: "Scans2024/Kirchweih". */
  name: string;
  drive: string;
  images: number;
};

/**
 * The drive names come along.
 *
 * An empty folder list would otherwise mean two things: no stick, or a stick without pictures.
 * The screen would answer somebody who just plugged one in with "Bitte USB-Stick einstecken".
 */
export type ImportFolders = {
  drives: string[];
  folders: ImportFolder[];
};

export function fetchImportFolders(): Promise<ImportFolders> {
  return adminFetch<ImportFolders>("/import/folders");
}

/** Same batch statements as the upload -- they apply to the whole folder. */
export function startStickImport(path: string, defaults: BatchDefaults): Promise<JobState> {
  return adminFetch<JobState>("/import/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path,
      ...(defaults.year !== undefined
        ? { year: defaults.year, precision: defaults.precision ?? "year" }
        : {}),
      ...(defaults.lat !== undefined && defaults.lon !== undefined
        ? { lat: defaults.lat, lon: defaults.lon }
        : {}),
      ...(defaults.placeName ? { place_name: defaults.placeName } : {}),
      ...(defaults.credit ? { credit: defaults.credit } : {}),
      ...(defaults.provenance ? { provenance: defaults.provenance } : {}),
    }),
  });
}

export function fetchJob(): Promise<JobState> {
  return adminFetch<JobState>("/backup/status");
}

/** Tell the device the result has been seen, so the screen goes back to the start. */
/** Restores a backup lying in the inbox. Replaces the entire collection. */
export function restoreFromIncoming(file: string): Promise<JobState> {
  return adminFetch<JobState>("/backup/incoming/restore", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file }),
  });
}

export function acknowledgeJob(): Promise<JobState> {
  return adminFetch<JobState>("/backup/acknowledge", { method: "POST" });
}

/**
 * Download the backup as one file.
 *
 * The detour through a ticket has a reason: the browser runs the download, and there is no way to
 * give it an `X-Admin-Token`. Putting the session token into the address would be shorter and
 * wrong -- addresses end up in history and in logs. The ticket is good for one minute and exactly
 * one download.
 *
 * Fetched through an invisible link rather than `fetch`: otherwise the whole archive would sit in
 * the browser's memory before anybody saw any of it -- several gigabytes at two thousand photos.
 */
export async function downloadBackupZip(): Promise<void> {
  const { ticket } = await adminFetch<{ ticket: string; expires_in_s: number }>(
    "/backup/zip/ticket",
    { method: "POST" },
  );

  const link = document.createElement("a");
  link.href = `/api/admin/backup/zip?ticket=${encodeURIComponent(ticket)}`;
  link.download = "";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

/**
 * Upload a single file.
 *
 * One request per file, although the endpoint would take a list: this is what lets the screen
 * count "Bild 7 von 40". A batch of scans is quickly a gigabyte, and one request that large would
 * show nothing at all for minutes.
 */
export function uploadPhoto(file: File, defaults: BatchDefaults): Promise<UploadResult> {
  const form = new FormData();
  form.append("files", file, file.name);
  if (defaults.year !== undefined) {
    form.append("year", String(defaults.year));
    form.append("precision", defaults.precision ?? "year");
  }
  if (defaults.lat !== undefined && defaults.lon !== undefined) {
    form.append("lat", String(defaults.lat));
    form.append("lon", String(defaults.lon));
  }
  if (defaults.placeName) form.append("place_name", defaults.placeName);
  if (defaults.credit) form.append("credit", defaults.credit);
  if (defaults.provenance) form.append("provenance", defaults.provenance);

  return adminFetch<UploadResult>("/upload", { method: "POST", body: form });
}
