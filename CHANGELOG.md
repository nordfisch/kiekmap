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
- `deploy/pi/99-kiekmap-usb.rules` und `kiekmap-usb-mount` hängen Sticks auf Pi OS Lite ein —
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
  `kiekmap-kiosk.service` startet cage mit Chromium im Vollbild, sobald `/api/health` antwortet.
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
  Infrastruktur) geworden
- Gespeicherte Zeitstempel sind durchgängig UTC — auch die der Sicherungsdatei und der Kopfdaten
  auf dem Stick, die bisher Ortszeit schrieben. „Wie lange her" zählt **Kalendertage** entlang der
  deutschen Tagesgrenze: eine Sicherung von gestern Abend ist „1 Tag", nicht „Heute"
- **Der Archivordner schlägt die EXIF-Koordinate, sobald er eine Hausnummer nennt** — bisher galt
  das Umgekehrte. Die Umkehrung steht auf einer Messung: Im Erstbestand teilten sich 278 von 413
  EXIF-verorteten Fotos ihre Koordinate mit einem anderen, an einem Punkt hingen 20 Fotos von vier
  verschiedenen Tagen. Solche Werte sind eingetragen, nicht gemessen. **Die Straßenmitte gewinnt
  weiterhin nicht** — sie wäre mit 150 m gröber als der Punkt, den sie ersetzte
- **Ein Ordner ohne Hausnummer verortet das Foto jetzt auf der Straße**, statt es unverortet zu
  lassen. Die alte Regel wollte verhindern, dass das Foto aus „Wo ist das?" fällt; seit es die
  dritte Frage gibt, fällt es nicht heraus, sondern in die genauere Frage hinein
- **Im „Hilf mit"-Bereich wird die Hausnummer vor dem Jahr gefragt.** Eine Frage wird erst erreicht,
  wenn die vor ihr leer ist — und mit 673 undatierten Fotos wäre die Nachschärf-Frage nie gestellt
  worden
- **Archivinterna gehören in die Herkunft, Fotorückseiten in die Beschreibung.** Eine Angabe, die
  dem Museum beim Verwalten hilft (Regalnummern wie „P 11"), steht in `provenance` und erscheint
  damit nachweislich nie im Kiosk; eine Angabe über das Bild steht in der Beschreibung. Der Präfix
  „Notiz:" bleibt dort stehen — er sagt, dass der Satz von der Rückseite des Abzugs stammt
- **Unter dem Vorschaubild steht der Titel**, und die Adresse nur, wo keiner da ist — umgekehrt als
  bisher. Fehlt die Hausnummer, sagt die Zeile das: „Hauptstraße Nr. ?". **Sichtbare Beschriftung
  und Vorlesetext kommen jetzt aus derselben Funktion**; vorher waren es zwei, die dasselbe sagen
  sollten und es seit dem Aufräumen der Titel nicht mehr taten
- **75 Fotos haben einen Titel aus ihrer Beschreibung bekommen** — zusammengefasst, nicht
  abgeschnitten: aus „Errichtung des Funkmastes" wurde „Funkmast". Ohne Titel sind noch 152; für
  die steht die Adresse unter dem Bild, ohne dass sie in die Daten geschrieben würde
- **Die Detailansicht fragt nicht mehr selbst, sondern verzweigt in den „Hilf mit"-Bereich.** Statt
  eingebetteter Auswahlraster stehen dort bis zu drei Schaltflächen — „Wo ist das?", „Welche
  Hausnummer?", „Wann war das?" —, je nachdem, was dem Foto fehlt; ein Tipp stellt dieses Foto im
  Bereich zu dieser Frage. Das spart bis zu 37 Knöpfe in der Textspalte und macht die **Ortsfrage
  überhaupt erst erreichbar**: Sie braucht die Karte, und die lag unter der Ansicht
- **Eine Jahreszahl im Text datiert das Foto nur, wenn ein Datumswort davorsteht** („um 1910",
  „im Jahre 1934", „Herbst 1970"). Zweistellige Kurzformen werden nicht ausgewertet: „78" ist von
  einer Regalnummer und einer Hausnummer nicht zu unterscheiden

### Behoben

- **Beim Nachschärfen fährt die Karte auf die angebotenen Hausnummern**, nicht mehr auf den
  Straßenpunkt. Bei einer Straße mit 132 Adressen lag genau eine von elf Beschriftungen im
  Ausschnitt; jetzt sind es alle, und die Karte fährt beim Wechsel des Abschnitts mit
- **Der Entwicklungsbestand hatte eine fehlende Migration**, wodurch jeder Besucherbeitrag mit 500
  endete — zwei Tage lang unbemerkt, weil die Tests ihr Schema aus den Modellen bauen
- **Wagenrückläufe in 59 Beschreibungen**, Reste von Windows-Zeilenenden
- **Fotos ohne Herkunftsangabe.** Wurde im Pfad keine Straße erkannt, stieg das Auswerten der
  Ordnerstruktur aus, bevor es die Herkunft vermerkte — obwohl die nur am Pfad hängt und gar nicht
  an der Straße. Drei Fotos des Erstbestands traf es: zwei, die lose in der Importwurzel lagen, und
  eines unter einem mehrdeutigen Straßennamen
- **Eine Hausnummer, die es unter dieser Schreibweise nicht mehr gibt**, findet jetzt ihr Haus über
  die Nachbarnummer mit derselben führenden Zahl („Schulstraße 2" → „2a"). Häuser werden aufgeteilt
  und neu nummeriert; im Erstbestand betraf das 57 Fotos an acht Adressen. Wo die führende Zahl gar
  nicht vorkommt, bleibt das Foto ehrlich straßengenau

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

- **Der Schließen-Knopf der Detailansicht steht wieder oben rechts.** Er saß seit `fe0c95f` in der
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
  im Code steht: `KIEKMAP_IMPORT_TAGS` (Schlagwörter für jedes Foto — in Holm „Gebäude"),
  `KIEKMAP_IMPORT_CREDIT` (Bildnachweis, wo die Datei niemanden nennt) und
  `KIEKMAP_IMPORT_PROVENANCE` (Vorspann der Herkunftsangabe aus dem Dateipfad)

### Behoben

- **Tests lasen die `.env` des Entwicklers mit.** Damit hing das Ergebnis davon ab, was auf
  *diesem* Rechner eingestellt ist — ein Eintrag wie `KIEKMAP_IMPORT_CREDIT` ließ Tests
  fehlschlagen, die mit den Voreinstellungen rechnen. Die Testumgebung liest die Datei nicht mehr
- **Der Eingangsordner hat die Ordnernamen nicht ausgewertet** — ausgerechnet er, den CLAUDE.md
  „den üblichen Weg für das Museumsteam" nennt. Der Erstbestand kam so herein: 929 Fotos, deren
  Straße und Hausnummer im Pfad standen und danach nirgends in der Datenbank. 413 statt 852
  verortet, **null** hausgenau, kein einziger Ortsname, 126 statt 922 Titel, 169 statt 926
  Herkunftsangaben. Auffällig war es nicht, weil die Metadaten-Schicht sauber lief — der Bestand
  sah nicht kaputt aus, nur leer.

  Die Ursache war nicht die vergessene Zeile, sondern **dass sie vergessen werden konnte**: Die
  Pfad-Schicht hing an den Aufrufern, und einer von vieren hatte sie nicht. Sie hängt jetzt am
  `root`-Parameter von `import_file` — wer einen fünften Importweg baut, muss die Frage „was ist
  die Wurzel dieser Datei?" *beantworten*, statt sie zu übersehen. Nebenbei sagt das
  Import-Protokoll nicht mehr „es fehlt noch: Ort" für Fotos, die gleich danach verortet werden
- **`_erledigt/` behält die Ordnerstruktur.** Bisher landete alles flach nebeneinander — bei einem
  nach Straßen abgelegten Stapel also genau die Information zerstört, die ihn ausmacht. Ein
  zweiter Lauf oder auch nur eine Stichprobe hatte danach nichts mehr zu lesen, und gleichnamige
  Dateien aus verschiedenen Häusern stapelten sich zu „023 (2).jpg"

### Geändert

- **Die Sprachregelung gilt jetzt überall, wo sie gelten sollte.** Sie stand seit Stufe 7 in
  CLAUDE.md, war aber nur zur Hälfte umgesetzt: 338 deutsche Kommentare standen in 52
  Produktivcode-Dateien neben 687 englischen, teils in derselben Datei, und neun Dateien hießen
  deutsch. Nachgezogen statt aufgeweicht — andersherum wären 687 Kommentare zu übersetzen gewesen
- Sechs Module und drei Testdateien heißen englisch. Zwei Namen sagen dabei endlich, was drinsteht:
  `admin/jahr.ts` → `admin/yearInput.ts` (es enthält die Jahrzehnt-Regel) und `admin/paging.ts` →
  `admin/pagination.ts` (es hieß nur so, weil `pager.ts` auf macOS mit `Pager.tsx` kollidierte).
  Dazu `frontend/src/texte/` → `frontend/src/text/`
- **Testdateien sind ganz deutsch**, nicht nur ihre Namen — 326 zu 10 war faktisch schon so. Ein
  Test-Docstring ist die Fortsetzung des Testnamens und trägt dasselbe Warum
- **Zitate und Datenwerte behalten ihre Umlaute.** Die Regel widersprach sich hier selbst: Sie
  verbot Umlaute im Quelltext und gab zwei Absätze später `so that "muhlenweg" finds the
  "Mühlenweg"` als erwünschtes Beispiel. `"März"` in der Monatsliste hat ohnehin keinen Ersatz —
  der Kiosk zeigte sonst „Maerz"
- Neu: `python tools/language_check.py` zählt deutsche und englische Kommentare je Datei und meldet
  jede, die die Regel bricht. Bewusst **kein Test** — die Spracherkennung ist eine Heuristik, und
  ein Test, der bei einem Fachbegriff falsch anschlägt, wird bald ausgeschaltet
- **`docs/archiv/` ist weg** — die drei Plandokumente (Stufenplan, Umbau des Verwaltungsmenüs,
  Besucheransicht, zusammen 1156 Zeilen). Sie waren die Quelle, aus der `history.md` und
  `backlog.md` entstanden sind, und wurden seither nicht mehr gepflegt; in der Git-Historie
  bleiben sie lesbar. Der erledigte Punkt „Sprach- und Namenskonsistenz prüfen" ist aus dem
  Backlog in die Historie gewandert — ein Backlog führt Offenes
- **Im Repo liegt kein Gemeindewappen mehr.** `frontend/public/logo.png` ist ein Platzhalter aus
  `tools/build_logo.py`; das Holmer Wappen wird auf dem Gerät eingesetzt, wie die Kartendaten.
  Der Grund ist keine Lizenzfrage — ein Wappen ist nach § 5 UrhG gemeinfrei —, sondern das
  **Wappenrecht**: Ein Hoheitszeichen darf nicht an jeden weitergegeben werden, der ein Repo
  klont, und ein Hinweis heilt das nicht, weil es um Erlaubnis geht und nicht um Zuschreibung.
  Siehe [docs/decisions.md](docs/decisions.md) Punkt 21
- **Der Beispielbestand liegt jetzt im Repo — und ist erfunden.** 18 gezeichnete Bilder aus
  `tools/build_seed.py` (1,1 MB statt 24 MB), dazu ausgedachte Menschen, Bildnachweise und
  Herkunftsangaben. Echt sind nur Straßennamen und Koordinaten: Ohne sie zeigt die Karte nichts
  und die Ortssuche im „Hilf mit"-Bereich findet nichts. Damit tut `make seed` in einem frischen
  Clone endlich das, was das README verspricht. Die Lücken des Bestands — 3 ohne Jahr, 2 ohne Ort,
  2 gelöschte, 8 Beiträge davon 2 zurückgenommene — zählt der Generator nach jedem Lauf nach und
  bricht ab, wenn eine fehlt
- Der Hinweis, dass alles erfunden ist, steht in `seed/README.md`, im README und in der Ausgabe
  von `make seed` selbst. Umgekehrt warnt `make seed-save` davor, echte Fotos zu committen

### Behoben

- **Der Dank versprach etwas, das nicht eintrat.** Wer ein Foto **ohne Ort** datierte, las „Danke!
  Das Foto ist jetzt auf der Zeitleiste" — und sah nichts: Ein Foto ohne Koordinaten steht auf
  keiner Karte, der Fokus bleibt stehen, der Zeitschieber springt nicht. Bei 673 Fotos ohne Jahr
  und 77 ohne Ort ist das kein Randfall

### Geändert

- **Nach einem Beitrag kommt dasselbe Foto mit der anderen Frage**, solange dieser Frage noch etwas
  fehlt — der Dank kündigt sie an („Danke! Und wissen Sie auch, wo das war?"). Damit gibt es die
  falsche Zusage nicht mehr, und der ergiebigste Moment des Bereichs wird genutzt: Wer gerade
  gesagt hat, wann das war, kennt das Foto und schaut es an. Erst wenn nichts mehr fehlt, kommt
  ein neues Bild; „Weiß ich nicht" bleibt der Ausweg. Siehe
  [docs/decisions.md](docs/decisions.md) Punkt 23

### Geändert

- **Die Straße wird im „Hilf mit"-Bereich gewählt statt getippt.** Erst der Anfangsbuchstabe, dann
  die Straße, dann die Hausnummer — dieselbe Bauform wie Jahrzehnt und Jahr. Damit hat die
  Besucheransicht **kein einziges Eingabefeld mehr** und braucht keine Tastatur; das Suchfeld war
  ohne eine nicht zu bedienen und sah aus wie ein defektes Bedienelement. Die Gruppen werden aus
  dem Ortsindex gerechnet, nicht aufgeschrieben: In Holm sind es zehn Knöpfe, von denen sieben
  direkt zur Straßenliste führen. Der Verwaltungsbereich behält seine Suche — dort ist eine
  Tastatur zur Hand. Siehe [docs/decisions.md](docs/decisions.md) Punkt 24
- Neu in `tiles/region.json`: **`streetChoice`** — wie viele Straßen zur Wahl stehen, die dem
  Ortsmittelpunkt nächsten. Der Ortsindex reicht sieben Kilometer weit und umfasst die
  Nachbardörfer; was darüber hinaus liegt, wird weiterhin auf der Karte angetippt. Fehlt der
  Schlüssel, gilt 80

### Behoben

- **Die Mengenanzeige des Zeitschiebers zeigte die Menge nicht.** Die Balken bündelten fest nach
  Jahrzehnten und skalierten linear gegen das hoechste — im Erstbestand mit seinen 256 taggenauen
  Aufnahmen aus 2010 bis 2024 waren das **zwei** Balken, einer voll und einer auf dem Sockel, auf
  dem auch ein Jahrzehnt mit einem einzigen Foto gelandet wäre. Jetzt richtet sich die Bündelung
  nach dem Bestand: nie feiner als die gröbste Datierung darin, und so breit, dass die Spanne in
  dreißig Balken passt. Die Höhe folgt der Wurzel statt der geraden Linie, ein leerer Balken bleibt
  leer. Siehe [docs/decisions.md](docs/decisions.md) Punkt 25
- Der letzte Balken der Leiste begann am rechten Rand und lief darüber hinaus. Die Achse reicht
  jetzt über das letzte Jahr hinaus, damit er darauf Platz hat

### Geändert

- **Der Zeitschieber ist ein Trimmer mit drei Anfassern**, nach dem Vorbild eines Videoschnitts:
  links und rechts je ein Anfasser für die Enden, und der ganze gewählte Bereich lässt sich
  anfassen und durch die Zeit schieben — ein Griff in seiner Mitte zeigt es an. Mit
  gleichbleibender Spanne durch die Jahrzehnte zu wandern kostete vorher zwei Griffe hintereinander,
  bei denen die Spanne zwischendurch falsch war. Am Rand der Achse bleibt die Spanne erhalten,
  statt zu schrumpfen. Die Pfeiltasten verschieben ebenfalls

### Behoben

- **„In welchem Abschnitt vom Hauptstraße?"** — die Frage nach Abschnitt und Hausnummer setzte
  einen festen Artikel vor den Straßennamen und traf damit bei jeder Straße das falsche
  Geschlecht, die nicht männlich ist. Der Name steht jetzt vorn („Hauptstraße — welche
  Hausnummer?"), womit der Fall gar nicht erst entsteht; eine Geschlechterliste wäre genau das
  Ortswissen, das nicht in den Code gehört. Der Fehler ist alt, fiel aber erst auf, seit die
  Straße über Knöpfe gewählt wird und der Weg zur Hausnummer häufiger gegangen wird

### Behoben

- **Der Zeitschieber stand beim Start nicht auf der ganzen Breite.** Die Achse reicht seit dem
  9. August einen Balken über die jüngste Aufnahme hinaus, damit dieser Balken eigene Bahn hat —
  die anfängliche Auswahl endete aber weiter auf dem jüngsten Foto. Rechts blieb ein Stück offen,
  was aussah, als sei schon etwas weggefiltert. Die Auswahl greift jetzt über die ganze Achse; ein
  Zeitfilter geht deswegen nicht ans Backend, die undatierten Fotos bleiben also auf der Karte

### Behoben

- **„Auf der Karte zu sehen" meldete 252 statt 855.** Die Kachel der Verwaltung zählte Fotos mit
  Ort *und* Jahr, mit der Begründung, die Ansicht filtere auf beides zugleich. Das gilt nur,
  solange ein Zeitfilter aktiv ist — steht der Schieber auf der ganzen Achse, schickt der Kiosk
  bewusst keinen, und undatierte Fotos stehen auf der Karte. Beim Erstbestand mit seinen 670 Fotos
  ohne Jahr sagte die Kachel dem Museumsteam damit, drei Viertel der Sammlung seien unsichtbar,
  und schickte es datieren, was längst zu sehen war. Gezählt wird jetzt: veröffentlicht und mit
  Ort. Derselbe Fehler steckte in `python -m app.cli stats`, das dabei zugleich gelöschte Fotos
  mitzählte, wo die Verwaltung sie herausnimmt — beide Zahlen folgen jetzt derselben Regel

### Geändert

- **Der Kartentipp im „Hilf mit"-Bereich ist erst nach Ansage scharf.** Solange „Wo ist das?"
  stand, setzte jeder Tipp auf eine freie Kartenfläche einen Punkt — auch der von jemandem, der
  sich nur orientieren wollte. Ein Tipp daneben, ein bestätigender danach, und im Bestand stand
  eine Verortung, die niemand gemeint hat. Jetzt führt ein Knopf **„Auf der Karte zeigen"** dorthin,
  und solange er gedrückt ist, tritt die Straßenauswahl beiseite: Es ist immer nur ein Weg auf dem
  Schirm. Angeboten wird der Knopf über der jeweiligen Auswahl und in jedem Schritt — auch bei der
  Hausnummer, wo er am meisten einbringt: Wer die Straße kennt, aber die Nummer nicht, zeigt auf
  das Haus. Der gesetzte Punkt bleibt unabhängig davon sichtbar und lässt sich weiter ziehen

### Hinzugefügt

- **Ein Schalter für die Fotos ohne Jahr**, neben dem Zeitschieber. Aus der Meldung „507 Fotos ohne
  Jahr" ist „507 Fotos ohne Jahr **anzeigen**" mit Haken geworden. Ein Foto ohne Datum überlappt
  keinen Zeitraum und fiel deshalb aus jeder Auswahl heraus, sobald jemand den Schieber
  zusammenzog — bei diesem Bestand zwei Drittel der Sammlung, ohne dass irgendwo gestanden hätte,
  dass das passieren würde. Der Schalter steht anfangs an und geht **genau einmal** von selbst aus:
  beim ersten Einengen des Zeitraums, also in dem Moment, in dem die Auswahl anfängt, etwas zu
  bedeuten. Wer ihn danach von Hand wieder einschaltet, bei dem bleibt er an. Die API kennt dafür
  `include_undated`; eingeschaltet lautet die Bedingung „kein Datum **oder** Überlappung"

### Geändert

- **Die Adaptionsanleitung erklärt die Straßenauswahl.** Neuer Schritt 3 in
  [docs/adaption.md](docs/adaption.md): woher die Straßen kommen, wie man mit
  `GET /api/places/streets` nachsieht, was der Knopfbaum bekommt, wie `streetChoice` zu wählen ist
  und was eine zu eng oder zu weit gesetzte `bbox` anrichtet. Dazu zwei überholte Stellen
  berichtigt — die Prüfliste fragte noch nach der Ortssuche im „Hilf mit"-Bereich, die es dort
  nicht mehr gibt

### Geändert

- **Unter dem Vorschaubild auf der Karte steht jetzt Adresse und Jahr** statt der ausgeschriebenen
  Datumsangabe: „Lehmweg 17b — 1953", und wo kein Jahr bekannt ist, „Im Sande 18" allein. Die alte
  Zeile war an dieser Stelle zweimal falsch — unter den Kameraaufnahmen stand der Aufnahmetag, den
  auf einer Übersichtskarte niemand sucht, und unter den rund 670 undatierten Fotos siebenhundertmal
  „Jahr unbekannt". Ein Stapel zeigt die Adresse, die alle seine Fotos teilen, aber kein Jahr; fehlt
  beides, fällt die Zeile weg. Die Beschriftung für Vorlesewerkzeuge behält das volle Datum

### Hinzugefügt

- **Vom Foto direkt in seine Bearbeitung.** Neben dem Titel in der Detailansicht steht ein Stift;
  ein Tipp darauf fragt die PIN ab und öffnet danach **dieses** Foto im Bearbeiten-Bildschirm der
  Verwaltung. Wer am Gerät eine falsche Beschriftung sieht, musste bisher die Verwaltung öffnen,
  die PIN eingeben, in die Fotoliste gehen und suchen — und wonach man sucht, ist ausgerechnet der
  Titel, der falsch ist
- **Die ersten acht Zeichen des SHA-256** stehen in der Detailansicht ganz unten, unter dem
  Bildnachweis, klein und grau. Sie sind die Identität des Fotos unabhängig von der Datenbank, und
  **die Fotosuche der Verwaltung findet sie** — ohne das wäre es eine Kennung, die sich nirgends
  nachschlagen lässt

### Geändert

- **Die Knopfsprache der Besucheransicht.** Aus fünf Formen sind vier Rollen geworden — auswählen,
  übernehmen, zurück, überspringen —, und jede sieht wie ein Knopf aus. Die randlose graue Form
  las sich als Text und ist weg; sie hatte außerdem zwei verschiedene Dinge zusammengeworfen:
  *zurückgehen* bleibt beim Foto, *überspringen* legt es weg. „Weiß ich nicht — nächstes Foto" ist
  jetzt durch eine Linie vom Rest getrennt. „Reicht so — die Straße genügt" ist eine vollwertige
  Antwort und sieht seitdem aus wie „Hier war das". Vier Handlungen tragen ein Symbol **neben** der
  Beschriftung — Haken, Pfeil links, Pfeil rechts, Fadenkreuz —, gezeichnet im Quelltext, weil das
  Gerät offline läuft

### Geändert

- **Der Kopfbereich richtet sich an einer Mittellinie aus.** Wappen, Titel und Zeitschieber
  standen oben bündig und endeten fast fünfzig Pixel auseinander — das CSS behauptete an der
  Stelle, sie seien gleich hoch, und das galt nur für eine Schirmbreite. Drei Rechnungen sind
  durch eine gemeinsame Mitte ersetzt
- **Der Zeitraum lässt sich nicht mehr unter ein Jahrzehnt zusammenschieben.** Damit fällt der
  gezeichnete Griff in der Mitte des Schiebers weg: Er war die Antwort darauf, dass ein auf einen
  Balken zusammengeschobener Bereich keine Fläche mehr zum Anfassen hat, und diesen Zustand gibt
  es nun nicht mehr
- **Das Wappen lädt neu und setzt damit alles zurück** — Karte, Zeitraum, Beitragsbereich, offenes
  Foto. Der Besucherschirm hatte bisher gar keinen Weg zurück in den Anfangszustand
- **Der Titel „Bilder aus Holm" führt in die Verwaltung**, weiterhin über die PIN und ohne
  Unterstreichung. Die beiden Elemente haben damit die Rollen getauscht

### Hinzugefügt

- **Ein Foto, das nur seine Straße kennt, lässt sich in der Detailansicht auf eine Hausnummer
  nachschärfen.** Unter der Adresse steht dasselbe Nummernraster wie im „Hilf mit"-Bereich; ein
  Tipp, und aus „Am Kamp" wird „Am Kamp 5" — der Marker rückt von der Straßenmitte an das Haus.
  Solche Fotos galten bisher als verortet und wurden nie wieder vorgelegt, obwohl sie bei einer
  800-m-Straße bis zu 400 Meter danebenliegen können. Angeboten wird es nur, wo es etwas zu wählen
  gibt: bei straßengenauen Fotos, deren Straße im Ortsindex Adressen hat und deren Hausnummer nicht
  ohnehin schon im Namen steht
- **Der Beitrag geht durch eine eigene Tür** (`POST /api/contribute/{id}/housenumber`), die nur die
  Nummer der gewählten Adresse annimmt. Koordinate und Genauigkeit holt der Server aus dem
  Ortsverzeichnis — der Client bestimmt nichts. Die Regel „Besucher füllen nur leere Felder" bleibt
  daneben unverändert stehen; die Begründung steht in `docs/decisions.md`, Punkt 32
- **Zurücknehmen heißt hier zurücksetzen, nicht löschen.** Eine zurückgenommene Hausnummer legt das
  Foto wieder auf die Straßenmitte, mit dem Straßennamen und der **alten Quelle** — eine
  Kuratorenangabe wird also nicht stillschweigend zum Besucherbeitrag. Dafür merkt sich das
  Änderungsprotokoll seit jetzt auch die vorherige Herkunft
- **Ältere Ortsangaben lassen sich erst zurücknehmen, wenn die neueren zurückgenommen sind.** In
  der falschen Reihenfolge ließe eine Rücknahme sonst einen längst ersetzten Ort wieder auferstehen

### Hinzugefügt

- **„Welche Hausnummer?" ist die dritte Frage im „Hilf mit"-Bereich** — nach „Wo ist das?" und
  „Wann war das?", und ausdrücklich **nachrangig**: Sie kommt erst, wenn keine der beiden anderen
  noch etwas zu fragen hat. Ein Foto irgendwohin zu setzen ist mehr wert, als eines von der
  Straßenmitte an sein Haus zu rücken
- **Wer „Reicht so — die Straße genügt" gedrückt hat, wird nicht im selben Atemzug nach der
  Hausnummer gefragt.** Das ist die eine Ausnahme von der Rangfolge: Die Frage wäre schon
  beantwortet, und sie noch einmal zu stellen liest sich, als hätte niemand zugehört
- **Die Hausnummern einer Straße stehen auf der Karte, solange nach ihnen gefragt wird** — und nur
  so lange. Als Dauerebene wären es im engsten brauchbaren Ausschnitt 152 Zahlen neben den
  Vorschaubildern; im Moment der Frage sind es eine Handvoll, und sie beantworten genau das, was auf
  dem Schirm steht. Während der Abschnittswahl („1–19") steht nichts auf der Karte, und antippbar
  sind die Zahlen nicht — die Tipps gehören den Fotos
- **Die Karte fährt zur Straße, wenn die Nachschärf-Frage kommt.** Ohne das läge die Antwort
  regelmäßig außerhalb des Ausschnitts

### Geändert

- **Die Marker blenden ein, wenn die Gruppierung beim Zoomen kippt**, statt alle auf einmal zu
  springen. Beim Verschieben auf gleicher Stufe passiert nichts — eine Karte, die bei jeder
  Wischbewegung flackert, wäre schlimmer als der Sprung. Wer im Betriebssystem weniger Bewegung
  eingestellt hat, bekommt weiterhin den Sprung
- **Die Karte zeichnet ihre Marker deutlich seltener neu.** Sie hingen an zwei Ereignissen, die
  gemeinsam feuern — gemessen 31 und 30 bei einem einzigen Zoomschritt —, und wurden dabei rund
  sechzigmal komplett neu gebaut. Jetzt wird gezeichnet, wenn die Kamera zur Ruhe kommt, und auch
  dann nur, wenn sich die Menge der sichtbaren Gruppen wirklich geändert hat. Auf dem Pi ist das
  der Unterschied zwischen ruckeln und nicht ruckeln

### Behoben

- **Die Einstellungen der `.env` erreichen im Containerbetrieb wieder alle das Backend.** Die
  Compose-Datei reichte nur einzelne Werte durch; die übrigen fielen still auf ihre Vorgaben
  zurück. Getroffen hat es den Import: Fotos kamen an, aber ohne Schlagwort, ohne Bildnachweis und
  ohne Herkunftsangabe — ohne Fehlermeldung und ohne Eintrag im Protokoll. Die vier Werte, die den
  Container beschreiben und nicht den Ort, gewinnen weiterhin über die Datei

- **Ein Symlink unter `/media` wird nicht mehr als Datenträger angeboten.** `os.path.ismount`
  antwortet für einen Symlink grundsätzlich mit Nein, womit er wie ein gewöhnlicher Ordner aussah
  und die Suche ihm bis dorthin folgte, wohin er zeigt. Auf dem Entwicklungsmac führte das dazu,
  dass die Sicherung in das Verzeichnis lief, das sie sichert — vollständig und mit Handzettel,
  also aussehend wie eine richtige. Genau davor soll die Prüfung auf Einhängepunkte schützen

### Hinzugefügt

- `deploy/docker-compose.mac.yml` und `make prod-mac`: der Containerbetrieb lässt sich auf einem
  Mac fahren, wo es weder `/media` noch die Mount-Propagierung `rshared` gibt. Dieselben Abbilder,
  dieselbe nginx-Konfiguration — nur zwei Einhängungen anders

### Hinzugefügt

- `tools/check_settings.py`: prüft, ob jede Einstellung aus `config.py` den Container erreicht —
  und ob in `docker-compose.yml` und `deploy/.env.example` nur Namen stehen, die es wirklich gibt.
  Ein Tippfehler dort wirkt sonst folgenlos, und eine gelöschte `env_file`-Zeile ließe vier
  Einstellungen still auf ihre Vorgabe zurückfallen, ohne dass ein Test rot würde

### Geändert

- **Das Projekt heißt Kiekmap.** Nach außen mit großem K, im Quelltext und in Pfaden klein,
  `KIEKMAP_` als Präfix der Einstellungen. Für Besucher ändert sich nichts — der Name stand nie in
  der Oberfläche. **Sicherungen aus der Zeit davor werden nicht mehr erkannt**, weil der Name im
  Ordner und im Dateinamen des Archivs steht; einmal neu sichern genügt
- `tools/check_settings.py` liest jetzt auch die echte `.env` — die einzige Datei im Projekt, die
  niemand durchsieht, weil sie nicht versioniert ist. Sie meldet Einstellungen unter einem Präfix,
  das es nicht mehr gibt, und Tippfehler unter dem richtigen

### Behoben

- **Eine zurückgespielte Sicherung bringt ihr Schema jetzt selbst auf Stand.** Bisher musste man das
  Gerät danach von Hand neu starten; ohne den Neustart sah die Ausstellung völlig richtig aus und
  **nahm trotzdem nichts mehr an** — jeder Besucherbeitrag, jede Bearbeitung, jeder Upload endete
  mit einem Fehler. Der Hinweis im Handbuch entfällt damit
- **Eine Sicherung von einer neueren Programmversion wird abgelehnt, bevor etwas ersetzt ist**, mit
  einer Meldung, die sagt, was zu tun ist. Der Bestand auf dem Gerät bleibt unangetastet
- `make dev` und `make dev-backend` ziehen den Schemastand vorweg nach — im Container tut das der
  Entrypoint, auf dem Entwicklungsrechner bisher niemand
- `tools/check_anchors.py` prüft jetzt auch `operations.md`, `usermanual.md` und
  `development.md` — und **Verweise zwischen Dateien**, die bisher gar nicht geprüft wurden. Genau
  die brechen still: Wer einen Abschnitt umschreibt, liest seine eigene Datei, nicht die, die
  hineinverweisen

### Behoben

- **Die beiden Zeilen des Kopfbereichs brechen nicht mehr um.** „Bilder aus" und der Ortsname
  hingen an einer Schwelle im Ansichtsfenster, die 170 px zu spät griff — und selbst oberhalb davon
  blieben 0,3 px Luft, weshalb bei 1470 × 956 Safari umbrach und Chromium nicht. Beides misst sich
  jetzt an der Breite der eigenen Spalte; über den ganzen Bereich von 1024 bis 2560 px bleiben 25
  bis 56 Prozent Luft
- **Auch längere Ortsnamen bleiben einzeilig.** Der Name wird kleiner gesetzt, je länger er ist —
  bis zwölf Zeichen auf jedem Schirm, bis sechzehn auf einem breiten. Vorher brach schon
  „Hetlingen" um. Darunter greift ein Boden: Der Ortsname wird nie kleiner als die Zeile über ihm,
  und ein Umbruch ist ab da die bewusste Rückfallebene

### Geändert

- **Die Blätterknöpfe der Detailansicht stehen fest am unteren Rand**, waagerecht weiter mittig
  unter dem Bild. Vorher klebten sie am Bild und wanderten mit dessen Höhe — zwischen einem
  querformatigen und einem hochformatigen Foto lagen 103 px, sodass ein Stapel mit gemischten
  Formaten den Knopf beim Blättern unter dem Finger wegzog
- **Der Schließen-Knopf steht immer in der Ecke des Bildschirms**, nicht mehr am rechten Rand des
  Inhalts — bei einem schmalen Foto rückte er sonst mit dem Inhalt nach innen

### Behoben

- **Die Textspalte der Detailansicht drückt das Bild nicht mehr zusammen.** Sie stand fest auf
  24 rem und ließ dem querformatigen Scan auf einem 1024er Panel nur 466 px; jetzt wächst sie mit,
  und es sind 610 px. Auf 1920 × 1080 ändert sich nichts — dort war auch nichts zu ändern

### Behoben

- **Fotos mit einem Straßennamen und einer Koordinate aus dem EXIF lassen sich jetzt ebenfalls auf
  eine Hausnummer nachschärfen.** Die Bedingung verlangte eine Genauigkeit, die nur ein Kurator
  setzt, und schloss damit 46 Fotos aus — begründet mit einer Annahme über EXIF-Koordinaten, die
  vier Tage vorher widerlegt worden war. Gemeldet worden war es als „der Knopf fehlt, sobald das
  Jahr bekannt ist"; das Jahr hatte damit nichts zu tun, es war nur bei den betroffenen Fotos
  häufiger bekannt. Die Frage wächst von 70 auf 116 Fotos

### Hinzugefügt

- **395 Fotos aus dem neueren Archivstand des Museums.** Der Bestand wächst von 929 auf **1324**;
  alle 395 sind verortet, 221 hausgenau, und der Zeitschieber reicht jetzt von 1884 bis 2024
- `tools/to_jpeg.py` stellt aus einem Archivordner eine JPEG-Kopie her. Ein Browser zeigt kein
  TIFF an, und die Detailansicht reicht die Originaldatei heraus. Die Einstellung ist am
  Erstbestand **gemessen** (Pillow, Qualität 92, 4:4:4, `optimize`) und steht fest: Zwei Läufe
  über dieselbe Datei müssen denselben SHA-256 ergeben, sonst käme beim nächsten Archivstand jedes
  vorhandene Bild ein zweites Mal herein
- 41 Titel und Beschreibungen aus dem neueren Archivstand für Fotos, die wir schon hatten — jede
  im Änderungsprotokoll und damit einzeln zurücknehmbar

### Behoben

- **Ein Ordner aus lauter Nullen ist keine Hausnummer.** `Lehmweg/00 div/` wurde zur Adresse
  „Lehmweg 0" — die es nirgends gibt, und weil in dem Namen eine Ziffer steht, hätte der
  „Hilf mit"-Bereich nie angeboten, sie richtigzustellen. „00" ist der Ablagekorb des Archivs

### Geändert

- **Der Titel aus dem Ordnernamen wiederholt die Adresse nicht mehr.** „14 Gasthof Petersen" ergibt
  „Gasthof Petersen", die Adresse steht darunter in `place_name`; ein Ordner, der nur eine Nummer
  nennt, lässt den Titel leer. Punkt 41 hatte 815 solcher Titel von Hand bereinigt — der Import
  schrieb 323 davon mit dem nächsten Archivstand zurück
- **Ein Titel gilt ab 60 Zeichen als Bildunterschrift und wandert in die Beschreibung**, vorher ab
  120. Die Zahl ist gemessen: Von 781 handgesetzten Titeln überschreitet keiner 58 Zeichen
- **Der Name der Scannersoftware landet in keinem Feld.** „Intel(R) JPEG Library, version
  [1.51.12.44]" stand als Titel von 35 Fotos. Anders als ein zu langer Titel weicht er auch nicht
  in die Beschreibung aus — dort stünde er im Kiosk unter dem Bild
- **Die 395 Fotos des neuen Archivstands sind nachbereinigt** — 423 Felder in sechs Schritten.
  Kein Titel im Bestand ist noch länger als 58 Zeichen, keiner wiederholt seine Adresse, 11 Fotos
  sind aus ihrem eigenen Text datiert

### Behoben

- **Die Herkunft nennt jetzt immer auch den Pfad im Archiv.** Bei 265 Fotos fehlte er — genau bei
  denen, deren Datei selbst schon eine Herkunft nannte („Familie Boysen"): Der Import füllte das
  Feld nur, wenn es leer war. Wer ein Foto geliehen hat, steht in der Datei; **wo es lag, steht
  nur im Pfad** und geht beim Import verloren, weil die Datei im Bestand nach ihrem SHA-256 heißt.
  Beides steht jetzt nebeneinander
- **Ein abgeschnittener Bildnachweis** bei 19 Fotos: „Förderkreis für Kultur und Brauc" ist genau
  32 Zeichen lang — die Längengrenze des IPTC-Feldes 2:80. Ersetzt durch den vollen Namen
- **Der Bildnachweis ist vereinheitlicht:** Vier Schreibweisen des Förderkreises heißen jetzt alle
  „Förderkreis Kultur und Brauchtum in der Gemeinde Holm e. V."; „August" ohne Nachnamen ist bei
  9 Fotos zu „August Möller" ergänzt. 104 Felder, jedes im Änderungsprotokoll

### Behoben

- **Die Umwandlung nach JPEG nimmt die Metadaten mit** — EXIF, IPTC und XMP. Vorher gingen sie
  verloren: 12 Fotos verloren dabei ihren Fotografen, eine Beschreibung und eine Datierung, und
  fünf trugen danach den Vorgabe-Bildnachweis der Sammlung statt „Hubert Wulf". **Eine falsche
  Zuschreibung sieht aus wie eine Auskunft** — deshalb fiel es niemandem auf. Die 12 sind
  nachgezogen
- **Ein TIFF mit krummem XMP-Tag beendet nicht mehr den ganzen Importlauf.** 25 Archivscans legen
  ihr XMP in einem Zahlen-Tag ab; Pillow wirft darauf `TypeError`, und den fing der Import nicht —
  er ist auf `OSError` und `ValueError` gefasst. TIFF ist ein erlaubtes Format, der Fall also
  erreichbar
- **Ein Unterordner darf seine Straße wiederholen.** `Hörnstraße/Hörnstraße 14` wurde nicht als
  Hausnummer gelesen; das Foto hieß „Hörnstraße 14" über der Zeile „Hörnstraße". Abgeschnitten
  wird nur, wenn dahinter wirklich eine Hausnummer steht — sonst würde aus „Twietenhof" unter
  „Twiete" ein „nhof"

### Hinzugefügt

- **`python -m app.cli dubletten` findet dasselbe Bild mehrfach im Bestand** — über einen
  Differenzhash auf den Vorschaubildern, der Helligkeit, Farbstich und Verkleinerung erträgt. Er
  findet und schreibt nichts: Bei einem Paar trug die *kleinere* Fassung den Bildtext, bei einem
  anderen stand auf einem von zwei sonst gleichen Bildern ein Lastwagen

### Geändert

- **45 Dubletten sind aus der Ausstellung genommen** — 39 Gruppen zusammengeführt, 58 Felder und
  11 Schlagwörter vorher auf das behaltene Foto übernommen. Der Bestand steht bei 1279 sichtbaren
  Fotos, 1275 auf der Karte. „Herausgenommen" heißt weiterhin: aus der Ausstellung, nicht von der
  Platte

### Hinzugefügt

- **Ein Schlagwort für den ganzen Stapel beim Import** — im Formular und beim Stick. Anders als
  Jahr, Ort und Bildnachweis füllt es nicht nur, was leer ist: **eine Schlagwortliste ist eine
  Menge**, das Stapelwort tritt also neben das, was die Datei mitbringt. Mehrere durch Komma
  getrennt

### Geändert

- **Der Abbruch am PIN-Feld heißt „Abbrechen und zurück"** statt „Zurück zur Karte" — erst die
  Handlung, dann das Ziel. Wer schon Ziffern getippt hat, las dort keine Abkürzung zum Verwerfen

### Geändert

- **Der Erstbestand ist durchgesehen** — Punkt 1, der älteste offene Eintrag, in zehn Schritte
  zerlegt und abgearbeitet. **55 Fotos datiert und 14 auf den Monat geschärft:** die
  Bereinigungsrunde vom August hatte im Text nur nach vierstelligen Jahreszahlen gesucht, „80er
  Jahre" und „Foto aus der Nachkriegszeit" liefen ihr durch. Der Bestand steht bei 749 Fotos ohne
  Jahr statt 804, 35 davon jahrzehntgenau statt 5
- **86 Beschreibungen bereinigt** — 16 trugen ihren eigenen Text zweimal, 15 eine Ordnernotiz über
  acht Straßen, 10 wortgleich den Titel, 34 die Adresse, die schon im Ortsfeld steht. Nicht
  angetastet wurden die 131, die den Titel enthalten und dabei **mehr** sagen als er
- **Kein Programmname steht mehr in einem Titel** — zweimal die Scannersoftware, sechsmal „Google
  Maps 2026". Die sechs Kartenbilder sind jetzt Google Maps gutgeschrieben statt dem, der sie
  eingestellt hat; der steht nach `decisions.md`, Punkt 36, in der Herkunft
- **Elf Schlagwörter waren Sätze** und sind in die Beschreibung gewandert, wörtlich. Zwei fielen
  weg, weil sie nur wiederholten, was Ort und Datierung schon sagen. 281 Schlagwörter statt 291

### Behoben

- **Ein aufgehender Cluster wächst jetzt aus dem angetippten Punkt heraus** statt aus der oberen
  linken Ecke der Karte hereinzufliegen. Gemeint war immer ein Aufblenden an Ort und Stelle; die
  Animation lief auf demselben Element, in dessen Inline-Stil MapLibre die Position schreibt, und
  gewann gegen sie
- **Die Vergrößerung beim Berühren eines Markers gibt es wieder** — dieselbe Ursache, andere
  Richtung: als gewöhnliche Regel verlor sie gegen den Inline-Stil und tat gar nichts
- **Ein Kreis liegt immer über einem Vorschaubild** und ist damit erreichbar. Verdeckt war er
  vorher nicht antippbar, und das ist der einzige Weg zu den Fotos dahinter; ein verdecktes Bild
  kostet dagegen nichts, weil der Kreis darüber zu denselben Fotos führt
- **Ein Absturz der Oberfläche lässt das Gerät nicht mehr weiß stehen.** Ein Fehler beim Rendern
  riss die ganze Seite ab, und der Leerlauf-Neustart, der sonst jeden verfahrenen Zustand heilt,
  ging mit unter — ohne Tastatur und Adressleiste war die Vitrine damit tot. Jetzt steht ein
  deutscher Satz da, die Seite lädt sich nach acht Sekunden selbst neu, und ein Knopf tut es
  sofort. **Beim zweiten Mal lädt nichts mehr von selbst**, sonst flackerte der Bildschirm bei
  einem Fehler, der beim Laden wiederkommt
- **Der Eingangsordner verliert bei einem Abbruch nicht mehr, was er schon gelesen hat.** Der
  ganze Durchgang wurde erst am Ende gesichert, während jede Datei schon vorher nach `_erledigt/`
  wanderte: Eine Ausnahme mittendrin nahm die Fotos davor mit — und das Import-Protokoll gleich
  dazu, das den Verlust hätte zeigen sollen
- **Die Uhrzeiten im Verwaltungsbereich stimmen.** Besucherbeiträge, Import-Protokoll und
  Sicherungskachel standen zwei Stunden zu früh: Gespeichert wird UTC, und ein Zeitstempel ohne
  Zonenmarker gilt im Browser laut Norm als Ortszeit. Die API nennt die Zone jetzt. **Das
  Scandatum aus dem EXIF bleibt absichtlich ohne** — es ist die Wanduhrzeit eines Scanners und
  wäre umgerechnet um zwei Stunden falsch
- Der Name des heruntergeladenen Archivs trägt das Datum der Ortszeit, wie der Ordner
  `vorher-…` daneben. Eine Sicherung um halb eins nachts hiess vorher nach gestern
- Die Lizenz der Kartensymbole wird von `make tiles` mitgeholt, bisher blieb sie im
  Temporaerverzeichnis liegen
- Die Zuordnung von MIME-Typ zu Dateiendung steht nur noch an einer Stelle (`suffix_for_mime`).
  Ein Foto mit einem Typ, den dieses Programm nie geschrieben hat — denkbar aus einer
  zurückgespielten Sicherung —, ergab vorher stillschweigend einen Pfad, den es nicht gibt; jetzt
  steht im Protokoll, woran es lag

### Geändert

- Die drei Datumsformate des Verwaltungsbereichs liegen zusammen in `admin/format.ts`, mit dem
  Grund dabei, warum sie sich unterscheiden. Sichtbar ändert sich nichts
- `services/backup.py` ist ein Paket aus zehn Modulen geworden — Laufwerke, Bestand, Schreiben,
  Archiv, Wiederherstellen, Zustand, Auftrag. `from app.services import backup` heißt weiterhin
  dasselbe, und am Programm ändert sich nichts
- `docs/history.md` hat ein **Register** bekommen: eine Zeile je Abschnitt mit Datum und
  Sprungmarke, erzeugt von `tools/build_register.py` und von `make check` nachgeprüft. Die Datei
  bleibt eine — geteilt hätte sie ihre Reihenfolge verloren, und die ist ihr eigentlicher Inhalt
- `tools/check_anchors.py` erkennt Überschriften der ersten Ebene als Sprungmarken und prüft auch
  `docs/architecture.md`, die bis dahin fehlte
- Die Übersicht in `docs/index.md` hat eine Gruppe „Es übernehmen" für `adaption.md` und
  `licensing.md` — beide richten sich an ein zweites Museum, nicht an Entwickler dieses Geräts
- Acht Verweise auf `history.md` zeigen jetzt auf die Stelle, die sie meinen, statt auf die Datei
- `tools/language_check.py` prüft jetzt auch, ob die Dokumentation ihre Umlaute schreibt statt
  sie zu umschreiben. Die Regel stand seit Monaten in `development.md`, mit dem Satz, dieses
  Werkzeug beantworte sie — es las aber nur `.py`, `.ts` und `.tsx`. Rund 900 Stellen in
  `decisions.md` und `history.md` sind nachgezogen, dazu 177 Stellen mit `ss` statt `ß`

- **Alle 185 Commits tragen eine Identität**, `Kalle Erlhoff <kiekmap@erlhoff.de>`. Vorher waren
  es drei, zwei davon von Git aus Konto- und Rechnernamen erzeugt, weil `user.email` nirgends
  gesetzt war. Der Baum ist dabei byte-gleich geblieben
- Commits und Tags werden **signiert** (SSH). Die Commits vor dem 25. August 2026 bleiben
  unsigniert: Bis dahin gab es keinen Remote, also nichts, wogegen eine Signatur geschützt hätte —
  und rückwirkend signiert würden sie unbrauchbar, sobald `allowed_signers` je eine
  Gültigkeitsspanne für den Schlüssel bekommt
- Das README beginnt mit demselben Satz wie die Beschreibung des Repos; es sind die zwei Texte,
  die ein Besucher zuerst sieht, und sie standen in verschiedenen Tönen

### Hinzugefügt

- `make check` prüft alles, was vor einem Commit laufen soll: Stil, die fünf Prüfungen neben den
  Tests, und die Tests selbst — die schnellen zuerst. Dazu `make docs-check` für die Prüfungen
  allein und ein Git-Hook unter `.githooks/pre-commit`, der nur sie ausführt (unter einer Sekunde,
  einzuschalten mit `git config core.hooksPath .githooks`)
- `tools/check_numbers.py` rechnet die Buchführung des Backlogs über seine eigenen Nummern nach:
  Jede je vergebene Nummer ist entweder offen oder vergriffen, die Übersichtstabelle deckt sich
  mit dem Fliesstext, und jede Zeile verweist auf ihren eigenen Punkt
- **Das Projekt steht unter der Apache-Lizenz 2.0**, Copyright 2026 Kalle Erlhoff — `LICENSE` und
  `NOTICE` liegen an der Wurzel und gelten für Code, Dokumentation und die Beispielbilder. Der
  Fotobestand des Museums ist ausdrücklich nicht erfasst: Eine Softwarelizenz lizenziert das
  Programm, nicht die Daten
- **Die Lizenzhinweise der mitgelieferten Pakete reisen jetzt mit.** `make notices` erzeugt zu
  jedem Artefakt eine `THIRD-PARTY.txt` mit den vollen Lizenztexten — 37 Pakete im Frontend, 26 im
  Backend. Das Bundle trug vorher zwei Hinweise für siebenunddreißig Pakete
- Die Karte nennt neben OpenStreetMap auch die Datenlizenz: „© OpenStreetMap-Mitwirkende, ODbL"
- `docs/licensing.md` beantwortet als neunte Datei, was weitergegeben werden darf und unter welchen
  Bedingungen
- Beispiele in Tests, Kommentaren und Dokumentation nennen keine Namen aus dem Holmer Bestand
  mehr, sondern den erfundenen Kader aus `seed/`. Am Programm ändert sich nichts
- Jeder Abschnitt der Historie nennt sein Datum in den ersten Zeilen darunter; die Prüfung bricht
  ab, wenn einer es nicht tut. Neun hatten es vergessen
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS` und Meldungsvorlagen unter
  `.github/` — die fünf Dateien, die ein veröffentlichtes Repo hat. Sicherheitsmeldungen laufen
  über die private Meldung bei GitHub, damit keine Adresse im Klartext im Repo steht
- **Ein Branch-Modell:** `develop` für den Alltag, `main` für den Stand, der im Museum läuft, dazu
  kurzlebige `feature/`- und `fix/`-Branches. **Squash-Merge ist abgeschaltet** — die
  Dokumentation zitiert Commits einzeln mit Hash, und ein Squash vernichtet genau die
- `.github/pull_request_template.md` mit der Prüfliste vor dem Absenden
