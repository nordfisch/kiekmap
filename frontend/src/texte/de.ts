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

export const t = {
  app: {
    title: "Bilder aus unserem Ort",
    loadingMap: "Karte wird geladen …",
  },

  map: {
    noPhotos: "Hier gibt es noch keine Fotos im gewählten Zeitraum.",
    tooMany: (count: number) =>
      `${count} Fotos in diesem Ausschnitt — für mehr Übersicht näher heranzoomen`,
    markerLabel: (title: string, date: string) => `${title}, ${date} — groß anzeigen`,
    clusterLabel: (count: number) => `${count} Fotos — hineinzoomen`,
    pinLabel: "Gesetzter Ort, verschiebbar",
    untitled: "Ohne Titel",
    photoAlt: "Historisches Foto",
  },

  overlay: {
    dialogLabel: "Foto in voller Größe",
    close: "Schließen",
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
    title: "Hilf mit",
    askLocation: "Wo ist das?",
    askDate: "Von wann ist dieses Bild?",
    photoAlt: "Foto, dem eine Angabe fehlt",
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
    kinds: {
      strasse: "Straße",
      ortsteil: "Ortsteil",
      gebaeude: "Gebäude",
      natur: "Natur",
      flur: "Flur",
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
} as const;
