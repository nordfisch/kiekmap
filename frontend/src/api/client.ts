/** Backend access. The types mirror backend/app/schemas.py. */

export type PhotoMarker = {
  id: number;
  lat: number;
  lon: number;
  title: string | null;
  /** The address under the thumbnail. Absent for a photo located from EXIF alone. */
  place_name: string | null;
  /** Spelled out, for screen readers. What is *shown* is `date_short`. */
  date_label: string;
  /** The same dating as it fits on a map: the year, a decade as "1930er", undated empty. */
  date_short: string;
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
  /** Credit line, shown in the detail view below the description. */
  credit: string | null;
  date_from: string | null;
  date_to: string | null;
  date_label: string;
  date_precision: string;
  lat: number | null;
  lon: number | null;
  place_name: string | null;
  location_accuracy_m: number | null;
  title_source: string | null;
  date_source: string | null;
  location_source: string | null;
  /** For a scan, the date of the scanning run -- shown to the curator, never used as a dating. */
  exif_datetime: string | null;
  original_filename: string;
  /** The photo's identity independent of any database -- the file name is this hash. */
  sha256: string;
  imported_at: string;
  width: number;
  height: number;
  tags: string[];
  needs_location: boolean;
  needs_date: boolean;
  status: string;
  image_url: string;
  thumb_url: string;
};

export type Bar = { year: number; count: number };

export type Histogram = {
  bars: Bar[];
  /**
   * How many years one bar covers.
   *
   * Follows the collection instead of being fixed at a decade: as long as every dating fits inside
   * a year, the bars are yearly. See `bar_width` in `app/services/dates.py`.
   */
  step: number;
  /** Photos without a date: not on the timeline, but in the "Hilf mit" panel. */
  undated: number;
  /**
   * Span of the whole collection -- the axis of the time slider.
   *
   * The bars show the map viewport, the axis does not: it must not shift under the visitor's
   * hand. See kiosk/timeAxis.ts.
   */
  collection_from: number | null;
  collection_to: number | null;
};

/** [minLon, minLat, maxLon, maxLat] */
export type Bbox = [number, number, number, number];

export type TimeRange = { from: number; to: number };

export type Need = "location" | "date";

export type Task = {
  need: Need;
  /** How many photos of this kind are still open. It motivates. */
  open_count: number;
  /** Open tasks of the other question -- says whether "Weiß ich nicht" still leads anywhere. */
  open_other: number;
  /** null means nothing is missing any more. A pleasant state. */
  photo: PhotoDetail | null;
};

export type Place = {
  id: number;
  name: string;
  lat: number;
  lon: number;
  kind: string;
  /** Only for kind="adresse": the number on its own, for a button that reads "12". */
  housenumber: string | null;
  /** How precise this point is, in metres. Travels along with the contribution. */
  accuracy_m: number | null;
};

export type Precision = "day" | "month" | "year" | "decade";

/** The backend's `detail` if there is one -- it is written for the reader, the status code is not. */
export async function readError(response: Response): Promise<string> {
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
  showUndated: boolean,
  signal?: AbortSignal,
): Promise<PhotoList> {
  const params = new URLSearchParams({ bbox: bboxParam(bbox), limit: String(limit) });
  if (timeRange) {
    params.set("from_year", String(timeRange.from));
    params.set("to_year", String(timeRange.to));
  }
  // Sent even when it is on, which is the default: the parameter is what the switch beside the
  // slider stands for, and a request that leaves it out says nothing about it either way.
  params.set("include_undated", String(showUndated));
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
  body: {
    lat: number;
    lon: number;
    place_name?: string;
    accuracy_m?: number;
    session_id?: string;
  },
): Promise<PhotoDetail> {
  return postJson<PhotoDetail>(`/api/contribute/${id}/location`, body);
}

export function postDate(
  id: number,
  body: { year: number; precision: Precision; session_id?: string },
): Promise<PhotoDetail> {
  return postJson<PhotoDetail>(`/api/contribute/${id}/date`, body);
}

/** Free search over the gazetteer. Used by the admin area, which has a keyboard. */
export function searchPlaces(query: string, signal?: AbortSignal): Promise<Place[]> {
  return getJson<Place[]>(`/api/places?q=${encodeURIComponent(query)}`, signal);
}

/**
 * The streets the visitor can choose from, alphabetically.
 *
 * Which ones and how many the backend decides -- the nearest to the village centre, as many as
 * `streetChoice` in `region.json` says. Fetched once; a village fits in a few kilobytes.
 */
export function fetchStreets(signal?: AbortSignal): Promise<Place[]> {
  return getJson<Place[]>("/api/places/streets", signal);
}

/**
 * The house numbers of one street -- the second step of locating.
 *
 * By the street's id, not its name: the name would be going back out of the browser and is input,
 * not a fact.
 */
export function fetchHouseNumbers(placeId: number, signal?: AbortSignal): Promise<Place[]> {
  return getJson<Place[]>(`/api/places/${placeId}/housenumbers`, signal);
}
