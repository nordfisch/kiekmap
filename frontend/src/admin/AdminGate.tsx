/**
 * The way into the admin area: the village arms in the top left corner of the map.
 *
 * Visible on purpose -- a hidden gesture is one more thing for volunteers to remember, and the
 * PIN is the actual lock. A visitor who taps the arms out of curiosity gets a number pad and
 * taps "Zurück zur Karte".
 *
 * The image is `public/logo.png` and nothing in the code knows what is on it. Another museum
 * replaces that one file; the label reads the village name from region.json. See
 * docs/adaption.md.
 */

import { useAdmin } from "../store/admin";
import { t } from "../texte/de";

export function AdminGate({ regionName }: { regionName: string }) {
  const askPin = useAdmin((s) => s.askPin);

  return (
    <button
      type="button"
      className="admin-gate"
      title={t.admin.cornerHint}
      onClick={askPin}
      onContextMenu={(event) => event.preventDefault()}
    >
      <img className="admin-gate__logo" src="/logo.png" alt={t.admin.logoLabel(regionName)} />
    </button>
  );
}
