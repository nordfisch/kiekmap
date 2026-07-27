/**
 * Fotos an ihrem Aufnahmeort auf der Karte.
 *
 * Echte Vorschaubilder als Marker sind das Ziel -- ein Bild an seinem Ort ist unmittelbar
 * verstaendlich, ein Punkt ist es nicht. Bei hoher Dichte werden daraus aber hunderte Bildelemente,
 * die der Pi beim Schieben nicht mehr fluessig bewegt. Deshalb fasst supercluster nahe
 * beieinanderliegende Fotos zu einem Kreis mit Anzahl zusammen; beim Hineinzoomen loesen sie sich
 * wieder auf. Das ist zugleich die natuerlichste Geste am Touchscreen.
 */

import type maplibregl from "maplibre-gl";
import { Marker } from "maplibre-gl";
import { useEffect, useMemo, useRef } from "react";
import Supercluster from "supercluster";

import type { PhotoMarker } from "../api/client";
import { useKiosk } from "../store/kiosk";

/** Radius in Pixeln, innerhalb dessen zusammengefasst wird. Etwa eine Daumenbreite. */
const CLUSTER_RADIUS = 70;

/** Ab hier wird nicht mehr zusammengefasst -- naeher beieinander liegen Fotos selten sinnvoll. */
const CLUSTER_MAXZOOM = 17;

type FotoEigenschaften = { foto: PhotoMarker };

/** getClusters liefert Zusammenfassungen und Einzelfotos gemischt zurueck. */
type Gruppe = Supercluster.PointFeature<FotoEigenschaften | Supercluster.ClusterProperties>;

function istCluster(
  gruppe: Gruppe,
): gruppe is Supercluster.PointFeature<Supercluster.ClusterProperties> {
  return "cluster" in gruppe.properties && gruppe.properties.cluster;
}

function baueIndex(photos: PhotoMarker[]): Supercluster<FotoEigenschaften> {
  const index = new Supercluster<FotoEigenschaften>({
    radius: CLUSTER_RADIUS,
    maxZoom: CLUSTER_MAXZOOM,
  });
  index.load(
    photos.map((foto) => ({
      type: "Feature" as const,
      properties: { foto },
      geometry: { type: "Point" as const, coordinates: [foto.lon, foto.lat] },
    })),
  );
  return index;
}

function fotoElement(foto: PhotoMarker, beiKlick: () => void): HTMLElement {
  const wurzel = document.createElement("button");
  wurzel.type = "button";
  wurzel.className = "marker";
  wurzel.setAttribute(
    "aria-label",
    `${foto.title ?? "Foto"}, ${foto.date_label} — groß anzeigen`,
  );

  const bild = document.createElement("img");
  bild.className = "marker__bild";
  bild.src = foto.thumb_url;
  bild.alt = "";
  bild.loading = "lazy";
  bild.decoding = "async";
  // Hochkant und quer sollen gleich gross wirken, deshalb feste Hoehe statt fester Breite.
  bild.style.aspectRatio = `${foto.width} / ${foto.height}`;
  wurzel.appendChild(bild);

  const jahr = document.createElement("span");
  jahr.className = "marker__jahr";
  jahr.textContent = foto.date_label;
  wurzel.appendChild(jahr);

  wurzel.addEventListener("click", (ereignis) => {
    ereignis.stopPropagation();
    beiKlick();
  });
  return wurzel;
}

function clusterElement(anzahl: number, beiKlick: () => void): HTMLElement {
  const wurzel = document.createElement("button");
  wurzel.type = "button";
  wurzel.className = "cluster";
  wurzel.setAttribute("aria-label", `${anzahl} Fotos — hineinzoomen`);
  wurzel.textContent = String(anzahl);
  // Bei vielen Fotos etwas groesser, damit die Verteilung auf einen Blick lesbar ist.
  const groesse = Math.min(88, 48 + Math.log10(anzahl) * 26);
  wurzel.style.width = wurzel.style.height = `${Math.round(groesse)}px`;

  wurzel.addEventListener("click", (ereignis) => {
    ereignis.stopPropagation();
    beiKlick();
  });
  return wurzel;
}

export function PhotoLayer({ map }: { map: maplibregl.Map }) {
  const photos = useKiosk((s) => s.photos);
  const oeffneFoto = useKiosk((s) => s.oeffneFoto);
  const marker = useRef<Marker[]>([]);

  const index = useMemo(() => baueIndex(photos), [photos]);

  useEffect(() => {
    function zeichne() {
      // Marker werden vollstaendig neu gesetzt statt abgeglichen. Bei hoechstens einigen Dutzend
      // sichtbaren Elementen ist das guenstiger als der Abgleich -- und deutlich weniger Code,
      // in dem sich ein Zustandsfehler verstecken koennte.
      for (const alt of marker.current) alt.remove();
      marker.current = [];

      const grenzen = map.getBounds();
      const zoom = Math.round(map.getZoom());
      const gruppen = index.getClusters(
        [grenzen.getWest(), grenzen.getSouth(), grenzen.getEast(), grenzen.getNorth()],
        zoom,
      );

      for (const gruppe of gruppen) {
        const [lon, lat] = gruppe.geometry.coordinates as [number, number];

        if (istCluster(gruppe)) {
          const { cluster_id: clusterId, point_count: anzahl } = gruppe.properties;
          const element = clusterElement(anzahl, () => {
            // So weit hineinzoomen, dass diese Gruppe sich aufloest.
            map.easeTo({
              center: [lon, lat],
              zoom: Math.min(index.getClusterExpansionZoom(clusterId), CLUSTER_MAXZOOM + 1),
              duration: 500,
            });
          });
          marker.current.push(new Marker({ element }).setLngLat([lon, lat]).addTo(map));
        } else {
          const foto = gruppe.properties.foto;
          const element = fotoElement(foto, () => oeffneFoto(foto.id));
          marker.current.push(
            // Der Marker sitzt mit seiner Unterkante auf dem Ort, wie eine Stecknadel.
            new Marker({ element, anchor: "bottom" }).setLngLat([lon, lat]).addTo(map),
          );
        }
      }
    }

    zeichne();
    map.on("move", zeichne);
    map.on("zoom", zeichne);
    return () => {
      map.off("move", zeichne);
      map.off("zoom", zeichne);
      for (const alt of marker.current) alt.remove();
      marker.current = [];
    };
  }, [map, index, oeffneFoto]);

  return null;
}
