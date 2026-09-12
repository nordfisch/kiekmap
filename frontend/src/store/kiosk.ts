/**
 * State of the visitor view.
 *
 * Two loops run here at different speeds:
 *
 *   slow  viewport, time range or keyword changes -> one query after a short pause
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

  /**
   * Are photos without any date on the map?
   *
   * They overlap no period, so every time range drops all of them -- two thirds of this
   * collection. That used to be a side effect of touching the slider; now it is a switch beside
   * it, and this is its state.
   */
  showUndated: boolean;
  /**
   * Has the visitor worked that switch themselves?
   *
   * Until they have, the first narrowing of the range turns it off for them -- that is the moment
   * the period starts to mean something, so it is the moment to stop showing what lies outside
   * it. **Afterwards it stays where they put it.** Turning it off again on every further drag
   * would fight a choice somebody had just made by hand, and land right back at the complaint
   * this whole thing is about: the map losing photos without being asked.
   */
  undatedByHand: boolean;

  /**
   * The keyword the map is filtered by, or null.
   *
   * One at most. Combining keywords with "and" or "or" is a question nobody at a touchscreen
   * wants to answer. See decisions.md, point 80.
   */
  tag: string | null;

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
    bounds: [[number, number], [number, number]];
    seq: number;
  } | null;
  /** The time range the visitor had set before the focus moved it. */
  rangeBefore: TimeRange | null;
  /** The keyword the focus took away because the photo does not carry it, or null. */
  tagBefore: string | null;

  /**
   * Counts up whenever the map should show the whole region -- and stay there.
   *
   * Not ``focus``: a focus travels back when it ends. A counter rather than a flag, so the same
   * request twice moves the map twice.
   */
  overview: number;

  setViewport: (bbox: Bbox) => void;
  setTimeRange: (timeRange: TimeRange) => void;
  setShowUndated: (on: boolean) => void;
  /** A keyword from the corner of the map: the same one again switches it off. */
  setTag: (tag: string) => void;
  /**
   * The way in from the detail view: this keyword, with time and place wide open.
   *
   * Wide open because the visitor asks "what else is there with this keyword", not "what else is
   * there with this keyword here and in this decade". Closes the detail view.
   */
  filterByTag: (tag: string) => void;
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
  /**
   * Move the map onto a rectangle -- for the house numbers currently on offer.
   *
   * The counterpart to ``showLocation`` for a set of points rather than one: whoever is asked for
   * a house number has to see the numbers, and on a street of 132 addresses one point in its
   * middle shows none of them. Built with ``boundsOf``.
   */
  showArea: (bounds: [[number, number], [number, number]]) => void;
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
    const { bbox, timeRange, fullRange, showUndated, tag } = get();
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
        showUndated,
        tag,
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
      const histogram = await fetchHistogram(bbox, get().tag, signal);
      if (signal.aborted) return;

      const { timeRange } = get();
      const span =
        histogram.collection_from !== null && histogram.collection_to !== null
          ? { from: histogram.collection_from, to: histogram.collection_to }
          : null;

      // The axis, not the span: it reaches one bar past the youngest photo so that the last bar
      // has track of its own. Starting on the span would leave the trimmer short of the right
      // end -- looking as if something were already filtered out.
      const axis = axisBounds(span, histogram.step);

      set({
        histogram,
        fullRange: span,
        // First time round, select the whole axis: the visitor should see everything first and
        // narrow down afterwards, not the other way round. A selection already made stays
        // untouched -- and since the axis belongs to the collection rather than to the viewport,
        // panning the map no longer moves it underneath.
        //
        // Reaching past the youngest photo costs nothing: ``queryTimeFilter`` asks whether the
        // selection *covers* the span, not whether it equals it, so no filter goes to the backend
        // -- and the undated photos, which only show without one, stay on the map.
        timeRange: timeRange ?? (axis ? { from: axis.min, to: axis.max } : null),
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
    showUndated: true,
    undatedByHand: false,
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
    tagBefore: null,
    overview: 0,
    tag: null,

    setViewport(bbox) {
      if (sameViewport(get().bbox, bbox)) return;
      set({ bbox });
      scheduleLoad();
      void loadHistogram(bbox);
    },

    setTimeRange(timeRange) {
      // Clamped to the axis so the state cannot become invalid in the first place. The slider
      // clamps its own display once more -- see kiosk/timeAxis.ts.
      //
      // With the bar width, not without: the axis is rounded to it, and clamping against a
      // decade-wide axis while the bars are yearly would let a selection stand that the slider
      // then draws somewhere else.
      const bounds = axisBounds(get().fullRange, get().histogram?.step);
      const next = bounds ? clampRange(timeRange, bounds) : timeRange;

      const current = get().timeRange;
      if (current && current.from === next.from && current.to === next.to) return;

      // The first narrowing takes the undated off the map -- once, and only while nobody has
      // touched the switch.
      //
      // This is the moment the period starts to mean something: up to here the visitor has set
      // nothing, from here they have. Leaving photos on the map that lie in no period at all
      // would make the slider say something it does not do. ``queryTimeFilter`` is the right
      // question to ask, because it answers "is a filter going out at all" -- the switch goes off
      // exactly where photos would otherwise begin to vanish unasked.
      const { undatedByHand, fullRange } = get();
      const narrowed = queryTimeFilter(next, fullRange) !== null;
      set({ timeRange: next, ...(undatedByHand || !narrowed ? {} : { showUndated: false }) });
      scheduleLoad();
    },

    setShowUndated(on) {
      // ``undatedByHand`` never goes back: from here the switch is the visitor's, and the slider
      // stops reaching for it.
      set({ showUndated: on, undatedByHand: true });
      scheduleLoad();
    },

    setTag(tag) {
      // A choice made during the thank-you is the visitor's, so the end of the focus must not
      // bring back the keyword it had taken away.
      set((state) => ({ tag: state.tag === tag ? null : tag, tagBefore: null }));
      scheduleLoad();
      const { bbox } = get();
      if (bbox) void loadHistogram(bbox);
    },

    filterByTag(tag) {
      const { fullRange, histogram } = get();
      const axis = axisBounds(fullRange, histogram?.step);
      set((state) => ({
        tag,
        tagBefore: null,
        // The whole axis sends no time filter, and the undated photos belong to "wide open".
        // ``undatedByHand`` stays as it is: this is not the visitor touching the switch.
        timeRange: axis ? { from: axis.min, to: axis.max } : state.timeRange,
        showUndated: true,
        // A focus still running would take range and camera back at its end and undo this.
        focus: null,
        rangeBefore: null,
        openStack: [],
        openIndex: 0,
        overview: state.overview + 1,
      }));
      // The map reports its new viewport when it arrives. This load covers the case where the
      // region was already on screen and no "moveend" follows.
      void loadPhotos();
      const { bbox } = get();
      if (bbox) void loadHistogram(bbox);
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
      get().showArea(boundsAround(lat, lon));
    },

    showArea(bounds) {
      set((state) => ({ focus: { bounds, seq: (state.focus?.seq ?? 0) + 1 } }));
    },

    /**
     * Settle the view on a photo just completed -- for the duration of the thank-you.
     *
     * Map and time range are moved together and taken back together by ``releaseFocus``. A photo
     * without a place leaves both alone: it is on no map, and moving the slider would only hide
     * other photos.
     *
     * **The keyword goes too, if the photo does not carry it.** Otherwise the thank-you promises a
     * photo on the map that the filter hides. It comes back with the range.
     */
    showPhoto(photo) {
      const range = rangeForPhoto(photo, get().fullRange);
      if (photo.lat === null || photo.lon === null) return;

      const { tag, bbox } = get();
      const hidesIt = tag !== null && !photo.tags.includes(tag);

      set((state) => ({
        focus: {
          bounds: boundsAround(photo.lat as number, photo.lon as number),
          seq: (state.focus?.seq ?? 0) + 1,
        },
        // Remembered on the first pass only. If somebody contributes twice in quick succession,
        // the second call would otherwise take the first focus's range for "before" -- and the
        // visitor would end up with a decade they never set.
        rangeBefore: state.rangeBefore ?? state.timeRange,
        timeRange: range ?? state.timeRange,
        ...(hidesIt ? { tag: null, tagBefore: state.tagBefore ?? tag } : {}),
      }));
      void loadPhotos();
      if (hidesIt && bbox) void loadHistogram(bbox);
    },

    releaseFocus() {
      const { rangeBefore, tagBefore, bbox } = get();
      set({
        focus: null,
        rangeBefore: null,
        tagBefore: null,
        ...(rangeBefore ? { timeRange: rangeBefore } : {}),
        ...(tagBefore !== null ? { tag: tagBefore } : {}),
      });
      if (rangeBefore || tagBefore !== null) void loadPhotos();
      if (tagBefore !== null && bbox) void loadHistogram(bbox);
    },

    /**
     * Reload after something outside the map changed the collection.
     *
     * The contribution panel is the case this exists for. It promises "Das Foto ist jetzt auf der
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
