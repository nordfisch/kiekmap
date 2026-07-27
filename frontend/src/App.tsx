import { useEffect, useState } from "react";

import { MapView } from "./kiosk/MapView";
import { PhotoOverlay } from "./kiosk/PhotoOverlay";
import { TimeSlider } from "./kiosk/TimeSlider";
import { type Region, loadRegion } from "./region";
import { useKiosk } from "./store/kiosk";

function Kartenmeldung() {
  const total = useKiosk((s) => s.total);
  const truncated = useKiosk((s) => s.truncated);
  const laedt = useKiosk((s) => s.laedt);
  const fehler = useKiosk((s) => s.fehler);

  if (fehler) return <div className="meldung meldung--fehler">{fehler}</div>;
  if (truncated) {
    return (
      <div className="meldung">
        {total} Fotos in diesem Ausschnitt — für mehr Übersicht näher heranzoomen
      </div>
    );
  }
  if (!laedt && total === 0) {
    return <div className="meldung">Hier gibt es noch keine Fotos im gewählten Zeitraum.</div>;
  }
  return null;
}

export function App() {
  const [region, setRegion] = useState<Region | null>(null);
  const [fehler, setFehler] = useState<string | null>(null);

  useEffect(() => {
    const abbruch = new AbortController();
    loadRegion(abbruch.signal)
      .then(setRegion)
      .catch((e: unknown) => {
        if (abbruch.signal.aborted) return;
        setFehler(e instanceof Error ? e.message : String(e));
      });
    return () => abbruch.abort();
  }, []);

  if (fehler) return <div className="hinweis hinweis--fehler">{fehler}</div>;
  if (!region) return <div className="hinweis">Karte wird geladen …</div>;

  return (
    <>
      <div className="app">
        {/* Linke Spalte: Karte, darunter der Zeitschieber. Der Schieber filtert die Karte, also
            steht er auch nur unter ihr -- nicht unter dem Seitenbereich. */}
        <div className="app__karte">
          <MapView region={region} />
          <Kartenmeldung />
          <TimeSlider />
        </div>

        {/* Rechte Spalte ueber die volle Hoehe. */}
        <aside className="app__hilf-mit">
          <h2>Hilf mit</h2>
          <p className="platzhalter">
            Hier werden Fotos gezeigt, bei denen Ort oder Jahr fehlen &middot; Stufe 7
          </p>
        </aside>
      </div>

      <PhotoOverlay />
    </>
  );
}
