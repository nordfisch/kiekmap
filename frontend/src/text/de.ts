/**
 * Every piece of text that reaches a visitor's eyes.
 *
 * Kept in one place rather than inline, for two reasons: the museum team can have wording changed
 * without anyone hunting through components, and a second language would later be one more file
 * instead of a refactoring.
 *
 * One caveat for that second language: date labels ("1920er", "Juni 1955") are formatted on the
 * server. Making the kiosk bilingual would mean moving that formatting to the client.
 */

/**
 * The caption under a status tile of the overview.
 *
 * The value stands above it (`formatDaysSince()`), and value plus caption make one sentence:
 * "34 Tage seit der letzten Sicherung", "Heute gesichert", "Noch nie gesichert". Which is why the
 * caption changes along as soon as the number turns into a word -- and why the singular is
 * handled here: "1 Tage" would stand out on a museum device.
 */
function since(days: number | null, what: string, done: string): string {
  if (days === null || days <= 0) return done;
  return `${days === 1 ? "Tag" : "Tage"} seit ${what}`;
}

export const t = {
  app: {
    /**
     * The title above the "Hilf mit" panel, two lines beside the coat of arms.
     *
     * The place name deliberately does not stand here but comes from `region.json` -- otherwise
     * the one spot in the project where "Holm" sat in the code would be the largest type on the
     * screen.
     */
    titleLead: "Bilder aus",
    /**
     * The arms, which since 9 August 2026 reload instead of opening the admin area.
     *
     * Says what happens, not what it is: whoever hovers over a coat of arms and reads "Wappen"
     * learns nothing they could not see.
     */
    resetHint: "Von vorn beginnen",
    loadingMap: "Karte wird geladen …",
  },

  map: {
    noPhotos: "Hier gibt es noch keine Fotos im gewählten Zeitraum.",
    tooMany: (count: number) =>
      `${count} Fotos in diesem Ausschnitt — für mehr Übersicht näher heranzoomen`,
    markerLabel: (title: string, date: string) => `${title}, ${date} — groß anzeigen`,
    /**
     * What stands under a thumbnail on the map: address and year.
     *
     * Both parts may be missing, and neither absence gets a placeholder. A photo located from
     * EXIF alone has no address and shows the year; two thirds of this collection have no date
     * and show the address. Where both are missing the caption falls away entirely -- an empty
     * line under a picture asks nothing of the visitor, "Jahr unbekannt" seven hundred times over
     * does, and answers nothing.
     */
    markerCaption: (place: string | null, date: string) =>
      place && date ? `${place} — ${date}` : (place ?? date),
    clusterLabel: (count: number) => `${count} Fotos — hineinzoomen`,
    /** Several photos at the same spot: zooming in does not help here, paging does. */
    stackLabel: (count: number) => `${count} Fotos von dieser Stelle — ansehen`,
    pinLabel: "Gesetzter Ort, verschiebbar",
    untitled: "Ohne Titel",
    photoAlt: "Historisches Foto",
  },

  overlay: {
    dialogLabel: "Foto in voller Größe",
    close: "Schließen",
    prev: "Vorheriges",
    next: "Nächstes",
    position: (current: number, count: number) => `${current} von ${count}`,
    /**
     * The pencil beside the title. Only a label, no visible caption -- the icon carries it.
     *
     * Says what it opens rather than what it is ("Bearbeiten"), because a tap on it asks for the
     * PIN first. Somebody who reads it should not be surprised by a number pad.
     */
    edit: "In der Verwaltung bearbeiten — fragt die PIN ab",
  },

  timeline: {
    empty: "Für diesen Ausschnitt gibt es keine datierten Fotos.",
    loading: "…",
    to: "bis",
    /**
     * The switch beside the slider -- the count is the label, because that is where it stood
     * anyway. "anzeigen" makes it a thing one can do, not a fact one has to put up with.
     */
    undated: (count: number) => `${count} ${count === 1 ? "Foto" : "Fotos"} ohne Jahr anzeigen`,
    startHandle: "Anfangsjahr",
    endHandle: "Endjahr",
    /** The selected bar itself: it moves the whole period, it does not change its length. */
    rangeHandle: "Zeitraum verschieben",
  },

  help: {
    /** With a colon: the title leads into the question below it rather than standing alone. */
    title: "Hilf mit:",
    askLocation: "Wo ist das?",
    askDate: "Wann war das?",
    photoAlt: "Foto, dem eine Angabe fehlt",
    enlarge: "Foto groß anzeigen",
    allComplete: "Zurzeit ist alles vollständig. Vielen Dank an alle, die geholfen haben!",
    next: "Weiß ich nicht — nächstes Foto",
    stillOpen: (count: number, need: "location" | "date") =>
      `Noch ${count} Fotos ohne ${need === "location" ? "Ort" : "Jahr"}`,
    /**
     * Four thank-yous, because two of them are promises the view has to keep.
     *
     * "Das Foto ist jetzt auf der Karte" is only true where the map actually travels to it -- and
     * it does not for a photo without a place. Where something is still missing, the thank-you
     * therefore asks the other question instead of claiming anything.
     */
    thanksLocation: "Danke! Das Foto ist jetzt auf der Karte.",
    thanksDate: "Danke! Das Foto ist jetzt auf der Zeitleiste.",
    thanksLocationAskDate: "Danke! Und wissen Sie auch, wann das war?",
    thanksDateAskLocation: "Danke! Und wissen Sie auch, wo das war?",
  },

  location: {
    /**
     * Two hints for two states, because the map is only live in one of them.
     *
     * A single sentence naming both routes would be wrong in both directions: before the visitor
     * asks for it, tapping the map does nothing; afterwards, the street buttons are gone.
     */
    hintEmpty: "Wählen Sie die Straße — oder zeigen Sie die Stelle auf der Karte.",
    hintPicking: "Tippen Sie auf der Karte auf die Stelle.",
    hintSet: "Stimmt die Stelle? Der Punkt lässt sich auf der Karte noch verschieben.",
    pickOnMap: "Auf der Karte zeigen",
    /**
     * Back out of the map route -- worded for wherever it leads back to.
     *
     * Only ever offered when there is something to go back to: without a gazetteer the map is the
     * only route, and a way back would lead nowhere.
     */
    backToStreets: "Doch die Straße wählen",
    backToNumbers: "Doch die Hausnummer wählen",
    /**
     * The street is chosen, not typed -- the initial first, then the street.
     *
     * The visitor's side has no text field at all, so no keyboard is needed; see decisions.md.
     * `searchPlaceholder` and `kinds` below stay for the admin area, which has one.
     */
    askInitial: "Womit fängt die Straße an?",
    askStreet: "In welcher Straße?",
    otherInitial: "Anderer Buchstabe",
    /** Without `make places` there is no gazetteer -- then the map is the only way. */
    noStreets: "Tippen Sie die Stelle bitte auf der Karte an.",
    searchPlaceholder: "z. B. Mühlenweg",
    confirm: "Hier war das",
    clear: "Punkt entfernen",
    /**
     * Second step: street chosen, now the house number -- like decade, then year.
     *
     * "Reicht so" is a full answer, not a dodge: not every house is in OpenStreetMap, and nobody
     * knows the house number for every photo.
     *
     * **The street name is put in front, never inside the sentence.** German street names come in
     * all three genders -- der Mühlenweg, die Hauptstraße, das Feld -- so any article in front of
     * the placeholder is wrong for two thirds of them ("vom Hauptstraße"). A table of genders
     * would be exactly the kind of place-specific knowledge that must not enter the code, so the
     * sentence steps around the case instead of guessing it.
     */
    askHouseNumber: (street: string) => `${street} — welche Hausnummer?`,
    /** For long streets one step before that -- like the decade before the year. */
    askArea: (street: string) => `${street} — welcher Abschnitt?`,
    otherArea: "Anderer Abschnitt",
    noHouseNumber: "Reicht so — die Straße genügt",
    /** The opposite of "Reicht so": keep nothing, back to the start. */
    cancelStreet: "Doch nicht — von vorn",
    kinds: {
      strasse: "Straße",
      ortsteil: "Ortsteil",
      gebaeude: "Gebäude",
      natur: "Natur",
      flur: "Flur",
      adresse: "Adresse",
    } as Record<string, string>,
  },

  date: {
    askDecade: "Aus welchem Jahrzehnt stammt das Foto?",
    askYear: "Wissen Sie es genauer? Sonst genügt das Jahrzehnt.",
    wholeDecade: (decade: number) => `Ganze ${decade}er Jahre`,
    otherDecade: "Anderes Jahrzehnt",
  },

  errors: {
    regionMissing: (status: number) =>
      `Die Region konnte nicht geladen werden (HTTP ${status}). Wurde "make tiles" ausgeführt?`,
  },

  /**
   * The admin area.
   *
   * Used once or twice a year by volunteers. Which is why everything here is plain speech rather
   * than brevity: "Foto ist versteckt" is longer than "ausgeblendet", but nobody has to work out
   * what is meant.
   */
  admin: {
    logoLabel: (place: string) => `Wappen von ${place}`,
    /** On the title, which is the door since 9 August 2026 -- see decisions.md, point 26. */
    cornerHint: "Verwaltung öffnen",

    pin: {
      title: "PIN eingeben",
      hint: "Für Mitarbeiterinnen und Mitarbeiter des Museums.",
      delete: "Löschen",
      submit: "Weiter",
      cancel: "Zurück zur Karte",
      wrong: "Die PIN stimmt nicht.",
    },

    shell: {
      title: "Verwaltung",
      leave: "Verwaltung beenden",
      remaining: (minutes: number) =>
        minutes > 1 ? `Noch ${minutes} Minuten angemeldet` : "Anmeldung läuft gleich ab",
      sections: {
        overview: "Übersicht",
        photos: "Fotos",
        moderation: "Moderation",
        import: "Importieren",
        log: "Protokoll",
        backup: "Sicherung",
      },
    },

    overview: {
      total: "Fotos insgesamt",
      onMap: "Auf der Karte zu sehen",
      withoutLocation: "Ohne Ort",
      withoutDate: "Ohne Jahr",
      deleted: "Gelöscht",
      visitorChanges: "Beiträge von Besuchern",

      sinceBackup: (days: number | null) => since(days, "der letzten Sicherung", "gesichert"),
      sinceImport: (days: number | null) => since(days, "dem neuesten Import", "importiert"),
      sinceChange: (days: number | null) =>
        since(days, "dem jüngsten Besucherbeitrag", "gab es einen Besucherbeitrag"),

      reload: "Anzeige neu laden",
      reloadHint:
        "Hilft, wenn die Besucheransicht sich verhakt hat. Am Bestand ändert sich dabei nichts. " +
        "Von allein passiert dasselbe, sobald das Gerät fünf Minuten unberührt bleibt.",
    },

    photos: {
      title: "Liste aller Fotos",
      searchLabel: "Suchen in Titel, Ort und Dateiname",
      searchPlaceholder: "z. B. Kirchweih",
      filterAll: "Alle",
      filterWithoutLocation: "Ohne Ort",
      filterWithoutDate: "Ohne Jahr",
      filterDeleted: "Gelöscht",
      found: (shown: number, total: number) =>
        shown === total ? `${total} Fotos` : `${shown} von ${total} Fotos`,
      none: "Keine Fotos gefunden.",
      untitled: "Ohne Titel",
      missingLocation: "Ort fehlt",
      missingDate: "Jahr fehlt",
      deleted: "Gelöscht",
      edit: "Bearbeiten",
      delete: "Löschen",
      restore: "Wiederherstellen",
    },

    editor: {
      title: "Titel",
      description: "Beschreibung",
      year: "Jahr",
      yearHint: "Leer lassen, wenn das Jahr unbekannt ist.",
      /** The caption of the fieldset while importing -- more stands there than just the year. */
      time: "Zeit",
      precision: "Genauigkeit",
      precisionYear: "Jahr",
      precisionDecade: "Jahrzehnt",
      place: "Ort",
      placeSearch: "Straße oder Ort suchen",
      coordinates: "Koordinaten",
      clearLocation: "Ort entfernen",
      tags: "Schlagwörter",
      tagsHint: "Mit Komma getrennt.",

      /* Two fields, because they have two different readers: the credit stands beside the
         picture in the museum, the provenance is an internal note and never leaves the admin
         area. The hint lines say exactly that -- otherwise the lender's name ends up on the
         visitor's screen. */
      credit: "Bildnachweis",
      creditHint:
        "Steht in der Detailansicht unter der Beschreibung. Zum Beispiel: Sammlung Heimatmuseum Holm.",
      provenance: "Herkunft",
      provenanceHint:
        "Von wem das Bild kam, ob es eine Leihgabe ist, ob eine Freigabe vorliegt. " +
        "Nur hier zu sehen, nie auf dem Besucherschirm.",
      visible: "Auf der Karte zeigen",
      fileInfo: (filename: string, width: number, height: number) =>
        `${filename} · ${width} × ${height} Pixel`,
      scanDate: (date: string) => `Aufnahmedatum der Datei: ${date} (datiert das Foto nicht)`,
      save: "Speichern",
      cancel: "Abbrechen",
      saved: "Gespeichert.",

      /* Deleting takes the photo out of the exhibition but does not throw it away -- the
         confirmation says so, so that nobody hesitates, and the way back stands beside it. */
      delete: "Löschen",
      deleteConfirm: (title: string) =>
        `„${title}“ löschen? Das Foto verschwindet aus der Karte und aus allen Listen — ` +
        `die Datei bleibt erhalten und lässt sich unter „Gelöscht“ wiederherstellen.`,
      restore: "Wiederherstellen",
    },

    upload: {
      title: "Fotos hinzufügen",
      whereFrom: "Auswahl der zu importierenden Bilder",
      fromComputer: "Vom Rechner",
      fromStick: "Vom USB-Stick",
      chooseHint: "Bilder auf diesem Rechner auswählen",
      /** The promise stays in the tile even when the rest of the hint is gone. */
      fromStickHint: "Auf dem Stick wird nichts verändert, nur gelesen.",

      dropTitle: "Bitte Bilder auswählen.",
      /** "Ablegen", not "droppen": the people in front of this are often sixty. */
      dropHint: "Bilder hier ablegen oder",
      dropButton: "Auswählen",
      dropAgain: "Andere auswählen",
      toReview: "Fotos ohne Ort nacharbeiten",
      tooManyForTable:
        "Das sind zu viele für eine Tabelle. Was noch fehlt, findet sich in der Fotoliste — " +
        "und taucht im „Hilf mit“-Bereich auf.",
      step1: "Angaben für alle neu hinzugefügten Bilder (optional)",
      step1Hint: "Beides ist freiwillig und lässt sich hinterher je Bild ändern.",
      choose: "Bilder auswählen",
      chosen: (count: number) => `${count} ${count === 1 ? "Bild" : "Bilder"} ausgewählt`,
      start: "Importieren",
      progress: (done: number, total: number) => `Bild ${done} von ${total}`,
      summary: (imported: number, duplicates: number, rejected: number) =>
        [
          `${imported} aufgenommen`,
          duplicates > 0 ? `${duplicates} ${duplicates === 1 ? "war" : "waren"} schon da` : null,
          rejected > 0 ? `${rejected} abgewiesen` : null,
        ]
          .filter(Boolean)
          .join(", "),
      tableHint:
        "Die Bilder sind bereits gespeichert. Was hier liegen bleibt, taucht später im " +
        "„Hilf mit“-Bereich auf.",
      enlarge: (filename: string) => `${filename} groß anzeigen`,
      enlarged: "Foto in voller Größe",
      apply: "Übernehmen",
      applyAll: "Alle übernehmen",
      done: "Fertig",
      more: "Weitere hochladen",
      allApplied: "Alle Bilder sind bearbeitet.",
    },

    /**
     * Import from a USB stick.
     *
     * Unlike the upload from a computer, no table follows here: with two hundred pictures out of
     * one folder the "Unvollständig" list is the better place to work them over -- that is what
     * it was built for. So this route ends by jumping there.
     */
    stick: {
      title: "Oder von einem USB-Stick",
      searching: "Es wird nach einem Stick gesucht …",

      waitTitle: "Bitte USB-Stick einstecken.",
      waitHint: "Die Ordner mit Bildern erscheinen dann von allein.",
      /** The stick is in, only there is nothing on it -- a different answer from "please plug one in". */
      noImages: (drive: string) => `Auf „${drive}" sind keine Bilder.`,
      noImagesHint: "Gesucht wird in allen Ordnern des Sticks.",
      folder: (name: string, drive: string) => `${name} (auf ${drive})`,
      images: (count: number) => `${count} ${count === 1 ? "Bild" : "Bilder"}`,
      choose: "Auswählen",
      chosen: "Ausgewählt",
      running: "Bitte den Stick nicht abziehen, solange gelesen wird.",
      toIncomplete: "Unvollständige nacharbeiten",
      done: "Fertig",
    },

    changes: {
      title: "Was Besucher beigetragen haben",
      none: "Zurzeit gibt es nichts zu sichten.",
      showReverted: "Zurückgenommene mit anzeigen",
      fieldLocation: "Ort",
      fieldDate: "Jahr",
      /** Sharpened: the street centre became a house. Reverting sets it back to the street. */
      fieldHouseNumber: "Hausnummer",
      revert: "Zurücknehmen",
      reverted: "Zurückgenommen",
      locked: "Von Hand bearbeitet",
      revertHint: "Das Foto wird danach im „Hilf mit“-Bereich erneut gezeigt.",
    },

    imports: {
      title: "Protokoll der Foto-Importe",
      none: "Noch nichts aufgenommen.",
      all: "Alle",
      imported: "Aufgenommen",
      duplicate: "Dublette",
      rejected: "Abgewiesen",
    },

    /**
     * Backup onto a USB stick.
     *
     * Deliberately more text here than elsewhere. Whoever makes a backup once a year should be
     * able to read after every step what just happened and what to do next -- down to "Sie können
     * den Stick jetzt abziehen".
     */
    backup: {
      title: "Sicherung",
      intro:
        "Die Sicherung schreibt alle Fotos und alle Angaben aus dem Gerät heraus — " +
        "auf einen USB-Stick oder als eine Datei zum Herunterladen.",

      /* Two tiles as in the import. The stick sits on the left because it is the museum's route:
         the second time it writes only what is new, and it stays usable half-finished. */
      whereTo: "Wohin gesichert wird",
      toStick: "Auf USB-Stick",
      toStickHint:
        "Der übliche Weg. Schreibt nur, was neu ist, und ist beim zweiten Mal in Sekunden fertig.",
      toZip: "Als eine Datei",
      toZipHint: "Ein Download für den Rechner, an dem Sie gerade sitzen. Ohne Stick.",

      zipTitle: "Sicherung herunterladen",
      /* "Achtung, das dauert!" stands in for the whole paragraph that used to be here: that
         everything is packed anew each time and that an abort leaves the file useless. The
         reasoning is in the manual and in decisions.md -- on screen the warning is enough. */
      zipIntro:
        "Sie bekommen den ganzen Bestand als eine ZIP-Datei: alle Fotos, alle Vorschaubilder " +
        "und alle Angaben. Achtung, das dauert!",
      /* Without this sentence the missing way back would look like a defect. */
      zipRestoreHint:
        "Zum Zurückspielen die Datei auf einen USB-Stick entpacken, den Stick einstecken und " +
        "links „Zurückspielen“ wählen.",
      /* The second state of the same tile: a backup lying in the inbox is not restored but put
         up for confirmation. That folder otherwise takes photos in -- additively and without
         consequence -- while this replaces the entire collection. */
      incomingTitle: "Sicherung einspielen",
      incomingFound: (date: string, photos: string) =>
        `Im Eingangsordner liegt eine Sicherung vom ${date} mit ${photos} Fotos — zurückspielen?`,
      incomingStart: "Sicherung zurückspielen",
      incomingWhat:
        "Der jetzige Bestand wird dabei nicht gelöscht, sondern auf dem Gerät beiseitegelegt — " +
        "in einen Ordner mit dem heutigen Datum. Danach steht die Sicherung an seiner Stelle, " +
        "mit allen Fotos und allen Angaben.",
      /* The one moment at which the current collection could no longer be saved would be the
         one right before it is overwritten. Which is why the download stays here. */
      incomingDownloadFirst: "Vorher noch den jetzigen Bestand sichern?",

      zipStart: "Sicherung herunterladen",
      zipRunning:
        "Der Download läuft. Bei vielen Fotos dauert er einige Minuten — das Fenster " +
        "solange offen lassen.",

      noDrive: "Bitte USB-Stick einstecken.",
      noDriveHint: "Sobald der Stick steckt, erscheint er hier von allein.",
      searching: "Es wird nach einem Stick gesucht …",

      free: (free: string) => `${free} frei`,
      enough: (photos: string) => `genug für ${photos} Fotos`,
      notEnough: (needed: string) => `reicht nicht — gebraucht werden ${needed}`,
      existing: (date: string, photos: string) =>
        `Auf dem Stick liegt bereits eine Sicherung vom ${date} mit ${photos} Fotos.`,

      start: "Sicherung starten",
      startAgain: "Sicherung erneuern",
      done: "Fertig",
      cancelHint: "Bitte den Stick nicht abziehen, solange die Sicherung läuft.",

      lastNever: "Es wurde noch nie gesichert.",
      lastOn: (date: string, days: number) =>
        days === 0
          ? `Zuletzt gesichert: heute (${date})`
          : `Letzte Sicherung vor ${days} ${days === 1 ? "Tag" : "Tagen"} (${date})`,

      restoreTitle: "Eine Sicherung zurückspielen",
      restoreIntro:
        "Nur nötig, wenn das Gerät neu aufgesetzt wurde oder etwas verloren gegangen ist. " +
        "Der jetzige Bestand wird dabei ersetzt.",
      restoreNone: "Auf diesem Stick ist keine Sicherung, die sich zurückspielen ließe.",
      restore: "Zurückspielen",
      restoreConfirmTitle: "Wirklich zurückspielen?",
      restoreConfirm: (date: string, photos: string) =>
        `Der jetzige Bestand wird durch die Sicherung vom ${date} mit ${photos} Fotos ersetzt. ` +
        "Der bisherige Stand wird nicht gelöscht, sondern auf dem Gerät beiseitegelegt.",
      restoreYes: "Ja, zurückspielen",
      restoreNo: "Abbrechen",
    },

    pager: {
      prev: "Zurück",
      next: "Weiter",
      page: (current: number, count: number) => `Seite ${current} von ${count}`,
    },

    loading: "Wird geladen …",
    expired: "Die Anmeldung ist abgelaufen.",
  },
} as const;
