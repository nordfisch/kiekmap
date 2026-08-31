/**
 * The admin area's scrolling container, reachable from the views inside it.
 *
 * What scrolls is not the individual view but `.admin__body` around it. When a view swaps its
 * content -- photo list to editor, import choice to result -- that container stays put and keeps
 * its `scrollTop`. The new form then opens halfway down, with its heading above the top edge of
 * the screen.
 *
 * Because the container belongs to `AdminApp` while the swap happens inside the view, a context
 * passes it through. That is the alternative to giving every view one more prop that has nothing
 * to do with its actual job.
 */

import { type RefObject, createContext, useContext } from "react";

const ScrollAreaContext = createContext<RefObject<HTMLElement | null> | null>(null);

export const ScrollAreaProvider = ScrollAreaContext.Provider;

/**
 * The scrolling container, or `null` outside the admin area.
 *
 * Use in effects only: the ref does not announce when it fills, and on the first render it is
 * still empty.
 */
export function useScrollArea(): RefObject<HTMLElement | null> | null {
  return useContext(ScrollAreaContext);
}
