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

- **Bildnachweis und Herkunft je Foto.** Der Nachweis („Sammlung Heimatmuseum Holm") steht in der
  Detailansicht unter der Beschreibung; die Herkunft — von wem das Bild kam, ob eine Freigabe
  vorliegt — ist eine interne Notiz und **verlässt den Verwaltungsbereich nie**. Durchgesetzt wird
  das über getrennte Typen, nicht über eine Verabredung: Der Kiosk-Endpunkt hat für die Herkunft
  gar kein Feld. Beide sind auch gemeinsame Angabe des Stapel-Imports, neben Jahr und Ort
- **`make seed` und `make seed-save`.** Ein Beispielbestand zum Entwickeln und Testen: `seed/`
  enthält die Bilddateien und eine `seed.json` mit allem Übrigen, `make seed` stellt daraus in
  einer Minute einen Ausgangszustand her. Bilder plus JSON statt eines Datenbankabzugs, damit eine
  neue Spalte den Bestand nicht wertlos macht; das Einlesen geht durch die echte Import-Pipeline
  und prüft sie damit gleich mit. Die Lücken im Bestand — Fotos ohne Jahr, ohne Ort, ein
  zurückgenommener Besucherbeitrag — sind Absicht, sonst hätte der „Hilf mit"-Bereich nichts
  vorzulegen. **Die Bilder selbst sind noch nicht im Repo**, siehe `seed/README.md`

- **Die Sicherung gibt es auch als eine Datei.** Verwaltung → Sicherung → „Als eine Datei" lädt
  den ganzen Bestand als ZIP herunter — für den Fall, dass kein USB-Stick zur Hand ist. Das Archiv
  entsteht im Strom und unkomprimiert, liegt also nirgends vollständig; auf einem Pi mit 2 GB RAM
  ist das der Unterschied zwischen geht und geht nicht. **Es ist genau der Ordner, den auch der
  Stick bekommt, nur gezippt** — zurückspielen heißt deshalb: auf einen Stick entpacken und die
  vorhandene Wiederherstellung benutzen. Der Stick bleibt der bessere Weg, weil er nur Neues
  schreibt und auch halbfertig brauchbar ist; die Oberfläche sagt das

- **Eine Sicherung lässt sich über den Eingangsordner zurückspielen.** Wer die heruntergeladene
  ZIP-Datei in `data/incoming` legt, bekommt im Sicherungsbereich die Frage „Im Eingangsordner
  liegt eine Sicherung vom … mit … Fotos — zurückspielen?". **Von selbst passiert nichts:** Der
  Ordner nimmt sonst Fotos auf, was hinzufügend und folgenlos ist, während dies den ganzen Bestand
  ersetzt. Der bisherige Stand wird wie immer beiseitegelegt, nicht gelöscht, und das eingespielte
  Archiv wandert nach `_erledigt/`

- **Die Nacharbeits-Liste nach einem Stapel-Import zeigt jetzt Jahrzehnte und große Bilder.** Ein
  Klick auf das Vorschaubild zeigt das Foto groß — auf dem kleinen Bild sind Kirchweih und
  Feuerwehrfest nicht zu unterscheiden, und genau das braucht man zum Prüfen. Neben der Jahreszahl
  steht dasselbe Genauigkeitsfeld wie im Fotoeditor, „1920er" ist damit auch hier eintragbar. Eine
  bereits als Jahrzehnt gespeicherte Datierung bleibt eines, statt still zum Jahr zu werden

- **Undatierte Fotos lassen sich in der Detailansicht datieren.** Wer ein Foto groß ansieht und
  „Jahr unbekannt" liest, bekommt dort dieselbe Auswahl wie im „Hilf mit"-Bereich — erst das
  Jahrzehnt, dann das Jahr, alles über Knöpfe. Bisher musste man schließen und hoffen, dass der
  Beitragsbereich dasselbe Foto vorlegt. Eine Dankmeldung gibt es hier nicht: Aus „Jahr unbekannt"
  wird die Jahreszahl, und die Knöpfe verschwinden — an genau der Stelle, auf die geschaut wird

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
  Karte aus; neben dem Wappen steht „Bilder aus" über dem Ortsnamen. Wappen und Titel stehen
  zusammen so hoch wie der Zeitschieber daneben — von seiner ersten Zeile bis zur Jahresskala —,
  und ihre Oberkanten fluchten. „Hilf mit:" beginnt auf derselben Höhe wie die Karte
- „Weiß ich nicht — nächstes Foto" verschwindet, wenn es die letzte offene Aufgabe ist: Es gäbe
  kein nächstes, dasselbe Foto käme zurück. Der Task-Endpunkt zählt dafür auch die andere Frage mit
- Ist gar nichts mehr zu ergänzen, fällt der „Hilf mit"-Bereich ganz weg und die **Karte nimmt die
  volle Breite**. Eine Erfolgsmeldung, die monatelang dasteht, ist kein Inhalt — die Fotos sind es
- Der Leerlauf nach fünf Minuten **lädt die Seite neu**, statt nur den Zustand zurückzusetzen. Im
  Kiosk gibt es keine Browser-Bedienung: kein Reload-Knopf, keine Adressleiste, keine Tastatur —
  ein verhakter Zustand bliebe sonst bis zum Netzstecker stehen. Dazu ein Knopf „Anzeige neu
  laden" in der Verwaltung, für den Fall, dass jemand danebensteht
- Die Zeitachse zeigt immer den ganzen Bestand, die Balken darunter den sichtbaren Ausschnitt.
  Damit bedeutet dieselbe Stelle des Schiebers immer dasselbe Jahr — und eine leere Achse mit einem
  einzelnen Balken sagt, dass es hier nur Fotos aus diesem Jahrzehnt gibt
- Die Datierungsfrage heißt „Wann war das?", passend zu „Wo ist das?". Welche Jahrzehnte zur
  Auswahl stehen, ergibt sich aus dem **Bestand** (mindestens 1920er bis 2010er) statt aus
  `firstDecade`/`lastDecade` in `region.json` — das beschreibt die Sammlung und nicht den Ort, und
  eine Änderung daran zog bisher einen Kartenbau samt Netzzugang hinter sich her
- Bei langen Straßen kommt vor die Hausnummer ein **Abschnitt** — „1–13", „15–24" —, genau wie das
  Jahrzehnt vor dem Jahr. Dazu vertritt die Grundzahl ihre Buchstabenzusätze: Aus 78 Knöpfen im
  Mühlenweg werden vier plus zehn. Kurze Straßen behalten den einen Schritt
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
- Die Detailansicht ist auf Fluchtlinien gebaut: Bild, Textspalte und Schließen-Knopf beginnen auf
  derselben Höhe, die Blätterknöpfe stehen mittig **unter dem Bild** statt mittig im Schirm. Viel
  Text scrollt jetzt in seiner Spalte, statt oben den Schließen-Knopf zu überlagern und unten aus
  dem Bild zu laufen. Der Schließen-Knopf sitzt dafür nicht mehr über dem Foto, sondern führt die
  Textspalte an — in der Form der Blätterknöpfe, damit die Ansicht genau eine Knopfform kennt
- Ein Kreis auf der Karte nennt die Zahl der **Fotos**, nicht die der Stellen: Über einem
  Achterstapel und zwei Einzelbildern steht jetzt 10 statt 3
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
- **„Verwaltung beenden" lädt die Besucheransicht neu.** Wer die Verwaltung verlässt, hat meist
  etwas geändert — importiert, datiert, verortet, versteckt —, und die Karte bekam davon nichts
  mit: Sie hielt ihre Marker und ihr Histogramm die ganze Zeit über fest. Wer nachsah, ob sein
  Import angekommen ist, sah den Bestand von vorher. Gilt für alle drei Auswege: den Knopf oben
  rechts, die Kachel „Auf der Karte zu sehen" und „Anzeige neu laden"
- Die Hausnummern-Auswahl lässt sich **abbrechen**: „Doch nicht — von vorn" führt zurück zum
  Suchfeld, ohne gesetzten Punkt. Bisher gab es dort nur „Reicht so", und das ist eine Antwort und
  kein Rückweg — es behält den Pin auf der Straße. Ausserdem beendet ein Tipp auf die Karte die
  Auswahl jetzt: Vorher blieb das Knopfraster stehen und der nächste Tipp auf eine Hausnummer warf
  den eben gesetzten Punkt wieder weg
- **Fotos lassen sich löschen** — im Editor und in jeder Zeile der Fotoliste, beides mit
  Rückfrage. „Gelöscht" heißt dabei *aus der Ausstellung genommen*, nicht *von der Platte
  entfernt*: Datei und Datenbankzeile bleiben, „Wiederherstellen" holt beides zurück. Der
  bisherige Status „Versteckt" ist darin aufgegangen. Gelöschte Fotos zählen in keiner Kachel der
  Übersicht mehr mit und stehen in keiner Liste ausser „Gelöscht" — sonst wäre das Löschen dort
  wirkungslos, wo jemand hinsieht
- **`docs/index.md`** ist der Wegweiser durch die Dokumentation: acht Dateien, jede mit genau
  einer Frage, gruppiert nach *verstehen · daran arbeiten · betreiben*
- **`docs/architecture.md`** beschreibt, woraus das System besteht und wie die Teile
  zusammenspielen: die drei Prozesse, die beiden gebauten Artefakte und ihre getrennten Wege, was
  zur Bauzeit entsteht und was zur Laufzeit, wo der Zustand liegt und wie ein Foto hereinkommt.
  Bisher stand das nirgends — die Ordnerliste in `development.md` sagt, *was es gibt*, nicht *wie
  es zusammenhängt*
- Die Dokumentation ist neu geordnet. Die Dateinamen folgen jetzt der Konvention und sind englisch
  (`operations.md`, `development.md`, `usermanual.md`); der Inhalt bleibt deutsch, denn er richtet
  sich an Menschen. Aus den drei Plandokumenten, die alle Erledigtes mit Offenem mischten, sind
  **`docs/history.md`** (was gebaut wurde, in der Reihenfolge der Arbeit, und was dabei anders kam
  als geplant) und **`docs/backlog.md`** (was offen ist, nach Verwaltung, Besucher-Interface und
  Infrastruktur) geworden. Die Originalpläne liegen unter `docs/archiv/`
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
- **Eine Migration hätte alle Besucherbeiträge gelöscht.** SQLite kann Constraints nicht ändern,
  also baut Alembic die Tabelle neu — und mit eingeschalteten Fremdschlüsseln räumt dieses Löschen
  der alten Tabelle ab, was daran hängt: Besucherbeiträge (`ON DELETE CASCADE`), die
  Schlagwort-Zuordnungen, die Verknüpfungen des Import-Protokolls. Ohne jede Fehlermeldung.
  `alembic/env.py` schaltet die Prüfung für die Dauer einer Migration jetzt ab; ein Test fährt die
  Migration und zählt nach
- **Gleichnamige Straßen wurden zu einer verschmolzen.** Wer „Hauptstraße" eingab, bekam einen
  Punkt 2,26 km von der Ortsmitte — auf keiner Straße —, und der zweite Schritt bot 153
  Hausnummern aus siebzehn Dörfern an. Der Ausschnitt reicht über den Museumsort hinaus; die
  gleichnamigen Straßen darin wurden gemittelt, und `out center` liefert ohnehin die Mitte des
  umschließenden Rechtecks statt eines Punktes auf der Fahrbahn. Der Ortsindex trennt sie jetzt
  räumlich und nimmt die, deren **niedrigste Hausnummer** der Ortsmitte am nächsten liegt; als
  Punkt dient die **mittlere Hausnummer**, liegt also an einem Haus. Straßen ohne Hausnummern
  bekommen einen Punkt auf ihrem Verlauf. Nachgemessen: 0,18 km statt 2,26 km, 76 statt 153
  Hausnummern, keine Einträge mehr ausserhalb der Region
- Der Ortsindex führt nur noch **Straßen und Hausnummern**. Gebäude, Gewässer, Fluren und Ortsteile
  sind entfallen — für sie gibt es den Pin auf der Karte, und die „Elbe" war der zweite Fall
  desselben Fehlers: Sie mittelte sich aus ihren Teilstücken zu einem Punkt ausserhalb der Region
- **Der Bearbeitungsdialog öffnete sich mitten im Formular.** Wer in der Fotoliste nach unten
  gescrollt hatte und dann ein Foto öffnete, bekam das Formular an derselben Stelle — Vorschaubild
  und Titel standen oberhalb des Bildschirmrands. Gescrollt wird nämlich nicht die Ansicht, sondern
  der Bereich um sie herum, und der behielt beim Wechsel seine Position. Der Editor fängt jetzt
  oben an, und beim Schließen kehrt die Liste an ihre Stelle zurück — mit Filter, Suche und Seite,
  auch über mehrere Seiten hinweg. Dieselbe Ursache betraf den Abschnittswechsel und den Sprung
  von der Importmaske zur Ergebnistabelle; beide fangen jetzt ebenfalls oben an
- **Fotos am selben Ort waren nicht einzeln erreichbar.** Acht Bilder auf identischen Koordinaten
  wurden ab Zoom 18 zu acht Markern exakt übereinander, von denen nur der oberste antippbar war —
  und der Weg dorthin führte ins Leere, denn identische Punkte trennen sich bei keiner Zoomstufe

- **Schlagwörter aus IPTC wurden zu Zeichensalat.** Im Bestand standen „牁档癩潈浬", „楗瑮牥" und
  „浉匠湡敤" — das sind „ArchivHolm", „Winter" und „Im Sande", als UTF-16 gelesen. Die Textfunktion
  probierte `utf-16-le` zuerst, was für die Windows-Felder `XPTitle`/`XPKeywords` richtig ist und
  für IPTC falsch: **Jede** Bytefolge gerader Länge ist gültiges UTF-16, es fliegt also nie ein
  Fehler und der Rückfall auf UTF-8 kommt nie zum Zug. Kaputt waren deshalb genau die Wörter mit
  gerader Byte-Länge. Die beiden Fälle sind jetzt getrennt
- **Der Import hielt „OLYMPUS DIGITAL CAMERA" für einen Titel.** Kameras schreiben ihren eigenen
  Namen in das Titel- und das Beschreibungsfeld; das Foto galt damit als betitelt und wurde nie
  wieder jemandem vorgelegt, der einen echten Titel wüsste — dieselbe Falle wie das Scandatum, ein
  Feld weiter. Bekannte Kamera-Textbausteine werden jetzt verworfen
- **Der Schutz vor dem Migrations-Datenverlust hing an einer Revisionsnummer.** Beim
  Zusammenfassen der drei Migrationen zu einem Anfangsschema wäre der Test mit ihr verschwunden.
  Er läuft jetzt gegen eine Probe-Migration ohne feste Revision, deren Umgebung die echte
  `alembic/env.py` ausführt

- **Der Schließen-Knopf der Detailansicht steht wieder oben rechts.** Er saß seit `b20ff5c` in der
  Kopfzeile der Textspalte — in der Flucht, aber nicht dort, wo man ihn sucht. Die Ansicht hat
  jetzt eine eigene Kopfzeile über beiden Spalten; damit sitzt der Knopf am rechten Rand der ganzen
  Ansicht statt am rechten Rand einer Spalte. Die Fußzeile mit den Blätterknöpfen kostet weiterhin
  nur dann Platz, wenn es einen Stapel gibt: Ein einzelnes Foto bekommt die 4,5 rem als Bildhöhe

- **Hinter dem Foto in der Detailansicht blitzte manchmal eine schwarze Fläche auf.** Sie kam von
  `background: #000` am Bild — einer Zeile aus der Zeit, bevor das Element sein Seitenverhältnis
  als `aspect-ratio` mitbekam. Seitdem entspricht die Box dem Bild genau, der Hintergrund war also
  nur noch **vor** dem Zeichnen zu sehen: beim Öffnen und bei jedem Schritt durch einen Stapel.
  In dieser Zeit wird jetzt gar nichts gezeichnet — auch der Schlagschatten nicht, denn ein
  Schatten um eine leere Fläche sieht nach fehlendem Bild aus. Der Platz bleibt reserviert, es
  springt also nichts


### Hinzugefügt
- **Der Import wertet aus, was in den Dateien und ihren Ordnernamen schon steht.** Bisher kam nur
  ein Bruchteil davon an; ein Archiv, das nach Straße und Hausnummer abgelegt ist, musste danach
  Foto für Foto von Hand verortet werden. Die Regeln liegen in zwei Schichten, siehe
  [docs/decisions.md](docs/decisions.md) Punkt 20:
  - **Metadaten** — gilt für *alle* Importwege, auch das Hochladen im Browser: Fotograf und Rechte
    (EXIF `Artist`/`Copyright`, IPTC By-line, Credit, Source, Copyright) werden zu Bildnachweis
    und Herkunft, eine Beschreibung, die nur den Titel wiederholt, bleibt leer, und ein Titel von
    mehr als 120 Zeichen wandert in die Beschreibung — im Archiv steht die ganze Bildunterschrift
    im Titelfeld, bis zu 223 Zeichen
  - **Pfad** — für Eingangsordner, CLI und USB-Stick: Aus `Hauptstraße/14 Gasthof Petersen/` werden
    Ort, Titel, Ortsbezeichnung und Schlagwörter. **Die Straße erkennt der Ortsindex**, nicht ein
    Ordner namens „Straßen" — es steht damit weiterhin nichts Ortsspezifisches im Code
- **Ob ein EXIF-Datum das Foto datiert, entscheidet jetzt zuerst das Gerät.** Ein Scanner
  (`HP Scanjet 3670`) datiert nichts, ganz gleich welches Jahr dort steht — 116 Dateien des Holmer
  Erstbestands, 91 davon aus einem einzigen Scanlauf von 2015. Eine Kamera datiert, **auch nach
  1990**: Diese Aufnahmen sind wirklich von 2014. `exif_date_max_year` bleibt und entscheidet
  dort, wo die Datei kein Gerät nennt
- **„unbekannt" ist kein Bildnachweis.** In 82 Dateien steht das wörtlich als Fotograf; übernommen
  stünde unter 82 Fotos im Kiosk eine Zeile, die aussieht wie eine Auskunft und keine ist. Ebenso
  verworfen werden `default`, `single` und `x-default`
- **Doppelt kodierte Umlaute werden zurückgedreht** — „August MÃ¶ller" ist „August Möller". Das
  passiert in fremden Programmen, lange bevor die Datei hier ankommt; der Import ist die letzte
  Stelle, an der es auffallen kann
- **Der USB-Stick liest jetzt auch Unterordner**, wie der Eingangsordner es immer schon tat. Die
  Liste der angebotenen Ordner nennt zusätzlich das Laufwerk selbst — ein nach Straßen abgelegter
  Stick hätte sonst Straße für Straße eingelesen werden müssen —, und die Zahl daneben sagt, was
  ein Import wirklich aufnähme, statt was zufällig direkt im Ordner liegt
- **MPO-Dateien werden aufgenommen.** Das ist ein JPEG mit mehreren Bildern, wie es manche Kameras
  bei einer Serie schreiben; 28 Dateien des Erstbestands sind eines. Sein erstes Bild ist ein
  gewöhnliches JPEG — abgewiesen wären 28 Aufnahmen an einem Containerformat gescheitert, das
  niemand ausgesucht hat
- **`make empty` leert den Bestand** — der Schritt vor einem Erstimport. `make seed` wirft den
  Bestand auch weg, setzt aber etwas an seine Stelle; dieser Befehl lässt nichts, und es gibt
  keinen Weg zurück. Er nennt deshalb erst die Zahlen und will dann die **Anzahl der Fotos
  getippt** haben: Ein „j/n" lässt sich beantworten, ohne gelesen zu haben, eine Zahl nicht. Für
  Skripte gibt es `python -m app.cli empty --yes`. Ortsverzeichnis, Karte und Einstellungen
  bleiben stehen
- Drei neue Einstellungen für den Import, alle leer voreingestellt, damit nichts Ortsspezifisches
  im Code steht: `PHOTOMAP_IMPORT_TAGS` (Schlagwörter für jedes Foto — in Holm „Gebäude"),
  `PHOTOMAP_IMPORT_CREDIT` (Bildnachweis, wo die Datei niemanden nennt) und
  `PHOTOMAP_IMPORT_PROVENANCE` (Vorspann der Herkunftsangabe aus dem Dateipfad)

### Behoben

- **Tests lasen die `.env` des Entwicklers mit.** Damit hing das Ergebnis davon ab, was auf
  *diesem* Rechner eingestellt ist — ein Eintrag wie `PHOTOMAP_IMPORT_CREDIT` ließ Tests
  fehlschlagen, die mit den Voreinstellungen rechnen. Die Testumgebung liest die Datei nicht mehr
