/**
 * Der "Hilf mit"-Bereich am rechten Rand.
 *
 * Bei historischen Scans stehen Ort und Jahr nirgends in der Datei -- wer den Ort kennt, weiß es
 * aber oft auf den ersten Blick. Dieser Bereich ist deshalb nicht Beiwerk, sondern der Hauptweg,
 * auf dem das System an Daten kommt.
 */

import { useEffect } from "react";

import { useHilfMit } from "../store/hilfmit";
import { JahrAufgabe } from "./JahrAufgabe";
import { OrtsAufgabe } from "./OrtsAufgabe";

export function HelpPanel() {
  const bedarf = useHilfMit((s) => s.bedarf);
  const aufgabe = useHilfMit((s) => s.aufgabe);
  const laedt = useHilfMit((s) => s.laedt);
  const fehler = useHilfMit((s) => s.fehler);
  const dank = useHilfMit((s) => s.dank);
  const hole = useHilfMit((s) => s.hole);
  const ueberspringen = useHilfMit((s) => s.ueberspringen);

  useEffect(() => {
    void hole();
  }, [hole]);

  const foto = aufgabe?.photo ?? null;

  return (
    <aside className="hilf-mit">
      <h2 className="hilf-mit__titel">Hilf mit</h2>

      {dank ? (
        <div className="hilf-mit__dank">
          <span className="hilf-mit__haken" aria-hidden="true">
            ✓
          </span>
          <p>{dank}</p>
        </div>
      ) : !foto ? (
        <p className="hilf-mit__leer">
          {laedt
            ? "…"
            : fehler
              ? fehler
              : "Zurzeit ist alles vollständig. Vielen Dank an alle, die geholfen haben!"}
        </p>
      ) : (
        <>
          <p className="hilf-mit__frage">
            {bedarf === "location" ? "Wo ist das?" : "Von wann ist dieses Bild?"}
          </p>

          <img
            className="hilf-mit__bild"
            src={foto.thumb_url}
            alt={foto.title ?? "Foto, dem eine Angabe fehlt"}
            style={{ aspectRatio: `${foto.width} / ${foto.height}` }}
          />

          <div className="hilf-mit__bekannt">
            {foto.title && <span className="hilf-mit__foto-titel">{foto.title}</span>}
            {/* Was schon bekannt ist, hilft beim Erkennen -- ein Jahr grenzt die Möglichkeiten
                erheblich ein. */}
            {bedarf === "location" && !foto.needs_date && <span>{foto.date_label}</span>}
            {bedarf === "date" && foto.place_name && <span>{foto.place_name}</span>}
          </div>

          {fehler && <p className="hilf-mit__fehler">{fehler}</p>}

          {bedarf === "location" ? <OrtsAufgabe /> : <JahrAufgabe />}

          <button type="button" className="knopf knopf--leise hilf-mit__weiter" onClick={ueberspringen}>
            Weiß ich nicht — nächstes Foto
          </button>

          {aufgabe && aufgabe.open_count > 1 && (
            <p className="hilf-mit__offen">
              Noch {aufgabe.open_count} Fotos ohne {bedarf === "location" ? "Ort" : "Jahr"}
            </p>
          )}
        </>
      )}
    </aside>
  );
}
