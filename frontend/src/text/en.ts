/**
 * Every piece of text that reaches a visitor's eyes, in English. A translation of `de.ts`.
 *
 * `Texts` is `typeof de`, so `tsc` refuses to build this file while a key is missing, a function
 * takes the wrong number of arguments, or a string stands where a function belongs. What it cannot
 * catch is a sentence that says something else than the German one -- that is what reading is for.
 *
 * Written to the same rules as the German: one thought per sentence, active voice, no hedging.
 * These lines stand on a museum device in front of visitors.
 */

import type { Need } from "../api/client";
import type { Texts } from "./types";

/** The counterpart of `since` in `de.ts`. "34" above, "days since the last backup" below. */
function since(days: number | null, what: string, done: string): string {
  if (days === null || days <= 0) return done;
  return `${days === 1 ? "day" : "days"} since ${what}`;
}

export const en: Texts = {
  locale: "en-GB",

  app: {
    titleLead: "Pictures from",
    documentTitle: "Pictures from our village",
    resetHint: "Start again",
    loadingMap: "The map is loading …",

    crashTitle: "One moment, please",
    crashReloading: "Something did not work. The page will reload by itself in a moment.",
    crashStuck: "Something did not work. Please tap the button once.",
    crashRetry: "Try again",
  },

  map: {
    noPhotos: "There are no photos here yet in the selected period.",
    tooMany: (count: number) =>
      `${count} photos in this view — zoom in closer for a better overview`,
    markerLabel: (caption: string) => `${caption} — show large`,
    withDate: (what: string, date: string) => `${what} — ${date}`,
    /** The question mark is deliberate: sharpening wants the gap visible. See the German. */
    addressWithoutNumber: (street: string) => `${street} no. ?`,
    clusterLabel: (count: number) => `${count} photos — zoom in`,
    stackLabel: (count: number) => `${count} photos from this spot — look at them`,
    pinLabel: "Marked place, can be moved",
    untitled: "Untitled",
    photoAlt: "Historic photo",
    attribution:
      '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors, ODbL',
  },

  overlay: {
    dialogLabel: "Photo at full size",
    close: "Close",
    prev: "Previous",
    next: "Next",
    position: (current: number, count: number) => `${current} of ${count}`,
    edit: "Edit in the admin area — asks for the PIN",
  },

  timeline: {
    empty: "There are no dated photos for this view.",
    loading: "…",
    to: "to",
    undated: (count: number) => `Show ${count} ${count === 1 ? "photo" : "photos"} without a year`,
    startHandle: "First year",
    endHandle: "Last year",
    rangeHandle: "Move the period",
  },

  help: {
    title: "Help out:",
    ask: {
      location: "Where is this?",
      date: "When was this?",
      housenumber: "Which house number?",
    } satisfies Record<Need, string>,
    photoAlt: "Photo with something missing",
    enlarge: "Show the photo large",
    allComplete: "Everything is complete just now. Thank you to everyone who helped!",
    next: "I do not know — next photo",
    stillOpen: (count: number, need: Need) =>
      need === "housenumber"
        ? `Another ${count} photos where only the street is known`
        : `Another ${count} photos without a ${need === "location" ? "place" : "year"}`,
    thanks: {
      location: "Thank you! The photo is on the map now.",
      date: "Thank you! The photo is on the timeline now.",
      housenumber: "Thank you! The photo now sits at the right house.",
    } satisfies Record<Need, string>,
    thanksAsk: {
      location: "Thank you! And do you also know where that was?",
      date: "Thank you! And do you also know when that was?",
      housenumber: "Thank you! And do you also know which house number that is?",
    } satisfies Record<Need, string>,
  },

  location: {
    hintEmpty: "Choose the street — or point to the spot on the map.",
    hintPicking: "Tap the spot on the map.",
    hintSet: "Is the spot right? The point can still be moved on the map.",
    pickOnMap: "Point on the map",
    backToStreets: "Choose the street instead",
    backToNumbers: "Choose the house number instead",
    askInitial: "What does the street start with?",
    askStreet: "In which street?",
    otherInitial: "Another letter",
    noStreets: "Please tap the spot on the map.",
    /** The example keeps its umlaut: it is a street in Holm, not English prose. */
    searchPlaceholder: "e.g. Mühlenweg",
    confirm: "This is where it was",
    clear: "Remove the point",
    /**
     * The street name goes first here too, although English has one article.
     *
     * Not for grammar but for the eye: the name is what the visitor recognises, and both
     * languages then read the same way round on the same screen.
     */
    askHouseNumber: (street: string) => `${street} — which house number?`,
    askArea: (street: string) => `${street} — which section?`,
    otherArea: "Another section",
    noHouseNumber: "Good enough — the street will do",
    cancelStreet: "Not that — start again",
    /** The keys come from OpenStreetMap and stay German; only what is shown is translated. */
    kinds: {
      strasse: "Street",
      ortsteil: "District",
      gebaeude: "Building",
      natur: "Nature",
      flur: "Field name",
      adresse: "Address",
    } as Record<string, string>,
  },

  date: {
    askDecade: "Which decade is the photo from?",
    askYear: "Do you know it more exactly? Otherwise the decade is enough.",
    wholeDecade: (decade: number) => `The whole ${decade}s`,
    otherDecade: "Another decade",
  },

  errors: {
    regionMissing: (status: number) =>
      `The region could not be loaded (HTTP ${status}). Was "make tiles" run?`,
  },

  admin: {
    logoLabel: (place: string) => `Coat of arms of ${place}`,
    cornerHint: "Open the admin area",

    pin: {
      title: "Enter the PIN",
      hint: "For the museum's staff.",
      delete: "Delete",
      submit: "Continue",
      cancel: "Cancel and go back",
      wrong: "That PIN is not right.",
    },

    shell: {
      title: "Admin area",
      leave: "Leave the admin area",
      remaining: (minutes: number) =>
        minutes > 1 ? `Signed in for another ${minutes} minutes` : "The session expires shortly",
      sections: {
        overview: "Overview",
        photos: "Photos",
        moderation: "Moderation",
        import: "Import",
        log: "Log",
        backup: "Backup",
      },
    },

    overview: {
      total: "Photos in total",
      onMap: "Visible on the map",
      withoutLocation: "Without a place",
      withoutDate: "Without a year",
      deleted: "Deleted",
      visitorChanges: "Visitor contributions",

      sinceBackup: (days: number | null) => since(days, "the last backup", "backed up"),
      sinceImport: (days: number | null) => since(days, "the newest import", "imported"),
      sinceChange: (days: number | null) =>
        since(days, "the latest visitor contribution", "with a contribution"),

      reload: "Reload the display",
      reloadHint:
        "Helps when the visitor view has got stuck. Nothing in the collection changes. " +
        "The same happens by itself once the device is untouched for five minutes.",
    },

    photos: {
      title: "List of all photos",
      searchLabel: "Search in title, place and file name",
      searchPlaceholder: "e.g. Kirchweih",
      filterAll: "All",
      filterWithoutLocation: "Without a place",
      filterWithoutDate: "Without a year",
      filterDeleted: "Deleted",
      found: (shown: number, total: number) =>
        shown === total ? `${total} photos` : `${shown} of ${total} photos`,
      none: "No photos found.",
      untitled: "Untitled",
      missingLocation: "Place missing",
      missingDate: "Year missing",
      deleted: "Deleted",
      edit: "Edit",
      delete: "Delete",
      restore: "Restore",
    },

    editor: {
      title: "Title",
      description: "Description",
      year: "Year",
      yearHint: "Leave empty when the year is unknown.",
      time: "Time",
      precision: "Precision",
      precisionYear: "Year",
      precisionDecade: "Decade",
      place: "Place",
      placeSearch: "Search for a street or a place",
      coordinates: "Coordinates",
      clearLocation: "Remove the place",
      tags: "Keywords",
      tagsHint: "Separated by commas.",

      credit: "Credit",
      creditHint:
        "Stands in the detail view below the description. For example: " +
        "Sammlung Heimatmuseum Holm.",
      provenance: "Provenance",
      provenanceHint:
        "Who the picture came from, whether it is a loan, whether there is a release. " +
        "Visible only here, never on the visitor's screen.",
      visible: "Show on the map",
      fileInfo: (filename: string, width: number, height: number) =>
        `${filename} · ${width} × ${height} pixels`,
      scanDate: (date: string) => `Capture date of the file: ${date} (does not date the photo)`,
      save: "Save",
      cancel: "Cancel",
      saved: "Saved.",

      delete: "Delete",
      deleteConfirm: (title: string) =>
        `Delete “${title}”? The photo disappears from the map and from every list — ` +
        `the file is kept and can be restored under “Deleted”.`,
      restore: "Restore",
    },

    upload: {
      title: "Add photos",
      whereFrom: "Choosing the pictures to import",
      fromComputer: "From the computer",
      fromStick: "From a USB stick",
      chooseHint: "Choose pictures on this computer",
      fromStickHint: "Nothing on the stick is changed, only read.",

      tagsHint: "Every photo of this batch gets them. Separated by commas.",

      dropTitle: "Please choose pictures.",
      dropHint: "Drop pictures here or",
      dropButton: "Choose",
      dropAgain: "Choose others",
      toReview: "Work over the photos without a place",
      tooManyForTable:
        "That is too many for a table. What is still missing is in the photo list — " +
        "and turns up in the “Help out” panel.",
      step1: "Details for all newly added pictures (optional)",
      step1Hint: "Both are voluntary and can be changed per picture afterwards.",
      choose: "Choose pictures",
      chosen: (count: number) => `${count} ${count === 1 ? "picture" : "pictures"} chosen`,
      start: "Import",
      progress: (done: number, total: number) => `Picture ${done} of ${total}`,
      summary: (imported: number, duplicates: number, rejected: number) =>
        [
          `${imported} taken in`,
          duplicates > 0
            ? `${duplicates} ${duplicates === 1 ? "was" : "were"} already there`
            : null,
          rejected > 0 ? `${rejected} rejected` : null,
        ]
          .filter(Boolean)
          .join(", "),
      tableHint:
        "The pictures are saved already. What is left lying here turns up later in the " +
        "“Help out” panel.",
      enlarge: (filename: string) => `Show ${filename} large`,
      enlarged: "Photo at full size",
      apply: "Apply",
      applyAll: "Apply all",
      done: "Done",
      more: "Upload more",
      allApplied: "Every picture has been dealt with.",
    },

    stick: {
      title: "Or from a USB stick",
      searching: "Looking for a stick …",

      waitTitle: "Please plug in a USB stick.",
      waitHint: "The folders with pictures then appear by themselves.",
      noImages: (drive: string) => `There are no pictures on “${drive}”.`,
      noImagesHint: "Every folder on the stick is searched.",
      folder: (name: string, drive: string) => `${name} (on ${drive})`,
      images: (count: number) => `${count} ${count === 1 ? "picture" : "pictures"}`,
      choose: "Choose",
      chosen: "Chosen",
      running: "Please do not pull the stick out while it is being read.",
      toIncomplete: "Work over the incomplete ones",
      done: "Done",
    },

    changes: {
      title: "What visitors have contributed",
      none: "There is nothing to look through just now.",
      showReverted: "Show the ones taken back as well",
      fieldLocation: "Place",
      fieldDate: "Year",
      fieldHouseNumber: "House number",
      revert: "Take back",
      reverted: "Taken back",
      locked: "Edited by hand",
      revertHint: "The photo is shown again in the “Help out” panel afterwards.",
    },

    imports: {
      title: "Log of the photo imports",
      none: "Nothing taken in yet.",
      all: "All",
      imported: "Taken in",
      duplicate: "Duplicate",
      rejected: "Rejected",
    },

    backup: {
      title: "Backup",
      intro:
        "The backup writes every photo and every record out of the device — " +
        "onto a USB stick, or as one file to download.",

      whereTo: "Where the backup goes",
      toStick: "Onto a USB stick",
      toStickHint:
        "The usual route. Writes only what is new, and is finished in seconds the second time.",
      toZip: "As one file",
      toZipHint: "A download for the computer you are sitting at. Without a stick.",

      zipTitle: "Download the backup",
      zipIntro:
        "You get the whole collection as one ZIP file: every photo, every thumbnail and every " +
        "record. Careful, this takes a while!",
      zipRestoreHint:
        "To read it back in, unpack the file onto a USB stick, plug the stick in and choose " +
        "“Restore” on the left.",
      incomingTitle: "Read a backup in",
      incomingFound: (date: string, photos: string) =>
        `There is a backup from ${date} with ${photos} photos in the inbox folder — read it in?`,
      incomingStart: "Read the backup in",
      incomingWhat:
        "The collection as it stands is not deleted but set aside on the device — into a folder " +
        "with today's date. The backup then stands in its place, with every photo and every " +
        "record.",
      incomingDownloadFirst: "Save the collection as it stands first?",

      zipStart: "Download the backup",
      zipRunning:
        "The download is running. With many photos it takes several minutes — leave the window " +
        "open until it is done.",

      noDrive: "Please plug in a USB stick.",
      noDriveHint: "As soon as the stick is in, it appears here by itself.",
      searching: "Looking for a stick …",

      free: (free: string) => `${free} free`,
      enough: (photos: string) => `enough for ${photos} photos`,
      notEnough: (needed: string) => `not enough — ${needed} is needed`,
      existing: (date: string, photos: string) =>
        `There is already a backup from ${date} with ${photos} photos on the stick.`,

      start: "Start the backup",
      startAgain: "Renew the backup",
      done: "Done",
      cancelHint: "Please do not pull the stick out while the backup is running.",

      lastNever: "There has never been a backup.",
      lastOn: (date: string, days: number) =>
        days === 0
          ? `Last backed up: today (${date})`
          : `Last backup ${days} ${days === 1 ? "day" : "days"} ago (${date})`,

      restoreTitle: "Read a backup back in",
      restoreIntro:
        "Only needed when the device was set up again or something has been lost. " +
        "The collection as it stands is replaced.",
      restoreNone: "There is no backup on this stick that could be read back in.",
      restore: "Restore",
      restoreConfirmTitle: "Really read it back in?",
      restoreConfirm: (date: string, photos: string) =>
        `The collection as it stands is replaced by the backup from ${date} with ${photos} ` +
        "photos. The previous state is not deleted but set aside on the device.",
      restoreYes: "Yes, read it back in",
      restoreNo: "Cancel",
    },

    pager: {
      prev: "Back",
      next: "Next",
      page: (current: number, count: number) => `Page ${current} of ${count}`,
    },

    format: {
      never: "Never",
      today: "Today",
      bytes: "bytes",
    },

    loading: "Loading …",
    expired: "The session has expired.",
  },
};
