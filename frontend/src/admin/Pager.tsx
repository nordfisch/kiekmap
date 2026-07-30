/**
 * „Zurück · Seite 2 von 8 · Weiter" unter einer Liste.
 *
 * Seitenweise statt „Weitere anzeigen": Wer ein Foto bearbeitet, kommt danach auf dieselbe Seite
 * zurück. Beim Abarbeiten von „Ohne Ort" ist das der Unterschied zwischen Weiterarbeiten und
 * Wiederfinden.
 *
 * Passt alles auf eine Seite, ist hier nichts — bei siebenundzwanzig Fotos soll die Verwaltung
 * nicht nach Aktenverwaltung aussehen.
 */

import { t } from "../texte/de";
import { PAGE_SIZE, pageCount, pageNumber } from "./paging";

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
