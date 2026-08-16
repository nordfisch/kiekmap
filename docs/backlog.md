# Offene Punkte

Was noch aussteht, nach **Verwaltung · Besucher-Interface · Infrastruktur · Entwicklung**. Die
ersten drei betreffen das Programm, der letzte die Arbeit daran. Was schon gebaut ist, steht in
[history.md](history.md).

Jeder Eintrag trägt mit, was beim Aufgreifen sonst erst wieder herausgefunden werden müsste. Das
ist der Grund, warum er hier steht und nicht in einer Stichwortliste: Ein Punkt ohne seinen
Zusammenhang kostet beim zweiten Anlauf dieselbe Arbeit wie beim ersten.

## Wie diese Datei zu lesen ist

Jeder Punkt hat eine **Nummer**, eine **Art** und eine **Einordnung**. Alle drei stehen in der
Tabelle unten, und zwar nur dort — der Fließtext bleibt Text.

**Die Nummer ist die Kennung.** Sie wird einmal vergeben und **nie wieder**, auch nicht, wenn der
Punkt erledigt ist und in die [history.md](history.md) zieht; dort wird sie beim Umzug genannt.
Zitiert wird sie als „Punkt 7". Neue Punkte bekommen die nächste freie Nummer, nicht die nächste
Zeile — die Reihenfolge in dieser Datei darf sich also von der Zählung lösen, und genau das ist der
Sinn einer stabilen Kennung.

**Vier Arten**, weil vier verschiedene Dinge zu tun sind:

| Art | Was es heißt |
|---|---|
| **Fehler** | Etwas tut nicht, was es zusagt. |
| **Aufgabe** | Klar umrissen, es fehlt nur die Arbeit. |
| **Frage** | Vor der Arbeit ist zu entscheiden, *was* gebaut wird. |
| **Idee** | Noch nicht entschieden, ob überhaupt. |

**Zwei Achsen, und sie sind nicht dasselbe** — das ist der ganze Grund, sie zu trennen:

- **dringend** — es trifft heute jemanden (einen Besucher am Gerät oder das Museumsteam bei der
  Arbeit), oder es blockiert einen anderen Punkt.
- **wichtig** — ohne das ist das Projekt auf Dauer nicht das, was es sein soll.

Innerhalb jedes Bereichs steht oben, was beides ist, dann was wichtig ist, dann der Rest; bei
Gleichstand Fehler vor Aufgabe vor Frage vor Idee.

## Übersicht

| # | Punkt | Art | Einordnung |
|---|---|---|---|
| | **Verwaltung** | | |
| 1 | [Der Erstbestand braucht eine Durchsicht](#1--der-erstbestand-braucht-eine-durchsicht) | Aufgabe | wichtig · dringend |
| 50 | [Ein Schlagwort für den ganzen Stapel beim Import](#50--ein-schlagwort-für-den-ganzen-stapel-beim-import) | Aufgabe | wichtig |
| 51 | [Der Abbruch am PIN-Feld heißt „Abbrechen und zurück"](#51--der-abbruch-am-pin-feld-heißt-abbrechen-und-zurück) | Aufgabe | — |
| 31 | [Einstellungen in der Verwaltung pflegen statt in der `.env`](#31--einstellungen-in-der-verwaltung-pflegen-statt-in-der-env) | Frage | wichtig |
| 52 | [Den neueren Archivstand abgleichen und nachziehen](#52--den-neueren-archivstand-abgleichen-und-nachziehen) | Aufgabe | wichtig · dringend |
| 42 | [Dubletten finden, die beste behalten, den Rest zusammenführen](#42--dubletten-finden-die-beste-behalten-den-rest-zusammenführen) | Frage | wichtig |
| 34 | [Eine Karte in der Nachbearbeitung des Imports](#34--eine-karte-in-der-nachbearbeitung-des-imports) | Idee | — |
| | **Besucher-Interface** | | |
| 30 | [Die Karte nach Schlagwörtern filtern](#30--die-karte-nach-schlagwörtern-filtern) | Idee | wichtig |
| 40 | [Ein Durchgang über die ganze Oberfläche](#40--ein-durchgang-über-die-ganze-oberfläche) | Aufgabe | wichtig |
| 43 | [Der Zeitschieber soll jahrgenau zählen, nicht jahrzehntgenau](#43--der-zeitschieber-soll-jahrgenau-zählen-nicht-jahrzehntgenau) | Aufgabe | — |
| 54 | [Das Layout der Detailansicht dem Bildformat folgen lassen](#54--das-layout-der-detailansicht-dem-bildformat-folgen-lassen) | Idee | — |
| 8 | [Historische Karte als umschaltbare Grundkarte](#8--historische-karte-als-umschaltbare-grundkarte) | Idee | wichtig |
| 9 | [Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode](#9--bilder-in-bewegung-diashow-ken-burns-effekt-attract-mode) | Idee | wichtig |
| | **Infrastruktur** | | |
| 14 | [Bedienbarkeitstest mit der echten Zielgruppe](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) | Aufgabe | wichtig · dringend |
| 15 | [Abnahme auf dem ersten Pi](#15--abnahme-auf-dem-ersten-pi) | Aufgabe | wichtig |
| 18 | [Wiederherstellung wirklich proben](#18--wiederherstellung-wirklich-proben) | Aufgabe | wichtig |
| 19 | [Displayauflösung und -orientierung des Museumsgeräts](#19--displayauflösung-und--orientierung-des-museumsgeräts) | Frage | wichtig |
| 20 | [Das Gerät muss einen Stromausfall überstehen](#20--das-gerät-muss-einen-stromausfall-überstehen) | Frage | wichtig |
| | **Entwicklung** | | |
| 21 | [Deployment auf einem Webserver evaluieren](#21--deployment-auf-einem-webserver-evaluieren) | Frage | wichtig · dringend |
| 39 | [Den Code prüfen lassen](#39--den-code-prüfen-lassen) | Aufgabe | wichtig |
| 22 | [Versionierung, Releaseprozess und Veröffentlichung des Codes](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes) | Frage | wichtig |
| 23 | [Lizenz des Projekts und der verwendeten Komponenten](#23--lizenz-des-projekts-und-der-verwendeten-komponenten) | Frage | wichtig |

**Kein Fehler ist offen.** Was hier steht, ist Arbeit und Frage, nicht Reparatur.

**Zweiunddreißig Nummern sind vergriffen** — 2, 3, 4, 5, 6, 7, 11, 12, 13, 16, 17, 24, 25, 26, 27,
10, 28, 29, 32, 33, 35, 36, 37, 38, 41, 44, 45, 46, 47, 48, 49, 53. Sie sind erledigt, aufgelöst oder
gestrichen; was aus jeder wurde, steht in [history.md](history.md). Der nächste neue Punkt bekommt
die **55**.

---

## Verwaltung

### 1 · Der Erstbestand braucht eine Durchsicht

929 Fotos sind eingelesen, und am 11. und 12. August 2026 hat eine maschinelle Runde alles
herausgeholt, was sich aus Dateien, Ordnernamen und den vorhandenen Textfeldern ableiten ließ —
Verortung, Titel, Beschreibungen, Datierungen, Schlagwörter. Sie ist abgeschlossen und in der
[history.md](history.md) beschrieben; sie lief unter der Nummer 41, die damit vergriffen ist.

**Was jetzt hier steht, ist der Rest — und der braucht Ortskenntnis.** Er gehört dem Museumsteam,
nicht dem Rechner:

- **669 Fotos ohne Beschreibung.** Maschinell ist da nichts mehr zu holen: Eine Beschreibung ist
  genau das, was sich aus keinem vorhandenen Feld ableiten lässt. Wer das Bild ansieht und den Ort
  kennt, schreibt in einer Minute, was keine Regel je finden wird.
- **621 Fotos ohne Jahr.** Die 83, die eine Jahreszahl im Text trugen, sind durchgesehen; 52 sind
  datiert, 17 Vorschläge wurden verworfen, weil das Jahr das Gebäude datierte und nicht die
  Aufnahme ([decisions.md](decisions.md), Punkt 37). Der Rest trägt keinen Anhalt. **Ein Teil
  davon löst sich von selbst:** Es ist der Vorrat für „Wann war das?", und der Beitragsbereich
  legt ihn Besuchern vor. Die Zeitleiste reicht seit der Datierung von 1880 bis 2030 und ist damit
  brauchbar — jedes weitere Jahr macht sie dichter, keines mehr macht sie überhaupt erst möglich.

  **Noch nicht durchsucht sind die Schlagwörter**, und das ist der eine Anhalt, den die Runde vom
  11./12. August ausgelassen hat: Sie sah Titel und Beschreibung an, nicht die Stichwörter. Der
  Vorschlag ist, alle Fotos ohne Jahr, aber mit Beschreibung oder Schlagwörtern nach einer
  Jahreszahl zu durchsuchen, das Ergebnis **aufzulisten und erst nach Bestätigung zu übernehmen**.

  **Nachgezählt am 16. August 2026, und die Ausbeute ist klein:** Von 612 Fotos ohne Jahr tragen
  **5** ein Schlagwort mit vierstelliger Zahl und **32** eine Beschreibung mit einer — wobei die
  Beschreibungen weitgehend die schon verworfenen sein dürften; die Überschneidung ist beim
  Aufgreifen zuerst zu prüfen, sonst wird 17 Fotos zum zweiten Mal dieselbe Frage gestellt.

  **Wichtiger als die fünf Fotos ist, was dabei zum Vorschein kommt.** Vier der fünf Schlagwörter
  sind gar keine Stichwörter, sondern Sätze — „Hof Wilhelm Petersen, Seitenansicht, abgerissen
  1971", „Bauernhaus von Paul Stein, im Jahre 1987. Abriss 18.1.1988", „Fotokalender 2014". Sie
  stammen aus der Kommazerlegung von Punkt 41 und gehören in die Beschreibung, nicht in die
  Schlagwortliste. **Und sie zeigen Punkt 37 im Kleinen:** „abgerissen 1971" und „Abriss 18.1.1988"
  datieren den Abriss des Hauses, nicht die Aufnahme; „Fotokalender 2014" datiert den Kalender.
  Nur „ca 1943 1944" trägt ein Datumswort und käme durch.

  Der Weg — auflisten, bestätigen, übernehmen — ist derselbe, den „Offen ist auch das Wie" unten
  meint: Er lohnt nur, wenn er auch für die anderen Fragen dieses Punktes taugt, nicht als
  Einwegskript für fünf Fotos.
- **Rund 100 eigenständige Titel**, unter denen einzelne eher Notiz als Titel sind: „Vermutung:
  hinter der Zahnarztpraxis oder hinter der ‚Börse'". Ob so etwas ein Titel bleibt, in die
  Beschreibung wandert oder verschwindet, entscheidet nur, wer weiß, was auf dem Bild ist.
- **5 Fotos ohne Ort.** Vier lagen lose oben im Import-Ordner, eines kommt aus `Deelenweg`, wo der
  Ortsindex zwei Straßen kennt („Deelenweg I" und „II") und deshalb bewusst nicht rät. Für alle
  fünf gilt: Ein Blick auf das Bild beantwortet es, eine Regel nicht.
- **253 Schlagwörter**, jetzt alle wirklich Stichwörter — die Archivkürzel und die abgeschriebenen
  Rückseiten sind heraus. Ob die verbliebenen taugen, entscheidet sich erst mit
  [Punkt 30](#30--die-karte-nach-schlagwörtern-filtern), wenn daraus ein Filter wird.

**Die Zahlen sind vom 12. August 2026** und wandern: Jeder Besucherbeitrag verschiebt sie. Wer eine
davon braucht, holt sie sich mit `python -m app.cli stats`, statt sie hier abzulesen.

**Offen ist auch das Wie.** Ob dafür ein eigener Arbeitsbereich lohnt oder die vorhandene
Nacharbeits-Liste reicht, ist Teil der Frage — und sie stellt sich jetzt anders als vorher, weil
es nur noch um Fälle geht, bei denen ohnehin ein Mensch das Bild ansieht.

### 50 · Ein Schlagwort für den ganzen Stapel beim Import

Beim Hochladen ein Schlagwort eingeben, das **alle Fotos des Stapels** bekommen — und, wenn es sich
anbietet, in der Liste darunter auch einzelne nachbessern. Wer hundert Fotos aus einem Ordner
„Feuerwehr" hochlädt, weiß beim Hochladen, was sie gemeinsam haben, und niemand tippt es
hinterher hundertmal einzeln nach.

**Der Weg ist gebahnt.** `apply_batch_defaults` in `services/importer.py` nimmt schon Jahr,
Genauigkeit, Koordinate, Ortsname, Bildnachweis und Herkunft entgegen; das Formular in
`admin/ImportView.tsx` hat für Nachweis und Herkunft bereits Felder. Ein Schlagwortfeld daneben und
ein Durchreichen bis `add_tags` ist der ganze Umfang.

**Eine Regel gilt hier aber nicht, und das ist der Fallstrick.** Alle bisherigen Stapelangaben
füllen nur, *was leer ist* — „wo die Datei es besser weiß, gewinnt die Datei". **Schlagwörter sind
keine Felder, sondern eine Menge:** Sie werden ergänzt, nicht ersetzt, und ein Stapelschlagwort
tritt neben das, was die Datei mitbringt. `add_tags` in `services/tags.py` kann das bereits — es
überspringt, was das Foto schon trägt, und legt neue Namen nur einmal an.

Damit gäbe es **drei** Quellen für Schlagwörter, und die Reihenfolge sollte im Code stehen, bevor
jemand sie sich zusammenreimt: die Einstellung `KIEKMAP_IMPORT_TAGS` (gilt für jeden Import
dieses Geräts, in Holm `["Gebäude"]`), die Stichwörter aus der Datei selbst, und neu das
Stapelschlagwort.

**Für die Liste darunter ist es eine Frage, keine Aufgabe.** `ReviewTable` in `ImportView.tsx`
zeigt heute je Zeile Titel, Jahr und Ort — bewusst wenig, weil die Liste nach hundert Uploads
sonst zur Tabellenkalkulation wird. Ein viertes Feld je Zeile ist zu erproben, nicht zu beschließen;
für Einzelfälle gibt es den Foto-Editor, der ein Schlagwortfeld bereits hat.

**Was es wert ist, entscheidet sich mit
[Punkt 30](#30--die-karte-nach-schlagwörtern-filtern):** Solange aus Schlagwörtern kein Filter wird,
sammelt dieser Punkt Angaben, die niemand sieht.

### 51 · Der Abbruch am PIN-Feld heißt „Abbrechen und zurück"

Unter dem Zahlenfeld steht heute **„Zurück zur Karte"**. Das beschreibt, wohin es geht, aber nicht,
was passiert: Wer schon Ziffern getippt hat, liest dort keine Abkürzung zum Verwerfen. Richtig ist
**„Abbrechen und zurück"** — erst die Handlung, dann das Ziel.

Eine Zeile: `t.admin.pin.cancel` in `frontend/src/text/de.ts`. Dass sie hier steht und nicht
nebenbei geändert wurde, hat einen Grund — sie gehört zu
[Punkt 40](#40--ein-durchgang-über-die-ganze-oberfläche), dem Durchgang über die ganze Oberfläche,
und dort werden mehr solche Stellen auftauchen. Einzeln ist sie in zwei Minuten erledigt.

### 31 · Einstellungen in der Verwaltung pflegen statt in der `.env`

Was heute eingerichtet wird, wird in Dateien eingerichtet — und zwar in dreien, an drei Orten, mit
drei verschiedenen Wegen:

| Was | Wo heute | Wie geändert |
|---|---|---|
| PIN der Verwaltung | `.env` (`admin_pin_hash`) | `python -m app.cli pin`, Zeile eintragen, neu starten |
| Import-Schlagwörter, Bildnachweis, Herkunft | `.env` | Datei bearbeiten, neu starten |
| EXIF-Jahresgrenze | `.env` | dito |
| Anklickbare Schlagwörter ([Punkt 30](#30--die-karte-nach-schlagwörtern-filtern)) | wäre `.env` | dito |
| Ortsname, Ausschnitt, Zoomstufen, `streetChoice` | `tiles/region.json` → `data/region.json` | Datei bearbeiten, `make tiles` |
| Wappen | `frontend/public/logo.png` | Datei ersetzen, Frontend neu bauen |

Für ein Museumsteam, das ein- bis zweimal im Jahr an das Gerät geht, ist jeder dieser Wege
unerreichbar. **Die Idee ist deshalb richtig; zu klären ist der Zuschnitt.** Vier Fragen, und die
zweite ist die unangenehme:

**1. Was gehört überhaupt hinein?** `data_dir`, `media_dir` und `cors_origins` beschreiben den
Betrieb und gehören ins Deployment — die haben in einer Verwaltungsmaske nichts verloren. Alles
andere aus der Tabelle beschreibt die **Sammlung** oder den **Ort** und ist ein Kandidat.

**2. Nach einer Wiederherstellung sind die Einstellungen weg.** Die Sicherung nimmt neben der
Datenbank und den Bildern nur `region.json` und `places.json` mit (`LOOSE_FILES` in
`services/backup.py`) — **die `.env` nicht**. Wer ein Gerät ersetzt und die Sicherung einspielt,
hat den ganzen Bestand zurück, aber keine PIN, keine Import-Schlagwörter und keinen Bildnachweis.
Das ist heute schon so und fällt nur nicht auf, weil es noch kein zweites Gerät gab; **[Punkt
18](#18--wiederherstellung-wirklich-proben) wird es zutage fördern.** Einstellungen in der
Datenbank lösten es nebenbei mit.

**3. Die PIN ist ein Sonderfall in beide Richtungen.** Sie in der Verwaltung zu ändern liegt nahe —
man ist ja drin. Aber in der Datenbank reist sie mit der Sicherung: Wer eine ältere Sicherung
einspielt, bekommt die alte PIN zurück, ohne es zu merken. Und `python -m app.cli pin` wäre dann
eine zweite Quelle für dieselbe Sache. Beides ist lösbar, keines von selbst.

**4. Das Wappen ist keine Einstellung, sondern eine Datei im gebauten Frontend.** Über die
Verwaltung hochladen hieße, in ein Bauartefakt zu schreiben, das nginx statisch ausliefert. Es
müsste nach `data/` wandern und vom Backend kommen — dieselbe Bewegung, die `region.json` schon
gemacht hat, und aus demselben Grund: Was sich ändern darf, gehört unter das eingehängte
Verzeichnis.

**Und die Gegenrechnung, die nicht übersehen werden darf:** [adaption.md](adaption.md) sagt heute,
`region.json` und `.env` seien alles, was ein zweiter Ort anfassen muss — zwei Dateien, die man
weitergeben, vergleichen und in ein Repo legen kann. Wandern die Werte in die Datenbank, wird
daraus „starten und durch die Verwaltung gehen". Für Ehrenamtliche besser; für den, der ein
zweites Museum aufsetzt, ist die eine übergebbare Datei dann weg. Vielleicht ist die Antwort
beides: Datei als Startwert, Datenbank als Übersteuerung — genau das gehört durchdacht, bevor
etwas gebaut wird.

### 52 · Den neueren Archivstand abgleichen und nachziehen

Vom Museum ist ein **aktuellerer Datenbestand** eingetroffen. Er ist gegen den Stand abzugleichen,
aus dem der Erstbestand aufgebaut wurde, und alle hinzugekommenen Fotos aus dem Bereich **„Straßen"**
sind ebenfalls aufzunehmen.

**Der Abgleich erledigt sich zum großen Teil von selbst**, und das ist der Grund, warum dieser
Punkt klein anfangen kann: Der Import hasht jede Datei zuerst, und der SHA-256 entscheidet über
Dublette oder nicht. Ein zweiter Durchlauf über den ganzen neuen Ordner legt also **nur an, was
neu ist**; alles Bekannte landet als `duplicate` im Import-Protokoll und rührt den vorhandenen
Bestand nicht an. Die Arbeit von [Punkt 41](history.md) — 815 bereinigte Titel, 349 neu verortete
Fotos, 75 geschriebene Titel — bleibt damit unangetastet.

**Woran zu denken ist:**

- **Die Ordnerstruktur trägt die Verortung.** 758 der 929 Fotos kamen aus
  `01 Orte/Straßen/<Straße>/<Hausnummer>/`; genau daraus liest `services/foldermeta.py` Straße und
  Hausnummer. Kommt der neue Stand anders geschnitten, ist das **vor** dem Import zu klären — die
  171 übrigen Fotos liegen lose in `01 Orte/` und sind der Grund, warum fünf bis heute keinen Ort
  haben.
- **`KIEKMAP_IMPORT_PROVENANCE`** setzt das Präfix der Herkunft
  (`Online-Archiv des Museums, Verzeichnis 01 Orte/`). Steht der neue Stand woanders, gehört die
  Einstellung angepasst, sonst zeigt die Herkunft der neuen Fotos ins Leere.
- **Was inzwischen an den vorhandenen Fotos geändert wurde, darf nicht zurückfallen.** Der Import
  legt nur an und ändert nichts Bestehendes — das ist zu bestätigen, nicht zu glauben.

**Die Reihenfolge steht fest**, und sie ist der eigentliche Inhalt dieses Punktes:

1. **Dieser Punkt zuerst** — die neuen Fotos in den Bestand.
2. Dann [Punkt 42](#42--dubletten-finden-die-beste-behalten-den-rest-zusammenführen), die Dubletten.
   Vorher wäre die Arbeit zweimal zu machen, denn der neue Stand bringt neue Fassungen derselben
   Scans mit — und die erkennt der SHA-256 gerade **nicht**.
3. Und [Punkt 1](#1--der-erstbestand-braucht-eine-durchsicht) gilt für die neuen Fotos genauso: Was
   dort an Durchsicht aussteht, wächst mit ihnen.

### 42 · Dubletten finden, die beste behalten, den Rest zusammenführen

**Erst nach [Punkt 52](#52--den-neueren-archivstand-abgleichen-und-nachziehen)**, dem Nachziehen
des neueren Archivstands: Der bringt neue Fassungen derselben Scans mit, und wer vorher aufräumt,
macht die Arbeit zweimal.

Derselbe Scan liegt mehrfach im Bestand — in unterschiedlicher Scanqualität, mit anderer
Farbkorrektur, mal mit und mal ohne den Text darunter. **Der SHA-256 sieht davon nichts:** Er
erkennt nur bitgleiche Dateien, und zwei Durchläufe desselben Papierabzugs sind nie bitgleich.
Genau deshalb stand die Wiedererkennung über einen Perceptual Hash bisher als eigener Punkt 3 im
Backlog; sie geht hier auf, weil das Erkennen allein das Problem nicht löst.

**Der Punkt hat drei Teile, und nur der erste ist Technik:**

1. **Finden.** Perceptual Hash über die Vorschaubilder. Er erträgt Helligkeit, Kontrast und
   Farbstich; er erträgt **keinen** stark abweichenden Zuschnitt — und ein abgeschnittener
   Bildtext ist genau das. Was er findet, sind Kandidaten, keine Urteile.
2. **Auswählen.** Welche ist die beste? Auflösung ist ein Anhalt, aber nicht der einzige: Ein
   großer Scan mit Farbstich ist schlechter als ein kleiner sauberer, und die Fassung **mit** dem
   Text darunter trägt mehr Information, auch wenn sie schlechter aussieht.
3. **Zusammenführen.** Die Dubletten tragen Angaben, die das Behaltene nicht hat — Titel,
   Beschreibung, Jahr, Ort. Die gehören übernommen, **bevor** etwas verschwindet. Und
   „verschwinden" heißt hier gelöscht im Sinne von [decisions.md](decisions.md), Punkt 16: aus der
   Ausstellung genommen, nicht von der Platte entfernt — wer sich vertut, holt sie zurück.

**Zu entscheiden ist der Grad der Selbsttätigkeit.** Vollautomatisch verliert irgendwann das
bessere Bild, ohne dass es jemand merkt. Halbautomatisch — die Kandidaten werden paarweise
vorgelegt, jemand bestätigt — kostet Zeit, aber nur einmal. Bei 929 Fotos ist das tragbar; die
Frage ist, ob es das bei 5000 noch wäre.

### 34 · Eine Karte in der Nachbearbeitung des Imports

Nach einem Upload steht eine Tabelle mit bis zu dreißig Zeilen (`REVIEW_LIMIT`), in der Titel,
Jahr und **Ort** je Foto nachgetragen werden. Der Ort wird dort über die Ortssuche eingegeben
(`admin/PlaceField.tsx`) — getippt, mit Tastatur, was im Verwaltungsbereich in Ordnung ist. Wer
die Stelle aber *sieht* und den Straßennamen nicht weiß, ist damit ausgesperrt; im Kiosk gibt es
für genau diesen Fall den Kartentipp.

**Zu klären, bevor daraus eine Aufgabe wird:**

- **Was die Karte dort kostet.** Sie ist eine MapLibre-Instanz mit WebGL-Kontext. Verwaltung und
  Kiosk laufen nie gleichzeitig — die Verwaltung ersetzt die Ansicht —, es bliebe also bei einer;
  ob das auf einem Pi neben dreißig Vorschaubildern trägt, ist zu messen.
- **Eine Karte für dreißig Zeilen oder eine je Zeile.** Dreißig Karten sind sicher zu viel;
  denkbar wäre eine, die sich beim Antippen einer Zeile öffnet und den Punkt für diese Zeile
  setzt.
- **Ob es sich überhaupt lohnt.** Der Stapel-Import setzt Ort und Jahr **einmal für alle**, und
  genau dafür ist er gebaut: vierzig Bilder desselben Hofes. Die Zeilennachbearbeitung ist der
  Ausnahmefall im Ausnahmefall.

Nicht wichtig, nicht dringend — erst zu prüfen und zu bewerten, dann zu spezifizieren.

---

## Besucher-Interface

### 30 · Die Karte nach Schlagwörtern filtern

Die Karte filtert heute nach **Zeit** (Schieber) und **Ort** (Ausschnitt). Ein drittes Sieb kommt
dazu: das Schlagwort. Unten in der Ecke der Karte stehen einige wenige zur Wahl, und **immer nur
eines ist aktiv** — ein zweiter Tipp auf dasselbe schaltet es ab, ein Tipp auf ein anderes löst das
bisherige ab. Kein Und, kein Oder, keine Liste zum Abhaken.

**Dazu ein Weg aus der Detailansicht.** Die Schlagwörter eines Fotos sind dort heute nur Text
(`overlay__tags`, drei Zeilen in `PhotoOverlay.tsx`). Ein Tipp darauf soll die Ansicht schließen
und die Karte danach filtern — **Zeit und Ort weit offen**, andere Schlagwörter abgewählt. So
kommt man an Schlagwörter heran, die unten in der Ecke gar nicht angeboten werden. Das so gewählte
erscheint dort dann **neben** den eingerichteten, als ausgewählt, bis es abgewählt wird; danach
verschwindet es wieder samt seiner Auswahlmöglichkeit. Die eingerichteten bleiben.

**Der Bestand ist dafür heute nicht bereit, und das ist der wichtigste Satz dieses Punktes.**
Nachgezählt an den 929 Fotos:

| Schlagwort | Fotos | |
|---|---|---|
| Gebäude | **929** | trägt *jedes* Foto — filtert nichts weg |
| Hauptstraße | 227 | Straßenname, den die Karte über den Ort schon abbildet |
| Förderkreis-Cloud | 142 | Archivkürzel |
| ArchivHolm | 114 | Archivkürzel |
| Winter | 53 | das erste, das etwas über das Bild sagt |

Von 308 Schlagwörtern saßen **260 auf weniger als zehn Fotos**, und „Erntefest" — das Beispiel aus
der Idee — gibt es nicht; es gibt „Fest" und „Feuerwehr". **Die Archivkürzel und die abgeschriebenen
Fotorückseiten sind inzwischen heraus** ([history.md](history.md), 12. August 2026); von 308
Schlagwörtern sind 253 geblieben, und die sind alle wirklich Stichwörter. Ob sie für einen Filter
taugen, ist damit erst jetzt zu beurteilen — und die Zahlen in diesem Punkt sind vom 9. August und
entsprechend zu erneuern.

**Warum die Auswahl eingerichtet wird und sich nicht aus dem Bestand ergibt:** Die naheliegende
Regel wäre „die häufigsten", wie sie die angebotenen Jahrzehnte aus der Sammlung ableitet
(`kiosk/decades.ts`). Hier ergäbe sie „Gebäude, Hauptstraße, Förderkreis-Cloud" — die Häufigkeit
misst hier nicht Bedeutung. Also eine kuratierte Liste, zunächst als Umgebungsvariable neben
`import_tags` in `config.py`. Sie beschreibt die **Sammlung**, nicht den Ort, und gehört deshalb
gerade **nicht** in `region.json`.

**Was technisch fehlt:** `/api/photos` kennt keinen Schlagwortfilter (`api/photos.py`), nur
`/photos/tags/alle` gibt es schon. Dazu ein Zustand im Kiosk-Store neben `timeRange` und `bbox`,
der bei jeder Abfrage mitgeht — und die Abstimmung mit dem Fokus nach einem Beitrag, der Ort und
Zeit heute schon verstellt und zurücknimmt.

### 40 · Ein Durchgang über die ganze Oberfläche

Die Ansicht ist über zehn Stufen gewachsen, und jede Stufe hat für sich gestimmt. Was fehlt, ist
der Blick auf das Ganze: Rückmeldungen einholen, auf Einheitlichkeit prüfen, sammeln, was auffällt,
und es dann in einem Zug umsetzen statt in zwölf Einzelentscheidungen.

**Drei Befunde standen schon als eigene Punkte** und waren damit die erste Ernte dieses
Durchgangs, nicht sein Ersatz: Punkt 10 (Maße der Detailansicht) — und Punkt 28 (die
Knopfsprache) sowie Punkt 29 (der Kopfbereich). Alle drei sind inzwischen erledigt. Dass ein
Befund einzeln lösbar war, spricht nicht gegen diesen Punkt: Die Knopfsprache stand als eigener
Punkt da, *weil* jemand sie am Stück angesehen hatte. Genau das soll hier für den Rest passieren.

**Was dieser Punkt darüber hinaus leistet:**

- **Rückmeldungen einholen**, und zwar von Menschen, die das Gerät nicht gebaut haben. Der
  ergiebigste Weg dafür steht schon als
  [Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) hier — zusehen, ohne zu helfen.
  Dieser Punkt ist das, was danach mit dem Gesehenen passiert.
- **Beide Bereiche vergleichen.** Besucheransicht und Verwaltung haben eigene Maße für Knöpfe,
  Eingabefelder und Mindesthöhen; die 48 px aus der Zielgruppen-Regel sind an jeder Stelle einzeln
  eingehalten statt an einer. Das ist erträglich, solange es jemand weiß — und ein Fallstrick,
  sobald es niemand mehr weiß.
- **Sammeln statt sofort ändern.** Eine Liste, die am Stück entschieden wird, ergibt eine
  Oberfläche; zwölf einzeln entschiedene Kleinigkeiten ergeben zwölf Sonderfälle.

**Der erste Eintrag dieser Liste liegt schon vor.** Er stand bis zum 9. August 2026 als eigener
Punkt 13 hier: Beim Angleichen von „Hilf mit:" an „Bilder aus" (`45ae42d`) wurde aus dem Akzentbraun
eine stille graue Zeile — die bewusste Folge einer bewussten Entscheidung, aber es war zugleich der
einzige Blickfang der linken Spalte. Als eigener Punkt war das zu klein, um je an die Reihe zu
kommen, und zu vereinzelt, um richtig entschieden zu werden: Ob der Beitragsbereich seinen Zug aufs
Auge zurückbekommt, ist eine Frage an die Farbverteilung des ganzen Schirms, nicht an eine Zeile.
Genau dafür ist dieser Punkt da.

### 8 · Historische Karte als umschaltbare Grundkarte

**Der größte Posten auf dieser Seite** — und die einzige Idee, die aus einer schönen Karte eine
Aussage macht.

**Warum.** Historische Fotos auf einer historischen Karte. Der Besucher sähe das Foto *und* den
Ort, wie er damals aussah — und der Zeitschieber, der bisher nur filtert, bekäme eine zweite
Bedeutung.

**Woher.** Preußische Landesaufnahme (um 1880) oder Urkataster. Schleswig-Holstein stellt
Geobasisdaten über sein Open-Data-Portal bereit; ob die historischen Blätter für Kreis Pinneberg
dabei und in brauchbarer Auflösung sind, ist **ungeprüft**. Das ist der erste Schritt, nicht der
Code.

**Wie es ins Projekt passt.** Rasterkacheln, einmal heruntergeladen und als zweite PMTiles-Datei
verpackt — dasselbe Muster wie die heutige Kartendatei, kein neuer Datenweg und kein Bruch mit dem
Offline-Betrieb. `make tiles` bekäme einen zweiten Schritt.

**Der Haken, der die Form bestimmt.** Auf einer Karte von 1880 fehlen die Straßen, die es heute
gibt. Ortssuche und Verortung durch Besucher hängen aber an heutigen Straßennamen. Also
**umschaltbar**: heutige Karte zum Verorten, historische zum Anschauen. Ein Knopf auf der Karte,
kein Ersatz.

**Vorher zu klären:**

- Gibt es die Blätter für Holm, und in welcher Auflösung?
- Lizenz — meist DL-DE/BY-2.0 oder CC-BY, also mit Namensnennung nutzbar. Nachlesen, nicht
  annehmen. Die Nennung gehört dann neben die OpenStreetMap-Zeile.
- Größe. Raster ist um ein Vielfaches schwerer als Vektor; für 5 km Umkreis und Zoom 13–16 sollte
  es im zweistelligen Megabyte-Bereich bleiben, das ist zu messen.

*Der billige Teil ist bereits gebaut: der Kartenstil „Papier" in den Farben der Oberfläche
(`2e648f6`).*

### 9 · Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode

Heute lädt der Leerlauf nach fünf Minuten die Seite neu (`IDLE_MS` in `kiosk/idle.ts`) — der
Bildschirm steht dann in der Standardansicht und wartet. Ein bewegtes Bild würde Besucher eher an
das Gerät holen.

**Zu evaluieren ist der Ken-Burns-Effekt** — das langsame Fahren und Zoomen über ein stehendes
Foto, das Bewegung erzeugt, ohne dass etwas geschnitten werden müsste. Wenn er nicht trägt,
wenigstens eine schlichte Diashow. **Zwei Stellen hätten etwas davon, und das ist das eigentliche
Argument:** Was hier gebaut wird, wird zweimal gebraucht.

1. **Der Attract-Mode** bei Leerlauf, statt der wartenden Standardansicht.
2. **Die Blätteransicht in der Detailansicht.** Liegen mehrere Fotos an derselben Stelle, öffnen
   sie sich als Stapel und werden durchgeblättert (`stepInStack`, „x von y" im Überlagerungsbild).
   Heute nur von Hand — als Galerie, die von selbst weiterläuft, wäre das dieselbe Mechanik.

**Was vorher zu messen ist, und zwar am Gerät:**

- **Bewegtbild neben der Karte.** MapLibre hält bereits einen WebGL-Kontext. Eine
  CSS-Transformation über ein bildschirmfüllendes Foto ist für sich billig, zusammen mit der Karte
  auf einem Pi aber nicht selbstverständlich. Das gehört zum Dauerlauf aus
  [Punkt 15](#15--abnahme-auf-dem-ersten-pi): Ein Effekt, der stundenlang läuft,
  ist genau die Sorte Sache, an der ein Kiosk langsam stirbt.
- **Die Auflösung reicht möglicherweise nicht.** Vorschaubilder liegen in 240 und 1200 px
  (`THUMBNAIL_SIZES`). Auf einem 1080p-Schirm ist ein 1200er Bild knapp — und ein Ken-Burns-Effekt
  *zoomt hinein*, vergrößert den Mangel also. Entweder wird dafür das Original geladen, was
  mehrere Megabyte je Bild bedeutet, oder es kommt eine dritte Vorschaugröße dazu.

**Was der Attract-Mode nicht darf:** die Arbeit von jemandem wegwerfen, der gerade etwas
beigetragen hat. Der Leerlauf lädt heute neu, gerade *weil* das der sichere Zustand ist — derselbe
Zielkonflikt ist beim Wappen schon einmal entschieden worden, das seit dem 9. August 2026 neu
lädt (Punkt 29, erledigt): Dort war die Antwort, dass der Verlust hinnehmbar ist, weil es sonst
gar keinen Weg zurück gibt. **Beim Attract-Mode gilt das nicht** — er startet von selbst, und was
er wegwirft, hat niemand weggeworfen.

### 54 · Das Layout der Detailansicht dem Bildformat folgen lassen

**Der Rest von Punkt 10**, der am 16. August 2026 bewusst liegen geblieben ist. Behoben sind dort
die drei pragmatischen Teile: Die Textspalte wächst mit statt fest zu stehen (auf 1024 px bekommt
das Bild 610 statt 466 px), die Blätterknöpfe stehen fest am unteren Rand, und der Schließen-Knopf
sitzt in der Ecke des Schirms. Siehe [history.md](history.md) und
[decisions.md](decisions.md), Punkt 44.

**Was offen bleibt, ist der Weg an die Ursache:** Ein Querformat braucht Breite und hat Höhe übrig
— der Text gehörte dann **darunter**. Ein Hochformat braucht Höhe und hat Breite übrig — dort ist
der Text **daneben** richtig, so wie heute. Die Ansicht weiß, was sie zeigt: Das Bild trägt sein
Seitenverhältnis als `aspect-ratio` (`PhotoOverlay.tsx`), und `.overlay__content` ist ein Raster
mit zwei Spalten, das sich auf eine umstellen ließe.

**Der Bestand sagt, dass es sich lohnt: 884 Querformate gegen 44 Hochformate.** Genau deshalb ist
es aber nichts, was man nebenbei macht — die Umstellung trifft fast jedes Foto der Sammlung, und
ob sie besser aussieht, entscheidet sich auf einem Gerät in einem Raum und nicht in einem
Browserfenster.

**Deshalb wartet dieser Punkt auf
[Punkt 19](#19--displayauflösung-und--orientierung-des-museumsgeräts)**, und zwar wirklich: Steht
das Gerät am Ende **hochkant**, dreht sich die Rechnung um und die Umstellung müsste in die andere
Richtung gehen. Solange die Auflösung nicht feststeht, wäre jede Zahl hier eine Annahme.

### 43 · Der Zeitschieber soll jahrgenau zählen, nicht jahrzehntgenau

Die Balken hinter dem Zeitschieber zeigen heute nicht immer Jahre. `bar_width()` in
`backend/app/services/dates.py` weitet die Balken auf **zehn Jahre**, sobald irgendwo im Bestand
auch nur ein einziges Foto als „1920er" statt als Jahr datiert ist — und das betrifft praktisch die
ganze Sammlung: 673 der 929 Fotos tragen gar kein Jahr, aber ein gutes Stück des Rests trägt nur ein
Jahrzehnt. Die Folge: Ein Jahrzehnt bekommt einen einzigen Balken, auch wenn darunter drei
jahrgenau datierte Fotos in 1932 liegen und keines in den übrigen neun Jahren — die Verteilung
*innerhalb* der Dekade verschwindet vollständig.

**Gewünscht:** Die Achse zählt immer in Jahren. Ein auf ein Jahrzehnt datiertes Foto trägt zu
**jedem** der zehn Jahre ein Zehntel bei, statt seine ganze Zählung auf ein einziges Jahr (oder,
wie heute, auf einen zehn Jahre breiten Balken) zu häufen — dieselbe Überlegung wie beim
Überlappungs-Filter (`services/dates.py`, siehe CLAUDE.md): eine grobe Angabe verschwindet nicht,
sie verteilt sich ehrlich.

**Was das an der Berechnung ändert:**

- `bar_width()` entfiele in der heutigen Form oder würde auf `1` festgenagelt — die Funktion
  existiert nur, um Balken zu verbreitern, wenn feine Angaben fehlen; genau das soll nicht mehr
  passieren.
- Die SQL-Abfrage in `histogram()` (`api/photos.py`) gruppiert heute nach `bar_start`
  (`date_from` gekappt auf die Balkenbreite) und zählt Fotos. Eine gewichtete Zählung über einen
  Jahresbereich ist damit nicht mehr eine `GROUP BY`-Abfrage über eine Spalte, sondern eine Summe
  über die Jahre zwischen `date_from` und `date_to` — SQLite kennt kein `generate_series`, das
  bräuchte entweder eine Hilfstabelle mit Jahreszahlen oder das Aufsummieren in Python.
- `Bar.count` (`schemas.py`, `frontend/src/api/client.ts`) ist heute ein `int`. Zehntelwerte machen
  daraus einen Bruch — zu klären, ob roh als Fließkommazahl ausgeliefert oder für die Anzeige
  gerundet wird. Die Balkenhöhe (`TimeSlider.tsx`, `barHeight()`) ist bereits relativ zum höchsten
  Balken und käme mit Fließkommazahlen ohne Änderung aus; die Beschriftung `title={...}: ${count}`
  müsste einen Nachkommawert vertretbar formatieren.
- **Was unverändert bleibt:** Der Zeit*filter* selbst fragt weiterhin auf Überlappung ab
  (`date_from <= bis AND date_to >= von`) und zeigt ein jahrzehntdatiertes Foto bei jeder Auswahl,
  die die Dekade berührt — das hier betrifft nur die **Visualisierung** hinter dem Schieber, nicht,
  welche Fotos eine Auswahl zurückgibt.

**Zu prüfen vor dem Bauen:** Ob `MAX_BARS` (heute 30, zur Verbreiterung großer Zeitspannen) in
einer Welt ohne Balkenverbreiterung noch dieselbe Rolle spielt — bei jahrgenauer Zählung über einen
Bestand von hundert Jahren stünden sonst hundert schmale Balken, wo heute zehn breite stehen.

---

## Infrastruktur

### 14 · Bedienbarkeitstest mit der echten Zielgruppe

Eine ehrenamtliche Person die Sicherung durchführen lassen, **ohne zu helfen**, und zusehen, wo sie
stockt. Der aussagekräftigste Test des ganzen Projekts — und die zweite Hälfte des
Abnahmekriteriums von Stufe 9, die bisher fehlt.

**Dringend ist er, weil er kein Gerät braucht.** Über
[Punkt 21](#21--deployment-auf-einem-webserver-evaluieren) steht das System dem Museumsteam zur
Verfügung, bevor Display und Pi beschafft sind — und damit ist dieser Test heute durchführbar statt
erst nach der Beschaffung. Was er zutage fördert, ändert womöglich Dinge, die danach teurer zu
ändern sind.

### 15 · Abnahme auf dem ersten Pi

**Der gewichtigste offene Punkt des Projekts** — dringend ist er nur nicht, weil das Gerät fehlt.
Alles unter `deploy/pi/` ist **ungeprüft**; beim Bauen gab es keins. Die Shell-Syntax stimmt,
gelaufen ist nichts. Betroffen sind `setup-pi.sh`, `kiekmap-kiosk`, `kiekmap-kiosk.service`,
`update.sh`, `99-kiekmap-usb.rules` und `kiekmap-usb-mount`.

**Die Container selbst sind es nicht mehr** (Punkt 17, erledigt am 14. August 2026): Beide Abbilder
bauen, nginx liefert die Karte kachelweise aus, die Seite fragt nichts Fremdes an, und der
Schemastand wird beim Start nachgezogen. Geprüft wurde auf einem Mac, und das lässt genau zwei
Dinge offen, die hierher gehören: **der USB-Weg** (siehe Punkt 18) und **das Verhalten nach einem
Neustart oder Stromausfall** — `restart: unless-stopped` ist eine Zusage, die nur ein Gerät
einlösen kann.

**Der erste Pi ist damit zugleich die Abnahme der Stufen 9 und 10.** Was zuerst hakt, gehört nach
[operations.md](operations.md).

Die erwarteten Stolpersteine, damit sie nicht erst gesucht werden müssen:

- **`:rshared` am `/media`-Mount.** Ein Docker-Bind-Mount zeigt später eingehängte Datenträger nur
  mit dieser Propagation. Ohne sie bleibt ein eingesteckter Stick **ohne Fehlermeldung**
  unsichtbar — der teuerste Fehlerfall, weil er wie „kein Stick" aussieht.
- **`uid=1000` bei FAT-Sticks**, sonst gehört der Einhängepunkt root und die Sicherung schreibt
  nicht.
- **Schwarzer Bildschirm mit der Meldung *„unable to open primary DRM device"*:** Dann fehlt eine
  der vier Sitzungszeilen `PAMName`, `TTYPath`, `StandardInput`, `UtmpIdentifier` in der
  systemd-Unit, oder der Benutzer ist nicht in den Gruppen `video`/`render`.

**Die sechs Prüfungen.** Sie standen bis zum 9. August 2026 als eigener Punkt 16 hier, dessen Text
mit „Der praktische Teil von Punkt 15" begann — zwei Nummern für eine Sache. Die letzten beiden
kamen aus Punkt 12 und 24 dazu:

- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Gezogener Netzstecker im Betrieb** — hier zeigt sich, ob
  `--disable-session-crashed-bubble` das tut, wofür es gedacht ist.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen. Kioske
  sterben an einem langsamen Leck im Frontend, nicht am Backend.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.
- **Der 100-m-Fokus nach einem Besucherbeitrag.** Die Karte fährt auf hundert Meter heran, die
  Vektorkacheln reichen aber nur bis Zoom 15. MapLibre skaliert sauber hoch, die Beschriftungen
  werden dabei groß. Wirkt das im Museum unruhig, ist **der Radius die Stellschraube, nicht die
  Bauform** — deshalb ist es eine Prüfung und keine Aufgabe.
- **Eine USB-Tastatur im laufenden Betrieb anstecken.** Wird sie erkannt, ohne dass jemand den Pi
  neu startet?

**Wozu die Tastatur gebraucht wird**, damit die Prüfung ihren Sinn behält: Die Besucheransicht
braucht seit dem 8. August 2026 keine mehr (siehe [history.md](history.md)) — der
Verwaltungsbereich dagegen hat **13 Eingabefelder in sieben Dateien**, und daran soll sich nichts
ändern: Wer Fotos pflegt, tippt. Die Antwort steht damit fest — eine **ausleihbare** Tastatur, die
nur zur Pflege angesteckt wird. Sie liegt dann nicht im Ausstellungsraum herum, verschmutzt nicht
und öffnet den Besuchern keine Tastenwege in Chromium, die der Kiosk gerade zumacht (F11, Strg-W,
Alt-Tab). Offen ist nur noch die Prüfung oben.

### 18 · Wiederherstellung wirklich proben

Auf ein zweites, leeres Gerät zurückspielen. **Ein ungetestetes Backup ist kein Backup.** Erprobt
ist bisher nur der Weg gegen ein `hdiutil`-Prüfvolumen auf dem Mac.

**Der USB-Weg im Container ist weiterhin ungeprüft**, und zwar als Einziges aus dem erledigten
Punkt 17: Die Prüfung des Containerbetriebs am 14. August 2026 lief auf einem Mac, wo es weder
`/media` noch die Mount-Propagierung `rshared` gibt (siehe
[`deploy/docker-compose.mac.yml`](../deploy/docker-compose.mac.yml)). Genau `rshared` soll aber den
Fall lösen, dass ein Stick **nach** dem Start des Containers eingesteckt wird — der Fall, der im
Museum der Normalfall ist. Er braucht Blech und gehört in denselben Durchgang wie diese Probe.

### 19 · Displayauflösung und -orientierung des Museumsgeräts

Steht noch nicht fest und beeinflusst die Layoutmaße. Die Ansicht ist bisher gegen 1280 × 800
nachgemessen; die Variable `--crest` hat für schmale Schirme bereits eine Media Query.

**Zwei Punkte warten auf diese Antwort**, und beide werden von ihr nicht nur abgestuft, sondern
umgestellt:

- [Punkt 54](#54--das-layout-der-detailansicht-dem-bildformat-folgen-lassen), das Layout der
  Detailansicht. Steht das Gerät **hochkant**, dreht sich die Rechnung um: Dann hat das
  querformatige Bild Breite im Überfluss und der Text darunter Platz.
- Der Kopfbereich hat sich davon inzwischen gelöst (Punkt 29, erledigt): Die drei Elemente
  richten sich an einer gemeinsamen Mittellinie aus statt an drei Rechnungen, und das gilt in
  jeder Breite. **Die Auflösung entscheidet dort nichts mehr** — ein Hinweis darauf, dass eine
  Abhängigkeit von dieser Frage auch eine schlecht gebaute Stelle sein kann.

**Die Frage ist also kleiner, als sie aussieht, und sollte früh gestellt werden**: Es ist eine
Frage an das Museum, keine an den Code, und sie kostet nichts als ein Telefonat.

### 20 · Das Gerät muss einen Stromausfall überstehen

Gegen SD-Karten-Korruption bei Stromausfall. Der Pi wird im Museum nicht heruntergefahren, sondern
ausgeschaltet — das ist auf Dauer der wahrscheinlichste Ausfallgrund.

**Das Ziel steht, der Weg nicht.** Zu verhindern ist, dass ein Verlust der Stromversorgung mit
hoher Wahrscheinlichkeit dazu führt, dass das Gerät **nicht mehr unterbrechungsfrei startet**. Ein
Read-Only-Overlay ist dafür ein Mittel, nicht die Aufgabe — der Punkt hieß bis zum 16. August 2026
nach dem Mittel und ist deshalb umbenannt.

**Erst abzuwägen ist das Risiko**, bevor irgendetwas gebaut wird: Wie wahrscheinlich sind
Datenverlust und ein beschädigtes Dateisystem beim Ziehen des Steckers überhaupt? SQLite läuft im
WAL-Modus mit `synchronous=NORMAL`, was für die Datenbank selbst schon einiges abdeckt; die Frage
gilt der SD-Karte und dem Betriebssystem darauf.

**Eine leichtere Möglichkeit steht im Raum:** in der Verwaltung statt „Anzeige neu laden"
(`t.admin.…reload`) einen **Herunterfahren-Knopf**. Dann gäbe es einen geordneten Weg, das Gerät
auszuschalten, und ein Read-Only-Overlay wäre womöglich gar nicht nötig. Zu klären wäre, wer diesen
Knopf drückt und was passiert, wenn es niemand tut — die Abwägung gehört vor die Entscheidung.

*Aufgenommen am 16. August 2026, ausdrücklich noch ohne Analyse.*

---

## Entwicklung

Nicht das Programm, sondern die Arbeit daran: wie das Projekt geordnet, veröffentlicht und
weitergegeben wird.

### 21 · Deployment auf einem Webserver evaluieren

Das System dem Museumsteam **zunächst online** anbieten — zur Erprobung und vor allem zum Aufbau
der Fotodatenbank, bevor ein Pi im Ausstellungsraum steht. Die Bilder könnten so über Monate von
zu Hause aus eingepflegt werden.

**Das macht diesen Punkt dringend**, obwohl er nach einer Evaluierung aussieht: Sein Wert ist
zeitgebunden. Solange kein Zugang steht, pflegt niemand Fotos ein, und jede Woche Verzögerung ist
eine verlorene Woche Datenbankaufbau. Ausserdem hängt
[Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) daran — der Bedienbarkeitstest wird
so möglich, bevor Hardware beschafft ist.

Technisch ist der Weg kurz, und seit dem 14. August 2026 ist das keine Annahme mehr, sondern
gemessen (Punkt 17): Es läuft in Containern (`make prod`), das Frontend ist statisch, nginx steht
davor, und die Datenbank ist eine Datei. Die Fragen liegen woanders:

- **Was aus dem Offline-Versprechen wird.** Die Regel „null Anfragen an eine fremde Herkunft" bleibt
  erfüllt, sie kostet online nur nichts mehr. Umgekehrt gilt: Kartendatei und Ortsindex sind auf
  einen Rechner im Ausstellungsraum zugeschnitten — 4,6 MB Kacheln und 1,5 MB Ortsindex über eine
  langsame Leitung sind spürbar, aber tragbar.
- **Wie die Daten zurück auf den Pi kommen.** Das ist der eigentliche Zweck, und dafür gibt es das
  Werkzeug bereits: Sicherung und Wiederherstellung. Zu prüfen ist, ob der Weg auch als
  Übertragungsweg taugt — dann wäre der Umzug vom Webserver ins Museum ein bekannter Vorgang und
  kein Sonderfall.

#### Der Entwurf steht — am 15. August 2026 entschieden

Die Frage nach dem Zugriffsschutz ist beantwortet, damit sie beim Aufgreifen nicht noch einmal
gestellt werden muss.

**Eine Tür vor der ganzen Anwendung, nichts in ihr.** Das löst die offene Beitragstür und die
fehlende Ratenbegrenzung in einem Zug — beides ist hinter einer Anmeldung kein Problem mehr. Der
umgekehrte Weg, den Schutz *in* die Anwendung zu bauen, verbögte die Besucheransicht dauerhaft für
einen Betrieb, der Wochen dauert.

```
Internet ──HTTPS──► Caddy ──HTTP──► nginx (frontend) ──► uvicorn (backend)
                      │                unveraendert        unveraendert
                 Let's Encrypt
                 basic_auth
```

**Traefik und Keycloak sind geprüft und verworfen.** Frontend und Backend liegen **schon** auf
einem Ursprung und einem Port — nginx liefert die Seite und leitet `/api/` weiter, das Backend ist
nach aussen gar nicht veröffentlicht. Traefik brächte Routing für Dienste, die es nicht gibt.
Keycloak wäre ein zweites System mit eigener Datenbank für zwei bis fünf Ehrenamtliche, und weil
das Programm kein OIDC spricht, säße es hinter einem Auth-Proxy, der die eigentliche Arbeit tut.
Caddy dagegen ist vier Zeilen: automatisches Let's Encrypt, `basic_auth` eingebaut.

**Entschieden:** ein kleiner VPS in Deutschland (arm64, dieselbe Architektur wie Pi und Mac), ein
gemeinsames Passwort für Team und einzelne Testleser, und `deploy/docker-compose.web.yml` als
dritte Überlagerung neben der des Pi und der des Macs — die Pi-Datei bleibt unangetastet.

**Vier Dinge, die beim Bauen sonst erst wieder auffallen:**

1. **`ports: !reset []` beim `frontend`** ist die sicherheitskritische Zeile: Ohne sie umginge
   `http://<ip>/` den Türsteher. Compose führt `ports` sonst zusammen, statt zu ersetzen.
2. **Auch die API muss ohne Passwort 401 sagen**, nicht nur die Seite. Das ist die Prüfung, für die
   der ganze Entwurf existiert.
3. **Auf einem VPS gibt es keine USB-Sticks.** `find_drives` liefert eine leere Liste, der
   Sicherungsknopf hat kein Ziel — die Sicherung der Online-Instanz ist der **ZIP-Download**, und
   jemand muss ihn regelmässig ziehen. Die Instanz wird für Wochen der massgebliche Bestand sein.
4. **Die Admin-PIN wird länger.** `app.cli pin` nimmt bis zu zwölf Ziffern; vier sind im offenen
   Netz zu wenig, falls das gemeinsame Passwort weitergereicht wird. Kein Codeeingriff.

**Was der Entwurf nicht löst:** Eine Anmeldemaske vor dem Kiosk verfälscht
[Punkt 14](#14--bedienbarkeitstest-mit-der-echten-zielgruppe). Für Testleser, denen man das
Passwort nennt, ist das hinnehmbar; ein echter Bedienbarkeitstest mit unvorbereiteten Besuchern
gehört vor Ort auf ein Gerät.

### 39 · Den Code prüfen lassen

Das Programm ist von einer Person und einem Sprachmodell gebaut worden. Vor einer Veröffentlichung
([Punkt 22](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes)) und vor dem ersten
Dauerbetrieb im Museum gehört ein Durchgang von aussen darüber — durch ein anderes Modell oder
einen zweiten Menschen.

**Worauf sich das lohnt zu richten**, weil es die Stellen sind, die dieses Projekt eigen machen:

- **Die stillen Fachfehler.** Überlappung statt Enthaltensein bei den Datumsintervallen, das
  Scandatum, das nicht datieren darf, die Genauigkeit, die neben der Koordinate mitreist. Sie
  haben Tests — die Frage ist, ob die Tests das prüfen, was sie zu prüfen vorgeben.
- **Nebenwirkungen zwischen den Zuständen.** Karte, Zeitraum, Beitragsbereich und Fokus greifen
  ineinander; die beiden Fehler vom 8. und 9. August entstanden genau dort und waren an reinen
  Funktionen nicht zu sehen.
- **Was auf dem Pi anders ist.** Speicherverhalten über Stunden, WebGL neben Bewegtbild, die
  Annahmen in `deploy/pi/`, die noch nie gelaufen sind.

Kein Selbstzweck: Der Nutzen entsteht dort, wo jemand ohne die Vorgeschichte liest — und deshalb
Annahmen sieht, die dem, der sie getroffen hat, unsichtbar sind.

### 22 · Versionierung, Releaseprozess und Veröffentlichung des Codes

**Stand:** `development.md` kündigt SemVer-Tags und Conventional Commits an, beides zusammen
versioniert. Tatsächlich gibt es nach 99 Commits **keinen einzigen Tag**; `package.json` und
`pyproject.toml` stehen beide auf `0.1.0`, und `deploy/docker-compose.yml` baut Images mit
`${KIEKMAP_VERSION:-dev}`. Es fehlt also nicht die Entscheidung, sondern ihre Umsetzung: Was löst
eine Version aus, wer setzt den Tag, und wie kommt die Nummer in die beiden Dateien und in das
Image?

Daran hängt der Updateweg auf den Pi, der schon gebaut ist (`deploy/pi/update.sh` spielt ein
Update vom Stick ein) — er braucht etwas, das er einspielen kann.

**Die zweite, größere Frage: Wie öffentlich wird das Repo?** Zu recherchieren sind die üblichen
Vorgehensweisen und ihre Vor- und Nachteile. Die Bandbreite reicht von „alles öffentlich, von der
ersten Zeile an" bis „privates Arbeitsrepo, öffentlich nur die Release-Stände". Kurz gefasst:
Vollständige Offenheit ist die übliche und die ehrlichste Form, sie macht aber jede Zwischenstufe
und jeden Fehlversuch dauerhaft sichtbar; ein reines Release-Repo schützt davor, verliert aber die
Historie, die dieses Projekt gerade auszeichnet — die Commit-Nachrichten hier tragen die
Begründungen.

**Die beiden Blocker davor sind erledigt** (5. August 2026): das Wappen ist aus Repo und Historie
verschwunden, der Beispielbestand ist erfunden und mitgeliefert. Wie das ausging und was dabei
anders kam als geplant, steht in [history.md](history.md). **Offen bleibt der Releaseprozess
selbst** — und [Punkt 23](#23--lizenz-des-projekts-und-der-verwendeten-komponenten), der vor einer
Veröffentlichung ebenfalls beantwortet sein muss.

### 23 · Lizenz des Projekts und der verwendeten Komponenten

Noch festzulegen, und **Voraussetzung für [Punkt 22](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes)**.
Zwei getrennte Fragen, die oft verwechselt werden:

- **Unter welcher Lizenz steht Kiekmap selbst?** Für ein Projekt, das ausdrücklich für ein zweites
  Museum nachnutzbar sein soll, ist das keine Formalie — ohne Lizenz ist Nachnutzung rechtlich
  nicht erlaubt, auch wenn der Code offen daliegt.
- **Was verlangen die verwendeten Komponenten?** Bisher steht im README nur der Satz „Alle
  verwendeten Komponenten sind Open Source" — das ist geglaubt, nicht geprüft. Nachzusehen sind
  mindestens MapLibre GL (BSD-3), PMTiles, `@protomaps/basemaps` samt der mitgelieferten
  **Schriften und Symbole** unter `frontend/public/basemaps/`, die OpenStreetMap-Daten in Kacheln
  und Ortsindex (ODbL — verlangt Namensnennung, die auf der Karte steht) und die
  Python-Abhängigkeiten. Die Kombination entscheidet, welche Lizenz für Kiekmap überhaupt möglich
  ist.

Gehört anschließend in eine `LICENSE`-Datei und in den Lizenzabschnitt des README.
