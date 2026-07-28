/**
 * The import log.
 *
 * Its whole reason for existing: without it, a photo that was skipped is indistinguishable from
 * one that was never copied in. "Nichts passiert" is the one answer a volunteer cannot act on.
 */

import { useCallback, useState } from "react";

import { fetchImportLog } from "../api/admin";
import { t } from "../texte/de";
import { useLoaded } from "./useLoaded";

const RESULTS: { value: string; label: string }[] = [
  { value: "", label: t.admin.imports.all },
  { value: "imported", label: t.admin.imports.imported },
  { value: "duplicate", label: t.admin.imports.duplicate },
  { value: "rejected", label: t.admin.imports.rejected },
];

const LABELS: Record<string, string> = {
  imported: t.admin.imports.imported,
  duplicate: t.admin.imports.duplicate,
  rejected: t.admin.imports.rejected,
};

export function ImportLog() {
  const [result, setResult] = useState("");
  const { data, error, loading } = useLoaded(
    useCallback(() => fetchImportLog(result || undefined), [result]),
  );

  return (
    <div className="imports">
      <h3 className="admin__heading">{t.admin.imports.title}</h3>

      <div className="tabs tabs--filters">
        {RESULTS.map((option) => (
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
      {data && data.length === 0 && <p className="admin__note">{t.admin.imports.none}</p>}

      {data && data.length > 0 && (
        <ul className="log-rows">
          {data.map((entry) => (
            <li key={entry.id} className="log-row">
              <span className={`flag flag--${entry.result}`}>
                {LABELS[entry.result] ?? entry.result}
              </span>
              <span className="log-row__filename">{entry.filename}</span>
              <span className="log-row__message">{entry.message}</span>
              <span className="log-row__time">
                {new Date(entry.created_at).toLocaleString("de-DE", {
                  day: "numeric",
                  month: "numeric",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
