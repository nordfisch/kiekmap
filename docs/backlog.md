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
| 41 | [Den Erstbestand maschinell vorbereiten](#41--den-erstbestand-maschinell-vorbereiten) | Aufgabe | wichtig · dringend |
| 1 | [Der Erstbestand braucht eine Durchsicht](#1--der-erstbestand-braucht-eine-durchsicht) | Aufgabe | wichtig · dringend |
| 25 | [Vom Foto direkt in seine Bearbeitung](#25--vom-foto-direkt-in-seine-bearbeitung) | Aufgabe | wichtig |
| 31 | [Einstellungen in der Verwaltung pflegen statt in der `.env`](#31--einstellungen-in-der-verwaltung-pflegen-statt-in-der-env) | Frage | wichtig |
| 42 | [Dubletten finden, die beste behalten, den Rest zusammenführen](#42--dubletten-finden-die-beste-behalten-den-rest-zusammenführen) | Frage | wichtig |
| 34 | [Eine Karte in der Nachbearbeitung des Imports](#34--eine-karte-in-der-nachbearbeitung-des-imports) | Idee | — |
| | **Besucher-Interface** | | |
| 36 | [„Hilf mit" soll auch nachschärfen, nicht nur füllen](#36--hilf-mit-soll-auch-nachschärfen-nicht-nur-füllen) | Frage | wichtig |
| 27 | [Unter dem Vorschaubild: Adresse und Jahr](#27--unter-dem-vorschaubild-adresse-und-jahr) | Aufgabe | wichtig |
| 30 | [Die Karte nach Schlagwörtern filtern](#30--die-karte-nach-schlagwörtern-filtern) | Idee | wichtig |
| 35 | [Hausnummern auf der Karte](#35--hausnummern-auf-der-karte) | Idee | — |
| 40 | [Ein Durchgang über die ganze Oberfläche](#40--ein-durchgang-über-die-ganze-oberfläche) | Aufgabe | wichtig |
| 38 | [Sprünge beim Gruppieren, und wie genau die Punkte überhaupt liegen](#38--sprünge-beim-gruppieren-und-wie-genau-die-punkte-überhaupt-liegen) | Frage | — |
| 8 | [Historische Karte als umschaltbare Grundkarte](#8--historische-karte-als-umschaltbare-grundkarte) | Idee | wichtig |
| 9 | [Bilder in Bewegung: Diashow, Ken-Burns-Effekt, Attract-Mode](#9--bilder-in-bewegung-diashow-ken-burns-effekt-attract-mode) | Idee | wichtig |
| 28 | [Die Knopfsprache der Besucheransicht](#28--die-knopfsprache-der-besucheransicht) | Aufgabe | wichtig |
| 29 | [Der Kopfbereich: Maße, Wappen, Titel](#29--der-kopfbereich-maße-wappen-titel) | Aufgabe | wichtig |
| 10 | [Detailansicht: Maße aufräumen](#10--detailansicht-maße-aufräumen) | **Fehler** | — |
| | **Infrastruktur** | | |
| 14 | [Bedienbarkeitstest mit der echten Zielgruppe](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) | Aufgabe | wichtig · dringend |
| 15 | [Abnahme auf dem ersten Pi](#15--abnahme-auf-dem-ersten-pi) | Aufgabe | wichtig |
| 17 | [Containerbetrieb prüfen](#17--containerbetrieb-prüfen) | Aufgabe | wichtig |
| 18 | [Wiederherstellung wirklich proben](#18--wiederherstellung-wirklich-proben) | Aufgabe | wichtig |
| 19 | [Displayauflösung und -orientierung des Museumsgeräts](#19--displayauflösung-und--orientierung-des-museumsgeräts) | Frage | wichtig |
| 20 | [Read-Only-Overlay-Dateisystem](#20--read-only-overlay-dateisystem) | Idee | — |
| | **Entwicklung** | | |
| 21 | [Deployment auf einem Webserver evaluieren](#21--deployment-auf-einem-webserver-evaluieren) | Frage | wichtig · dringend |
| 39 | [Den Code prüfen lassen](#39--den-code-prüfen-lassen) | Aufgabe | wichtig |
| 37 | [Die Straßenauswahl in der Adaptionsanleitung erklären](#37--die-straßenauswahl-in-der-adaptionsanleitung-erklären) | Aufgabe | wichtig |
| 22 | [Versionierung, Releaseprozess und Veröffentlichung des Codes](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes) | Frage | wichtig |
| 23 | [Lizenz des Projekts und der verwendeten Komponenten](#23--lizenz-des-projekts-und-der-verwendeten-komponenten) | Frage | wichtig |

**Ein Fehler ist offen**: Punkt 10 zerdrückt das Foto auf einem kleinen Schirm.

**Vierzehn Nummern sind vergriffen** — 2, 3, 4, 5, 6, 7, 11, 12, 13, 16, 24, 26, 32, 33. Sie sind erledigt,
aufgelöst oder gestrichen; was aus jeder wurde, steht in [history.md](history.md). Der nächste
neue Punkt bekommt die **43**.

---

## Verwaltung

### 1 · Der Erstbestand braucht eine Durchsicht

929 Fotos sind eingelesen, und der Import hat aus Dateien und Ordnernamen herausgeholt, was
darin stand. Was er *nicht* konnte, ist jetzt Handarbeit — und weil es Ortskenntnis braucht,
gehört sie dem Museumsteam, nicht dem Rechner:

- **670 Fotos ohne Jahr.** Das ist gewollt: Es sind die historischen Scans, und ihr EXIF-Datum
  ist das des Scanlaufs. Sie sind der Vorrat für „Wann war das?" — aber die Zeitleiste zeigt
  vorerst nur 2010 bis 2024, weil ausschließlich die neuen Kameraaufnahmen datiert sind. Ein
  paar Dutzend datierte Altaufnahmen würden die Leiste erst brauchbar machen.
- **74 Fotos ohne Ort**, davon 7 auch ohne Straße — die vier losen Dateien oben im Import-Ordner
  und die aus `Deelenweg`, wo der Ortsindex zwei Straßen kennt („Deelenweg I" und „II") und
  deshalb bewusst nicht rät.
- **60 Fotos nur straßengenau** (58 vom Kurator, 2 von Besuchern), weil die Hausnummer nicht in
  OpenStreetMap steht. Sie sind zugleich der Vorrat für
  [Punkt 36](#36--hilf-mit-soll-auch-nachschärfen-nicht-nur-füllen), der sie vorlegen will.
- **Schlagwörter aus den Dateien**, die keine sind: „Wer hat eine bessere Vorlage?", „Or01-1",
  „Förderkreis-Cloud". Sie stammen aus der Archivarbeit und stehen jetzt im Kiosk.
- **18 Fotos heißen „Intel(R) JPEG Library, version [1.51.12.44]".** Das ist kein Titel, sondern
  ein EXIF-Feld, das ein Bildprogramm hinterlassen hat — und es steht heute als Überschrift in der
  Detailansicht. Von allen Befunden dieser Liste ist es der einzige, den ein Besucher sofort sieht.

**Alle Zahlen hier sind vom 9. August 2026**, und sie wandern: Jeder Besucherbeitrag verschiebt
sie, und die anderen Punkte dieser Datei tragen den Stand des Tages, an dem sie geschrieben wurden.
Wer eine davon braucht, holt sie sich mit `python -m app.cli stats`, statt sie hier abzulesen — die
Größenordnung stimmt, die letzte Stelle nicht.

Ob dafür ein eigener Arbeitsbereich lohnt oder die vorhandene Nacharbeits-Liste reicht, ist Teil
der Frage. Was davon **ohne Ortskenntnis** zu machen ist — Titel, Zusätze, Archivkürzel —, nimmt
[Punkt 41](#41--den-erstbestand-maschinell-vorbereiten) ab; hier bleibt, was nur das Museumsteam
weiß.

### 25 · Vom Foto direkt in seine Bearbeitung

Wer am Gerät ein falsch beschriftetes Foto sieht, hat heute keinen kurzen Weg dorthin: Verwaltung
öffnen, PIN, Fotoliste, suchen. Und Suchen heißt hier raten — wonach man sucht, ist ausgerechnet
der Titel, der falsch ist.

**Neben dem Titel der Detailansicht steht deshalb ein Stift** (oder der Titel selbst wird die
Fläche, das ist noch offen). Ein Tipp darauf fragt die PIN ab und öffnet danach **dieses** Foto im
Bearbeiten-Bildschirm. Kein Suchen, kein Nachschlagen — und deshalb auch keine Kennung, die sich
jemand aufschreiben müsste.

**Ganz unten, unter dem Bildnachweis, stehen die ersten acht Zeichen des SHA-256**, klein und grau.
Sie sind die Identität des Fotos unabhängig von jeder Datenbank: Ein neu aufgebauter Bestand
vergibt neue laufende Nummern, aber derselbe Scan behält seinen Hash. Damit lässt sich ein Foto
benennen, ohne es zu öffnen.

**Was fehlt, ist der Weg hinein.** Die PIN-Abfrage gibt es (`askPin` in `store/admin.ts`), den
Bearbeiten-Bildschirm auch (`admin/PhotoEditor.tsx`) — aber die Fotoliste öffnet ihn über eigenen
Zustand (`open(id)` in `admin/PhotoCare.tsx:77`). Von außen lässt sich „Verwaltung bei Foto 412
öffnen" nicht sagen. Das ist die eigentliche Arbeit: ein Ziel, das durch `useAdmin` und `AdminApp`
bis in die Fotoliste durchgereicht wird — verwandt mit dem `Target`, über das die Übersicht schon
heute in einen Bereich springt.

**Drei Dinge, die dabei zu bedenken sind:**

- **Es ist eine zweite Tür in die Verwaltung** — und dass sie erlaubt ist, ist entschieden und
  nicht mehr hier zu klären: [decisions.md](decisions.md), Punkt 26. Was dort steht und beim Bauen
  gilt: Sie ist sichtbar und trägt dieselbe PIN; der Punkt 7 von damals hat „sichtbar statt
  versteckt" festgelegt, nicht eine Höchstzahl an Türen.
- **Der Rückweg ist ein Neustart.** Die Verwaltung zu verlassen lädt die Seite neu (`leave()` in
  `store/admin.ts:99`), und das aus gutem Grund: Der Bestand hat sich gerade geändert. Wer einen
  Titel berichtigt und zurückgeht, steht also wieder in der Standardansicht, nicht bei seinem Foto.
- **Findet die Verwaltungssuche den Hash-Anfang?** Wenn nicht, steht in der Detailansicht eine
  Kennung, die sich nirgends nachschlagen lässt. Es wäre eine Zeile mehr im vorhandenen `or_(…)`
  (`api/admin.py:205`) — eine Zugabe, aber sie entscheidet, ob der Hash Auskunft ist oder Zierrat.

**Was von der Volltextsuche übrig bleibt.** Sie stand bis zum 9. August 2026 als eigener Punkt 4
hier, mit der Begründung, die Fotoliste suche „nur über den Titel". Das stimmte nicht: Das `or_(…)`
an derselben Stelle deckt Titel, **Ortsname und Dateiname** ab. Und wer über den Stift direkt vom
Foto in dessen Bearbeitung kommt, sucht überhaupt nicht mehr. Übrig bleibt eine Zeile —
**Beschreibung und Schlagwörter mit durchsuchen**, zwei weitere `ilike` im selben `or_(…)`. Ein
FTS5-Index dafür wäre bei 929 Fotos Aufwand ohne Wirkung; ein `LIKE` über wenige tausend Zeilen ist
in SQLite nicht messbar langsam. Erst bei einem Vielfachen des Bestands lohnt die Frage neu.

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

### 41 · Den Erstbestand maschinell vorbereiten

[Punkt 1](#1--der-erstbestand-braucht-eine-durchsicht) sagt, die Durchsicht brauche Ortskenntnis
und gehöre deshalb dem Museumsteam. Das stimmt für das Datieren und Verorten — **für den
größten Teil der übrigen Arbeit stimmt es nicht.** Titel umzustellen, Zusätze in die Beschreibung
zu heben und Archivkürzel auszusortieren braucht kein Ortswissen, sondern Ausdauer. Genau dafür
lässt sich ein Sprachmodell einspannen — mit Vorlage zur Bestätigung, nicht blind.

**Was der Bestand hergibt, nachgezählt an den 929 Fotos:**

| Befund | Fotos |
|---|---|
| Titel beginnt mit dem `place_name`, wiederholt also die Adresse daneben | **796** |
| davon mit einem Zusatz hinter dem Komma — „Hauptstraße 11a, **Gasthof Timm**" | **632** |
| ohne jede Beschreibung | **720** |
| Titel, die nur die Adresse sind | 163 |
| Titel aus dem EXIF-Schrott: „Intel(R) JPEG Library, version […]" | 18 |
| ohne Bildnachweis | 0 |
| ohne Herkunftsangabe | 3 |

Die Arbeit ist damit erstaunlich gut umrissen: **Der Zusatz hinter dem Komma ist der eigentliche
Titel**, die Adresse davor steht schon im `place_name`. Aus „Hauptstraße 11a, Gasthof Timm"
wird „Gasthof Timm" — und wo der Zusatz eher Anmerkung als Titel ist, gehört er in die
Beschreibung, die bei 720 Fotos leer ist.

**Dazu die Schlagwörter.** „Gebäude" liegt auf allen 929 und trägt damit nichts bei; Straßennamen
verdoppeln den Ort; „Förderkreis-Cloud", „ArchivHolm" und „Or01-1" sind Archivarbeit. Erst danach
wird [Punkt 30](#30--die-karte-nach-schlagwörtern-filtern) überhaupt sinnvoll.

**Und eine Folge, die nicht übersehen werden darf:** [Punkt 27](#27--unter-dem-vorschaubild-adresse-und-jahr)
hat sich für Adresse statt Titel unter dem Vorschaubild entschieden — **weil die Titel heute
Adressen sind**. Sind sie erst aufgeräumt, ist „Gasthof Timm — 1953" die bessere Beschriftung
als „Hauptstraße 11a — 1953". Die Entscheidung von Punkt 27 ist dann neu zu treffen.

**Und die Jahreszahl im Dateinamen gehört hierher.** Sie stand bis zum 9. August 2026 als eigener
Punkt 2 im Backlog, gedacht für den Erstimport — der ist gelaufen, und geraten wurde nichts.
`Kirchweih_1932_Muehle.jpg` trägt seine Datierung im Namen, und bei 673 Fotos ohne Jahr ist jedes
davon einen Blick wert. **Die Warnung von damals gilt unverändert:** `IMG_1932.jpg` ist ein
Kamerazähler, keine Jahreszahl. Ein Fund darf deshalb nur **Vorschlag** sein, nie Tatsache — sonst
entsteht genau der Fehler, den die EXIF-Regel aus Stufe 3 vermeidet: ein falsch datiertes Foto, das
nie zur Korrektur vorgelegt wird, weil es als datiert gilt. In diesem Punkt ist das keine
Zusatzbedingung mehr, sondern schon die Bauform.

**Vorgehen: vorlegen, nicht durchgreifen.** Jede Umstellung geht durch die Nacharbeits-Liste oder
eine eigene Ansicht, in der jemand bestätigt. Ein Sprachmodell, das 929 Titel ohne Rückfrage
umschreibt, macht aus einem sortierten Archiv ein unsortiertes — und die Herkunft der Angaben
(`title_source`) sagt danach nicht mehr die Wahrheit.

### 42 · Dubletten finden, die beste behalten, den Rest zusammenführen

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

### 36 · „Hilf mit" soll auch nachschärfen, nicht nur füllen

Der Beitragsbereich fragt heute nur nach dem, was **fehlt**: `needs_location` heißt schlicht
`lat is None`. Ein Foto, das irgendwo steht — und sei es in der Mitte einer 800-m-Straße —, gilt
als verortet und wird nie wieder vorgelegt. Dabei ist genau das der Fall, in dem jemand, der jeden
Tag daran vorbeigeht, die Hausnummer nennen könnte.

**Erkennen lassen sie sich, und zwar genau** — die Sorge, die Koordinate habe die Spur verwischt,
trifft nicht zu. Neben jedem Punkt steht, wie genau er ist (`location_accuracy_m`):

| Genauigkeit | Quelle | Fotos | was das heißt |
|---|---|---|---|
| 15 m | Kurator | 381 | das Haus |
| **150 m** | Kurator/Besucher | **60** | die Straße — Hausnummer war bekannt, stand aber nicht in OpenStreetMap |
| **leer** | EXIF | **413** | wo die Kamera stand, nicht wo das Haus steht |
| — | — | 75 | ohne Ort, wird heute schon gefragt |

Die 60 sind der klare Fall: `place_name` sagt „Hauptstraße 11a", der Punkt liegt aber auf der
Straßenmitte. **Der Name verspricht eine Genauigkeit, die die Koordinate nicht hat.**

**Der andere Fall aus der Frage entsteht gar nicht.** Ein Ordner ohne Hausnummer lässt das Foto
bewusst **unverortet** — `_locate` in `services/foldermeta.py` begründet es: Die Straßenmitte
„sähe aus wie eine Antwort", und das Foto fiele aus „Wo ist das?" heraus. Die Straße überlebt als
Schlagwort. Diese Fotos stecken also in den 75 und werden längst gefragt.

**Was zu bauen wäre:** eine zweite Art von Frage neben „Wo ist das?" — „Genauer: welche
Hausnummer?", mit der Straße bereits gesetzt, sodass die Auswahl direkt bei den Nummern beginnt.
Auf der Karte ändert sich nichts: Die Fotos stehen schon dort, nur ungenau.

**Die Entscheidung, an der es hängt:** [decisions.md](decisions.md), Punkt 5, erlaubt Besuchern
**nur leere Felder zu füllen** — was schon dasteht, ist unantastbar, sonst überschreibt der zweite
Besucher den ersten. Nachschärfen heißt aber, etwas Vorhandenes zu ersetzen. Nötig wäre eine eng
gefasste Ausnahme: **genauer darf ungenauer ersetzen, nie umgekehrt**, und niemals eine
15-m-Angabe. Das ist zu entscheiden, bevor etwas gebaut wird — die Regel von Punkt 5 ist der
Grund, warum Besucherbeiträge überhaupt ohne Moderation durchgehen dürfen.

**Und die 413 mit EXIF-Koordinate sind eine eigene Frage.** Ihre Genauigkeit ist nicht schlecht,
sondern **unbekannt**: Das Gerät weiß, wo der Fotograf stand — nicht, was er fotografiert hat. Wer
von der anderen Straßenseite knipst, liegt zwanzig Meter daneben. Sie alle vorzulegen wäre viel;
sie nie vorzulegen lässt einen stillen Fehler stehen. Diese Frage gehört getrennt beantwortet.

### 27 · Unter dem Vorschaubild: Adresse und Jahr

Unter jedem Vorschaubild auf der Karte steht heute die fertige Datumsangabe — und die ist an dieser
Stelle zweimal falsch. Für die 256 Kameraaufnahmen steht dort **„22. März 2014"**: Der Tag ist auf
einer Übersichtskarte nie der Punkt. Und unter den 673 Fotos ohne Datierung steht **„Jahr
unbekannt"**, siebenhundertmal dieselbe Zeile.

**Stattdessen: Adresse und Jahr** — „Lehmweg 17b — 1953", und wo kein Jahr bekannt ist, nur
„Im Sande 18".

**Warum die Adresse und nicht der Titel**, obwohl der naheliegender klingt: Der Bestand hat es
entschieden.

| | |
|---|---|
| `place_name` vorhanden | **922 von 929** |
| davon länger als 30 Zeichen | **keine** — die längste ist „Uetersener Straße 12" |
| Titel länger als 40 Zeichen | 105 |
| Titel, die „Intel(R) JPEG Library, version […]" lauten | 18 |

Die Adresse passt also immer unter ein Vorschaubild, der Titel oft nicht. Dass die Position auf der
Karte die Adresse schon ungefähr verrät, spricht nicht dagegen: Auf einer Dorfkarte sieht man die
Straße, nicht die Hausnummer.

**Zwei Dinge fehlen dafür im Datenweg:**

- **`PhotoMarker` trägt keinen `place_name`** (`schemas.py:12`). Sein Docstring begründet die
  schmale Form damit, dass bei mehreren hundert Markern die Antwortgröße zählt — eine kurze
  Zeichenkette je Marker sind bei 500 Markern rund 7 kB, also tragbar, aber die Begründung gehört
  bewusst überschrieben und nicht übersehen.
- **Es braucht eine kurze Datumsform.** `date_label` ist die ausgeschriebene Angabe für die
  Detailansicht; für die Karte wird das Jahr gebraucht („2014"), bei Jahrzehnten weiterhin
  „1930er" und bei Undatiertem gar nichts. Das gehört ins Backend neben `format_label`
  (`services/dates.py:108`), nicht als Zeichenkettenschnipselei ins Frontend.

**Die Beschriftung für Vorlesewerkzeuge behält das volle Datum** (`t.map.markerLabel`) — dort
stört die Genauigkeit nicht, und wer sich die Karte vorlesen lässt, hat den Marker nicht im Blick.

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

Von 308 Schlagwörtern sitzen **260 auf weniger als zehn Fotos**, und „Erntefest" — das Beispiel aus
der Idee — gibt es nicht; es gibt „Fest" und „Feuerwehr". Ein gebauter Filter hätte also zunächst
nichts Sinnvolles anzubieten. **Dieser Punkt hängt an
[Punkt 41](#41--den-erstbestand-maschinell-vorbereiten)**, wo die Schlagwörter aus der Archivarbeit
aussortiert werden — vorher lohnt der Bau nicht.

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

### 35 · Hausnummern auf der Karte

Die Frage war, ob Hausnummern die Orientierung erleichtern. **Die Daten liegen bereit** — der
Ortsindex hält 7323 Adressen mit Koordinaten, es bräuchte also keine neuen Kacheln und keinen
Download, nur eine eigene Ebene. Die Menge spricht trotzdem dagegen, jedenfalls flächendeckend:

| Ausschnitt | Adressen darin |
|---|---|
| Standardansicht, 5 × 3 km | **1223** |
| einmal hineingezoomt, 2 × 1,2 km | 1031 |
| eng, 1 × 0,6 km | 551 |
| ganz nah, 0,5 × 0,3 km | 152 |

Selbst im engsten brauchbaren Ausschnitt stünden **152 Zahlen** auf dem Schirm — neben den
Vorschaubildern, um die es auf dieser Karte eigentlich geht. Als Dauerebene wäre das keine
Orientierung, sondern Rauschen.

**Wo es dagegen Sinn ergibt, ist der Moment, in dem jemand eine Hausnummer sucht.** Steht im
„Hilf mit"-Bereich die Nummernauswahl einer Straße, ließen sich genau **deren** Nummern auf der
Karte zeigen — der Median liegt bei 13 je Straße, 149 der 345 Straßen haben zwischen 5 und 19.
Das ist eine Handvoll Punkte statt einer Wand, und sie beantworten genau die Frage, die gerade
auf dem Schirm steht. Dasselbe gilt für den Fokus nach einem Beitrag, der auf hundert Meter
heranfährt.

Zu bedenken: Die sechs längsten Straßen haben über hundert Adressen — für die bräuchte auch die
gezielte Anzeige eine Grenze, ähnlich wie die Nummernauswahl selbst sie schon kennt.

**Damit ist die Frage beantwortet und der Punkt hängt an
[Punkt 36](#36--hilf-mit-soll-auch-nachschärfen-nicht-nur-füllen).** Er bleibt eine Idee, aber
keine offene mehr: Er ist die Zugabe zur Nummernauswahl, nicht die eigene Kartenebene, nach der
gefragt war. Wer 36 baut — die zweite Frage „Genauer: welche Hausnummer?" —, entscheidet dabei
ohnehin, ob die Nummern dazu auf der Karte stehen. Getrennt gebaut lohnt das nicht.

### 38 · Sprünge beim Gruppieren, und wie genau die Punkte überhaupt liegen

Zwei Fragen an dieselbe Ansicht, beide zu prüfen, bevor daran etwas geändert wird.

**1. Die Marker springen beim Zoomen.** Die Ursache steht in einer Zeile: `draw()` in
`PhotoLayer.tsx` fragt den Index mit `Math.round(map.getZoom())` ab. Der Zoom läuft beim Wischen
stetig, die Gruppierung wechselt aber erst, wenn die gerundete Stufe kippt — und dann alle
Marker auf einmal. Zu prüfen ist, was besser trägt: die gerundete Stufe beibehalten und den
Wechsel **animieren** (die Marker sind DOM-Elemente, ein Ein- und Ausblenden wäre billig), oder
feiner abfragen und dafür häufiger neu zeichnen. Das Zweite kostet auf einem Pi mehr, als es auf
einem Entwicklungsrechner aussieht — der Touch-Test aus
[Punkt 15](#15--abnahme-auf-dem-ersten-pi) misst das.

**2. Wie genau liegen die Punkte, und wie genau sollen sie liegen?** Gemessen am Bestand liegen
854 verortete Fotos auf nur **294 verschiedenen Punkten**:

| Fotos auf einem Punkt | Punkte | Fotos |
|---|---|---|
| einzeln | 160 | 160 |
| 2 bis 4 | 92 | 248 |
| 5 bis 9 | 26 | 162 |
| 10 bis 19 | 11 | 134 |
| **20 und mehr** | **5** | **150** |

Der größte Stapel hat **51 Fotos** auf einer Koordinate (Schulstraße 2). Das ist kein Zufall,
sondern gewollt: Fotos derselben Adresse bekommen dieselbe Koordinate, und `stacks.ts` fasst alles
im Umkreis von etwa einem Meter **vor** dem Gruppieren zu einem Marker zusammen — sonst lägen
einundfünfzig Marker exakt übereinander, von denen nur der oberste erreichbar wäre.

Zu prüfen ist, ob das die richtige Balance ist. Ein Stapel von 51 ist ein Blätterwerk, durch das
niemand blättert. Denkbar wäre, Fotos derselben Adresse **leicht zu streuen**, sobald weit genug
hineingezoomt ist — dann würden aus einem Marker fünfzig, die man einzeln sieht. Dagegen spricht,
dass eine gestreute Position eine Genauigkeit vortäuscht, die es nicht gibt; und
[Punkt 36](#36--hilf-mit-soll-auch-nachschärfen-nicht-nur-füllen) will diese Ungenauigkeit gerade
sichtbar halten, um sie beheben zu lassen. Erst prüfen, dann entscheiden.

### 40 · Ein Durchgang über die ganze Oberfläche

Die Ansicht ist über zehn Stufen gewachsen, und jede Stufe hat für sich gestimmt. Was fehlt, ist
der Blick auf das Ganze: Rückmeldungen einholen, auf Einheitlichkeit prüfen, sammeln, was auffällt,
und es dann in einem Zug umsetzen statt in zwölf Einzelentscheidungen.

**Drei Befunde stehen schon als eigene Punkte** und sind damit die erste Ernte dieses Durchgangs,
nicht sein Ersatz:
[Punkt 10](#10--detailansicht-maße-aufräumen) (Maße der Detailansicht),
[Punkt 28](#28--die-knopfsprache-der-besucheransicht) (fünf Knopfformen, und die leiseste trägt
die folgenreichste Handlung) und
[Punkt 29](#29--der-kopfbereich-maße-wappen-titel) (drei Elemente, fast fünfzig Pixel Höhenspanne).

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
Zielkonflikt steht in [Punkt 29](#29--der-kopfbereich-maße-wappen-titel) beim Wappen, das neu
laden soll.

### 10 · Detailansicht: Maße aufräumen

Zwei Kleinigkeiten an derselben Ansicht — die zweite zieht allerdings deutlich mehr nach sich als
die erste.

**1. Die Textspalte drängt das Bild auf schmalen Schirmen zu klein.** `--overlay-aside` ist fest
auf 24 rem gesetzt, bei 18 px Wurzelschrift also 432 px. Zusammen mit Rand und Abstand
(90 + 36 px) bleiben dem Bild auf 1280 px Breite 722 px, auf **1024 px nur noch 466 px** — bei
einem querformatigen Scan gut ein Drittel des Schirms. Der `minmax(16rem, …)` in
`grid-template-columns` federt das nicht ab: Er gibt nur eine Untergrenze an, die Spalte bleibt bei
ihrer Wunschbreite, solange sie passt.

Das ist der Grund, warum dieser Punkt als Fehler geführt wird und nicht als Ausbau: Eine Ansicht,
die bei kleinerer Auflösung ihr Hauptobjekt zerdrückt, tut nicht, was sie zusagt.

**Zwei Wege, und der zweite geht an die Ursache:**

1. **Die Spalte mitwachsen lassen** statt sie zu setzen — `clamp(16rem, 28vw, 24rem)`. Billig, aber
   nur eine Milderung: Auch eine schmalere Seitenspalte nimmt dem querformatigen Bild Breite. Zu
   klären wäre, ob der Text dann noch ohne unruhige Umbrüche steht.
2. **Das Layout dem Bild folgen lassen.** Ein Querformat braucht Breite und hat Höhe übrig — der
   Text gehört **darunter**. Ein Hochformat braucht Höhe und hat Breite übrig — dort ist der Text
   **daneben** richtig, so wie heute. Die Ansicht weiß, was sie zeigt: Das Bild trägt sein
   Seitenverhältnis schon als `aspect-ratio` (`PhotoOverlay.tsx`), und `.overlay__content` ist ein
   Raster mit zwei Spalten, das sich auf eine umstellen ließe.

**Der Bestand sagt, welcher Fall zählt: 884 Querformate gegen 44 Hochformate.** Der Weg über die
Ausrichtung hilft also fast immer und kostet in den 44 Fällen nichts — die Spalte bleibt dort, wo
sie heute steht.

**Wie dringend das ist, hängt an
[Punkt 19](#19--displayauflösung-und--orientierung-des-museumsgeräts)**, und zwar in beide
Richtungen: Auf 1920 × 1080 ist nichts zu tun, auf einem 1024er Panel schon — und steht das Gerät
am Ende **hochkant**, dreht sich die Rechnung ganz um. Solange die Auflösung nicht feststeht, ist
jede Zahl hier eine Annahme.

**2. Der Schließen-Knopf soll ganz oben rechts stehen, nicht am rechten Rand des Inhalts.** Heute
sitzt er bündig mit der rechten Kante der Textspalte. Bei einem breiten Foto ist das dasselbe wie
„oben rechts im Schirm"; bei einem schmalen rückt der ganze Inhalt zusammen und der Knopf mit ihm
nach innen. Er soll stattdessen **immer** in der Ecke stehen, mit einem vernünftigen Abstand zum
Rand.

**Der zweite Teil wartet auf [Punkt 28](#28--die-knopfsprache-der-besucheransicht)**, und deshalb
ist er nicht längst erledigt: Der Schließen-Knopf ist heute absichtlich so hoch wie die
Blätterknöpfe (3,5 rem), damit die Ansicht genau eine Knopfform kennt. Löst man ihn aus dem Raster,
ist diese Bindung weg — dann sollte vorher feststehen, welche Größen es überhaupt geben soll.

### 28 · Die Knopfsprache der Besucheransicht

Der „Hilf mit"-Bereich ist über mehrere Stufen gewachsen, und man sieht es. **Jede Handlung soll
ein Knopf sein und wie einer aussehen** — heute gibt es fünf Formen, und die wichtigste Grenze
verläuft an der falschen Stelle:

| Handlung | Form heute |
|---|---|
| Buchstabe, Straße, Jahrzehnt, Jahr, Hausnummer, Abschnitt | Raster- bzw. Listenknopf, weiß mit Rand, 3 rem |
| „Hier war das", „Ganze 1920er Jahre" | gefüllt, braun, 1,1 rem Schrift |
| „Reicht so — die Straße genügt" | weiß mit Rand, volle Breite |
| „Anderer Buchstabe", „Anderes Jahrzehnt", „Doch nicht — von vorn", „Punkt entfernen" | **randlos, grau, 2,75 rem** |
| „Weiß ich nicht — nächstes Foto" | dieselbe randlose Form |

**Zwei Dinge stimmen daran nicht.** Die randlose Form (`.button--quiet`) sieht nicht nach Knopf
aus, sondern nach Text — für die Zielgruppe genau das Falsche. Und sie wirft zwei verschiedene
Dinge zusammen: **zurückgehen** („Anderer Buchstabe", „Doch nicht") und **überspringen** („Weiß ich
nicht — nächstes Foto"). Das eine bleibt beim Foto, das andere legt es weg; sie sollten nicht
gleich aussehen.

Dazu kommt das Maß: `.button--quiet` ist 2,75 rem hoch, bei 18 px Wurzelschrift also 49,5 px. Die
48 px aus der Zielgruppen-Regel sind damit eingehalten — aber knapp, und an jeder Stelle einzeln
statt an einer.

**Zu klären: Symbole wie und wo.** Für Übernehmen, Zurück, Abbrechen und Nächstes Foto liegen sie
nahe. Bei der Zielgruppe ist ein Symbol **neben** der Beschriftung der sichere Weg; ein Symbol
**statt** der Beschriftung spart Platz und verlangt Vorwissen, das ältere Besucher nicht
mitbringen müssen. Und Symbole müssen mitgeliefert werden — kein CDN, keine Icon-Schriftart aus
dem Netz; entweder als Inline-SVG im Quelltext oder gar nicht.

**Was daran hängt:** [Punkt 10](#10--detailansicht-maße-aufräumen) wartet darauf. Der
Schließen-Knopf der Detailansicht ist an die Blätterknöpfe gebunden, damit die Ansicht eine
Knopfform kennt; erst wenn feststeht, welche Größen es gibt, kann er aus dem Raster. **Der
Verwaltungsbereich bleibt ausdrücklich außen vor** — er hat eigene Maße, wird ein- bis zweimal im
Jahr benutzt und folgt einer anderen Regel: Dort zählt Klartext mehr als Kompaktheit.

### 29 · Der Kopfbereich: Maße, Wappen, Titel

Die obere Zeile trägt drei Dinge nebeneinander — Wappen, Titel und Zeitschieber —, und sie sind
weder gleich hoch noch gleich gemeint. Vier Änderungen, die zusammengehören, weil sie dieselbe
Fläche betreffen.

**1. Die drei stehen oben bündig und enden weit auseinander.** Nachgemessen bei 18 px
Wurzelschrift:

| | Oberkante | Unterkante | Höhe |
|---|---|---|---|
| Titelblock | 13,5 px | 85,0 px | 71,5 px |
| Wappen | 13,5 px | **98,0 px** | 84,5 px |
| Zeitschieber, erste Zeile bis Jahresskala | 13,5 px | **133,6 px** | 120,1 px |

**Die Zahlen sind vom 9. August 2026 vormittags und schon überholt:** Seit dem Schalter „507 Fotos
ohne Jahr anzeigen" ([decisions.md](decisions.md), Punkt 28) trägt die Kopfzeile des Schiebers einen
50 px hohen Knopf statt eines Wortes und ist entsprechend gewachsen. Die Größenordnung des
Problems ändert das nicht — sie vergrößert es. **Nachmessen gehört zum ersten Schritt dieses
Punktes**, nicht das Übernehmen der Tabelle.

Fast fünfzig Pixel Unterschied an den Unterkanten. Das CSS behauptet an dieser Stelle das
Gegenteil: Ein Kommentar bei `.app__heading-lead` rechnet vor, dass beide Titelzeilen zusammen
genau `--crest` ergeben und „damit genau so hoch wie der Schieber nebenan" stehen. Das galt einmal
für den breiten Schirm; `--crest` schrumpft auf schmalen Schirmen per Media Query, der Schieber
nicht, und seine Bahn ist am 9. August von 3 auf 3,5 rem gewachsen. **Gewollt ist stattdessen:
vertikal mittig im Höhenbereich des höchsten beteiligten Elements** — dann trägt die Aussage sich
selbst, statt von drei Rechnungen abzuhängen, die auseinanderlaufen können.

**2. Der Griff in der Mitte des Zeitschiebers**, die zwei Striche, kommt vorerst weg oder wird
durch ein schlichtes Auge-Symbol ersetzt. **Zu bedenken:** Der Griff ist heute das, was übrig
bleibt, wenn der Zeitraum auf einen einzigen Balken zusammengeschoben ist — dann hat der Bereich
keine Fläche mehr zum Anfassen. Fällt der Griff ersatzlos weg, braucht dieser Fall eine andere
Antwort, etwa eine Mindestbreite des Bereichs.

**3. Das Wappen lädt neu und setzt die Filter zurück.** Damit ist die alte Frage nach einem
Reload-Knopf beantwortet — sie stand bis heute als eigener Punkt 11 hier:

> Auf dem Besucherschirm gibt es keinen Weg, die Anzeige zurückzusetzen. Es gibt drei Umwege: fünf
> Minuten warten, die PIN eingeben und die Verwaltung wieder verlassen, oder den Netzstecker. Für
> einen Besucher, der sich verhakt hat, ist keiner davon eine Antwort.

Der Einwand von damals gilt weiter und gehört beim Bauen bedacht: **Ein Knopf, den fast niemand
braucht, wird trotzdem gedrückt — von Kindern zuerst**, und er wirft die Arbeit weg, die gerade
jemand angefangen hat. Ein halb gesetzter Punkt, ein gewähltes Jahrzehnt, ein offener Stapel: alles
fort. Das Wappen kostet immerhin keine zusätzliche Fläche, und die Bauform ist keine unsichtbare
Geste — die wurde in Stufe 8 aus gutem Grund verworfen (siehe [history.md](history.md)).

**4. Der Titel „Bilder aus Holm" führt in die Verwaltung**, weiterhin über die PIN und **ohne
Unterstreichung**. Das tauscht die Rollen: Bisher war das Wappen die Tür. Zusammen mit dem Stift
aus [Punkt 25](#25--vom-foto-direkt-in-seine-bearbeitung) gibt es danach zwei Türen, und keine
davon ist mehr das Wappen — **entschieden ist das bereits**, in [decisions.md](decisions.md),
Punkt 26, an einer Stelle statt zweimal nebenbei. Hier bleibt die Arbeit.

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
gelaufen ist nichts. Betroffen sind `setup-pi.sh`, `photomap-kiosk`, `photomap-kiosk.service`,
`update.sh`, `99-photomap-usb.rules` und `photomap-usb-mount`.

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

### 17 · Containerbetrieb prüfen

`make prod` ist ungeprüft, weil beim Bauen kein Docker lief. Auf dem Pi ist das der einzige
Betriebsmodus — und für
[Punkt 21](#21--deployment-auf-einem-webserver-evaluieren) ist es der Weg, auf dem das System
überhaupt irgendwo hinkommt.

### 18 · Wiederherstellung wirklich proben

Auf ein zweites, leeres Gerät zurückspielen. **Ein ungetestetes Backup ist kein Backup.** Erprobt
ist bisher nur der Weg gegen ein `hdiutil`-Prüfvolumen auf dem Mac.

### 19 · Displayauflösung und -orientierung des Museumsgeräts

Steht noch nicht fest und beeinflusst die Layoutmaße. Die Ansicht ist bisher gegen 1280 × 800
nachgemessen; die Variable `--crest` hat für schmale Schirme bereits eine Media Query.

**Zwei Punkte warten auf diese Antwort**, und beide werden von ihr nicht nur abgestuft, sondern
umgestellt:

- [Punkt 10](#10--detailansicht-maße-aufräumen), die Maße der Detailansicht. Auf 1920 × 1080 ist
  nichts zu tun, auf einem 1024er Panel viel — und steht das Gerät **hochkant**, dreht sich die
  Rechnung um: Dann hat das querformatige Bild Breite im Überfluss und der Text darunter Platz.
- [Punkt 29](#29--der-kopfbereich-maße-wappen-titel), der Kopfbereich. Auf schmalen Schirmen
  schrumpft `--crest`, der Zeitschieber nicht — die Höhen laufen dort schon heute auseinander.

**Die Frage ist also kleiner, als sie aussieht, und sollte früh gestellt werden**: Es ist eine
Frage an das Museum, keine an den Code, und sie kostet nichts als ein Telefonat.

### 20 · Read-Only-Overlay-Dateisystem

Gegen SD-Karten-Korruption bei Stromausfall. Der Pi wird im Museum nicht heruntergefahren, sondern
ausgeschaltet — das ist auf Dauer der wahrscheinlichste Ausfallgrund.

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

Technisch ist der Weg kurz: Es läuft schon in Containern (`make prod`), das Frontend ist statisch,
nginx steht davor, und die Datenbank ist eine Datei. Die Fragen liegen woanders:

- **Zugriffsschutz.** Die PIN ist für einen Touchscreen in einem Museumsraum gebaut — vier Ziffern,
  gesichert durch eine Sperre nach fünf Fehlversuchen. Im offenen Netz ist das zu wenig, und vor
  allem schützt sie nur die Verwaltung: Der „Hilf mit"-Bereich nimmt **Beiträge ohne jede
  Anmeldung** an. Online wäre das eine offene Tür. Naheliegend ist ein Schutz **vor** der ganzen
  Anwendung (HTTP-Basisauthentifizierung im nginx oder ein Zugang über VPN), nicht ein zweiter
  Schutz in der Anwendung.
- **Was aus dem Offline-Versprechen wird.** Die Regel „null Anfragen an eine fremde Herkunft" bleibt
  erfüllt, sie kostet online nur nichts mehr. Umgekehrt gilt: Kartendatei und Ortsindex sind auf
  einen Rechner im Ausstellungsraum zugeschnitten — 4,6 MB Kacheln und 1,5 MB Ortsindex über eine
  langsame Leitung sind spürbar, aber tragbar.
- **Wie die Daten zurück auf den Pi kommen.** Das ist der eigentliche Zweck, und dafür gibt es das
  Werkzeug bereits: Sicherung und Wiederherstellung. Zu prüfen ist, ob der Weg auch als
  Übertragungsweg taugt — dann wäre der Umzug vom Webserver ins Museum ein bekannter Vorgang und
  kein Sonderfall.

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

### 37 · Die Straßenauswahl in der Adaptionsanleitung erklären

[adaption.md](adaption.md) sagt einem zweiten Museum, was es anfassen muss. Die Straßenauswahl im
„Hilf mit"-Bereich — seit dem 8. August der Hauptweg zur Verortung — kommt dort bisher nur als
eine Zeile zu `streetChoice` vor. Das reicht nicht: Wer die Software für seinen Ort aufsetzt, muss
wissen, **wie er prüft, dass der Baum trägt**, und was er tut, wenn er es nicht tut.

Hineingehört:

- **Woher die Straßen kommen** — `make places` holt sie über Overpass aus OpenStreetMap in den
  Ortsindex; ohne diesen Schritt bleibt der Bereich leer und sagt das auch (`t.location.noStreets`).
- **Wie `streetChoice` zu wählen ist.** Der Wert entscheidet, wie viele Fragen bis zur Straße
  nötig sind. In Holm ergeben 80 Straßen zehn Buchstabengruppen, sieben davon führen direkt zur
  Liste. Ein dichter bebauter Ort braucht einen kleineren Wert, ein weitläufiger verträgt einen
  größeren — **die Zahl ist zu prüfen, nicht zu übernehmen.**
- **Wie man das nachsieht, ohne zu raten**: `GET /api/places/streets` liefert genau die Liste, die
  der Baum bekommt. Wer sie sich ansieht, weiß vor dem ersten Besucher, ob der Ortskern
  vollständig drin ist und wie viele Fremdorte mitkommen.
- **Was schiefgehen kann.** Der Ortsindex reicht so weit wie die `bbox`; bei einem knapp gesetzten
  Ausschnitt fehlen Randstraßen, bei einem weiten kommen Nachbardörfer mit und verdrängen die
  eigenen aus den nächsten `streetChoice`.

Das ist die Sorte Wissen, die genau einmal erarbeitet wurde und beim zweiten Museum sonst noch
einmal erarbeitet werden müsste — siehe [decisions.md](decisions.md), Punkt 24.

### 22 · Versionierung, Releaseprozess und Veröffentlichung des Codes

**Stand:** `development.md` kündigt SemVer-Tags und Conventional Commits an, beides zusammen
versioniert. Tatsächlich gibt es nach 99 Commits **keinen einzigen Tag**; `package.json` und
`pyproject.toml` stehen beide auf `0.1.0`, und `deploy/docker-compose.yml` baut Images mit
`${PHOTOMAP_VERSION:-dev}`. Es fehlt also nicht die Entscheidung, sondern ihre Umsetzung: Was löst
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

- **Unter welcher Lizenz steht Photomap selbst?** Für ein Projekt, das ausdrücklich für ein zweites
  Museum nachnutzbar sein soll, ist das keine Formalie — ohne Lizenz ist Nachnutzung rechtlich
  nicht erlaubt, auch wenn der Code offen daliegt.
- **Was verlangen die verwendeten Komponenten?** Bisher steht im README nur der Satz „Alle
  verwendeten Komponenten sind Open Source" — das ist geglaubt, nicht geprüft. Nachzusehen sind
  mindestens MapLibre GL (BSD-3), PMTiles, `@protomaps/basemaps` samt der mitgelieferten
  **Schriften und Symbole** unter `frontend/public/basemaps/`, die OpenStreetMap-Daten in Kacheln
  und Ortsindex (ODbL — verlangt Namensnennung, die auf der Karte steht) und die
  Python-Abhängigkeiten. Die Kombination entscheidet, welche Lizenz für Photomap überhaupt möglich
  ist.

Gehört anschließend in eine `LICENSE`-Datei und in den Lizenzabschnitt des README.
