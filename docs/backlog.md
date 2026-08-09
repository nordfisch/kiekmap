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
| 25 | [Vom Foto direkt in seine Bearbeitung](#25--vom-foto-direkt-in-seine-bearbeitung) | Aufgabe | wichtig |
| 2 | [Jahreszahl aus dem Dateinamen raten](#2--jahreszahl-aus-dem-dateinamen-raten) | Idee | — |
| 3 | [Perceptual Hash gegen zugeschnittene Dubletten](#3--perceptual-hash-gegen-zugeschnittene-dubletten) | Idee | — |
| 4 | [Volltextsuche über SQLite FTS5](#4--volltextsuche-über-sqlite-fts5) | Idee | — |
| | **Besucher-Interface** | | |
| 26 | [Der Punkt auf der Karte erst nach Ansage](#26--der-punkt-auf-der-karte-erst-nach-ansage) | Aufgabe | wichtig |
| 8 | [Historische Karte als umschaltbare Grundkarte](#8--historische-karte-als-umschaltbare-grundkarte) | Idee | wichtig |
| 9 | [Attract-Mode](#9--attract-mode) | Idee | wichtig |
| 10 | [Detailansicht: Maße aufräumen](#10--detailansicht-maße-aufräumen) | **Fehler** | — |
| 11 | [Braucht der Kiosk einen eigenen Reload-Knopf?](#11--braucht-der-kiosk-einen-eigenen-reload-knopf) | Frage | — |
| 12 | [Der 100-m-Fokus liegt über der Kachelauflösung](#12--der-100-m-fokus-liegt-über-der-kachelauflösung) | Frage | — |
| 13 | [„Hilf mit:" hat seine Akzentfarbe verloren](#13--hilf-mit-hat-seine-akzentfarbe-verloren) | Idee | — |
| | **Infrastruktur** | | |
| 14 | [Bedienbarkeitstest mit der echten Zielgruppe](#14--bedienbarkeitstest-mit-der-echten-zielgruppe) | Aufgabe | wichtig · dringend |
| 15 | [Abnahme auf dem ersten Pi](#15--abnahme-auf-dem-ersten-pi) | Aufgabe | wichtig |
| 16 | [Die vier Prüfungen, die das Gerät brauchen](#16--die-vier-prüfungen-die-das-gerät-brauchen) | Aufgabe | wichtig |
| 17 | [Containerbetrieb prüfen](#17--containerbetrieb-prüfen) | Aufgabe | wichtig |
| 18 | [Wiederherstellung wirklich proben](#18--wiederherstellung-wirklich-proben) | Aufgabe | wichtig |
| 19 | [Displayauflösung und -orientierung des Museumsgeräts](#19--displayauflösung-und--orientierung-des-museumsgeräts) | Frage | wichtig |
| 20 | [Read-Only-Overlay-Dateisystem](#20--read-only-overlay-dateisystem) | Idee | — |
| 24 | [Eine Tastatur für die Pflege am Gerät](#24--eine-tastatur-für-die-pflege-am-gerät) | Frage | wichtig |
| | **Entwicklung** | | |
| 21 | [Deployment auf einem Webserver evaluieren](#21--deployment-auf-einem-webserver-evaluieren) | Frage | wichtig · dringend |
| 22 | [Versionierung, Releaseprozess und Veröffentlichung des Codes](#22--versionierung-releaseprozess-und-veröffentlichung-des-codes) | Frage | wichtig |
| 23 | [Lizenz des Projekts und der verwendeten Komponenten](#23--lizenz-des-projekts-und-der-verwendeten-komponenten) | Frage | wichtig |

**Ein Fehler ist offen**: Punkt 10 zerdrückt das Foto auf einem kleinen Schirm. Beide Fehler, die
diese Datei kennt, sind erst durch die Einordnung als solche benannt worden — vorher galt sie als
fehlerfrei. Der andere, **Punkt 5**, ist am 8. August 2026 behoben und in die
[history.md](history.md) gezogen; seine Nummer bleibt vergriffen.

---

## Verwaltung

### 1 · Der Erstbestand braucht eine Durchsicht

929 Fotos sind eingelesen, und der Import hat aus Dateien und Ordnernamen herausgeholt, was
darin stand. Was er *nicht* konnte, ist jetzt Handarbeit — und weil es Ortskenntnis braucht,
gehört sie dem Museumsteam, nicht dem Rechner:

- **673 Fotos ohne Jahr.** Das ist gewollt: Es sind die historischen Scans, und ihr EXIF-Datum
  ist das des Scanlaufs. Sie sind der Vorrat für „Wann war das?" — aber die Zeitleiste zeigt
  vorerst nur 2010 bis 2024, weil ausschließlich die neuen Kameraaufnahmen datiert sind. Ein
  paar Dutzend datierte Altaufnahmen würden die Leiste erst brauchbar machen.
- **77 Fotos ohne Ort**, davon 7 auch ohne Straße — die vier losen Dateien oben im Import-Ordner
  und die aus `Deelenweg`, wo der Ortsindex zwei Straßen kennt („Deelenweg I" und „II") und
  deshalb bewusst nicht rät.
- **58 Fotos nur straßengenau**, weil die Hausnummer nicht in OpenStreetMap steht.
- **Schlagwörter aus den Dateien**, die keine sind: „Wer hat eine bessere Vorlage?", „Or01-1",
  „Förderkreis-Cloud". Sie stammen aus der Archivarbeit und stehen jetzt im Kiosk.

Ob dafür ein eigener Arbeitsbereich lohnt oder die vorhandene Nacharbeits-Liste reicht, ist Teil
der Frage.

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

- **Es ist eine zweite Tür in die Verwaltung.** [decisions.md](decisions.md), Punkt 7, hat bewusst
  genau eine festgelegt — das Wappen —, und in Stufe 8 wurde eine unsichtbare Geste dafür
  verworfen. Diese Tür ist sichtbar und durch dieselbe PIN gesichert, widerspricht dem also nicht;
  aber sie ändert die Entscheidung, und das gehört dort vermerkt.
- **Der Rückweg ist ein Neustart.** Die Verwaltung zu verlassen lädt die Seite neu (`leave()` in
  `store/admin.ts:99`), und das aus gutem Grund: Der Bestand hat sich gerade geändert. Wer einen
  Titel berichtigt und zurückgeht, steht also wieder in der Standardansicht, nicht bei seinem Foto.
- **Findet die Verwaltungssuche den Hash-Anfang?** Wenn nicht, steht in der Detailansicht eine
  Kennung, die sich nirgends nachschlagen lässt. Es wäre eine Zeile mehr im vorhandenen `or_(…)`
  (`api/admin.py:205`) — eine Zugabe, aber sie entscheidet, ob der Hash Auskunft ist oder Zierrat.

### 2 · Jahreszahl aus dem Dateinamen raten

`Kirchweih_1932_Muehle.jpg` trägt seine Datierung im Namen, und beim Erstimport von einigen
hundert Scans ist das viel wert.

**Vorsicht:** `IMG_1932.jpg` ist ein Kamerazähler, keine Jahreszahl. Das Ergebnis darf deshalb nur
als **Vorschlag** markiert werden, nie als Tatsache — sonst entsteht genau der Fehler, den die
EXIF-Regel aus Stufe 3 vermeidet: ein falsch datiertes Foto, das nie zur Korrektur vorgelegt wird,
weil es als datiert gilt.

### 3 · Perceptual Hash gegen zugeschnittene Dubletten

Der SHA-256 erkennt nur bitgleiche Dateien. Zwei Scans desselben Fotos mit unterschiedlichem
Zuschnitt oder Kontrast sind für ihn zwei verschiedene Bilder — im Museumsbestand ein realistischer
Fall, wenn dasselbe Original zweimal durch den Scanner ging.

### 4 · Volltextsuche über SQLite FTS5

Über Titel, Beschreibung und Schlagwörter. Heute sucht die Fotoliste im Verwaltungsbereich nur über
den Titel.

---

## Besucher-Interface

### 26 · Der Punkt auf der Karte erst nach Ansage

Solange die Frage „Wo ist das?" steht, ist **die ganze Karte scharf**: Jeder Tipp auf eine freie
Fläche setzt einen Punkt (`PinLayer.tsx:28`). Wer während der Frage nur schauen will — die Karte
verschieben, sich orientieren, ein Foto in der Nähe suchen — beantwortet sie dabei versehentlich.

Das ist mehr als unsauber, es geht an die Datenqualität: Sobald ein Punkt steht, wechselt der
Beitragsbereich auf „Stimmt die Stelle?" und bietet **„Hier war das"** an. Ein Tipp daneben und ein
bestätigender Tipp danach — und im Bestand steht eine Verortung, die niemand gemeint hat.

**Der Kartentipp soll deshalb erst nach ausdrücklicher Ansage scharf sein**, über einen Knopf im
Beitragsbereich: „Auf der Karte zeigen" oder ein Fadenkreuz. Das passt zu dem, was seit dem
8. August ohnehin der Hauptweg ist — die Straße wird über Knöpfe gewählt (Punkt 6, erledigt). Der
Kartentipp ist der zweite Weg für den, der die Stelle kennt, aber den Straßennamen nicht; ihn eine
Ansage kosten zu lassen, ist bei einem Weg für den Ausnahmefall vertretbar.

**Die Falle steckt im `active`-Schalter.** Er hängt heute an drei Dingen zugleich: ob der
Kartentipp einen Punkt setzt, ob der Punkt überhaupt gezeichnet wird, und ob er sich ziehen lässt
(`PinLayer.tsx:19, 42, 57`). Wer nur das Erste abschalten will und das Ganze abschaltet, nimmt
damit auch den Punkt weg, den die **Straßenwahl** gesetzt hat — und die Zusage „Der Punkt lässt
sich auf der Karte noch verschieben" (`t.location.hintSet`) gilt nicht mehr. Zu trennen sind also
**Scharfschaltung** und **Anzeige samt Ziehen**.

Dazu gehört, dass der Zustand beim Wechsel des Fotos zurückfällt — `load()` in
`store/contribute.ts` setzt Punkt, Etikett und Genauigkeit schon heute zurück, dort gehört er hin.
Und `t.location.hintEmpty` sagt derzeit „Tippen Sie auf der Karte auf die Stelle — oder wählen Sie
die Straße."; das stimmt danach nicht mehr.

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

### 9 · Attract-Mode

Diashow bei Leerlauf statt Standardansicht. Heute lädt der Leerlauf nach fünf Minuten die Seite
neu — ein bewegtes Bild würde Besucher eher an das Gerät holen.

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
die bei kleinerer Auflösung ihr Hauptobjekt zerdrückt, tut nicht, was sie zusagt. **Wie schlimm es
ist, hängt an [Punkt 19](#19--displayauflösung-und--orientierung-des-museumsgeräts)** — auf
1920 × 1080 ist nichts zu tun, auf einem 1024er Panel schon. Naheliegend wäre, die Spalte
mitwachsen zu lassen (`clamp(16rem, 28vw, 24rem)`) statt sie zu setzen. Zu klären ist vorher, ob
der Text dann noch ohne unruhige Umbrüche steht.

**2. Der Schließen-Knopf soll ganz oben rechts stehen, nicht am rechten Rand des Inhalts.** Heute
sitzt er bündig mit der rechten Kante der Textspalte. Bei einem breiten Foto ist das dasselbe wie
„oben rechts im Schirm"; bei einem schmalen rückt der ganze Inhalt zusammen und der Knopf mit ihm
nach innen. Er soll stattdessen **immer** in der Ecke stehen, mit einem vernünftigen Abstand zum
Rand.

**Das wird zusammen mit einer Vereinheitlichung der Schaltflächen- und Eingabefeldgrößen gemacht**,
und deshalb steht es hier und ist nicht schon erledigt: Der Knopf ist heute absichtlich so hoch wie
die Blätterknöpfe (3,5 rem), damit die Ansicht genau eine Knopfform kennt. Löst man ihn aus dem
Raster, ist diese Bindung weg — dann sollte vorher feststehen, welche Größen es überhaupt geben
soll. Betroffen sind beide Bereiche: Besucheransicht und Verwaltung haben eigene Maße für Knöpfe,
Eingabefelder und deren Mindesthöhe, und die 48 px aus der Zielgruppen-Regel sind bisher an jeder
Stelle einzeln eingehalten statt an einer.

### 11 · Braucht der Kiosk einen eigenen Reload-Knopf?

Auf dem Besucherschirm gibt es heute keinen Weg, die Anzeige zurückzusetzen. Es gibt drei
Umwege: fünf Minuten warten (der Leerlauf lädt neu), die PIN eingeben und die Verwaltung wieder
verlassen (lädt seit `1e99559` ebenfalls neu), oder den Netzstecker.

Für einen Besucher, der sich verhakt hat, sind alle drei keine Antwort. Für eine ehrenamtliche
Person, die danebensteht, reicht der Weg über die Verwaltung — aber nur, wenn sie die PIN weiß.

**Was dagegen spricht**, und deshalb ist es eine Frage und keine Aufgabe: Ein Knopf im
Besucherbild, den fast niemand braucht, wird trotzdem gedrückt — von Kindern zuerst. Er nimmt
Fläche, und er wirft die Arbeit weg, die gerade jemand angefangen hat. Die Ansicht kann sich
ausserdem kaum noch verhaken: Der Leerlauf lädt neu statt zurückzusetzen, seit `8c1f880`.

**Der naheliegende Mittelweg wäre eine unauffällige Geste** — ein langer Druck auf das Wappen etwa.
Genau diese Bauform wurde in Stufe 8 für den Verwaltungszugang **verworfen**, weil eine unsichtbare
Geste etwas ist, das Ehrenamtliche sich merken müssten (siehe [history.md](history.md), Stufe 8).
Wer sie hier wieder aufgreift, sollte das wissen und begründen.

### 12 · Der 100-m-Fokus liegt über der Kachelauflösung

Nach einem Besucherbeitrag fährt die Karte auf hundert Meter heran; die Vektorkacheln reichen bis
Zoom 15. MapLibre skaliert sauber hoch, die Beschriftungen werden dabei aber groß. Falls das im
Museum unruhig wirkt, ist **der Radius die Stellschraube, nicht die Bauform** — zu beurteilen ist
das erst am Gerät, also mit [Punkt 15](#15--abnahme-auf-dem-ersten-pi).

### 13 · „Hilf mit:" hat seine Akzentfarbe verloren

Beim Angleichen an „Bilder aus" (`45ae42d`) wurde aus dem Akzentbraun eine stille graue Zeile. Das
war die bewusste Folge einer bewussten Entscheidung — aber es war zugleich der einzige Blickfang
der linken Spalte. Falls der Beitragsbereich seinen Zug aufs Auge zurückbekommen soll, ist das die
Stelle.

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

### 16 · Die vier Prüfungen, die das Gerät brauchen

Der praktische Teil von [Punkt 15](#15--abnahme-auf-dem-ersten-pi), und ohne Gerät nicht zu haben:

- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Gezogener Netzstecker im Betrieb** — hier zeigt sich, ob
  `--disable-session-crashed-bubble` das tut, wofür es gedacht ist.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen. Kioske
  sterben an einem langsamen Leck im Frontend, nicht am Backend.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.

### 17 · Containerbetrieb prüfen

`make prod` ist ungeprüft, weil beim Bauen kein Docker lief. Auf dem Pi ist das der einzige
Betriebsmodus — und für
[Punkt 21](#21--deployment-auf-einem-webserver-evaluieren) ist es der Weg, auf dem das System
überhaupt irgendwo hinkommt.

### 18 · Wiederherstellung wirklich proben

Auf ein zweites, leeres Gerät zurückspielen. **Ein ungetestetes Backup ist kein Backup.** Erprobt
ist bisher nur der Weg gegen ein `hdiutil`-Prüfvolumen auf dem Mac.

### 19 · Displayauflösung und -orientierung des Museumsgeräts

Steht noch nicht fest und beeinflusst die Layoutmaße; an dieser Antwort hängt
[Punkt 10](#10--detailansicht-maße-aufräumen). Die Ansicht ist bisher gegen 1280 × 800
nachgemessen; die Variable `--crest` hat für schmale Schirme bereits eine Media Query.

### 20 · Read-Only-Overlay-Dateisystem

Gegen SD-Karten-Korruption bei Stromausfall. Der Pi wird im Museum nicht heruntergefahren, sondern
ausgeschaltet — das ist auf Dauer der wahrscheinlichste Ausfallgrund.

### 24 · Eine Tastatur für die Pflege am Gerät

Der Rest der Tastaturfrage aus Punkt 6, und der bleibt: **Der Verwaltungsbereich hat 13
Eingabefelder in sieben Dateien** — Titel, Beschreibung, Schlagwörter, Suche, Jahr, Ortssuche. Die
sind ohne Tastatur nicht zu bedienen, und daran soll sich nichts ändern: Wer Fotos pflegt, tippt,
und die PIN auf dem Zahlenfeld hilft dabei nicht.

Die Besucheransicht braucht seit dem 8. August 2026 keine mehr (siehe [history.md](history.md)).
Damit ist die Frage nicht mehr, *ob* eine Tastatur an das Gerät gehört, sondern **welche und
wann**: eine ausleihbare, die nur zur Pflege angesteckt wird, ist die naheliegende Antwort. Sie
liegt dann nicht im Ausstellungsraum herum, verschmutzt nicht und öffnet den Besuchern keine
Tastenwege in Chromium, die der Kiosk gerade zumacht (F11, Strg-W, Alt-Tab).

**Zu prüfen ist nur eins:** ob eine USB-Tastatur am laufenden Kiosk erkannt wird, ohne dass jemand
den Pi neu startet. Das ist eine Frage an das Gerät, keine an den Code — sie gehört zu
[Punkt 15](#15--abnahme-auf-dem-ersten-pi).

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
