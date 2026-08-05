/**
 * Fotos, die auf demselben Punkt liegen.
 *
 * Am Gasthof Petersen liegen acht Fotos auf identischen Koordinaten. supercluster fasst sie
 * unterhalb von `CLUSTER_MAXZOOM` zu einem Kreis zusammen, darüber gar nicht mehr — dann werden
 * es acht Marker exakt übereinander, von denen nur der oberste erreichbar ist. Und der Weg dorthin
 * war eine Sackgasse: Ein Tipp auf den Kreis zoomte genau in diesen Stapel hinein, denn
 * **identische Punkte trennen sich bei keiner Zoomstufe.**
 *
 * Deshalb wird hier **vor** dem Clustern gruppiert. supercluster sieht damit gar keine Dubletten
 * mehr, und ein Stapel ist auf jeder Zoomstufe ein Marker.
 */

import type { PhotoMarker } from "../api/client";

/**
 * Fünf Nachkommastellen, also rund ein Meter.
 *
 * Trifft den tatsächlichen Fall: Fotos, die über die Ortssuche verortet wurden, tragen exakt
 * dieselbe Koordinate der Straße. Wer den Punkt von Hand gesetzt hat, liegt daneben und bleibt ein
 * eigener Marker — richtig so, denn dann *ist* es eine andere Stelle.
 */
const PLACES = 5;

export type Stack = {
  lat: number;
  lon: number;
  /** In der Reihenfolge der Liste; vorne das zuletzt bearbeitete Foto. */
  photos: PhotoMarker[];
};

function key(photo: PhotoMarker): string {
  return `${photo.lat.toFixed(PLACES)},${photo.lon.toFixed(PLACES)}`;
}

export function groupByLocation(photos: PhotoMarker[]): Stack[] {
  const stacks = new Map<string, Stack>();

  for (const photo of photos) {
    const id = key(photo);
    const stack = stacks.get(id);
    if (stack) stack.photos.push(photo);
    // Der Ort des Stapels ist der des ersten Fotos -- die anderen liegen ohnehin im Meter daneben.
    else stacks.set(id, { lat: photo.lat, lon: photo.lon, photos: [photo] });
  }

  return [...stacks.values()];
}
