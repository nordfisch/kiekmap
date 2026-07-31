# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach SemVer.

## [Unveröffentlicht]

### Hinzugefügt

- Projektgerüst: Ordnerstruktur, Git-Repo, README
- `docs/decisions.md` mit den Technologieentscheidungen und ihren Begründungen
- `tiles/region.json` als Platzhalter für die Region des Museumsorts
- FastAPI-Backend mit `/api/health`, SQLite im WAL-Modus, Alembic, Dockerfile
- Migrationen laufen beim Containerstart automatisch — auf dem Pi soll niemand daran denken müssen
- `Makefile` mit `dev`, `test`, `lint`, `migrate`, `tiles`, `prod`
- `deploy/docker-compose.yml` für den Betrieb auf dem Pi
- React-Frontend mit MapLibre und offline gelesenen PMTiles-Vektorkacheln
- `tiles/build-tiles.sh` baut Kacheln, Schriften und Symbole für die Region — Schriften und
  Symbole werden mit heruntergeladen, sonst bliebe die Karte offline ohne Beschriftung
- Grundlayout: Karte mit Zeitschieber darunter, „Hilf mit"-Bereich rechts über die volle Höhe
- nginx-Konfiguration mit Range-Requests für die Kartendatei und `/api`-Proxy
- Datenmodell: Fotos mit Zeitintervall statt Zeitpunkt, Herkunft pro Feld, Schlagwörter,
  Änderungsprotokoll, Ortsverzeichnis, Import-Protokoll
- Import-Pipeline: SHA-256 als Dateiname und Dublettenschutz, EXIF und IPTC, Vorschaubilder in
  zwei Größen, Beachtung der EXIF-Ausrichtung, CMYK-Umwandlung
- **EXIF-Datumsangaben ab 1990 gelten als Scandatum und datieren das Foto nicht** — sonst läge
  ein Foto von 1932 auf der Zeitleiste bei 2019 und würde nie zur Korrektur vorgelegt
- Überwachter Eingangsordner: importiert erst, wenn eine Datei fertig geschrieben ist, und räumt
  sie danach nach `_erledigt/` bzw. `_problem/` — gelöscht wird nie
- `python -m app.cli import|scan|stats` für Massenimport und Bestandsübersicht
- Abfrage-API: `/api/photos` mit Kartenausschnitt und Zeitraum, `/histogram` für den Zeitschieber,
  Auslieferung von Vorschaubild und Original mit dauerhaftem Cache
- Der Zeitfilter fragt auf **Überlappung** der Intervalle ab — ein auf „1920er" datiertes Foto
  erscheint damit auch bei der Auswahl 1925–1930
- Fotos erscheinen als Vorschaubilder an ihrem Aufnahmeort; bei hoher Dichte fasst supercluster
  sie zu einem Kreis mit Anzahl zusammen, der beim Antippen aufgeht
- Foto-Overlay in voller Größe, schließbar per Tippen daneben, Knopf oder Escape
- Zeitschieber mit zwei Griffen und Jahrzehnt-Histogramm im Hintergrund, fingergerecht bemessen
- Kartenbewegung und Zeitraum lösen entprellt genau eine Abfrage aus; überholte werden verworfen
- „Hilf mit"-Bereich: zufällige Fotos ohne Ort oder Jahr, Verortung per Pin auf der Karte oder
  über die Ortssuche, Datierung über Jahrzehnt und optional Jahr
- Besucherbeiträge werden direkt übernommen, aber nur in leere Felder — kuratierte Angaben sind
  unantastbar, und Koordinaten außerhalb der Region werden abgewiesen
- `tiles/build-places.py` baut einen Ortsindex aus OpenStreetMap; die Suche findet „Mühlenweg"
  auch bei Eingabe ohne Umlaut und läuft ohne Internet
- `make places` baut und lädt den Ortsindex, `python -m app.cli places` lädt ihn neu
- Admin-Bereich: Klick auf das Ortswappen über der Karte, PIN auf einem Zahlenfeld mit großen
  Tasten, Sitzung mit Ablauf. Die Sperre nach fünf Fehlversuchen ist der eigentliche Schutz einer
  vierstelligen PIN — sie macht aus Sekunden Jahre
- `python -m app.cli pin` erzeugt den PIN-Hash für die `.env`; die PIN selbst wird nie gespeichert
- Statusübersicht, Fotoliste mit Filter „unvollständig" und Suche, Metadateneditor mit Ortssuche,
  Besucherbeiträge sichten und einzeln zurücknehmen, Import-Protokoll
- Beim Bearbeiten heißt ein **fehlendes** Feld „unverändert lassen", ein **leeres** Feld „löschen" —
  sonst ließe sich eine falsche Datierung nur ersetzen, nie herausnehmen
- Ein Besucherbeitrag lässt sich nicht mehr zurücknehmen, wenn das Feld inzwischen von Hand
  bearbeitet wurde; das würde die Arbeit des Kurators mit wegwerfen
- Stapel-Upload: Ort und Jahr optional für den ganzen Stapel, danach eine Tabelle mit Vorschau,
  Titel aus dem Dateinamen, Jahr und Ort je Bild änderbar, „Übernehmen" und „Alle übernehmen".
  Die Fotos sind schon **nach dem Hochladen** in der Datenbank — ein geschlossener Browser darf
  keine Uploads kosten. Dubletten werden benannt („3 waren schon da")
- Das Ortswappen liegt als austauschbare Datei unter `frontend/public/logo.png`; im Code steht
  nirgends, was darauf zu sehen ist
- Sicherung auf USB-Stick: Stick einstecken, ein Knopf, Fortschrittsbalken, am Ende „Der Stick
  kann jetzt abgezogen werden". Ein Ordner statt eines Archivs — eine abgebrochene Sicherung ist
  so teilweise brauchbar statt komplett wertlos
- Die zweite Sicherung schreibt nur, was dazugekommen ist: der Dateiname ist der Hash des Inhalts,
  ein gleicher Name ist dasselbe Bild
- `VACUUM INTO` schreibt die Datenbank konsistent heraus, ohne den Kiosk anzuhalten
- Als Sicherungsziel gelten nur echte Einhängepunkte, die auch beschreibbar sind — sonst liefe die
  Sicherung auf dieselbe SD-Karte, gegen deren Ausfall sie schützt
- Wiederherstellen kopiert erst daneben und schaltet zuletzt um; der bisherige Stand wird nach
  `data/vorher-<Datum>/` beiseitegelegt, mitsamt Write-Ahead-Log, und nie gelöscht
- Erinnerung „Letzte Sicherung vor 34 Tagen" auf der Startseite der Verwaltung, ab 30 Tagen rot
- `deploy/pi/99-photomap-usb.rules` und `photomap-usb-mount` hängen Sticks auf Pi OS Lite ein —
  dort gibt es keinen Automounter
- „Weiß ich nicht — nächstes Foto" wechselt jetzt die Frage zwischen Ort und Jahr. Wer einen Ort
  nicht erkennt, weiß vielleicht trotzdem das Jahrzehnt; dieselbe Frage noch einmal ist der Grund,
  warum jemand nach drei Bildern aufhört
- Läuft eine der beiden Fragen leer, fällt der „Hilf mit"-Bereich auf die andere zurück, statt
  „alles vollständig" zu melden, während Hunderte Fotos auf eine Jahreszahl warten
- Import vom USB-Stick im Admin-Bereich, unter dem Upload über den Rechner: Ordner mit Bildern
  erscheinen von allein, sobald ein Stick steckt; Ort und Jahr aus demselben Formular gelten für
  beide Wege. **Auf dem Stick wird nichts verschoben und nichts gelöscht** — anders als im
  überwachten Eingangsordner, der Aufgenommenes nach `_erledigt/` räumt
- Nach dem Lesen führt ein Knopf in die „Unvollständig"-Liste statt in eine Tabelle: bei
  zweihundert Bildern aus einem Ordner ist sie der bessere Ort zum Nacharbeiten
- Kiosk-Betrieb auf dem Pi: `deploy/pi/setup-pi.sh` richtet einen frischen Raspberry Pi ein,
  `photomap-kiosk.service` startet cage mit Chromium im Vollbild, sobald `/api/health` antwortet.
  Frisches Browserprofil bei jedem Start; systemd startet nach einem Absturz neu
- `deploy/pi/update.sh` spielt ein Update vom USB-Stick ein, ohne den Bestand anzufassen —
  Kartendaten werden erst danebengelegt und dann umbenannt, der Ortsindex ausdrücklich neu geladen
- Leerlauf-Reset: Nach fünf Minuten ohne Berührung schließt sich ein offenes Foto, Zeitraum und
  Kartenausschnitt kehren zur Standardansicht zurück. Sonst stünde das Gerät morgens im Zustand
  des letzten Besuchers vom Vorabend. Als Anwesenheit zählen Tippen, Tasten und Scrollen — keine
  Mausbewegung
- Hausnummern im Ortsindex: Wer eine Straße antippt, wählt danach die Hausnummer aus einem
  Knopfraster — oder tippt „Reicht so", denn nicht jedes Haus steht in OpenStreetMap. Ohne sie
  bekam jedes Foto einer 800 m langen Straße denselben Punkt
- In der freien Suche erscheinen Adressen erst ab einer Ziffer in der Eingabe. Sonst wären die
  zwölf Plätze der Trefferliste nach den Hausnummern einer Straße voll — der Lehmweg hat 139
- Hausnummern werden natürlich sortiert: 1, 1a, 2, 9, 10 — nicht 1, 10, 1a, 2, 9
- `location_accuracy_m` wird endlich benutzt: 150 m für eine Straße, 15 m für eine Hausnummer,
  nichts für einen von Hand getippten Punkt
- Eigener Kartenstil „Papier" in den Farben der Oberfläche: Erde in Papierton, Grün zu Salbei
  entsättigt, Wasser in mattem Graublau statt Türkis. Regel beim Aussuchen: nichts auf der Karte
  darf so gesättigt sein wie ein Foto. Dazu ohne Geschäfte, Hausnummern und Autobahnschilder, und
  mit Straßen auf 80 % ihrer Breite — die kleinen Straßennamen bleiben, an ihnen hängt die
  Verortung

### Geändert

- Bezeichner und Code-Kommentare durchgängig auf Englisch; Deutsch bleibt für Oberfläche,
  Fehlermeldungen, Dokumentation und Commit-Nachrichten
- Die beiden Migrationen zu einer initialen zusammengefasst, mit englischen Index- und
  Constraint-Namen — möglich, solange nichts ausgeliefert ist
- `CLAUDE.md` (für Coding-Agents) und `docs/entwicklung.md` (für Entwickler) ergänzt
- `docs/adaption.md` und `docs/stufenplan.md` ergänzt
- Query-Parameter `von`/`bis` heißen jetzt `from_year`/`to_year` — die Konvention verlangt
  Englisch für die API
- Faustregel für Meldungen eingeführt: erscheint sie im Kiosk oder Admin-Bereich, ist sie deutsch,
  sonst englisch. OpenAPI-Beschreibungen sind damit englisch, CLI-Ausgaben bleiben deutsch
- Jahrzehnte der Datumsfrage kommen aus `region.json` statt aus dem Code
- Kiosk-Aufteilung auf ein Raster aus zwei Spalten und zwei Zeilen: links Titelbereich über
  „Hilf mit", rechts Zeitschieber über der Karte. Der Schieber steht damit weiterhin genau über
  der Karte, die er filtert, und das Wappen führt den Bereich an, statt die Karte zu verdecken.
  Der Ortsname im Titel kommt aus `region.json`

- Verwaltungsmenü aufgeräumt: **Übersicht · Fotos · Moderation · Importieren · Protokoll ·
  Sicherung**. Erst die Pflege des Bestands, dann das Hinzufügen, dann das Technische. „Beiträge"
  heißt jetzt Moderation, „Import" heißt Protokoll — es stand als Protokoll in Konkurrenz zum
  Hochladen
- Der Fotofilter trennt **„Ohne Ort"** und **„Ohne Jahr"** statt eines gemeinsamen
  „Unvollständig". Verorten und Datieren sind zwei Arbeiten; wer die eine macht, will die andere
  nicht dazwischen
- Jede Zahl der Übersicht ist ein Weg: Fotos insgesamt, Versteckt, Ohne Ort und Ohne Jahr führen
  in die passend gefilterte Liste, die Besucherbeiträge in die Moderation. Nur „auf der Karte zu
  sehen" bleibt eine Anzeige — es ist das Ergebnis, keine Aufgabe
- „Importieren" fragt jetzt **erst die Quelle**, dann was für alle gilt: zwei gleichrangige
  Kacheln für Rechner und Stick statt eines Nachtrags unter einer Trennlinie. Jahr und Ort werden
  einmal gefragt und gelten für beide Wege
- Jahr und Ort stehen nebeneinander, beide im Rahmen. „Ganzes Jahrzehnt" lässt sich nur bei vollen
  Jahrzehnten wählen — sonst rundete das Backend eine 1934 stillschweigend zu den 1930ern ab. Wird
  die Zahl nachträglich geändert, nimmt sich das Häkchen selbst zurück
- Nach dem Import gilt für beide Wege dieselbe Regel: bis 30 Bilder die Nacharbeits-Tabelle,
  darüber die Zusammenfassung mit einem Sprung in die Liste „Ohne Ort"
- Die Besucheransicht kommt ohne Trennlinien zwischen Titel, Zeitschieber, Beitragsbereich und
  Karte aus; neben dem Wappen steht „Bilder aus" über dem Ortsnamen, beide Zeilen zusammen so hoch
  wie das Wappen. „Hilf mit" ist genauso gesetzt wie „Bilder aus"
- Die Zeitachse zeigt immer den ganzen Bestand, die Balken darunter den sichtbaren Ausschnitt.
  Damit bedeutet dieselbe Stelle des Schiebers immer dasselbe Jahr — und eine leere Achse mit einem
  einzelnen Balken sagt, dass es hier nur Fotos aus diesem Jahrzehnt gibt
- Die Datierungsfrage heißt „Wann war das?", passend zu „Wo ist das?". Welche Jahrzehnte zur
  Auswahl stehen, ergibt sich aus dem **Bestand** (mindestens 1920er bis 2010er) statt aus
  `firstDecade`/`lastDecade` in `region.json` — das beschreibt die Sammlung und nicht den Ort, und
  eine Änderung daran zog bisher einen Kartenbau samt Netzzugang hinter sich her
- Beim Verorten fährt die Karte schon heran, sobald über die Ortssuche eine Straße oder Hausnummer
  gewählt ist — der Besucher sieht, wo sein Punkt gelandet ist, bevor er bestätigt. Ein selbst auf
  die Karte getippter oder verschobener Pin lässt sie stehen: Dort hat er gerade gezielt
- Nach einem Besucherbeitrag stellt sich die Ansicht für die Dauer des Dankes auf dieses Foto ein:
  Die Karte fährt auf hundert Meter heran, der Zeitraum auf das Jahrzehnt der Angabe — oder ganz
  auf, wenn das Foto undatiert ist. Danach kehren beide zusammen zurück
- Der „Hilf mit"-Bereich springt bei jedem Wechsel nach oben, und sein Vorschaubild öffnet das Foto
  in voller Größe
- Fotos an derselben Stelle stehen als **ein** Marker mit Anzahl auf der Karte und lassen sich im
  Vollbild durchblättern. Die Kartenabfrage sortiert dafür nach dem zuletzt bearbeiteten Foto
- Unter den sechs Zahlen der Übersicht steht jetzt eine Trennlinie und darunter, in denselben drei
  Spalten, der Betrieb: Tage seit der letzten Sicherung, seit dem neuesten Import und seit dem
  jüngsten Besucherbeitrag. Die Sicherungskachel ersetzt den bisherigen Erinnerungsknopf und wird
  rot, sobald sie fällig ist; „Zuletzt aufgenommen" entfällt. An den Rändern steht ein Wort statt
  einer Zahl — „Heute gesichert", „Noch nie importiert"
- Auch „Auf der Karte zu sehen" ist jetzt ein Weg: die Kachel führt zurück zur Karte, denselben
  Weg wie „Verwaltung beenden". Damit führt jede Zahl der Übersicht irgendwohin
- Unter den beiden Quellenkacheln liegt jetzt **eine Fläche an fester Stelle**, die nur ihren
  Inhalt wechselt — gestrichelt, solange gewartet wird, mit vollem Rand, sobald etwas da ist, wie
  im Sicherungsbereich. Bei „Vom Rechner" ist sie zugleich Ablagefläche für Dateien; der Knopf
  „Auswählen" bleibt der verlässliche Weg, weil es auf dem Kiosk kein Ziehen und Ablegen gibt.
  Beim Stick unterscheidet sie jetzt drei Lagen: kein Stick, Stick ohne Bilder, Ordner gefunden —
  vorher hätte sie jemandem, der gerade eingesteckt hat, „Bitte USB-Stick einstecken" entgegen-
  gehalten
- Jahreszahl und Genauigkeit sind ein **gemeinsames Bauteil** für beide Stellen, an denen datiert
  wird — den Stapel beim Importieren und das einzelne Foto im Editor. Vorher war es dort ein
  Ankreuzfeld unter der Zahl, hier ein breites Auswahlfeld daneben, und die Regel für „Jahrzehnt"
  galt nur an einer der beiden Stellen. Jetzt überall: „Jahr" und „Jahrzehnt" zur Auswahl, beide
  Felder gleich breit, die Genauigkeit gesperrt, solange kein Jahr dasteht, und „Jahrzehnt" nur
  bei runden Jahreszahlen
- Klarere Überschriften: „Liste aller Fotos", „Protokoll der Foto-Importe", „Auswahl der zu
  importierenden Bilder", „Angaben für alle neu hinzugefügten Bilder (optional)". Der Fotobereich
  hatte als einziger gar keine
- Fotoliste, Moderation und Protokoll lassen sich **seitenweise** durchblättern, dreißig Zeilen je
  Seite. Vorher hörten alle drei still auf — die Fotoliste schrieb „60 von 214 Fotos", an die
  übrigen 154 kam niemand heran. Der Filterwechsel fängt wieder auf Seite eins an, und wer den
  letzten Eintrag der letzten Seite abarbeitet, rutscht auf die letzte noch vorhandene
- Gespeicherte Zeitstempel sind durchgängig UTC — auch die der Sicherungsdatei und der Kopfdaten
  auf dem Stick, die bisher Ortszeit schrieben. „Wie lange her" zählt **Kalendertage** entlang der
  deutschen Tagesgrenze: eine Sicherung von gestern Abend ist „1 Tag", nicht „Heute"

### Behoben

- Marker verschwanden gelegentlich von der Karte: der `load`-Rückruf konnte eine bereits entfernte
  Karteninstanz an die Ebenen weiterreichen. Die Vorschaubilder wurden dann sogar geladen, waren
  aber nie zu sehen
- Karte und Zeitleiste blieben nach einem Besucherbeitrag stehen. Der Dank versprach „Das Foto ist
  jetzt auf der Karte", zu sehen war es aber erst, wenn jemand die Karte verschob — also gerade bei
  den älteren Besuchern, für die der Bereich gebaut ist, gar nicht. Ein Beitrag stößt jetzt ein
  Nachladen von Markern und Histogramm an
- **Der Zeitschieber lief aus seinem Feld.** Nach dem Hineinzoomen in einen Bereich mit weniger
  Jahrzehnten als der Gesamtbestand stand die Achse auf dem neuen Ausschnitt, die Auswahl aber
  noch auf dem alten — der Auswahlbalken zeichnete sich dann mit `left: -300%` quer über Wappen
  und Titel, beide Griffe lagen außerhalb des Bildschirms. Die Achse spannt jetzt über den ganzen
  Bestand und steht still; dazu ist die Positionsrechnung auf 0…1 geklammert
- **Fotos am selben Ort waren nicht einzeln erreichbar.** Acht Bilder auf identischen Koordinaten
  wurden ab Zoom 18 zu acht Markern exakt übereinander, von denen nur der oberste antippbar war —
  und der Weg dorthin führte ins Leere, denn identische Punkte trennen sich bei keiner Zoomstufe
