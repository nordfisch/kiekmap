/**
 * What visitors have contributed.
 *
 * Contributions take effect at the kiosk straight away -- that immediacy is what makes people
 * join in. This list is the counterweight: whoever looks after the collection sees what happened
 * and can take a single statement back.
 *
 * Taking back means clearing, not restoring: a visitor may only ever fill what was empty, so
 * there is nothing to restore. The photo returns to the "Hilf mit" panel and can be answered
 * again, which is usually the point.
 */

import { useCallback, useEffect, useState } from "react";

import { fetchChanges, revertChange } from "../api/admin";
import { t } from "../text/de";
import { Pager } from "./Pager";
import { clampOffset } from "./pagination";
import { useLoaded } from "./useLoaded";

const FIELD_NAMES: Record<string, string> = {
  location: t.admin.changes.fieldLocation,
  date: t.admin.changes.fieldDate,
};

function when(iso: string): string {
  return new Date(iso).toLocaleString("de-DE", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function Changes() {
  const [includeReverted, setIncludeReverted] = useState(false);
  const [offset, setOffset] = useState(0);
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // The checkbox changes the set -- so start over, or you would stand past its end.
  useEffect(() => setOffset(0), [includeReverted]);

  const {
    data,
    error: loadError,
    loading,
    reload,
  } = useLoaded(
    useCallback(() => fetchChanges(includeReverted, offset), [includeReverted, offset]),
  );

  useEffect(() => {
    if (data) setOffset((current) => clampOffset(current, data.total));
  }, [data]);

  async function revert(id: number) {
    setBusy(id);
    setError(null);
    try {
      await revertChange(id);
      reload();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="changes">
      <h3 className="admin__heading">{t.admin.changes.title}</h3>

      <label className="field__check">
        <input
          type="checkbox"
          checked={includeReverted}
          onChange={(event) => setIncludeReverted(event.target.checked)}
        />
        {t.admin.changes.showReverted}
      </label>

      {(error || loadError) && <p className="admin__error">{error ?? loadError}</p>}
      {loading && !data && <p className="admin__note">{t.admin.loading}</p>}

      {data && data.changes.length === 0 && <p className="admin__note">{t.admin.changes.none}</p>}

      {data && data.changes.length > 0 && (
        <ul className="photo-rows">
          {data.changes.map((change) => (
            <li key={change.id} className="photo-row">
              <img className="photo-row__thumb" src={change.thumb_url} alt="" />
              <div className="photo-row__text">
                <span className="photo-row__title">
                  {change.photo_title || t.admin.photos.untitled}
                </span>
                <span className="photo-row__meta">
                  {FIELD_NAMES[change.field] ?? change.field}: {change.new_value}
                </span>
                <span className="photo-row__meta">{when(change.created_at)}</span>
              </div>

              {change.reverted_at ? (
                <span className="flag flag--muted">{t.admin.changes.reverted}</span>
              ) : change.revertable ? (
                <button
                  type="button"
                  className="button"
                  title={t.admin.changes.revertHint}
                  onClick={() => void revert(change.id)}
                  disabled={busy === change.id}
                >
                  {t.admin.changes.revert}
                </button>
              ) : (
                <span className="flag flag--muted">{t.admin.changes.locked}</span>
              )}
            </li>
          ))}
        </ul>
      )}

      {data && <Pager total={data.total} offset={offset} onOffset={setOffset} />}
    </div>
  );
}
