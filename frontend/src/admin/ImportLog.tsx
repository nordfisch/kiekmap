/**
 * The import log.
 *
 * Its whole reason for existing: without it, a photo that was skipped is indistinguishable from
 * one that was never copied in. "Nichts passiert" is the one answer a volunteer cannot act on.
 */

import { useCallback, useEffect, useState } from "react";

import { fetchImportLog } from "../api/admin";
import { t } from "../text";
import { formatLogTime } from "./format";
import { Pager } from "./Pager";
import { clampOffset } from "./pagination";
import { useLoaded } from "./useLoaded";

/** Functions, not constants: `t` is only resolved after this module has been imported. */
function results(): { value: string; label: string }[] {
  return [
    { value: "", label: t.admin.imports.all },
    { value: "imported", label: t.admin.imports.imported },
    { value: "duplicate", label: t.admin.imports.duplicate },
    { value: "rejected", label: t.admin.imports.rejected },
  ];
}

function labels(): Record<string, string> {
  return {
    imported: t.admin.imports.imported,
    duplicate: t.admin.imports.duplicate,
    rejected: t.admin.imports.rejected,
  };
}

export function ImportLog() {
  const [result, setResult] = useState("");
  const [offset, setOffset] = useState(0);

  // A different tab is a different list -- so start over again.
  useEffect(() => setOffset(0), [result]);

  const { data, error, loading } = useLoaded(
    useCallback(
      () => fetchImportLog(result || undefined, offset),
      [result, offset],
    ),
  );

  useEffect(() => {
    if (data) setOffset((current) => clampOffset(current, data.total));
  }, [data]);

  return (
    <div className="imports">
      <h3 className="admin__heading">{t.admin.imports.title}</h3>

      <div className="tabs tabs--filters">
        {results().map((option) => (
          <button
            key={option.value}
            type="button"
            className={result === option.value ? "tab tab--active" : "tab"}
            onClick={() => setResult(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>

      {error && <p className="admin__error">{error}</p>}
      {loading && !data && <p className="admin__note">{t.admin.loading}</p>}
      {data && data.entries.length === 0 && (
        <p className="admin__note">{t.admin.imports.none}</p>
      )}

      {data && data.entries.length > 0 && (
        <ul className="log-rows">
          {data.entries.map((entry) => (
            <li key={entry.id} className="log-row">
              <span className={`flag flag--${entry.result}`}>
                {labels()[entry.result] ?? entry.result}
              </span>
              <span className="log-row__filename">{entry.filename}</span>
              <span className="log-row__message">{entry.message}</span>
              <span className="log-row__time">
                {formatLogTime(entry.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}

      {data && (
        <Pager total={data.total} offset={offset} onOffset={setOffset} />
      )}
    </div>
  );
}
