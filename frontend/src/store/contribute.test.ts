import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// `importOriginal` instead of a complete mock, and that because of exactly one line: `NEEDS` is
// the ranking of the three questions. Copied into the test as a list it would be a second truth --
// the order in `client.ts` could be swapped without a test noticing. Verified: with a copy, not one
// failed when the order was swapped.
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  fetchTask: vi.fn(),
  postLocation: vi.fn(),
  postDate: vi.fn(),
  postHouseNumber: vi.fn(),
  // The kiosk store hangs off the same layer -- a contribution makes it reload.
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import {
  type Need,
  type PhotoDetail,
  type Task,
  fetchHistogram,
  fetchPhotos,
  fetchTask,
  postDate,
  postHouseNumber,
  postLocation,
} from "../api/client";
import { t } from "../text/de";
import { useContribute } from "./contribute";
import { useKiosk } from "./kiosk";

const fetched = vi.mocked(fetchTask);
const photosFetched = vi.mocked(fetchPhotos);
const histogramFetched = vi.mocked(fetchHistogram);
const locationPosted = vi.mocked(postLocation);
const datePosted = vi.mocked(postDate);
const housenumberPosted = vi.mocked(postHouseNumber);

function task(need: Need, photoId: number | null, open = 3, other = 3): Task {
  return {
    need,
    open_count: photoId === null ? 0 : open,
    open_other: other,
    photo: photoId === null ? null : ({ id: photoId, title: `Photo ${photoId}` } as PhotoDetail),
  };
}

/**
 * Answers according to the kind asked for -- the way the collection in the museum does.
 *
 * The refinement question is empty by default. Whoever wants to check it states it explicitly --
 * otherwise every test would incidentally check a question it is not about.
 */
function collection(forPlace: Task, forYear: Task, forNumber = task("housenumber", null)) {
  fetched.mockImplementation((need: Need) =>
    Promise.resolve(need === "location" ? forPlace : need === "date" ? forYear : forNumber),
  );
}

beforeEach(() => {
  fetched.mockReset();
  photosFetched.mockReset().mockResolvedValue({ photos: [], total: 0, truncated: false });
  histogramFetched.mockReset().mockResolvedValue({
    bars: [],
    step: 1,
    undated: 0,
    collection_from: null,
    collection_to: null,
  });
  locationPosted.mockReset().mockResolvedValue({ id: 1 } as PhotoDetail);
  datePosted.mockReset().mockResolvedValue({ id: 1, needs_date: false } as PhotoDetail);
  housenumberPosted.mockReset().mockResolvedValue({ id: 1, place_name: "Am Kamp 12" } as PhotoDetail);

  useContribute.setState({
    need: "location",
    task: null,
    loading: false,
    error: null,
    thanks: null,
    skipped: [],
    pickingOnMap: false,
    pin: null,
    pinLabel: null,
  });
  // A viewport has to be set, otherwise there would be nothing to reload.
  useKiosk.setState({ bbox: [9.6, 53.57, 9.75, 53.67] });
});

describe("the I do not know button", () => {
  it("changes the question, not only the photo", async () => {
    // Somebody who does not recognise a place may still know the decade. The same question
    // over again is the reason somebody stops after three images.
    collection(task("location", 1), task("date", 2));
    useContribute.setState({ need: "location", task: task("location", 1) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("date"));

    expect(useContribute.getState().task?.photo?.id).toBe(2);
  });

  it("changes back again too", async () => {
    collection(task("location", 1), task("date", 2));
    useContribute.setState({ need: "date", task: task("date", 2) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("location"));
  });

  it("remembers the photo that was skipped", async () => {
    collection(task("location", 1), task("date", 2));
    useContribute.setState({ need: "location", task: task("location", 7) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("date"));

    // The list applies to every kind of question: skipped once is skipped. Checked over *every*
    // call rather than a named one -- which question comes next is decided by the ranking, and
    // that is not the subject here.
    expect(useContribute.getState().skipped).toEqual([7]);
    for (const [, skippedIds] of fetched.mock.calls) {
      expect(skippedIds).toEqual([7]);
    }
  });
});

describe("falling back when a question runs dry", () => {
  it("stays with the current question when the other has nothing left", async () => {
    // The case that otherwise breaks the switch: in a collection where every photo is located
    // but half have no year, the screen would otherwise read "everything complete" -- while
    // hundreds of photos wait for a year.
    collection(task("location", 5), task("date", null));
    useContribute.setState({ need: "location", task: task("location", 4) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().task?.photo?.id).toBe(5));

    expect(useContribute.getState().need).toBe("location");
  });

  it("reports completeness only once all three questions are empty", async () => {
    // The silent error would be to report everything complete while refinement is still open.
    collection(task("location", null), task("date", null), task("housenumber", null));
    useContribute.setState({ need: "location", task: task("location", 1) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().loading).toBe(false));

    expect(useContribute.getState().task?.photo).toBeNull();
  });

  it("takes hold on the first load too", async () => {
    // A collection where nothing is dated yet: the opening question still has to show something.
    collection(task("location", null), task("date", 9));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(9);
  });
});

describe("the ranking of the three questions", () => {
  it("reaches the refinement when nothing is open after the place", async () => {
    /**
     * Putting a photo somewhere at all is worth more than moving one from the middle of the street
     * to its house -- and that ranking sits solely in the order of `NEEDS`, not in a case
     * distinction.
     */
    collection(task("location", null), task("date", null), task("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("housenumber");
    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });

  it("takes the house number before the year when both have something", async () => {
    /**
     * The test that really checks the order in `NEEDS`: both questions could deliver, and only the
     * position in the tuple decides. Without it, "housenumber" and "date" could be swapped without
     * a test noticing -- verified, not one failed.
     *
     * That the house number comes first was decided on 11 August 2026 from a number and not from a
     * feeling: a year is worth more than a house number, but the collection holds 673 undated
     * photos against 71 that could be refined. Behind the year the third question would never have
     * been reached -- see `services/needs.py`.
     */
    collection(task("location", null), task("date", 8), task("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("housenumber");
    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });

  it("leaves the refinement alone while a photo without a place stands there", async () => {
    // The other direction: *one* unlocated photo is enough to make the finer question wait.
    collection(task("location", 3), task("date", null), task("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("location");
  });

  it("reaches the refinement from the year question", async () => {
    // The exception applies only to the question being refined -- from the year question the way
    // is open, otherwise the third question would never be reachable from inside the panel.
    collection(task("location", null), task("date", null), task("housenumber", 12));
    useContribute.setState({ need: "date", task: task("date", 8) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("housenumber"));

    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });
});

describe("the sharpened map falls back", () => {
  /**
   * A tap on the map only counts after an explicit announcement -- and that announcement applies
   * to *this* photo. If it survived the switch, the next tap would locate a photo the visitor has
   * not even looked at yet.
   */
  beforeEach(() => {
    collection(task("location", 5), task("date", 6));
  });

  it("on the next photo", async () => {
    useContribute.setState({ need: "location", task: task("location", 4), pickingOnMap: true });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().loading).toBe(false));

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("even when the question stays the same", async () => {
    /**
     * The path that leaves the component standing: if the other question has nothing left,
     * ``load`` falls back to the original one. ``need`` stays "location", ``LocationTask`` stays
     * mounted -- a ``useState`` inside the component would not reset here. That is exactly why the
     * switch lives in the store.
     */
    collection(task("location", 5), task("date", null));
    useContribute.setState({ need: "location", task: task("location", 4), pickingOnMap: true });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().task?.photo?.id).toBe(5));

    expect(useContribute.getState().need).toBe("location");
    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("on every load, not only on the two convenient paths", async () => {
    /**
     * ``skip`` and ``contribute`` reset it themselves -- which is why it would not be noticed if
     * ``load`` did not. But ``load`` is the place that sees *every* change of photo, including the
     * one from the detail view and the one when the panel is first built. This test covers exactly
     * the line that otherwise only tidies up after the other two.
     */
    useContribute.setState({ need: "location", task: task("location", 4), pickingOnMap: true });

    await useContribute.getState().load();

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("after a contribution", async () => {
    useContribute.setState({ need: "location", task: task("location", 4), pickingOnMap: true });
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 });

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("is off from the start", () => {
    // Somebody who only wants to look should not answer the question by accident.
    expect(useContribute.getInitialState().pickingOnMap).toBe(false);
  });
});

describe("map and timeline after a contribution", () => {
  beforeEach(() => {
    collection(task("location", 2), task("date", 3));
    useContribute.setState({
      need: "location",
      task: task("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
  });

  it("reloads both as soon as a contribution has arrived", async () => {
    // The thank-you promises that the photo is now on the map. Without this reload that only
    // became true once somebody panned the map -- so for the older visitors the panel is built
    // for, not at all.
    await useContribute.getState().submitLocation();

    expect(photosFetched).toHaveBeenCalled();
    // The histogram belongs with it: a located photo moves out of "without a place", a dated
    // one out of "without a year" into a decade bar.
    expect(histogramFetched).toHaveBeenCalled();
  });

  it("does not reload when the contribution was rejected", async () => {
    // The most frequent case: somebody else was faster (HTTP 409). Then nothing has changed, and
    // a reload would only be load on the Pi.
    locationPosted.mockRejectedValue(new Error("Dieses Foto hat inzwischen schon eine Angabe."));

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().error).toContain("inzwischen");
    expect(photosFetched).not.toHaveBeenCalled();
  });

  it("does not reload while no viewport is known", async () => {
    // Before the map is first built there is no bbox -- then there is nothing to query either.
    useKiosk.setState({ bbox: null });

    await useContribute.getState().submitLocation();

    expect(photosFetched).not.toHaveBeenCalled();
  });
});

describe("after a contribution: the same photo, the other question", () => {
  /**
   * A freshly imported scan often has neither a place nor a year -- in the museum collection that
   * is 673 photos without a year and 77 without a place. Which question comes first is decided by
   * chance.
   */
  const datedWithoutPlace = {
    id: 1,
    lat: null,
    lon: null,
    needs_location: true,
    needs_date: false,
  } as PhotoDetail;

  const locatedWithoutYear = {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    needs_location: false,
    needs_date: true,
  } as PhotoDetail;

  const complete = {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    needs_location: false,
    needs_date: false,
  } as PhotoDetail;

  beforeEach(() => {
    vi.useFakeTimers();
    // The tasks the collection would deliver of its own accord: photo 2 and photo 3. If 1 comes
    // instead of them, the chain has taken hold.
    collection(task("location", 2), task("date", 3));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("thanks without a promise while the place is missing", async () => {
    /**
     * The error at issue here. Promising that the photo is now on the timeline was a pledge the
     * view cannot redeem: a photo without a place stands on no map, the focus stays where it was,
     * and the visitor reads a sentence and sees nothing.
     */
    useContribute.setState({ need: "date", task: task("date", 1) });
    datePosted.mockResolvedValue(datedWithoutPlace);

    await useContribute.getState().submitDate(1930, "decade");

    expect(useContribute.getState().thanks).not.toContain("Zeitleiste");
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.location);
  });

  it("offers the same photo for the place question once it was dated", async () => {
    // Somebody who has just said when it was knows the photo -- and is looking at it. Offering a
    // random other one throws exactly that moment away.
    useContribute.setState({ need: "date", task: task("date", 1) });
    datePosted.mockResolvedValue(datedWithoutPlace);

    await useContribute.getState().submitDate(1930, "decade");
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("location");
    expect(useContribute.getState().task?.photo?.id).toBe(1);
  });

  it("offers the same photo for the year question once it was located", async () => {
    // The same rule in the other direction, so that it stays a rule and not a special case.
    useContribute.setState({
      need: "location",
      task: task("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    locationPosted.mockResolvedValue(locatedWithoutYear);

    await useContribute.getState().submitLocation();
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.date);

    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(1);
  });

  it("promises the map only once the photo can be seen on it", async () => {
    // The old sentence stays -- only where it is true.
    useContribute.setState({
      need: "location",
      task: task("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    locationPosted.mockResolvedValue(complete);

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().thanks).toBe(t.help.thanks.location);
  });

  it("does not ask for the house number straight after good enough", async () => {
    /**
     * The one real exception to the pure ranking, and it hangs on the *answering*. Somebody who has
     * just pressed "good enough -- the street will do" and confirmed the place has already answered
     * the question about the exact house; asking it again in the same breath reads as though
     * nobody had listened.
     *
     * Without the `refines` line the chain would lead to "housenumber" here, because nothing is
     * open after the place and the year.
     */
    collection(task("location", null), task("date", null), task("housenumber", 12));
    useContribute.setState({
      need: "location",
      task: task("location", 12),
      pin: { lat: 53.62, lon: 9.676 },
      pinLabel: "Am Kamp",
      pinAccuracy: 150,
    });
    locationPosted.mockResolvedValue(complete);

    await useContribute.getState().submitLocation();
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).not.toBe("housenumber");
  });

  it("moves to the next photo when nothing is missing any more", async () => {
    // The chain has to end, otherwise the visitor would be offered the same photo a second time.
    useContribute.setState({
      need: "location",
      task: task("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    locationPosted.mockResolvedValue(complete);

    await useContribute.getState().submitLocation();
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(3);
  });
});

describe("the map while locating", () => {
  beforeEach(() => {
    useKiosk.setState({ focus: null, rangeBefore: null, bbox: [9.6, 53.57, 9.75, 53.67] });
  });

  it("zooms in on a hit from the place search", () => {
    // The visitor did not set the point themselves -- they want to see where it landed.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    // The viewport wraps around the point -- the focus carries no coordinate of its own, the map
    // reads `bounds` alone.
    const [[west, south], [east, north]] = useKiosk.getState().focus!.bounds;
    expect(53.62).toBeGreaterThan(south);
    expect(53.62).toBeLessThan(north);
    expect(9.676).toBeGreaterThan(west);
    expect(9.676).toBeLessThan(east);
  });

  it("leaves it alone for a point tapped on the map", () => {
    // That is where they just aimed. A map that jumps away under the finger feels like a slip.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 });

    expect(useKiosk.getState().focus).toBeNull();
  });

  it("travels back when the point is removed", () => {
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });
    useContribute.getState().setPin(null);

    expect(useKiosk.getState().focus).toBeNull();
  });

  it("gives a label only to the place search", () => {
    // This is how the house-number choice tells a tap on the map from a hit of its own: only its
    // own carries a label. If that promise broke, the grid of buttons would stay after a tap on
    // the map and throw the point just set away on the next tap.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });
    expect(useContribute.getState().pinLabel).toBe("Mühlenweg");

    useContribute.getState().setPin({ lat: 53.63, lon: 9.677 });
    expect(useContribute.getState().pinLabel).toBeNull();
  });

  it("leaves the range alone while nothing has been contributed", () => {
    useKiosk.setState({ timeRange: { from: 1950, to: 1959 }, fullRange: { from: 1920, to: 2019 } });

    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
    expect(useKiosk.getState().rangeBefore).toBeNull();
  });
});

describe("asking from inside a photo", () => {
  /**
   * The way out of the detail view: somebody looking at a photo full size and tapping the year
   * question there means exactly that photo. The wish goes to the server, which checks it against
   * the same condition as any other photo -- see `api/contribute.py`.
   */
  function collectionWithWish(forPlace: Task, forYear: Task, requested?: Task) {
    fetched.mockImplementation((need: Need, _skippedIds: number[], photoId?: number | null) => {
      if (photoId != null && requested && requested.need === need) {
        return Promise.resolve(requested);
      }
      return Promise.resolve(need === "location" ? forPlace : forYear);
    });
  }

  it("puts the requested photo to the requested question", async () => {
    collectionWithWish(task("location", 3), task("date", 8), task("date", 42));

    await useContribute.getState().askAbout(42, "date");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(42);
  });

  it("passes the photo id on only for the requested question", async () => {
    // The fallback applies to a *different* question. A wish travelling along there would mean:
    // offer me this photo for a question it has nothing to say about.
    collectionWithWish(task("location", 3), task("date", 8), task("date", 42));

    await useContribute.getState().askAbout(42, "date");

    expect(fetched).toHaveBeenCalledWith("date", [], 42, expect.anything());
  });

  it("falls back to the ranking when the photo needs nothing more", async () => {
    /**
     * Between the tap and the load, somebody else may have answered. The server then offers a
     * different photo -- and the panel carries on instead of standing there with a question that
     * is already answered.
     */
    collectionWithWish(task("location", 3), task("date", 8));

    await useContribute.getState().askAbout(42, "date");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(8);
  });

  it("takes the usual path afterwards", async () => {
    /**
     * The test that records that **no** special rule was built here: after the answer, the thanks
     * and the chain follow as after any other contribution. Whoever answers from inside a photo has
     * landed in the contribution panel, and that is where the next question belongs.
     */
    collectionWithWish(task("location", 3), task("date", 8), task("date", 42));
    datePosted.mockResolvedValue({
      id: 42,
      needs_date: false,
      needs_location: true,
    } as PhotoDetail);

    await useContribute.getState().askAbout(42, "date");
    await useContribute.getState().submitDate(1932, "year");

    // The thanks asks for what this photo is still missing -- and that is the place.
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.location);
  });
});
