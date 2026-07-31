import { useEffect, useState } from "react";

import { AdminApp } from "./admin/AdminApp";
import { AdminGate } from "./admin/AdminGate";
import { PinPad } from "./admin/PinPad";
import { HelpPanel } from "./kiosk/HelpPanel";
import { MapView } from "./kiosk/MapView";
import { PhotoOverlay } from "./kiosk/PhotoOverlay";
import { TimeSlider } from "./kiosk/TimeSlider";
import { type Region, loadRegion } from "./region";
import { useAdmin } from "./store/admin";
import { useKiosk } from "./store/kiosk";
import { t } from "./texte/de";

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
  const [error, setError] = useState<string | null>(null);
  const view = useAdmin((s) => s.view);
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
      <div className="app">
        <header className="app__title">
          <AdminGate regionName={region.name} />
          <h1 className="app__heading">
            <span className="app__heading-lead">{t.app.titleLead}</span>
            <span className="app__heading-place">{region.name}</span>
          </h1>
        </header>

        <TimeSlider />

        <HelpPanel />

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
