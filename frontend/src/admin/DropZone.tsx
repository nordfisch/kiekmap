/**
 * Die Fläche unter den beiden Quellenkacheln.
 *
 * Sie steht immer an derselben Stelle und wechselt nur ihren Inhalt — beim Umschalten der Quelle
 * springt die Maske sonst, weil links ein Betriebssystem-Dateifeld und rechts eine Ordnerliste
 * stünde. Gestrichelt, solange gewartet wird; mit vollem Rand, sobald etwas da ist. Genau die
 * Dramaturgie des Sicherungsbereichs, die jemand aus dem Team schon kennt.
 */

import { type ReactNode, useRef, useState } from "react";

import { t } from "../texte/de";

/** Dieselben Formate, die auch das Dateifeld annimmt. */
const ACCEPT = "image/jpeg,image/png,image/tiff,image/webp";

function isImage(file: File): boolean {
  return ACCEPT.split(",").includes(file.type);
}

export function DropZone({
  title,
  hint,
  filled,
  children,
}: {
  /** Große erste Zeile. */
  title?: string;
  /** Graue zweite Zeile. */
  hint?: ReactNode;
  /** Voller Rand statt gestrichelt: es gibt etwas zu sehen. */
  filled?: boolean;
  children?: ReactNode;
}) {
  return (
    <div className={filled ? "dropzone dropzone--filled" : "dropzone"}>
      {title && <p className="dropzone__title">{title}</p>}
      {hint && <p className="dropzone__hint">{hint}</p>}
      {children}
    </div>
  );
}

/**
 * Die Fläche für „Vom Rechner": Dateien annehmen, per Knopf oder per Ablegen.
 *
 * **Der Knopf ist der verlässliche Weg.** Auf dem Kiosk mit Touch gibt es kein Ziehen und Ablegen;
 * das Ablegen ist die Zugabe für die, die am Rechner sitzen. Deshalb ein echter Knopf, der das
 * versteckte Dateifeld auslöst, und kein als Knopf verkleidetes Label — das wäre mit der Tastatur
 * nicht erreichbar.
 */
export function FileDropZone({
  files,
  onFiles,
}: {
  files: File[];
  onFiles: (files: File[]) => void;
}) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  const chosen = files.length > 0;

  return (
    <div
      className={[
        "dropzone",
        chosen ? "dropzone--filled" : "",
        over ? "dropzone--over" : "",
      ]
        .filter(Boolean)
        .join(" ")}
      onDragOver={(event) => {
        // Ohne das Abfangen öffnet der Browser die Datei einfach selbst.
        event.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(event) => {
        event.preventDefault();
        setOver(false);
        // Was sonst noch im Ordner lag, bleibt liegen -- nicht kommentarlos mitschicken.
        onFiles(Array.from(event.dataTransfer.files).filter(isImage));
      }}
    >
      <p className="dropzone__title">
        {chosen ? t.admin.upload.chosen(files.length) : t.admin.upload.dropTitle}
      </p>
      <p className="dropzone__hint">
        {!chosen && <span>{t.admin.upload.dropHint} </span>}
        <button type="button" className="button" onClick={() => input.current?.click()}>
          {chosen ? t.admin.upload.dropAgain : t.admin.upload.dropButton}
        </button>
      </p>

      <input
        ref={input}
        className="visually-hidden"
        type="file"
        multiple
        accept={ACCEPT}
        onChange={(event) => onFiles(Array.from(event.target.files ?? []))}
      />
    </div>
  );
}
