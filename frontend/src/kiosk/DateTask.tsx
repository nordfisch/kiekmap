// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * "Wann war das?" -- dating a photo, in the contribution panel.
 *
 * Only the wiring now: the visible flow lives in `DatePicker`, because the detail view shows it
 * too. What stays here is the one binding that makes this place what it is -- the contribution
 * goes to the photo of the running question.
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

  // What is on offer follows from the collection -- see kiosk/decades.ts.
  const decades = useMemo(() => offeredDecades(collection), [collection]);

  return (
    <DatePicker
      decades={decades}
      disabled={loading}
      onPick={(year, precision) => void submitDate(year, precision)}
    />
  );
}
