/**
 * Die Startseite der Verwaltung: was da ist, was fehlt, und wann zuletzt etwas geschah.
 *
 * Jede Zahl ist ein Weg. Vorher nannte diese Seite sechs Zahlen, von denen genau eine
 * irgendwohin führte — wer „4 ohne Ort" las, musste sich selbst zum Filter durchklicken. Für
 * jemanden, der zweimal im Jahr hier ist, ist das die halbe Bedienung.
 *
 * Oben der Bestand, unter der Trennlinie der Betrieb: seit wann nicht gesichert, seit wann nichts
 * aufgenommen, seit wann kein Besucher etwas beigetragen. Dieselben drei Spalten, damit die untere
 * Zeile nicht „ungefähr", sondern durch dasselbe Raster bündig steht.
 */

import { useCallback } from "react";

import { type Selection, fetchOverview } from "../api/admin";
import { useAdmin } from "../store/admin";
import { t } from "../texte/de";
import { formatDaysSince } from "./format";
import { useLoaded } from "./useLoaded";

/** Wohin eine Kachel führt. `filter` gilt nur für den Fotobereich, `kiosk` verlässt die Verwaltung. */
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
  /** Nur die Sicherungskachel: rot, sobald sie fällig ist. */
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

  // Ohne Ziel bleibt es eine Anzeige. Ein Knopf, der nichts tut, ist schlimmer als kein Knopf.
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

  /** Abmelden und neu laden: Danach steht die Besucheransicht frisch da. */
  async function reload() {
    await leave();
    window.location.reload();
  }

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
        {/* Der einzige Weg hier heraus statt tiefer hinein -- derselbe wie „Verwaltung beenden". */}
        <Figure
          label={t.admin.overview.onMap}
          value={String(data.on_map)}
          onClick={() => onNavigate({ section: "kiosk" })}
        />
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

      {/* Im Kiosk gibt es keine Browser-Bedienung -- kein Reload-Knopf, keine Adressleiste, keine
          Tastatur. Ohne diesen Knopf bliebe bei einer verhakten Anzeige nur der Netzstecker (oder
          fünf Minuten warten, bis der Leerlauf neu lädt). Er meldet zugleich ab, damit danach die
          Besucheransicht dasteht und nicht die Verwaltung. */}
      <div className="overview__repair">
        <button type="button" className="button" onClick={() => void reload()}>
          {t.admin.overview.reload}
        </button>
        <p className="admin__note">{t.admin.overview.reloadHint}</p>
      </div>
    </div>
  );
}
