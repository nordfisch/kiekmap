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
      <div className="app">
        {/* Left column: map with the time slider below it. The slider filters the map, so it sits
            only under the map -- not under the side panel. */}
        <div className="app__map">
          <MapView region={region} />
          <AdminGate regionName={region.name} />
          <MapNotice />
          <TimeSlider />
        </div>

        {/* Right column, full height. */}
        <HelpPanel region={region} />
      </div>

      <PhotoOverlay />
      {view === "pin" && <PinPad />}
    </>
  );
}
