/**
 * The admin area's start page: what is there, what is missing, and when something last happened.
 *
 * Every number is a route. This page used to name six numbers, exactly one of which led anywhere
 * -- whoever read "4 ohne Ort" had to click their own way to the filter. For somebody who is here
 * twice a year that is half of the operation.
 *
 * The collection above, the running of the device below the rule: how long since a backup, since
 * anything was taken in, since a visitor contributed. The same three columns, so the lower row
 * lines up through the same grid rather than "roughly".
 */

import { useCallback } from "react";

import { type Selection, fetchOverview } from "../api/admin";
import { useAdmin } from "../store/admin";
import { t } from "../text";
import { formatDaysSince } from "./format";
import { useLoaded } from "./useLoaded";

/** Where a tile leads. `filter` applies to the photo section only, `kiosk` leaves the admin area. */
export type Target = {
  section: "photos" | "moderation" | "log" | "backup" | "kiosk";
  filter?: Selection;
};

function Figure({
  label,
  value,
  muted,
  overdue,
  onClick,
}: {
  label: string;
  value: string;
  muted?: boolean;
  /** The backup tile only: red as soon as it is due. */
  overdue?: boolean;
  onClick?: () => void;
}) {
  const className = [
    "figure",
    muted ? "figure--muted" : "",
    overdue ? "figure--overdue" : "",
    onClick ? "figure--link" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const content = (
    <>
      <span className="figure__value">{value}</span>
      <span className="figure__label">{label}</span>
    </>
  );

  // Without a target it stays a readout. A button that does nothing is worse than no button.
  if (!onClick) return <div className={className}>{content}</div>;

  return (
    <button type="button" className={className} onClick={onClick}>
      {content}
    </button>
  );
}

export function Overview({ onNavigate }: { onNavigate: (target: Target) => void }) {
  const { data, error, loading } = useLoaded(useCallback(() => fetchOverview(), []));
  const leave = useAdmin((s) => s.leave);

  if (loading && !data) return <p className="admin__note">{t.admin.loading}</p>;
  if (error) return <p className="admin__error">{error}</p>;
  if (!data) return null;

  return (
    <div className="overview">
      <div className="overview__figures">
        <Figure
          label={t.admin.overview.total}
          value={String(data.total)}
          onClick={() => onNavigate({ section: "photos", filter: "all" })}
        />
        {/* The only way out of here rather than deeper in -- the same as "Verwaltung beenden". */}
        <Figure
          label={t.admin.overview.onMap}
          value={String(data.on_map)}
          onClick={() => onNavigate({ section: "kiosk" })}
        />
        <Figure
          label={t.admin.overview.deleted}
          value={String(data.deleted)}
          muted
          onClick={() => onNavigate({ section: "photos", filter: "deleted" })}
        />

        <Figure
          label={t.admin.overview.withoutLocation}
          value={String(data.without_location)}
          onClick={() => onNavigate({ section: "photos", filter: "without_location" })}
        />
        <Figure
          label={t.admin.overview.withoutDate}
          value={String(data.without_date)}
          onClick={() => onNavigate({ section: "photos", filter: "without_date" })}
        />
        <Figure
          label={t.admin.overview.visitorChanges}
          value={String(data.visitor_changes)}
          muted
          onClick={() => onNavigate({ section: "moderation" })}
        />
      </div>

      <hr className="overview__rule" />

      <div className="overview__figures">
        <Figure
          label={t.admin.overview.sinceBackup(data.backup.days_since)}
          value={formatDaysSince(data.backup.days_since)}
          overdue={data.backup.overdue}
          onClick={() => onNavigate({ section: "backup" })}
        />
        <Figure
          label={t.admin.overview.sinceImport(data.days_since_import)}
          value={formatDaysSince(data.days_since_import)}
          onClick={() => onNavigate({ section: "log" })}
        />
        <Figure
          label={t.admin.overview.sinceChange(data.days_since_change)}
          value={formatDaysSince(data.days_since_change)}
          onClick={() => onNavigate({ section: "moderation" })}
        />
      </div>

      {/* The kiosk has no browser controls -- no reload button, no address bar, no
          keyboard. Without this button a stuck display would leave only the power plug (or five
          minutes of waiting until the idle reset reloads).

          Since "Verwaltung beenden" reloads by itself, it technically does the same thing. It
          stays anyway: whoever wants to fix a stuck display looks for "neu laden", not for
          "beenden". The button is the name for the route, not a second route. */}
      <div className="overview__repair">
        <button type="button" className="button" onClick={() => void leave()}>
          {t.admin.overview.reload}
        </button>
        <p className="admin__note">{t.admin.overview.reloadHint}</p>
      </div>
    </div>
  );
}
