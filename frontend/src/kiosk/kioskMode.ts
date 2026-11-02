/**
 * Whether this page is the kiosk on the device.
 *
 * `deploy/pi/kiekmap-kiosk` opens the page as `http://localhost/?kiosk`. A development machine and
 * the online instance open it without the marker, and there the page stays as it is: the cursor
 * is hidden only where a finger, not a mouse, is the normal way in.
 *
 * Every reload on the device -- the idle timer, the slide show, the error page -- goes through
 * `location.reload()`, which keeps the query. A navigation to `/` would drop the marker.
 */
export function isKiosk(search: string): boolean {
  return new URLSearchParams(search).has("kiosk");
}
