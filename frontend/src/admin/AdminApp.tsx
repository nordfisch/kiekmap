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

import { useAdmin } from "../store/admin";
import { t } from "../texte/de";
import { Backup } from "./Backup";
import { BatchUpload } from "./BatchUpload";
import { Changes } from "./Changes";
import { ImportLog } from "./ImportLog";
import { Overview } from "./Overview";
import { PhotoCare } from "./PhotoCare";

type Section = "overview" | "photos" | "upload" | "changes" | "imports" | "backup";

const SECTIONS: { value: Section; label: string }[] = [
  { value: "overview", label: t.admin.shell.sections.overview },
  { value: "photos", label: t.admin.shell.sections.photos },
  { value: "upload", label: t.admin.shell.sections.upload },
  { value: "changes", label: t.admin.shell.sections.changes },
  { value: "imports", label: t.admin.shell.sections.imports },
  { value: "backup", label: t.admin.shell.sections.backup },
];

const TICK_MS = 10_000;

export function AdminApp() {
  const leave = useAdmin((s) => s.leave);
  const dropSession = useAdmin((s) => s.dropSession);
  const [section, setSection] = useState<Section>("overview");
  const [photoFilter, setPhotoFilter] = useState<"all" | "incomplete">("all");
  const [minutes, setMinutes] = useState<number | null>(null);

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
        {section === "overview" && (
          <Overview
            onShowIncomplete={() => {
              setPhotoFilter("incomplete");
              setSection("photos");
            }}
            onShowBackup={() => setSection("backup")}
          />
        )}
        {/* Remounted when the filter changes, so the list starts on the right one. */}
        {section === "photos" && <PhotoCare key={photoFilter} initialFilter={photoFilter} />}
        {section === "upload" && <BatchUpload />}
        {section === "changes" && <Changes />}
        {section === "imports" && <ImportLog />}
        {section === "backup" && <Backup />}
      </main>
    </div>
  );
}
