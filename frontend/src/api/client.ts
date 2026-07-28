/** Backend access. The types mirror backend/app/schemas.py. */

export type PhotoMarker = {
  id: number;
  lat: number;
  lon: number;
  title: string | null;
  /** Ready-made German label ("1932", "1920er") -- the frontend does no date arithmetic. */
  date_label: string;
  width: number;
  height: number;
  thumb_url: string;
};

export type PhotoList = {
  photos: PhotoMarker[];
  total: number;
  /** True when the limit kicked in: then the map should invite zooming in. */
  truncated: boolean;
};

export type PhotoDetail = {
  id: number;
  title: string | null;
  description: string | null;
  date_label: string;
  date_precision: string;
  lat: number | null;
  lon: number | null;
  place_name: string | null;
  original_filename: string;
  width: number;
  height: number;
  tags: string[];
  needs_location: boolean;
  needs_date: boolean;
  image_url: string;
  thumb_url: string;
};

export type DecadeCount = { decade: number; count: number };

export type Histogram = {
  decades: DecadeCount[];
  /** Photos without a date: not on the timeline, but in the "Hilf mit" panel. */
  undated: number;
  earliest: number | null;
  latest: number | null;
};

/** [minLon, minLat, maxLon, maxLat] */
export type Bbox = [number, number, number, number];

export type TimeRange = { from: number; to: number };

export type Need = "location" | "date";

export type Task = {
  need: Need;
  /** How many photos of this kind are still open. It motivates. */
  open_count: number;
  /** null means nothing is missing any more. A pleasant state. */
  photo: PhotoDetail | null;
};

export type Place = {
  id: number;
  name: string;
  lat: number;
  lon: number;
  kind: string;
};

export type Precision = "day" | "month" | "year" | "decade";

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    if (body.detail) return body.detail;
  } catch {
    /* response without JSON -- the status code has to do */
  }
  return `HTTP ${response.status}`;
}

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal });
  if (!response.ok) throw new Error(await readError(response));
  return (await response.json()) as T;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(await readError(response));
  return (await response.json()) as T;
}

function bboxParam(bbox: Bbox): string {
  // Five decimal places is about a metre. More only makes the URL long and stops equal viewports
  // from being recognised as equal.
  return bbox.map((value) => value.toFixed(5)).join(",");
}

export function fetchPhotos(
  bbox: Bbox,
  timeRange: TimeRange | null,
  limit: number,
  signal?: AbortSignal,
): Promise<PhotoList> {
  const params = new URLSearchParams({ bbox: bboxParam(bbox), limit: String(limit) });
  if (timeRange) {
    params.set("from_year", String(timeRange.from));
    params.set("to_year", String(timeRange.to));
  }
  return getJson<PhotoList>(`/api/photos?${params}`, signal);
}

/** Without a time range: the slider should show where anything is at all. */
export function fetchHistogram(bbox: Bbox, signal?: AbortSignal): Promise<Histogram> {
  return getJson<Histogram>(`/api/photos/histogram?bbox=${bboxParam(bbox)}`, signal);
}

export function fetchPhoto(id: number, signal?: AbortSignal): Promise<PhotoDetail> {
  return getJson<PhotoDetail>(`/api/photos/${id}`, signal);
}

export function fetchTask(need: Need, skipped: number[], signal?: AbortSignal): Promise<Task> {
  const params = new URLSearchParams({ need });
  if (skipped.length) params.set("exclude", skipped.join(","));
  return getJson<Task>(`/api/contribute/next?${params}`, signal);
}

export function postLocation(
  id: number,
  body: { lat: number; lon: number; place_name?: string; session_id?: string },
): Promise<PhotoDetail> {
  return postJson<PhotoDetail>(`/api/contribute/${id}/location`, body);
}

export function postDate(
  id: number,
  body: { year: number; precision: Precision; session_id?: string },
): Promise<PhotoDetail> {
  return postJson<PhotoDetail>(`/api/contribute/${id}/date`, body);
}

export function searchPlaces(query: string, signal?: AbortSignal): Promise<Place[]> {
  return getJson<Place[]>(`/api/places?q=${encodeURIComponent(query)}`, signal);
}
