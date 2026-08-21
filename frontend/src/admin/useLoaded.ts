// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * Load once, keep the three states apart, allow reloading.
 *
 * Every list in the admin area needs the same thing, and each of them needs to distinguish
 * "still loading" from "loaded and empty" -- otherwise an empty list would flash "nothing found"
 * before the answer arrives.
 */

import { useCallback, useEffect, useState } from "react";

export type Loaded<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
};

/** `load` has to be stable -- wrap it in useCallback, otherwise this reloads on every render. */
export function useLoaded<T>(load: () => Promise<T>): Loaded<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let current = true;
    setLoading(true);

    load()
      .then((value) => {
        if (!current) return;
        setData(value);
        setError(null);
      })
      .catch((e: unknown) => {
        if (!current) return;
        setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (current) setLoading(false);
      });

    // A superseded answer must not overwrite the current one -- the search field fires a request
    // per keystroke.
    return () => {
      current = false;
    };
  }, [load, attempt]);

  return { data, error, loading, reload: useCallback(() => setAttempt((n) => n + 1), []) };
}
