/**
 * Zeitraum-Schieber mit zwei Griffen.
 *
 * Eigenbau statt Bibliothek, aus drei Gruenden, die jeder fuer sich schon reichen wuerde:
 *
 *   - Die Griffe muessen fuer Finger gross sein. Ein Bereichsregler mit 16-px-Knopf ist am
 *     Touchscreen unbedienbar; die Fasszone ist hier so gross wie eine Fingerkuppe.
 *   - Hinter dem Balken liegt das Histogramm. Es zeigt dem Besucher, wo im Zeitraum ueberhaupt
 *     etwas zu finden ist -- ohne das schiebt man blind.
 *   - Zwei Griffe auf einer Achse mit Zeigerereignissen sind ueberschaubar; die Anpassung einer
 *     fremden Komponente an all das waere mehr Arbeit als das hier.
 */

import { type PointerEvent as ReactPointerEvent, useCallback, useMemo, useRef, useState } from "react";

import { useKiosk } from "../store/kiosk";

type Griff = "von" | "bis";

/** Auf ganze Jahre runden, aber die Spanne auf Jahrzehnte aufrunden -- das liest sich besser. */
function aufJahrzehnt(jahr: number, richtung: "ab" | "auf"): number {
  return richtung === "ab" ? Math.floor(jahr / 10) * 10 : Math.ceil(jahr / 10) * 10;
}

export function TimeSlider() {
  const histogramm = useKiosk((s) => s.histogramm);
  const spanne = useKiosk((s) => s.spanne);
  const zeitraum = useKiosk((s) => s.zeitraum);
  const setzeZeitraum = useKiosk((s) => s.setzeZeitraum);

  const bahn = useRef<HTMLDivElement>(null);

  // Der gezogene Griff steht in einem Ref, nicht nur im State.
  //
  // Zeigerereignisse kommen schneller, als React neu rendert: bei einer zuegigen Wischbewegung
  // treffen die ersten pointermove-Ereignisse ein, bevor der State-Wechsel sichtbar ist. Ein
  // Handler, der dann noch den alten Wert liest, verwirft die Bewegung -- der Griff bleibt kleben.
  // Das Ref wird synchron gesetzt, der State dient nur der Darstellung.
  const gezogenRef = useRef<Griff | null>(null);
  const [gezogen, setGezogen] = useState<Griff | null>(null);

  const grenzen = useMemo(() => {
    if (!spanne) return null;
    return { min: aufJahrzehnt(spanne.von, "ab"), max: aufJahrzehnt(spanne.bis, "auf") };
  }, [spanne]);

  const jahrZuAnteil = useCallback(
    (jahr: number) => {
      if (!grenzen || grenzen.max === grenzen.min) return 0;
      return (jahr - grenzen.min) / (grenzen.max - grenzen.min);
    },
    [grenzen],
  );

  const positionZuJahr = useCallback(
    (clientX: number): number => {
      if (!bahn.current || !grenzen) return 0;
      const kasten = bahn.current.getBoundingClientRect();
      const anteil = Math.min(1, Math.max(0, (clientX - kasten.left) / kasten.width));
      return Math.round(grenzen.min + anteil * (grenzen.max - grenzen.min));
    },
    [grenzen],
  );

  const verschiebe = useCallback(
    (griff: Griff, clientX: number) => {
      if (!zeitraum || !grenzen) return;
      const jahr = positionZuJahr(clientX);
      if (griff === "von") {
        setzeZeitraum({ von: Math.min(jahr, zeitraum.bis), bis: zeitraum.bis });
      } else {
        setzeZeitraum({ von: zeitraum.von, bis: Math.max(jahr, zeitraum.von) });
      }
    },
    [zeitraum, grenzen, positionZuJahr, setzeZeitraum],
  );

  function beiZeigerStart(griff: Griff) {
    return (ereignis: ReactPointerEvent<HTMLElement>) => {
      ereignis.preventDefault();
      ereignis.stopPropagation();
      // Zeiger einfangen: der Finger darf beim Ziehen den Griff verlassen, ohne dass die Bewegung
      // abreisst. Ohne das rutscht man am Touchscreen staendig heraus.
      ereignis.currentTarget.setPointerCapture(ereignis.pointerId);
      gezogenRef.current = griff;
      setGezogen(griff);
    };
  }

  function beiZeigerBewegung(ereignis: ReactPointerEvent<HTMLElement>) {
    if (!gezogenRef.current) return;
    verschiebe(gezogenRef.current, ereignis.clientX);
  }

  function beiZeigerEnde() {
    gezogenRef.current = null;
    setGezogen(null);
  }

  /** Tippen auf die Bahn bewegt den naeheren Griff dorthin. */
  function beiBahnKlick(ereignis: ReactPointerEvent<HTMLDivElement>) {
    if (!zeitraum || gezogenRef.current) return;
    const jahr = positionZuJahr(ereignis.clientX);
    const griff: Griff =
      Math.abs(jahr - zeitraum.von) <= Math.abs(jahr - zeitraum.bis) ? "von" : "bis";
    verschiebe(griff, ereignis.clientX);
  }

  if (!grenzen || !zeitraum || !histogramm) {
    return (
      <div className="zeitleiste zeitleiste--leer">
        {histogramm ? "Für diesen Ausschnitt gibt es keine datierten Fotos." : "…"}
      </div>
    );
  }

  const hoechster = Math.max(1, ...histogramm.decades.map((d) => d.count));
  const vonAnteil = jahrZuAnteil(zeitraum.von);
  const bisAnteil = jahrZuAnteil(zeitraum.bis);

  return (
    <div className="zeitleiste">
      <div className="zeitleiste__kopf">
        <span className="zeitleiste__auswahl">
          {zeitraum.von} <span className="zeitleiste__bis">bis</span> {zeitraum.bis}
        </span>
        {histogramm.undated > 0 && (
          <span className="zeitleiste__undatiert">
            {histogramm.undated} {histogramm.undated === 1 ? "Foto" : "Fotos"} ohne Jahr
          </span>
        )}
      </div>

      <div
        ref={bahn}
        className="zeitleiste__bahn"
        onPointerDown={beiBahnKlick}
        onPointerMove={beiZeigerBewegung}
        onPointerUp={beiZeigerEnde}
        onPointerCancel={beiZeigerEnde}
      >
        {/* Histogramm: wo liegt ueberhaupt etwas? */}
        <div className="zeitleiste__histogramm" aria-hidden="true">
          {histogramm.decades.map((balken) => {
            const anteil = jahrZuAnteil(balken.decade);
            const breite = 10 / (grenzen.max - grenzen.min);
            const innerhalb = balken.decade + 9 >= zeitraum.von && balken.decade <= zeitraum.bis;
            return (
              <div
                key={balken.decade}
                className={`zeitleiste__balken${innerhalb ? " zeitleiste__balken--aktiv" : ""}`}
                style={{
                  left: `${anteil * 100}%`,
                  width: `${breite * 100}%`,
                  height: `${Math.max(6, (balken.count / hoechster) * 100)}%`,
                }}
                title={`${balken.decade}er: ${balken.count}`}
              />
            );
          })}
        </div>

        <div className="zeitleiste__schiene" />
        <div
          className="zeitleiste__gewaehlt"
          style={{ left: `${vonAnteil * 100}%`, right: `${(1 - bisAnteil) * 100}%` }}
        />

        {(["von", "bis"] as const).map((griff) => (
          <div
            key={griff}
            className={`zeitleiste__griff${gezogen === griff ? " zeitleiste__griff--aktiv" : ""}`}
            style={{ left: `${(griff === "von" ? vonAnteil : bisAnteil) * 100}%` }}
            onPointerDown={beiZeigerStart(griff)}
            onPointerMove={beiZeigerBewegung}
            onPointerUp={beiZeigerEnde}
            onPointerCancel={beiZeigerEnde}
            role="slider"
            tabIndex={0}
            aria-label={griff === "von" ? "Anfangsjahr" : "Endjahr"}
            aria-valuemin={grenzen.min}
            aria-valuemax={grenzen.max}
            aria-valuenow={griff === "von" ? zeitraum.von : zeitraum.bis}
            onKeyDown={(e) => {
              const schritt = e.key === "ArrowLeft" ? -1 : e.key === "ArrowRight" ? 1 : 0;
              if (!schritt) return;
              e.preventDefault();
              const neu = (griff === "von" ? zeitraum.von : zeitraum.bis) + schritt;
              setzeZeitraum(
                griff === "von"
                  ? { von: Math.max(grenzen.min, Math.min(neu, zeitraum.bis)), bis: zeitraum.bis }
                  : { von: zeitraum.von, bis: Math.min(grenzen.max, Math.max(neu, zeitraum.von)) },
              );
            }}
          />
        ))}
      </div>

      <div className="zeitleiste__skala" aria-hidden="true">
        <span>{grenzen.min}</span>
        <span>{grenzen.max}</span>
      </div>
    </div>
  );
}
