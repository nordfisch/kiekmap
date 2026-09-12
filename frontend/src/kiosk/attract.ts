/**
 * The slide show while nobody uses the device -- its timing and its camera paths.
 *
 * Four tiles rather than one photo on the whole screen. Measured on 12 September 2026 over the
 * 1279 published photos: a single photo in 1920×1080 with room to zoom needs a new thumbnail size
 * and leaves half the collection out. A tile of 960×540 is covered by the existing 1200 px
 * thumbnail with room for a zoom of 1.25, and 807 photos qualify. See decisions.md, point 81.
 *
 * Every value that decides how the show *feels* is a constant here, so it can be adjusted on the
 * device without touching the component.
 */

/** One tile turns over this often, never two at once. */
export const FLIP_EVERY_MS = 5_000;

/** How long the turn itself takes. */
export const FLIP_MS = 1_600;

/**
 * How long one camera path lasts.
 *
 * Four tiles times five seconds: every photo stands for twenty seconds, which is exactly one path.
 * It moves from the moment it appears until it turns over, and never stands still.
 */
export const KEN_BURNS_MS = 20_000;

/** The strongest zoom. More needs a larger thumbnail than the 1200 px one; see above. */
export const MAX_ZOOM = 1.25;

/** The pixel width of the largest thumbnail, the one the show loads. */
export const THUMB_WIDTH = 1200;

/** How many photos one request fetches. */
export const SUPPLY = 24;

/**
 * The band floats across the screen, so that no bright shape stands in one place for hours.
 *
 * Two periods that share no small multiple: the band never passes the same point on the same
 * course twice, and the eye finds no pattern to follow. About 10 px per second on a 1080p screen,
 * slow enough to read while it moves.
 */
export const BAND_X_MS = 71_000;
export const BAND_Y_MS = 47_000;

/** The gap the band keeps to every edge of the screen, in pixels. */
export const BAND_MARGIN = 24;

/**
 * The year and place under a photo: in shortly after the turn, out after ten seconds.
 *
 * A caption that stood for the whole twenty seconds would be a bright box in the same corner of
 * the same tile all night.
 */
export const CAPTION_IN_MS = 900;
export const CAPTION_OUT_MS = 11_000;

/**
 * The order the tiles turn in: top left, bottom right, top right, bottom left.
 *
 * Crosswise rather than in reading order. Reading order runs as a sweep across the wall, and a
 * visible pattern draws the eye away from the photos. In a grid of four some neighbours still
 * follow each other; crosswise keeps it to two of four steps.
 */
const ORDER = [0, 3, 1, 2] as const;

/** Which tile turns at this step. */
export function nextTile(step: number): number {
  return ORDER[((step % ORDER.length) + ORDER.length) % ORDER.length]!;
}

/**
 * How far one photo can be zoomed on this tile without being scaled up.
 *
 * The thumbnail is shrunk to fit its longer side into 1200 px. The browser first scales it to
 * cover the tile, and whatever of it is left over is the room for the zoom. A photo that barely
 * covers the tile gets 1.0: it then only drifts, which looks calm, instead of turning soft.
 */
export function zoomLimit(
  photo: { width: number; height: number },
  tile: { width: number; height: number },
): number {
  const shrink = Math.min(1, THUMB_WIDTH / Math.max(photo.width, photo.height));
  const width = photo.width * shrink;
  const height = photo.height * shrink;
  const cover = Math.max(tile.width / width, tile.height / height);
  return Math.max(1, Math.min(MAX_ZOOM, 1 / cover));
}

export type Frame = { scale: number; x: number; y: number };

/** How far the pan across a photo reaches vertically, as a share of the room. */
const PAN_RISE = 0.6;

/**
 * A camera path, always across the whole room the zoom frees.
 *
 * Three kinds, drawn at random: into a corner, out of a corner, or across the photo from one side
 * to the other at full zoom. A path to a random point inside the room moved too little to be
 * seen: most points lie near the middle. The drift is in percent of the tile and never larger
 * than the room. One percent more and a strip of the tile's background shows at the edge.
 *
 * `random` is passed in so that the path can be tested.
 */
export function kenBurnsPath(zoom: number, random: () => number): [Frame, Frame] {
  const room = ((zoom - 1) / (2 * zoom)) * 100;
  const kind = Math.floor(random() * 3);
  const sx = random() < 0.5 ? -1 : 1;
  const sy = random() < 0.5 ? -1 : 1;
  // `|| 0` turns the -0 of a zero room into 0, so a still path compares equal to one.
  const at = (scale: number, x: number, y: number): Frame => ({
    scale,
    x: x * room || 0,
    y: y * room || 0,
  });

  const whole = at(1, 0, 0);
  const corner = at(zoom, sx, sy);
  if (kind === 0) return [whole, corner];
  if (kind === 1) return [corner, whole];
  return [at(zoom, -sx, -sy * PAN_RISE), at(zoom, sx, sy * PAN_RISE)];
}

/**
 * How far the band can travel without leaving the screen, in pixels.
 *
 * Measured, not set: the band is as wide as its text, and the text depends on the language and on
 * the place name. Zero on a screen too narrow for the band to move at all.
 */
export function bandTravel(
  stage: { width: number; height: number },
  band: { width: number; height: number },
): { x: number; y: number } {
  return {
    x: Math.max(0, stage.width - band.width - 2 * BAND_MARGIN),
    y: Math.max(0, stage.height - band.height - 2 * BAND_MARGIN),
  };
}

/** The CSS transform for one frame. Scale first, so the drift stays inside the scaled image. */
export function transformOf(frame: Frame): string {
  return `scale(${frame.scale}) translate(${frame.x}%, ${frame.y}%)`;
}
