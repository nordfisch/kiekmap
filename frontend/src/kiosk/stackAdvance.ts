/**
 * A stack in the detail view pages through itself.
 *
 * Nearly every tap on the map opens a stack: photos placed through the place search share the
 * coordinate of their street, and on 26 September 2026 that put 1184 of the 1275 photos on the map
 * into 143 stacks, half of them six photos or larger. A visitor who does not find the paging
 * buttons sees the first photo of each and nothing else. See decisions.md, point 95.
 *
 * **Not the slide show's timing.** `FLIP_EVERY_MS` in `attract.ts` is five seconds for a picture
 * with a one-line caption; the detail view has a column of text beside the picture.
 *
 * **No zoom.** The detail view already shows the 1200 px thumbnail at nearly the height of the
 * screen, so a camera path would scale it up and turn it soft. The photo fades in instead -- the
 * fade lives in the stylesheet, under `.overlay__image`.
 *
 * **Paging by itself is not somebody using the device.** It calls the store and dispatches no
 * event, and `watchForIdle` listens to events only. The idle slide show therefore starts after
 * five minutes even in the middle of a long stack -- which is right, because nobody is there.
 */

/**
 * How long one photo stands before the next one comes.
 *
 * Counted from the moment the photo is visible, not from the moment it was asked for: a slow load
 * must not shorten the time to look at it.
 */
export const STAND_MS = 8_000;

/**
 * The photo after this one, starting again after the last.
 *
 * Starting again rather than stopping: whoever walks up in the middle of a stack still gets to see
 * all of it. A stack of one has no next photo and returns its own index.
 */
export function nextInStack(index: number, length: number): number {
  if (length <= 1) return 0;
  return (index + 1) % length;
}
