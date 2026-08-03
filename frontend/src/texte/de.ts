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
    /** Das Gegenteil von „Reicht so": nichts behalten, zurück auf Anfang. */
    cancelStreet: "Doch nicht — von vorn",
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

      /* Zwei Felder, weil sie zwei verschiedene Leser haben: Der Nachweis steht neben dem Bild
         im Museum, die Herkunft ist eine interne Notiz und verlässt den Verwaltungsbereich nie.
         Die Hinweiszeilen sagen genau das — sonst landet der Name des Leihgebers auf dem
         Besucherschirm. */
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

      /* Löschen nimmt das Foto aus der Ausstellung, wirft es aber nicht weg — das sagt die
         Rückfrage, damit niemand zögert, und der Weg zurück steht daneben. */
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
      title: "Sicherung",
      intro:
        "Die Sicherung schreibt alle Fotos und alle Angaben aus dem Gerät heraus — " +
        "auf einen USB-Stick oder als eine Datei zum Herunterladen.",

      /* Zwei Kacheln wie beim Importieren. Der Stick steht links, weil er der Weg für das Museum
         ist: Er schreibt beim zweiten Mal nur das Neue und bleibt auch halbfertig brauchbar. */
      whereTo: "Wohin gesichert wird",
      toStick: "Auf USB-Stick",
      toStickHint:
        "Der übliche Weg. Schreibt nur, was neu ist, und ist beim zweiten Mal in Sekunden fertig.",
      toZip: "Als eine Datei",
      toZipHint: "Ein Download für den Rechner, an dem Sie gerade sitzen. Ohne Stick.",

      zipTitle: "Sicherung herunterladen",
      /* „Achtung, das dauert!" steht für den ganzen Absatz, der hier einmal stand: dass jedes Mal
         alles neu gepackt wird und ein Abbruch die Datei unbrauchbar macht. Die Begründung dazu
         steht im Handbuch und in decisions.md — auf dem Bildschirm reicht die Warnung. */
      zipIntro:
        "Sie bekommen den ganzen Bestand als eine ZIP-Datei: alle Fotos, alle Vorschaubilder " +
        "und alle Angaben. Achtung, das dauert!",
      /* Ohne diesen Satz sähe die fehlende Rückrichtung wie ein Fehler aus. */
      zipRestoreHint:
        "Zum Zurückspielen die Datei auf einen USB-Stick entpacken, den Stick einstecken und " +
        "links „Zurückspielen“ wählen.",
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
