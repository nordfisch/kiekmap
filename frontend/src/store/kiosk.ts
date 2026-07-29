/**
 * State of the visitor view.
 *
 * Two loops run here at different speeds:
 *
 *   slow  viewport or time range changes -> one query after a short pause
 *   fast  the map is panned -> the photos already loaded are re-clustered
 *
 * Without that separation every twitch on the touchscreen would fire a request.
 */

import { create } from "zustand";

import {
  type Bbox,
  type Histogram,
  type PhotoMarker,
  type TimeRange,
  fetchHistogram,
  fetchPhotos,
} from "../api/client";

/** How long the map has to stand still before loading. */
export const DEBOUNCE_MS = 250;

/** More markers make no sense on a map -- and the Pi should stay responsive. */
export const MAX_PHOTOS = 500;

type KioskState = {
  bbox: Bbox | null;
  timeRange: TimeRange | null;
  /** The full span from the histogram. The slider cannot go beyond it. */
  fullRange: TimeRange | null;

  photos: PhotoMarker[];
  total: number;
  truncated: boolean;
  histogram: Histogram | null;

  loading: boolean;
  error: string | null;

  /** Id of the photo shown full screen, or null. */
  openPhotoId: number | null;

  setViewport: (bbox: Bbox) => void;
  setTimeRange: (timeRange: TimeRange) => void;
  openPhoto: (id: number | null) => void;
  refresh: () => void;
  reset: () => void;
};

let photoAbort: AbortController | null = null;
let histogramAbort: AbortController | null = null;
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

export function sameViewport(a: Bbox | null, b: Bbox | null): boolean {
  if (!a || !b) return a === b;
  return a.every((value, index) => Math.abs(value - b[index]!) < 1e-5);
}

/**
 * Which time filter goes to the backend.
 *
 * When the selection covers the whole known span the filter has no effect -- then better send
 * none. This is not a speed trick: with a filter, photos whose dating reaches beyond the span
 * would drop out. The visitor who set nothing should see everything.
 */
export function queryTimeFilter(
  timeRange: TimeRange | null,
  fullRange: TimeRange | null,
): TimeRange | null {
  if (!timeRange || !fullRange) return null;
  const coversEverything = timeRange.from <= fullRange.from && timeRange.to >= fullRange.to;
  return coversEverything ? null : timeRange;
}

export const useKiosk = create<KioskState>((set, get) => {
  async function loadPhotos() {
    const { bbox, timeRange, fullRange } = get();
    if (!bbox) return;

    // Discard superseded requests: on a touchscreen people swipe in quick succession, and the
    // answer for a long-abandoned viewport must not overwrite the current one.
    photoAbort?.abort();
    photoAbort = new AbortController();
    const signal = photoAbort.signal;

    set({ loading: true, error: null });
    try {
      const list = await fetchPhotos(
        bbox,
        queryTimeFilter(timeRange, fullRange),
        MAX_PHOTOS,
        signal,
      );
      set({
        photos: list.photos,
        total: list.total,
        truncated: list.truncated,
        loading: false,
      });
    } catch (e) {
      if (signal.aborted) return;
      set({ loading: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  async function loadHistogram(bbox: Bbox) {
    histogramAbort?.abort();
    histogramAbort = new AbortController();
    const signal = histogramAbort.signal;

    try {
      const histogram = await fetchHistogram(bbox, signal);
      if (signal.aborted) return;

      const { timeRange } = get();
      const span =
        histogram.earliest !== null && histogram.latest !== null
          ? { from: histogram.earliest, to: histogram.latest }
          : null;

      set({
        histogram,
        fullRange: span,
        // First time round, select the whole span: the visitor should see everything first and
        // narrow down afterwards, not the other way round. A selection already made stays
        // untouched, even when the span changes while panning the map.
        timeRange: timeRange ?? span,
      });
    } catch {
      /* Without a histogram the slider stays empty -- the map keeps working. */
    }
  }

  function scheduleLoad() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      debounceTimer = null;
      void loadPhotos();
    }, DEBOUNCE_MS);
  }

  return {
    bbox: null,
    timeRange: null,
    fullRange: null,
    photos: [],
    total: 0,
    truncated: false,
    histogram: null,
    loading: false,
    error: null,
    openPhotoId: null,

    setViewport(bbox) {
      if (sameViewport(get().bbox, bbox)) return;
      set({ bbox });
      scheduleLoad();
      void loadHistogram(bbox);
    },

    setTimeRange(timeRange) {
      const current = get().timeRange;
      if (current && current.from === timeRange.from && current.to === timeRange.to) return;
      set({ timeRange });
      scheduleLoad();
    },

    openPhoto(id) {
      set({ openPhotoId: id });
    },

    /**
     * Reload after something outside the map changed the collection.
     *
     * The "Hilf mit" panel is the case this exists for. It promises "Das Foto ist jetzt auf der
     * Karte" -- and without this the promise only came true once somebody happened to pan the
     * map, which is exactly what the older visitors it is written for do not do.
     *
     * The histogram goes along: a photo that has just been dated moves out of ``undated`` and
     * into a decade bar. Whatever time range the visitor has set stays untouched -- see
     * ``loadHistogram``.
     *
     * Not debounced, unlike the map: a contribution is one deliberate act, and the whole point is
     * that it shows up immediately.
     */
    refresh() {
      const { bbox } = get();
      if (!bbox) return;
      void loadPhotos();
      void loadHistogram(bbox);
    },

    /** For the idle reset: back to the state the device should be in each morning. */
    reset() {
      const { fullRange } = get();
      set({ openPhotoId: null, timeRange: fullRange });
      scheduleLoad();
    },
  };
});
