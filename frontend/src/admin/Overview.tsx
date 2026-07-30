/**
 * Die Startseite der Verwaltung: was da ist, und was fehlt.
 *
 * Jede Zahl ist ein Weg. Vorher nannte diese Seite sechs Zahlen, von denen genau eine
 * irgendwohin führte — wer „4 ohne Ort" las, musste sich selbst zum Filter durchklicken. Für
 * jemanden, der zweimal im Jahr hier ist, ist das die halbe Bedienung.
 *
 * Zwei Zeilen zu drei Kacheln: oben der Bestand, unten die Arbeit. Nur „auf der Karte zu sehen"
 * führt nirgendwohin — es ist das Ergebnis, keine Aufgabe.
 */

import { useCallback } from "react";

import { type Selection, fetchOverview } from "../api/admin";
import { t } from "../texte/de";
import { formatDate } from "./format";
import { useLoaded } from "./useLoaded";

/** Wohin eine Kachel führt. `filter` gilt nur für den Fotobereich. */
export type Target = { section: "photos" | "moderation" | "backup"; filter?: Selection };

function Figure({
  label,
  value,
  muted,
  onClick,
}: {
  label: string;
  value: string;
  muted?: boolean;
  onClick?: () => void;
}) {
  const className = muted ? "figure figure--muted" : "figure";
  const content = (
    <>
      <span className="figure__value">{value}</span>
      <span className="figure__label">{label}</span>
    </>
  );

  // Ohne Ziel bleibt es eine Anzeige. Ein Knopf, der nichts tut, ist schlimmer als kein Knopf.
  if (!onClick) return <div className={className}>{content}</div>;

  return (
    <button type="button" className={`${className} figure--link`} onClick={onClick}>
      {content}
    </button>
  );
}

export function Overview({ onNavigate }: { onNavigate: (target: Target) => void }) {
  const { data, error, loading } = useLoaded(useCallback(() => fetchOverview(), []));

  if (loading && !data) return <p className="admin__note">{t.admin.loading}</p>;
  if (error) return <p className="admin__error">{error}</p>;
  if (!data) return null;

  const lastImport = data.last_import_at ? formatDate(data.last_import_at) : t.admin.overview.never;

  return (
    <div className="overview">
      <div className="overview__figures">
        <Figure
          label={t.admin.overview.total}
          value={String(data.total)}
          onClick={() => onNavigate({ section: "photos", filter: "all" })}
        />
        <Figure label={t.admin.overview.onMap} value={String(data.on_map)} />
        <Figure
          label={t.admin.overview.hidden}
          value={String(data.hidden)}
          muted
          onClick={() => onNavigate({ section: "photos", filter: "hidden" })}
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

      <p className="admin__note">
        {t.admin.overview.lastImport}: {lastImport}
      </p>

      {/* Die Erinnerung an die Sicherung bleibt, wo sie war -- sie ist keine Zahl über den
          Bestand, sondern eine Aufforderung. Rot, sobald sie fällig ist. */}
      <button
        type="button"
        className={
          data.backup.overdue
            ? "button backup__reminder-button backup__reminder-button--overdue"
            : "button backup__reminder-button"
        }
        onClick={() => onNavigate({ section: "backup" })}
      >
        {data.backup.last_backup_at
          ? t.admin.backup.lastOn(
              formatDate(data.backup.last_backup_at),
              data.backup.days_since ?? 0,
            )
          : t.admin.backup.lastNever}
      </button>
    </div>
  );
}
