/**
 * "Zurück · Seite 2 von 8 · Weiter" underneath a list.
 *
 * Pages rather than "show more": whoever edits a photo comes back to the same page afterwards.
 * When working through "Ohne Ort" that is the difference between carrying on and searching again.
 *
 * If everything fits on one page there is nothing here -- with twenty-seven photos the admin area
 * should not look like records management.
 */

import { t } from "../text";
import { PAGE_SIZE, pageCount, pageNumber } from "./pagination";

export function Pager({
  total,
  offset,
  onOffset,
  size = PAGE_SIZE,
}: {
  total: number;
  offset: number;
  onOffset: (offset: number) => void;
  size?: number;
}) {
  const pages = pageCount(total, size);
  if (pages <= 1) return null;

  const current = pageNumber(offset, size);

  return (
    <div className="pager">
      <button
        type="button"
        className="button"
        disabled={current <= 1}
        onClick={() => onOffset(Math.max(0, offset - size))}
      >
        {t.admin.pager.prev}
      </button>
      <span className="pager__label">{t.admin.pager.page(current, pages)}</span>
      <button
        type="button"
        className="button"
        disabled={current >= pages}
        onClick={() => onOffset(offset + size)}
      >
        {t.admin.pager.next}
      </button>
    </div>
  );
}
