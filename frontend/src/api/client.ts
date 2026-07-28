/** Zugriff auf das Backend. Die Typen spiegeln backend/app/schemas.py. */

export type PhotoMarker = {
  id: number;
  lat: number;
  lon: number;
  title: string | null;
  /** Fertig formuliert ("1932", "1920er") -- das Frontend rechnet nicht mit Daten. */
  date_label: string;
  width: number;
  height: number;
  thumb_url: string;
};

export type PhotoListe = {
  photos: PhotoMarker[];
  total: number;
  /** Wahr, wenn die Obergrenze gegriffen hat: dann sollte zum Hineinzoomen aufgefordert werden. */
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

export type Jahrzehnt = { decade: number; count: number };

export type Histogramm = {
  decades: Jahrzehnt[];
  /** Fotos ohne Datierung: nicht auf der Zeitleiste, aber im "Hilf mit"-Bereich. */
  undated: number;
  earliest: number | null;
  latest: number | null;
};

/** [minLon, minLat, maxLon, maxLat] */
export type Bbox = [number, number, number, number];

export type Zeitraum = { von: number; bis: number };

async function hole<T>(pfad: string, signal?: AbortSignal): Promise<T> {
  const antwort = await fetch(pfad, { signal });
  if (!antwort.ok) {
    let grund = `HTTP ${antwort.status}`;
    try {
      const koerper = (await antwort.json()) as { detail?: string };
      if (koerper.detail) grund = koerper.detail;
    } catch {
      /* Antwort ohne JSON -- der Statuscode muss reichen. */
    }
    throw new Error(grund);
  }
  return (await antwort.json()) as T;
}

function bboxParam(bbox: Bbox): string {
  // Fünf Nachkommastellen sind gut einen Meter genau. Mehr macht die URL nur lang und verhindert,
  // dass gleiche Ausschnitte als gleich erkannt werden.
  return bbox.map((wert) => wert.toFixed(5)).join(",");
}

function mitZeitraum(params: URLSearchParams, zeitraum: Zeitraum | null): URLSearchParams {
  if (zeitraum) {
    params.set("von", String(zeitraum.von));
    params.set("bis", String(zeitraum.bis));
  }
  return params;
}

export function ladePhotos(
  bbox: Bbox,
  zeitraum: Zeitraum | null,
  limit: number,
  signal?: AbortSignal,
): Promise<PhotoListe> {
  const params = mitZeitraum(new URLSearchParams({ bbox: bboxParam(bbox) }), zeitraum);
  params.set("limit", String(limit));
  return hole<PhotoListe>(`/api/photos?${params}`, signal);
}

/** Ohne Zeitraum: der Schieber soll zeigen, wo überhaupt etwas liegt. */
export function ladeHistogramm(bbox: Bbox, signal?: AbortSignal): Promise<Histogramm> {
  return hole<Histogramm>(`/api/photos/histogram?bbox=${bboxParam(bbox)}`, signal);
}

export function ladeDetail(id: number, signal?: AbortSignal): Promise<PhotoDetail> {
  return hole<PhotoDetail>(`/api/photos/${id}`, signal);
}

// --- "Hilf mit" -------------------------------------------------------------

export type Bedarf = "location" | "date";

export type Aufgabe = {
  need: Bedarf;
  /** Wie viele Fotos dieser Art noch offen sind. Motiviert. */
  open_count: number;
  /** null heißt: es fehlt nichts mehr. Ein schöner Zustand. */
  photo: PhotoDetail | null;
};

export type Ort = {
  id: number;
  name: string;
  lat: number;
  lon: number;
  kind: string;
};

export type Genauigkeit = "day" | "month" | "year" | "decade";

async function sende<T>(pfad: string, koerper: unknown): Promise<T> {
  const antwort = await fetch(pfad, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(koerper),
  });
  if (!antwort.ok) {
    let grund = `HTTP ${antwort.status}`;
    try {
      const daten = (await antwort.json()) as { detail?: string };
      if (daten.detail) grund = daten.detail;
    } catch {
      /* Antwort ohne JSON */
    }
    throw new Error(grund);
  }
  return (await antwort.json()) as T;
}

export function ladeAufgabe(
  bedarf: Bedarf,
  uebersprungen: number[],
  signal?: AbortSignal,
): Promise<Aufgabe> {
  const params = new URLSearchParams({ need: bedarf });
  if (uebersprungen.length) params.set("exclude", uebersprungen.join(","));
  return hole<Aufgabe>(`/api/contribute/next?${params}`, signal);
}

export function sendeOrt(
  id: number,
  daten: { lat: number; lon: number; place_name?: string; session_id?: string },
): Promise<PhotoDetail> {
  return sende<PhotoDetail>(`/api/contribute/${id}/location`, daten);
}

export function sendeDatum(
  id: number,
  daten: { year: number; precision: Genauigkeit; session_id?: string },
): Promise<PhotoDetail> {
  return sende<PhotoDetail>(`/api/contribute/${id}/date`, daten);
}

export function sucheOrte(anfrage: string, signal?: AbortSignal): Promise<Ort[]> {
  return hole<Ort[]>(`/api/places?q=${encodeURIComponent(anfrage)}`, signal);
}
