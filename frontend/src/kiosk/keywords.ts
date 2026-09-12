/**
 * Which keyword buttons stand in the corner of the map.
 *
 * The configured ones always. A keyword chosen from the detail view that is not among them stands
 * beside them for as long as it is chosen: switched off or replaced, it disappears with its button.
 * Without it the visitor would see a filtered map and no button that says so or switches it off.
 */
export function cornerTags(offered: readonly string[], chosen: string | null): string[] {
  if (chosen === null || offered.includes(chosen)) return [...offered];
  return [...offered, chosen];
}
