/**
 * A title suggestion from the file name.
 *
 * Scans arrive as "Kirchweih_1932_Muehle.jpg" or "umzug-hauptstrasse (2).tif" -- the file name is
 * usually the only description that exists, and typing it a second time is work someone already
 * did at the scanner.
 *
 * Only a suggestion: it fills the field in the upload table and is not stored until the row is
 * confirmed. Nothing here writes to the database.
 */

/** Extensions we might see. Cutting at the last dot would eat into "St. Martin 1955". */
const EXTENSION = /\.(jpe?g|png|tiff?|webp|gif|bmp)$/i;

export function titleFromFilename(filename: string): string {
  return filename
    .replace(EXTENSION, "")
    // Underscores are always a stand-in for a space.
    .replace(/_+/g, " ")
    // A hyphen with spaces around it separates; one inside a word belongs to it ("Süd-West").
    .replace(/\s+-\s+/g, " ")
    // "bild (2)" is a copy counter, not a title.
    .replace(/\s*\(\d+\)\s*$/, "")
    .replace(/\s+/g, " ")
    .trim();
}
