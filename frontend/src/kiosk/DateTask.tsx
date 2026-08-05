/**
 * „Wann war das?" -- ein Foto datieren, im Beitragsbereich.
 *
 * Nur noch die Verdrahtung: Der sichtbare Ablauf steht in `DatePicker`, weil die Detailansicht
 * ihn ebenfalls zeigt. Was hier bleibt, ist die eine Zuordnung, die diese Stelle ausmacht -- der
 * Beitrag geht an das Foto der laufenden Frage.
 */

import { useMemo } from "react";

import { useContribute } from "../store/contribute";
import { useKiosk } from "../store/kiosk";
import { DatePicker } from "./DatePicker";
import { offeredDecades } from "./decades";

export function DateTask() {
  const submitDate = useContribute((s) => s.submitDate);
  const loading = useContribute((s) => s.loading);
  const collection = useKiosk((s) => s.fullRange);

  // Was zur Wahl steht, ergibt sich aus dem Bestand -- siehe kiosk/decades.ts.
  const decades = useMemo(() => offeredDecades(collection), [collection]);

  return (
    <DatePicker
      decades={decades}
      disabled={loading}
      onPick={(year, precision) => void submitDate(year, precision)}
    />
  );
}
