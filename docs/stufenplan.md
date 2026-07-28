# Stufenplan

Der Bauplan des Projekts: was fertig ist, was noch kommt, und woran man erkennt, dass eine Stufe
fertig ist. Das *Warum* der technischen Entscheidungen steht in [decisions.md](decisions.md), das
*Wie* der Arbeit in [entwicklung.md](entwicklung.md).

Jede Stufe endet in einem lauffähigen, committeten Zustand.

## Zielbild

Ein Touchscreen-Kiosk für das Heimatmuseum Holm: historische Ortsfotos auf einer Karte, filterbar
über einen Zeitraum-Schieber, plus ein „Hilf mit"-Bereich, in dem Besucher fehlende Angaben
ergänzen. Vollständig offline auf einem Raspberry Pi, gesichert durch Einstecken eines USB-Sticks
und einen Knopfdruck.

```
┌────────────────────────────────────────┬──────────────┐
│                                        │  HILF MIT    │
│         Karte des Ortes                │              │
│         Fotos an ihrem Aufnahmeort     │  [Foto]      │
│                                        │  "Wo ist     │
│                                        │   das?"      │
├────────────────────────────────────────┤              │
│  1880 ├──●━━━━━━━━━━━━━━━●──┤ 1990     │  [Karte][×]  │
└────────────────────────────────────────┴──────────────┘
```

---

## Stand

| Stufe | Inhalt | Status |
|---|---|---|
| 0 | Repo-Gerüst, Entscheidungsdokumentation | ✅ |
| 1 | FastAPI + SQLite + Alembic + Docker | ✅ |
| 2 | Frontend-Gerüst, Offline-Karte, Entwicklungsumgebung | ✅ |
| 3 | Import-Pipeline: Hash-Dedup, EXIF, Thumbnails, Eingangsordner | ✅ |
| 4 | Abfrage-API: bbox + Zeitraum, Histogramm, Auslieferung | ✅ |
| 5 | Karte mit Foto-Markern und Clustering, Foto-Overlay | ✅ |
| 6 | Zeitschieber mit Jahrzehnt-Histogramm | ✅ |
| 7 | „Hilf mit": Verortung, Datierung, Ortssuche | ✅ |
| 7.5 | Sprachregelung, Textmodul, Entwicklerdoku | ✅ |
| 7.6 | Deutsche Texte im Backend nach Konvention ordnen | ✅ |
| **8** | **Admin-Bereich mit Stapel-Upload** | **als Nächstes** |
| 9 | Sicherung und Wiederherstellung auf USB | offen |
| 10 | Kiosk-Deployment auf dem Pi | offen |
| 11 | Ausbau nach Bedarf | offen |

Was in den fertigen Stufen entstanden ist, steht im [CHANGELOG](../CHANGELOG.md).

---

## Stufe 7.6 — Deutsche Texte im Backend nach Konvention ordnen ✅

Bestandsaufnahme nach der Sprachumstellung. Umgesetzt:

- **Query-Parameter englisch.** `?von=…&bis=…` heißt jetzt `?from_year=…&to_year=…` (nicht `from`,
  das ist in Python reserviert). Zieht sich durch bis in `TimeRange = { from, to }` im Frontend.
- **Faustregel eingeführt:** *Kann die Meldung im Kiosk oder im Admin-Bereich erscheinen? Dann
  Deutsch, sonst Englisch.* Damit wurden die `bbox`-Parsefehler und der Thumbnail-Größenfehler
  englisch, während 404, 409 und die Regionsprüfung deutsch blieben — sie erscheinen im
  Foto-Overlay bzw. im „Hilf mit"-Bereich.
- **OpenAPI-Beschreibungen englisch.** Sie stehen *in* der API und werden neben Feldnamen wie
  `open_count` gelesen.
- **CLI-Ausgaben bleiben deutsch.** Den Erstimport führt auch das Museumsteam aus.

Die Konventionstabellen in [CLAUDE.md](../CLAUDE.md) und [entwicklung.md](entwicklung.md) nennen die
Regel; ein Kommentar in `app/api/photos.py` erklärt sie an der Stelle, wo beide Sorten Meldungen
nebeneinander stehen.

Nicht angefasst und weiterhin richtig so: Fehlermeldungen an Besucher und Kuratoren, das
Import-Protokoll, die Ordnernamen `_erledigt`/`_problem` und die Datumsbeschriftungen. Letztere
sitzen architektonisch auf der falschen Seite für Mehrsprachigkeit — siehe
[adaption.md](adaption.md).

---

## Stufe 8 — Admin-Bereich mit Stapel-Upload

**Einstieg.** 3 Sekunden Druck auf die untere linke Bildschirmecke öffnet ein Zahlenfeld mit großen
Tasten; nach der PIN der Admin-Bereich. Für Besucher unsichtbar, für Eingeweihte in zwei Sekunden
erreichbar. PIN statt Passwort, weil am Touchscreen getippt wird. Token mit Ablauf, damit ein
vergessener Login nicht über Nacht offen bleibt.

**Fotopflege.** Liste mit Filter „unvollständig", Metadateneditor, Besucheränderungen sichten und
einzeln zurücknehmen, Import-Protokoll, Statusübersicht.

**Stapel-Upload.** Vor dem Hochladen lassen sich Ort und Jahr *optional* für den ganzen Stapel
angeben — bei Bildern von einer Kirchweih sind beide identisch, und das einmal statt vierzigmal
einzugeben ist der ganze Unterschied. Danach erscheint der Stapel als Tabelle:

```
┌──────┬──────────────────────────────────────┬──────────────┐
│ [▣]  │ Titel  Kirchweih 1932 Muehle         │              │
│ Bild │ Jahr   1932       Ort  Kirche        │ [Übernehmen] │
├──────┼──────────────────────────────────────┼──────────────┤
│ [▣]  │ Titel  Umzug_Hauptstrasse            │              │
│ Bild │ Jahr   1932       Ort  Kirche        │ [Übernehmen] │
└──────┴──────────────────────────────────────┴──────────────┘
                                        [ Alle übernehmen ]
```

Titel ist aus dem Dateinamen vorbelegt, Jahr und Ort aus den Stapelangaben; alles änderbar.
„Übernehmen" speichert die Zeile und entfernt sie aus der Liste, „Alle übernehmen" erledigt den Rest.

Die Fotos sind bereits **nach dem Hochladen** in der Datenbank, nicht erst nach „Übernehmen" — ein
geschlossener Browser darf keine Uploads kosten. Die Tabelle ist eine Nacharbeitsliste, keine
Warteschlange; was liegen bleibt, taucht im „Hilf mit"-Bereich auf. Dubletten werden im Ergebnis
benannt („3 waren schon da") statt still übersprungen.

**Fertig, wenn:** du am Touchscreen ohne Tastatur hinein- und wieder hinauskommst, einen Stapel
hochladen und dabei Ort und Jahr für alle setzen kannst, und ein Foto vollständig über die
Oberfläche pflegen kannst.

---

## Stufe 9 — Sicherung und Wiederherstellung auf USB

Bewusst eine gestaltete Funktion, kein Shell-Skript: Die Zielgruppe sind ältere Ehrenamtliche, die
das ein- bis zweimal im Jahr tun. Ein Skript bedeutet in der Praxis, dass es nie ausgeführt wird.

```
Stick einstecken
  ┌──────────────────────────────────────────────────┐
  │  ✓ USB-Stick erkannt:  SANDISK 32 GB             │
  │    28,4 GB frei — genug für 2.150 Fotos          │
  │        [   SICHERUNG  STARTEN   ]                │
  └──────────────────────────────────────────────────┘
        ↓
  │  Sichere Foto 340 von 2.150 …   ████░░░░░  16 %  │
        ↓
  ┌──────────────────────────────────────────────────┐
  │  ✓ Sicherung abgeschlossen                       │
  │    2.150 Fotos und alle Angaben gesichert        │
  │    Sie können den Stick jetzt abziehen.          │
  └──────────────────────────────────────────────────┘
```

Ohne Stick steht dort nur „Bitte USB-Stick einstecken" — kein Knopf, der ins Leere führt.

**Ordner statt ZIP** auf dem Stick: eine abgebrochene Sicherung ist dann teilweise brauchbar statt
komplett wertlos, und man kann sie an jedem Rechner öffnen. **Inkrementell** über die Hash-
Dateinamen: liegt der Name schon dort, ist es dasselbe Bild — die zweite Sicherung dauert Sekunden.
**`VACUUM INTO`** schreibt die Datenbank konsistent heraus, ohne den Betrieb anzuhalten.

**Wiederherstellen** packt daneben aus und schaltet erst am Ende um; der bisherige Stand wird vorher
beiseitegelegt. Eine abgebrochene Wiederherstellung darf den laufenden Bestand nie zerstören.

**Erinnerung** statt Automatik: „Letzte Sicherung vor 34 Tagen", ab 30 Tagen rot.

*Bekannter Fallstrick:* Auf Pi OS Lite mountet nichts von selbst (udev-Regel nötig), und ein
Docker-Bind-Mount zeigt neu eingehängte Datenträger nur mit `rshared`-Propagation. Ohne das bleibt
der Stick im Container unsichtbar.

**Fertig, wenn:** jemand aus der Zielgruppe die Sicherung ohne Hilfe und ohne Anleitung schafft —
und die Wiederherstellung auf einem zweiten, leeren Gerät nachweislich funktioniert.

---

## Stufe 10 — Kiosk-Deployment auf dem Pi

Raspberry Pi OS **Lite** plus **cage**, ein winziger Wayland-Compositor, der genau ein Programm im
Vollbild anzeigt. Robuster als der volle Desktop: nichts kann sich in den Vordergrund drängen, kein
Hintergrundbild blitzt beim Booten auf, keine Update-Hinweise, kein Bildschirmschoner.

Ablauf nach dem Einschalten (~20 s):

1. Docker startet, die Container laufen mit `restart: unless-stopped` von selbst hoch.
2. `photomap-kiosk.service` wartet auf `/api/health` — sonst begrüßt das Museum seine Besucher für
   ein paar Sekunden mit einer Fehlerseite.
3. `cage -- chromium --kiosk` startet, Mauszeiger ausgeblendet, Energiesparen aus, Browserprofil bei
   jedem Start frisch.
4. Stürzt Chromium ab, startet systemd ihn neu. Fällt der Strom aus, bootet der Pi in denselben
   Zustand.

Dazu ein **Leerlauf-Reset** im Frontend: nach einigen Minuten ohne Berührung schließt sich ein
offenes Foto, Karte und Zeitraum kehren zur Standardansicht zurück. Sonst steht das Gerät morgens
im Zustand des letzten Besuchers vom Vorabend.

Ergänzend `docs/betrieb.md` (SD-Klon, Wartungsausgang, Fehlersuche) und `update.sh` für das
Offline-Update vom Stick.

**Fertig, wenn:** der Pi nach einem Kaltstart ohne Tastatur von selbst in der Karte landet — und
nach einem gezogenen Netzstecker genauso wieder hochkommt.

---

## Stufe 11 — Ausbau nach Bedarf

Nichts davon ist eingeplant, alles ist naheliegend:

- **Perceptual Hash** gegen inhaltlich gleiche, aber unterschiedlich zugeschnittene Scans. Der
  SHA-256 erkennt die nicht.
- **Jahreszahl aus dem Dateinamen** raten (`Kirchweih_1932_Muehle.jpg`). Vorsicht: `IMG_1932.jpg`
  ist ein Kamerazähler. Nur als Vorschlag markieren, nie als Tatsache.
- **Historische Karte** als umschaltbares Overlay (Urkataster o. ä.).
- **Attract-Mode**: Diashow bei Leerlauf statt Standardansicht.
- **Rechte und Herkunft** pro Foto — im Museumskontext oft relevant.
- **Volltextsuche** über SQLite FTS5.
- **Read-Only-Overlay-Dateisystem** gegen SD-Korruption bei Stromausfall.

---

## Prüfungen, die durch alle Stufen gehen

- **Offline-Test (der wichtigste).** Netz trennen, Karte bewegen. In den DevTools darf keine Anfrage
  an eine fremde Herkunft stehen:
  ```js
  performance.getEntriesByType('resource')
    .filter(e => !e.name.startsWith(location.origin) && !e.name.startsWith('data:')).length  // 0
  ```
- **Unschärfe-Test.** Ein Foto „1920er" muss bei Auswahl 1925–1930 erscheinen. Der Fall, der bei
  naiver Datumsabfrage still falsch wird.
- **Touch-Test am Zielgerät.** Marker, Slider-Griffe und die Schließfläche mit dem Finger bedienen,
  nicht mit der Maus. Ziel: unter 1,5 s vom Loslassen bis zu aktualisierten Markern.
- **Dauerlauf.** Einen Tag laufen lassen, danach Chromiums Speicherverbrauch prüfen — Kioske sterben
  an einem langsamen Leck im Frontend, nicht am Backend.
- **Kaltstart.** Netzstecker ziehen und wieder einstecken. Ohne Tastatur, ohne Klick, ohne
  Fehlerseite zurück in die Karte.
- **Wiederherstellung wirklich proben.** Auf ein zweites, leeres Gerät zurückspielen. Ein
  ungetestetes Backup ist kein Backup.
- **Bedienbarkeitstest mit der echten Zielgruppe.** Eine ehrenamtliche Person die Sicherung
  durchführen lassen, ohne zu helfen, und zusehen, wo sie stockt. Der aussagekräftigste Test des
  ganzen Projekts.

## Offene Punkte

- Displayauflösung und -orientierung des Museumsgeräts (beeinflusst die Layoutmaße)
- Rechte- und Herkunftsangaben pro Foto — im Museumskontext oft relevant, noch nicht spezifiziert
- Lizenz des Projekts
