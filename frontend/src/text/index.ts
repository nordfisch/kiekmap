/**
 * Which language the device speaks. Resolved once, before the first render.
 *
 * The 30 files that show text import `t` from here. `setLanguage` is called exactly once, in
 * `main.tsx`, after `/api/config` has answered and before `createRoot().render()` -- so no
 * component ever sees the wrong catalogue.
 *
 * **Resolved at startup, not through a context.** The language is a property of the instance, not
 * a choice for the visitor: it never changes while the device runs. A React context would be more
 * than is needed, and it would not even work -- eleven of the thirty importers are not components
 * (`region.ts`, `store/*.ts`, `kiosk/mapCaption.ts`), and no hook runs there.
 *
 * `t` is an exported `let`. ES modules bind by reference, so every importer sees the reassignment.
 * Nothing reads `t` at module level -- only inside functions, which run after the switch.
 */

import { de } from "./de";
import { en } from "./en";
import type { Language, Texts } from "./types";

export type { Language, Texts };

const CATALOGUES: Record<Language, Texts> = { de, en };

export let t: Texts = de;

/** Everything the interface says, in one call. Before the first render, and never again. */
export function setLanguage(language: Language): void {
  t = CATALOGUES[language];
}
