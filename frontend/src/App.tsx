import { type CSSProperties, useEffect, useState } from "react";

import { AdminApp } from "./admin/AdminApp";
import { PinPad } from "./admin/PinPad";
import { Crest } from "./kiosk/Crest";
import { HelpPanel } from "./kiosk/HelpPanel";
import { MapView } from "./kiosk/MapView";
import { PhotoOverlay } from "./kiosk/PhotoOverlay";
import { TimeSlider } from "./kiosk/TimeSlider";
import { type Region, loadRegion } from "./region";
import { useAdmin } from "./store/admin";
import { useContribute } from "./store/contribute";
import { useKiosk } from "./store/kiosk";
import { t } from "./text/de";

function MapNotice() {
  const total = useKiosk((s) => s.total);
  const truncated = useKiosk((s) => s.truncated);
  const loading = useKiosk((s) => s.loading);
  const error = useKiosk((s) => s.error);

  if (error) return <div className="notice notice--error">{error}</div>;
  if (truncated) return <div className="notice">{t.map.tooMany(total)}</div>;
  if (!loading && total === 0) return <div className="notice">{t.map.noPhotos}</div>;
  return null;
}

export function App() {
  const [region, setRegion] = useState<Region | null>(null);
  // Everything complete means: a task was fetched and there was none. The thank-you does not
  // count yet -- it should be allowed to finish before the column disappears.
  const complete = useContribute((s) => s.task !== null && s.task.photo === null && !s.thanks);
  const [error, setError] = useState<string | null>(null);
  const view = useAdmin((s) => s.view);
  const askPin = useAdmin((s) => s.askPin);
  const restore = useAdmin((s) => s.restore);

  useEffect(() => {
    const abort = new AbortController();
    loadRegion(abort.signal)
      .then(setRegion)
      .catch((e: unknown) => {
        if (abort.signal.aborted) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    return () => abort.abort();
  }, []);

  // A reload during work should not ask for the PIN again.
  useEffect(() => {
    void restore();
  }, [restore]);

  if (error) return <div className="splash splash--error">{error}</div>;
  if (!region) return <div className="splash">{t.app.loadingMap}</div>;

  // The admin area replaces the kiosk rather than covering it: the map would keep loading tiles
  // behind it for nothing, and on a Pi that is not free.
  if (view === "admin") return <AdminApp />;

  return (
    <>
      {/* Two columns, two rows:
       *
       *     Titel  │ Zeitschieber
       *     ───────┼─────────────
       *     Hilf   │ Karte
       *     mit    │
       *
       * The slider still sits directly above the map it filters, and the arms head the panel
       * rather than covering the map. The grid itself is in styles/global.css. */}
      <div className={complete ? "app app--complete" : "app"}>
        <header className="app__title">
          <Crest regionName={region.name} />
          {/* The title is the door into the admin area -- deliberately without an underline: it
              is the heading of this device, and it should not read as a link to a visitor. The
              PIN is the lock, the same as it always was; only the surface has changed hands with
              the arms beside it. See decisions.md, point 26. */}
          <h1 className="app__heading">
            <button
              type="button"
              className="app__heading-door"
              title={t.admin.cornerHint}
              onClick={() => askPin()}
            >
              <span className="app__heading-lead">{t.app.titleLead}</span>
              {/* The length of the name goes into the CSS as a number, because CSS cannot measure
                  text. That one figure is what lets the header keep its promise -- no line ever
                  wraps -- for "Klein Nordende-Lieth" and not only for "Holm". The arithmetic is
                  in styles/global.css at .app__heading-place. */}
              <span
                className="app__heading-place"
                style={{ "--name-length": region.name.length } as CSSProperties}
              >
                {region.name}
              </span>
            </button>
          </h1>
        </header>

        <TimeSlider />

        {/* When everything is complete the column falls away entirely rather than leaving a
              success message standing -- and the map gets the width. */}
        {!complete && <HelpPanel />}

        <div className="app__map">
          <MapView region={region} />
          <MapNotice />
        </div>
      </div>

      <PhotoOverlay />
      {view === "pin" && <PinPad />}
    </>
  );
}
