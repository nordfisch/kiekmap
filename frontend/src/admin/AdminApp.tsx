/**
 * The admin area.
 *
 * A full screen of its own rather than a panel over the map: whoever is in here is working, not
 * looking at photographs. The way back is the one button in the header.
 *
 * The remaining time is shown because the session ends on its own. Every request pushes it back,
 * so nobody is thrown out while working -- but a login forgotten in the evening does close.
 */

import { useEffect, useLayoutEffect, useRef, useState } from "react";

import { type Selection } from "../api/admin";
import { useAdmin } from "../store/admin";
import { t } from "../text/de";
import { Backup } from "./Backup";
import { Changes } from "./Changes";
import { ImportLog } from "./ImportLog";
import { ImportView } from "./ImportView";
import { Overview, type Target } from "./Overview";
import { PhotoCare } from "./PhotoCare";
import { ScrollAreaProvider } from "./scrollArea";

/**
 * The order is deliberate: first tending the collection, then adding to it, then the technical
 * part. "Moderation" sits beside "Fotos" because both are work on content.
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
  const body = useRef<HTMLElement>(null);

  // Changing section starts at the top. Otherwise you would stand in the new section at the point
  // you had scrolled to in the old one -- in "Protokoll" after a long photo list, in mid-air.
  useLayoutEffect(() => {
    body.current?.scrollTo({ top: 0 });
  }, [section]);

  /** One route for every tile of the overview: set section and filter together. */
  function navigate(target: Target) {
    // "Auf der Karte zu sehen" leads out of the admin area, the same way as the button top right
    // -- so with signing out and reloading. Whoever wants back in types the PIN again.
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

      {/* The scrolling area, not the view inside it -- see scrollArea.tsx. */}
      <main className="admin__body" ref={body}>
        <ScrollAreaProvider value={body}>
          {section === "overview" && <Overview onNavigate={navigate} />}
          {/* Remounted when the filter changes, so the list starts on the right one. */}
          {section === "photos" && <PhotoCare key={photoFilter} initialFilter={photoFilter} />}
          {section === "import" && (
            <ImportView
              onReview={() => navigate({ section: "photos", filter: "without_location" })}
            />
          )}
          {section === "moderation" && <Changes />}
          {section === "log" && <ImportLog />}
          {section === "backup" && <Backup />}
        </ScrollAreaProvider>
      </main>
    </div>
  );
}
