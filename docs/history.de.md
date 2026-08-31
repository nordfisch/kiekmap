# Entstehung

Was gebaut wurde, in der Reihenfolge, in der es gebaut wurde — und vor allem: **was dabei anders
kam als geplant.** Das ist der Zweck dieser Datei. Sie ist aus drei Plandokumenten zusammengeführt
— dem Stufenplan, dem Umbau des Verwaltungsmenüs und der Besucheransicht —, die danach entfielen;
in der Git-Historie sind sie weiter zu lesen.

Drei Dateien beschreiben dasselbe Projekt und beantworten drei verschiedene Fragen:

| Datei | Frage |
|---|---|
| [../CHANGELOG.md](../CHANGELOG.md) | *Was kann das Programm?* — sortiert nach Keep a Changelog |
| [decisions.md](decisions.md) | *Warum ist es technisch so gebaut?* — die Grundsatzentscheidungen |
| [architecture.md](architecture.md) | *Woraus besteht es, und wie greift es ineinander?* |
| **history.de.md** | *Wie ist es dazu gekommen?* — die Reihenfolge und die Überraschungen |
| [Issues](https://github.com/nordfisch/kiekmap/issues) | *Was fehlt noch?* |

Die Überraschungen sind das, was sonst niemand aufschreibt. Sie stehen hier als
*„Was der Plan nicht wusste"* und sind der eigentliche Grund für diese Datei.

## Diese Datei ist abgeschlossen

Sie endet am 25. August 2026 mit der Veröffentlichung und der Fassung v0.8.0. Was danach kam, steht
in den Commits, in den Pull Requests und in den geschlossenen Issues — dort entsteht es ohnehin.

**Sie bleibt deutsch.** Übersetzt wäre sie eine zweite Fassung, die veraltet, und ihr Wert liegt in
der Nuance. Vier Monate Arbeitstagebuch bleiben also, wie sie sind.

**Eine Nachfolgerin gibt es nicht.** Was die Arbeit lehrt, wird ein Punkt in
[decisions.md](decisions.md) mit kurzer Begründung; wie es verlief, steht in den Commits und den
geschlossenen Issues.

Ein neuer Abschnitt hier macht `python3 tools/build_register.py --check` rot, weil das
Änderungsregister dann nicht mehr stimmt. Das ist die beabsichtigte Reibung. Eine Änderung an
vorhandener Prosa fängt das Werkzeug nicht — dafür gibt es das Review.

## Nummernregister

Die Punktnummern des damaligen Backlogs. **„Punkt N" meint hier nie ein Issue.** Die Zählung
reicht bis 66, wurde nie neu vergeben und endete am 31. August 2026 mit dem Umzug in die
[GitHub-Issues](https://github.com/nordfisch/kiekmap/issues). Zu Issue-Nummern konnten die Nummern
nicht werden, weil GitHub einen Zähler mit den Pull Requests teilt; die Begründung steht in
[decisions.md](decisions.md), Punkt 69.

### Offen beim Abschluss — vierzehn Punkte

| Punkt | Issue |
|---|---|
| 8 | [#15 · Historische Karte als umschaltbare Grundkarte](https://github.com/nordfisch/kiekmap/issues/15) |
| 9 | [#16 · Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode](https://github.com/nordfisch/kiekmap/issues/16) |
| 14 | [#17 · Bedienbarkeitstest mit der echten Zielgruppe](https://github.com/nordfisch/kiekmap/issues/17) |
| 15 | [#18 · Abnahme auf dem ersten Pi](https://github.com/nordfisch/kiekmap/issues/18) |
| 18 | [#19 · Wiederherstellung wirklich proben](https://github.com/nordfisch/kiekmap/issues/19) |
| 19 | [#20 · Displayauflösung und -orientierung des Museumsgeräts](https://github.com/nordfisch/kiekmap/issues/20) |
| 20 | [#21 · Das Gerät muss einen Stromausfall überstehen](https://github.com/nordfisch/kiekmap/issues/21) |
| 21 | [#22 · Deployment auf einem Webserver evaluieren](https://github.com/nordfisch/kiekmap/issues/22) |
| 30 | [#23 · Die Karte nach Schlagwörtern filtern](https://github.com/nordfisch/kiekmap/issues/23) |
| 31 | [#24 · Einstellungen in der Verwaltung pflegen statt in der `.env`](https://github.com/nordfisch/kiekmap/issues/24) |
| 34 | [#25 · Eine Karte in der Nachbearbeitung des Imports](https://github.com/nordfisch/kiekmap/issues/25) |
| 40 | [#26 · Ein Durchgang über die ganze Oberfläche](https://github.com/nordfisch/kiekmap/issues/26) |
| 43 | [#27 · Der Zeitschieber soll jahrgenau zählen, nicht jahrzehntgenau](https://github.com/nordfisch/kiekmap/issues/27) |
| 54 | [#28 · Das Layout der Detailansicht dem Bildformat folgen lassen](https://github.com/nordfisch/kiekmap/issues/28) |

### Vergriffen — zweiundfünfzig Nummern

Erledigt, aufgelöst oder gestrichen. Wo ein Abschnitt dieser Datei die Nummer im Titel führt, steht
er dabei:

- **1** — [Punkt 1: der Erstbestand, in zehn Schritten durchgesehen](#punkt-1-der-erstbestand-in-zehn-schritten-durchgesehen)
- **22** — [Punkt 22: der Weg nach draussen, an einem Tag](#punkt-22-der-weg-nach-draussen-an-einem-tag)
- **23** — [Punkt 23: die Lizenz war die kleinere Hälfte](#punkt-23-die-lizenz-war-die-kleinere-hälfte)
- **39** — [Punkt 39: der Durchgang von aussen](#punkt-39-der-durchgang-von-aussen)
- **41** — [Der Rest von Punkt 41: Text stand in den falschen Feldern](#der-rest-von-punkt-41-text-stand-in-den-falschen-feldern)
- **42** — [Punkt 42: 44 Gruppen, und die Maschine durfte nicht entscheiden](#punkt-42-44-gruppen-und-die-maschine-durfte-nicht-entscheiden)
- **55** — [Punkt 55, beantwortet mit Nein](#punkt-55-beantwortet-mit-nein)
- **56** — [Punkt 56: der aufgehende Cluster, und zwei stille Nachbarn](#punkt-56-der-aufgehende-cluster-und-zwei-stille-nachbarn)
- **57** — [Punkt 57, 58 und 59, behoben am selben Tag](#punkt-57-58-und-59-behoben-am-selben-tag)
- **58** — [Punkt 57, 58 und 59, behoben am selben Tag](#punkt-57-58-und-59-behoben-am-selben-tag)
- **59** — [Punkt 57, 58 und 59, behoben am selben Tag](#punkt-57-58-und-59-behoben-am-selben-tag)
- **60** — [Punkt 60: 938 Zeilen in zehn Dateien, und die Tests merken nichts davon](#punkt-60-938-zeilen-in-zehn-dateien-und-die-tests-merken-nichts-davon)
- **61** — [Punkt 61: zwei Regeln, und beide lagen anders als notiert](#punkt-61-zwei-regeln-und-beide-lagen-anders-als-notiert)
- **62** — [Punkt 62: die vierte Prüfung prüft etwas anderes als geplant](#punkt-62-die-vierte-prüfung-prüft-etwas-anderes-als-geplant)
- **63** — [Punkt 63: eine Frage, und die Antwort stand längst im Repo](#punkt-63-eine-frage-und-die-antwort-stand-längst-im-repo)
- **64** — [Punkt 64, Abschnitt 1: die Namen aus dem Repo](#punkt-64-abschnitt-1-die-namen-aus-dem-repo)
- **65** — [Punkt 65: veröffentlicht](#punkt-65-veröffentlicht)
- **66** — [Punkt 66: sechs Meldungen, ein Haken](#punkt-66-sechs-meldungen-ein-haken)

Die übrigen — 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 24, 25, 26, 27, 28, 29, 32, 33, 35, 36, 37,
38, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53 — sind weiter unten unter ihrem Datum beschrieben, ohne
die Nummer in der Überschrift zu führen. `grep -n "Punkt 44" docs/history.de.md` findet die Stelle.

<!-- register:anfang -- erzeugt von tools/build_register.py, nicht von Hand ändern -->

## Änderungsregister

95 Einträge. **Gesucht wird hier meist ein Datum**, nicht ein Titel —
die Titel sind Merkhilfen. Für ein Stichwort ist `grep` das bessere Werkzeug; die
Datei ist ausführlich genug dafür.

| Datum | Abschnitt |
|---|---|
| 28.–30. Juli 2026 | **[Teil I — Die Stufen 0 bis 10](#teil-i--die-stufen-0-bis-10)** |
| 28.–30. Juli 2026 | [Stufe 0 — Gerüst und Entscheidungen](#stufe-0--gerüst-und-entscheidungen) |
| 28.–30. Juli 2026 | [Stufe 1 — FastAPI, SQLite, Alembic, Docker](#stufe-1--fastapi-sqlite-alembic-docker) |
| 28.–30. Juli 2026 | [Stufe 2 — Frontend-Gerüst und Offline-Karte](#stufe-2--frontend-gerüst-und-offline-karte) |
| 28.–30. Juli 2026 | [Stufe 3 — Import-Pipeline](#stufe-3--import-pipeline) |
| 28.–30. Juli 2026 | [Stufe 4 — Abfrage-API](#stufe-4--abfrage-api) |
| 28.–30. Juli 2026 | [Stufen 5 und 6 — Karte mit Markern, Zeitschieber](#stufen-5-und-6--karte-mit-markern-zeitschieber) |
| 28.–30. Juli 2026 | [Stufe 7 — „Hilf mit"](#stufe-7--hilf-mit) |
| 28.–30. Juli 2026 | [Stufe 7.5 — Sprachregelung](#stufe-75--sprachregelung) |
| 28.–30. Juli 2026 | [Stufe 7.6 — Deutsche Texte im Backend nach Konvention ordnen](#stufe-76--deutsche-texte-im-backend-nach-konvention-ordnen) |
| 28.–30. Juli 2026 | [Stufe 8 — Admin-Bereich mit Stapel-Upload](#stufe-8--admin-bereich-mit-stapel-upload) |
| 28.–30. Juli 2026 | [Das Raster der Kioskansicht](#das-raster-der-kioskansicht) |
| 28.–30. Juli 2026 | [Stufe 9 — Sicherung und Wiederherstellung auf USB](#stufe-9--sicherung-und-wiederherstellung-auf-usb) |
| 28.–30. Juli 2026 | [Vormerkung erledigt: „Weiß ich nicht" wechselt die Frage](#vormerkung-erledigt-weiß-ich-nicht-wechselt-die-frage) |
| 28.–30. Juli 2026 | [Der Dank lief ins Leere](#der-dank-lief-ins-leere) |
| 28.–30. Juli 2026 | [Kartenstil „Papier"](#kartenstil-papier) |
| 28.–30. Juli 2026 | [Vormerkung erledigt: Hausnummern im Ortsindex](#vormerkung-erledigt-hausnummern-im-ortsindex) |
| 28.–30. Juli 2026 | [Stufe 10 — Kiosk-Deployment auf dem Pi](#stufe-10--kiosk-deployment-auf-dem-pi) |
| 28.–30. Juli 2026 | [Vormerkung erledigt: Import vom USB-Stick](#vormerkung-erledigt-import-vom-usb-stick) |
| 30. Juli 2026 | **[Teil II — Umbau des Verwaltungsmenüs](#teil-ii--umbau-des-verwaltungsmenüs)** |
| 30.–31. Juli 2026 | **[Teil III — Nachbesserungen an der Verwaltung](#teil-iii--nachbesserungen-an-der-verwaltung)** |
| 30.–31. Juli 2026 | [Statuskacheln in der Übersicht](#statuskacheln-in-der-übersicht) |
| 30.–31. Juli 2026 | [Seitenweises Blättern](#seitenweises-blättern) |
| 30.–31. Juli 2026 | [Gemeinsames Jahresfeld, Überschriften](#gemeinsames-jahresfeld-überschriften) |
| 30.–31. Juli 2026 | [Ablagefeld für beide Importwege](#ablagefeld-für-beide-importwege) |
| 31. Juli 2026 | **[Teil IV — Besucheransicht: Fehler und Verbesserungen](#teil-iv--besucheransicht-fehler-und-verbesserungen)** |
| 31. Juli 2026 | [1. Ruhigeres Bild](#1-ruhigeres-bild) |
| 31. Juli 2026 | [2. Der Zeitschieber lief aus seinem Feld](#2-der-zeitschieber-lief-aus-seinem-feld) |
| 31. Juli 2026 | [3. Jahrzehnte kommen aus dem Bestand](#3-jahrzehnte-kommen-aus-dem-bestand) |
| 31. Juli 2026 | [4. Der eigene Beitrag wird sofort sichtbar](#4-der-eigene-beitrag-wird-sofort-sichtbar) |
| 31. Juli 2026 | [5. Fotos am selben Ort](#5-fotos-am-selben-ort) |
| 31. Juli 2026 | [6. Das Foto im Beitragsbereich groß ansehen](#6-das-foto-im-beitragsbereich-groß-ansehen) |
| 31. Juli – 2. August 2026 | **[Teil V — Nachbesserungen an der Besucheransicht](#teil-v--nachbesserungen-an-der-besucheransicht)** |
| 2. August – 25. August 2026 | **[Teil VI — Einzelne Punkte aus dem Backlog](#teil-vi--einzelne-punkte-aus-dem-backlog)** |
| 2. August 2026 | [Verwaltung verlassen lädt die Besucheransicht neu](#verwaltung-verlassen-lädt-die-besucheransicht-neu) |
| 2. August 2026 | [Der Bearbeitungsdialog fängt oben an](#der-bearbeitungsdialog-fängt-oben-an) |
| 2. August 2026 | [Gleichnamige Straßen werden nicht mehr verschmolzen](#gleichnamige-straßen-werden-nicht-mehr-verschmolzen) |
| 2. August 2026 | [Fotos löschen — und ein Datenverlust, der beinahe unbemerkt geblieben wäre](#fotos-löschen--und-ein-datenverlust-der-beinahe-unbemerkt-geblieben-wäre) |
| 2. August 2026 | [Abbruch in der Hausnummern-Auswahl](#abbruch-in-der-hausnummern-auswahl) |
| 2. August 2026 | [`architecture.md` — was es gibt und wie es ineinandergreift](#architecturemd--was-es-gibt-und-wie-es-ineinandergreift) |
| 3. August 2026 | [Ein Beispielbestand — und drei Funde auf dem Weg dahin](#ein-beispielbestand--und-drei-funde-auf-dem-weg-dahin) |
| 3. August 2026 | [Der Schließen-Knopf steht wieder oben rechts](#der-schließen-knopf-steht-wieder-oben-rechts) |
| 3. August 2026 | [Der schwarze Blitz hinter dem Bild](#der-schwarze-blitz-hinter-dem-bild) |
| 3. August 2026 | [Die Sicherung gibt es jetzt auch als eine Datei](#die-sicherung-gibt-es-jetzt-auch-als-eine-datei) |
| 3. August 2026 | [Der Rückweg führt durch den Eingangsordner](#der-rückweg-führt-durch-den-eingangsordner) |
| 4. August 2026 | [Datieren in der Detailansicht](#datieren-in-der-detailansicht) |
| 4.–5. August 2026 | [Der Erstbestand: 929 Fotos aus einem sortierten Archiv](#der-erstbestand-929-fotos-aus-einem-sortierten-archiv) |
| 5. August 2026 | [Sprach- und Namenskonsistenz](#sprach--und-namenskonsistenz) |
| 5. August 2026 | [Zwei Blocker vor der Veröffentlichung](#zwei-blocker-vor-der-veröffentlichung) |
| 8. August 2026 | [Der Backlog bekommt eine Ordnung — und liefert zwei Fehler ab](#der-backlog-bekommt-eine-ordnung--und-liefert-zwei-fehler-ab) |
| 8. August 2026 | [Der Dank, der nichts einlöste](#der-dank-der-nichts-einlöste) |
| 8. August 2026 | [Die Tastaturfrage, beantwortet ohne Tastatur](#die-tastaturfrage-beantwortet-ohne-tastatur) |
| 9. August 2026 | [Was der Erstbestand über den Zeitschieber verriet](#was-der-erstbestand-über-den-zeitschieber-verriet) |
| 9. August 2026 | [Der Durchgang über den Backlog](#der-durchgang-über-den-backlog) |
| 9. August 2026 | [Die Kachel, die drei Viertel der Sammlung verschwinden liess](#die-kachel-die-drei-viertel-der-sammlung-verschwinden-liess) |
| 9. August 2026 | [Die Karte antwortet erst, wenn sie gefragt wird](#die-karte-antwortet-erst-wenn-sie-gefragt-wird) |
| 9. August 2026 | [Was der Schieber wegnahm, ohne es zu sagen](#was-der-schieber-wegnahm-ohne-es-zu-sagen) |
| 9. August 2026 | [Die Straßenauswahl in der Adaptionsanleitung](#die-straßenauswahl-in-der-adaptionsanleitung) |
| 9. August 2026 | [Siebenhundertmal „Jahr unbekannt"](#siebenhundertmal-jahr-unbekannt) |
| 9. August 2026 | [Der kurze Weg vom Foto in seine Bearbeitung](#der-kurze-weg-vom-foto-in-seine-bearbeitung) |
| 9. August 2026 | [Fünf Formen, vier Rollen](#fünf-formen-vier-rollen) |
| 9. August 2026 | [Die Kopfzeile findet ihre Mitte](#die-kopfzeile-findet-ihre-mitte) |
| 9. und 10. August 2026 | [Nachschärfen: der Weg vom Ort zur Hausnummer](#nachschärfen-der-weg-vom-ort-zur-hausnummer) |
| 10. August 2026 | [Die dritte Frage, die Zahlen auf der Karte und ein Wächter zu viel](#die-dritte-frage-die-zahlen-auf-der-karte-und-ein-wächter-zu-viel) |
| 11. August 2026 | [Der Erstbestand wird bereinigt — und zwei Regeln drehen sich um](#der-erstbestand-wird-bereinigt--und-zwei-regeln-drehen-sich-um) |
| 12. August 2026 | [Der Rest von Punkt 41: Text stand in den falschen Feldern](#der-rest-von-punkt-41-text-stand-in-den-falschen-feldern) |
| 12. August 2026 | [Ein Antwortweg statt zweier -- und ein Fehler, der zwei Tage lief](#ein-antwortweg-statt-zweier----und-ein-fehler-der-zwei-tage-lief) |
| 12. August 2026 | [Der Titel kommt auf die Karte, und die Beschriftung bekommt einen Mund](#der-titel-kommt-auf-die-karte-und-die-beschriftung-bekommt-einen-mund) |
| 14. August 2026 | [Der Containerbetrieb ist keine Zusage mehr, sondern gemessen](#der-containerbetrieb-ist-keine-zusage-mehr-sondern-gemessen) |
| 15. August 2026 | [Aus dem Arbeitsnamen wird Kiekmap](#aus-dem-arbeitsnamen-wird-kiekmap) |
| 15. August 2026 | [Der Neustart entfällt: die Wiederherstellung migriert selbst](#der-neustart-entfällt-die-wiederherstellung-migriert-selbst) |
| 16. August 2026 | [Der Kopfbereich hört auf, am Ansichtsfenster zu hängen](#der-kopfbereich-hört-auf-am-ansichtsfenster-zu-hängen) |
| 16. August 2026 | [Die Detailansicht: das Bild bekommt Platz, die Knöpfe bekommen einen Ort](#die-detailansicht-das-bild-bekommt-platz-die-knöpfe-bekommen-einen-ort) |
| 16. August 2026 | [Der Knopf, der angeblich am Jahr hing](#der-knopf-der-angeblich-am-jahr-hing) |
| 16. August 2026 | [Der Diff, der keiner war](#der-diff-der-keiner-war) |
| 16. August 2026 | [Was auf dem Weg verloren ging](#was-auf-dem-weg-verloren-ging) |
| 16. August 2026 | [Punkt 55, beantwortet mit Nein](#punkt-55-beantwortet-mit-nein) |
| 16. August 2026 | [Punkt 42: 44 Gruppen, und die Maschine durfte nicht entscheiden](#punkt-42-44-gruppen-und-die-maschine-durfte-nicht-entscheiden) |
| 16. August 2026 | [Zwei kleine Punkte, und einer hatte einen Fallstrick](#zwei-kleine-punkte-und-einer-hatte-einen-fallstrick) |
| 18. August 2026 | [Punkt 1: der Erstbestand, in zehn Schritten durchgesehen](#punkt-1-der-erstbestand-in-zehn-schritten-durchgesehen) |
| 18. August 2026 | [Punkt 56: der aufgehende Cluster, und zwei stille Nachbarn](#punkt-56-der-aufgehende-cluster-und-zwei-stille-nachbarn) |
| 19. August 2026 | [Punkt 39: der Durchgang von aussen](#punkt-39-der-durchgang-von-aussen) |
| 19. August 2026 | [Punkt 57, 58 und 59, behoben am selben Tag](#punkt-57-58-und-59-behoben-am-selben-tag) |
| 19. August 2026 | [Punkt 61: zwei Regeln, und beide lagen anders als notiert](#punkt-61-zwei-regeln-und-beide-lagen-anders-als-notiert) |
| 19. August 2026 | [Punkt 62: die vierte Prüfung prüft etwas anderes als geplant](#punkt-62-die-vierte-prüfung-prüft-etwas-anderes-als-geplant) |
| 19. August 2026 | [Punkt 63: eine Frage, und die Antwort stand längst im Repo](#punkt-63-eine-frage-und-die-antwort-stand-längst-im-repo) |
| 19. August 2026 | [Punkt 60: 938 Zeilen in zehn Dateien, und die Tests merken nichts davon](#punkt-60-938-zeilen-in-zehn-dateien-und-die-tests-merken-nichts-davon) |
| 21. August 2026 | [Punkt 23: die Lizenz war die kleinere Hälfte](#punkt-23-die-lizenz-war-die-kleinere-hälfte) |
| 21. August 2026 | [Punkt 64, Abschnitt 1: die Namen aus dem Repo](#punkt-64-abschnitt-1-die-namen-aus-dem-repo) |
| 21. August 2026 | [Punkt 64, Abschnitt 2: CLAUDE.md war zur Hälfte ein Tagebuch](#punkt-64-abschnitt-2-claudemd-war-zur-hälfte-ein-tagebuch) |
| 21. August 2026 | [Punkt 64, Abschnitt 3: die Historie war nicht zu lang, sie hatte keinen Eingang](#punkt-64-abschnitt-3-die-historie-war-nicht-zu-lang-sie-hatte-keinen-eingang) |
| 22. August 2026 | [Punkt 64, Abschnitt 4: die Regel stand da und wurde nicht geprüft](#punkt-64-abschnitt-4-die-regel-stand-da-und-wurde-nicht-geprüft) |
| 25. August 2026 | [Punkt 22: der Weg nach draussen, an einem Tag](#punkt-22-der-weg-nach-draussen-an-einem-tag) |
| 25. August 2026 | [Punkt 66: sechs Meldungen, ein Haken](#punkt-66-sechs-meldungen-ein-haken) |
| 25. August 2026 | [Punkt 65: veröffentlicht](#punkt-65-veröffentlicht) |

<!-- register:ende -->
---

# Teil I — Die Stufen 0 bis 10

`bc6345d` … `006f266` · 28.–30. Juli 2026.

Der ursprüngliche Bauplan sah elf Stufen vor, jede in einem lauffähigen, committeten Zustand
endend, jede mit einem Abnahmekriterium in der Form *„Fertig, wenn …"*. Zehn davon sind gebaut.

## Stufe 0 — Gerüst und Entscheidungen

`bc6345d` · Ordnerstruktur, Git-Repo, README, `docs/decisions.md`, `tiles/region.json` als
Platzhalter für den Museumsort.

Die Entscheidungsdatei stand **vor** dem ersten Backend-Commit. Das war kein Formalismus: Aus ihr
folgt, dass nichts Ortsspezifisches in den Code kommt — die Eigenschaft, die ein zweites Museum
ohne Fork möglich macht und die sich später nicht mehr nachrüsten ließe.

## Stufe 1 — FastAPI, SQLite, Alembic, Docker

`d6a3536` · Backend mit `/api/health`, SQLite im WAL-Modus, Migrationen, Dockerfile.

Migrationen laufen beim Containerstart automatisch (`backend/docker-entrypoint.sh`) — auf dem Pi
soll niemand daran denken müssen.

## Stufe 2 — Frontend-Gerüst und Offline-Karte

`bbde347`, `9784979` · React mit MapLibre, Vektorkacheln aus einer PMTiles-Datei, nginx mit
Range-Requests, `tiles/build-tiles.sh`, Region Holm festgelegt.

**Was der Plan nicht wusste:** Der Protomaps-Kartenstil verweist standardmäßig auf
`protomaps.github.io`. Schriften und Symbole mussten mit heruntergeladen und unter
`frontend/public/basemaps/` abgelegt werden — sonst hätte die Karte offline zwar Flächen, aber
keine Beschriftung. Seither gilt die Prüfung: **null Anfragen an eine fremde Herkunft.**

## Stufe 3 — Import-Pipeline

`cb7cbc2` · Datenmodell und Import: SHA-256 als Dateiname und Dublettenschutz, EXIF und IPTC,
Vorschaubilder in zwei Größen, EXIF-Ausrichtung, CMYK-Umwandlung, überwachter Eingangsordner,
`python -m app.cli import|scan|stats`.

Hier entstand die Regel, die das ganze Datenmodell prägt: **ein EXIF-Datum ab 1990 ist das Datum
des Scans und datiert das Foto nicht.** Ohne sie läge ein Foto von 1932 auf der Zeitleiste bei
2019 — und gälte damit als datiert, würde also nie zur Korrektur vorgelegt. Der Fehler wäre still.

Der Eingangsordner räumt Aufgenommenes nach `_erledigt/` bzw. `_problem/`. **Gelöscht wird nie.**

## Stufe 4 — Abfrage-API

`6eecd20` · `/api/photos` mit Kartenausschnitt und Zeitraum, `/histogram`, Auslieferung von
Vorschaubild und Original mit dauerhaftem Cache.

Die zweite stille Falle des Projekts: Datierungen sind **Intervalle**, keine Zeitpunkte. Der
Zeitfilter fragt deshalb auf **Überlappung** ab (`date_from <= bis AND date_to >= von`), nicht auf
Enthaltensein. Bei der naiven Abfrage verschwände der Großteil des Bestands lautlos aus der
Ansicht — ein auf „1920er" datiertes Foto erschiene bei der Auswahl 1925–1930 nicht.

## Stufen 5 und 6 — Karte mit Markern, Zeitschieber

`7c7ea60` · Fotos als Vorschaubilder an ihrem Aufnahmeort, supercluster bei hoher Dichte,
Foto-Overlay in voller Größe, Zeitschieber mit zwei Griffen und Jahrzehnt-Histogramm.

Kartenbewegung und Zeitraum lösen entprellt genau eine Abfrage aus; überholte werden verworfen.

**Was der Plan nicht wusste:** Zeigerereignisse kommen schneller, als React rendert. Der gezogene
Slider-Griff steht deshalb in einem Ref, nicht nur im State — sonst bleibt er bei einer zügigen
Wischbewegung kleben.

## Stufe 7 — „Hilf mit"

`75601df` · Zufällige Fotos ohne Ort oder Jahr, Verortung per Pin auf der Karte oder über die
Ortssuche, Datierung über Jahrzehnt und optional Jahr, Ortsindex aus OpenStreetMap
(`tiles/build-places.py`).

Besucherbeiträge werden **direkt übernommen**, aber nur in leere Felder: Kuratierte Angaben sind
unantastbar, Koordinaten außerhalb der Region werden abgewiesen. Die Suche findet „Mühlenweg" auch
bei Eingabe ohne Umlaut und läuft ohne Internet.

## Stufe 7.5 — Sprachregelung

`1f60d31`, `ae7ce90`, `db1d9b4`, `e405057`, `1bc6ebf` · Bezeichner und Code-Kommentare
durchgängig englisch, Oberflächentexte in `frontend/src/text/de.ts`, `CLAUDE.md`,
`docs/development.md`, `docs/adaption.md`, der Stufenplan.

Der Grund ist nicht Konvention um ihrer selbst willen: `def zeitraum(...) -> DatePrecision` erzeugt
an jeder Grenze zum Bibliothekscode einen Bruch. **Testnamen bleiben die Ausnahme und deutsch** —
sie sind Spezifikationssätze, keine Bezeichner, und `test_scandatum_datiert_das_foto_nicht` ist die
wertvollste Dokumentation im Repo.

## Stufe 7.6 — Deutsche Texte im Backend nach Konvention ordnen

`90325b4` · Bestandsaufnahme nach der Umstellung.

Query-Parameter `?von=…&bis=…` heißen seither `?from_year=…&to_year=…` (nicht `from`, das ist in
Python reserviert). Dabei entstand die **Faustregel**, die alle Grenzfälle ohne Einzelabwägung
entscheidet:

> *Kann diese Meldung im Kiosk oder im Admin-Bereich erscheinen? Dann Deutsch, sonst Englisch.*

Ein 404 auf ein gelöschtes Foto landet im Overlay des Besuchers — deutsch. Eine kaputte `bbox`
sieht nur, wer die API selbst aufruft — englisch. Die CLI ist die Ausnahme in der Ausnahme: Den
Erstimport führt auch das Museumsteam aus, ihre Ausgaben bleiben deutsch.

**Nebenbei ein Fehler, der schwer zu fassen war:** Marker verschwanden gelegentlich von der Karte.
Der `load`-Rückruf konnte eine bereits entfernte Karteninstanz an die Ebenen weiterreichen — die
Vorschaubilder wurden dann sogar geladen, waren aber nie zu sehen. Seither hat der Rückruf einen
`disposed`-Riegel, der später beim Fokus-Effekt (Teil IV, Punkt 4) noch einmal gebraucht wurde.

## Stufe 8 — Admin-Bereich mit Stapel-Upload

`7e6d0d1` · Klick auf das Ortswappen, PIN auf einem Zahlenfeld mit großen Tasten, Sitzung mit
Ablauf. Fotoliste mit Filter und Suche, Metadateneditor, Besucherbeiträge sichten und einzeln
zurücknehmen, Import-Protokoll, Statusübersicht. Stapel-Upload mit Ort und Jahr für den ganzen
Stapel und einer Nacharbeitstabelle.

**Anders als ursprünglich geplant:** Vorgesehen war ein drei Sekunden langer Druck auf die untere
linke Bildschirmecke — für Besucher unsichtbar. Das sichtbare Wappen hat gewonnen: Das Schloss ist
die PIN, nicht das Versteck, und eine unsichtbare Geste ist etwas, das Ehrenamtliche sich merken
müssten. Wer aus Neugier tippt, sieht ein Zahlenfeld und tippt „Zurück zur Karte".

Eine vierstellige PIN sind zehntausend Möglichkeiten, die ein Skript in Sekunden durchprobiert
hätte. **Das Gegengewicht ist die Sperre nach fünf Fehlversuchen** — sie macht aus Sekunden Jahre
und ist der eigentliche Schutz, nicht die Länge der PIN.

**Was der Plan nicht wusste:** Beim Bearbeiten muss ein **fehlendes** Feld „unverändert lassen"
heißen und ein **leeres** Feld „löschen". Ohne diesen Unterschied ließe sich eine falsche
Datierung nur durch eine andere ersetzen, nie durch „weiß man nicht" — und das Foto käme nie
wieder in den „Hilf mit"-Bereich. Pydantic hält die beiden über `model_fields_set` auseinander,
der Endpunkt liest `exclude_unset`.

Dazu: Das Zurücknehmen eines Besucherbeitrags wird verweigert, sobald das Feld inzwischen von Hand
bearbeitet wurde — sonst würde die Arbeit des Kurators mit weggeworfen.

*Fertig, wenn: du am Touchscreen ohne Tastatur hinein- und wieder hinauskommst, einen Stapel
hochladen und dabei Ort und Jahr für alle setzen kannst, und ein Foto vollständig über die
Oberfläche pflegen kannst.* ✅

## Das Raster der Kioskansicht

`91c9aca` · Zwei Spalten, zwei Zeilen: links Titelbereich über „Hilf mit", rechts Zeitschieber
über der Karte.

Der Schieber steht damit genau über der Karte, die er filtert — nicht über dem Beitragsbereich.
Das Wappen führt die linke Spalte an, statt die Karte zu verdecken, und ist zugleich der Weg in
die Verwaltung.

## Stufe 9 — Sicherung und Wiederherstellung auf USB

`fdf9413` · Stick einstecken, ein Knopf, Fortschrittsbalken, am Ende „Der Stick kann jetzt
abgezogen werden".

Bewusst eine **gestaltete Funktion, kein Shell-Skript**: Die Zielgruppe sind ältere Ehrenamtliche,
die das ein- bis zweimal im Jahr tun. Ein Skript bedeutet in der Praxis, dass es nie ausgeführt
wird. Ohne Stick steht dort nur „Bitte USB-Stick einstecken" — kein Knopf, der ins Leere führt.

Drei Bauentscheidungen und ihr Grund:

- **Ordner statt Archiv** auf dem Stick: Eine abgebrochene Sicherung ist dann teilweise brauchbar
  statt komplett wertlos, und man kann sie an jedem Rechner öffnen.
- **Inkrementell über die Hash-Dateinamen:** Liegt der Name schon dort, ist es dasselbe Bild — die
  zweite Sicherung dauert Sekunden.
- **`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Kiosk anzuhalten.

Wiederherstellen kopiert erst daneben und schaltet zuletzt um; der bisherige Stand wandert nach
`data/vorher-<Datum>/` und wird nie gelöscht. Eine abgebrochene Wiederherstellung darf den
laufenden Bestand nicht zerstören. Statt einer Automatik gibt es eine Erinnerung: „Letzte
Sicherung vor 34 Tagen", ab 30 Tagen rot.

**Was der Plan nicht wusste:** Ein Laufwerk muss ein echter Einhängepunkt **und** beschreibbar
sein. Ohne das Erste liefe die Sicherung auf dieselbe SD-Karte, gegen deren Ausfall sie schützt;
ohne das Zweite fiele ein schreibgeschützter Stick erst auf, nachdem jemand den Knopf gedrückt hat.

*Fertig, wenn: jemand aus der Zielgruppe die Sicherung ohne Hilfe und ohne Anleitung schafft — und
die Wiederherstellung auf einem zweiten, leeren Gerät nachweislich funktioniert.* — Die Funktion
ist gegen einen echten eingehängten Datenträger erprobt (sichern, inkrementell erneuern,
zurückspielen, Beiseitelegen). **Beide Hälften des Kriteriums brauchen aber das Gerät und die
Zielgruppe und standen deshalb im Backlog.**

## Vormerkung erledigt: „Weiß ich nicht" wechselt die Frage

`6d515ed` · Wer einen Ort nicht erkennt, weiß vielleicht trotzdem das Jahrzehnt. Dieselbe Frage
noch einmal ist der Grund, warum jemand nach drei Bildern aufhört.

**Was der Plan nicht wusste** — beziehungsweise: was er als Verdacht notierte und was sich
bestätigte: Läuft eine der beiden Fragen leer, muss das Laden auf die andere zurückfallen. Sonst
stünde „Zurzeit ist alles vollständig" auf dem Schirm, während Hunderte Fotos auf eine Jahreszahl
warten. Der Rückfall greift jetzt bei **jedem** Laden, nicht nur beim Wechseln — und behebt
denselben Fehler damit auch nach einem abgegebenen Beitrag.

## Der Dank lief ins Leere

`7146923` · **Karte und Zeitleiste blieben nach einem Besucherbeitrag stehen.** Der Dank versprach
„Das Foto ist jetzt auf der Karte", zu sehen war es aber erst, wenn jemand die Karte verschob und
damit eine neue Abfrage auslöste — also gerade bei den älteren Besuchern, für die der Bereich
gebaut ist, gar nicht. Der unmittelbare Effekt, der überhaupt der Grund für den „Hilf mit"-Bereich
ist, lief damit ins Leere.

`refresh()` lädt seither Marker **und** Histogramm nach: Ein verortetes Foto wandert aus „ohne
Ort" heraus, ein datiertes aus „ohne Jahr" in einen Jahrzehnt-Balken. Nicht entprellt, anders als
beim Kartenverschieben — ein Beitrag ist eine einzelne bewusste Handlung, und genau die soll sofort
sichtbar werden. Bei einem abgelehnten Beitrag (HTTP 409, jemand war schneller) wird nicht
nachgeladen; es hat sich nichts geändert.

## Kartenstil „Papier"

`d435d1d` · Erde in Papierton, Grün zu Salbei entsättigt, Wasser in mattem Graublau statt Türkis.

Die Regel beim Aussuchen: **Nichts auf der Karte darf so gesättigt sein wie ein Foto.** Dazu ohne
Geschäfte, Hausnummern und Autobahnschilder, und mit Straßen auf 80 % ihrer Breite — die kleinen
Straßennamen bleiben, an ihnen hängt die Verortung.

## Vormerkung erledigt: Hausnummern im Ortsindex

`7821519` · Verortung in zwei Schritten: Straße antippen, dann die Hausnummer aus einem
Knopfraster — oder „Reicht so", denn nicht jedes Haus steht in OpenStreetMap. Ohne sie bekam jedes
Foto einer 800 m langen Straße denselben Punkt.

**Was der Plan nicht wusste:** Es sind **7686 Adressen**, nicht „einige hundert bis zweitausend" —
die Bounding Box reicht über Holm hinaus. Der Ortsindex wuchs von 827 auf 8513 Einträge,
`places.json` von 130 kB auf 1,5 MB. Die Suche blieb trotzdem unter 6 ms. Der Lehmweg allein hat
139 Hausnummern — deshalb erscheinen Adressen in der freien Suche erst ab einer Ziffer in der
Eingabe, sonst wären die zwölf Plätze der Trefferliste von einer einzigen Straße belegt.

Dabei fand `location_accuracy_m` endlich seine Verwendung: 150 m für eine Straße, 15 m für eine
Hausnummer, nichts für einen von Hand getippten Punkt. Und Hausnummern werden natürlich sortiert —
1, 1a, 2, 9, 10, nicht 1, 10, 1a, 2, 9.

## Stufe 10 — Kiosk-Deployment auf dem Pi

`3b8893c` · Raspberry Pi OS **Lite** plus **cage**, ein winziger Wayland-Compositor, der genau ein
Programm im Vollbild anzeigt. Robuster als der volle Desktop: nichts kann sich in den Vordergrund
drängen, kein Hintergrundbild blitzt beim Booten auf, keine Update-Hinweise, kein
Bildschirmschoner.

Ablauf nach dem Einschalten (~20 s): Docker startet, die Container laufen von selbst hoch;
`kiekmap-kiosk.service` wartet auf `/api/health` — sonst begrüßt das Museum seine Besucher für
ein paar Sekunden mit einer Fehlerseite; dann `cage -- chromium --kiosk`. Stürzt Chromium ab,
startet systemd ihn neu.

**Was der Plan nicht wusste — dreierlei:**

1. Der Leerlauf-Reset brachte ans Licht, dass `useKiosk.reset()` und `useContribute.reset()` seit
   den Stufen 6 und 7 existierten und **nie jemand sie aufgerufen hatte**. Sie sind seither
   getestet.
2. Was als Anwesenheit zählt, muss eng gefasst sein: Tippen, Tasten, Scrollen — *keine*
   Mausbewegung. Ein vom Ärmel angestoßener Zeiger hielte den Kiosk sonst die ganze Nacht wach.
3. Beim Schreiben der Chromium-Aufrufzeile fielen zwei Flaggen an, die man erst nach dem ersten
   Museumstag vermisst hätte: `--disable-session-crashed-bubble` (nach einem gezogenen Netzstecker
   fragt Chromium sonst „Seiten wiederherstellen?" — mitten in der Ausstellung) und
   `--overscroll-history-navigation=0` (ein Wisch nach rechts löste sonst „Zurück" aus, auf einer
   Karte, die man wischt).

*Fertig, wenn: der Pi nach einem Kaltstart ohne Tastatur von selbst in der Karte landet — und nach
einem gezogenen Netzstecker genauso wieder hochkommt.* — **Gebaut und dokumentiert, aber auf
keinem Pi gelaufen**; es gab beim Bauen kein Gerät. Geprüft sind der Leerlauf-Reset und die
Shell-Syntax aller Skripte. Alles andere stand im Backlog.

## Vormerkung erledigt: Import vom USB-Stick

`006f266` · Unter dem Upload über den Rechner. Ordner mit Bildern erscheinen von allein, sobald
ein Stick steckt; Ort und Jahr aus demselben Formular gelten für beide Wege.

**Bewusst anders als geplant:** Nach dem Lesen kommt *keine* Nacharbeitstabelle. Wer einen Ordner
mit zweihundert Bildern einliest, will keine Tabelle mit zweihundert Zeilen; die
„Unvollständig"-Liste aus Stufe 8 ist genau dafür gebaut. Der Weg endet deshalb mit einem Knopf
dorthin. Beim Upload über den Rechner bleibt die Tabelle — dort hat jemand vierzig Dateien
ausgesucht und will sie beschriften.

Die Warnung aus der Vormerkung erwies sich als die wichtigste Zusage und bekam einen eigenen Test:
**Auf dem Stick wird nichts verschoben und nichts gelöscht.** Der überwachte Eingangsordner räumt
Aufgenommenes nach `_erledigt/` — dort ist das richtig, es ist unser Ordner. Auf einem fremden
Datenträger wäre es ein Übergriff.

**Was der Plan nicht nannte:** Der Pfad wird gegen die erkannten Laufwerke geprüft (`..` bringt
niemanden heraus), und der Import teilt sich den einen Auftrag mit der Sicherung — zwei
gleichzeitige Schreibläufe auf dieselbe SQLite-Datei wären eine Fehlerquelle ohne Not.

---

# Teil II — Umbau des Verwaltungsmenüs

`0ce0a16` · 30. Juli 2026. Der Plan dazu stand in `docs/archiv/umbau-verwaltung.md`, bis das
Verzeichnis am 5. August 2026 entfiel.

Der Admin-Bereich war über die Stufen 8 bis 10 gewachsen, und man sah es ihm an. Drei Dinge
störten konkret: Der Filter kannte nur „Unvollständig" und warf zwei verschiedene Arbeiten
zusammen; die Übersicht nannte sechs Zahlen, von denen nur eine irgendwohin führte; und die
Menünamen überschnitten sich („Hochladen" und „Import" klingen beide nach dem Hereinholen von
Bildern, dabei war das zweite ein Protokoll).

Ziel: eine Verwaltung, in der jemand, der zweimal im Jahr hier ist, **von jeder Zahl aus dorthin
kommt, wo die Arbeit stattfindet.**

1. **Menü** — Übersicht · Fotos · Moderation · Importieren · Protokoll · Sicherung. Erst die
   Pflege des Bestands, dann das Hinzufügen, dann das Technische.
2. **Fotofilter aufgeteilt** in „Ohne Ort" und „Ohne Jahr". Verorten und Datieren sind zwei
   Arbeiten; wer die eine macht, will die andere nicht dazwischen.
3. **Zahlen werden Wege.** Die Kacheln der Übersicht sind Knöpfe und führen in die passend
   gefilterte Liste. Nur „auf der Karte zu sehen" blieb zunächst eine reine Anzeige — es ist das
   Ergebnis, keine Aufgabe.
4. **Importieren fragt erst die Quelle**, dann was für alle gilt: zwei gleichrangige Kacheln statt
   eines Nachtrags unter einer Trennlinie. Jahr und Ort werden **einmal** gefragt und gelten für
   beide Wege.
5. **Nach dem Import eine Regel für beide Wege:** bis 30 Bilder die Nacharbeitstabelle, darüber
   die Zusammenfassung mit einem Sprung in die Liste „Ohne Ort". Die Grenze (`REVIEW_LIMIT`) hat
   einen zweiten Grund: Ohne sie wanderte die Nutzlast von zweihundert Fotos durch einen Status,
   der im Sekundentakt abgefragt wird.

**Der wichtigste Einzelfund war eine stille Falle.** `date_range()` rundet ein Jahrzehnt ab: Wer
1934 eintrug und „Jahrzehnt" wählte, bekam kommentarlos 1930–1939 gespeichert — die 4 verschwand,
ohne dass jemand es merkte. Seither ist „Ganzes Jahrzehnt" nur bei durch zehn teilbaren
Jahreszahlen wählbar, und ein gesetztes Häkchen **nimmt sich selbst zurück**, wenn die Zahl
danach geändert wird. Nur auszugrauen hätte nicht gereicht: Ein gesetztes, aber ausgegrautes Feld
schickte beim Absenden weiterhin `decade`.

**Was der Plan nicht wusste:**

- Die Sicherungs-Erinnerung auf der Startseite verlinkte durch den Umbau versehentlich in die
  Fotoliste. Sie führt jetzt in den Abschnitt „Sicherung".
- Die Dateiauswahl brauchte eine sichtbare Beschriftung — ein `input type="file"` zeigt von sich
  aus kaum etwas an, und in der Maske stand sonst nur ein fast leerer Kasten.
- Die Kuratoren-Anleitung war weiter veraltet als gedacht: Sie beschrieb noch den alten Ablauf und
  trug zwei Platzhalter aus den Stufen 9 und 10, die längst gebaut waren.
- `ImportOutcome` brauchte ein Feld `source` — für die Nacharbeitstabelle wird der Name der
  Quelldatei gebraucht, und `path` war schon mit dem Ablageort belegt.

---

# Teil III — Nachbesserungen an der Verwaltung

`7e79a76` … `bd83b10` · 30.–31. Juli 2026. **Ohne Plandokument** — die Punkte kamen einzeln
aus dem Durchsehen der fertigen Oberfläche.

## Statuskacheln in der Übersicht

`7e79a76` · Unter den sechs Zahlen eine Trennlinie, darunter in denselben drei Spalten der
Betrieb: Tage seit der letzten Sicherung, seit dem neuesten Import, seit dem jüngsten
Besucherbeitrag. Die Sicherungskachel ersetzt den bisherigen Erinnerungsknopf und wird rot, sobald
sie fällig ist. An den Rändern steht ein Wort statt einer Zahl — „Heute gesichert", „Noch nie
importiert". Dazu: „Auf der Karte zu sehen" führt jetzt zurück zur Karte, denselben Weg wie
„Verwaltung beenden" — damit führt **jede** Zahl der Übersicht irgendwohin.

**Was dabei auffiel:** „Wie lange ist das her?" kann der Browser nicht beantworten. Ein
gespeicherter Zeitstempel trägt keine Zeitzone, und JavaScript liest ihn als Ortszeit. Die Antwort
hängt außerdem davon ab, wo die Tagesgrenze liegt. `services/dates.days_since()` zählt deshalb
**Kalendertage** im Backend, entlang der deutschen Tagesgrenze: Eine Sicherung von gestern Abend
ist „1 Tag", nicht „Heute". Bei der Gelegenheit wurden auch die Zeitstempel der Sicherungsdatei
und der Kopfdaten auf dem Stick auf UTC umgestellt — sie schrieben bisher Ortszeit.

## Seitenweises Blättern

`b4cdf45` · Fotoliste, Moderation und Protokoll, dreißig Zeilen je Seite.

Vorher hörten alle drei **still** auf. Die Fotoliste schrieb „60 von 214 Fotos" — an die übrigen
154 kam niemand heran. Der Filterwechsel fängt wieder auf Seite eins an, und wer den letzten
Eintrag der letzten Seite abarbeitet, rutscht auf die letzte noch vorhandene.

## Gemeinsames Jahresfeld, Überschriften

`34c6b1d` · Jahreszahl und Genauigkeit sind seither **ein Bauteil** für beide Stellen, an denen
datiert wird: den Stapel beim Importieren und das einzelne Foto im Editor. Vorher war es dort ein
Ankreuzfeld unter der Zahl, hier ein breites Auswahlfeld daneben — und die Jahrzehnt-Regel aus
Teil II galt nur an einer der beiden Stellen. Im selben Bereich galt zweierlei Recht.

Dazu klarere Überschriften: „Liste aller Fotos", „Protokoll der Foto-Importe", „Auswahl der zu
importierenden Bilder", „Angaben für alle neu hinzugefügten Bilder (optional)". Der Fotobereich
hatte als einziger gar keine.

## Ablagefeld für beide Importwege

`c0cc9d2`, `df6c617`, `bd83b10` · Unter den beiden Quellenkacheln liegt jetzt **eine Fläche an
fester Stelle**, die nur ihren Inhalt wechselt — gestrichelt, solange gewartet wird, mit vollem
Rand, sobald etwas da ist, wie im Sicherungsbereich. Bei „Vom Rechner" ist sie zugleich
Ablagefläche für Dateien; der Knopf „Auswählen" bleibt der verlässliche Weg, denn auf dem Kiosk
gibt es kein Ziehen und Ablegen.

Beim Stick unterscheidet sie **drei** Lagen: kein Stick, Stick ohne Bilder, Ordner gefunden.
Vorher hätte sie jemandem, der gerade eingesteckt hat, „Bitte USB-Stick einstecken"
entgegengehalten — die Art Sackgasse, in der eine ehrenamtliche Person aufgibt.

---

# Teil IV — Besucheransicht: Fehler und Verbesserungen

`a1ed8ea` … `4bfd18e` · 31. Juli 2026. Der Plan dazu stand in
`docs/archiv/besucheransicht.md`, bis das Verzeichnis am 5. August 2026 entfiel.

Sechs Punkte aus dem Durchsehen der Kioskansicht: ein handfester Fehler, zwei Sackgassen in der
Bedienung, drei Verbesserungen. Abgearbeitet wurden sie in der Reihenfolge 2 – 1 – 3 – 4 – 5 – 6:
zuerst die kleinste isolierte Änderung, damit alles Weitere schon richtig aussieht; dann das
Fundament, auf dem zwei andere Punkte aufbauen.

## 1. Ruhigeres Bild

`a1ed8ea` · Alle vier Trennlinien zwischen Titel, Zeitschieber, Beitragsbereich und Karte fallen —
die Bereiche unterscheiden sich danach nur noch durch den Papierton gegen die Karte, und das ist
die einzige Kante mit einer Aufgabe. Neben dem Wappen steht „Bilder aus" statt „Bilder aus
unserem", beide Zeilen größer, zusammen so hoch wie das Wappen.

## 2. Der Zeitschieber lief aus seinem Feld

`fac5095` · **Der handfeste Fehler.** Nach dem Hineinzoomen auf zwei Fotos am Friedhofsweg (beide
„1950er") stand auf der Skala 1950–1960, in der Auswahl aber weiterhin 1920 bis 2019. Die Elemente
rechnen ihre Position in Prozent der Achse aus:

```
.timeline__selected   left: -300%  right: -590%   →  x = -2373 … 6557 px
.timeline__handle     left: -300%                 →  x = -2400 px  (ausserhalb des Bildschirms)
```

Der Auswahlbalken war **8930 px breit** und lief quer über Wappen und Titel. Geklammert wurde
nirgends — weder im Code noch per CSS.

Die Ursache lag tiefer als die Darstellung: Die Achse kam aus dem Histogramm des **sichtbaren
Ausschnitts** und änderte sich bei jedem Zoom, während die Auswahl bewusst stehenblieb. Das ist
kein Randfall — es passiert bei jedem Hineinzoomen in einen Bereich mit weniger Jahrzehnten als
der Gesamtbestand, im Museum also ständig.

**Die Achse spannt seither über den ganzen Bestand und steht still**; nur die Balken darunter
zeigen den Ausschnitt. Damit verschwindet auch die Ursache dahinter: Vorher bedeutete dieselbe
Stelle des Schiebers nach jedem Zoom ein anderes Jahr. Zusätzlich ist die Positionsrechnung auf
0…1 geklammert — der bauliche Riegel, falls Achse und Auswahl je wieder auseinanderlaufen. Steht
in [decisions.md](decisions.md), Punkt 14.

## 3. Jahrzehnte kommen aus dem Bestand

`a6ecc72` · Die Datierungsfrage heißt seither „Wann war das?", passend zu „Wo ist das?".

**Der eigentliche Fund war eine Fehlablage.** `firstDecade`/`lastDecade` standen in
`tiles/region.json` — einer Datei, in der jeder andere Schlüssel Geografie beschreibt und die vom
Kartenbau gelesen wird. Was die Sammlung umspannt, hat damit nichts zu tun. Genau diese Fehlablage
zog beim Ändern zweier Jahreszahlen den Kartenbau und einen Netzzugang hinter sich her.

Die Angabe verschwand **ersatzlos**. Welche Jahrzehnte zur Auswahl stehen, ergibt sich seither aus
dem Bestand, vereinigt mit einem Mindestfenster von 1920er bis 2010er. Findet sich später ein Foto
von 1890, wächst die Reihe nach vorn, sobald das Team es datiert hat — von selbst, ohne dass
jemand eine Einstellung sucht.

*(Ein zuvor geplanter Umbau — `make region`, ein Verteilskript, eine Baumarke — wurde gestrichen.
Er hätte den falschen Ort bequemer erreichbar gemacht, statt ihn zu räumen.)*

## 4. Der eigene Beitrag wird sofort sichtbar

`f4155e4` · Nach einem Beitrag stellt sich die Ansicht für die Dauer des Dankes (2,2 s) auf dieses
Foto ein: Die Karte fährt auf hundert Meter heran, der Zeitraum auf das Jahrzehnt der Angabe —
oder ganz auf, wenn das Foto undatiert ist. Danach kehren **beide zusammen** zurück. Außerdem
springt der „Hilf mit"-Bereich bei jedem Wechsel nach oben.

Die Angaben kommen aus erster Hand: `postLocation()` und `postDate()` geben das aktualisierte Foto
zurück, das vorher weggeworfen wurde. Entschieden wird allein nach dem Foto, wie es jetzt dasteht
— welcher Weg den Beitrag ausgelöst hat, spielt keine Rolle.

**Der Fall „Ort, kein Jahr" deckt eine falsche Zusage ab:** Undatierte Fotos stehen auf der Karte
nur, solange kein Zeitfilter aktiv ist. Wer den Schieber eingeengt hat und dann ein undatiertes
Foto verortet, bekäme sonst eine leere Stelle zu sehen — unter dem Satz „Das Foto ist jetzt auf
der Karte".

**Die Falle, die der Plan vorwegnahm und die tatsächlich zuschlug:** Bei zwei Beiträgen
hintereinander darf `showPhoto` den vorherigen Zeitraum **nur merken, wenn noch keiner gemerkt
ist**. Sonst merkt sich der zweite Aufruf den Zeitraum des ersten Fokus, und der Besucher bekommt
am Ende ein Jahrzehnt zurück, das er nie eingestellt hat.

## 5. Fotos am selben Ort

`871f75c` · **Die zweite Sackgasse.** Am Gasthof Petersen lagen acht Fotos auf identischen
Koordinaten. Ab Zoom 18 fasste supercluster nichts mehr zusammen — aus den acht wurden acht Marker
exakt übereinander, von denen nur der oberste erreichbar war. Und der Weg dorthin führte ins
Leere: Ein Tipp auf die „8" zoomte genau in diesen Stapel hinein. **Identische Punkte trennen sich
bei keiner Zoomstufe.**

Fotos auf demselben Punkt werden seither **vor** dem Clustern zu einem Eintrag zusammengefasst.
supercluster sieht gar keine Dubletten mehr; der Stapel ist auf jeder Zoomstufe ein Marker, so
dargestellt wie ein einzelnes Foto, mit einer Anzahl in der Ecke. Ein Tipp öffnet die
Vollbildansicht mit zwei großen Blätterknöpfen. Das Denkmodell bleibt *ein Ort = ein Marker = die
Fotos von dort*. Steht in [decisions.md](decisions.md), Punkt 15.

Gruppiert wird auf fünf Nachkommastellen, rund einen Meter — das trifft den tatsächlichen Fall:
Über die Ortssuche verortete Fotos tragen exakt dieselbe Koordinate der Straße. Wer den Punkt von
Hand gesetzt hat, bleibt ein eigener Marker; dann *ist* es eine andere Stelle. Oben im Stapel
liegt das zuletzt bearbeitete Foto — die Kartenabfrage sortiert dafür nach `updated_at`, was mit
Punkt 4 zusammenspielt: Die Karte fährt hin, und das eben ergänzte Foto liegt obenauf.

## 6. Das Foto im Beitragsbereich groß ansehen

`359df72` · Das Vorschaubild im „Hilf mit"-Bereich war ein totes `<img>`. Dabei ist „genauer
hinsehen" genau das, was jemand tut, **bevor** er sagt, wo das war — auf 160 px ist ein Hof kaum
zu erkennen. Es öffnet jetzt dieselbe Vollbildansicht wie ein Marker auf der Karte. Ein gesetzter
Pin bleibt dabei erhalten: Er liegt im Store, nicht in der Ansicht.

---

# Teil V — Nachbesserungen an der Besucheransicht

`5f8aaf3` … `8581be2` · 31. Juli – 2. August 2026. **Ohne Plandokument**, wie Teil III.

- **Die Karte fährt schon beim Setzen des Punktes heran** (`5f8aaf3`) — sobald über die Ortssuche
  eine Straße oder Hausnummer gewählt ist, nicht erst nach dem Bestätigen. Der Besucher sieht, wo
  sein Punkt gelandet ist, bevor er ihn abgibt. Ein selbst auf die Karte getippter oder
  verschobener Pin lässt sie stehen: Dort hat er gerade gezielt.
- **Hausnummern in zwei Schritten** (`81c2477`) — bei langen Straßen kommt ein **Abschnitt** vor
  die Nummer („1–13", „15–24"), genau wie das Jahrzehnt vor dem Jahr. Dazu vertritt die Grundzahl
  ihre Buchstabenzusätze. Aus 78 Knöpfen im Mühlenweg werden vier plus zehn. Kurze Straßen
  behalten den einen Schritt.
- **„Hilf mit:" führt in die Frage** (`4aa18a6`) — mit Doppelpunkt, und der Abstand zur Frage
  darunter ist derselbe wie zwischen „Bilder aus" und dem Ortsnamen.
- **Zwei Oberkanten in einer Flucht** (`edeef85`) — die des Wappens mit der des gewählten
  Zeitraums, die von „Hilf mit:" mit der der Karte.
- **Kreise zählen Fotos, nicht Stellen** (`3ba9461`) — eine Folge der Stapel-Gruppierung aus
  Teil IV: Über einem Achterstapel und zwei Einzelbildern stand 3 statt 10. Gelöst über die
  `map`/`reduce`-Aggregation von supercluster.
- **Titel auf Schieberhöhe, Leerlauf lädt neu** (`7b5a9c7`) — Wappen und Titel stehen zusammen so
  hoch wie der Zeitschieber daneben, von seiner ersten Zeile bis zur Jahresskala. Und der Leerlauf
  nach fünf Minuten **lädt die Seite neu**, statt nur den Zustand zurückzusetzen: Im Kiosk gibt es
  keine Browser-Bedienung — kein Reload-Knopf, keine Adressleiste, keine Tastatur —, ein verhakter
  Zustand bliebe sonst bis zum Netzstecker stehen. Dazu ein Knopf „Anzeige neu laden" in der
  Verwaltung, für den Fall, dass jemand danebensteht.
- **Weniger Beiwerk, wenn nichts mehr fehlt** (`7054112`) — „Weiß ich nicht — nächstes Foto"
  verschwindet, wenn es die letzte offene Aufgabe ist; es gäbe kein nächstes, dasselbe Foto käme
  zurück. Ist gar nichts mehr zu ergänzen, fällt der Beitragsbereich ganz weg und die **Karte
  nimmt die volle Breite**. Eine Erfolgsmeldung, die monatelang dasteht, ist kein Inhalt — die
  Fotos sind es.
- **Ein Abstand für waagerecht und senkrecht** (`962fc8f`) — eine Variable `--gap` statt zweier
  Zahlen, die auseinanderlaufen.
- **Die Detailansicht auf Fluchtlinien gebaut** (`8581be2`) — Bild, Textspalte und
  Schließen-Knopf beginnen auf derselben Höhe; die Blätterknöpfe stehen mittig **unter dem Bild**
  statt mittig im Schirm. Viel Text scrollt in seiner Spalte, statt oben den Schließen-Knopf zu
  überlagern und unten aus dem Bild zu laufen. Der Schließen-Knopf verließ dafür die Ecke über dem
  Foto und führt jetzt die Textspalte an — in der Form der Blätterknöpfe, damit die Ansicht genau
  eine Knopfform kennt. *Dabei gefunden:* Die Bildbreite war auf `62vw` gedeckelt, was die
  Textspalte nicht einrechnete; bei einem querformatigen Foto lief der Inhalt über seine eigenen
  Ränder hinaus.

---

# Teil VI — Einzelne Punkte aus dem Backlog

Ab hier keine Blöcke mehr, sondern einzeln aufgegriffene Einträge aus dem Backlog.

## Verwaltung verlassen lädt die Besucheransicht neu

`0609153` · 2. August 2026.

„Verwaltung beenden" führte zurück zur Karte, ohne dass die Ansicht ihre Daten neu holte. Wer
gerade dreißig Fotos importiert oder eine Datierung korrigiert hatte, stand vor dem Bestand von
vorher — und die naheliegende Erklärung, es habe nicht geklappt, war die falsche.

**Das Neuladen sitzt in `leave()`, nicht in `dropSession()`, und das ist keine Feinheit.** Ein
abgelaufenes Token aus der `sessionStorage` lässt `restore()` beim Start über `onAdminSignedOut`
genau in `dropSession()` landen — ein Neuladen dort lüde die Seite endlos neu. Der Docstring hält
das jetzt fest, damit es niemand „aufräumt".

Damit gehen alle drei Auswege denselben Weg: der Knopf oben rechts, die Kachel „Auf der Karte zu
sehen" und „Anzeige neu laden". Der letzte tut technisch dasselbe wie der erste und bleibt
trotzdem stehen — wer eine verhakte Anzeige reparieren will, sucht nach „neu laden" und nicht nach
„beenden". Er ist der Name für den Weg, nicht ein zweiter Weg.

## Der Bearbeitungsdialog fängt oben an

`9f21118` · 2. August 2026.

Wer in der Fotoliste nach unten gescrollt hatte und dann ein Foto öffnete, bekam das Formular an
derselben Stelle — mittendrin, mit Vorschaubild und Titel oberhalb des Bildschirmrands.

**Gescrollt wird nicht die Ansicht, sondern `.admin__body` um sie herum.** `PhotoCare` tauscht nur
seinen eigenen Inhalt gegen den Editor; der Container bleibt und behält seinen `scrollTop`. Der
Inhalt darunter ist dann ein völlig anderer.

**Was der Bericht nicht wusste:** Filter, Suche und Seite waren nie das Problem. `PhotoCare` bleibt
beim Öffnen des Editors gemountet — nur `editing` wechselt —, also lebt sein State weiter. Die als
wichtigste genannte Zusage war schon erfüllt; offen war allein die Scrollposition, und die ist
billig zu haben, wenn man sie beim Öffnen merkt.

Weil der Container `AdminApp` gehört, der Wechsel aber in der Ansicht passiert, reicht ihn ein
Context durch (`admin/scrollArea.tsx`). Die Alternative wäre ein weiteres Prop an jeder Ansicht
gewesen, das mit ihrer Aufgabe nichts zu tun hat.

**Damit waren es drei Stellen, nicht eine** — die Ursache ist allgemein, und wer nur die gemeldete
Stelle geflickt hätte, hätte die anderen beiden stehen lassen:

| | vorher |
|---|---|
| Fotoliste → Editor | Formular öffnet mittendrin; Rückkehr an zufälliger Stelle |
| Abschnittswechsel | nach langer Fotoliste steht man im „Protokoll" mitten im Nichts |
| Importieren, Phasenwechsel | wer unten auf „Importieren" tippt, steht mitten in der Ergebnistabelle |

*Nachgemessen, auch mit Paginierung (`PAGE_SIZE` zum Prüfen vorübergehend auf 5): Seite 4 von 6,
auf 196,5 gescrollt, Foto geöffnet → 0. Nach „Speichern" wie nach „Abbrechen" wieder 196,5,
Seite 4 von 6, Filter „Alle". Der Phasenwechsel beim Importieren ist ungeprüft — dazu bräuchte es
einen echten Import.*

> **Eine Grenze, die bleibt und die keine ist:** Fällt das bearbeitete Foto durch die Änderung aus
> dem aktiven Filter — Ort ergänzt in der Liste „Ohne Ort" —, wird die Liste kürzer, und
> `clampOffset` zieht den Versatz auf eine Seite, die es noch gibt. „Gleiche Seite" gilt also nur,
> solange die Trefferzahl das hergibt. Das ist gewollt: Die Alternative wäre eine leere Seite
> hinter dem Ende.

## Gleichnamige Straßen werden nicht mehr verschmolzen

`8c2d860` · 2. August 2026.

Wer bei der Verortung „Hauptstraße" eingab, bekam einen Punkt **2,26 km von Holms Ortsmitte** — auf
keiner Straße, mitten im Feld. Und der zweite Schritt bot **153 Hausnummern aus siebzehn Dörfern**
an, jede mehrfach.

**Zwei Ursachen, beide im Bauskript.** Gleichnamige Wegstücke wurden nach `(Name, Art)` gruppiert
und ihre Mittelpunkte gemittelt; der Ausschnitt reicht über Holm hinaus, also lagen darin siebzehn
Hauptstraßen, und der Durchschnitt landete zwischen ihnen. Dazu liefert Overpass mit `out center`
die Mitte des umschließenden Rechtecks — bei einer gebogenen Straße also einen Punkt neben der
Fahrbahn.

**Die Lösung kam aus einem Vorschlag im Gespräch und ist besser als die geplante.** Der Plan sah
vor, die ortsnächste Straßengruppe geometrisch zu bestimmen. Stattdessen entscheidet jetzt die
**niedrigste Hausnummer**: Sie liegt in einem gewachsenen Dorf am Ortskern und bleibt dort, auch
wenn die Straße weit hinausführt — die Mitte einer langen Straße wandert dagegen mit ihr aus dem
Ort heraus. Und der Vertreterpunkt ist die **mittlere Hausnummer**, liegt also an einem Haus statt
auf der Fahrbahn; für „Wo war das?" ist das die brauchbarere Antwort.

**Was der Vorschlag nicht wusste:** Ein erster Einfall war, die Postleitzahl in die Konfiguration
aufzunehmen — dann gäbe es je Name nur noch eine Straße. Die Messung sprach dagegen: **29 % der
Straßen (141 von 486) haben gar keine Hausnummer** und damit auch keine PLZ, und an den
Straßen-Wegen selbst steht sie ohnehin nie. Ein Stichprobenlauf gegen Overpass zeigte zudem, dass
sie an 17 % der Adressknoten fehlt. Ein geometrischer Rückfall war also in jedem Fall nötig — er
ist geblieben und deckt genau diese 141 Straßen ab, mit einem Punkt auf ihrem Verlauf
(`out geom` statt `out center`).

**Der Index führt seither nur noch Straßen und Adressen.** Gebäude, Gewässer, Fluren und Ortsteile
sind entfallen — für sie gibt es den Pin auf der Karte. Damit erledigte sich der zweite Fall
desselben Fehlers: Die „Elbe" hatte sich aus ihren Teilstücken zu einem Punkt **ausserhalb der
Region** gemittelt, den das Backend bei einem Beitrag abgewiesen hätte. Dazu werden Wege jetzt auf
den Ausschnitt zugeschnitten, denn Overpass liefert jeden Weg vollständig, sobald er die Bounding
Box nur berührt.

**Die Rechnung steht als `tiles/geometry.py` mit 19 Tests daneben**, und `make test` hat dafür ein
drittes Ziel bekommen. Der Grund ist derselbe wie überall in diesem Projekt: Beide Fehler passieren
**still**. Das Skript lief grün durch, der Index wurde gebaut, und erst im Museum hätte jemand auf
„Hauptstraße" getippt.

*Nachgemessen:*

| | vorher | nachher |
|---|---|---|
| Punkt der Hauptstraße, Abstand zur Ortsmitte | 2,26 km | **0,18 km** |
| Hausnummern der Hauptstraße | 153, alphabetisch sortiert | **76**, in Gehreihenfolge |
| Straßen, deren Punkt auf einer eigenen Hausnummer liegt | — | **345 von 345** |
| Einträge ausserhalb der Region | 54 | **0** |

> **Was bleibt:** Fotos, die vorher auf einen falschen Punkt verortet wurden, stehen weiter dort.
> Der Ortsindex wird ersetzt, die Fotos werden nicht neu verortet — sie sind an ihrem `place_name`
> erkennbar und über die Fotoliste zu korrigieren.

## Fotos löschen — und ein Datenverlust, der beinahe unbemerkt geblieben wäre

`1ceb9b5` · 2. August 2026.

Aus „Verstecken" wurde „Löschen": derselbe Status unter dem Wort, unter dem das Museumsteam ihn
sucht. Bedient wird es im Editor und in jeder Zeile der Fotoliste, beide mit Rückfrage; gelöschte
Fotos zählen in keiner Kachel mehr mit und stehen in keiner Liste ausser „Gelöscht". Die
Begründung steht als Punkt 16 in [decisions.md](decisions.md).

**Der eigentliche Fund war die Migration.** Sie benennt den Wert `hidden` in `deleted` um, und
weil SQLite einen Check-Constraint nicht ändern kann, baut Alembic die Tabelle `photos` dazu neu:
Kopie anlegen, **Original löschen**, umbenennen. Beim ersten Lauf gegen die Entwicklungsdatenbank
nahm dieses `DROP` mit, was daran hing:

| | vorher | nachher |
|---|---|---|
| Besucherbeiträge (`changes`, ON DELETE CASCADE) | 21 | **0** |
| Schlagwort-Zuordnungen (`photo_tags`) | vorhanden | **0** |
| Verknüpfte Einträge im Import-Protokoll (ON DELETE SET NULL) | 38 | **0** |

**Nichts davon warf einen Fehler.** Die Migration lief grün durch, die Fotos waren alle noch da,
und aufgefallen ist es nur, weil die Übersicht danach „0 Beiträge von Besuchern" zeigte, wo vorher
21 standen. Auf dem Museums-Pi wäre der Verlust Wochen später aufgefallen — und dann unwiederbringlich.

Die Ursache ist eine Kette, die einzeln überall richtig aussieht: `app/db.py` schaltet
`PRAGMA foreign_keys=ON` über einen Listener auf der **Engine-Klasse** ein, gilt also für jede
Engine des Prozesses. `alembic/env.py` importiert die Modelle und damit `app.db` — die
Migrationsverbindung erbt die Einstellung. Und mit eingeschalteten Fremdschlüsseln räumt der
Tabellenneubau ab, was auf die Tabelle zeigt.

`env.py` schaltet die Prüfung jetzt für die Dauer der Migration ausdrücklich ab. Das gilt für
**jede künftige Batch-Migration**, nicht nur für diese eine — dieselbe Falle stünde sonst beim
nächsten Constraint wieder auf.

Dazu ein Test, der die Migration wirklich fährt (`tests/test_migrations.py`): Foto, Beitrag,
Schlagwort und Protokolleintrag anlegen, migrieren, nachzählen. Ohne die Reparatur ist er rot.

> **Verloren sind die Testdaten dieser Entwicklungsdatenbank** — 21 Besucherbeiträge, die
> Schlagwörter und die Verknüpfungen des Import-Protokolls. Die Fotos selbst sind vollständig.

*Nebenbei repariert:* `test_alte_sicherung_ist_ueberfaellig` schrieb seinen Zeitstempel in
Ortszeit, gelesen wird er als UTC. Zwischen 22 und 24 Uhr MESZ rutschte der umgerechnete Stempel
auf den nächsten Kalendertag und der Test war rot — zwei Stunden am Tag, seit die Kalendertage
eingeführt wurden.

## Abbruch in der Hausnummern-Auswahl

`55199a7` · 2. August 2026.

Sobald eine Straße gewählt war, zeigte der Beitragsbereich nur noch das Knopfraster der
Hausnummern. Zurück führte einzig „Reicht so" — und das ist **keine Abbruchtaste, sondern eine
Antwort**: Es behält den Pin auf der Straße. Wer die Straße versehentlich getroffen hatte, kam
nicht mehr heraus, ohne etwas zu behaupten.

Daneben steht jetzt **„Doch nicht — von vorn"**: zurück zur Startansicht, ohne gesetzten Punkt.
Leiser gestaltet als „Reicht so", weil es keine Antwort ist, sondern ein Rückweg — dieselbe Form
wie „Anderer Abschnitt" darüber.

**Der subtilere Teil war der zweite:** Ein Tipp auf die Karte beendet die Auswahl jetzt. Vorher
lief beides nebeneinander her — der Pin wanderte, das Knopfraster blieb stehen, und der nächste
Tipp auf eine Hausnummer warf den eben gesetzten Punkt wieder weg. Ein Tipp auf die Karte ist die
bestimmtere Aussage: Dort hat jemand gerade gezielt.

**Woran das erkannt wird, war der eigentliche Fund:** Der Store setzt ein Etikett am Pin **nur**,
wenn er aus der Ortssuche kommt — eine Eigenschaft, die seit dem Heranfahren der Karte
(Teil V) besteht und dort aus einem anderen Grund gebraucht wird. Ein Pin ohne Etikett ist also
per Definition einer von der Karte. Damit ist die ganze Regel eine Zeile, ohne zusätzlichen
Zustand und ohne Vergleich von Koordinaten.

Diese Zusage trägt jetzt die Bedienung an zwei Stellen und hat deshalb einen eigenen Test bekommen.
Bräche sie, bliebe das Knopfraster nach einem Kartentipp still stehen — der Fehler, der eben
behoben wurde, wäre wieder da, ohne dass irgendetwas rot würde.

## `architecture.md` — was es gibt und wie es ineinandergreift

`b035011` · 2. August 2026.

Es gab keine Stelle, an der jemand nachlesen konnte, **aus welchen Teilen das System besteht**. Wer
einstieg, musste sich das aus vier Dateien und dem Code zusammensuchen: `development.md` listete
die Ordner, `decisions.md` begründete Einzelentscheidungen, `operations.md` beschrieb den Betrieb
auf dem Pi — die Verbindung dazwischen stand nirgends.

**Die Abgrenzung war der eigentliche Teil der Arbeit**, sonst wäre eine vierte Datei entstanden,
die dasselbe noch einmal sagt. Die Regel, nach der geschnitten wurde: `architecture.md` beschreibt
*Zusammenhänge* und verweist für Begründungen weiter, statt sie zu wiederholen. Der Abschnitt
„Aufbau" in `development.md` bleibt eine Ordnerliste und verweist jetzt hierher.

Was nur hier steht, weil es zwischen den Teilen liegt und deshalb bisher nirgends hingehörte:

- **Drei Prozesse, zwei davon in Containern.** Chromium ist bewusst keiner.
- **nginx ist der Grund, warum es keinen Tileserver braucht** — es beantwortet Range-Requests auf
  die Kartendatei, und deshalb steht in seiner Konfiguration `gzip off` an genau dieser Stelle.
- **Bauzeit gegen Laufzeit.** Kartendatei und Ortsindex entstehen auf dem Entwicklungsrechner und
  gehen danach *getrennte Wege* — die eine ins Frontend-Image, der andere in die Datenbank.
  `region.json` dient dabei zwei Zwecken: Sie steuert den Bau und konfiguriert die laufende
  Ansicht.
- **Der Zustand liegt an drei Stellen** — SQLite, Dateisystem, `sessionStorage` — mit je einer
  eigenen Aufgabe.
- **Vier Importwege, eine Funktion.** Alle laufen durch `import_file()`, und die schreibt immer
  einen Protokolleintrag.
- **Sicherung, Wiederherstellung und Stick-Import teilen sich einen Auftrag**, damit nie zwei
  Schreibläufe auf dieselbe SQLite-Datei treffen.

Dazu ein Diagramm, das die drei Prozesse, die zwei gebauten Artefakte und ihre Wege in einem Bild
zeigt — die Frage „was läuft wo?" beantwortet es schneller als jeder Absatz.

## Ein Beispielbestand — und drei Funde auf dem Weg dahin

3. August 2026.

Jeder Test der Karte, des Zeitschiebers und des „Hilf mit"-Bereichs lief bis hierhin gegen eine von
Hand befüllte `data/`, die niemand sonst hatte und die zwischen zwei Versuchen nicht
zurückzusetzen war. Das README versprach in seiner Kommandotabelle längst ein `make seed` — das
Ziel gab es nicht.

Die Reihenfolge stand fest, sobald der erste Blick in die Daten fiel: **Die zwanzig echten Holmer
Fotos existierten nur als SHA-benannte Dateien**, ihre Originalnamen und alle Metadaten
ausschließlich in der Datenbank, die geleert werden sollte. Der Export musste also vor allem
anderen kommen — und wurde vor dem Löschen Datei für Datei per SHA-256 gegen seinen Eintrag
nachgerechnet.

### Die Form: Bilder und JSON, kein Datenbankabzug

Ein Abzug ist wertlos, sobald eine Spalte dazukommt — und genau das war zwei Tage vorher passiert.
Hier kostet eine neue Spalte eine Zeile je Foto. Dazu kommt, dass `make seed` durch die **echte**
Import-Pipeline geht statt Zeilen zu schreiben: Es erzeugt die Vorschaubilder, füllt das
Import-Protokoll und prüft den Import gleich mit.

Der Rundlauf ist als Test festgehalten (`test_ausgangszustand_uebersteht_das_hin_und_zurueck`),
und einer seiner Geschwister beschreibt den Fall, der sonst still kaputtginge:
`test_luecken_bleiben_luecken` — beim Zurückholen läuft jedes Foto durch den Import, und wenn der
dabei ein Datum oder einen Ort einträgt, verschwindet das Foto aus dem Beitragsbereich. **Die
Lücke muss die stärkere Angabe sein.**

### Was der Plan nicht wusste, erstens: die Schlagwörter waren Zeichensalat

Im Bestand standen die Schlagwörter `牁档癩潈浬`, `楗瑮牥` und `浉匠湡敤`. Das sind „ArchivHolm",
„Winter" und „Im Sande", als UTF-16 gelesen.

`_text()` in `services/exif.py` probierte `utf-16-le` **zuerst** — richtig für die
Windows-Felder `XPTitle` und `XPKeywords`, die wirklich UCS2-LE sind, falsch für IPTC. Die Tücke:
**Jede** Bytefolge gerader Länge ist gültiges UTF-16, es fliegt also nie ein `UnicodeDecodeError`
und der Rückfall auf UTF-8 kommt nie zum Zug. Der Beweis stand in den Daten selbst — kaputt waren
genau die Wörter mit gerader Byte-Länge, heil die mit ungerader („Gebäude", „Hauptstraße"). Das
sah nach Zufall aus und war eine Regel.

Die Funktion ist jetzt zweigeteilt: `_xp_text()` für die XP-Felder, `_text()` für alles übrige.

### Was der Plan nicht wusste, zweitens: der Import hielt „OLYMPUS DIGITAL CAMERA" für einen Titel

Zwei Fotos trugen genau diesen Satz als Titel *und* als Beschreibung. Er steht wirklich in den
Dateien — Olympus-Kameras schreiben ihren eigenen Namen in beide Felder.

**Das ist dieselbe Falle wie das Scandatum, ein Feld weiter.** Der Wert ist da, das Foto gilt
damit als betitelt und wird nie wieder jemandem vorgelegt, der einen echten Titel wüsste. Also
dieselbe Behandlung: `_statement()` verwirft eine kleine Liste bekannter Kamera-Textbausteine, und
kein Titel ist ehrlicher als dieser.

### Was der Plan nicht wusste, drittens: der Testschutz hing an den Revisionsnummern

Die drei Migrationen wurden zu einem Anfangsschema zusammengefasst — es gibt kein Gerät im Feld,
also gab es keine Datenbank, von der ein Migrationsweg irgendwohin geführt hätte. Mit den Dateien
verschwand auch die Migration, die den Datenverlust angerichtet hatte.

Beinahe verschwunden wäre damit aber der Test, der ihn seither verhindert: Er zog namentlich auf
die Revision `b7c41d0a92e3` hoch. Ein Test, der mit dem Fehler stirbt, den er bewacht, ist keiner.

Er läuft jetzt gegen eine **Probe-Migration** unter `tests/fixtures/sample_migration/` — eine
einzige Revision, die `photos` mit `recreate="always"` neu baut und sonst nichts. Ihre `env.py`
tut nur eines: sie führt die **echte** aus. Eine eigene Kopie der Fremdschlüssel-Regel würde nur
sich selbst bestätigen. Die Gegenprobe steht: Wird das `PRAGMA foreign_keys=OFF` in
`alembic/env.py` auf `ON` gedreht, ist der Test rot.

### Bildnachweis und Herkunft

Als einziger schema-wirksamer Backlog-Punkt vorgezogen, weil die Angaben beim Kuratieren ohnehin
mit eingegeben werden. Der Backlog ließ offen, ob es ein Feld oder zwei sind und wer sie sieht —
es sind zwei, und **die Trennung ist der Punkt**:

- `credit` — Bildnachweis, eine Zeile, im Besucher-Overlay unter der Beschreibung
- `provenance` — Herkunft, Leihgeber, Freigabe, nur in der Verwaltung

Durchgesetzt wird das nicht durch eine Verabredung, sondern durch den Typ: Der Kiosk-Endpunkt
liefert `PhotoDetail`, und diese Klasse hat kein Feld für die Herkunft. Die Verwaltung bekommt
`PhotoAdminDetail`, das davon erbt und eines hinzufügt. Der Test dazu heißt
`test_herkunft_erscheint_nicht_in_der_besucheransicht` und prüft den Fehlerfall, nicht den
Erfolgsfall.

Beide sind auch **gemeinsame Angabe** beim Stapel-Import, neben Jahr und Ort — eine Kiste Scans
kommt fast immer von einer Person.

### Der Bestand selbst

Aus 28 Zeilen wurden 16: neun synthetische Testbilder heraus (die gehören nach
`backend/tests/fixtures/`, auf ihnen ist nichts zu sehen, was auf einer Karte Sinn ergäbe), drei
von vier 4K-Videostandbildern desselben Motivs heraus — sie belegten 40 der 51 MB —, und ein Foto
auf Wunsch.

Was beim Durchsehen sonst noch auffiel und korrigiert wurde:

- **Drei Fotos lagen 1,6 km neben ihrer eigenen Adresse.** Sie trugen „Hauptstraße 14" als Namen
  und Koordinaten im freien Feld bei „An den Wischen". Der Ortsindex sagte eindeutig, welche der
  beiden Angaben stimmt.
- **Zwei Titel waren Dateinamen** („pic 158-1"). Geleert — aus demselben Grund, aus dem der
  Kamera-Filter entstand.
- **Die Beitragsliste enthielt nur Statuswechsel aus dem Ausprobieren**, während mehrere Fotos
  `*_source = visitor` trugen, **ohne** dass es dazu einen Protokolleintrag gab. Das Zurücknehmen
  in der Verwaltung hängt aber genau daran. Jetzt gibt es zu jeder Besucherangabe einen Eintrag,
  und einer davon ist zurückgenommen — sonst ließe sich der Fall nie ansehen.

**Die Lücken im Bestand sind Absicht.** Ein Bestand, in dem alles vollständig ist, prüft die
Hälfte des Programms nicht: Ohne undatierte und unverortete Fotos hat der „Hilf mit"-Bereich
nichts vorzulegen. Sie entstehen aus nachgelieferten Scans, nicht aus dem Löschen echter Angaben —
ein frisch importierter Scan hat von sich aus weder Ort noch Jahr, und das ist zugleich der
realistische Fall.

## Der Schließen-Knopf steht wieder oben rechts

3. August 2026.

Der Umbau vom 2. August (`8581be2`) hatte ihn aus der Ecke in die Kopfzeile der Textspalte geholt.
Das fluchtete mit der Oberkante des Bildes — aber es las sich nicht wie ein Schließen-Knopf. Die
gewohnte Stelle ist oben rechts.

Die Ansicht hat dafür eine eigene Kopfzeile bekommen, die **über beide Spalten geht**. Das ist der
ganze Trick: Stünde der Knopf weiter in der Textspalte, säße er am rechten Rand *dieser Spalte*;
über beide Spalten gespannt sitzt er am rechten Rand der ganzen Ansicht. Drei Zeilen also — Kopf,
darunter Bild und Text nebeneinander, darunter die Blätterknöpfe.

**Die Frage, die der Backlog offengelassen hatte:** Sollen Kopf- und Fußzeile ihre Höhe auch dann
reservieren, wenn nichts darin steht? Die Kopfzeile ist nie leer. Die Fußzeile gibt es nur bei
einem Stapel — und sie reserviert **nicht**. Ein einzelnes Foto ist der häufigere Fall und bekommt
die 4,5 rem als Bildhöhe, auf 1280 × 800 rund 8 % mehr Bild. Der Preis ist, dass die Unterkante
des Bildes bei Stapel und Einzelfoto verschieden hoch sitzt; zwei Öffnungen sieht aber niemand
nebeneinander, und der Schließen-Knopf steht in beiden Fällen an derselben Stelle. Das ist der
Punkt, an dem die Ansicht ruhig wirkt.

Nachgemessen auf 1280 × 800, in beiden Zuständen und für Hoch- wie Querformat: Der Knopf schließt
auf **0 px** mit dem rechten Rand des Inhalts ab, Bild und Text fangen auf **0 px** genau in
derselben Zeile an, und die Blätterknöpfe stehen auf **0 px** mittig unter dem Bild — nicht mittig
im Schirm, was der eigentliche Grund dafür ist, dass die linke Spalte `auto` breit ist und nicht
`1fr`. Auf 1024 × 768 passt der Inhalt ebenfalls vollständig in den Schirm.

## Der schwarze Blitz hinter dem Bild

3. August 2026.

In der Detailansicht war gelegentlich eine schwarze Fläche hinter dem Foto zu sehen. Die Suche nach
der Ursache ging über drei Verdachtsmomente, und die ersten zwei waren falsch:

- **Kein Alphakanal.** Kein einziges Vorschaubild trägt Transparenz — die WebP-Erzeugung wandelt
  vorher um.
- **Kein Seitenverhältnis-Fehler.** Über alle achtzehn Fotos des Beispielbestands nachgemessen
  stimmt das Verhältnis der Bildbox mit dem des Vorschaubilds auf **0 %** überein. `object-fit:
  contain` lässt also nirgends einen Rand frei.

Damit blieb nur eine Erklärung übrig, und sie war die richtige: **`background: #000` auf
`.overlay__image`.** Die Zeile stammte aus der Zeit, bevor das Element sein Seitenverhältnis als
`aspect-ratio` mitbekam — damals konnte die Box breiter oder höher sein als das Bild darin, und der
Rand brauchte eine Farbe. Seitdem entspricht die Box dem Bild genau, und der Hintergrund ist nur
noch in einem einzigen Moment zu sehen: **bevor das Bild gezeichnet ist.** Die Box steht wegen
`aspect-ratio` schon in voller Größe da, das Bild ist noch unterwegs.

Deshalb „gelegentlich": Es traf beim Öffnen und bei jedem Schritt durch einen Stapel, und wie lange,
hing an der Dateigröße. Auf dem Entwicklungsrechner über localhost kaum zu sehen, auf dem Pi mit
einem großen Scan lang genug.

Die Zeile ist ersatzlos entfallen — und damit trat der Fehler ein zweites Mal auf, nur anders
herum. Ohne Hintergrund blieb im Ladezustand der **Schlagschatten um eine leere Fläche** stehen,
und das sieht schlechter aus als das Schwarz vorher: Es wirkt wie ein Bild, das fehlt.

Also die Ursache eine Stufe tiefer angefasst. Das Bild wird jetzt erst gezeichnet, wenn es geladen
ist — `visibility: hidden`, solange nicht. Das nimmt den Schatten mit, während `display: none` den
Platz genommen hätte und die Ansicht beim Blättern gesprungen wäre. Die Bedingung hängt an der
Foto-Kennung, nicht an einem Umschalter: `loadedId === detail.id`. Damit gilt sie beim ersten
Öffnen und bei jedem Schritt durch einen Stapel gleichermaßen, ohne dass irgendwo etwas
zurückgesetzt werden muss.

**Der eine Fallstrick dabei** steht als Kommentar daneben: Liegt das Bild schon im Cache, ist es
unter Umständen fertig, bevor React `onLoad` hängen kann — dann bliebe es für immer unsichtbar.
Deshalb prüft zusätzlich die `ref`-Funktion `node.complete`. Denselben Wert noch einmal zu setzen
ist für React ein Nichtstun, es schleift also nicht.

Nachgemessen über sieben Blätterschritte: kein Foto blieb verborgen, und die Ladeklasse zeichnet
nachweislich nichts, auch keinen Schatten.

*Nachtrag zur Fehlersuche selbst:* Die Meldung lautete „jetzt ist da eine Fläche mit Schatten zu
sehen", mit der Vermutung, die Fläche sei größer als das Bild. Das war sie nicht — nachgemessen
0,03 px Rand auf 366 px Breite. Die Fläche war nicht zu groß, sie war leer. Der Unterschied klingt
klein und ist der ganze Unterschied zwischen der falschen und der richtigen Reparatur.

## Die Sicherung gibt es jetzt auch als eine Datei

3. August 2026.

Sichern ging nur über einen USB-Stick. Für das Museum ist das richtig und bleibt der Hauptweg —
aber es gibt zwei Fälle, in denen es nicht trägt: Es liegt kein Stick bereit, oder man sitzt beim
Entwickeln vor dem Rechner und will den Bestand einfach herunterladen.

**Der Entwurf steht und fällt mit einer Eigenschaft:** Das Archiv ist genau der Ordner, den auch
der Stick bekommt, nur gezippt. Daraus folgt alles Weitere — vor allem, dass die fehlende
Upload-Wiederherstellung keine Lücke ist, sondern eine Unbequemlichkeit: auf einen Stick
entpacken, vorhandene Wiederherstellung benutzen. Es gibt damit **keinen zweiten
Wiederherstellungsweg**, der eigene Fehler haben könnte.

Weil diese Eigenschaft leicht zu zerstören und schwer zu bemerken wäre, hält
`test_entpacktes_archiv_laesst_sich_wiederherstellen` sie fest: Archiv bauen, in ein
Prüf-Laufwerk entpacken, `run_restore` laufen lassen, nachzählen. Bricht der Test, ist der Rückweg
weg — und zwar lautlos.

### Im Strom, nicht im Speicher

Die Frage, die der Backlog offengelassen hatte: Wird das Archiv im Speicher gebaut, auf die
SD-Karte geschrieben oder im Strom erzeugt? Auf einem Pi mit 2 GB RAM scheidet das Erste aus, und
die SD-Karte ist genau das, wovor die Sicherung schützt. Also im Strom.

Das braucht eine Senke für `zipfile`, die nichts aufhebt — `_ArchiveStream`, drei Methoden. Zwei
davon sind offensichtlich (`write` sammelt, `tell` zählt mit, weil `zipfile` daraus seine Offsets
rechnet). Die dritte ist der eigentliche Schalter: **`seekable()` sagt nein**, und daraufhin
arbeitet `zipfile` mit Data Descriptors, statt später in Kopfdaten zurückzuspringen, die längst
ausgeliefert sind. Ein `seek` gibt es deshalb bewusst nicht — mit einem würde die Klasse still
anfangen zu lügen.

`ZIP_STORED` ist dabei keine Sparsamkeit: JPEG und WebP sind komprimiert, ein zweiter Durchgang
kostet den Pi nur Zeit. ZIP64 ist Pflicht, zweitausend Scans gehen ohne Weiteres über vier
Gigabyte.

### Zwei Fallstricke, die erst beim ersten großen Bestand aufgefallen wären

**`proxy_buffering`** steht im nginx auf der Voreinstellung — es hätte den ganzen Strom erst auf
die SD-Karte gesammelt, bevor der Browser ein Byte sieht. Genau der Fallstrick, den bei den Kacheln
schon das `gzip off` daneben abfängt, und genau der, der auf einem Bestand von achtzehn Fotos
nichts tut.

**Ein Browser-Download kann keinen `X-Admin-Token` mitschicken.** Der kurze Weg wäre, den
Sitzungstoken in die Adresse zu hängen; er ist falsch, weil Adressen im Verlauf, in Lesezeichen
und in Proxy-Protokollen landen und dieser Token den ganzen Verwaltungsbereich öffnet. Stattdessen
ein `TicketStore` nach dem Vorbild des `SessionStore`: ein Ticket kauft genau einen Download, wird
beim Einlösen vergessen und ist nach einer Minute wertlos.

### Was die Oberfläche sagen muss

Die Maske hat die Form des Importbereichs übernommen — zwei gleichrangige Kacheln, darunter eine
Fläche an fester Stelle. Der Stick steht links, weil er die bessere Sicherung ist.

Zwei Sätze stehen dabei bewusst auf dem Bildschirm und nicht nur in der Dokumentation. Der erste
ordnet den Weg ein: Das Archiv ist nicht inkrementell, und ein abgebrochener Download ist
wertlos — beides Eigenschaften, die genau die Begründung für „Ordner statt ZIP" waren
([decisions.md](decisions.md), Punkt 11). Der zweite sagt, wie eine solche Datei wieder ins Gerät
kommt; ohne ihn sähe die fehlende Rückrichtung wie ein Fehler aus.

Am echten Bestand nachgemessen: 31 MB in 132 Stücken, entpackt 18 Fotos, 36 Vorschaubilder, eine
lesbare Datenbank ohne WAL daneben — und `is_restorable` sagt ja.

## Der Rückweg führt durch den Eingangsordner

3. August 2026.

Die Sicherung als Datei gab es seit dem Vormittag, der Rückweg nicht — man musste sie auf einen
Stick entpacken. Der Backlog hatte dafür drei Hindernisse notiert, und alle drei hingen am Upload
durch den Browser: `client_max_body_size`, eine zweiphasige Fortschrittsanzeige und der dreifache
Platzbedarf beim Auspacken.

**Der Eingangsordner räumt alle drei ab.** Die Datei liegt schon auf der Platte — kein Upload,
keine nginx-Grenze, keine zweite Anzeige. Und weil direkt in den Arbeitsordner entpackt wird statt
erst daneben, bleibt es beim Dreifachen statt beim Vierfachen; mehr geht nicht, solange das Archiv
seine eigene Quelle ist.

### Die Entscheidung, die den Entwurf prägt

Der Ordner tut bisher etwas **Hinzufügendes und Folgenloses**: Ein Foto zu viel darin ist ein Foto
zu viel. Eine Wiederherstellung **ersetzt den ganzen Bestand**. Beides ohne Rückfrage in denselben
Ordner zu legen, hieße: Eine versehentlich dorthin kopierte Datei tauscht die Sammlung aus, und auf
einem Kiosk fällt das wochenlang niemandem auf.

Deshalb spielt sich nichts von selbst ein. Die Datei wird **erkannt** und im Sicherungsbereich
vorgelegt — dieselbe Rückfrage mit Datum und Anzahl, die der Stick-Weg schon stellt. Die Kachel
„Als eine Datei" bekommt dafür einen zweiten Zustand und wird vorgewählt, sobald etwas wartet.
Darunter steht weiterhin der Download: Sonst wäre der einzige Moment, in dem sich der *jetzige*
Bestand nicht mehr sichern lässt, ausgerechnet der unmittelbar vor dem Überschreiben.

### Was der Plan nicht wusste

**Ohne eine Zeile im Watcher tut nichts davon etwas.** Das Archiv wäre in `import_file` gelaufen,
dort als „Kein lesbares Bild" abgewiesen worden und in `_problem/` gelandet — bevor es überhaupt
jemand hätte bestätigen können. `_candidates()` übergeht es jetzt. Die Gegenprobe steht: Ohne die
Zeile ist `test_zip_im_eingang_landet_nicht_im_problemordner` rot.

**Ein Name kollidierte.** `importer._move_aside` sollte öffentlich werden, damit die Sicherung das
eingespielte Archiv nach `_erledigt/` räumen kann. Aber `import_file` hat einen **Parameter**
namens `move_aside` — die Funktion wäre in seinem Geltungsbereich verdeckt gewesen, und die Aufrufe
darin hätten den Wahrheitswert aufzurufen versucht. Stattdessen heißt die öffentliche Variante
`move_to_done` und ist zugleich enger: Sie kennt nur ein Ziel.

**Halb kopierte Dateien brauchen keine Sonderbehandlung.** Der Watcher wartet sonst darauf, dass
eine Dateigröße sich nicht mehr ändert. Für ein Archiv genügt der Versuch, es zu öffnen: Ohne sein
Zentralverzeichnis am Ende ist ein ZIP für `zipfile` schlicht kein ZIP.

Am echten Bestand geprüft: 18 Fotos gesichert, fünf Dateien gelöscht, eingespielt — 18 wieder da,
das Archiv in `_erledigt/`, der alte Stand in `vorher-2026-08-03-2341/`, und die Abschlussmeldung
nennt beide.

## Datieren in der Detailansicht

4. August 2026.

Wer ein undatiertes Foto groß ansah, las dort „Jahr unbekannt" und hatte keine Möglichkeit, es zu
sagen — er hätte schließen und hoffen müssen, dass der Beitragsbereich ihm zufällig dasselbe Foto
vorlegt. Jetzt steht die Auswahl in der Ansicht selbst.

**Mit Knöpfen, nicht mit einem Zahlenfeld.** Die ganze Besucheransicht hat genau ein Eingabefeld,
und ob das Gerät je eine Tastatur bekommt, ist im Backlog offen — ein Zahlenfeld wäre dort ein
Bedienelement, das nichts annimmt. Es ist dasselbe zweistufige Verfahren wie im Beitragsbereich,
und deshalb ist es jetzt ein Bauteil: `DatePicker` zeigt Jahrzehnt und Jahr, `DateTask` hängt den
Beitrag der laufenden Frage daran, die Detailansicht den zum Foto, das gerade zu sehen ist.

### Was der Weg absichtlich nicht tut

`submitDateFor` geht **nicht** durch `contribute()`, und das sind zwei bewusste Auslassungen:

- **Kein Dank.** Die Rückmeldung ist die Ansicht selbst — aus „Jahr unbekannt" wird „1963", und die
  Knöpfe verschwinden, an genau der Stelle, auf die geschaut wird. Das ist der Fall, den der
  Backlog unter *„Die Dankmeldung: brauchen wir sie, und stimmt sie immer?"* als den beschreibt, in
  dem der Satz überflüssig ist: Wo die Ansicht sich sichtbar ändert, sagt sie es schon.
- **Kein Kartenfokus.** Die Karte liegt unter der Detailansicht. Sie irgendwohin zu fahren, sähe
  niemand.

### Die Regel, die still gebrochen wäre

**Der Beitragsbereich zieht nur weiter, wenn er dasselbe Foto nach dem Jahr fragte.** Ohne das legt
er es gleich noch einmal vor, der Besucher antwortet ein zweites Mal — und bekommt „Dieses Foto hat
inzwischen schon eine Angabe bekommen". Eine Meldung, die klingt, als sei jemand anders schneller
gewesen, obwohl er selbst es war.

Fragte er nach dem **Ort**, bleibt er stehen: Den braucht das Foto unverändert. Beide Fälle sind
im Store getestet und am laufenden Gerät nachgestellt — bei der Ortsfrage blieb dasselbe Foto
stehen, bei der Jahresfrage wechselte die Ansicht auf „Wo ist das?".

### Reichweite

Größer als erwartet: Undatierte Fotos stehen sehr wohl auf der Karte, weil die Kartenabfrage den
Zeitfilter weglässt, solange der Schieber den ganzen Bestand umspannt. Erst wer den Zeitraum
einengt, blendet sie aus — richtig so. Die Auswahl ist damit über den Marker *und* über „Foto groß
anzeigen" erreichbar.

## Der Erstbestand: 929 Fotos aus einem sortierten Archiv

`501c844` … `a9fccd3` · 4.–5. August 2026.

Der Anlass war ein Ordner mit 929 Bildern, den das Museum vorbereitet hatte — und die Frage, ob
daraus ein Programm entsteht, das einmal läuft, oder ob der Import selbst es lernt. Es wurde das
Zweite. Was das kostete und was dabei anders kam als gedacht, steht hier.

### Was der Ordner schon wusste

```
Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
```

Straße, Hausnummer, Hausname — dreimal Auskunft, in einem Pfad. 801 der 929 Fotos lagen so, 124
nur unter einer Straße, 4 ganz oben. Diese Namen zu verwerfen hätte geheißen: Ehrenamtliche tippen
929 Adressen ab, die schon da sind, und Besucher werden nach dem Ort von Fotos gefragt, deren
Adresse danebensteht.

### Zwei Funde vor der ersten Zeile Code

Bevor irgendetwas gebaut wurde, wurde der Ordner vermessen. Zwei Ergebnisse haben den Entwurf
danach getragen:

**116 Fotos tragen ein Scandatum, 91 davon aus einem einzigen Lauf von 2015.** Sie unbesehen zu
datieren hätte 91 historische Ortsbilder auf der Zeitleiste bei 2015 abgelegt — und weil sie damit
als datiert gelten, wären sie nie mehr jemandem vorgelegt worden. Genau der Fehler, gegen den
`exif_date_max_year` gebaut wurde. Der Fund war aber zugleich die Widerlegung dieser Regel in
ihrer bisherigen Form: 256 Fotos sind **echte Kameraaufnahmen von 2010 bis 2024**, und die
Jahresgrenze hätte sie alle mit verworfen. Die Regel musste also nicht schärfer werden, sondern
zweistufig: erst das Gerät, das die Datei nennt, und die Jahresgrenze nur dort, wo keines
dasteht. Geprüft wurde das an den Bildern selbst — von 256 Kamerafotos sind 234 farbige Aufnahmen
der Häuser, wie sie heute stehen, und die 22 fast graustufigen zeigen trübes Wetter, Schnee und
eine dunkle Scheune. Keine Reprofotos alter Abzüge, also trägt die Umkehrung.

**In 82 Dateien steht als Fotograf wörtlich „unbekannt".** Ein Nichtwert, der ein Feld füllt. Das
ist dieselbe Falle wie „OLYMPUS DIGITAL CAMERA" ein Feld weiter, und die Antwort dieselbe: Was
nichts sagt, gilt als leer.

### Drei Fehler, die erst der echte Lauf zeigte

Der Probelauf auf eine Straße und danach der volle Lauf haben drei Dinge zutage gefördert, die
kein Testentwurf vorweggenommen hätte:

1. **`UNIQUE constraint failed: tags.name`** — mitten im Import. Die Sitzung läuft mit
   `autoflush=False`; ein Schlagwort, das die Pfad-Schicht für ein Foto anlegte, war für die
   Abfrage des nächsten noch unsichtbar. Zwei Fotos an derselben Adresse legten es also zweimal
   an. Seitdem schreibt `add_tags` ein neues Schlagwort sofort heraus — und zwar **nach** dem
   Flush des Fotos, denn davor ist es noch nicht in der Sitzung und die Verknüpfung ginge
   verloren.
2. **Der Ordner „2" wurde zur Straße „Kolonie Autal 2".** Damit das Archiv auch kürzen darf
   („Wiesengrund" für „Im Wiesengrund"), sucht die Straßenerkennung notfalls wortweise — und die
   Hausnummer 2 unter „Achter de Möhl" fand eindeutig eine Straße, die den Namen zufällig auf
   eine Zahl enden lässt. Zwei Fotos lagen danach am anderen Ende des Dorfes. Seitdem gilt: Jedes
   Wort muss einen Buchstaben enthalten. Aufgefallen ist es nur, weil die Zahlen zweier Läufe
   verglichen wurden — 381 hausgenaue Fotos beim ersten, 379 beim zweiten.
3. **Der Titel war manchmal ein ganzer Absatz.** Bis zu 223 Zeichen, mit Zeilenumbrüchen: Wer das
   Archiv pflegte, schrieb die Bildunterschrift dorthin, wo der Cursor stand. Als Überschrift ist
   das eine Textwand. Weggeworfen gehört sie trotzdem nicht — sie wandert in die Beschreibung, und
   den Titel liefert der Ordner.

Dazu kamen zwei Kleinigkeiten mit demselben Muster: `x-default`, ein Sprachmarker aus XMP, stand
als Titel; und „August MÃ¶ller" ist „August Möller", zweimal durch die falsche Kodierung gedreht.
Beides passiert in fremden Programmen, lange bevor eine Datei hier ankommt — der Import ist die
letzte Stelle, an der es noch auffallen kann.

### Was herauskam

929 aufgenommen, keine einzige Dublette, zwei `Thumbs.db` abgewiesen. 852 Fotos verortet, davon
381 hausgenau; 256 datiert; 922 mit Titel, alle mit Bildnachweis, 926 mit Herkunftsangabe. 77
Fotos ohne Ort und 673 ohne Jahr — das ist kein Rest, sondern der Vorrat des „Hilf mit"-Bereichs.

Der Bestand liegt als ZIP-Sicherung außerhalb des Repos (1,4 GB, 2791 Einträge, geprüft), und die
Entwicklung läuft danach wieder auf den 18 Fotos des Beispielbestands weiter.

### Was die Entscheidung eigentlich war

Nicht die Regeln, sondern ihre **Trennung in zwei Schichten**: Metadaten für alle vier
Importwege, Pfad nur für die drei, die einen haben. Damit bekam das Hochladen im Browser die
Metadaten-Regeln geschenkt, ohne die Pfad-Regeln zu erben — und der USB-Stick verhält sich seither
wie der Eingangsordner, weil er dieselbe Schicht durchläuft. Wäre es ein einmaliges Skript
geworden, hätte das nächste Archiv wieder eines gebraucht.

## Sprach- und Namenskonsistenz

`cc0b275` … `43ab391` · 5. August 2026.

Die Sprachregelung stand seit Stufe 7.5 in CLAUDE.md und galt als geklärt. Der Backlog-Punkt dazu
forderte etwas anderes: **nachsehen statt annehmen.** Die Messung über alle 108 Quelldateien war
die eigentliche Arbeit — was danach zu tun war, ergab sich fast von selbst.

### Vier Regeln waren lückenlos eingehalten, ohne dass es jemand geprüft hatte

Kein deutscher Oberflächentext stand fest im TSX, kein deutscher Name in einem API-Pfad, einem
Query-Parameter oder einem JSON-Feld, die CLI-Ausgaben waren durchweg deutsch — und **90 von 90
Commit-Nachrichten trugen keinen einzigen Umlaut**. Genau das hatte der Backlog-Punkt verlangt:
„ein Durchgang über `git log` sollte es bestätigen statt es anzunehmen."

Zwei Regeln waren es nicht: **338 deutsche Kommentare in 52 Produktivcode-Dateien** neben 687
englischen, teils in derselben Datei, und neun deutsche Dateinamen. Nachgezogen statt aufgeweicht
— bei den Kommentaren war das zugleich der billigere Weg, andersherum wären 687 zu übersetzen
gewesen.

### Die Regel widersprach sich selbst

Sie verbot Umlaute im Python-Quelltext und gab zwei Absätze weiter ``so that "muhlenweg" finds the
"Mühlenweg"`` als *erwünschtes* Beispiel — mit Umlaut. Alle fünfzehn gefundenen Stellen waren von
dieser Art: zitierte Beispiele oder Datenwerte. `"März"` in der Monatsliste von `services/dates.py`
hat ohnehin keinen Ersatz; ohne Umlaut zeigte der Kiosk „März".

Daraus wurde die Präzisierung: **In deutscher Prosa im Quelltext werden Umlaute umschrieben, in
Zitaten und Datenwerten bleiben sie.** Das ist keine Ausnahme von der Regel, sondern ihre
Ausformulierung — Prosa ist etwas anderes als der Gegenstand, über den sie spricht.

### Die Tests waren längst eine eigene, stimmige Welt

326 deutsche gegen 10 englische Kommentare. Die Regel nannte als Ausnahme nur die *Testnamen* und
beschrieb damit die Hälfte der Wirklichkeit — dabei ist ein Test-Docstring die Fortsetzung des
Testnamens und trägt dasselbe Warum („Das EXIF sagt 2019, das Foto ist historisch"). Seitdem steht
in der Regel, was ohnehin galt: **Testdateien sind ganz deutsch.** Die zehn englischen Ausreißer
in `conftest.py` zogen nach.

### Zwei Umbenennungen lösten die Sinnfrage mit

Der Backlog-Punkt hatte nicht nur nach der Sprache gefragt, sondern danach, ob ein Dateiname sagt,
was drinsteht. `admin/jahr.ts` enthielt die Jahrzehnt-Regel und heißt jetzt `yearInput.ts`, wie das
`YearField`, dem es dient. `admin/paging.ts` hieß nur so, weil `pager.ts` auf macOS mit `Pager.tsx`
kollidiert wäre; als `pagination.ts` kollidiert nichts mehr.

### Das Prüfskript meldete einen Verstoß, der keiner war

`tools/language_check.py` zählt deutsche und englische Kommentare je Datei. Es fand `config.py`
schuldig — wegen ``KIEKMAP_IMPORT_PROVENANCE="Online-Archiv des Museums, Verzeichnis 01 Orte/"``,
einem Einstellungswert. Zu „beheben" wäre das nur durch Fälschen des Beispiels gewesen. Das Skript
streicht Zitiertes deshalb, bevor es zählt; die Regel oben ist dieselbe Einsicht in Worten.

**Bewusst kein Test.** Die Spracherkennung ist eine Wortlisten-Heuristik, und ein Test, der bei
einem Fachbegriff falsch anschlägt, wird binnen eines Monats ausgeschaltet — danach ist gar nichts
mehr bewacht.

### Und die erste Gegenprobe griff nicht

Um zu prüfen, ob das Skript überhaupt etwas findet, wurde ein deutscher Satz eingeschmuggelt — und
das Skript schwieg. Nicht weil es blind war: Der Satz hing vorn in einem langen englischen
Docstring, dessen übrige Wörter ihn überstimmten. Die Probe war falsch gebaut, nicht das Werkzeug.
Als eigenständiger Kommentar gesetzt, fand es ihn sofort — und in der Gegenrichtung auch einen
englischen Kommentar in einer Testdatei, beide mit Exitcode 1.

Das ist die Lehre, die über diesen Tag hinausreicht: **Eine Gegenprobe, die nicht anschlägt,
beweist erst einmal nichts über den Code — sie stellt eine Frage an die Probe.**

## Zwei Blocker vor der Veröffentlichung

`4e4d393` … `4216e06` · 5. August 2026.

Der Backlog-Punkt zur Veröffentlichung nannte zwei Dinge, die vorher zu klären seien. Beide waren
schnell geklärt — und beide anders, als die Frage gestellt war.

### Das Wappen: keine Lizenzfrage

Die Vermutung war „urheberrechtlich vermutlich heikel, also nachsehen und einen Hinweis
aufnehmen". Die Wikipedia-Seite zum Holmer Wappen trägt aber **zwei** Bausteine, und nur der
erste ist die gute Nachricht:

> „Nach § 5 Abs. 1 UrhG (Deutschland) sind amtliche Werke wie Wappen gemeinfrei."

> „Wappen sind allgemein unabhängig von ihrem urheberrechtlichen Status in ihrer Nutzung
> gesetzlich beschränkt."

**Urheberrechtlich ist nichts zu klären. Das Hindernis ist das Wappenrecht** — ein Hoheitszeichen,
dessen Führung die Gemeinde regelt. Daraus folgt der Satz, an dem die ursprüngliche Absicht
zerbrach: **Ein Hinweis heilt das nicht.** Bei einer Lizenz hilft Namensnennung, man nennt den
Urheber und darf. Hier geht es um Erlaubnis, und die ist durch keine Fußnote zu ersetzen. Dazu
kommt, dass die Erlaubnis für den eigenen Kiosk im eigenen Ort etwas anderes ist als die
Erlaubnis, das Zeichen an jeden weiterzugeben, der ein Repo klont.

Der Tausch selbst kostete eine Datei und keine Zeile Logik — weil im Code nirgends steht, was auf
dem Bild zu sehen ist. Dieselbe Eigenschaft, die ein zweites Museum ohne Fork auskommen lässt, hat
hier ein Rechtsproblem auf einen Dateitausch reduziert. Begründung: [decisions.md](decisions.md),
Punkt 21.

### Der Rewrite: erst „später", nach einer Prüfung „sofort"

Der Plan sah den Schnitt durch die Historie für den Tag der Veröffentlichung vor — „heute
ausgeführt zerbräche er jeden vorhandenen Klon". Dann kam die Rückfrage, ob das jemand von Hand
tun müsse, und mit ihr der Blick auf etwas, das vorher niemand nachgesehen hatte: **Das Repo hat
keinen Remote, einen Branch, eine Arbeitskopie.** Es war nie irgendwohin gepusht. Es gab also
keinen fremden Klon, der zerbrechen konnte — und der Preis stieg mit jeder Woche.

Der Preis war die Dokumentation, und er war messbar: **83 der 97 Kurz-Hashes änderten sich, 61
Zitate in drei Dateien wurden ungültig**, allein `history.de.md` nennt 71 Commits. Genau diese
Verweise machen die Historie hier wertvoll; sie aufzugeben wäre der eigentliche Verlust gewesen.
Sie sind mitgezogen: `filter-branch` lässt die alte Historie unter `refs/original/` stehen, alt und
neu ließen sich Position für Position paaren, gegengeprüft an den Betreffzeilen — 97 von 97
paarweise gleich.

**Die Abnahme war nicht der grüne Durchlauf**, sondern zweierlei: dass jeder der 76 zitierten
Hashes `git cat-file` besteht (er tut es), und dass das echte Wappen in keinem Blob der Historie
mehr auftaucht (es tut es nicht — geprüft über seinen SHA-256, nicht über den Dateinamen).

### Der Beispielbestand: die Lücken sind der Wert, nicht die Schönheit

Gegen erzeugte Bilder sprach der Einwand aus dem Backlog: „sieht aber nie aus wie ein Museum". Das
stimmt — und trifft nicht, worum es geht. Der Wert dieses Bestands sind seine **Lücken**: drei
Fotos ohne Jahr, zwei ohne Ort, eines ohne beides, zwei gelöschte, acht Besucherbeiträge davon
zwei zurückgenommene. Ohne sie prüft der Bestand die Hälfte des Programms nicht. Achtzehn
gezeichnete Ansichten aus `tools/build_seed.py` tun das genauso gut wie echte Aufnahmen, kosten
1,1 statt 24 MB und stellen nie wieder eine Rechtsfrage. Der Generator zählt die Lücken nach jedem
Lauf nach und bricht ab, wenn eine fehlt.

**Echt bleiben nur Straßennamen und Koordinaten**, und das ist keine Nachlässigkeit: Die Punkte
müssen in der `bbox` liegen, sonst zeigt die Karte nichts, und `place_name` muss zum Ortsindex
passen, sonst findet die Ortssuche nichts — und die ist das Herzstück der Vorführung. Ein
Personenbezug entstünde erst durch die Bindung von Namen an Adressen, und die ist erfunden.

### Drei Dinge, die dabei schiefgingen

- **Der Generator löschte die echten Museumsfotos**, bevor sie beiseitegelegt waren. Sie waren
  vollständig zu retten, weil `data/` sie noch trug und `seed.export` sie an einen beliebigen Ort
  schreiben kann — aber gerettet werden musste, was gar nicht erst hätte gefährdet sein dürfen.
- **`seed.json` bekam zunächst keinen SHA-256.** Der ist der Änderungsmelder von `seed.load`; ohne
  ihn warnte jedes `make seed` achtzehnmal. Eine Warnung, die immer kommt, ist eine, die niemand
  mehr liest.
- **`language_check.py` fand fünf deutsche Kommentare im neuen Generator** — im Werkzeug, das am
  Tag zuvor genau dafür gebaut worden war. Es hat sich sofort bezahlt gemacht.

Dazu eine Kleinigkeit mit derselben Lehre wie beim SHA-256: Der Zeitstempel in `seed.json` kam aus
der Uhr und war damit das eine Feld, das jeder Neubau änderte. Jetzt steht dort der Tag, an dem
der Bestand entworfen wurde — zweimal bauen erzeugt zweimal dasselbe.

## Der Backlog bekommt eine Ordnung — und liefert zwei Fehler ab

8. August 2026. Punkt 24 des Backlogs, „Backlog ordnen und klassifizieren", war der letzte Eintrag
der Datei und beschrieb ihr eigenes Problem: Sie mischte auf 405 Zeilen Fehler, Aufgaben,
Entscheidungsfragen und Ideen in einer Gliederung, die nur nach Bereich sortierte, und kein Punkt
war zitierbar, weil es ihn nur unter seiner Überschrift gab.

Was daraus wurde, steht in [decisions.md](decisions.md), Punkt 22: vier Arten, zwei Achsen, eine
Nummer je Punkt, alles in einer Übersichtstabelle am Dateianfang. Erwartet war Aufräumarbeit.
Herausgekommen sind zwei Dinge, die die Datei vorher nicht gesagt hatte.

### Zwei Fehler in einer Datei, die sich für fehlerfrei hielt

Über der Gliederung stand der Satz „Zurzeit ist kein Fehler offen — alles hier ist Ausbau." Beim
Durchgehen der 24 Einträge mit der Frage *tut das, was dasteht, nicht was es zusagt?* blieben zwei
hängen:

- **Punkt 5, die Dankmeldung.** Wer ein Foto **ohne Ort** datiert, liest „Danke! Das Foto ist jetzt
  auf der Zeitleiste" — und sieht nichts, weil `rangeForPhoto()` für ein Foto ohne Koordinaten
  bewusst `null` liefert. Eine falsche Zusage an einen Besucher, und der Eintrag nennt den Fall
  selbst den Regelfall im Museumsbestand.
- **Punkt 10, die Detailansicht.** `--overlay-aside` steht fest auf 24 rem; auf einem 1024er Panel
  bleiben dem Foto dadurch 466 px.

Beide standen seit Wochen ausführlich beschrieben in der Datei — als Gestaltungsfragen. Die Sache
war jedes Mal richtig aufgeschrieben und falsch einsortiert. **Eine Ordnung ist nicht nur Ordnung;
sie stellt eine Frage, die vorher niemand gestellt hat.** Das war der überraschendste Ertrag
dieser Aufräumarbeit, und er kostete nichts weiter als eine Spalte.

### Die Dringlichkeit hat das Projekt umsortiert

Die zweite Achse — dringend, nicht nur wichtig — war als Feinheit gedacht und hat die Reihenfolge
des Projekts gedreht. „Abnahme auf dem ersten Pi" war der Punkt, der überall als der wichtigste
offene genannt wurde, in dieser Datei, in der `CLAUDE.md`, in der `index.md`. Wichtig ist er
geblieben. **Dringend ist er nicht — es gibt kein Gerät.** Dasselbe gilt für alles daran Hängende:
die vier Prüfungen, der Containerbetrieb, die Wiederherstellung, das Read-Only-Overlay.

Dringend ist stattdessen der Weg, der ohne Gerät auskommt: das System dem Museumsteam über einen
Webserver zur Verfügung stellen. Daran hängt der Bedienbarkeitstest mit einer ehrenamtlichen
Person — der aussagekräftigste Test des Projekts, bisher aufgeschoben bis zum fertigen Pi, und
plötzlich heute machbar. Was er zutage fördert, ist danach teurer zu ändern.

Aus vier gerätegebundenen Punkten weit oben wurde so ein dringendes Paar in einem Bereich, in dem
vorher gar nichts dringend war. Es hat sich nichts am Projekt geändert, nur die Frage, die man an
die Liste stellt.

### Was dabei noch auffiel

Punkt 7 hieß „Kopfzeile des Zeitschiebers aufräumen" und war der kleinste Eintrag der
Besucherseite. Er heißt jetzt **„Zeitschieber verfeinern"** und trägt zwei weitere Dinge: dass die
Histogrammbalken linear gegen das höchste Jahrzehnt skalieren und deshalb bei großem Bestand alles
außer dem Schwerpunkt auf denselben Sockel drücken — die Beispieldaten mit ihren achtzehn Fotos
konnten das nie zeigen — und den Wunsch nach einem dritten Anfasser in der Mitte, mit dem sich der
gewählte Zeitraum als Ganzes verschieben lässt.

Punkt 24 ist mit diesem Commit erledigt und seine Nummer damit vergriffen; der nächste neue Punkt
bekommt die 25.

## Der Dank, der nichts einlöste

8. August 2026. Der erste Punkt, den die neue Einordnung als Fehler ausgewiesen hatte, war zugleich
der billigste zu beheben — und derjenige, bei dem die naheliegende Reparatur die schlechtere
gewesen wäre.

Der Befund stand seit Wochen im Backlog, nur unter der falschen Überschrift: Nach jedem Beitrag
stand „Danke! Das Foto ist jetzt auf der Zeitleiste." Für ein Foto **ohne Ort** ist das eine Zusage,
die die Ansicht nicht einlösen kann. `showPhoto()` steigt ohne Koordinaten sofort aus, die Karte
bleibt stehen, der Schieber springt nicht — und der Besucher liest einen Satz und sieht nichts. Bei
673 Fotos ohne Jahr und 77 ohne Ort trifft das nicht den Rand des Bestands, sondern seine Mitte.

### Die Reparatur, die nicht genommen wurde

Der Backlog schlug selbst einen ehrlicheren Satz vor: „Sobald jemand weiß, wo das war, erscheint es
auf der Karte." Damit wäre die Meldung wahr gewesen — und der Besucher stünde weiterhin in einer
Sackgasse, unmittelbar nachdem er gezeigt hat, dass er dieses Foto kennt. **Ein wahrer Satz war
nicht dasselbe wie eine gelöste Lage.**

Genommen wurde deshalb die Kette: Wo dem Foto noch etwas fehlt, fragt der Dank danach — „Danke! Und
wissen Sie auch, wo das war?" — und die nächste Frage gilt **demselben** Foto. Der Fall „Zusage ins
Leere" kann damit nicht mehr entstehen; wo nichts zu zeigen ist, steht die nächste Frage.

Das war keine neue Idee, sondern eine vorhandene zu Ende gedacht. „Weiß ich nicht" wechselt seit
Stufe 6 *die Frage* und nicht nur das Bild, weil wer den Ort nicht kennt, das Jahrzehnt sehr wohl
kennen kann. Nach einem geglückten Beitrag wechselte die Frage auch schon — nur sprang das Foto
dabei weg, ausgerechnet im ergiebigsten Moment, den der Bereich je bekommt.

### Warum es so billig war

Kein Backend, keine API-Änderung, kein neuer Zustand. Der Grund liegt in einer Entscheidung von
früher: Ein Beitrag gibt das **aktualisierte Foto** zurück, statt den Client raten zu lassen — und
`PhotoDetail` trägt `needs_location` und `needs_date` mit. Der Store wusste also längst, was dem
Foto noch fehlt; es hatte nur nie jemand gefragt. Die Zähler kommen weiter aus dem regulären Abruf,
ersetzt wird allein das Foto, damit „Noch 2 Fotos ohne Ort" richtig bleibt.

Der Dank blieb, samt seiner 2,2 Sekunden. Er ist zugleich der Zeitgeber für den Kartenfokus, und
als Übergang zwischen zwei Fragen ist die Pause für die Zielgruppe eher Gewinn.

### Die Abnahme war der Gegenversuch

Fünf Tests, alle grün — das sagt für sich genommen wenig. Aussagekräftig war der Gegenversuch: die
Kette im Store abgeschaltet und noch einmal laufen lassen. Drei der fünf fielen um, darunter der
eine, der den Fehler beschreibt („dankt ohne Versprechen, solange der Ort fehlt"); die zwei, die
den unveränderten Fall prüfen, blieben grün. Genau so sollte es aussehen.

Dazu der Durchgang am laufenden Kiosk, weil sich der Fehler nur dort zeigte: ein Foto **mit** Ort
datiert (Karte fährt hin, „auf der Zeitleiste" stimmt), dann das eine Foto des Beispielbestands
**ohne** Ort und ohne Jahr — dafür ist es da — datiert und gesehen, wie der Dank nach dem Ort
fragt und dasselbe Bild mit der Ortsfrage zurückkommt, jetzt mit „1920er" neben dem Titel. Verortet
man es dann, endet die Kette und ein neues Foto kommt.

Punkt 5 ist damit erledigt; seine Nummer bleibt vergriffen.

## Die Tastaturfrage, beantwortet ohne Tastatur

8. August 2026. Punkt 6 des Backlogs war seit Stufe 6 offen und hieß „was ist ohne sie erreichbar,
und wollen wir eine?". Er beschrieb sorgfältig drei Wege — echte Tastatur, Bildschirmtastatur,
gar keine — und übersah, dass es einen vierten gibt.

Denn der Punkt trug seine eigene Auflösung schon mit: **Die ganze Besucheransicht hat genau ein
Eingabefeld.** Alles andere ist Knopf. Wer diese eine Stelle in Knöpfe verwandelt, muss die Frage
nach der Tastatur nicht beantworten, sondern hat sie nicht mehr.

### Erst messen, dann entwerfen

Die Idee stand schnell: die Straße erfragen wie das Jahr, erst grob, dann genau. Ob das in zwei
oder drei Fragen mit je zehn Knöpfen aufgeht, ist aber keine Geschmacksfrage — also wurde der
echte Ortsindex ausgezählt, bevor eine Zeile Code entstand:

| | |
|---|---|
| Straßen im Index | **486**, bis 7 km hinaus, mit den Nachbardörfern |
| davon im 2-km-Umkreis | **73** |
| Ballungen bei 700 m Nachbarschaft | **16** — davon eine mit 379 Straßen |

Die dritte Zeile hat eine Idee erledigt, die vorher plausibel klang: nach **Gegend** gliedern,
Ortskern und Elbufer und Neubaugebiet. Das Straßennetz hängt zusammen; die Dörfer trennen sich
geografisch nicht, sie müssten von Hand gezogen werden — je Ort neu, was genau die Eigenschaft
zerstört hätte, die ein zweites Museum ohne Fork auskommen lässt.

Die zweite Zeile entschied den Zuschnitt. **Alle 486 kosten eine vierte Frage** — „Am …" allein
hat 29 Einträge, „Sch …" 18. Die ortsnächsten achtzig dagegen fallen in zehn Buchstabengruppen,
von denen sieben direkt zur Straßenliste führen.

### Was der laufende Kiosk zeigte

```
A · B–D · E · F–G · H · I · K–L · M–R · S · T–Z
  H  →  Ha · He · Hinterm Hof · Ho
  A  →  Achter de Möhl · Ahrensbergweg · Al · Am · An
```

Zwei Dinge daran waren nicht geplant und ergaben sich aus den Daten. **Gruppen mit genau einer
Straße zeigen deren Namen** statt eines Kürzels — ein Knopf „Hi", der zu einem einzigen
„Hinterm Hof" führt, wäre ein Schritt für nichts. Und die Gruppen mussten **nach den Namen**
schneiden statt nach fester Tiefe: Die vierzehn Straßen hinter dem A kommen erst nach vier Zeichen
auseinander, weil dreizehn davon mit „Am " oder „An " anfangen.

Der erste Entwurf des Verfahrens verfeinerte, bis genügend Gruppen zusammenkamen. Das teilte zu
fein — ein Testfall mit drei O-Straßen zerlegte sie in „Olm" und „Ost", statt beide unter O zu
lassen. Die Regel heißt seitdem umgekehrt: **den gröbsten Schnitt nehmen, der überhaupt trennt.**

### Zwei Fehler in einem Nachmittag

- **Die Blattebene zeigte eine einzige Straße.** Im JSX lief die Blattebene noch über die
  *Gruppen* statt über die Straßen darin — bei zehn Straßen wäre eine erschienen. Beim Lesen des
  eigenen Codes aufgefallen, vor dem ersten Aufruf.
- **Gleich weite Straßen wurden willkürlich ausgewählt.** Zwei Straßen können denselben Punkt
  haben; welche von beiden es dann in die achtzig schafft, hing an der Reihenfolge, in der SQLite
  die Zeilen herausgab. Ein Test, dessen Erwartung ich für falsch hielt, war in Wahrheit der
  Hinweis darauf. Der Name entscheidet seitdem den Gleichstand.

Die Abnahme am Ende war ein einziger Ausdruck im laufenden Kiosk: `felder: 0`. Die Besucheransicht
hat kein Eingabefeld mehr.

Was von Punkt 6 bleibt, ist der Verwaltungsteil — dreizehn Eingabefelder in sieben Dateien, die
Eingabefelder bleiben sollen. Er steht jetzt als eigener Punkt 24 im Backlog, und die Frage lautet
dort nicht mehr *ob* eine Tastatur, sondern *welche und wann*.

## Was der Erstbestand über den Zeitschieber verriet

9. August 2026. Punkt 7 des Backlogs hieß „Zeitschieber verfeinern" und bündelte drei Dinge: die
Kopfzeile solle weg, die Mengenanzeige stimme nicht, und ein dritter Anfasser fehle. Eines davon
ist entschieden statt umgesetzt — **die Kopfzeile bleibt**. Die beiden anderen sind gebaut.

### Erst messen

Der Bestand war frisch eingespielt, und das war der Unterschied. Die Anzeige an achtzehn erfundenen
Beispielfotos zu beurteilen hätte nichts gebracht; an 929 echten fiel sofort auf, was fehlt:

| | |
|---|---|
| Fotos | 929, davon **673 ohne Jahr** |
| datiert | 256 — ausnahmslos taggenau, aus dem Kamera-EXIF |
| Jahrzehnte | **zwei**: 2010er mit 245, 2020er mit 11 |
| Jahre | 2010:47 · 2011:7 · 2013:2 · **2014:118** · 2016:7 · 2017:25 · 2018:30 · 2019:9 · 2020:1 · 2024:10 |

Zwei Balken, einer voll, einer auf dem Sockel. Und die Zeile darunter zeigt, was dabei verloren
ging: 2014 ist der Ausreißer dieses Bestands, 2012 und 2015 sind leer, und beides war auf der
Leiste nicht zu sehen.

### Die Regel, die dabei entstand

Die naheliegende Antwort — „dann eben Jahresbalken" — wäre eine Falle gewesen, und zwar eine, die
erst in einem Jahr zuschnappt. Ein auf „1920er" datiertes Foto trägt `date_from = 1920-01-01`;
sobald das Museum historische Fotos datiert, türmten sich zehn Jahrgänge auf dem Balken 1920. Das
sähe nicht nach Fehler aus, sondern nach Befund.

Also **nie feiner als die gröbste Datierung im Bestand**, dazu eine Breite, die in dreißig Balken
passt. Heute ergibt das Jahresbalken, morgen Jahrzehnte — und der Umschwung kommt genau in dem
Moment, in dem er muss. Begründung in [decisions.md](decisions.md), Punkt 25.

### Zwei Fehler, die nur der laufende Kiosk zeigte

Beide Tests waren grün, als sie auftraten.

- **Der letzte Balken lief aus der Bahn.** Mit der auf die Bündelbreite gerundeten Achse endet
  diese auf 2024 — und der Balken *für* 2024 begann damit bei 100 % und stand daneben. Die Achse
  muss über das letzte Jahr hinausreichen, damit der letzte Balken darauf Platz hat. Denselben
  Fehler hatte der alte Code auch schon, nur brauchte er eine Aufnahme im letzten Jahrzehnt der
  Achse, um sichtbar zu werden.
- **Der mittlere Griff bewegte nichts.** `onPointerMove` hing am Griff *und* an der Bahn darunter,
  und weil Zeigerereignisse aufsteigen, lief er zweimal je Bewegung. Für die beiden Enden war das
  folgenlos — denselben Anfasser zweimal an dieselbe Stelle zu setzen ändert nichts. Das
  Verschieben des ganzen Zeitraums aber rechnet mit einer Differenz, und der zweite Aufruf sah
  noch den alten Zustand und legte ihn zurück. Der Griff ließ sich anfassen, färbte sich, und der
  Zeitraum stand still. **Ein Fehler, den keine reine Funktion hätte zeigen können**: Die
  Rechnung war richtig, sie lief nur zweimal.

Die Bewegung selbst hat einen eigenen Test bekommen, weil sie an einer Stelle still falsch wird:
Am Rand der Achse darf der Zeitraum nicht *schrumpfen*. Begrenzt wird deshalb die Verschiebung, nie
die Enden einzeln — am Gerät nachgefahren, von 2014–2018 bis 2021–2025 und zurück auf 2010–2014,
die Spanne blieb bei vier Jahren.

## Der Durchgang über den Backlog

9. August 2026. Zwei Tage nachdem der Backlog seine Ordnung bekommen hatte, kamen zwölf neue
Punkte hinzu (`546a40c`) — und damit war zu prüfen, ob die Liste noch stimmt. Vier Fragen an jeden
der siebenunddreißig Einträge: Überschneidet er sich mit einem anderen? Will das noch jemand?
Stimmt seine Einordnung? Und, die ergiebigste: **widerspricht sein Text dem, was inzwischen gebaut
ist?**

Die letzte Frage hat am meisten gefunden, und das war zu erwarten: Ein Backlog beschreibt einen
Zustand, den die Arbeit ständig verlässt.

- **Punkt 4 stand auf einer falschen Tatsache.** „Heute sucht die Fotoliste im Verwaltungsbereich
  nur über den Titel" — tatsächlich deckt das `or_(…)` in `api/admin.py` Titel, Ortsname *und*
  Dateiname ab. Der Punkt bestand also aus einer Lücke, die es nicht gab. Was von ihm übrig
  blieb, ist eine Zeile in Punkt 25.
- **Punkt 1 nannte 58 straßengenaue Fotos**, während Punkt 30 auf derselben Seite 60 zählte.
  Beide hatten recht, zu verschiedenen Zeitpunkten: Zwei Besucherbeiträge waren dazugekommen.
- **Punkt 1 nannte die unsinnigen Schlagwörter, aber nicht die achtzehn Fotos, die
  „Intel(R) JPEG Library, version [1.51.12.44]" heiszen.** Von allen Befunden der Durchsicht ist
  das der einzige, den ein Besucher sofort sieht — er steht als Überschrift in der Detailansicht.
- **Punkt 30 verwies auf Punkt 1**, wo die Schlagwörter aufgeräumt würden. Das tat inzwischen
  Punkt 41.

**Sechs Nummern sind dabei vergriffen gegangen.** Vier gingen in einem anderen Punkt auf: 16 („Der
praktische Teil von Punkt 15" — so begann sein Text buchstäblich), 12 und 24 wurden zu Prüfungen
innerhalb von Punkt 15, und 13 wurde der erste Eintrag der Sammelliste von Punkt 40. Zwei fielen
weg: Punkt 2 zielte auf den Erstimport, der gelaufen ist, und ging als Warnung in Punkt 41 ein;
Punkt 4 löste sich in der oben beschriebenen Fehlannahme auf.

**Und die 24 war doppelt vergeben.** Sie hiesz erst „Backlog ordnen und klassifizieren" und wurde
am 8. August erledigt; noch am selben Tag bekam der Rest der Tastaturfrage aus Punkt 6 dieselbe
Nummer. Das verstößt gegen die Regel, die drei Absätze weiter oben in derselben Datei steht —
und es fällt niemandem auf, solange nicht jemand beide Stellen nebeneinander liest. Die
Vergabestelle war der Backlog, das Gedächtnis war diese Datei, und die beiden hatten keinen
Abgleich. Seitdem führt der Backlog die vergriffenen Nummern **ausdrücklich auf**, direkt unter
der Übersichtstabelle. Eine Liste, die man sehen kann, ist die einzige Fassung dieser Regel, die
sich selbst durchsetzt.

Der Backlog führt danach **31 Punkte**, elf Nummern sind vergriffen, die nächste freie ist 43.

## Die Kachel, die drei Viertel der Sammlung verschwinden liess

9. August 2026. Punkt 32 des Backlogs war der erste Fehler, den die neue Einordnung als
*wichtig und dringend* ausgewiesen hatte, und er brauchte am Ende **eine Zeile**. Die Übersicht
der Verwaltung meldete für den Erstbestand 252 Fotos als „auf der Karte zu sehen"; zu sehen waren
855.

Die Kachel zählte Fotos mit Ort **und** Jahr, und der Kommentar darüber gab die Begründung:
„Both are needed for the map: the view filters on place and time at once." Der Satz war einmal
richtig. Er wurde falsch, als der Kiosk anfing, bei ganz aufgezogenem Schieber **gar keinen**
Zeitfilter zu schicken — damit hängt `_viewport_filters` die Datumsbedingungen nicht an, und
undatierte Fotos stehen auf der Karte. Der Regelfall ist genau dieser: Ein Besucher, der nichts
eingestellt hat, sieht alles.

**Der Schaden war nicht die schiefe Zahl, sondern die Arbeit, die sie ausgelöst hätte.** Bei 670
Fotos ohne Jahr sagte die Kachel dem Museumsteam, drei Viertel der Sammlung seien unsichtbar. Die
naheliegende Antwort darauf ist, zu datieren — und zwar Fotos, die längst auf der Karte liegen.
Eine falsche Zahl auf einer Startseite ist harmlos; eine falsche Zahl, die einer Handvoll
Ehrenamtlicher sagt, womit sie ihre Zeit verbringen sollen, ist es nicht.

**Derselbe Fehler steckte in `python -m app.cli stats`** — und dort noch einer dazu: Die
CLI zählte gelöschte Fotos überall mit, während die Verwaltung sie überall herausnimmt. Die
Schlusszeile verglich damit zwei verschiedene Grundgesamtheiten miteinander. Beide Programme
zählen jetzt nach derselben Regel, was die Abnahme erst möglich machte: CLI und API gaben
hinterher unabhängig voneinander dieselbe Zahl aus.

**Was der Fall über Kommentare sagt.** Der Kommentar hat den Fehler nicht verursacht, aber er hat
ihn drei Monate lang gedeckt: Wer die Zeile las, fand eine Begründung und las weiter. Ein
Kommentar, der ein *Warum* behauptet, wird geglaubt — deshalb steht an der Stelle jetzt nicht nur
die neue Regel, sondern auch, woran sie hängt und wo ihr Gegenstück liegt
(`_viewport_filters` in `api/photos.py`). Ändert sich dort etwas, ist hier die Fundstelle.

Die beiden Tests dazu beschreiben den Fehlerfall, nicht den Erfolgsfall:
`test_foto_ohne_jahr_steht_auf_der_karte` und die Gegenprobe ohne Ort. Zurückgedreht fällt der
erste sofort — nachgeprüft, bevor der Commit stand.

## Die Karte antwortet erst, wenn sie gefragt wird

9. August 2026. Punkt 26 des Backlogs. Solange „Wo ist das?" auf dem Schirm stand, war die ganze
Karte scharf — jeder Tipp auf eine freie Fläche setzte einen Punkt. Wer nur schauen wollte,
beantwortete die Frage dabei versehentlich, und weil der Bereich danach **„Hier war das"** anbot,
brauchte es nur einen zweiten, bestätigenden Tipp, damit im Bestand eine Verortung stand, die
niemand gemeint hat.

Die Umsetzung war ein Schalter und eine Trennung. **Der Schalter** heiszt „Auf der Karte zeigen"
und liegt im Store, nicht in der Komponente — das war die eine Entscheidung, die beim Aufschreiben
des Punktes Arbeit gekostet hat und beim Bauen keine Minute. `LocationTask` wird bei fast jedem
Fotowechsel abgebaut, ein `useState` fällt dort also von selbst zurück; nur auf dem einen Weg
nicht, auf dem `load()` zur ursprünglichen Frage zurückfällt, weil die andere leergelaufen ist.
Genau dieser Weg kommt, wenn eine Art von Lücke abgearbeitet ist. Er ist heute kaum zu treffen und
wäre später schwer zu finden gewesen.

**Die Trennung** betrifft `PinLayer`: Ob ein Tipp einen Punkt setzt und ob der Punkt gezeichnet und
gezogen werden kann, sind seitdem zwei Bedingungen. Hätte man beides zusammen abgeschaltet, wäre
mit dem scharfen Tipp auch der Punkt verschwunden, den die **Straßenwahl** gesetzt hat — und die
Zusage „Der Punkt lässt sich auf der Karte noch verschieben" hätte nicht mehr gegolten.

**Beim Prüfen kam der Zusatz, der den Punkt erst rund macht.** Erst stand der Knopf unter der
Straßenwahl und nur dort. Er gehört **darüber** — er ist die Alternative *zu* der Liste, nicht
der letzte Ausweg dahinter — und er gehört **auch in den Hausnummernschritt**, wo er am meisten
einbringt: Wer die Straße kennt, die Nummer aber nicht, zeigt auf das Haus, statt „Reicht so" zu
drücken. Das ist derselbe Fall, den Punkt 36
für den Bestand lösen will — hier fällt er nebenbei mit ab.

### Was die Gegenprobe über die eigenen Tests sagte

Zurückgedreht wurde einzeln an allen drei Stellen, die den Schalter zurücksetzen. Zwei fielen,
eine nicht: `skip()` setzt zwar selbst zurück, ruft danach aber `load()`, und dessen `set` läuft
noch vor dem ersten `await` — die Zeile ist nachweislich wirkungslos. Sie steht trotzdem, weil
direkt darüber Punkt, Etikett und Genauigkeit dieselbe Symmetrie haben und eine fehlende Zeile
dort wie ein Versehen läse.

Wertvoller war der erste Durchgang der Gegenprobe: Er zeigte, dass **keiner** der neuen Tests die
Rücksetzung in `load()` deckte, weil alle über `skip()` oder `contribute()` liefen, die je selbst
zurücksetzen. `load()` ist aber die Stelle, die jeden Fotowechsel sieht. Der Test dafür ruft
`load()` seitdem unmittelbar auf — geschrieben, weil die Gegenprobe nicht fiel, nicht weil eine
Lücke aufgefallen wäre.

## Was der Schieber wegnahm, ohne es zu sagen

9. August 2026. Punkt 33 des Backlogs, und der zweite Teil desselben Missverständnisses wie
Punkt 32 am selben Tag: „undatiert" und „unsichtbar" sind nicht dasselbe, fallen im Kopf aber
leicht zusammen. Bei 32 zählte deshalb eine Zahl falsch. Hier war es schlimmer — die Zahl stimmte,
aber der Besucher erfuhr nie, was ihm abhandenkam.

Ein Foto ohne Datum überlappt keinen Zeitraum. Es fiel damit aus **jeder** Auswahl heraus, sobald
jemand den Schieber auch nur ein Stück zusammenzog: zwei Drittel der Sammlung, lautlos, ohne dass
irgendwo gestanden hätte, dass das passieren würde. Am laufenden Bestand nachgemessen — 855 Fotos
ohne Zeitfilter, 3 in der Auswahl 1950 bis 1994.

Aus der Meldung „507 Fotos ohne Jahr" neben dem Schieber ist deshalb ein **Schalter** geworden:
„507 Fotos ohne Jahr anzeigen", mit Haken. Die Zahl stand ohnehin dort; es kommt kein
Bedienelement hinzu, ein vorhandenes bekommt einen Zweck.

### Die Frage, an der es hängt, hat der Auftraggeber besser beantwortet als der Vorschlag

Der Backlog hatte zwei Möglichkeiten für den Anfangszustand aufgeschrieben und keine gute dabei:
**an** zeigt beim ersten Blick alles, macht den Schieber aber unehrlich; **aus** macht ihn sofort
ehrlich und kostet drei Viertel der Karte, bevor jemand etwas getan hat.

Die Antwort war keine von beiden: **an — und beim ersten Zusammenziehen des Zeitraums geht er von
selbst aus.** Das ist genau der Moment, in dem die Auswahl anfängt, etwas zu bedeuten. Bis dahin
hat der Besucher nichts eingestellt und soll alles sehen; ab da hat er etwas eingestellt und soll
sehen, was das bewirkt.

Beim Bauen kam eine Präzisierung dazu, ohne die der Einfall sich selbst im Weg gestanden hätte:
**automatisch nur einmal.** Wer den Schalter von Hand wieder einschaltet, bei dem bleibt er an,
auch beim nächsten Zug am Schieber. Ginge er jedes Mal wieder aus, wäre genau die Nebenwirkung
zurück, gegen die der ganze Punkt gebaut ist — nur eine Ebene höher, und ärgerlicher, weil sie
eine Entscheidung überschriebe, die jemand gerade getroffen hat.

Wonach die Automatik greift, ist `queryTimeFilter` — dieselbe Funktion, die entscheidet, ob
überhaupt ein Zeitfilter zum Backend geht. Der Schalter geht damit exakt dort aus, wo sonst Fotos
anfingen zu verschwinden. Eine eigene Regel dafür wäre eine zweite Wahrheit gewesen.

### Zwei Fallen, die beim Schreiben der Tests auffielen

**Das Histogramm hätte sich selbst abgeschaltet.** Es zählt die undatierten Fotos, und diese Zahl
ist die Beschriftung des Schalters. Hätte es `include_undated` mitbeachtet, stünde dort nach dem
Abschalten eine Null — das Etikett verschwände, und mit ihm der einzige Weg zurück. Der Endpunkt
erzwingt den Wert deshalb, so wie er den Zeitfilter schon immer verworfen hat.

**Ein Test prüft nichts, wenn der Store vorher aussteigt.** Die Gegenprobe lief einzeln gegen alle
drei Bedingungen der Automatik, und die dritte fiel nicht: Der Test dafür setzte einen Zeitraum,
den das Einklemmen an der Achse unverändert liesz — `setTimeRange` stieg beim Vergleich mit dem
alten Wert aus, bevor die Logik überhaupt erreicht war. Ein grüner Test, der nie an der Stelle
vorbeikam, die er zu schützen vorgibt. Er setzt jetzt einen Zeitraum, der sich wirklich ändert
und die Spanne trotzdem überdeckt: Endgriff von 2030 auf 2026, während das jüngste Foto bei 2024
liegt.

## Die Straßenauswahl in der Adaptionsanleitung

9. August 2026. Punkt 37, und der günstigste des Tages: reine Dokumentation. Die
[adaption.md](adaption.md) sagt einem zweiten Museum, was es anfassen muss — die Straßenauswahl
kam dort seit dem 8. August nur als eine Zeile zu `streetChoice` vor, obwohl sie inzwischen der
Hauptweg zur Verortung ist.

Der neue Schritt 3 beantwortet vier Fragen, die sonst beim zweiten Museum noch einmal erarbeitet
werden müssten: woher die Straßen kommen (`make places` über Overpass), wie man nachsieht, was
der Baum bekommt (`GET /api/places/streets`, mit fertigem Aufruf), wie `streetChoice` zu wählen
ist, und was schiefgehen kann — eine zu enge `bbox` lässt Randstraßen fehlen, eine zu weite
holt Nachbardörfer herein, die die eigenen aus den nächsten `streetChoice` verdrängen.

**Die Zahlen darin sind nachgerechnet, nicht abgeschrieben.** Der Backlog behauptete zehn
Buchstabengruppen, sieben davon direkt zur Liste; nachgefahren mit `nearby_streets` und
`groupStreets` gegen den laufenden Ortsindex kam genau das heraus — 80 Straßen, 10 Knöpfe,
7 direkt, und A, H und I mit einem Zwischenschritt. Die Doku nennt die Gruppen jetzt beim Namen,
damit ein zweites Museum sein eigenes Ergebnis danebenhalten kann.

**Zwei Stellen waren nebenbei veraltet.** Die Prüfliste am Ende fragte noch, ob „die Ortssuche im
Hilf mit-Bereich lokale Straßennamen findet" — die gibt es dort seit dem 8. August nicht mehr.
Und der Fall ohne Ortsindex sieht seit dem Kartenschalter vom selben Tag anders aus: Der Bereich
sagt nicht nur, man möge auf die Karte tippen, er schaltet sie auch von sich aus scharf.

`tools/check_anchors.py` prüft die `adaption.md` ab jetzt mit — sie hat seit diesem Punkt
Verweise auf ihre eigenen Abschnitte, und die Abschnitte sind dabei umnummeriert worden.

## Siebenhundertmal „Jahr unbekannt"

9. August 2026. Punkt 27, und der letzte des Tages. Unter jedem Vorschaubild auf der Karte stand
die fertige Datumsangabe — eine Zeile, die an dieser Stelle in beide Richtungen danebenlag: unter
den 256 Kameraaufnahmen „22. März 2014", unter den rund 670 undatierten Fotos „Jahr unbekannt",
siebenhundertmal untereinander.

Jetzt steht dort **Adresse und Jahr**. Die Entscheidung für die Adresse statt des Titels hatte der
Bestand längst getroffen: Keine der 922 Adressen ist länger als dreißig Zeichen, 105 Titel sind
länger als vierzig, und achtzehn heiszen „Intel(R) JPEG Library". Die Adresse passt immer unter
ein Vorschaubild, der Titel oft nicht.

**Der Stapel war der Fall, den der Backlog nicht bedacht hatte.** Er beschrieb nur „jedes
Vorschaubild" — aber ein Marker mit einundfünfzig Fotos ist ein Sonderfall mit einer eigenen
Antwort. Die Adresse teilen alle, denn genau deshalb liegen sie auf einem Marker; das Jahr teilen
sie nicht, und das oberste zu nehmen setzte ein Datum unter fünfzig Fotos, die es nicht tragen.
Ein Stapel zeigt seitdem die Adresse und kein Jahr — und die Adresse nur, wenn wirklich **alle**
seine Fotos sie teilen: Zwei über EXIF verortete Aufnahmen können auf einen Meter zusammenfallen,
ohne miteinander zu tun zu haben. Am laufenden Kiosk stand genau so ein Marker: einer ganz ohne
Zeile, neben „Wedeler Straße 2" mit zweien und „Bredhornweg 17 — 2017" mit einem.

**Zwei Kleinigkeiten fielen beim Bauen auf.** Die CSS-Klasse hiesz `marker__year` und hätte
danach gelogen — sie heiszt jetzt `marker__caption`. Und die Zeile brauchte eine Breitengrenze:
„Uetersener Straße 12 — 1953" ist gut doppelt so breit wie das Vorschaubild darüber und hätte
sich über die Nachbarmarker geschoben. Neun rem, dann zwei Zeilen, dann abgeschnitten; nachgemessen
am Bestand kommt der breiteste Fall auf 147 px und bleibt darunter.

Die Testfixture `make_photo` kennt seitdem `month`, `day` und `place_name` — ohne die drei liesz
sich der Fall „22. März 2014 wird zu 2014" gar nicht aufschreiben.

## Der kurze Weg vom Foto in seine Bearbeitung

9. August 2026. Punkt 25, die zweite Tür aus Entscheidung 26 — und der Punkt, dessen Arbeit an
einer Stelle lag, die man ihm nicht ansieht. Der Stift neben dem Titel war eine Stunde Arbeit; die
PIN-Abfrage gab es, den Bearbeiten-Bildschirm auch. **Was fehlte, war die Möglichkeit, von aussen
„Verwaltung bei Foto 412 öffnen" zu sagen.** Die Fotoliste öffnete ihren Editor über eigenen
Zustand, und dieser Zustand war von nirgendwo erreichbar.

Das Ziel reist jetzt durch den Admin-Store, `AdminApp` und die Fotoliste — verwandt mit dem
`Target`, über das die Übersicht schon in einen Bereich springt.

**Die eigentliche Frage war nicht, wie es hineinkommt, sondern wann es wieder verschwindet.** Ein
Ziel, das stehen bleibt, legt beim Schließen des Editors dasselbe Foto wieder vor — und an der
Fotoliste käme niemand mehr vorbei. Es fällt deshalb an vier Stellen zurück: beim Abbrechen der
PIN, beim Ende der Sitzung, sobald die Verwaltung es aufgegriffen hat, und beim nächsten Ziel.
`AdminApp` liest es einmal beim Aufbau in eigenen Zustand und räumt es sofort weg; die Fotoliste
öffnet einmal und merkt sich, dass sie es getan hat. Zwei Riegel, weil einer davon in einem
`useEffect` sitzt und ein zweiter Lauf sonst genügt.

**Der Typprüfer hat dabei einen Fehler gefunden, den kein Test gefunden hätte.** `AdminGate`
reichte `askPin` direkt als `onClick` durch. Seit die Funktion eine optionale Fotonummer nimmt,
wäre das Klickereignis an deren Stelle angekommen — ein `MouseEvent` als Fotonummer, und die
Verwaltung hätte beim Tippen auf das Wappen versucht, ein Foto zu öffnen, das es nicht gibt.

### Die Kennung, und was sie kosten darf

Unter dem Bildnachweis stehen jetzt die ersten acht Zeichen des SHA-256. Acht Hexzeichen sind vier
Milliarden Möglichkeiten — kurz genug zum Abschreiben, eindeutig genug für einen
Museumsbestand, dieselbe Länge, die git aus demselben Grund nimmt.

**Sie steht dort nur, weil die Verwaltungssuche sie findet.** Der Backlog hatte das als offene
Frage notiert, und es war die richtige: Ohne die eine zusätzliche Zeile im vorhandenen `or_(…)`
wäre das eine Zahl, die sich nirgends nachschlagen lässt — Zierrat statt Auskunft. Sie ersetzt
den Stift nicht, sondern deckt den Fall ab, den er nicht kann: jemanden, der sich ein Foto notiert
und später an einem anderen Gerät danach sucht.

### Was ungeprüft blieb

Die Besucherseite ist am laufenden Kiosk nachgefahren: Stift neben dem Titel, 50 px Fläche,
Kennung `21b56ce1` unter dem Bildnachweis, ein Tipp bringt das Zahlenfeld. **Der Weg dahinter
nicht** — dafür braucht es die PIN dieses Geräts, und die gehört nicht in eine Sitzung wie
diese. Gedeckt ist er durch Tests des Stores und durch die Gegenprobe an allen vier
Rücksetzungen; was am Bildschirm noch niemand gesehen hat, ist der Sprung in den
Bearbeiten-Bildschirm selbst.

## Fünf Formen, vier Rollen

9. August 2026. Punkt 28, und der erste des Tages, bei dem der Backlog eine Frage stellte statt
eine Aufgabe zu beschreiben. Die Bestandsaufnahme zuerst: **zwanzig Knöpfe in fünf Formen**, und
keine Form sagte, was ihr Knopf tut. Dahinter lagen vier Rollen — auswählen, übernehmen,
zurück, überspringen —, und die Formen schnitten quer dazu.

**Der schlimmste Schnitt lief mitten durch eine Rolle.** Dieselbe leise, randlose Form trug
„Anderer Buchstabe" und „Weiß ich nicht — nächstes Foto". Das eine geht einen Schritt zurück und
bleibt beim Foto, das andere legt das Foto weg. Sie sahen gleich aus.

Und die Form selbst war das zweite Problem: grau, ohne Rand, kleiner als alles andere — sie las
sich als Text. Für eine Zielgruppe, die einmal im Jahr vor diesem Gerät steht, ist ein Knopf, der
nicht nach Knopf aussieht, kein Knopf.

### Zwei Fragen, die der Auftraggeber entschieden hat

**Wie laut darf „Reicht so — die Straße genügt" sein?** Es war ein schlichter weißer Knopf,
während „Hier war das" und „Ganze 1920er Jahre" gefüllt waren — obwohl alle drei dasselbe tun:
abschließen. Dagegen stand die Sorge, ein gefüllter Knopf ziehe den Blick von den Hausnummern
darüber weg. Entschieden: **genauso laut.** Nicht jedes Haus steht in OpenStreetMap, und wer die
Nummer nicht kennt, soll das ohne Zögern sagen können; Konkurrenz entsteht nicht, weil in diesem
Schritt kein zweiter gefüllter Knopf auf dem Schirm steht.

**Wie setzt sich „Überspringen" ab?** Entschieden: dieselbe Knopfform wie die übrigen — damit es
wie ein Knopf aussieht —, getrennt durch eine Linie und deutlichen Abstand, mit einem Pfeil nach
rechts. Keine eigene Farbe: Die Ansicht kommt mit Papier, Tinte und einem Akzentbraun aus, und das
soll sie.

Beim Bauen kam eine Kleinigkeit dazu, die nur am Gerät auffällt: Der Abstand über dem Knopf
gehört **ausserhalb** von ihm. Als Innenabstand wäre er mittippbar gewesen — ein zwei Zentimeter
hoher Streifen über der Beschriftung, der das Foto weglegt.

### Die Symbole

Vier: Haken, Pfeil links, Pfeil rechts, Fadenkreuz. **Neben der Beschriftung, nie an ihrer
Stelle** — ein Piktogramm allein verlangt Vorwissen, neben den Worten muss es nur bestätigen, was
gelesen wurde. Und deshalb so wenige: Ein Symbol auf jedem Knopf wäre Zierde, und Zierde erklärt
nichts.

Gezeichnet in `kiosk/icons.tsx`, nicht geladen. Kein Symbolzeichensatz, kein CDN — das Gerät ist
offline, und ein Symbol, das nicht lädt, hinterlässt einen Knopf, der nichts sagt. Der Stift aus
Punkt 25 ist bei der Gelegenheit dorthin gezogen; er ist das einzige Symbol ohne Beschriftung, und
das darf er, weil er nicht dem Besucher gehört.

### Was sich dabei nebenbei gelöst hat

Punkt 10 wartete auf diesen hier: Sein
Schließen-Knopf ist an die Blätterknöpfe gebunden, damit die Detailansicht *eine* Knopfform
kennt. Jetzt gibt es vier benannte Rollen — und keine heißt „schließen". Aus „darf er aus dem
Raster?" ist damit „welche Rolle bekommt er?" geworden, und das steht dort jetzt als erster
Schritt.

Nachgemessen am laufenden Kiosk: fünf Rollen im Einsatz (die vier plus das Jahresraster),
Mindesthöhe 54 px, und kein Knopf ausserhalb der Raster ohne Symbol.

## Die Kopfzeile findet ihre Mitte

9. August 2026. Punkt 29, vier Änderungen an derselben Zeile — und zwei davon haben eine Rechnung
durch eine Regel ersetzt.

**Die Höhen.** Wappen, Titel und Zeitschieber standen oben bündig und endeten fast fünfzig
Pixel auseinander. Das CSS behauptete an genau dieser Stelle das Gegenteil: Ein Kommentar rechnete
vor, dass beide Titelzeilen zusammen `--crest` ergeben und „damit genau so hoch wie der Schieber
nebenan" stehen. Das stimmte einmal — für eine Schirmbreite, und bis der Schieber am 9. August
von 3 auf 3,5 rem wuchs. Drei Rechnungen, die auseinanderlaufen konnten, sind jetzt eine
gemeinsame Mittellinie: `align-items: center` im Titelfeld, `justify-content: center` im
Schieberfeld. Nachgemessen liegen alle drei Mitten auf demselben Pixel — 84.

**Und damit hat sich [Punkt 19](https://github.com/nordfisch/kiekmap/issues/20)
zur Hälfte erledigt**, ohne dass jemand die Frage beantwortet hätte. Er stand als Blocker für
den Kopfbereich, weil dort `--crest` schrumpfte und der Schieber nicht. Eine Mittellinie gilt in
jeder Breite. Wo eine Abhängigkeit von einer offenen Frage verschwindet, sobald man die Stelle
richtig baut, war die Abhängigkeit vielleicht nie die Frage.

**Der Griff und sein Boden.** Der Auftrag war knapp: „slider mindestbreite 1 jahrzehnt. kein auge
symbol." Beides zusammen ist die Antwort auf die Frage, die der Backlog offengelassen hatte — der
gezeichnete Griff in der Mitte war das, was übrig blieb, wenn der Zeitraum auf einen Balken
zusammengeschoben war, und ein Ersatzsymbol wäre die Antwort auf ein Problem gewesen, das der
Boden gerade abschafft.

Beim Bauen kam eine Entscheidung dazu, die der Auftrag nicht traf: **Was passiert am Boden mit dem
anderen Ende?** Es mitzuschieben klingt geschmeidiger und ist die Falle — ein Zug am linken Ende
trüge das rechte über das Achsenende, wo es geklemmt würde, und der Zeitraum käme schmaler
zurück, als er hineinging. Genau das Schrumpfen, das `shiftRange` an anderer Stelle schon einmal
verhindern musste. Das bewegte Ende stoppt also, das andere bleibt.

Am Gerät nachgefahren: 1950 bis 1959, zehn Jahre einschließlich beider Enden, 65 px
Greiffläche. Vom anderen Ende her rührt sich nichts mehr.

**Der Rollentausch.** Das Wappen lädt neu und setzt damit alles zurück; der Titel „Bilder aus
Holm" ist die Tür in die Verwaltung. `AdminGate` heißt deshalb jetzt `Crest` und liegt unter
`kiosk/` — eine Komponente namens „Verwaltungstür", die eine Seite neu lädt, wäre genau die
Sorte Name, die später jemanden in die Irre führt. Die CSS-Klasse ist mitgezogen und von
`admin.css` nach `global.css` gewandert.

### Der Fehler beim Aufräumen der Dokumentation

Beim Herausschneiden des erledigten Punktes aus dem Backlog habe ich zwischen zwei Überschriften
geschnitten, ohne zu prüfen, welche von beiden weiter vorn steht — Punkt 10 lag vor Punkt 29, und
`t[:start] + t[end:]` hat den Abschnitt dazwischen **verdoppelt** statt ihn zu entfernen. Aufgefallen
ist es an der Zählung: 23 Zeilen in der Tabelle, 25 Überschriften im Text. Dasselbe Muster wie am
8. August, als derselbe Griff einen Punkt gelöscht hat; damals fand es die Ankerprüfung, diesmal
der Abgleich von Tabelle und Text. Beide Male war die Ursache dieselbe Annahme — dass die
Reihenfolge im Text der in der Tabelle folgt. Sie tut es nicht.

## Nachschärfen: der Weg vom Ort zur Hausnummer

9. und 10. August 2026, Punkt 36. Geplant war eine Frage im Beitragsbereich. Gebaut wurde ein
Schreibweg, eine dritte Bedingung und ein Nummernraster in der Detailansicht — die Frage im Bereich
steht noch aus, und das ist kein Rückstand, sondern das Ergebnis des Nachzählens.

**Das Nachzählen hat die Antwort umgedreht.** Der Punkt stand seit Wochen mit einer Tabelle im
Backlog: 60 Fotos liegen straszengenau, ihr `place_name` verspricht eine Hausnummer, die Koordinate
hält sie nicht. Der naheliegende Schluss war, genau diese 60 vorzulegen. Beim zweiten Hinsehen
zerfielen sie in **58 und 2**. Bei den 58 steht die Hausnummer im Namen — bekannt ist sie also,
fehlen tut die Koordinate. Auf die Rückfrage „das kann doch gar nicht passieren, wenn die
Hausnummer bekannt ist" kam die dritte Messung und mit ihr der Grund: **Die Häuser sind aufgeteilt
oder neu nummeriert worden.** Im Ortsindex steht 2a statt 2, 13a bis 13d statt 13. Bei 55 von 58
liegt dieselbe Zahl mit anderem Zusatz im Index, bei 3 eine Nachbarnummer, bei **keinem** gar
nichts.

Damit war der größte Teil von Punkt 36 kein Besucherfall mehr. Ein Besucher am Kiosk weiß auch
nicht, wo die frühere Schulstraße 2 stand; der Ortsindex weiß es fast immer. Die 58 sind als
Punkt 41 (a) zur maschinellen Arbeit geworden. Übrig blieben **2** — und beide stammen von
Besuchern, die „Reicht so — die Straße genügt" gedrückt haben. Der Fall ist also echt und
wächst, nur ist er heute klein.

**Eine zweite Erkenntnis kam vom Kurator und zeigt, warum die Frage trotzdem gebaut gehört.** Von
72 Fotos ohne Ort tragen **64** als Titel exakt einen Straßennamen; sie stammen aus Ordnern, die
eine Straße ohne Hausnummer nannten, und `_locate` lässt solche Fotos bewusst unverortet. Die
Begründung dafür stand im Code: Die Straßenmitte „sähe aus wie eine Antwort", und das Foto
fiele aus „Wo ist das?" heraus. **Mit der dritten Frage fällt es nicht heraus, sondern hinein** —
die Begründung ist hinfällig, und der Widerruf steht in decisions.md, nicht nur im Backlog. Das
ergibt eine Abhängigkeit in beide Richtungen: Ohne Punkt 41 (b) hat die Frage 2 Fotos und
erscheint nie; ohne die Frage verschöbe (b) 64 Fotos in eine Frage, die es nicht gibt.

**Die eigene Tür.** Nachschärfen heißt, eine vorhandene Angabe zu ersetzen — was decisions.md
Punkt 5 verbietet, und dieser Punkt ist der Grund, warum Besucherbeiträge überhaupt ohne
Moderation durchgehen dürfen. Die naheliegende Lösung wäre gewesen, `_require_empty` um „ausser
wenn genauer" zu erweitern. Sie fällt aus einem Grund aus, der erst beim Hinsehen sichtbar wird:
`POST /location` nimmt `accuracy_m` **vom Client** entgegen. Heute ist das harmlos, weil das Feld
ohnehin leer sein muss. Entschiede die Genauigkeit über das Überschreiben, wäre sie ein
Schlüssel in der Hand dessen, der davon profitiert — ein Aufruf mit `accuracy_m: 1` ersetzte jede
Angabe im Bestand. Also ein eigener Endpunkt, der **keine Koordinate annimmt**: Der Client schickt
die Nummer der gewählten Adresse, alles Übrige holt der Server aus dem Ortsverzeichnis.

**Drei Stellen fragen dasselbe, also fragt es jetzt eine.** `needs_location` gab es zweimal — als
`@property` auf dem Modell und als SQL-Ausdruck im Endpunkt. Zwei Formulierungen, beide für sich
plausibel, und niemand hätte gemerkt, wenn sie auseinandergelaufen wären. Vor der dritten Frage
sind sie zu `hybrid_property` und `services/needs.py` zusammengefallen. **Die Reihenfolge des
Tupels `NEEDS` ist die Rangfolge** — „Nachschärfen kommt zuletzt" steht damit nicht in einer
Fallunterscheidung, sondern in der Position eines Wortes.

### Vier Bedingungen, und die dritte war die stille

Wer gefragt wird, entscheidet ein `and_()` aus vier Teilen. Der wichtigste ist der, den man
weglassen würde: **141 der 486 Straßen haben im Ortsindex gar keine Adressen.** Ohne die
`exists()`-Klausel stünde die Frage „welche Hausnummer?" auf dem Schirm — mit keinem einzigen Knopf
darunter. Genau deshalb liegt die Bedingung in einem Dienst und nicht auf dem Modell: Ob der
Ortsindex antworten kann, weiß ein Foto-Objekt ohne Sitzung nicht.

Der Ziffern-Test (`place_name` ohne Ziffer) ist eine Heuristik und irrt zugunsten des Nichtfragens:
Eine „Straße des 17. Juni" würde nie vorgelegt. Das ist die harmlose Richtung, und der Test hält
fest, dass es Absicht ist.

### Zwei Gegenproben, die zuerst nicht griffen

Bei der Genauigkeitsbedingung ist mir das zweimal hintereinander passiert: Erst war das
hausgenaue Testfoto „Am Kamp 1" — es fiel schon an der Ziffernregel heraus, nicht an der
Genauigkeit. Dann „Gasthof Timm" — es fiel an der `exists()`-Klausel heraus. Beide Male hätte
der Test bestanden, wäre die Bedingung gelöscht worden. Erst „Am Kamp" mit 15 m schließt wirklich
nur die Genauigkeit aus. Der Grund steht seitdem im Docstring des Tests, weil die nächste Person
sonst dieselbe Falle stellt.

### Der Wächter, der nichts bewachte

`_is_newest` sollte verhindern, dass eine Rückname in falscher Reihenfolge einen längst ersetzten
Ort wieder auferstehen lässt. Er verglich Zeitstempel — und traf nie zu. Der Grund ist SQLite:
`server_default=func.now()` schreibt ganze Sekunden (`14:24:37`), ein gebundenes Python-`datetime`
schreibt Mikrosekunden (`14:24:37.000000`), verglichen wird als Text, und die kürzere Zeichenkette
verliert. Die Bedingung war gebaut, sah richtig aus und tat nichts. Sie vergleicht jetzt
`Change.id`, und die Falle steht im Docstring.

### Und ein selbst gemachter Verlust

Nach einer Gegenprobe habe ich die Änderung mit `git checkout --` zurückgenommen — und damit
nicht nur die Gegenprobe, sondern die ganze, noch nicht committete Store-Methode. Wiederhergestellt
war sie in zwei Minuten, weil sie im Gespräch stand. Die Lehre ist trotzdem billiger zu haben als
ein zweites Mal: Eine Gegenprobe wird aus einer Kopie zurückgeholt, nicht aus HEAD.

## Die dritte Frage, die Zahlen auf der Karte und ein Wächter zu viel

10. August 2026, zweite Lieferung zum Nachschärfen: die Frage im Beitragsbereich (Punkt 36), die
Hausnummern auf der Karte (Punkt 35) und der Stufenwechsel beim Zoomen (Punkt 38). Damit sind alle
drei Punkte erledigt.

**Die Rangfolge ist ein Array.** Aus dem Hin und Her zwischen zwei Fragen ist eine Liste geworden:
`NEEDS = ["location", "date", "housenumber"]`, und die Reihenfolge *ist* die Rangfolge. „Nachschärfen
kommt zuletzt" steht damit in der Position eines Wortes und nicht in einer Fallunterscheidung.
Dieselbe Reihenfolge steht im Backend in `services/needs.py`; sie zweimal zu haben ist der Preis
dafür, dass Frontend und Backend nicht dieselbe Datei lesen können.

**Eine Unterscheidung, die beim Bauen erst entstand:** *leergelaufen* und *beantwortet* sind nicht
dasselbe. Läuft eine Frage leer, ist jede andere fair; nur eine Antwort kann eine weitere Frage
überflüssig machen. Daraus wurden zwei Funktionen — `nextNeeds` und `nextAfterAnswer` —, und die
Ausnahme („wer gerade `Reicht so` gedrückt hat, wird nicht nach der Hausnummer gefragt") hängt
allein an der zweiten.

Der erste Anlauf hatte die Ausnahme in `nextNeeds` und damit an der falschen Stelle: Der
Nachschärf-Frage war dadurch von der Ortsfrage aus gar nicht mehr beizukommen. Der zweite Anlauf
setzte sie richtig, und der Test fiel trotzdem — weil `load` sich seinen Rückfall selbst
ausrechnete und die eben beantwortete Frage dabei wieder hereinholte. `load` nimmt jetzt die ganze
Reihenfolge entgegen, statt sie sich zu denken. **Wer lädt, weiß warum; die Ladefunktion nicht.**

### Eine Gegenprobe, die nichts bewachte

Beim Absichern der Rangfolge ist mir derselbe Fehler in neuer Gestalt begegnet. Die Attrappe der
API-Schicht im Test enthielt `NEEDS` als **abgeschriebene Liste** — mit dem ausdrücklichen
Kommentar, das sei „der echte Wert". Die Gegenprobe zeigte das Gegenteil: „date" und „housenumber"
in `client.ts` zu vertauschen liess **keinen einzigen Test** fallen. Zwei Fehler auf einmal, und
beide ohne Symptom:

1. Die Attrappe war eine zweite Wahrheit. Sie liest jetzt über `importOriginal` den echten Wert.
2. Kein Test unterschied die Reihenfolge. Alle prüfbaren Fälle hatten höchstens eine Frage mit
   Vorrat — da entscheidet die Reihenfolge nichts. Erst ein Fall, in dem **beide** liefern könnten,
   prüft sie wirklich.

### Was die Animation zweimal verschluckt hat

Punkt 38 sah nach einer CSS-Regel aus und war eine Messung. Der Wechsel wurde markiert, war aber
nie zu sehen — zweimal aus verschiedenen Gründen, und beide fand erst der Blick auf die laufende
Seite:

**Erstens** hing `draw()` an `move` *und* `zoom`. Gemessen: ein Tipp auf „+" ergab 31 `move`- und 30
`zoom`-Ereignisse, es wurde also alles rund sechzigmal je Zoomstufe neu gebaut. Der als einblendend
markierte Marker war einen Frame später weg. Nötig war nichts davon: MapLibre hält Marker selbst
auf ihren Koordinaten, gezeichnet werden muss nur eine geänderte *Menge*. Jetzt hängt es an
`moveend`, und ein Vergleich der gezeichneten Gruppen lässt selbst dann die Arbeit ausfallen, wenn
sich nichts geändert hat.

**Zweitens** ist eine Umgruppierung nicht ein Zeichnen. Direkt nach dem Zoom werden die Fotos des
neuen Ausschnitts geholt, und wenn sie ankommen, entstehen alle Marker noch einmal — dieser zweite
Aufbau ist kein Stufenwechsel und nahm die Einblendung wieder mit. Wer während einer laufenden
Einblendung entsteht, gehört seitdem dazu (`stillEntering`).

Beides ist erst am Gerät aufgefallen, nicht im Test. Ein Zähler in der Konsole hat je zwei
Minuten gekostet und beide Male die Ursache genannt — was hier den Ausschlag gab, war nicht mehr
Nachdenken, sondern die Bereitschaft, nachzusehen.

### Und derselbe Griff daneben, ein zweites Mal

`git checkout --` auf eine Datei, um eine Gegenprobe zurückzunehmen — und damit auch die noch
nicht committete Arbeit darin. Am selben Tag zum zweiten Mal, diesmal `client.ts` und `NEEDS`.
Wiederhergestellt in zwei Minuten; die Lehre bleibt dieselbe wie am Vormittag und ist zweimal
teurer bezahlt als nötig: **Eine Gegenprobe wird aus einer Kopie zurückgeholt, nie aus HEAD.**

## Der Erstbestand wird bereinigt — und zwei Regeln drehen sich um

*11. August 2026.* Punkt 41 stand als der große Posten im Backlog: 929 Fotos, deren Titel die
Adresse daneben wiederholten, 77 ohne Ort, 58 mit einer Hausnummer, die es im Ortsindex nicht mehr
gibt. Vorgesehen war ein Sprachmodell mit einer Vorlage-Ansicht, in der jemand jede Umstellung
bestätigt.

**Gebaut wurde nichts davon.** Eine halbe Stunde Nachzählen am Bestand sagte etwas anderes als
die Planung:

- Die 58 „Fälle" waren **neun Adressen**. 38 Fotos hingen an „Schulstraße 2" allein. Eine
  Nachbarnummer-Regel mit Vorlage-Liste zu bauen wäre Maschinerie für neun Zeilen gewesen.
- Die 632 Komma-Titel („Hauptstraße 11a, Gasthof Timm") liessen sich **mechanisch** trennen,
  und der Zusatz stand ohnehin schon als Schlagwort am Foto — nachgezählt bei allen 632, ohne eine
  einzige Ausnahme. Ein Sprachmodell hätte nichts gewusst, was nicht schon dastand.
- Die Jahreszahl im Dateinamen, seit Monaten als eigener Teilpunkt geführt, betraf **null** Fotos.

Die Arbeit lief als Einmalaktion an `data/kiekmap.db`, nicht als Werkzeug: Trockenlauf vorlegen,
schreiben, nachzählen. Die Rückfahrkarte war eine Dateikopie. Was an Code dabei entstand, sind
drei Regeln in `services/foldermeta.py` und eine Funktion in `services/places.py` — damit der
nächste Import die Lücken nicht neu erzeugt.

### Die Ursache, die eine Zeile weit weg lag

Drei Fotos hatten keine Herkunftsangabe, und die Vermutung im Backlog lautete, es hänge am nicht
auflösbaren Straßennamen. Es hing an einer Zeile: `apply_folder_meta` stieg aus, sobald keine
Straße erkannt war — und die Herkunft, die nur am Pfad hängt und gar nicht an der Straße, wurde
erst danach gesetzt. Zwei der drei Fotos lagen lose in der Importwurzel, das dritte unter
„Deelenweg", das zwischen „Deelenweg I" und „Deelenweg II" nicht zu entscheiden ist. Dort arbeitet
die Eindeutigkeitsprüfung genau richtig; sie nahm die Herkunft nur als Nebenschaden mit.

### Was das Nachmessen über die EXIF-Koordinaten ergab

Der größte Posten stand nicht im Backlog. 413 Fotos lagen auf einer EXIF-Koordinate, und
`_locate` liess sie dort: „EXIF schlägt den Ordner immer", mit der Begründung, die Kamera habe
tatsächlich dort gestanden. Beim Vorlegen fiel auf, dass 349 dieser Fotos eine im Ortsindex
auffindbare Archivadresse hatten — bis zu 689 m entfernt vom Punkt, auf dem sie lagen.

Die Frage war, welche Seite irrt. Beantwortet hat sie eine Abfrage von drei Zeilen: **278 der 413
teilen ihre Koordinate mit einem anderen Foto**, an einem Punkt hängen 20 Fotos von vier
verschiedenen Tagen. Sechs gleiche Nachkommastellen an vier Tagen liefert kein Empfänger. Die
Werte sind eingetragen worden, nicht gemessen — es stand also nie Messung gegen Ablage, sondern
eine Ablage gegen eine andere. Siehe [decisions.md](decisions.md), Punkt 34.

**Das ist beim Vorlegen aufgefallen, nicht beim Planen.** Der Plan hatte die Zahl 331 und den Satz
„die GPS-Angabe ist echt"; beides war falsch, und beides stand schon im Plan, bevor jemand
nachgesehen hatte. Der Trockenlauf vor jedem Schritt hat sich hier ein einziges Mal bezahlt
gemacht und damit für die ganze Aktion.

### Die Rangfolge war aus dem Gefühl gebaut

Nach dem Bereinigen sollte die Nachschärf-Frage endlich Fotos haben — 71 statt keinem. Am
laufenden Kiosk kam sie trotzdem nicht: Überspringen der Jahresfrage führte zurück zu „Wo ist
das?".

Der Grund stand in `NEEDS`: `location, date, housenumber`. Eine Frage wird erst erreicht, wenn die
vor ihr **leer** ist — und 673 undatierte Fotos laufen nie leer. Die dritte Frage wäre nie
gestellt worden, und der ganze Aufwand von Punkt 36 hätte brachgelegen. Die Reihenfolge ist
umgedreht; die Begründung steht in [decisions.md](decisions.md), Punkt 35.

**Und die Reihenfolge liess sich vertauschen, ohne dass im Backend ein Test fiel.** Gemerkt hat es
allein einer im Frontend, wo dieselbe Liste ein zweites Mal steht — genau die Doppelung, die sonst
als Schwäche gilt. Die Lücke ist mit `TestRangfolge` geschlossen, und die Lehre ist dieselbe wie
beim Mock, der im Juli seine eigene Kopie von `NEEDS` hielt: **Eine Reihenfolge braucht einen Test,
der genau sie prüft, nicht nur ihre Wirkung im Normalfall.**

### Was am Ende dastand

924 von 929 Fotos auf der Karte statt 852. Kein Titel mehr, der die Adresse daneben wiederholt.
Und zwei Fehler, die vorher nicht zu sehen waren, weil der Bestand sie verdeckt hatte: Die
Marker-Beschriftung zeigt die Adresse, während der Vorlesetext den Titel nennt — identisch,
solange beide dasselbe waren (Punkt 44). Und bei einer Straße mit 132 Adressen liegen die
angebotenen Hausnummern ausserhalb des Kartenausschnitts, weil die Karte zur Straßenmitte fährt
(Punkt 45). Beide sind erst aufgefallen, als der bereinigte Bestand sie sichtbar machte.

## Der Rest von Punkt 41: Text stand in den falschen Feldern

*12. August 2026.* Nach der Verortung blieben drei Teilpunkte, die im Backlog nach drei Aufgaben
aussahen — Titel durchsehen, Schlagwörter sichten, Beschreibungen ergänzen. **Nachgemessen war es
eine:** Beschreibungen standen als Titel, abgeschriebene Fotorückseiten standen als Schlagwort,
Archiv-Regalnummern standen als Schlagwort. Und das Feld, in das all das gehört, war bei 720 von
929 Fotos leer.

Umgeräumt wurde in vier Zügen: 23 lange Titel und 39 Notizen in die Beschreibung, 6 Reste einer
Dateibenennung (`dav`, `dig`) geleert, 23 Regalnummern an die Herkunft. Danach hatten 260 Fotos
eine Beschreibung statt 209, und von 308 Schlagwörtern blieben 253 — alle davon wirklich
Stichwörter.

### Die Regalnummer wollte in die Beschreibung, und das war die falsche Tür

Die Ansage lautete zuerst, die Signaturen („P 11", „O 40") an die Beschreibung zu hängen, damit
sie erhalten bleiben. Erhalten bleiben sollten sie — nur steht die Beschreibung im Kiosk unter dem
Bild. Unter einem Hof des 19. Jahrhunderts hätte dann „P 35" gestanden.

`provenance` ist das Feld dafür, und der Grund steht seit Stufe 8 im Docstring von `PhotoDetail`:
Das öffentliche Schema hat kein Feld dafür, *damit* die Angabe nicht auf den Schirm im
Ausstellungsraum gerät. Nachgeprüft nach dem Umräumen: `/api/photos/247` liefert 28 Felder, und
keines davon enthält das Wort „Signatur". Siehe [decisions.md](decisions.md), Punkt 36.

### Zwei Anläufe, das Datieren zu automatisieren, und beide waren falsch

83 undatierte Fotos trugen eine Jahreszahl im Text. Der erste Anlauf las jede vierstellige Zahl und
mied eine Liste von Warnwörtern — *vor*, *erbaut*, *abgerissen*. Vorgelegt sah man sofort, was die
Liste nicht kannte: **bebaut**, **abgebrannt**, **Baujahr**. Jedes davon hätte ein Foto auf das
Baujahr des Hauses datiert statt auf die Aufnahme.

Der zweite Anlauf drehte die Richtung um: nicht „ein Jahr ohne Warnwort", sondern **„ein Jahr, dem
*um*, *ca.*, *im Jahre*, *Herbst*, *Dezember* oder *aus den* vorausgeht"**. Eine Warnwortliste ist
nie fertig; ein positives Muster ist es. Aus 83 wurden 23 klare Fälle und 46 zweifelhafte — und
die 46 waren als Liste mit Fundstelle und Begründung in fünf Minuten durchzusehen.

Ausserdem verworfen: **zweistellige Kurzformen**. „78" für 1978 ist im Bestand üblich und von
Regalnummern („P 37" -> 1937) und Hausnummern („Friedhofsweg 30" -> 1930) nicht zu unterscheiden.
62 Fotos hingen daran und bleiben undatiert.

Am Ende: **52 datiert, 17 Vorschläge verworfen.** Und das Verworfene ist die teurere Hälfte der
Entscheidung — ein verworfener Vorschlag kostet nichts, das Foto bleibt in „Wann war das?". Ein
angenommener falscher macht das Foto datiert, nimmt es aus der Frage und legt es an die falsche
Stelle der Zeitleiste, wo es niemand mehr ansieht. Siehe [decisions.md](decisions.md), Punkt 37.

### Was man am Ende sehen konnte

Der Zeitschieber lief vorher von **2010 bis 2025** — die einzigen datierten Fotos waren die
Neuaufnahmen. Jetzt läuft er von **1880 bis 2030**, mit Balken über die ganze Spanne. Das
Museum hat zum ersten Mal eine Zeitleiste, und sie war die ganze Zeit im Bestand vorhanden, nur in
den falschen Feldern.

Nebenbei gefunden und mitgenommen: 59 Beschreibungen trugen Wagenrückläufe aus
Windows-Zeilenenden.

### Punkt 41 ist damit aus dem Backlog gezogen

Die maschinelle Vorbereitung des Erstbestands ist abgeschlossen: Was sich aus Dateien, Ordnernamen
und den vorhandenen Textfeldern ableiten liess, ist abgeleitet. **Die Nummer 41 bleibt vergriffen**
und wird nie neu vergeben — wer sie in einer alten Notiz findet, findet sie hier.

Was noch von Hand zu tun war, hat **Punkt 1** aufgenommen -- am 18. August 2026 abgearbeitet und
damit ebenfalls vergriffen; er steht weiter unten in dieser Datei. Es war genau das,
was Ortskenntnis braucht: 669 fehlende Beschreibungen, 621 undatierte Fotos ohne Anhalt im Text,
rund 100 Titel, die eher Notiz als Titel sind, und 5 Fotos ohne Ort. Zwei Fehler, die erst durch
das Aufräumen sichtbar wurden, stehen als Punkt 44 und 45 daneben.

## Ein Antwortweg statt zweier -- und ein Fehler, der zwei Tage lief

*12. August 2026.* Zwei Punkte, die am selben Tag entstanden waren, als der bereinigte Erstbestand
sichtbar machte, was der lückenhafte verdeckt hatte.

### Die Karte folgt jetzt den Nummern, nicht der Straße

Punkt 45 war in zwanzig Minuten erledigt und ist trotzdem lehrreich. Die Karte fuhr beim
Nachschärfen zum **Straßenpunkt** -- richtig gedacht, und auf einer Straße mit 132 Adressen
falsch: Der Punkt liegt in der Mitte, die angebotenen Nummern liegen an einem Ende. Nachgemessen
lag genau **eine von elf** Beschriftungen im Ausschnitt.

Die Nummern standen längst im Store (`offeredNumbers`); die Karte sah sie nur nicht an. Jetzt
hängt der Effekt an ihnen statt am Foto, und damit fährt die Karte auch beim Wechsel des
Abschnitts mit -- vorher blieb sie stehen. Am Lehmweg nachgezählt: **elf von elf.**

Nebenbei stellte sich heraus, dass `focus` ein `lat` und ein `lon` trug, die **nirgends gelesen**
wurden; `MapView` benutzt allein `bounds`. Beide sind weg, und `showArea(bounds)` steht neben
`showLocation(lat, lon)`.

### Die Detailansicht fragt nicht mehr selbst

Punkt 46 nimmt zurück, was am 10. August gebaut wurde, und die Begründung von damals ist dabei
nicht falsch geworden -- sie ist überholt. Die eingebetteten Auswahlraster gab es, **weil der
Bereich das Nachschärfen nicht vorlegen konnte**; inzwischen ist es dort die zweite Frage.

Was den Ausschlag gab, waren zwei Zahlen: bis zu **37 Schaltflächen** in der Textspalte, davon
fünfzehn Jahrzehnte -- die Datierung des Erstbestands hatte das Problem selbst vergrößert. Und
**null** von drei Fragen zum Ort, weil der die Karte braucht und die unter dem Overlay liegt.

Jetzt stehen dort bis zu drei Knöpfe, und ein Tipp gibt Foto und Frage an den Bereich weiter. Der
Server lernte dafür einen `photo_id`-Parameter -- **einen Wunsch, keine Anweisung**: Er prüft ihn
gegen dieselbe Bedingung wie jedes andere Foto und fällt sonst auf die Zufallswahl zurück. Alles
danach ist der gewöhnliche Ablauf; `contribute()` blieb unangetastet. Siehe
[decisions.md](decisions.md), Punkt 38.

### Der Fund beim Abnehmen: seit zwei Tagen ging kein Beitrag mehr durch

Beim Prüfen am laufenden Kiosk antwortete `POST /contribute/67/date` mit **500**:

```
sqlite3.OperationalError: table changes has no column named old_source
```

Die Alembic-Revision vom 10. August war auf `data/kiekmap.db` nie gelaufen. **Zwei Tage lang
scheiterte damit jeder Besucherbeitrag** -- und 393 grüne Tests standen daneben, weil sie ihr Schema
aus den Modellen bauen und eine fehlende Migration grundsätzlich nicht bemerken können.

**Die Ursache war eine Wiederherstellung, und damit trifft der Fehler das Museum genauso.** In
`data/` lagen zwei `vorher-…`-Ordner -- die Spur, die eine Wiederherstellung hinterlässt --, der
jüngste vom 11. August mit demselben Zeitstempel wie die Datenbank. Eingespielt worden war eine
Sicherung vom 5. August, also von vor der Migration. **Eine Sicherung bringt ihr Schema mit:**
`_swap_in` tauscht `kiekmap.db` im Ganzen aus, `_reopen_database` hängt das laufende Programm nur
neu an sie. Migrationen laufen beim *Start*, und eine Wiederherstellung ist kein Start.

Ein Neustart behebt es. Das steht jetzt im [Benutzerhandbuch](usermanual.md) als Einschränkung und
in [operations.md](operations.md) mit Diagnose und Abhilfe -- samt dem umgekehrten, schlimmeren
Fall: Eine Sicherung, die *neuer* ist als das Programm, lässt das Gerät gar nicht erst hochkommen.

Dass es niemandem auffiel, hat einen zweiten Grund, und der ist der unangenehmere: **Alles Prüfen
der letzten Tage war lesend.** Die Bereinigung des Erstbestands schrieb an der API vorbei; im Kiosk
wurde nachgesehen, ob Fragen *erscheinen*. Ob eine Antwort ankommt, hat zwei Tage niemand versucht.
Aufgenommen als Punkt 47 — behoben am 15. August 2026, siehe unten.

**Die Lehre ist älter als dieser Fehler und hier wieder bezahlt worden:** Ein Durchgang, der nur
schaut, prüft die Hälfte. Der erste Klick, der etwas *schreibt*, hat gefunden, was zwei Tage
Nachdenken und dreihundert Tests nicht fanden.

## Der Titel kommt auf die Karte, und die Beschriftung bekommt einen Mund

*12. August 2026.* Punkt 44 sah nach einer Zeile aus und war eine Entscheidung über den Bestand.

Unter dem Vorschaubild stand die Adresse, im `aria-label` desselben Knopfes der Titel. **Der Fehler
war nicht die falsche Zeile, sondern dass es zwei gab** -- zwei Formulierungen derselben Sache, an
zwei Stellen. Beide zu berichtigen hätte ihn nur vertagt. Es gibt jetzt eine
(`kiosk/mapCaption.ts`), und beide Sinne lesen sie.

### Die Frage, die vorher zu klären war

227 Fotos hatten keinen Titel. Der Vorschlag lautete, für alle einen zu erzeugen und **in die
Daten zu schreiben**: aus der Beschreibung, sonst aus Adresse und Jahr. Nachgezählt hiess das
89 aus Beschreibungen und 138 aus Adressen -- und die Adresstitel wiederholten sich stark:
zwanzigmal „Hauptstraße Nr. ?", vierzehnmal „Hörnstraße 9".

**Damit stünde in `title` wieder wörtlich das, was in `place_name` daneben steht** -- genau das,
was einen Tag zuvor für 815 Fotos entfernt worden war. Dazu zwei Folgen, die erst beim Aufschreiben
sichtbar wurden: Ein kopierter Titel veraltet, sobald ein Besucher die Hausnummer nachschärft. Und
die Unterscheidung „hat einen Titel" verschwände -- danach hätten alle 929 einen, und
Punkt 1 hätte seine Arbeitsgrundlage verloren.

Gebaut wurde deshalb die Hälfte, die Zugewinn ist: **75 Titel aus Beschreibungen geschrieben**,
zusammengefasst statt abgeschnitten -- „Errichtung des Funkmastes" wurde „Funkmast". Die 152
Adressfälle werden **abgeleitet**; auf der Karte steht dasselbe, nur veraltet nichts und `title`
bleibt ehrlich leer.

14 Beschreibungen taugten nicht: Sie sprechen über Besitzer, Rückseiten oder Ortsvermutungen
(„2018 Besitzer Dennis Knop", „Text auf der Rückseite: 12.4.63 Holm"), nicht über das Motiv.

### „Hauptstraße Nr. ?"

Fehlt die Hausnummer, steht sie als Fragezeichen da. Das ist dieselbe Haltung wie beim Nichtstreuen
der Stapel (decisions.md, Punkt 33): Die Ungenauigkeit soll **sichtbar** bleiben, damit jemand sie
behebt. Auf 82 Markern steht jetzt genau die Lücke, nach der der Beitragsbereich fragt.

### Was der Plan nicht wusste

**Es sind 75 Titel, nicht 60.** Beim Vorlegen hatte ich die *verschiedenen* Titel gezählt (53) und
daraus eine Fotozahl gemacht. Aufgefallen ist es erst, als das Skript die Zuordnung gegen den
Bestand prüft -- 75 zugeordnet, 14 offen, zusammen die 89. Dieselbe Prüfung hätte auch eine
falsche id gefunden; sie stand aus einem anderen Grund darin und hat einen anderen Fehler
gefangen.

**Und die Abschnittsüberschrift ist zum zweiten Mal an derselben Stelle verschwunden.** Wer einen
Backlog-Punkt entfernt, sucht „bis zum nächsten `###`" -- steht der Punkt als letzter in seinem
Bereich, liegt zwischen ihm und dem nächsten `###` die Trennlinie und ein `##`. Beim ersten Mal
(Punkt 45/46) fiel es durch die Anker-Prüfung auf, beim zweiten Mal beim Nachzählen der
Abschnitte. **Das Suchmuster muss bei `##` genauso halten wie bei `###`.**

---

## Der Containerbetrieb ist keine Zusage mehr, sondern gemessen

*14. August 2026.* Punkt 17. `make prod` war nie gelaufen -- beim Bauen stand kein Docker zur
Verfügung. Auf dem Pi ist das der einzige Betriebsmodus, und
[Punkt 21](https://github.com/nordfisch/kiekmap/issues/22) begründete sich ausdrücklich mit „es läuft schon in Containern": genau
der Satz, den niemand geprüft hatte.

Der Entwicklungsmac taugte dafür besser als erwartet. Docker Server 27.4 auf `linux/arm64` ist
dieselbe Architektur wie ein 64-Bit-Pi, die Abbilder bauen also nativ. **Beide bauten auf Anhieb**
-- `npm ci` und `pip install` zum ersten Mal gegen eine reine Umgebung, was der eigentliche Zweck
dieser Prüfung war. nginx liefert die Kartendatei mit **206 Partial Content** und ohne gzip aus,
die Schriften kommen aus dem Abbild, ein tiefer Link auf `/admin` landet bei der Einzelseite, und
die Seite fragt **null fremde Herkünfte** an. Der Entrypoint zieht den Schemastand nach.

### Der Fund: die `.env` erreichte den Container nur zur Hälfte

Der `environment:`-Block nannte vier Variablen. Die übrigen fielen im Container still auf ihre
Vorgaben zurück, und das traf den Import: **kein Schlagwort, kein Bildnachweis, keine Herkunft.**
Nichts schlug fehl, nichts stand im Protokoll -- die Fotos kamen an, nur ohne ihre Zuschreibung.

Behoben mit `env_file: ../.env` statt einer Aufzählung. Die vier Container-Wahrheiten
(`DATA_DIR`, `MEDIA_DIR`, `CORS_ORIGINS`, der PIN-Hash) stehen weiter unter `environment:` und
gewinnen dort -- die Gegenprobe steht in den Daten: Die `.env` des Macs sagt
`KIEKMAP_MEDIA_DIR=/Volumes`, im Container steht `/media`. Wer künftig eine Einstellung
einführt, muss nichts weiter tun.

### Beinahe hätte die Messung gelogen

Die erste Probe war ein Foto aus dem Bestand mit geändertem Hash. Es kam mit dem Schlagwort
„Gebäude" an -- **und das sah wie ein Beweis aus, dass die Einstellung ankommt.** Sie kam aus den
Metadaten der Datei selbst. Erst der Blick in `docker exec … env` zeigte, dass
`import_tags` im Container leer war; der saubere Zeuge war die Herkunft, die schlicht `None` blieb.
**Ein Fund, der aus zwei Quellen stammen kann, ist kein Fund, bevor man die Quellen getrennt hat.**

### Was auf dem Mac nicht zu prüfen war

`/media` gibt es unter macOS nicht, und `rshared` ist eine Mount-Propagierung des Linux-Kerns, die
über die Dateifreigabe von Docker Desktop nicht durchgeht. Dafür gibt es jetzt
`deploy/docker-compose.mac.yml`, das genau diese beiden Einhängungen ersetzt und sonst nichts.
**Der USB-Weg der Sicherung bleibt damit ungeprüft** -- gerade der Fall, den `rshared` lösen
soll, nämlich ein erst nach dem Start eingesteckter Stick. Er ist nach
[Punkt 18](https://github.com/nordfisch/kiekmap/issues/19) gewandert, das Verhalten nach Stromausfall und Neustart nach
[Punkt 15](https://github.com/nordfisch/kiekmap/issues/18). Wer später „Container sind geprüft" zitiert, soll die zwei Lücken
mitlesen.

### Und ein Fehler von mir, der lehrreicher war als das Ergebnis

Für den Durchgang habe ich den Bestand kopiert -- Datenbank, Fotos, Vorschaubilder. Zweimal
danebengegriffen. Erst fehlte die **WAL-Datei**: Ohne sie lag die Kopie beim Stand vom 12. August,
die 75 Titel waren nicht dabei. Dann fehlte **`region.json`**, und das legte den halben Kiosk
lahm -- `nearby_streets` gab eine leere Liste zurück, der Beitragsbereich hatte keine Straßen
anzubieten, und die Karte stand auf einem Ausschnitt von 150 Metern. Beides sah nach einem
Container-Fehler aus und war keiner. **Die Sicherung des Programms nimmt `region.json` und
`places.json` von sich aus mit** (`LOOSE_FILES` in `services/backup.py`) -- von Hand kopieren tut
das niemand.

### Nachtrag: ein Symlink liess die Sicherung ins eigene Verzeichnis laufen

Noch am selben Abend, und gefunden, weil Kalle die eine Zeile der Prüfliste nachholte, die ich
nicht selbst machen konnte: die Sicherung. Sie lief durch -- **auf einen Datenträger, der keiner
war.**

Die Überlagerung hängt `/Volumes` als `/media` ein, und dort liegt auf **jedem** Mac ein
Symlink auf `/`, benannt nach dem internen Volume -- das war später die wichtigste Berichtigung an
diesem Eintrag: kein Zufall dieser Maschine, sondern der Normalfall für alle, die der
`operations.md` folgen und zum Entwickeln `KIEKMAP_MEDIA_DIR=/Volumes` setzen. Aufgefallen war es
nur nie, weil niemand den Sicherungsknopf auf einem Mac gedrückt hatte. Weil
`os.path.ismount` für einen Symlink grundsätzlich `False` sagt, galt er als gewöhnlicher Ordner;
die Suche stieg eine Ebene hinab -- die Ebene, die es für `/media/<benutzer>/<bezeichnung>`
braucht -- und folgte ihm bis in die Wurzel. Angeboten wurden zwei „Laufwerke" namens `data` und
`media`. **931 Fotos und 1,45 GB landeten in dem Ordner, den sie sichern**, mit Handzettel, also
aussehend wie eine richtige Sicherung.

Der Docstring von `find_drives` benannte diesen Fall bereits als den, den die Einhängeprüfung
verhindern soll. Der Symlink war das Loch darin. Behoben in zwei Zeilen, festgehalten als
[Punkt 40](decisions.md).

**Zwei Dinge daran sind das Aufschreiben wert.** Erstens: Der Fund kam aus dem Rest, den ich als
ungeprüft stehengelassen hatte. Eine ehrlich benannte Lücke ist mehr wert als eine, die man
übersieht -- und dasselbe galt gleich noch einmal, siehe unten. Zweitens: **Die erste Gegenprobe schlug nicht aus.** Die im Test eingesetzte
`_is_mounted` vergleicht Pfade wörtlich, und wörtlich ist `media/Danger/data` nicht
`anderswo/data` -- der Test war auch ohne die Absicherung grün und hätte nichts bewacht. Er
vergleicht jetzt aufgelöst, und dann fällt genau einer. Eine Gegenprobe ohne Ausschlag ist ein
Ergebnis.


### Nachtrag zum Nachtrag: der Weg, den ich umgangen hatte

Beim Aufschreiben der Prüfliste fiel mir auf, dass ich den Import **über den Eingangsordner**
geprüft hatte -- weil der ohne Anmeldung arbeitet und ich also allein damit durchkam. Der geht
aber gar nicht durch nginx. Durch den Proxy waren bis dahin lauter GETs gelaufen und **zwei POSTs
von je ein paar Byte**, beides Anmeldungen. Der Stapel-Upload, also die einzige Stelle, an der
große Datenmengen in die andere Richtung fließen, war damit ungeprüft -- und mit ihm die Zeile
`client_max_body_size 128m`, ohne die nginx bei **einem Megabyte** mit 413 abbricht, bevor das
Backend die Datei überhaupt sieht.

Zwei Fotos mit 3,2 und 3,6 MB gingen durch. Die Zeile greift, und der Bildnachweis stand dran --
womit die `env_file`-Behebung auch auf dem HTTP-Weg belegt ist und nicht nur beim Eingangsordner.
Danach wurden beide wieder entfernt, hart: `photos`, `photo_tags`, `changes`, `import_log` und die
sechs Dateien. Nicht auf `status='deleted'` gesetzt, denn sie sollen nirgends auftauchen, auch
nicht unter „gelöscht".

**Bequemlichkeit sucht sich den Weg, der ohne fremde Hilfe geht** -- und genau der war der
falsche. Wer eine Prüfung allein fahren kann, prüft womöglich nicht das, worauf es ankommt.

### Ein Wächter für die Einstellungen

Auf die Frage, ob die drei Funde denn nun behoben seien, kam beim Nachmessen heraus: zwei ja, und
einer war nie ein Fehler im Programm gewesen -- der Upload-Weg war nur ungeprüft. **Aber die
Behebung des ersten war ungeschützt.** Wer `env_file: ../.env` aus der Compose-Datei löscht,
bekommt weiterhin 394 grüne Backend-Tests: Eine Compose-Datei wird von keinem Test angefasst, und
genau das hatte den Fehler beim ersten Mal so lange am Leben gehalten.

`tools/check_settings.py` schließt das, als drittes Werkzeug neben `language_check.py` und
`check_anchors.py` -- Skript und nicht Test, weil es Dateien liest, die die Tests nicht kennen. Es
holt die Feldnamen mit `ast` aus `config.py` (kein Import, also kein venv nötig) und liest die
Compose-Datei mit einem gezielten Leser statt mit PyYAML, das im System-Python fehlt.

Drei Fragen, und die zweite und dritte sind so viel wert wie die erste: Erreicht jede Einstellung
den Container? Steht in `environment:` nur, was es auch gibt? Und dasselbe für `.env.example`,
samt der auskommentierten Zeilen -- es ist die Vorlage, mit der jede neue Einrichtung anfängt, ein
Tippfehler darin reist also mit.

Drei Gegenproben, jede einzeln gefahren, jede mit eigener Meldung: `env_file` entfernt,
`KIEKMAP_CORS_ORIGIN` statt `_ORIGINS`, `KIEKMAP_DATADIR` statt `_DATA_DIR`.

**Und die erste Gegenprobe nannte vier Einstellungen, nicht drei.** Neben Schlagwort, Bildnachweis
und Herkunft war auch `KIEKMAP_EXIF_DATE_MAX_YEAR` unerreichbar -- die Zahl, ab der ein
EXIF-Datum als Scandatum gilt und ein Foto **nicht** datieren darf. Sie steht in `CLAUDE.md` als
einer der drei Dinge, die man hier falsch machen kann; im Betrieb war sie schlicht nicht
einstellbar. Aufgefallen ist das nicht mir, sondern dem Werkzeug, beim ersten Lauf.

---

## Aus dem Arbeitsnamen wird Kiekmap

*15. August 2026.* Punkt 48. Der bisherige Name beschrieb, was das Programm tut; **Kiekmap** —
plattdeutsch *kieken* — sagt, was es ist, und nennt dabei keinen Ort. Warum das keine Geschmacks-,
sondern eine Bauentscheidung ist, steht als [Punkt 41](decisions.md) daneben: Das zweite Museum
soll eine eigene `region.json` brauchen und keinen Fork, und ein Ortsname im Paket hätte dieser
Zusage widersprochen, lange bevor jemand sie technisch verletzt.

**213 Ersetzungen in 38 versionierten Dateien**, dazu vier umbenannte Dateien unter `deploy/pi/`,
die Datenbankdatei, die nicht versionierte `.env` und die editierbare Installation im venv. Für
Besucher ändert sich nichts — der Name stand nie in der Oberfläche, die Seite heißt „Bilder aus
unserem Ort".

**Der Zeitpunkt war der letzte günstige.** Kein Pi im Feld, kein Git-Remote, der einzige Bestand
auf dem Entwicklungsrechner. Einen Tag später im Betrieb hätte dasselbe Geräte, Sticks und
fremde Arbeitskopien betroffen.

### Die Falle, die diese Umbenennung selbst gestellt hat

Mit dem Präfix ändert sich der Name **jeder** Einstellung. Eine `.env`, die niemand anfasst,
wird danach gelesen wie Luft: Pydantic kennt die alten Schlüssel nicht mehr, ignoriert sie
stillschweigend, und die ganze Konfiguration steht auf ihren Vorgaben. Schlagwort, Bildnachweis,
Herkunft und der PIN-Hash weg — **derselbe Fehler wie am Vortag, nur aus einer anderen Richtung.**

Der Wächter von gestern hätte ihn nicht gefangen: Er las die Compose-Datei und die
`.env.example`, nicht die echte `.env`. Genau die ist aber die einzige Datei im Projekt, die
niemand je durchsieht, weil sie nicht versioniert ist. `tools/check_settings.py` liest sie jetzt
mit und stellt zwei Fragen an sie: Steht hier eine Einstellung unter einem Präfix, den es nicht
mehr gibt? Und trägt ein Schlüssel mit richtigem Präfix einen Namen, den es nicht gibt?

Die Suche nach dem falschen Präfix ist bewusst eng: Sie schlägt nur an, wenn der Teil **hinter**
dem Präfix eine Einstellung benennt, die es wirklich gibt. Eine `.env` darf halten, was ihr
Besitzer sonst noch hineinschreibt; `…_IMPORT_TAGS` unter fremdem Präfix ist dagegen keine fremde
Variable, sondern unsere, verschrieben.

Beide Gegenproben gefahren: einmal die ganze `.env` auf den alten Präfix zurückgedreht (sechs
Meldungen), einmal ein Buchstabe an einem Schlüssel entfernt (eine).

### Nebenbei ausgeräumt

`backend/*.egg-info/` lag im Repo, obwohl es ein Bauartefakt der editierbaren Installation ist.
Statt es umzubenennen, ist es herausgeflogen und steht jetzt in der `.gitignore`. Und im venv
lagen nach dem Neuinstallieren **beide** Verteilungen nebeneinander — die alte ist deinstalliert,
sonst hätte sie bei der nächsten Fehlersuche verwirrt.

### Was danach gemessen wurde

394 Backend- und 173 Frontend-Tests, alle drei Werkzeuge, und der Containerbetrieb von vorn: Beide
Abbilder neu gebaut, „Kiekmap: Schemastand prüfen ..." im Startprotokoll, `kiekmap.db` im
Datenverzeichnis, 929 Fotos, 811 davon im ersten Ausschnitt, **null fremde Herkünfte**, PIN-Hash
und Import-Einstellungen im Container angekommen.

---

## Der Neustart entfällt: die Wiederherstellung migriert selbst

*15. August 2026.* Punkt 47, der zweite der beiden offenen Fehler.

Seit dem 12. August stand in beiden Handbüchern, dass man das Gerät nach einer zurückgespielten
Sicherung einmal neu starten muss. Das war richtig und hat den Betrieb abgedeckt — **aber eine
Anweisung an Menschen ist die schwächste Stelle, die eine Zusage haben kann.** Befolgen muss sie
jemand, der ein- bis zweimal im Jahr an dieses Gerät geht; wer sie vergisst, merkt nichts, denn
der Fehler zeigt sich erst beim nächsten Besucher, der etwas beitragen will.

Jetzt tut es das Programm. `services/schema.py` ist die eine Stelle, an der von aussen mit Alembic
gesprochen wird, und `backup._swap_in` ruft sie — dort, weil beide Wege (Stick und Archiv) durch
diese Funktion gehen und ihr Docstring ohnehin sagt, dass hier nichts auseinanderlaufen darf.

**Die Reihenfolge ist der ganze Punkt.** Die Ablehnung einer zu neuen Sicherung kommt **vor** dem
Tausch, das Migrieren **danach**. Beides ist mit einem eigenen Test belegt, und der dritte prüft
die Zusage dazwischen: Nach einer Ablehnung liegt kein `vorher-`Ordner da, kein Arbeitsordner, und
die Fotos von heute sind noch da. Eine Sicherung, die dieses Programm nicht lesen kann, darf das
Gerät nicht halb ersetzt zurücklassen.

### Der Test, der gefehlt hat

`test_migrationen_und_modelle_beschreiben_dasselbe_schema` baut das Schema einmal über
`alembic upgrade head` und einmal über `create_all` und vergleicht Tabellen und Spaltennamen.

**Das ist der Test, dessen Fehlen den Fehler zwei Tage lang unsichtbar hielt:** Alle übrigen Tests
bauen ihr Schema aus den Modellen und können eine fehlende Migration deshalb grundsätzlich nicht
bemerken — 393 grüne Tests standen neben einer Datenbank, an der nichts mehr zu schreiben war.

Verglichen werden Namen, nicht Typen und Indizes: Die beiden Wege unterscheiden sich dort in
Kleinigkeiten, die nichts bedeuten, und ein Test, der daran hängenbleibt, wird abgeschaltet statt
gelesen. Die Gegenprobe: eine Spalte an ein Modell gehängt, ohne Migration — genau ein Test fällt.

### Zwei Funde am Rand, beide aus derselben Ecke

**Der Testaufbau war im ersten Anlauf ein Widerspruch.** Um eine Sicherung von vor der Migration
nachzubilden, hatte ich nur den Stempel zurückgedreht — die Testdatenbank entsteht aber aus den
Modellen und trägt die Spalte längst. Die Migration lief dann gegen eine Spalte, die schon da war.
Eine Nachbildung, die nur die Hälfte nachbildet, prüft nichts.

**Und `check_anchors.py` sah zwei Drittel der Dokumentation nicht.** `operations.md` und
`usermanual.md` standen nicht in seiner Liste, und **dateiübergreifende** Anker
(`usermanual.md#…`) prüft es bis heute gar nicht — dabei sind genau die es, die still brechen: Wer
einen Abschnitt umschreibt, liest seine eigene Datei, nicht die drei, die hineinverweisen. Beides
nachgezogen; der erste Lauf fand sofort drei tote Verweise, einen davon aus einer älteren Runde.

### Was danach gemessen wurde

398 Backend-Tests, dazu der ganze Weg im Container gegen ein temporäres Datenverzeichnis: eine
Sicherung auf dem Anfangsschema eingespielt, `old_source` danach wieder da, Stempel auf dem Kopf.
Und der umgekehrte Fall abgelehnt, mit unverändertem Bestand. **Der Container war dabei der
eigentliche Prüfpunkt**, denn dort läuft uvicorn in `/srv` und nicht in `backend/` — die
`alembic.ini` nennt ihren Skriptordner relativ, weshalb `schema._config()` ihn absolut setzt.

---

## Der Kopfbereich hört auf, am Ansichtsfenster zu hängen

*16. August 2026.* Punkt 49, gemeldet mit einem Bildschirmfoto bei 1470 x 956: „Bilder" / „aus" /
„Holm", dreizeilig untereinander.

**Die erste Ursache war ein Fallstrick, die zweite der eigentliche Fehler.** `--crest` schaltete
bei `@media (max-width: 85rem)` herunter, und in einer Medienabfrage ist `rem` immer 16 px — die
Umschaltung griff bei 1360 px statt bei den gedachten 1530. Das allein zu berichtigen wäre aber
zu kurz gesprungen gewesen: **Nachgerechnet blieben auch oberhalb der Schwelle 0,3 px** zwischen
dem, was „Bilder aus" braucht, und dem, was die Spalte hergibt. Bei 1470 px brach Safari um und
Chromium nicht — ein Pixel entschied.

Jetzt messen sich Wappen und Titel an der Breite ihrer eigenen Zelle (`cqi`), nicht am
Ansichtsfenster. Es gibt keine Schwelle mehr, an der etwas kippen könnte, und über den ganzen
Bereich von 1024 bis 2560 px bleiben 25 bis 56 Prozent Luft. Als
[Punkt 43](decisions.md) festgehalten.

### Der Prüfstein war nicht „Bilder aus", sondern der Ortsname

Der Backlog-Eintrag hatte es vorhergesagt, und die Messung bestätigte es: Die engste Zeile ist der
**Ortsname** — vier fette Zeichen auf 0,54 der Wappenhöhe sind breiter als zehn magere auf 0,28.
Und seine Länge steht nicht fest, sie kommt aus `region.json`.

Nach dem ersten Umbau war „Holm" gerettet und **„Hetlingen" brach immer noch um.** Ein Kopfbereich,
der nur mit einem vierbuchstabigen Ortsnamen hält, ist keine Behebung, sondern dieselbe
Zerbrechlichkeit mit etwas mehr Spielraum — und er widerspräche der Zusage, dass ein zweites
Museum nur seine `region.json` braucht.

**CSS kann Text nicht messen**, also bekommt es die eine Zahl, die fehlt: `App.tsx` gibt die
Zeichenzahl des Namens als `--name-length` mit, und die Schriftgröße ist der kleinere Wert aus
gewachsener Proportion und „Platz neben dem Wappen, geteilt durch die Zeichen". Danach stand jeder
geprobte Name einzeilig — bis „Klein Nordende-Lieth" bei **zwölf Pixeln** landete.

**Also ein Boden**, und mit ihm endet die Zusage bewusst: nie kleiner als die Zeile darüber. Wo er
greift, bricht der Name um. Das ist die bessere der beiden schlechten Antworten und war auch vorher
schon die gewählte — nur steht jetzt in `docs/adaption.md`, wo die Grenze liegt: bis zwölf
Zeichen auf jedem Schirm, bis sechzehn auf einem breiten.

### Was daran zu lernen war

**Zweimal habe ich zu früh gemessen und mir selbst etwas bestätigt, das nicht stimmte.** Erst
zählte ich Zeilen mit `getClientRects()` auf dem Element — das zählt Blöcke, nicht Zeilen, und
meldete brav „1". Dann verglich ich die Textbreite mit der Breite ihres Kastens und bekam überall
„-1 % Luft"; der Kasten ist ein Flex-Element ohne `flex: 1`, seine Breite **ist** die der
breitesten Zeile. Erst die dritte Messung — natürliche Textbreite gegen den wirklich freien Platz
— sagte etwas über die Sache. **Eine Messung, die immer dasselbe antwortet, misst nichts.**

---

## Die Detailansicht: das Bild bekommt Platz, die Knöpfe bekommen einen Ort

*16. August 2026.* Punkt 10, der letzte der beiden Masz-Fehler in der Besucheransicht.

### Der Knopf, der davonlief

Die Blätterknöpfe standen unmittelbar unter dem Bild und wanderten mit dessen Höhe.
Nachgemessen auf 1024 x 768, indem das Seitenverhältnis der Reihe nach durchgestellt wurde:
zwischen 3:2 quer und 2:3 hoch lagen **103 px**. Wer durch einen Stapel blättert, dessen Fotos
verschiedene Formate haben, jagt den Knopf über den Schirm -- und greift im schlimmsten Fall ins
Bild, wo eben noch „Nächstes" stand.

Jetzt sind sie senkrecht verankert und stehen waagerecht weiter mittig **unter dem Bild**. Nach dem
Umbau: **0 px Sprung** bei jedem geprüften Format, und die Mitte der Knopfzeile liegt auf die
Pixel genau auf der Bildmitte. Als [Punkt 44](decisions.md) festgehalten, samt der Regel dahinter:
Was der Besucher trifft, steht still; was er ansieht, darf sich bewegen.

Dass Bild und Text weiter **in einer Flucht** anfangen, ist dabei erhalten geblieben -- das war
eine eigene Entscheidung vom 9. August und hatte keinen Grund zu fallen. Der Block aus Bild und
Text rückt jetzt als Ganzes nach unten, wenn das Bild niedrig ist; die Knopfzeile bleibt, wo sie
ist.

### Die Textspalte, die das Bild zerdrückte

`--overlay-aside` stand fest auf 24 rem, also 432 px. Auf einem 1024er Panel blieben dem
querformatigen Scan damit 466 px -- weniger als die Hälfte des Schirms für das, was die Ansicht
zeigen soll. Jetzt wächst die Spalte mit (`clamp(16rem, 28vw, 24rem)`):

| Schirm | vorher | nachher | |
|---|---|---|---|
| 1024 px | 466 px | **610 px** | +31 % |
| 1280 px | 722 px | 796 px | +10 % |
| 1366 px | 808 px | 858 px | +6 % |
| 1920 px | 1362 px | 1362 px | ±0 |

**Genau die Verteilung, die der Backlog-Eintrag vorhergesagt hat:** „Auf 1920 x 1080 ist nichts zu
tun, auf einem 1024er Panel schon." Die Behebung greift dort, wo der Fehler war, und rührt nicht
an, was schon stimmte.

**Der zweite Weg aus dem Eintrag -- das Layout dem Bildformat folgen lassen -- ist nicht gebaut**,
und das war Absicht: Er stellt bei 884 von 929 Fotos die Ansicht um und will auf einem echten
Gerät beurteilt werden, nicht im Browser. Er bleibt der nächste Schritt, wenn
[Punkt 19](https://github.com/nordfisch/kiekmap/issues/20) die Auflösung geklärt hat.

### Der Schließen-Knopf und die Rollenfrage

Der Eintrag verlangte, vor der Arbeit zu entscheiden, welche Rolle der Knopf bekommt -- fünfte
Rolle oder Sonderfall. **Sonderfall.** Die vier Rollen aus Punkt 30 sind die Sprache des
Beitragsbereichs, wo ein Besucher Fragen beantwortet und die Form sagen muss, was ein Knopf tut;
Schließen ist keine davon, und Punkt 30 sagt ausdrücklich „mehr sollen es nicht werden". Dass die
Detailansicht auf ihrem dunklen Grund ohnehin eine eigene Knopffamilie führt, macht es zur
einfachsten Antwort statt zur Ausnahme.

Er steht jetzt in der Ecke des Schirms -- 45 px von oben und rechts, unabhängig davon, wie breit
der Inhalt gerade ist.

---

## Der Knopf, der angeblich am Jahr hing

*16. August 2026.* Punkt 53, gemeldet als: In der Detailansicht fehle der Weg zur Hausnummer,
sobald das Jahr bekannt sei.

**Die Beobachtung stimmte, die Erklärung nicht.** Weder das Backend noch das Frontend fragen an
dieser Stelle nach dem Jahr -- die Detailansicht holt die Hausnummern für *jedes* geöffnete Foto
und zeigt den Knopf, wenn die Liste nicht leer ist. Das Nachzählen ergab etwas anderes:

| Fotos mit bloßem Straßennamen | Anzahl | davon mit Jahr | Knopf? |
|---|---|---|---|
| straßengenau, vom Kurator | 71 | 13 | ja |
| **ohne Genauigkeit, aus dem EXIF** | **53** | **35** | **nein** |

Wer sich durchklickt, sieht damit eine saubere Korrelation -- die mit Jahr sind überwiegend gerade
die ohne Knopf -- und schließt auf die falsche Ursache. **Eine gemeldete Beobachtung ist ein
Befund, ihre Erklärung eine Vermutung.**

### Die eigentliche Ursache war eine Annahme, die niemand nachgezogen hat

`_needs_housenumber` verlangte ausdrücklich 150 m Genauigkeit und begründete das so: „Das Gerät
weiß, wo der Fotograf stand, nicht was er fotografiert hat." **Dieser Satz war am 12. August
widerlegt worden** -- 278 von 413 EXIF-Koordinaten des Erstbestands teilten sich zwei Fotos, es
sind eingetragene Werte und keine Messungen. Es steht seitdem in `CLAUDE.md` unter den drei Dingen,
die man hier falsch machen kann; in `needs.py` stand weiter die alte Begründung.

Nachgemessen für diese 53: **30 von ihnen teilen ihren Punkt mit einem anderen Foto, sechs hängen
an einem einzigen.** Eine eingetragene Koordinate an einer benannten Straße ist genau der Fall,
für den die Frage gebaut wurde.

Die Bedingung nennt jetzt, was sie meint -- auf der Karte, nicht schon hausgenau, Straßenname ohne
Ziffer, Adressen im Ortsindex. **Die Frage wächst von 70 auf 116 Fotos, 46 kommen dazu, 30 davon
mit bekanntem Jahr, keines fällt weg.** Als [Punkt 45](decisions.md) festgehalten.

### Der Test, der seinen eigenen Namen nicht hielt

Es gab einen `test_foto_aus_dem_exif_wird_nicht_vorgelegt`. Er war grün, und er prüft --
nichts dergleichen: Sein Foto hatte **gar keinen Straßennamen** und fiel schon an dieser Bedingung
heraus. Der EXIF-Fall stand zwei Wochen ungeprüft da, während ein Test mit genau diesem Namen
danebenstand und Sicherheit vortäuschte.

**Ein Test, dessen Name etwas anderes sagt als sein Aufbau, deckt eine Lücke zu, statt sie zu
schließen** -- er ist schlimmer als gar keiner, weil er die Frage als beantwortet ausweist. Er
heißt jetzt nach dem, was er misst, und der EXIF-Fall hat seinen eigenen daneben. Dazu ein dritter
für die neue Bedingung „muss überhaupt auf der Karte sein": Ohne sie stünden in der
Detailansicht „Wo ist das?" und „Welche Hausnummer?" nebeneinander und bäten darum, dasselbe Foto
zweimal zu verorten.

### Und ein Messfehler von mir, im selben Atemzug

Die Gegenrechnung „was kommt dazu" meldete erst **0**, obwohl die Zahlen von 70 auf 116 stiegen.
`NOT (accuracy == 150)` ist in SQL nicht wahr, wenn `accuracy` NULL ist, sondern NULL -- und genau
die Fotos ohne Genauigkeit waren die gesuchten. Über Mengen gezählt statt über SQL-Negation kam
die richtige Antwort. **Zwei Zahlen, die einander widersprechen, sind ein Geschenk**; hier hätte
das Ergebnis sonst „keine Änderung" gelautet, mitten in einer Änderung.

## Der Diff, der keiner war

*16. August 2026 -- Punkt 52, der neuere Archivstand.*

Vom Museum kam ein Ordner mit 619 Bildern, bereits als Differenz geliefert: der heutige Bestand
des Museums minus dem, was in unseren Erstimport ging. Dazu ein Satz: „Unsere Umwandlung von PNG
und TIFF nach JPG ist noch nicht erfolgt, diese Dateien dürften doppelt sein -- bitte nachholen."

Beides stimmte. Der zweite Satz stimmte weit mehr, als er sollte.

### Erst das Rezept, und es lag im Bild selbst

Der Erstbestand war schon umgewandelt angekommen; wie, hatte niemand aufgeschrieben. Im Repo stand
nichts, im Shell-Verlauf nichts, und `sips` traf es auf Anhieb nicht.

Die Antwort steht in den Dateien. Ein JPEG trägt seine **Quantisierungstabellen** mit sich, und
die sind ein Fingerabdruck der Einstellung: Wer Pillow mit jeder Qualität von 60 bis 100 einmal
laufen lässt und vergleicht, bekommt eine Zahl. Vier Referenzdateien, viermal dieselbe Antwort --
**Qualität 92**, Subsampling 4:4:4. Mit `optimize=True` kam die erste Datei bitgleich heraus.

Gemessen an den 19 Dateien, für die beide Fassungen vorliegen: **vier bitgleich, achtzehn
pixelgleich.** Die neunzehnte, `Weidenstieg/Straszenauffahrt`, hat jemand von Hand umgewandelt,
bevor es ein Rezept gab. Die Gegenprobe mit Qualität 90 trifft keine einzige.

Das Rezept liegt jetzt als `tools/to_jpeg.py` im Repo, mit sieben Tests -- Punkt 46 in
`decisions.md` sagt, warum es festgeschraubt gehört und nicht nachjustiert wird.

**Ein Fallstrick nebenbei**, gefunden vom eigenen Test: Mit `optimize` will libjpeg das ganze Bild
in einem Block, und Pillow schätzt diesen Block auf ein Byte je Bildpunkt. Ein Foto bei Qualität
92 braucht ein Drittel davon -- die Holmer Scans haben es deshalb nie gemerkt. Ein kleines Bild
voller feiner Struktur überläuft die Schätzung, und das Speichern bricht ab mit „broken data
stream when writing image file". Ein Testbild aus Pixelrauschen fiel sofort darauf herein, ein
echtes Foto nie. Der Test heißt jetzt nach dem Fall.

### Dann die Zahl, mit der niemand gerechnet hatte

Der Import erkennt Dubletten am SHA-256. Eine zweite Umwandlung desselben TIFF trägt andere
Metadatenblöcke, also greift er dort nicht -- verglichen wurde deshalb der **Bildinhalt**: erst
pixelgenau bei gleichen Kantenlängen, das siebt fast alles weg.

Von den 89 umgewandelten Dateien waren 25 Dubletten, 23 davon mit Abweichung exakt 0,00. Nach
Namen wäre das zweimal danebengegangen: `Heimatmuseum Holm (1).tif` hat keinen Namensvetter und
ist trotzdem eine Dublette, die 51 PNG der Museumsscheune heißen `01.png` bis `51.png` wie ein
Dutzend Fotos anderswo und sind trotzdem alle neu.

Und dann derselbe Vergleich über **alle 619** statt nur über die 89:

**223 zeigten ein Bild, das schon im Bestand stand.**

Der Grund liegt im XMP: `x:xmptk='Image::ExifTool 11.65'`. Das Museum hat seinen Bestand durch
ExifTool laufen lassen und dabei die Metadaten neu geschrieben. `P4139301.JPG` liegt alt mit
1 848 144 Bytes vor, neu mit 1 843 343 -- dieselben Bildpunkte, andere Bytes. **Ein Diff über
Bytes ist kein Diff über Bilder** (`decisions.md`, Punkt 47), und damit war die Zusage im Backlog
hinfällig, der Abgleich erledige sich über den SHA-256 von selbst. Er hätte 223 zweite
Fassungen angelegt.

Ein zweiter, grober Durchgang über 32x32-Graustufen fand sechs weitere, die beim Neuausspielen
auch die Größe geändert hatten -- darunter eine **Sporthalle in 3052x2289, die im Bestand nur
mit 1024x768 liegt.** Der Abstand zwischen Treffer und Nicht-Treffer war dabei kein Ermessen: 212
Treffer bei exakt 0,00, der höchste bei 3,01, der nächste Nicht-Treffer bei 56.

### Der eigentliche Wert lag woanders

Das Museum hat **katalogisiert**. Aus „Ohlsen Optik" wurde „Betriebsgebäude der Firma
Ohlsen-Optik"; ein Foto trägt jetzt „Hof Hinrich Petersen mit Eternitdach nach dem Bombenangriff
1943", wo vorher nichts stand. Und `Im Ort 13` wurde zu `Im Ort 16, Hof Rissler` -- eine
korrigierte Adresse.

Ein blindes Übernehmen hätte dabei mehr zerstört als gebracht, und die drei Gründe sind alle
still:

1. **Das Archiv führt Titel und Beschreibung als dasselbe Feld.** ExifTool hat denselben langen
   Text in beide geschrieben. Unsere Titel sind kurz und von Hand gesetzt -- 815 davon aus Punkt 41.
2. **Gerätetexte stehen darin wie Beschreibungen.** „Intel(R) JPEG Library, version [1.51.12.44]"
   wäre **22-mal** zurückgekommen. Genau das hatte Punkt 41 entfernt.
3. **Die Zeilenenden unterscheiden sich** (`\r\n` gegen `\n`). Ohne Vereinheitlichung sieht
   identischer Text verschieden aus.

Von 79 vermeintlichen Treffern blieben nach diesen drei Filtern **41 Schreibvorgänge**: 34 leere
Beschreibungen gefüllt, 4 Titel gesetzt (nur wo Titel *und* Beschreibung leer waren und der Text
unter 60 Zeichen blieb), 3 Beschreibungen ersetzt. Jede steht im Änderungsprotokoll und ist
einzeln zurücknehmbar.

**Drei Fotos blieben liegen, mit Namen und Grund** -- sie stehen jetzt in Punkt 1. Bei Foto 17
setzt das Archiv nur die Adresse dagegen, die ohnehin am Foto steht; bei 218 sind wir genauer als
das Archiv; bei 398 liest das Archiv den Namen anders („Harmsen" statt „Harms") und hängt eine
Leihgeberadresse an, die nach Punkt 36 in die Herkunft gehört.

### Was der Bestand jetzt ist

395 Fotos aufgenommen, 0 abgewiesen. **1324 Fotos, 1320 auf der Karte** -- alle 395 neuen sind
verortet, 221 hausgenau. Der Zeitschieber läuft von 1884 bis 2024.

Die Zusage, dass der Import nur anlegt und nichts Bestehendes anfasst, ist **nachgemessen und
nicht geglaubt**: die 929 alten Zeilen aus der Sicherung Spalte für Spalte gegen die Datenbank
gehalten, null Unterschiede, null verschwundene Fotos, null veränderte Schlagwortzuordnungen.

Nebenbei fiel `Lehmweg/00 div/` auf. Als Hausnummer gelesen wird daraus **„Lehmweg 0"** -- eine
Adresse, die es nirgends gibt, und weil in dem Namen eine Ziffer steht, hätte der
„Hilf mit"-Bereich nie angeboten, sie richtigzustellen. „00" ist der Ablagekorb des Archivs;
`split_housenumber` weiß das jetzt.

**Was der Stand noch enthält, ist ungehoben:** 251 der 395 neuen Dateien tragen einen Ort im XMP,
und `services/exif.py` liest kein XMP. Bei 40 der zurückgestellten weicht er von unserem
Ortsnamen ab, oft um eine Hausnummer, die uns fehlt. Das ist der neue Punkt 55.

### Und dann standen die langen Titel da

*Noch am 16. August, unmittelbar danach.* Die Rückmeldung kam sofort: „Jetzt sind ein paar sehr
lange Titel hinzugekommen, teilweise auch mit Jahreszahl im Titel." Die Frage dahinter war, welche
Schritte der Bereinigung von Punkt 41 sich auf die 395 neuen anwenden liessen.

Nachgezählt sah es harmlos aus: acht Titel über 60 Zeichen, neunzehn mit einer Jahreszahl. Die
Zahl daneben war die eigentliche:

**323 der 395 trugen den Adressabklatsch, den Punkt 41 an 815 Titeln entfernt hatte.**

127 hiessen genau wie ihre Adresse -- „Am Felde 31" über „Am Felde 31" --, 196 waren „Adresse,
Zusatz". Das ist kein Zufall und war kein neuer Fehler: `apply_folder_meta` setzte den Titel
weiterhin auf `meta.title`, also „Straße Hausnummer, Zusatz". Punkt 41 hatte den Bestand
aufgeräumt und die Ursache stehen lassen; die nächste Lieferung war damit die nächste
Bereinigung. `decisions.md`, Punkt 48.

Drei Regeln sind deshalb in den Import gewandert, jede mit Test und Gegenprobe:

- **Der Ordnertitel ist der Zusatz**, nicht die Adresse davor. Nennt der Ordner nur eine Nummer,
  bleibt der Titel leer.
- **`TITLE_MAX` fällt von 120 auf 60.** Die Zahl ist gemessen: Von den 781 Titeln, die das Museum
  von Hand gesetzt hat, überschreitet **keiner 58 Zeichen**, der Mittelwert liegt bei 13.
- **Der Name der Scannersoftware landet in keinem der beiden Felder.** „Intel(R) JPEG Library,
  version [1.51.12.44]" kam als Titel von 35 Fotos. Anders als eine zu lange Bildunterschrift darf
  er auch nicht in die Beschreibung ausweichen -- das schöbe denselben Unsinn eine Zeile tiefer,
  wo er im Kiosk unter dem Bild steht.

Dazu die Einmalaktion über die 395: **423 Felder**, in sechs Schritten, jeder Schritt der Reihe
nach, weil erst nach dem Abschneiden des Adressvorsatzes feststeht, welcher Titel wirklich zu lang
ist. Nichts ging dabei verloren -- was aus einem Feld verschwand, stand danach entweder woanders am
Foto oder war nie eine Aussage über das Foto, und jede Änderung steht mit ihrem alten Wert im
Änderungsprotokoll.

### Der Trockenlauf hat den teuersten Fehler gefangen

Der Datierungsschritt folgte Punkt 37: eine Jahreszahl datiert nur, wenn ein Datumswort davorsteht.
Er meldete 13 Fotos. Zwei davon lauteten:

    ca. 1970 wurde dieses Haus abgerissen und durch ein Mehrfamilienhaus ersetzt

Das Datumswort steht sauber davor. Nur datiert die Zahl den **Abriss**, und die Aufnahme liegt
zwingend davor -- sonst gäbe es das Haus auf dem Bild nicht. Zwei Fotos wären auf das Jahr ihres
eigenen Verschwindens datiert worden und danach nie wieder gefragt worden.

Punkt 37 hatte die Warnwortliste zugunsten des positiven Musters verworfen, weil eine Warnwortliste
nie fertig wird. Das stimmt -- gebraucht werden trotzdem beide, und sie tun Verschiedenes: Das Wort
davor sagt, *dass* eine Zahl ein Datum ist, das Wort dahinter, *wovon*. Und der alte Einwand trifft
nur eine Richtung: **Eine Liste, die ausschließlich ablehnt, darf unvollständig sein.**
`decisions.md`, Punkt 49.

Beim ersten Anlauf griff der neue Wächter nicht, und auch das war lehrreich: Er sah nur das
*erste* Ereignis im Text. Dort stand „1968 wurde der Hof ausgesiedelt, ca. 1970 abgerissen" -- eine
andere Jahreszahl, also kein Treffer. Über alle Ereignisse gesucht, fiel es.

### Was am Ende dastand

**Kein Titel im Bestand ist länger als 58 Zeichen**, über alle 1004 hinweg, der mittlere hat 13.
Null Adressabklatsch, null Gerätetexte. Die Datierung wächst von 160 auf 171, der Zeitschieber
reicht bis 2025.

Ein Schritt der Liste lief ins Leere, und die Zahl davor war falsch gemessen: „13 Hausnummern, die
der Ortsindex nicht kennt" zählte auf exakte Übereinstimmung und übersah, dass der Import längst
`address_near` benutzt -- die Nachbarnummer-Regel aus Punkt 41. **Alle 221 Fotos mit Hausnummer
liegen hausgenau**, es war nichts nachzuschärfen.

### Zwei Meldungen aus dem Museum, und beide zeigten auf dieselbe Zeile

*Ebenfalls 16. August 2026.* „Du hast den Pfad an einigen Stellen nicht in die Herkunft
übernommen" -- mit einem Beispiel, `ee44c8ae`, und der Angabe, wie es lauten soll.

Es waren **265 Fotos**, und sie hatten alle dasselbe gemeinsam: Ihre Datei nannte selbst eine
Herkunft. `apply_folder_meta` schrieb den Archivpfad nur in ein *leeres* Feld und stand damit vor
jeder Angabe, die jemand schon gemacht hatte -- „Familie Boysen", „Sammlung Jan Wendt",
„August Möller".

**Die Regel war genau falsch herum.** Wer ein Foto geliehen hat, steht in der Datei und ist
gesichert. Wo es im Archiv lag, steht nur im Pfad -- und der geht beim Import verloren, denn im
Bestand heißt die Datei nach ihrem SHA-256. Von den beiden Angaben fehlte die, die sich nie
wiederherstellen lässt. `decisions.md`, Punkt 50.

Zugeordnet wurden die 265 über genau diesen SHA-256: beide Archivordner liegen noch auf der
Platte, jede Datei einmal gehasht, **265 von 265 gefunden**. Die Regel im Import hängt den Pfad
jetzt an, statt zu schweigen; ein Test und seine Gegenprobe halten das fest.

### Und der Bildnachweis, der an einer runden Zahl endete

Die zweite Meldung: „Der Bildnachweis ist bei einigen kaputt, da steht ‚Förderkreis für Kultur und
Brauc'."

Das sieht nach einem Tippfehler aus und ist keiner. **Die Zeichenkette ist genau 32 Zeichen lang**,
und 32 ist die Längengrenze des IPTC-Feldes 2:80. Nicht wir haben gekürzt -- das Programm, das
die Datei beschriftet hat, hat an seiner Feldgrenze aufgehört, und wir haben es unbesehen
übernommen. 19 Fotos, ersetzt durch den vollen Namen.

**Beim Nachzählen fiel die Probe für den ganzen Fall gleich mit an:** Ein Blick auf Zeichen- und
Bytelänge der häufigsten Werte eines Textfeldes zeigt so etwas sofort. Es war der einzige;
„August" bei neun Fotos ist mit sechs Zeichen keine Feldgrenze, sondern eine unvollständige
Eingabe und gehört zu Punkt 1. `decisions.md`, Punkt 51.

## Was auf dem Weg verloren ging

*16. August 2026, nach vier Rückfragen des Museums.* Die erste lautete: „Hast du bei der
Umwandlung nach JPG die Metadaten mitgenommen?"

**Nein.** Farbprofil und Auflösung ja, EXIF, IPTC und XMP nicht -- Pillow schreibt diese Blöcke
nur, wenn man sie ausdrücklich übergibt. Nachgezählt: 12 der 89 umgewandelten Dateien trugen
Metadaten, alle 12 sind importiert.

**Der Ausfall war unsichtbar, und das ist der Kern.** Der Import setzt
``credit=info.credit or settings.import_credit`` -- die Vorgabe aus der ``.env`` springt ein, wenn
die Datei nichts sagt. Fünf Fotos trugen danach „Sammlung Heimatmuseum Holm", wo „Hubert Wulf"
hätte stehen müssen. Kein leeres Feld, keine Meldung, nichts zu sehen: **wo eine Vorgabe die
Lücke füllt, wird aus einem Verlust eine Behauptung.** `decisions.md`, Punkt 52.

Dazu verloren: eine Beschreibung („Collage von verschiedenen Häusern in der Niederstraße"), vier
Herkunftsangaben („CD Niederstraße Holm - alte Häuser - FW -2002") und, in einer nicht importierten
Datei, eine **GPS-Koordinate**.

### Der Weg dorthin ging durch zwei falsche Annahmen

Die erste: das IPTC eines TIFF liege im Photoshop-Block, Tag 34377. Bei 25 Dateien stimmt das --
bei `Heimatmuseum Holm (1).tif` sind darin aber nur 28 Byte, und die IPTC-Felder stehen in Tag
33723. Pillows eigener Leser holt sie von dort, und zwar **an seinem eigenen verstümmelten Wert
vorbei**, direkt aus den Rohbytes.

Daraus wurde die Lösung: Der Block wird nicht kopiert, sondern **aus dem zurückgeschrieben, was
``getiptcinfo`` liefert** -- dieselbe Funktion, mit der der Import die Datei später liest. Damit
ist der Rundlauf per Konstruktion wahr und nicht per Hoffnung.

Die zweite Annahme: man könne das EXIF eines TIFF einfach übernehmen. Kann man nicht -- dessen
erstes Verzeichnis ist Struktur (`StripOffsets`, `RowsPerStrip`), und `tobytes()` scheitert an
einer der Holmer Dateien. Es wird deshalb aus einer Liste neu gebaut: die neun Tags, die etwas über
das Bild sagen, plus die beiden Unterverzeichnisse für EXIF und GPS.

### Die Probe, die zählt

Nicht „sind die Bytes mitgekommen", sondern **„liest unser eigener Leser aus der Kopie dasselbe wie
aus der Quelle"**. Über alle 89 Dateien: **64 von 64 lesbaren kommen unverändert durch**, und zwei
Läufe geben denselben SHA-256.

Die übrigen 25 waren nicht lesbar, und das war der zweite Fund des Tages.

### Ein TIFF, das den ganzen Importlauf beendet hätte

`read_image_info` warf bei 25 der Archivscans einen `TypeError`: Ihr XMP-Paket liegt in einem
Zahlen-Tag, Pillow gibt Zahlen zurück, und jeder spätere `getexif()` jagt einen regulären
Ausdruck darüber.

``import_file`` fängt `OSError` und `ValueError`. **Einen `TypeError` fängt es nicht** -- eine
einzige solche Datei hätte also nicht sich selbst, sondern den ganzen Lauf beendet. Und TIFF ist
ein erlaubtes Format; der Ordner am Stick darf eines enthalten.

Entschärft wird es jetzt in `exif.open_image`, durch das **jeder** Leser geht: `thumbnails` lief
über `ImageOps.exif_transpose` in dieselbe Falle, einen Schritt weiter. Der Test baut das TIFF
nach, statt eine Fixture einzuchecken.

## Punkt 55, beantwortet mit Nein

*16. August 2026, nachdem der Gesamtbestand vorlag.* Das Vorgehen sah fünf Schritte vor, und der
dritte hiess **„erst messen, dann bauen"**: Bevor `services/exif.py` XMP lesen lernt, sollte
feststehen, ob es sich lohnt. Es hat sich nicht gelohnt -- und das ist der Wert des Schritts.

### Zuerst: der gelieferte Diff war vollständig

`01 Orte/Straßen` enthält 1322 Bilddateien. 1034 liegen byte-identisch bei uns. Die übrigen 288
sind **restlos erklärt**: 199 sind die zurückgestellten Dubletten -- neuere Byte-Fassungen von
Fotos, die wir haben --, 89 sind die TIFF, PNG und WEBP, aus denen wir JPEG gemacht haben. **Null
Dateien in keinem von beiden.**

Damit war die große Sorge vom Tag zuvor ausgeräumt: Der Diff des Museums war über Hashes
gerechnet und hat nichts übersehen. Es versteckt sich kein zweiter Import.

### Dann: was im XMP wirklich steht

1189 der 1322 Dateien tragen XMP. Die Felder klangen vielversprechend -- 874 Ortsangaben, 534
Beschreibungen, 410 Fotografen. Angesehen sind es andere Dinge:

* `dc:creator`: **„unbekannt"** und **„Winter"**. Für „unbekannt" gibt es die Regel seit dem
  Erstimport, 82 Fotos trugen es wörtlich.
* `dc:description`: **„Gebäude"**, **„Abriss & Neubau"**, **„Winterspaziergang"** -- das Archiv
  nutzt das Beschreibungsfeld als Kategorie. Die 352 Fälle, die ein leeres Feld gefüllt hätten,
  wären zum großen Teil Kategoriewörter unter dem Bild gewesen.
* `Iptc4xmpCore:Location`: **515-mal genau das, was der Ordner schon sagt.**

Beim Ort, dem stärksten Feld, bleiben nach Abzug des Bekannten **26 Fotos, die eine Hausnummer
gewinnen könnten**. Neun davon tragen denselben Wert „Am Felde 5" -- derselbe Stapelwert, der als
veraltete `photoshop:Location` auch auf Fotos unter den Nummern 9, 10, 16 und 31 klebt. Zwei
widersprechen dem Ordner, einer nennt statt einer Nummer „Am Sportzentrum Geräteraum".

**Übrig bleibt eine Handvoll.** Dafür den Leser umbauen, zwei widersprüchliche Ortsfelder
gegeneinander entscheiden und 259 Konflikte vorlegen -- nein. `decisions.md`, Punkt 53; Punkt 55
ist aufgelöst und seine Nummer vergriffen.

### Und wieder war der Nebenfund der Ertrag

Beim Vergleich der Ortsangaben mit den Ordnernamen fiel **`Hörnstraße/Hörnstraße 14`** auf: ein
Ordner, der seine Straße wiederholt. `split_housenumber` sieht keine führende Ziffer, macht
daraus einen *Namen*, und das Foto hiess **„Hörnstraße 14" über der Zeile „Hörnstraße"** -- genau
der Adressabklatsch, den Punkt 48 zwei Stunden vorher abgeschafft hatte.

Ein Ordner, ein Foto. Die Regel trotzdem in den Code, weil sie zwei Zeilen kostet und dieselbe ist:
Wiederholt der Unterordner die Straße, wird sie abgeschnitten -- **aber nur, wenn dahinter
wirklich eine Hausnummer steht.** Sonst wäre aus „Twietenhof" unter „Twiete" ein „nhof" geworden;
der Vorsatz allein ist zu lose als Grund. Das Foto steht jetzt hausgenau, 15 m von seiner
EXIF-Koordinate entfernt.

### Ein Messfehler von mir, unterwegs

Der erste Durchgang fand **null** solcher Ordner. Der Grund lag nicht in den Daten: macOS liefert
Dateinamen in zerlegter Unicode-Form, „Hörnstraße" aus dem Dateisystem ist also nicht dieselbe
Zeichenkette wie „Hörnstraße" aus dem Ortsindex, und `startswith` sagte nein. `place_service.normalize`
fängt das ab -- mein Vergleichsskript daneben tat es nicht.

## Punkt 42: 44 Gruppen, und die Maschine durfte nicht entscheiden

*16. August 2026.* Der letzte Schritt des Vorgehens, und der einzige, bei dem die Zahl kleiner war
als befürchtet.

Der SHA-256 erkennt eine Kopie der Datei, nicht denselben Papierabzug zweimal gescannt. Gesucht
wurde deshalb mit einem **Differenzhash über 256 Bit** auf den 240er Vorschaubildern, die ohnehin
schon dalagen: 876 000 Paare, ein XOR je Paar, wenige Sekunden.

**44 Gruppen über 95 Fotos** -- sieben Prozent des Bestands. 40 Paare, drei Dreier, ein Sechser.

### Die Schwelle wurde angesehen, nicht gewählt

Sechzig Paare als Kontaktblatt nebeneinandergelegt und durchgeblättert. Bis Abstand 12 ist es
zweifelsfrei dasselbe Bild; bis 30 fast immer; und selbst bei 37 bis 40 ist die Mehrheit noch eine
Dublette. **Das Signal reißt nicht ab, es wird unscharf** -- also eine großzügige Vorgabe und
ein Mensch am Ende.

### Drei Gruppen zeigten, warum

* **Dieselbe Grundsteinlegung an zwei Adressen**: Foto 810 auf Schulstraße 9, Jahr 1971; Foto 580
  auf Lehmweg 8, Jahr 1968. Eines war falsch abgelegt, und ohne die Dublettensuche hätte das
  niemand nebeneinander gesehen. Zwei weitere Gruppen ebenso.
* **Das kleinere Bild trägt den Bildtext** „Dörpshus vor dem Brand", das größere nicht.
  Auflösung ist dort das falsche Kriterium -- genau der Fall, den der Backlog vorausgesagt hatte.
* **Ein Lastwagen** steht auf einem von drei sonst gleichen Straßenbildern. Zwei Momente.

### Was daraus wurde

Eine Entscheidungsliste mit 44 Zeilen ans Museum, 36 Vorschläge und 8 zum Ansehen. Zurück kamen
drei Entscheidungen -- welche Adresse bei zweien richtig ist, und welche der sechs Farbfassungen
bleibt -- und ein „sonst alle fraglichen Gruppen behalten".

**39 Gruppen zusammengeführt, 45 Fotos aus der Ausstellung, 58 Felder und 11 Schlagwörter
übernommen, bevor etwas verschwand.** Der Bestand steht bei 1279 sichtbaren Fotos, 1275 auf der
Karte.

Der Finder liegt als `services/similar.py` im Repo, mit `python -m app.cli dubletten`. Er findet
und schreibt nichts.

### Ein Fehler in genau der Zeile, die es zu können glaubte

Beim ersten Lauf des fertigen Befehls meldete er **eine** Gruppe, wo fünf stehen mussten. Die
Union-Find-Struktur fasst zusammen, indem sie jedem Foto eine Wurzel gibt -- und mein Einsammeln
nahm nur die Nicht-Wurzeln mit. **Aus jeder Gruppe fiel damit ein Foto**, und ein Paar schrumpfte
auf eines und verschwand aus der Meldung. Am Bestand hätte das ausgesehen wie „keine Dubletten
gefunden".

Aufgefallen ist es nur, weil ich den Befehl direkt nach dem Zusammenführen an den fünf bewusst
behaltenen Gruppen ausprobiert habe und die Zahl nicht stimmte. Der Test dazu heißt jetzt
`test_beide_fotos_stehen_in_der_gruppe`.

## Zwei kleine Punkte, und einer hatte einen Fallstrick

*16. August 2026 -- Punkt 50 und 51.*

**Punkt 51 war eine Zeile.** Unter dem Zahlenfeld stand „Zurück zur Karte" -- das sagt, wohin es
geht, aber nicht, was passiert. Wer schon Ziffern getippt hat, liest dort keine Abkürzung zum
Verwerfen. Jetzt steht dort **„Abbrechen und zurück"**: erst die Handlung, dann das Ziel. Am
laufenden Kiosk nachgesehen.

**Punkt 50 sah nach zwei Feldern aus und hatte eine Entscheidung in sich.** Ein Schlagwort für den
ganzen Stapel, durchgereicht bis `add_tags` -- so weit die Aufgabe. Der Fallstrick stand im Backlog
und hat sich beim Bauen bestätigt: **Alle anderen Stapelangaben füllen nur, was leer ist.** Jahr,
Ort, Bildnachweis, Herkunft geben der Datei den Vortritt, weil jedes dieser Felder einen Wert hält
und Füllen also Entscheiden hiesse.

Eine Schlagwortliste hält keinen Wert, sondern eine Menge. Wer hundert Fotos aus einem Ordner
„Feuerwehr" hochlädt, will nicht entweder das Stapelwort oder das der Datei, sondern beides. Das
Stapelschlagwort tritt deshalb **neben** das der Datei, statt ihm zu weichen -- und damit gibt es
drei Quellen, deren Reihenfolge jetzt im Code steht statt in jemandes Kopf. `decisions.md`,
Punkt 55.

Beides gilt für den Upload **und** für den Stick, weil der Stick der Weg des Museumsteams ist.
Vier Tests, zwei Gegenproben: eine gegen das Übernehmen selbst, eine gegen die Kommazerlegung.

Die Liste unter dem Import bekommt **kein** viertes Feld -- der Backlog nannte das ausdrücklich
eine Frage und keine Aufgabe, und für den Einzelfall gibt es den Foto-Editor, der ein
Schlagwortfeld längst hat.

## Punkt 1: der Erstbestand, in zehn Schritten durchgesehen

*18. August 2026 -- der letzte Punkt, der seit dem ersten Import offenstand.*

Punkt 1 war seit dem Erstimport der älteste offene Eintrag und zuletzt eine Sammelstelle: Zahlen
aus drei verschiedenen Monaten, Beobachtungen ohne Auftrag, Fälle, die längst erledigt waren,
neben solchen, die nie jemand anfassen konnte. Er wurde erst **geordnet**, dann abgearbeitet.

### Die Zerlegung war die halbe Arbeit

Der Punkt vermischte zwei Arten Arbeit, und das war der Grund für die Unübersichtlichkeit: Regeln,
die ein Rechner anwenden und gegenprüfen kann, und Fälle, bei denen jemand das Bild ansehen und
den Ort kennen muss. Getrennt waren es zehn Schritte -- und **fünf davon standen vorher gar nicht
im Backlog**, sondern kamen beim Nachmessen heraus.

### Was der Rechner konnte: 1.1 bis 1.5

**1.1 -- 16 Beschreibungen trugen ihren eigenen Text zweimal**, durch eine Leerzeile getrennt. Eine
Naht aus dem Metadatenabgleich vom 16. August, bei der zwei Quellen desselben Archivs aneinander-
gehängt wurden, statt sich zu decken. Auf dem Kiosk stand der Absatz doppelt unter dem Bild.

**1.2 -- 45 Beschreibungen, und die Zahl zeigte in die falsche Richtung.** 137 Beschreibungen
enthielten den Titel des Fotos; **131 davon sagen mehr als er** -- „Funkmast" im Titel, „Errichtung
des Funkmastes" in der Beschreibung. Die zu streichen hätte Angaben vernichtet. Wortgleich waren
zehn. Von 92 Adress-Echos begannen 37 mit der Adresse; 34 sind abgetrennt, zwei blieben stehen,
weil ihre Beschreibung „Lehmweg 11 und 11a" sagt und damit mehr weiß als das Ortsfeld, das nur
eine Hausnummer trägt.

**1.3 -- 55 Fotos datiert, 14 auf den Monat geschärft.** Die Bereinigungsrunde vom 11./12. August
hatte im Text nach **vierstelligen Jahreszahlen** gesucht. Alles andere, womit Menschen datieren,
lief ihr durch: „80er Jahre", „in den 1930gern", „Winter 63", „Foto aus der Nachkriegszeit". Das war
die größere Hälfte. Die ergiebigste einzelne Fundstelle war eine Ordnernotiz auf achtzehn Fotos.
50 weitere Funde sind **begründet nicht** übernommen: 26 datieren ein Ereignis statt der Aufnahme,
15 den Stand des Archivs, eines das Einscannen. `decisions.md`, Punkt 56.

**1.4 -- acht Titel nannten ein Programm statt einer Sache**, zweimal die Scannersoftware, sechsmal
„Google Maps 2026". Kein neuer Titel ist erfunden: jeder kam aus einem Schlagwort des Fotos selbst
oder aus dem Rest seines eigenen Titels. Dabei kam ein Fehler heraus, den keine Regel findet -- die
sechs Kartenbilder waren dem gutgeschrieben, der sie eingestellt hat, nicht der Quelle.

**1.5 -- elf Schlagwörter waren Sätze** aus der Kommazerlegung von Punkt 41. Neun sind **wörtlich**
in die Beschreibung übernommen, zwei fielen ersatzlos weg, weil sie nur wiederholten, was Ort und
Datierung schon sagen.

### Der Fehler, der die Lehre trug

Mitten in 1.3 fiel auf, dass **„Notiz: Schule 78" undatiert dastand, während „Notiz: 1978" an drei
Nachbarfotos längst als Datierung akzeptiert war.** Dieselbe Archivnotiz, dieselbe Aussage, zwei
Zeichen kürzer -- und meine Suche kannte das zweistellige Jahr nur hinter einem Jahreszeitwort.
Elf Fotos hingen daran.

Das ist derselbe Fehler, den die Runde im August gemacht hatte, eine Ebene tiefer und von mir
wiederholt: **Bei einer Suche nach Mustern bestimmt die Form des Musters den Befund, nicht der
Bestand.** Wer nur eine Schreibweise sucht, misst seine eigene Annahme. Die Gegenprobe ist billig --
nachsehen, ob dieselbe Aussage anderswo in einer Schreibweise steht, die man schon akzeptiert hat.
`decisions.md`, Punkt 56.

### Was dabei herauskam

| | vorher | nachher |
|---|---|---|
| Fotos ohne Jahr | 804 | **749** |
| monatsgenau datiert | 3 | **17** |
| jahrzehntgenau datiert | 5 | **35** |
| Schlagwörter | 291 | **281** |

Die Genauigkeit `decade` war vorher praktisch ungenutzt, obwohl das Datenmodell sie von Anfang an
trägt -- weil niemand nach Jahrzehnten gesucht hatte.

### Was bleibt, ist Kuratieren, kein Backlogpunkt mehr

942 Fotos ohne Beschreibung, 310 ohne Titel, 4 ohne Ort, drei namentlich vorgemerkte Fälle und die
Frage, ob die 281 Schlagwörter als Filter taugen. Das ist keine Aufgabe mit Ende, sondern die
laufende Arbeit am Bestand: Wer das Bild ansieht und den Ort kennt, schreibt in einer Minute, was
keine Regel je finden wird. Die Frage nach den Schlagwörtern entscheidet sich ohnehin erst mit
Punkt 30, wenn daraus ein Filter wird.

## Punkt 56: der aufgehende Cluster, und zwei stille Nachbarn

*18. August 2026 -- eine Animation, die aus der Ecke kam, und warum.*

Wer auf einen Kreis mit einer Zahl tippt, zoomt so weit hinein, dass die Gruppe zerfällt. Was dann
erschien, **flog aus der oberen linken Ecke der Karte herein**. Gewünscht war das Gegenteil: aus
dem Punkt herauswachsen, den der Finger gerade berührt hat.

### Kein Gestaltungsmangel, sondern ein Kaskadenkonflikt

Gemeint war nie ein Flug, sondern ein Aufblenden an Ort und Stelle -- `marker-enter` setzte
`opacity: 0` und `transform: scale(0.88)`. Nur schreibt MapLibre die Position seiner Marker als
`transform: translate(...)` in den **Inline-Stil desselben Elements**. Eine Animation steht in der
Kaskade über dem Inline-Stil: für 180 ms gewann `scale(0.88)`, die Verschiebung war weg, das
Element stand bei `translate(0, 0)` -- der linken oberen Ecke des Kartencontainers.

**Derselbe Konflikt hatte einen zweiten Effekt still ausgeschaltet.** `.marker:hover` setzte
`transform: scale(1.08)`. Eine gewöhnliche Regel steht in der Kaskade *unter* dem Inline-Stil --
sie verlor und tat gar nichts, seit es Marker gibt. Zwei Symptome, entgegengesetzte Richtungen,
eine Ursache: **zwei Ebenen stritten sich um eine Eigenschaft an einem Element.**

Die Lösung ist eine Hülle. Aussen die Verschiebung durch die Karte, innen alles, was das
Stylesheet will. Darauf lässt sich das Gewünschte aufsetzen: Beim Antippen ist bekannt, welcher
Kreis gemeint war; sein Ort in Bildschirmpunkten minus der Ort des neuen Markers ergibt den Vektor.

### Denselben Fehler noch einmal gemacht

Der erste Anlauf legte die Animation auf die Hülle -- also wieder auf genau das Element, das
MapLibre verschiebt. Der Konflikt bestand unverändert fort, nur um den Versatz verschoben.
Aufgefallen ist es nicht beim Ansehen, sondern beim **Nachmessen**: Die Startpunkte der dreizehn
Marker lagen 483 Pixel auseinander, statt auf einem Punkt. Nach der Korrektur -- Animation auf den
Marker, Hülle für die Karte -- ist die Streuung **null**, alle siebzehn starten auf `(288, 330)`,
der Kartenmitte, wo der angetippte Kreis nach dem Heranfahren steht.

**Eine Animation lässt sich nicht durch Hinsehen prüfen.** 320 ms sind zu kurz, um zu erkennen,
ob etwas aus einem Punkt kommt oder aus vier benachbarten. Gemessen wurde am Inline-`transform` der
Hülle, den MapLibre schreibt: Der steht still, während das Innere sich bewegt, und bleibt auch
dann lesbar, wenn der Marker inzwischen ersetzt wurde.

### Und der Kreis, den kein Finger erreicht

Während der Prüfung fiel im Museum auf, dass **ein Vorschaubild einen Kreis verdecken kann**.
MapLibre hängt die Marker in der Reihenfolge an, in der supercluster sie liefert; ein später
gebautes Bild liegt also über einem früher gebauten Kreis. Ein verdeckter Kreis ist nicht
antippbar, und damit ist der einzige Weg zu den Fotos dahinter zu. Umgekehrt kostet ein verdecktes
Bild nichts -- der Kreis darüber führt zu denselben Fotos. **Ein Kreis liegt deshalb immer über
einem Bild.**

Der erste Versuch war eine Stufe zu wenig: Wer etwas berührt, holt es nach vorn, damit die
Vergrößerung nicht am Nachbarn abgeschnitten wird -- und ein berührtes Vorschaubild stieg damit
über jeden Kreis. Gemessen: zwei gerade befreite Kreise waren wieder zu. Jetzt sind es **zwei
Bänder zu zwei Stufen**: Berührtes steigt innerhalb seines eigenen Bandes. Siebzehn von siebzehn
Kreisen sind erreichbar, auch mit einem berührten Bild daneben.

## Punkt 39: der Durchgang von aussen

Am 19. August 2026 ist der Code geprüft worden — der Punkt, der seit Langem verlangte, dass jemand
ohne die Vorgeschichte darüberliest, bevor veröffentlicht wird und bevor das Gerät im Museum steht.
Geprüft wurde Stand `31812f9`: Backend, Frontend, Deployment, Dokumentation und die Tests selbst.

### Der Zustand, gemessen und nicht geschätzt

| Prüfung | Ergebnis |
|---|---|
| `pytest` | 428 grün, 7,7 s |
| `vitest` | 173 grün, 19 Dateien |
| `tsc -b --noEmit` | sauber |
| `prettier --check` | sauber |
| `tools/language_check.py` | 542 deutsche, 1458 englische Kommentare, kein Verstoß |
| `tools/check_anchors.py` | kein toter Anker in acht Dateien |
| `tools/check_settings.py` | acht Einstellungen, alle erreichen den Container |

Die Trennung, auf der das Backend steht — `api/` dünn, `services/` denkend —, ist durchgehalten;
kein Endpunkt trägt Fachlogik. Mehrere Konstanten sind **gemessen und nicht gewählt**: `TITLE_MAX`
an 781 handgesetzten Titeln, die Rangfolge in `services/needs.py` an 612 gegen 116 Fotos, die
Dublettenschwelle an sechzig durchgeblätterten Paaren.

### Die Frage aus dem Punkt selbst, beantwortet

Punkt 39 fragte, ob die Tests prüfen, was sie zu prüfen **vorgeben** — bei Namen, die wie
Zusagen klingen, ist das keine rhetorische Frage. Sie tun es.
`test_dates.py::TestUeberlappung` prüft wirklich die Überlappung, samt Randberührung und samt dem
undatierten Foto, das in keiner Auswahl erscheinen darf; `TestBalkenbreite` prüft die leere
Sammlung, an der eine Division scheitern könnte.

Auch die zweite Sorge des Punktes — Nebenwirkungen zwischen den Zuständen, an reinen Funktionen
nicht zu sehen — ist inzwischen gegenstandslos: `store/kiosk.test.ts` und
`store/contribute.test.ts` prüfen Fokus, die Rückgabe des Zeitraums nach zwei Beiträgen und den
Schalter für die undatierten Fotos in beide Richtungen. Die beiden Fehler vom 8. und 9. August
haben ihre Tests bekommen.

### Drei Fehler, und alle drei fallen beim Benutzen nicht auf

Das ist die Eigenschaft, die sie verbindet, und der Grund, warum ein Durchgang von aussen etwas
findet, was das tägliche Arbeiten nicht findet. Sie wurden Punkt 57, 58 und 59 — und **alle
drei sind noch am selben Tag behoben worden**; siehe unten.

**Der Eingangs-Watcher sichert einen ganzen Durchgang auf einmal.** `session.commit()` steht hinter
der Schleife, während `import_file` jede Datei schon in sich nach `_erledigt/` verschiebt. Eine
Ausnahme mitten im Durchgang nimmt die Zeilen aller vorher gelesenen Fotos mit — und, weil es in
derselben Transaktion hängt, auch das Import-Protokoll, das genau diesen Fall sichtbar machen
sollte. Die Lösung stand die ganze Zeit einen Modul weiter: `import_from_folder` committet in der
Schleife und begründet es sogar.

**Zeitstempel gehen als UTC hinaus und werden als Ortszeit gelesen.** Und das ist der
interessanteste der drei, weil er schon einmal angefasst worden war: Der Commit vom 30. Juli 2026
hat die zweite Uhr beseitigt und für die Übersichtskacheln den Zeitstempel gar nicht mehr gesendet,
sondern Tage — mit einem Kommentar in `schemas.py`, der den Befund wörtlich benennt. Das Problem war
also **bekannt und umgangen, nicht behoben**. Übrig blieben die drei Stellen, die weiterhin einen
rohen Stempel schicken; in der Beitragsliste steht seither an zwölf Besucherbeiträgen eine Uhrzeit,
die zwei Stunden zu früh ist.

**Ein Fehler beim Rendern hinterlässt einen weißen Bildschirm.** Es gibt keine `ErrorBoundary` —
und der Leerlauf-Neustart, der das Gerät sonst von jedem verfahrenen Zustand heilt, hängt in
`MapView` und ist mit dem Absturz weg. Auf einem Gerät ohne Tastatur, ohne Adressleiste und ohne
Reload-Knopf heißt das: die Vitrine steht weiß, bis jemand den Stecker zieht.

### Was der Durchgang über das Umgehen gelernt hat

Der zweite Fehler ist der lehrreiche. Er war nicht übersehen worden — er war **an der Stelle, wo er
auffiel, sauber gelöst** worden, indem der Zeitstempel dort durch eine Tagesangabe ersetzt wurde.
Das war die richtige Lösung für die Kacheln und zugleich der Grund, warum die drei anderen Stellen
liegen blieben: Wer ein Symptom beseitigt, verliert den Anlass, nach den übrigen zu suchen. Der
Kommentar, der dabei entstand, beschreibt die Ursache genau — und stand vier Wochen unbeachtet da.

**Ein Kommentar, der eine Ursache benennt, ist kein Ersatz dafür, sie zu suchen.** Dasselbe Muster
wie beim Erstbestand am 18. August, nur eine Ebene höher: Dort bestimmte die Form des Suchmusters
den Befund, hier bestimmte der Ort des Symptoms den Umfang der Reparatur.

### Der Rest, und was ausdrücklich nicht gefunden wurde

Vier weitere Punkte sind ins Backlog gewandert: die Sicherung, die sechs Module in einer Datei ist
(60); zwei Regeln, die an zwei Orten stehen (61); die drei Prüfungen, die nur von Hand laufen und
keine Zahl nachzählen (62); und die Frage, ob die bestehende Arbeitsweise beim Testen der
Oberfläche als Entscheidung aufgeschrieben gehört (63). Zwei Betriebsbefunde sind an die Punkte 21
und 22 angehängt worden — die Arithmetik hinter „vier Ziffern sind zu wenig" und die ungepinnten
Abhängigkeiten des Backends.

Nicht gefunden wurde ein Fachfehler. Keine der Stellen, die dieses Projekt eigen machen — die
Überlappung, das Scandatum, die Genauigkeit neben der Koordinate, die Vorrangregeln beim Import —
hält nicht, was sie zusagt. Auch ein Verdacht löste sich in Luft auf: `httpx2` in den
Entwicklungsabhängigkeiten sieht nach Vertipper aus, ist aber das echte Nachfolgepaket von `httpx`
aus demselben Haus.

## Punkt 57, 58 und 59, behoben am selben Tag

`687c429` … `7801f1a` · 19. August 2026.

Alle drei Fehler aus dem Durchgang sind noch am selben Tag repariert worden. Jedes Mal lag die
richtige Lösung schon im Repo — einmal einen Modul weiter, einmal als Reflex, der hier falsch
war, einmal als Kommentar, dem vier Wochen lang niemand gefolgt ist.

### Der Watcher: die Regel stand nebenan

`session.commit()` wanderte in die Schleife, wo es in `importer.import_from_folder` seit jeher
steht. Zwei Zeilen, und ein Test, der ohne sie fehlschlägt: Eine Ausnahme beim zweiten Foto darf
das erste nicht mitnehmen. Er prüft in einer **frischen Sitzung** nach, denn genau darum geht es —
steht die Zeile in der Datenbank oder nur im Gedächtnis der abgebrochenen? Dazu die zweite Hälfte
der Zusage: Was liegen blieb, kommt beim nächsten Blick herein.

Bemerkenswert ist nicht der Fehler, sondern dass die Begründung dagegen schon geschrieben dastand:
„Ein halb herausgezogener Stick lässt dann liegen, was schon gelesen wurde, statt nichts." Derselbe
Satz gilt für den Eingangsordner. **Eine Regel wandert nicht von selbst mit, nur weil sie
aufgeschrieben ist.**

### Die Fehlergrenze: der Aufräumreflex war der Fehler

Die erste Fassung war ordentlich gebaut — Zeitgeber als Feld, `componentWillUnmount`, `clearTimeout`.
Und sie tat nichts. Der Bildschirm zeigte die Meldung und blieb dann stehen.

Aufgefallen ist es **nicht beim Lesen, sondern beim Messen**: ein Absturzschalter in `App`, ein
`console.log` vor und nach dem Setzen des Zeitgebers, und die Spur las sich in zwei Zeilen —
„Timer gesetzt", direkt danach „unmount, Timer war 3". Nach dem Fangen baut React den Baum von
Grund auf neu und nimmt die Fehlergrenze mit; das Aufräumen löschte also jedes Mal genau die
Selbstheilung, um derentwillen es sie gibt. Warum der Zeitgeber jetzt stehen bleibt, steht als
Punkt 57 in [decisions.md](decisions.md).

Nachgemessen im Browser, nicht angesehen: `timeOrigin` der neu geladenen Seite minus dem Vermerk
über den letzten Versuch ergab **8003 ms**, und der Navigationstyp war `reload`. Der zweite
Absturz danach zeigte den anderen Satz — „Bitte einmal auf die Schaltfläche tippen" — und lud
nicht noch einmal. Genau die zwei Zustände, die der Entwurf vorsieht.

**Beide Male hätte ein Blick nicht gereicht.** Der Watcher-Fehler braucht eine Ausnahme mitten im
Durchgang, die im Betrieb vielleicht nie eintritt; die tote Selbstheilung sieht aus wie eine
funktionierende, solange niemand acht Sekunden wartet und nachsieht, ob wirklich neu geladen wurde.

### Und Punkt 58: der Marker gehört an das Ende, das die Zone kennt

Der dritte Fehler war der, der am längsten unbemerkt dastand — und der einzige, dessen Ursache
schon einmal aufgeschrieben worden war, ohne dass jemand ihr gefolgt wäre.

Die Wahl bestand zwischen „drei Anzeigestellen im Browser rechnen um" und „das Backend sagt, welche
Zone es meint". Die zweite ist die kürzere und die haltbarere: Ein `UtcDatetime` in `schemas.py`
sagt es einmal, sieben Felder tragen es, und `Changes.tsx`, `ImportLog.tsx` und `Backup.tsx` sind
unverändert geblieben. Die vierte Anzeigestelle, die jemand später dazubaut, ist damit von selbst
richtig.

Am Wert nachgemessen, im Browser und in `Europe/Berlin`:

| | angezeigt |
|---|---|
| `2026-08-05T08:10:58` (vorher) | 5. August um **08:10** |
| `2026-08-05T08:10:58Z` (jetzt) | 5. August um **10:10** |
| `2018-08-28T14:07:18` (Scandatum) | 28. August um 14:07 |

**Die dritte Zeile ist der eigentliche Ertrag.** Das EXIF-Datum bekommt den Marker ausdrücklich
nicht: Es kommt aus einer Kamera oder einem Scanner, die die Wanduhr ihres Standorts schreiben und
von keiner Zone wissen. Wer es mit den übrigen zusammen auf UTC umstellt, verschiebt einen Scan von
14:00 auf 16:00 und erfindet eine Tatsache. Ein Zeitstempel trägt nicht nur einen Wert, sondern
eine Herkunft — dieselbe Einsicht wie bei den Feldern der Fotos, eine Ebene tiefer. Es hat einen
eigenen Test, der ohne die Änderung **als einziger von sechs bestanden hätte**: Was schon richtig
war, muss richtig bleiben.

Daneben lag die zweite Uhr, die der 30. Juli übersehen hatte: `reverted_at` kam aus
`datetime.now()`. Sie steht jetzt als `dates.utc_now()` an einer Stelle und hat einen Namen. Und
zwei Dateinamen, die Menschen im Dateimanager lesen, waren sich uneins — der beiseitegelegte
Ordner schrieb Ortszeit, der Name des heruntergeladenen Archivs UTC; jetzt beide Ortszeit, denn
wer um halb eins nachts eine Sicherung zieht, sucht das heutige Datum.

## Punkt 61: zwei Regeln, und beide lagen anders als notiert

`9eb72cd` · 19. August 2026.

Der Backlogeintrag sagte „zwei Regeln stehen an zwei Orten". Beim Aufgreifen stellte sich heraus,
dass die eine an **drei** Orten stand und die andere gar keine Doppelung war.

### Die Dateiendung: drei Aufrufer, einer davon rechnete

`ALLOWED_FORMATS` in `services/storage.py` sagt, welche Endung zu welchem MIME-Typ gehört. Drei
Stellen brauchen die Umkehrung, und jede beantwortete sie für sich:

- `services/seed.py` baute sich die Tabelle aus `ALLOWED_FORMATS` — richtig, mit Warnung für
  Unbekanntes.
- `api/photos.py` rechnete auf dem String: `mime.split("/")[-1]`, mit `jpeg` und `tiff` von Hand
  zurückgebogen. Das stimmte zufällig mit der Tabelle überein und hätte in dem Augenblick
  aufgehört zu stimmen, in dem ein Format hereinkommt, dessen Endung nicht das Ende seines
  MIME-Typs ist.
- `services/importer.py` liest die Tabelle vorwärts und war nie betroffen.

Jetzt gibt es `suffix_for_mime()`, aus derselben Tabelle abgeleitet. Der Test dazu prüft keine
Beispiele, sondern **die Tabelle gegen sich selbst**: Was der Import ablegen darf, muss die
Auslieferung benennen können. Das ist die Form von Gegenprobe, die ein Auseinanderlaufen nicht
bemerkt, sondern unmöglich macht.

Nebenbei ist ein stiller Fall laut geworden: Ein Foto mit einem MIME-Typ, den dieses Programm nie
geschrieben hat — denkbar aus einer zurückgespielten Sicherung — ergab vorher stillschweigend
einen Pfad, den es nicht gibt. Die Antwort an den Besucher ist dieselbe geblieben, weil sie für ihn
stimmt; im Protokoll steht jetzt, woran es wirklich lag.

### Das Datumsformat: keine Doppelung, sondern drei Entscheidungen ohne Ort

Hier lag der Backlogeintrag schlicht falsch. Er sprach von „drei Fassungen, eine davon tot" und
unterstellte, es sei dieselbe Formatierung. Nachgesehen sind es drei verschiedene, und jede lässt
etwas anderes weg:

| wo | was fehlt | warum |
|---|---|---|
| Sicherungskachel | die Uhrzeit | Eine Sicherung ist ein Tag, keine Minute |
| Besucherbeiträge | das Jahr | Die Liste zeigt, was in dieser Saison hereinkam |
| Import-Protokoll | nichts, aber der Monat ist eine Zahl | Die Spalte ist schmal und in `tabular-nums` gesetzt, damit die Zeilen untereinander stehen |

**Zusammenlegen hätte also etwas gekostet**, nicht gespart — entweder die Ausrichtung im Protokoll
oder die Lesbarkeit in den anderen beiden. Was wirklich fehlte, war ein Ort: Zwei der drei standen
in den Komponenten, die vierte Fassung war exportiert und wurde von niemandem benutzt. Alle drei
liegen jetzt in `admin/format.ts`, mit der Tabelle oben als Kommentar, damit der Nächste sie nicht
„aufräumt".

Ihre Tests prüfen deshalb nicht, wie ein Datum in Berlin aussieht, sondern **was jede Form
weglässt** — und laufen damit in jeder Zeitzone. Die Zone selbst ist seit
[Punkt 58](decisions.md) kein Thema dieser Funktionen mehr.

**Ein Backlogeintrag ist eine Notiz, kein Befund.** Beide Hälften dieses Punktes sahen beim
Aufschreiben anders aus als beim Aufgreifen, und in beiden Fällen war das Nachsehen billiger als
das Vertrauen.

## Punkt 62: die vierte Prüfung prüft etwas anderes als geplant

`8555da0` · 19. August 2026.

Der Punkt hatte zwei Hälften — „die drei Prüfungen laufen nur von Hand" und „sie zählen nicht
nach". Die erste war eine Aufgabe, die zweite entpuppte sich als Fehlschluss.

### Der Ort: `make check` und ein Hook, den man nicht merkt

`make check` bündelt Stil, die Prüfungen und alle Tests, die schnellen zuerst — wer den Stil
verletzt hat, soll das nach zwei Sekunden erfahren und nicht nach zehn. Es hat sich beim ersten
Lauf gleich bewährt und den Zeilenumbruch in der frisch geschriebenen Prüfung selbst bemängelt.

Daneben liegt `.githooks/pre-commit`, und der führt **nur die vier schnellen Prüfungen** aus, keine
Testreihe. Die Überlegung dahinter: Die Tests laufen ohnehin, weil `make test` sie ausführt und
niemand sie vergisst — vergessen wurden genau die vier, die unter einer Sekunde brauchen. **Ein
Hook, den man merkt, wird abgeschaltet.** Er ist versioniert, aber nicht aufgedrängt: einmal je
Klon mit `git config core.hooksPath .githooks`.

Eine CI wäre der nächste Schritt und bleibt liegen, weil sie einen Ort braucht — und der hängt an
Punkt 22.

### Das Nachzählen: gemessen, dann verworfen

Der Plan war, eine Prüfung die Zahlen im Text nachrechnen zu lassen. Das Symptom lag ja vor:
`index.md` nannte „33 Entscheidungen" bei 56 und „21 Punkte" bei 17.

**Die Messung fand etwas anderes als das Gesuchte.** Das Muster „N Punkte" trifft in dieser
Dokumentation vier Stellen, und **keine einzige davon darf berichtigt werden**: Zweimal steht die
alte, falsche Zahl mit Absicht da — als Zitat im Backlogpunkt selbst. Zweimal sind Punkte auf einer
Karte gemeint. Und einmal steht in dieser Datei hier ein Satz, der an seinem Datum stimmte und
stehenbleiben muss.

Eine Zahl in laufendem Text ist fast nie eine Behauptung über den Jetztzustand; sie ist ein Zitat
oder ein Protokolleintrag, und beide werden durch eine Berichtigung falsch. Die zwei Stellen, die
wirklich aktuell sein sollten, haben ihre Zahlen deshalb gestern verloren, statt heute eine Prüfung
zu bekommen.

### Was stattdessen geprüft wird

Die Buchführung des Backlogs über sich selbst — Struktur statt Prosa, mit einer Zusage, die
entweder gilt oder nicht: **Jede je vergebene Nummer ist entweder offen oder vergriffen.** Keine
Lücke, kein Überhang, keine zweimal. Dazu die Übereinstimmung von Tabelle und Fließtext, der Anker
jeder Zeile auf ihren *eigenen* Punkt, und das ausgeschriebene Zahlwort vor der Liste
(„Vierundvierzig Nummern sind vergriffen").

Der Anlass ist Erfahrung: Ein Punkt, der in die Historie zieht, verlangt vier Bearbeitungen an drei
Stellen. An diesem einen Tag ist das viermal passiert.

`decisions.md` bekommt dieselbe Prüfung in schwächerer Form — dort sind Lücken **erlaubt**, weil
Punkt 8 zurückgezogen wurde und seine Nummer mit einer Begründung leer bleibt. Geprüft wird nur,
dass keine Nummer zweimal vorkommt und dass sie aufsteigen. Eine Lücke ist dort eine Aussage, kein
Fehler.

Geprüft ist die Prüfung selbst an neun absichtlich verbogenen Fassungen der beiden Dateien: fremder
Anker, Zeile ohne Abschnitt, Nummer offen und vergriffen zugleich, verschwundene Nummer bei sonst
stimmigem Zahlwort, Nummer jenseits der nächsten freien, umformulierter Satz, doppelte und
vertauschte Entscheidungsnummer. Alle neun fallen auf, die unveränderten Dateien nicht.

## Punkt 63: eine Frage, und die Antwort stand längst im Repo

`1ad98b3` · 19. August 2026.

Der Punkt fragte, ob die bestehende Arbeitsweise beim Testen der Oberfläche als Entscheidung
aufgeschrieben gehört — oder ob stattdessen Komponententests fällig sind. Er ist **aufgelöst**,
nicht erledigt: Es war nichts zu bauen, sondern etwas zu entscheiden.

### Erst messen

Die Behauptung im Backlogeintrag lautete, die Praxis sei „erkennbar Absicht und funktioniert".
Behauptet war das leicht; nachgesehen sieht es so aus: **Jedes `useMemo` in einer Komponente ruft
eine importierte reine Funktion auf** — `offeredDecades`, `buildIndex`, `groupStreets`,
`axisBounds`, `blocksOf(groupByBase(…))`. Sechzehn reine Module tragen die Entscheidungen, rund
fünfundzwanzig Komponenten die Darstellung. Die Praxis hielt also, bevor sie irgendwo stand.

Dabei fiel auf, dass die Regel schärfer ist als „Komponenten werden nicht getestet":
`PhotoLayer.test.ts` prüft `buildIndex` **aus einer `.tsx`-Datei**, ohne etwas zu rendern. Die
Dateiendung ist kein Kriterium. Die Frage ist, ob ein Wert berechnet oder ein Knopf gezeichnet
wird.

### Und dabei eine Lücke gefunden

Der Zeitschieber rechnete die Fingerposition selbst in ein Jahr um — klammern, runden, mitten in
der Komponente. Das ist genau die Sorte Fehler, für die das ganze Vorgehen existiert: Ein
Rundungsfehler wählt 1931, wo der Besucher auf 1932 gezielt hat, und **auf dem Bildschirm sieht
nichts falsch aus.** Die Karte zeigt einfach etwas anderes.

Jetzt ist es `yearAtFraction` in `timeAxis.ts`, die Umkehrung von `fraction` — und der Test prüft
genau das: Jedes Jahr der Achse muss aus seinem eigenen Anteil wieder herauskommen. Die
Fingerposition selbst bleibt in der Komponente, denn wo der Finger ist, gehört dem DOM; was das
bedeutet, gehört der Achse.

Im Browser nachgemessen: Bahn von 333 bis 604, gezogen auf 468 — das sind 49,8 %, auf der Achse
1880 bis 2030 also 1954,7. Auf dem Bildschirm stand danach **1955 bis 2030**.

### Wo die Grenze verläuft

Der Gegenfall aus derselben Messung: Die Größe eines Kreises auf der Karte,
`48 + log10(Anzahl) × 26`, bleibt in `PhotoLayer.tsx`. Auch eine Rechnung — aber ein falscher Wert
ergibt einen Kreis, der falsch *aussieht*. **Sichtbar falsch braucht keinen Test.** Das ist das
Kriterium, und es ist dasselbe, das die vier wichtigsten Testklassen des Backends ausgewählt hat.

Kein jsdom also: Es wäre ein nachgebauter Browser, und geprüft würde der Nachbau. Was am Rendern
dieses Programms wirklich schiefgehen kann — null fremde Herkünfte offline, ein Kreis unter einem
Vorschaubild noch mit dem Finger zu treffen, eine Beschriftung im Ausstellungsraum lesbar — prüft
jsdom ohnehin nicht. Das erste ist ein Einzeiler in den Entwicklerwerkzeugen, das zweite wurde am
Inline-`transform` nachgemessen, das dritte braucht einen Menschen vor dem Gerät und heißt
Punkt 14.

`decisions.md`, Punkt 60.

## Punkt 60: 938 Zeilen in zehn Dateien, und die Tests merken nichts davon

`41fde20` · 19. August 2026.

Der letzte Punkt aus dem Durchgang, und der einzige, der ausdrücklich als „nicht dringend, nicht
wichtig" dastand — mit der Warnung, dass er den am besten getesteten Teil des Backends bewegt.

### Die Bedingung stand vor dem Zuschnitt

Nicht „wie schneide ich das", sondern: **Woran erkenne ich hinterher, dass nichts kaputtgegangen
ist?** Neben der Datei liegen 908 Zeilen Testcode. Werden sie mitumgeschrieben, sind sie kein
Beweis mehr, sondern eine zweite Behauptung.

Also ein Paket mit einer Tür statt zehn neuer Importpfade: `app/services/backup/__init__.py` reicht
die zweiunddreißig Namen durch, die der Rest des Programms benutzt. `from app.services import
backup` heißt weiterhin dasselbe.

Nachgezählt am Ende: **sechs geänderte Zeilen** in 1814 Zeilen Testcode, und keine davon eine
Zusage. Es sind die Stellen, an denen `monkeypatch` `_is_mounted` und `_is_writable` umsetzt —
jetzt an `backup.drives` statt an `backup`. 439 Tests vorher, 439 Tests nachher.

Dass diese sechs Stellen überhaupt kommen würden, liess sich vorher sehen: Ein `grep` nach
`backup._` in den Tests findet genau sie. **Wer vor einem Umbau nachsieht, welche privaten Namen
von aussen angefasst werden, kennt die Bruchstellen, bevor er sie erzeugt.**

### Was die Trennung ans Licht brachte

Die Wiederherstellung setzte den Größen-Zwischenspeicher mit `global _size_cache` zurück. Das
funktioniert nur, solange beide in derselben Datei stehen — in einer Datei sieht man es gar nicht,
über zwei Module hinweg ist es sofort ein Fehler. Daraus wurde `collection.forget_size()`: aus
einem stillen Zugriff eine benannte Handlung.

Ähnlich die Unterstriche. Wer zwischen Modulen gebraucht wird, verliert ihn — `copy_if_new`,
`vacuum_into`, `human_size`, `manifest_bytes`. Der fehlende Unterstrich ist die Auskunft „das
benutzt jemand anderes"; in einer einzigen Datei konnte man das nicht sehen.

### Zehn Dateien

| Datei | Zeilen | wofür |
|---|---|---|
| `common.py` | 75 | Namen, Fehler, das gemeinsame Vokabular |
| `manifest.py` | 150 | was eine Sicherung über sich selbst sagt |
| `drives.py` | 118 | welche Datenträger es gibt |
| `collection.py` | 113 | was „der Bestand" auf der Platte ist |
| `write.py` | 94 | ihn auf den Stick schreiben |
| `archive.py` | 165 | dasselbe als eine Datei zum Herunterladen |
| `restore.py` | 206 | ihn zurückholen |
| `state.py` | 62 | wann zuletzt gesichert wurde |
| `job.py` | 105 | der eine lange Auftrag |
| `__init__.py` | 98 | die Tür, und wo was steht |

Der Schnitt folgt den Kommentarbalken, die vorher schon in der Datei standen. Das ist kein Zufall,
sondern der Grund, warum der Umbau überhaupt in einer Sitzung machbar war: **Die Grenzen waren
längst gezogen, sie waren nur nicht durchgesetzt.**

`decisions.md`, Punkt 61.

## Punkt 23: die Lizenz war die kleinere Hälfte

`ca49d21` · 21. August 2026.

Der Punkt hiess „Lizenz des Projekts und der verwendeten Komponenten" und war Voraussetzung für
die Veröffentlichung. Die Arbeit lag nicht bei der Wahl, sondern beim Nachzählen.

### Erst messen: 169 Pakete, keins davon Copyleft

Im README stand seit jeher: *„Alle verwendeten Komponenten sind Open Source."* Der Backlogeintrag
sagte dazu, das sei geglaubt und nicht geprüft. Geprüft, und zwar an den **installierten** Paketen
statt an den Manifestdateien, stimmt es: 39 Python-Pakete und 128 npm-Pakete, durchweg MIT, ISC,
BSD-2, BSD-3, Apache-2.0, HPND und PSF. Kein einziges Copyleft, nichts, was eine Wahl vorgeschrieben
oder eine Veröffentlichung verhindert hätte.

Das war die beruhigende Hälfte. Die andere kam beim Blick auf das, was das Repo **verlässt**.

### Drei Lücken, und die erste war eine echte Verletzung

**Das gebaute Frontend nannte seine Herkunft nicht.** 1,4 MB Bundle, 37 Pakete darin, genau
**zwei** Lizenzhinweise — `@license React` und ein Verweis auf MapLibres BSD-3. Kein einziger
Copyright-Vermerk hatte den Bau überlebt. MIT verlangt ihn wörtlich „in all copies or substantial
portions", BSD-3 ebenso für die Binärform. Von den Sorgen, mit denen dieser Punkt aufgegriffen
wurde — Lizenzverletzung, Haftung, Namensnennung —, war ausgerechnet die erste die begründete.

**Die Kartensymbole reisten ohne ihren Lizenztext.** `build-tiles.sh` holt aus dem Assets-Archiv
zwei Ordner heraus und wirft den Rest samt LICENSE mit dem Temporärverzeichnis weg. Dass die
Schriften korrekt belegt waren, war Zufall: Ihre `OFL.txt` liegt *innerhalb* von `fonts/`.

**Und die Karte nannte die Datenlizenz nicht.** Unten rechts stand „© OpenStreetMap-Mitwirkende" —
die Namensnennung stimmte, die ODbL fehlte. Vektorkacheln sind eine abgeleitete Datenbank, und die
verlangt, als solche kenntlich zu sein.

### Was die Bestandsaufnahme nebenbei zutage förderte

Zwei Dinge, nach denen niemand gesucht hatte. Erstens: **Weder `pyproject.toml` noch
`package.json` nannten einen Autor.** Zweitens, und das ist die feinere: **Die Tabelle `places`
steht unter ODbL** — sie kommt aus OpenStreetMap und liegt in `kiekmap.db`, also in jeder
Sicherung. Wer die Datenbank aus dem Haus gibt, gibt fremdlizenziertes Material mit. Dafür steht
jetzt ein Satz im Handbuch, in der Sprache, in der das Handbuch geschrieben ist.

### Die Wahl, und wie das Bauen sie prüfte

**Apache-2.0**, entschieden an §4.2: Das Projekt ist zum Übernehmen gebaut, und geänderte Dateien
müssen als geändert gekennzeichnet sein — eine missratene Übernahme bleibt damit sichtbar eine
Übernahme. Die Begründung samt der verworfenen Alternativen steht in
[decisions.md](decisions.md), Punkt 62.

`tools/build_notices.py` erzeugt die Hinweisdateien und ist dabei dreimal an sich selbst
gescheitert, jedes Mal an derselben Sorte Fehler: **eine Zeichenkette, die fast richtig zerlegt
wurde.** Der Dateiname aus `pyproject.toml` behielt sein Anführungszeichen. Die Trennzeichen für
Versionsangaben liessen bei `pydantic!=1.8` ein `pydantic!` übrig. Und `dependencies = [ … ]` wurde
beim ersten `]` abgeschnitten — das steckt in `uvicorn[standard]`, die Liste war nach einem Eintrag
zu Ende.

Aufgefallen ist keiner davon beim Lesen, sondern an der Zahl am Zeilenende: **9 Pakete, dann 16,
dann 26.** Ein Werkzeug, das eine Vollzähligkeit herstellen soll, muss die Zahl mitschreiben, die
es erreicht hat — sonst produziert es zuverlässig und leise das Falsche. Dieselbe Lehre wie bei
`tools/build_seed.py`, das seine Lücken nachzählt und abbricht, wenn eine fehlt.

## Punkt 64, Abschnitt 1: die Namen aus dem Repo

`20e4dfe` … `9c99c48` · 21. August 2026.

Vor der Veröffentlichung stand die Frage, ob die Abschnitte zur Bereinigung des Erstbestands aus
dieser Datei heraus müssten — es stünden echte Namen darin.

### Die Datenbank wusste es besser als die Suche

Nach Verdacht zu suchen hätte gefunden, woran ich mich erinnere. Gesucht wurde deshalb nach
Befund: Aus `data/kiekmap.db` liessen sich die Namen ziehen, die im Bestand wirklich vorkommen —
mit ihrer Häufigkeit —, und mit dieser Liste wurde das Repo durchsucht.

Das förderte einen Namen zutage, den die erste Zählung übersehen hatte, obwohl er im Bestand
**176 mal** vorkommt. Er stand nicht nur in der Dokumentation, sondern im **Produktivcode**, im
Kommentar über der Funktion, die Marker beschriftet. **Wer nach dem sucht, was er kennt, findet
nicht, was da ist.**

### 87 Fundstellen, und der Kader stand schon bereit

Ersetzt, nicht gestrichen — der Wert dieser Stellen liegt im Muster, nie im Wert. Und der
Beispielbestand unter `seed/` hatte die Rollen längst besetzt: Sein *Gasthof Petersen* liegt an
derselben Hausnummer wie das Gasthaus, das er ersetzt; seine *Familie Wendt* ist der Nachlass, seine
*Familie Boysen* der frühere Eigentümer, sein *A. Brahms* der Fotograf. Vier weitere Namen mussten
erfunden werden, mehr nicht.

Kein Beispiel hat dabei an Schärfe verloren. Das Kodierungsbeispiel — ein Name, der zweimal durch
die falsche Kodierung gedreht wurde — brauchte nur einen Umlaut, nicht diesen Umlaut.

### Der Test hat die Arbeit geprüft

Von 439 Tests schlug einer fehl: Eine **kleingeschriebene** Fassung desselben Namens war der
Ersetzung durchgegangen. Sie steht dort, weil sie belegt, dass eine Beschreibung ihren Titel auch
dann nicht wiederholen darf, wenn sie anders geschrieben ist — und genau diese Eigenschaft machte
sie unsichtbar für eine Suche, die auf Großschreibung baute. Zweimal derselbe Fehler an einem
Nachmittag, auf zwei Ebenen.

### Was offen bleibt

Der Git-Verlauf. 177 Commits tragen die alten Fassungen; allein einer der Namen steht in sechzehn
davon. Solange das Repo privat ist, trifft das niemanden — mit der Veröffentlichung wird es
öffentlich, und danach ist es nicht mehr zu ändern. Was daraus wurde, steht im nächsten
Abschnitt.

### Und der Verlauf gleich mit

Am selben Tag ist `git filter-repo --replace-text --replace-message` über die 180 Commits gelaufen,
nach zwei Sicherungen und einem Probelauf auf einer Kopie. Der Baum von `HEAD` ist danach
**byte-gleich** mit dem davor — dieselbe Prüfsumme —, alle Commits sind erhalten, und keiner der
gefundenen Namen steht noch in einer Dateifassung oder einer Commit-Nachricht.

> **Nachtrag vom 25. August 2026.** *„Der gefundenen"* ist die richtige Einschränkung, und sie war
> beim Schreiben nicht gemeint. Ein letzter Durchgang vor der Veröffentlichung fand **drei
> weitere** — ein Nachname, ein Hausname, ein Fototitel. Der Lauf vom 21. August suchte nach Namen,
> die die Datenbank als Namen kennt; diese drei standen in **Prosa**, in Beispielen, nicht in
> Datenfeldern. Im Arbeitsbaum sind sie ersetzt. **Im Verlauf bleiben sie stehen** — bewusst: Ein
> vierter Rewrite an einem Tag hätte alle Hashes erneut verschoben, die zitierten Kennungen erneut
> nachzuziehen verlangt und den Tag `v0.8.0` gekostet, und das für drei Namen, die nur in
> Beispielsätzen alter Commits stehen und die kein Leser der aktuellen Dateien je zu sehen bekommt.

**Möglich war das ohne Kosten, weil es keinen Remote gibt.** Niemand hatte eine Kopie, die
unbrauchbar werden konnte. Nach der Veröffentlichung wäre derselbe Lauf ein Bruch für jeden, der
schon geklont hat — das ist der ganze Grund, warum diese Entscheidung vorher fallen musste.

**Ein Nebeneffekt war einzukalkulieren und fast übersehen worden:** Diese Datei zitiert
Commit-Kennungen. 146 der 180 Commits haben eine neue bekommen, 29 Zitate zeigten danach ins Leere.
`filter-repo` schreibt dafür eine Zuordnungstabelle nach `.git/filter-repo/commit-map`; damit liess
sich jedes einzeln nachziehen. Zwei Kennungen blieben übrig und **durften nicht angefasst werden** —
sie sind keine Commits, sondern die acht Zeichen eines Foto-Hashes, wie der Kiosk sie unter dem
Bildnachweis zeigt. Nachgesehen in der Datenbank: Zu beiden gibt es genau ein Foto.

## Punkt 64, Abschnitt 2: CLAUDE.md war zur Hälfte ein Tagebuch

`4a30fd3` · 21. August 2026.

Die Frage war, ob Überschneidungen zwischen `CLAUDE.md` und den Dateien für Menschen ein Problem
sind. Sie hing an einer technischen Vorfrage, die sich nachschlagen liess: **Wird die Datei
überhaupt gebraucht, oder täte es ein Querverweis?**

Sie wird gebraucht. `CLAUDE.md` wird bei jedem Sitzungsstart automatisch und vollständig geladen
und ist der einzige Projekttext, der garantiert im Kontext steht. Alles andere kostet einen
Werkzeugaufruf und — schwerer wiegend — das Urteil, überhaupt nachzusehen. **Ein Querverweis wirkt
nur, wenn der Leser schon weiß, dass er ihm folgen muss.** Gewöhnliche Links werden nicht
mitgeladen; `@pfad`-Importe schon, aber vollständig, sie sparen also nichts.

Damit war die Antwort umgekehrt zur Vermutung: Überschneidung ist in Ordnung, **Umfang nicht**. Die
Empfehlung lautet unter 200 Zeilen, weil längere Dateien nicht nur Kontext kosten, sondern die
Befolgung senken. Die Datei stand bei 385 — und der Abschnitt „Stand" allein bei 199, so lang wie
die Empfehlung für das Ganze.

### Der Stand war kein Stand, sondern ein Verlauf

Er erzählte sieben Arbeitstage nach, mit Zahlen, die sich mit jedem Import ändern. Alles davon
steht in dieser Datei hier. Geblieben sind 31 Zeilen, und ihr Kriterium ist nicht „was ist
passiert", sondern **„was nähme man sonst falsch an"**: dass `deploy/pi/` geprüft sei, dass alte
Sicherungen noch erkannt werden, dass die Verwaltung ohne PIN läuft.

Dasselbe Kriterium hat die Sprachregelung von 53 auf 36 Zeilen gebracht — Tabelle und Faustregel
bleiben, weil sie beim Tippen gelten; die Begründung steht in `development.md`, wo sie gelesen
wird, wenn jemand sie wissen will. Und der Verzeichnisbaum wich den vier Sätzen, die man ihm nicht
ansieht: dass `services/` der Ort fürs Denken ist, dass `api/` dünn bleibt, dass die
Frontend-Typen `schemas.py` spiegeln.

### Beim Kürzen ging etwas verloren, und die Gegenprobe fand es

Die gemessene Qualitätseinstellung in `tools/to_jpeg.py` — nicht nachzujustieren, weil zwei Läufe
über dieselbe Datei denselben SHA-256 ergeben müssen — stand nur im Stand und wäre mit ihm
verschwunden. Sie ist jetzt dort, wo sie hingehört: unter „Was man nicht anfassen soll".

Gefunden hat sie eine Gegenprobe über **jede** entfernte Kernaussage: Hat sie anderswo ein Zuhause?
Vierzig Aussagen, neununddreißig hatten eines. **Wer kürzt, muss nachzählen, was er wegnimmt** —
sonst kürzt er genau das eine weg, das nirgends sonst steht.

### Und eine Regel gegen das Nachwachsen

Der Stand ist nicht aus Versehen gewachsen, sondern weil jeder erledigte Punkt dort vermerkt wurde.
Gemessen berührte ein Arbeitsschritt vier bis neun Doku-Dateien. Jetzt sind es drei bis vier, und
es steht geschrieben: CHANGELOG, history, backlog — dazu decisions.md, wenn eine Entscheidung
herauskam. **`CLAUDE.md` gehört nicht dazu**, denn sie sagt, wie man arbeitet, nicht was geschehen
ist.

---

## Punkt 64, Abschnitt 3: die Historie war nicht zu lang, sie hatte keinen Eingang

21. August 2026.

Die Frage im Punkt lautete: aufteilen oder nicht? 3.858 Zeilen, die größte Datei im Repo, rein
chronologisch angehängt. Die Antwort kam aus dem Messen, und sie war eine andere Frage.

### Erst messen

90 Abschnitte, der mittlere 55 Zeilen lang. Teil VI allein 3.294 Zeilen — 85 Prozent der Datei
unter einer Überschrift, die „Einzelne Punkte aus dem Backlog" heißt, also *alles Übrige*. Das sah
zunächst nach dem Befund aus.

War es aber nicht. Die 56 Abschnitte von Teil VI verteilen sich auf zwanzig Arbeitstage, zwei bis
acht am Tag, gleichmässig groß, streng in der Reihenfolge ihres Entstehens. **Die Datei ist
geordnet — sie zeigt ihre Ordnung nur nicht.** Die Datumsangaben lagen in der Prosa, wo nichts
sie erreicht.

Und dann die Zahl, die den Ausschlag gab: **31 Verweise aus anderen Dateien zeigen hierher, 30
davon ohne Anker.** Auf 3.858 Zeilen. Wer aus `decisions.md` einem „siehe history.de.md" folgt,
landet in Zeile 1 und hat nichts gewonnen. Das ist der Befund, nicht die Länge — eine Datei, die
niemand von vorn liest, darf lang sein; ein Verweis, der nichts eingrenzt, ist kaum einer.

### Aufteilen hätte das Gegenteil bewirkt

Nach Jahr: gegenstandslos, das Projekt ist vier Monate alt. Nach Thema: Es zerstört die
Reihenfolge, und die ist das Einzige, was diese Datei gegenüber CHANGELOG und Entscheidungen
voraushat. Dazu kämen Kosten, die niemand bemerkt: Anhängen bräuchte plötzlich eine Entscheidung —
*in welche Datei?* —, und Abschnitte wie „Punkt 57, 58 und 59, behoben am selben Tag" gehören in
drei Themen gleichzeitig.

### Drei Schritte statt eines Schnitts

Ein **Register** am Anfang, eine Zeile je Abschnitt mit Datum und Sprungmarke. Es ersetzt die
Tabelle der Arbeitsblöcke, die eine Commit-Spanne nannte — `0609153` … `b035011` — und damit seit
fünfzig Abschnitten falsch war. Die Spanne von Teil VI rechnet das Register jetzt aus seinen
Abschnitten aus; sie kann nicht wieder veralten.

**Das Datum ist der Eingang, nicht der Titel.** Gesucht wird ein Tag. Die Überschriften hier sind
Merkhilfen — „Der Diff, der keiner war", „Der schwarze Blitz hinter dem Bild" —, und die taugen
zum Wiedererkennen, nicht zum Suchen: Man kann nicht nach einem Fehler suchen, den man noch nicht
benennen kann. Dafür gibt es `grep`, und die Datei ist ausführlich genug dafür.

**Acht Verweise haben ein Ziel bekommen**, die, die erkennbar eine Stelle meinten. Einer davon war
schon von aussen sichtbar schief: `[Punkt 62](history.de.md)` — eine Beschriftung, die einen Punkt
nennt, und ein Ziel, das die ganze Datei ist. Die übrigen 22 meinen wirklich die Datei und bleiben.

### Die Gewohnheit war eingeschlafen

Die Zusage, die das Register braucht, lautet: *Jeder Abschnitt nennt sein Datum in den ersten
Zeilen darunter.* Sie war nie aufgeschrieben, und sie wurde trotzdem 81 Mal eingehalten — und
**neunmal nicht, in den neuesten Abschnitten**. Genau die, die zuletzt geschrieben wurden. Die
Sperre in `tools/build_register.py` hat sie in der ersten Sekunde aufgezählt, was ihr Wert ist:
Eine Konvention ohne Prüfung hält, bis jemand sie nicht kennt.

Für die Teile I bis V gilt eine Ausnahme, und sie ist keine Nachsicht, sondern Ehrlichkeit:
Niemand hat notiert, an welchem Tag Stufe 4 gebaut wurde. Bekannt ist der Block, 28. bis 30. Juli.
Also nennt der Block sein Datum einmal und seine Abschnitte erben es. Ein Teil, der keins nennt —
Teil VI —, gibt keins weiter, und seine Abschnitte müssen selbst liefern. Eine Regel, ein Satz,
keine Sonderfälle.

### Was der Weg noch aufdeckte

**Git taugte nicht als Datumsquelle**, obwohl es nach der besseren Idee aussah: eine Messung statt
einer Behauptung. Nachgesehen meldet Git für alle 28 Abschnitte der Teile I bis V den 2. August —
den Tag, an dem sie aus drei Plandokumenten zusammengeführt wurden. Es datiert das Aufschreiben,
nicht die Arbeit. Und einen Tag zuvor hatte `git filter-repo` alle Datumsangaben auf einmal
verschoben; eine Quelle, die das tut, trägt kein Register.

**`architecture.md` fehlte in `tools/check_anchors.py`.** Aufgefallen ist es nur, weil der neue
Verweis dorthin nicht geprüft wurde. Kein Vorsatz — die Datei kam später dazu und war nie
nachgetragen worden, und niemand hatte es gemerkt, weil bis dahin kein Anker in sie hinein oder
aus ihr heraus zeigte.

**Und der Ankerprüfer kannte nur `##` und tiefer.** Die Annahme dahinter war vernünftig: Eine
Überschrift der ersten Ebene ist ein Dokumenttitel, und auf den verweist niemand. Bis das Register
auf die sechs Teile verwies und alle sechs als tot gemeldet wurden. Die Änderung kann nur Anker
hinzufügen, nie welche wegnehmen — was vorher grün war, bleibt grün.

### Und die Ablage

`seed/README.md` stand längst in der Übersicht; die Frage im Punkt war schon beantwortet.
`adaption.md` dagegen stand falsch. Sie lag mit `licensing.md` unter „Daran arbeiten" — aber
niemand, der an diesem Gerät weiterbaut, liest sie. Beide richten sich an jemanden, der ein
**eigenes** aufsetzt. Das ist ein anderer Mensch mit einer anderen Frage, und es ist der
eigentliche Zweck des Projekts. Die Übersicht hat dafür jetzt „Es übernehmen".

---

## Punkt 64, Abschnitt 4: die Regel stand da und wurde nicht geprüft

22. August 2026.

Der letzte Abschnitt hatte zwei Hälften, die nichts miteinander zu tun schienen: fünf Dateien, die
ein veröffentlichtes Repo üblicherweise hat und die hier fehlten — und eine Umlaut-Drift in der
Dokumentation. Beide gehen auf dasselbe zurück: **Etwas war zugesagt, und niemand hat nachgesehen.**

### Die Drift war keine Praxis, sondern zwei Dateien

Der Punkt notierte sie als allgemeines Nachlassen und stellte die Frage, ob die Regel an die
Praxis anzupassen sei. Gemessen fiel die Frage weg:

| | Umlaute | umschrieben |
|---|--:|--:|
| `decisions.md` | 830 | **338** |
| `history.de.md` | 1.252 | **568** |
| die neun übrigen Dateien zusammen | 1.936 | **8** |

**Elf von dreizehn Dateien halten die Regel makellos ein.** Die Regel ist nicht aus der Zeit
gefallen; zwei Dateien sind es. Und innerhalb von ihnen ist die Drift nicht gleichmäßig: In
`history.de.md` steht das erste Drittel bei 713 zu 16, das mittlere bei 192 zu 352. Das ist keine
Gewohnheit, die nachlässt, sondern eine Strecke Arbeit, in der die Regel für Quelltext auf die
Dokumentation übergriff.

Dazu dasselbe Bild beim `ß`: 177 Stellen mit `ss`, wo ein `ß` hingehört — `heisst`, `Strasse`,
`weiss` —, in denselben zwei Dateien, die daneben 268 Mal ein richtiges `ß` tragen. Ein Satz
schrieb „Die Strasse wird gewählt", der nächste „dann die Straße". Derselbe Fehler, dieselbe
Ursache, also derselbe Durchgang.

### 900 Ersetzungen, und die Vorsicht lag in der Ausnahmeliste

Eine naive Ersetzung `ue → ü` macht aus „neue" ein „nü", aus „Feuerwehr" ein „Feürwehr", aus
„Quelle" ein „Qülle". Der Weg war deshalb: **erst alle 547 verschiedenen Wörter mit `ue`, `oe`
oder `ae` auflisten, dann die echten aussortieren.** Rund dreißig sind echt — `neue`, `bauen`,
`zuerst`, `Quelle`, `dauert`, `quer`, `genauer`, `schauen`, `streuen`, `Feuerwehr`, `aktuell`,
`Vertrauen`, `bequem`, dazu zwei Namen: `Uetersener` und `Hauenweg`.

Zwei Fallstricke hat erst der Probelauf gezeigt. Die Ausnahmeliste war
**groß-klein-empfindlich** — „neue" stand drin, „Neue" nicht, und „Nachbauen" wurde zu
„Nachbaün". Und sie sperrte **zu viel**: „strassengenauen" trägt beides, ein echtes `aue` aus
Straße und genau, und ein `ss`, wo ein `ß` hingehört. Die Ausnahme muss also nur die eine
Ersetzung sperren, nicht die andere.

Vier Wörter fielen ganz durch, weil sie kaputt waren, nicht umschrieben: `ruecht` (statt „rückt"),
`verstoeszt` und `straszengenaue` (mit `sz` statt `ß`), und `Wagenrueckaeufe` — dem ein `l` fehlte,
seit es „Wagenrückläufe" heißen sollte. Vier Tippfehler, die jahrelang unentdeckt geblieben
wären, weil niemand nach ihnen suchte.

**Neun Stellen lagen ausserhalb der beiden Dateien**, in `CHANGELOG`, `development.md` und
`licensing.md`. Auch sie sind mitgezogen; die drei echten Ausnahmen — OSM-Werte in Codespannen,
Testnamen, und das Beispiel in CLAUDE.md, das eine umschriebene Meldung *zeigt* — blieben.

### Die Prüfung, die schon versprochen war

Und hier der eigentliche Fund. In [development.md](development.md) steht seit Monaten, direkt
unter dem Absatz über Umlaute: *„Ob eine Datei sich daran hält, beantwortet
`tools/language_check.py`."* **Das tat sie nicht.** Das Werkzeug las `.py`, `.ts` und `.tsx` und
beantwortete eine andere Frage — in welcher Sprache ein Kommentar geschrieben ist. Die Umlautfrage
hat es nie gestellt, und die Dokumentation hat es nie angesehen.

Jetzt tut es beides. Übersprungen werden drei Dinge, und jedes hat einen Grund: umzäunte Blöcke
und Codespannen, weil dort Bezeichner und Kommandos stehen und die Umschreibung richtig ist;
und Zitiertes, weil CLAUDE.md eine umschriebene Meldung als eigenes Beispiel der Regel führt.

Dabei noch ein kleiner Fehler, der zeigt, wie fein die Sache ist: Das Zitat in CLAUDE.md öffnet
mit `„` und schließt mit `”`. Der vorhandene Zitatfilter erwartete `“`, fand es nicht — und
paarte das Anführungszeichen stattdessen mit dem **nächsten**, wodurch genau das Zitat unbedeckt
blieb, das gedeckt sein musste. Die eigene Regel wurde am eigenen Beispiel gemeldet.

**Die Liste der Suchformen ist mit Absicht kurz.** Sie läuft im Commit-Hook, und eine
Fehlmeldung genügt, damit jemand die Prüfung abschaltet. `neue`, `Quelle`, `dauert` und
`Feuerwehr` stehen deshalb nicht darin, obwohl sie ein `ue` tragen.

### Und die Gegenprobe zog die Umbenennung nach

Der Ankerprüfer meldete unmittelbar danach einen toten Verweis: Die Überschrift „die Knoepfe
bekommen einen Ort" heißt jetzt „die Knöpfe", und ein Verweis vom Vortag zeigte noch auf die
alte Sprungmarke. Genau der Fall, für den die Prüfung am 15. August dazugekommen war — und der
erste, den sie im laufenden Betrieb gefangen hat.

### Fünf Dateien, und zwei Entscheidungen darin

`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `AUTHORS` und zwei Meldungsvorlagen unter
`.github/`. Zwei Dinge daran waren nicht technisch zu entscheiden:

**Die Kontaktadresse.** Eine Adresse im Klartext wird abgegriffen und steht danach in jedem Fork
und jedem Archiv. Gewählt wurde stattdessen die private Meldung bei GitHub — kein Klartext im
Repo, und der Weg taugt zugleich als der eine nicht-öffentliche Kanal, den auch der Kodex braucht.

**Der Verhaltenskodex.** Nicht der Contributor Covenant, sondern fünfzehn Zeilen in der Stimme des
Projekts, mit dem wunden Punkt ausgeschrieben: Es gibt einen Betreuer, und ein Kodex ohne
jemanden, der ihn durchsetzt, ist eine Zusage ohne Deckung. Der Wechsel zum Covenant steht als
nächster Schritt darin, falls je eine Gemeinschaft entsteht.

Das Leitmotiv aller fünf ist dasselbe: **eine Veröffentlichung darf keine stille Zusage werden.**
Deshalb steht in `CONTRIBUTING.md` ausdrücklich, dass eine Meldung Wochen liegen bleiben kann, und
in `SECURITY.md` eine Liste dessen, was **kein** Fund ist, sondern Entwurf — die Besucheransicht
ohne Anmeldung, der Beitragsweg ohne Ratenbegrenzung, der unverschlüsselte Bestand.

Eine Vorlage hätte beinahe eine Adresse erfunden, die es nicht gibt: GitHub verlangt für
Verweise in `config.yml` eine absolute Adresse, und die des Repos steht erst mit
Punkt 22 fest. Der Verweis ist weggeblieben, mit einem Kommentar an seiner Stelle.

### Und der CHANGELOG sortierte seit zwei Wochen alles unter „Behoben"

Beim Nachtragen aufgefallen, weil der eigene Eintrag an einer sichtbar falschen Stelle landete:
**25 Einträge standen unter dem letzten `### Behoben`, und nur acht davon waren Behebungen.** Die
Apache-Lizenz, das Register, `licensing.md`, die fünf neuen Dateien — alles Hinzugefügtes, alles
unter „Behoben". Die Überschrift war einmal richtig und ist dann einfach stehen geblieben, während
darunter weitergeschrieben wurde.

Der Kopf der Datei sagt *„Format nach Keep a Changelog"*. Wieder eine Zusage, die niemand
nachrechnet — dieselbe Sorte Fund wie die Umlautregel und aus demselben Grund gefunden: nicht
durch Suchen, sondern durch Hinschreiben. Die 25 sind auf neun Behebungen, sieben Änderungen und
neun Hinzufügungen verteilt.

**Damit ist Punkt 64 vollständig** und aus dem Backlog gezogen. Was von der Durchsicht bleibt, ist
kein Punkt mehr, sondern eine Prüfung mehr in `make check`.

---

## Punkt 22: der Weg nach draussen, an einem Tag

`eb98f12` · 25. August 2026.

Punkt 22 hiess „Versionierung, Releaseprozess und Veröffentlichung" und war der letzte offene
Punkt vor dem Schritt nach draussen. Vier seiner fünf Teile sind an diesem Tag gebaut worden; der
fünfte, die Veröffentlichung selbst, ist keine Arbeit, sondern eine Entscheidung und zieht als
Punkt 65 weiter.

### Erst die Frist, dann alles andere

Die Reihenfolge kam nicht aus der Grösse der Teile, sondern aus ihrer Umkehrbarkeit. **Genau ein
Schritt hatte eine Frist:** Solange es keinen Remote gibt, kostet ein Umschreiben des Verlaufs
nichts.

Gemessen trugen 185 Commits **drei** Identitäten. `user.name` und `user.email` waren nirgends
gesetzt, also baute Git die Adresse aus Konto- und Rechnernamen — und der Rechnerwechsel Anfang
August erzeugte von selbst eine dritte. Zwei der drei Adressen waren keine Postfächer, sondern
Auskunft über die Arbeitsumgebung. Kein Commit war signiert, kein Schlüssel lag vor.

Beides ist an diesem Tag bereinigt worden, in zwei Rewrites: eine Identität für alle, und alle 188
signiert, auch die aus der Zeit vor dem Schlüssel. Die Begründung dafür steht in
[decisions.md](decisions.md), Punkt 67 — samt des Preises, den man kennen muss.

### Der Rewrite hing nicht an der Dauer, sondern an einer Rückfrage

Der erste Versuch lief zwei Minuten in ein Zeitlimit. Der Verdacht fiel auf die 3,2 GB
unversionierter Fotos im Arbeitsbaum, durch die Git beim Aufräumen läuft. Tatsächlich fragte
`filter-repo` wegen des Laufs vom 21. August **interaktiv** nach — *„Treat this run as a
continuation (Y/N)?"* —, und `--force` deckt diese Frage nicht ab. Nach dem Beiseitelegen des alten
Datensatzes: 0,28 Sekunden.

### Ein Verweis war schon vorher kaputt

Der Nachlauf über die zitierten Kurz-Hashes förderte einen zutage, der keinen Commit mehr traf:
`6eb4c69` im CHANGELOG. Er stammte aus der Zeit **vor** dem Rewrite vom 21. August, und dessen
Nachlauf hatte nur `docs/` geprüft. Über beide Zuordnungstabellen liess er sich verketten. Die
Gegenprobe läuft seither über jeden siebenstelligen Hash in `docs/`, `CHANGELOG`, `README` und
`CLAUDE.md`.

### Das Branch-Modell, und eine Korrektur nach einer Stunde

Zwei langlebige Zweige: `develop` für den Alltag, `main` für den Stand, der ausgeliefert ist. Das
ist **nicht** GitHub Flow, auch wenn es so aussieht — die Begründung steht in
[decisions.md](decisions.md), Punkt 66.

Darin stand zunächst „`feature/*` → `develop` per Rebase". **Der erste Pull Request hat das
widerlegt.** Ein Rebase erzeugt die Commits neu, GitHub baut sie auf dem Server, und dort liegt
kein Schlüssel: Die drei Commits kamen **unsigniert** heraus. 190 signierte und drei Löcher.

Das Argument im Punkt sprach gegen *Squash*, nicht für Rebase — ein gewöhnlicher Merge erhält jeden
Commit genauso einzeln. Rebase war eine Voreinstellung, die ich mitgebracht und nicht am Projekt
geprüft hatte. Seither: Merge-Commit in beide Richtungen, und Rebase-Merge ist auch in den
Repo-Einstellungen abgeschaltet. Die drei Löcher sind nachsigniert.

### Was ein Release erst zu einem Release macht

**Die Versionsnummer stand an fünf Stellen, nicht an zwei.** Die fünfte war die wichtigste und
wäre am ehesten liegengeblieben: `__version__` in `app/__init__.py` ist das, was `/api/health`
antwortet. Alle fünf standen auf `0.1.0`. Das Gerät hätte dauerhaft die falsche Fassung von sich
behauptet, während der Image-Tag weiterzählt — und die eine Frage, für die es die Gesundheitsabfrage
gibt, hätte eine falsche Antwort bekommen.

**Die Abhängigkeiten sind festgenagelt**, und dabei fiel eine Lizenzlücke auf, die still offen war:
`build_notices.py` las die Paketliste vom Entwicklungs-venv ab. `greenlet`, das SQLAlchemy auf
Linux mitbringt, wird auf einem Mac nie installiert und fehlte deshalb in `THIRD-PARTY.txt`. Jetzt
kommt die Liste aus der Lockdatei — sie *ist* die Liste dessen, was ins Abbild kommt — und die
Umgebungsmarker werden gegen beide Zielplattformen ausgewertet. Der laufende Container hat es
bestätigt.

Nebenbei: **`pip install .` im Dockerfile tat nie, was es aussieht.** `app/` wird erst danach
kopiert, die Paketsuche fand also nichts und installierte eine Distribution ohne Inhalt. Gezogen
wurden immer nur die Abhängigkeiten.

**`make release`** baut den Ordner, den `deploy/pi/update.sh` erwartet. Von Hand waren das vier
Befehle aus `operations.md`, und der vergessene ist die `version`-Datei: Ohne sie bleibt
`KIEKMAP_VERSION` in der `.env` des Pi stehen, und der nächste Start zieht das **alte** Abbild
wieder hoch. Das Gerät liefe dann mit der alten Software und sagte es nirgends. Geprüft wurde nicht
nur der Bau, sondern der Weg, den der Pi geht: bauen, sichern, Abbilder lokal löschen, laden,
starten — `{"status":"bereit","version":"0.8.0"}`.

### Die CI hat sich in ihrer ersten Stunde bezahlt gemacht

Drei Läufe, zwei echte Fehler, beide unsichtbar auf dem Entwicklungsrechner:

**`make check` wäre unter Node 22 gebrochen** — also bei der Fassung, zu der das Makefile selbst
rät. Die Node-Versionsprüfung trug Backslash-Zeilenenden innerhalb einfacher Anführungszeichen, wo
die Shell sie nicht entfernt. Node 18 verzieh den durchgereichten Backslash, Node 22 wertet `-e`
durch einen TypeScript-fähigen Parser aus und bricht ab.

**`build_notices.py` importiert seit der Marker-Auswertung `packaging`**, wurde aber mit dem
System-Python aufgerufen. Der Entwicklungsrechner bringt es zufällig mit, eine frische Umgebung
nicht. Es läuft jetzt mit dem Python des venv — als einziges der sieben Werkzeuge, und das ist
keine Notlösung: Die sechs Prüfungen daneben sind reine Leser, dieses hier liest Paket-Metadaten
und braucht das venv ohnehin. Es hatte nur so getan, als bräuchte es keins.

Dazu ein Grenzfall, den die Umlautprüfung an sich selbst fand: `.github/` stand als Ganzes in ihrer
Prosa-Liste. **Ein Workflow ist Quelltext**, näher an einem Shell-Skript als an einer Anleitung.

### Zwei Hürden, die nicht im Drehbuch standen

**GitHub lehnte den Push ab** — `GH007: Your push would publish a private email address`. Der
Schutz bewachte genau die Entscheidung, die bewusst gefallen war: eine dedizierte Adresse, die in
den Commits stehen *darf*. Er ist abgeschaltet.

**Branch-Schutz gibt es auf einem privaten Repo im Gratistarif nicht.** Beide Wege antworten mit
`403 Upgrade to GitHub Pro or make this repository public` — der klassische und der neuere über
Rulesets. Er zieht damit in die Veröffentlichung um.

### Und der Tag

`develop` → `main` als Merge-Commit, **lokal gemacht statt über den Knopf**: GitHubs Nachricht
hiesse „Merge pull request #6 from kerlhoff/develop", und für den einen Commit, auf den `main`
zeigt und an dem der Tag hängt, ist das zu wenig. Danach `v0.8.0`, signiert.

**Nicht `1.0.0`**, weil das unter SemVer eine stabile öffentliche Schnittstelle zusagt: Alles unter
`deploy/pi/` ist ungeprüft, die Abnahme auf dem ersten Gerät steht aus. Die `1.0.0` wird nach
[Punkt 15](https://github.com/nordfisch/kiekmap/issues/18) vergeben — das macht aus ihm einen Meilenstein statt einer Fussnote.

---

## Punkt 66: sechs Meldungen, ein Haken

25. August 2026.

Der erste Push nach GitHub brachte eine Beigabe mit: **sechs Schwachstellen, eine als kritisch
eingestuft.** Der Reflex wäre gewesen, sie der Reihe nach abzuarbeiten. Nachgezählt hingen alle
sechs an **einem** Paket.

### Erst messen, wieder einmal

`npm audit --omit=dev` meldete **null**. Alle sechs waren `devDependencies`, keine stand in
`frontend/public/THIRD-PARTY.txt` — auf dem Pi läuft nginx mit dem gebauten Bundle, vite, vitest
und esbuild sind Werkzeug und keine Ware.

Die kritische betraf die Vitest-Oberfläche, *„when Vitest UI server is listening"*. Hier läuft
`vitest run`, headless; `@vitest/ui` war nicht einmal installiert. Der verwundbare Dienst wird nie
gestartet.

**Und die übrigen kamen aus einer zweiten Ebene.** Direkt installiert waren `vite 6.4.3` und
`esbuild 0.25.12`, beide längst gepatcht. Daneben lagen:

```
node_modules/vitest/node_modules/vite      5.4.21
node_modules/vitest/node_modules/esbuild   0.21.5
```

Vitest 2 brachte seine eigenen alten Kopien mit. Ein Hauptversionssprung war also nicht die
gründlichere von mehreren Möglichkeiten, sondern die einzige.

### Der Sprung kostete nichts

Der beste Fall für einen Hauptversionswechsel: **keine Testkonfiguration**, reine Logiktests, kein
jsdom — die Angriffsfläche war klein. Nach `vitest@^3` liefen 189 von 189 Tests, der Typprüfer war
still, das Bundle baute. Im Baum liegt jetzt je ein `vite` und ein `esbuild`; die Sperrdatei ist
dabei um rund neunhundert Zeilen geschrumpft.

Übrig blieb eine Meldung, `nanoid` über `vite → postcss`, und die war mit `npm audit fix` erledigt.
**Null.**

### Zwei Dinge nebenbei

Beim Neuberechnen des Baums meldete npm, ein Paket verlange Node ≥ 22, während hier 18 läuft.
Nachgesehen war es `@mapbox/jsonlint-lines-primitives`, eine transitive Abhängigkeit von
**maplibre-gl** — vorbestanden, nur durch die Neuberechnung sichtbar geworden, und nichts, was der
Sprung verursacht hätte.

Und `THIRD-PARTY.txt` blieb auf beiden Seiten **unverändert**. Das ist die Gegenprobe zur ganzen
Einschätzung: Was sich hier bewegt hat, wird nicht ausgeliefert.

**Der Grund, es trotzdem vor der Veröffentlichung zu tun**, war nie das Risiko. Es war die rote
Fahne, die sonst am ersten Tag am Repo gehangen hätte — und die Fragen aufwirft, die die Antwort
nicht wert sind.

---

## Punkt 65: veröffentlicht

25. August 2026.

Das Repo liegt öffentlich unter `github.com/nordfisch/kiekmap`. Der Schritt selbst war ein Schalter;
was daran hing, war die Liste dahinter — und drei Punkte davon **gab es vorher gar nicht.**

### Was erst öffentlich existiert

**Der Meldeweg aus `SECURITY.md`.** Beide Dateien, `SECURITY.md` und `CODE_OF_CONDUCT.md`,
verweisen auf die private Sicherheitsmeldung bei GitHub als *den* vertraulichen Kanal. Den Schalter
dafür gibt es nur auf öffentlichen Repos — solange das Repo privat war, zeigte die Zusage ins Leere.
Jetzt steht sie.

**Der Branch-Schutz.** Am selben Tag noch mit `403 Upgrade to GitHub Pro or make this repository
public` abgewiesen, klassisch wie über Rulesets. Jetzt: beide Zweige ohne Force-Push und ohne
Löschen, `develop` mit `make check` als Pflichtprüfung, `main` mit Pull Request und null Freigaben.
`enforce_admins` bleibt aus, damit der Release-Merge weiter lokal gemacht werden kann — der eine
Commit, auf den `main` zeigt, soll die Signatur des Betreuers tragen und keine Nachricht der Form
„Merge pull request".

**Und das Abzeichen im README**, das vorher nur ein kaputtes Bild gewesen wäre.

### Eine Einstellung, die beim Nachsehen auffiel

`secret_scanning` stand auf `disabled`. Auf öffentlichen Repos ist es kostenlos, und es bewacht
genau das, was vor der Veröffentlichung von Hand geprüft worden war: Zugangsdaten im Baum und im
Verlauf. Zusammen mit dem Push-Schutz eingeschaltet — die Handprüfung sagt etwas über einen
Zeitpunkt, der Scanner über jeden künftigen Push.

### Ein Release ohne Abbilder

`v0.8.0` als GitHub-Release, mit dem Quelltext, den GitHub selbst beilegt, und **ohne gebaute
Abbilder**. Ein Abbild aus `python:3.12-slim` oder `nginx:1.27-alpine` enthält GPL-lizenziertes
Userland; wer es weitergibt, übernimmt dessen Pflichten. Wer die Dockerfiles veröffentlicht, lässt
sie dort, wo sie hingehören. Der Weg über `abbilder.tar` bleibt für das eigene Gerät richtig — siehe
[licensing.md](licensing.md).

### Womit Punkt 22 vollständig ist

Fünf Teile, an einem Tag: Identität und Signatur, Branch-Modell, Versionierung, Releaseprozess,
CI — und jetzt die Veröffentlichung. Was bleibt, steht in
[Punkt 15](https://github.com/nordfisch/kiekmap/issues/18): Das Gerät im Museum fehlt noch, und mit ihm die Abnahme, an der die `1.0.0`
hängt.

