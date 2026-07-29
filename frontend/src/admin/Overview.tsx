/**
 * The start page of the admin area: what is there, and what is missing.
 *
 * The gaps come first, not the total. After a scanning session the question is never "how many
 * photos are there" but "how much still has no year".
 */

import { useCallback } from "react";

import { fetchOverview } from "../api/admin";
import { t } from "../texte/de";
import { formatDate } from "./format";
import { useLoaded } from "./useLoaded";

function Figure({ label, value, muted }: { label: string; value: string; muted?: boolean }) {
  return (
    <div className={muted ? "figure figure--muted" : "figure"}>
      <span className="figure__value">{value}</span>
      <span className="figure__label">{label}</span>
    </div>
  );
}

export function Overview({
  onShowIncomplete,
  onShowBackup,
}: {
  onShowIncomplete: () => void;
  onShowBackup: () => void;
}) {
  const { data, error, loading } = useLoaded(useCallback(() => fetchOverview(), []));

  if (loading && !data) return <p className="admin__note">{t.admin.loading}</p>;
  if (error) return <p className="admin__error">{error}</p>;
  if (!data) return null;

  const lastImport = data.last_import_at ? formatDate(data.last_import_at) : t.admin.overview.never;

  return (
    <div className="overview">
      <div className="overview__figures">
        <Figure label={t.admin.overview.total} value={String(data.total)} />
        <Figure label={t.admin.overview.onMap} value={String(data.on_map)} />
        <Figure label={t.admin.overview.withoutLocation} value={String(data.without_location)} />
        <Figure label={t.admin.overview.withoutDate} value={String(data.without_date)} />
        <Figure label={t.admin.overview.hidden} value={String(data.hidden)} muted />
        <Figure
          label={t.admin.overview.visitorChanges}
          value={String(data.visitor_changes)}
          muted
        />
      </div>

      <p className="admin__note">
        {t.admin.overview.lastImport}: {lastImport}
      </p>

      {/* The backup reminder belongs on the start page, not only in its own section -- that is the
          whole point of a reminder. Red once it is due. */}
      <button
        type="button"
        className={
          data.backup.overdue
            ? "button backup__reminder-button backup__reminder-button--overdue"
            : "button backup__reminder-button"
        }
        onClick={onShowBackup}
      >
        {data.backup.last_backup_at
          ? t.admin.backup.lastOn(
              formatDate(data.backup.last_backup_at),
              data.backup.days_since ?? 0,
            )
          : t.admin.backup.lastNever}
      </button>

      {data.without_location + data.without_date > 0 && (
        <button type="button" className="button" onClick={onShowIncomplete}>
          {t.admin.overview.toIncomplete}
        </button>
      )}
    </div>
  );
}
