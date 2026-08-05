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
  type PhotoDetail,
  type PhotoMarker,
  type TimeRange,
  fetchHistogram,
  fetchPhotos,
} from "../api/client";
import { boundsAround, rangeForPhoto } from "../kiosk/focus";
import { axisBounds, clampRange } from "../kiosk/timeAxis";

/** How long the map has to stand still before loading. */
export const DEBOUNCE_MS = 250;

/** More markers make no sense on a map -- and the Pi should stay responsive. */
export const MAX_PHOTOS = 500;

type KioskState = {
  bbox: Bbox | null;
  timeRange: TimeRange | null;
  /**
   * Span of the whole collection -- the axis of the slider.
   *
   * Deliberately not the span of the current viewport: the axis must not move under the visitor's
   * hand while they pan the map. See kiosk/timeAxis.ts.
   */
  fullRange: TimeRange | null;

  photos: PhotoMarker[];
  total: number;
  truncated: boolean;
  histogram: Histogram | null;

  loading: boolean;
  error: string | null;

  /**
   * The photos currently shown full screen, and which of them.
   *
   * A list rather than one id, because photos at the same spot open as a stack that can be paged
   * through. A single photo is the stack of length one.
   */
  openStack: number[];
  openIndex: number;

  /**
   * Where the map travels for the duration of the thank-you, or null.
   *
   * The map belongs to `MapView`, the state to this store -- this is the bridge between them, as
   * with the reset after idling. `seq` makes sure the same place twice fires twice.
   */
  focus: {
    lat: number;
    lon: number;
    bounds: [[number, number], [number, number]];
    seq: number;
  } | null;
  /** The time range the visitor had set before the focus moved it. */
  rangeBefore: TimeRange | null;

  setViewport: (bbox: Bbox) => void;
  setTimeRange: (timeRange: TimeRange) => void;
  /** A single photo -- the short form for a stack of length one. */
  openPhoto: (id: number | null) => void;
  openStackAt: (ids: number[], index?: number) => void;
  /** Page through the open stack; stops at either end. */
  stepInStack: (delta: number) => void;
  /**
   * Move only the map somewhere -- for the pin just set, before anything has been contributed.
   *
   * Leaves the time range alone: this is not a contribution yet, it is only about showing the
   * visitor where their point landed.
   */
  showLocation: (lat: number, lon: number) => void;
  /** After a contribution: set map and time range so that this photo is visible. */
  showPhoto: (photo: PhotoDetail) => void;
  /** Take both back together -- at the end of the thank-you. */
  releaseFocus: () => void;
  refresh: () => void;
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
        histogram.collection_from !== null && histogram.collection_to !== null
          ? { from: histogram.collection_from, to: histogram.collection_to }
          : null;

      set({
        histogram,
        fullRange: span,
        // First time round, select the whole span: the visitor should see everything first and
        // narrow down afterwards, not the other way round. A selection already made stays
        // untouched -- and since the span belongs to the collection rather than to the viewport,
        // panning the map no longer moves it underneath.
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
    openStack: [],
    openIndex: 0,
    focus: null,
    rangeBefore: null,

    setViewport(bbox) {
      if (sameViewport(get().bbox, bbox)) return;
      set({ bbox });
      scheduleLoad();
      void loadHistogram(bbox);
    },

    setTimeRange(timeRange) {
      // Clamped to the axis so the state cannot become invalid in the first place. The slider
      // clamps its own display once more -- see kiosk/timeAxis.ts.
      const bounds = axisBounds(get().fullRange);
      const next = bounds ? clampRange(timeRange, bounds) : timeRange;

      const current = get().timeRange;
      if (current && current.from === next.from && current.to === next.to) return;
      set({ timeRange: next });
      scheduleLoad();
    },

    openPhoto(id) {
      set({ openStack: id === null ? [] : [id], openIndex: 0 });
    },

    openStackAt(ids, index = 0) {
      set({ openStack: ids, openIndex: index });
    },

    stepInStack(delta) {
      const { openStack, openIndex } = get();
      const next = openIndex + delta;
      if (next < 0 || next >= openStack.length) return;
      set({ openIndex: next });
    },

    showLocation(lat, lon) {
      set((state) => ({
        focus: { lat, lon, bounds: boundsAround(lat, lon), seq: (state.focus?.seq ?? 0) + 1 },
      }));
    },

    /**
     * Settle the view on a photo just completed -- for the duration of the thank-you.
     *
     * Map and time range are moved together and taken back together by ``releaseFocus``. A photo
     * without a place leaves both alone: it is on no map, and moving the slider would only hide
     * other photos.
     */
    showPhoto(photo) {
      const range = rangeForPhoto(photo, get().fullRange);
      if (photo.lat === null || photo.lon === null) return;

      set((state) => ({
        focus: {
          lat: photo.lat as number,
          lon: photo.lon as number,
          bounds: boundsAround(photo.lat as number, photo.lon as number),
          seq: (state.focus?.seq ?? 0) + 1,
        },
        // Remembered on the first pass only. If somebody contributes twice in quick succession,
        // the second call would otherwise take the first focus's range for "before" -- and the
        // visitor would end up with a decade they never set.
        rangeBefore: state.rangeBefore ?? state.timeRange,
        timeRange: range ?? state.timeRange,
      }));
      void loadPhotos();
    },

    releaseFocus() {
      const { rangeBefore } = get();
      set({ focus: null, rangeBefore: null, ...(rangeBefore ? { timeRange: rangeBefore } : {}) });
      if (rangeBefore) void loadPhotos();
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
  };
});
