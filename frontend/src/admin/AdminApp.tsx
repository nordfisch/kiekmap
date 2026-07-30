/**
 * The admin area.
 *
 * A full screen of its own rather than a panel over the map: whoever is in here is working, not
 * looking at photographs. The way back is the one button in the header.
 *
 * The remaining time is shown because the session ends on its own. Every request pushes it back,
 * so nobody is thrown out while working -- but a login forgotten in the evening does close.
 */

import { useEffect, useState } from "react";

import { type Selection } from "../api/admin";
import { useAdmin } from "../store/admin";
import { t } from "../texte/de";
import { Backup } from "./Backup";
import { Changes } from "./Changes";
import { ImportLog } from "./ImportLog";
import { ImportView } from "./ImportView";
import { Overview, type Target } from "./Overview";
import { PhotoCare } from "./PhotoCare";

/**
 * Reihenfolge mit Absicht: erst die Pflege des Bestands, dann das Hinzufügen, dann das
 * Technische. „Moderation" steht neben „Fotos", weil beides Inhaltsarbeit ist.
 */
type Section = "overview" | "photos" | "moderation" | "import" | "log" | "backup";

const SECTIONS: { value: Section; label: string }[] = [
  { value: "overview", label: t.admin.shell.sections.overview },
  { value: "photos", label: t.admin.shell.sections.photos },
  { value: "moderation", label: t.admin.shell.sections.moderation },
  { value: "import", label: t.admin.shell.sections.import },
  { value: "log", label: t.admin.shell.sections.log },
  { value: "backup", label: t.admin.shell.sections.backup },
];

const TICK_MS = 10_000;

export function AdminApp() {
  const leave = useAdmin((s) => s.leave);
  const dropSession = useAdmin((s) => s.dropSession);
  const [section, setSection] = useState<Section>("overview");
  const [photoFilter, setPhotoFilter] = useState<Selection>("all");
  const [minutes, setMinutes] = useState<number | null>(null);

  /** Ein Weg für alle Kacheln der Übersicht: Abschnitt und Filter zusammen setzen. */
  function navigate(target: Target) {
    // „Auf der Karte zu sehen" führt aus der Verwaltung heraus, denselben Weg wie der Knopf oben
    // rechts -- also mit Abmelden. Wer zurück will, gibt die PIN erneut ein.
    if (target.section === "kiosk") {
      void leave();
      return;
    }
    if (target.filter) setPhotoFilter(target.filter);
    setSection(target.section);
  }

  useEffect(() => {
    function tick() {
      // Read from the store rather than from a dependency: every request pushes expiresAt back,
      // and re-creating this interval on each of them would be pointless churn.
      const { expiresAt } = useAdmin.getState();
      if (expiresAt === null) return;
      const left = expiresAt - Date.now();
      if (left <= 0) dropSession();
      else setMinutes(Math.ceil(left / 60_000));
    }

    tick();
    const timer = setInterval(tick, TICK_MS);
    return () => clearInterval(timer);
  }, [dropSession]);

  return (
    <div className="admin">
      <header className="admin__header">
        <h1 className="admin__title">{t.admin.shell.title}</h1>
        {minutes !== null && (
          <span className="admin__remaining">{t.admin.shell.remaining(minutes)}</span>
        )}
        <button type="button" className="button admin__leave" onClick={() => void leave()}>
          {t.admin.shell.leave}
        </button>
      </header>

      <nav className="tabs">
        {SECTIONS.map((entry) => (
          <button
            key={entry.value}
            type="button"
            className={section === entry.value ? "tab tab--active" : "tab"}
            onClick={() => setSection(entry.value)}
          >
            {entry.label}
          </button>
        ))}
      </nav>

      <main className="admin__body">
        {section === "overview" && <Overview onNavigate={navigate} />}
        {/* Remounted when the filter changes, so the list starts on the right one. */}
        {section === "photos" && <PhotoCare key={photoFilter} initialFilter={photoFilter} />}
        {section === "import" && (
          <ImportView onReview={() => navigate({ section: "photos", filter: "without_location" })} />
        )}
        {section === "moderation" && <Changes />}
        {section === "log" && <ImportLog />}
        {section === "backup" && <Backup />}
      </main>
    </div>
  );
}
