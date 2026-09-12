/**
 * The slide show while nobody uses the device.
 *
 * Four tiles. Every photo drifts and zooms on its own path, and every five seconds one tile turns
 * over to the next photo. The timing and its reasons are in `attract.ts`.
 *
 * **Every way out is a reload.** A tap on a photo leaves a note for the page after the reload,
 * which opens the map around that photo with its detail view (`handoff.ts`). A tap beside the
 * photos lands on the start view. Before the slide show the idle timer reloaded; the reload moved
 * to the end of the show, and it discards no more than it did before. See decisions.md, point 81.
 */

import { useEffect, useRef, useState } from "react";

import { type PhotoMarker, fetchShowcase } from "../api/client";
import { useKiosk } from "../store/kiosk";
import { t } from "../text";
import {
  BAND_X_MS,
  BAND_Y_MS,
  CAPTION_IN_MS,
  CAPTION_OUT_MS,
  FLIP_EVERY_MS,
  KEN_BURNS_MS,
  SUPPLY,
  bandTravel,
  kenBurnsPath,
  nextTile,
  transformOf,
  zoomLimit,
} from "./attract";
import { leaveHandoff } from "./handoff";

const TILES = 4;

/** How long the other tiles take to fade after a tap, before the reload. */
const LEAVE_MS = 400;

type Tile = {
  /** Front and back of the card. Which one faces the visitor follows from `turns`. */
  faces: [PhotoMarker | null, PhotoMarker | null];
  /** Half turns so far. Always counted up, so the card always turns the same way. */
  turns: number;
};

function thumb(photo: PhotoMarker): string {
  return `/api/photos/${photo.id}/thumb?size=1200`;
}

function captionOf(photo: PhotoMarker): string {
  return [photo.date_short, photo.place_name].filter(Boolean).join(" · ");
}

export function AttractMode({ regionName }: { regionName: string }) {
  const attract = useKiosk((s) => s.attract);
  if (!attract) return null;
  return <Wall regionName={regionName} />;
}

function Wall({ regionName }: { regionName: string }) {
  const [tiles, setTiles] = useState<Tile[]>(() =>
    Array.from({ length: TILES }, () => ({ faces: [null, null], turns: 0 })),
  );
  const [chosen, setChosen] = useState<number | null>(null);
  const supply = useRef<PhotoMarker[]>([]);
  const cursor = useRef(0);
  const tilesRef = useRef(tiles);
  tilesRef.current = tiles;

  useEffect(() => {
    const abort = new AbortController();
    let step = 0;
    let turning = false;

    function shown(): Set<number> {
      return new Set(
        tilesRef.current.flatMap((tile) =>
          tile.faces[tile.turns % 2] ? [tile.faces[tile.turns % 2]!.id] : [],
        ),
      );
    }

    /** The next photo not already on the wall. A small collection repeats, a large one never. */
    function take(): PhotoMarker | null {
      const photos = supply.current;
      if (photos.length === 0) return null;
      const visible = shown();
      for (let tries = 0; tries < photos.length; tries++) {
        const photo = photos[cursor.current % photos.length]!;
        cursor.current += 1;
        if (!visible.has(photo.id) || photos.length <= TILES) return photo;
      }
      return null;
    }

    async function refill() {
      try {
        const more = await fetchShowcase(SUPPLY, abort.signal);
        if (abort.signal.aborted || more.length === 0) return;
        supply.current = more;
        cursor.current = 0;
      } catch {
        /* The photos in hand go round once more. */
      }
    }

    async function turn() {
      if (turning) return;
      turning = true;
      try {
        if (cursor.current >= supply.current.length - TILES) void refill();
        const photo = take();
        if (!photo) return;
        // Turned only once the picture is decoded: otherwise the back of the card arrives empty
        // and fills in mid-turn.
        const image = new Image();
        image.src = thumb(photo);
        await image.decode();
        if (abort.signal.aborted) return;

        const index = nextTile(step++);
        setTiles((current) =>
          current.map((tile, position) => {
            if (position !== index) return tile;
            const faces: Tile["faces"] = [...tile.faces];
            faces[(tile.turns + 1) % 2] = photo;
            return { faces, turns: tile.turns + 1 };
          }),
        );
      } catch {
        /* A photo that does not decode is skipped; the next turn takes the one after it. */
      } finally {
        turning = false;
      }
    }

    async function start() {
      await refill();
      // The first four go up without a turn.
      const first = Array.from({ length: TILES }, () => take());
      if (abort.signal.aborted) return;
      setTiles(first.map((photo) => ({ faces: [photo, null], turns: 0 })));
    }

    void start();
    const timer = setInterval(() => void turn(), FLIP_EVERY_MS);
    return () => {
      abort.abort();
      clearInterval(timer);
    };
  }, []);

  function leave(photo: PhotoMarker | null, position: number | null) {
    if (chosen !== null) return;
    if (photo) leaveHandoff({ id: photo.id, lat: photo.lat, lon: photo.lon });
    setChosen(position ?? -1);
    setTimeout(() => window.location.reload(), photo ? LEAVE_MS : 0);
  }

  return (
    <div
      className={chosen === null ? "attract" : "attract attract--leaving"}
      role="dialog"
      aria-modal="true"
      aria-label={t.attract.label}
      onClick={() => leave(null, null)}
    >
      {/* The wall shifts by a few pixels over minutes, so the dark joints between the tiles do
          not stand on the same pixels all night. */}
      <div className="attract__wall">
        {tiles.map((tile, position) => {
          const photo = tile.faces[tile.turns % 2] ?? null;
          return (
            <button
              // Tiles keep their place, so the position is their identity.
              key={position}
              type="button"
              className={
                chosen === position ? "attract__tile attract__tile--chosen" : "attract__tile"
              }
              aria-label={
                photo ? t.attract.tileLabel(captionOf(photo) || t.map.photoAlt) : undefined
              }
              onClick={(event) => {
                event.stopPropagation();
                leave(photo, position);
              }}
            >
              <span
                className="attract__card"
                style={{ transform: `rotateY(${tile.turns * 180}deg)` }}
              >
                <Face photo={tile.faces[0]} side="front" still={chosen !== null} />
                <Face photo={tile.faces[1]} side="back" still={chosen !== null} />
              </span>
            </button>
          );
        })}
      </div>
      <Band text={t.attract.band(regionName)} />
    </div>
  );
}

/**
 * The one line that asks for something, floating slowly across the screen.
 *
 * Two nested elements, one moving sideways and one up and down, each on its own period. Transforms
 * only, so the compositor moves it. How far it may go is measured against the screen and the band
 * itself, and measured again when the window changes size: a band that slid half off the screen
 * would ask for nothing.
 */
function Band({ text }: { text: string }) {
  const across = useRef<HTMLDivElement>(null);
  const down = useRef<HTMLDivElement>(null);
  const band = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const stage = across.current?.parentElement;
    if (!stage || !across.current || !down.current || !band.current) return;
    let running: Animation[] = [];

    function float() {
      running.forEach((animation) => animation.cancel());
      const travel = bandTravel(
        { width: stage!.clientWidth, height: stage!.clientHeight },
        { width: band.current!.offsetWidth, height: band.current!.offsetHeight },
      );
      const options = {
        direction: "alternate",
        iterations: Infinity,
        easing: "ease-in-out",
      } as const;
      running = [
        across.current!.animate(
          [{ transform: "translateX(0)" }, { transform: `translateX(${travel.x}px)` }],
          { ...options, duration: BAND_X_MS },
        ),
        down.current!.animate(
          [{ transform: "translateY(0)" }, { transform: `translateY(${travel.y}px)` }],
          { ...options, duration: BAND_Y_MS },
        ),
      ];
      // Not from the corner every time: each show picks up the path somewhere along it.
      running.forEach((animation) => {
        animation.currentTime = Math.random() * 2 * Number(animation.effect?.getTiming().duration);
      });
    }

    float();
    const observer = new ResizeObserver(float);
    observer.observe(stage);
    return () => {
      observer.disconnect();
      running.forEach((animation) => animation.cancel());
    };
  }, [text]);

  return (
    <div ref={across} className="attract__drift">
      <div ref={down}>
        <p ref={band} className="attract__band">
          {text}
        </p>
      </div>
    </div>
  );
}

/**
 * One side of a tile, with its own camera path.
 *
 * The path starts when the photo arrives, which for a new photo is the moment the tile turns.
 * Web Animations rather than a CSS class, because every photo gets a path of its own and CSS
 * cannot draw a random number.
 */
function Face({
  photo,
  side,
  still,
}: {
  photo: PhotoMarker | null;
  side: "front" | "back";
  still: boolean;
}) {
  const image = useRef<HTMLImageElement>(null);
  const animation = useRef<Animation | null>(null);
  const [captioned, setCaptioned] = useState(false);

  // In after the turn, out after ten seconds. See CAPTION_IN_MS.
  useEffect(() => {
    setCaptioned(false);
    if (!photo) return;
    const show = setTimeout(() => setCaptioned(true), CAPTION_IN_MS);
    const hide = setTimeout(() => setCaptioned(false), CAPTION_OUT_MS);
    return () => {
      clearTimeout(show);
      clearTimeout(hide);
    };
  }, [photo]);

  useEffect(() => {
    const element = image.current;
    if (!photo || !element) return;
    const box = element.parentElement!.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    const zoom = zoomLimit(photo, { width: box.width * ratio, height: box.height * ratio });
    const [from, to] = kenBurnsPath(zoom, Math.random);
    animation.current = element.animate(
      [{ transform: transformOf(from) }, { transform: transformOf(to) }],
      { duration: KEN_BURNS_MS, easing: "ease-in-out", fill: "forwards" },
    );
    return () => animation.current?.cancel();
  }, [photo]);

  // The tapped photo holds still while the others fade: the hand sees where the tap arrived.
  useEffect(() => {
    if (still) animation.current?.pause();
  }, [still]);

  return (
    <span className={`attract__face attract__face--${side}`}>
      {photo && (
        <>
          <img ref={image} className="attract__image" src={thumb(photo)} alt="" />
          {captionOf(photo) && (
            // The corner changes from photo to photo, for the same reason the caption fades.
            <span
              className={`attract__caption attract__caption--${photo.id % 4}${captioned ? " attract__caption--on" : ""}`}
            >
              {captionOf(photo)}
            </span>
          )}
        </>
      )}
    </span>
  );
}
