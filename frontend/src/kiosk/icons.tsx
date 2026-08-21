// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

/**
 * The symbols of the visitor view.
 *
 * **Drawn here, not fetched.** No icon font, no CDN, no sprite sheet from the net -- the device is
 * offline, and a symbol that fails to load leaves a button that says nothing. Inline SVG costs a
 * few hundred bytes and travels with the bundle.
 *
 * **Beside the label, never instead of it.** Visitors are often older people who use this device
 * once. A pictogram alone asks them to know what it means; next to the words it only has to
 * confirm what they have already read. That is also why the set is small: four actions carry a
 * symbol -- take, back, skip, show on the map -- and everything else carries none. A symbol on
 * every button would be decoration, and decoration teaches nothing.
 *
 * They inherit ``currentColor`` and the surrounding size, so a filled button gets a white symbol
 * and a quiet one a grey symbol without either being told about it.
 */

type IconProps = { className?: string };

function Icon({ children, className }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      className={className ?? "button__icon"}
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

/** Take this answer. */
export function CheckIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M4 12.5 9.5 18 20 6.5" />
    </Icon>
  );
}

/** A step back, staying with the same photo. */
export function BackIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M11 5 4 12l7 7" />
      <path d="M4 12h16" />
    </Icon>
  );
}

/** Put this photo away and bring the next one -- deliberately the mirror image of ``BackIcon``. */
export function SkipIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M13 5l7 7-7 7" />
      <path d="M20 12H4" />
    </Icon>
  );
}

/** Arm the map for a tap. A crosshair, because that is what the map turns into. */
export function CrosshairIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="6.5" />
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
    </Icon>
  );
}

/**
 * Into the admin area, at this photo.
 *
 * The one symbol that stands alone, and the one that may: it does not belong to the visitor. See
 * decisions.md, point 26.
 */
export function PencilIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M4 20h4L19 9a2.5 2.5 0 0 0-3.5-3.5L4.5 16.5 4 20z" />
    </Icon>
  );
}
