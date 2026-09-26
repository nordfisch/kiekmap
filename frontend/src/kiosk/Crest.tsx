/**
 * The village arms over the top left corner of the map -- and the way back to the start.
 *
 * **It used to be the door to the admin area; since 9 August 2026 the title beside it is.** See
 * decisions.md, point 26. A tap starts the slide show, and every way out of the slide show
 * reloads the page. That puts map, time range, contribution panel and any open photo back where
 * the device stands each morning. Until September 2026 the tap reloaded directly; see point 81.
 *
 * A reload rather than a state reset in code: it cannot forget a piece of state somebody adds
 * later, and the device fetches everything it needs from the next room.
 *
 * **The objection is real and was weighed rather than dismissed:** a button almost nobody needs
 * gets pressed anyway -- by children first -- and it throws away whatever somebody had just
 * begun. A half-placed pin, a chosen decade, an open stack: gone. What tips it is that the
 * visitor's side has no other way back at all; the alternatives were waiting five minutes, typing
 * the PIN and leaving again, or the power lead.
 *
 * The image is `public/logo.png` and nothing in the code knows what is on it. Another museum
 * replaces that one file; the label reads the village name from region.json. See
 * docs/adaption.md.
 */

import { useKiosk } from "../store/kiosk";
import { t } from "../text";

export function Crest({ regionName }: { regionName: string }) {
  const startAttract = useKiosk((s) => s.startAttract);
  return (
    <button
      type="button"
      className="crest"
      title={t.app.resetHint}
      onClick={startAttract}
      onContextMenu={(event) => event.preventDefault()}
    >
      <img className="crest__logo" src="/logo.png" alt={t.admin.logoLabel(regionName)} />
    </button>
  );
}
