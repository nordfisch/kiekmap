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
 * Die Beschriftung unter einer Statuskachel der Übersicht.
 *
 * Der Wert steht darüber (`formatDaysSince()`), Wert und Beschriftung ergeben zusammen einen Satz:
 * „34 Tage seit der letzten Sicherung", „Heute gesichert", „Noch nie gesichert". Deshalb wechselt
 * die Beschriftung mit, sobald aus der Zahl ein Wort wird — und deshalb steht hier die Einzahl:
 * „1 Tage" fällt auf einem Museumsgerät auf.
 */
function since(days: number | null, what: string, done: string): string {
  if (days === null || days <= 0) return done;
  return `${days === 1 ? "Tag" : "Tage"} seit ${what}`;
}

export const t = {
  app: {
    /**
     * Der Titel über dem „Hilf mit"-Bereich, zweizeilig neben dem Wappen.
     *
     * Der Ortsname steht bewusst nicht hier, sondern kommt aus `region.json` — sonst wäre der
     * einzige Ort im Projekt, an dem „Holm" im Code stünde, ausgerechnet die größte Schrift
     * auf dem Bildschirm.
     */
    titleLead: "Bilder aus",
    loadingMap: "Karte wird geladen …",
  },

  map: {
    noPhotos: "Hier gibt es noch keine Fotos im gewählten Zeitraum.",
    tooMany: (count: number) =>
      `${count} Fotos in diesem Ausschnitt — für mehr Übersicht näher heranzoomen`,
    markerLabel: (title: string, date: string) => `${title}, ${date} — groß anzeigen`,
    clusterLabel: (count: number) => `${count} Fotos — hineinzoomen`,
    /** Mehrere Fotos an derselben Stelle: Hineinzoomen hilft hier nicht, Blättern schon. */
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
  },

  timeline: {
    empty: "Für diesen Ausschnitt gibt es keine datierten Fotos.",
    loading: "…",
    to: "bis",
    undated: (count: number) => `${count} ${count === 1 ? "Foto" : "Fotos"} ohne Jahr`,
    startHandle: "Anfangsjahr",
    endHandle: "Endjahr",
  },

  help: {
    /** Mit Doppelpunkt: Der Titel fuehrt in die Frage darunter, statt fuer sich zu stehen. */
    title: "Hilf mit:",
    askLocation: "Wo ist das?",
    askDate: "Wann war das?",
    photoAlt: "Foto, dem eine Angabe fehlt",
    enlarge: "Foto groß anzeigen",
    allComplete: "Zurzeit ist alles vollständig. Vielen Dank an alle, die geholfen haben!",
    next: "Weiß ich nicht — nächstes Foto",
    stillOpen: (count: number, need: "location" | "date") =>
      `Noch ${count} Fotos ohne ${need === "location" ? "Ort" : "Jahr"}`,
    thanksLocation: "Danke! Das Foto ist jetzt auf der Karte.",
    thanksDate: "Danke! Das Foto ist jetzt auf der Zeitleiste.",
  },

  location: {
    hintEmpty: "Tippen Sie auf der Karte auf die Stelle — oder suchen Sie den Straßennamen.",
    hintSet: "Stimmt die Stelle? Der Punkt lässt sich auf der Karte noch verschieben.",
    searchLabel: "Straße oder Ort suchen",
    searchPlaceholder: "z. B. Mühlenweg",
    confirm: "Hier war das",
    clear: "Punkt entfernen",
    /**
     * Zweiter Schritt: Straße gewählt, jetzt die Hausnummer — wie Jahrzehnt, dann Jahr.
     *
     * „Reicht so" ist eine vollwertige Antwort, kein Ausweichen: Nicht jedes Haus steht in
     * OpenStreetMap, und niemand weiß bei jedem Foto die Hausnummer.
     */
    askHouseNumber: (street: string) => `Welche Hausnummer im ${street}?`,
    /** Bei langen Straßen ein Schritt davor — wie das Jahrzehnt vor dem Jahr. */
    askArea: (street: string) => `In welchem Abschnitt vom ${street}?`,
    otherArea: "Anderer Abschnitt",
    noHouseNumber: "Reicht so — die Straße genügt",
    otherStreet: "Andere Straße",
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
   * Der Admin-Bereich.
   *
   * Er wird ein- bis zweimal im Jahr von Ehrenamtlichen benutzt. Deshalb steht hier überall
   * Klartext statt Kürze: „Foto ist versteckt" ist länger als „ausgeblendet", aber niemand muss
   * überlegen, was gemeint ist.
   */
  admin: {
    logoLabel: (place: string) => `Wappen von ${place}`,
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
      hidden: "Versteckt",
      visitorChanges: "Beiträge von Besuchern",

      sinceBackup: (days: number | null) => since(days, "der letzten Sicherung", "gesichert"),
      sinceImport: (days: number | null) => since(days, "dem neuesten Import", "importiert"),
      sinceChange: (days: number | null) =>
        since(days, "dem jüngsten Besucherbeitrag", "gab es einen Besucherbeitrag"),
    },

    photos: {
      title: "Liste aller Fotos",
      searchLabel: "Suchen in Titel, Ort und Dateiname",
      searchPlaceholder: "z. B. Kirchweih",
      filterAll: "Alle",
      filterWithoutLocation: "Ohne Ort",
      filterWithoutDate: "Ohne Jahr",
      filterHidden: "Versteckt",
      found: (shown: number, total: number) =>
        shown === total ? `${total} Fotos` : `${shown} von ${total} Fotos`,
      none: "Keine Fotos gefunden.",
      untitled: "Ohne Titel",
      missingLocation: "Ort fehlt",
      missingDate: "Jahr fehlt",
      hidden: "Versteckt",
      edit: "Bearbeiten",
    },

    editor: {
      title: "Titel",
      description: "Beschreibung",
      year: "Jahr",
      yearHint: "Leer lassen, wenn das Jahr unbekannt ist.",
      /** Die Beschriftung des Rahmens beim Importieren -- dort steht mehr als nur die Jahreszahl. */
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
      visible: "Auf der Karte zeigen",
      hidden: "Verstecken",
      hiddenHint: "Versteckte Fotos bleiben erhalten, sind aber für Besucher nicht zu sehen.",
      fileInfo: (filename: string, width: number, height: number) =>
        `${filename} · ${width} × ${height} Pixel`,
      scanDate: (date: string) => `Aufnahmedatum der Datei: ${date} (datiert das Foto nicht)`,
      save: "Speichern",
      cancel: "Abbrechen",
      saved: "Gespeichert.",
    },

    upload: {
      title: "Fotos hinzufügen",
      whereFrom: "Auswahl der zu importierenden Bilder",
      fromComputer: "Vom Rechner",
      fromStick: "Vom USB-Stick",
      chooseHint: "Bilder auf diesem Rechner auswählen",
      /** Die Zusicherung bleibt in der Kachel stehen, auch wenn der Rest des Hinweises weg ist. */
      fromStickHint: "Auf dem Stick wird nichts verändert, nur gelesen.",

      dropTitle: "Bitte Bilder auswählen.",
      /** „Ablegen", nicht „droppen": die Zielgruppe steht oft mit sechzig davor. */
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
      apply: "Übernehmen",
      applyAll: "Alle übernehmen",
      done: "Fertig",
      more: "Weitere hochladen",
      allApplied: "Alle Bilder sind bearbeitet.",
    },

    /**
     * Import vom USB-Stick.
     *
     * Anders als beim Upload über den Rechner steht hier nach dem Lesen keine Tabelle: Bei zwei-
     * hundert Bildern aus einem Ordner ist die „Unvollständig"-Liste der bessere Ort zum
     * Nacharbeiten — dafür ist sie gebaut. Deshalb endet dieser Weg mit einem Sprung dorthin.
     */
    stick: {
      title: "Oder von einem USB-Stick",
      searching: "Es wird nach einem Stick gesucht …",

      waitTitle: "Bitte USB-Stick einstecken.",
      waitHint: "Die Ordner mit Bildern erscheinen dann von allein.",
      /** Der Stick steckt, nur ist nichts darauf -- eine andere Auskunft als „bitte einstecken". */
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
     * Sicherung auf USB-Stick.
     *
     * Hier steht bewusst mehr Text als anderswo. Wer einmal im Jahr eine Sicherung macht, soll
     * nach jedem Schritt lesen können, was gerade passiert ist und was als Nächstes zu tun ist —
     * bis hin zu „Sie können den Stick jetzt abziehen".
     */
    backup: {
      title: "Sicherung auf USB-Stick",
      intro:
        "Die Sicherung schreibt alle Fotos und alle Angaben auf einen USB-Stick. " +
        "Der Stick lässt sich an jedem Rechner öffnen; die Bilder liegen dort als Dateien.",

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
