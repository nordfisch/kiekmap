/**
 * Die Region des Museumsorts.
 *
 * Wird zur Laufzeit von `/tiles/region.json` geholt und nicht ins Bundle gebacken -- aus demselben
 * Grund wie die Kartendatei selbst: sie gehoert zum Ort, nicht zur Software. So laesst sich der
 * Kartenausschnitt auf dem Pi anpassen, ohne das Frontend neu zu bauen.
 */

export type Region = {
  name: string;
  /** [minLon, minLat, maxLon, maxLat] in WGS84 */
  bbox: [number, number, number, number];
  center: [number, number];
  defaultZoom: number;
  minZoom: number;
  maxZoom: number;
};

export async function loadRegion(signal?: AbortSignal): Promise<Region> {
  const response = await fetch("/tiles/region.json", { signal });
  if (!response.ok) {
    throw new Error(
      `Die Region konnte nicht geladen werden (HTTP ${response.status}). ` +
        `Wurde "make tiles" ausgefuehrt?`,
    );
  }
  return (await response.json()) as Region;
}
