/**
 * The keyword buttons in the top left corner of the map.
 *
 * Top left because the zoom buttons take the top right and the notices the bottom. One keyword at
 * most is active; the store holds it. Which buttons stand here is `cornerTags` in `keywords.ts`.
 */

import { useEffect, useState } from "react";

import { fetchOfferedTags } from "../api/client";
import { useKiosk } from "../store/kiosk";
import { t } from "../text";
import { cornerTags } from "./keywords";

export function KeywordCorner() {
  const tag = useKiosk((s) => s.tag);
  const setTag = useKiosk((s) => s.setTag);
  const [offered, setOffered] = useState<string[]>([]);

  // Once per page load. The list changes with the `.env`, and that needs a restart anyway.
  useEffect(() => {
    const abort = new AbortController();
    fetchOfferedTags(abort.signal)
      .then(setOffered)
      .catch(() => {
        /* Without the list the corner stays empty. The map works without it. */
      });
    return () => abort.abort();
  }, []);

  const buttons = cornerTags(offered, tag);
  if (buttons.length === 0) return null;

  return (
    <div className="keywords" role="group" aria-label={t.map.keywords}>
      {buttons.map((name) => (
        <button
          key={name}
          type="button"
          className={name === tag ? "keywords__button keywords__button--on" : "keywords__button"}
          aria-pressed={name === tag}
          onClick={() => setTag(name)}
        >
          {name}
        </button>
      ))}
    </div>
  );
}
