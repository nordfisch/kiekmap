// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The area below the two source tiles.
 *
 * It always sits in the same place and only changes its content -- switching source would
 * otherwise make the form jump, because on the left there would be an operating-system file
 * field and on the right a folder list. Dashed while it waits, full border as soon as something
 * is there. Exactly the choreography of the backup area, which somebody from the team already
 * knows.
 */

import { type ReactNode, useRef, useState } from "react";

import { t } from "../text/de";

/** The same formats the file field accepts. */
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
  /** Full border instead of dashed: there is something to see. */
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
 * The area for "Vom Rechner": take files, by button or by dropping.
 *
 * **The button is the reliable route.** On the touch kiosk there is no dragging and dropping;
 * dropping is the extra for those sitting at a computer. Hence a real button that triggers the
 * hidden file field, and not a label dressed up as one -- that would be unreachable by keyboard.
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
      className={["dropzone", chosen ? "dropzone--filled" : "", over ? "dropzone--over" : ""]
        .filter(Boolean)
        .join(" ")}
      onDragOver={(event) => {
        // Without intercepting it the browser simply opens the file itself.
        event.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(event) => {
        event.preventDefault();
        setOver(false);
        // Whatever else lay in the folder stays there -- not sent along without a word.
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
