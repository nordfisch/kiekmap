import type { de } from "./de";

/**
 * The shape every language has to fill.
 *
 * `typeof de` is the whole construction. A missing key in `en.ts`, a function with the wrong
 * number of arguments, a string where a function belongs -- each of them stops `tsc`, and `tsc`
 * runs in `make check` before anything is built. That is stricter than Java's `ResourceBundle`,
 * where the same mistake surfaces at runtime, in front of whoever is standing at the device.
 *
 * It is also why no i18n library is needed here. `i18next` brings lazy loading, ICU plural rules
 * and switching at runtime; a kiosk with two languages and one fixed setting needs none of it,
 * and every dependency is one more dependency in offline operation.
 */
export type Texts = typeof de;

/** The values `KIEKMAP_LANGUAGE` accepts. The backend refuses anything else at startup. */
export type Language = "de" | "en";
