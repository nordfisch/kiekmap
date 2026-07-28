import { useEffect, useState } from "react";

import { HelpPanel } from "./kiosk/HelpPanel";
import { MapView } from "./kiosk/MapView";
import { PhotoOverlay } from "./kiosk/PhotoOverlay";
import { TimeSlider } from "./kiosk/TimeSlider";
import { type Region, loadRegion } from "./region";
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

  if (error) return <div className="splash splash--error">{error}</div>;
  if (!region) return <div className="splash">{t.app.loadingMap}</div>;

  return (
    <>
      <div className="app">
        {/* Left column: map with the time slider below it. The slider filters the map, so it sits
            only under the map -- not under the side panel. */}
        <div className="app__map">
          <MapView region={region} />
          <MapNotice />
          <TimeSlider />
        </div>

        {/* Right column, full height. */}
        <HelpPanel region={region} />
      </div>

      <PhotoOverlay />
    </>
  );
}
